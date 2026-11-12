"""Known gate failures and the protections around them (ticket H1 of 2026-11-11-consistency-review-findings).

Each test runs the real hook scripts as processes on a synthetic transcript, as test_phase_gate_hook.py does. No
private session content is copied: every transcript here is a minimal reproduction built from the shape of the
evidence named in the docstring.

Tests marked @unittest.expectedFailure reproduce a defect that exists today. The ticket named in the docstring
removes the decorator when it fixes the defect. Every other test passes today and must keep passing.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_phase_gate_hook import APPROVED, ROUTER, hook_context, hooked, say, sha, skill, tool, user

ROOT = Path(__file__).resolve().parents[1]
GATE = ROOT / "hooks/phase_gate.py"
REPLY = ROOT / "hooks/plain_reply.py"
CACHE = tempfile.TemporaryDirectory()  # the gate's transcript cache, kept out of the system temp folder
RECORD = 'R="python -X utf8 -I skills/workflow/scripts/record.py"'


def tearDownModule():
    CACHE.cleanup()


def run_gate(event) -> dict | None:
    result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(GATE), "--hook-protocol=1"], input=json.dumps(event),
                            capture_output=True, text=True, encoding="utf-8",
                            env={**os.environ, "WORKFLOW_AXA_GATE_CACHE": CACHE.name})
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["hookSpecificOutput"] if result.stdout.strip() else None


def run_reply(event) -> tuple[int, str]:
    result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(REPLY)], input=json.dumps(event),
                            capture_output=True, text=True, encoding="utf-8",
                            env={**os.environ, "WORKFLOW_AXA_GATE_CACHE": CACHE.name})
    return result.returncode, result.stdout.strip()


def write_rows(path: Path, rows):
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")


class GateCase(unittest.TestCase):
    """A temporary repository with task folders and a sessions folder, like ApprovalGateTests."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.repo = self.base / "repo"
        (self.repo / ".git").mkdir(parents=True)
        self.sessions = self.base / "sessions"
        self.sessions.mkdir()
        self.path = self.sessions / "current.jsonl"

    def task(self, name, *lines, write_paths=None, report="plan-r1.html"):
        """A task folder with a checkpoint and, unless report is None, its HTML plan report. write_paths puts a
        report manifest in the report, as render_report.py does."""
        folder = self.repo / "docs" / "plans" / name
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "PLAN.md").write_text("# Task\n\n## Current checkpoint\n- Status: x\n" + "\n".join(lines)
                                        + "\n\n## Goal\nx\n", encoding="utf-8")
        if report:
            (folder / "reviews").mkdir(exist_ok=True)
            manifest = "" if write_paths is None else (
                '<script type="application/json" id="report-manifest">'
                + json.dumps({"schema_version": 1, "sources": [], "write_paths": write_paths}) + "</script>")
            (folder / "reviews" / report).write_text("<!DOCTYPE html>" + manifest, encoding="utf-8")
        return folder

    def records(self, name):
        return tool("Write", file_path=str(self.repo / "docs/plans" / name / "TODO.md"), content="x")

    def present(self, name, report="plan-r1.html"):
        return say(f"Plan report: {self.repo / 'docs/plans' / name / 'reviews' / report}. Approve?")

    def approval(self, name, words="Yes to both"):
        return [self.records(name), self.present(name), user(words)]

    def fire(self, rows, tool_name, data, hooks=True):
        write_rows(self.path, hooked(rows, self.repo) if hooks else rows)
        return run_gate({"tool_name": tool_name, "tool_input": data, "transcript_path": str(self.path),
                         "cwd": str(self.repo)})

    def decision(self, *args, **kwargs):
        out = self.fire(*args, **kwargs)
        return out and out["permissionDecision"]

    def code(self, rel="src/a.ts"):
        return {"file_path": str(self.repo / rel)}


# H2: a phase starts only through a real phase start


class PhaseEntryRegressions(GateCase):

    def test_a_whole_read_of_a_phase_skill_outside_a_workflow_session_demands_no_reads(self):
        """H2. Evidence: FINDINGS Part 5 ("Hooks firing outside their phase"): plain_reply.py:209-210 and :227-231
        count a whole Read of any <phase>/SKILL.md as loading that phase. Here nobody started a workflow: the user
        asked a question and the agent read the specify skill to answer it. Today the Stop hook demands
        workflow-specify's required reads. Its session check (item b) also fires here, because the path contains
        "workflow-axa"; both belong to H2. Expected after H2: no demand."""
        rows = [user("explain how the specify phase decides on tickets"),
                tool("Read", file_path="D:\\workflow-axa\\skills\\workflow-specify\\SKILL.md"),
                say("It writes one ticket per independent change.")]
        write_rows(self.path, rows)
        self.assertEqual(run_reply({"transcript_path": str(self.path), "cwd": str(self.repo)}), (0, ""))

    def test_a_whole_read_of_a_phase_skill_still_activates_the_write_gate(self):
        """Protection, kept by H2 (passes, must keep passing). A whole Read of a phase SKILL.md turns the write gate
        on (phase_gate.py feed, the router's fallback), so an Edit without an approved task is refused, even when the
        read came from a question. H2 first proposed dropping this; the owner's agreement says "Preserve ALL existing
        approval gates, safety hooks, and blocking protections", so H2 narrows only the Stop hook (plain_reply.py)."""
        rows = [user("explain how the specify phase decides on tickets"),
                tool("Read", file_path="D:\\workflow-axa\\skills\\workflow-specify\\SKILL.md"),
                say("It writes one ticket per independent change."), user("thanks, now fix the typo in a.ts")]
        out = self.fire(rows, "Edit", self.code(), hooks=False)
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn("has not written or named a task folder", out["permissionDecisionReason"])

    def test_a_path_containing_workflow_axa_does_not_make_a_workflow_session(self):
        """H2. Evidence: FINDINGS Part 5: plain_reply.py:34-38 treats a session as a workflow session when any tool
        input contains the string "workflow-axa", which is every path in this repository. A plain edit in the
        workflow-axa checkout that ends with "Done" then gets the workflow "no review" demand. Today: blocked with
        that reason. Expected after H2: silent, like the same session in another folder (next test)."""
        rows = [user("fix the typo in the gate comment"),
                tool("Edit", file_path="D:/workflow-axa/hooks/phase_gate.py", old_string="teh", new_string="the"),
                say("Fixed the typo.\n\n**Done.**")]
        write_rows(self.path, rows)
        self.assertEqual(run_reply({"transcript_path": str(self.path), "cwd": "D:\\workflow-axa"}), (0, ""))

    def test_a_broken_plain_reply_copy_adds_no_blocking_and_keeps_the_write_gate(self):
        """H2 review: the gate's read checks go through plain_reply.scan_reads. With a broken plain_reply.py in the
        plugin root they are skipped, as before H2 (the error then reached main() and allowed non-edit tools), but
        the write gate still judges edits. Control: a working copy holds the render back for the report guides."""
        root = self.base / "plugin"
        (root / "hooks").mkdir(parents=True)
        for name in ("phase_gate.py", "phase_reads.py", "plain_reply.py"):
            (root / "hooks" / name).write_bytes((ROOT / "hooks" / name).read_bytes())
        (self.repo / "AGENTS.md").write_text('<!-- workflow-axa:required-read phases=specify path="tests/README.md" -->\n',
                                             encoding="utf-8")
        (self.repo / "tests").mkdir()
        (self.repo / "tests/README.md").write_text("x", encoding="utf-8")
        write_rows(self.path, [ROUTER, skill("workflow-axa:workflow-specify")])
        render = {"command": "python render_report.py --input p.json --output docs/plans/t/reviews/p.html"}

        def gate(tool_name, data):
            result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(root / "hooks/phase_gate.py"),
                                     "--hook-protocol=1"], capture_output=True, text=True, encoding="utf-8",
                                    input=json.dumps({"tool_name": tool_name, "tool_input": data, "cwd": str(self.repo),
                                                      "transcript_path": str(self.path)}),
                                    env={**os.environ, "WORKFLOW_AXA_GATE_CACHE": CACHE.name,
                                         "CLAUDE_PLUGIN_ROOT": str(root)})
            self.assertEqual((result.returncode, result.stderr), (0, ""))
            out = json.loads(result.stdout)["hookSpecificOutput"] if result.stdout.strip() else None
            return out and out["permissionDecision"] + ": " + out["permissionDecisionReason"]

        self.assertIn("deny: workflow-axa: read these whole before rendering", gate("Bash", render))
        self.assertIn("Not yet read: tests/README.md", gate("Skill", {"skill": "workflow-axa:workflow-specify"}))
        (root / "hooks/plain_reply.py").write_text("def broken(:\n", encoding="utf-8")
        self.assertIsNone(gate("Bash", render))
        self.assertIsNone(gate("Skill", {"skill": "workflow-axa:workflow-specify"}))
        self.assertTrue(gate("Edit", self.code()).startswith("deny: "))

    def test_the_same_plain_session_in_another_folder_is_silent(self):
        """Control for the test above (passes today, must keep passing): only the folder name differs."""
        rows = [user("fix the typo in the gate comment"),
                tool("Edit", file_path="D:/other-project/hooks/gate.py", old_string="teh", new_string="the"),
                say("Fixed the typo.\n\n**Done.**")]
        write_rows(self.path, rows)
        self.assertEqual(run_reply({"transcript_path": str(self.path), "cwd": "D:\\other-project"}), (0, ""))

    def test_a_started_workflow_still_demands_the_phase_reads(self):
        """Control (passes today, must keep passing): after a real phase start (a Skill call), the Stop hook still
        names the unread required file. H2 narrows the trigger, it does not remove the check."""
        rows = [user("/workflow-axa:workflow add a badge"), skill("workflow-axa:workflow-clarify"),
                say("Questions are ready.")]
        write_rows(self.path, rows)
        code, out = run_reply({"transcript_path": str(self.path), "cwd": str(self.repo)})
        self.assertEqual(code, 0)
        self.assertIn("workflow-clarify: grilling/SKILL.md", json.loads(out)["reason"])


