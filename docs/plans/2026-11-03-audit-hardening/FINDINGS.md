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
