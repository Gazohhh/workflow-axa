# Decisions

- D1 (by: user, 2026-11-15) Implement REDESIGN.md v6; verify each change with Opus and Astra; no commit or push; tests on D: repos via worktrees.
- D2 (by: agent) Work in a detached worktree `D:\workflow-axa-redesign` (no branch, since branches need the owner's OK). Reason: isolation from the main checkout's uncommitted edits.
- D3 (by: user, 2026-11-15) Decision B: REDESIGN.md v6 §18 presented the proposal (live runs only on Claude Code and Codex/T3 on existing plans, at most 20, stop on a plan usage limit, nothing billed per use). The owner's next message gave the go for v6 and explicitly asked for tests on the D: repos. Live runs stay within that proposal; anything beyond it needs a new OK.
- D4 (by: user, 2026-11-16) Button test: register the sandbox under .artifacts as a temporary T3 project, run the button-answer test in 1-2 of the 5 held runs, then remove the project.
- D5 (by: user, 2026-11-16) The remaining runs: the button test first, the rest for the T26 pilot. The pilot uses worktrees of the D: repos only.
- D6 (by: user, 2026-11-16) Codex: test anyway with the old global rules still loaded (a real case, since existing projects have old rules); 1 of the 4 runs. Open design question for a spar with Astra: how the new package handles stale installed or project rules (for example rule-maker re-checking each project instead of trusting its current AGENTS.md). Not blocking: the work continues.
- D7 (by: user, 2026-11-16) May run `tools/verification_summary.py --run --write` in the redesign worktree now and again at T25 (it rewrites VALIDATION.md there; nothing committed).

- D8 (by: user, 2026-11-16) T26 trial worktrees start from the current branches, after `git fetch --all`: D:\Hooqd master (its release/production and release/staging branches are merges of master), D:\Cheflabels-labeler-V2 development/main, D:\workflow-paperclip master. Detached worktrees only; the owner's existing edits in those checkouts stay untouched; nothing is committed.
- D9 (by: user, 2026-11-16) The live-run total grows from 20 to 26 (decision B amended). 3 runs go to the T26 trial (one per repo) and up to 6 to the observed /interrogate and /no-comments runs that T23 left unmet. Each run still stops at a plan usage limit, and nothing is billed per use.

- D10 (by: user, 2026-11-16) The live-run total grows from 26 to 29 (D9 amended). The 8 remaining runs cover: an /interrogate rerun (4: main, two adversaries, confirmation), the /no-comments dry run (2), a redo of r19 (1), and a recheck of r20 after the router fix (1). The reasons: r19 was lost to the test driver's over-broad isolation prompt, and r21 was cut off by a T3 server restart after 12 tool calls with no subagent.

- D11 (by: user, 2026-11-16) Release 2.9.0-rc.1, owner's words: "So everything is done? if so merge it to main repo and push commit it and install latest version". The owner then chose:
  - legacy_inventory.py --apply for all 8 workspaces with pre-offer tasks (Cheflabels-labeler-V2, Hooqd, Pletrix-Cheflabels, android-launcher, rutjes-administratie, workflow-axa, workflow-paperclip; 48 tasks);
  - regenerate VALIDATION.md before the commit;
  - update the Codex skill copies (~/.agents/skills), run global_policy.py --apply and activate_rules.py --apply;
  - switch the running sessions now.
  Commit and push only for workflow-axa (main fast-forward from bfc18fd). The owner's 5 staged task-record files in the main checkout stay uncommitted.
