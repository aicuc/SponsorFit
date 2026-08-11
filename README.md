<p align="center">
  <img src="assets/sponsorfit.svg" alt="SponsorFit" width="560">
</p>

<h1 align="center">SponsorFit 💸</h1>

<p align="center"><strong>Turn any open-source repo into a sustainable business.</strong></p>
<p align="center">Find the people who would happily pay for what you already love building.</p>

SponsorFit reads a repository, identifies the value behind the code, simulates the buyers with the strongest reason to pay, and turns those hypotheses into a concrete validation plan. It is both a Codex Skill for deep analysis and a zero-dependency Python CLI for a fast offline first pass.

```console
$ sponsorfit .

Scanning repository evidence...

YOUR BEST CUSTOMER:
AI infrastructure startups building document RAG

THEY PAY FOR:
Hosted batch API, difficult-format support, monitoring, and an SLA

BEST BUSINESS MODEL:
Open-source parser + usage-based hosted API + enterprise self-hosting

BUILD THIS NEXT:
Public accuracy benchmark

FIRST REVENUE MOVE:
Find 10 prospects via GitHub dependents and sell a narrow paid pilot.
```

> SponsorFit does not hallucinate a market. It separates what the repository proves from what a maintainer still needs to validate.

## Why SponsorFit

Most monetization advice starts with a menu: SaaS, subscriptions, consulting, enterprise. SponsorFit starts somewhere more useful:

> Who wants this badly enough to pay—and what costly job are they hiring the project to do?

It produces:

- a repository-grounded project snapshot;
- the outcomes users actually buy, not a feature summary;
- ranked customer hypotheses with transparent scoring;
- first-person **Happiest Sponsor** simulations;
- an open-source-friendly free/paid boundary;
- a first $100 / $1,000 / $10,000 revenue ladder;
- the next Revenue, Adoption, Trust, Enterprise, and Community work to prioritize.

Every material claim is labeled:

- **Observed** — directly visible in the repository or GitHub data;
- **Inferred** — reasoned from observed evidence;
- **Hypothesis** — must be tested with real buyers.

## How it works

```text
Repository + optional public GitHub signals
                    ↓
           Bounded evidence bundle
                    ↓
       Value and customer hypotheses
                    ↓
         Happiest Sponsor ranking
                    ↓
 Open-source-friendly offer + next actions
```

The scanner reads README files, manifests, languages, license, tests, docs, examples, changelog, and maturity signals. With `--github`, it can use an authenticated `gh` CLI to add public repository, issue, pull request, and release metadata. Secrets, dependency directories, and build outputs are excluded.

## Five-minute quick start

Requirements: Python 3.10+ and, only for URL input, `git`.

```bash
git clone <repository-url> sponsorfit
cd sponsorfit
python3 -m pip install .
sponsorfit /path/to/your/repository
```

No API key and no runtime Python dependencies are required.

Analyze a GitHub URL without keeping a clone:

```bash
sponsorfit https://github.com/owner/repo
```

Save a report or obtain machine-readable evidence:

```bash
sponsorfit . -o sponsorfit-report.md
sponsorfit . --format evidence
sponsorfit . --format json > sponsorfit.json
sponsorfit . --github
```

The CLI deliberately uses conservative heuristics. For context-aware reasoning, buyer simulation, and tailored validation strategy, use the Codex Skill.

## Install as a Codex Skill

Clone this project into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
git clone <repository-url> ~/.codex/skills/sponsorfit
```

Restart Codex if needed, open the repository you want to analyze, and ask:

```text
Use $sponsorfit to find this project's happiest sponsors and its fastest path to the first $1,000.
```

You can also keep the project elsewhere and symlink it:

```bash
ln -s /absolute/path/to/sponsorfit ~/.codex/skills/sponsorfit
```

## Example reports

SponsorFit should not give every project the same business model:

| Repository type | Happiest sponsor | Recommended first offer |
| --- | --- | --- |
| [PDF / OCR](examples/pdf-ocr-report.md) | RAG infrastructure startup | Paid ingestion-quality pilot, then hosted batch API |
| [AI agent developer tool](examples/agent-tool-report.md) | Dev-tool startup embedding it | Stable integration + support agreement |
| [Small GitHub utility](examples/small-utility-report.md) | Agency repeating the workflow | Fixed-scope batch automation service |

## The SponsorFit philosophy

1. **Evidence first.** Repository facts before business storytelling.
2. **Demand is earned, not generated.** A plausible persona is still only a hypothesis.
3. **Open source is the growth engine.** The useful core, docs, interoperability, and security fixes stay open.
4. **Operational value gets paid.** Reliability, volume, coordination, governance, and accountable support are natural paid boundaries.
5. **Talk before building.** The best next feature is often a buyer conversation or benchmark.

## Development

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
python3 scripts/scan_repository.py . --format markdown
```

The project intentionally uses the Python standard library. See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## Roadmap

- [x] Offline local repository analysis
- [x] Git URL support and optional `gh` enrichment
- [x] Evidence labeling, customer scoring, revenue ladder, and share card
- [x] Codex Skill and deterministic CLI companion
- [ ] Quote repository paths beside every observation in CLI reports
- [ ] Detect GitHub dependents and recurring issue themes more deeply
- [ ] Let maintainers supply constraints, audience evidence, and interview notes
- [ ] Export a reusable customer-interview worksheet
- [ ] Add benchmark fixtures for more repository archetypes

The roadmap follows user evidence. Open an issue describing the repository, the output that was wrong, and what a real buyer told you.

## Contributing

Bug reports, new repository archetypes, scoring critiques, and anonymized validation results are welcome. The most useful contribution is a small fixture where SponsorFit made a concrete bad recommendation and a test for the improved behavior.

## License

[MIT](LICENSE) © 2026 SponsorFit contributors.

