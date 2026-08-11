# SponsorFit MVP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a publishable Codex Skill and lightweight Python CLI that turns repository evidence into buyer, monetization, and first-revenue guidance.

**Architecture:** Keep judgment in the Codex workflow and deterministic collection in a zero-runtime-dependency Python package. The scanner emits a compact evidence bundle from local files and optional GitHub CLI metadata; the skill turns that evidence into a rigorously labeled SponsorFit Report. The CLI also produces a useful offline heuristic report so it works without an AI API.

**Tech Stack:** Python 3.10+, standard library, `unittest`, Codex Skill Markdown, optional `git` and `gh` CLIs.

---

### Task 1: Initialize and define the skill

**Files:**
- Create: `SKILL.md`
- Create: `agents/openai.yaml`
- Create: `references/scoring.md`
- Create: `references/report-template.md`

1. Run the official `init_skill.py` initializer in a temporary directory.
2. Write the evidence-first workflow and progressive-disclosure links.
3. Define transparent customer and opportunity scoring.
4. Validate the skill metadata.

### Task 2: Build repository evidence collection

**Files:**
- Create: `src/sponsorfit/repository.py`
- Create: `src/sponsorfit/models.py`
- Create: `scripts/scan_repository.py`
- Test: `tests/test_repository.py`

1. Write tests for file discovery, metadata extraction, secret exclusion, and truncation.
2. Implement local repository inspection and optional `gh` enrichment.
3. Add URL cloning with automatic temporary cleanup.
4. Run targeted tests.

### Task 3: Build the offline analysis and CLI

**Files:**
- Create: `src/sponsorfit/analysis.py`
- Create: `src/sponsorfit/render.py`
- Create: `src/sponsorfit/cli.py`
- Create: `pyproject.toml`
- Test: `tests/test_analysis.py`
- Test: `tests/test_cli.py`

1. Write tests for archetype-specific customer recommendations and scoring.
2. Implement evidence-labeled heuristic analysis.
3. Render terminal and Markdown outputs, including the share card.
4. Expose `sponsorfit PATH_OR_URL` and verify exit behavior.

### Task 4: Add publishable project materials

**Files:**
- Create: `README.md`
- Create: `LICENSE`
- Create: `CONTRIBUTING.md`
- Create: `examples/pdf-ocr-report.md`
- Create: `examples/agent-tool-report.md`
- Create: `examples/small-utility-report.md`
- Create: `.github/ISSUE_TEMPLATE/bug_report.yml`
- Create: `.github/ISSUE_TEMPLATE/feature_request.yml`
- Create: `assets/sponsorfit.svg`

1. Lead README with a concrete demo and five-minute quick start.
2. Document CLI and Codex Skill installation.
3. Provide three materially different example reports.
4. Add a concise roadmap, contribution path, license, and issue templates.

### Task 5: Verify the release candidate

1. Run `python -m unittest discover -s tests -v`.
2. Install the package into a temporary virtual environment and run `sponsorfit .`.
3. Run the repository scanner in JSON and Markdown modes.
4. Run `quick_validate.py` on the project root.
5. Inspect `git diff --check` and the final file tree; fix all failures.
