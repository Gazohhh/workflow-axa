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
