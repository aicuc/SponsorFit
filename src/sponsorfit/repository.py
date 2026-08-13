from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator
from urllib.parse import urlparse

from .models import RepositoryEvidence


IGNORED_DIRS = {
    ".git", ".hg", ".svn", ".venv", "venv", "node_modules", "vendor",
    "dist", "build", "coverage", ".next", "target", "__pycache__", ".tox",
}
SENSITIVE_NAMES = {
    ".env", ".env.local", ".env.production", "credentials.json",
    "id_rsa", "id_ed25519", ".npmrc", ".pypirc",
}
SENSITIVE_SUFFIXES = {".pem", ".key", ".p12", ".pfx"}
IGNORED_FILES = {".DS_Store"}
TEXT_EXTENSIONS = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".kt": "Kotlin", ".rb": "Ruby",
    ".php": "PHP", ".swift": "Swift", ".c": "C", ".h": "C/C++",
    ".cpp": "C++", ".cs": "C#", ".scala": "Scala", ".sh": "Shell",
    ".lua": "Lua", ".ex": "Elixir", ".exs": "Elixir",
}
MANIFEST_NAMES = {
    "package.json", "pyproject.toml", "cargo.toml", "go.mod", "gemfile",
    "composer.json", "pom.xml", "build.gradle", "requirements.txt",
}
PYPROJECT_METADATA_SECTIONS = {"project", "tool.poetry"}
PYPROJECT_SCALAR_KEYS = {"name", "description", "version"}
ISSUE_THEME_TERMS = {
    "installation": ("install", "setup", "packag", "dependency"),
    "compatibility": ("windows", "macos", "linux", "python 3", "node ", "version", "compatib"),
    "performance": ("slow", "performance", "latency", "memory", "timeout"),
    "reliability": ("crash", "fail", "broken", "error", "retry", "hang"),
    "integration": ("integration", "plugin", "api", "webhook", "connector"),
    "documentation": ("docs", "documentation", "example", "tutorial"),
    "security": ("security", "vulnerability", "cve", "permission", "auth"),
}


def _is_sensitive(path: Path) -> bool:
    name = path.name.lower()
    return (
        name in SENSITIVE_NAMES
        or path.suffix.lower() in SENSITIVE_SUFFIXES
        or name.startswith(".env.")
        or "secret" in name
    )


def _safe_text(path: Path, limit: int = 32_000) -> str:
    if _is_sensitive(path) or not path.is_file():
        return ""
    try:
        raw = path.read_bytes()[:limit]
        if b"\x00" in raw:
            return ""
        return raw.decode("utf-8", errors="replace")
    except OSError:
        return ""


def _read_pyproject_fallback(text: str) -> dict[str, str]:
    """Read basic pyproject metadata when Python's tomllib is unavailable."""
    sections: dict[str, dict[str, str]] = {
        section: {} for section in PYPROJECT_METADATA_SECTIONS
    }
    current_section = ""

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1].strip()
            continue
        if current_section not in PYPROJECT_METADATA_SECTIONS or "=" not in line:
            continue

        key, raw_value = (part.strip() for part in line.split("=", 1))
        if key not in PYPROJECT_SCALAR_KEYS or len(raw_value) < 2:
            continue
        quote = raw_value[0]
        if quote not in {'"', "'"} or raw_value[-1] != quote:
            continue
        sections[current_section][key] = raw_value[1:-1]

    return sections["project"] or sections["tool.poetry"]


def _iter_files(root: Path, max_files: int = 5_000) -> Iterator[Path]:
    seen = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS and not d.startswith("."))
        for filename in sorted(files):
            if filename in IGNORED_FILES:
                continue
            path = Path(current) / filename
            if path.is_symlink() or _is_sensitive(path):
                continue
            yield path
            seen += 1
            if seen >= max_files:
                return


def _read_manifest(path: Path) -> dict[str, Any]:
    text = _safe_text(path, 64_000)
    if not text:
        return {}
    if path.name.lower() in {"package.json", "composer.json"}:
        try:
            parsed = json.loads(text)
            keys = ("name", "description", "version", "dependencies", "devDependencies", "scripts")
            return {key: parsed[key] for key in keys if key in parsed}
        except (json.JSONDecodeError, TypeError):
            return {"parse_error": "Invalid JSON"}
    if path.name.lower() == "pyproject.toml":
        try:
            import tomllib
        except ModuleNotFoundError:
            return _read_pyproject_fallback(text)
        else:
            try:
                parsed = tomllib.loads(text)
                project = parsed.get("project", {})
                poetry = parsed.get("tool", {}).get("poetry", {})
                data = project or poetry
                keys = ("name", "description", "version", "dependencies")
                return {key: data[key] for key in keys if key in data}
            except (ValueError, TypeError):
                return {"parse_error": "Invalid TOML"}
    lines = [line.strip() for line in text.splitlines() if line.strip() and not line.startswith("#")]
    return {"excerpt": lines[:30]}


