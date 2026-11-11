"""Stop hook: substantive gaps prompt one correction; cosmetic wording alone must not create a loop."""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks/plain_reply.py"


def transcript(folder: Path, reply: str, workflow: bool = True) -> Path:
    path = folder / "session.jsonl"
    prompt = "/workflow-axa:workflow add a badge" if workflow else "explain this function"
    rows = [{"type": "user", "message": {"role": "user", "content": prompt}},
            {"type": "assistant", "message": {"content": [{"type": "text", "text": reply}]}}]
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
    return path


def fire(event):
    result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input=json.dumps(event),
                            capture_output=True, text=True, encoding="utf-8")
    return result.returncode, result.stdout.strip()


class PlainReplyHookTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def test_cosmetic_wording_alone_does_not_force_another_turn(self):
        path = transcript(self.dir, "I've built it; it doesn't change the CSS — done.")
        self.assertEqual(fire({"transcript_path": str(path)}), (0, ""))
        self.assertEqual(fire({"transcript_path": str(path), "stop_hook_active": True}), (0, ""))

    def test_clean_reply_code_and_other_sessions_pass(self):
        self.assertEqual(fire({"transcript_path": str(transcript(self.dir, "I built it. It does not change the CSS."))}), (0, ""))
        self.assertEqual(fire({"transcript_path": str(transcript(self.dir, "Run `a; b` and see ```x — y; don't```."))}), (0, ""))
        self.assertEqual(fire({"transcript_path": str(transcript(self.dir, "It doesn't matter.", workflow=False))}), (0, ""))
        self.assertEqual(fire({"transcript_path": str(self.dir / "missing.jsonl")}), (0, ""))
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input="nope", capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_required_phase_files_must_be_opened(self):
        # Round 17: the agent ignored both phase reminders and never opened grilling or simple-english.
        path = self.dir / "session.jsonl"
        rows = [{"type": "user", "message": {"role": "user", "content": "/workflow-axa:workflow add"}},
                {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill",
                                                               "input": {"skill": "workflow-axa:workflow-clarify"}}]}},
                {"type": "assistant", "message": {"content": [{"type": "text", "text": "Questions are ready."}]}}]
        path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        decision = json.loads(fire({"transcript_path": str(path)})[1])
        self.assertIn("workflow-clarify: grilling/SKILL.md", decision["reason"])
        self.assertNotIn("ui-design", decision["reason"])  # no visible change in this session
        rows.insert(2, {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read",
                        "input": {"file_path": "D:\\workflow-axa\\skills\\grilling\\SKILL.md"}}]}})
        path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        self.assertEqual(fire({"transcript_path": str(path)}), (0, ""))
        rows.insert(3, {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Write",
                        "input": {"file_path": "plan.json", "content": "{\"ui_review\": {}}"}}]}})
        path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        self.assertIn("rule-maker/rules/DESIGN.md", json.loads(fire({"transcript_path": str(path)})[1])["reason"])

    def test_only_whole_reads_count_as_opened(self):
        # Round v2 (Hooqd): `wc -c .../simple-english/SKILL.md` counted as reading it, so the hook stayed silent.
        path = self.dir / "session.jsonl"
        def bash(command):
            return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash", "input": {"command": command}}]}}
        base = [{"type": "user", "message": {"role": "user", "content": "/workflow-axa:workflow add"}},
                {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill",
                 "input": {"skill": "workflow-axa:workflow-clarify"}}]}}]
        done = {"type": "assistant", "message": {"content": [{"type": "text", "text": "Questions are ready."}]}}
        g = "/d/workflow-axa/skills/grilling/SKILL.md"
        # A successful combined command cannot prove that a conditional cat ran.
        for command in (f"wc -c {g}", f"ls {g}", f"cat {g} | head -40", f"grep -n gate {g}",
                        f"cd /d/x && cat {g}; echo ---"):
            with self.subTest(command=command):
                path.write_text("\n".join(json.dumps(r) for r in base + [bash(command), done]), encoding="utf-8")
                self.assertIn("grilling/SKILL.md", json.loads(fire({"transcript_path": str(path)})[1])["reason"])
        for command in (f"cat {g}", f"cd /d/x; cat {g}; echo ---"):
            with self.subTest(command=command):
                path.write_text("\n".join(json.dumps(r) for r in base + [bash(command), done]), encoding="utf-8")
                self.assertEqual(fire({"transcript_path": str(path)}), (0, ""))
        partial = {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read",
                   "input": {"file_path": "D:\\workflow-axa\\skills\\grilling\\SKILL.md", "limit": 30}}]}}
        path.write_text("\n".join(json.dumps(r) for r in base + [partial, done]), encoding="utf-8")
        self.assertIn("grilling/SKILL.md", json.loads(fire({"transcript_path": str(path)})[1])["reason"])

    def test_a_whole_read_of_a_phase_skill_loads_that_phase_only_in_a_started_session(self):
        # E5: the router's fallback ("or read its SKILL.md in full") loaded the phase, but its required reads were
        # never checked. A partial read does not load it.
        path = self.dir / "session.jsonl"
        def read(**data):
            return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": data}]}}
        base = [{"type": "user", "message": {"role": "user", "content": "/workflow-axa:workflow add"}}]
        done = {"type": "assistant", "message": {"content": [{"type": "text", "text": "Questions are ready."}]}}
        skill = "D:\\workflow-axa\\skills\\workflow-clarify\\SKILL.md"
        path.write_text("\n".join(json.dumps(r) for r in base + [read(file_path=skill), done]), encoding="utf-8")
        self.assertIn("workflow-clarify: grilling/SKILL.md", json.loads(fire({"transcript_path": str(path)})[1])["reason"])
        path.write_text("\n".join(json.dumps(r) for r in base + [read(file_path=skill, limit=20), done]), encoding="utf-8")
        self.assertEqual(fire({"transcript_path": str(path)}), (0, ""))
        # H2 (2026-11-11): the read loads the phase only in a session that started a workflow or wrote a task record.
        # A whole read to explain the skill loads nothing.
        question = [{"type": "user", "message": {"role": "user", "content": "how does clarify work?"}}]
        path.write_text("\n".join(json.dumps(r) for r in question + [read(file_path=skill), done]), encoding="utf-8")
        self.assertEqual(fire({"transcript_path": str(path)}), (0, ""))
        record = {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Write", "input": {
            "file_path": "D:/p/docs/plans/2026-11-11-x/TODO.md", "content": "x"}}]}}
        path.write_text("\n".join(json.dumps(r) for r in question + [record, read(file_path=skill), done]), encoding="utf-8")
        self.assertIn("workflow-clarify: grilling/SKILL.md", json.loads(fire({"transcript_path": str(path)})[1])["reason"])
        # When the host sets CLAUDE_PLUGIN_ROOT, only the package's own copy loads the phase.
        path.write_text("\n".join(json.dumps(r) for r in base + [read(file_path=skill), done]), encoding="utf-8")
        with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "D:\\workflow-axa"}):
            self.assertIn("workflow-clarify: grilling/SKILL.md", json.loads(fire({"transcript_path": str(path)})[1])["reason"])
        with mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": "C:\\plugins\\workflow-axa\\2.8.0"}):
            self.assertEqual(fire({"transcript_path": str(path)}), (0, ""))

    def test_code_changed_without_review_or_delivery_cannot_end_as_done(self):
        # Loop w2/w3 (Altinstar): comment edits were made, then "Done" and closed with no review and no deliver.
        path = self.dir / "session.jsonl"
        edit = {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Edit",
                "input": {"file_path": "D:/proj/src/services/GameCalls.ts", "old_string": "a", "new_string": "b"}}]}}
        record = {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Write",
                  "input": {"file_path": "D:/proj/docs/plans/t/PLAN.md", "content": "x"}}]}}
        rows = [{"type": "user", "message": {"role": "user", "content": "/workflow-axa:workflow fix typos"}},
                record, edit,
                {"type": "assistant", "message": {"content": [{"type": "text", "text": "The edits are made.\n\n**Done.**"}]}}]
        path.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
        reason = json.loads(fire({"transcript_path": str(path)})[1])["reason"]
        self.assertIn("no review", reason)
        reviewed = rows[:3] + [
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Agent",
             "input": {"description": "Independent review of the diff", "prompt": "review"}}]}},
            {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill",
             "input": {"skill": "workflow-axa:workflow-deliver"}}]}}, rows[3]]
        path.write_text("\n".join(json.dumps(r) for r in reviewed), encoding="utf-8")
        self.assertNotIn("no review", fire({"transcript_path": str(path)})[1])
        records_only = rows[:2] + rows[3:]
        path.write_text("\n".join(json.dumps(r) for r in records_only), encoding="utf-8")
        self.assertNotIn("no review", fire({"transcript_path": str(path)})[1])
        # Loop w5 (Hooqd, PletrixV2): helper files in the session scratchpad, outside the project, triggered it.
        scratch = {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Write",
                   "input": {"file_path": "C:\\Users\\x\\AppData\\Local\\Temp\\claude\\s\\scratchpad\\fill.py", "content": "x"}}]}}
        path.write_text("\n".join(json.dumps(r) for r in rows[:2] + [scratch, rows[3]]), encoding="utf-8")
        self.assertEqual(fire({"transcript_path": str(path), "cwd": "D:\\proj"}), (0, ""))
        waiting = rows[:3] + [{"type": "assistant", "message": {"content": [{"type": "text",
                  "text": "Built.\n\n**Waiting on you:** approve the review step."}]}}]
        path.write_text("\n".join(json.dumps(r) for r in waiting), encoding="utf-8")
        self.assertNotIn("no review", fire({"transcript_path": str(path)})[1])

    def test_only_a_review_agent_or_the_code_review_skill_counts_as_a_review(self):
        # Whole-feature review: any Agent call whose input mentioned "review" anywhere (even "preview") cleared it.
        path = self.dir / "session.jsonl"
        def call(name, **data):
            return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": data}]}}
        start = [{"type": "user", "message": {"role": "user", "content": "/workflow-axa:workflow fix typos"}},
                 call("Edit", file_path="D:/proj/src/a.ts", old_string="a", new_string="b")]
        done = {"type": "assistant", "message": {"content": [{"type": "text", "text": "**Done.**"}]}}
        for signal in (call("Agent", description="Preview the page", prompt="review the diff"),
                       call("Agent", description="Build ticket T2", prompt="then ask for a review"),
                       call("Read", file_path="D:/workflow-axa/skills/code-review/SKILL.md", limit=20)):
            with self.subTest(signal=signal):
                path.write_text("\n".join(json.dumps(r) for r in start + [signal, done]), encoding="utf-8")
                self.assertIn("no review", fire({"transcript_path": str(path)})[1])
        for signal in (call("Agent", description="Fresh check", subagent_type="code-reviewer", prompt="x"),
                       call("Agent", description="Review ticket T2", prompt="x"),
                       call("Skill", skill="workflow-axa:code-review"),
                       call("Read", file_path="D:\\workflow-axa\\skills\\code-review\\SKILL.md")):
            with self.subTest(signal=signal):
                path.write_text("\n".join(json.dumps(r) for r in start + [signal, done]), encoding="utf-8")
                self.assertNotIn("no review", fire({"transcript_path": str(path)})[1])

    def test_a_behind_rules_stamp_must_reach_the_owner(self):
        # Round v1 (Altinstar): rules_stamp.py said BEHIND, and the reply never mentioned it.
        path = self.dir / "session.jsonl"
        stamp = {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1",
                 "content": "STATE: BEHIND project 1.7.0 (AGENTS.md, checked 2026-11-03) < installed 1.8.0\nSAY: ..."}]}}
        rows = [{"type": "user", "message": {"role": "user", "content": "/workflow-axa:workflow plan it"}},
                {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read",
                 "input": {"file_path": "D:/workflow-axa/skills/grilling/SKILL.md"}}]}},
                stamp,
                {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill",
                 "input": {"skill": "workflow-axa:workflow-clarify"}}]}},
                {"type": "assistant", "message": {"content": [{"type": "text", "text": "Questions are ready."}]}}]
        path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        self.assertIn("rules audit", json.loads(fire({"transcript_path": str(path)})[1])["reason"])
        rows[-1]["message"]["content"][0]["text"] = ("Questions are ready. This project's rules were last checked "
                                                     "against shared rules 1.7.0. Do you want the rules audit?")
        path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        self.assertEqual(fire({"transcript_path": str(path)}), (0, ""))

    def test_reads_before_the_phase_load_count_until_compaction(self):
        # Round 22: the router read the design files, then clarify loaded. The hook demanded them again
        # three turns running, and the late reread made the presented plan report stale.
        path = self.dir / "session.jsonl"
        read = lambda rel: {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read",
                            "input": {"file_path": f"D:/workflow-axa/skills/{rel}"}}]}}
        rows = [{"type": "user", "message": {"role": "user", "content": "/workflow-axa:workflow add"}},
                read("grilling/SKILL.md"),
                {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill",
                                                               "input": {"skill": "workflow-axa:workflow-clarify"}}]}},
                {"type": "assistant", "message": {"content": [{"type": "text", "text": "Questions are ready."}]}}]
        path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        self.assertEqual(fire({"transcript_path": str(path)}), (0, ""))
        rows.insert(2, {"type": "system", "subtype": "compact_boundary", "content": "Conversation compacted"})
        path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        self.assertIn("workflow-clarify: grilling/SKILL.md", json.loads(fire({"transcript_path": str(path)})[1])["reason"])

    def test_report_phase_stop_names_missing_flowchart_guide(self):
        path = self.dir / 'session.jsonl'
        for phase in ('workflow-specify', 'workflow-deliver'):
            rows = [{'type': 'user', 'message': {'role': 'user', 'content': f'/workflow-axa:{phase}'}},
                    {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'Waiting for approval.'}]}}]
            path.write_text('\n'.join(json.dumps(r) for r in rows), encoding='utf-8')
            reason = json.loads(fire({'transcript_path': str(path)})[1])['reason']
            self.assertIn('codebase-map/FLOWCHART-DESIGN.md', reason)

    def test_project_required_reads_leave_package_guide_stop_checks_unchanged(self):
        # R10: project declarations are enforced before phase entry and report operations (phase_gate.py), not here.
        # The package-guide check keeps its legacy evidence: an ID-less whole read still counts, a failed one does not.
        (self.dir / '.git').mkdir()
        (self.dir / 'AGENTS.md').write_text('<!-- workflow-axa:required-read phases=specify,execute,deliver '
                                            'path="tests/README.md" -->\n', encoding='utf-8')
        path = self.dir / 'session.jsonl'
        grilling = 'D:/workflow-axa/skills/grilling/SKILL.md'
        load = {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Skill',
                'input': {'skill': 'workflow-axa:workflow-clarify'}}]}}
        done = {'type': 'assistant', 'message': {'content': [{'type': 'text', 'text': 'Questions are ready.'}]}}
        legacy = {'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'name': 'Read',
                  'input': {'file_path': grilling}}]}}
        failed = [{'type': 'assistant', 'message': {'content': [{'type': 'tool_use', 'id': 'g1', 'name': 'Read',
                   'input': {'file_path': grilling}}]}},
                  {'type': 'user', 'message': {'role': 'user', 'content': [{'type': 'tool_result', 'tool_use_id': 'g1',
                   'is_error': True, 'content': 'Permission denied'}]}}]
        start = [{'type': 'user', 'message': {'role': 'user', 'content': '/workflow-axa:workflow add'}}, load]
        event = {'transcript_path': str(path), 'cwd': str(self.dir)}
        path.write_text('\n'.join(json.dumps(r) for r in start + [legacy, done]), encoding='utf-8')
        self.assertEqual(fire(event), (0, ''))
        path.write_text('\n'.join(json.dumps(r) for r in start + failed + [done]), encoding='utf-8')
        reason = json.loads(fire(event)[1])['reason']
        self.assertIn('workflow-clarify: grilling/SKILL.md', reason)
        self.assertNotIn('tests/README.md', reason)
        # A valid JSON line that is not an object is skipped, not a reason to drop the whole check.
        path.write_text('\n'.join(json.dumps(r) for r in [[1]] + start + failed + ['text', done]), encoding='utf-8')
        self.assertIn('workflow-clarify: grilling/SKILL.md', json.loads(fire(event)[1])['reason'])

    def test_hooks_json_wires_it_on_stop(self):
        data = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/plain_reply.py", data["hooks"]["Stop"][0]["hooks"][0]["command"])


