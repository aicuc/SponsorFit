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


def _iter_files(root: Path, max_files: int = 5_000) -> Iterator[Path]:
    seen = 0
    for current, dirs, files in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in IGNORED_DIRS and not d.startswith("."))
        for filename in sorted(files):
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
    candidates = sorted(root.glob("LICENSE*")) + sorted(root.glob("COPYING*"))
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


def _github_metadata(root: Path) -> dict[str, Any]:
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
                "recentIssues": ["gh", "issue", "list", "--repo", repo_name, "--limit", "20", "--json", "title,state,labels,comments"],
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

    for path in files:
        language = TEXT_EXTENSIONS.get(path.suffix.lower())
        if language:
            try:
                language_bytes[language] += path.stat().st_size
            except OSError:
                pass
        if path.name.lower() in MANIFEST_NAMES and len(path.relative_to(root).parts) <= 3:
            manifests[str(path.relative_to(root))] = _read_manifest(path)

    readmes = sorted(files, key=lambda p: (not p.name.lower().startswith("readme"), len(p.parts)))
    readme_path = next((path for path in readmes if path.name.lower().startswith("readme")), None)
    readme = _safe_text(readme_path, 40_000) if readme_path else ""

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
    if not description:
        for manifest in manifests.values():
            candidate = manifest.get("description")
            if isinstance(candidate, str):
                description = candidate[:300]
                break

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
        github=_github_metadata(root) if include_github else {"status": "not_requested"},
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
