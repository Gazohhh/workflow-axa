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
SKILL_BUDGETS = {'workflow': 700, 'codebase-map': 850, 'task-status': 450, 'resume-task': 500, 'workflow-doctor': 450, 'plan-review': 550, 'rule-maker': 850, 'ui-design': 850, 'workflow-clarify': 850, 'workflow-specify': 850, 'workflow-execute': 900, 'workflow-deliver': 850, 'grilling': 1350, 'tdd': 850, 'code-review': 1550, 'writing-for-agents': 2150, 'codebase-design': 1100, 'domain-modeling': 700, 'implement-spec': 650, 'retro': 1050, 'simple-english': 1450}
REGISTERED_NAMES = tuple(SKILL_BUDGETS)
REQUIRED = (
    "skills/ui-design/LIVE-KIT.md", "skills/ui-design/scripts/inspect_kit_index.py",
    "skills/codebase-map/scripts/kit_bindings.py", "tests/test_strict_kit.py", "tests/test_kit_index.py",
    "skills/codebase-map/UI-FLOW.md", "skills/codebase-map/scripts/screen_flow.py",
    "skills/codebase-map/assets/ui-review.css", "skills/codebase-map/assets/ui-review.js",
    "skills/rule-maker/AUDIT.md", "skills/rule-maker/INSTALLATION.md",
    "skills/rule-maker/scripts/audit_installation.py", "skills/rule-maker/rules/POLICY.md",
    "skills/rule-maker/rules/operations.md", "skills/rule-maker/rules/angular.md",
    "skills/rule-maker/rules/ionic.md", "skills/rule-maker/rules/capacitor.md",
    "skills/ui-design/KIT.md", "skills/ui-design/CATALOGUE.md",
    "skills/ui-design/templates/KIT.md", "skills/ui-design/templates/DESIGN.md", "skills/ui-design/templates/design-kit.json",
    "skills/ui-design/scripts/check_design_kit.py", "tests/test_design_kit.py", "tests/test_rules_audit.py",

    ".claude-plugin/plugin.json", ".claude-plugin/marketplace.json",
    "README.md", "CHANGELOG.md", "VALIDATION.md", "docs/DESIGN.md",
    "skills/workflow/SKILL.md", "skills/workflow/TASK-FOLDER.md",
    "skills/workflow/AUDIT.md",
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
    "skills/ui-design/SKILL.md", "skills/ui-design/agents/openai.yaml",
    "skills/ui-design/CONTRACT.md", "skills/ui-design/VERIFY.md", "skills/ui-design/EXAMPLES.md",
    "skills/ui-design/scripts/review_ui_diff.py", "tests/test_ui_design.py", "tests/behavioral/ui-design.json",
)
REQUIRED += tuple(f"skills/{name}/{file}" for name in REGISTERED_NAMES for file in ("SKILL.md", "agents/openai.yaml"))
REQUIRED += ("VENDORED-SKILLS.md", "skills/retro/scripts/digest_sessions.py", "skills/workflow/scripts/open_items.py", "skills/workflow/scripts/record.py", "skills/codebase-map/scripts/screenshot_report.py", "tests/test_screenshot_report.py", "tests/test_open_items.py", "tests/test_record.py", "tools/vendor_specialists.py", "tests/test_vendored_specialists.py", "skills/ui-design/scripts/class_rules.py", "tests/test_class_rules.py", "hooks/phase_reads.py", "tests/test_phase_reads_hook.py", "hooks/plain_reply.py", "tests/test_plain_reply_hook.py")
REQUIRED += ("skills/codebase-map/assets/report-style.css", "skills/codebase-map/assets/report-style-compat.css", "skills/codebase-map/assets/report-extra.js", "tests/test_simple_english.py", "skills/simple-english/LICENSE")
REQUIRED += ("skills/workflow/scripts/ticket_records.py", "skills/workflow/examples/readable-todo.md", "RC3-CASES.md", "tests/test_rc3_reliability.py")
REQUIRED += ("skills/codebase-map/TASK-REPORT.md", "skills/codebase-map/scripts/task_report.py", "skills/codebase-map/assets/task-report.css", "tests/test_task_report.py")


_UNITS = ("one", "two", "three", "four", "five", "six", "seven", "eight", "nine")
NUMBER_WORDS = {word: i + 1 for i, word in enumerate(_UNITS)}
NUMBER_WORDS.update({w: i + 10 for i, w in enumerate(("ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
                                                      "sixteen", "seventeen", "eighteen", "nineteen"))})
for _tens, _base in (("twenty", 20), ("thirty", 30)):
    NUMBER_WORDS[_tens] = _base
    NUMBER_WORDS.update({f"{_tens}-{unit}": _base + i + 1 for i, unit in enumerate(_UNITS)})
_COUNT = "(\\d+|" + "|".join(sorted(NUMBER_WORDS, key=len, reverse=True)) + ")"
# A total: "21 skills", "twenty-one registered skills", "all twenty complete skill folders".
TOTAL_RE = re.compile(rf"\b{_COUNT}\s+(?:(?:registered|complete|installable|local|bundled|separate)\s+)*"
                      r"(?:skills|skill folders)\b", re.I)  # a bare "N folders" is not a skill count
