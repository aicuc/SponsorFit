from __future__ import annotations

from .models import CustomerOpportunity, RepositoryEvidence, SponsorFitAnalysis


WEIGHTS = {
    "pain": 20,
    "willingness_to_pay": 20,
    "ease_of_reaching": 15,
    "strategic_fit": 15,
    "product_fit": 15,
    "revenue_potential": 15,
}


def _score(values: tuple[int, int, int, int, int, int]) -> dict[str, int]:
    """Convert 1-5 judgments into the published weighted score."""
    return {
        key: round(value / 5 * weight)
        for (key, weight), value in zip(WEIGHTS.items(), values)
    }


def _customer(
    customer_type: str,
    pain: str,
    workaround: str,
    matters: str,
    pay_for: str,
    not_pay: str,
    required: str,
    budget: str,
    reach: str,
    score_values: tuple[int, int, int, int, int, int],
) -> CustomerOpportunity:
    return CustomerOpportunity(
        customer_type, pain, workaround, matters, pay_for, not_pay,
        required, budget, reach, _score(score_values),
    )


def classify(evidence: RepositoryEvidence) -> str:
    # Weight the project's own opening description, not examples and roadmap text
    # later in a README. This prevents a monetization tool mentioning "PDF" in an
    # example from being classified as a PDF product itself.
    text = " ".join([evidence.description, evidence.readme_excerpt[:1_500]]).lower()
    if any(term in text for term in ("pdf", "ocr", "document pars", "document extract")):
        return "document-processing"
    if any(term in text for term in ("agent", "developer tool", "sdk", "cli", "plugin", "api")):
        return "developer-tool"
    if evidence.files_count < 80:
        return "small-utility"
    return "open-source-library"


