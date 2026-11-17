#!/usr/bin/env python3
"""The machine's workflow-axa settings: `~/.workflow-axa/settings.json` (REDESIGN.md §3.6, contract C-CSS-1).

This is the only code that reads the file. It holds two settings:
- the CSS switch, `{"css": "on"}` or `{"css": "off"}`: a missing or unreadable file, invalid JSON, a non-object or any
  other value means **off**; a project can only be stricter: a line `css: never` in its DESIGN.md (root or docs/) turns
  it off there; `on` lets an approved change include styling; DESIGN.md defines what counts as styling;
- the default debate depth of /spar, `{"spar": {"default_depth": ...}}`: quick, normal, thorough or a
  whole number from 1 (the old names standard and deep mean normal and thorough); missing means normal, an invalid
  saved value means normal with a notice. A depth named in
  the /spar command overrides it without saving.

usage:
  settings.py show [--root PROJECT]        print the machine setting and, with --root, the effective one
  settings.py css on|off                  change the machine setting (the owner runs this, or approves it)
  settings.py init                        create the file with css off, only when it does not exist yet
  settings.py spar depth <depth>          change the default /spar depth (the owner runs this, or asks for it)

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
DEPTHS = ("quick", "normal", "thorough")
OLD_DEPTHS = {"standard": "normal", "deep": "thorough"}
DEPTH_HELP = "quick, normal, thorough or a whole number from 1 to 999999"
WHOLE = re.compile(r"[1-9][0-9]{0,5}")
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


def depth_value(value) -> str | None:
    """A valid /spar depth as text, or None: a named depth, or a whole number from 1 (as a number or digits)."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value) if 1 <= value < 10 ** 6 else None
    if isinstance(value, str):
        if value in DEPTHS:
            return value
        if value in OLD_DEPTHS:
            return OLD_DEPTHS[value]
        if WHOLE.fullmatch(value):
            return value
    return None


def spar_depth(path: Path | None = None) -> tuple[str, str | None]:
    """The default /spar effort and, when the saved value isn't valid, a notice saying so (then: normal). The old
    names standard and deep read as normal and thorough."""
    try:
        data = json.loads((path or settings_path()).read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError):
        return "normal", None
    spar = data.get("spar") if isinstance(data, dict) else None
    if not isinstance(spar, dict) or "default_depth" not in spar:
        return "normal", None
    depth = depth_value(spar["default_depth"])
    if depth is None:
        return "normal", (f"spar.default_depth {spar['default_depth']!r} is not a valid depth ({DEPTH_HELP}); "
                          "using normal")
    return depth, None


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
    spar = sub.add_parser("spar")
    spar.add_argument("setting", choices=("depth",))
    spar.add_argument("value")
    args = parser.parse_args(argv)
    path = settings_path(args.file)
    if args.command == "show":
        depth, notice = spar_depth(path)
        out = {"file": str(path), "exists": path.is_file(), **read(path), "spar_default_depth": depth}
        if notice:
            out["spar_notice"] = notice
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
    if args.command == "spar":
        depth = depth_value(args.value)
        if depth is None:
            print(f"REFUSED: {args.value!r} is not a /spar depth; use {DEPTH_HELP}", file=sys.stderr)
            return 2
        try:
            current = json.loads(path.read_text(encoding="utf-8")).get("spar")
        except (OSError, ValueError, UnicodeError, AttributeError):
            current = None
        write(path, {"spar": {**(current if isinstance(current, dict) else {}), "default_depth": depth}})
        print(f"/spar now defaults to depth {depth} on this machine ({path})")
        return 0
    write(path, {"css": args.value})
    print(f"css is now {args.value} for every project on this machine ({path})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
