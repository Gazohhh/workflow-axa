# Findings: approval gate false refusals

Owner request (2026-11-12): "Alright do all the follow-ups as well" (follow-up 3 of task 2026-11-12-owned-skills-and-repo-test-run: the gate refused the owner's "no review.html is needed"). Related: docs/RULE-CONTRACTS.md hook candidates 1 and 6; the recorded Altinstar approval failures (10 denied edits, 24 failed approval checks, requirement IDs read as revisions, worker-session approval problems, 90 goal-stop blocks), which must be reproduced from real transcripts before any hook change. AGENTS.md: develop hook candidates in an isolated copy first.

## Open questions (sent 2026-11-12, round 1)
Q4 What does this task cover?
  a) First reproduce the recorded Altinstar approval failures from the real transcripts, then fix the confirmed false refusals together with hook candidates 1 (report waiver wording) and 6 (plan waiver), built and tested in an isolated candidate copy. Recommended: a
  b) Only hook candidates 1 and 6 now; the Altinstar failures later.
  c) All 6 hook candidates from docs/RULE-CONTRACTS.md, plus the Altinstar failures.


## Answers (round 1, 2026-11-12, owner via question tool)
- Q4: c (all 6 hook candidates from docs/RULE-CONTRACTS.md plus the Altinstar failures)


## Reproduction (2026-11-12, read-only research subagent; sources: ~/.claude/projects/d--Altinstar-Altinstar-react session 64f51ac2-... and subagents/, this repo's session 25eea459-...)
- E1 R1/R2 read as revisions: reproduced (11-04 10:29-17:20, main and worker); fixed in rc.4 (phase_gate.py:84-85 matches lowercase rN, plan-rN/review-rN, "revision R7"); pinned by tests/test_gate_regressions.py AltinstarRegressions.
- E2 still open, related: checkpoint() (phase_gate.py:1266-1268) recognises only exactly "## Current checkpoint"; Altinstar used "### Current checkpoint (D4)", so the whole PLAN is scanned and an old "approved r7" elsewhere can outrank the current approval.
- E3 "24 failed approval checks" = 9 unique denials: (a) 11-05 11:46-11:52 quote "Approve D5 plan and D5-A7" (2 main, 5 workers): the report was named only inside the AskUserQuestion text, which pre-rc.4 did not count as presentation; (b) 11-04 15:46 worker: approval question named no report and no "no report" words: refusal by design.
- E4 worker approval problems: mostly by design (a linked worktree never borrows another worktree's records, :1858-1861, :1950; stale PLAN copy there; main-checkout workers repeat the main refusal). Message could name the stale copy.
- E5 "90 goal-stop blocks" = 33 user entries from the host's /goal Stop evaluator, not a workflow-axa hook; workflow-axa's own Stop hook stays quiet while waiting since rc.4 (pinned test passes).
- E6 "10 denied edits" undercounted: 21 unique denials up to the retro (9 main, 12 workers); also 2 "current task changed" and 1 unattributable inline python write, both intended.
- E7 2026-11-12 "Yes go" refusal: reproduced, open. (1) NO_REPORT (:87) misses "no review.html is needed" / "no need for a review"; (2) the waiver is judged one quote at a time (presentation_start :1420, consent_at :1395, approval_problem :1741), so an earlier waiver message plus a later short "Yes go" never combine; (3) the agent's recorded quote dropped the leading "Sure".
- Code areas per hook candidate (docs/RULE-CONTRACTS.md): 1 NO_REPORT :87, report_problem :1810, presentation_start :1420, approval_problem :1741; 2 approval_problem near APPROVAL :70; 3 review_ui_diff.py cues from authority_problem/judge :2228; 4 shell_writes :525, git_writes :387, Project.is_record near :216; 5 small_route_problem :1659, small_change :1574; 6 waived path in approval_problem :1731-1745, report_problem :1815, presentation_start.
- Regression ideas: checkpoint heading variant; waiver wording; waiver + short approval; report named only in the question (pin rc.4); linked worktree stale record message.

## Open questions (sent 2026-11-12, round 2)
Q6 Report and plan waivers (candidates 1 and 6): what should the gate accept?
  a) The owner's own words declining the report or the plan in any owner message of this task after the plan is shown or in the same answer, matched by a wider word list ("no report", "no review.html", "no html", "no need for a review/report", "don't need to see the plan"); the Approval line quotes that message and the approval answer, both whole. Recommended: a
  b) Only the wider word list, still inside the single quoted approval answer.
  c) Keep today's narrow rule; the agent asks for "no report" words when needed.
Q7 Agreement before approval (candidate 2):
  a) Block implementation writes while the checkpoint Agreement line is not agreed, waived, legacy or not required (combined-gates answer counts). Recommended: a
  b) Warn only (the agent sees a note), never block.
  c) Leave it to instructions.
