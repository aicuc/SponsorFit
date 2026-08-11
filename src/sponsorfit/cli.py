from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .analysis import analyze
from .render import evidence_markdown, report_markdown
from .repository import prepared_repository, scan_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sponsorfit",
        description="Find who would happily pay for an open-source repository.",
    )
    parser.add_argument("source", nargs="?", default=".", help="Local repository path or Git URL")
    parser.add_argument("--github", action="store_true", help="Enrich with public GitHub metadata via gh")
    parser.add_argument("--format", choices=("markdown", "json", "evidence"), default="markdown")
    parser.add_argument("-o", "--output", type=Path, help="Write output to a file")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def run(args: argparse.Namespace) -> str:
    with prepared_repository(args.source) as root:
        evidence = scan_repository(root, include_github=args.github)
        analysis = analyze(evidence)
        if args.format == "json":
            return json.dumps(
                {"evidence": evidence.to_dict(), "analysis": analysis.to_dict()},
                indent=2, ensure_ascii=False, default=str,
            ) + "\n"
        if args.format == "evidence":
            return evidence_markdown(evidence)
        return report_markdown(evidence, analysis)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        print("Scanning repository evidence...", file=sys.stderr)
        output = run(args)
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(output, encoding="utf-8")
            print(f"SponsorFit report written to {args.output}")
        else:
            print(output, end="" if output.endswith("\n") else "\n")
        return 0
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"sponsorfit: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
