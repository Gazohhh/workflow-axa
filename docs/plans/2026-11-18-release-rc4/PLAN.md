# Release 2.9.0-rc.4

## Current checkpoint
- Updated / phase: 2026-11-18; the offer waits for the owner's answer
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: docs-tests; modifiers none. A version bump, release notes, verification and installation; no behaviour change. Scope: the task. Classification question: not asked
- Agreement (gate one): not required. A release step the owner asked for ("release it", 2026-11-18)
- Offer: #2 approved (owner, question tool, 2026-11-18); #1 superseded before it was shown
- Implementation: not started
- Verification / owner acceptance: not run
- Blockers: none
- Changed files: none

## Goal

The owner, 2026-11-18, after docs/plans/2026-11-17-spar-owner-in-loop was delivered: "can we release it or not or do we need to wait for who?", then "release it". Main is at 163bc23 with that work pushed and checked.

## Steps

1. Version 2.9.0-rc.3 becomes 2.9.0-rc.4 everywhere the package states it: .claude-plugin/plugin.json, skills/rule-maker/rules/version.json (package_version; rules stay 1.9.0), README.md's title, skills/codebase-map/scripts/render_report.py, and the four tests/behavioral/*.json candidate_version fields.
2. CHANGELOG.md gets the rc.4 entry in plain words, with the known gaps: the owner's verdict on a proposal both debaters accepted is untested live, and the new rules have not run Claude against GPT. UPGRADE.md gets "Upgrade to 2.9.0-rc.4 (from 2.9.0-rc.3)".
3. VALIDATION.md is rewritten with `tools/verification_summary.py --run --write VALIDATION.md`.
4. Commit and push to main.
5. Install: update the Claude Code plugin from the marketplace and replace the Codex copies in ~/.agents/skills from `tools/build_release.py`'s ZIP after a backup, then `audit_installation.py --check-global`.
6. The released task's checkpoint says it shipped in rc.4.
