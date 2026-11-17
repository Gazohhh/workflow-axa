# TODO

| Ticket | What | Status | Depends on |
|---|---|---|---|
| T1 | Move the worktree onto 00ac3ae, keeping all local work | Verified | — |
| T2 | Run 5's fixes F3, F4 and F6 | Verified | T1 |
| T3 | Checks (F7) | Verified | T2 |

### T1 — Move the worktree onto 00ac3ae, keeping all local work
Status: Verified
Evidence: FINDINGS V1; HEAD 00ac3ae; no conflict markers; each contract row once

What needs to happen: PLAN "How" steps 1-4.

How to verify: the backup exists; `git rev-parse HEAD` is 00ac3ae; no conflict markers (grep); each contract row appears once; `git diff --name-only 00ac3ae` lists only the five tasks' files.

### T2 — Run 5's fixes F3, F4 and F6
Status: Verified
Evidence: FINDINGS V2; test_spar OK with the new F3 and F4 tests

What needs to happen: PLAN "How" step 5, each with a text test written first where SPAR.md names one.

How to verify: test_spar; grep for the stale record lines.

### T3 — Checks (F7)
Status: Verified
Evidence: FINDINGS V3; suite 1512 run, only the 4 known VALIDATION.md count failures

What needs to happen: PLAN "How" step 6.

How to verify: test_spar, test_owned_skills, test_settings, test_approval_hook, test_phase_gate_hook, test_simple_english, test_offers; `python -X utf8 -I tools/validate.py`; the full suite. Only the 4 known VALIDATION.md failures are expected.
