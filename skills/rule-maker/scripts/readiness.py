#!/usr/bin/env python3
"""Read-only rules inventory and declared-assessment checker, NOT a permission/security boundary.

inspect prints inputs to review, never READY from file presence. assess reads an explicit
assessment from stdin/file and checks its binding to current inputs. No output files written.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

RULES = Path(__file__).resolve().parents[1] / "rules"
MAX_BYTES = 2_000_000
NAMES = ("AGENTS.md", "AGENTS.override.md", "CLAUDE.md", "CLAUDE.local.md", ".claude/CLAUDE.md")
CONFIGS = ("package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock", "tsconfig.json",
           "npm-shrinkwrap.json", "bun.lock", "bun.lockb", "pnpm-workspace.yaml",
           "composer.json", "composer.lock", ".php-version", ".tool-versions",
           "angular.json", "ionic.config.json", "capacitor.config.ts", "capacitor.config.js", "capacitor.config.json",
           "Cargo.toml", "Cargo.lock", "rust-toolchain.toml", "rust-toolchain",
           "ProjectSettings/ProjectVersion.txt", "Packages/manifest.json", "Packages/packages-lock.json")
REQUIRED = ("identity", "trust", "shared_rules", "project_rules", "scope", "versions",
            "verification", "output_safety", "authority", "conflicts", "loading")
WAIVABLE = {"project_rules", "verification"}
MODES = {"plan", "change", "test", "read-only", "setup"}


def bounded_file(path: Path, root: Path) -> str | None:
    if not path.resolve().is_relative_to(root):
        raise ValueError(f"Input escapes the inspected root: {path}")
    for p in (path, *path.parents):
        if p == root.parent:
            break
        if p.is_symlink() or (p.exists() and getattr(p.lstat(), "st_file_attributes", 0) & 0x400):
            raise ValueError(f"Linked/junction rule input needs manual review: {path}")
    if not path.exists():
        return None
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError(f"Input is not a bounded ordinary file: {path}")
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_path(value: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Use nonempty relative forward-slash paths.")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or ":" in value or any(c in value for c in "\n\r\x00"):
        raise ValueError(f"Unsafe relative path: {value!r}")
    return path


def workspace_identity(root: Path) -> dict:
    """Read Git identity without running repo scripts/hooks or taking optional locks."""
    executable = shutil.which("git")
    if not executable:
        return {"kind": "git-unavailable", "limit": "Verify branch/worktree identity manually; disk paths alone are insufficient."}
    if any(os.environ.get(k) for k in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE")):
        raise ValueError("Custom Git environment requires explicit manual identity review.")
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    def read(*args):
        return subprocess.run([executable, "--no-optional-locks", "-C", str(root), *args],
                              capture_output=True, text=True, timeout=5, env=env)
    found = read("rev-parse", "--show-toplevel", "--absolute-git-dir")
    if found.returncode:
        if (root/".git").exists() or "not a git repository" not in found.stderr.lower():
            raise ValueError("Cannot establish Git identity; inspect trust/access before continuing.")
        return {"kind": "not-a-git-repository"}
    lines = found.stdout.splitlines()
    if len(lines) != 2 or Path(lines[0]).resolve() != root:
        raise ValueError("Supply the actual repository root; nested/multiple roots require separate scoped checks.")
    branch = read("symbolic-ref", "--quiet", "HEAD")
    commit = read("rev-parse", "--verify", "HEAD")
    if branch.returncode not in (0, 1) or (commit.returncode and branch.returncode):
        raise ValueError("Cannot establish branch/commit identity.")
    return {"kind": "git", "git_dir": lines[1], "branch": branch.stdout.strip() or None,
            "commit": commit.stdout.strip() if commit.returncode == 0 else None}


def snapshot(root: Path, scopes: list[str], *, task: str, host: str, sources=(), shared: Path = RULES) -> dict:
    root = root.expanduser().resolve(strict=True)
    shared = shared.expanduser().resolve(strict=True)
    if not root.is_dir() or not shared.is_dir():
        raise ValueError("Repository and rules paths must be directories.")
    if not scopes or not task.strip() or not host.strip():
        raise ValueError("Scope, task and actual host/profile identity are required.")
    scope_paths = sorted({relative_path(value).as_posix() for value in scopes})
    candidates = set()
    for value in scope_paths:
        relative = relative_path(value)
        target = root / relative
        if not target.resolve().is_relative_to(root):
            raise ValueError("Scope escapes the inspected root.")
        if target.is_symlink():
            raise ValueError("Linked scope needs explicit manual review.")
        # Include target as a possible directory even when a proposed path is not present yet.
        directory = relative if target.is_dir() or not target.exists() else relative.parent
        for current in (directory, *directory.parents):
            for name in NAMES + CONFIGS:
                candidates.add((current / name).as_posix())
            rules_dir = root / current / ".claude/rules"
            if rules_dir.exists():
                if rules_dir.is_symlink():
                    raise ValueError("Linked scoped-rules directory needs manual review.")
                for parent, dirs, files in os.walk(rules_dir, followlinks=False):
                    if any((Path(parent)/d).is_symlink() for d in dirs):
                        raise ValueError("Linked scoped-rules directory needs manual review.")
                    for name in files:
                        if name.endswith(".md"):
                            candidates.add((Path(parent)/name).relative_to(root).as_posix())
                    if len(candidates) > 512:
                        raise ValueError("Too many inputs: split the scope; no silent truncation.")
    candidates.update(relative_path(s).as_posix() for s in sources)
    if len(candidates) > 512:
        raise ValueError("Too many inputs: split the scope.")
    project = {s: bounded_file(root/s, root) for s in sorted(candidates)}
    manifest_path = shared / "version.json"
    bounded_file(manifest_path, shared)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or not isinstance(manifest.get("files"), list):
        raise ValueError("Unknown rules library manifest.")
    if not {"START.md", "CORE.md", "READINESS.md"}.issubset(manifest["files"]):
        raise ValueError("Incomplete rules library.")
    if not isinstance(manifest.get("sha256"), dict) or set(manifest["sha256"]) != set(manifest["files"]):
        raise ValueError("Incomplete rules-library integrity manifest.")
    modules = {"version.json": bounded_file(manifest_path, shared)}
    for name in manifest["files"]:
        if not isinstance(name, str) or Path(name).name != name:
            raise ValueError("Unsafe shared library entry.")
        digest = bounded_file(shared/name, shared)
        if digest is None or not (shared/name).read_text(encoding="utf-8").strip():
            raise ValueError(f"Missing/empty shared rule: {name}")
        if digest != manifest["sha256"][name]:
            raise ValueError(f"Mixed/modified rules library: {name}")
        modules[name] = digest
    result = {"root": str(root), "workspace": workspace_identity(root), "shared_root": str(shared), "scope": scope_paths,
              "task": task, "host": host, "project_inputs": project,
              "shared_inputs": modules, "rules_version": manifest.get("rules_version")}
    result["fingerprint"] = hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()
    return result


def verdict(state: str, reasons: list[str], allowed=()) -> dict:
    return {"state": state, "reasons": reasons, "allowed_modes": list(allowed),
            "implementation_approved": False,
            "limits": "Checks declared assessment/freshness only; not semantic truth, authentic consent, model compliance or host enforcement."}


def evaluate(data: dict, current: dict, mode: str) -> dict:
    if mode not in MODES or not isinstance(data, dict) or data.get("schema_version") != 1:
        return verdict("BLOCKED", ["Unknown mode/schema or malformed assessment."])
    if mode == "read-only":
        return verdict("READ_ONLY", ["Inspection only; no mutation or setup authority."], ["read-only"])
    if data.get("snapshot") != current:
        return verdict("BLOCKED", ["Assessment is missing or stale; re-read changed scope/rules/inputs."])
    checks = data.get("checks")
    if not isinstance(checks, dict) or any(name not in checks for name in REQUIRED):
        return verdict("BLOCKED", ["Required assessment categories are missing."])
    if set(checks) - set(REQUIRED) - {"design"}:
        return verdict("BLOCKED", ["Unknown assessment category; inspect instead of ignoring it."])
    missing = []
    for name, item in checks.items():
        if not isinstance(item, dict) or item.get("status") not in {"verified", "missing", "blocked", "not-applicable"}:
            return verdict("BLOCKED", [f"Unrecognised assessment: {name}."])
        if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
            return verdict("BLOCKED", [f"Missing evidence/reason: {name}."])
        if item["status"] == "not-applicable" and name != "design":
            return verdict("BLOCKED", [f"Required category cannot be skipped: {name}."])
        if item["status"] == "blocked" or (item["status"] == "missing" and name not in WAIVABLE):
            return verdict("BLOCKED", [f"Unresolved indispensable prerequisite: {name}."])
        if item["status"] == "missing":
            missing.append(name)
    if mode == "setup":
        setup = data.get("setup_consent", {})
        if not isinstance(setup, dict) or setup.get("authority_confirmed") is not True or not setup.get("response_ref"):
            return verdict("NEEDS_SETUP", ["No explicit authorised setup response recorded."])
        paths = setup.get("paths")
        if not isinstance(paths, list) or not paths or any(not isinstance(p, str) or not p.strip() for p in paths):
            return verdict("BLOCKED", ["Setup consent must name exact permitted setup artifacts."])
        return verdict("SETUP_ONLY", ["Only named authorised setup artifacts; no application work."], ["setup"])
    if not missing:
        return verdict("READY", ["Declared applicable coverage and fingerprints match; normal task approval still required."], ["plan", "change", "test"])
    exception = data.get("exception")
    if exception is None:
        return verdict("NEEDS_SETUP", ["Missing " + ", ".join(missing) + "; ask setup / bounded exception / read-only / stop."])
    if not isinstance(exception, dict):
        return verdict("BLOCKED", ["Malformed exception."])
    gaps, operations = exception.get("gaps"), exception.get("operations")
    valid = (exception.get("authority_confirmed") is True and exception.get("active") is True
             and isinstance(exception.get("response_ref"), str) and bool(exception["response_ref"].strip())
             and isinstance(exception.get("reason"), str) and bool(exception["reason"].strip())
             and isinstance(exception.get("expires"), str) and exception["expires"] in {"task", "work-unit"}
             and isinstance(gaps, list) and all(isinstance(x, str) for x in gaps) and set(gaps) == set(missing)
             and isinstance(operations, list) and all(isinstance(x, str) for x in operations)
             and mode in operations and set(operations).issubset({"plan", "change", "test"})
             and exception.get("snapshot_fingerprint") == current.get("fingerprint"))
    if not valid:
        return verdict("BLOCKED", ["Exception is expired, incomplete or bound to different scope/rules/operations."])
    return verdict("LIMITED_EXCEPTION", ["Known omissions explicitly excepted; remaining safeguards and task approval still apply."], operations)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("inspect", "assess"))
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--scope", action="append", required=True)
    parser.add_argument("--source", action="append", default=[], help="Additional inspected project reference; relative path.")
    parser.add_argument("--task", required=True)
    parser.add_argument("--host", required=True, help="Actual host/profile identifier; not a claimed live verification.")
    parser.add_argument("--mode", choices=sorted(MODES), default="plan")
    parser.add_argument("--input", default="-", help="Assessment JSON from stdin by default; no file required.")
    args = parser.parse_args(argv)
    try:
        current = snapshot(args.root, args.scope, task=args.task, host=args.host, sources=args.source)
        if args.action == "inspect":
            result = {"state": "REVIEW_REQUIRED", "snapshot": current,
                      "required_checks": list(REQUIRED),
                      "limits": "File presence is not readiness; review actual content and include imported/linked references through --source."}
            code = 0
        else:
            raw = sys.stdin.buffer.read(MAX_BYTES+1) if args.input == "-" else Path(args.input).read_bytes()
            if len(raw) > MAX_BYTES:
                raise ValueError("Assessment exceeds size limit.")
            result = evaluate(json.loads(raw), current, args.mode)
            code = 0 if result["state"] in {"READY", "LIMITED_EXCEPTION", "SETUP_ONLY", "READ_ONLY"} else 2
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return code
    except (OSError, UnicodeError, ValueError, TypeError, subprocess.SubprocessError) as exc:
        print(json.dumps(verdict("BLOCKED", [str(exc)]), indent=2))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
