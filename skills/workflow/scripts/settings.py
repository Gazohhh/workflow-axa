#!/usr/bin/env python3
"""The machine's workflow-axa settings: `~/.workflow-axa/settings.json` (REDESIGN.md §3.6, contract C-CSS-1).

This is the only code that reads the file. Today it holds one switch, `{"css": "on"}` or `{"css": "off"}`:
- a missing or unreadable file, invalid JSON, a non-object or any other value means **off**;
- a project can only be stricter: a line `css: never` in its DESIGN.md (root or docs/) turns it off there;
- `on` lets an approved change include styling; DESIGN.md defines what counts as styling.

usage:
  settings.py show [--root PROJECT]        print the machine setting and, with --root, the effective one
  settings.py css on|off                  change the machine setting (the owner runs this, or approves it)
  settings.py init                        create the file with css off, only when it does not exist yet

`--file PATH` (or WORKFLOW_AXA_SETTINGS) points at another settings file, for tests. Changing the setting is a
protected operation: in a workflow session the hook allows an agent to run `css on|off` only after the owner's Yes to
that exact question.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

VALUES = ("on", "off")
DEFAULT = {"css": "off"}
NEVER = re.compile(r"^\s*(?:[-*]\s*)?css\s*:\s*never\b", re.I | re.M)
FENCE = re.compile(r"^\s*(`{3,}|~{3,})")


def settings_path(explicit: str | os.PathLike | None = None) -> Path:
    if explicit:
        return Path(explicit)
    if os.environ.get("WORKFLOW_AXA_SETTINGS"):
        return Path(os.environ["WORKFLOW_AXA_SETTINGS"])
    return Path.home() / ".workflow-axa" / "settings.json"


def read(path: Path | None = None) -> dict:
    """The machine settings, every unknown or broken value replaced by its safe default (off)."""
    try:
        data = json.loads((path or settings_path()).read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return dict(DEFAULT)
    if not isinstance(data, dict):
        return dict(DEFAULT)
    css = data.get("css")
    return {"css": css if css in VALUES else "off"}


def project_never(root: Path) -> bool:
    """The project's DESIGN.md (root or docs/) says `css: never` outside code blocks. A DESIGN.md that exists but
    can't be read counts as `css: never`: an unknown project policy never lets the machine switch allow styling."""
    for candidate in (root / "DESIGN.md", root / "docs" / "DESIGN.md"):
        if not os.path.lexists(candidate):
            continue
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return True
        kept, fence = [], ""
        for line in text.splitlines():
            found = FENCE.match(line)
            if fence:
                fence = "" if found and found.group(1)[0] == fence[0] else fence
                continue
            if found:
                fence = found.group(1)
                continue
            kept.append(re.sub(r"`[^`\n]*`", "", line))
        if NEVER.search("\n".join(kept)):
            return True
    return False


def css_allowed(root: Path | None = None, path: Path | None = None) -> bool:
    """Whether styling may be written now: the machine switch is on and the project doesn't say `css: never`."""
    return read(path)["css"] == "on" and not (root is not None and project_never(root))


def write(path: Path, data: dict) -> None:
    """Replace the file atomically, keeping keys this version doesn't know."""
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        existing = json.loads(path.read_text(encoding="utf-8"))
        existing = existing if isinstance(existing, dict) else {}
    except (OSError, ValueError, UnicodeError):
        existing = {}
    existing.update(data)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix=".settings-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(json.dumps(existing, indent=2) + "\n")
        os.replace(name, path)
        name = None
    finally:
        if name and os.path.exists(name):
            os.unlink(name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", help="settings file (default ~/.workflow-axa/settings.json or WORKFLOW_AXA_SETTINGS)")
    sub = parser.add_subparsers(dest="command", required=True)
    show = sub.add_parser("show")
    show.add_argument("--root", type=Path)
    css = sub.add_parser("css")
    css.add_argument("value", choices=VALUES)
    sub.add_parser("init")
    args = parser.parse_args(argv)
    path = settings_path(args.file)
    if args.command == "show":
        out = {"file": str(path), "exists": path.is_file(), **read(path)}
        if args.root:
            out["project_css_never"] = project_never(args.root)
            out["css_allowed_here"] = css_allowed(args.root, path)
        print(json.dumps(out, indent=2))
        return 0
    if args.command == "init":
        if path.exists():
            print(f"KEPT: {path} exists; nothing changed")
            return 0
        write(path, DEFAULT)
        print(f"CREATED: {path} with css off")
        return 0
    write(path, {"css": args.value})
    print(f"css is now {args.value} for every project on this machine ({path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