def call(name, **data):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": data}]}}


def said(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


def typed(text):
    return {"type": "user", "message": {"role": "user", "content": text}}


EDIT = call("Edit", file_path="D:/p/src/a.py", old_string="a", new_string="b")
DONE = said("Fixed it.\n\n**Done.**")


class SessionCheckTests(unittest.TestCase):
    """H2 review (agreement R12): which sessions get the Stop checks. Only the old match of "workflow-axa" anywhere in
    a tool input (a path) is dropped; package skills and typed package commands still make a workflow session."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "session.jsonl"

    def stop(self, rows, hook=HOOK, env=None):
        self.path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(hook)], capture_output=True, text=True,
                                input=json.dumps({"transcript_path": str(self.path), "cwd": "D:\\p"}),
                                encoding="utf-8", env=env)
        return result.returncode, result.stdout.strip()

    def assert_review_demand(self, rows):
        code, out = self.stop(rows)
        self.assertEqual(code, 0)
        self.assertIn("no review", out and json.loads(out)["reason"])

    def test_a_package_skill_call_makes_a_workflow_session(self):
        for name in ("workflow-axa:code-review", "code-review", "workflow-axa:workflow", "workflow"):
            with self.subTest(skill=name):
                self.assert_review_demand([typed("fix it"), call("Skill", skill=name), EDIT, DONE])

    def test_typed_package_text_makes_a_workflow_session(self):
        self.assert_review_demand([typed("fix it, then run workflow-axa:code-review"), EDIT, DONE])

    def test_a_workflow_axa_path_or_another_plugins_skill_does_not(self):
        for row in (call("Read", file_path="D:/workflow-axa/hooks/phase_gate.py"),
                    call("Skill", skill="otherplugin:code-review"), call("Skill", skill="otherplugin:workflow")):
            with self.subTest(row=row):
                self.assertEqual(self.stop([typed("fix it"), row, EDIT, DONE]), (0, ""))

    def test_only_a_real_phase_start_demands_phase_reads(self):
        clarify = "D:/workflow-axa/skills/workflow-clarify/SKILL.md"
        ready = said("Questions are ready.")
        # A package skill makes a workflow session, but not a phase start: a whole read loads no phase.
        self.assertEqual(self.stop([typed("fix it"), call("Skill", skill="workflow-axa:code-review"),
                                    call("Read", file_path=clarify), ready]), (0, ""))
        # Another plugin's phase-named skill is not this package's phase.
        self.assertEqual(self.stop([typed("/workflow-axa:workflow add"), call("Skill", skill="otherplugin:workflow-clarify"),
                                    ready]), (0, ""))
        code, out = self.stop([typed("/workflow-axa:workflow add"), call("Skill", skill="workflow-clarify"), ready])
        self.assertIn("workflow-clarify: grilling/SKILL.md", json.loads(out)["reason"])

    def test_a_broken_or_missing_phase_gate_leaves_the_stop_hook_silent(self):
        root = Path(self.tmp.name) / "plugin"
        (root / "hooks").mkdir(parents=True)
        for name in ("plain_reply.py", "phase_reads.py"):
            (root / "hooks" / name).write_bytes((ROOT / "hooks" / name).read_bytes())
        rows = [typed("/workflow-axa:workflow add"), call("Skill", skill="workflow-axa:workflow-clarify"),
                said("Questions are ready.")]
        env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(root)}
        self.assertEqual(self.stop(rows, root / "hooks/plain_reply.py", env), (0, ""))  # phase_gate.py missing
        for broken in ("def broken(:\n", "import no_such_module_h2\n", "raise AttributeError('x')\n"):
            with self.subTest(broken=broken):
                (root / "hooks/phase_gate.py").write_text(broken, encoding="utf-8")
                self.assertEqual(self.stop(rows, root / "hooks/plain_reply.py", env), (0, ""))
        # Control: the same plugin root with a working phase_gate.py demands the reads.
        (root / "hooks/phase_gate.py").write_bytes((ROOT / "hooks/phase_gate.py").read_bytes())
        code, out = self.stop(rows, root / "hooks/plain_reply.py", env)
        self.assertIn("workflow-clarify: grilling/SKILL.md", json.loads(out)["reason"])


if __name__ == "__main__":
    unittest.main()
