# Decisions

All policies below were recommended in the prior review and accepted by the user's 2026-10-09 "yes to all of it" response. Implementation details remain within that approval.

- D1 — Approved: one user-facing workflow with conditionally loaded references, not a collection of mandatory commands.
- D2 — Approved: the user owns behavior, material architecture tradeoffs, new dependencies/services/costs, schema/public-interface changes, destructive actions and publication. Routine implementation within approved constraints is delegated.
- D3 — Approved: a clear, genuinely low-risk direct edit is authorization for that exact edit; record it first without another approval round. Small file/line count alone does not establish low risk.
- D4 — Approved: file scope is bounded by area and purpose; necessary related callers/tests/docs/cleanup are included unless expressly protected. New scope or a reserved decision needs approval.
- D5 — Approved: one active task owner, persisted checkpoints, reconciliation against actual files, and explicit transfer of both records and uncommitted work. Support same-worktree and cross-machine recovery without guessing the team's setup.
- D6 — Approved: use helpers/subagents only when available and useful; no mandatory external grilling dependency or unrequested installation.
- D7 — Approved: use concrete abstraction/comment/cleanup criteria. The user has not supplied additional before/after code samples; examples in this package are illustrative, not attributed user artifacts.
- D8 — Approved: audit without automatic staging. Staging, commits, pushes, uploads and deployment require separately explicit authorization.
- D9 — Approved: reuse owner-approved unchanged audience/purpose/language/terminology when applicable; ask only for missing or changed meaning.
- D10 — Implementation choice within R1: label the package 2.0.0-rc.1 because defaults change materially and live team-host evaluations have not run. This creates no Git tag or release.
- D11 — Implementation choice within R1: standard-library Python local checks and a disposable fixture, no new package dependency, background service or CI workflow.

## R2 decisions — 16 October 2026
- D12 — Approved: the user's latest request accepts the seven improvements summarized immediately beforehand. Prior historical D6's lack of a mandatory external dependency is superseded by the subsequent specialist-integration task; Matt's current integrations remain external and intact.
- D13 — Approved: only flowchart guidance/rendering is local; do not restore the diagram-design dependency or replace Matt's research/debugging/TDD/review with condensed local methods.
- D14 — Within R2: use version 2.3.0 for the changed interview/task-resolution behavior. Reuse this established maintenance record and preserve prior approvals/outcomes below it.
- D15 — Within R2: assess skill-creator and webapp-testing as optional, separately approved helpers, not new startup prerequisites. No installation, API calls or paid model runs.
- D16 — Within R2: retain report CSS/JS and renderer behavior; build screenshots from the previous 2.2.1 example as carry-forward references. Those images are test references, not newly obtained individual human approvals. Never automatically replace them after a failure.