def _supplemental_customers(archetype: str) -> list[CustomerOpportunity]:
    if archetype == "document-processing":
        return [
            _customer(
                "Document automation consultancy",
                "Edge cases and maintenance make client automations unprofitable.",
                "Carry private parser forks for each engagement.",
                "Maintainer-backed components reduce delivery and support risk.",
                "Commercial support, reusable templates, and escalation access.",
                "A generic cloud UI that cannot fit client workflows.",
                "Stable extension points and a partner support package.",
                "$3,000–$20,000/year", "Automation agencies and implementation partners",
                (4, 4, 3, 4, 4, 4),
            ),
            _customer(
                "Research archive or public-interest foundation",
                "Important document collections remain hard to search and access.",
                "Fund one-off extraction projects with little reusable infrastructure.",
                "Open benchmarks and format support create durable public infrastructure.",
                "Sponsored format support, accessibility work, and reproducible benchmarks.",
                "Exclusive ownership of community improvements.",
                "A defined collection, public deliverables, and impact measures.",
                "$5,000–$40,000 grant or sponsorship", "Digital humanities labs and open-data funders",
                (3, 3, 2, 5, 3, 3),
            ),
        ]
    if archetype == "developer-tool":
        return [
            _customer(
                "Engineering consultancy rolling the tool out for clients",
                "Each client rollout repeats configuration and enablement work.",
                "Maintain internal templates and unsupported integrations.",
                "A supported partner path makes delivery faster and more credible.",
                "Training, implementation kits, and escalation support.",
                "Per-seat charges for developers who only consume open-source output.",
                "Repeatable deployment recipes and a partner support agreement.",
                "$2,000–$15,000/year", "DevOps consultancies and solution partners",
                (3, 4, 3, 4, 4, 4),
            ),
            _customer(
                "Adjacent platform vendor seeking a maintained integration",
                "Its users expect an integration that neither community reliably owns.",
                "Build a demo integration that becomes stale.",
                "Maintainer ownership creates a credible shared adoption channel.",
                "A sponsored integration, compatibility tests, and joint launch.",
                "Undirected sponsorship without a concrete user outcome.",
                "Audience overlap and a defined integration roadmap.",
                "$3,000–$25,000 sponsorship", "Ecosystem marketplaces and partner teams",
                (3, 4, 4, 4, 4, 3),
            ),
        ]
    if archetype == "small-utility":
        return [
            _customer(
                "Software distributor packaging the utility",
                "Users need trusted binaries and timely security updates across platforms.",
                "Package releases downstream and absorb breakage.",
                "A maintainer support relationship makes distribution predictable.",
                "Release coordination, provenance, and priority fixes.",
                "New end-user features unrelated to packaging.",
                "Signed releases, CI coverage, and a disclosure policy.",
                "$1,000–$5,000/year", "Package maintainers and software distributors",
                (2, 3, 3, 4, 4, 2),
            ),
            _customer(
                "Niche community funding one missing workflow",
                "A shared edge case remains unsolved because no individual can justify the work.",
                "Members maintain incompatible scripts.",
                "A sponsored open feature benefits the whole community.",
                "A milestone-based implementation released in the open.",
                "Permanent exclusive control or a recurring plan without ongoing work.",
                "A specific acceptance test and pooled sponsor commitment.",
                "$500–$5,000 milestone", "Existing issue participants and niche forums",
                (2, 3, 4, 5, 3, 2),
            ),
        ]
    return [
        _customer(
            "Consultancy standardizing delivery on the library",
            "Repeated client integrations depend on undocumented expert knowledge.",
            "Maintain internal wrappers and onboarding material.",
            "Direct maintainer access makes delivery repeatable.",
            "Partner training, implementation guidance, and escalation support.",
            "A hosted dashboard unrelated to its delivery workflow.",
            "Stable extension points and a scoped partner package.",
            "$2,000–$15,000/year", "Ecosystem consultancies and integrators",
            (3, 4, 3, 4, 4, 3),
        ),
        _customer(
            "Foundation funding shared ecosystem infrastructure",
            "A widely shared capability depends on unpaid maintenance.",
            "Fund isolated features or wait for volunteer capacity.",
            "Milestone funding improves open infrastructure for many downstream users.",
            "Security, accessibility, maintenance, or interoperability milestones.",
            "Closed features that reduce public benefit.",
            "Visible downstream impact and a concrete public milestone.",
            "$5,000–$50,000 grant", "Language foundations and open-source funds",
            (3, 3, 2, 5, 4, 3),
        ),
    ]


def _maturity(evidence: RepositoryEvidence) -> tuple[str, str]:
    points = sum((
        bool(evidence.manifests), evidence.has_tests, evidence.has_ci,
        evidence.has_docs, evidence.has_examples, evidence.has_changelog,
        evidence.license_name != "Unknown",
    ))
    if points >= 6:
        return "Established", "Ready to test a paid offer; demand is still unverified"
    if points >= 3:
        return "Working project", "Ready for customer discovery before productizing"
    return "Early", "Earn trust and validate one painful use case first"


def _document_customers() -> list[CustomerOpportunity]:
    return [
        _customer(
            "AI infrastructure startup building document RAG",
            "Unreliable extraction creates bad retrieval and costly support incidents.",
            "Glue together OCR vendors, parsers, and manual cleanup.",
            "A stable ingestion layer shortens time-to-production and improves answer quality.",
            "A hosted batch API, difficult-format support, monitoring, and an SLA.",
            "A thin hosted wrapper with no quality evidence.",
            "Benchmark results, async batch jobs, retries, observability, and data-retention controls.",
            "$199–$1,500/month or usage-based", "GitHub dependents, RAG Discords, AI founder communities",
            (5, 5, 4, 5, 5, 5),
        ),
        _customer(
            "Operations team processing high-volume forms",
            "Staff rekey data and fix extraction errors every week.",
            "Outsource data entry or maintain brittle scripts.",
            "Automation replaces recurring labor rather than merely adding a developer library.",
            "Workflow setup, human review queues, exports, and managed operation.",
            "Parser accuracy on clean sample PDFs alone.",
            "A narrow industry template, audit trail, and measurable error-rate reduction.",
            "$2,000–$15,000 implementation + support", "Industry operators and automation agencies",
            (5, 5, 3, 4, 4, 5),
        ),
        _customer(
            "Regulated enterprise document platform team",
            "Cloud-only document processing violates security or residency requirements.",
            "Run legacy software on-premises and absorb maintenance risk.",
            "A maintained self-hosted path removes procurement and compliance blockers.",
            "Private deployment, SSO/RBAC, audit logs, support, and commercial indemnity.",
            "Community code that lacks a support owner.",
            "Security documentation, predictable releases, deployment tooling, and an SLA.",
            "$15,000–$80,000/year", "Security-conscious platform teams and solution partners",
            (4, 5, 2, 5, 4, 5),
        ),
    ]