VENDORED_RE = re.compile(rf"\b{_COUNT}\s+vendored\b", re.I)
_VERSION = r"(\d+\.\d+\.\d+(?:-[0-9A-Za-z.]*[0-9A-Za-z])?)"
PACKAGE_RE = re.compile(r"\bworkflow[ -]axa\s*(?:—|–|-|:)?\s*v?" + _VERSION, re.I)
RULES_RE = re.compile(r"\b(?:rules|library)\b(?:\s+library)?\s*\(?\s*" + _VERSION, re.I)
SECTION_VERSION_RE = re.compile(r"\b(?:\d+\.\d+\.\d+(?:-rc\.\d+)?|rc\.\d+)\b")


def _current_sections(text: str, version: str) -> str:
    """Drop `##` sections whose heading names only an older release; they are history."""
    kept = []
    for part in re.split(r"(?m)^(?=## )", text):
        heading = part.split("\n", 1)[0]
        if heading.startswith("## ") and SECTION_VERSION_RE.search(heading) and version not in heading:
            continue
        kept.append(part)
    return "".join(kept)


def doc_fact_errors(root: Path, version: str, rules_version: str, skills: int, vendored: int) -> list[str]:
    """Hand-kept counts and versions in the user-facing docs must match the manifests."""
    errors: list[str] = []
    validation = (root / "VALIDATION.md").read_text(encoding="utf-8")
    current = re.search(r"\A# [^\n]*\n\n(## Current verification\n.*?)(?=\n## History)", validation, re.S)
    if not current:
        errors.append("VALIDATION.md must open with '## Current verification' followed by a '## History' heading.")
    scoped = {
        "README.md": (root / "README.md").read_text(encoding="utf-8"),
        "CHANGELOG.md": _current_sections((root / "CHANGELOG.md").read_text(encoding="utf-8"), version),
        "UPGRADE.md": _current_sections((root / "UPGRADE.md").read_text(encoding="utf-8"), version),
        "VENDORED-SKILLS.md": (root / "VENDORED-SKILLS.md").read_text(encoding="utf-8"),
        "VALIDATION.md": current[1] if current else "",
    }
    for name, text in scoped.items():
        text = re.sub(r"^```.*?^```[^\n]*$", "", text, flags=re.M | re.S)
        expected = vendored if name == "VENDORED-SKILLS.md" else skills
        for match in TOTAL_RE.finditer(text):
            count = int(match[1]) if match[1].isdigit() else NUMBER_WORDS[match[1].lower()]
            if count != expected:
                errors.append(f"{name} states {count} skills ('{match[0]}'); the package has {expected}.")
        for match in VENDORED_RE.finditer(text):
            count = int(match[1]) if match[1].isdigit() else NUMBER_WORDS[match[1].lower()]
            if count != vendored:
                errors.append(f"{name} states {count} vendored skills ('{match[0]}'); the package has {vendored}.")
        for match in PACKAGE_RE.finditer(text):
            if match[1] != version:
                errors.append(f"{name} states package {match[1]} ('{match[0]}'); plugin.json says {version}.")
        for match in RULES_RE.finditer(text):
            if match[1] != rules_version:
                errors.append(f"{name} states rules {match[1]} ('{match[0]}'); version.json says {rules_version}.")
    return errors


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
        expected_registered = [f"./skills/{name}" for name in REGISTERED_NAMES]
        if plugin.get("skills") != expected_registered:
            errors.append("Register the twenty-one workflow-axa skills exactly once in the approved order.")
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

    registered_names = REGISTERED_NAMES
    expected_skills = {root / f"skills/{name}/SKILL.md" for name in registered_names}
    if set((root / "skills").rglob("SKILL.md")) != expected_skills:
        errors.append("Exactly the twenty-one registered workflow-axa SKILL.md files are required.")
    budgets = SKILL_BUDGETS
    for name in registered_names:
        budget = budgets[name]
        core = (root / f"skills/{name}/SKILL.md").read_text(encoding="utf-8")
        header = re.match(r'\A---\nname: ' + re.escape(name) + r'\ndescription: ("[^\n]+")\n(?:disable-model-invocation: true\n)?---\n', core)
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

    skill_roots = [root / f"skills/{name}" for name in REGISTERED_NAMES]
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

    try:
        rules_version = json.loads((root / "skills/rule-maker/rules/version.json").read_text(encoding="utf-8")).get(
            "rules_version", "")
        # Each vendored skill folder carries its upstream LICENSE (VENDORED-SKILLS.md); our own folders do not.
        vendored = sum((root / f"skills/{name}/LICENSE").is_file() for name in REGISTERED_NAMES)
        errors += doc_fact_errors(root, str(plugin.get("version", "")), str(rules_version),
                                  len(REGISTERED_NAMES), vendored)
    except (OSError, ValueError, AttributeError) as exc:
        errors.append(f"Documentation facts error: {exc}")
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
    print(f"PASS: package structure, manifest consistency, minimal metadata, twenty-one local skills, relative links, core budget ({words} workflow words).")
    print("NOT RUN: Claude/Codex host validation and live behavioral evaluations.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
