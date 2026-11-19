"""Speed of hooks/approval.py (T1 of docs/plans/2026-11-19-workflow-speed): the same allow/refuse decisions, with no
transcript parse for calls that write nothing and an incremental parse for the calls that do."""
from __future__ import annotations

import json
import os
import statistics
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from test_approval_hook import OFFER, ROOT, TASK, ApprovalHookCase, Rows, load_hook, offers

RECORD = ROOT / "skills/workflow/scripts/record.py"


class SpeedCase(ApprovalHookCase):

    def setUp(self):
        super().setUp()
        own = tempfile.TemporaryDirectory()
        self.addCleanup(own.cleanup)
        self.cache = own.name

    def approved(self, offer=None):
        rows = self.presented(offer=offer)
        rows.owner("yes")
        return rows

    def in_process(self):
        """The hook as a module, with the gate's caches, the settings file and the home folder of this test."""
        module = load_hook()
        g = module.gate()
        for patch in (mock.patch.object(g, "CACHE_DIR", Path(self.cache)),
                      mock.patch.dict(os.environ, {"WORKFLOW_AXA_SETTINGS": str(self.settings),
                                                   "WORKFLOW_AXA_HOME": str(self.base / "axa-home")})):
            patch.start()
            self.addCleanup(patch.stop)
        return module


class DecisionsStayTheSame(SpeedCase):
    """Characterisation: today's decisions for each kind of call, through the hook process."""

    def test_read_only_shell_commands_are_allowed_approved_or_not(self):
        for command in ("git status", "ls -la", "git log --oneline -3"):
            with self.subTest(command=command):
                self.allowed(Rows().router(), tool="Bash", data={"command": command})
                self.allowed(self.approved(), tool="Bash", data={"command": command})

    def test_a_shell_redirect_needs_the_file_in_an_approved_offer(self):
        self.allowed(self.approved(), tool="Bash", data={"command": f"echo x > {self.repo / 'src/vat.ts'}"})
        self.denied(self.approved(), "needs an approved offer that lists src/other.ts", tool="Bash",
                    data={"command": f"echo x > {self.repo / 'src/other.ts'}"})
        self.denied(Rows().router(), "needs an approved offer", tool="Bash",
                    data={"command": f"echo x > {self.repo / 'src/vat.ts'}"})

    def test_git_writes_need_the_operation(self):
        self.allowed(self.approved(), tool="Bash", data={"command": "git commit -m vat"})
        self.denied(self.approved(), 'no approved offer lists "git push"', tool="Bash", data={"command": "git push"})
        self.denied(Rows().router(), tool="Bash", data={"command": "git commit -m vat"})

    def test_edits_inside_and_outside_the_offer(self):
        self.allowed(self.approved())
        self.denied(self.approved(), "needs an approved offer that lists src/other.ts",
                    data={"file_path": str(self.repo / "src/other.ts"), "old_string": "a", "new_string": "b"})
        self.denied(Rows().router(), "needs an approved offer")

    def test_an_mcp_write_needs_the_tool_among_the_operations(self):
        self.denied(self.approved(), "has no approved offer that lists mcp__notion__create_page",
                    tool="mcp__notion__create_page", data={"title": "x"})
        offers.revise(self.folder, self.offer["id"], {**OFFER, "operations": ["git commit", "mcp__notion__create_page"]})
        self.allowed(self.approved(offer=offers.load(self.folder, 2)), tool="mcp__notion__create_page",
                     data={"title": "x"})

    def test_the_css_switch_needs_a_yes_to_its_question(self):
        run_on = {"command": "python settings.py css on"}
        rows = Rows().router()
        self.denied(rows, "protected operation", tool="Bash", data=run_on)
        rows.say("Turn CSS on for every project on this machine? Yes / No")
        rows.owner("yes")
        self.allowed(rows, tool="Bash", data=run_on)

    def test_installs_keep_their_safeguard(self):
        self.denied(self.approved(), "installs packages", tool="Bash", data={"command": "npm install left-pad"})

    def test_changing_the_worktrees_needs_its_own_operation(self):
        self.denied(self.approved(), 'no approved offer lists "git worktree"', tool="Bash",
                    data={"command": "git worktree add ../other"})

    def test_deriving_needs_an_approved_parent_though_it_writes_no_path(self):
        command = f'python -X utf8 -I "{RECORD}" offer derive "{self.folder}" {self.offer["id"]} child.json'
        self.denied(Rows().router(), "needs an approved parent", tool="Bash", data={"command": command})
        self.allowed(self.approved(), tool="Bash", data={"command": command})

    def test_a_stop_pauses_writes_but_not_reads(self):
        rows = self.approved()
        rows.owner("stop")
        self.denied(rows, "stopped the work")
        self.allowed(rows, tool="Bash", data={"command": "git status"})