def _description_from_readme(text: str) -> str:
    for paragraph in re.split(r"\n\s*\n", text):
        clean = " ".join(
            line.strip() for line in paragraph.splitlines()
            if line.strip() and not line.lstrip().startswith(("#", "[", "!", "```", "<"))
        )
        if len(clean) >= 30:
            return clean[:300]
    return ""


def _detect_license(root: Path) -> str:
    candidates = [
        path for path in sorted(root.glob("LICENSE*")) + sorted(root.glob("COPYING*"))
        if not path.is_symlink()
    ]
    if not candidates:
        return "Unknown"
    text = _safe_text(candidates[0], 8_000).lower()
    matches = [
        ("mit license", "MIT"), ("apache license", "Apache-2.0"),
        ("gnu affero", "AGPL"), ("gnu general public license", "GPL"),
        ("mozilla public license", "MPL-2.0"), ("bsd 3-clause", "BSD-3-Clause"),
    ]
    for marker, label in matches:
        if marker in text:
            return label
    return candidates[0].name


def _git_remote(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            check=True, capture_output=True, text=True, timeout=3,
        )
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def _issue_themes(issues: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return deterministic themes that recur in at least two issue titles/labels."""
    grouped: dict[str, list[str]] = {}
    for issue in issues:
        title = str(issue.get("title", "")).strip()
        labels = issue.get("labels", [])
        label_text = " ".join(
            str(label.get("name", "")) if isinstance(label, dict) else str(label)
            for label in labels if label
        )
        haystack = f"{title} {label_text}".lower()
        for theme, terms in ISSUE_THEME_TERMS.items():
            if any(term in haystack for term in terms):
                grouped.setdefault(theme, []).append(title)

    return [
        {"theme": theme, "count": len(titles), "sample_titles": titles[:3]}
        for theme, titles in sorted(grouped.items(), key=lambda item: -len(item[1]))
        if len(titles) >= 2
    ]


def _find_dependent_candidates(repo_name: str, package_names: list[str]) -> list[dict[str, str]]:
    """Find public code-search matches; these are candidates, not verified dependents."""
    candidates: dict[str, dict[str, str]] = {}
    for package_name in package_names[:3]:
        try:
            result = subprocess.run(
                [
                    "gh", "search", "code", package_name, "--limit", "20",
                    "--json", "path,repository,url",
                ],
                check=True, capture_output=True, text=True, timeout=15,
            )
            matches = json.loads(result.stdout)
        except (OSError, subprocess.SubprocessError, json.JSONDecodeError, TypeError):
            continue
        for match in matches if isinstance(matches, list) else []:
            repository = match.get("repository", {})
            matched_repo = (
                repository.get("nameWithOwner", "") if isinstance(repository, dict)
                else str(repository)
            )
            if not matched_repo or matched_repo.casefold() == repo_name.casefold():
                continue
            candidates.setdefault(matched_repo, {
                "repository": matched_repo,
                "path": str(match.get("path", "")),
                "url": str(match.get("url", "")),
                "matched_package": package_name,
            })
    return [candidates[key] for key in sorted(candidates)]


def _github_metadata(root: Path, package_names: list[str] | None = None) -> dict[str, Any]:
    if not shutil.which("gh"):
        return {"status": "unavailable", "reason": "gh is not installed"}
    remote = _git_remote(root)
    if "github.com" not in remote:
        return {"status": "unavailable", "reason": "no GitHub origin found"}
    fields = "nameWithOwner,description,stargazerCount,forkCount,watchers,licenseInfo,repositoryTopics,latestRelease,createdAt,updatedAt"
    try:
        result = subprocess.run(
            ["gh", "repo", "view", remote, "--json", fields],
            check=True, capture_output=True, text=True, timeout=12,
        )
        data = json.loads(result.stdout)
        repo_name = data.get("nameWithOwner")
        if repo_name:
            enrichments = {
                "recentIssues": ["gh", "issue", "list", "--repo", repo_name, "--limit", "50", "--json", "title,state,labels,comments"],
                "recentPullRequests": ["gh", "pr", "list", "--repo", repo_name, "--limit", "20", "--json", "title,state,labels,author"],
                "recentReleases": ["gh", "release", "list", "--repo", repo_name, "--limit", "10", "--json", "tagName,name,publishedAt,isLatest"],
            }
            for key, command in enrichments.items():
                try:
                    extra = subprocess.run(
                        command, check=True, capture_output=True, text=True, timeout=10,
                    )
                    data[key] = json.loads(extra.stdout)
                except (OSError, subprocess.SubprocessError, json.JSONDecodeError):
                    data[key] = []
            data["issueThemes"] = _issue_themes(data.get("recentIssues", []))
            data["dependentCandidates"] = _find_dependent_candidates(
                repo_name, package_names or [root.name]
            )
        data["status"] = "available"
        return data
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {"status": "unavailable", "reason": type(exc).__name__}


def scan_repository(root: Path, include_github: bool = False) -> RepositoryEvidence:
    root = root.resolve()
    if not root.is_dir():
        raise ValueError(f"Repository path is not a directory: {root}")

    files = list(_iter_files(root))
    lower_parts = {part.lower() for path in files for part in path.relative_to(root).parts}
    names = {path.name.lower() for path in files}
    language_bytes: Counter[str] = Counter()
    manifests: dict[str, dict[str, Any]] = {}
    signals: list[str] = []
    source_paths: dict[str, list[str]] = {
        "repository": ["."],
        "files": [str(path.relative_to(root)) for path in files[:12]],
    }

    for path in files:
        language = TEXT_EXTENSIONS.get(path.suffix.lower())
        if language:
            try:
                language_bytes[language] += path.stat().st_size
            except OSError:
                pass
            source_paths.setdefault("languages", [])
            relative = str(path.relative_to(root))
            if len(source_paths["languages"]) < 12:
                source_paths["languages"].append(relative)
        if path.name.lower() in MANIFEST_NAMES and len(path.relative_to(root).parts) <= 3:
            relative = str(path.relative_to(root))
            manifests[relative] = _read_manifest(path)
            source_paths.setdefault("manifests", []).append(relative)

    readmes = sorted(files, key=lambda p: (not p.name.lower().startswith("readme"), len(p.parts)))
    readme_path = next((path for path in readmes if path.name.lower().startswith("readme")), None)
    readme = _safe_text(readme_path, 40_000) if readme_path else ""
    if readme_path:
        source_paths["readme"] = [str(readme_path.relative_to(root))]

    joined = (readme + "\n" + json.dumps(manifests, default=str)).lower()
    for label, terms in {
        "AI/ML": ("llm", "machine learning", "artificial intelligence", "rag", "agent"),
        "PDF/OCR": ("pdf", "ocr", "document parsing"),
        "Developer tool": ("developer tool", "cli", "sdk", "api", "plugin"),
        "Self-hosting": ("self-host", "docker", "kubernetes", "on-prem"),
        "Enterprise": ("enterprise", "sso", "audit log", "compliance", "rbac"),
    }.items():
        if any(term in joined for term in terms):
            signals.append(label)

    description = _description_from_readme(readme)
    if description and readme_path:
        source_paths["description"] = [str(readme_path.relative_to(root))]
    if not description:
        for manifest_path, manifest in manifests.items():
            candidate = manifest.get("description")
            if isinstance(candidate, str):
                description = candidate[:300]
                source_paths["description"] = [manifest_path]
                break

    license_candidates = [
        path for path in sorted(root.glob("LICENSE*")) + sorted(root.glob("COPYING*"))
        if not path.is_symlink()
    ]
    if license_candidates:
        source_paths["license"] = [str(license_candidates[0].relative_to(root))]
    if {"tests", "test", "spec", "__tests__"} & lower_parts:
        source_paths["tests"] = [
            f"{name}/" for name in ("tests", "test", "spec", "__tests__")
            if (root / name).exists()
        ][:4]
    if (root / ".github" / "workflows").is_dir():
        source_paths["ci"] = [".github/workflows/"]
    for key, names_for_key in {
        "docs": ("docs", "documentation"),
        "examples": ("examples", "example", "samples"),
    }.items():
        found = [f"{name}/" for name in names_for_key if (root / name).exists()]
        if found:
            source_paths[key] = found
    changelog_paths = [
        str(path.relative_to(root)) for path in files
        if path.name.lower().startswith(("changelog", "changes", "history"))
    ][:4]
    if changelog_paths:
        source_paths["changelog"] = changelog_paths
    if signals:
        source_paths["signals"] = list(dict.fromkeys(
            source_paths.get("readme", []) + source_paths.get("manifests", [])
        ))

    package_names = [
        value.get("name") for value in manifests.values()
        if isinstance(value.get("name"), str) and len(value["name"].strip()) >= 3
    ]

    return RepositoryEvidence(
        name=root.name,
        root=root,
        description=description,
        readme_excerpt=readme[:8_000],
        manifests=manifests,
        languages=dict(language_bytes.most_common()),
        license_name=_detect_license(root),
        files_count=len(files),
        has_tests=bool({"tests", "test", "spec", "__tests__"} & lower_parts),
        has_ci=(root / ".github" / "workflows").is_dir(),
        has_docs=bool({"docs", "documentation"} & lower_parts),
        has_examples=bool({"examples", "example", "samples"} & lower_parts),
        has_changelog=any(name.startswith(("changelog", "changes", "history")) for name in names),
        signals=signals,
        github=_github_metadata(root, package_names or [root.name]) if include_github else {"status": "not_requested"},
        sources=source_paths,
    )


def _is_repo_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "ssh", "git"} or value.startswith("git@")


@contextmanager
def prepared_repository(source: str) -> Iterator[Path]:
    if not _is_repo_url(source):
        yield Path(source)
        return
    if not shutil.which("git"):
        raise RuntimeError("git is required to analyze a repository URL")
    with tempfile.TemporaryDirectory(prefix="sponsorfit-") as temp_dir:
        destination = Path(temp_dir) / "repo"
        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", source, str(destination)],
                check=True, timeout=120,
            )
        except subprocess.SubprocessError as exc:
            raise RuntimeError(f"Could not clone repository: {source}") from exc
        yield destination
