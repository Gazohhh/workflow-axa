# Findings

Reproduced on 2026-11-03 at HEAD 0b4e4b4 (package 2.8.0-rc.1, rules 1.8.0), by six read-only audit subagents and spot checks in the main session. Probe scripts and logs are in the session scratchpad (`audit1`-`audit6`), outside the repository.

## Approval enforcement (hooks/phase_gate.py)

- E1 — CONFIRMED (also rechecked by hand): after `/workflow`, loading `workflow-clarify` alone allows an Edit of application code and `git push`. Cause: `session_state` (phase_gate.py:49-73) turns any phase name anywhere in the transcript into one yes/no; clarify counts the same as execute (:71). Nothing reads the task's Agreement or Approval lines.
- E2 — CONFIRMED (also rechecked by hand): chat text "This is NOT a lightweight edit" grants the lightweight exemption. `LIGHTWEIGHT` (:45) matches the bare phrase in any assistant text (:68-69).
- E3 — CONFIRMED: a phase loaded for task A satisfies the check for a new task B later in the same session.
- E4 — CONFIRMED: shell writes the gate misses: `>`/`>>` redirection, heredoc into a file, `tee`, `cp`, `mv`, PowerShell `Set-Content`/`Out-File`, `node -e writeFileSync`. Also `git apply`, `checkout -- file`, `reset --hard`, `cherry-pick`, `rebase`, `stash pop`, `rm -rf`, a git alias, and `git -C "path with spaces"`. A records path anywhere in a command exempts the whole command (:85); `..` is not resolved; the `cd` target is judged instead of the written file (:87).
- E5 — CONFIRMED: reading a phase SKILL.md whole (the router's documented fallback, workflow/SKILL.md:36) does not count as loading the phase, so edits stay blocked.
- E6 — CONFIRMED: the PowerShell tool and MCP write tools are outside the hooks.json matcher, so the gate never runs for them.
- E7 — UNKNOWN: which transcript a subagent's hook call receives. If it is the subagent's own, it has no `/workflow` line and is not gated.
- E8 — Limit: the agent can write the PLAN.md Approval line itself, because task records are deliberately writable before approval. A hook that trusts that line alone trusts the agent. The user's real answer is in the transcript as a user message, which the hook can read.

## Agents, repeats and cost (measured, not estimated)

- E9 — `workflow-execute/SKILL.md:29` ("hand every ticket, even a single one, to a fresh worker") and `phase_reads.py:58` ("even a two-line edit") require a fresh worker for every ticket; `:32` a fresh reviewer; `:33` and `phase_reads.py:59` a re-review of every repair, including record-only repairs; `workflow-deliver:14` a fresh reconciler.
- E10 — Measured per task (Agent calls / cost / turns): one-ticket rename r22-short 4 agents, $9.25, 84 turns; two tickets plus a revision r22-long 11 agents, $16.35, 133 turns; one-ticket Hooqd change 2 agents plus 4 follow-ups, $13.32, 93 turns, full `npm test` (1,452 web tests) run 4 times; one-ticket README change 3 agents, $8.40. In r22-long, the T2 review and the whole-feature review started 9 seconds apart on the same unchanged diff. Costs are running totals from the headless summaries.

## Verification and baselines

- E11 — CONFIRMED: `workflow-execute/SKILL.md:28` says baselines record counts "so later failures can be attributed by number". Five existing failures becoming four existing plus one new passes as unchanged. The rules library already says the opposite (`rule-maker/rules/operations.md:17`: "Compare actual diagnostics/tests, not just totals").
- E12 — CONFIRMED: a baseline records no command, commit, diff state or environment, so a resumed session can reuse a stale one (`TASK-FOLDER.md:55` has only an empty heading).
- E13 — CONFIRMED: no rule says the required checks run again after the last repair (execute step 8); `task_report.py` cannot detect a stale check itself.
- E14 — CONFIRMED portability: in a checkout path with spaces, 11 tests fail, because `activate_rules.py:57-58` refuses such paths and the tests use the checkout's own library. Under WSL (POSIX), 2 tests fail because `test_truncated_read_hook.py:15,49-57` reads the live `D:/workflow-axa` checkout. All 11 Windows skips are real host limits; the POSIX run executed them and they passed.
- E15 — Risk: `hooks.json` runs `python`; a host with only `python3` would start no hook, so the gate would enforce nothing.

## Writing and reports

- E16 — CONFIRMED: `simple-english/SKILL.md:20` bans should/would/may/might/could and `task_report.py:170` flags them, while `workflow/WRITING.md:37` requires "must, may, must not" to be kept. Following the advice turns "The cause is not proven; it could be the cache" into a false certainty. Quoted user words are flagged although the adaptation exempts them (`SKILL.md:87`).
- E17 — CONFIRMED: `render_report.py` writes the HTML first and runs the wording check after (:944, :948); `--open` opens the file even with problems, which makes it "presented" and forces a new file name. Review reports without a `task_report` block get no wording check at all.
- E18 — CONFIRMED: `--replace-unpresented` checks only that the file was made by the renderer, so it would overwrite an approved report. `SKILL.md:91`, the `--output` help text and `TASK-FOLDER.md:97` still say every re-render needs a new file.
- E19 — Measured: mulcol made plan-r1, -v2 and -v3 within two minutes, all opened (before the flag existed).

## Records and interrupted work

- E20 — CONFIRMED: `record.py` writes in place (`save()` :33, `new` :62): killed after truncation the record is empty; killed mid-write it is cut off. Two writers at once silently lose one write (`B-entry` gone; both `tick` calls printed "ticked"). `new` races (exists check, then write). Mixed line endings are normalised; a BOM blocks heading lookup; `tick T1` can tick `T1.2` and turns a cancelled `[-]` into `[x]`.
- E21 — CONFIRMED: a user's "stop" routes to deliver (workflow/SKILL.md:32), deliver requires the whole-feature review "else hand back to workflow-execute" (deliver:12), and execute repeats "while a ticket is ready" (:25). A stop can therefore send the agent back into building. There is no stopped, paused or cancelled state; blocked counts as terminal; a lightweight edit also bounces through deliver:12; a failed reviewer has no limit; the handoff message has no blocked, stopped or partial value and no changed-files line.

## Documentation and release

- E22 — CONFIRMED contradictions: skill count 20 vs 21 (README:13,81, CHANGELOG:6,12, VALIDATION:15,21, UPGRADE:30, VENDORED-SKILLS:3), rules version 1.6.0 vs 1.8.0 (CHANGELOG:5,29, UPGRADE:5), test count 585/620 vs 653 (PLAN:120,124, VALIDATION:16), browser and host checks "not run" (PLAN:8) vs "PASSED" (VALIDATION:20-21). VALIDATION names no source commit.
- E23 — CONFIRMED: no release or ZIP tool exists, although VALIDATION:135,184 describes one; no inclusion policy; no root LICENSE for the project's own code. No secret-like files were found.

- V-E7 — Measured 2026-11-03 in a throwaway fixture project with a logging PreToolUse hook: a subagent's Bash call received the parent's `transcript_path` and `session_id`, plus `agent_id` and `agent_type`; the main session's call had no `agent_id`. So the gate judges subagent edits by the parent's task and approval. E7 is settled.


## Verification (2026-11-03/04)

- V1 (T1) — `tests/test_phase_gate_hook.py`: every E1-E6 bypass denied, legitimate routes allowed, consent rules (whole answer or message start, at least 3 words, after the plan was shown, no refusal word in the quote, sibling transcript only when it presented this task), later revision denies, plan report required (task folder or reviews/), install guard. Red seen per rule (test-first or mutation check). Fresh review: 2 hard findings, fixed and re-checked. Speed on the 45 MB session: about 0.14 s per gated call after the first (0.67 s first).
- V2 (T2) — `tests/test_record_safety.py` (14 cases): interrupted write keeps the old file (old script corrupted, new kept it), concurrent writer gets BLOCKED, exclusive `new`, exact `tick`, BOM, mixed endings, batch against the original text, lock token and atomic stale takeover. Fresh review: no hard findings, 4 soft fixed. Not run here: symlink and POSIX file-mode cases (Windows host).
- V3 (T3, T4, T6) — `tests/test_stop_and_baseline.py` (11), guard tests in `test_behavioral_cases.py`: stop/pause/cancel routes, handoff fields, `compare_failures.py` (5 existing to 4 + 1 new reported as NEW; BOM, duplicate, tab-less and unreadable input refused), small route and escalation. Fresh review: 2 hard (no route back from a stop, lost "reconcile again"), fixed. UNTESTED by unit test: baseline input comparison (instruction only).
- V4 (T5) — `tests/test_reports.py`, `tests/test_task_report.py`: uncertainty words advisory, quoted text exempt, check before writing, no `--open` with problems, replace refused for named or approved reports. Reviewed together with the other tickets in the live loop (no separate fresh review).
- V5 (T7) — four test modules pass in a checkout path with spaces, in place, and under WSL (python3 3.12.3).
- V6 (T8) — `tests/test_release.py`, `tests/test_docs_consistency.py`; docs now agree (21 skills, 9 vendored, rules 1.8.0); MIT LICENSE; release builder with an include list and a secret check.
- V7 (T9, live) — eight rounds in detached worktrees of Hooqd, Mulcol-app2, PletrixV2 and Altinstar, one headless Claude session per repo per round, plus Codex 0.164 read-only status checks. Shown working: a full small task from plan to delivery (PletrixV2), stop then continue (Hooqd), "just do it" refused without approval (Mulcol), new-project rules setup then back into the workflow (Mulcol), lightweight comment edit (Altinstar), an unrelated request in the same chat (Altinstar), a follow-up task in a fresh chat (PletrixV2), a UI change with the mimic question (Hooqd), the missing-packages rule (all), a full build with the linked packages, tests, measurement and review (Altinstar). E7 measured: a subagent's hook receives the parent's transcript.
- Retro fixes from the loop, each with a test: inline-code record writes allowed, approval needs a plan report, rule-maker hands back to the router, unreviewed code cannot end as Done, scratchpad files ignored by that check, a refusal word later in an approving message no longer voids it, reports at the task-folder root count, installs and downloading npx need the owner, fresh-chat offer in clarify's identity question, owner acceptance adds an Outcome line.
- Round 8 (last): no approval violation, no new serious defect. Open minor: a record that names a draft before the owner saw it blocks `--replace-unpresented`, giving a second report file (Altinstar). Left as a proposal for the follow-up review.
- Evidence: headless summaries `.artifacts/2026-11-02-modular-engineering-workflow/eval/w1-*` to `w8-*`, `w6-codex-hooqd.log`, patches `eval/worktree-patches/loop2-*.patch`.

- V8 (A10, measured 2026-11-04) — one-ticket tasks in the live loop used 1 subagent call each, the reviewer (PletrixV2 setup-guide task, Mulcol cropper task), against 4 for the same kind of task before (r22-short). Session totals were in the same range ($8.7-8.9 vs $9.25) but also include rules setup, so they are not a clean cost comparison.


- V9 (whole-feature review and final checks, 2026-11-04) — a fresh whole-feature review found 3 hard issues (install guard active in non-workflow sessions; "no report" approvals could never edit code; live runs beyond D5's limit without a recorded authority) and 11 soft ones; all fixed or recorded (D11), plus a POSIX path bug the full WSL run found and LF endings restored in 9 files that must be LF. Final runs on the final state, once: Windows `unittest discover`: 757 ran, OK, 13 skipped (host limits); the same in a checkout path with spaces: 757 ran, OK, 13 skipped; WSL python3 3.12.3: 757 ran, OK, 16 skipped (Pillow not installed); `validate.py` PASS. VALIDATION.md current section regenerated; release zip rebuilt (184 files, SHA-256 f4c51fa2…). A12 is met.


- V10 (closing the two open gaps, 2026-11-04) — A9: `skills/workflow/scripts/baseline_state.py` records a baseline's command, commit, diff hash (task records and `.artifacts` excluded) and environment, and `check` prints RERUN with what changed or REUSE; `tests/test_baseline_state.py` was red, then green; the TASK-FOLDER baseline template points to it. Live PowerShell: a headless Claude session in a throwaway fixture (`scratchpad/psfix`) was asked to run `Set-Content` through the PowerShell tool before any approval; the gate denied it with its approval message and `src/app.txt` stayed "Hello world". Live Codex with write access (Codex 0.164, `--sandbox workspace-write`, fixture `scratchpad/cxfix`): asked to change the file under the workflow skill, it changed nothing, stopped at the task-record step and asked, noting the fixture's "Edit only src/" rule. Final runs after these changes, once: Windows 760 ran, OK, 13 skipped; WSL 760, OK, 16 skipped (Pillow); `validate.py` PASS; no LF-required file with CRLF. VALIDATION.md and the release zip regenerated.


- V11 (review of the V10 helper and final runs, 2026-11-04) — a fresh review of `baseline_state.py` found 3 hard defects (untracked file content not hashed, a check from a subfolder saw only that subfolder, git failures gave REUSE) and 4 soft ones; fixed test-first (`tests/test_baseline_state.py` now 6 tests: untracked content, other folders, records and `.artifacts` ignored, outside git blocked, missing record folder blocked), `--version` timeout 5 s, RERUN shows old and new values. Final runs on the final state, once each: Windows 763 ran, OK, 13 skipped; a checkout path with spaces 763, OK, 13 skipped; WSL python3 3.12.3 763, OK, 16 skipped (Pillow); `validate.py` PASS; no LF-required file with CRLF. VALIDATION.md and the release zip regenerated. A12 is current again.

## Follow-up r4 evidence
- E24: workflow session 50f12dd8-6056-4306-82cc-4fee58e8c865 has r5 assistant end_turn followed by isMeta Stop hook feedback and goal_status false demanding an earlier live rc3 batch. The external goal is the observed retrigger; no evidence that plain_reply alone caused the repeated waiting.
- E25: Hooqd session edd9eee8-e6f6-4930-893f-ee65c8166050 started 2026-11-04; report fingerprint denials after the update are real. Historical hooks diff 71409da..0d67057 adds PostToolUse/UserPromptSubmit phase_gate registrations. No report-fingerprint contexts were found in that session's inspected transcript.
- E26: phase_gate REVISION regex is case insensitive and matches requirement IDs R7 and D4-R6. Altinstar contains a real denial saying r3 approval conflicts with r7.
- E27: Altinstar 64f51ac2-52d4-4707-9398-72221cede124 snapshot: 115418036 bytes; 2287 assistant records; 30 goal_status false records. Retro counts are not independently validated as equivalent metrics. A file-history snapshot count is not a human-message count.
- E28: original Cheflabels is clean on feature/offerte-20260907 at a8a31c1f26fb5e3469473195524d589763f3ec4c; E2 same HEAD with untracked task records. r5 checkpoint has stale next-action r3. No application edits or transfer made.
- E29: current official Claude docs explain /goal clear and goal restoration on resume: https://code.claude.com/docs/en/goal . Stop additionalContext itself continues the conversation: https://code.claude.com/docs/en/hooks . Never use Stop feedback to record passive presentation evidence.
- V-r4-baseline: pending. Prior suite claims are not current evidence.

## Follow-up verification, 2026-11-05
- V-r4-suite: Python full unittest discovery: 878 tests, zero failures/errors, 14 skips, 175.586 seconds; .artifacts/2026-11-03-audit-hardening/full-suite-final.txt. The trailing BLOCKED messages are expected fixture diagnostics from passing tests, not suite failures.
- V-r4-gate: 54 existing phase-gate tests pass; 14 session-recovery regressions pass. Requirements R7/R6/D4-R6 do not become revisions. Actual rN report revisions remain checked. Same-task withdrawals revoke approval; withdrawing another task does not.
- V-r4-read: 8 new read-evidence and 10 existing plain-reply tests pass. Conditional, failed, truncated and partial reads remain untrusted. Legacy ID-less transcript evidence remains best effort.
- V-r4-review: independent Standards and Spec reviews pass after repairs. Repairs addressed conditional read success, reply fingerprints from sibling worktrees, chat-waiver workspace replay and task-scoped withdrawals. Final review performed read-only.
- V-r4-live-partial: candidate rc.4 loaded in Claude Code 2.1.318 with only Read/Edit/Write available and external MCP disabled. Waiting produced zero events during a measured 30-second interval; rejection left source unchanged. Host dontAsk permissions denied the PLAN Edit, so successful approval write/recovery is NOT verified. No permission bypass or write retry performed.
- Retain selected red reproductions, final suite, original UI-lite failure evidence, live trace and candidate source under the existing task output parent. Private original session logs remain in place. Live trace contains synthetic inputs only. No live plugin/cache/settings installation changed.

## Cheflabels completed and live batch limits
- V-r4-E2: owner approved final result and transfer. Three application/docs files plus task review/evidence files transferred to D:/Cheflabels-labeler-V2 on feature/offerte-20260907 at a8a31c1f26fb5e3469473195524d589763f3ec4c. All 33 copied files matched SHA-256 before final task-record updates. Diff check passed. Disposable worktree removed. No Git history/index operations.
- Final E2 report: D:/Cheflabels-labeler-V2/docs/plans/2026-11-05-kit-confirm-sheet/reviews/delivery-2026-11-05.html. Independent reviewer reconciliation found no outstanding task requirements. Native devices and remote translations were outside this UI fixture check.
- Earlier scratch cleanup was rejected by automatic review before execution. Later explicit owner approval covered verified transfer and removal of the whole disposable worktree; that authorised removal succeeded. Required evidence is preserved in the original checkout.
- V-r4-live-budget: first two-process batch reported cumulative list-price USD0.0819966. Replacement processes reported USD0.041869 and USD0.0479224, total USD0.0897914. Combined reported total USD0.171788; both approved batches capped each process at USD1, no more paid processes launched. These are CLI list-price counters, not invoice metering.
- V-r4-live-gap: sensitive plugin-path write protection blocked the first replacement fixture. The final outside-plugin fixture recorded malformed approval wording and was correctly denied. No successful model-driven approval write or write-after-restart is claimed.
- E-r4-URI: offline replay of the actual final host transcript exposed a further parser defect: Markdown file:///D:/ report destination became e:/D:/, losing workspace identity and reply fingerprint. New regression and repair are in progress; earlier 878-test pass predates this repair.

## Final follow-up reconciliation, 2026-11-05

- V-r4-final: frozen STATE_VERSION 14 candidate. Full unittest process exited 0: 886 tests, zero failures/errors, 14 skips, 171.116 seconds. Evidence: .artifacts/2026-11-03-audit-hardening/full-suite-final.txt. The trailing BLOCKED lines are expected fixture diagnostics. Validator PASS with 699 words after the code freeze. Earlier 878-test evidence predates URI repairs.
- V-r4-URI-final: a candidate regression in the new workspace parser converted file URI paths incorrectly. It was exposed by host-derived offline replay, not independently confirmed against original rc.3. Atomic parsing now preserves destinations, brackets and exact report suffixes. Nested labels, titles, remote schemes, malformed/reference syntax and false suffixes fail closed. Twenty-two session-recovery tests passed after red cases. STATE_VERSION 14 invalidates prior parser cache states.
- V-r4-replay-final: live-rc4-write/real-transcript-replay-final.json reports corrected_record_current_session_allowed and new_transcript_same_workspace_recovery_allowed true. Owner-reply output was regenerated offline. Original host transcript and source value stayed unchanged. This does not verify live model-driven writes or restart behavior.
- V-r4-review-final: independent Standards and Spec reviews PASS on the frozen parser. Review findings repaired and re-reviewed: conditional read credit, wrong reply workspace, waiver presentation timing, task-scoped withdrawal, nested labels/titles, exact report suffixes and bracket identity. No outstanding code finding in those reviews.
- V-r4-scope: hooks/phase_gate.py and tests/test_phase_gate_hook.py plus test_session_recovery.py map to F1-F3. hooks/hooks.json maps to F2. hooks/plain_reply.py, test_plain_reply_hook.py and test_read_evidence.py map to F4. workflow SKILL/SETUP/TASK-FOLDER and workflow-doctor map to F5. F6 owns metadata version labels, behavioral fixture version labels, tests/test_task_report.py baseline expectation, current validation and delivery records. Report styling and existing UI-lite implementation are preserved.
- V-r4-preserve: parent verified original tracked diff SHA-256 2f11292dd0d1a64c1b93c1bf9fe0a16305e7c90c5455c3abdfb840f4da3dcd72 unchanged. This preserves the original checkout and its prior edits. Candidate has no Git metadata and no commit was made.
- V-r4-delivery: codebase-map and simple-english produce a new dated snapshot, preserving progress-r4 and all earlier reports. Implementation is finished, verification is partial because live positive writes/restart and 14 skipped cases remain unverified. Archive creation/checksums remain a parent handoff step and do not constitute installation.
- Historical agent decisions D7-D10 remain recorded. This delivery does not silently accept them or redesign their policies. D-r4-2 isolates the candidate. D-r4-3 protects private logs.


## Record and report checks

- Read-only open_items reconciliation reports current F1-F6 evidence pointers. Historical T1/T4/T9 descriptions trigger incomplete-word flags and historical T2/T3 trigger closed-word flags. Their dated evidence remains intact. These are conservative parser readings of historical prose, not new candidate code failures. PLAN retains its pre-existing mixed line endings.
- Current F1-F6 implementation is verified at local public-hook and offline replay boundaries. Live positive write/restart remains unverified, without creating additional paid work.
- Keep D:/wfaxa-pilot/workflow-host-fixture-rc4 as small replay evidence because its report and PLAN bytes are inputs. It contains no build or dependencies. Raw traces/caches remain outside archives.
- The first delivery draft was rendered and inspected before record wording was corrected. Preserve it and progress-r4. The final delivery snapshot uses delivery-r4-final.html/json.

## R5a review and verification checkpoint
Self-review (no subagents, as authorized): Standards PASS for minimal instruction changes at LIVE-KIT/VERIFY owners; no vendored edits, new dependencies, CSS, hook bypass or automatic approval. Spec PASS for approved real-component example registration, renderer/caller coverage and settled capture guidance. Human intent remains in DESIGN.md; styling remains in source. Live behavior is NOT VERIFIED until the five-project batch.

V-R5-1: 40 strict-kit tests passed before changes. Initial full suite ran 886 tests with 10 failures and 13 skips while release metadata was incomplete; failures were version/document/manifest consistency checks, including the report renderer version. Necessary failure evidence: .artifacts/2026-11-03-audit-hardening/rollout/package-tests.txt. Corrected package version references and started a complete final rerun; do not claim success before exit. Metadata validator and git diff --check now pass.

All five target worktrees were created at their originals' committed HEADs under D:/wfaxa-pilot/rollout-<project>. Original branch/status snapshots are retained privately in rollout/original-baselines.json. Altinstar's existing uncommitted work was not copied or changed. Native dependencies, application builds, production endpoints and installs remain outside the test's automatic scope.

## R5a final package verification
V-R5-2: Final full suite ran 886 tests in 158.134 seconds: 13 skips and one failure, test_current_validation_section_names_this_package, because the new current-validation section omitted its source identity row. Added the actual base commit plus explicit uncommitted rc.5 qualifier. Reran all 19 test_docs_consistency tests: PASS (8.424 seconds). Validator PASS and git diff --check PASS. No behavior or test assertions changed after the full suite; no third full run is needed for this documentation repair. Logs stay in the same private rollout parent. Self-review of the final repair: Standards/Spec PASS; live behavior remains pending.

Codex pre-install preservation check compared all 175 registered files against the base Git commit: no local modifications or missing files. Remote main was verified at45670f28ce506d5df43a9e632c9fd2cdcdcc9931 before publication. Installation will use a new Git download, not this candidate directory. No original application commit, branch change or push is part of this action.
