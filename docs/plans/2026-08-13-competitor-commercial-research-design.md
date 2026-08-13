# Competitor Commercial Research Design

## Goal

Extend SponsorFit from repository-only buyer hypotheses into commercial research for either a GitHub project or a product idea. Make the default outcome a supported answer to: who buys, how comparable products close, what they charge, what public financial evidence exists, and which monetization path should be tested first.

## Design

Keep one skill with two input paths. Repository inputs use the existing scanner and evidence ledger. Idea inputs create a compact assumption ledger covering the job, intended user, outcome, delivery form, and constraints. Both paths then find direct competitors, indirect substitutes, and commercial analogs before producing customer and monetization recommendations.

Separate detailed web-research instructions into `references/commercial-research.md`. Require source hierarchy, dated evidence, sales-funnel reconstruction, customer-evidence limits, and strict separation of revenue, funding, profitability, and valuation. Keep the main `SKILL.md` focused on orchestration.

Expand the report around competitor dossiers and a cross-competitor commercial comparison. Rank several monetization paths instead of jumping to one generic SaaS answer. Each path must identify a buyer, offer, paid unit, acquisition channel, sales motion, price hypothesis, operating burden, commercial analog, and fast falsification test.

## Failure handling and validation

When prices or financial results are private, report that no reliable public evidence was found and use observable CTAs or packaging only for labeled inference. Never turn funding, stars, customer logos, or search snippets into profitability claims. Validate the skill structure with `quick_validate.py`, check the interface metadata, and inspect the diff for accidental changes outside the skill resources.
