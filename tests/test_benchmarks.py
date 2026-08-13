from __future__ import annotations

import json
import unittest
from pathlib import Path

from sponsorfit.analysis import analyze
from sponsorfit.models import RepositoryEvidence


FIXTURES = Path(__file__).parent / "fixtures" / "archetype-benchmarks.json"


class ArchetypeBenchmarkTests(unittest.TestCase):
    def test_archetype_recommendations_match_benchmark_fixtures(self) -> None:
        cases = json.loads(FIXTURES.read_text(encoding="utf-8"))

        for case in cases:
            with self.subTest(case=case["name"]):
                evidence = RepositoryEvidence(
                    name=case["name"],
                    root=Path("/benchmark") / case["name"],
                    description=case["description"],
                    files_count=case["files_count"],
                    manifests={"manifest": {"name": case["name"]}},
                    has_tests=True,
                    has_ci=True,
                    has_docs=True,
                    has_examples=True,
                    license_name="MIT",
                )
                result = analyze(evidence)

                self.assertEqual(result.archetype, case["expected_archetype"])
                self.assertIn(case["expected_customer_contains"], result.customers[0].customer_type)
                self.assertIn(case["expected_model_contains"], result.model)


if __name__ == "__main__":
    unittest.main()
