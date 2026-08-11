#!/usr/bin/env python3
"""Emit a bounded SponsorFit evidence bundle from a repository."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from sponsorfit.render import evidence_markdown  # noqa: E402
from sponsorfit.repository import prepared_repository, scan_repository  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", nargs="?", default=".")
    parser.add_argument("--github", action="store_true")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    args = parser.parse_args()
    try:
        with prepared_repository(args.source) as root:
            evidence = scan_repository(root, include_github=args.github)
            if args.format == "json":
                print(json.dumps(evidence.to_dict(), indent=2, ensure_ascii=False, default=str))
            else:
                print(evidence_markdown(evidence))
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"scan_repository.py: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