Q8 No new CSS and small-change contents (candidates 3 and 5): block or warn?
  a) Warn only: the gate tells the agent when an edit adds a stylesheet rule, <style>, style="" or (on the small route) a new tag or class; the agent must then ask DESIGN.md rule 4's question. Never blocks, because the cues also match legitimate code. Recommended: a
  b) Block those edits unless a recorded owner exception covers them.
  c) Leave both to instructions.
Q9 Bulk deletes of test output (candidate 4):
  a) Block `git clean`, a recursive delete of `.artifacts` itself and wildcard deletes under `.artifacts`; single named files stay allowed. Recommended: a
  b) Warn only.
  c) Leave it to instructions.


## Answers (round 2, 2026-11-12, owner via question tool)
- Q6: c (keep today's waiver rule; no change to candidates 1 and 6)
- Q7: "i dont understand explain better" (open; re-asked in plain words as Q7b)
- Q8: a (warn only for new CSS and small-change contents)
- Q9: a (block bulk deletes of .artifacts: git clean, deleting .artifacts itself, wildcard deletes under it)
- Q7b (sent 2026-11-12, round 3): The workflow has two separate yeses: first "yes, this is what we build" (agreement), later "yes, start coding" (plan approval). Today the hook only checks the second one. Should the hook also refuse code changes when the first yes is missing from the record?
  a) Yes, refuse code changes until the agreement is recorded; a single "yes to both" answer counts, and old tasks marked legacy still pass. Recommended: a
  b) No refusal; only a warning to the agent.
  c) No change.

- Q7b: a (the hook also refuses code changes until the agreement is recorded; a single "yes to both" counts; legacy passes)

- Q13 (sent 2026-11-12): agreement 1 in PLAN.md ## Agreement. a) Agree. Recommended: a  b) Change something (say what).

- Q13 answered 2026-11-12 (owner via question tool): "a) Agree (Recommended)".


## Plan review (2026-11-12, fresh subagent, plan-review skill)
- Must-fix, resolved in TODO r1 before presentation: T0/T8 candidate had no task records (records committed on main first, candidate never edits docs/plans); T8 commit by explicit paths and the owner-OK steps named; T2 existing test helpers lack an Agreement line (helpers get a default line; files named); T3 had added recursive deletes under .artifacts beyond the agreement (dropped).
- Should-fix, resolved: T2 choices stated (plain "Agreement:" accepted, "not agreed" negative, single-gate and legacy tasks unchecked, Agreement line only, scope = writes the gate already checks); T3 placement after scan/active check, git clean -n allowed, more path forms tested; T4 uses the existing PostToolUse output and review_ui_diff.py PATTERNS, no new script or registration, "adds" defined for Write; one "application file" definition; T7 adds the hooks.json description; T5 says "differs" not "outdated". Note: T1 pins "## Current checkpoint (date)" headings.
- Q14 (sent 2026-11-12): approve plan r1 (TODO.md T0-T8) and the steps T8 names as needing the owner's OK (worktree and branch, commits, merge into main, verification_summary.py --run --write, push, reinstall)?
  a) "Approve r1, no report" (no HTML plan report; the plan is in TODO.md). Recommended: a
  b) Make an HTML plan report first.
  c) Change something.

- Q14 answered 2026-11-12: "Approve r1, no report".

- E8 (2026-11-12): after an assistant message containing "**Plan r1**" and the path `docs/plans/2026-11-12-approval-gate-false-refusals` followed in the same message by an AskUserQuestion, the owner chose "Approve r1, no report" twice; the gate still said it "found no presentation of this task's plan in this session". Suspects: the presentation and the question in one assistant message, or the backticked path. To reproduce in T2/T6 work; the owner was asked to type the approval as a plain message.

- E9 (2026-11-12): the owner typed "Approve" after the plan r1 presentation. The gate quote rule needs at least three words and, without a report, the words "no report" in the quote, so a clear one-word approval cannot be recorded. Candidate for this task's scope review; the owner was asked once more for the full words.

- Q14 final: the owner typed "**Approve r1, no report**" (2026-11-12) after the plan r1 presentation.

- E8 cause (2026-11-12, read-only code reading, hooks/phase_gate.py:1168-1170): a chat presentation counts only when TASK_PATH finds the task path followed by "/" (the code appends "/" only at the end of the whole text). The presentation "Plan r1 for docs/plans/2026-11-12-approval-gate-false-refusals is unchanged" had the bare folder name, so chat_presented never recorded r1; the earlier message had the path only inside a link to TODO.md but no "r1". Candidate fix for this task: accept the bare folder path. Presented once more with docs/plans/2026-11-12-approval-gate-false-refusals/TODO.md and r1.

- Q14 final answer 2026-11-12 (typed, after the plan r1 presentation naming docs/plans/2026-11-12-approval-gate-false-refusals/TODO.md): "Approve r1, no report".
