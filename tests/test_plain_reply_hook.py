"""plain_reply Stop hook: one rewrite request for contractions, em-dashes or semicolons in workflow sessions only."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

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

    def test_contractions_dashes_and_semicolons_ask_for_one_rewrite(self):
        path = transcript(self.dir, "I've built it; it doesn't change the CSS — done.")
        code, out = fire({"transcript_path": str(path)})
        self.assertEqual(code, 0)
        decision = json.loads(out)
        self.assertEqual(decision["decision"], "block")
        for word in ("contractions", "em-dashes", "semicolons"):
            self.assertIn(word, decision["reason"])
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
        self.assertIn("rule-maker/rules/design.md", json.loads(fire({"transcript_path": str(path)})[1])["reason"])

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
        for command in (f"wc -c {g}", f"ls {g}", f"cat {g} | head -40", f"grep -n gate {g}"):
            with self.subTest(command=command):
                path.write_text("\n".join(json.dumps(r) for r in base + [bash(command), done]), encoding="utf-8")
                self.assertIn("grilling/SKILL.md", json.loads(fire({"transcript_path": str(path)})[1])["reason"])
        for command in (f"cat {g}", f"cd /d/x && cat {g}; echo ---"):
            with self.subTest(command=command):
                path.write_text("\n".join(json.dumps(r) for r in base + [bash(command), done]), encoding="utf-8")
                self.assertEqual(fire({"transcript_path": str(path)}), (0, ""))
        partial = {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read",
                   "input": {"file_path": "D:\\workflow-axa\\skills\\grilling\\SKILL.md", "limit": 30}}]}}
        path.write_text("\n".join(json.dumps(r) for r in base + [partial, done]), encoding="utf-8")
        self.assertIn("grilling/SKILL.md", json.loads(fire({"transcript_path": str(path)})[1])["reason"])

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

    def test_hooks_json_wires_it_on_stop(self):
        data = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/plain_reply.py", data["hooks"]["Stop"][0]["hooks"][0]["command"])


if __name__ == "__main__":
    unittest.main()
