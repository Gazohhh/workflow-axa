"""The flow recipes and their index (T9 of docs/plans/2026-11-15-workflow-redesign, contract C-FLOW-1)."""
from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.validate import ROOT, flow_index_errors, registered_names, validate_package

FLOWS = ROOT / "skills/workflow/flows"
RECIPES = ("bug", "feature", "new-project", "ui", "refactor", "architecture", "performance", "migration", "docs-tests")


def copy_package(destination: Path) -> Path:
    return Path(shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(
        ".git", "__pycache__", ".artifacts", ".local-fixtures", "dist", "plans", "archive")))


class FlowIndexTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.clean = copy_package(Path(cls.tmp.name) / "clean")

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def candidate(self) -> Path:
        return Path(shutil.copytree(self.clean, Path(tempfile.mkdtemp(dir=self.tmp.name)) / "c"))

    def errors(self, root):
        return flow_index_errors(root, registered_names(root))

    def test_the_nine_recipes_are_indexed_and_valid(self):
        self.assertEqual(sorted(p.stem for p in FLOWS.glob("*.md") if p.name not in ("INDEX.md", "TEMPLATE.md")),
                         sorted(RECIPES))
        self.assertEqual(self.errors(ROOT), [])

    def test_a_recipe_without_a_row_fails(self):
        root = self.candidate()
        (root / "skills/workflow/flows/extra.md").write_text(
            "---\nname: extra\nuses: [tdd]\nfallbacks: [Direct check]\napproval-exceptions: none\n---\n# Extra\n",
            encoding="utf-8")
        self.assertTrue(any("extra.md has no row" in e for e in self.errors(root)))

    def test_a_duplicate_row_fails(self):
        root = self.candidate()
        index = root / "skills/workflow/flows/INDEX.md"
        text = index.read_text(encoding="utf-8")
        row = next(line for line in text.splitlines() if line.startswith("| bug |"))
        index.write_text(text.replace(row, row + "\n| bug | another signal | [bug.md](bug.md) |"), encoding="utf-8")
        self.assertTrue(any("'bug' (bug.md) more than once" in e for e in self.errors(root)))

    def test_a_row_without_a_file_fails(self):
        root = self.candidate()
        (root / "skills/workflow/flows/bug.md").unlink()
        self.assertTrue(any("lists bug.md, which does not exist" in e for e in validate_package(root)))

    def test_an_unregistered_skill_or_a_signals_key_fails(self):
        root = self.candidate()
        path = root / "skills/workflow/flows/bug.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("uses: [tdd, code-review, grilling]", "uses: [tdd, diagnosing-bugs]"), encoding="utf-8")
        self.assertTrue(any("'diagnosing-bugs'" in e for e in self.errors(root)))
        path.write_text(text.replace("approval-exceptions: none", "approval-exceptions: none\nsignals: wrong result"),
                        encoding="utf-8")
        self.assertTrue(any("signals belong in INDEX.md" in e for e in self.errors(root)))

    def test_the_template_and_the_index_are_not_recipes(self):
        root = self.candidate()
        (root / "skills/workflow/flows/TEMPLATE.md").write_text("no frontmatter at all\n", encoding="utf-8")
        self.assertEqual(self.errors(root), [])

    def test_recipes_carry_no_approval_rules_of_their_own(self):
        """Approval rules live in the common process; a recipe states only its approval-exceptions line."""
        for name in RECIPES:
            body = (FLOWS / f"{name}.md").read_text(encoding="utf-8").split("\n---\n", 1)[1]
            with self.subTest(recipe=name):
                self.assertNotRegex(body, r"(?i)\b(?:plan report|review\.html|approval line|gate two)\b")


class FallbackAndRouterTests(unittest.TestCase):
    """T10: FALLBACKS.md (contract C-FB-1) and the router's recipe choice."""

    fallbacks = (ROOT / "skills/workflow/FALLBACKS.md").read_text(encoding="utf-8")
    router = (ROOT / "skills/workflow/SKILL.md").read_text(encoding="utf-8")

    def named(self):
        return set(re.findall(r"^\| [^|]+ \| ([^|]+?) \| [^|]+ \| [^|]+ \|$", self.fallbacks, re.M)) - {"Fallback", "---"}

    def test_thirteen_named_fallbacks_and_six_pause_conditions(self):
        self.assertEqual(len(self.named()), 13)
        pauses = self.fallbacks.split("## What may pause work", 1)[1]
        self.assertEqual(len(re.findall(r"^\d\. ", pauses, re.M)), 6)
        self.assertIn("Fallback: <name> — <substitute>; <evidence>; <remaining limitation>", self.fallbacks)

    def test_every_fallback_a_recipe_names_is_defined(self):
        for name in RECIPES:
            head = (FLOWS / f"{name}.md").read_text(encoding="utf-8").split("\n---\n", 1)[0]
            listed = re.search(r"^fallbacks: \[(.*)\]$", head, re.M)[1]
            for fallback in (f.strip() for f in listed.split(",")):
                with self.subTest(recipe=name, fallback=fallback):
                    self.assertIn(fallback, self.named())

    def test_only_the_ui_recipe_loads_ui_design(self):
        """No backend case loads UI files: ui-design comes only from the ui recipe or the UI modifier."""
        for name in RECIPES:
            head = (FLOWS / f"{name}.md").read_text(encoding="utf-8").split("\n---\n", 1)[0]
            with self.subTest(recipe=name):
                self.assertEqual("ui-design" in head, name == "ui")
        self.assertIn("Load `ui-design` only for the ui recipe or the UI modifier", self.router)

    def test_the_router_asks_one_question_only_when_not_sure(self):
        self.assertIn("*Fix something broken · Add or change a feature · Start a new project · Only investigate*",
                      self.router)
        self.assertIn("at most one such question per task", self.router)
        self.assertIn("Never ask small versus complex bug", self.router)
        self.assertIn("[flows/INDEX.md](flows/INDEX.md)", self.router)
        self.assertIn("[FALLBACKS.md](FALLBACKS.md)", self.router)


class FlowPromptTests(unittest.TestCase):
    """Labelled prompts (classification) and one behavioural case per recipe, for observed host runs."""

    data = json.loads((ROOT / "tests/behavioral/flows.json").read_text(encoding="utf-8"))

    def test_every_recipe_has_three_prompts_and_one_case(self):
        for name in RECIPES:
            with self.subTest(recipe=name):
                self.assertGreaterEqual(sum(p["recipe"] == name for p in self.data["prompts"]), 3)
                cases = [c for c in self.data["cases"] if c["recipe"] == name]
                self.assertEqual(len(cases), 1)
                self.assertTrue(cases[0]["expect"])

    def test_labels_name_a_recipe_or_a_router_mode_and_nothing_counts_as_run(self):
        allowed = set(RECIPES) | {"inspect", "ask"}
        for prompt in self.data["prompts"]:
            self.assertIn(prompt["recipe"], allowed)
            self.assertLessEqual(set(prompt["modifiers"]), {"ui", "security", "compatibility"})
        for case in self.data["cases"]:
            self.assertEqual((case["mode"], case["result"]), ("live-host", "NOT_RUN"))

    def test_the_index_rows_match_the_labels(self):
        rows = re.findall(r"^\| ([\w-]+) \|", (FLOWS / "INDEX.md").read_text(encoding="utf-8"), re.M)
        self.assertEqual(sorted(r for r in rows if r != "Recipe"), sorted(RECIPES))


if __name__ == "__main__":
    unittest.main()
