# Decisions

Asked in plain words after run 5 (thread b9817ad7), answered in the question tool on 2026-11-17:

- D1 (by: user) Q1, a spar held during a task that ends in "Turn this into a workflow plan": update the task you're already in, with the changed plan approved first (Recommended). This confirms the /spar task's D31.
- D2 (by: user) Q2: ship /spar in rc.3 and list the situations not yet tried live in the release notes (Recommended).
- D3 (by: user) Q3: put the worktree guard, the approval-button fix and the lost-answer fix in rc.3 too (Recommended).
- D4 (by: user) Q4: fix pstack's two weak live results (L5, Unslop not reached; L6, a small request skipped the safety step) before rc.3, not as known limits.
- D5 (by: agent) Run 5's O4 (merge with the 4 known failures, or together with the release records): nothing is committed before the rc.3 step, so the merge stays uncommitted in the worktree and the 4 known VALIDATION.md failures clear when that step rewrites it.
- D6 (by: user, 2026-11-17) "Make sure everything that has been said in that chat is also being done … I just want everything to be merged first before we work on this fix." The owner's new request (plain-English decision questions without ticket or synthesis ids as the basis, grilling style for owner decisions, Unslop for tickets, records and SPAR.md, then an internal test) is a follow-up task after this merge.

- D7 (by: user, 2026-11-17) "Unslop is meant for everything and simplification of language in general, not just spar." The follow-up task covers all writing a person reads.
- D8 (by: user, 2026-11-17) "I want everything pushed … then we don't continue working in multiple worktrees, but clean." Q1: rewrite VALIDATION.md, "confirm with GPT if correct and if you both agree then yes; if not, continue until you both agree". Q2: remove the extra worktree and the pilot copies run1-run5 (Recommended). Then work on D:/workflow-axa main.
- D9 (by: user, 2026-11-17) Then spar with GPT until both agree on Unslop and plain language for everything, with at most 30 launches (Q3, Recommended); implement and test if it differs from today; push to main; live tests; then the rc.3 release, installable.
