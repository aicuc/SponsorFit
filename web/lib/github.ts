import type { RepositorySnapshot } from "./types";

const OWNER_PATTERN = /^[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?$/;
const REPOSITORY_PATTERN = /^[A-Za-z0-9._-]{1,100}$/;

interface GitHubRepository {
  name: string;
  full_name: string;
  html_url: string;
  description: string | null;
  language: string | null;
  topics?: string[];
  stargazers_count: number;
  forks_count: number;
  open_issues_count: number;
  license: { spdx_id?: string; name?: string } | null;
  updated_at: string;
  archived: boolean;
  owner: { login: string };
}

interface GitHubReadme {
  content?: string;
  encoding?: string;
}

export class GitHubRepositoryError extends Error {
  public readonly status: number;

  constructor(
    message: string,
    status: number,
  ) {
    super(message);
    this.status = status;
    this.name = "GitHubRepositoryError";
  }
}

export function parseGitHubRepository(input: string): {
  owner: string;
  repository: string;
} {
  const value = input.trim();
  let parts: string[];

  if (/^https?:\/\//i.test(value)) {
    let url: URL;
    try {
      url = new URL(value);
    } catch {
      throw new GitHubRepositoryError("Enter a valid GitHub repository URL.", 400);
    }
    if (!["github.com", "www.github.com"].includes(url.hostname.toLowerCase())) {
      throw new GitHubRepositoryError("Only public github.com repositories are supported.", 400);
    }
    parts = url.pathname.split("/").filter(Boolean);
  } else {
    parts = value.split("/").filter(Boolean);
  }

  if (parts.length !== 2) {
    throw new GitHubRepositoryError(
      "Use a repository URL like https://github.com/owner/repository.",
      400,
    );
  }

  const owner = parts[0];
  const repository = parts[1].replace(/\.git$/i, "");
  if (!OWNER_PATTERN.test(owner) || !REPOSITORY_PATTERN.test(repository)) {
    throw new GitHubRepositoryError("That GitHub owner or repository name is not valid.", 400);
  }

  return { owner, repository };
}

function headers(): HeadersInit {
  const result: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "SponsorFit-Web",
  };
  if (process.env.GITHUB_TOKEN) {
    result.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  }
  return result;
}

async function githubFetch<T>(url: string): Promise<T> {
  const response = await fetch(url, {
    headers: headers(),
    signal: AbortSignal.timeout(8_000),
  });

  if (response.status === 404) {
    throw new GitHubRepositoryError("Repository not found or not public.", 404);
  }
  if (response.status === 403 || response.status === 429) {
    throw new GitHubRepositoryError(
      "GitHub's public API limit is busy. Try again shortly or configure GITHUB_TOKEN.",
      429,
    );
  }
  if (!response.ok) {
    throw new GitHubRepositoryError("GitHub could not return this repository right now.", 502);
  }
  return (await response.json()) as T;
}

export async function fetchRepositorySnapshot(input: string): Promise<RepositorySnapshot> {
  const { owner, repository } = parseGitHubRepository(input);
  const base = `https://api.github.com/repos/${encodeURIComponent(owner)}/${encodeURIComponent(repository)}`;
  const [metadata, readmeResult] = await Promise.all([
    githubFetch<GitHubRepository>(base),
    githubFetch<GitHubReadme>(`${base}/readme`).catch((error: unknown) => {
      if (error instanceof GitHubRepositoryError && error.status === 404) {
        return null;
      }
      throw error;
    }),
  ]);

  let readme = "";
  if (readmeResult?.content && readmeResult.encoding === "base64") {
    readme = Buffer.from(readmeResult.content, "base64").toString("utf8").slice(0, 12_000);
  }

  return {
    owner: metadata.owner.login,
    name: metadata.name,
    fullName: metadata.full_name,
    url: metadata.html_url,
    description: metadata.description || "",
    language: metadata.language,
    topics: metadata.topics || [],
    stars: metadata.stargazers_count,
    forks: metadata.forks_count,
    openIssues: metadata.open_issues_count,
    license: metadata.license?.spdx_id || metadata.license?.name || null,
    updatedAt: metadata.updated_at,
    archived: metadata.archived,
    readme,
  };
}
