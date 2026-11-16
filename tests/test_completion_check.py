"""skills/workflow-deliver/scripts/completion_check.py (T18 of docs/plans/2026-11-15-workflow-redesign), on real git
repositories in temporary folders."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("completion_check_under_test",
                                              ROOT / "skills/workflow-deliver/scripts/completion_check.py")
cc = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = cc
spec.loader.exec_module(cc)


class CompletionCheck(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.git("init", "-q")
        for rel in ("src/a.ts", "src/b.ts", "src/owner.ts"):
            self.write(rel, "one\n")
        self.task = self.root / "docs/plans/2026-11-16-t"
        self.task.mkdir(parents=True)
        self.commit("start")

    def git(self, *args):
        subprocess.run(["git", "-C", str(self.root), "-c", "user.name=t", "-c", "user.email=t@example.invalid", *args],
                       check=True, capture_output=True)

    def commit(self, message):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def write(self, rel, text):
        (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
        (self.root / rel).write_text(text, encoding="utf-8")

    def review(self, sid, kind="independent", result="passed"):
        with open(self.task / "FINDINGS.md", "a", encoding="utf-8") as f:
            f.write(f"- Review {sid}: reviewer-1 ({kind}) {result}: T1\n")

    def problems(self):
        return cc.check(self.root, self.task)[0]

    def test_a_reviewed_change_passes_and_a_later_edit_needs_review_again(self):
        cc.baseline(self.root, self.task)
        self.write("src/a.ts", "two\n")
        self.assertIn("never reviewed", self.problems()[0])
        sid = cc.snapshot(self.root, self.task, ["src/a.ts"])
        self.review(sid)
        self.assertEqual(self.problems(), [])
        self.write("src/a.ts", "three\n")  # changed after (or during) the review
        self.assertIn("changed after its last review snapshot", self.problems()[0])

    def test_the_owners_earlier_edits_are_left_out_unless_they_change_again(self):
        self.write("src/owner.ts", "owner edit\n")
        self.write("notes.txt", "owner's untracked file\n")
        cc.baseline(self.root, self.task)
        self.assertEqual(self.problems(), [])
        self.write("src/owner.ts", "owner edit, then the task\n")
        self.assertIn("src/owner.ts", self.problems()[0])

    def test_restoring_or_deleting_a_file_dirty_at_baseline_counts(self):
        self.write("src/owner.ts", "owner edit\n")
        self.write("notes.txt", "owner's untracked file\n")
        cc.baseline(self.root, self.task)
        self.git("checkout", "--", "src/owner.ts")  # restored to HEAD: not in git diff any more
        (self.root / "notes.txt").unlink()  # a pre-existing untracked file deleted
        found = " ".join(self.problems())
        self.assertIn("src/owner.ts", found)
        self.assertIn("notes.txt", found)

    def test_committed_task_work_still_counts(self):
        cc.baseline(self.root, self.task)
        self.write("src/a.ts", "two\n")
        self.commit("task work")
        self.assertIn("src/a.ts", self.problems()[0])

    def test_renames_and_deletions_need_the_reviewed_snapshot(self):
        cc.baseline(self.root, self.task)
        self.git("mv", "src/a.ts", "src/renamed.ts")
        (self.root / "src/b.ts").unlink()
        self.assertEqual({p.split(":")[0] for p in self.problems()}, {"src/a.ts", "src/renamed.ts", "src/b.ts"})
        self.review(cc.snapshot(self.root, self.task, ["src/a.ts", "src/renamed.ts", "src/b.ts"]))
        self.assertEqual(self.problems(), [])

    def test_failed_pending_and_superseded_results(self):
        cc.baseline(self.root, self.task)
        self.write("src/a.ts", "two\n")
        sid = cc.snapshot(self.root, self.task, ["src/a.ts"])
        for result in ("failed", "pending"):
            with self.subTest(result=result):
                (self.task / "FINDINGS.md").write_text("", encoding="utf-8")
                self.review(sid, result=result)
                self.assertIn(f"{sid}, {result}", self.problems()[0])
        (self.task / "FINDINGS.md").write_text("", encoding="utf-8")
        self.review(sid, result="passed")
        self.review(sid, result="failed")  # the latest line counts
        self.assertIn(f"{sid}, failed", self.problems()[0])
        self.review(sid, result="passed")
        self.assertEqual(self.problems(), [])

    def test_a_self_review_passes_but_is_named(self):
        cc.baseline(self.root, self.task)
        self.write("src/a.ts", "two\n")
        self.review(cc.snapshot(self.root, self.task, ["src/a.ts"]), kind="self")
        problems, notes = cc.check(self.root, self.task)
        self.assertEqual(problems, [])
        self.assertIn("self-reviewed only", notes[0])

    def test_the_evidence_is_never_rewritten(self):
        cc.baseline(self.root, self.task)
        with self.assertRaises(cc.Unknown):
            cc.baseline(self.root, self.task)  # never replaced
        self.write("src/a.ts", "two\n")
        first = cc.snapshot(self.root, self.task, ["src/a.ts"])
        self.write("src/a.ts", "three\n")
        second = cc.snapshot(self.root, self.task, ["src/a.ts"])
        data = cc.load(self.task)
        self.assertNotEqual(data["snapshots"][first], data["snapshots"][second])  # S1 kept as it was

    def test_a_newer_failed_review_of_the_same_bytes_wins_over_an_older_pass(self):
        cc.baseline(self.root, self.task)
        self.write("src/a.ts", "two\n")
        first = cc.snapshot(self.root, self.task, ["src/a.ts"])
        self.review(first)
        second = cc.snapshot(self.root, self.task, ["src/a.ts"])  # the same version, reviewed again
        self.assertIn(f"{second}, has no review line yet", self.problems()[0])
        self.review(second, result="failed")
        self.assertIn(f"{second}, failed", self.problems()[0])

    def test_concurrent_calls_never_share_an_id_or_two_baselines(self):
        import threading
        results, errors = [], []

        def call(fn):
            try:
                results.append(fn())
            except cc.Unknown as exc:
                errors.append(exc)
        threads = [threading.Thread(target=call, args=(lambda: cc.baseline(self.root, self.task),)) for _ in range(4)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual((len(results), len(errors)), (1, 3))  # exactly one baseline
        self.write("src/a.ts", "two\n")
        results.clear()
        threads = [threading.Thread(target=call, args=(lambda: cc.snapshot(self.root, self.task, ["src/a.ts"]),))
                   for _ in range(6)]
        [t.start() for t in threads]
        [t.join() for t in threads]
        self.assertEqual(sorted(results, key=lambda s: int(s[1:])), [f"S{n}" for n in range(1, 7)])
        self.assertEqual(len(cc.load(self.task)["snapshots"]), 6)

    def test_a_damaged_record_is_undecided_not_a_crash(self):
        cc.baseline(self.root, self.task)
        for bad in ("[]", '{"base": 1}', "not json"):
            with self.subTest(bad=bad):
                (self.task / "completion.json").write_text(bad, encoding="utf-8")
                self.assertEqual(cc.main(["check", str(self.root), str(self.task)]), 2)

    def test_no_baseline_or_no_git_is_undecided(self):
        with self.assertRaises(cc.Unknown):
            cc.check(self.root, self.task)
        self.assertEqual(cc.main(["check", str(self.root), str(self.task)]), 2)
        self.assertEqual(cc.main(["check", str(self.root.parent / "nowhere"), str(self.task)]), 2)

    def test_task_records_are_not_review_targets(self):
        cc.baseline(self.root, self.task)
        (self.task / "PLAN.md").write_text("x", encoding="utf-8")
        self.assertEqual(self.problems(), [])
        self.assertEqual(cc.main(["check", str(self.root), str(self.task)]), 0)


if __name__ == "__main__":
    unittest.main()
