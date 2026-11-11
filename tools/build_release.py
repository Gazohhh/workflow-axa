#!/usr/bin/env python3
"""Build the installable workflow-axa ZIP from an explicit include list.

The archive holds only what an installation needs: the plugin manifest, the registered
skills, the hooks, the licence and the user-facing documents. Tests, tools, task records
and evaluation output stay in the source checkout. Entries are sorted and carry a fixed
timestamp, so the same tree always gives the same bytes and SHA-256.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_FILES = ("LICENSE", "README.md", "CHANGELOG.md", "UPGRADE.md", "VALIDATION.md", "VENDORED-SKILLS.md",
              "docs/DESIGN.md", "docs/ARCHITECTURE.md", "docs/EVALUATION.md")
INCLUDED_DIRS = (".claude-plugin", "hooks")  # plus each skill folder plugin.json registers
SKIPPED_PARTS = {".git", ".artifacts", "__pycache__", ".local-fixtures"}
SKIPPED_SUFFIXES = {".pyc", ".pyo"}
SECRET_NAME = re.compile(r"(token|secret|credential)", re.I)
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


class ReleaseError(Exception):
    pass


@dataclass(frozen=True)
class Release:
    path: Path
    sha256: str
    files: tuple[str, ...]


def looks_secret(name: str) -> bool:
    lower = name.lower()
    return (lower == ".env" or lower.startswith(".env.") or lower.endswith((".pem", ".key"))
            or bool(SECRET_NAME.search(name)))


def _walk(root: Path, folder: str) -> list[str]:
    base = root / folder
    if not base.is_dir() or base.is_symlink():
        raise ReleaseError(f"Included folder is missing or a link: {folder}")
    found = []
    for path in base.rglob("*"):
        relative = path.relative_to(root)
        if any(part in SKIPPED_PARTS for part in relative.parts) or path.suffix in SKIPPED_SUFFIXES:
            continue
        if path.is_symlink():
            raise ReleaseError(f"Refusing a link inside the release: {relative.as_posix()}")
        if path.is_file():
            found.append(relative.as_posix())
    return found


def included_folders(root: Path) -> tuple[str, ...]:
    try:
        plugin = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        skills = [entry.removeprefix("./") for entry in plugin["skills"]]
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        raise ReleaseError(f"Cannot read the registered skills from plugin.json: {exc}") from exc
    for folder in skills:
        if not isinstance(folder, str) or not re.fullmatch(r"skills/[a-z0-9-]+", folder):
            raise ReleaseError(f"Unexpected skill path in plugin.json: {folder}")
    return (*INCLUDED_DIRS, *skills)


def collect(root: Path) -> list[str]:
    """Return the sorted release paths, or raise when a file is missing or looks like a secret."""
    files = set()
    for folder in included_folders(root):
        files.update(_walk(root, folder))
    for name in ROOT_FILES:
        path = root / name
        if not path.is_file() or path.is_symlink():
            raise ReleaseError(f"Included file is missing or a link: {name}")
        files.add(name)
    secrets = sorted(name for name in files if looks_secret(name.rsplit("/", 1)[-1]))
    if secrets:
        raise ReleaseError("Refusing to package files that look like secrets: " + ", ".join(secrets))
    return sorted(files)


def default_output_dir(root: Path, ignored=None) -> Path:
    """dist/ when Git ignores it; otherwise the ignored .artifacts/release/ folder."""
    if ignored is None:
        ignored = lambda path: _git_ignores(root, path)
    return root / "dist" if ignored("dist/workflow-axa.zip") else root / ".artifacts/release"


def _git_ignores(root: Path, relative: str) -> bool:
    try:
        return subprocess.run(["git", "-C", str(root), "check-ignore", "-q", relative],
                              capture_output=True, timeout=30).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def build_release(root: Path, output_dir: Path) -> Release:
    root = root.resolve()
    output_dir = output_dir.resolve()
    files = collect(root)
    plugin = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    version = str(plugin.get("version", ""))
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
        raise ReleaseError(f"plugin.json has no usable version: {version!r}")
    if any(output_dir.is_relative_to(root / folder) for folder in (*included_folders(root), "docs")):
        raise ReleaseError(f"Output folder is inside the release contents: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"workflow-axa-{version}.zip"
    partial = target.with_name(target.name + ".partial")
    with zipfile.ZipFile(partial, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in files:
            info = zipfile.ZipInfo(name, date_time=FIXED_TIME)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            info.create_system = 3
            archive.writestr(info, (root / name).read_bytes(), compresslevel=9)
    partial.replace(target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    return Release(target, digest, tuple(files))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, help="folder for the ZIP (default: dist/ if Git ignores it, "
                                                    "else .artifacts/release/)")
    args = parser.parse_args()
    output = args.output or default_output_dir(args.root.resolve())
    if args.output is None and output.name == "release":
        print("dist/ is not ignored by Git; writing to .artifacts/release/ instead.")
    try:
        result = build_release(args.root, output)
    except (ReleaseError, OSError) as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    for name in result.files:
        print(name)
    print(f"{len(result.files)} files -> {result.path} ({result.path.stat().st_size} bytes)")
    print(f"SHA-256 {result.sha256}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
