from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class RepositoryEvidence:
    """A bounded, serializable view of repository evidence."""

    name: str
    root: Path
    description: str = ""
    readme_excerpt: str = ""
    manifests: dict[str, dict[str, Any]] = field(default_factory=dict)
    languages: dict[str, int] = field(default_factory=dict)
    license_name: str = "Unknown"
    files_count: int = 0
    has_tests: bool = False
    has_ci: bool = False
    has_docs: bool = False
    has_examples: bool = False
    has_changelog: bool = False
    signals: list[str] = field(default_factory=list)
    github: dict[str, Any] = field(default_factory=dict)
    sources: dict[str, list[str]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["root"] = str(self.root)
        return data


@dataclass
class MaintainerContext:
    """Optional evidence and constraints supplied directly by a maintainer."""

    constraints: list[str] = field(default_factory=list)
    audience_evidence: list[str] = field(default_factory=list)
    interview_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, list[str]]:
        return asdict(self)

    @property
    def is_empty(self) -> bool:
        return not (self.constraints or self.audience_evidence or self.interview_notes)


@dataclass(frozen=True)
class CustomerOpportunity:
    customer_type: str
    pain_point: str
    workaround: str
    why_it_matters: str
    pay_for: str
    not_pay_for: str
    required_features: str
    budget: str
    reach: str
    scores: dict[str, int]

    @property
    def total(self) -> int:
        return sum(self.scores.values())

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["total"] = self.total
        return data


@dataclass
class SponsorFitAnalysis:
    archetype: str
    maturity: str
    monetization_readiness: str
    values: list[str]
    customers: list[CustomerOpportunity]
    model: str
    model_reason: str
    stays_free: list[str]
    paid: list[str]
    never_paywall: list[str]
    build_next: list[dict[str, str]]
    risks: list[str]

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["customers"] = [customer.to_dict() for customer in self.customers]
        return data
