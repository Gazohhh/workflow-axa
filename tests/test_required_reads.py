"""The shared required-read parser (T6 of docs/plans/2026-11-15-workflow-redesign, G3 and N3).

skills/rule-maker/scripts/required_reads.py is the only parser of the declaration grammar; docs_check.py and
hooks/phase_gate.py both use it. `paths=` scopes a read to tasks whose recorded scope names a matching file.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

import tempfile

from test_phase_gate_hook import ROUTER, run_hook

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


rr = load("required_reads_under_test", ROOT / "skills/rule-maker/scripts/required_reads.py")


class ParserTests(unittest.TestCase):

    def test_well_formed_declarations(self):
        found = rr.parse('<!-- workflow-axa:required-read phases=specify,execute path="tests/README.md" -->\n'
                         'text\n'
                         '<!-- workflow-axa:required-read phases=specify path="docs/finance.md" '
                         'paths="src/finance/**,app/Billing/*" -->\n')
        self.assertEqual([(d.line, d.phases, d.path, d.paths, d.error) for d in found], [
            (1, ("specify", "execute"), "tests/README.md", (), ""),
            (3, ("specify",), "docs/finance.md", ("src/finance/**", "app/Billing/*"), "")])

    def test_malformed_declarations_carry_their_error(self):
        cases = ['<!-- workflow-axa:required-read phases=plan path="a.md" -->',
                 '<!-- workflow-axa:required-read path="a.md" -->',
                 '<!-- workflow-axa:required-read phases=specify path="../a.md" -->',
                 '<!-- workflow-axa:required-read phases=specify path="docs/*.md" -->',
                 '<!-- workflow-axa:required-read phases=specify path="a.md" paths="/abs/**" -->',
                 '<!-- workflow-axa:required-read phases=specify path="a.md" paths="src/[ab]/**" -->',
                 '<!-- workflow-axa:required-read phases=specify path="a.md" paths="" -->']
        for text in cases:
            with self.subTest(text=text):
                [declaration] = rr.parse(text)
                self.assertTrue(declaration.error)

    def test_a_declaration_must_start_its_own_line(self):
        self.assertEqual(rr.parse('see <!-- workflow-axa:required-read phases=specify path="a.md" -->'), [])

    def test_paths_scope_the_read(self):
        [scoped] = rr.parse('<!-- workflow-axa:required-read phases=specify path="a.md" paths="src/finance/**,*.sql" -->')
        self.assertTrue(rr.applies(scoped, ["src/finance/vat.ts"]))
        self.assertTrue(rr.applies(scoped, ["src/finance/deep/x/y.ts"]))
        self.assertTrue(rr.applies(scoped, ["schema.sql"]))
        self.assertFalse(rr.applies(scoped, ["docs/guide.md", "AGENTS.md"]))
        self.assertFalse(rr.applies(scoped, ["src/financeX/a.ts", "db/schema.sql"]))
        self.assertTrue(rr.applies(scoped, None))  # unknown scope: required (fail safe)
        [plain] = rr.parse('<!-- workflow-axa:required-read phases=specify path="a.md" -->')
        self.assertTrue(rr.applies(plain, ["docs/guide.md"]))

    def test_a_folder_or_glob_scope_overlapping_the_declaration_requires_the_read(self):
        [scoped] = rr.parse('<!-- workflow-axa:required-read phases=specify path="a.md" paths="src/finance/**" -->')
        self.assertTrue(rr.applies(scoped, ["src/"]))  # the folder contains the declared area
        self.assertTrue(rr.applies(scoped, ["src/finance/deep/"]))
        self.assertTrue(rr.applies(scoped, ["src/**"]))
        self.assertFalse(rr.applies(scoped, ["docs/"]))
        self.assertFalse(rr.applies(scoped, ["src/other/"]))

    def test_docs_check_and_the_gate_use_this_module(self):
        for rel in ("skills/rule-maker/scripts/docs_check.py", "hooks/phase_gate.py"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            with self.subTest(file=rel):
                self.assertIn("required_reads.py", text)
                self.assertNotIn("phases=([a-z]+", text)  # no second copy of the grammar


class ScopedGateTests(unittest.TestCase):
    """N3: the session's project required docs/finance-quotations.md before every specify, a docs-only task too."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = Path(tmp.name) / "repo"
        (self.repo / ".git").mkdir(parents=True)
        (self.repo / "tests").mkdir()
        (self.repo / "tests/README.md").write_text("# How to verify\n", encoding="utf-8")
        self.path = Path(tmp.name) / "session.jsonl"

    def rules(self, *lines):
        (self.repo / "AGENTS.md").write_text("# Rules\n\n" + "\n".join(lines) + "\n", encoding="utf-8")

    def denied(self, rows):
        self.path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        out = run_hook({"tool_name": "Skill", "tool_input": {"skill": "workflow-specify"}, "cwd": str(self.repo),
                        "transcript_path": str(self.path)})
        return out and out["permissionDecision"] == "deny" and out["permissionDecisionReason"] or None

    def scoped(self):
        (self.repo / "docs").mkdir(exist_ok=True)
        (self.repo / "docs/finance.md").write_text("# Finance\n", encoding="utf-8")
        self.rules('<!-- workflow-axa:required-read phases=specify path="docs/finance.md" paths="src/finance/**" -->')

    def task(self, *lines, name="2026-11-15-t", body=""):
        folder = self.repo / "docs/plans" / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "PLAN.md").write_text("# T\n\n## Current checkpoint\n- Status: x\n" + "\n".join(lines) + "\n\n## Goal\n"
                                        + body + "\n", encoding="utf-8")
        return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Write",
                "input": {"file_path": str(folder / "TODO.md"), "content": "x"}}]}}

    def test_a_task_outside_the_scope_needs_no_read(self):
        self.scoped()
        rows = [ROUTER, self.task("- Scope paths: `docs/guide.md`, `AGENTS.md`")]
        self.assertIsNone(self.denied(rows))
        rows = [ROUTER, self.task("- Changed files: `docs/guide.md`")]
        self.assertIsNone(self.denied(rows))

    def test_a_task_inside_the_scope_needs_the_read(self):
        self.scoped()
        self.assertIn("docs/finance.md", self.denied([ROUTER, self.task("- Scope paths: `src/finance/vat.ts`")]))
        self.assertIn("docs/finance.md", self.denied([ROUTER, self.task("- Scope paths: `src/`")]))  # parent folder

    def test_an_unknown_scope_needs_the_read(self):
        self.scoped()
        self.assertIn("docs/finance.md", self.denied([ROUTER]))  # no task recorded yet
        self.assertIn("docs/finance.md", self.denied([ROUTER, self.task("- Status note without paths")]))
        # Incidental backticked references in prose are never scope: only the Scope paths / Changed files line is.
        rows = [ROUTER, self.task(body="See `record.py` and `docs/guide.md` for the VAT change.")]
        self.assertIn("docs/finance.md", self.denied(rows))
        self.assertIn("docs/finance.md", self.denied([ROUTER, self.task("- Scope paths: `../outside/a.ts`")]))
        # One entry it can't read makes the whole scope unknown, never the readable subset.
        for line in ("- Scope paths: `docs/guide.md`, `src/finance/my file.ts`",
                     "- Scope paths: `docs/guide.md`, src/finance/vat.ts",
                     "- Scope paths: `docs/guide.md` and the finance service",
                     "- Changed files: none"):
            with self.subTest(line=line):
                self.assertIn("docs/finance.md", self.denied([ROUTER, self.task(line)]))

    def test_a_record_written_to_another_task_does_not_change_whose_scope_counts(self):
        """The finance task is current at the owner's last message; a note written into a docs task afterwards must
        not let its docs-only scope skip the finance read (the N4 task-switch assumption)."""
        self.scoped()
        rows = [ROUTER, self.task("- Scope paths: `src/finance/vat.ts`", name="2026-11-15-finance"),
                {"type": "user", "message": {"role": "user", "content": "go ahead"}},
                self.task("- Scope paths: `docs/guide.md`", name="2026-11-15-docs")]
        self.assertIn("docs/finance.md", self.denied(rows))
        # The mirror case: the docs task is current at the owner's message; a later finance note doesn't change that.
        rows = [ROUTER, self.task("- Scope paths: `docs/guide.md`", name="2026-11-15-docs"),
                {"type": "user", "message": {"role": "user", "content": "go ahead"}},
                self.task("- Scope paths: `src/finance/vat.ts`", name="2026-11-15-finance")]
        self.assertIsNone(self.denied(rows))

    def test_an_unscoped_declaration_of_the_same_file_applies_to_every_task(self):
        self.scoped()
        (self.repo / "CLAUDE.md").write_text('<!-- workflow-axa:required-read phases=specify path="docs/finance.md" -->\n',
                                             encoding="utf-8")
        rows = [ROUTER, self.task("- Changed files: `docs/guide.md`")]
        self.assertIn("docs/finance.md", self.denied(rows))

    def test_a_plugin_copy_without_the_parser_fails_closed(self):
        import os
        import subprocess
        plugin = Path(self.repo.parent) / "plugin"
        (plugin / "hooks").mkdir(parents=True)
        for name in ("phase_gate.py", "read_evidence.py"):
            (plugin / "hooks" / name).write_bytes((ROOT / "hooks" / name).read_bytes())
        self.rules('<!-- workflow-axa:required-read phases=specify path="tests/README.md" -->')
        self.path.write_text(json.dumps(ROUTER), encoding="utf-8")
        done = subprocess.run([sys.executable, "-X", "utf8", "-I", str(plugin / "hooks/phase_gate.py"), "--hook-protocol=1"],
                              input=json.dumps({"tool_name": "Skill", "tool_input": {"skill": "workflow-specify"},
                                                "cwd": str(self.repo), "transcript_path": str(self.path)}),
                              capture_output=True, text=True, encoding="utf-8",
                              env={**os.environ, "CLAUDE_PLUGIN_ROOT": str(plugin)})
        out = json.loads(done.stdout)["hookSpecificOutput"]
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("required_reads.py cannot be loaded", out["permissionDecisionReason"])

    def test_a_malformed_paths_value_blocks_the_phase(self):
        self.rules('<!-- workflow-axa:required-read phases=specify path="tests/README.md" paths="/etc/**" -->')
        self.assertIn("not a list of root-relative globs", self.denied([ROUTER]))


class DocsCheckNotes(unittest.TestCase):

    def test_docs_check_notes_a_malformed_paths_value(self):
        import subprocess
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / "a.md").write_text("# A\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("# Rules\n\n[A](a.md)\n\n"
                                            '<!-- workflow-axa:required-read phases=specify path="a.md" paths="/x/**" -->\n',
                                            encoding="utf-8")
            done = subprocess.run([sys.executable, "-X", "utf8", "-I", str(ROOT / "skills/rule-maker/scripts/docs_check.py"),
                                   str(root), "--json"], capture_output=True, text=True, encoding="utf-8")
            findings = json.loads(done.stdout)["findings"]
            self.assertTrue(any(f["code"] == "malformed-marker" and f["severity"] == "note" for f in findings), findings)


if __name__ == "__main__":
    unittest.main()
