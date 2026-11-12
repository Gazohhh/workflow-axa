#!/usr/bin/env python3
"""Validate this package's structure and links; not host behavior or full YAML schemas."""

from __future__ import annotations

import argparse
import functools
import hashlib
import importlib.util
import json
import re
import sys
from dataclasses import dataclass
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
    "skills/rule-maker/rules/OPERATIONS.md", "skills/rule-maker/rules/ANGULAR.md",
    "skills/rule-maker/rules/IONIC.md", "skills/rule-maker/rules/CAPACITOR.md",
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
    "tests/test_reports.py", "tools/browser_smoke.py",
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
    "skills/rule-maker/rules/PHP.md", "skills/rule-maker/rules/LARAVEL.md", "skills/rule-maker/rules/RUST.md",
    "skills/rule-maker/rules/data-contracts.md", "skills/rule-maker/rules/LIFETIMES.md",
    "skills/rule-maker/rules/RELIABILITY.md", "skills/rule-maker/rules/TESTING.md",
    "skills/rule-maker/rules/SECURITY.md", "skills/rule-maker/rules/PERFORMANCE.md", "skills/rule-maker/rules/COMPATIBILITY.md",
    "tests/test_version_facts.py", "tests/test_engineering_rules.py", "tests/behavioral/engineering-rules.json",
    "skills/plan-review/SKILL.md", "skills/plan-review/agents/openai.yaml",
    "skills/ui-design/SKILL.md", "skills/ui-design/agents/openai.yaml",
    "skills/ui-design/CONTRACT.md", "skills/ui-design/VERIFY.md", "skills/ui-design/EXAMPLES.md",
    "skills/ui-design/scripts/review_ui_diff.py", "tests/test_ui_design.py", "tests/behavioral/ui-design.json",
)
REQUIRED += tuple(f"skills/{name}/{file}" for name in REGISTERED_NAMES for file in ("SKILL.md", "agents/openai.yaml"))
REQUIRED += ("VENDORED-SKILLS.md", "skills/retro/scripts/digest_sessions.py", "skills/workflow/scripts/open_items.py", "skills/workflow/scripts/record.py", "skills/codebase-map/scripts/screenshot_report.py", "tests/test_screenshot_report.py", "tests/test_open_items.py", "tests/test_record.py", "skills/ui-design/scripts/class_rules.py", "tests/test_class_rules.py", "hooks/phase_reads.py", "tests/test_phase_reads_hook.py", "hooks/plain_reply.py", "tests/test_plain_reply_hook.py",
             "hooks/duplicate_skills.py", "tests/test_duplicate_skills_hook.py")
REQUIRED += ("skills/codebase-map/assets/report-style.css", "skills/codebase-map/assets/report-style-compat.css", "skills/codebase-map/assets/report-extra.js", "tests/test_simple_english.py", "skills/simple-english/LICENSE")
REQUIRED += ("skills/workflow/scripts/ticket_records.py", "skills/workflow/examples/readable-todo.md", "docs/archive/RC3-CASES.md", "tests/test_rc3_reliability.py")
REQUIRED += ("skills/codebase-map/TASK-REPORT.md", "skills/codebase-map/scripts/task_report.py", "skills/codebase-map/assets/task-report.css", "tests/test_task_report.py")
REQUIRED += ("CONTEXT.md", "tests/test_validate_budgets.py", "tests/test_owned_skills.py")
# Skills that began as copies of MIT-licensed projects (VENDORED-SKILLS.md credits them). They are our own text now;
# each folder keeps its LICENSE because the licence requires the copyright notice to travel with the text.
FORMERLY_COPIED = ("grilling", "tdd", "code-review", "writing-for-agents", "codebase-design", "domain-modeling",
                   "implement-spec", "retro", "simple-english")
REQUIRED += tuple(f"skills/{name}/LICENSE" for name in FORMERLY_COPIED)

