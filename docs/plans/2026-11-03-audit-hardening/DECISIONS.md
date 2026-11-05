# Decisions

Open questions for the owner (asked 2026-11-03 with the r1 plan).

## Q1 — What counts as approval for code edits
- (a) The current task's Approval line, and the user's words it quotes must appear in a real user message in this session or the recorded one. Recommended: the agent can write the line, but it cannot fake a user message.
- (b) The Approval line alone. Simpler, but the agent can write it itself.
- (c) Keep today's rule (any phase name in the session). Not recommended: E1-E3 show it lets edits through.

## Q2 — Small-change route
- (a) One builder (the main session) and one independent reviewer, with the escalation rule in T6. Recommended.
- (b) Keep a fresh worker for every ticket.
Asking both gates in one message for small changes stays as today ("both at once when nothing is open"). Changing that is a separate policy choice, and this plan does not change it.

## Q3 — A licence for workflow-axa's own code
The vendored skills carry their own MIT licences, but the project has none at its root. Options: (a) MIT, (b) another licence you name, (c) none for now, private use.

## Q4 — Release package
- (a) Add `tools/build_release.py` now, with the include list in T8. Recommended.
- (b) Later.

## Q5 — Paid live acceptance runs (T9)
Measured live runs cost between about $1 and $17 each in this session's headless summaries. Options:
- (a) Up to 8 headless Claude runs on fixtures, plus Codex runs.
- (b) Claude only.
- (c) None: report only the static and helper tests.

## Answers (owner, 2026-11-03)
- D1 (Q1): (a) "Line + your real words". Code edits and git writes need the current task's Approval line, and the user's words it quotes must appear in a real user message.
- D2 (Q2): (a) "1 builder + 1 review". Small route as in T6, with the escalation rule.
- D3 (Q3): "MIT."
- D4 (Q4): "Build the release tool now."
- D5 (Q5): "Allow up to 8 Claude runs plus Codex runs where useful, but avoid unnecessary paid runs."

## Approval (owner, 2026-11-03)
- D6: agreement and plan r1: "Yes to both".

## Choices made during T1 (by: agent, 2026-11-03; the owner can reverse them)
- D7: an answer the owner picks in an AskUserQuestion dialog counts as the owner's words for the approval check. The owner's "Yes to both" exists only in that form. Question text the agent wrote, tool output, subagent hand-backs and task notifications never count.
- D8: one current task per session: the last task folder the session wrote records in, or the one the owner named.
- D9: a `Lightweight edit:` line never allows git writes; an approval line without a revision number (`rN`) is refused, so older tasks reach new code through clarify.

- D10 (by: agent, 2026-11-04): T3 named resume-task/SKILL.md, but it stays unchanged: its 500-word budget is full, and the route back from a stopped or paused task now lives in the router table and TASK-FOLDER "Stop, pause and cancel", which resume-task already reads. The owner can reverse this.

- D11 (owner, 2026-11-03): the owner's later goal "do not stop untill everything works with tests on all the 4 repo's do not commit push and keep looping all of them untill best results and each round do a retro check" widened D5's "up to 8 Claude runs" for the live loop. Actual: 32 headless Claude turns over 8 rounds (4 repositories) plus 1 Codex read-only run, and the earlier 24 v-rounds were part of the version-line task. The same goal also ended local commits: nothing after 9e8338e is committed.

## Follow-up r4 decisions
- D-r4-1 (user): "fix all of it" directs continuation of the original testing/bug-fix/E2 objective. Prior live-installation and final-transfer restrictions remain active.
- D-r4-2 (agent): use one isolated source snapshot at D:/wfaxa-pilot/workflow-fixes. Do not edit hooks under D:/workflow-axa, which running sessions may load. No Git metadata copied and no Git writes performed.
- D-r4-3 (agent): preserve raw private logs in place; save concise observations and synthetic fixtures only. Generic code does not absorb Altinstar-specific device/build tooling.

## Follow-up owner approvals, 2026-11-05
- Owner approved Cheflabels r5 implementation in its disposable worktree, then approved temporary use of the original existing dependencies after compatibility checking. Final transfer approval is separate and remains pending.
- Owner approved at most two isolated Claude processes, capped at USD 1 each, USD 2 total, no retries or extra model/subagent calls. The first process checked waiting/rejection but its host permissions prevented writing. The second process is restricted to read-only restart reconciliation; no retry of the denied edit. No further paid test process is authorised by this batch.

## Replacement host batch and final transfer approval
- Owner answered "Approve replacement $2 batch": at most two processes, USD1 each, acceptEdits in synthetic fixture only, no shell/network/subagents or live installation changes.
- Owner answered "Approve result and final transfer": accepted Cheflabels final screenshot, browser/build/review and D16 scroll fix; authorised only three application/docs files plus task evidence to original feature/offerte-20260907, verify, then remove disposable worktree, no commit/push.

## Final authority reconciliation, 2026-11-05

Direct instruction "fix all of it" authorized isolated follow-up implementation. It did not approve r4 HTML or live installation. Earlier r1 approval and D7-D10 remain historical. Later explicit approvals supersede the earlier pending Cheflabels transfer line. The accepted result was transferred and its disposable worktree removed. Both paid batches ended within their approved caps. No further paid sessions, installation or policy acceptance is requested.

## Publication and Git installation authority, 2026-11-05
Owner: "Alright put it here in main branch please and push it than install latest version from git not local".
This authorizes integrating the tested rc.4 candidate (including preserved UI-lite work) into D:/workflow-axa main, committing/pushing to origin, and replacing the local-directory Claude marketplace with Gazohhh/workflow-axa from GitHub. Rules READY: existing project/shared scope and explicit publication/install authority. Baseline main and remote/main both 0d67057a6e15b72436624e48b0698bab00185ab5; pre-existing tracked changes matched the preserved snapshot. Selected non-sensitive test evidence is published under this task's evidence folder so fresh Git installs have valid documentation links. Raw host traces remain private.
