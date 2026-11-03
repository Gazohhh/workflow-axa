"""record.py: line-ending-safe task-record edits (retro E23: ~100 inline scripts per eval run)."""
from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "skills/workflow/scripts/record.py"


def run(*args, stdin=None):
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), *map(str, args)],
                          input=stdin, capture_output=True, text=True, encoding="utf-8")


class RecordTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name, text, eol):
        path = self.dir / name
        path.write_bytes(text.replace("\n", eol).encode("utf-8"))
        return path

    def test_set_line_keeps_crlf(self):
        plan = self.write("PLAN.md", "# T\n- Next safe action: old\n- Other: x\n", "\r\n")
        self.assertEqual(run("set-line", plan, "- Next safe action:", "- Next safe action: run T2 check").returncode, 0)
        raw = plan.read_bytes()
        self.assertIn(b"- Next safe action: run T2 check\r\n", raw)
        self.assertNotIn(b"\n-", raw.replace(b"\r\n", b""))

    def test_append_keeps_lf_and_separates(self):
        findings = self.write("FINDINGS.md", "# F\n\n## E1\nold\n", "\n")
        self.assertEqual(run("append", findings, "-", stdin="## E2\nnew line ü\n").returncode, 0)
        self.assertEqual(findings.read_text(encoding="utf-8"), "# F\n\n## E1\nold\n\n## E2\nnew line ü\n")

    def test_tick_requires_evidence_and_an_open_box(self):
        todo = self.write("TODO.md", "- [ ] T1 — build it\n- [x] T2 — done; verified: V1\n", "\r\n")
        self.assertEqual(run("tick", todo, "T1", " ").returncode, 1)
        self.assertEqual(run("tick", todo, "T9", "V3").returncode, 1)
        self.assertEqual(run("tick", todo, "T1", "FINDINGS V3").returncode, 0)
        self.assertIn(b"- [x] T1 \xe2\x80\x94 build it; verified: FINDINGS V3\r\n", todo.read_bytes())

    def test_tick_does_not_double_the_verified_prefix(self):
        todo = self.write("TODO.md", "- [ ] T2 — add button\n", "\n")
        self.assertEqual(run("tick", todo, "T2", "verified: V3").returncode, 0)
        self.assertEqual(todo.read_text(encoding="utf-8"), "- [x] T2 — add button; verified: V3\n")

    def test_new_creates_once(self):
        target = self.dir / "FINDINGS.md"
        self.assertEqual(run("new", target, "-", stdin="# Findings\n\n## E1\nfirst\n").returncode, 0)
        self.assertEqual(target.read_text(encoding="utf-8"), "# Findings\n\n## E1\nfirst\n")
        self.assertEqual(run("new", target, "-", stdin="other").returncode, 2)
        self.assertEqual(run("new", self.dir / "missing-folder" / "PLAN.md", "-", stdin="x").returncode, 2)

    def test_new_follows_crlf_input_or_siblings(self):
        # Round-4 retro: a CRLF project's new records came out LF.
        crlf_input = self.dir / "in.txt"
        crlf_input.write_bytes(b"# Plan\r\nline\r\n")
        self.assertEqual(run("new", self.dir / "PLAN.md", crlf_input).returncode, 0)
        self.assertEqual((self.dir / "PLAN.md").read_bytes(), b"# Plan\r\nline\r\n")
        self.assertEqual(run("new", self.dir / "TODO.md", "-", stdin="# Todo\n- [ ] T1\n").returncode, 0)
        self.assertEqual((self.dir / "TODO.md").read_bytes(), b"# Todo\r\n- [ ] T1\r\n")

    def test_replace_section_keeps_other_sections_and_crlf(self):
        plan = self.write("PLAN.md", "# T\n\n## Agreement\nold line\n### Sub\nold sub\n\n## Approval\nkeep me\n", "\r\n")
        self.assertEqual(run("replace-section", plan, "## Agreement", "-", stdin="new agreement\n").returncode, 0)
        raw = plan.read_bytes().decode("utf-8")
        self.assertIn("## Agreement\r\n\r\nnew agreement\r\n\r\n## Approval\r\nkeep me", raw)
        self.assertNotIn("old sub", raw)
        self.assertEqual(run("replace-section", plan, "## Missing", "-", stdin="x").returncode, 1)

    def test_batch_applies_all_or_nothing_and_keeps_crlf(self):
        # Round-4 retro: 14 silent node -e replaces and three line-ending repair calls in one run.
        plan = self.write("PLAN.md", "# T\n- Goal: next to the name\n- R1: next to the name\n- Next: x\n", "\r\n")
        good = '[{"find": "- Goal: next to the name", "replace": "- Goal: under the name"}, {"find": "- Next: x", "replace": "- Next: y"}]'
        result = run("batch", plan, "-", stdin=good)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(plan.read_bytes(), b"# T\r\n- Goal: under the name\r\n- R1: next to the name\r\n- Next: y\r\n")
        before = plan.read_bytes()
        for edits, code in (('[{"find": "- Next: y", "replace": "q"}, {"find": "the name", "replace": "z"}]', 1),
                            ('[{"find": "missing", "replace": "z"}]', 1), ('{"find": "x"}', 2), ('not json', 2)):
            with self.subTest(edits=edits):
                self.assertEqual(run("batch", plan, "-", stdin=edits).returncode, code)
                self.assertEqual(plan.read_bytes(), before)

    def test_replace_section_refuses_a_duplicate_heading(self):
        # Round 7: a body that repeated its heading left "## Approval" twice.
        plan = self.write("PLAN.md", "# T\n\n## Approval\nold\n", "\n")
        result = run("replace-section", plan, "## Approval", "-", stdin="## Approval\nnew\n")
        self.assertEqual(result.returncode, 1)
        self.assertIn("would appear twice", result.stdout)
        self.assertEqual(plan.read_text(encoding="utf-8"), "# T\n\n## Approval\nold\n")

    def test_missing_line_or_file_blocks_without_writing(self):
        plan = self.write("PLAN.md", "# T\n", "\n")
        self.assertEqual(run("set-line", plan, "- Absent:", "x").returncode, 1)
        self.assertEqual(plan.read_text(encoding="utf-8"), "# T\n")
        self.assertEqual(run("append", self.dir / "missing.md", "-", stdin="x").returncode, 2)


if __name__ == "__main__":
    unittest.main()
