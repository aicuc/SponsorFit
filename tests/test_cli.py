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


if __name__ == "__main__":
    unittest.main()
