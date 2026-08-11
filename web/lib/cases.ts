import type { CaseStudy } from "./types";

export const CASE_STUDIES: CaseStudy[] = [
  {
    slug: "docling",
    repository: "docling-project/docling",
    repositoryUrl: "https://github.com/docling-project/docling",
    category: "Document infrastructure",
    accent: "lime",
    outcome: "Turn difficult documents into structured data that downstream AI systems can use.",
    observed: [
      "Open-source document conversion project",
      "Supports multiple document formats and AI-oriented workflows",
      "Developer-facing Python surface",
    ],
    customer: "AI infrastructure teams operating document ingestion in production",
    offer: "A managed batch pipeline, difficult-format support, monitoring, and deployment assurance",
    nextMove: "Publish a reproducible accuracy and throughput benchmark for ten hostile document sets",
    lesson: "Accuracy is interesting; accountable ingestion quality is budget-worthy.",
  },
  {
    slug: "aider",
    repository: "Aider-AI/aider",
    repositoryUrl: "https://github.com/Aider-AI/aider",
    category: "AI developer tool",
    accent: "orange",
    outcome: "Help developers modify real codebases with an AI pair-programming workflow.",
    observed: [
      "Terminal-first developer experience",
      "Works across existing repositories",
      "Model and editor integrations are central to usage",
    ],
    customer: "Small engineering teams trying to standardize AI-assisted development",
    offer: "Shared policy, approved model routing, usage visibility, and rollout support",
    nextMove: "Interview five teams with repeat usage before building any management surface",
    lesson: "Individual love creates adoption; team consistency creates a paid boundary.",
  },
  {
    slug: "uv",
    repository: "astral-sh/uv",
    repositoryUrl: "https://github.com/astral-sh/uv",
    category: "Developer infrastructure",
    accent: "blue",
    outcome: "Make Python project and package workflows dramatically faster and more predictable.",
    observed: [
      "Command-line tooling for Python developers",
      "Performance and compatibility are prominent project values",
      "Sits inside repeatable development and CI workflows",
    ],
    customer: "Platform teams standardizing Python tooling across many repositories",
    offer: "Migration programs, compatibility assurance, enterprise rollout, and support",
    nextMove: "Map the recurring blockers reported by teams migrating large monorepos",
    lesson: "The binary stays open; migration risk and organizational rollout carry value.",
  },
  {
    slug: "n8n",
    repository: "n8n-io/n8n",
    repositoryUrl: "https://github.com/n8n-io/n8n",
    category: "Workflow automation",
    accent: "pink",
    outcome: "Connect systems and automate business workflows without rebuilding every integration.",
    observed: [
      "Visual workflow automation product",
      "A broad integration surface",
      "Self-hosting and operational workflows are important",
    ],
    customer: "Operations teams and agencies running business-critical automations",
    offer: "Managed operation, collaboration, governance, execution reliability, and support",
    nextMove: "Package one high-frequency industry workflow with a measurable operational outcome",
    lesson: "Users do not buy nodes; they buy workflows that keep running.",
  },
  {
    slug: "bruno",
    repository: "usebruno/bruno",
    repositoryUrl: "https://github.com/usebruno/bruno",
    category: "API developer tool",
    accent: "violet",
    outcome: "Give API teams a local, version-controlled way to collaborate on requests.",
    observed: [
      "Developer-facing API client",
      "Local files and Git collaboration are part of the product shape",
      "Team workflows grow around an open desktop core",
    ],
    customer: "API teams that need a consistent, governable request workflow",
    offer: "Team synchronization, access controls, organization policy, and enterprise support",
    nextMove: "Validate the one collaboration failure that causes teams to abandon local-only workflows",
    lesson: "A useful local core earns trust; coordination and governance fund the business.",
  },
];

export function getCaseStudy(slug: string): CaseStudy | undefined {
  return CASE_STUDIES.find((item) => item.slug === slug);
}