# Word ceilings for the reference .md files under skills/ (path below skills/), excluding SKILL.md files. Each
# ceiling is the file's final size after the 2026-11-11 wording work plus 5 percent, rounded up to the next ten
# (the formerly copied skills' files: their 2026-11-12 size, when they became our own text, plus 5 percent). Where that came out above the earlier headroom ceiling, the
# earlier ceiling stays (rule-maker/rules/DESIGN.md, workflow/SETUP.md, workflow/VISUAL-REVIEW.md).
REFERENCE_BUDGETS = {
    'codebase-map/DIAGRAM-DESIGN.md': 50, 'codebase-map/examples/FINDINGS.md': 90, 'codebase-map/examples/PLAN.md': 150,
    'codebase-map/examples/README.md': 230, 'codebase-map/examples/STATUS.md': 270, 'codebase-map/examples/TODO.md': 80,
    'codebase-map/examples/ui-review/README.md': 320, 'codebase-map/examples/ui-review/UI-FINDINGS.md': 100,
    'codebase-map/examples/ui-review/UI-PLAN.md': 210, 'codebase-map/examples/ui-review/UI-TODO.md': 90,
    'codebase-map/FLOWCHART-DESIGN.md': 1460, 'codebase-map/REPORT.md': 2440, 'codebase-map/TASK-REPORT.md': 2160,
    # AUDIT.md (next line) holds rule additions from the 2026-11-11 V1 review: 929 words, ceiling about 5 percent above.
    'codebase-map/UI-FLOW.md': 2790, 'rule-maker/AUDIT.md': 970, 'rule-maker/CHECKER.md': 750,
    # DOCS.md (next line) holds rule additions from the 2026-11-11 V1 review: 1,272 words plus 5 percent.
    'rule-maker/DOCS.md': 1340, 'rule-maker/INSTALLATION.md': 630, 'rule-maker/rules/ANGULAR.md': 340,
    # CHANGES.md (next line) is the rules history file and grows each release: 972 words at 1.8.7 plus 5 percent.
    'rule-maker/rules/CAPACITOR.md': 340, 'rule-maker/rules/CHANGES.md': 1020, 'rule-maker/rules/COMPATIBILITY.md': 330,
    'rule-maker/rules/CORE.md': 690, 'rule-maker/rules/data-contracts.md': 360, 'rule-maker/rules/DESIGN.md': 1130,
    'rule-maker/rules/ENGINEERING.md': 490, 'rule-maker/rules/IONIC.md': 310, 'rule-maker/rules/LARAVEL.md': 420,
    'rule-maker/rules/LIFETIMES.md': 340, 'rule-maker/rules/OPERATIONS.md': 420, 'rule-maker/rules/PERFORMANCE.md': 350,
    'rule-maker/rules/PHP.md': 340, 'rule-maker/rules/PIXIJS.md': 130, 'rule-maker/rules/POLICY.md': 450,
    'rule-maker/rules/REACT.md': 260, 'rule-maker/rules/READINESS.md': 1600, 'rule-maker/rules/RELIABILITY.md': 330,
    'rule-maker/rules/RUST.md': 340, 'rule-maker/rules/SECURITY.md': 350, 'rule-maker/rules/SOURCES.md': 730,
    'rule-maker/rules/START.md': 600, 'rule-maker/rules/TESTING.md': 390, 'rule-maker/rules/THREEJS.md': 130,
    'rule-maker/rules/TYPESCRIPT.md': 230, 'rule-maker/rules/UNITY.md': 210, 'rule-maker/rules/VERSIONS.md': 550,
    'rule-maker/rules/VITE.md': 140, 'rule-maker/SETUP.md': 760, 'ui-design/CATALOGUE.md': 540,
    'ui-design/CONTRACT.md': 550, 'ui-design/EXAMPLES.md': 450, 'ui-design/KIT.md': 1040, 'ui-design/LIVE-KIT.md': 3010,
    'ui-design/templates/DESIGN.md': 730, 'ui-design/templates/KIT.md': 260, 'ui-design/VERIFY.md': 1050,
    'workflow/ARTIFACTS.md': 930, 'workflow/AUDIT.md': 1710, 'workflow/CHATGPT-PROMPTS.md': 230,
    'workflow/examples/readable-todo.md': 590, 'workflow/GROUNDING.md': 500, 'workflow/OPTIONAL-HELPERS.md': 390,
    'workflow/PDF-DELIVERABLE.md': 1040, 'workflow/RULES.md': 220, 'workflow/SETUP.md': 2310,
    'workflow/SPECIALISTS.md': 820, 'workflow/TASK-FOLDER.md': 3290, 'workflow/templates/PROJECT-ROUTING.md': 820,
    'workflow/VISUAL-REVIEW.md': 2120, 'workflow/WRITING.md': 690,
    'codebase-design/DEEPENING.md': 410, 'codebase-design/DESIGN-IT-TWICE.md': 430,
    'domain-modeling/ADR-FORMAT.md': 460, 'domain-modeling/GLOSSARY-FORMAT.md': 360,
    'simple-english/references/rule-catalog.md': 1820, 'simple-english/references/strict-vocabulary.md': 960,
    'simple-english/references/use-cases.md': 620, 'simple-english/references/word-swaps.md': 520,
    'tdd/mocking.md': 220, 'tdd/tests.md': 310, 'writing-for-agents/SKILL-MECHANICS.md': 440,
}
SYNONYMS_FAIL = True  # A rejected CONTEXT.md synonym in skill prose fails validation.
REPEAT_WORDS = 25


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


