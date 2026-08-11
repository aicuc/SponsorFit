import { analyzeRepository } from "@/lib/analyze";
import {
  fetchRepositorySnapshot,
  GitHubRepositoryError,
  parseGitHubRepository,
} from "@/lib/github";
import type { SponsorPreview } from "@/lib/types";

export const runtime = "nodejs";

const RATE_WINDOW_MS = 60_000;
const RATE_LIMIT = 10;
const CACHE_TTL_MS = 10 * 60_000;

const requestLog = new Map<string, number[]>();
const previewCache = new Map<string, { expires: number; preview: SponsorPreview }>();

function clientKey(request: Request): string {
  return request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() || "local";
}

function isRateLimited(key: string): boolean {
  const now = Date.now();
  const recent = (requestLog.get(key) || []).filter((time) => now - time < RATE_WINDOW_MS);
  recent.push(now);
  requestLog.set(key, recent);
  return recent.length > RATE_LIMIT;
}

function errorResponse(message: string, status: number) {
  return Response.json({ error: message }, { status });
}

export async function POST(request: Request) {
  if (isRateLimited(clientKey(request))) {
    return errorResponse("Too many previews at once. Try again in a minute.", 429);
  }

  const contentLength = Number(request.headers.get("content-length") || 0);
  if (contentLength > 2_000) {
    return errorResponse("Request is too large.", 413);
  }

  let repository: unknown;
  try {
    const body = (await request.json()) as { repository?: unknown };
    repository = body.repository;
  } catch {
    return errorResponse("Send a JSON body with a repository URL.", 400);
  }

  if (typeof repository !== "string" || repository.length > 300) {
    return errorResponse("Enter a public GitHub repository URL.", 400);
  }

  try {
    const parsed = parseGitHubRepository(repository);
    const cacheKey = `${parsed.owner}/${parsed.repository}`.toLowerCase();
    const cached = previewCache.get(cacheKey);
    if (cached && cached.expires > Date.now()) {
      return Response.json(cached.preview, { headers: { "X-SponsorFit-Cache": "HIT" } });
    }

    const snapshot = await fetchRepositorySnapshot(repository);
    const preview = analyzeRepository(snapshot);
    if (previewCache.size >= 100) {
      const firstKey = previewCache.keys().next().value;
      if (firstKey) previewCache.delete(firstKey);
    }
    previewCache.set(cacheKey, { expires: Date.now() + CACHE_TTL_MS, preview });
    return Response.json(preview, { headers: { "X-SponsorFit-Cache": "MISS" } });
  } catch (error: unknown) {
    if (error instanceof GitHubRepositoryError) {
      return errorResponse(error.message, error.status);
    }
    if (error instanceof Error && error.name === "TimeoutError") {
      return errorResponse("GitHub took too long to respond. Try again.", 504);
    }
    return errorResponse("SponsorFit could not analyze this repository right now.", 500);
  }
}
