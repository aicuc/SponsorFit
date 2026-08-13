# Roadmap Completion Design

## Scope and compatibility

Complete the five unchecked CLI roadmap items without changing existing command behavior. Repository observations gain explicit relative-path citations. Optional maintainer context is accepted through repeatable flags and a reusable JSON file, merged in that order and included in Markdown and JSON output. A new `worksheet` format exports a reusable interview guide. GitHub enrichment remains optional and failure-tolerant.

## Evidence and GitHub data flow

`scan_repository` records a bounded `sources` ledger alongside the existing evidence fields. Renderers cite those paths next to observed statements, without exposing absolute paths or reading excluded files. GitHub issue titles and labels are grouped with deterministic keyword rules; recurring themes require at least two matching issues. Because GitHub has no supported API that directly lists every dependent repository, SponsorFit uses authenticated `gh search code` results as conservative dependent candidates, excludes the analyzed repository, deduplicates results, and labels the output as candidates.

## Maintainer context and worksheet

A `MaintainerContext` model holds constraints, audience evidence, and interview notes. `--context` accepts a JSON object containing arrays for those fields; `--constraint`, `--audience-evidence`, and `--interview-note` can be repeated and are appended. Invalid shapes fail with a clear CLI error. Reports distinguish maintainer-provided statements from observed repository facts. The worksheet pre-fills the leading customer hypothesis and project details but leaves evidence, frequency, cost, authority, and follow-up fields blank for reuse.

## Testing and completion criteria

Unit tests cover source ledgers, issue-theme grouping, dependent-candidate command parsing, context merge and validation, worksheet export, and Markdown/JSON rendering. A data-driven benchmark fixture exercises multiple repository archetypes and expected commercial recommendations. Existing Python and web tests must remain green. A roadmap item is checked only after its implementation and tests pass.
