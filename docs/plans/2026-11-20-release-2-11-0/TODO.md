# Tickets

### T1 — Release 2.11.0
Status: Ready
- Scope:
  - Commit the delivered rework (its files plus docs/spar/ and both task folders).
  - Merge main (8a56c42, 2.10.0) into spar/architecture-review.
  - Bump 2.10.0 to 2.11.0 in .claude-plugin/plugin.json, README.md, UPGRADE.md, skills/codebase-map/scripts/render_report.py, skills/rule-maker/rules/version.json (package_version) and the four tests/behavioral candidate_version fields.
  - CHANGELOG.md: a 2.11.0 entry, with the "Unreleased" heading of 2.10.0 fixed if it is stale.
  - UPGRADE.md: an "Upgrade to 2.11.0" section.
  - docs/DESIGN.md: a 2.11.0 design note.
  - VALIDATION.md through `tools/verification_summary.py --run --write` (the approval of this offer is the owner's OK for it).
  - Commit the release, then a release-records commit, then `git push origin HEAD:main`.
- How to verify: `python -X utf8 -I tools/validate.py` PASS, the full suite OK, and `git log origin/main` showing the release commits.
- Rules: AGENTS.md (release docs; validate checks counts and versions).
