#!/usr/bin/env python3
"""Validate this package's structure and links; not host behavior or full YAML schemas."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {".git", "__pycache__", ".artifacts", ".local-fixtures"}
REQUIRED = (
    ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
    "README.md", "CHANGELOG.md", "VALIDATION.md", "docs/DESIGN.md",
    "skills/workflow/SKILL.md", "skills/workflow/TASK-FOLDER.md",
    "skills/workflow/QUESTIONS.md", "skills/workflow/AUDIT.md",
    "skills/workflow/PDF-DELIVERABLE.md", "skills/workflow/CHATGPT-PROMPTS.md",
    "skills/workflow/agents/openai.yaml", "tests/README.md", "tests/SCENARIOS.md",
    "tools/create_fixture.py", "skills/workflow/SPECIALISTS.md", "skills/workflow/SETUP.md",
    "skills/workflow/specialists.json", "skills/workflow/scripts/check_specialists.py",
    "tests/test_specialists.py", "tests/test_reports.py", "tools/browser_smoke.py",
    "skills/workflow/GROUNDING.md", "skills/workflow/VISUAL-REVIEW.md",
    "skills/workflow/templates/PROJECT-ROUTING.md", "skills/codebase-map/SKILL.md",
    "skills/codebase-map/REPORT.md", "skills/codebase-map/FLOWCHART-DESIGN.md", "skills/codebase-map/agents/openai.yaml",
    "skills/codebase-map/scripts/render_report.py", "skills/codebase-map/assets/report.css",
    "skills/codebase-map/assets/report.js", "skills/codebase-map/examples/review.json",
    "skills/codebase-map/examples/review.html",
)


def validate_package(root: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    for name in REQUIRED:
        if not (root / name).is_file():
            errors.append(f"Missing required file: {name}")
    if errors:
        return errors

    plugin = {}
    try:
        plugin = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        market = json.loads((root / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
        if plugin.get("name") != "workflow-axa":
            errors.append("Plugin name must stay workflow-axa.")
        version = plugin.get("version", "")
        if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
            errors.append("Plugin version must use the package's semantic-version format.")
        elif f"## {version} —" not in (root / "CHANGELOG.md").read_text(encoding="utf-8"):
            errors.append("Plugin version has no matching changelog entry.")
        if plugin.get("skills") != ["./skills/workflow", "./skills/codebase-map"]:
            errors.append("Register workflow and codebase-map exactly once.")
        entries = market.get("plugins", [])
        if len(entries) != 1 or entries[0].get("name") != "workflow-axa" or entries[0].get("source") != "./":
            errors.append("Marketplace must point to this one local plugin.")
    except (ValueError, TypeError, AttributeError, OSError) as exc:
        errors.append(f"Manifest error: {exc}")

    try:
        catalogue = json.loads((root / "skills/workflow/specialists.json").read_text(encoding="utf-8"))
        if catalogue.get("workflow_version") != plugin.get("version"):
            errors.append("Specialist catalogue version must match plugin version.")
        if catalogue.get("schema_version") != 1 or not catalogue.get("skills"):
            errors.append("Specialist catalogue schema/skills are missing.")
        routes = (root / "skills/workflow/SPECIALISTS.md").read_text(encoding="utf-8")
        for name, row in catalogue["skills"].items():
            if row.get("invocation") not in {"model", "manual"}:
                errors.append(f"Unknown specialist invocation policy: {name}")
            if row.get("invocation") == "model" and f"`{name}`" not in routes:
                errors.append(f"Missing explicit specialist route: {name}")
            if not row.get("required_files") or "SKILL.md" not in row["required_files"]:
                errors.append(f"Specialist entrypoint not required: {name}")
            for relative in row.get("required_files", []):
                if Path(relative).is_absolute() or ".." in Path(relative).parts:
                    errors.append(f"Unsafe specialist reference: {name}/{relative}")
    except (ValueError, TypeError, AttributeError, KeyError, OSError) as exc:
        errors.append(f"Specialist catalogue error: {exc}")

    expected_skills = {root / f"skills/{name}/SKILL.md" for name in ("workflow", "codebase-map")}
    if set((root / "skills").rglob("SKILL.md")) != expected_skills:
        errors.append("Exactly the registered workflow and codebase-map SKILL.md files are required.")
    for name, budget in (("workflow", 1200), ("codebase-map", 800)):
        core = (root / f"skills/{name}/SKILL.md").read_text(encoding="utf-8")
        header = re.match(r'\A---\nname: ' + re.escape(name) + r'\ndescription: ("[^\n]+")\n---\n', core)
        if not header:
            errors.append(f"{name}: skill metadata needs its name and JSON-quoted description.")
        else:
            try:
                description = json.loads(header[1])
                if not description.strip() or len(description) > 1024 or "<" in description or ">" in description:
                    errors.append(f"{name}: invalid description length/markup.")
            except ValueError as exc:
                errors.append(f"{name}: invalid quoted description: {exc}")
        if len(core.split()) > budget:
            errors.append(f"{name}: exceeds the team's {budget}-word maintenance budget.")
        metadata = (root / f"skills/{name}/agents/openai.yaml").read_text(encoding="utf-8")
        match = re.fullmatch(r'interface:\n  display_name: ("[^\n]+")\n  short_description: ("[^\n]+")\n', metadata)
        if not match:
            errors.append(f"{name}: unexpected minimal OpenAI metadata shape.")
        else:
            try:
                if not all(json.loads(value).strip() for value in match.groups()):
                    errors.append(f"{name}: empty OpenAI display string.")
            except (ValueError, AttributeError) as exc:
                errors.append(f"{name}: invalid OpenAI string: {exc}")

    skill_roots = [root / "skills/workflow", root / "skills/codebase-map"]
    for path in sorted(root.rglob("*.md")):
        if any(part in IGNORED for part in path.relative_to(root).parts):
            continue
        text = path.read_text(encoding="utf-8-sig")
        text = re.sub(r"^```.*?^```[^\n]*$", "", text, flags=re.M | re.S)
        for target in re.findall(r"\[[^\]\n]*\]\(([^)\n]+)\)", text):
            target = target.strip().split(' "', 1)[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("#") or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if not resolved.is_relative_to(root) or not resolved.exists():
                errors.append(f"Broken/outside relative link in {path.relative_to(root)}: {target}")
            elif any(path.is_relative_to(sr) and not resolved.is_relative_to(sr) for sr in skill_roots):
                errors.append(f"Skill reference escapes the separately installable skill folder: {target}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        errors = validate_package(args.root)
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1
    words = len((args.root / "skills/workflow/SKILL.md").read_text(encoding="utf-8").split())
    print(f"PASS: package structure, manifest consistency, minimal metadata, two skills, relative links, core budget ({words} words).")
    print("NOT RUN: Claude/Codex host validation and live behavioral evaluations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
