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
# Files this validator itself reads. Which skills, hooks, assets and tests must exist is asserted independently by
# tests/test_package_contract.py, so a deleted file can't validate itself away (REDESIGN.md §11, G2/G5).
BASE_FILES = (".claude-plugin/plugin.json", ".claude-plugin/marketplace.json", "README.md", "CHANGELOG.md",
              "UPGRADE.md", "VALIDATION.md", "VENDORED-SKILLS.md", "CONTEXT.md", "skills/rule-maker/rules/version.json")
# One default ceiling per kind of file, advisory: a file above it is printed as a NOTE, never a failure (G5).
SKILL_CEILING = 2200
REFERENCE_CEILING = 3300


SKILL_ENTRY = re.compile(r"\./skills/([a-z0-9][a-z0-9-]*)")


def skill_entries(root: Path) -> list:
    try:
        entries = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8")).get("skills")
    except (OSError, ValueError, AttributeError):
        return []
    return entries if isinstance(entries, list) else []


def manifest_entry_errors(root: Path) -> list[str]:
    """plugin.json `skills` must be a non-empty list of unique `./skills/<name>` strings. Checked before any entry is
    used as a path, so a malformed entry (absolute, `..`, not a string) is never read."""
    entries = skill_entries(root)
    bad = [entry for entry in entries if not isinstance(entry, str) or not SKILL_ENTRY.fullmatch(entry)]
    errors = [f"plugin.json skill entry {json.dumps(entry)} is not ./skills/<name>." for entry in bad]
    if not entries:
        errors.append("plugin.json must register its skills as a non-empty list.")
    duplicates = sorted({e for e in entries if isinstance(e, str) and entries.count(e) > 1})
    errors += [f"plugin.json registers {entry} more than once." for entry in duplicates]
    return errors


def registered_names(root: Path) -> tuple[str, ...]:
    """The skills plugin.json registers, in its order; only well-formed `./skills/<name>` entries."""
    return tuple(found[1] for entry in skill_entries(root)
                 if isinstance(entry, str) and (found := SKILL_ENTRY.fullmatch(entry)))


def credit_rows(root: Path) -> list[tuple[list[str], list[str]]]:
    """VENDORED-SKILLS.md's credits table: per row, the backticked skill names (first column) and the backticked
    licence paths (third column), where `<name>` stands for each name of the row."""
    rows = []
    for line in (root / "VENDORED-SKILLS.md").read_text(encoding="utf-8").splitlines():
        cells = line.strip().strip("|").split("|")
        if line.startswith("|") and len(cells) >= 3 and not set(cells[0].strip()) <= {"-", " "}:
            names = re.findall(r"`([a-z0-9][a-z0-9-]*)`", cells[0])
            paths = [p for p in re.findall(r"`([^`]+)`", cells[2]) if p.endswith("LICENSE")]
            if names:
                rows.append((names, paths))
    return rows


def licensed_skills(root: Path) -> list[str]:
    """The formerly copied skills, from the credits table."""
    return sorted({name for names, _ in credit_rows(root) for name in names})


def licence_files(root: Path) -> list[str]:
    """Every licence file the credits table names: the licence requires the notice to travel with the text."""
    return sorted({p.replace("<name>", name) if "<name>" in p else p
                   for names, paths in credit_rows(root) for name in names for p in paths})


SYNONYMS_FAIL = False  # G4: a rejected CONTEXT.md synonym in skill prose is an advisory NOTE.
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


FLOWS = "skills/workflow/flows"
FLOW_KEYS = ("name", "uses", "fallbacks", "approval-exceptions")


def flow_index_errors(root: Path, registered: tuple[str, ...]) -> list[str]:
    """C-FLOW-1: every INDEX.md row names an existing recipe and every recipe has a row (INDEX.md and TEMPLATE.md
    excluded); each recipe's frontmatter has exactly name (its file name), uses (registered skills), fallbacks and
    approval-exceptions, and never routing signals, which live only in the index."""
    folder = root / FLOWS
    if not folder.is_dir():
        return []
    index = folder / "INDEX.md"
    if not index.is_file():
        return [f"{FLOWS}/INDEX.md is missing; the router reads only the index."]
    errors = []
    rows = {}
    for line in index.read_text(encoding="utf-8").splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")] if line.startswith("|") else []
        link = re.fullmatch(r"\[([\w.-]+\.md)\]\(([\w.-]+\.md)\)", cells[-1]) if len(cells) == 3 else None
        if link:
            if cells[0] in rows or link[2] in rows.values():
                errors.append(f"{FLOWS}/INDEX.md lists '{cells[0]}' ({link[2]}) more than once.")
            rows[cells[0]] = link[2]
            if link[1] != link[2] or Path(link[2]).stem != cells[0]:
                errors.append(f"{FLOWS}/INDEX.md: row '{cells[0]}' must link its own file {cells[0]}.md.")
    files = sorted(p.name for p in folder.glob("*.md") if p.name not in ("INDEX.md", "TEMPLATE.md"))
    for name, file in rows.items():
        if not (folder / file).is_file():
            errors.append(f"{FLOWS}/INDEX.md lists {file}, which does not exist.")
    for file in files:
        if file not in rows.values():
            errors.append(f"{FLOWS}/{file} has no row in INDEX.md.")
            continue
        text = (folder / file).read_text(encoding="utf-8")
        found = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
        fields = dict(re.findall(r"^([\w-]+):\s*(.*)$", found[1], re.M)) if found else {}
        if sorted(fields) != sorted(FLOW_KEYS):
            errors.append(f"{FLOWS}/{file}: frontmatter must have exactly {', '.join(FLOW_KEYS)} (signals belong in "
                          f"INDEX.md); it has {', '.join(sorted(fields)) or 'none'}.")
            continue
        if fields["name"] != Path(file).stem:
            errors.append(f"{FLOWS}/{file}: name must be {Path(file).stem}.")
        uses = re.fullmatch(r"\[([^\]]*)\]", fields["uses"].strip())
        for skill in [s.strip() for s in uses[1].split(",") if s.strip()] if uses else [None]:
            if skill not in registered:
                errors.append(f"{FLOWS}/{file}: uses names {skill!r}, which is not a registered skill.")
        fallbacks = re.fullmatch(r"\[([^\]]+)\]", fields["fallbacks"].strip())
        if not fallbacks or not fields["approval-exceptions"].strip():
            errors.append(f"{FLOWS}/{file}: fallbacks must list at least one name and approval-exceptions must be set.")
    return errors