# H3: another task's record write and an approved edit


A, B = "2026-11-03-fix", "2026-11-04-other"


class TaskSwitchRegressions(GateCase):
    """Task A is approved with write_paths that cover src/a.ts. The session then writes a record of task B, with
    no user message after it, and edits src/a.ts. Today every such edit stops with "the current task changed"."""

    def rows(self):
        # B is approved in the same session first, so B's own approval is real; then A; then a note to B.
        return [ROUTER] + self.approval(B) + self.approval(A) + [self.records(B)]

    def test_a_record_of_another_approved_task_does_not_stop_an_edit_task_a_covers(self):
        """H3. Evidence: FINDINGS Q17 ("task records of a second task no longer stop edits of the first") and the
        H3 ticket. B has approved write_paths of its own (src/b.ts) and src/a.ts is outside them, so the edit can
        only belong to A. Today: deny ("changed to 2026-11-04-other"). Expected after H3: allowed."""
        self.task(A, APPROVED, write_paths=["src/a.ts"])
        self.task(B, APPROVED, write_paths=["src/b.ts"])
        self.assertIsNone(self.fire(self.rows(), "Edit", self.code()))

    def test_a_file_outside_both_tasks_is_still_refused(self):
        """H3 never widens an approval: src/c.ts is in neither task's write_paths, so the edit stays refused."""
        self.task(A, APPROVED, write_paths=["src/a.ts"])
        self.task(B, APPROVED, write_paths=["src/b.ts"])
        self.assertEqual(self.decision(self.rows(), "Edit", self.code("src/c.ts")), "deny")
        # A shell write task A covers passes the same way; a git write (no file list of its own) keeps the stop.
        self.assertIsNone(self.decision(self.rows(), "Bash", {"command": "sed -i s/a/b/ src/a.ts"}))
        out = self.fire(self.rows(), "Bash", {"command": "git commit -m x"})
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn(f"changed to {B}", out["permissionDecisionReason"])

    def assert_switch_stop(self):
        out = self.fire(self.rows(), "Edit", self.code())
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn(f"changed to {B}", out["permissionDecisionReason"])

    def test_the_stop_remains_when_task_b_has_no_write_paths(self):
        """H3 must keep this stop (passes today): B's report has no write_paths, so the edit may belong to B."""
        self.task(A, APPROVED, write_paths=["src/a.ts"])
        self.task(B, APPROVED)
        self.assert_switch_stop()

    def test_the_stop_remains_when_task_b_is_not_approved(self):
        """H3 must keep this stop (passes today): B has no approval yet, so it has no approved write_paths."""
        self.task(A, APPROVED, write_paths=["src/a.ts"])
        self.task(B, "- Approval: not approved; revision r1 proposed", write_paths=["src/b.ts"])
        self.assert_switch_stop()

    def test_the_stop_remains_when_task_a_has_no_write_paths(self):
        """H3 must keep this stop (passes today): A's report has no write_paths, so nothing says A owns the file."""
        self.task(A, APPROVED)
        self.task(B, APPROVED, write_paths=["src/b.ts"])
        self.assert_switch_stop()

    def test_the_stop_remains_when_task_a_is_approved_for_another_revision(self):
        """H3 must keep this stop (passes today): A's approval covers r1, but its checkpoint now names r2."""
        self.task(A, APPROVED, "- Revision: r2 adds an export button", write_paths=["src/a.ts"])
        self.task(B, APPROVED, write_paths=["src/b.ts"])
        self.assert_switch_stop()

    def test_the_stop_remains_when_the_file_is_in_both_tasks(self):
        """H3 must keep this stop (passes today): both tasks may change src/a.ts, so the gate cannot tell which."""
        self.task(A, APPROVED, write_paths=["src/a.ts"])
        self.task(B, APPROVED, write_paths=["src/a.ts", "src/b.ts"])
        self.assert_switch_stop()


# H3: the `git apply` that passed on 2026-11-11


GUARD, REWORK = "2026-11-11-guard", "2026-11-11-rework"
PATCH = 'git apply --whitespace=nowarn "C:/x/report-rework.patch" && echo APPLIED'


def variable_record(task, note="- asked the owner"):
    """The record helper run through a variable holding the whole interpreter command, as on 2026-11-11."""
    return f"{RECORD} && $R append docs/plans/{task}/PLAN.md - <<'EOF'\n{note}\nEOF\n"


class ChainedCommandRegressions(GateCase):
    """Evidence (main session, 2026-11-11): `git apply` alone was refused because the current task (report-rework)
    had no plan report. Then `R="python ... record.py" && $R append docs/plans/<report-rework>/PLAN.md - <<'EOF' ...
    EOF` followed by `git apply ... && echo APPLIED` on the next line printed APPLIED. Replaying the shape shows the
    chain is not the cause: the gate never sees a record write made through `$R` (shell_writes only follows
    record.py named as an interpreter argument), so its current task stayed the last task it saw written, the
    approved duplicate-skill-guard task, and git writes are not bounded by that task's write_paths."""

    def setUp(self):
        super().setUp()
        self.task(GUARD, APPROVED, write_paths=["hooks/x.py"])
        self.task(REWORK, "- Blockers: asked the owner", report=None)

    def real_rows(self):
        return [ROUTER] + self.approval(GUARD) + [tool("Bash", command=variable_record(REWORK)),
                                                  user("the answer on the patch yes")]

    def test_the_2026_11_11_chained_git_apply_is_refused(self):
        """H3 ("The `git apply` case from H1 is refused without approval"). Today: allowed. Expected after H3:
        refused, because the work belongs to report-rework, which has no approval."""
        out = self.fire(self.real_rows(), "Bash", {"command": variable_record(REWORK, "- applying") + PATCH})
        self.assertEqual(out and out["permissionDecision"], "deny")

    def test_the_same_git_apply_alone_is_refused(self):
        """H3. The same state with `git apply` alone: today also allowed, which shows that judging the chained
        project write "as if it ran alone" (the H3 wording) does not close this case by itself. A fix needs the
        `$R` record write to move the current task, or git writes to be bounded, or both. The second changes what
        an approval allows, which H3 sends to the owner."""
        out = self.fire(self.real_rows(), "Bash", {"command": "git apply x.patch"})
        self.assertEqual(out and out["permissionDecision"], "deny")

    def test_a_command_that_writes_another_tasks_record_and_applies_a_patch_is_refused(self):
        """H3. A literal record.py write of report-rework chained with `git apply`, while the approved guard task is
        current. The record write is visible, but a command's own writes do not change the task its other writes
        are judged against. Before H3: allowed. Since H3 the patch is read, and src/a.ts is outside the guard task's
        write_paths (hooks/x.py), so the command is refused for that path."""
        (self.repo / "x.patch").write_text(patch(("hooks/x.py", "hooks/x.py"), ("src/a.ts", "src/a.ts")),
                                           encoding="utf-8")
        out = self.fire([ROUTER] + self.approval(GUARD), "Bash", {"command": self.record_and_apply()})
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn("`git apply` writing src/a.ts is outside the files the approved plan may change",
                      out["permissionDecisionReason"])

    def test_the_same_command_with_a_patch_the_approved_task_covers_is_allowed(self):
        """Companion: the same command with a readable patch that touches only hooks/x.py is judged against the
        approved guard task (the command's own record write does not change that) and allowed."""
        (self.repo / "x.patch").write_text(patch(("hooks/x.py", "hooks/x.py")), encoding="utf-8")
        self.assertIsNone(self.fire([ROUTER] + self.approval(GUARD), "Bash", {"command": self.record_and_apply()}))

    def record_and_apply(self):
        return (f"python -X utf8 -I skills/workflow/scripts/record.py append docs/plans/{REWORK}/PLAN.md - "
                "&& git apply x.patch")

    def test_an_edit_outside_the_approved_write_paths_is_refused_in_the_same_state(self):
        """Must keep passing. Before H3 the `$R` write was invisible, so the guard task stayed current and this Edit
        was refused by its write_paths. Since H3 the `$R` write makes report-rework current, and the Edit is refused
        because report-rework has no approval. Refused either way."""
        out = self.fire(self.real_rows(), "Edit", self.code())
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn(f"current task {REWORK}", out["permissionDecisionReason"])

    def test_chained_record_writes_never_carry_a_git_write_without_any_approval(self):
        """Passes today, must keep passing: with no approved task at all, every chained form is refused."""
        rows = [ROUTER, self.records(REWORK), user("the answer on the patch yes")]
        literal = f"python -X utf8 -I skills/workflow/scripts/record.py append docs/plans/{REWORK}/PLAN.md -"
        for command in (variable_record(REWORK) + PATCH, f"{literal} && git apply x.patch",
                        f"{literal} <<'EOF' && git apply x.patch\nnote\nEOF",
                        f"{literal} <<'EOF'\nnote\nEOF\ngit apply x.patch", "git apply x.patch"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(rows, "Bash", {"command": command}), "deny")


