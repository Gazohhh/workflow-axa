"""No line points at SIMPLE-ENGLISH.md for a rule that moved to WRITING.md
(docs/plans/2026-11-17-plain-owner-questions R3, T2).

Every tracked text line in the searched paths that names the old file must be on KEEP: it concerns what
SIMPLE-ENGLISH.md still holds (its Strict and CHECK modes, its references, its licence and credit). A new mention,
even in a kept file, fails until someone decides which kind it is.
"""
from __future__ import annotations

import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERN = "SIMPLE-" + "ENGLISH"
PATHS = ("skills", "hooks", "tests", "tools", "docs", "CONTEXT.md", "README.md", "AGENTS.md", "VENDORED-SKILLS.md")
EXCLUDED = ("docs/plans/", "docs/archive/")
TEXT_SUFFIXES = (".md", ".py", ".json", ".yaml", ".yml", ".txt", ".html", ".css", ".js")

KEEP = {
    ("AGENTS.md", "(its folder, its archive copy, or beside SIMPLE-ENGLISH.md) and keep the"),
    ("AGENTS.md", "Covers: skills/grilling/, skills/tdd/, skills/code-review/, skills/writing-for-agents/, skills/codebase-design/, skills/domain-modeling/, skills/workflow/SIMPLE-ENGLISH.md, docs/archive/skills/"),
    ("skills/workflow/SIMPLE-ENGLISH.md", "<!-- Reference text, formerly the simple-english skill (unregistered in 2.9.0); licence: SIMPLE-ENGLISH.LICENSE, credits: VENDORED-SKILLS.md. -->"),
    ("tests/test_owned_skills.py", 'self.assertIn("MIT License", (ROOT / "skills/workflow/SIMPLE-ENGLISH.LICENSE").read_text(encoding="utf-8"))'),
    ("tests/test_package_contract.py", "# skills/workflow/SIMPLE-ENGLISH.LICENSE (KEY_FILES). test_owned_skills checks the archive copies."),
    ("tests/test_release.py", 'self.assertIn("skills/workflow/SIMPLE-ENGLISH.md", self.names)'),
    ("tests/test_release.py", 'self.assertIn("skills/workflow/SIMPLE-ENGLISH.LICENSE", self.names)'),
    ("tests/test_release.py", 'shipped = (ROOT / "skills/workflow/SIMPLE-ENGLISH.md").read_text(encoding="utf-8")'),
    ("tests/test_simple_english.py", 'TEXT = ROOT / "skills/workflow/SIMPLE-ENGLISH.md"'),
    ("tests/test_simple_english.py", 'self.assertIn("MIT License", (ROOT / "skills/workflow/SIMPLE-ENGLISH.LICENSE").read_text(encoding="utf-8"))'),
    ("tests/test_simple_english.py", '"""Numbered writing rules in a SIMPLE-ENGLISH.md text outside the sections it keeps (its modes)."""'),
    ("tests/test_simple_english.py", '"""R1: one owner. SIMPLE-ENGLISH.md keeps its modes and points to WRITING.md; a numbered rule anywhere else'),
    ("tests/test_simple_english.py", "simple-english skill) keeps only its Strict and CHECK modes, references, licence and credit"),
    ('README.md', '| `simple-english` | reference text `skills/workflow/SIMPLE-ENGLISH.md` for Strict mode and CHECK requests; its plain-writing rules now live in `skills/workflow/WRITING.md` |'),
    ('README.md', "`workflow-execute` owns ticket execution. It never branches, commits, merges or touches a tracker. The four phase skills read the shared policies in the installed `workflow` folder, so they need the whole package, not a single copied folder. **Bundled specialists.** `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design` and `domain-modeling` ship as separate skills in this package (plugin names `workflow-axa:<name>`). The plain-English rules (formerly `simple-english`) live in `skills/workflow/WRITING.md`, which the workflow uses for every report and delivery message; `skills/workflow/SIMPLE-ENGLISH.md` keeps the Strict and CHECK modes. Each is one text maintained in this package and keeps its MIT `LICENSE` (VENDORED-SKILLS.md). The phases load these sibling skills, so a removed skill or a host's same-named command cannot change the workflow. Optional installed specialists named in `skills/workflow/SPECIALISTS.md` (`research`, `diagnosing-bugs`, `prototype`, `pr`, `wizard`) block only the step that needs them, and are checked only when that step runs. This candidate also contains rc.8's Windows verification fixes."),
    ('VENDORED-SKILLS.md', '| `simple-english` (reference text `skills/workflow/SIMPLE-ENGLISH.md`; its plain-writing rules are now in `skills/workflow/WRITING.md`) | [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish), `skills/simple-english/` version 2.1.1, last copied at commit `a6fcb4fde098b33617cc1578d151ebf58774b883` | MIT, `skills/workflow/SIMPLE-ENGLISH.LICENSE` and `docs/archive/skills/simple-english/LICENSE` |'),
    ('docs/RULE-CONTRACTS.md', "| SIMPLE-ENGLISH.md (reference text, formerly simple-english) | Strict mode and CHECK only; the common rules are WRITING.md's | Strict vocabulary; CHECK against the rule catalog | Whether a Plain-mode catalog hit is a suggestion |"),
    ('skills/workflow/WRITING.md', "How to write anything a person reads: questions, chat updates, plans, tickets, findings, reports. Agent instructions (skills, AGENTS.md) follow this package's `writing-for-agents` skill (`../writing-for-agents/SKILL.md`) for structure; this file covers the human-facing text. It is the one owner of the common writing rules and of the Unslop check. [SIMPLE-ENGLISH.md](SIMPLE-ENGLISH.md) keeps only its Strict and CHECK modes."),
    ('tests/test_package_contract.py', '"tools/digest_sessions.py", "skills/workflow/SIMPLE-ENGLISH.md", "skills/workflow/SIMPLE-ENGLISH.LICENSE", "skills/rule-maker/scripts/required_reads.py", "skills/workflow/flows/INDEX.md", "skills/workflow/FALLBACKS.md", "skills/workflow/scripts/settings.py", "skills/workflow/scripts/offers.py", "hooks/approval.py", "hooks/read_evidence.py", "skills/workflow-deliver/scripts/completion_check.py", "skills/workflow/scripts/legacy_inventory.py", "skills/workflow/flows/TEMPLATE.md",'),
    ('tests/test_simple_english.py', '"""The writing rules: WRITING.md owns every common rule and the Unslop check; SIMPLE-ENGLISH.md (formerly the'),
}


