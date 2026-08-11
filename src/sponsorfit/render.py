from __future__ import annotations

import json
from typing import Any

from .models import RepositoryEvidence, SponsorFitAnalysis


def evidence_markdown(evidence: RepositoryEvidence) -> str:
    languages = ", ".join(evidence.languages) or "Not detected"
    github = evidence.github
    github_line = github.get("reason", github.get("status", "unknown"))
    if github.get("status") == "available":
        github_line = f"{github.get('stargazerCount', 0)} stars, {github.get('forkCount', 0)} forks"
    return f"""# SponsorFit Evidence Bundle

## Repository

- Name: {evidence.name}
- Description: {evidence.description or 'Not found'}
- Languages: {languages}
- License: {evidence.license_name}
- Files scanned: {evidence.files_count}
- Tests / CI / docs / examples / changelog: {evidence.has_tests} / {evidence.has_ci} / {evidence.has_docs} / {evidence.has_examples} / {evidence.has_changelog}
- Detected signals: {', '.join(evidence.signals) or 'None'}
- GitHub enrichment: {github_line}

## Manifests

```json
{json.dumps(evidence.manifests, indent=2, ensure_ascii=False, default=str)}
```

## README excerpt

{evidence.readme_excerpt or '_No README content found._'}
"""


def _table(rows: list[list[Any]], headers: list[str]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value).replace("|", "\\|") for value in row) + " |")
    return "\n".join(lines)


