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
