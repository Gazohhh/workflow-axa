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
