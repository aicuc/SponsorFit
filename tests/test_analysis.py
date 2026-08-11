from __future__ import annotations

import unittest
from pathlib import Path

from sponsorfit.analysis import analyze, classify
from sponsorfit.models import RepositoryEvidence


def evidence(description: str, files: int = 100) -> RepositoryEvidence:
    return RepositoryEvidence(
        name="demo", root=Path("/tmp/demo"), description=description,
        files_count=files, manifests={"pyproject.toml": {"name": "demo"}},
        has_tests=True, has_ci=True, license_name="MIT",
    )


class AnalysisTests(unittest.TestCase):
    def test_document_project_gets_document_specific_buyers(self) -> None:
        result = analyze(evidence("OCR and PDF extraction for RAG"))
        self.assertEqual(result.archetype, "document-processing")
        self.assertIn("RAG", result.customers[0].customer_type)
        self.assertIn("hosted API", result.model)

    def test_developer_tool_does_not_reuse_document_answers(self) -> None:
        result = analyze(evidence("A CLI developer tool for deployment automation"))
        self.assertEqual(result.archetype, "developer-tool")
        self.assertIn("team", result.model.lower())
        self.assertNotIn("OCR", " ".join(item.customer_type for item in result.customers))

    def test_small_unknown_repo_is_classified_as_utility(self) -> None:
        item = evidence("Renames files using a predictable convention", files=12)
        self.assertEqual(classify(item), "small-utility")
        result = analyze(item)
        self.assertIn("services", result.model)

    def test_scores_are_bounded_and_ranked(self) -> None:
        result = analyze(evidence("A reusable data processing library"))
        totals = [item.total for item in result.customers]
        self.assertEqual(totals, sorted(totals, reverse=True))
        self.assertTrue(all(0 <= total <= 100 for total in totals))

    def test_every_archetype_has_at_least_five_customer_hypotheses(self) -> None:
        descriptions = [
            "OCR and PDF extraction for RAG",
            "A CLI developer tool for deployment automation",
            "A reusable data processing library",
        ]
        for description in descriptions:
            with self.subTest(description=description):
                self.assertGreaterEqual(len(analyze(evidence(description)).customers), 5)

    def test_examples_later_in_readme_do_not_override_project_description(self) -> None:
        item = evidence("A CLI that analyzes open-source business opportunities")
        item.readme_excerpt = "A CLI for maintainers.\n" + ("x" * 1600) + "\nPDF OCR example"
        self.assertEqual(classify(item), "developer-tool")


if __name__ == "__main__":
    unittest.main()
