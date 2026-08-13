from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .analysis import analyze
from .models import MaintainerContext
from .render import evidence_markdown, interview_worksheet_markdown, report_markdown
from .repository import prepared_repository, scan_repository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sponsorfit",
        description="Find who would happily pay for an open-source repository.",
    )
    parser.add_argument("source", nargs="?", default=".", help="Local repository path or Git URL")
    parser.add_argument("--github", action="store_true", help="Enrich with public GitHub metadata via gh")
    parser.add_argument("--format", choices=("markdown", "json", "evidence", "worksheet"), default="markdown")
    parser.add_argument("-o", "--output", type=Path, help="Write output to a file")
    parser.add_argument("--context", type=Path, help="Load maintainer context from a JSON file")
    parser.add_argument("--constraint", action="append", default=[], help="Add a maintainer constraint (repeatable)")
    parser.add_argument("--audience-evidence", action="append", default=[], help="Add audience evidence (repeatable)")
    parser.add_argument("--interview-note", action="append", default=[], help="Add an interview note (repeatable)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return parser


def _maintainer_context(args: argparse.Namespace) -> MaintainerContext:
    data: dict[str, object] = {}
    if args.context:
        try:
            loaded = json.loads(args.context.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid context JSON: {exc.msg}") from exc
        if not isinstance(loaded, dict):
            raise ValueError("context must be a JSON object")
        data = loaded

    fields = {
        "constraints": args.constraint,
        "audience_evidence": args.audience_evidence,
        "interview_notes": args.interview_note,
    }
    merged: dict[str, list[str]] = {}
    for key, cli_values in fields.items():
        file_values = data.get(key, [])
        if not isinstance(file_values, list) or not all(isinstance(item, str) for item in file_values):
            raise ValueError(f"{key} must be a list of strings")
        merged[key] = [item.strip() for item in [*file_values, *cli_values] if item.strip()]
    return MaintainerContext(**merged)


def run(args: argparse.Namespace) -> str:
    context = _maintainer_context(args)
    with prepared_repository(args.source) as root:
        evidence = scan_repository(root, include_github=args.github)
        analysis = analyze(evidence)
        if args.format == "json":
            return json.dumps(
                {"evidence": evidence.to_dict(), "context": context.to_dict(), "analysis": analysis.to_dict()},
                indent=2, ensure_ascii=False, default=str,
            ) + "\n"
        if args.format == "evidence":
            return evidence_markdown(evidence, context)
        if args.format == "worksheet":
            return interview_worksheet_markdown(evidence, analysis, context)
        return report_markdown(evidence, analysis, context)


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
