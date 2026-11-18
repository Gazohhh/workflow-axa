# Findings

- D1 (by: user, 2026-11-18) "release it", then offer #2 approved from the summary (question tool).
- F1 Offer #1 was superseded before it was shown: a command in backticks inside the behaviour text came out garbled in the presentation (the link-word formatting wraps words that are already inside backticks). Follow-up for a later release; offer #2 avoids backticks in its text.

- V1 Steps 1-3: version 2.9.0-rc.4 in plugin.json, rules/version.json (rules stay 1.9.0), README.md, the renderer version and four tests/behavioral files; CHANGELOG.md rc.4 entry with the known gaps; UPGRADE.md rc.3 to rc.4 section. verification_summary.py --run --write VALIDATION.md: 1544 ran, 1530 passed, 14 skipped, 0 failed; validate PASS.
