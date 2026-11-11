# Duplicate skill copy guard

## Current checkpoint
- Updated / phase: 2026-11-11; closed for the automated part. r1 and r2 delivered, all five tickets verified. Report reviews/delivery-r2-2026-11-11.html
- Agreement (gate one): agreed; revision r2 including its additions R7 to R10, 2026-11-11, the owner said "Yes to both" (D15)
- Approval (gate two): approved; revision r2, report docs/plans/2026-11-11-duplicate-skill-guard/reviews/plan-r2.html, 2026-11-11, the owner said "Yes to both"
- Implementation: implemented
- Verification / owner acceptance: automated checks passed (V17). Owner's live check of r1 done (V12 to V14). The r2 repairs were not seen live
- Blockers: none
- Changed files: r1: hooks/duplicate_skills.py (new), tests/test_duplicate_skills_hook.py (new), hooks/hooks.json, tools/validate.py, skills/workflow-doctor/SKILL.md, skills/workflow/SETUP.md, CHANGELOG.md. r2: hooks/duplicate_skills.py, tests/test_duplicate_skills_hook.py, skills/workflow/SETUP.md, CHANGELOG.md. Outside the repository: 21 links removed from ~/.claude/skills (FINDINGS V1)
- Next safe action: none for the guard. The owner decides about committing

## Working context
- Owner: Gazoh; repository D:\workflow-axa, branch main, main checkout
- Task identity: new task, no related record under docs/plans. The owner asked for it on 2026-11-11 as the step before the larger consistency work (the five review findings), which is a separate later task pending Q4.
- Local changes before this task: 18 staged files of the uncommitted 2.8.0-rc.35 work (see FINDINGS E5). Not mine. Untouched.
- Rules: READY / AGENTS.md, tests/README.md, rule-maker START, CORE, READINESS / scope: hooks, skills, tests of this repository / rules 1.8.5, stamp NONE / hook edits need an isolated candidate location (AGENTS.md Boundaries)
- Decision check: FINDINGS "Question round 1"
- Test output folder: .artifacts/2026-11-11-duplicate-skill-guard/, removed after delivery except cited proof

## Goal and acceptance
The owner's words (2026-11-11): "this is the second time i got the duplicate skill issue i want to prevent this and ask user to delete this as otherwise different results may produce while the workflow works correct. I want consistency"

## Agreement

Revision r1, proposed 2026-11-11. Not yet agreed.

Requirements
- R1 (owner, 2026-11-11: "i want to prevent this and ask user to delete this"): at the start of every Claude Code session the plugin checks whether a workflow-axa skill name is also visible from a second place: the personal skills folder (`~/.claude/skills`, or the folder under CLAUDE_CONFIG_DIR) or the project's `.claude/skills`.
- R2 (same message): when it finds one, the agent tells the owner in its first reply: the exact paths, that different copies can give different results, and the request to delete them. The guard never deletes, moves or edits anything itself.
- R3 (Q3 a): while duplicates exist, workflow change work waits: loading workflow-clarify, workflow-specify or workflow-execute, or a bare duplicate skill name, is refused with the same message. Read-only questions, task-status and workflow-doctor keep working.
- R4 (Q3 a): the owner can lift the pause for one session with the words "continue with duplicates" in a real user message. Text from the agent, a tool or a file does not count. The next session checks again.
- R5 (assumption, the owner can reject it): equal bytes still count as a duplicate, because the copies drift at the next update.
- R6 (assumption, the owner can reject it): the guard also compares the shared rules copy that the global instructions import (`~/.agents/skills/rule-maker/rules`) with the plugin's rules. A difference is reported at session start as a warning. It does not pause work.

What stays the same
- `hooks/phase_gate.py` and the approval gates are not changed. The guard is a new, separate hook script with its own registration.
- `~/.agents/skills` stays: Codex and the global rules import use it.
- workflow-doctor and `audit_installation.py` keep their behavior. workflow-doctor gets one line that names the guard.
- The 18 staged rc.35 files stay staged and untouched (Q1 a). The guard is released as rc.36.

Not included
- Codex: it has no hooks, so nothing runs there.
- Old versions in the plugin cache, and the 17 broken links in `~/.claude/skills`.
- Other plugins that ship a skill with a different name for the same job (for example superpowers). That belongs to the second task.
- The five review findings (Q4 a): separate second task after this one is delivered.

