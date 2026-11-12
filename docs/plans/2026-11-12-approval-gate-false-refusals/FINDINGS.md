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


## Checks
- V1 T0 (2026-11-12): candidate worktree .artifacts/2026-11-12-approval-gate-false-refusals/candidate on branch gate-rc38 at c3a966b. Baseline in the candidate (Windows 11, Python 3.14.2, Git 2.38.0): suite Ran 1206, FAILED (failures=1, skipped=13): test_package.PackageTests.test_current_package, first error: validate FAIL "Broken/outside relative link in docs/plans/2026-11-12-rules-audits-altinstar-pletrix/altinstar-proposed-AGENTS.md". Cause: the Altinstar proposal copy committed in c3a966b (its links point into Altinstar). Fixed on main by renaming it to .txt (validate.py PASS on main); the candidate keeps the old copy until the T8 merge, so this one failure is an existing, known baseline failure in the candidate. Output: .artifacts/2026-11-12-approval-gate-false-refusals/baseline-*.txt

- E10 (2026-11-12): a builder subagent working in the linked candidate worktree was refused on its first edit: the gate checks the approval against the subagent's own transcript, and from a linked worktree it does not find the main session's transcript (workers in the main checkout did write in the previous task). Same family as E4. Not fixed in this task (not in agreement 1); recorded as a further hook candidate. T1-T6 are built in the owner session instead.

- E8 correction (2026-11-12): the cause recorded above is wrong. TASK_PATH (hooks/phase_gate.py:65) accepts whitespace after the folder path, so the bare path did count. The cause of the refusals of the AskUserQuestion answers and of the typed "**Approve r1, no report**" (bold markers) is not confirmed; suspects: answers given in the same assistant message as the presentation, and the markdown asterisks in the typed answer breaking the whole-message match. Not investigated further in this task (outside agreement 1); hook candidate.

