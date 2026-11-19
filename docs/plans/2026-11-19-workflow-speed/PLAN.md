# Workflow speed (Matt Pocock and Lauren Tan review)

## Current checkpoint
- Updated / phase: 2026-11-19; released as 2.10.0 (17cc1ec); owner acceptance pending
- Recipe: feature; modifiers Compatibility — the owner wants the workflow faster: cheaper hooks, less always-read text and fewer stops; existing tasks, offers and approvals keep working; scope: the task; classification question: not asked (the owner's "do all of it" on the 16-item comparison settles the kind of work)
- Agreement (gate one): agreed — agreement 1, 2026-11-19 (owner: "Agree")
- Offer: #5 draft (merge and release 2.10.0); #4 approved (T9); #3 approved (T0-T8); #2 approved (worktree)
- Implementation: implemented (T0-T9; T3 short of its word target)
- Verification / owner acceptance: V9-V12 passed apart from A1; owner acceptance pending
- Blockers: none
- Changed files: 64 files on speed/2.10 (list: .artifacts/2026-11-19-workflow-speed/changed-files.txt)
- Scope paths: `hooks/`, `skills/`, `tests/`, `tools/`
- Next safe action: owner restarts sessions to load 2.10.0 and accepts it; owner removes the worktree D:/workflow-axa-speed and branch speed/2.10 (the hook refuses it from this session, E18)

## Working context
- Owner: Gazoh; repository D:\workflow-axa-speed (worktree of D:\workflow-axa), branch speed/2.10 at 1a0d523; created under offer #2
- Rules: READY / AGENTS.md, START.md, CORE.md, READINESS.md, TASK-FOLDER.md, refactor recipe read; rules_stamp NONE (installed 1.9.0); docs_check 0 blocking, 9 notes / scope: this task / limits: none
- Evidence: FINDINGS E1-E6; research by three subagents in this session (Matt Pocock, Lauren Tan/pstack, workflow-axa cost map)
- Test output: .artifacts/2026-11-19-workflow-speed/ (in the worktree); cleanup when the task is delivered

## Goal and acceptance
Make a workflow-axa flow faster without making it less correct: items 1-16 of the comparison the owner approved in chat on 2026-11-19 ("Do all of it").

## Agreement
Agreement 1 (agreed by the owner 2026-11-19: "Agree").

Requirements (source: the 16-item comparison the owner approved in chat, "Do all of it", plus D1-D5):
- R1 Hooks: a call that writes nothing never parses the transcript (item 1); the transcript parse reads only what was added since the last call (item 2); the after-call hook no longer runs on Read and loads the old-task code only when an old pre-offer task exists (item 3); each hook event starts at most one Python process (item 4).
- R2 Reading: the router reads only its SKILL.md, flows/INDEX.md and the one recipe; rare sections (old pre-offer tasks, host goals, paid runs, report cleanup, setup) move to files read only when their case comes up (item 5). RULES.md no longer re-reads START.md and CORE.md (item 6). Each repeated rule has one owner file; other files link to it in one line (item 7). Rules a script already checks shrink to one line that names the check (item 8).
- R3 Stops: one-ticket work with nothing open gets no separate agreement stop (item 9); grilling asks every open question in one round with a recommendation each (item 10); the lightweight offer is one short message (files, check, why) with only Approve / Change something (item 15, D1).
- R4 Review: a one-ticket diff with no blast-radius trigger gets one reviewer covering both axes; larger or risky diffs keep two (item 11). A finding counts only with a reproducing command or a concrete line and failure (item 12). docs_check runs once per task phase that needs it instead of three times (item 13).
- R5 Execution: each recipe's steps are copied into the todo list, and every subagent brief says the bar in the brief is the whole bar (item 14); multi-ticket work starts each ticket in a fresh subagent or after /clear (item 16).

What happens:
- Owner: fewer questions on small work; the same two gates on anything bigger; the offer question stays the only implementation approval.
- Agent: reads about 10k words instead of about 25k before code on a bug fix; tool calls stop waiting on a transcript parse.
- Hook: same allow/refuse decision for every recorded case as today; on an error it still refuses writes.

Stays the same: the offer and its one question for every change (D1); the approval hook and what it protects; record.py and offer formats; existing task folders, offers and pre-offer approvals; report renderer and design; Codex copies (handled at release).

Not included: merging into main, pushing, release and reinstall (each needs the owner's later approval, D2/D4); fixing the Altinstar approval failures (separate investigation); new skills.

Acceptance:
- A1 A one-ticket bug fix reads at most 10k words of workflow text before code (measured by the new measuring script).
- A2 With a 20k-event transcript, a read-only Bash call's hook time stays within 50 ms of a 1k-event transcript; Read starts no hook.
- A3 The full suite and tools/validate.py pass; no test is removed or weakened.
- A4 Recorded approval cases (existing fixtures plus new characterisation fixtures) give the same allow/refuse result before and after.
- A5 A live bug-fix pilot on the new version finishes with the same result as on today's version, in less wall-clock time and fewer tokens, within the 50 USD cap (D5).
- A6 A one-ticket bug fix asks the owner at most one approval question (the offer) before code.

Assumptions you can reject:
- Item 4 means one process per hook event; the before-call and after-call events stay separate processes, because the host starts them separately.
- docs_check keeps its readiness run (it blocks on broken required reads); the clarify and delivery runs check only changed files.
- Work happens in D:\workflow-axa-speed on speed/2.10 from main 1a0d523 (D3), with commits after each green round (D2).
- Subagents work on separate files in parallel; I review and merge their results.

## Outcome
Delivered 2026-11-19 as partial: everything was built and tested, but one acceptance target was missed (A1) and the review-coverage check could not run (no completion baseline).

Asked: make workflow-axa faster without making it less correct (items 1-16, agreement 1), plus the owner's Hooqd approval bug report (T9, offer #4). Built on branch speed/2.10 in D:/workflow-axa-speed, commits 122b2aa, 7906ece, 8e3b87e, 10a1e47, 470e793, 3972094 (64 files). Not pushed, not merged; D:/workflow-axa untouched.

Verdicts:
- R1 hooks: verified (V2, V10): read-only shell 354-537 ms -> about 190 ms flat; Read 160-180 -> about 105 ms; Edit 386-613 -> 363-419 ms. Read stays in the after-call matcher (legacy fingerprints, E7).
- R2 reading: partial: router 14,536 -> 8,145 words; bug path 28,726 -> 20,059; before code 17,858. The router still reads RULES.md and TASK-FOLDER.md (V7 Spec 3).
- R3 stops: verified in text and tests (V3, V9); live pilot asked one approval question where 2.9.2 asked four (V11).
- R4 review: verified (V3, V9). "Modest diff" for one reviewer is about 300 changed lines, an agent choice (E12).
- R5 execution: verified in text and tests (V6, V9); not yet observed in a multi-ticket live run.
- T9 Hooqd refusals: verified (V9, V12).
- A1 (<= 10k words before code): failed, 17,858 (V10).
- A2: partial: read-only hook time flat across 1k-20k events; Read still starts one hook process.
- A3: verified: full suite passes except the documented intermittent lock test, which passes on rerun (V9); no test removed or weakened (V7 Spec).
- A4: verified by characterisation and equivalence tests (test_hook_speed, test_shadow_comparison) and V7/V12 probes.
- A5: verified on one sample each (V11).
- A6: verified on the live pilot (V11).

Reviews: Standards and Spec reviewers on 1a0d523..8e3b87e (V7); one independent reviewer on 8e3b87e..470e793 (V12); all findings fixed except Standards F2 (forged event cache, low, pre-existing class of weakness: owner decision). completion_check.py check: exit 2, no baseline was recorded when execution started, so "every change reviewed in its current form" is not machine-proven.

Agent decisions (by: agent) for the owner to see: D12 (T9 as a one-ticket offer); E12 one reviewer up to about 300 changed lines; T2 kept Read in the matcher; T5 made no completion_check change; T6 did not keep large single tickets in the session.

Open follow-ups: misleading refusal for shell chains with variable paths (E16); forged-cache hardening (V7 F2); older offers.py copies reject an offer with "lightweight" (V7 Spec 4), so release must update every copy together; rules version.json string not bumped although READINESS.md changed; A1 gap.

Kept evidence: .artifacts/2026-11-19-workflow-speed/ (baseline.json, r1.json, r2.json, final.json, suite logs, review probes, pilot/). Scratch to remove after the owner's decision on merge: baseline-tree/, the pilot fixtures in D:/workflow-axa-pilots/2026-11-19-workflow-speed/.

Next safe action: owner decides whether to merge speed/2.10 into main (live hooks switch at once), release as 2.10.0 and reinstall; or ask for another round on A1.


Release 2026-11-19: 2.10.0 released under offer #5: main fast-forwarded, release commit 17cc1ec pushed, Claude plugin and Codex copies updated (FINDINGS R1, R2). The worktree and its merged branch remain (E18).