def patch(*files):
    """A unified diff: each item is (old, new) with None for /dev/null, or a (from, to, 'rename') triple."""
    out = []
    for item in files:
        if len(item) == 3:
            old, new, _ = item
            out += [f"diff --git a/{old} b/{new}", "similarity index 90%", f"rename from {old}", f"rename to {new}"]
            continue
        old, new = item
        name = new or old
        out.append(f"diff --git a/{name} b/{name}")
        if old is None:
            out.append("new file mode 100644")
        if new is None:
            out.append("deleted file mode 100644")
        out += [f"--- {'a/' + old if old else '/dev/null'}", f"+++ {'b/' + new if new else '/dev/null'}",
                "@@ -1 +1 @@", "-x", "+y"]
    return "\n".join(out) + "\n"


class GitFileWrites(GateCase):
    """H3 (D36): git commands that write files are checked against the current task's approved write_paths like an
    Edit. Git commands that write no files stay as they are."""

    def setUp(self):
        super().setUp()
        self.task(A, APPROVED, write_paths=["src/a.ts", "src/new/"])
        self.approved = [ROUTER] + self.approval(A)

    def write_patch(self, name, *files):
        (self.repo / name).write_text(patch(*files), encoding="utf-8")

    def assert_outside(self, command, rows=None):
        out = self.fire(rows or self.approved, "Bash", {"command": command})
        self.assertEqual(out and out["permissionDecision"], "deny", command)
        self.assertIn("is outside the files the approved plan may change", out["permissionDecisionReason"])

    def test_git_read_commands_and_patch_reports_keep_todays_behavior(self):
        """git status/diff/log write nothing and stay allowed. `git apply --check/--stat/--numstat/--summary` write
        nothing either, but the gate has always counted every `git apply` as a git write, so without approval they stay
        refused: the owner's agreement says "Preserve ALL existing approval gates, safety hooks, and blocking
        protections". With a valid approval they stay approval-only (no per-file check), as before H3."""
        self.write_patch("x.patch", ("src/b.ts", "src/b.ts"))
        reports = ("git apply --check x.patch", "git apply --stat x.patch", "git apply --numstat x.patch",
                   "git apply --summary x.patch", "git apply --check --stat x.patch")
        for command in reports:
            with self.subTest(approved=True, command=command):
                self.assertIsNone(self.fire(self.approved, "Bash", {"command": command}))
        unapproved = [ROUTER, self.records(A)]
        self.task(A, "- Approval: not approved; revision r1 proposed", write_paths=["src/a.ts"])
        for command in ("git status", "git diff", "git log --oneline -5"):
            with self.subTest(command=command):
                self.assertIsNone(self.fire(unapproved, "Bash", {"command": command}))
        for command in reports + ("git apply x.patch", "git apply --check --apply x.patch",
                                  "git apply --stat --apply x.patch"):
            with self.subTest(approved=False, command=command):
                self.assertEqual(self.decision(unapproved, "Bash", {"command": command}), "deny")

    def test_git_apply_inside_the_write_paths_with_a_valid_approval_is_allowed(self):
        self.write_patch("ok.patch", ("src/a.ts", "src/a.ts"), (None, "src/new/x.ts"))
        for command in ("git apply ok.patch", "git apply --whitespace=nowarn ok.patch", "git apply --3way ok.patch",
                        f'git apply "{(self.repo / "ok.patch").as_posix()}" && echo APPLIED'):
            with self.subTest(command=command):
                self.assertIsNone(self.fire(self.approved, "Bash", {"command": command}))

    def test_git_apply_outside_the_write_paths_is_refused(self):
        cases = {"modify.patch": [("src/a.ts", "src/a.ts"), ("src/b.ts", "src/b.ts")],
                 "create.patch": [(None, "src/c.ts")], "delete.patch": [("src/b.ts", None)],
                 "rename.patch": [("src/a.ts", "src/b.ts", "rename")]}
        for name, files in cases.items():
            with self.subTest(patch=name):
                self.write_patch(name, *files)
                self.assert_outside(f"git apply {name}")

    def test_strip_and_directory_values_in_a_separate_word_match_the_joined_forms(self):
        (self.repo / "deep.patch").write_text(patch(("top/src/a.ts", "top/src/a.ts")).replace(
            "a/top/", "a/x/top/").replace("b/top/", "b/x/top/"), encoding="utf-8")  # a/x/top/src/a.ts
        (self.repo / "flat.patch").write_text(patch(("a.ts", "a.ts")), encoding="utf-8")
        for command in ("git apply -p3 deep.patch", "git apply -p 3 deep.patch", "git apply --directory=src flat.patch",
                        "git apply --directory src flat.patch", "git apply --directory src/ -p 1 flat.patch"):
            with self.subTest(command=command):
                self.assertIsNone(self.fire(self.approved, "Bash", {"command": command}))
        for command in ("git apply -p2 deep.patch", "git apply -p 2 deep.patch", "git apply flat.patch",
                        "git apply --directory=lib flat.patch", "git apply --directory lib flat.patch"):
            with self.subTest(command=command):
                self.assert_outside(command)

    def test_hunk_lines_that_look_like_headers_are_not_read_as_files(self):
        hunk = ("diff --git a/src/a.ts b/src/a.ts\n--- a/src/a.ts\n+++ b/src/a.ts\n@@ -1,3 +1,3 @@\n context\n"
                "--- a/src/b.ts\n+++ b/src/c.ts\n")  # a removed "-- a/src/b.ts" line and an added "++ b/src/c.ts" line
        (self.repo / "hunk.patch").write_text(hunk, encoding="utf-8")
        self.assertIsNone(self.fire(self.approved, "Bash", {"command": "git apply hunk.patch"}))
        # A plain unified diff (no `diff --git`): the header after a complete hunk starts a new file section.
        plain = ("--- a/src/a.ts\n+++ b/src/a.ts\n@@ -1,2 +1,2 @@\n-x\n--- y\n+z\n+++ w\n"
                 "--- a/src/b.ts\n+++ b/src/b.ts\n@@ -1 +1 @@\n-x\n+y\n")
        (self.repo / "plain.patch").write_text(plain, encoding="utf-8")
        self.assert_outside("git apply plain.patch")
        (self.repo / "plain.patch").write_text(plain.replace("src/b.ts", "src/new/b.ts"), encoding="utf-8")
        self.assertIsNone(self.fire(self.approved, "Bash", {"command": "git apply plain.patch"}))
        # A hunk that claims more lines than it has does not hide the next file's `diff --git` header.
        short = ("diff --git a/src/a.ts b/src/a.ts\n--- a/src/a.ts\n+++ b/src/a.ts\n@@ -1,50 +1,50 @@\n-x\n+y\n"
                 + patch(("src/b.ts", "src/b.ts")))
        (self.repo / "short.patch").write_text(short, encoding="utf-8")
        self.assert_outside("git apply short.patch")

    def test_each_file_is_listed_once_per_command(self):
        """shell_writes is also read by plain_reply.py, so its targets are an interface: one target per file."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("phase_gate_h3", GATE)
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        self.write_patch("one.patch", ("src/a.ts", "src/a.ts"), ("src/b.ts", "src/c.ts", "rename"))
        self.write_patch("two.patch", ("src/a.ts", "src/a.ts"))
        targets = gate.shell_writes("git apply one.patch two.patch one.patch", str(self.repo))
        files = [where for kind, where, _ in targets if kind == "path"]
        self.assertEqual(sorted(f.rsplit("/", 1)[-1] for f in files), ["a.ts", "b.ts", "c.ts"])

    def test_git_apply_with_a_patch_the_gate_cannot_read_is_refused(self):
        for command in ("git apply missing.patch", "git apply -", "git apply < x.patch", "cat x.patch | git apply"):
            with self.subTest(command=command):
                out = self.fire(self.approved, "Bash", {"command": command})
                self.assertEqual(out and out["permissionDecision"], "deny")
                self.assertIn("cannot read the patch", out["permissionDecisionReason"])

    def test_git_checkout_and_restore_of_files_are_checked(self):
        for command in ("git checkout -- src/a.ts", "git checkout HEAD~1 -- src/a.ts src/new/y.ts",
                        "git restore src/a.ts", "git restore --staged src/a.ts", "git restore -s HEAD src/a.ts",
                        "git restore --source=HEAD --worktree -- src/a.ts"):
            with self.subTest(command=command):
                self.assertIsNone(self.fire(self.approved, "Bash", {"command": command}))
        for command in ("git checkout -- src/b.ts", "git checkout HEAD -- src/a.ts src/b.ts", "git restore src/b.ts",
                        "git restore --staged src/b.ts", "git restore -s HEAD src/b.ts",
                        "git restore --source=HEAD~2 src/b.ts"):
            with self.subTest(command=command):
                self.assert_outside(command)

    def test_a_git_file_write_without_approval_is_refused_as_before(self):
        self.write_patch("ok.patch", ("src/a.ts", "src/a.ts"))
        for command in ("git apply ok.patch", "git checkout -- src/a.ts", "git restore src/a.ts"):
            with self.subTest(command=command):
                self.assertEqual(self.decision([ROUTER, self.records(B)], "Bash", {"command": command}), "deny")


class NestedFixtureRepositories(GateCase):
    """V2 (paid session): a disposable fixture repository (its own `.git`) under the project's .artifacts folder made
    the gate refuse writes there as "outside the files the approved plan may change". The .artifacts exemption is
    about the outer project; a nested repository elsewhere in the project gets no exemption."""

    def setUp(self):
        super().setUp()
        self.task(A, APPROVED, write_paths=["src/a.ts"])
        self.approved = [ROUTER] + self.approval(A)
        self.fixture = self.repo / ".artifacts" / A / "runs" / "x"
        (self.fixture / ".git").mkdir(parents=True)
        (self.fixture / "src").mkdir()
        (self.fixture / "src" / "page.html").write_text("x\n", encoding="utf-8")

    def test_writes_into_a_fixture_repository_under_artifacts_are_allowed(self):
        page = str(self.fixture / "src" / "page.html")
        rel = f".artifacts/{A}/runs/x/src"
        for tool_name, data in (("Edit", {"file_path": page, "old_string": "x", "new_string": "y"}),
                                ("Write", {"file_path": str(self.fixture / "src" / "new.html"), "content": "y"}),
                                ("Bash", {"command": f"cp src/a.ts {rel}/a.ts"}),
                                ("Bash", {"command": f"mv {rel}/page.html {rel}/moved.html"}),
                                ("Bash", {"command": f"cd {self.fixture.as_posix()} && cp src/page.html src/b.html"})):
            with self.subTest(tool=tool_name, data=data):
                self.assertIsNone(self.fire(self.approved, tool_name, data))

    def test_project_files_and_other_nested_repositories_stay_gated(self):
        out = self.fire(self.approved, "Edit", self.code("src/b.ts"))
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn("is outside the files the approved plan may change", out["permissionDecisionReason"])
        (self.repo / "vendor" / "lib" / ".git").mkdir(parents=True)
        self.assertEqual(self.decision(self.approved, "Edit", self.code("vendor/lib/x.ts")), "deny")
        self.assertEqual(self.decision(self.approved, "Bash", {"command": "cp src/a.ts vendor/lib/x.ts"}), "deny")
        # A linked worktree of this same repository is the project, not output, even when it sits under .artifacts.
        linked = self.repo / ".artifacts" / A / "wt"
        linked.mkdir(parents=True)
        (linked / ".git").write_text(f"gitdir: {(self.repo / '.git' / 'worktrees' / 'wt').as_posix()}\n", encoding="utf-8")
        self.assertEqual(self.decision(self.approved, "Edit", {"file_path": str(linked / "src" / "b.ts")}), "deny")


class VariableRecordWrites(GateCase):
    """H3 (D36): a record write through a shell variable that holds the record.py command moves the current task, as
    the literal form does."""

    def setUp(self):
        super().setUp()
        self.task(GUARD, APPROVED, write_paths=["hooks/x.py"])
        self.task(REWORK, "- Blockers: asked the owner", report=None)

    def edit_after(self, command):
        rows = [ROUTER] + self.approval(GUARD) + [tool("Bash", command=command), user("ok")]
        return self.fire(rows, "Edit", self.code("hooks/x.py"))

    def test_a_variable_holding_record_py_moves_the_current_task(self):
        for command in (variable_record(REWORK),
                        f'{RECORD}; ${{R}} append docs/plans/{REWORK}/FINDINGS.md - <<\'EOF\'\nx\nEOF\n',
                        f'R="python -X utf8 -I D:/w/skills/workflow/scripts/record.py" && $R set-line '
                        f'docs/plans/{REWORK}/PLAN.md Status x'):
            with self.subTest(command=command):
                out = self.edit_after(command)
                self.assertEqual(out and out["permissionDecision"], "deny")
                self.assertIn(REWORK, out["permissionDecisionReason"])

    def test_a_variable_without_record_py_does_not(self):
        # The guard task stays current: its approval covers hooks/x.py.
        for command in (f'R="python other.py" && $R append docs/plans/{REWORK}/PLAN.md -',
                        f'$R append docs/plans/{REWORK}/PLAN.md -'):
            with self.subTest(command=command):
                self.assertIsNone(self.edit_after(command))


# H4: the small-change route (agreement R11, A15)


SMALL_YES = '- Approval: small change approved 2026-11-11: "yes, go ahead"'


class SmallChangeRoute(GateCase):
    """A `- Small change: <files> — <what changes>` checkpoint line plus the owner's quoted yes allows writes to exactly
    those existing files without an HTML report, when the yes is a real user message after an assistant message that
    says "Small change:" and names every listed file. Everything else is refused with the full-route message."""

    def setUp(self):
        super().setUp()
        for name in ("src/a.ts", "src/b.ts", "src/c.ts"):
            (self.repo / name).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / name).write_text("x\n", encoding="utf-8")
        self.small("src/a.ts, src/b.ts")

    def small(self, files, approval=SMALL_YES):
        self.task(A, f"- Small change: {files} — rename the Save button label", approval, report=None)

    def offer(self, files="src/a.ts, src/b.ts"):
        return say(f"Here is the change.\n\nSmall change: {files} — rename the Save button label\n\nApprove?")

    def rows(self, *middle):
        return [ROUTER, self.records(A)] + list(middle or (self.offer(), user("yes, go ahead")))

    def refused(self, rows, tool_name, data, *words):
        out = self.fire(rows, tool_name, data)
        self.assertEqual(out and out["permissionDecision"], "deny", data)
        for word in words:
            self.assertIn(word, out["permissionDecisionReason"])
        return out["permissionDecisionReason"]

    def test_listed_files_are_writable_after_the_quoted_yes(self):
        self.assertIsNone(self.fire(self.rows(), "Edit", self.code("src/a.ts")))
        self.assertIsNone(self.fire(self.rows(), "Bash", {"command": "sed -i s/a/b/ src/b.ts"}))
        self.assertIsNone(self.fire(self.rows(), "Bash", {"command": "git checkout -- src/a.ts"}))

    def test_an_unlisted_or_new_file_is_refused_with_the_full_route_message(self):
        (self.repo / "c.patch").write_text(patch(("src/c.ts", "src/c.ts")), encoding="utf-8")
        for tool_name, data in (("Edit", self.code("src/c.ts")), ("Write", self.code("src/new.ts")),
                                ("Bash", {"command": "git restore src/c.ts"}),
                                ("Bash", {"command": "git apply c.patch"}),
                                ("mcp__x__write_file", {})):
            with self.subTest(data=data):
                self.refused(self.rows(), tool_name, data, "Small change", "full route")

    def test_the_offer_must_come_while_this_task_is_current(self):
        rows = [ROUTER, self.offer(), self.records(A), user("yes, go ahead")]
        self.refused(rows, "Edit", self.code("src/a.ts"), "Small change")

    def test_the_offer_line_must_list_exactly_the_checkpoint_files(self):
        for files in ("src/b.ts,src/a.ts", " `src/a.ts` ,  ./src/b.ts "):
            with self.subTest(files=files):
                self.assertIsNone(self.fire(self.rows(self.offer(files), user("yes, go ahead")), "Edit",
                                            self.code("src/a.ts")))
        absolute = f"{(self.repo / 'src/a.ts').as_posix()}, {(self.repo / 'src/b.ts').as_posix()}"
        prose = say("Small change: src/a.ts — rename the label. It also touches src/b.ts.")
        for offer in [self.offer(f) for f in ("src/a.ts.bak, src/b.ts", "lib/src/a.ts, src/b.ts", "src/a.tsx, src/b.ts",
                                              "src/a.ts, src/b.ts, src/c.ts", "src/a.ts and src/b.ts", absolute)] + [prose]:
            with self.subTest(offer=offer):
                self.refused(self.rows(offer, user("yes, go ahead")), "Edit", self.code("src/a.ts"), "Small change")

    def test_a_line_edited_after_the_yes_to_add_a_file_needs_a_new_offer(self):
        rows = self.rows()
        self.small("src/a.ts, src/b.ts, src/c.ts")
        self.refused(rows, "Edit", self.code("src/a.ts"), "Small change")
        again = rows + [self.offer("src/a.ts, src/b.ts, src/c.ts"), user("yes, go ahead")]
        self.assertIsNone(self.fire(again, "Edit", self.code("src/c.ts")))

    def test_a_description_changed_after_the_yes_needs_a_new_offer(self):
        """SP8: the yes binds the description after the dash too, not only the file set."""
        rows = self.rows()
        self.task(A, "- Small change: src/a.ts, src/b.ts — rename the Save button label and remove the Cancel button",
                  SMALL_YES, report=None)
        self.refused(rows, "Edit", self.code("src/a.ts"), "Small change", "description")
        # An offer that shows a different description does not count either.
        self.small("src/a.ts, src/b.ts")
        other = say("Small change: src/a.ts, src/b.ts — remove the Cancel button\n\nApprove?")
        self.refused(self.rows(other, user("yes, go ahead")), "Edit", self.code("src/a.ts"), "Small change")
        # Spacing differences do not matter; a new offer of the changed description and a new yes do.
        spaced = say("Small change: src/a.ts, src/b.ts —   rename the  Save button label  \n\nApprove?")
        self.assertIsNone(self.fire(self.rows(spaced, user("yes, go ahead")), "Edit", self.code("src/a.ts")))
        changed = "rename the Save button label and remove the Cancel button"
        self.task(A, f"- Small change: src/a.ts, src/b.ts — {changed}", SMALL_YES, report=None)
        again = rows + [say(f"Small change: src/a.ts, src/b.ts — {changed}"), user("yes, go ahead")]
        self.assertIsNone(self.fire(again, "Edit", self.code("src/a.ts")))

    def test_harmless_decoration_of_the_description_still_binds(self):
        """RR1: emphasis, end punctuation and a short approval question after the description do not change what the
        owner saw. Anything that changes the description's words still needs a new offer."""
        files = "src/a.ts, src/b.ts"
        for shown in ("rename the Save button label. Approve?", "rename the Save button label.",
                      "*rename the Save button label*", "**rename the Save button label**!", "rename the Save button label? OK?",
                      "_rename the Save button label_. Shall I proceed?"):
            with self.subTest(shown=shown):
                offer = say(f"Small change: {files} — {shown}")
                self.assertIsNone(self.fire(self.rows(offer, user("yes, go ahead")), "Edit", self.code("src/a.ts")))
        # A decorated checkpoint line matches a plain offer too.
        self.task(A, f"- Small change: {files} — *rename the Save button label*.", SMALL_YES, report=None)
        self.assertIsNone(self.fire(self.rows(), "Edit", self.code("src/a.ts")))
        self.small(files)
        for shown in ("rename the Save button label. Also delete the Cancel button?", "rename the Save button",
                      "rename the Save button label and the title", "rename the Save button label. Remove it?",
                      "rename the Cancel button label. Approve?"):
            with self.subTest(shown=shown):
                offer = say(f"Small change: {files} — {shown}")
                self.refused(self.rows(offer, user("yes, go ahead")), "Edit", self.code("src/a.ts"), "description")

    def test_an_offer_wrapped_in_inline_code_binds_like_a_plain_one(self):
        """V2 (paid session): the agent showed the whole offer as one inline-code span, the owner said "yes", and every
        edit was refused because the offer was not recognized. One leading and one matching trailing backtick around
        the whole line are dropped; the file set and description must still match exactly."""
        (self.repo / "src/page.html").write_text("<label>Name</label>\n", encoding="utf-8")
        change = 'change the Name field\'s label text from "Name" to "Full name"'
        self.task(A, f"- Small change: src/page.html — {change}",
                  '- Approval: small change approved 2026-11-11: "yes"', report=None)
        for shown in (f"`- Small change: src/page.html — {change}`", f"`Small change: src/page.html — {change}`",
                      f"Small change: `src/page.html` — {change}"):
            with self.subTest(shown=shown):
                self.assertIsNone(self.fire(self.rows(say(shown), user("yes")), "Edit", self.code("src/page.html")))
        other = say("`- Small change: src/page.html — change the Email field's label text from \"Email\" to \"E-mail\"`")
        self.refused(self.rows(other, user("yes")), "Edit", self.code("src/page.html"), "Small change")

    def test_an_offer_in_a_subagent_message_or_a_tool_result_does_not_count(self):
        sidechain = dict(self.offer(), isSidechain=True)
        result = user([{"type": "tool_result", "tool_use_id": "t1",
                        "content": "Small change: src/a.ts, src/b.ts — rename the Save button label"}])
        for offer in (sidechain, result):
            with self.subTest(offer=offer):
                self.refused(self.rows(offer, user("yes, go ahead")), "Edit", self.code("src/a.ts"), "Small change")

    def test_a_listed_file_is_never_deleted_or_renamed(self):
        for command in ("rm src/a.ts", "del src/a.ts", "erase src/a.ts", "unlink src/a.ts", "git rm src/a.ts",
                        ": > src/a.ts", "> src/a.ts", "cat /dev/null > src/a.ts", "truncate -s 0 src/a.ts"):
            with self.subTest(command=command):
                self.refused(self.rows(), "Bash", {"command": command}, "a small change never deletes a file",
                             "full route")
        for command in ("Remove-Item src/a.ts", "Remove-Item -Path src/a.ts", "Clear-Content src/a.ts"):
            with self.subTest(command=command):
                self.refused(self.rows(), "PowerShell", {"command": command}, "a small change never deletes a file")
        for command in ("mv src/a.ts src/b.ts", "git mv src/a.ts src/b.ts"):
            with self.subTest(command=command):
                self.refused(self.rows(), "Bash", {"command": command}, "full route")
        # Writing content into a listed file is still an edit.
        self.assertIsNone(self.fire(self.rows(), "Bash", {"command": "echo y > src/a.ts"}))

    def test_an_ask_user_question_offer_and_its_answer_work(self):
        question = "Small change: src/a.ts, src/b.ts — rename the Save button label"
        ask = {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "q1", "name": "AskUserQuestion",
               "input": {"questions": [{"question": question, "options": [{"label": "Yes, go ahead"}]}]}}]}}
        answer = user([{"type": "tool_result", "tool_use_id": "q1", "content": "answered"}],
                      toolUseResult={"answers": {question: "yes, go ahead"}})
        self.assertIsNone(self.fire(self.rows(ask, answer), "Edit", self.code("src/a.ts")))
        # A question that was never answered presents nothing; an answer to another question does not count.
        self.refused(self.rows(ask, user("unrelated")), "Edit", self.code("src/a.ts"), "Small change")
        other = user([{"type": "tool_result", "tool_use_id": "q1", "content": "answered"}],
                     toolUseResult={"answers": {"another question": "yes, go ahead"}})
        self.refused(self.rows(ask, other), "Edit", self.code("src/a.ts"), "Small change")

    def real_git(self):
        """Turn the fake repository into a real one with src/a.ts, src/b.ts and src/c.ts committed."""
        import shutil
        shutil.rmtree(self.repo / ".git")

        def run(*args):
            subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)

        run("init", "-q")
        run("config", "user.email", "t@example.invalid")
        run("config", "user.name", "t")
        run("add", "src")
        run("commit", "-q", "-m", "base")
        (self.repo / "src/a.ts").write_text("changed\n", encoding="utf-8")

    def test_git_writes_follow_the_lightweight_commit_rule(self):
        """Commit, push and other git writes that are not file writes: the quoted yes alone never allows them. A
        commit needs the owner's latest message to ask for it and may include only the listed files; everything else
        keeps the full gate. Git file writes stay limited to the listed files."""
        self.real_git()
        commit = {"command": "git add src/a.ts && git commit -m 'rename the label'"}
        out = self.fire(self.rows(), "Bash", commit)
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn("latest message", out["permissionDecisionReason"])
        asked = self.rows(self.offer(), user("yes, go ahead"), user("commit it"))
        self.assertIsNone(self.fire(asked, "Bash", commit))
        for command in ("git push origin main", "git commit --amend -m x", "git branch -D x",
                        "git reset --hard", "git merge x", "git rebase main", "git stash", "git checkout -f"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(self.rows(self.offer(), user("yes, go ahead"),
                                                         user(f"commit it and run {command}")), "Bash",
                                               {"command": command}), "deny")
        # A changed file that is not listed keeps the commit refused.
        (self.repo / "src/c.ts").write_text("changed\n", encoding="utf-8")
        out = self.fire(asked, "Bash", commit)
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn("src/c.ts", out["permissionDecisionReason"])
        # Without the small-change yes, a commit request alone does not allow the commit either.
        self.assertEqual(self.decision(self.rows(self.offer(), user("commit it")), "Bash", commit), "deny")
        # Git file writes of listed files still pass with the yes alone.
        self.assertIsNone(self.fire(self.rows(), "Bash", {"command": "git checkout -- src/b.ts"}))

    def test_installs_stay_blocked(self):
        self.assertEqual(self.decision(self.rows(), "Bash", {"command": "npm install left-pad"}), "deny")

    def test_the_yes_must_follow_a_message_naming_every_listed_file(self):
        cases = {"yes before the offer": (user("yes, go ahead"), self.offer()),
                 "offer names one file": (self.offer("src/a.ts"), user("yes, go ahead")),
                 "no offer": (say("I will rename the label in src/a.ts and src/b.ts."), user("yes, go ahead")),
                 "yes from the agent": (self.offer(), say("yes, go ahead"))}
        for name, middle in cases.items():
            with self.subTest(case=name):
                self.refused(self.rows(*middle), "Edit", self.code("src/a.ts"), "Small change")

    def test_a_withdrawal_or_a_stop_after_the_yes_still_counts(self):
        for later in (user("I withdraw the approval"), user("stop")):
            with self.subTest(later=later):
                rows = self.rows(self.offer(), user("yes, go ahead"), later)
                self.assertEqual(self.decision(rows, "Edit", self.code("src/a.ts")), "deny")

    def test_a_later_session_reconfirms_on_its_own_line(self):
        """SP2: the yes from an earlier session is not in this transcript. The agent shows the same offer again, gets a
        new yes and records it on a Reconfirmed line; the original Approval quote stays unchanged."""
        line = "- Small change: src/a.ts, src/b.ts — rename the Save button label"
        later = self.rows(self.offer(), user("yes, still fine"))
        reason = self.refused(later, "Edit", self.code("src/a.ts"),
                              '`- Reconfirmed (gate two): small change, <date>: "<the owner\'s whole answer>"`',
                              "never change the original Approval quote")
        self.assertNotIn("quote their whole answer on the `- Approval:` line", reason)
        again = '- Reconfirmed (gate two): small change, 2026-11-12: "yes, still fine"'
        self.task(A, line, SMALL_YES, again, report=None)
        self.assertIsNone(self.fire(later, "Edit", self.code("src/a.ts")))
        # The same rules as the Approval quote: whole message, after a matching offer shown while the task is
        # current, no later withdrawal or stop; the Approval line must still say approved.
        cases = {"part of the message": (SMALL_YES, '- Reconfirmed (gate two): small change, 2026-11-12: "yes"', later),
                 "yes before the offer": (SMALL_YES, again, self.rows(user("yes, still fine"), self.offer())),
                 "offer before the task": (SMALL_YES, again, [ROUTER, self.offer(), self.records(A),
                                                             user("yes, still fine")]),
                 "subagent offer": (SMALL_YES, again, self.rows(dict(self.offer(), isSidechain=True),
                                                                user("yes, still fine"))),
                 "withdrawn": (SMALL_YES, again, later + [user("I withdraw the approval")]),
                 "stopped": (SMALL_YES, again, later + [user("stop")]),
                 "approval withdrawn on the line": ('- Approval: not approved: "yes, go ahead"', again, later),
                 "not a small change confirmation": (SMALL_YES, '- Reconfirmed (gate two): r1, 2026-11-12: '
                                                                '"yes, still fine"', later)}
        for name, (approval, confirmed, rows) in cases.items():
            with self.subTest(case=name):
                self.task(A, line, approval, confirmed, report=None)
                self.assertEqual(self.decision(rows, "Edit", self.code("src/a.ts")), "deny")
        # Unlisted files stay refused with a valid Reconfirmed line.
        self.task(A, line, SMALL_YES, again, report=None)
        self.refused(later, "Edit", self.code("src/c.ts"), "full route")

    def test_the_approval_line_must_quote_the_whole_yes(self):
        for approval in ('- Approval: small change approved 2026-11-11: "yes"', "- Approval: small change approved",
                         '- Approval: not approved: "yes, go ahead"'):
            with self.subTest(approval=approval):
                self.small("src/a.ts, src/b.ts", approval)
                self.assertEqual(self.decision(self.rows(), "Edit", self.code("src/a.ts")), "deny")

    def test_an_invalid_line_counts_as_absent_with_a_clear_reason(self):
        cases = {"src/, src/a.ts": "src/ is a folder", "src/*.ts": "src/*.ts is a wildcard",
                 "src/a.ts, src/z.ts": "src/z.ts does not exist", "": "names no files"}
        for files, word in cases.items():
            with self.subTest(files=files):
                self.small(files)
                rows = self.rows(self.offer(files), user("yes, go ahead"))
                reason = self.refused(rows, "Edit", self.code("src/a.ts"), word)
                self.assertIn("no plan report", reason)  # as if the line were absent
                self.assertIn("Approval needs the plan report from workflow-specify", reason)  # ST6: CONTEXT.md term

    def test_a_task_with_a_plan_report_keeps_the_full_route(self):
        """The small route applies only without a plan report; with one, the full approval rules apply as before."""
        self.task(A, "- Small change: src/a.ts, src/b.ts — rename the Save button label", SMALL_YES)
        self.assertEqual(self.decision(self.rows(), "Edit", self.code("src/a.ts")), "deny")

    def test_a_plan_report_refusal_says_the_small_change_line_was_ignored(self):
        """SP4: with a plan report the small route does not apply, and the refusal says why the valid line is ignored."""
        self.task(A, "- Small change: src/a.ts, src/b.ts — rename the Save button label", SMALL_YES)
        self.refused(self.rows(), "Edit", self.code("src/a.ts"),
                     "Its `- Small change:` line is ignored because this task has a plan report",
                     "use the full route or a new task")

    def test_an_approval_naming_a_missing_report_keeps_the_full_route(self):
        """D46: the small route needs a task folder with no .html report (SETUP.md, VISUAL-REVIEW.md). An Approval line
        that names a report file that does not exist (a typo or an old name) must not open the small route while
        another report exists."""
        self.task(A, "- Small change: src/a.ts, src/b.ts — rename the Save button label",
                  '- Approval: small change approved 2026-11-11 (reviews/plan-r9.html): "yes, go ahead"')
        self.refused(self.rows(), "Edit", self.code("src/a.ts"), "no plan report named plan-r9.html",
                     "Its `- Small change:` line is ignored because this task has a plan report")

    def test_the_stop_hook_demands_report_guides_when_the_approval_names_a_missing_report(self):
        """D46: with a plan report present, an Approval line naming a missing report does not make this a small change
        task for the Stop hook either; the report guides are still demanded."""
        self.task(A, "- Small change: src/a.ts, src/b.ts — rename the Save button label",
                  '- Approval: small change approved 2026-11-11 (reviews/plan-r9.html): "yes, go ahead"')
        rows = [user("/workflow-axa:workflow rename the save label"), skill("workflow-axa:workflow-specify"),
                self.records(A), self.offer(), user("yes, go ahead"),
                tool("Edit", file_path=self.code("src/a.ts")["file_path"], old_string="x", new_string="y"),
                say("Renamed.\n\n**Done.**")]
        write_rows(self.path, rows)
        code, out = run_reply({"transcript_path": str(self.path), "cwd": str(self.repo)})
        self.assertIn("TASK-REPORT.md", json.loads(out)["reason"])

    def test_the_stop_hook_skips_report_guides_but_demands_the_review(self):
        rows = [user("/workflow-axa:workflow rename the save label"), skill("workflow-axa:workflow-specify"),
                self.records(A), self.offer(), user("yes, go ahead"),
                tool("Edit", file_path=self.code("src/a.ts")["file_path"], old_string="x", new_string="y"),
                say("Renamed.\n\n**Done.**")]
        write_rows(self.path, rows)
        code, out = run_reply({"transcript_path": str(self.path), "cwd": str(self.repo)})
        reason = json.loads(out)["reason"]
        self.assertIn("no review", reason)
        for guide in ("TASK-REPORT.md", "simple-english/SKILL.md", "FLOWCHART-DESIGN.md"):
            self.assertNotIn(guide, reason)
        # An invalid Small change line (a missing file) counts as absent: the report guides are demanded again.
        self.small("src/a.ts, src/z.ts")
        write_rows(self.path, rows + [say("Checked again.\n\n**Done.**")])
        self.assertIn("TASK-REPORT.md", json.loads(run_reply({"transcript_path": str(self.path),
                                                               "cwd": str(self.repo)})[1])["reason"])
        # Control: the same task with a plan report gets the report guides demanded.
        self.task(A, "- Small change: src/a.ts, src/b.ts — rename the Save button label", SMALL_YES)
        write_rows(self.path, rows + [say("Checked.\n\n**Done.**")])
        self.assertIn("TASK-REPORT.md", json.loads(run_reply({"transcript_path": str(self.path),
                                                               "cwd": str(self.repo)})[1])["reason"])


