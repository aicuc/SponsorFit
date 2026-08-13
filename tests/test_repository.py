from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from sponsorfit.repository import (
    _find_dependent_candidates,
    _issue_themes,
    _read_pyproject_fallback,
    scan_repository,
)


class RepositoryScanTests(unittest.TestCase):
    def test_python_310_fallback_reads_basic_pyproject_metadata(self) -> None:
        metadata = _read_pyproject_fallback(
            """
            [build-system]
            requires = ["setuptools"]

            [project]
            name = "clearpdf"
            version = '1.2.3'
            description = "Parse PDF files"
            dependencies = ["example"]
            """
        )

        self.assertEqual(
            metadata,
            {
                "name": "clearpdf",
                "version": "1.2.3",
                "description": "Parse PDF files",
            },
        )

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
            self.assertEqual(evidence.sources["description"], ["README.md"])
            self.assertIn("src/main.py", evidence.sources["languages"])
            self.assertEqual(evidence.sources["tests"], ["tests/"])

    def test_groups_only_recurring_issue_themes(self) -> None:
        themes = _issue_themes([
            {"title": "Install fails on Windows", "labels": [{"name": "bug"}]},
            {"title": "Windows installation path is broken", "labels": [{"name": "bug"}]},
            {"title": "Add dark mode", "labels": [{"name": "enhancement"}]},
        ])

        self.assertEqual(themes[0]["theme"], "installation")
        self.assertEqual(themes[0]["count"], 2)
        self.assertNotIn("dark mode", json.dumps(themes).lower())

    @patch("sponsorfit.repository.subprocess.run")
    def test_code_search_returns_deduplicated_dependent_candidates(self, run) -> None:
        run.return_value.stdout = json.dumps([
            {
                "path": "pyproject.toml",
                "repository": {"nameWithOwner": "buyer/app"},
                "url": "https://github.com/buyer/app/blob/main/pyproject.toml",
            },
            {
                "path": "requirements.txt",
                "repository": {"nameWithOwner": "buyer/app"},
                "url": "https://github.com/buyer/app/blob/main/requirements.txt",
            },
            {
                "path": "pyproject.toml",
                "repository": {"nameWithOwner": "owner/tool"},
                "url": "https://github.com/owner/tool/blob/main/pyproject.toml",
            },
        ])

        candidates = _find_dependent_candidates("owner/tool", ["tool"])

        self.assertEqual([item["repository"] for item in candidates], ["buyer/app"])
        self.assertEqual(candidates[0]["matched_package"], "tool")

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
