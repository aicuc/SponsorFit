# Contributing to SponsorFit

SponsorFit improves when recommendations become more specific, more honest about evidence, and easier to test with real buyers.

## Good first contributions

- Add a small repository fixture that exposes a bad classification.
- Add a test before changing a heuristic.
- Improve a customer archetype with evidence from anonymized interviews.
- Tighten secret exclusion or bounded repository scanning.
- Clarify the five-minute installation path.

## Local workflow

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
python3 -m unittest discover -s tests -v
python3 scripts/scan_repository.py . --format json
```

Keep runtime dependencies at zero unless a dependency produces a clear user benefit that cannot be achieved safely with the standard library. Keep pull requests focused, add tests for behavioral changes, and never commit repository content collected from private projects.

## Improving commercial recommendations

Distinguish repository evidence from market evidence. Do not encode an anecdote as a universal rule. A useful issue or pull request includes:

1. the repository archetype;
2. the recommendation SponsorFit made;
3. why it was wrong or generic;
4. the buyer evidence that contradicted it;
5. a proposed fixture or test.

By contributing, you agree that your contribution is licensed under the MIT License.

