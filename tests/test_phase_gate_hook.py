"""The phase gate: after /workflow, code edits and git writes need the current task's recorded approval, quoting the
user's real words (D1 of 2026-11-03-audit-hardening). Task records stay writable; loading a phase grants nothing."""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks/phase_gate.py"
ROUTER = {"type": "user", "message": {"role": "user", "content":
          "<command-message>workflow</command-message>\n<command-name>/workflow</command-name>\n<command-args>bug</command-args>"}}
APPROVED = '- Approval: revision r1 approved by the owner 2026-11-03: "Yes to both" (report `reviews/plan-r1.html`).'
TASK = "2026-11-03-fix"


def skill(name):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Skill", "input": {"skill": name}}]}}


def say(text):
    return {"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}}


def user(content, **extra):
    return {"type": "user", "message": {"role": "user", "content": content}, **extra}


def tool(name, **data):
    return {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": name, "input": data}]}}


def hook_context(event, *lines):
    """A host-recorded hook context entry, as Claude Code stores the gate's PostToolUse/UserPromptSubmit output."""
    return {"type": "attachment", "attachment": {"type": "hook_additional_context", "hookEvent": event, "content": list(lines)}}


REPORT_PATH = re.compile(r'(?:[A-Za-z]:)?[^\s"\'`]*?docs/plans/[\w.-]+/(?:reviews/)?[\w.-]+\.html')


def hooked(rows, root):
    """The rows as the host records them while the gate's fingerprint hooks run: a report the agent names is first read
    (a fingerprint before the presentation), and each owner answer gets the presented reports' current fingerprints."""
    out, shown = [], {}
    for row in rows:
        content = (row.get("message") or {}).get("content")
        if row.get("type") == "assistant" and isinstance(content, list):
            text = " ".join(str(b.get("text", "")) for b in content if isinstance(b, dict) and b.get("type") == "text")
            for found in REPORT_PATH.findall(text.replace("\\", "/")):
                path = Path(found) if re.match(r'^(?:[A-Za-z]:|/)', found) else Path(root) / found
                if path.is_file():
                    rel = "docs/plans/" + found.split("docs/plans/", 1)[1]
                    shown[rel] = path
                    out.append(hook_context("PostToolUse", f"workflow-axa report fingerprint: {rel} sha256={sha(path)}"))
        out.append(row)
        typed = row.get("type") == "user" and not row.get("isSidechain") and "toolUseResult" not in row and (
            isinstance(content, str) or any(isinstance(b, dict) and b.get("type") == "text" for b in content or []))
        answered = row.get("type") == "user" and isinstance(row.get("toolUseResult"), dict) and "answers" in row["toolUseResult"]
        if (typed or answered) and shown:
            out.append(hook_context("UserPromptSubmit" if typed else "PostToolUse",
                                    *(f"workflow-axa report at owner reply: {rel} sha256={sha(path)}" for rel, path in shown.items()
                                      if path.is_file())))
    return out


def sha(path):
    import hashlib
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


CACHE = tempfile.TemporaryDirectory()  # the hook's transcript cache, kept out of the system temp folder


def tearDownModule():
    CACHE.cleanup()


def run_hook(event, process_cwd=None) -> dict | None:
    result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input=json.dumps(event),
                            capture_output=True, text=True, encoding="utf-8", cwd=process_cwd,
                            env={**os.environ, "WORKFLOW_AXA_GATE_CACHE": CACHE.name})
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)["hookSpecificOutput"] if result.stdout.strip() else None