def mentions(root: Path) -> list[tuple[str, str]]:
    files = subprocess.run(["git", "-C", str(root), "ls-files", "--", *PATHS], capture_output=True, text=True,
                           check=True).stdout.splitlines()
    found = []
    for rel in files:
        if rel.startswith(EXCLUDED) or not rel.endswith(TEXT_SUFFIXES) or rel == "tests/test_writing_mentions.py":
            continue
        try:
            text = (root / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        found += [(rel, line.strip()) for line in text.splitlines() if PATTERN in line]
    return found


def unexpected(found: list[tuple[str, str]]) -> list[tuple[str, str]]:
    return [m for m in found if m not in KEEP]


class OldFileMentions(unittest.TestCase):
    def test_every_mention_is_a_kept_one(self):
        self.assertEqual(unexpected(mentions(ROOT)), [],
                         "sort each line: point it to WRITING.md, or keep it here with its reason")

    def test_a_planted_mention_fails_even_in_a_kept_file(self):
        for planted in (("skills/wait-what/SKILL.md", "Read ../workflow/" + PATTERN + ".md first."),
                        ("AGENTS.md", "The tells live in " + PATTERN + ".md.")):
            with self.subTest(planted=planted):
                self.assertEqual(unexpected(mentions(ROOT) + [planted])[-1:], [planted])


PLACES = {
    "skills/grilling/SKILL.md", "skills/spar/SKILL.md", "skills/spar/SPAR-FILE.md", "skills/wait-what/SKILL.md",
    "skills/resume/SKILL.md", "skills/rule-maker/AUDIT.md", "skills/rule-maker/DIAGNOSE.md", "skills/ui-design/SKILL.md",
    "skills/interrogate/SKILL.md", "skills/code-review/SKILL.md", "skills/code-review/BLAST-RADIUS.md",
    "skills/plan-review/SKILL.md", "skills/codebase-map/SKILL.md", "skills/codebase-map/TASK-REPORT.md",
    "skills/codebase-map/scripts/render_report.py", "skills/workflow-clarify/SKILL.md",
    "skills/workflow-specify/SKILL.md", "skills/workflow-execute/SKILL.md", "skills/workflow-deliver/SKILL.md",
    "skills/workflow/SKILL.md", "skills/workflow/TASK-FOLDER.md", "skills/workflow/VISUAL-REVIEW.md",
    "skills/writing-for-agents/SKILL.md", "skills/domain-modeling/SKILL.md", "skills/no-comments/SKILL.md",
}


def listed_places(context: str) -> set[str]:
    part = context.split("## Places that write for a person", 1)[1].split("\n## ", 1)[0]
    return set(re.findall(r"(?m)^\| `(skills/[^`]+)`", part))


def places_without_pointer(texts: dict[str, str]) -> list[str]:
    return sorted(rel for rel, text in texts.items() if "WRITING.md" not in text)


class PlacesThatWriteForAPerson(unittest.TestCase):
    """R4 and owner Q1: the places that write something a person reads are listed once in CONTEXT.md, and each
    points to WRITING.md."""

    def test_the_list_is_complete_and_each_place_points_to_writing(self):
        listed = listed_places((ROOT / "CONTEXT.md").read_text(encoding="utf-8"))
        self.assertEqual(listed, PLACES)
        texts = {rel: (ROOT / rel).read_text(encoding="utf-8") for rel in listed}
        self.assertEqual(places_without_pointer(texts), [])

    def test_a_place_that_loses_its_pointer_fails(self):
        texts = {rel: (ROOT / rel).read_text(encoding="utf-8") for rel in PLACES}
        texts["skills/resume/SKILL.md"] = texts["skills/resume/SKILL.md"].replace("WRITING.md", "the rules")
        self.assertEqual(places_without_pointer(texts), ["skills/resume/SKILL.md"])


if __name__ == "__main__":
    unittest.main()
