#!/usr/bin/env python3
"""Freeze record-backed report prose into a new draft JSON, or check it for drift.

Only fields whose locator explicitly opts into `heading:...` or `ticket:...` are
projected. Other fields remain authored by the agent. This tool never edits the
records, the input JSON, or an existing/approved visual-review snapshot.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills/workflow/scripts"))
from ticket_records import parse, section_text  # noqa: E402


class ProjectionError(ValueError):
    pass


def _markdown_text(lines: list[str]) -> str:
    """Keep punctuation, bullets and commands as evidence, despite plain-text display."""
    return "\n".join(line.rstrip() for line in lines).strip()


def _heading(text: str, title: str) -> str:
    lines = text.splitlines()
    heads = []
    fence = None
    for n, line in enumerate(lines):
        marker = re.match(r"^\s*(`{3,}|~{3,})", line)
        if marker:
            fence = None if fence == marker[1][0] else marker[1][0] if fence is None else fence
            continue
        if fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if match:
            heads.append((n, len(match[1]), match[2].strip()))
    found = [(n, level) for n, level, name in heads if name.casefold() == title.casefold()]
    if len(found) != 1:
        raise ProjectionError(f'Heading {title!r} occurs {len(found)} times (expected exactly once)')
    start, level = found[0]
    end = next((n for n, depth, _ in heads if n > start and depth <= level), len(lines))
    result = _markdown_text(lines[start + 1:end])
    if not result:
        raise ProjectionError(f'Heading {title!r} has no content')
    return result


def _ticket(text: str, identifier: str) -> tuple[str, str]:
    lines = text.splitlines()
    matching = [ticket for ticket in parse(lines) if ticket.qualified == identifier]
    if len(matching) != 1:
        raise ProjectionError(f'Ticket {identifier!r} occurs {len(matching)} times (expected exactly once)')
    item = matching[0]
    if item.mark is not None:
        raise ProjectionError(f'Ticket {identifier!r} is a legacy checkbox; write a labelled ticket first')
    visible = set(range(len(lines)))
    sections = {}
    for name in ("what needs to happen", "what should work", "technical details", "how to verify"):
        sections[name] = _markdown_text(section_text(lines, visible, item.start, item.end, name))
    if not sections["what needs to happen"] or not sections["what should work"]:
        raise ProjectionError(f'Ticket {identifier!r} needs both What needs to happen and What should work')
    spec = "\n\n".join(
        f'{name.capitalize()}:\n{sections[name]}' for name in
        ("what needs to happen", "technical details", "how to verify") if sections[name]
    )
    return spec, sections["what should work"]


def _record(task_folder: Path, sources: dict, source_id: str) -> str:
    entry = sources.get(source_id)
    if not entry:
        raise ProjectionError(f'Unknown source ID {source_id!r}')
    raw = entry.get("path")
    if not isinstance(raw, str) or not raw or Path(raw).is_absolute() or Path(raw).suffix != ".md":
        raise ProjectionError(f'Source {source_id!r} must name a relative Markdown record')
    path = task_folder / raw
    if path.is_symlink() or not path.resolve().is_relative_to(task_folder.resolve()):
        raise ProjectionError(f'Source {source_id!r} escapes the task folder')
    if not path.is_file():
        raise ProjectionError(f'Missing source {source_id!r}: {raw}')
    return path.read_text(encoding="utf-8")


def project(data: dict, task_folder: Path) -> tuple[dict, list[str]]:
    """Return a copied report and opt-in field changes; never invent authority or checks."""
    output = json.loads(json.dumps(data))
    source_list = output.get("sources", [])
    if not isinstance(source_list, list):
        raise ProjectionError('sources must be a list')
    sources = {entry["id"]: entry for entry in source_list}
    if len(sources) != len(source_list):
        raise ProjectionError('Source IDs must be unique')
    report = output.get("task_report")
    if not isinstance(report, dict):
        raise ProjectionError('Input needs a task_report; see TASK-REPORT.md')
    changes = []
    for section in report.get("sections", []):
        locator = section.get("locator", "")
        if not locator.startswith("heading:"):
            continue
        value = _heading(_record(task_folder, sources, section["source"]), locator[len("heading:"):].strip())
        if section.get("text") != value:
            changes.append(f'task_report.sections[{section["id"]}].text')
            section["text"] = value
    for ticket in report.get("tickets", []):
        locator = ticket.get("locator", "")
        if not locator.startswith("ticket:"):
            continue
        identifier = locator[len("ticket:"):].strip()
        record = sources.get(ticket["source"], {})
        if Path(record.get("path", "")).name != "TODO.md":
            raise ProjectionError(f'Ticket {identifier!r} must cite TODO.md')
        spec, expected = _ticket(_record(task_folder, sources, ticket["source"]), identifier)
        for key, value in (("specification", spec), ("expected", expected)):
            if ticket.get(key) != value:
                changes.append(f'task_report.tickets[{ticket["task"]}].{key}')
                ticket[key] = value
    return output, changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--task", type=Path, required=True, help="Existing folder containing PLAN/TODO records")
    parser.add_argument("--input", type=Path, required=True, help="Unapproved report input JSON")
    choice = parser.add_mutually_exclusive_group(required=True)
    choice.add_argument("--check", action="store_true", help="Report stale projected fields without writing")
    choice.add_argument("--output", type=Path, help="Write a new, never-overwritten draft JSON")
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding="utf-8"))
        if data.get("state") != "draft":
            raise ProjectionError('Projection requires state=draft; presented reports are immutable')
        updated, changes = project(data, args.task)
        if args.check:
            if changes:
                print("DRIFT: " + ", ".join(changes))
                return 1
            print("OK: opt-in report fields match their source records")
            return 0
        target = args.output
        if target.resolve() == args.input.resolve() or target.exists() or target.is_symlink():
            raise ProjectionError('Output must be a new file; snapshots and input are never overwritten')
        # Exclusive creation prevents a concurrent writer from replacing an approved report.
        with target.open("x", encoding="utf-8") as stream:
            json.dump(updated, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        print(f'Created draft {target}; {len(changes)} sourced field(s) refreshed')
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f'REFUSED: {exc}', file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
