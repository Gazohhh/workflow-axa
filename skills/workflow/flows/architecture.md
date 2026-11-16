---
name: architecture
uses: [codebase-design, domain-modeling, plan-review]
fallbacks: [Conditional design]
approval-exceptions: none
---

# Architecture

Decide ownership, boundaries or a public contract with real alternatives on the table.

1. **State the constraints:** what must hold (callers, data, performance, teams, deadlines) and what is still open.
2. **Design it twice.** With `codebase-design`, sketch two or three genuinely different options, each with its interface and what it costs.
3. **Consequences.** For each option: what changes for callers, tests, migration and maintenance.
4. **Decide.** Recommend one and say why; offer an ADR through `domain-modeling` when a future reader will need the reason.
5. **Check the plan** with `plan-review` before any tickets.

Analysis alone needs no approval. Implementation follows the common process. Unknown dependencies: record Conditional design with its assumptions.

**Done when:** the decision and its reasons are recorded, and the follow-up work is either planned or explicitly deferred.
