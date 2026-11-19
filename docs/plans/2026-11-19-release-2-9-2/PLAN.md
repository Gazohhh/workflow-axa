# Release 2.9.2

## Current checkpoint
- Updated / phase: 2026-11-19; released and installed; waiting for the owner's acceptance
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: docs-tests; modifiers none. A version bump, release notes, verification, publication and installation; no behaviour change beyond the delivered task. Scope: the task. Classification question: not asked
- Agreement (gate one): not required. A release step the owner asked for ("we need to push this right and make a new release", 2026-11-19)
- Offer: #1 approved (owner, question tool, 2026-11-19)
- Implementation: steps 1-6 done (FINDINGS V1-V3)
- Verification / owner acceptance: 1632 tests 0 failed, validate PASS, plugin 2.9.2, Codex DISK_MATCH; owner acceptance pending
- Blockers: none
- Changed files: none
- Next safe action: owner restarts sessions and accepts 2.9.2; then delete the release artifacts

## Working context
- Owner: Cem. Repository D:\workflow-axa, branch main (the only branch; equal to origin/main at 4791859 after git fetch, 2026-11-19).
- Releases: docs/plans/2026-11-19-offer-visibility (delivered). 2.9.1 was pushed but not installed on this machine; the Claude plugin cache shows 2.9.0-rc.4.
- The live Claude hook already runs the new code from the working tree (directory marketplace).
- Output: .artifacts/2026-11-19-release-2-9-2/ for the build ZIP and the Codex backup.

## Steps
1. Version 2.9.1 becomes 2.9.2 in .claude-plugin/plugin.json, skills/rule-maker/rules/version.json (package_version; rules stay 1.9.0), README.md's title, the codebase-map renderer's version constant and the four tests/behavioral/*.json candidate_version fields.
2. CHANGELOG.md: the Unreleased entry becomes 2.9.2 with its known limits. UPGRADE.md gets "Upgrade to 2.9.2 (from 2.9.1)".
3. VALIDATION.md is rewritten with tools/verification_summary.py --run --write VALIDATION.md.
4. One release commit (these files, the offer-visibility task and its code, and the owner's two record lines in docs/plans/2026-11-18-bug-reproducer) and a push to main.
5. Install: Claude marketplace update and plugin update; Codex copies in ~/.agents/skills replaced from tools/build_release.py's ZIP after a checked backup; audit_installation.py --check-global.
6. Release records: this task's evidence lines in a second commit and push.
