#!/usr/bin/env python3
"""Read-only specialist inventory. Checks files, not host availability or invocation."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
from pathlib import Path

CATALOGUE = Path(__file__).resolve().parents[1] / "specialists.json"
SKIP = {".git", "__pycache__", "node_modules", ".venv", ".artifacts"}
MAX_FILE_BYTES = 16 * 1024 * 1024
MAX_FILES = 10000


def scalar(header: str, key: str) -> str | None:
    """Read only the plain/quoted single-line fields this catalogue needs, not YAML."""
    matches = re.findall(rf"^{re.escape(key)}:[ \t]*(.*)$", header, re.M)
    if not matches:
        return None
    if len(matches) != 1:
        raise ValueError(f"Duplicate frontmatter field: {key}")
    value = matches[0].strip()
    if value.startswith('"'):
        value = json.loads(value)
    elif value.startswith("'") and value.endswith("'"):
        value = value[1:-1].replace("''", "'")
    else:
        value = value.split(" #", 1)[0].strip()
    if not isinstance(value, str) or not value or value[0] in "|>{[&*!":
        raise ValueError(f"Unsupported frontmatter scalar: {key}")
    return value


def metadata(path: Path) -> tuple[str, bool]:
    text = path.read_text(encoding="utf-8-sig")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)", text, re.S)
    if not match:
        raise ValueError("Missing SKILL.md frontmatter")
    name = scalar(match[1], "name")
    if not name or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("Missing/unsupported skill name")
    flag = scalar(match[1], "disable-model-invocation")
    if flag is None:
        return name, False
    if flag.lower() not in {"true", "false", "yes", "no", "on", "off", "1", "0"}:
        raise ValueError("Unsupported disable-model-invocation value")
    return name, flag.lower() in {"true", "yes", "on", "1"}


def discover(roots: list[Path]) -> list[Path]:
    found: set[Path] = set()
    for root in roots:
        root = root.expanduser().resolve()
        if not root.is_dir():
            raise ValueError(f"Skill root is not a readable directory: {root}")
        def fail(error: OSError) -> None:
            raise error
        for directory, dirs, files in os.walk(root, followlinks=False, onerror=fail):
            current = Path(directory)
            dirs[:] = sorted(d for d in dirs if d not in SKIP)
            if "SKILL.md" in files:
                found.add((current / "SKILL.md").resolve())
                dirs[:] = []
                continue
            # Installers may symlink whole skill directories; do not follow arbitrary trees.
            for child in dirs:
                candidate = current / child
                if candidate.is_symlink() and (candidate / "SKILL.md").is_file():
                    found.add((candidate / "SKILL.md").resolve())
            if len(found) > MAX_FILES:
                raise ValueError("Too many skill directories; supply narrower roots")
    return sorted(found)


def fingerprint(folder: Path) -> str:
    """Hash the complete skill tree, including names and supporting files, byte-for-byte."""
    digest = hashlib.sha256()
    count = 0
    def fail(error: OSError) -> None:
        raise error
    for directory, dirs, files in os.walk(folder, followlinks=False, onerror=fail):
        dirs[:] = sorted(d for d in dirs if d not in SKIP)
        for name in dirs + files:
            path = Path(directory) / name
            if path.is_symlink():
                raise ValueError(f"Symlink inside skill tree needs manual review: {path.name}")
        for name in sorted(files):
            path = Path(directory) / name
            info = path.stat()
            if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE_BYTES:
                raise ValueError(f"Unsupported/oversized skill file: {path.name}")
            count += 1
            if count > MAX_FILES:
                raise ValueError("Too many files in skill tree")
            relative = path.relative_to(folder).as_posix().encode("utf-8")
            content_hash = hashlib.sha256(path.read_bytes()).digest()
            digest.update(len(relative).to_bytes(8, "big") + relative + content_hash)
    return digest.hexdigest()


def check(roots: list[Path], catalogue: dict, selected: list[str], baseline: dict | None = None) -> dict:
    entries = catalogue["skills"]
    unknown = sorted(set(selected) - set(entries))
    if unknown or not selected:
        raise ValueError(f"Select known skill names; unknown: {', '.join(unknown)}")
    if baseline is not None:
        if (baseline.get("schema_version") != 1 or baseline.get("workflow_version") != catalogue["workflow_version"]
                or baseline.get("source") != catalogue["source"]["repository"]
                or not isinstance(baseline.get("skills"), dict)):
            raise ValueError("Baseline is not an inventory for this workflow/source; review before replacing it")
    index: dict[str, list[tuple[Path, bool]]] = {}
    scan_errors = []
    for path in discover(roots):
        try:
            name, disabled = metadata(path)
            index.setdefault(name, []).append((path, disabled))
        except (ValueError, OSError, UnicodeError) as exc:
            scan_errors.append(f"{path}: {exc}")
    results = {}
    for name in sorted(set(selected)):
        spec = entries[name]
        candidates = index.get(name, [])
        result = {"status": "MISSING", "expected_invocation": spec["invocation"],
                  "paths": [str(path) for path, _ in candidates], "issues": [], "fingerprint": None}
        results[name] = result
        if not candidates:
            continue
        if len(candidates) > 1:
            result["status"] = "AMBIGUOUS"
            result["issues"].append("Multiple physical copies; resolve using host inventory, not name precedence guesses")
            continue
        path, disabled = candidates[0]
        result["status"] = "ON_DISK"
        expected_disabled = spec["invocation"] == "manual"
        if disabled != expected_disabled:
            result["status"] = "POLICY_MISMATCH"
            result["issues"].append("Invocation flag differs from the reviewed catalogue")
        missing = [name for name in spec["required_files"] if not (path.parent / name).is_file()]
        if missing:
            result["status"] = "INCOMPLETE"
            result["issues"].append("Missing required files: " + ", ".join(missing))
        try:
            result["fingerprint"] = fingerprint(path.parent)
        except (ValueError, OSError) as exc:
            result["status"] = "UNVERIFIED"
            result["issues"].append(str(exc))
        if baseline is not None:
            previous = baseline["skills"].get(name, {})
            old_hash = previous.get("fingerprint")
            if (previous.get("status") != "ON_DISK" or not isinstance(old_hash, str)
                    or not re.fullmatch(r"[0-9a-f]{64}", old_hash)):
                result["issues"].append("No usable entry in the approved baseline")
                if result["status"] == "ON_DISK":
                    result["status"] = "NO_BASELINE"
            elif old_hash != result["fingerprint"]:
                result["issues"].append("Skill content differs from baseline; compatibility review required")
                if result["status"] == "ON_DISK":
                    result["status"] = "CHANGED"
    ok = not scan_errors and all(row["status"] == "ON_DISK" for row in results.values())
    return {"schema_version": 1, "workflow_version": catalogue["workflow_version"],
            "source": catalogue["source"]["repository"], "disk_check_passed": ok,
            "runtime_status": "NOT_CHECKED", "source_authenticity": "NOT_CHECKED",
            "baseline_comparison": "CHECKED" if baseline is not None else "NOT_REQUESTED",
            "scan_errors": scan_errors, "skills": results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, action="append", required=True,
                        help="Actual installed skill/collection root; repeat for multiple active roots")
    parser.add_argument("--profile", choices=("collection", "routed"), default="collection")
    parser.add_argument("--only", nargs="+", help="Check only these catalogue skill names")
    parser.add_argument("--baseline", type=Path, help="Previously reviewed/approved JSON inventory; never rewritten")
    parser.add_argument("--json", action="store_true", help="Emit inventory JSON on stdout; saves nothing itself")
    args = parser.parse_args()
    try:
        catalogue = json.loads(CATALOGUE.read_text(encoding="utf-8"))
        selected = args.only or [name for name, row in catalogue["skills"].items()
                                if args.profile == "collection" or row["invocation"] == "model"]
        baseline = json.loads(args.baseline.read_text(encoding="utf-8-sig")) if args.baseline else None
        result = check(args.root, catalogue, selected, baseline)
    except (OSError, UnicodeError, ValueError, KeyError, TypeError, AttributeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for name, row in result["skills"].items():
            print(f"{row['status']}: {name}")
            for issue in row["issues"]:
                print(f"  {issue}")
        for issue in result["scan_errors"]:
            print(f"SCAN_ERROR: {issue}")
        print("NOT CHECKED: host discovery/enabled state, permissions, source authenticity, invocation and behavior.")
    return 0 if result["disk_check_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
