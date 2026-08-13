from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

from sponsorfit.cli import main


class CliTests(unittest.TestCase):
    def test_markdown_report_contains_share_card(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "# AgentKit\n\nA developer tool for building reliable AI agents.\n",
                encoding="utf-8",
            )
            output = StringIO()
            with redirect_stdout(output):
                code = main([str(root)])
            self.assertEqual(code, 0)
            self.assertIn("Your Happiest Sponsor Is", output.getvalue())
            self.assertIn("YOUR BEST CUSTOMER:", output.getvalue())
            self.assertIn("Observed", output.getvalue())
            self.assertIn("Candidate #5", output.getvalue())
            self.assertIn("Opportunity / 100", output.getvalue())
            self.assertIn("Source: `README.md`", output.getvalue())

    def test_json_output_is_machine_readable(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Small tool\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                code = main([str(root), "--format", "json"])
            payload = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertIn("analysis", payload)
            self.assertIn("evidence", payload)

    def test_bad_path_returns_clear_error(self) -> None:
        error = StringIO()
        with redirect_stderr(error):
            code = main(["/definitely/not/a/repository"])
        self.assertEqual(code, 2)
        self.assertIn("not a directory", error.getvalue())

    def test_context_file_and_repeatable_flags_are_merged(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "# AgentKit\n\nA developer CLI for reliable deployments.\n",
                encoding="utf-8",
            )
            context = root / "context.json"
            context.write_text(json.dumps({
                "constraints": ["Keep local use free"],
                "audience_evidence": ["Three agencies use batch mode"],
                "interview_notes": ["Upgrades cause monthly incidents"],
            }), encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                code = main([
                    str(root), "--context", str(context),
                    "--constraint", "No hosted customer data",
                    "--audience-evidence", "One team requested SSO",
                    "--interview-note", "Budget owner is platform lead",
                ])

            self.assertEqual(code, 0)
            report = output.getvalue()
            self.assertIn("Maintainer-provided context", report)
            self.assertIn("Keep local use free", report)
            self.assertIn("No hosted customer data", report)
            self.assertIn("One team requested SSO", report)
            self.assertIn("Budget owner is platform lead", report)

    def test_json_output_includes_maintainer_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Tool\n", encoding="utf-8")
            output = StringIO()
            with redirect_stdout(output):
                code = main([str(root), "--format", "json", "--constraint", "Stay offline"])
            payload = json.loads(output.getvalue())
            self.assertEqual(code, 0)
            self.assertEqual(payload["context"]["constraints"], ["Stay offline"])

    def test_invalid_context_returns_clear_error(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Tool\n", encoding="utf-8")
            context = root / "context.json"
            context.write_text('{"constraints": "not-a-list"}', encoding="utf-8")
            error = StringIO()
            with redirect_stderr(error):
                code = main([str(root), "--context", str(context)])
            self.assertEqual(code, 2)
            self.assertIn("constraints must be a list of strings", error.getvalue())

    def test_exports_reusable_interview_worksheet(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "# AgentKit\n\nA developer CLI for reliable deployments.\n",
                encoding="utf-8",
            )
            output = StringIO()
            with redirect_stdout(output):
                code = main([str(root), "--format", "worksheet"])

            worksheet = output.getvalue()
            self.assertEqual(code, 0)
            self.assertIn("Customer Interview Worksheet", worksheet)
            self.assertIn("Current workaround", worksheet)
            self.assertIn("Frequency and cost", worksheet)
            self.assertIn("Evidence after the call", worksheet)


if __name__ == "__main__":
    unittest.main()