# E35: agreement and plan revisions share one number space


class RevisionNumberRegressions(GateCase):

    def test_an_agreement_revision_above_the_approved_plan_revision_refuses_the_write(self):
        """E35 (FINDINGS, 2026-11-11). Characterization, not a defect marker: today the gate refuses an approved
        write when the checkpoint's Agreement line names agreement revision r3 and the Approval line approves plan
        revision r1, because any rN in the checkpoint is read as a plan revision.
        Owner decision, not H2/H3/H4: TASK-FOLDER.md:43 asks for a revision on the Agreement line, so agreement r3
        with plan r1 is a legitimate state. But test_phase_gate_hook
        test_a_later_revision_anywhere_in_the_checkpoint_voids_the_approval pins "- Agreement: revision r2 agreed by
        the owner" as voiding an r1 approval, so a fix needs a decision on separate number spaces first. This test
        records today's behavior so no later ticket changes it by accident."""
        self.task(A, APPROVED, "- Agreement (gate one): agreed r3 (Behavior, Scope)")
        out = self.fire([ROUTER] + self.approval(A), "Edit", self.code())
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn("names revision r3", out["permissionDecisionReason"])
        # The workaround used since E35: an Agreement line without an rN token.
        self.task(A, APPROVED, "- Agreement (gate one): agreed (sections Behavior and Scope)")
        self.assertIsNone(self.fire([ROUTER] + self.approval(A), "Edit", self.code()))