@functools.cache
def _docs_check():
    """skills/rule-maker/scripts/docs_check.py, loaded by path: its repeated-paragraph function is reused here."""
    name = "workflow_axa_docs_check"
    spec = importlib.util.spec_from_file_location(name, ROOT / "skills/rule-maker/scripts/docs_check.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses look their module up while the file runs
    spec.loader.exec_module(module)
    return module


def _skill_markdown(root: Path) -> list[tuple[str, Path]]:
    """(path below skills/, file) of each .md under skills/."""
    found = []
    for path in sorted((root / "skills").rglob("*.md")):
        if any(part in IGNORED for part in path.relative_to(root).parts):
            continue
        found.append((path.relative_to(root / "skills").as_posix(), path))
    return found


def reference_files(root: Path) -> dict[str, int]:
    """Word count of each reference file: a skill .md that is not SKILL.md."""
    return {relative: len(path.read_text(encoding="utf-8").split())
            for relative, path in _skill_markdown(root) if path.name != "SKILL.md"}


def reference_budget_errors(root: Path) -> list[str]:
    errors, files = [], reference_files(root)
    for relative, words in files.items():
        budget = REFERENCE_BUDGETS.get(relative)
        if budget is None:
            errors.append(f"skills/{relative}: no word budget; add one to REFERENCE_BUDGETS in tools/validate.py.")
        elif words > budget:
            errors.append(f"skills/{relative}: {words} words exceed its {budget}-word budget.")
    for relative in sorted(set(REFERENCE_BUDGETS) - set(files)):
        errors.append(f"skills/{relative}: has a word budget in tools/validate.py but no file.")
    return errors


def repeat_notes(root: Path) -> list[str]:
    """Paragraphs of REPEAT_WORDS or more words that appear in two or more skill .md files. Each one fails validation."""
    files = dict((path, relative) for relative, path in _skill_markdown(root))
    notes = []
    for repeat in _docs_check().repeated_paragraphs(list(files), REPEAT_WORDS):
        places = ", ".join(f"skills/{files[path]}:{line}" for path, line in repeat.places)
        words = repeat.text.split()
        notes.append(f"repeated paragraph ({len(words)} words) in {places}: \"{' '.join(words[:8])} ...\"")
    return notes


@dataclass(frozen=True)
class Vocabulary:
    terms: list[str]  # case-folded
    avoid: dict[str, str]  # case-folded rejected synonym -> its term
    identifiers: list[str]  # exact forms a hook, script, test or record depends on
    owners: list[tuple[str, str]]  # (rule, owner file)


def read_vocabulary(root: Path) -> Vocabulary:
    """Parse CONTEXT.md: `**Term**:` lines with an `_Avoid_: a, b` line under `## Language`, the backticked list
    items under `## Identifiers that keep their form`, and the two-column table under `## Rule owners`."""
    terms, avoid, identifiers, owners = [], {}, [], []
    section = ""
    for number, line in enumerate((root / "CONTEXT.md").read_text(encoding="utf-8").splitlines(), 1):
        if line.startswith("## "):
            section = line[3:].strip()
        elif section == "Language" and (term := re.fullmatch(r"\*\*(.+?)\*\*:\s*", line)):
            terms.append(term[1].casefold())
        elif section == "Language" and (rejected := re.fullmatch(r"_Avoid_:\s*(.+)", line)):
            if not terms:
                raise ValueError(f"CONTEXT.md:{number}: an _Avoid_ line needs a **Term**: line above it")
            for word in rejected[1].split(","):
                if word.strip():
                    avoid[word.strip().casefold()] = terms[-1]
        elif section == "Identifiers that keep their form" and (item := re.match(r"- `([^`]+)`", line)):
            identifiers.append(item[1])
        elif section == "Rule owners" and line.startswith("|"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) == 2 and re.fullmatch(r"`[^`]+`", cells[1]):
                owners.append((cells[0], cells[1].strip("`")))
    return Vocabulary(terms, avoid, identifiers, owners)


def vocabulary_errors(root: Path) -> list[str]:
    vocabulary, errors = read_vocabulary(root), []
    if not vocabulary.terms or not vocabulary.owners:
        errors.append("CONTEXT.md needs its ## Language terms and its ## Rule owners table.")
    for word in sorted(set(vocabulary.avoid) & {identifier.casefold() for identifier in vocabulary.identifiers}):
        errors.append(f"CONTEXT.md lists '{word}' both as a rejected synonym and as an identifier.")
    for rule, owner in vocabulary.owners:
        if not (root / owner).is_file():
            errors.append(f"CONTEXT.md names a missing owner file for '{rule}': {owner}")
    return errors


def synonym_findings(root: Path) -> list[str]:
    """Each CONTEXT.md rejected synonym in skill .md prose: outside code, HTML comments and the identifiers that keep
    their form."""
    vocabulary, docs_check, findings = read_vocabulary(root), _docs_check(), []
    patterns = {word: re.compile(r"(?<![\w-])" + r"\s+".join(map(re.escape, word.split())) + r"(?![\w-])", re.I)
                for word in vocabulary.avoid}
    masked = [re.compile(re.escape(identifier), re.I) for identifier in vocabulary.identifiers
              if any(pattern.search(identifier) for pattern in patterns.values())]
    for relative, path in _skill_markdown(root):
        lines = docs_check.prose_lines(path.read_text(encoding="utf-8-sig"))
        for number, line in enumerate(lines, 1):
            for identifier in masked:
                line = identifier.sub(lambda found: " " * len(found[0]), line)
            for word, pattern in patterns.items():
                for _ in pattern.finditer(line):
                    findings.append(f"synonym '{word}' (use '{vocabulary.avoid[word]}') in skills/{relative}:{number}")
    return findings


def package_notes(root: Path) -> list[str]:
    """Advisory findings printed as NOTE lines; they never fail validation."""
    root = root.resolve()
    notes: list[str] = []
    if not SYNONYMS_FAIL and (root / "CONTEXT.md").is_file():
        notes += synonym_findings(root)
    return notes


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

    errors += reference_budget_errors(root)
    errors += repeat_notes(root)  # A8: a paragraph repeated across skill files fails validation
    try:
        errors += vocabulary_errors(root)
        if SYNONYMS_FAIL:
            errors += synonym_findings(root)
    except (OSError, ValueError) as exc:
        errors.append(f"CONTEXT.md error: {exc}")

    try:
        rules_version = json.loads((root / "skills/rule-maker/rules/version.json").read_text(encoding="utf-8")).get(
            "rules_version", "")
        errors += doc_fact_errors(root, str(plugin.get("version", "")), str(rules_version),
                                  len(REGISTERED_NAMES), len(FORMERLY_COPIED))
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
    try:
        notes = package_notes(args.root)
    except (OSError, UnicodeError, ValueError) as exc:
        notes = [f"advisory reports not produced: {exc}"]
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        for note in notes:
            print(f"NOTE: {note}")
        return 1
    words = len((args.root / "skills/workflow/SKILL.md").read_text(encoding="utf-8").split())
    print(f"PASS: package structure, manifest consistency, minimal metadata, twenty-one local skills, relative links, core budget ({words} workflow words).")
    print("NOT RUN: Claude/Codex host validation and live behavioral evaluations.")
    for note in notes:
        print(f"NOTE: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
