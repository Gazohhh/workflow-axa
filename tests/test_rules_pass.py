"""The rules-library pass of the 2026-11-15 redesign (ticket T11): one owner per rule.

P7: the CSS prohibition was repeated in START, CORE, READINESS, DESIGN, ANGULAR and IONIC. It now lives only in
DESIGN.md; the other modules point to it. CORE carries the comment rules (contract C-CMT-1), OPERATIONS the standing
diagnostic allowance, POLICY the protection/preference split.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULES = ROOT / "skills/rule-maker/rules"
# Phrases that state the styling prohibition itself (not a pointer to it).
PROHIBITION = re.compile(r"(?i)never write css|no new css|no css is ever|write no css|not write css|"
                         r"do not create, modify or inject css")


class RulesPass(unittest.TestCase):

    def text(self, name):
        return (RULES / name).read_text(encoding="utf-8")

    def test_the_css_prohibition_lives_only_in_design_md(self):
        holders = sorted(p.name for p in RULES.glob("*.md")
                         if p.name not in ("CHANGES.md", "SOURCES.md") and PROHIBITION.search(p.read_text(encoding="utf-8")))
        self.assertEqual(holders, ["DESIGN.md"])
        for name in ("START.md", "CORE.md", "READINESS.md", "IONIC.md", "ANGULAR.md"):
            with self.subTest(module=name):
                self.assertIn("DESIGN.md", self.text(name))

    def test_design_md_defines_what_counts_as_styling_once(self):
        design = self.text("DESIGN.md")
        self.assertIn("## What counts as styling", design)
        for pattern in ("`<style>`", "`style=\"\"`", "Tailwind", "CSS-in-JS", "theme and token files"):
            self.assertIn(pattern, design.split("## What counts as styling", 1)[1].split("##", 1)[0])
        self.assertIn("stricter, never looser", design)

    def test_core_carries_the_comment_rules_and_engineering_the_detail(self):
        core = self.text("CORE.md")
        self.assertIn("## Comments are claims, not evidence — required", core)
        self.assertIn("**New code carries no comments** (default)", core)
        for phrase in ("raise it as a possible bug", "only in lines an approved change already edits",
                       "Keep unverified \"do not remove\" claims and tool-read annotations", "PHPDoc",
                       "Rust `// SAFETY:`", "[ENGINEERING.md](ENGINEERING.md) \"Comments\""):
            self.assertIn(phrase, core)
        detail = self.text("ENGINEERING.md").split("## Comments", 1)[1].split("##", 1)[0]
        for phrase in ("possible bug", "comment debt", "any authority it names is given", "never just removed"):
            self.assertIn(phrase, detail)

    def test_core_defaults_subtract_first_and_fix_the_root_cause(self):
        core = self.text("CORE.md")
        self.assertIn("Subtract before you add", core)
        self.assertIn("a guard fixes only a legitimate state", core)

    def test_operations_states_the_standing_diagnostic_allowance(self):
        allowance = self.text("OPERATIONS.md").split("## Standing diagnostic allowance", 1)[1].split("##", 1)[0]
        for condition in ("owned disposable location", "synthetic, sanitised or already authorised",
                          "established isolated target", "no protected operation, install, external change",
                          "resource limits", "artifact policy", "never the test by itself"):
            self.assertIn(condition, allowance)

    def test_policy_splits_protections_from_preferences(self):
        policy = self.text("POLICY.md")
        self.assertIn("## Protections and preferences", policy)
        self.assertIn("overrides a preference", policy)
        self.assertIn("Changing a protection itself needs the policy owner", policy)

    def test_the_skip_text_is_active_after_the_cutover(self):
        """T17 applied candidates/READINESS-SKIP.md: the readiness question is set up now / skip for this task."""
        self.assertIn("Skip for this task", self.text("READINESS.md"))
        self.assertIn("skip for this task", self.text("START.md"))

    def test_every_candidate_replacement_was_applied(self):
        """Each `Old:` sentence of the cutover (T17) is gone and its `New:` sentence is present, including the
        new-project setup sentence."""
        candidate = (ROOT / "docs/plans/2026-11-15-workflow-redesign/candidates/READINESS-SKIP.md").read_text(encoding="utf-8")
        self.assertIn("An empty new project needs an agreed minimal setup before scaffolding", candidate)
        files = {rel: (ROOT / "skills" / rel).read_text(encoding="utf-8")
                 for rel in ("rule-maker/rules/READINESS.md", "rule-maker/rules/START.md", "workflow/SKILL.md",
                             "workflow/RULES.md")}
        files["resume-task/SKILL.md"] = (ROOT / "skills/resume/SKILL.md").read_text(encoding="utf-8")  # T21 merge
        for section in re.split(r"^## ", candidate, flags=re.M)[1:]:
            target = next((name for name in files if name in section.split("\n", 1)[0]), None)
            old = re.search(r'^Old: "(.+?)"', section, re.M)
            new = re.search(r'^New: "(.+?)"$', section, re.M)
            if target and old:
                with self.subTest(file=target, old=old[1][:40]):
                    self.assertNotIn(old[1], files[target])
                    if new:
                        self.assertIn(new[1].rstrip('"'), files[target].replace("\r\n", "\n"))


if __name__ == "__main__":
    unittest.main()
