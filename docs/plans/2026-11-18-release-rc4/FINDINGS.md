# Findings

- D1 (by: user, 2026-11-18) "release it", then offer #2 approved from the summary (question tool).
- F1 Offer #1 was superseded before it was shown: a command in backticks inside the behaviour text came out garbled in the presentation (the link-word formatting wraps words that are already inside backticks). Follow-up for a later release; offer #2 avoids backticks in its text.

- V1 Steps 1-3: version 2.9.0-rc.4 in plugin.json, rules/version.json (rules stay 1.9.0), README.md, the renderer version and four tests/behavioral files; CHANGELOG.md rc.4 entry with the known gaps; UPGRADE.md rc.3 to rc.4 section. verification_summary.py --run --write VALIDATION.md: 1544 ran, 1530 passed, 14 skipped, 0 failed; validate PASS.

- V2 Steps 4-6: commit ebd7c2a pushed to origin/main. Claude Code: marketplace update and plugin update took workflow-axa from 2.9.0-rc.3 to 2.9.0-rc.4 (read from D:\workflow-axa); sessions pick it up after a restart. Codex: tools/build_release.py built workflow-axa-2.9.0-rc.4.zip (216 files, SHA-256 6dba59d75b0a4cf528e849eeb686fd37522d7d9784a7aad637dbdce1257113e3) in .artifacts/2026-11-18-release-rc4; a dry run showed only files this release changed (renderer, version.json, the three spar files); the 20 folders were backed up to .artifacts/2026-11-18-release-rc4/codex-backup and checked, then replaced, and all equal the build. audit_installation.py --check-global: DISK_MATCH, declared 2.9.0-rc.4, nothing missing, changed or unexpected; the global CLAUDE.md and AGENTS.md references MATCH. The spar task checkpoint says it shipped in rc.4.
- Retention: the backup, the extracted build and the ZIP in .artifacts/2026-11-18-release-rc4 may be deleted after the owner accepts rc.4.
