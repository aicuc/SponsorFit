# SponsorFit Roadmap Completion Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete and verify all five unchecked CLI roadmap capabilities.

**Architecture:** Extend the bounded evidence model with relative source paths and optional maintainer context. Keep GitHub enrichment best-effort, use deterministic issue-theme analysis and clearly labeled code-search dependent candidates, then expose the new data through Markdown, JSON, and worksheet renderers.

**Tech Stack:** Python 3.10 standard library, `unittest`, optional GitHub CLI, Markdown.

---

### Task 1: Source-cited repository observations

**Files:**
- Modify: `src/sponsorfit/models.py`
- Modify: `src/sponsorfit/repository.py`
- Modify: `src/sponsorfit/render.py`
- Test: `tests/test_repository.py`
- Test: `tests/test_cli.py`

1. Add failing tests asserting the evidence ledger uses repository-relative paths and rendered observed claims cite them.
2. Run `python3 -m unittest tests.test_repository tests.test_cli -v`; expect failures for missing sources.
3. Add bounded `sources` collection during scanning and citation helpers in both Markdown renderers.
4. Re-run the focused tests; expect PASS.

### Task 2: Deeper GitHub signals

**Files:**
- Modify: `src/sponsorfit/repository.py`
- Modify: `src/sponsorfit/render.py`
- Test: `tests/test_repository.py`

1. Add failing pure-function tests for recurring issue themes and mocked `gh search code` dependent candidates.
2. Run the repository tests; expect failures for missing helpers and enrichment keys.
3. Implement deterministic theme grouping, increase bounded issue coverage, and gather/deduplicate code-search candidates while excluding the source repository.
4. Render both signals with explicit candidate/hypothesis language and re-run tests.

### Task 3: Maintainer-supplied context

**Files:**
- Modify: `src/sponsorfit/models.py`
- Modify: `src/sponsorfit/cli.py`
- Modify: `src/sponsorfit/render.py`
- Test: `tests/test_cli.py`

1. Add tests for JSON loading, repeated-flag merging, invalid context, Markdown output, and JSON serialization.
2. Run CLI tests; expect argument/model failures.
3. Implement `MaintainerContext`, parser flags, strict JSON validation, merging, and labeled rendering.
4. Run CLI tests; expect PASS.

### Task 4: Customer interview worksheet

**Files:**
- Modify: `src/sponsorfit/cli.py`
- Modify: `src/sponsorfit/render.py`
- Test: `tests/test_cli.py`

1. Add a failing test for `--format worksheet` and its reusable discovery fields.
2. Implement a pre-filled, hypothesis-labeled Markdown worksheet.
3. Run CLI tests; expect PASS.

### Task 5: Archetype benchmark fixtures and documentation

**Files:**
- Create: `tests/fixtures/archetype-benchmarks.json`
- Create: `tests/test_benchmarks.py`
- Modify: `README.md`
- Modify: `web/app/page.tsx` if the web Roadmap is rendered there.

1. Add data-driven fixtures for document processing, developer tools, small utilities, and general libraries.
2. Add a benchmark test asserting classification, customer, and model expectations.
3. Run the full Python and web test suites.
4. Check all five Roadmap items only after every related test passes.

### Task 6: Final verification

1. Run `python3 -m unittest discover -s tests -v`.
2. Run `npm test` and `npm run lint` in `web`.
3. Run representative CLI Markdown, JSON, evidence, and worksheet commands against this repository.
4. Inspect `git diff --check` and the final diff for unrelated changes.
