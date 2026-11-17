# Decisions

- D1 — Agreement 1 (R1–R12), agreed 2026-11-17, by: user ("Agree"), after the owner challenged the first recipe mapping (FINDINGS E12), which added R5 for every recipe and R12.
- D2 — No release records in this task; the separate rc.3 release step bumps the version and writes CHANGELOG from this task's summary. by: user (Q1 answer: "Ask the other session working in workflow-axa before you do that"; peer reply recorded in FINDINGS Q1; agreement 1 assumption, not rejected).
- D3 — Blast radius stays owned by code-review as a sibling reference file, not a new registered skill (deletion test, skill-count cost). by: agent (sparring E1), within agreement 1.

- D4 — Offer #1 (26f9c07acafe90ed) answered 2026-11-17 with "Approve from this summary" (question tool; the report first was recommended and declined). by: user. Presentation decision: chat.

- D5 — Live test run (owner, 2026-11-17: "do a live test-run to see if it worked or not simple test-case please"): one isolated `claude -p` session (Opus 5.5), hard cap $3 total through --max-budget-usd, no retries. by: user (cap answer "$3 total (Recommended)"). The case is BR-inspect-question on a clean synthetic fixture in the session scratchpad.
- D6 — Commit and push to main after the live run proves the change (owner: "When your done and proven make sure to commit and push please your changes"; branch answer "main (Recommended)"; only main exists, local equals origin at c5e954b). Offer #1 excluded git writes, so offer #2 adds `git commit` and `git push`. by: user.

- D7 — Offer #2 (217635360dc8da40) answered 2026-11-17 with "Approve from this summary" (question tool). by: user. Presentation decision: chat.

- D8 — Second live run L2 with realistic settings (owner answer: "Realistic settings (Recommended)"), 2026-11-17: the same fixture and plain prompt, the owner's user settings and global CLAUDE.md loaded, cap $3, no retries. Edits and git writes are still denied by a flag-level settings file. by: user.

- D9 — Routing fix and live run L3 (owner answer: "Fix routing, then run L3 (Recommended)"), 2026-11-17. code-review's description names impact questions, and its body sends such a question to BLAST-RADIUS.md alone, report only. Then one live run L3 with realistic settings, cap $3, no retries; commit and push only if it passes. L3's P1 becomes "report only, fixture unchanged, no records", because the route is now code-review, not the workflow router. Offer #3 revises #2. by: user.

- D10 — Offer #3 (caf68c3207bf0209) answered 2026-11-17 with "Approve from this summary" (question tool). by: user. Presentation decision: chat.

- D11 — Live run L4 (owner answer: "Run L4 with --add-dir (Recommended)"), 2026-11-17: identical to L3 plus `--add-dir D:/workflow-axa`, cap $3, no retries. Commit and push only if P1-P4 pass. Offer #3's condition names L3, so a passing L4 is presented as offer #4 before any git write. by: user.

- D12 — Offer #4 (82aa57b13c102a54) answered 2026-11-17 with "Approve from this summary" (question tool). Commit on main and push after the full-suite rerun passes. by: user. Presentation decision: chat.