class ReadOnlyCallsSkipTheTranscript(SpeedCase):

    def test_a_call_that_writes_nothing_never_reads_the_events(self):
        module = self.in_process()
        rows = self.approved()
        rows.owner("stop")
        with mock.patch.object(module, "read_events", side_effect=AssertionError("read_events called")):
            for command in ("git status", "ls -la", "git diff HEAD", "cat src/vat.ts"):
                with self.subTest(command=command):
                    self.assertIsNone(module.problem_for(self.event(rows, tool="Bash", data={"command": command})))
            self.assertIsNone(module.problem_for(self.event(rows, tool="Read",
                                                            data={"file_path": str(self.repo / "src/vat.ts")})))

    def test_calls_that_need_the_conversation_still_read_it(self):
        module = self.in_process()
        derive = f'python -X utf8 -I "{RECORD}" offer derive "{self.folder}" {self.offer["id"]} child.json'
        for data in ({"command": derive}, {"command": "python settings.py css on"},
                     {"command": "git worktree add ../other"}, {"command": "git commit -m x"}):
            with self.subTest(command=data["command"]), \
                    mock.patch.object(module, "read_events", wraps=module.read_events) as spy:
                module.problem_for(self.event(Rows().router(), tool="Bash", data=data))
                self.assertTrue(spy.called)


def conversation(rows: Rows, folder: Path, offer: dict, turns: int):
    """A varied conversation: typed turns, tool calls and their results, questions with answers, a queued message,
    an entry without a uuid, sidechain and broken lines, and an offer presented as text and by question."""
    for n in range(turns):
        rows.owner(f"please look at docs/plans/{TASK} step {n}")
        rows.say(f"Working on step {n}.")
        tool_id = f"t{n}"
        rows.append({"type": "assistant", "uuid": rows.uid(), "message": {"content": [
            {"type": "text", "text": "Reading."},
            {"type": "tool_use", "id": tool_id, "name": "Read", "input": {"file_path": "src/vat.ts"}}]}})
        rows.append({"type": "user", "uuid": rows.uid(), "toolUseResult": {"file": "x" * 200},
                     "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_id,
                                                              "content": "export const vat = 1;\n" * 20}]}})
        if n % 3 == 0:
            question = f"Which rounding for step {n}?"
            asked = rows.ask(question, ["Per line", "Per total"])
            rows.answer(asked, question, "Per line")
        if n % 4 == 0:
            rows.append({"type": "attachment", "uuid": rows.uid(), "attachment": {
                "type": "queued_command", "commandMode": "prompt", "origin": {"kind": "human"},
                "prompt": f"also step {n}"}})
            rows.append({"type": "assistant", "message": {"content": [{"type": "text", "text": "no uuid"}]}})
            rows.append({"type": "user", "isSidechain": True, "uuid": rows.uid(), "message": {"content": "agent"}})
    rows.say("Here is the offer:\n\n```\n" + offers.rendering(offer, folder) + "\n```\n\nApprove?")
    rows.owner("yes")
    question = offers.presentation(offer, folder, question=True)
    asked = rows.ask(question, ["Approve from this summary", "Change something"])
    rows.answer(asked, question, "Approve from this summary")