# Altinstar items (memory note of 2026-11-05)


class AltinstarRegressions(GateCase):

    def test_requirement_ids_are_not_report_revisions(self):
        """Altinstar, requirement IDs read as revisions. Evidence: in the Altinstar main session and two of its
        worker sessions on 2026-11-04 the gate refused approved edits with "approves r3, but the checkpoint names
        revision r7" and "approves r2 ... r7". Before 45670f2 (2.8.0-rc.4, 2026-11-05) REVISION was
        `r(\\d+)` with re.I, so an uppercase requirement or ticket ID such as R7 counted. Fixed since rc.4; this
        pins it (passes today). An explicit "revision R7" still counts, by design (phase_gate.py:65)."""
        self.task(A, APPROVED, "- Requirements: R1, R2 and R7 covered; tickets T1-T7")
        self.assertIsNone(self.fire([ROUTER] + self.approval(A), "Edit", self.code()))
        self.task(A, APPROVED, "- Status: revision R7 drafted")
        self.assertEqual(self.decision([ROUTER] + self.approval(A), "Edit", self.code()), "deny")

    def test_qualified_requirement_ids_are_not_revisions_either(self):
        """T6 of 2026-11-12-approval-gate-false-refusals (FINDINGS E1): "R6 (FSR)" and "D4-R6" were read as
        revision r6 before rc.4. Pin (passes today)."""
        self.task(A, APPROVED, "- Requirements: R6 (FSR) and D4-R6 covered")
        self.assertIsNone(self.fire([ROUTER] + self.approval(A), "Edit", self.code()))

    def test_a_report_named_only_inside_the_approval_question_counts_as_presented(self):
        """T6 of 2026-11-12-approval-gate-false-refusals (FINDINGS E3a): on 2026-11-05 the owner answered "Approve D5
        plan and D5-A7" to a question whose text named the plan report; the chat text did not. Since rc.4 an answered
        question that names the report presents it. Pin (passes today)."""
        folder = self.task(A, APPROVED)
        report = folder / "reviews" / "plan-r1.html"
        rel = f"docs/plans/{A}/reviews/plan-r1.html"
        question = f"Approve the plan in {report}?"
        ask = {"type": "assistant", "message": {"content": [{"type": "tool_use", "id": "q1", "name": "AskUserQuestion",
               "input": {"questions": [{"question": question, "options": [{"label": "Yes to both"}]}]}}]}}
        answer = user([{"type": "tool_result", "tool_use_id": "q1", "content": "answered"}],
                      toolUseResult={"answers": {question: "Yes to both"}})
        # The fingerprints the host records: the agent read the report before asking, and the gate marks the answer.
        read = hook_context("PostToolUse", f"workflow-axa report fingerprint: {rel} sha256={sha(report)}")
        reply = hook_context("PostToolUse", f"workflow-axa report at owner reply: {rel} sha256={sha(report)}")
        rows = [ROUTER, self.records(A), read, ask, answer, reply]
        self.assertIsNone(self.fire(rows, "Edit", self.code(), hooks=False))

    def test_the_stop_hook_never_adds_a_turn_while_waiting_or_on_its_own_retry(self):
        """Altinstar, repeated goal stops. Evidence: the repeated stops in the Altinstar sessions were the host's
        session-scoped /goal Stop hook ("A session-scoped Stop hook is now active with condition ..."), not a
        workflow-axa hook, so they cannot be reproduced with these scripts. This pins the workflow-axa side (passes
        today): plain_reply.py stays silent at "Waiting on you" and on stop_hook_active, even with unread files."""
        rows = [user("/workflow-axa:workflow add a badge"), skill("workflow-axa:workflow-clarify"),
                say("**Waiting on you:** answer Q1 to Q3.")]
        write_rows(self.path, rows)
        self.assertEqual(run_reply({"transcript_path": str(self.path), "cwd": str(self.repo)}), (0, ""))
        rows[-1] = say("Questions are ready.")
        write_rows(self.path, rows)
        self.assertEqual(run_reply({"transcript_path": str(self.path), "stop_hook_active": True}), (0, ""))