def _developer_customers() -> list[CustomerOpportunity]:
    return [
        _customer(
            "Small engineering team standardizing an internal workflow",
            "Every developer maintains a slightly different fragile setup.",
            "Copy snippets, scripts, and tribal knowledge between repositories.",
            "A supported team workflow saves engineering time and reduces operational surprises.",
            "Team configuration, hosted coordination, policy controls, and priority support.",
            "The same local features already available in the open-source core.",
            "Shared state, CI integration, clear security posture, and admin controls.",
            "$49–$299/month per team", "GitHub users, maintainers, DevOps communities",
            (4, 4, 5, 5, 5, 4),
        ),
        _customer(
            "Developer-tool startup embedding the project",
            "Building and maintaining this capability distracts from its own product.",
            "Fork the project or assemble lower-quality dependencies.",
            "A reliable integration compresses roadmap time and transfers maintenance risk.",
            "Stable API, premium integration, roadmap access, and response-time SLA.",
            "A logo placement or generic sponsorship tier.",
            "Version guarantees, integration tests, usage guidance, and support terms.",
            "$500–$3,000/month", "Dependency graph, GitHub code search, founder networks",
            (4, 5, 4, 5, 5, 5),
        ),
        _customer(
            "Enterprise platform engineering group",
            "Unmanaged tooling creates security, governance, and rollout problems.",
            "Build an internal fork and assign engineers to maintain it.",
            "A supported distribution reduces governance work across many teams.",
            "SSO, policy, auditability, long-term support, and private deployment.",
            "Cosmetic features or an arbitrary seat gate.",
            "Security review material, admin capabilities, support, and release discipline.",
            "$10,000–$75,000/year", "Platform engineering events and existing enterprise users",
            (4, 5, 2, 5, 4, 5),
        ),
    ]


def _utility_customers() -> list[CustomerOpportunity]:
    return [
        _customer(
            "Consultant or agency repeating this task for clients",
            "Small manual steps compound across many client engagements.",
            "Maintain private scripts and checklists.",
            "A dependable automation protects margin and makes delivery repeatable.",
            "A pro CLI bundle, batch mode, templates, and commercial support.",
            "A subscription for an occasional single-file command.",
            "Batch workflows, stable output, and one integration used in client delivery.",
            "$49–$199 one-time or $29–$99/month", "Agencies, freelancer communities, GitHub users",
            (3, 3, 4, 4, 5, 3),
        ),
        _customer(
            "Engineering team using the utility in CI",
            "A tiny tool becomes a release dependency with no clear support owner.",
            "Pin an old version or carry an internal fork.",
            "Maintenance guarantees are more valuable than additional commands.",
            "Priority fixes, compatibility guarantees, and CI-oriented features.",
            "Features unrelated to the production workflow.",
            "Tests, semantic releases, security policy, and documented compatibility.",
            "$1,000–$8,000/year support", "GitHub dependents and package registry users",
            (3, 4, 4, 5, 5, 3),
        ),
        _customer(
            "Individual power user",
            "The task is annoying but not usually business-critical.",
            "Use manual steps or several free tools.",
            "Convenience can justify a small one-time purchase.",
            "Polished binaries, presets, and automatic updates.",
            "Enterprise packaging or recurring fees without recurring value.",
            "Frictionless installation and a visibly faster workflow.",
            "$10–$39 one-time", "Product Hunt, niche Reddit communities, package registries",
            (2, 2, 5, 3, 4, 2),
        ),
    ]