class PhaseGateHookTests(unittest.TestCase):
    """Sessions without a task folder (Hooqd and r24 retros), rule-maker, the report guides and the wiring."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "session.jsonl"

    def fire(self, rows, tool_name, tool_input, cwd="D:\\Hooqd"):
        self.path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        return run_hook({"tool_name": tool_name, "tool_input": tool_input, "transcript_path": str(self.path), "cwd": cwd})

    def test_hooqd_session_is_blocked_before_code_and_push(self):
        # Hooqd retro: investigation, "Let's do that, push when done", then edits and a push with no phase loaded.
        rows = [ROUTER, say("Waiting on you: should I start the fix as a workflow task?"),
                {"type": "user", "message": {"role": "user", "content": "Let's do that, push when done"}}]
        edit = self.fire(rows, "Edit", {"file_path": "D:\\Hooqd\\frontend\\packages\\api\\src\\transport.ts"})
        self.assertEqual(edit["permissionDecision"], "deny")
        self.assertIn("workflow-clarify", edit["permissionDecisionReason"])
        push = self.fire(rows, "Bash", {"command": "cd /d/Hooqd && git fetch -q && git push -q origin master"})
        self.assertIn("git push", push["permissionDecisionReason"])
        # The Hooqd session also edited source from Bash: sed -i and a Python heredoc writing the file.
        for command in ("cd /d/Hooqd/frontend; sed -i 's/a/b/' apps/operator/src/x.tsx",
                        "cd /d/Hooqd/frontend; python - <<'EOF'\np='packages/api/src/transport.ts'\nopen(p,'w').write(s)\nEOF"):
            with self.subTest(command=command):
                self.assertEqual(self.fire(rows, "Bash", {"command": command})["permissionDecision"], "deny")

    def test_a_project_inside_temp_is_still_gated(self):
        # r24 live check: the project lived under AppData/Local/Temp, and `sed -i` there slipped through.
        project = "C:/Users/x/AppData/Local/Temp/claude/s/scratchpad/r22-short"
        sed = {"command": f'cd "{project}" && sed -i "s/Delete/Erase/" index.html app.js'}
        self.assertEqual(self.fire([ROUTER], "Bash", sed, cwd=project)["permissionDecision"], "deny")
        edit = {"file_path": project + "/index.html"}
        self.assertEqual(self.fire([ROUTER], "Edit", edit, cwd=project)["permissionDecision"], "deny")

    def test_allowed_cases(self):
        rows = [ROUTER]
        for tool_name, data in (("Write", {"file_path": "D:/Hooqd/docs/plans/2026-11-03-upload-timeout/PLAN.md"}),
                                ("Write", {"file_path": "D:/Hooqd/.artifacts/checks/x.log"}),
                                ("Write", {"file_path": "C:/Users/x/AppData/Local/Temp/scratch/note.md"}),
                                ("Bash", {"command": "cd C:/Users/x/AppData/Local/Temp/scratch && sed -i 's/a/b/' n.txt"}),
                                ("Bash", {"command": "sed -i 's/a/b/' docs/plans/t/TODO.md"}),
                                ("Bash", {"command": "git status --short && git diff"}),
                                ("Read", {"file_path": "D:/Hooqd/backend/app.php"})):
            with self.subTest(tool=tool_name, data=data):
                self.assertIsNone(self.fire(rows, tool_name, data))
        self.assertIsNone(self.fire([say("plain session")], "Edit", {"file_path": "D:/Hooqd/frontend/src/a.ts"}))

    def test_a_drive_letter_path_never_resolves_into_the_process_folder(self):
        # WSL run (Python 3.12): pathlib treats "D:/..." as relative on POSIX, so the worktree search walked up to
        # ".", the hook's own folder, found its .git there, and task records counted as project code.
        process = Path(self.tmp.name) / "checkout"
        (process / ".git").mkdir(parents=True)
        self.path.write_text(json.dumps(ROUTER), encoding="utf-8")
        for target in ("D:/Hooqd/docs/plans/2026-11-03-upload-timeout/PLAN.md", "D:/Hooqd/.artifacts/checks/x.log"):
            with self.subTest(target=target):
                event = {"tool_name": "Write", "tool_input": {"file_path": target}, "transcript_path": str(self.path),
                         "cwd": "D:\\Hooqd"}
                self.assertIsNone(run_hook(event, process_cwd=str(process)))

    def test_rule_maker_may_write_rule_files_only(self):
        # D20: rule-maker writes the rules-checked line into AGENTS.md during setup or audit, without a phase.
        rows = [ROUTER, skill("workflow-axa:rule-maker")]
        for tool_name, data in (("Edit", {"file_path": "D:/Hooqd/AGENTS.md"}),
                                ("Edit", {"file_path": "D:/Hooqd/.claude/rules/frontend.md"}),
                                ("Bash", {"command": "cd /d/Hooqd && sed -i 's/1.7.0/1.8.0/' AGENTS.md"})):
            with self.subTest(data=data):
                self.assertIsNone(self.fire(rows, tool_name, data))
        self.assertEqual(self.fire(rows, "Edit", {"file_path": "D:/Hooqd/src/a.ts"})["permissionDecision"], "deny")
        both = {"command": "cd /d/Hooqd && sed -i 's/1.7.0/1.8.0/' AGENTS.md src/a.ts"}
        self.assertEqual(self.fire(rows, "Bash", both)["permissionDecision"], "deny")  # judged per file
        self.assertEqual(self.fire([ROUTER], "Edit", {"file_path": "D:/Hooqd/AGENTS.md"})["permissionDecision"], "deny")

    def test_report_render_waits_for_the_report_guides(self):
        # Round v3: in all four worktrees the report guides were read only after the Stop hook asked, so reports
        # were rendered (and in r22 went stale) before the rules for writing them were read.
        render = {"command": "python -X utf8 -I D:/workflow-axa/skills/codebase-map/scripts/render_report.py --input p.json --output docs/plans/t/reviews/p.html"}
        rows = [ROUTER, skill("workflow-axa:workflow-specify")]
        denied = self.fire(rows, "Bash", render)
        self.assertEqual(denied["permissionDecision"], "deny")
        self.assertIn("simple-english/SKILL.md", denied["permissionDecisionReason"])
        self.assertIn("codebase-map/TASK-REPORT.md", denied["permissionDecisionReason"])
        read = lambda rel: {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read",
                            "input": {"file_path": f"D:/workflow-axa/skills/{rel}"}}]}}
        rows += [read("simple-english/SKILL.md"), read("codebase-map/TASK-REPORT.md"), read("codebase-map/UI-FLOW.md")]
        self.assertIsNone(self.fire(rows, "Bash", render))
        self.assertIsNone(self.fire([say("plain session")], "Bash", render))
        # E5: the router's fallback, reading the phase SKILL.md whole, loads the phase like the skill tool does.
        whole = [ROUTER, read("workflow-specify/SKILL.md")]
        self.assertEqual(self.fire(whole, "Bash", render)["permissionDecision"], "deny")
        self.assertEqual(self.fire(whole, "PowerShell", render)["permissionDecision"], "deny")

    def test_bad_input_is_ignored(self):
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HOOK)], input="nope", capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stdout), (0, ""))

    def test_hooks_json_wires_it_before_edits_shells_and_mcp_writes(self):
        # E6: the PowerShell tool and MCP write tools were outside the matcher, so the gate never ran for them.
        data = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
        entry = data["hooks"]["PreToolUse"][0]
        self.assertIn("${CLAUDE_PLUGIN_ROOT}/hooks/phase_gate.py", entry["hooks"][0]["command"])
        matcher = re.compile(entry["matcher"])
        for name in ("Edit", "Write", "MultiEdit", "NotebookEdit", "Bash", "PowerShell", "mcp__UnityMCP__create_script",
                     "mcp__UnityMCP__manage_script", "mcp__trello__trelloWriteCard", "mcp__x__apply_text_edits",
                     "mcp__claude_ai_Claude_Docs__update", "mcp__x__delete_file", "mcp__x__import_model",
                     "mcp__UnityMCP__execute_code"):
            with self.subTest(name=name):
                self.assertTrue(matcher.fullmatch(name))
        for name in ("Read", "Glob", "Grep", "Skill", "mcp__trello__trelloReadCard", "mcp__x__get_sha"):
            with self.subTest(name=name):
                self.assertFalse(matcher.fullmatch(name))


class ApprovalGateTests(unittest.TestCase):
    """Permission comes from the current task's PLAN.md Approval line and the user's quoted words (E1-E8, D1)."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.repo = self.base / "repo"
        (self.repo / ".git").mkdir(parents=True)
        self.sessions = self.base / "sessions"
        self.sessions.mkdir()
        self.path = self.sessions / "current.jsonl"
        self.code = str(self.repo / "src" / "a.ts")

    def task(self, name=TASK, *lines, root=None, report="plan-r1.html"):
        folder = (root or self.repo) / "docs" / "plans" / name
        folder.mkdir(parents=True, exist_ok=True)
        checkpoint = "\n".join(lines)
        (folder / "PLAN.md").write_text(f"# Task\n\n## Current checkpoint\n- Status: x\n{checkpoint}\n\n## Goal\nx\n",
                                        encoding="utf-8")
        if report:  # the HTML plan report workflow-specify renders
            (folder / "reviews").mkdir(exist_ok=True)
            (folder / "reviews" / report).write_text("<!DOCTYPE html>", encoding="utf-8")
        return folder

    def records(self, name=TASK, root=None):
        """The session writes this task's records, which makes it the current task."""
        return tool("Write", file_path=str((root or self.repo) / "docs/plans" / name / "TODO.md"), content="x")

    def present(self, name=TASK):
        """The agent names the plan report to the user: approval words count only after this."""
        return say(f"Plan report: {self.repo / 'docs/plans' / name / 'reviews/plan-r1.html'}. Approve?")

    def approval(self, words, name=TASK):
        return [self.records(name), self.present(name), user(words)]

    def session(self, path, rows, hooks=True):
        path.write_text("\n".join(json.dumps(row) for row in (hooked(rows, self.repo) if hooks else rows)), encoding="utf-8")

    def fire(self, rows, tool_name, data, cwd=None, transcript=True, hooks=True):
        self.session(self.path, rows, hooks)
        event = {"tool_name": tool_name, "tool_input": data, "cwd": str(cwd or self.repo)}
        if transcript:
            event["transcript_path"] = str(self.path)
        return run_hook(event)

    def decision(self, *args, **kwargs):
        out = self.fire(*args, **kwargs)
        return out and out["permissionDecision"]

    def approved_rows(self):
        self.task(TASK, APPROVED)
        return [ROUTER] + self.approval("Yes to both")

    # Legitimate routes

    def test_an_approved_task_allows_code_edits_shell_writes_and_git(self):
        rows = self.approved_rows()
        for tool_name, data in (("Edit", {"file_path": self.code}),
                                ("Write", {"file_path": self.code}),
                                ("Bash", {"command": "echo x > src/a.ts"}),
                                ("Bash", {"command": "git commit -m x && git push"}),
                                ("PowerShell", {"command": "Set-Content -Path src/a.ts -Value x"}),
                                ("mcp__UnityMCP__create_script", {"path": "Assets/Scripts/X.cs"})):
            with self.subTest(tool=tool_name, data=data):
                self.assertIsNone(self.fire(rows, tool_name, data))

    def test_the_quote_must_be_the_whole_answer_with_conditions(self):
        self.task(TASK, APPROVED)
        for said in (user([{"type": "text", "text": "Yes  to both!"}]), user("yes to both")):
            with self.subTest(said=said):
                rows = [ROUTER, self.records(), self.present(), said]
                self.assertIsNone(self.decision(rows, "Edit", {"file_path": self.code}))
        # Review H1: a slash command's arguments are not consent.
        command = user("<command-message>workflow</command-message>\n<command-name>/workflow</command-name>\n"
                       "<command-args>yes to both</command-args>")
        self.assertEqual(self.decision([ROUTER, self.records(), self.present(), command], "Edit",
                                       {"file_path": self.code}), "deny")

    def test_waived_and_legacy_revisions_count(self):
        for line in ('- Approval: waived for revision r2 by the owner: "skip the report"',
                     '- Approval (gate two): legacy single-gate approval, revision r1: "skip the report"'):
            with self.subTest(line=line):
                self.task(TASK, line)
                rows = [ROUTER] + self.approval("skip the report")
                self.assertIsNone(self.decision(rows, "Edit", {"file_path": self.code}))

    def test_records_and_output_stay_writable_before_approval(self):
        self.task(TASK, "- Approval: not approved; revision r1 proposed")
        rows = [ROUTER, skill("workflow-axa:workflow-clarify"), self.records()]
        plan = self.repo / "docs/plans" / TASK
        for tool_name, data in (("Write", {"file_path": str(plan / "PLAN.md")}),
                                ("Edit", {"file_path": str(plan / "reviews/plan-r1.json")}),
                                ("Write", {"file_path": str(self.repo / ".artifacts" / TASK / "run.log")}),
                                ("Bash", {"command": f"echo x > docs/plans/{TASK}/notes.md"}),
                                ("Bash", {"command": f"python -X utf8 -I D:/x/record.py set-line docs/plans/{TASK}/PLAN.md a b"}),
                                ("PowerShell", {"command": f"Set-Content -Path docs/plans/{TASK}/x.md -Value y"}),
                                ("Bash", {"command": "echo x > /dev/null; ls 2> err.log; ls 2>&1 | tee /tmp/x.log"}),
                                ("Bash", {"command": "git status && git diff && git log -1 && git checkout main"}),
                                ("PowerShell", {"command": "Get-Content src/a.ts; Remove-Item $env:TEMP\\x.txt"})):
            with self.subTest(tool=tool_name, data=data):
                self.assertIsNone(self.fire(rows, tool_name, data))

    def test_a_resumed_session_finds_the_quote_in_an_earlier_transcript(self):
        self.task(TASK, APPROVED)
        self.session(self.sessions / "earlier.jsonl", self.approval("Yes to both"))
        rows = [ROUTER, user(f"continue docs/plans/{TASK}")]
        self.assertIsNone(self.decision(rows, "Edit", {"file_path": self.code}))
        # A subagent's transcript (a subfolder, sidechain prompts written by the agent) is not the user's word.
        (self.sessions / "earlier.jsonl").unlink()
        agents = self.sessions / "s1" / "subagents"
        agents.mkdir(parents=True)
        (agents / "agent-1.jsonl").write_text(json.dumps(user("Yes to both", isSidechain=True)), encoding="utf-8")
        (self.sessions / "other.jsonl").write_text(json.dumps(user("Yes to both", isSidechain=True)), encoding="utf-8")
        self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")

    def earlier(self, *later):
        """An earlier session of this project: the plan shown, the owner's approval, then any later messages."""
        rows = self.approval("Yes to both") + [user(words) for words in later]
        self.session(self.sessions / "earlier.jsonl", rows)

    def test_inherited_approval_stops_at_a_later_withdrawal_restriction_stop_or_change(self):
        # P1 live test: approval survives a new session only for the unchanged report and conditions.
        self.task(TASK, APPROVED)
        resumed = [ROUTER, user(f"continue docs/plans/{TASK}")]
        edit = {"file_path": self.code}
        for later, decision, why in ((("looks good",), None, ""),
                                     (("I withdraw that approval",), "deny", "withdraws it"),
                                     (("but nothing in src/b.ts",), "deny", "may restrict it"),
                                     (("stop",), None, "")):  # the resumed session asks to continue
            with self.subTest(later=later):
                self.earlier(*later)
                out = self.fire(resumed, "Edit", edit)
                self.assertEqual(out and out["permissionDecision"], decision)
                if why:
                    self.assertIn(why, out["permissionDecisionReason"])
        self.earlier("stop")
        out = self.fire([ROUTER, user(f"show the state of docs/plans/{TASK} please")], "Edit", edit)
        self.assertIn("nobody has asked to continue", out["permissionDecisionReason"])
        # A restriction the checkpoint records carries over with the approval.
        self.task(TASK, APPROVED, '- Owner restriction, 2026-11-03: "but nothing in src/b.ts"')
        self.earlier("but nothing in src/b.ts")
        self.assertIsNone(self.fire(resumed, "Edit", edit))
        # Report identity is its content (SHA-256), not its timestamp.
        self.earlier()
        report = self.repo / "docs/plans" / TASK / "reviews/plan-r1.html"
        stamp = report.stat()
        report.write_text("<!DOCTYPE html><p>another plan</p>", encoding="utf-8")
        os.utime(report, ns=(stamp.st_atime_ns, stamp.st_mtime_ns))  # changed content, unchanged timestamp
        out = self.fire(resumed, "Edit", edit)
        self.assertIn("not the report that was approved", out["permissionDecisionReason"])
        report.write_text("<!DOCTYPE html>", encoding="utf-8")  # the approved bytes again, with a newer timestamp
        later = (self.sessions / "earlier.jsonl").stat().st_mtime + 60
        os.utime(report, (later, later))
        self.assertIsNone(self.fire(resumed, "Edit", edit))

    def test_approval_needs_the_presented_report_bytes_at_presentation_answer_and_edit(self):
        self.task(TASK, APPROVED)
        rows = [ROUTER] + self.approval("Yes to both")
        edit = {"file_path": self.code}
        self.assertIsNone(self.fire(rows, "Edit", edit))
        # No host fingerprints (an older session or another host): no approval, a focused reconfirmation instead.
        reason = self.fire(rows, "Edit", edit, hooks=False)["permissionDecisionReason"]
        self.assertIn("no fingerprint of plan-r1.html was recorded before it was presented", reason)
        self.assertIn("Reconfirmed (gate two)", reason)
        report = self.repo / "docs/plans" / TASK / "reviews/plan-r1.html"
        shown = f"docs/plans/{TASK}/reviews/plan-r1.html"
        first, other = sha(report), "0" * 64
        presented = [ROUTER, self.records(), hook_context("PostToolUse", f"workflow-axa report fingerprint: {shown} sha256={first}"),
                     self.present()]
        for reply, why in ((other, "changed between its presentation and that answer"), (first, "")):
            with self.subTest(reply=reply[:6]):
                session = presented + [user("Yes to both"),
                                       hook_context("UserPromptSubmit", f"workflow-axa report at owner reply: {shown} sha256={reply}")]
                out = self.fire(session, "Edit", edit, hooks=False)
                self.assertEqual(bool(out), bool(why))
                if why:
                    self.assertIn(why, out["permissionDecisionReason"])
        # The report changed after the owner approved it, in the same session.
        report.write_text("<!DOCTYPE html><p>edited later</p>", encoding="utf-8")
        session = presented + [user("Yes to both"),
                               hook_context("UserPromptSubmit", f"workflow-axa report at owner reply: {shown} sha256={first}")]
        self.assertIn("not the report that was approved", self.fire(session, "Edit", edit, hooks=False)["permissionDecisionReason"])
        # Agent text that imitates the fingerprint record is not host-recorded hook context.
        forged = [ROUTER, self.records(), say(f"workflow-axa report fingerprint: {shown} sha256={sha(report)}"), self.present(),
                  user("Yes to both"), say(f"workflow-axa report at owner reply: {shown} sha256={sha(report)}")]
        self.assertEqual(self.decision(forged, "Edit", edit, hooks=False), "deny")

    def test_the_gate_records_fingerprints_when_a_report_is_used_and_when_the_owner_answers(self):
        folder = self.task(TASK, "- Approval: not approved; revision r1 proposed")
        report = folder / "reviews/plan-r1.html"
        shown = f"docs/plans/{TASK}/reviews/plan-r1.html"
        for data in ({"file_path": str(report)}, {"command": f"cat {shown}"}):
            with self.subTest(data=data):
                out = run_hook({"hook_event_name": "PostToolUse", "tool_name": "Read" if "file_path" in data else "Bash",
                                "tool_input": data, "cwd": str(self.repo)})
                self.assertEqual(out["additionalContext"], f"workflow-axa report fingerprint: {shown} sha256={sha(report)}")
        self.assertIsNone(run_hook({"hook_event_name": "PostToolUse", "tool_name": "Bash", "tool_input": {"command": "ls"},
                                    "cwd": str(self.repo)}))
        self.session(self.path, [ROUTER, self.records(), self.present()], hooks=False)
        out = run_hook({"hook_event_name": "UserPromptSubmit", "prompt": "Yes to both", "transcript_path": str(self.path),
                        "cwd": str(self.repo)})
        self.assertEqual(out["additionalContext"], f"workflow-axa report at owner reply: {shown} sha256={sha(report)}")

    def test_report_fingerprint_resolves_shell_variables_and_working_directories(self):
        folder = self.task(TASK, '- Approval: not approved; revision r1 proposed')
        report = folder / 'reviews/plan-r1.html'
        rel = f'docs/plans/{TASK}/reviews/plan-r1.html'
        task = f'docs/plans/{TASK}'
        good = (
            ('Bash', f'cat {rel}'),
            ('Bash', f'T={task}; head -c 3000 $T/reviews/plan-r1.html'),
            ('Bash', f'T="{task}"; cat "$T/reviews/plan-r1.html"'),
            ('Bash', f'cd {task} && cat reviews/plan-r1.html'),
            ('Bash', f'R="{self.repo.as_posix()}"; cd "$R"; T="{task}"; cat "$T/reviews/plan-r1.html"'),
            ('PowerShell', f"$t = '{task}'; Get-Content \"$t/reviews/plan-r1.html\""),
            # Audit 2026-11-05: forms the literal capture handled before the repair, and a relative path in code.
            ('Bash', f"python -c \"print(open('{rel}', encoding='utf-8').read()[:4000])\""),
            ('Bash', f"python - <<'EOF'\nprint(open('{rel}', encoding='utf-8').read())\nEOF"),
            ('Bash', f'bash -c "cat {rel}"'),
            ('Bash', f'cd {task}/reviews && python -c "print(open(\'plan-r1.html\').read())"'),
        )
        for tool_name, command in good:
            with self.subTest(tool=tool_name, command=command):
                out = run_hook({'hook_event_name': 'PostToolUse', 'tool_name': tool_name,
                                'tool_input': {'command': command}, 'cwd': str(self.repo)})
                self.assertIsNotNone(out)
                self.assertEqual(out['additionalContext'],
                                 f'workflow-axa report fingerprint: {rel} sha256={sha(report)}')
        for command in (f'cat $UNSET/reviews/plan-r1.html',
                        f'cd "$UNSET" && cat {rel}',
                        f'cat ../../outside/{rel}',
                        f'cat {task}/reviews/missing.html',
                        f'cd "$UNSET" && python -c "print(open(\'plan-r1.html\').read())"',
                        f"python - <<'EOF'\nprint(open('$UNSET/reviews/plan-r1.html').read())\nEOF"):
            with self.subTest(unresolved=command):
                self.assertIsNone(run_hook({'hook_event_name': 'PostToolUse', 'tool_name': 'Bash',
                                            'tool_input': {'command': command}, 'cwd': str(self.repo)}))

    def test_variable_path_report_approval_allows_edits_and_resumes_only_in_scope(self):
        folder = self.task(TASK, APPROVED)
        report = folder / 'reviews/plan-r1.html'
        manifest = json.dumps({'schema_version': 1, 'sources': [], 'write_paths': ['src/a.ts']})
        report.write_text(f'<!DOCTYPE html><script type="application/json" id="report-manifest">{manifest}</script>',
                          encoding='utf-8')
        read_cmd = f'T=docs/plans/{TASK}; cat "$T/reviews/plan-r1.html"'
        record = run_hook({'hook_event_name': 'PostToolUse', 'tool_name': 'Bash',
                           'tool_input': {'command': read_cmd}, 'cwd': str(self.repo)})
        self.assertIsNotNone(record)
        rows = [ROUTER, self.records(), tool('Bash', command=read_cmd),
                hook_context('PostToolUse', record['additionalContext']), self.present()]
        self.session(self.path, rows, hooks=False)
        reply = run_hook({'hook_event_name': 'UserPromptSubmit', 'prompt': 'Yes to both',
                          'transcript_path': str(self.path), 'cwd': str(self.repo)})
        self.assertIsNotNone(reply)
        rows += [user('Yes to both'), hook_context('UserPromptSubmit', reply['additionalContext'])]
        self.assertIsNone(self.fire(rows, 'Edit', {'file_path': self.code}, hooks=False))
        self.assertEqual(self.decision(rows, 'Edit', {'file_path': str(self.repo / 'tests/new.py')}, hooks=False), 'deny')
        self.session(self.sessions / 'previous.jsonl', rows, hooks=False)
        resumed = [ROUTER, user(f'Continue docs/plans/{TASK}')]
        self.assertIsNone(self.fire(resumed, 'Edit', {'file_path': self.code}, hooks=False))
        self.assertEqual(self.decision(resumed, 'Edit', {'file_path': str(self.repo / 'tests/new.py')}, hooks=False), 'deny')

    def test_a_mentioned_report_cannot_approve_bytes_the_owner_was_not_shown(self):
        # Audit 2026-11-05: a path merely mentioned in a command (here inside an echo) records the file's real bytes.
        # If the report then changes in a way no hook sees, the answer-time fingerprint differs and approval fails.
        folder = self.task(TASK, APPROVED)
        report = folder / 'reviews/plan-r1.html'
        mention = f'echo "next: docs/plans/{TASK}/reviews/plan-r1.html"'
        record = run_hook({'hook_event_name': 'PostToolUse', 'tool_name': 'Bash',
                           'tool_input': {'command': mention}, 'cwd': str(self.repo)})
        self.assertIsNotNone(record)  # a mention records the current bytes, as the literal capture always did
        report.write_text('<!DOCTYPE html><p>a different plan, written by a script no hook saw</p>', encoding='utf-8')
        rows = [ROUTER, self.records(), tool('Bash', command=mention),
                hook_context('PostToolUse', record['additionalContext']), self.present()]
        self.session(self.path, rows, hooks=False)
        reply = run_hook({'hook_event_name': 'UserPromptSubmit', 'prompt': 'Yes to both',
                          'transcript_path': str(self.path), 'cwd': str(self.repo)})
        rows += [user('Yes to both'), hook_context('UserPromptSubmit', reply['additionalContext'])]
        out = self.fire(rows, 'Edit', {'file_path': self.code}, hooks=False)
        self.assertEqual(out['permissionDecision'], 'deny')
        self.assertIn('changed between its presentation and that answer', out['permissionDecisionReason'])

    def test_the_approved_reports_write_paths_bound_file_writes(self):
        folder = self.task(TASK, APPROVED)
        manifest = json.dumps({"schema_version": 1, "sources": [], "write_paths": ["src/a.ts", "docs/"]})
        (folder / "reviews/plan-r1.html").write_text(
            f'<!DOCTYPE html><script type="application/json" id="report-manifest">{manifest}</script>', encoding="utf-8")
        rows = [ROUTER] + self.approval("Yes to both")
        for tool_name, data in (("Edit", {"file_path": self.code}),
                                ("Write", {"file_path": str(self.repo / "docs/guide/x.md")}),
                                ("Bash", {"command": "echo x > src/a.ts"}),
                                ("Write", {"file_path": str(folder / "FINDINGS.md")})):  # task records stay writable
            with self.subTest(data=data):
                self.assertIsNone(self.fire(rows, tool_name, data))
        for tool_name, data in (("Edit", {"file_path": str(self.repo / "tests/test_a.py")}),
                                ("Bash", {"command": "echo x > tests/new_test.py"}),
                                ("Edit", {"file_path": str(self.repo / "src/b.ts")})):
            with self.subTest(data=data):
                out = self.fire(rows, tool_name, data)
                self.assertEqual(out["permissionDecision"], "deny")
                self.assertIn("outside the files the approved plan may change (src/a.ts, docs/)", out["permissionDecisionReason"])
        self.assertIsNone(self.fire(rows, "Bash", {"command": "git commit -m x"}))  # git stays approval-only
        # A report without write paths keeps approval-only behaviour; a malformed list asks for a re-rendered plan.
        (folder / "reviews/plan-r1.html").write_text("<!DOCTYPE html>", encoding="utf-8")
        self.assertIsNone(self.fire([ROUTER] + self.approval("Yes to both"), "Edit", {"file_path": str(self.repo / "tests/t.py")}))
        bad = json.dumps({"schema_version": 1, "write_paths": "src/"})
        (folder / "reviews/plan-r1.html").write_text(f'<script type="application/json" id="report-manifest">{bad}</script>', encoding="utf-8")
        out = self.fire([ROUTER] + self.approval("Yes to both"), "Edit", {"file_path": self.code})
        self.assertIn("unreadable form", out["permissionDecisionReason"])

    def test_an_earlier_approval_of_another_revision_does_not_carry_over(self):
        self.task(TASK, '- Approval: revision r2 approved by the owner 2026-11-03: "Yes to both" (report `reviews/plan-r2.html`).',
                  report="plan-r2.html")
        self.earlier()  # the owner approved r1's report
        self.assertEqual(self.decision([ROUTER, user(f"continue docs/plans/{TASK}")], "Edit", {"file_path": self.code}), "deny")

    def test_a_resumed_task_is_reconfirmed_on_its_own_line_and_keeps_the_original_quote(self):
        again = '- Reconfirmed (gate two): r1, 2026-11-04: "Still yes to both"'
        edit = {"file_path": self.code}
        rows = [ROUTER, self.records(), self.present(), user("Still yes to both")]
        # No earlier session holds the answer: the gate asks for a focused reconfirmation of the same report.
        self.task(TASK, APPROVED)
        reason = self.fire(rows, "Edit", edit)["permissionDecisionReason"]
        self.assertIn("Reconfirmed (gate two): r1", reason)
        self.assertIn(f"docs/plans/{TASK}/reviews/plan-r1.html", reason)
        self.assertIn("keep this Approval line unchanged", reason)
        folder = self.task(TASK, APPROVED, again)
        self.assertIsNone(self.fire(rows, "Edit", edit))
        self.assertIn(APPROVED, (folder / "PLAN.md").read_text(encoding="utf-8"))
        # It needs the report shown again in this session, the owner's own words, and the same revision.
        self.assertEqual(self.decision([ROUTER, self.records(), user("Still yes to both")], "Edit", edit), "deny")
        for line in ('- Reconfirmed (gate two): r1, 2026-11-04: "Yes, go ahead"',
                     '- Reconfirmed (gate two): r2, 2026-11-04: "Still yes to both"'):
            with self.subTest(line=line):
                self.task(TASK, APPROVED, line)
                self.assertEqual(self.decision(rows, "Edit", edit), "deny")

    def test_a_resumed_session_is_pointed_at_its_existing_task(self):
        # P1 live test: the first block told a resumed session to start workflow-clarify.
        self.task(TASK, APPROVED)
        reason = self.fire([ROUTER, user("Continue the fix task.")], "Edit", {"file_path": self.code})["permissionDecisionReason"]
        self.assertIn(f"Existing tasks here: {TASK}", reason)
        self.assertIn("update its records first", reason)

    def test_a_listed_lightweight_file_is_allowed_and_only_that_file(self):
        self.task(TASK, "- Approval: not required", "- Lightweight edit: `src/a.ts`, README.md — fix a comment typo",
                  report=None)  # a lightweight edit needs no plan report
        rows = [ROUTER, self.records()]
        self.assertIsNone(self.decision(rows, "Edit", {"file_path": self.code}))
        self.assertIsNone(self.decision(rows, "Edit", {"file_path": str(self.repo / "README.md")}))
        self.assertEqual(self.decision(rows, "Edit", {"file_path": str(self.repo / "src/b.ts")}), "deny")
        self.assertEqual(self.decision(rows, "Bash", {"command": "git commit -m typo"}), "deny")

    # E1: a phase name is not approval

    def test_loading_a_phase_grants_nothing(self):
        self.task(TASK, "- Approval: not approved; revision r1 proposed")
        for phase in ("workflow-clarify", "workflow-specify", "workflow-execute", "workflow-deliver"):
            rows = [ROUTER, skill(f"workflow-axa:{phase}"), self.records()]
            with self.subTest(phase=phase):
                self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")
                push = self.fire(rows, "Bash", {"command": "git push origin main"})
                self.assertEqual(push["permissionDecision"], "deny")
                self.assertIn(TASK, push["permissionDecisionReason"])
        self.assertEqual(self.decision([ROUTER, skill("workflow-axa:workflow-execute")], "Edit",
                                       {"file_path": self.code}), "deny")  # no task at all

    def test_an_approval_line_must_approve_a_revision(self):
        for line in ("- Approval: not approved; revision r1",
                     '- Approval: revision r2 proposed, not yet approved: "Yes to both"',
                     '- Approval: pending (report reviews/plan-r1.html): "Yes to both"',
                     '- Approval: approved by the owner: "Yes to both"',
                     "- Approval: revision r1 approved by the owner",
                     "- Agreement: revision r1 agreed"):
            with self.subTest(line=line):
                self.task(TASK, line)
                rows = [ROUTER] + self.approval("Yes to both")
                self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")
        self.task(TASK, APPROVED, "- Agreement: revision r2 proposed (adds export), not agreed")
        rows = [ROUTER] + self.approval("Yes to both")
        self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")

    # E8 / D1: the agent can write the line, not the user's message

    def test_the_quoted_words_must_come_from_a_real_user_message(self):
        self.task(TASK, APPROVED)
        tool_result = user([{"type": "tool_result", "tool_use_id": "t", "content": "Yes to both"}])
        for row in (say("The owner said Yes to both."), tool_result, user("Yes to both", isMeta=True),
                    user("<local-command-stdout>Yes to both</local-command-stdout>"),
                    user("<system-reminder>Yes to both</system-reminder>"), user("Yes to bothering")):
            with self.subTest(row=row):
                out = self.fire([ROUTER, self.records(), self.present(), row], "Edit", {"file_path": self.code})
                self.assertEqual(out["permissionDecision"], "deny")
                self.assertIn("Yes to both", out["permissionDecisionReason"])

    def test_an_ask_user_question_answer_counts_but_its_question_text_does_not(self):
        # The owner approved this audit's plan by picking "Yes to both" in AskUserQuestion: the host stores the choice
        # in toolUseResult.answers. The question text and the options are the agent's words.
        self.task(TASK, APPROVED)
        ask = tool("AskUserQuestion", questions=[{"question": "Approve? Yes to both?", "options": [{"label": "Yes to both"}]}])
        ask["message"]["content"][0]["id"] = "ask1"
        def answer(choice, tool_use_id="ask1"):
            return {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_use_id,
                    "content": f'The user answered: "Approve? Yes to both?"="{choice}"'}]},
                    "toolUseResult": {"questions": [], "answers": {"Approve? Yes to both?": choice}}}
        shown = [ROUTER, self.records(), self.present(), ask]
        self.assertIsNone(self.decision(shown + [answer("Yes to both")], "Edit", {"file_path": self.code}))
        self.assertIsNone(self.decision(shown + [answer("Yes to both (Recommended)")], "Edit", {"file_path": self.code}))
        self.assertEqual(self.decision(shown + [answer("No, change it")], "Edit", {"file_path": self.code}), "deny")
        bash = tool("Bash", command="echo")
        bash["message"]["content"][0]["id"] = "b1"
        self.assertEqual(self.decision([ROUTER, self.records(), self.present(), bash, answer("Yes to both", "b1")], "Edit",
                                       {"file_path": self.code}), "deny")
        # A subagent's hand-back and a task notification arrive as user entries, but they are model output.
        for origin in ({"kind": "peer", "from": "a1"}, {"kind": "task-notification"}):
            with self.subTest(origin=origin):
                rows = [ROUTER, self.records(), self.present(), user("Yes to both", origin=origin)]
                self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")
        self.assertIsNone(self.decision([ROUTER, self.records(), self.present(), user("Yes to both", origin={"kind": "human"})], "Edit",
                                        {"file_path": self.code}))

    # E2: chat text is not a lightweight record

    def test_chat_text_never_grants_lightweight(self):
        self.task(TASK, "- Approval: not approved")
        for text in ("This is NOT a lightweight edit.", "Lightweight edit: a typo in a code comment."):
            with self.subTest(text=text):
                rows = [ROUTER, say(text), self.records()]
                self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")

    # E3 and changed scope: another task's approval does not carry over

    def test_a_new_task_does_not_inherit_an_old_tasks_approval(self):
        self.task("2026-11-01-old", APPROVED)
        self.task(TASK, "- Approval: not approved; revision r1 proposed")
        rows = [ROUTER] + self.approval("Yes to both", "2026-11-01-old") + [skill("workflow-axa:workflow-execute")]
        self.assertIsNone(self.decision(rows, "Edit", {"file_path": self.code}))
        rows += [user("Now also add an export button"), skill("workflow-axa:workflow-clarify"), self.records(TASK)]
        out = self.fire(rows, "Edit", {"file_path": self.code})
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn(TASK, out["permissionDecisionReason"])
        self.assertEqual(self.decision(rows, "Bash", {"command": "git push"}), "deny")

    def test_the_task_is_resolved_in_the_edited_files_worktree(self):
        self.task(TASK, APPROVED)
        other = self.base / "repo-wt"  # a linked worktree of the same repository, outside the cwd
        (self.repo / ".git" / "worktrees" / "wt").mkdir(parents=True)
        other.mkdir()
        (other / ".git").write_text(f"gitdir: {self.repo / '.git' / 'worktrees' / 'wt'}\n", encoding="utf-8")
        rows = [ROUTER] + self.approval("Yes to both")
        target = {"file_path": str(other / "src" / "a.ts")}
        self.assertEqual(self.decision(rows, "Edit", target), "deny")  # that worktree has no such task
        self.task(TASK, APPROVED, root=other)
        self.assertIsNone(self.decision(rows, "Edit", target))
        unrelated = self.base / "elsewhere"
        (unrelated / ".git").mkdir(parents=True)
        self.assertIsNone(self.decision(rows[:1], "Edit", {"file_path": str(unrelated / "x.ts")}))  # not this project

    # E4: shell writes, judged per written path

    def test_shell_writes_into_project_files_are_gated(self):
        self.task(TASK, "- Approval: not approved")
        rows = [ROUTER, self.records()]
        spaced = self.base / "path with spaces"
        (spaced / ".git").mkdir(parents=True)
        commands = ("echo x > src/a.ts", "echo x >> src/a.ts", "echo x>src/a.ts", "cat > src/a.ts <<'EOF'\nx\nEOF",
                    "echo x | tee src/a.ts", "cp /tmp/x src/a.ts", "mv src/a.ts /tmp/a.ts", "rm -rf src",
                    "node -e \"require('fs').writeFileSync('src/a.ts', 'x')\"",
                    "python -c \"open('src/a.ts', 'w').write('x')\"",
                    "git apply fix.diff", "git checkout -- src/a.ts", "git checkout HEAD~1 -- src/a.ts",
                    "git restore src/a.ts", "git reset --hard", "git cherry-pick abc123", "git rebase main",
                    "git stash pop", "git clean -fd", "git merge feature", "git -c alias.x='!rm -rf src' x",
                    f'git -C "{spaced}" commit -m x',
                    f"echo x > src/a.ts # docs/plans/{TASK}/", f"echo x > src/a.ts; echo y > docs/plans/{TASK}/n.md",
                    f"echo x > docs/plans/{TASK}/../../../src/a.ts", f"cd docs/plans/{TASK} && echo x > ../../../src/a.ts",
                    f"cd docs/plans/{TASK} && sed -i 's/a/b/' ../../../src/a.ts",
                    "git switch main", "git stash", "git stash push -m wip", "git branch -D old",
                    "git worktree add ../wt feature")
        for command in commands:
            with self.subTest(command=command):
                self.assertEqual(self.decision(rows, "Bash", {"command": command}), "deny")
        for command in ("echo x > C:/Users/x/AppData/Local/Temp/s.txt", "cd src && cat a.ts",
                        f"cd src && echo x > ../docs/plans/{TASK}/n.md", "git checkout main", "git branch -a",
                        "git stash list", "git worktree list", "git branch -d old"):
            with self.subTest(command=command):
                self.assertIsNone(self.decision(rows, "Bash", {"command": command}))

    # E6: the PowerShell tool and MCP write tools are judged too

    def test_powershell_and_mcp_writes_are_gated(self):
        self.task(TASK, "- Approval: not approved")
        rows = [ROUTER, self.records()]
        for command in ("Set-Content -Path src/a.ts -Value x", "'x' | Out-File src/a.ts", "Add-Content src/a.ts 'x'",
                        "New-Item -ItemType File src/new.ts", "Remove-Item -Recurse -Force src",
                        "Copy-Item C:/tmp/x -Destination src/a.ts", "Move-Item src/a.ts src/b.ts",
                        "[IO.File]::WriteAllText('src/a.ts', 'x')", "git push origin main",
                        f'git -C "{self.repo}" reset --hard'):
            with self.subTest(command=command):
                self.assertEqual(self.decision(rows, "PowerShell", {"command": command}), "deny")
        self.assertEqual(self.decision(rows, "mcp__UnityMCP__create_script", {"path": "Assets/Scripts/X.cs"}), "deny")
        self.assertEqual(self.decision(rows, "mcp__trello__trelloWriteCard", {"name": "x"}), "deny")
        self.assertIsNone(self.decision(rows, "mcp__trello__trelloReadCard", {"id": "x"}))
        self.assertIsNone(self.decision(rows, "mcp__x__edit_file", {"path": f"docs/plans/{TASK}/x.md"}))

    # Review of T1: consent must be the user's whole answer, after the plan, for this task

    def test_partial_or_refused_quotes_are_not_consent(self):
        cases = (('"approve this plan"', "No, I do not approve this plan yet"),
                 ('"not yet"', "not yet"), ('"approve this plan"', "I do approve this plan now"),
                 ('"go ahead now"', "Please do not go ahead now"), ('"Yes to both"', "I said earlier: yes to both"))
        for quote, message in cases:
            with self.subTest(quote=quote, message=message):
                self.task(TASK, f"- Approval: revision r1 approved by the owner: {quote}")
                rows = [ROUTER] + self.approval(message)
                self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")
        self.task(TASK, '- Approval: revision r1 approved by the owner: "No changes needed, go ahead"')
        self.assertIsNone(self.decision([ROUTER] + self.approval("No changes needed, go ahead."), "Edit",
                                        {"file_path": self.code}))  # a refusal word is fine when the whole message matches

    def test_installs_and_downloading_npx_need_the_owner(self):
        # Loop w7 (Altinstar): `npx vitest` in a worktree without node_modules fetched vitest from the registry.
        rows = [ROUTER, user("fix it")]
        for command in ("npx vitest run src/x.test.ts", "npm ci", "npm install left-pad", "yarn add zod",
                        "pnpm add zod", "pip install requests", "cd frontend && npm i"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(rows, "Bash", {"command": command}), "deny")
        bin_dir = self.repo / "node_modules" / ".bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        (bin_dir / "vitest").write_text("", encoding="utf-8")
        self.assertIsNone(self.decision(rows, "Bash", {"command": "npx vitest run src/x.test.ts"}))
        self.assertIsNone(self.decision(rows, "Bash", {"command": "npm test"}))
        allowed = [ROUTER, user("You may run npm ci in this worktree.")]
        self.assertIsNone(self.decision(allowed, "Bash", {"command": "npm ci"}))

    def test_the_install_guard_uses_the_gates_own_activation(self):
        # Whole-feature review: "/workflow" anywhere in the transcript (skill lists, pasted CLAUDE.md) counted as a
        # workflow session, so 30 of 60 real non-workflow transcripts would have blocked npm install.
        pasted = [user("<system-reminder>\n/workflow is listed here\nworkflow-axa:workflow too\n</system-reminder>\nfix the build"),
                  user("Contents of CLAUDE.md: use /workflow for features", isMeta=True),
                  say("I could use /workflow-axa:workflow for this.")]
        for command in ("npm ci", "npx vitest run"):
            with self.subTest(command=command):
                self.assertIsNone(self.decision(pasted, "Bash", {"command": command}))
        self.assertEqual(self.decision(pasted + [ROUTER], "Bash", {"command": "npm ci"}), "deny")

    def test_install_permission_comes_from_the_users_words_around_install(self):
        allowed = ("install it, no need to ask", "You may run npm ci. No other changes.",
                   "Yes, installing is fine")
        for words in allowed:
            with self.subTest(words=words):
                self.assertIsNone(self.decision([ROUTER, user(words)], "Bash", {"command": "npm ci"}))
        refused = (user("Fix the tests. Do not install anything."), user("never run npm ci here"),
                   user("You may run npm ci", origin={"kind": "task-notification"}),
                   user("<local-command-stdout>npm install done</local-command-stdout>"),
                   user([{"type": "tool_result", "tool_use_id": "t", "content": "you may install"}]))
        for row in refused:
            with self.subTest(row=row):
                self.assertEqual(self.decision([ROUTER, user("fix it"), row], "Bash", {"command": "npm ci"}), "deny")
        ask = tool("AskUserQuestion", questions=[{"question": "Install?", "options": [{"label": "Yes, install them"}]}])
        ask["message"]["content"][0]["id"] = "ask1"
        answer = {"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "ask1",
                  "content": "answered"}]}, "toolUseResult": {"questions": [], "answers": {"Install?": "Yes, install them"}}}
        self.assertIsNone(self.decision([ROUTER, user("fix it"), ask, answer], "Bash", {"command": "npm ci"}))

    def test_more_install_and_download_forms_are_guarded(self):
        rows = [ROUTER, user("fix it")]
        for command in ("pnpm dlx create-vite", "npm exec vitest", "yarn dlx sv", "bunx vitest", "composer install",
                        "py -m pip install requests", "npx @scope/pkg@1.2 run"):
            with self.subTest(command=command):
                self.assertEqual(self.decision(rows, "Bash", {"command": command}), "deny")
        bin_dir = self.repo / "node_modules" / ".bin"
        bin_dir.mkdir(parents=True, exist_ok=True)
        (bin_dir / "pkg").write_text("", encoding="utf-8")
        (bin_dir / "vitest").write_text("", encoding="utf-8")
        for command in ("npx @scope/pkg@1.2 run", "npx pkg@latest", "npm exec -- vitest", "bunx vitest"):
            with self.subTest(command=command):
                self.assertIsNone(self.decision(rows, "Bash", {"command": command}))

    def test_an_approval_may_record_the_users_explicit_report_waiver(self):
        # A visible task/revision proposal plus the whole actual answer is required.
        answer = "Go ahead without the report"
        self.task(TASK, f'- Approval: revision r1 approved by the owner: "{answer}"', report=None)
        shown = [ROUTER, self.records(), skill("workflow-axa:workflow-specify"),
                 say(f"Plan revision r1 for docs/plans/{TASK}/: update src/a.ts only. Approve?")]
        self.assertIsNone(self.decision(shown + [user(answer)], "Edit", {"file_path": self.code}))
        self.assertEqual(self.decision(shown + [user("fix it")], "Edit", {"file_path": self.code}), "deny")
        self.assertEqual(self.decision(shown[:-1] + [user(answer)], "Edit", {"file_path": self.code}), "deny")
        self.task(TASK, '- Approval: revision r1 approved, no report: "Yes to both"', report=None)
        out = self.fire(shown + [user("Yes to both")], "Edit", {"file_path": self.code})
        self.assertIn("no plan report", out["permissionDecisionReason"])

    def test_a_report_at_the_task_folder_root_counts(self):
        # Loop w6 (Altinstar): the project keeps review-r1.html in the task folder itself, not in reviews/.
        folder = self.repo / "docs/plans" / TASK
        self.task(TASK, '- Approval: revision r1 approved by the owner: "Yes to both" (report `review-r1.html`)')
        for old in (folder / "reviews").glob("*.html"):
            old.unlink()
        (folder / "review-r1.html").write_text("<!DOCTYPE html>", encoding="utf-8")
        rows = [ROUTER, self.records(), say(f"Plan report: {folder / 'review-r1.html'}. Approve?"), user("Yes to both")]
        self.assertIsNone(self.decision(rows, "Edit", {"file_path": self.code}))

    def test_a_refusal_word_later_in_an_approving_message_does_not_void_it(self):
        # Loop w5 (Mulcol): "Approved. (c): skip the checks and report them as not run." was refused for its "not".
        self.task(TASK, '- Approval: revision r1 approved by the owner: "Approved. (c): skip the checks and report them as not run."')
        rows = [ROUTER] + self.approval("Approved. (c): skip the checks and report them as not run.")
        self.assertIsNone(self.decision(rows, "Edit", {"file_path": self.code}))
        self.task(TASK, '- Approval: revision r1 approved by the owner: "No, I do not"')
        rows = [ROUTER] + self.approval("No, I do not approve this plan yet.")
        self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")

    def test_the_answer_must_follow_the_plan_presentation(self):
        self.task(TASK, APPROVED)
        rows = [ROUTER, self.records(), user("Yes to both"), self.present()]
        self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")
        loaded = [ROUTER, self.records(), skill("workflow-axa:workflow-specify"), user("Yes to both")]
        self.assertEqual(self.decision(loaded, "Edit", {"file_path": self.code}), "deny")

    def test_another_tasks_earlier_session_does_not_count(self):
        self.task(TASK, APPROVED)
        other = [self.records("2026-11-01-other"), self.present("2026-11-01-other"), user("Yes to both")]
        self.session(self.sessions / "earlier.jsonl", other)
        rows = [ROUTER, user(f"continue docs/plans/{TASK}")]
        self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")

    def test_ide_context_text_is_not_the_users_words(self):
        self.task(TASK, APPROVED)
        for said in (user("<ide_selection>Yes to both</ide_selection>"),
                     user([{"type": "text", "text": "<ide_opened_file>Yes to both</ide_opened_file>"}])):
            with self.subTest(said=said):
                rows = [ROUTER, self.records(), self.present(), said]
                self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")
        opened = user([{"type": "text", "text": "<ide_opened_file>The user opened src/a.ts</ide_opened_file>"},
                       {"type": "text", "text": "Yes to both"}])
        self.assertIsNone(self.decision([ROUTER, self.records(), self.present(), opened], "Edit", {"file_path": self.code}))

    def test_a_later_revision_anywhere_in_the_checkpoint_voids_the_approval(self):
        for line in ("- Revision: r2 adds an export button", "- Agreement: revision r2 agreed by the owner",
                     "- Status: r2 drafted, not approved"):
            with self.subTest(line=line):
                self.task(TASK, APPROVED, line)
                self.assertEqual(self.decision([ROUTER] + self.approval("Yes to both"), "Edit",
                                               {"file_path": self.code}), "deny")
        self.task(TASK, APPROVED, "- Fixture: r22-short replay")  # a fixture name is not a revision
        self.assertIsNone(self.decision([ROUTER] + self.approval("Yes to both"), "Edit", {"file_path": self.code}))

    def test_only_written_task_paths_switch_the_task(self):
        self.task(TASK, APPROVED)
        rows = [ROUTER] + self.approval("Yes to both")
        looked = rows + [tool("Bash", command="ls docs/plans/2026-11-02-other && mkdir -p /tmp/x")]
        self.assertIsNone(self.decision(looked, "Edit", {"file_path": self.code}))
        made = rows + [tool("Bash", command="mkdir -p docs/plans/2026-11-02-other")]
        self.assertEqual(self.decision(made, "Edit", {"file_path": self.code}), "deny")

    def test_a_task_switch_after_the_last_user_message_is_stopped(self):
        self.task(TASK, APPROVED)
        self.task("2026-11-02-other", "- Approval: not approved")
        rows = [ROUTER] + self.approval("Yes to both") + [self.records("2026-11-02-other"), self.records(TASK)]
        out = self.fire(rows, "Edit", {"file_path": self.code})
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("changed to", out["permissionDecisionReason"])
        self.assertIsNone(self.decision(rows + [user(f"Yes, this is docs/plans/{TASK}")], "Edit", {"file_path": self.code}))

    def test_a_whole_read_of_the_router_skill_activates_the_gate(self):
        router = str(ROOT / "skills/workflow/SKILL.md")
        self.assertEqual(self.decision([tool("Read", file_path=router)], "Edit", {"file_path": self.code}), "deny")
        self.assertIsNone(self.decision([tool("Read", file_path=router, limit=20)], "Edit", {"file_path": self.code}))

    def test_inline_code_writing_task_records_is_free_and_unknown_targets_are_named(self):
        # Live run w1 (Altinstar): node -e writing the task's own PLAN.md through a shell variable was denied.
        self.task(TASK, "- Approval: not approved")
        rows = [ROUTER, self.records()]
        for command in (f"cd {self.repo}; f=docs/plans/{TASK}/PLAN.md; node -e \"require('fs').writeFileSync('$f', 'x')\"",
                        f"python -c \"open('docs/plans/{TASK}/PLAN.md', 'w').write('x')\""):
            with self.subTest(command=command):
                self.assertIsNone(self.decision(rows, "Bash", {"command": command}))
        self.assertIsNone(self.decision(rows, "PowerShell", {"command": f"$f = 'docs/plans/{TASK}/x.md'; Set-Content $f y"}))
        out = self.fire(rows, "Bash", {"command": "node -e \"require('fs').writeFileSync(process.argv[1], 'x')\" a"})
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("could not tell which file", out["permissionDecisionReason"])
        self.assertIn("record.py", out["permissionDecisionReason"])

    def test_record_writes_after_cd_into_a_variable_resolve_to_the_task_folder(self):
        # rc3 trial L6: `cd "$R"` with R set in the same command was not expanded, so record.py writing the task's
        # own PLAN.md looked like a code write and was denied before approval.
        self.task(TASK, "- Approval: not approved; revision r1 proposed")
        rows = [ROUTER, skill("workflow-axa:workflow-specify"), self.records()]
        tool_dir = "D:/w/skills"
        record = f'R="{self.repo.as_posix()}"; W="{tool_dir}"; T="docs/plans/{TASK}"; cd "$R"; '
        for command in (record + 'python -X utf8 -I "$W/workflow/scripts/record.py" set-line "$T/PLAN.md" "- a:" "b"',
                        record + 'echo x > "$T/notes.md"',
                        f'cd "{self.repo.as_posix()}"; python -X utf8 -I {tool_dir}/record.py set-line docs/plans/{TASK}/TODO.md a b'):
            with self.subTest(command=command):
                self.assertIsNone(self.fire(rows, "Bash", {"command": command}, cwd=self.base))
        # The resolved folder is still judged: code there, or a docs/plans folder that is not the project's, needs approval.
        for command in (record + 'echo x > src/a.ts',
                        f'R="{self.repo.as_posix()}/src"; cd "$R"; python -X utf8 -I {tool_dir}/record.py set-line docs/plans/{TASK}/PLAN.md a b'):
            with self.subTest(command=command):
                self.assertEqual(self.decision(rows, "Bash", {"command": command}, cwd=self.base), "deny")

    def test_writes_relative_to_an_unresolved_variable_folder_need_an_explicit_path(self):
        # A folder named by a variable set outside the command is not guessed, record or not.
        self.task(TASK, "- Approval: not approved; revision r1 proposed")
        rows = [ROUTER, self.records()]
        for command in (f'cd "$REPO"; python -X utf8 -I D:/w/record.py set-line docs/plans/{TASK}/PLAN.md a b',
                        'cd "$REPO"; echo x > src/a.ts',
                        'cd "$REPO"; cd sub; echo x > a.ts',
                        'cd "$REPO" && git commit -m x',
                        'cd "$REPO"; bash -c "echo x > a.ts"'):
            with self.subTest(command=command):
                out = self.fire(rows, "Bash", {"command": command})
                self.assertEqual(out["permissionDecision"], "deny")
                self.assertIn("explicit path", out["permissionDecisionReason"])
        # Absolute targets after it are judged as usual, and nothing changes once the task is approved... except the
        # unresolved folder, which still needs an explicit path.
        record = self.repo / "docs/plans" / TASK / "PLAN.md"
        self.assertIsNone(self.fire(rows, "Bash", {"command": f'cd "$REPO"; echo x > "{record.as_posix()}"'}))
        self.assertEqual(self.decision(self.approved_rows(), "Bash", {"command": 'cd "$REPO"; echo x > src/a.ts'}), "deny")

    def test_a_crash_inside_the_gate_blocks_edit_tools_only(self):
        self.assertEqual(self.decision([ROUTER], "Edit", ["not", "a", "dict"]), "deny")
        self.assertIsNone(self.fire([ROUTER], "Read", ["not", "a", "dict"]))

    def test_an_approval_needs_the_html_plan_report(self):
        # Live rounds w2/w3 (Mulcol, Altinstar): an Approval line was written and answered without workflow-specify,
        # so no TODO and no HTML plan report existed, and code was edited under it.
        rows = [ROUTER] + self.approval("Yes to both")
        folder = self.task(TASK, APPROVED, report=None)
        out = self.fire(rows, "Edit", {"file_path": self.code})
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("no plan report", out["permissionDecisionReason"])
        self.assertIn("Lightweight edit", out["permissionDecisionReason"])
        self.assertEqual(self.decision(rows, "Bash", {"command": "git push"}), "deny")
        self.task(TASK, APPROVED, report="plan-r2.html")  # a report, but not the one the Approval line names
        self.assertEqual(self.decision(rows, "Edit", {"file_path": self.code}), "deny")
        (folder / "reviews" / "plan-r1.html").write_text("<!DOCTYPE html>", encoding="utf-8")
        self.assertIsNone(self.decision(rows, "Edit", {"file_path": self.code}))

    # Unreadable input

    def test_an_unreadable_transcript_blocks_edit_tools_and_a_missing_path_allows(self):
        self.path.write_text("not json\n{broken", encoding="utf-8")
        event = {"tool_name": "Edit", "tool_input": {"file_path": self.code}, "transcript_path": str(self.path),
                 "cwd": str(self.repo)}
        out = run_hook(event)
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("could not be read", out["permissionDecisionReason"])
        event["tool_input"] = {"file_path": str(self.repo / "docs/plans" / TASK / "PLAN.md")}
        self.assertIsNone(run_hook(event))  # records stay writable
        push = dict(event, tool_name="Bash", tool_input={"command": "git push"})
        self.assertEqual(run_hook(push)["permissionDecision"], "deny")  # review: git writes too
        self.assertIsNone(run_hook(dict(event, tool_name="Bash", tool_input={"command": "echo x > src/a.ts"})))
        self.assertIsNone(self.fire([ROUTER], "Edit", {"file_path": self.code}, transcript=False))


if __name__ == "__main__":
    unittest.main()
