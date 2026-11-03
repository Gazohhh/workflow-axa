"""class_rules.py: every rule for a class, with nested selectors joined and context-only rules marked."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/ui-design/scripts/class_rules.py"


def run(root, *classes):
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), str(root), *classes],
                          capture_output=True, text=True, encoding="utf-8")


class ClassRulesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "styles").mkdir()
        (self.root / "styles/app.scss").write_text(
            "/* .sm-chip in a comment */\n.sm-chip {\n  display: block;\n}\n"
            ".line-chip {\n  display: flex;\n  .sm-chip.info-chip {\n    display: inline-flex;\n  }\n}\n"
            "@media (min-width: 600px) {\n  .title, .head {\n    &.wide .sm-chip { width: 1px; }\n  }\n}\n"
            ".sm-chipper { color: red; }\n", encoding="utf-8")
        (self.root / "node_modules").mkdir()
        (self.root / "node_modules/lib.css").write_text(".sm-chip { color: blue; }\n", encoding="utf-8")

    def test_lists_plain_nested_and_media_rules_with_context(self):
        result = run(self.root, "sm-chip")
        self.assertEqual(result.returncode, 0, result.stdout)
        out = result.stdout
        self.assertIn("styles/app.scss:2  .sm-chip\n", out)
        self.assertIn("styles/app.scss:7  .line-chip .sm-chip.info-chip  [needs context]", out)
        self.assertIn(".title.wide .sm-chip  [needs context]", out)
        self.assertIn(".head.wide .sm-chip  [needs context]", out)
        self.assertNotIn("sm-chipper", out)
        self.assertNotIn("node_modules", out)
        self.assertNotIn(":1 ", out)  # the comment is not a rule

    def test_compare_shows_both_parents_and_rules_for_children(self):
        # Round-5 retro: a parent that restyles its children was still offered as a match.
        result = run(self.root, "--compare", "line-chip", "title")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("== FROM .line-chip", result.stdout)
        self.assertIn(".line-chip  [itself]  display: flex", result.stdout)
        self.assertIn("== INTO .title", result.stdout)
        self.assertIn("[styles children]  width: 1px", result.stdout)
        self.assertIn("browsers make h1-h6, strong, b and th bold by default", result.stdout)
        self.assertEqual(run(self.root, "--compare", "only-one").returncode, 2)

    def test_match_requires_the_whole_class_set_of_an_existing_element(self):
        # Round-15 retro: a new button took "btn btn-danger" while the existing ones were "btn btn-small btn-danger".
        (self.root / "page.html").write_text('<ul>\n<li><button class="btn btn-small btn-danger">Delete</button></li>\n</ul>\n', encoding="utf-8")
        (self.root / "app.js").write_text("li.innerHTML = '<span class=\"tag tag-muted\">x</span>';\n", encoding="utf-8")
        ok = run(self.root, "--match", "button", "btn-danger", "btn", "btn-small")
        self.assertEqual(ok.returncode, 0, ok.stdout)
        self.assertIn("MATCH page.html:2", ok.stdout)
        partial = run(self.root, "--match", "button", "btn", "btn-danger")
        self.assertEqual(partial.returncode, 1)
        self.assertIn("NO MATCH", partial.stdout)
        self.assertIn("same tag, some of the classes: page.html:2", partial.stdout)
        self.assertEqual(run(self.root, "--match", "span", "tag", "tag-muted").returncode, 0)  # HTML inside a JS string
        self.assertEqual(run(self.root, "--match", "button").returncode, 2)

    def test_match_finds_classes_added_by_a_binding(self):
        # Round 17: Angular adds the chip variant with [ngClass]; a static-only search reported no match.
        (self.root / "card.html").write_text('<div class="chip" [ngClass]="chip.className">x</div>\n', encoding="utf-8")
        (self.root / "card.ts").write_text("const chip = { className: 'chip-neutral' };\n", encoding="utf-8")
        result = run(self.root, "--match", "div", "chip", "chip-neutral")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("BOUND MATCH card.html:1", result.stdout)
        self.assertEqual(run(self.root, "--match", "div", "chip", "chip-unknown").returncode, 1)

    def test_no_match_and_bad_input(self):
        self.assertEqual(run(self.root, "missing-class").returncode, 1)
        self.assertEqual(run(self.root, ".sm-chip").returncode, 2)
        self.assertEqual(run(self.root / "nope", "x").returncode, 2)


if __name__ == "__main__":
    unittest.main()
