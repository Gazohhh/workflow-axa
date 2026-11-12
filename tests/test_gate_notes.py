"""T4 of 2026-11-12-approval-gate-false-refusals (owner Q8 a): after an edit, the gate notes new styling in an
application file, and a new tag or class in a small change. It never refuses."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest

from test_gate_regressions import CACHE, GATE, A, GateCase, write_rows
from test_phase_gate_hook import APPROVED, ROUTER, hooked


def run_post(event) -> str:
    result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(GATE), "--hook-protocol=1"],
                            input=json.dumps(event), capture_output=True, text=True, encoding="utf-8",
                            env={**os.environ, "WORKFLOW_AXA_GATE_CACHE": CACHE.name})
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"] if result.stdout.strip() else ""


class StyleNotes(GateCase):

    def after(self, tool_name, data, rows=None):
        write_rows(self.path, hooked(rows if rows is not None else [ROUTER] + self.approval(A), self.repo))
        return run_post({"hook_event_name": "PostToolUse", "tool_name": tool_name, "tool_input": data,
                         "transcript_path": str(self.path), "cwd": str(self.repo)})

    def edit(self, rel, old, new):
        return {"file_path": str(self.repo / rel), "old_string": old, "new_string": new}

    def test_new_styling_in_an_application_file_gets_one_note(self):
        self.task(A, APPROVED)
        for rel, old, new in (("src/a.scss", ".a {}", ".a {}\n.btn { color: red; }"),
                              ("src/a.html", "<p>x</p>", '<p style="color:red">x</p>'),
                              ("src/a.tsx", "<p/>", "<p/>\n<style>{css}</style>")):
            with self.subTest(rel=rel):
                note = self.after("Edit", self.edit(rel, old, new))
                self.assertIn("DESIGN.md rule 4", note)
                self.assertEqual(note.count("DESIGN.md rule 4"), 1)

    def test_no_note_for_docs_tests_unchanged_styles_or_inactive_sessions(self):
        self.task(A, APPROVED)
        self.assertNotIn("DESIGN.md", self.after("Edit", self.edit("README.md", "x", '<p style="a">')))
        self.assertNotIn("DESIGN.md", self.after("Edit", self.edit("tests/test_a.py", "x", 'style="a"')))
        self.assertNotIn("DESIGN.md", self.after("Edit", self.edit("src/a.html", '<p style="a">x</p>',
                                                                    '<p style="a">y</p>')))
        self.assertNotIn("DESIGN.md", self.after("Edit", self.edit("src/a.scss", "", ".b { color: red; }"),
                                                 rows=[]))

    def test_a_write_is_compared_with_the_file_before_it(self):
        self.task(A, APPROVED)
        note = self.after("Write", {"file_path": str(self.repo / "src/b.css"), "content": ".c { margin: 0; }\n"})
        self.assertIn("DESIGN.md rule 4", note)

    def test_a_large_stylesheet_edit_stays_within_the_hook_time_limit(self):
        """T4 timing (review V8): a long line with `{` and many colons once made the stylesheet pattern backtrack for
        seconds. The hook timeout is 5 s; this asserts well under it."""
        import time
        self.task(A, APPROVED)
        long_line = "a {" + "b:" * 100_000
        many = "\n".join(f".c{i} {{ margin: {i}px; }}" for i in range(20_000))
        start = time.monotonic()
        note = self.after("Edit", self.edit("src/a.scss", long_line + "\n" + many, long_line + "\n" + many + "\n.x { color: red; }"))
        self.assertLess(time.monotonic() - start, 3.0)
        self.assertIn("DESIGN.md rule 4", note)

    def test_a_small_change_notes_a_new_tag_or_class(self):
        (self.repo / "src").mkdir()
        (self.repo / "src/page.html").write_text("<p>Old</p>\n", encoding="utf-8")
        self.task(A, "- Small change: src/page.html — reword the heading", report=None)
        note = self.after("Edit", self.edit("src/page.html", "<p>Old</p>", '<p class="lead">New</p><b>x</b>'))
        self.assertIn("small change", note.lower())
        plain = self.after("Edit", self.edit("src/page.html", "<p>Old</p>", "<p>New</p>"))
        self.assertNotIn("small change", plain.lower())


if __name__ == "__main__":
    unittest.main()