def report_markdown(evidence: RepositoryEvidence, analysis: SponsorFitAnalysis) -> str:
    top = analysis.customers[0]
    customer_rows = [
        [index, item.customer_type, item.pain_point, item.budget, item.total]
        for index, item in enumerate(analysis.customers, 1)
    ]
    sponsor_sections = []
    candidate_details = []
    medals = ["🥇", "🥈", "🥉"]
    for index, item in enumerate(analysis.customers, 1):
        urgency = "High" if item.scores["pain"] >= 16 else "Medium" if item.scores["pain"] >= 12 else "Low"
        willingness = "High" if item.scores["willingness_to_pay"] >= 16 else "Medium" if item.scores["willingness_to_pay"] >= 12 else "Low"
        accessibility = "High" if item.scores["ease_of_reaching"] >= 12 else "Medium" if item.scores["ease_of_reaching"] >= 9 else "Low"
        candidate_details.append(f"""### Candidate #{index}: {item.customer_type}

- **Current workaround:** {item.workaround}
- **Why the project matters:** {item.why_it_matters}
- **Hypothesis — willingness to pay:** {willingness}; {item.budget}
- **Hypothesis — urgency:** {urgency}
- **Hypothesis — market accessibility:** {accessibility}; {item.reach}
- **Required before payment:** {item.required_features}
""")
    for index, item in enumerate(analysis.customers[:3]):
        sponsor_sections.append(f"""## {medals[index]} Happiest Sponsor #{index + 1}

**Role:** {item.customer_type}

**What I am trying to do:** I need to solve this problem: {item.pain_point}

**Why I care about your project:** {item.why_it_matters}

**What I would happily pay for:** {item.pay_for}

**What I would NOT pay for:** {item.not_pay_for}

**What you need to build before I pay:** {item.required_features}

**How much I might pay:** {item.budget}

**Where you can find people like me:** {item.reach}
""")
    build_rows = [
        [row["rank"], row["feature"], row["buyer"], row["type"], row["opportunity_score"], row["effort"], row["why"]]
        for row in analysis.build_next
    ]
    values = "\n".join(f"- {value}" for value in analysis.values)
    free = "\n".join(f"- {value}" for value in analysis.stays_free)
    paid = "\n".join(f"- {value}" for value in analysis.paid)
    never = "\n".join(f"- {value}" for value in analysis.never_paywall)
    risks = "\n".join(f"- {risk}" for risk in analysis.risks)
    first_channel = top.reach.split(",")[0]
    first_offer = top.pay_for.split(",")[0]
    outreach = (
        f"Hi — I maintain {evidence.name}, an open-source project for "
        f"{evidence.description or 'this workflow'}. I’m speaking with a few {top.customer_type.lower()} teams "
        f"that struggle with {top.pain_point.lower()} I’m not selling software yet; could I ask how you handle it today "
        "and show you a small prototype? Twenty minutes, and I’ll share what I learn."
    )
    seven_days = [
        "List 20 reachable people matching the top customer profile.",
        "Send 10 problem-interview messages; do not pitch features.",
        "Run two interviews and record current workaround, frequency, and cost.",
        "Publish one evidence-backed use case or benchmark.",
        f"Offer a manual pilot of {first_offer.lower()}.",
        "Ask for a paid commitment or explicit reason for declining.",
        "Keep, change, or kill the hypothesis based on repeated evidence.",
    ]
    return f"""# SponsorFit Report: {evidence.name}

> This offline MVP labels repository facts as **Observed**, reasoned conclusions as **Inferred**, and unvalidated demand as **Hypothesis**.

## 1. Project Snapshot

- **Observed — What it does:** {evidence.description or 'No clear description was found; improve the README before commercial outreach.'}
- **Observed — Technical footprint:** {', '.join(evidence.languages) or 'Unknown'}; {evidence.files_count} files scanned; {evidence.license_name} license.
- **Inferred — Primary category:** {analysis.archetype}
- **Inferred — Current maturity:** {analysis.maturity}
- **Inferred — Monetization readiness:** {analysis.monetization_readiness}

## 2. What This Project Really Sells

**Inferred:**

{values}

## 3. Ideal Customer Ranking

**Hypothesis — compare opportunities; do not treat scores as market facts.**

{_table(customer_rows, ['Rank', 'Customer', 'Pain', 'Expected budget', 'Score / 100'])}

Scoring weights: pain 20, willingness to pay 20, ease of reaching 15, strategic fit 15, product fit 15, revenue potential 15.

### Candidate details

{chr(10).join(candidate_details)}

## 4. Your Happiest Sponsors

{chr(10).join(sponsor_sections)}
# Your Happiest Sponsor Is…

**{top.customer_type}** — it combines the strongest problem urgency, product fit, and plausible budget in this repository-only analysis. Validate this with conversations before building.

## 5. Best Monetization Model

**{analysis.model}**

{analysis.model_reason}

### What should stay free

{free}

### What could be paid

{paid}

### What should never be paywalled

{never}

## 6. Monetization Architecture

```text
Free open-source core
        ↓ adoption and trust
Professional / hosted layer
        ↓ operational value
Enterprise layer: governance, deployment, support
```

## 7. Pricing Hypothesis

- First pilot: price a narrow outcome, not feature access.
- Starting range for the top customer: **{top.budget}**.
- Validate by asking for a paid pilot; compliments and waitlists are weak evidence.

## 8. How to Make the First $1,000

1. **Customer:** Contact {top.customer_type.lower()} teams already using adjacent tools.
2. **Where:** Start with {first_channel}; use repository dependents or issue participants when available.
3. **Offer:** Sell a manually delivered pilot around {first_offer.lower()}.
4. **Price:** Seek 2 × $500 or 1 × $1,000, with a clear outcome and two-week scope.
5. **Outreach message:**

   > {outreach}

6. **Validate before building:** Confirm the problem occurs at least monthly, has an owner, has a costly workaround, and can access budget.

### Revenue ladder

- **First $100:** Charge for one manual setup, audit, or workflow improvement. Learn why the buyer pays.
- **First $1,000:** Repeat the same scoped outcome with two customers; write down the common delivery steps.
- **First $10,000:** Productize only the repeated steps and sell an annual support, hosted, or team offer.

## 9. Top Things to Build Next

{_table(build_rows, ['Rank', 'Feature', 'Buyer', 'Type', 'Opportunity / 100', 'Effort', 'Why'])}

Opportunity scores are relative repository-only hypotheses using buyer pain, revenue evidence, reachability, technical fit, competitive advantage, and reverse-scored effort. Validate before committing roadmap capacity.

## 10. Risks

{risks}

## 11. 7-Day Action Plan

{chr(10).join(f'{index}. {item}' for index, item in enumerate(seven_days, 1))}

---

```text
YOUR BEST CUSTOMER:
{top.customer_type}

THEY PAY FOR:
{top.pay_for}

BEST BUSINESS MODEL:
{analysis.model}

BUILD THIS NEXT:
{analysis.build_next[0]['feature']}

FIRST REVENUE MOVE:
Find 10 prospects via {first_channel} and sell a narrow paid pilot.
```
"""
