"""The output read and the cited-sources rule: one owner each, pointers at the step that uses them
(docs/plans/2026-11-24-reviewer-output-and-sources R1-R3). They prove the text says it, not that an agent follows it."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from test_new_skills import pointer_targets  # noqa: E402

AUDIT, WRITING = "skills/workflow/AUDIT.md", "skills/workflow/WRITING.md"


def text(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def flat(body: str) -> str:
    return " ".join(body.split())


def section(relative: str, heading: str) -> str:
    return flat(text(relative).split(heading + "\n", 1)[1].split("\n## ", 1)[0])


def files_with(phrase: str) -> list[str]:
    return sorted(p.relative_to(ROOT).as_posix() for p in (ROOT / "skills").rglob("*.md")
                  if phrase in flat(p.read_text(encoding="utf-8")))


class OutputRead(unittest.TestCase):
    """R1: a fresh reviewer reads the finished output before the plan; what it leaves out reaches the owner."""

    def test_the_reader_gets_the_output_alone_and_comes_first(self):
        rule = section(AUDIT, "## Output read")
        for phrase in ("message, report, dashboard or document", "before any review against the plan or the diff",
                       "a fresh reviewer only the finished output and who reads it", "which question it answers",
                       "the obvious questions", "not agent instructions"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, rule)

    def test_a_left_out_question_goes_to_the_owner_and_is_no_note(self):
        rule = section(AUDIT, "## Output read")
        self.assertIn("goes to the owner as an open choice before delivery", rule)
        self.assertIn("never a note", rule)
        self.assertIn("the agreement with the owner excludes in words", rule)
        self.assertIn("all in one question", rule)

    def test_spar_shows_the_left_out_questions_to_the_owner(self):
        self.assertIn("as evidence and to the owner at checkpoint (a), or the conclusion without debaters",
                      flat(text("skills/spar/SKILL.md")))

    def test_missing_output_or_subagents_is_said_out_loud(self):
        rule = section(AUDIT, "## Output read")
        self.assertIn("`NOT VERIFIED`", rule)
        self.assertIn("self-check", rule)

    def test_each_review_points_to_the_one_rule(self):
        self.assertEqual([AUDIT], files_with("which question it answers"))
        for relative in ("skills/code-review/SKILL.md", "skills/plan-review/SKILL.md", "skills/spar/SKILL.md",
                         "skills/workflow-deliver/SKILL.md"):
            with self.subTest(file=relative):
                self.assertIn('AUDIT.md` "Output read"', text(relative))
                self.assertEqual({(ROOT / AUDIT).resolve()}, set(pointer_targets(relative, "workflow/AUDIT.md")))

    def test_code_review_runs_it_before_the_axes_and_shows_it_first(self):
        body = text("skills/code-review/SKILL.md")
        self.assertLess(body.index("Output read"), body.index("### 4. Run the axes"))
        self.assertIn("under `## Reader`, first", flat(body))

    def test_plan_review_runs_it_before_the_task_records(self):
        body = text("skills/plan-review/SKILL.md")
        self.assertLess(body.index("Output read"), body.index("Read the task records"))


class CitedSources(unittest.TestCase):
    """R2: a cited source carries what was read there, or says unverified."""

    def test_url_and_quote_or_unverified(self):
        rule = section(WRITING, "## Cited sources")
        for phrase in ("method, formula, number, threshold or standard", "URL", "exact sentence or formula",
                       "\"unverified\"", "question cards", "offers", "before you send"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, rule)

    def test_reviewers_open_the_source_and_a_breach_is_a_finding(self):
        rule = section(WRITING, "## Cited sources")
        self.assertIn("A reviewer opens each cited source", rule)
        self.assertIn("is a finding", rule)

    def test_unslop_5_is_a_pointer_for_methods(self):
        row = next(line for line in text(WRITING).splitlines() if line.startswith("| Unslop 5 "))
        self.assertIn('"Cited sources"', row)

    def test_each_place_points_to_the_one_rule(self):
        self.assertEqual([WRITING], files_with("exact sentence or formula"))
        for relative in ("skills/grilling/SKILL.md", "skills/workflow-specify/SKILL.md", "skills/code-review/SKILL.md",
                         "skills/plan-review/SKILL.md", "skills/spar/SKILL.md"):
            with self.subTest(file=relative):
                self.assertIn('WRITING.md` "Cited sources"', text(relative))
                self.assertIn((ROOT / WRITING).resolve(), pointer_targets(relative, "workflow/WRITING.md"))

    def test_the_standards_brief_pastes_the_rule(self):
        brief = flat(text("skills/code-review/SKILL.md").split("**Standards brief**", 1)[1].split("**Spec brief**", 1)[0])
        self.assertIn('WRITING.md` "Cited sources", pasted in full, with the spec\'s path', brief)
        self.assertIn("each tell is a note, except a \"Cited sources\" breach", brief)

    def test_every_spar_brief_carries_the_line(self):
        t3 = text("skills/spar/T3.md")
        briefs = [part.split("```", 1)[0] for part in t3.split("```text")[1:]]
        self.assertEqual(2, len(briefs))
        for brief in briefs:
            self.assertIn("each source you name: its URL and the words you read there, or \"unverified\"", flat(brief))


class ObservedRuns(unittest.TestCase):
    def test_both_rules_have_a_live_case(self):
        cases = {c["id"]: c for c in json.loads(text("tests/behavioral/cases.json"))["cases"]}
        for identifier in ("B31", "B32"):
            with self.subTest(case=identifier):
                self.assertEqual(("live-host", "NOT_RUN"), (cases[identifier]["mode"], cases[identifier]["result"]))


if __name__ == "__main__":
    unittest.main()
