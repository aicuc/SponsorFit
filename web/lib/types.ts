export type EvidenceLabel = "Observed" | "Inferred" | "Hypothesis";

export interface RepositorySnapshot {
  owner: string;
  name: string;
  fullName: string;
  url: string;
  description: string;
  language: string | null;
  topics: string[];
  stars: number;
  forks: number;
  openIssues: number;
  license: string | null;
  updatedAt: string;
  archived: boolean;
  readme: string;
}

export interface PreviewItem {
  label: EvidenceLabel;
  eyebrow: string;
  value: string;
  detail: string;
}

export interface SponsorPreview {
  archetype: string;
  repository: Omit<RepositorySnapshot, "readme" | "topics" | "openIssues" | "archived">;
  project: PreviewItem;
  customer: PreviewItem;
  offer: PreviewItem;
  nextMove: PreviewItem;
  caveat: string;
}

export interface CaseStudy {
  slug: string;
  repository: string;
  repositoryUrl: string;
  category: string;
  accent: string;
  outcome: string;
  observed: string[];
  customer: string;
  offer: string;
  nextMove: string;
  lesson: string;
}
