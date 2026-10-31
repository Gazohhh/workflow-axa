#!/usr/bin/env python3
"""Check selected design-kit references; never approve designs or write project files."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import stat
import sys
from pathlib import Path

MAX_FILE = 2_000_000
MAX_TOTAL = 32_000_000
TOP = {"schema_version", "kit_id", "revision", "status", "scope", "approval", "preview", "items"}
ITEM = {"id", "kind", "name", "purpose", "status", "scope", "sources", "approval", "variants", "states", "uses"}
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}\Z")
HASH = re.compile(r"[a-f0-9]{64}\Z")


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON field: {key}")
        result[key] = value
    return result


def text(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 4000 or any(ord(c) < 32 for c in value):
        raise ValueError(f"Invalid {label}.")
    return value


def path_value(value):
    text(value, "relative path")
    if "\\" in value or ":" in value or value.startswith("/") or any(c in value for c in "*?[]"):
        raise ValueError("Use literal repository-relative forward-slash paths, not URLs or globs.")
    path = Path(value)
    if ".." in path.parts:
        raise ValueError("Path traversal is not allowed.")
    return path


def string_list(value, label, *, nonempty=False):
    if not isinstance(value, list) or len(value) > 256 or (nonempty and not value):
        raise ValueError(f"Invalid {label} list.")
    values = [text(v, label) for v in value]
    if len(set(values)) != len(values):
        raise ValueError(f"Duplicate {label}.")
    return values


def scopes(value):
    return [path_value(v) for v in string_list(value, "scope", nonempty=True)]


def reference(value, *, optional=False):
    if value is None and optional:
        return
    if not isinstance(value, dict) or set(value) != {"path", "sha256"}:
        raise ValueError("Reference must contain exactly path and sha256.")
    path_value(value["path"])
    if not isinstance(value["sha256"], str) or not HASH.fullmatch(value["sha256"]):
        raise ValueError("Reference needs a SHA-256 fingerprint of the actual inspected file.")


class Reader:
    def __init__(self, root: Path):
        self.root = root.expanduser().absolute()
        for part in (self.root, *self.root.parents):
            if part.is_symlink() or (part.exists() and getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("Linked/junction root needs manual review.")
        if not self.root.is_dir():
            raise ValueError("Root must be an existing directory.")
        self.root = self.root.resolve()
        self.total = 0
        self.cache = {}

    def read(self, relative: str):
        p = self.root / path_value(relative)
        if not p.resolve().is_relative_to(self.root):
            raise ValueError("Reference leaves the supplied root.")
        if p in self.cache:
            return self.cache[p]
        for part in (p, *p.parents):
            if part == self.root.parent:
                break
            if part.is_symlink() or (part.exists() and getattr(part.lstat(), "st_file_attributes", 0) & 0x400):
                raise ValueError("Linked/junction reference needs manual review.")
        info = p.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_size > MAX_FILE:
            raise ValueError("Reference is not a bounded ordinary file.")
        with p.open("rb") as stream:
            raw = stream.read(MAX_FILE + 1)
        self.total += len(raw)
        if len(raw) > MAX_FILE or self.total > MAX_TOTAL:
            raise ValueError("Reference input size limit exceeded.")
        self.cache[p] = raw
        return raw

    def match(self, ref):
        return hashlib.sha256(self.read(ref["path"])).hexdigest() == ref["sha256"]


def covered(requested: Path, allowed: list[Path]) -> bool:
    return any(requested == p or requested.is_relative_to(p) for p in allowed)


def validate(data):
    if not isinstance(data, dict) or set(data) != TOP or type(data["schema_version"]) is not int or data["schema_version"] != 1:
        raise ValueError("Unknown or incomplete catalogue schema/fields.")
    if not ID.fullmatch(text(data["kit_id"], "kit identity")):
        raise ValueError("Invalid kit identity.")
    text(data["revision"], "revision")
    if data["status"] not in ("draft", "approved", "deprecated"):
        raise ValueError("Unknown catalogue status.")
    kit_scope = scopes(data["scope"])
    reference(data["approval"], optional=True)
    reference(data["preview"], optional=True)
    if data["status"] == "approved" and (data["approval"] is None or data["preview"] is None):
        raise ValueError("Approved catalogue requires authority and preview-boundary references.")
    entries = data["items"]
    if not isinstance(entries, list) or len(entries) > 256:
        raise ValueError("Invalid item list.")
    rows = {}
    for item in entries:
        if not isinstance(item, dict) or set(item) != ITEM:
            raise ValueError("Unknown or incomplete item fields.")
        key = text(item["id"], "item identity")
        if not ID.fullmatch(key) or key in rows:
            raise ValueError("Invalid or duplicate item identity.")
        text(item["name"], "name"); text(item["purpose"], "purpose")
        if item["kind"] not in ("component", "pattern", "tokens") or item["status"] not in ("candidate", "approved", "deprecated"):
            raise ValueError("Unknown item kind/status.")
        allowed = scopes(item["scope"])
        if any(not covered(p, kit_scope) for p in allowed):
            raise ValueError("Item scope exceeds the catalogue's scope.")
        if not isinstance(item["sources"], list) or len(item["sources"]) > 32:
            raise ValueError("Invalid sources list.")
        for source in item["sources"]:
            reference(source)
        source_paths = [Path(r["path"]).as_posix() for r in item["sources"]]
        if len(source_paths) != len(set(source_paths)):
            raise ValueError("Duplicate source path.")
        reference(item["approval"], optional=True)
        if item["status"] == "approved" and (not item["sources"] or item["approval"] is None):
            raise ValueError("Approved entry requires actual source and separate approval reference.")
        for name in ("variants", "states", "uses"):
            string_list(item[name], name)
        rows[key] = item
    for item in rows.values():
        if set(item["uses"]) - rows.keys():
            raise ValueError("Unknown composition/dependency identity.")
    active, done = set(), set()
    def visit(key):
        if key in active:
            raise ValueError("Cyclic component/pattern dependencies.")
        if key in done:
            return
        active.add(key)
        for other in rows[key]["uses"]:
            visit(other)
        active.remove(key); done.add(key)
    for key in rows:
        visit(key)
    return rows


def inspect(root: Path, catalogue: str, selected=(), scope_values=()):
    reader = Reader(root)
    raw = reader.read(catalogue)
    data = json.loads(raw.decode("utf-8-sig"), object_pairs_hook=unique_object)
    return inspect_data(reader, data, raw, selected, scope_values)


def inspect_data(reader: Reader, data: dict, raw: bytes, selected=(), scope_values=()):
    """Check a saved catalogue or a report's projection of an authoritative local record."""
    rows = validate(data)
    selection = list(dict.fromkeys(selected)) if selected else list(rows)
    if any(key not in rows for key in selection):
        raise ValueError("Requested item does not exist in this catalogue.")
    requested = [path_value(p) for p in scope_values]
    relevant = set()
    def add(key):
        if key in relevant:
            return
        relevant.add(key)
        for child in rows[key]["uses"]:
            add(child)
    for key in selection:
        add(key)
    blocked, pending = [], []
    if data["status"] == "deprecated":
        blocked.append("Catalogue is deprecated; no automatic replacement is authorised.")
    elif data["status"] != "approved":
        pending.append("Catalogue is a draft; no design approval established.")
    if any(not covered(p, scopes(data["scope"])) for p in requested):
        blocked.append("Requested scope is outside this catalogue.")
    for name in ("approval", "preview"):
        if data[name] is not None and not reader.match(data[name]):
            blocked.append(f"Catalogue {name} reference is stale.")
    details = []
    for key in sorted(relevant):
        row = rows[key]
        issues = []
        if row["status"] == "deprecated":
            issues.append("Deprecated entry cannot supply active design authority.")
        if any(not covered(p, scopes(row["scope"])) for p in requested):
            issues.append("Requested scope not covered by this entry.")
        for ref in row["sources"] + ([row["approval"]] if row["approval"] is not None else []):
            if not reader.match(ref):
                issues.append("Stale reference: " + ref["path"])
        if issues:
            blocked.extend(f"{key}: {message}" for message in issues)
        elif row["status"] != "approved":
            pending.append(f"{key}: candidate has no usable design approval.")
        details.append({"id": key, "declared_status": row["status"], "problems": issues})
    if not relevant:
        pending.append("No catalogue entries; no approved component coverage.")
    state = "BLOCKED" if blocked else "DRAFT" if pending else "REVIEW_REQUIRED"
    return {"schema_version": 1, "state": state, "kit_id": data["kit_id"], "revision": data["revision"],
            "catalogue_sha256": hashlib.sha256(raw).hexdigest(), "selected": selection, "checked_items": details,
            "scope_coverage_checked": bool(requested), "blockers": blocked, "pending": pending,
            "approval_authenticated": False, "implementation_approved": False, "runtime_verified": False,
            "limits": "Only listed local references checked; read the actual decision, API and style dependencies. No automatic design approval, component execution, complete dependency discovery or preview-isolation proof."}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--item", action="append", default=[])
    parser.add_argument("--scope", action="append", default=[])
    args = parser.parse_args(argv)
    try:
        result = inspect(args.root, args.catalog, args.item, args.scope)
        print(json.dumps(result, indent=2))
        return {"REVIEW_REQUIRED": 0, "DRAFT": 1, "BLOCKED": 2}[result["state"]]
    except (OSError, ValueError, UnicodeError, TypeError, RecursionError) as exc:
        print(json.dumps({"state": "BLOCKED", "reason": str(exc), "approval_authenticated": False, "implementation_approved": False}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
