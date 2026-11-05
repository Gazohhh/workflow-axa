"""Vendored Matt Pocock skills: separate skills with provenance, license and adaptation, loaded by the phases."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("grilling", "tdd", "code-review", "writing-for-agents", "codebase-design", "domain-modeling", "implement-spec", "retro")
USER_ONLY = {"implement-spec", "retro"}


class VendoredSkillTests(unittest.TestCase):
    def test_each_is_a_registered_separate_skill_with_license(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        for name in NAMES:
            folder = ROOT / "skills" / name
            self.assertIn(f"./skills/{name}", plugin["skills"])
            self.assertIn("MIT License", (folder / "LICENSE").read_text(encoding="utf-8"), name)
            text = (folder / "SKILL.md").read_text(encoding="utf-8")
            self.assertTrue(text.startswith(f"---\nname: {name}\n"), name)
            self.assertEqual("disable-model-invocation: true" in text.split("---", 2)[1], name in USER_ONLY, name)
            self.assertIn("## workflow-axa adaptation", text, name)
            self.assertIn("Bundled with workflow-axa from [mattpocock/skills]", text, name)
        self.assertFalse((ROOT / "skills/workflow/specialists").exists(), "old bundled folder must be gone")

    def test_provenance_records_every_upstream_file(self):
        readme = (ROOT / "VENDORED-SKILLS.md").read_text(encoding="utf-8")
        self.assertRegex(readme, r"commit `[0-9a-f]{40}`")
        rows = re.findall(r"^\| ([\w-]+) \| `([^`]+)` \| `([0-9a-f]{16})` \| (`[0-9a-f]{16}`|—) \|$", readme, re.M)
        self.assertEqual({r[0] for r in rows}, set(NAMES))
        copied = [p for name in NAMES for p in (ROOT / "skills" / name).glob("*.md")]
        self.assertEqual(len(rows), len(copied))
        # The upstream text inside each SKILL.md must stay byte-identical to what was vendored.
        for name, path, _, body_hash in rows:
            if not path.endswith("/SKILL.md"):
                continue
            text = (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            body = text.split("overrides it where they conflict.\n\n", 1)[1].split("\n---\n\n## workflow-axa adaptation\n", 1)[0]
            self.assertEqual("`" + hashlib.sha256(body.encode("utf-8")).hexdigest()[:16] + "`", body_hash, name)

    def test_phase_skills_load_their_sibling_copies(self):
        uses = {"workflow-clarify": ["../grilling/SKILL.md"],
                "workflow-execute": ["../tdd/SKILL.md", "../code-review/SKILL.md"],
                "workflow-specify": ["../codebase-design/SKILL.md"]}
        for skill, paths in uses.items():
            text = (ROOT / f"skills/{skill}/SKILL.md").read_text(encoding="utf-8")
            for path in paths:
                self.assertIn(path, text, skill)
            self.assertNotRegex(text, r"installed `(grilling|tdd|code-review)`", skill)

    def test_session_digest_lists_human_messages_and_skills(self):
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            lines = [
                {"type": "user", "timestamp": "2026-11-02T10:00:00Z", "message": {"content": "/workflow add a filter"}},
                {"type": "assistant", "timestamp": "2026-11-02T10:01:00Z", "message": {"content": [
                    {"type": "tool_use", "name": "Skill", "input": {"skill": "workflow"}},
                    {"type": "tool_use", "name": "AskUserQuestion", "input": {"questions": [{"question": "Remember it?"}]}}]}},
                {"type": "user", "timestamp": "2026-11-02T10:02:00Z", "message": {"content": [
                    {"type": "tool_result", "is_error": True, "content": "Permission denied"}]}},
                {"type": "user", "timestamp": "2026-11-02T10:03:00Z", "message": {"content": "<task-notification>done</task-notification>"}},
                {"type": "user", "timestamp": "2026-11-02T10:04:00Z", "message": {"content": "is it done?"}},
            ]
            (logs / "s1.jsonl").write_text("\n".join(json.dumps(l) for l in lines) + "\nnot json\n", encoding="utf-8")
            out = Path(tmp) / "digest.md"
            subprocess.run([sys.executable, "-X", "utf8", "-I", str(ROOT / "skills/retro/scripts/digest_sessions.py"), str(logs), str(out)],
                           check=True, capture_output=True)
            text = out.read_text(encoding="utf-8")
        self.assertIn("human messages: 2", text)
        self.assertIn("is it done?", text)
        self.assertNotIn("task-notification", text)
        self.assertIn("skills: ['workflow']", text)
        self.assertIn("Q: Remember it?", text)
        self.assertIn("tool errors: 1 (denied 1); hook denials: 0", text)

    def test_session_digest_counts_hook_denials(self):
        # P1-P3 digest: seven phase-gate denials showed as "denied 0".
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            block = {"type": "tool_result", "is_error": True,
                     "content": "PreToolUse:Edit hook error: workflow-axa: editing src/a.py needs implementation approval"}
            (logs / "s1.jsonl").write_text(json.dumps({"type": "user", "message": {"content": [block]}}), encoding="utf-8")
            out = Path(tmp) / "digest.md"
            subprocess.run([sys.executable, "-X", "utf8", "-I", str(ROOT / "skills/retro/scripts/digest_sessions.py"), str(logs), str(out)],
                           check=True, capture_output=True)
            self.assertIn("tool errors: 1 (denied 0); hook denials: 1", out.read_text(encoding="utf-8"))

    def test_session_digest_accepts_stream_system_messages(self):
        # Native CLI stream-json has string messages for permission denials.
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            rows = [
                {"type": "system", "subtype": "permission_denied", "message": "Permission denied"},
                {"type": "system", "message": "status"},
                {"type": "user", "message": {"content": "Continue the approved task"}},
                None,
            ]
            (logs / "s1.jsonl").write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
            out = Path(tmp) / "digest.md"
            result = subprocess.run([sys.executable, "-X", "utf8", "-I",
                                     str(ROOT / "skills/retro/scripts/digest_sessions.py"), str(logs), str(out)],
                                    capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            text = out.read_text(encoding="utf-8")
            self.assertIn("human messages: 1", text)
            self.assertIn("Continue the approved task", text)
            self.assertIn("host permission denials: 1", text)
            self.assertIn("tool errors: 0", text)

    def test_session_digest_hides_secrets_and_counts_typed_commands(self):
        # Hooqd retro: a pasted server password reached the digest, and a typed /workflow showed as "skills: []".
        with tempfile.TemporaryDirectory() as tmp:
            logs = Path(tmp) / "logs"
            logs.mkdir()
            typed = ("<command-message>workflow</command-message>\n<command-name>/workflow</command-name>\n"
                     "<command-args>bug, ssh credentials sqoore EXAMPLEnotArealSecret9, token: abc123</command-args>")
            lines = [{"type": "user", "timestamp": "2026-11-03T14:11:00Z", "message": {"content": typed}},
                     {"type": "user", "timestamp": "2026-11-03T14:12:00Z", "message": {"content": "password=hunter2 please"}}]
            (logs / "s1.jsonl").write_text("\n".join(json.dumps(l) for l in lines), encoding="utf-8")
            out = Path(tmp) / "digest.md"
            subprocess.run([sys.executable, "-X", "utf8", "-I", str(ROOT / "skills/retro/scripts/digest_sessions.py"), str(logs), str(out)],
                           check=True, capture_output=True)
            text = out.read_text(encoding="utf-8")
        for secret in ("EXAMPLEnotArealSecret9", "abc123", "hunter2"):
            self.assertNotIn(secret, text)
        self.assertIn("<redacted>", text)
        self.assertIn("skills: ['/workflow']", text)


if __name__ == "__main__":
    unittest.main()