def ceiling_notes(root: Path) -> list[str]:
    """Advisory: SKILL.md files above SKILL_CEILING words and reference files above REFERENCE_CEILING words."""
    notes = []
    for relative, path in _skill_markdown(root):
        words = len(path.read_text(encoding="utf-8").split())
        ceiling = SKILL_CEILING if path.name == "SKILL.md" else REFERENCE_CEILING
        if words > ceiling:
            notes.append(f"skills/{relative}: {words} words, above the {ceiling}-word default ceiling")
    return notes


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
    notes: list[str] = ceiling_notes(root)
    if not SYNONYMS_FAIL and (root / "CONTEXT.md").is_file():
        notes += synonym_findings(root)
    return notes


def validate_package(root: Path) -> list[str]:
    errors: list[str] = []
    root = root.resolve()
    for name in BASE_FILES:
        if not (root / name).is_file():
            errors.append(f"Missing required file: {name}")
    errors += manifest_entry_errors(root)
    if errors:
        return errors
    skill_names = registered_names(root)
    required = BASE_FILES + tuple(f"skills/{name}/{file}" for name in skill_names for file in ("SKILL.md", "agents/openai.yaml"))
    # Archived skills' licences live under docs/archive/, which the source checkout has and the shipped package
    # leaves out; there they are required, and every shipped licence is required everywhere.
    has_archive = (root / "docs/archive").is_dir()
    required += tuple(p for p in licence_files(root) if has_archive or not p.startswith("docs/archive/"))
    if any(not paths for _, paths in credit_rows(root)):
        errors.append("VENDORED-SKILLS.md: every credits row names its licence file in the third column.")
    for name in required:
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

    expected_skills = {root / f"skills/{name}/SKILL.md" for name in skill_names}
    if set((root / "skills").rglob("SKILL.md")) != expected_skills:
        errors.append(f"Exactly the {len(skill_names)} SKILL.md files plugin.json registers are required.")
    for name in skill_names:
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
        metadata = (root / f"skills/{name}/agents/openai.yaml").read_text(encoding="utf-8")
        match = re.fullmatch(r'interface:\n  display_name: ("[^\n]+")\n  short_description: ("[^\n]+")\n'
                             r'(policy:\n  allow_implicit_invocation: false\n)?', metadata)
        user_only = "\ndisable-model-invocation: true\n" in core.split("\n---\n", 1)[0] + "\n"
        if not match:
            errors.append(f"{name}: unexpected minimal OpenAI metadata shape.")
        elif bool(match.group(3)) != user_only:
            errors.append(f"{name}: SKILL.md's disable-model-invocation and agents/openai.yaml's "
                          "allow_implicit_invocation: false must agree (both user-only, or neither).")
        else:
            try:
                if not all(json.loads(value).strip() for value in match.groups()[:2]):
                    errors.append(f"{name}: empty OpenAI display string.")
            except (ValueError, AttributeError) as exc:
                errors.append(f"{name}: invalid OpenAI string: {exc}")

    skill_roots = [root / f"skills/{name}" for name in skill_names]
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

    errors += repeat_notes(root)  # A8: a paragraph repeated across skill files fails validation
    errors += flow_index_errors(root, skill_names)
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
                                  len(skill_names), len(licensed_skills(root)))
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
    count = len(registered_names(args.root.resolve()))
    print(f"PASS: package structure, manifest consistency, minimal metadata, {count} local skills, relative links ({words} workflow words).")
    print("NOT RUN: Claude/Codex host validation and live behavioral evaluations.")
    for note in notes:
        print(f"NOTE: {note}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