class CheckpointHeadingRegressions(GateCase):
    """T1 of 2026-11-12-approval-gate-false-refusals (FINDINGS E2). The Altinstar PLAN used the heading
    `### Current checkpoint (D4)`; the gate only knew `## Current checkpoint`, read the whole PLAN and let an old
    revision elsewhere outrank the current approval."""

    def plan(self, text):
        folder = self.task(A, APPROVED)
        (folder / "PLAN.md").write_text(text, encoding="utf-8")

    def test_a_deeper_or_suffixed_checkpoint_heading_is_the_checkpoint(self):
        self.plan(f"# Task\n\n### Current checkpoint (D4)\n- Status: x\n{APPROVED}\n\n"
                  "### Revision log\n- r7 drafted earlier\n")
        self.assertIsNone(self.fire([ROUTER] + self.approval(A), "Edit", self.code()))
        self.plan(f"# Task\n\n## Current checkpoint (2026-10-09)\n- Status: x\n{APPROVED}\n\n"
                  "## History\n- r7 drafted earlier\n")
        self.assertIsNone(self.fire([ROUTER] + self.approval(A), "Edit", self.code()))

    def test_the_section_ends_only_at_a_heading_of_the_same_or_higher_level(self):
        self.plan(f"# Task\n\n### Current checkpoint (D4)\n- Status: x\n{APPROVED}\n#### Detail\n- r7 drafted\n")
        out = self.fire([ROUTER] + self.approval(A), "Edit", self.code())
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn("r7", out["permissionDecisionReason"])

    def test_without_a_checkpoint_heading_the_whole_plan_is_read(self):
        self.plan(f"# Task\n\n## Status\n{APPROVED}\n\n## History\n- r7 drafted earlier\n")
        self.assertEqual(self.decision([ROUTER] + self.approval(A), "Edit", self.code()), "deny")


