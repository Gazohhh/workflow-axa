# Findings

## Evidence
- E1: `hooks/phase_gate.py:962-973` `human_words` drops delegate hand-backs (`DELEGATE_REPORT`), T3 handoffs and restart notes (`HOST_NOTICE`), but not T3's agent-sent marker. Probe: `human_words('[T3 Code: the agent in T3 thread "90c9636a" sent this message, not the user.]\n\nyes') is None` → False on ee0e979.
- E2: `hooks/approval.py:525-528` (`decide`) runs `RESTRICTS` (`phase_gate.py:1668`) on the whole message. Probe: a fenced paste "only 3 failed, but fine" matches → True.
- E3: `approval.py:1326` `cannot_place` runs `RUN_TIME_REDIRECT` (`:1240`) and `INDIRECT_WRITE` (`:1255`) on the raw command, heredoc bodies included. `another_worktree` (`:1462`) refuses when it is true and other worktrees exist (`:1475`). Probes on ee0e979, all True: `sh -n deploy/x.sh`, `grep -n 'x$' f 2>$null`, `adb shell sh /data/local/tmp/x.sh`, `git commit -m 'see sh x.sh'`, a record.py heredoc whose body says `sh -n x.sh -> $5`, `bash <<'EOF'\nrm "$p"\nEOF` (intended), `sh deploy/x.sh` (intended).
- E4: live reproduction in this session: a scratch `sed -i 's/...$/.../'` was refused with the same message, because the pattern held a `$`.
- E5: `skills/workflow/scripts/offers.py:218-219` `_covers("a/b/", "a/b")` → False.
- E6: `approval.py:838` `CUSTOM_PROPERTY` `--[\w-]+\s*:` makes line 0 of `protected $signature = 'x {--dry-run : Only show}';` a style line. `touches_styling` (`:927-936`) has `rel` available to pass down.
- E7: `skills/workflow-execute/SKILL.md:25` is the only instruction to run `completion_check.py baseline`, inside the lightweight-edit paragraph; "Before you start" (`:12-19`) does not name it. `completion_check.py:117` raises "no baseline".
- E8: `open_items.py:60-71` `record_problems` is shown by `--task` (`:97`). Older PLANs use "Implementation: complete …" (for example docs/plans/2026-10-29-record-lifecycle/PLAN.md:6).
- E9: `hooks/duplicate_skills.py:179-190` `session_start` checks duplicates, the rules copy and overlapping plugins only. `skills/workflow/scripts/settings.py:51-58` reads a missing settings.json as CSS off without a note. On this machine C:/Users/Cem/.workflow-axa/ holds only settings.json (`"css": "on"`); ARTIFACTS.md is missing while the global CLAUDE.md imports it.
- E10: `approval.py:817-821` `names_operation` matches exact operation text, case and spacing ignored; `validated` (`:728`) and `project_offers` (`:652`) are the existing offer checks that `run_approved` reuses.

## Journeys
- J1: owner approves or narrows an offer in a T3 thread where an agent also posts (E1, E2).
- J2: an agent in a linked worktree runs a read-only or device command (E3, E4).
- J3: an offer that lists `folder/` deletes the folder (E5).
- J4: a PHP edit on a machine with CSS off (E6).
- J5: a session starts execution and later runs the review check (E7, E8).
- J6: a session starts on a machine with missing ~/.workflow-axa files (E9).