class IncrementalParse(SpeedCase):

    def write(self, rows: Rows, path: Path, tail: str = ""):
        lines = [json.dumps(r) for r in rows.rows]
        lines.insert(len(lines) // 2, "{broken json")
        path.write_text("\n".join(lines) + "\n" + tail, encoding="utf-8")

    def cold(self, module, path: Path):
        with tempfile.TemporaryDirectory() as fresh, mock.patch.object(module.gate(), "CACHE_DIR", Path(fresh)):
            return module.read_events(path, self.repo)

    def caches(self):
        return sorted((Path(self.cache) / "events").glob("*.json"))

    def test_cached_events_equal_a_cold_parse_after_appends(self):
        module = self.in_process()
        rows = Rows().router()
        conversation(rows, self.folder, self.offer, 6)
        self.write(rows, self.path, tail='{"type": "user", "uuid": "partial", "message": {"role": "user", "cont')
        first = module.read_events(self.path, self.repo)
        self.assertEqual(first, self.cold(module, self.path))
        self.assertEqual(len(self.caches()), 1)
        conversation(rows, self.folder, self.offer, 5)
        self.write(rows, self.path)
        self.assertEqual(module.read_events(self.path, self.repo), self.cold(module, self.path))
        rows.owner("revoke")
        self.write(rows, self.path, tail=json.dumps(rows.rows[-1]))
        again = module.read_events(self.path, self.repo)
        self.assertEqual(again, self.cold(module, self.path))
        self.assertIn("revoke", [e.text for e in again if e.kind == "user"][-1])

    def test_the_offer_files_are_judged_at_every_call(self):
        module = self.in_process()
        rows = Rows().router()
        conversation(rows, self.folder, self.offer, 2)
        self.write(rows, self.path)
        tasks = [e for e in module.read_events(self.path, self.repo) if e.kind in ("offer_shown", "offer_asked")]
        self.assertTrue(tasks)
        (self.folder / "offers" / f"offer-{self.offer['id']}.json").unlink()
        events = module.read_events(self.path, self.repo)
        self.assertFalse([e for e in events if e.kind in ("offer_shown", "offer_asked")])
        self.assertEqual(events, self.cold(module, self.path))

    def test_a_damaged_cache_is_ignored_and_rebuilt(self):
        module = self.in_process()
        rows = Rows().router()
        conversation(rows, self.folder, self.offer, 4)
        self.write(rows, self.path)
        expected = module.read_events(self.path, self.repo)
        cache = self.caches()[0]
        whole = cache.read_bytes()
        for damage in (whole[:len(whole) // 2], b"not json", b"[]", b'{"v": 1}', b"",
                       whole.replace(b'"offset": ', b'"offset": 1')):
            with self.subTest(damage=damage[:20]):
                cache.write_bytes(damage)
                self.assertEqual(module.read_events(self.path, self.repo), expected)
                self.assertEqual(json.loads(cache.read_text(encoding="utf-8"))["offset"],
                                 self.path.stat().st_size)

    def test_a_rewritten_transcript_invalidates_the_cache(self):
        module = self.in_process()
        long = Rows().router()
        conversation(long, self.folder, self.offer, 5)
        self.write(long, self.path)
        module.read_events(self.path, self.repo)
        short = Rows().router()
        short.owner("a different start")
        conversation(short, self.folder, self.offer, 1)
        self.write(short, self.path)
        self.assertEqual(module.read_events(self.path, self.repo), self.cold(module, self.path))
        same_length = self.path.read_bytes().replace(b"a different start", b"a DIFFERENT start")
        self.path.write_bytes(same_length)
        events = module.read_events(self.path, self.repo)
        self.assertIn("a DIFFERENT start", [e.text for e in events])
        self.assertEqual(events, self.cold(module, self.path))
        middle = self.path.read_bytes().replace(b"Working on step 0.", b"Working on step X.")
        self.path.write_bytes(middle)
        self.assertEqual(module.read_events(self.path, self.repo), self.cold(module, self.path))

    def test_an_unwritable_cache_only_costs_time(self):
        module = self.in_process()
        rows = Rows().router()
        conversation(rows, self.folder, self.offer, 2)
        self.write(rows, self.path)
        blocked = Path(self.cache) / "events"
        blocked.write_text("a file where the folder should be", encoding="utf-8")
        self.assertEqual(module.read_events(self.path, self.repo), self.cold(module, self.path))


FAST = (
    ("Bash", "git status", True),
    ("Bash", "git status --porcelain", True),
    ("Bash", "git log --oneline -3", True),
    ("Bash", "git diff HEAD", True),
    ("Bash", "git show HEAD:src/vat.ts", True),
    ("Bash", "git rev-parse --show-toplevel", True),
    ("Bash", "git ls-files src", True),
    ("Bash", "git branch --list", True),
    ("Bash", "ls -la src", True),
    ("Bash", "cat src/vat.ts", True),
    ("Bash", 'grep -rn "vat" src', True),
    ("Bash", "rg vat src", True),
    ("Bash", "head -5 src/vat.ts", True),
    ("Bash", "tail -n 5 src/vat.ts", True),
    ("Bash", "wc -l src/vat.ts", True),
    ("Bash", "find . -name '*.ts'", True),
    ("PowerShell", "Get-Content src/vat.ts", True),
    ("PowerShell", "Get-ChildItem -Recurse src", True),
    ("PowerShell", "Select-String -Path src/vat.ts -Pattern vat", True),
    ("Bash", "git status > x", False),
    ("Bash", "git status >> x", False),
    ("Bash", "cat a | tee b", False),
    ("Bash", "find . -delete", False),
    ("Bash", "find . -name x -exec rm {} +", False),
    ("Bash", "find . -fprint out.txt", False),
    ("Bash", "git -c core.worktree=.. status", False),
    ("Bash", "git -C .. status", False),
    ("Bash", "git --git-dir=x status", False),
    ("Bash", "GIT_DIR=x git status", False),
    ("Bash", "ls; rm x", False),
    ("Bash", "ls && rm x", False),
    ("Bash", "ls || rm x", False),
    ("Bash", "cat $(rm x)", False),
    ("Bash", "cat `rm x`", False),
    ("Bash", "ls\nrm x", False),
    ("Bash", "git diff --output=x", False),
    ("Bash", "git branch topic", False),
    ("Bash", "git branch -D topic", False),
    ("Bash", "git clean -fdx", False),
    ("Bash", "git commit -m x", False),
    ("Bash", "git worktree add ../other", False),
    ("Bash", "git worktree list", False),
    ("Bash", "rm x", False),
    ("Bash", "rg --pre ./script vat", False),
    ("Bash", "npm install left-pad", False),
    ("Bash", 'grep -n "npm install" README.md', False),
    ("Bash", "python settings.py css on", False),
    ("Bash", 'cat "settings.py css on"', False),
    ("Bash", "cat record.py", False),
    ("Bash", "cat legacy_inventory.py", False),
    ("Bash", "cat render_report.py", False),
    ("Bash", "python -X utf8 -I tools/validate.py", False),
    ("Bash", "/usr/bin/git status", False),
    ("Bash", "", False),
    ("PowerShell", "Get-Content x | Set-Content y", False),
    ("PowerShell", "Get-Content (Remove-Item x)", False),
    ("PowerShell", "Get-ChildItem; Remove-Item x", False),
    ("PowerShell", "& rm x", False),
    ("PowerShell", "Remove-Item x", False),
    ("Edit", "", False),
    ("Read", "", False),
)


class ReadOnlyFastPath(SpeedCase):
    """Item 4: a shell call that provably writes nothing is allowed before the gate loads; every other call takes the
    full path. The fast path never allows what the full path refuses."""

    def setUp(self):
        super().setUp()
        from test_approval_hook import git
        (self.repo / ".git").rmdir()
        git(self.repo, "init", "-q")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "base")
        git(self.repo, "worktree", "add", "-q", "--detach", str(self.base / "linked"))

    def data(self, tool, command):
        if tool in ("Bash", "PowerShell"):
            return {"command": command}
        return {"file_path": str(self.repo / "src/vat.ts"), "old_string": "1", "new_string": "2"}

    def test_the_fast_path_takes_only_the_read_only_commands(self):
        module = self.in_process()
        rows = Rows().router()
        for tool, command, fast in FAST:
            with self.subTest(tool=tool, command=command):
                event = self.event(rows, tool=tool, data=self.data(tool, command))
                self.assertEqual(module.fast_allow(json.dumps(event)), fast)

    def test_the_fast_path_and_the_full_path_decide_alike(self):
        module = self.in_process()
        for label, rows in (("not approved", Rows().router()), ("approved", self.approved()),
                            ("stopped", self.approved()), ("no workflow", Rows())):
            if label == "stopped":
                rows.owner("stop")
            for tool, command, fast in FAST:
                with self.subTest(rows=label, tool=tool, command=command):
                    event = self.event(rows, tool=tool, data=self.data(tool, command))
                    full = module.problem_for(event)
                    if module.fast_allow(json.dumps(event)):
                        self.assertIsNone(full)
                    hooked = self.finish(self.start(event))
                    self.assertEqual(hooked is None, full is None or full is module.LEGACY, (hooked, full))

    def test_the_writes_the_fast_path_leaves_out_are_still_refused(self):
        rows = Rows().router()
        for tool, command in (("Bash", "git status > src/x.ts"), ("Bash", "cat src/vat.ts | tee src/x.ts"),
                              ("Bash", "ls; rm src/vat.ts"), ("Bash", "git -c core.worktree=.. status"),
                              ("PowerShell", "Get-Content src/vat.ts | Set-Content src/x.ts")):
            with self.subTest(command=command):
                self.denied(rows, tool=tool, data={"command": command})

    def test_without_a_transcript_every_call_is_allowed_as_before(self):
        module = self.in_process()
        for tool, command, _ in FAST:
            with self.subTest(tool=tool, command=command):
                event = {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": self.data(tool, command),
                         "cwd": str(self.repo)}
                self.assertTrue(module.fast_allow(json.dumps(event)))
                self.assertIsNone(module.problem_for(event))
                self.assertIsNone(self.finish(self.start(event)))

    def test_an_unreadable_transcript_takes_the_full_path(self):
        module = self.in_process()
        event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git status"},
                 "cwd": str(self.repo), "transcript_path": str(self.sessions)}
        self.assertFalse(module.fast_allow(json.dumps(event)))
        missing = dict(event, transcript_path=str(self.sessions / "missing.jsonl"))
        self.assertTrue(module.fast_allow(json.dumps(missing)))
        self.assertIsNone(module.problem_for(missing))

    def test_input_that_is_no_hook_event_is_allowed_as_before(self):
        module = self.in_process()
        for raw in ("not json", "[]", json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Bash",
                                                  "transcript_path": str(self.path),
                                                  "tool_input": {"command": "rm x"}})):
            with self.subTest(raw=raw):
                self.assertTrue(module.fast_allow(raw))


