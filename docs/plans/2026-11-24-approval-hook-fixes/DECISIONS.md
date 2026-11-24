# Decisions

- D1 — Derive's parent check comes from the gate's own shell parse, not a widened text regex. Reason: a regex still guesses spelling, the same class of bug as this task. by: user, 2026-11-24 (spar, after the coordinator's comparison: "A").
- D2 — The parent id travels in the gate's write label, wording and reader in one phase_gate function, pinned by a test. Reason: smaller change; GPT preferred a data field (dissent recorded in SPAR.md). by: user, 2026-11-24 ("Label (Recommended)").
- D3 — Agreement 2 agreed. by: user, 2026-11-24 ("approve").

- D4 — Offer #1 approved from the summary (question tool, "Approve from this summary"); presentation chat. by: user, 2026-11-24.

- D5 — Copy the 5 candidate files into D:\workflow-axa now (T5). by: user, 2026-11-24 ("Copy now (Recommended)").

- D6 — Fix the existing CSS-dependent test, then commit and push (offer #2, which supersedes #1, approved from the summary). by: user, 2026-11-24 ("yes fix it than commit and push"; "Approve from this summary").

- D7 — Rebase this task's commit onto the newer origin/main (4 commits, release 2.11.0) with git pull --rebase, then push (offer #3, supersedes #2). by: user, 2026-11-24 ("Approve from this summary").

- D8 — Release the fixes as 2.11.1 (offer #4, supersedes #3; the owner's OK for verification_summary.py --run --write included). Note: 6d86d70 (this task's rebased commit) reached origin/main at 14:43:31 by a push from this checkout (git reflog origin/main: "update by push"), before V12 finished; no push command in this session or another local Claude transcript made it, so who ran it is unknown. V12 then passed on that same tree. by: user, 2026-11-24 ("alright version bump please"; "Approve from this summary").
