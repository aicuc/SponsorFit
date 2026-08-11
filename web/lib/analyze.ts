import type { RepositorySnapshot, SponsorPreview } from "./types";

type Archetype =
  | "document-processing"
  | "developer-tool"
  | "automation"
  | "data-infrastructure"
  | "open-source-library";

interface Recommendation {
  name: string;
  customer: string;
  customerDetail: string;
  offer: string;
  offerDetail: string;
  nextMove: string;
  nextDetail: string;
}

const RECOMMENDATIONS: Record<Archetype, Recommendation> = {
  "document-processing": {
    name: "Document infrastructure",
    customer: "AI infrastructure teams building document workflows",
    customerDetail:
      "They feel the cost of extraction errors through failed retrieval, manual cleanup, and support incidents.",
    offer: "Reliable batch ingestion, difficult-format support, monitoring, and an SLA",
    offerDetail:
      "Keep the parsing core open; charge for operational reliability, volume, and accountable support.",
    nextMove: "Publish an accuracy benchmark on ten difficult real-world documents",
    nextDetail:
      "A benchmark turns a broad quality claim into evidence a technical buyer can evaluate.",
  },
  "developer-tool": {
    name: "Developer tool",
    customer: "Small engineering teams standardizing a shared workflow",
    customerDetail:
      "Individual developers create adoption, while teams feel the pain of inconsistent setup and unsupported integrations.",
    offer: "Team configuration, one maintained integration, and priority support",
    offerDetail:
      "Keep local developer use open; charge where coordination and maintenance responsibility begin.",
    nextMove: "Ship one production-grade integration and interview five teams using adjacent tools",
    nextDetail:
      "A narrow integration is easier to validate than a broad collaboration platform.",
  },
  automation: {
    name: "Workflow automation",
    customer: "Agencies and operators repeating this workflow for clients",
    customerDetail:
      "Small manual steps become expensive when repeated across clients, files, or weekly operating cycles.",
    offer: "A fixed-scope workflow pilot with batch mode, templates, and setup support",
    offerDetail:
      "Sell the completed outcome first, then productize only the steps that repeat across paid pilots.",
    nextMove: "Run three manual pilots around one measurable workflow outcome",
    nextDetail:
      "Paid service delivery reveals the edge cases and integrations worth turning into product features.",
  },
  "data-infrastructure": {
    name: "Data infrastructure",
    customer: "Platform teams operating the project in production",
    customerDetail:
      "Their budget appears when reliability, observability, governance, and migration risk become ongoing work.",
    offer: "Managed operation, observability, migration help, and a support agreement",
    offerDetail:
      "The open engine drives adoption; the operational layer transfers risk to a responsible maintainer.",
    nextMove: "Map the ten most active production users and test a support-backed pilot",
    nextDetail:
      "Issue authors, dependents, and integration maintainers are stronger leads than a generic waitlist.",
  },
  "open-source-library": {
    name: "Open-source library",
    customer: "Product teams depending on the project in production",
    customerDetail:
      "They pay to reduce upgrade, compatibility, and maintenance uncertainty around a useful dependency.",
    offer: "Long-term support, migration help, compatibility guarantees, and sponsored integrations",
    offerDetail:
      "Core behavior should stay open; paid value comes from certainty, speed, and a named support owner.",
    nextMove: "Find ten dependents and ask which upgrade or integration risk costs them the most",
    nextDetail:
      "Dependency conversations expose real production pain before you commit to a hosted product.",
  },
};

function includesAny(text: string, terms: string[]): boolean {
  return terms.some((term) => text.includes(term));
}

export function classifyRepository(snapshot: RepositorySnapshot): Archetype {
  const text = [
    snapshot.description,
    snapshot.topics.join(" "),
    // The opening section describes the project. Examples and roadmap content
    // later in a README must not override that primary evidence.
    snapshot.readme.slice(0, 1_500),
  ]
    .join(" ")
    .toLowerCase();

  if (
    includesAny(text, [
      "pdf",
      "ocr",
      "document parsing",
      "document extraction",
      "document intelligence",
    ])
  ) {
    return "document-processing";
  }

  if (
    includesAny(text, [
      "workflow automation",
      "automate workflows",
      "no-code",
      "low-code",
      "automation platform",
    ])
  ) {
    return "automation";
  }

  if (
    includesAny(text, [
      "database",
      "observability",
      "data pipeline",
      "stream processing",
      "vector database",
      "data infrastructure",
    ])
  ) {
    return "data-infrastructure";
  }

  if (
    includesAny(text, [
      "developer tool",
      "command-line",
      "command line",
      " cli ",
      "terminal",
      "coding agent",
      "developer experience",
      "api client",
    ])
  ) {
    return "developer-tool";
  }

  return "open-source-library";
}

export function analyzeRepository(snapshot: RepositorySnapshot): SponsorPreview {
  const archetype = classifyRepository(snapshot);
  const recommendation = RECOMMENDATIONS[archetype];
  const description = snapshot.description.trim();
  const footprint = [
    snapshot.language || "language not reported",
    `${snapshot.stars.toLocaleString("en-US")} stars`,
    snapshot.license ? `${snapshot.license} license` : "license not reported",
  ].join(" · ");

  return {
    archetype: recommendation.name,
    repository: {
      owner: snapshot.owner,
      name: snapshot.name,
      fullName: snapshot.fullName,
      url: snapshot.url,
      description: snapshot.description,
      language: snapshot.language,
      stars: snapshot.stars,
      forks: snapshot.forks,
      license: snapshot.license,
      updatedAt: snapshot.updatedAt,
    },
    project: {
      label: "Observed",
      eyebrow: "What the repository proves",
      value: description || `${snapshot.fullName} needs a clearer one-line project description.`,
      detail: footprint,
    },
    customer: {
      label: "Hypothesis",
      eyebrow: "Happiest sponsor",
      value: recommendation.customer,
      detail: recommendation.customerDetail,
    },
    offer: {
      label: "Hypothesis",
      eyebrow: "What they could pay for",
      value: recommendation.offer,
      detail: recommendation.offerDetail,
    },
    nextMove: {
      label: "Inferred",
      eyebrow: "Best next validation move",
      value: recommendation.nextMove,
      detail: recommendation.nextDetail,
    },
    caveat:
      "This is a repository-grounded preview, not proof of demand. Validate the sponsor and offer through real conversations before building.",
  };
}
