# TODO

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Find duplicate copies at session start and ask the owner to delete them | Verified | none |
| T2 | Pause change work while duplicates exist, with a one-session override | Verified | T1 |
| T3 | Register the guard, document it and release it under rc.35 (D10) | Verified | T2 |

## Tickets

### T1 — Find duplicate copies at session start and ask the owner to delete them
Status: Verified

What needs to happen: A new hook script looks, when a session starts, for a workflow-axa skill name that Claude Code can also see from a second place. It gives the agent a message with the exact paths and the request to delete them. It also compares the shared rules copy that the global instructions import with the plugin's rules.

What should work:
- A folder or link `<config dir>/skills/<name>` or `<project>/.claude/skills/<name>` that contains a SKILL.md, for a name the plugin registers, is reported with its full path.
- Equal bytes are still reported (R5).
- No duplicate and equal rules: the script prints nothing.
- A broken link, a name the plugin does not register, or an old plugin cache version is not reported.
- The rules copy named in the global CLAUDE.md import differs in any file: one warning line that names the copy. No import line: no rules check.
- Malformed input, an unreadable folder or a missing plugin.json: the script prints nothing and exits 0. It never stops a session from starting.
- The script changes no file.

Technical details:
- May change: `hooks/duplicate_skills.py` (new), `tests/test_duplicate_skills_hook.py` (new). Must not change: `hooks/phase_gate.py`, `hooks/hooks.json`, anything outside the repository.
- Skill names come from `.claude-plugin/plugin.json` `skills`. No second name list.
- Config dir: `CLAUDE_CONFIG_DIR`, else `~/.claude`. Project: the event's `cwd`.
- Test seam: run the script as a process with a SessionStart event on stdin, with a temporary home, config dir and project. This catches detection, wording and no-write behavior. It misses how a real host shows the message; the T3 human check covers that.
- TDD: yes.

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_duplicate_skills_hook.py" -v` from the repository root. Expected: all pass. Output: console only.

Verification: passed

References:
- Supports: R1, R2, R5, R6, A1, A4, A5
- Depends on: none
- Rules: AGENTS.md (hook candidates stay isolated: the script is not registered until T3), tests/README.md
- Evidence: V5; reviews 1 and 2 in FINDINGS

### T2 — Pause change work while duplicates exist, with a one-session override
Status: Verified

What needs to happen: The same script refuses to load a change-phase skill while a duplicate exists, and lets the owner lift that for one session with the words "continue with duplicates".

What should work:
- PreToolUse for the Skill tool: with a duplicate present, `workflow-clarify`, `workflow-specify`, `workflow-execute` (with or without the `workflow-axa:` prefix) and any bare name that has a duplicate are denied. The reason repeats the paths and both ways out: delete them, or say "continue with duplicates".
- `task-status`, `workflow-doctor`, `workflow`, `resume-task` from the plugin and every other tool are allowed.
- The check runs again at each Skill call. After the owner deletes the copies, the next call is allowed without a restart.
- UserPromptSubmit: a prompt that is exactly "continue with duplicates" (any letter case; changed from "contains" by owner decision D9) stores an override for that session ID. Later Skill calls in that session are allowed. Another session ID is still paused.
- The words inside a tool result, an agent message or a file do not create the override, because only the UserPromptSubmit event is read.
- Malformed input or an unwritable state folder: allow and print nothing. A guard defect must not block work.

Technical details:
- May change: `hooks/duplicate_skills.py`, `tests/test_duplicate_skills_hook.py`. Must not change: `hooks/phase_gate.py`, `hooks/hooks.json`.
- Override state: one small file per session under the system temp folder (`workflow-axa-gate`, the folder `phase_gate.py` already uses, own file name prefix), or the folder in `WORKFLOW_AXA_GATE_CACHE`.
- Deny output uses the same PreToolUse JSON that `phase_gate.py` prints (`permissionDecision: deny`).
- Test seam: the script as a process with PreToolUse and UserPromptSubmit events. It misses real host behavior for a denied Skill call; the T3 human check covers that.
- TDD: yes.

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_duplicate_skills_hook.py" -v`. Expected: all pass.

Verification: passed

References:
- Supports: R3, R4, A2, A3, A4
- Depends on: T1
- Rules: AGENTS.md, tests/README.md
- Evidence: V8; reviews 1 to 3 of T2 in FINDINGS

### T3 — Register the guard, document it and release it under rc.35 (D10)
Status: Verified

What needs to happen: Prerequisite that makes T1 and T2 run in real sessions: register the script in the plugin's hook file, add it to the package check, name it in the docs and set the version.

What should work:
- `hooks/hooks.json` runs the script on SessionStart, on PreToolUse for Skill and on UserPromptSubmit. Existing registrations keep their order and content. The description names the new guard.
- `tools/validate.py` requires the new script and its test.
- `skills/workflow-doctor/SKILL.md` and `skills/workflow/SETUP.md` each say in one or two sentences what the guard does and what it cannot do (no Python, Codex).
- Version stays 2.8.0-rc.35 by owner decision D10 (the ticket first said rc.36). The guard has a bullet in the rc.35 CHANGELOG entry.

