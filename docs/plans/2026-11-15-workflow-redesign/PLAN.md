# Workflow redesign (v6)

## Current checkpoint

- Updated / phase: 2026-11-16; delivered (implementation complete; release actions wait for the owner)
- Agreement (gate one): agreed — REDESIGN.md v6, every section agreed by Opus and Astra (rounds 12–17)
- Approval (gate two): approved 2026-11-15, owner's words: "I want you to start making a plan of execution now when done you got my go to start working on this goal. For each change verify with Astra and Opus if both agree with implementation than you continue to next work. Create a new task inside docs making tickets so you can work from there. Do not stop untill it's done. On my D I got some repo's you can clone into a worktree and start doing some tests if implementation is as expected. Do not commit or push anything."
- Implementation: done, T1–T26 (TODO.md)
- Verification / owner acceptance: full suite 1399 OK, validate PASS (V16); owner acceptance pending
- Blockers: none
- Changed files: see TODO.md per ticket and FINDINGS
- Next safe action: the owner decides the release actions listed under Outcome

## Working context
- Owner: Cem (AXA Studios)
- Repository: workflow-axa; worktree `D:\workflow-axa-redesign`, detached at bfc18fd (rc.39), no branch. The main checkout `D:\workflow-axa` keeps the owner's uncommitted docs/plans edits untouched.
- Live hooks load from the installed copy (`~/.claude/plugins/cache/gazohhh/workflow-axa/2.8.0-rc.39`), so this candidate doesn't affect running sessions.
- Reviewer: GPT-6 Astra (Low) through T3, the same thread as the planning rounds; every ticket is checked by Opus and Astra before the next starts.
- Test output: `.artifacts/2026-11-15-workflow-redesign/` in this worktree; pilot worktrees of D: repos are task-owned and removed only under TODO.md "Cleanup".

## Goal and acceptance
Implement REDESIGN.md v6 (§14 checkpoints 1–8), except the steps that need the owner's separate OK:
- no commit, push, branch, reinstall or global activation (`global_policy.py --apply`, `activate_rules.py --apply`, `verification_summary.py --run --write`);
- live host runs limited by decision B (proposal: Claude Code and Codex/T3 on existing plans, at most 20 runs, stop on a plan usage limit; nothing billed per use).

Done when: every ticket T1–T26 is done with both verdicts; the validator and the full suite pass; the pilot results are in FINDINGS. Delivery reports implementation, verification gaps and the unperformed release actions (commit, push, reinstall, activation) separately.

## Baseline before this change
- `python -X utf8 -I tools/validate.py` in `D:\workflow-axa-redesign` at bfc18fd, clean tree, Windows 11, Python 3.14.2: exit 0, "PASS … twenty-one local skills …".
- `python -X utf8 -m unittest discover -s tests -p "test_*.py"`: exit 0, 1229 tests, 13 skipped, ~300 s.

## Approach and scope
REDESIGN.md §14, adapted to one session: checkpoints in order, each split into tickets (TODO.md). Hook candidates are developed in this worktree only. The new approval adapter replaces phase_gate in `hooks/hooks.json` of the candidate; the installed copy keeps rc.39 until the owner reinstalls.

## Approval
The owner's go above covers every ticket in TODO.md. Excluded (owner OK needed each time): commits, pushes, branches, reinstall, global activation, paid runs beyond decision B.

## Outcome

Delivered 2026-11-16 in the detached worktree D:\workflow-axa-redesign (base bfc18fd, rc.39). Nothing was committed, pushed, branched, installed or activated.

**Implemented (T1–T26, each with Opus and Astra Agree; details in FINDINGS):**
- The offer model: approval comes from a recorded offer and the one question. hooks/approval.py is the checker; phase_gate.py is the legacy checker for inventoried pre-offer tasks; legacy_inventory.py.
- Record writes no longer switch the task.
- The plain_reply, phase_reads and truncated_read hooks are removed; duplicate_skills only diagnoses.
- completion_check.py; flows/ recipes and FALLBACKS.md; the CSS switch (settings.py, off by default).
- Skills:
  - resume replaces task-status and resume-task; rule-maker diagnose replaces workflow-doctor;
  - implement-spec and retro are archived; simple-english becomes skills/workflow/SIMPLE-ENGLISH.md;
  - new /interrogate (with snapshot.py), /no-comments and /wait-what;
  - code-review gains comment, reader-load and blast-radius checks;
  - 19 skills.
- Version 2.9.0-rc.1, rules library 1.9.0, global artifact policy 2.9.0. The docs and the CHANGELOG are updated.
- T26 fixes from the live pilot: F1 (the SessionStart note no longer claims a plugin is loaded), F2 (offers only through workflow-specify; the hook's no-offer refusal says how to create one), F4 (/no-comments makes its offer through workflow-specify).

**Verified:**
- Last full suite: 1399 ran, 0 failed, 14 skipped (V16); validate PASS (19 skills).
- VALIDATION.md was generated at T25 (V15, CURRENT then). The T26 changes and these records make it stale now. Regenerating it needs the owner's OK (D7 covered T25 only).
- Live host runs, 29 of the 29 allowed (D10): T16 runs 1–17, and the T26 pilot r18–r29 on worktrees of Hooqd, Cheflabels-labeler-V2 and workflow-paperclip.
- Offline replays on those worktrees: 9/9.

**Gaps (not verified):**
- Live approval, implementation, completion checking and delivery on real repos (the T26 runs were single-turn).
- The F4 fix was not retested live (no runs left).
- Behavioural cases B15–B29 are NOT_RUN.
- The T26 comparison with the baseline is contextual, not matched.
- The /no-comments trial differed from the expected keeps of exported-interface docs (a judgement difference).
- A known intermittent failure, test_record_safety.test_parallel_appends_lose_nothing (a leftover lock, about 1 in 30 runs), also happens on rc.39. It is unfixed and recorded as a follow-up, because a leftover lock blocks record writes for 5 minutes.

**Not done, needing the owner's OK:**
- commit, push and merge of the worktree changes;
- reinstalling the plugin or replacing the cache;
- `global_policy.py --apply` (the installed ~/.workflow-axa/ARTIFACTS.md still says 2.5.0);
- `activate_rules.py --apply`;
- `legacy_inventory.py --apply` before switching an active install to 2.9.0;
- `verification_summary.py --run --write` for a current VALIDATION.md;
- retiring tools/stage_candidate.py and its test;
- removing the retained evidence under .artifacts/2026-11-15-workflow-redesign/ after delivery.