Acceptance
- A1 (R1, R2): in a test home with a link `skills/tdd`, the session-start output names that exact path and asks for deletion. With no duplicate it prints nothing.
- A2 (R3): with a duplicate present, loading workflow-clarify is refused with the message. Loading task-status is allowed.
- A3 (R4): after a user message with "continue with duplicates", workflow-clarify loads in that session. The same words in a tool result change nothing. A new session is paused again.
- A4 (R2): after every test the test home has the same files as before.
- A5 (R6): a changed byte in the second rules copy gives a warning and no pause.
- A6: the existing test suite passes as before, with pre-existing failures named.

Limits
- Without Python no hook runs, so no guard. Live behavior in a real Claude Code session is checked by the owner after installation (human check).

## Approval

Revision r1, report reviews/plan-r1.html, approved 2026-11-11. Owner's answer to "Approve it to start implementation, or describe what needs changing.": "approve". Included: T1, T2, T3. Excluded: commit, push, installation of rc.36, anything outside write_paths. A change to behavior or to the file list needs a new revision.


## Agreement revision r2 (proposed 2026-11-11; the two points marked "needs the owner's yes" were answered with "sure fix it", D13)
Changes to r1 that came out of the build and its reviews. Everything else in r1 stands.
- R4, decided by the owner (D9): only a message that is exactly the words "continue with duplicates" lifts the pause. The words inside a longer message do not count.
- R4, decided by the agent, needs the owner's yes: the override ends 12 hours after the words were sent. Reason: a resumed session keeps its ID, so the override would otherwise last for days. Effects: a session open longer than 12 hours is paused again, and a session resumed within 12 hours is not.
- R3, decided by the agent, needs the owner's yes: a change skill typed as a slash command is stopped in the user-message event, because a typed command loads without a Skill tool call. The message is shown to the owner directly.
- R1, decided by the agent from the host documentation (E12): project skills folders are checked in the start folder and each parent up to the repository root.
- R2, decided by the agent: the request to delete says "If an entry is a link, remove only the link, not the folder it points at."
- R3, decided by the agent to follow ticket T2: when the override marker cannot be stored at all, the call is allowed.
- Ticket T3, decided by the owner (D10): version stays 2.8.0-rc.35.


## Outcome
Delivered partial on 2026-11-11. Report: reviews/delivery-2026-11-11.html. Nothing is committed.

Asked, agreed, built
- Asked: find a second copy of a workflow-axa skill, ask the owner to delete it, keep sessions consistent.
- Agreed: revision r1 ("yes", D6) and the changes of revision r2 ("sure fix it", D13). Approved plan: r1 ("approve", D7).
- Built: hooks/duplicate_skills.py with its 55 tests, the registration in hooks/hooks.json, the package check entry, one sentence in workflow-doctor, one paragraph in workflow/SETUP.md, one bullet in the rc.35 CHANGELOG entry. hooks/phase_gate.py is unchanged. Version stays 2.8.0-rc.35 (D10). Outside the repository: 21 duplicate links removed from ~/.claude/skills.

Tickets
- T1 verified (V5). T2 verified (V8). T3 implemented, verification pending: its human check in a live session has no result yet.

Checks (final state, V11)
- Guard tests: 55, all pass. Package check: PASS. Full suite: 1020 tests, 4 failures, 13 skipped. The 4 failures are the baseline four from the staged rc.35 work. The suite includes 9 tests of the owner's separate report patch.
- The seven behaviours of D11 each ran by test name and passed. "Existing hook registrations unchanged" rests on the diff, no test asserts it.

Reviews
- One independent reviewer, Standards and Spec separate: two rounds on T1, three on T2, the whole feature, and a diff check of the docs. A fresh subagent that did not build the work did the reconciliation.

Acceptance verdicts
- A1, A2, A3, A5, A6 verified. A4 partial: one snapshot test, not every test.
- Requirements R1 to R4 partial, because nothing was observed in a live session. R5 and R6 verified. R6 compares only the first import.

Remaining defects (need an approved r2 plan before any edit)
1. skills/workflow/SETUP.md and CHANGELOG.md say a bare duplicate name is also stopped when typed as a slash command. Untrue: only the three change commands are.
2. An existing read-only temp folder keeps the pause, against ticket T2. Untested.
3. No test asserts that existing hook registrations are unchanged.
4. On resume or compact the session-start note says "paused" while an override is active.

Agent decisions for the owner to know
- D3: 6 more links removed than the 15 approved. Reported, not explicitly confirmed.
- 12 hour limit and the stop of a typed command: answered with "sure fix it" (D13). Read by the agent as agreement.
- Parent folders checked, the link warning, a marker that cannot be stored allows the call: shown, not answered one by one.
- Worker choices kept: a change-skill name under another plugin's prefix is paused, `workflow-axa:tdd` loads even when a `tdd` copy exists.