def _library_customers() -> list[CustomerOpportunity]:
    return [
        _customer(
            "Product team depending on the library in production",
            "A core dependency has upgrade, reliability, and maintenance risk.",
            "Pin versions, maintain patches, and rely on best-effort community help.",
            "Support and compatibility guarantees reduce expensive engineering uncertainty.",
            "Priority support, LTS releases, migration help, and a roadmap agreement.",
            "Core library behavior that the community already maintains.",
            "Documented release policy, strong tests, case studies, and response targets.",
            "$3,000–$20,000/year", "GitHub dependents, issue authors, package registry users",
            (4, 4, 5, 5, 5, 4),
        ),
        _customer(
            "Company needing a specialized implementation",
            "The open-source primitive does not complete its end-to-end workflow.",
            "Assign an internal engineer without deep project expertise.",
            "The maintainer can deliver the integration faster and with less technical risk.",
            "Implementation, integration, training, and a support retainer.",
            "Vague consulting without a scoped business outcome.",
            "A repeatable service package and one clearly defined target workflow.",
            "$5,000–$30,000/project", "Issue discussions, conferences, ecosystem partners",
            (4, 5, 3, 5, 4, 5),
        ),
        _customer(
            "Ecosystem vendor that benefits from adoption",
            "It needs credible integrations and educational examples for shared users.",
            "Build and maintain a one-off integration internally.",
            "A maintained integration expands both projects' reach.",
            "Sponsored integration, tutorial, benchmark, or co-marketing work.",
            "A donation without a concrete ecosystem outcome.",
            "Visible adoption, a shared audience, and a defined integration deliverable.",
            "$2,000–$15,000 sponsorship", "Adjacent vendors and foundations",
            (3, 4, 4, 4, 4, 3),
        ),
    ]


