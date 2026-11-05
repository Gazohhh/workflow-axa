#!/usr/bin/env python3
"""Compare two lists of failing tests by identity, not by count. Read-only.

usage: python -X utf8 -I compare_failures.py <baseline.txt> <now.txt>

Each file has one failing test per line: `<test id><TAB><first error line>`. A failure is EXISTING only when the
same test fails with the same first error line. Prints NEW, CHANGED, FIXED and an EXISTING count; exits 1 when
anything is NEW or CHANGED (audit E11: five existing failures becoming four plus one new passed as unchanged).
"""
from __future__ import annotations

import sys
from pathlib import Path


class BadInput(ValueError):
    pass


def read(path: Path) -> dict[str, str]:
    """Failing tests by ID. A BOM is ignored; a missing tab, a duplicate ID or an unreadable file is refused."""
    try:
        text = path.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        raise BadInput(f"{path}: cannot read as UTF-8 ({exc.__class__.__name__})") from exc
    failures = {}
    for number, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        if "\t" not in line:
            raise BadInput(f"{path} line {number}: expected `<test id><TAB><first error line>`")
        test, _, error = line.partition("\t")
        test = test.strip()
        if test in failures:
            raise BadInput(f"{path} line {number}: duplicate test id {test!r}")
        failures[test] = " ".join(error.split())
    return failures


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2
    try:
        before, after = read(Path(argv[1])), read(Path(argv[2]))
    except BadInput as exc:
        print(f"BLOCKED: {exc}")
        return 2
    new = sorted(set(after) - set(before))
    fixed = sorted(set(before) - set(after))
    changed = sorted(t for t in set(before) & set(after) if before[t] != after[t])
    existing = len(set(before) & set(after)) - len(changed)
    for test in new:
        print(f"NEW {test}: {after[test]}")
    for test in changed:
        print(f"CHANGED {test}: was {before[test]!r}, now {after[test]!r}")
    for test in fixed:
        print(f"FIXED {test}")
    print(f"EXISTING {existing} (same test, same first error line)")
    return 1 if new or changed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
