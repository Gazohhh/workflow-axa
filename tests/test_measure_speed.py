import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "measure_speed.py"


def run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), *args],
                          capture_output=True, text=True, encoding="utf-8", cwd=ROOT)


class MeasureSpeed(unittest.TestCase):
    def test_json_has_the_three_measurements(self):
        result = run("--json", "--sizes", "50")
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(set(data), {"words", "hooks", "stops"})

    def test_bug_path_words_count_every_file_once(self):
        data = json.loads(run("--json", "--sizes", "50").stdout)
        bug = data["words"]["bug"]
        self.assertEqual(len(bug["files"]), len(set(bug["files"])))
        self.assertEqual(bug["total"], sum(bug["per_file"].values()))
        self.assertGreater(bug["total"], 0)

    def test_bug_before_code_is_the_bug_path_without_review_and_delivery(self):
        words = json.loads(run("--json", "--sizes", "50").stdout)["words"]
        for name in ("router", "bug", "lightweight", "bug_before_code"):
            self.assertIn(name, words)
        before, bug = words["bug_before_code"], words["bug"]
        for after in ("skills/code-review/SKILL.md", "skills/workflow-deliver/SKILL.md"):
            self.assertIn(after, bug["files"])
            self.assertNotIn(after, before["files"])
        self.assertIn("skills/workflow-execute/SKILL.md", before["files"])
        self.assertLessEqual(set(before["files"]), set(bug["files"]))
        self.assertEqual(before["total"], sum(before["per_file"].values()))
        self.assertLess(before["total"], bug["total"])

    def test_hook_timings_cover_each_call_kind_and_size(self):
        data = json.loads(run("--json", "--sizes", "50").stdout)
        for kind in ("bash_read_only", "read", "edit"):
            self.assertIn("50", data["hooks"][kind])
            self.assertGreaterEqual(data["hooks"][kind]["50"]["median_ms"], 0)

    def test_stops_lists_the_owner_questions_of_the_bug_path(self):
        data = json.loads(run("--json", "--sizes", "50").stdout)
        self.assertIn("one_ticket_bug", data["stops"])
        self.assertIsInstance(data["stops"]["one_ticket_bug"]["questions"], list)

    def test_unknown_option_fails(self):
        self.assertNotEqual(run("--nope").returncode, 0)


if __name__ == "__main__":
    unittest.main()