## Decision check
- Q (agent's own, settled): ignore agent-marked messages completely, pauses included. The request says "make marked messages not-owner"; recorded as an assumption in the Agreement.
- Q (agent's own, settled): R9 warns only for the template states in progress, implemented, partial (E8).
- Proposal option (c), questions ending in "?" never narrow: not taken. The coordinator's brief says keep "only the tests?" as a narrowing.
- Break-it notes: a `python - <<EOF` body still counts (SCRIPT_READER); a commit message naming another worktree's path is not a write there; the `run:` text is compared exactly, so `sh x.sh; rm y` does not match `run: sh x.sh`.

## Check results
- V1: baseline, see PLAN "Baseline before this change".

- E11: correction to the proposal. On ee0e979 an agent-marked "yes" already approved nothing, because the marker text keeps the message from matching an approval word exactly (the "it cannot approve" subtest passed before the change). What agents could do was narrow or withdraw an approved offer (E1, V2).
- E12: pre-existing limit, unchanged: `adb shell "echo $(rm $p)"` passes on ee0e979 and after, because `cannot_place` does not read a `$(...)` substitution as its own command. Other limits kept: an unfenced paste still narrows; the session-start check runs only at session start.
- E13: live reproduction during this task: the installed hook (D:/workflow-axa, unchanged) refused a `record.py append` heredoc whose body named `$p`, the R4 false refusal.
- V2 (T1, red): `python -X utf8 -B -m unittest discover -s tests -p "test_approval_hook.py" -k another_agent -k fenced_or_quoted` on ee0e979 plus the new tests: `FAILED (failures=5)` (agent narrowing and withdrawal; three fenced or quoted pastes).
- V3 (T1, green): same command after the change: `Ran 2 tests`, `OK`. Whole file: `Ran 180 tests in 141.485s`, `OK`; `test_phase_gate_hook.py`: `Ran 97 tests in 93.907s`, `OK`.
- V4 (T3, red/green): `-p "test_open_items.py" -k review_baseline` on the old script: `FAILED (failures=4)`; after: whole file `OK`.
- V5 (T4, red/green): `-p "test_duplicate_skills_hook.py" -k machine_files` on the old hook: `FAILED (errors=1)` (no note printed); after: `Ran 47 tests in 11.747s`, `OK`.
- V6 (T2, red/green): `-p "test_approval_hook.py" -k write_nothing_here -k still_judged_by_it -k run_operation -k console_signature` on the old hook: `FAILED (failures=10)`; `-p "test_offers.py" -k FolderPaths`: `FAILED (failures=1)`. After the change and the review repairs: `Ran 3 tests … OK` (last run, after the F8 repair); `test_offers.py` `Ran 26 tests … OK`.
- Review S1: independent subagent (code-review, both axes, blast radius) failed: 4 important (F1 heredoc bodies of path-named shells and builtins dropped; F2 `-m` blanking across the command and inside `"$(...)"`; F3 facts cache key not bumped; S1 `run:` matched without case and spacing) and 1 nit (F4 `>$null$p`). All repaired with regression subtests.
- Review S2: same reviewer failed: F5 unquoted heredoc to record.py or `git commit -F -` runs `$(...)`; F6 `-m` match crossed a line break; F7 `git` as another program's argument. All repaired with subtests.
- Review S3: same reviewer failed: F8 (nit) a `@"…"@` block dropped with a quoted record.py heredoc. Repaired with a subtest.
- Review S4: same reviewer passed: the F8 repair holds, nothing new.
- V7 (whole task): worktree at ee0e979 plus diff sha256 67b1422b9d5eda000efec99e250aeecd1c82921839aaf604b5b70bd685247242 (snapshot S4), Windows 11, Python 3.14.2. `python -X utf8 -B -m unittest discover -s tests -p "test_*.py"`: `Ran 1736 tests in 715.423s`, `OK (skipped=14)` (baseline 1727, OK, 14 skipped; 9 new tests). `python -X utf8 -B tools/validate.py`: PASS with the same existing NOTE as the baseline. UNTESTED — a live T3 session with an agent-sent message, a live PowerShell or adb run, and these hooks installed as the live plugin (D:/workflow-axa is unchanged).

- Review S1: code-review subagent ad40af97 (independent) failed: whole diff, Standards and Spec, blast radius (F1-F4, S1)
- Review S2: code-review subagent ad40af97 (independent) failed: repair diff for S1 (F5-F7)
- Review S3: code-review subagent ad40af97 (independent) failed: repair diff for S2 (F8)
- Review S4: code-review subagent ad40af97 (independent) passed: repair diff for S3; the final state of all 11 files (whole-feature review was S1 plus these repair reviews)
