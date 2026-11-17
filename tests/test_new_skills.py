"""interrogate, no-comments and wait-what (REDESIGN.md §3.8-3.10), and code-review's new checks (§6 row 8). T23."""
from __future__ import annotations

import json
import re
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from validate import repeat_notes, validate_package  # noqa: E402

NEW = ("interrogate", "no-comments", "wait-what")
POLICY = "policy:\n  allow_implicit_invocation: false\n"


def text(name: str) -> str:
    return (ROOT / f"skills/{name}/SKILL.md").read_text(encoding="utf-8")


def flat(name: str) -> str:
    return " ".join(text(name).split())


class Registration(unittest.TestCase):
    def test_registered_user_invoked_with_metadata(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        for name in NEW:
            with self.subTest(skill=name):
                self.assertIn(f"./skills/{name}", plugin["skills"])
                front = text(name).split("---", 2)[1]
                self.assertIn(f"\nname: {name}\n", front)
                self.assertIn("\ndisable-model-invocation: true\n", front)
                metadata = (ROOT / f"skills/{name}/agents/openai.yaml").read_text(encoding="utf-8")
                self.assertTrue(metadata.endswith(POLICY), metadata)

    def test_validate_requires_both_user_only_markers_to_agree(self):
        # Astra T22+T23 review: Codex reads agents/openai.yaml, Claude reads SKILL.md; both must say user-only.
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(shutil.copytree(ROOT, Path(tmp) / "c", ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".artifacts", ".local-fixtures", "dist", "plans", "archive")))
            self.assertEqual([e for e in validate_package(copy) if "allow_implicit_invocation" in e], [])
            meta = copy / "skills/wait-what/agents/openai.yaml"
            meta.write_bytes(meta.read_bytes().split(b"policy:")[0])
            self.assertTrue(any("wait-what" in e and "must agree" in e for e in validate_package(copy)))
            other = copy / "skills/tdd/agents/openai.yaml"
            other.write_bytes(other.read_bytes() + POLICY.encode())
            self.assertTrue(any("tdd" in e and "must agree" in e for e in validate_package(copy)))

    def test_no_markdown_link_leaves_its_skill_folder(self):
        for name in NEW + ("code-review",):
            folder = (ROOT / "skills" / name).resolve()
            for target in re.findall(r"\]\(([^)#]+)\)", text(name)):
                with self.subTest(skill=name, target=target):
                    self.assertNotIn(":", target)
                    self.assertTrue((folder / target).resolve().is_relative_to(folder), target)

    def test_no_repeated_paragraph_with_other_skill_texts_or_core(self):
        notes = repeat_notes(ROOT)
        for name in NEW + ("code-review", "rule-maker/rules/CORE.md"):
            self.assertFalse([n for n in notes if f"skills/{name}" in n], notes)


class Interrogate(unittest.TestCase):
    """§3.8: a pinned target, two adversaries, confirmation on a pristine copy, three lists, reports only."""

    def test_contract(self):
        body = flat("interrogate")
        for phrase in ("can an adversary show a concrete failure",
                       "Open with one sentence in your own words",
                       "Get its id with `python -X utf8 -I scripts/snapshot.py id <repo>`", "never compute it by hand",
                       "Two adversaries", "Label each one", "8 probe commands per adversary",
                       "standing diagnostic allowance", "reported as the named experiment instead of run",
                       "`snapshot.py copy <repo> <new owned .artifacts path> <snapshot id>`",
                       "`snapshot.py fill <repo> <that checkout> <snapshot id>`",
                       "never write through a link or junction", "When it does, stop: the copy isn't the target",
                       "run `snapshot.py check <repo> <snapshot id>` on the live target",
                       "an agent other than its finder reruns it on a fresh, pristine copy of the same snapshot",
                       "mark the whole report **stale**",
                       "**Reproduced failures:**", "**Unverified concerns:**", "**Untested surfaces:**",
                       "This skill reports only", "never runs it unasked",
                       "a record write never changes which task the session is on"):  # T24: writes never move it
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)