- E11 (2026-11-12): the owner session's own edit in the candidate worktree was refused as well: the main-checkout presentation and approval do not carry over to a linked worktree (by design: worktree approvals are not shared automatically; memory rule). T0's assumption that a committed PLAN copy is enough was wrong. Q15 asks the owner: reconfirm r1 inside the worktree (Reconfirmed line in the candidate's PLAN copy, never committed there) or build in the main checkout instead.

- Q15 answered 2026-11-12: "Build in the main checkout" (D1).

- V2 T1 (2026-11-12, main checkout on c3a966b + working changes): red first: CheckpointHeadingRegressions.test_a_deeper_or_suffixed_checkpoint_heading_is_the_checkpoint failed ("approves r1, but the checkpoint names revision r7"); the two guard tests passed before and after. Fix: checkpoint() in hooks/phase_gate.py accepts any heading level with text starting "Current checkpoint" and ends at the next heading of the same or higher level. Green: CheckpointHeading 3 OK; test_gate_regressions, test_phase_gate_hook, test_followup_boundaries, test_rc3_reliability, test_session_recovery all OK.

- E12 (2026-11-12, incident): the live gate of this session loads hooks/phase_gate.py from D:\workflow-axa itself (proven: the PreToolUse hook raised NameError agreement_problem, a name that exists only in the working copy here). D1's premise ("running sessions load hooks from the plugin cache") was wrong. The T2 change landed in two edits; between them the live gate crashed ("the phase gate failed (NameError ...)") and refuses every project write, including the repair. Asked the owner to run `git -C D:\workflow-axa checkout -- hooks/phase_gate.py` (restores the committed gate; loses the T1 change in that file only; tests stay). Next: build the hook changes in a plain copy under .artifacts, test there, then write the finished file into hooks/ once.

- V3 T1 + T2 in the working copy (2026-11-12): after the owner restored hooks/phase_gate.py, the copy reproduced the red tests (CheckpointHeading 1, AgreementGate 3 subtests). T1 and T2 code applied in the copy only; green: test_gate_regressions, test_phase_gate_hook (helper adds a default Agreement line for two-gate tasks), test_followup_boundaries, test_rc3_reliability, test_session_recovery all OK. The V2 entry above describes the same T1 change, which was lost by the restore and re-applied here.

- V4 T3 in the working copy (2026-11-12): red first: BulkArtifactDeletes.test_bulk_deletes_are_refused failed for all 7 commands (allowed today). Added bulk_delete() (git clean except -n/--dry-run; delete of .artifacts itself; wildcard delete under .artifacts) checked in judge after the active and protocol checks, before the exemption filter can return early. Green: BulkArtifactDeletes 2 OK incl. "cd .artifacts && rm *" (the parser follows cd); all five gate test files OK.

- V5 T4 in the working copy (2026-11-12): red first: test_gate_notes.StyleNotes 3 tests failed (no note today). Added style_notes() in the existing PostToolUse output (no new script or registration): styling cues from review_ui_diff.py (inline-or-runtime-style, style-injection-or-css-in-js) plus stylesheet rules in .css/.scss/.sass/.less/.styl files, counted before and after the edit (Write: against the committed file); small change: tags or class names that are new in a listed file. Never refuses; only in active sessions; Markdown, docs/plans, .artifacts and test files excluded. Two fixes during green: the cue module needs registering in sys.modules while it loads (dataclasses), and line-based comparison noted unchanged styles (switched to match counts). Green: test_gate_notes 4 OK; all five gate test files OK. Timing: 0.57 s for a 1.1-million-character edit (5 s hook limit).

- V6 T5 in the working copy (2026-11-12): red first: LinkedWorktreeCopies.test_a_differing_plan_copy_is_named failed (no note). Added worktree_copy_note() appended to refusals in judge: in a linked worktree (.git file with gitdir .../.git/worktrees/...), when the task's PLAN.md differs from the main checkout's copy, the message says so; refusal unchanged. Green: LinkedWorktreeCopies 2 OK; all six gate test files OK.
- V7 T6 pins (2026-11-12, tests only): "R6 (FSR)" and "D4-R6" are not revisions: passes on the live gate. E3a pin: a report named only inside an answered AskUserQuestion counts as presented when the host recorded its fingerprints (report read before asking; mark at the answer): passes on the live gate and the copy. Without the fingerprint rows it is refused ("cannot verify report evidence"), which is the later fingerprint rule working as designed, not a defect; the first draft of the pin left them out.

- V8 code review of T1-T6 (2026-11-12, fresh subagent, code-review, independent, axes sequential): no crash path found; all six gate test files OK. Must-fix: git clean matched in raw text (refused `git commit -m "... git clean ..."`). Should-fix: STYLE_RULE quadratic on long lines (60 KB 1.4 s, 200 KB 15 s); T2 would refuse three real tasks in other repos (Pletrix web-app-parity-check "agreed ... awaiting-approval"; Hooqd kit-token-enumeration and putten-board-size with no state word); missing timing test. Notes: style_notes exception could drop fingerprints; costs in sessions without the workflow; T5 note should name both paths and only follow approval refusals; documented-limit list for T3 (missed forms) and T1 (a `# ` line inside a fenced block ends the section).
- V9 repairs in the working copy (2026-11-12): git clean read from parsed words (split_bodies/segments/lex), new tests: commit message, echo and heredoc mentioning git clean allowed, `git -C . clean -fd` refused; AGREED/NOT_AGREED: the first state word decides (new allowed case "agreed ..., awaiting approval"); STYLE_RULE without colon backtracking and NOTE_LIMIT 4,000,000 characters; style_notes checks the active session first and runs in its own try; T5 note names both copies and is added only to approval refusals; new timing test (long `{b:b:...` line + 20,000 rules) under 3 s. All six gate test files OK. Repair diff: .artifacts/2026-11-12-approval-gate-false-refusals/phase_gate-repair.diff. Hooqd kit-token-enumeration and putten-board-size records stay refused until their Agreement lines say agreed (T7 upgrade note).

- V10 re-review of the repairs (2026-11-12, same reviewer): S1, S2, S3, Spec1, Spec2 (Pletrix), Spec3, Spec5 fixed; S4, S5, Spec4, Spec6, the two Hooqd records and the "approval" substring decision for the worktree note accepted as documented (T7). New should-fix found and repaired: `bash -c` / `powershell -Command` wrappers around git clean (tests added, red then green), then the reviewer's slowdown note (read only the first -c flag; 2,000 repeats now 0.01 s). No exception path found. All six gate test files OK in the copy after the last repair.

- V11 live (2026-11-12): the finished hooks/phase_gate.py copied from the working copy into D:\workflow-axa\hooks in one write (219 insertions, 4 deletions; parses). Full suite on main: Ran 1223, OK (skipped=13); validate.py PASS. Output: .artifacts/2026-11-12-approval-gate-false-refusals/suite-T6.txt, validate-T6.txt

- V12 T7 (worker + owner session, 2026-11-12): RULE-CONTRACTS.md (checked-by lines with current phase_gate.py lines, candidates 2-5 done in rc.38, 1 and 6 owner decision unchanged, new candidates 7 for E8/E9 and 8 for E10/E11, known gaps), hooks/hooks.json description only, SETUP.md (one short "rc.38" row pointing to RULE-CONTRACTS.md and one sentence on local directory marketplaces, trimmed by the owner session to stay within the 2310-word budget instead of raising it), ARCHITECTURE.md, CHANGELOG rc.38, UPGRADE rc.38 (agreement line for two-gate tasks, the two Hooqd tasks, bulk deletes, local hook loading), README, tests/README, version fields 2.8.0-rc.38 (rules stay 1.8.8). validate.py: only FAIL is VALIDATION.md still rc.37 (T8 regenerates it); docs_check 0 blocking. Correction to E9: the worker found no three-word quote minimum in phase_gate.py; E9's three-word claim is unverified.

- V13 whole-feature review (2026-11-12, fresh subagent, code-review + AUDIT, independent, axes sequential): all 38 RULE-CONTRACTS.md line citations correct; documented behaviour and limits match the code; Q6 c holds (waiver logic unchanged); the six two-gate PLANs in this repo pass the agreement check; hooks diff limited to phase_gate.py and the hooks.json description; no live-check claim. Must-fix (records): stale checkpoint and TODO T0/T7/T8 states: fixed. Should-fix: SETUP.md row named after a version: renamed "Agreement/deletes". Notes fixed: refused-state list says "such as ... awaiting"; UPGRADE no longer names client task folders; the gate's refusal text now lists "not required" (changed in the working copy, gate tests OK there, then copied live; live file parses). validate.py: only VALIDATION.md rc.37 remains (T8).

- V14 T8 VALIDATION (2026-11-12, working tree on c3a966b): first verification_summary.py --run --write ran the suite while VALIDATION.md still said rc.37 (4 failures, all from that line) and quoted the validator's rc.37 error into its own table, which made every later validate run fail on it. The quoted cell was blanked by hand ("regenerated below") and the tool run again: exit 0; 1223 ran, 1210 passed, 13 skipped, 0 failed; validate.py PASS. Output: .artifacts/2026-11-12-approval-gate-false-refusals/verification-summary-2.txt. Tool defect noted for later: a failing validator message that names the old version keeps VALIDATION.md failing.