class ReadOnlyTiming(SpeedCase):

    def transcript(self, events: int) -> Path:
        rows = Rows().router()
        while len(rows.rows) < events:
            conversation(rows, self.folder, self.offer, 50)
        path = self.sessions / f"s-{events}.jsonl"
        path.write_text("\n".join(json.dumps(r) for r in rows.rows[:events]) + "\n", encoding="utf-8")
        return path

    def median_ms(self, module, path: Path) -> float:
        event = {"hook_event_name": "PreToolUse", "tool_name": "Bash", "tool_input": {"command": "git status"},
                 "cwd": str(self.repo), "transcript_path": str(path)}
        self.assertIsNone(module.problem_for(event))
        runs = []
        for _ in range(9):
            start = time.perf_counter()
            module.problem_for(event)
            runs.append((time.perf_counter() - start) * 1000)
        return statistics.median(runs)

    def test_a_long_transcript_costs_a_read_only_call_little_more_than_a_short_one(self):
        module = self.in_process()
        small, large = self.transcript(1000), self.transcript(20000)
        short_ms, long_ms = self.median_ms(module, small), self.median_ms(module, large)
        self.assertLess(long_ms - short_ms, 50, f"1k events {short_ms:.1f} ms, 20k events {long_ms:.1f} ms")


if __name__ == "__main__":
    unittest.main()