class NoComments(unittest.TestCase):
    """§3.9: verdicts, the main agent's check, one offer, behavior unchanged; CORE owns the exceptions."""

    def test_contract(self):
        body = flat("no-comments")
        for phrase in ("`../rule-maker/rules/CORE.md`", "the current diff against the base branch",
                       "**delete:**", "**keep:** name the CORE exception", "**reshape:**",
                       "raise it as a **possible bug**", "Unverified: **keep** it and list it for the owner",
                       "Remove one only when the offer justifies its replacement and the type check or lint passes without it",
                       "Reject an edit outside the scope or a verdict with the wrong reason",
                       "until a revised offer names that exact removal",
                       "Make one offer through `workflow-specify` step 5 (`record.py offer create`)", "it ends with the one question",
                       "An offer in your own words can't be approved", "Show the presentation `record.py offer present` prints",
                       "Change nothing before it is approved",
                       "**Removing a comment must not change behavior.**",
                       "Report a reshape that would change behavior instead of making it"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_the_exception_list_is_not_copied(self):
        # CORE owns the list; any of its specific items here would be a second copy to keep in step.
        body = flat("no-comments").lower()
        for item in ("licence header", "license header", "safety:", "issue link", "public api doc", "static-analysis"):
            self.assertNotIn(item, body)
        self.assertIn("Its approved offer is the approved change CORE requires", flat("no-comments"))


class WaitWhat(unittest.TestCase):
    """§3.10 and §3.4: no new work, a non-answer, the pending question unchanged, no tool call to re-present."""

    def test_contract(self):
        body = flat("wait-what")
        for phrase in ("Add nothing new", "two or three sentences",
                       "one idea per sentence", "the actor first, in the active voice",
                       "the same word for the same thing", "`CONTEXT.md` keeps its name and gets a short definition",
                       "concrete names, numbers and file paths",
                       "present the same offer again exactly as `workflow-specify` step 5 says",
                       "If that offer was superseded or revoked, say so instead", "Never rebuild, shorten or change an offer",
                       "Repeat any other pending question word for word",
                       "only reading `CONTEXT.md` and `../workflow/WRITING.md`",
                       "No new work, no edits, no records", "`/wait-what` is not an answer"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)
        self.assertNotRegex(body, r"record\.py (?!offer present)")

    def test_short(self):
        self.assertLess(len(text("wait-what").split()), 400)


class CodeReviewChecks(unittest.TestCase):
    """§6 row 8: comments and reader load in the pasted Standards list; blast radius under Standards."""

    def test_checks_are_pasted_into_the_standards_brief(self):
        body = flat("code-review")
        for phrase in ("**Comments** (from `../rule-maker/rules/CORE.md`)", "report it as a possible bug",
                       "**Reader load** (a judgement call)", "Do **not** merge or rerank findings",
                       "**plus the smell baseline and the comment and reader-load checks from step 3** pasted in full"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_blast_radius_step(self):
        body = flat("code-review")
        for phrase in ("### 4b. Blast radius", "[BLAST-RADIUS.md](BLAST-RADIUS.md)",
                       "anything outside the diff reads what changed",
                       "Put the result under `## Standards` as its own item, \"Blast radius\"",
                       "reopen any assumption that the implementation or new evidence changes or contradicts",
                       "the item says \"none\" with the boundary trace that shows it", "This step reports only"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)
        self.assertNotIn("Search for the callers outside the diff", body)


class ImpactQuestionRouting(unittest.TestCase):
    """Live runs L1 and L2: a plain "what could this break?" never loaded the method. The description routes it."""

    def test_description_names_impact_questions(self):
        front = text("code-review").split("---", 2)[1]
        description = json.loads(re.search(r"\ndescription: (\"[^\n]+\")\n", front)[1])
        self.assertIn("what could this change break?", description)
        metadata = (ROOT / "skills/code-review/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn("what could this change break", metadata)

    def test_an_impact_question_follows_the_method_alone(self):
        body = flat("code-review")
        self.assertIn("## Impact questions", text("code-review"))
        for phrase in ("skips the two axes", "[BLAST-RADIUS.md](BLAST-RADIUS.md)", "no two-axis review", "report only"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body.split("## Impact questions", 1)[1][:600])

    def test_metadata_still_validates(self):
        self.assertEqual([], [e for e in validate_package(ROOT) if "code-review" in e])


MIT_BODY = """Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""


def assert_mit_licence(case: unittest.TestCase, relative: str, holder: str) -> None:
    """The whole file, whitespace-collapsed, equals the standard MIT text for this holder."""
    expected = " ".join(f"MIT License\n\nCopyright (c) 2026 {holder}\n\n{MIT_BODY}".split())
    case.assertEqual(expected, " ".join((ROOT / relative).read_text(encoding="utf-8").split()), relative)


class BlastRadiusMethod(unittest.TestCase):
    """skills/code-review/BLAST-RADIUS.md owns the method (agreement 1, R1)."""

    def body(self) -> str:
        return " ".join((ROOT / "skills/code-review/BLAST-RADIUS.md").read_text(encoding="utf-8").split())

    def test_method_parts(self):
        body = self.body()
        for phrase in ("Callers are the input, not the result", "**Find the safety facts.**", "no cap",
                       "## Evidence ladder", "say which step it reached",
                       "## Where grep stops", "pinned version", "local patch", "async order", "teardown",
                       "JSON or API shape", "DB column", "wire or file format", "another language", "config key",
                       "feature flag", "saved data", "downstream", "its `copy` command", "never start it yourself",
                       "Reproduced in an isolated running instance of the application",
                       "**Risks**", "**Cleared**", "**Before you merge**",
                       "boundary trace", "standing diagnostic allowance",
                       "`python -X utf8 -I ../interrogate/scripts/snapshot.py id <repo>`",
                       "unproven", "`/interrogate`", "reports only",
                       "## Planning, with no diff yet", "## Asked directly"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, body)

    def test_no_multi_model_step_and_no_source_name(self):
        body = self.body().lower()
        for word in ("arena", "models", "pstack", "upstream"):
            with self.subTest(word=word):
                self.assertNotIn(word, body)

    def test_licence_travels_with_the_text(self):
        assert_mit_licence(self, "skills/code-review/BLAST-RADIUS.LICENSE", "Lauren Tan")

    def test_no_paragraph_repeats_between_the_step_and_the_method(self):
        self.assertEqual([], [n for n in repeat_notes(ROOT) if "BLAST-RADIUS.md" in n])


POINTER = re.compile(r"`((?:\.\./)+[\w./-]+\.md)`")


def pointer_targets(relative: str, name: str) -> list[Path]:
    """Code-form pointers (`../x/Y.md`) in a skill file that end in `name`, resolved from that file's folder.
    validate.py checks Markdown links only, so these need their own check."""
    path = ROOT / relative
    return [(path.parent / found).resolve() for found in POINTER.findall(path.read_text(encoding="utf-8"))
            if found.endswith(name)]


class BlastRadiusRouting(unittest.TestCase):
    """Planning and routing points name the method (agreement 1, R3, R4, R12; TODO T2)."""

    PHRASES = {
        "skills/workflow-clarify/SKILL.md": ("**Safety assumptions**", "each with the check that could falsify it"),
        "skills/workflow-specify/SKILL.md": ("each safety assumption from clarify",),
        "skills/plan-review/SKILL.md": ("records no safety assumptions",),
        "skills/workflow/SKILL.md": ("blast-radius trigger in code-review step 4b", "a docs fix whose text only tests read stays lightweight"),
        "skills/workflow/flows/INDEX.md": ("\"what could this break\"", "**Compatibility**"),
        "skills/workflow-execute/SKILL.md": ("step 4b", "again on the whole diff"),
        "skills/workflow/AUDIT.md": ("a tool, test, validator or other document reads",),
        "skills/workflow-deliver/SKILL.md": ("a \"Blast radius\" result", "open Risks and unproven safety facts"),
    }
    POINTED = ("skills/workflow-clarify/SKILL.md", "skills/workflow/flows/INDEX.md", "skills/workflow/AUDIT.md")

    def test_each_point_names_its_part(self):
        for relative, phrases in self.PHRASES.items():
            body = " ".join((ROOT / relative).read_text(encoding="utf-8").split())
            for phrase in phrases:
                with self.subTest(file=relative, phrase=phrase):
                    self.assertIn(phrase, body)

    def test_the_compatibility_modifier_requires_the_method(self):
        index = (ROOT / "skills/workflow/flows/INDEX.md").read_text(encoding="utf-8")
        line = next(l for l in index.splitlines() if l.startswith("- **Compatibility**"))
        self.assertIn("BLAST-RADIUS.md", line)

    def test_pointers_resolve(self):
        method = (ROOT / "skills/code-review/BLAST-RADIUS.md").resolve()
        for relative in self.POINTED:
            with self.subTest(file=relative):
                targets = pointer_targets(relative, "BLAST-RADIUS.md")
                self.assertTrue(targets, "no code-form pointer to BLAST-RADIUS.md")
                self.assertEqual({method}, set(targets))
        for path in sorted((ROOT / "skills").rglob("*.md")):
            for target in pointer_targets(path.relative_to(ROOT).as_posix(), "BLAST-RADIUS.md"):
                with self.subTest(file=path.relative_to(ROOT).as_posix()):
                    self.assertEqual(method, target)


if __name__ == "__main__":
    unittest.main()
