"""record.py safety (audit E20, ticket T2): interrupted writes, concurrent writers, exact ticks, encodings, batch."""
from __future__ import annotations

import contextlib
from concurrent.futures import ThreadPoolExecutor
import importlib.util
import io
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "skills/workflow/scripts/record.py"


def run(*args, stdin=None):
    return subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), *map(str, args)],
                          input=stdin, capture_output=True, text=True, encoding="utf-8")


def load_record_module():
    spec = importlib.util.spec_from_file_location("record_under_test", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_in_process(module, *args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = module.main(["record.py", *map(str, args)])
    return code, out.getvalue()


# A child process that dies hard (os._exit, no cleanup) at a chosen point of the write. Both the old in-place
# route (Path.write_bytes) and the temp-file route (os.write, os.replace) are covered, so the test does not
# depend on which one the script uses.
CRASH_CHILD = r'''
import importlib.util, os, pathlib, sys
spec = importlib.util.spec_from_file_location("rec", sys.argv[1])
rec = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rec)
point = sys.argv[2]
def in_place_crash(self, data):
    with open(self, "wb") as handle:
        if point == "mid-write":
            handle.write(bytes(data)[: len(data) // 2])
    os._exit(9)
pathlib.Path.write_bytes = in_place_crash
if point == "before-replace":
    os.replace = lambda *a, **k: os._exit(9)
else:
    real_write = os.write
    def half_then_die(fd, data):
        if b"## E2" not in bytes(data):  # let the lock file's own write through; die on the record text
            return real_write(fd, data)
        real_write(fd, bytes(data)[: max(1, len(data) // 2)])
        os._exit(9)
    os.write = half_then_die
sys.exit(rec.main(["record.py"] + sys.argv[3:]))
'''


class RecordSafetyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def write(self, name, data: bytes):
        path = self.dir / name
        path.write_bytes(data)
        return path

    def leftovers(self, name):
        return sorted(p.name for p in self.dir.iterdir() if p.name != name and name in p.name)

    # 1. Interruption-safe writes
    def crash(self, point, *args):
        return subprocess.run([sys.executable, "-X", "utf8", "-I", "-c", CRASH_CHILD, str(SCRIPT), point, *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8")

    def test_crash_before_replace_keeps_the_old_file_and_a_stale_lock_can_be_taken_over(self):
        original = b"# T\r\n- Next safe action: old\r\n- Other: x\r\n"
        plan = self.write("PLAN.md", original)
        result = self.crash("before-replace", "set-line", plan, "- Next safe action:", "- Next safe action: new")
        self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
        self.assertEqual(plan.read_bytes(), original)
        # The dead writer's lock is still there: a fresh lock blocks, an old one is taken over with a message.
        lock = self.dir / "PLAN.md.lock"
        self.assertTrue(lock.exists())
        blocked = run("set-line", plan, "- Next safe action:", "- Next safe action: new")
        self.assertNotEqual(blocked.returncode, 0)
        self.assertIn("BLOCKED", blocked.stdout)
        self.assertEqual(plan.read_bytes(), original)
        old = time.time() - 3600
        os.utime(lock, (old, old))
        taken = run("set-line", plan, "- Next safe action:", "- Next safe action: new")
        self.assertEqual(taken.returncode, 0, taken.stdout)
        self.assertIn("stale lock", taken.stdout)
        self.assertEqual(plan.read_bytes(), b"# T\r\n- Next safe action: new\r\n- Other: x\r\n")
        self.assertFalse(lock.exists())

    def test_crash_during_the_temp_write_keeps_the_old_file(self):
        original = b"# F\n\n## E1\nold\n"
        findings = self.write("FINDINGS.md", original)
        entry = self.write("entry.txt", ("## E2\n" + "new line\n" * 200).encode())
        result = self.crash("mid-write", "append", findings, entry)
        self.assertEqual(result.returncode, 9, result.stdout + result.stderr)
        # The crash hit the temp file's write: a half-written temp file is left beside the intact record.
        temps = list(self.dir.glob(".FINDINGS.md.*.tmp"))
        self.assertEqual(len(temps), 1, self.leftovers("FINDINGS.md"))
        self.assertTrue(0 < temps[0].stat().st_size < len(original) + len(entry.read_bytes()))
        self.assertEqual(findings.read_bytes(), original)

    @unittest.skipIf(os.name == "nt", "POSIX permission bits")
    def test_the_file_mode_is_kept(self):
        plan = self.write("PLAN.md", b"# T\n- A: 1\n")
        os.chmod(plan, 0o640)
        self.assertEqual(run("set-line", plan, "- A:", "- A: 2").returncode, 0)
        self.assertEqual(plan.stat().st_mode & 0o777, 0o640)

    # 2. No silent lost update
    def test_a_second_writer_is_blocked_while_the_first_holds_the_lock(self):
        todo = self.write("TODO.md", b"- [ ] T1 \xe2\x80\x94 a\n- [ ] T2 \xe2\x80\x94 b\n")
        rec = load_record_module()
        real_replace = os.replace
        second = {}

        def replace_after_a_rival(src, dst):
            if not second:
                second["result"] = run("tick", todo, "T2", "V2")
            return real_replace(src, dst)

        with mock.patch("os.replace", replace_after_a_rival), mock.patch("pathlib.Path.write_bytes",
                                                                          side_effect=AssertionError("in-place write")):
            code, out = run_in_process(rec, "tick", todo, "T1", "V1")
        self.assertEqual(code, 0, out)
        self.assertNotEqual(second["result"].returncode, 0)
        self.assertIn("BLOCKED", second["result"].stdout)
        self.assertEqual(todo.read_text(encoding="utf-8"), "- [x] T1 — a; verified: V1\n- [ ] T2 — b\n")
        self.assertEqual(self.leftovers("TODO.md"), [])  # lock and temp file are gone
        self.assertEqual(run("tick", todo, "T2", "V2").returncode, 0)  # the retry succeeds; nothing lost
        self.assertIn("- [x] T2 — b; verified: V2", todo.read_text(encoding="utf-8"))

    def test_a_change_after_the_read_is_refused_and_kept(self):
        plan = self.write("PLAN.md", b"# T\n- A: 1\n")
        rec = load_record_module()
        real_fsync = os.fsync

        def editor_saves_meanwhile(fd):
            real_fsync(fd)
            plan.write_bytes(b"# T\n- A: editor\n")

        with mock.patch("os.fsync", editor_saves_meanwhile):
            code, out = run_in_process(rec, "set-line", plan, "- A:", "- A: 2")
        self.assertNotEqual(code, 0)
        self.assertIn(f"BLOCKED: {plan} changed since it was read; reload and retry", out)
        self.assertEqual(plan.read_bytes(), b"# T\n- A: editor\n")
        self.assertEqual(self.leftovers("PLAN.md"), [])

    def test_a_writer_deletes_only_its_own_lock(self):
        plan = self.write("PLAN.md", b"# T\n- A: 1\n")
        lock = self.dir / "PLAN.md.lock"
        rec = load_record_module()
        real_replace = os.replace

        def lock_taken_over_meanwhile(src, dst):
            lock.write_bytes(b"rival-token\n")  # another writer took the lock over as stale
            return real_replace(src, dst)

        with mock.patch("os.replace", lock_taken_over_meanwhile):
            code, out = run_in_process(rec, "set-line", plan, "- A:", "- A: 2")
        self.assertEqual(code, 0, out)
        self.assertEqual(lock.read_bytes(), b"rival-token\n")  # the rival's lock survives

    def test_a_stale_lock_is_taken_over_by_rename_and_a_fresh_rival_lock_is_kept(self):
        plan = self.write("PLAN.md", b"# T\n- A: 1\n")
        lock = self.write("PLAN.md.lock", b"dead-writer\n")
        old = time.time() - 3600
        os.utime(lock, (old, old))
        rec = load_record_module()
        real_rename = os.rename

        def rival_got_there_first(src, dst):
            if Path(src) == lock:  # between our age check and our rename, a rival replaced the stale lock
                lock.write_bytes(b"rival-token\n")
            return real_rename(src, dst)

        with mock.patch("os.rename", rival_got_there_first):
            code, out = run_in_process(rec, "set-line", plan, "- A:", "- A: 2")
        self.assertNotEqual(code, 0, out)
        self.assertIn("BLOCKED", out)
        self.assertEqual(plan.read_bytes(), b"# T\n- A: 1\n")
        self.assertEqual(lock.read_bytes(), b"rival-token\n")
        self.assertEqual(self.leftovers("PLAN.md"), ["PLAN.md.lock"])
        # Without a rival the stale lock is renamed away, and nothing is left afterwards.
        lock.write_bytes(b"dead-writer\n")
        os.utime(lock, (old, old))
        code, out = run_in_process(rec, "set-line", plan, "- A:", "- A: 2")
        self.assertEqual(code, 0, out)
        self.assertIn("stale lock", out)
        self.assertEqual(self.leftovers("PLAN.md"), [])

    def test_a_symlinked_record_stays_a_link(self):
        target = self.write("real-PLAN.md", b"# T\n- A: 1\n")
        link = self.dir / "PLAN.md"
        try:
            link.symlink_to(target)
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlinks unavailable: {exc}")
        self.assertEqual(run("set-line", link, "- A:", "- A: 2").returncode, 0)
        self.assertTrue(link.is_symlink())
        self.assertEqual(target.read_bytes(), b"# T\n- A: 2\n")

    def test_parallel_appends_lose_nothing(self):
        findings = self.write("FINDINGS.md", b"# F\n")
        procs = []
        try:
            for _ in range(8):
                procs.append(subprocess.Popen(
                    [sys.executable, "-X", "utf8", "-I", str(SCRIPT), "append", str(findings), "-"],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE))
            # A worker can refuse the lock before reading stdin. communicate handles
            # that closed pipe while retaining the actual exit status and diagnostics.
            with ThreadPoolExecutor(max_workers=8) as workers:
                pending = [workers.submit(proc.communicate, f"entry-{number}\n".encode(), timeout=60)
                           for number, proc in enumerate(procs)]
                results = [future.result() for future in pending]
            codes = [proc.returncode for proc in procs]
            for code, (stdout, stderr) in zip(codes, results):
                self.assertIn(code, (0, 1), (stdout, stderr))
                self.assertEqual(stderr, b'')
                if code == 1:
                    self.assertIn(b'BLOCKED:', stdout)
                    self.assertIn(b'is being changed by another writer', stdout)
        finally:
            for proc in procs:
                if proc.poll() is None:
                    proc.kill()
                proc.communicate(timeout=10)
        text = findings.read_text(encoding="utf-8")
        written = {n for n in range(8) if f"entry-{n}" in text}
        self.assertEqual(written, {n for n, code in enumerate(codes) if code == 0})
        self.assertTrue(written)
        self.assertEqual(self.leftovers("FINDINGS.md"), [])

    # 3. new creates exclusively
    def test_new_refuses_a_file_that_appears_during_the_call(self):
        target = self.dir / "PLAN.md"
        rec = load_record_module()
        real_read_text = rec.read_text

        def rival_creates_it(source):
            target.write_bytes(b"rival\n")
            return real_read_text(source)

        source = self.write("in.txt", b"# Plan\n")
        with mock.patch.object(rec, "read_text", rival_creates_it):
            code, out = run_in_process(rec, "new", target, source)
        self.assertNotEqual(code, 0)
        self.assertIn("BLOCKED", out)
        self.assertEqual(target.read_bytes(), b"rival\n")

    # 4. tick: exact ID, never a cancelled line
    def test_tick_matches_the_exact_ticket_id(self):
        todo = self.write("TODO.md", "- [ ] T1.2 — sub\n- [ ] T1 — main\n".encode())
        self.assertEqual(run("tick", todo, "T1", "V1").returncode, 0)
        self.assertEqual(todo.read_text(encoding="utf-8"), "- [ ] T1.2 — sub\n- [x] T1 — main; verified: V1\n")
        only_sub = self.write("TODO2.md", "- [ ] T1.2 — sub\n".encode())
        self.assertEqual(run("tick", only_sub, "T1", "V1").returncode, 1)
        self.assertEqual(only_sub.read_text(encoding="utf-8"), "- [ ] T1.2 — sub\n")

    def test_tick_refuses_a_cancelled_ticket(self):
        original = "- [-] T3 — dropped by the owner\n".encode()
        todo = self.write("TODO.md", original)
        result = run("tick", todo, "T3", "V3")
        self.assertEqual(result.returncode, 1)
        self.assertIn("cancelled", result.stdout)
        self.assertEqual(todo.read_bytes(), original)

    # 5. Line endings, BOM, non-UTF-8
    def test_a_bom_file_keeps_its_bom_and_its_first_heading_is_found(self):
        plan = self.write("PLAN.md", b"\xef\xbb\xbf## Agreement\r\nold\r\n\r\n## Approval\r\nkeep\r\n")
        result = run("replace-section", plan, "## Agreement", "-", stdin="new\n")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(plan.read_bytes(), b"\xef\xbb\xbf## Agreement\r\n\r\nnew\r\n\r\n## Approval\r\nkeep\r\n")

    def test_lf_files_stay_lf(self):
        plan = self.write("PLAN.md", b"# T\n- A: 1\n")
        self.assertEqual(run("set-line", plan, "- A:", "- A: 2").returncode, 0)
        self.assertEqual(plan.read_bytes(), b"# T\n- A: 2\n")

    def test_mixed_line_endings_keep_each_line_ending(self):
        plan = self.write("PLAN.md", b"# T\r\n- A: 1\n- B: 1\r\n- C: 1\n")
        self.assertEqual(run("set-line", plan, "- B:", "- B: 2").returncode, 0)
        self.assertEqual(plan.read_bytes(), b"# T\r\n- A: 1\n- B: 2\r\n- C: 1\n")
        self.assertEqual(run("set-line", plan, "- A:", "- A: 2").returncode, 0)
        self.assertEqual(plan.read_bytes(), b"# T\r\n- A: 2\n- B: 2\r\n- C: 1\n")

    def test_a_non_utf8_file_blocks_without_a_traceback(self):
        original = "# Caf\xe9\n- A: 1\n".encode("cp1252")
        plan = self.write("PLAN.md", original)
        result = run("set-line", plan, "- A:", "- A: 2")
        self.assertEqual(result.returncode, 2)
        self.assertIn("BLOCKED", result.stdout)
        self.assertIn("UTF-8", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(plan.read_bytes(), original)
        self.assertEqual(self.leftovers("PLAN.md"), [])

    # 6. batch: every edit is checked against the original text
    def test_batch_refuses_chained_and_overlapping_matches(self):
        original = b"# T\n- A: alpha\n- B: other\n"
        plan = self.write("PLAN.md", original)
        for edits in ('[{"find": "alpha", "replace": "beta"}, {"find": "beta", "replace": "gamma"}]',
                      '[{"find": "- A: alpha", "replace": "x"}, {"find": "alpha\\n- B", "replace": "y"}]'):
            with self.subTest(edits=edits):
                result = run("batch", plan, "-", stdin=edits)
                self.assertEqual(result.returncode, 1, result.stdout)
                self.assertEqual(plan.read_bytes(), original)
        # Independent edits still apply, even when a replacement repeats another edit's find text.
        result = run("batch", plan, "-", stdin='[{"find": "alpha", "replace": "other"}, {"find": "- B: other", "replace": "- B: done"}]')
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(plan.read_bytes(), b"# T\n- A: other\n- B: done\n")


if __name__ == "__main__":
    unittest.main()
