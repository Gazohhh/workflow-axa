#!/usr/bin/env python3
"""Validate this package's structure and links; not host behavior or full YAML schemas."""

from __future__ import annotations

import argparse
import hashlib
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
    "skills/workflow/ARTIFACTS.md", "skills/workflow/scripts/global_policy.py",
    "skills/workflow/WRITING.md", "skills/workflow/OPTIONAL-HELPERS.md",
    "tools/visual_regression.py", "tests/behavioral/cases.json", "tests/behavioral/README.md",
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
    "skills/task-status/SKILL.md", "skills/task-status/agents/openai.yaml",
    "skills/resume-task/SKILL.md", "skills/resume-task/agents/openai.yaml",
    "skills/workflow-doctor/SKILL.md", "skills/workflow-doctor/agents/openai.yaml",
    "skills/rule-maker/SKILL.md", "skills/rule-maker/agents/openai.yaml",
    "skills/rule-maker/rules/START.md", "skills/rule-maker/rules/CORE.md",
    "skills/rule-maker/rules/READINESS.md", "skills/rule-maker/SETUP.md",
    "skills/rule-maker/scripts/activate_rules.py", "skills/rule-maker/scripts/readiness.py",
    "skills/workflow/RULES.md", "skills/rule-maker/scripts/version_facts.py",
    "skills/rule-maker/rules/ENGINEERING.md", "skills/rule-maker/rules/VERSIONS.md",
    "skills/rule-maker/rules/php.md", "skills/rule-maker/rules/laravel.md", "skills/rule-maker/rules/rust.md",
    "skills/rule-maker/rules/data-contracts.md", "skills/rule-maker/rules/lifetimes.md",
    "skills/rule-maker/rules/reliability.md", "skills/rule-maker/rules/testing.md",
    "skills/rule-maker/rules/security.md", "skills/rule-maker/rules/performance.md", "skills/rule-maker/rules/compatibility.md",
    "tests/test_version_facts.py", "tests/test_engineering_rules.py", "tests/behavioral/engineering-rules.json",
    "skills/plan-review/SKILL.md", "skills/plan-review/agents/openai.yaml",
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
        expected_registered = ["./skills/workflow", "./skills/codebase-map", "./skills/task-status", "./skills/resume-task", "./skills/workflow-doctor", "./skills/plan-review", "./skills/rule-maker"]
        if plugin.get("skills") != expected_registered:
            errors.append("Register the seven workflow-axa skills exactly once in the approved order.")
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

    try:
        library = root / "skills/rule-maker/rules"
        rules = json.loads((library / "version.json").read_text(encoding="utf-8"))
        names = rules.get("files", [])
        actual = {p.name for p in library.glob("*.md")}
        if (rules.get("schema_version") != 1 or not isinstance(names, list)
                or any(not isinstance(name, str) or Path(name).name != name for name in names)
                or len(names) != len(set(names)) or set(names) != actual):
            errors.append("Shared rules manifest must list each bundled Markdown module exactly once.")
        elif rules.get("package_version") != plugin.get("version"):
            errors.append("Shared rules package version must match the plugin.")
        elif not isinstance(rules.get("sha256"), dict) or set(rules["sha256"]) != actual:
            errors.append("Shared rules hash inventory must match every bundled module.")
        else:
            for name in names:
                source = library / name
                if source.is_symlink() or hashlib.sha256(source.read_bytes()).hexdigest() != rules["sha256"][name]:
                    errors.append(f"Shared rules fingerprint mismatch: {name}")
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        errors.append(f"Shared rules manifest error: {exc}")

    registered_names = ("workflow", "codebase-map", "task-status", "resume-task", "workflow-doctor", "plan-review", "rule-maker")
    expected_skills = {root / f"skills/{name}/SKILL.md" for name in registered_names}
    if set((root / "skills").rglob("SKILL.md")) != expected_skills:
        errors.append("Exactly the seven registered workflow-axa SKILL.md files are required.")
    budgets = {"workflow": 1250, "codebase-map": 850, "task-status": 450, "resume-task": 500, "workflow-doctor": 450, "plan-review": 550, "rule-maker": 850}
    for name in registered_names:
        budget = budgets[name]
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

    skill_roots = [root / f"skills/{name}" for name in ("workflow", "codebase-map", "task-status", "resume-task", "workflow-doctor", "plan-review", "rule-maker")]
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
    print(f"PASS: package structure, manifest consistency, minimal metadata, seven local skills, relative links, core budget ({words} workflow words).")
    print("NOT RUN: Claude/Codex host validation and live behavioral evaluations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