Technical details:
- May change: `hooks/hooks.json`, `tools/validate.py`, `skills/workflow-doctor/SKILL.md`, `skills/workflow/SETUP.md`, `CHANGELOG.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `skills/rule-maker/rules/version.json`, `README.md`, `UPGRADE.md`, `VALIDATION.md`, `tests/README.md`, and tests that pin the version or the hook list. Several of these carry staged rc.35 edits: add to them, never revert them.
- Before editing `hooks/hooks.json`, confirm that running sessions load hooks from the plugin cache copy and not from this checkout (AGENTS.md Boundaries). If they load from this checkout, stop and ask.
- TDD: no for the registration and docs (configuration). The existing package tests cover them.

How to verify:
- `python -X utf8 tools/validate.py` and `python -X utf8 -m unittest discover -s tests -p "test_*.py"` from the repository root. Expected: the same result as the baseline taken before T1, plus the new tests. Output: console, summary in FINDINGS.
- Human check: in a fresh Claude Code session (the version stays rc.35, D10; sessions load this checkout, E9), a fresh Claude Code session with a test link `~/.claude/skills/tdd` shows the request to delete it in the first reply, refuses workflow-clarify, and accepts it after "continue with duplicates". Asked for at delivery.

Verification: passed

Owner acceptance: Gazoh, 2026-11-11: "Yes worked seeing: ..." and "done you can check" (V12 start message, V13 typed command stopped, V14 override and load)

References:
- Supports: A6, enables R1 to R4 in real sessions
- Depends on: T2
- Rules: AGENTS.md, tests/README.md, VENDORED-SKILLS.md (no vendored text changes)
- Evidence: V9, V11, V12, V13, V14; whole-feature review and reconciliation in FINDINGS

## Bigger checks
- Whole feature against the agreement: one test run that starts a session with a duplicate, is refused, overrides, and leaves the test home unchanged (A4).
- Existing hooks: `tests/test_phase_gate_hook.py`, `test_phase_reads_hook.py` and `test_plain_reply_hook.py` still pass unchanged.
- Cannot be checked here: how a live Claude Code session shows the message, and Codex. Needs: the owner's check in a fresh session.


## Revision r2 tickets (approved 2026-11-11, D15)

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T4 | Make the guard's messages exact, and pin the other hooks' registrations | Verified | none |
| T5 | Correct the two doc texts | Verified | T4 |

### T4 — Make the guard's messages exact, and pin the other hooks' registrations
Status: Verified

What needs to happen: The start note and the refusal name the three paused skills. The start note tells the truth when the override is active. A new test pins the registrations of the other hooks.

What should work:
- The session-start message and the Skill refusal contain "workflow-clarify, workflow-specify and workflow-execute".
- With an active override the start note names the copies, asks for deletion and says the pause is lifted for this session. It does not say the skills stay paused.
- Without a session ID, or with an expired or missing marker, the start note is as before.
- The typed-command message is unchanged.
- A test holds the expected commands of every hook except the guard, per event and in order. It passes on hooks/hooks.json and fails on a copy with one command removed or changed.

Technical details:
- May change: `hooks/duplicate_skills.py`, `tests/test_duplicate_skills_hook.py`. Must not change: `hooks/hooks.json`, `hooks/phase_gate.py`, any doc.
- The start note reuses `pause_lifted`. No new file, no new setting.
- Test seam: the script as a process with SessionStart and PreToolUse events, and the hooks.json file read by the test. It misses how a live agent rephrases the note. The owner saw that live once (V12).
- TDD: yes.

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_duplicate_skills_hook.py" -v` from the repository root. Expected: all pass.

Verification: passed

References:
- Supports: R7, R8, R10, A7, A8, A10
- Depends on: none
- Rules: AGENTS.md, tests/README.md
- Evidence: V15

### T5 — Correct the two doc texts
Status: Verified

What needs to happen: Remove the untrue statement about typed bare names and name the read-only temp folder limit.

What should work:
- `skills/workflow/SETUP.md`, paragraph "Duplicate skill copies": the three change skills do not load, also when typed. A bare duplicate name does not load through the Skill tool. The limits name the read-only temp folder.
- `CHANGELOG.md`, the guard bullet under 2.8.0-rc.35: the same two facts.
- After T4: both texts say that an active override changes the start note.

Technical details:
- May change: `skills/workflow/SETUP.md`, `CHANGELOG.md`. Must not change: any other file. Both files carry staged rc.35 edits: add to them, revert none.
- TDD: no (docs). The contract is the final code.

How to verify:
- A reviewer compares each sentence with `hooks/duplicate_skills.py`. `python -X utf8 tools/validate.py` passes.

Verification: passed

References:
- Supports: R9, A9
- Depends on: T4
- Rules: AGENTS.md
- Evidence: V16; review of r2 in FINDINGS

## Bigger checks for r2
- After both tickets: the hook tests, `python -X utf8 tools/validate.py` and the full suite. Expected: the result of V11 plus the new tests (A11).
- One independent review of both tickets together, Standards and Spec.
- Not checked: a live session. The owner may repeat the earlier live check.