def analyze(evidence: RepositoryEvidence) -> SponsorFitAnalysis:
    archetype = classify(evidence)
    maturity, readiness = _maturity(evidence)

    if archetype == "document-processing":
        customers = _document_customers()
        values = [
            "Reduce manual document handling", "Improve downstream data and retrieval quality",
            "Process volume reliably", "Keep sensitive data under control", "Transfer operational risk",
        ]
        model = "Open-source parser + usage-based hosted API + enterprise self-hosting"
        reason = "The parsing primitive drives adoption; buyers pay when volume, reliability, security, and support become operational concerns."
        paid = ["Managed batch API", "Monitoring and retry workflows", "Enterprise deployment and SLA"]
        build = [
            ("1", "Public accuracy benchmark", "AI/RAG teams", "Trust", "Medium", "Makes quality claims measurable"),
            ("2", "Async batch API with retries", "AI/RAG teams", "Revenue", "Medium", "Packages the recurring operational job"),
            ("3", "Data-retention controls", "Regulated teams", "Enterprise", "Medium", "Removes a procurement blocker"),
            ("4", "Ten difficult-format examples", "All users", "Adoption", "Low", "Shows where the project wins"),
            ("5", "Error corpus contribution flow", "Community", "Community", "Low", "Turns edge cases into a moat"),
        ]
    elif archetype == "developer-tool":
        customers = _developer_customers()
        values = [
            "Standardize a developer workflow", "Save engineering time", "Reduce integration risk",
            "Create governance across teams", "Transfer maintenance responsibility",
        ]
        model = "Open-source local core + paid team workflow + enterprise controls"
        reason = "Individual developers create adoption, while teams pay for coordination, policy, integration guarantees, and support."
        paid = ["Shared team workflows", "Premium integrations and hosted coordination", "SSO, audit, policy, and SLA"]
        build = [
            ("1", "One production-grade integration", "Tool startups", "Revenue", "Medium", "Tests a concrete paid outcome"),
            ("2", "Five-minute quick start", "Individual developers", "Adoption", "Low", "Reduces time to first value"),
            ("3", "Compatibility and release policy", "Production teams", "Trust", "Low", "Makes dependency risk legible"),
            ("4", "Shared team configuration", "Engineering teams", "Enterprise", "Medium", "Creates a natural team boundary"),
            ("5", "Community recipe gallery", "Community", "Community", "Low", "Expands use cases without bloating core"),
        ]
    elif archetype == "small-utility":
        customers = _utility_customers()
        values = [
            "Remove a repetitive manual step", "Make batch work repeatable",
            "Reduce CI maintenance risk", "Package expert defaults into a command",
        ]
        model = "Free utility + fixed-scope implementation and support services"
        reason = "A small utility rarely supports SaaS economics initially; services and support validate who has recurring, costly usage."
        paid = ["Batch and workflow setup", "Commercial support", "Polished binary bundle if users request it"]
        build = [
            ("1", "Batch mode for one repeated workflow", "Agencies", "Revenue", "Low", "Converts convenience into measurable labor savings"),
            ("2", "Single-command install", "All users", "Adoption", "Low", "Maximizes trial"),
            ("3", "CI test matrix", "Engineering teams", "Trust", "Low", "Supports production adoption"),
            ("4", "Versioned support policy", "Teams", "Enterprise", "Low", "Makes support sellable"),
            ("5", "Preset contribution guide", "Power users", "Community", "Low", "Lets niches extend the tool"),
        ]
    else:
        customers = _library_customers()
        values = [
            "Avoid rebuilding a technical primitive", "Reduce dependency maintenance risk",
            "Accelerate specialized implementations", "Gain direct maintainer expertise",
        ]
        model = "Open-source library + support and implementation services"
        reason = "The repository evidence does not yet justify a hosted product; paid support and scoped implementation test demand with minimal product risk."
        paid = ["Priority support and LTS", "Fixed-scope implementation", "Sponsored ecosystem integrations"]
        build = [
            ("1", "Dependency/user discovery", "Production teams", "Revenue", "Low", "Finds buyers before building"),
            ("2", "Production quick start", "Evaluators", "Adoption", "Low", "Moves users toward real use"),
            ("3", "Release and support policy", "Production teams", "Trust", "Low", "Makes operational ownership explicit"),
            ("4", "Enterprise deployment guide", "Larger teams", "Enterprise", "Medium", "Surfaces enterprise blockers"),
            ("5", "Integration contribution template", "Partners", "Community", "Low", "Creates repeatable ecosystem growth"),
        ]

    stays_free = ["Core library/CLI and local use", "Essential documentation and examples", "Bug fixes and security fixes"]
    never_paywall = ["Security disclosures and patches", "Existing community functionality", "Basic interoperability and data export"]
    customers += _supplemental_customers(archetype)
    risks = [
        "Customer demand is inferred from repository evidence, not validated interviews.",
        "A paid layer introduced before repeat usage may distract from adoption.",
        "Pricing is a test range; revise it after five buyer conversations.",
    ]
    relative_scores = {"1": "84", "2": "78", "3": "72", "4": "68", "5": "64"}
    rows = [
        {
            "rank": rank, "feature": feature, "buyer": buyer, "type": kind,
            "effort": effort, "why": why, "opportunity_score": relative_scores[rank],
        }
        for rank, feature, buyer, kind, effort, why in build
    ]
    return SponsorFitAnalysis(
        archetype, maturity, readiness, values,
        sorted(customers, key=lambda item: item.total, reverse=True),
        model, reason, stays_free, paid, never_paywall, rows, risks,
    )