class AgreementGateRegressions(GateCase):
    """T2 of 2026-11-12-approval-gate-false-refusals (owner Q7b a): on the two-gate route a code change waits for a
    recorded agreement (gate one) as well as the plan approval (gate two)."""

    TWO_GATE = '- Approval (gate two): r1 approved by the owner 2026-11-12: "Yes to both" (report `reviews/plan-r1.html`)'

    def test_a_missing_or_pending_agreement_refuses_the_write(self):
        for agreement in ("- Agreement (gate one): pending, agreement 1 proposed",
                          "- Agreement (gate one): not agreed yet", None):
            with self.subTest(agreement=agreement):
                self.task(A, *([agreement] if agreement else []), self.TWO_GATE)
                out = self.fire([ROUTER] + self.approval(A), "Edit", self.code())
                self.assertEqual(out and out["permissionDecision"], "deny")
                self.assertIn("Agreement (gate one)", out["permissionDecisionReason"])

    def test_a_recorded_agreement_allows_the_write(self):
        for agreement in ('- Agreement (gate one): agreed 2026-11-12, agreement 1: "a) Agree (Recommended)"',
                          "- Agreement (gate one): agreed per the delegated task; the plan keeps its status awaiting "
                          "approval",
                          "- Agreement: agreed 2026-11-12", "- Agreement (gate one): waived by the owner",
                          "- Agreement (gate one): legacy", "- Agreement (gate one): not required - lightweight"):
            with self.subTest(agreement=agreement):
                self.task(A, agreement, self.TWO_GATE)
                self.assertIsNone(self.fire([ROUTER] + self.approval(A), "Edit", self.code()))

    def test_single_gate_and_legacy_tasks_are_not_checked(self):
        self.task(A, APPROVED)  # `- Approval:` without "(gate two)": an older single-gate task
        self.assertIsNone(self.fire([ROUTER] + self.approval(A), "Edit", self.code()))

    def test_a_legacy_two_gate_approval_needs_no_agreement_line(self):
        """Assumption A1 of agreement 1 (delivery reconciliation): a legacy Approval line passes without one."""
        self.task(A, '- Approval (gate two): legacy single-gate approval, revision r1: "Yes to both"')
        self.assertIsNone(self.fire([ROUTER] + self.approval(A), "Edit", self.code()))


