import assert from "node:assert/strict";
import test from "node:test";

import { analyzeRepository, classifyRepository } from "../lib/analyze.ts";
import { GitHubRepositoryError, parseGitHubRepository } from "../lib/github.ts";
import type { RepositorySnapshot } from "../lib/types.ts";

function snapshot(overrides: Partial<RepositorySnapshot> = {}): RepositorySnapshot {
  return {
    owner: "example",
    name: "project",
    fullName: "example/project",
    url: "https://github.com/example/project",
    description: "A useful open-source library",
    language: "TypeScript",
    topics: [],
    stars: 120,
    forks: 8,
    openIssues: 4,
    license: "MIT",
    updatedAt: "2026-08-11T00:00:00Z",
    archived: false,
    readme: "",
    ...overrides,
  };
}

test("parses canonical GitHub URLs and owner/repository shorthand", () => {
  assert.deepEqual(parseGitHubRepository("https://github.com/aicuc/SponsorFit"), {
    owner: "aicuc",
    repository: "SponsorFit",
  });
  assert.deepEqual(parseGitHubRepository("aicuc/SponsorFit.git"), {
    owner: "aicuc",
    repository: "SponsorFit",
  });
});

test("rejects non-GitHub hosts and nested repository paths", () => {
  for (const input of [
    "https://example.com/aicuc/SponsorFit",
    "https://github.com/aicuc/SponsorFit/issues",
    "not-a-repository",
  ]) {
    assert.throws(
      () => parseGitHubRepository(input),
      (error: unknown) => error instanceof GitHubRepositoryError && error.status === 400,
    );
  }
});

test("classifies document processing from repository evidence", () => {
  const repository = snapshot({
    description: "Extract structured data from PDF documents",
  });
  assert.equal(classifyRepository(repository), "document-processing");
  assert.match(analyzeRepository(repository).customer.value, /AI infrastructure/i);
});

test("classifies developer tools and keeps recommendations labeled as hypotheses", () => {
  const repository = snapshot({
    description: "A command-line developer tool for coding agents",
  });
  const result = analyzeRepository(repository);
  assert.equal(result.archetype, "Developer tool");
  assert.equal(result.project.label, "Observed");
  assert.equal(result.customer.label, "Hypothesis");
  assert.equal(result.offer.label, "Hypothesis");
  assert.equal(result.nextMove.label, "Inferred");
});

test("classifies workflow automation before the generic library fallback", () => {
  assert.equal(
    classifyRepository(snapshot({ description: "A low-code workflow automation platform" })),
    "automation",
  );
  assert.equal(classifyRepository(snapshot()), "open-source-library");
});

test("does not let examples later in the README override the project description", () => {
  const repository = snapshot({
    description: "A command-line developer tool for open-source maintainers",
    readme: `${"Repository business analysis and customer discovery. ".repeat(40)}PDF OCR example`,
  });
  assert.equal(classifyRepository(repository), "developer-tool");
});
