# Decisions

- D1 (by: user, 2026-11-17) "Yes to all": fix before the next release, which is 2.9.0-rc.3; its own task, offer and review; a fail-closed guard that refuses writes in another worktree than the session's, for file paths and git commands; the full per-worktree lookup (F2) after the release.
- D2 (by: agent, 2026-11-17) One-ticket work with the behaviour decided by the owner: agreement not required (VISUAL-REVIEW "No separate agreement").

- D3 (by: user, 2026-11-17) Offer #1 (7b023fa57fd3672e) approved with the question tool's "Approve from this summary (Recommended)".

- D4 (by: user, 2026-11-17) Offer #1 re-presented unchanged after a later owner message and answered "Approve from this summary (Recommended)" again; the guard is rebuilt to resolve every path a write command names (Astra review 2).

- D5 (by: user, 2026-11-17) After 7 review rounds: "One more round, then release". Astra does round 8; if it finds only rare or general gaps, rc.3 ships with them recorded as known limits, and a follow-up task takes a structural fix (confining where shell commands can write) plus F5.
