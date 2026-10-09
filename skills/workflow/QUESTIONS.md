# Questions and decision boundaries

## Classify what is missing

| Missing information | Action |
|---|---|
| A discoverable fact: implementation owner, actual dependency version, test command, existing convention | Inspect the available code/tools/authoritative docs. Ask only when the fact is inaccessible and needed. |
| A user-owned choice needed before useful dependent work | Ask now; pause that dependent work without choosing an answer for the user. |
| A user-owned choice that can wait while useful investigation proceeds | Record it and batch it with other currently answerable choices. |
| An immaterial unknown | Leave it labelled unknown; do not invent a decision or interrupt the task. |

Research first and batch by default. Do not ask the user to do searches the agent can perform. Do not perform a long, expensive investigation whose usefulness depends on an unanswered constraint. Independent approved work may continue in the active session; do not promise background activity the host cannot perform.

A decision is blocking when its answer changes which meaningful next action is valid, safe, in scope, or useful. Examples: whether paid services are allowed before researching integrations; whether to retain compatibility before selecting a migration; whether a published interface may change. Preferences about a final report's title usually do not block code investigation.

## Ask a useful batch

For each question give a stable ID, the decision, the relevant evidence, reasonable options, the recommendation, and what it blocks. Keep it short. Ask only questions whose prerequisites are settled; an answer can legitimately reveal a later question. Avoid both rigid "exactly two messages" promises and drip-fed questions that could have been grouped.

```text
Q1 — May this change introduce an external service?
Evidence: the existing offline path has no network dependency.
Options: keep it local; allow a service with an agreed budget.
Recommendation: keep it local. Blocks: integration design, not caller inspection.
```

For a structured decision batch, design clarification or requested interview, invoke the installed `grilling` specialist through [SPECIALISTS.md](SPECIALISTS.md), with its Q adapter. Do not merely emulate it or automatically invoke the user-only `grill-me` wrapper. This document controls timing and approval; the specialist supplies the interview method. Reuse settled answers and keep the tree within the task. Ordinary single access/factual questions need no interview. If the specialist is missing, follow the preflight exception path rather than silently substituting this document.

## Interpret answers without expanding them

Reuse answers already present in the request, task records, or approved project policy. A clear "yes to all recommendations" accepts the explicitly presented recommendations; record those choices instead of asking again. A partial answer settles only the items it addresses. "Go" approves a clearly identified settled plan, not ambiguous options or a revised plan the user has not seen. Silence and an agent's recommendation are not approval.

Default delegated details follow the core approval boundary: ordinary implementation under the chosen approach is not another design interview. Record genuinely material choices, not every local name. Escalate when the proposed action crosses a protected boundary, introduces a reserved decision, or changes the agreed outcome/risk.

## Close research honestly

A research or plan-only deliverable can be complete while implementation decisions remain open, provided its requested investigation and reporting are complete. Present findings, supported recommendations, unknowns, and the decisions required for a later phase. For implementation, leave affected work blocked and describe completed independent work. Neither route permits inventing an answer to make the report look finished.
