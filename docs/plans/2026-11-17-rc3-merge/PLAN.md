# Merge the pstack work into the redesign worktree before rc.3

## Current checkpoint
- Updated / phase: 2026-11-17; done: merged, pushed (bcb76ec), cleaned up (FINDINGS V4); shipped in 2.9.0-rc.3 (2026-11-17, docs/plans/2026-11-17-release-rc3)
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: migration; modifiers none — moves the worktree's base from c5e954b to pstack's 00ac3ae and keeps every uncommitted change; scope: the task; classification question: not asked
- Agreement (gate one): not required — the owner's decisions D1-D4 and run 5's agreed fix list (SPAR.md S2) set the behaviour
- Offer: #1 approved (owner, question tool, 2026-11-17)
- Implementation: T1-T3 verified (FINDINGS V1-V3)
- Verification / owner acceptance: not run
- Blockers: none
- Changed files: the worktree now sits on 00ac3ae; conflicts resolved in CONTEXT.md, docs/RULE-CONTRACTS.md, tests/test_owned_skills.py; fixes in skills/spar/SKILL.md, CONTEXT.md, README.md, tests/test_spar.py and three task records

## Goal

Owner, 2026-11-17: "I just want everything to be merged first." pstack's blast-radius and Unslop work is committed on main as 00ac3ae. This worktree holds five unfinished tasks on c5e954b: /spar, the worktree guard, the approval-button fix, the lost-answer fix and the wait-what row. All five go into rc.3 (D3). Run 5 (D:/workflow-axa-spar-pilot/run5/docs/spar/2026-11-17-rc3-merge-fit/SPAR.md, both debaters agreed on S2) checked that the two pieces of work fit, and listed the fixes.

## How

1. Back up first: the full diff against c5e954b, every untracked file and the seven files both sides changed go to `.artifacts/2026-11-17-rc3-merge/`, with the snapshot id.
2. Write pstack's version of every file only pstack changed (no local change there).
3. For the seven files both changed (CONTEXT.md, README.md, docs/RULE-CONTRACTS.md, skills/workflow-clarify/SKILL.md, tests/README.md, tests/test_owned_skills.py, tests/test_package_contract.py), run a three-way merge (base c5e954b, ours the worktree, theirs 00ac3ae) and resolve each conflict by hand as SPAR.md F2 says: both sides' terms, rows and tests, each row exactly once.
4. `git reset --mixed 00ac3ae`: HEAD and the index move to pstack's commit and the files on disk stay as they are, so `git diff` then shows only the five tasks' work.
5. Fixes from run 5: F3, /spar cites OPERATIONS.md "Standing diagnostic allowance"; F4, the Spar term in CONTEXT.md points to SKILL.md step 5 and SPAR-FILE.md instead of saying it starts a task; F6, stale records (/spar checkpoint D18/D19, TODO T1 effort names, pstack's handoff commit).
6. Checks (F7): the targeted tests, every contract row once (grep count), validate and the full suite. Expected: only the 4 known VALIDATION.md count failures, which clear in the rc.3 step.

Not in this task: the Unslop review of /spar's text (F5) and the owner's plain-English request go into the follow-up task, with pstack's two live-run gaps (D4).
