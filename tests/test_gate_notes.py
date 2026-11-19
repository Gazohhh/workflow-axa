"""T4 of 2026-11-12-approval-gate-false-refusals (owner Q8 a): after an edit, the gate notes new styling in an
application file, and a new tag or class in a small change. It never refuses."""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import unittest

from test_gate_regressions import CACHE, GATE, ROOT, A, GateCase, write_rows
from test_phase_gate_hook import APPROVED, ROUTER, hooked

HEAVY = re.compile(r'\|\s+(?:hashlib|subprocess|tempfile)\s*$', re.M)


def run_registered(hook_event: str, event) -> subprocess.CompletedProcess:
    """The command hooks.json registers for the event, as the host runs it, with Python's import log on stderr."""
    command = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"][hook_event][0]["hooks"][0]["command"]
    args = [a.replace("${CLAUDE_PLUGIN_ROOT}", str(ROOT)).strip('"') for a in re.findall(r'"[^"]*"|\S+', command)]
    args[0] = sys.executable if args[0] == "python" else args[0]
    result = subprocess.run([args[0], "-X", "importtime", *args[1:]], input=json.dumps(event), capture_output=True,
                            text=True, encoding="utf-8", env={**os.environ, "WORKFLOW_AXA_GATE_CACHE": CACHE.name})
    assert result.returncode == 0, result.stderr
    return result


def output(result: subprocess.CompletedProcess) -> str:
    return json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"] if result.stdout.strip() else ""


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
        self.assertNotIn("DESIGN.md", self.after("Edit", self.edit(f"docs/plans/{A}/x.html", "x", 'style="a"')))
        self.assertNotIn("DESIGN.md", self.after("Edit", self.edit(".artifacts/run/a.html", "x", 'style="a"')))
        self.assertNotIn("DESIGN.md", self.after("Edit", self.edit("src/a.spec.ts", "x", 'style="a"')))
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


CUE = "sty" + "le"


class AfterCallHook(GateCase):
    """Item 3 of 2026-11-19-workflow-speed: the registered PostToolUse/UserPromptSubmit hook gives the output it gave
    before, and an event that cannot produce output returns before the gate's heavy imports."""

    def setUp(self):
        super().setUp()
        self.report = self.task(A, APPROVED) / "reviews/plan-r1.html"
        write_rows(self.path, hooked([ROUTER] + self.approval(A), self.repo))

    def event(self, tool_name, data):
        return {"hook_event_name": "PostToolUse", "tool_name": tool_name, "tool_input": data,
                "transcript_path": str(self.path), "cwd": str(self.repo)}

    def cases(self):
        code, doc, shown = str(self.repo / "src/a.tsx"), str(self.repo / "README.md"), f"docs/plans/{A}/reviews/plan-r1.html"
        digest = hashlib.sha256(self.report.read_bytes()).hexdigest()
        mark = f"workflow-axa report fingerprint: {shown} sha256={digest}"
        reply = f"workflow-axa report at owner reply: {shown} sha256={digest}"
        added = f"<p/>\n<{CUE}>{{css}}</{CUE}>"
        return (
            ("cue edit", "PostToolUse", self.event("Edit", {"file_path": code, "old_string": "<p/>",
                                                           "new_string": added}), "DESIGN.md rule 4"),
            ("markdown edit", "PostToolUse", self.event("Edit", {"file_path": doc, "old_string": "<p/>",
                                                                "new_string": added}), ""),
            ("markdown write", "PostToolUse", self.event("Write", {"file_path": doc, "content": added}), ""),
            ("report read", "PostToolUse", self.event("Read", {"file_path": str(self.report)}), mark),
            ("code read", "PostToolUse", self.event("Read", {"file_path": code}), ""),
            ("report bash", "PostToolUse", self.event("Bash", {"command": f"cat {shown}"}), mark),
            ("quoted report bash", "PostToolUse", self.event("Bash", {"command": f'cat "{shown[:-2]}"ml'}), mark),
            ("plain bash", "PostToolUse", self.event("Bash", {"command": "git status"}), ""),
            ("plain powershell", "PostToolUse", self.event("PowerShell", {"command": "Get-ChildItem"}), ""),
            ("question", "PostToolUse", self.event("AskUserQuestion", {"questions": []}), reply),
            ("prompt", "UserPromptSubmit", {"hook_event_name": "UserPromptSubmit", "prompt": "Yes to both",
                                            "transcript_path": str(self.path), "cwd": str(self.repo)}, reply),
        )

    def test_the_registered_hook_keeps_its_output(self):
        for name, hook_event, event, expected in self.cases():
            with self.subTest(case=name):
                today = run_post(event)
                if expected:
                    self.assertIn(expected, today)
                else:
                    self.assertEqual(today, "")
                self.assertEqual(output(run_registered(hook_event, event)), today)

    def test_an_event_without_output_skips_the_heavy_imports(self):
        for name, hook_event, event, expected in self.cases():
            with self.subTest(case=name):
                result = run_registered(hook_event, event)
                self.assertEqual(bool(HEAVY.search(result.stderr)), bool(expected))
        for raw in ("nope", "[]"):
            with self.subTest(stdin=raw):
                result = subprocess.run([sys.executable, "-X", "utf8", "-I", "-X", "importtime", str(GATE),
                                         "--hook-protocol=1"], input=raw, capture_output=True, text=True, encoding="utf-8")
                self.assertEqual((result.returncode, result.stdout), (0, ""))
                self.assertIsNone(HEAVY.search(result.stderr))


if __name__ == "__main__":
    unittest.main()
