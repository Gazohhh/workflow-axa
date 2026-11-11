"""simple-english: vendored with provenance and an adaptation; the report steps load it (owner request 2026-11-03)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/simple-english"
MARK = "\n---\n\n## workflow-axa adaptation\n"


class SimpleEnglishTests(unittest.TestCase):
    def test_registered_with_license_and_adaptation(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertIn("./skills/simple-english", plugin["skills"])
        self.assertIn("MIT License", (SKILL / "LICENSE").read_text(encoding="utf-8"))
        text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Bundled with workflow-axa from [AminBlg/SimpleEnglish]", text)
        self.assertIn("DESIGN.md rule 4's question, which is quoted word for word", text)

    def test_upstream_text_and_references_are_unchanged(self):
        readme = (ROOT / "VENDORED-SKILLS.md").read_text(encoding="utf-8")
        rows = re.findall(r"^\| `skills/simple-english/([^`]+)` \| `([0-9a-f]{16})` \| (`[0-9a-f]{16}`|—) \|$", readme, re.M)
        self.assertEqual(len(rows), 5)
        for path, file_hash, body_hash in rows:
            raw = (SKILL / path).read_bytes()
            if path == "SKILL.md":
                text = raw.decode("utf-8")
                body = text.split("unchanged; the **workflow-axa adaptation** at the end overrides it where they conflict.\n\n", 1)[1]
                body = body[:body.index(MARK)]
                self.assertEqual(hashlib.sha256(body.encode("utf-8")).hexdigest()[:16], body_hash.strip("`"))
            else:
                self.assertEqual(hashlib.sha256(raw).hexdigest()[:16], file_hash)

    def test_report_steps_load_it(self):
        for path in ("skills/codebase-map/TASK-REPORT.md", "skills/workflow/VISUAL-REVIEW.md", "skills/workflow-deliver/SKILL.md"):
            self.assertIn("simple-english", (ROOT / path).read_text(encoding="utf-8"), path)


if __name__ == "__main__":
    unittest.main()
