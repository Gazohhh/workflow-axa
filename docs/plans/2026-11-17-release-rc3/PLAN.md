# Release 2.9.0-rc.3

## Current checkpoint
- Updated / phase: 2026-11-17; released and installed (FINDINGS V1, V2); owner acceptance pending
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: docs-tests; modifiers none — a version bump, release notes, verification and installation; no behaviour change; scope: the task; classification question: not asked
- Agreement (gate one): not required — release step the owner asked for (rc3-merge D9: "at the end of this we would have a new installable skill with everything")
- Offer: #1 approved (owner, question tool, 2026-11-17)
- Implementation: steps 1-6 done
- Verification / owner acceptance: 1536 tests 0 failed, validate PASS, plugin 2.9.0-rc.3, Codex DISK_MATCH; owner acceptance pending
- Blockers: none
- Changed files: none

## Goal

The owner, 2026-11-17: "When done merge to main again to start the tests, then at the end of this we would have a new installable skill with everything, right?" Main is at 5b9feb6 with all work pushed and checked: /spar, the worktree guard, the approval fixes, the pstack blast-radius and Unslop work, and the plain-writing rule set with plain owner questions.

## Steps

1. Version 2.9.0-rc.2 becomes 2.9.0-rc.3 everywhere the package states it: .claude-plugin/plugin.json, skills/rule-maker/rules/version.json (package_version; rules stay 1.9.0), README.md's title, skills/codebase-map/scripts/render_report.py, and the four tests/behavioral/*.json candidate_version fields.
2. CHANGELOG.md gets the rc.3 entry, in plain words, with the known gaps listed (DECISIONS of docs/plans/2026-11-17-rc3-merge D2): /spar not yet tried live with a kept SPAR.md turned into a plan, a cancel, one-model mode, or a cross-model run since agreement 7; the worktree-guard follow-ups. UPGRADE.md gets "Upgrade to 2.9.0-rc.3 (from 2.9.0-rc.2)".
3. VALIDATION.md is rewritten with `tools/verification_summary.py --run --write VALIDATION.md` (the full suite and validate).
4. Commit and push to main.
5. Install: update the Claude Code plugin from the marketplace (D:/workflow-axa) and reinstall the Codex copies in ~/.agents/skills from `tools/build_release.py`'s ZIP, after a backup, then `audit_installation.py --check-global`.
6. Each task released here gets a checkpoint line saying it shipped in rc.3.