Limits
- No live session. Windows only. Junctions, not true symbolic links. The block output for a typed command is not seen on a host. Without Python no hook runs. Codex has no hooks.
- The delivery report keeps the plan's four diagrams and the older single "agreed behavior" block. Its build-plan view still says rc.36 in one node note if the renderer did not pick up the change: not checked view by view.

Kept evidence
- .artifacts/2026-11-11-duplicate-skill-guard/: baseline-suite.txt, pre-patch-suite.txt, post-patch-suite.txt, final-suite.txt, report screenshots, report-review-bundle.zip. Remove after the owner's acceptance, except what a later check cites.

Next safe action
- The owner checks the guard in a fresh session and answers on the r2 repairs.


### Additions to revision r2 (proposed 2026-11-11 after the delivery, asked together with plan r2)
The owner said "plan r2" on 2026-11-11 for the four remaining defects. These lines say what will be true after the repairs.
- R7 (owner's live check, V12: the agent added "deliver" by itself): both guard messages name the paused skills: workflow-clarify, workflow-specify and workflow-execute.
- R8 (remaining defect 4): when the override is active for the session, the session-start note still names the copies and asks for deletion, and says that the pause is lifted for this session. It no longer says the skills stay paused.
- R9 (remaining defects 1 and 2): the docs say only what the guard does. A typed bare duplicate name such as `/tdd` is not stopped. A temp folder path that is not a folder lets work continue. A temp folder that exists but refuses writes keeps the pause, and the way out is to delete the copies. This replaces the r2 line "when the override marker cannot be stored at all, the call is allowed" for that one case. No code change for it.
- R10 (remaining defect 3): a test pins the registrations of the other hooks, so a later edit that changes or drops one fails.

Acceptance
- A7 (R7): the session-start message and the refusal each contain the three skill names. The typed-command message is unchanged.
- A8 (R8): with a duplicate and an active override, the start note contains the paths and "lifted for this session" and does not contain "stay paused". Without an override it is as before.
- A9 (R9): skills/workflow/SETUP.md and CHANGELOG.md no longer say a bare duplicate name is stopped when typed, and both name the read-only temp folder limit.
- A10 (R10): the new test fails when a command of another hook is removed or changed in a copy of hooks.json, and passes on the real file.
- A11: the hook tests, the package check and the full suite give the same result as V11, plus the new tests.

What stays the same: everything else in r1 and r2. hooks/phase_gate.py. The version 2.8.0-rc.35. No change to what is paused or to the override.


## Approval history
- r1: reviews/plan-r1.html, 2026-11-11, D7. Tickets T1 to T3. Delivered, all three verified.
- r2: reviews/plan-r2.html, 2026-11-11, D15. Tickets T4 and T5. Asked together with the agreement to the r2 additions.


## Outcome of revision r2
Delivered partial on 2026-11-11. Report: reviews/delivery-r2-2026-11-11.html. Nothing is committed. Reconciliation self-performed by the builder: the task is two small tickets and the independent review ran on the final files except for one removed clause.

- Asked: "plan r2" for the four defects of the first delivery (D14). Agreed and approved: "Yes to both" (D15).
- Built: T4 (hooks/duplicate_skills.py, tests/test_duplicate_skills_hook.py) and T5 (skills/workflow/SETUP.md, CHANGELOG.md). Both verified.
- The first delivery's ticket T3 is also verified since the owner's live check (V12 to V14). All five tickets of the task are verified.
- Checks, final state (V17): hook tests 59, all pass. Package check PASS. Full suite 1024 tests, 4 failures, 13 skipped. The 4 failures are the baseline four from the staged rc.35 work.
- Review: one independent reviewer on both tickets, Standards and Spec. One finding repaired with a test (a false reason in the new start note), one closed in the test, one left as a limit. The one-clause repair was not sent back.
- Acceptance: A7, A8, A9, A10, A11 verified with test events. Requirement R9's choice to keep the pause for a read-only temp folder is documented, not coded, as approved.
- The four defects of the first delivery: 1 (untrue doc sentence) fixed. 2 (read-only temp folder) settled in the docs as approved. 3 (no test for the other hooks) fixed. 4 (start note on resume) fixed.
- Limits: the r2 repairs were not seen in a live session. The pinning test does not notice an extra key on an existing hook entry. A refused bare duplicate name gets a reason that names the three change skills. The earlier limits stand.
- Agent decisions: none new beyond the approved plan, except removing the false clause the reviewer found.
- Kept evidence: .artifacts/2026-11-11-duplicate-skill-guard/r2-final-suite.txt and the earlier files. r2-suite.txt is a run that overlapped an edit and is not counted.
- Next safe action: none for the guard. The owner decides about committing.
