from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from sponsorfit.repository import scan_repository


class RepositoryScanTests(unittest.TestCase):
    def test_extracts_project_evidence_and_ignores_secrets_and_dependencies(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text(
                "# ClearPDF\n\nA reliable PDF and OCR parser for RAG pipelines.\n",
                encoding="utf-8",
            )
            (root / "pyproject.toml").write_text(
                '[project]\nname="clearpdf"\ndescription="Parse PDF files"\n',
                encoding="utf-8",
            )
            (root / "src").mkdir()
            (root / "src" / "main.py").write_text("print('ok')\n", encoding="utf-8")
            (root / "tests").mkdir()
            (root / "tests" / "test_main.py").write_text("def test_ok(): pass\n", encoding="utf-8")
            (root / ".env").write_text("TOKEN=do-not-read\n", encoding="utf-8")
            (root / "node_modules").mkdir()
            (root / "node_modules" / "noise.js").write_text("x" * 1000, encoding="utf-8")

            evidence = scan_repository(root)

            self.assertEqual(evidence.description, "A reliable PDF and OCR parser for RAG pipelines.")
            self.assertIn("PDF/OCR", evidence.signals)
            self.assertTrue(evidence.has_tests)
            self.assertIn("Python", evidence.languages)
            self.assertNotIn("JavaScript", evidence.languages)
            self.assertNotIn("do-not-read", json.dumps(evidence.to_dict()))

    def test_reports_unknown_license_without_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "README.md").write_text("# Tool\n", encoding="utf-8")
            evidence = scan_repository(root)
            self.assertEqual(evidence.license_name, "Unknown")
            self.assertEqual(evidence.github["status"], "not_requested")

    def test_does_not_follow_file_symlinks_outside_repository(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            secret = Path(outside) / "notes.txt"
            secret.write_text("private-outside-content", encoding="utf-8")
            try:
                (root / "README.md").symlink_to(secret)
            except OSError:
                self.skipTest("symlinks are unavailable on this platform")
            evidence = scan_repository(root)
            self.assertNotIn("private-outside-content", json.dumps(evidence.to_dict()))


if __name__ == "__main__":
    unittest.main()