class BulkArtifactDeletes(GateCase):
    """T3 of 2026-11-12-approval-gate-false-refusals (owner Q9 a): git clean, deleting .artifacts itself and wildcard
    deletes under it are refused in an active session; named files and folders stay deletable (ARTIFACTS.md)."""

    def run_shell(self, command, tool_name="Bash"):
        self.task(A, APPROVED)
        return self.fire([ROUTER] + self.approval(A), tool_name, {"command": command})

    def test_bulk_deletes_are_refused(self):
        for tool_name, command in (("Bash", "git clean -fdx"), ("Bash", "git -C . clean -fd"),
                                   ("Bash", 'bash -c "git clean -fdx"'), ("PowerShell", 'powershell -Command "git clean -fdx"'),
                                   ("Bash", "rm -rf .artifacts"),
                                   ("Bash", "rm -rf ./.artifacts/"), ("Bash", f"rm -rf {self.repo / '.artifacts'}"),
                                   ("Bash", "rm .artifacts/*"), ("Bash", "rm -rf .artifacts/task/*.png"), ("Bash", "cd .artifacts && rm *"),
                                   ("PowerShell", "Remove-Item .artifacts\\* -Recurse")):
            with self.subTest(command=command):
                out = self.run_shell(command, tool_name)
                self.assertEqual(out and out["permissionDecision"], "deny")
                self.assertIn(".artifacts", out["permissionDecisionReason"])

    def test_named_items_and_a_dry_run_stay_allowed(self):
        for command in ("rm .artifacts/task/a.txt", "rm -rf .artifacts/task/old-run", "git clean -n",
                        'git commit -m "never run git clean here"', "echo 'run git clean -fdx'",
                        "git commit -F - <<'EOF'\nRefuse git clean in bulk\nEOF"):
            with self.subTest(command=command):
                out = self.run_shell(command)
                self.assertNotIn("bulk", (out or {}).get("permissionDecisionReason", ""))
        self.assertIsNone(self.run_shell("rm .artifacts/task/a.txt"))


class LinkedWorktreeCopies(GateCase):
    """T5 of 2026-11-12-approval-gate-false-refusals (FINDINGS E4, E10, E11): a write refused in a linked worktree whose
    PLAN copy differs from the main checkout's says so, instead of only asking for approval again."""

    def linked(self):
        main_git = self.repo / ".git" / "worktrees" / "wt"
        main_git.mkdir(parents=True)
        wt = self.base / "wt"
        wt.mkdir()
        (wt / ".git").write_text(f"gitdir: {main_git}\n", encoding="utf-8")
        return wt

    def plan_in(self, root, *lines):
        folder = root / "docs" / "plans" / A
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "PLAN.md").write_text("# Task\n\n## Current checkpoint\n" + "\n".join(lines) + "\n", encoding="utf-8")

    def fire_in(self, root, rows):
        write_rows(self.path, hooked(rows, root))
        return run_gate({"tool_name": "Edit", "tool_input": {"file_path": str(root / "src/a.ts")},
                         "transcript_path": str(self.path), "cwd": str(root)})

    def test_a_differing_plan_copy_is_named(self):
        wt = self.linked()
        self.plan_in(self.repo, APPROVED, "- Status: main copy")
        self.plan_in(wt, "- Approval: not approved")
        rows = [ROUTER, tool("Write", file_path=str(wt / "docs/plans" / A / "TODO.md"), content="x")]
        out = self.fire_in(wt, rows)
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn("differs from the main checkout", out["permissionDecisionReason"])

    def test_identical_copies_keep_the_usual_message(self):
        wt = self.linked()
        self.plan_in(self.repo, "- Approval: not approved")
        self.plan_in(wt, "- Approval: not approved")
        rows = [ROUTER, tool("Write", file_path=str(wt / "docs/plans" / A / "TODO.md"), content="x")]
        out = self.fire_in(wt, rows)
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertNotIn("differs from the main checkout", out["permissionDecisionReason"])


# Adversarial cases the gate already blocks (all pass today and must keep passing)


class AdversarialRegressions(GateCase):

    def test_an_approval_quote_from_before_the_report_was_shown_is_refused(self):
        self.task(A, APPROVED)
        rows = [ROUTER, self.records(A), user("Yes to both"), self.present(A)]
        self.assertEqual(self.decision(rows, "Edit", self.code()), "deny")

    def test_approval_words_only_in_assistant_text_are_refused(self):
        self.task(A, APPROVED)
        for row in (say("The owner said: Yes to both"), say("Yes to both")):
            with self.subTest(row=row):
                rows = [ROUTER, self.records(A), self.present(A), row]
                self.assertEqual(self.decision(rows, "Edit", self.code()), "deny")

    def test_an_approval_line_for_another_revision_is_refused(self):
        # The owner was shown and approved r1's report; the Approval line claims r2 and its report.
        self.task(A, '- Approval: revision r2 approved by the owner 2026-11-03: "Yes to both" (report `reviews/plan-r2.html`).',
                  report="plan-r2.html")
        (self.repo / "docs/plans" / A / "reviews/plan-r1.html").write_text("<!DOCTYPE html><p>r1</p>", encoding="utf-8")
        rows = [ROUTER] + self.approval(A)
        self.assertEqual(self.decision(rows, "Edit", self.code()), "deny")
        # And an r1 approval whose checkpoint has moved on to r2.
        self.task(A, APPROVED, "- Status: r2 drafted, not approved")
        self.assertEqual(self.decision([ROUTER] + self.approval(A), "Edit", self.code()), "deny")

    def test_a_powershell_write_to_a_project_file_without_approval_is_refused(self):
        self.task(A, "- Approval: not approved; revision r1 proposed")
        rows = [ROUTER, self.records(A)]
        for command in ("Set-Content -Path src/a.ts -Value x", "[IO.File]::WriteAllText('src/a.ts', 'x')",
                        f"Set-Content docs/plans/{A}/x.md y; Set-Content src/a.ts x"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(rows, "PowerShell", {"command": command}), "deny")

    def test_an_mcp_write_tool_without_approval_is_refused(self):
        self.task(A, "- Approval: not approved; revision r1 proposed")
        rows = [ROUTER, self.records(A)]
        for name, data in (("mcp__UnityMCP__create_script", {"path": "Assets/Scripts/X.cs"}),
                           ("mcp__x__write_file", {"file_path": str(self.repo / "src/a.ts")}),
                           ("mcp__x__apply_text_edits", {})):
            with self.subTest(name=name):
                self.assertEqual(self.decision(rows, name, data), "deny")

    def test_a_resumed_session_keeps_a_valid_approval_only_for_the_same_report(self):
        self.task(A, APPROVED)
        write_rows(self.sessions / "earlier.jsonl", hooked(self.approval(A), self.repo))
        resumed = [ROUTER, user(f"continue docs/plans/{A}")]
        self.assertIsNone(self.fire(resumed, "Edit", self.code()))
        report = self.repo / "docs/plans" / A / "reviews/plan-r1.html"
        report.write_text("<!DOCTYPE html><p>a changed plan</p>", encoding="utf-8")
        out = self.fire(resumed, "Edit", self.code())
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn("not the report that was approved", out["permissionDecisionReason"])

    def test_an_interrupted_session_whose_last_message_is_the_agents_is_refused(self):
        self.task(A, APPROVED)
        rows = [ROUTER, self.records(A), self.present(A), user("[Request interrupted by user]"),
                say("Understood. Yes to both, so I will apply the plan now.")]
        self.assertEqual(self.decision(rows, "Edit", self.code()), "deny")
        self.assertEqual(self.decision(rows, "Bash", {"command": "git commit -m x"}), "deny")


# Reply marks: an approval keeps its evidence however many prompts follow it


class ReplyMarkRegressions(GateCase):

    def handbacks(self, count, digest):
        shown = f"docs/plans/{A}/reviews/plan-r1.html"
        return [hook_context("UserPromptSubmit", f"workflow-axa report at owner reply: {shown} sha256={digest}")] * count

    def test_an_approval_survives_many_later_hand_backs(self):
        """Evidence: FINDINGS (gate reply cap). UserPromptSubmit fires on every subagent hand-back and records a
        reply mark each time. The gate kept only the last 50 marks per report, so after 50 hand-backs the mark
        recorded at the owner's answer was gone and the approved task's edits were refused with "no fingerprint of
        plan-r1.html was recorded with that answer". Expected: the edit is allowed."""
        self.task(A, APPROVED)
        report = self.repo / "docs/plans" / A / "reviews/plan-r1.html"
        rows = hooked([ROUTER] + self.approval(A), self.repo) + [user("multiple choice please")] + self.handbacks(60, sha(report))
        self.assertIsNone(self.fire(rows, "Edit", self.code(), hooks=False))

    def test_the_mark_at_the_answer_still_decides_after_many_hand_backs(self):
        """Only the first mark after the owner's answer counts. Later hand-back marks with the current report bytes
        must not repair an answer given while a different report was on disk. With the 50-mark cap the answer's own
        mark was dropped and a later hand-back mark took its place, so this edit was allowed. Expected: refused."""
        self.task(A, APPROVED)
        report = self.repo / "docs/plans" / A / "reviews/plan-r1.html"
        approved = hooked([ROUTER] + self.approval(A), self.repo)
        stale = [row for row in approved if "report at owner reply" not in json.dumps(row)]
        self.assertLess(len(stale), len(approved))  # the helper did record a reply mark at the answer
        rows = stale + self.handbacks(1, "0" * 64) + self.handbacks(60, sha(report))
        out = self.fire(rows, "Edit", self.code(), hooks=False)
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn("changed between its presentation and that answer", out["permissionDecisionReason"])


if __name__ == "__main__":
    unittest.main()
