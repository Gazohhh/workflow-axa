#!/usr/bin/env python3
"""Compare explicitly named skill installations; no writes, host execution or network."""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import re
import stat
import sys
from pathlib import Path

SKILLS = Path(__file__).resolve().parents[2]
NAMES = ("workflow", "codebase-map", "task-status", "resume-task", "workflow-doctor", "plan-review", "rule-maker", "ui-design")
MAX_BYTES = 2_000_000
MAX_FILES = 512


def ordinary(path: Path, boundary: Path) -> bytes | None:
    """Never follow an unreviewed candidate link or read a pipe/device."""
    if not path.absolute().is_relative_to(boundary.absolute()):
        raise ValueError("Input leaves its candidate boundary.")
    for part in (path, *path.parents):
        if part == boundary.parent:
            break
        try:
            info = part.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Linked/junction input requires manual inspection: {path}")
    try:
        info = path.stat()
    except FileNotFoundError:
        return None
    if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_BYTES:
        raise ValueError(f"Not a bounded ordinary input: {path}")
    with path.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Input grew beyond the size limit.")
    return data


def skill_root(value: Path) -> Path:
    value = value.expanduser().absolute()
    # Reject links before resolving, including links in ancestor directories.
    for part in (value, *value.parents):
        if part.is_symlink() or (part.exists() and getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError("Linked installation path needs explicit manual inspection.")
    if not value.is_dir():
        raise ValueError(f"Installation directory does not exist: {value}")
    if value.name == "rule-maker":
        value = value.parent
    elif (value / "skills").is_dir():
        value = value / "skills"
    if not (value / "rule-maker").is_dir():
        raise ValueError(f"No rule-maker in candidate: {value}")
    return value.resolve(strict=True)


def baseline_files(base: Path) -> dict[str, str]:
    result = {}
    for name in NAMES:
        folder = base / name
        if not folder.is_dir():
            raise ValueError(f"Trusted comparison installation is incomplete: {name}")
        for parent, dirs, files in os.walk(folder, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d != "__pycache__")
            for dirname in dirs:
                target = Path(parent) / dirname
                if target.is_symlink() or getattr(target.lstat(), "st_file_attributes", 0) & 0x400:
                    raise ValueError("Linked directory in trusted comparison installation.")
            for filename in sorted(files):
                if filename.endswith((".pyc", ".pyo")):
                    continue
                target = Path(parent) / filename
                raw = ordinary(target, base)
                if raw is None:
                    raise ValueError("Comparison input disappeared.")
                result[target.relative_to(base).as_posix()] = hashlib.sha256(raw).hexdigest()
                if len(result) > MAX_FILES:
                    raise ValueError("Comparison exceeds bounded file count.")
    return result


def declared_version(base: Path) -> str:
    raw = ordinary(base / "rule-maker/rules/version.json", base)
    if raw is None:
        return "UNKNOWN"
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("Invalid library manifest.")
    version = data.get("package_version")
    return version if isinstance(version, str) and re.fullmatch(r"\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?", version) else "UNKNOWN"


def inspect(candidates: list[Path], baseline: Path = SKILLS) -> dict:
    base = skill_root(baseline)
    expected = baseline_files(base)
    actual_paths = list(dict.fromkeys(skill_root(p) for p in (candidates or [base])))
    if len(actual_paths) > 24:
        raise ValueError("Supply at most 24 explicit candidate installations.")
    rows = []
    for candidate in actual_paths:
        missing, changed = [], []
        for relative, digest in expected.items():
            raw = ordinary(candidate / relative, candidate)
            if raw is None:
                missing.append(relative)
            elif hashlib.sha256(raw).hexdigest() != digest:
                changed.append(relative)
        rows.append({"skills_root": str(candidate), "declared_version": declared_version(candidate),
                     "state": "MATCH" if not missing and not changed else "DRIFT", "missing": missing, "changed": changed})
    return {"schema_version": 1, "expected_version": declared_version(base), "comparison_source": str(base),
            "state": "WARNING" if len(rows) > 1 or any(r["state"] != "MATCH" for r in rows) else "DISK_MATCH",
            "candidates": rows, "multiple_copies": len(rows) > 1,
            "host_loading": "NOT_VERIFIED", "compliance": "NOT_VERIFIED", "enforcement": "NOT_VERIFIED",
            "limits": ["Comparison is against this trusted local package, not a remote latest release or security signature.",
                       "Only named candidate copies and expected skill files are checked; extra files and hidden host caches need inspection.",
                       "Matching bytes or global blocks do not prove the host selected or followed them."]}


def activation_module():
    target = Path(__file__).with_name("activate_rules.py")
    spec = importlib.util.spec_from_file_location("workflow_axa_activation_audit", target)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", action="append", type=Path, default=[])
    parser.add_argument("--check-global", action="store_true")
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--claude-dir", type=Path)
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--host", choices=("both", "claude", "codex"), default="both")
    args = parser.parse_args(argv)
    try:
        activation = activation_module()
        activation.validate_library(SKILLS / "rule-maker/rules")
        result = inspect(args.candidate)
        if args.check_global:
            home = args.home.expanduser()
            if not home.is_absolute():
                raise ValueError("Home must be absolute.")
            claude = args.claude_dir or Path(os.environ.get("CLAUDE_CONFIG_DIR") or home / ".claude")
            codex = args.codex_home or Path(os.environ.get("CODEX_HOME") or home / ".codex")
            changes = activation.build_plan(home, claude.expanduser(), codex.expanduser(), args.host)
            result["global_references"] = [{"path": str(c.path), "state": "MATCH" if c.before == c.after else "MISSING" if c.before is None else "UPDATE"} for c in changes]
            if any(c.before != c.after for c in changes):
                result["state"] = "WARNING"
        print(json.dumps(result, indent=2))
        return 0 if result["state"] == "DISK_MATCH" else 1
    except (OSError, ValueError, UnicodeError, TypeError, RecursionError) as exc:
        print(json.dumps({"state": "BLOCKED", "reason": str(exc), "host_loading": "NOT_VERIFIED"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
