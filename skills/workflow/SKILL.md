---
name: workflow
description: "Use for repository features, bug fixes, refactors, or explicitly requested workflow research, planning, audits, and task resumption. Records work before implementation, separates user decisions from delegated execution, and verifies scoped changes. Do not turn explanation-only requests into repository work."
---

# Workflow

Investigate facts, obtain approval for user-owned decisions, and execute the agreed work without repeated permission requests. Leave records that another agent can reconcile with the actual files after an unexpected interruption.

## 1. Establish context and mode

Read applicable repository instructions, including relevant `AGENTS.md`, `CLAUDE.md`, directory overrides, and required references. Respect the host's instruction precedence. Report missing required guidance; do not create policy files without approval. Inspect the repository root and, where Git is available, the branch/worktree and staged, unstaged, and untracked changes. State the working location; other repositories are outside scope.

Choose the smallest suitable mode:
- **Explain:** answer without scaffolding or mutations.
- **Research / plan / audit only:** investigate and record; no implementation or automatic audit fixes.
- **Implement:** investigate, propose, obtain approval, then execute.
- **Lightweight edit:** an explicit, unambiguous low-risk request authorizes that exact edit. Record first, then edit and verify without another approval round. File count is not a risk test; behavior, dependencies, interfaces, security, or uncertain impact require the normal route.

Explicit read-only/no-file instructions override record creation: provide a continuation summary instead and disclose that nothing was persisted. Resumption starts with step 2, not blind continuation of a checked TODO.

## 2. Establish the task record

Before substantial discovery or any implementation, read [TASK-FOLDER.md](TASK-FOLDER.md) and create or claim `docs/plans/YYYY-MM-DD-<slug>/`, respecting an established project location. Match existing work by its goal and scope, never recency alone. Resolve ambiguous ownership before writes. One active owner maintains the records; related task histories remain evidence, not authority.

Record confirmed context, unknowns, scope, active work, and the next safe action. On resumption reconcile the record with actual files, approval, worktree changes, and verification freshness. Mark interrupted work uncertain until inspected. Never infer that a stopped subagent finished. Sanitize stored evidence; do not record secrets or unnecessary personal data.

Read [SPECIALISTS.md](SPECIALISTS.md) and verify the relevant installed specialists before the next phase. Use its explicit routes and adapters, not optional suggestions. Record resolved skills and availability; recheck on host/account or dependency changes. Follow [SETUP.md](SETUP.md) only when setup is needed and authorized.

**Ready:** the task location, owner, checkpoint and next phase's specialist readiness are known.

## 3. Investigate and settle decisions

Inspect the behavior's owner, existing implementations, callers and alternative paths, tests and their runner, relevant data/configuration, and current project documentation. Identify replacements and their possible leftovers. Establish a useful test baseline before changing behavior; record inaccessible environments rather than guessing. Use the routed research/diagnosis/design specialist when applicable and authoritative guidance matching actual versions.

Discoverable facts are the agent's job. Batch nonblocking decisions after useful investigation; ask early only when a user-owned answer blocks meaningful progress or changes the authorized direction. Read [QUESTIONS.md](QUESTIONS.md) when handling missing information or approval ambiguity. Do not repeat answered questions. Unresolved choices can remain in a research report without authorizing implementation.

**Ready:** explain what exists, what must change, affected paths/docs, evidence, and the remaining decision boundaries.

## 4. Record the plan and approval

Write acceptance criteria, the approach, bounded file areas, protected areas, risks, verification, documentation, and directly superseded code to remove. Map actionable TODOs, dependencies, specialist routes and test seams; avoid a second competing task list. Present the plan and currently answerable decisions together.

The user owns changed behavior, material architecture tradeoffs, new dependencies/services/costs, schema/public-interface changes, destructive actions, and publication. Within an approved approach, delegate local names, established file placement, implementation details, required callers/tests/docs, scoped replacement cleanup, and task-caused fixes.

Record the approved revision, user response, selected options, included work, and exclusions **before implementation**. Reuse already explicit approval of the same settled scope; a prepared prompt alone does not settle unchosen tradeoffs. A recommendation or edited plan is not approval. Expansion or a new user-owned choice pauses only dependent work; independently approved work may continue. Do not keep asking permission for actions already covered.

**Ready:** each next implementation step is covered by recorded approval or the exact lightweight request, with no unresolved decision on which it depends.

## 5. Execute bounded work units

Before each unit, update its active TODO, intended change, and verification checkpoint. Afterwards record actual changes, observed results, and the next action. Keep units small enough to recover after a hard stop; never defer recordkeeping until credits run low.

Use the routed implementation/reference specialist for this unit. Keep behavior with its existing owner. Helpers should express a real operation or remove meaningful repetition; names such as `normalize` are neither automatically justified nor banned. Comments explain non-obvious reasons or constraints, not obvious syntax. Avoid speculative layers, fallback paths, and unrelated refactoring. Update existing authoritative docs and remove directly superseded callers/config/tests/debug code within scope; track approved temporary migration leftovers explicitly.

Use subagents only when useful and available. Give each the approved scope, task IDs, rules, evidence, write ownership, and verification expectations. Parallelize independent work; serialize shared-file changes and dependencies. Subagents report to the owner rather than editing task records. Without them, perform the same work and reviews yourself and label the limitation honestly. Install no helper merely to satisfy this workflow.

Expected failing regression tests are part of debugging. Fix task-caused failures within scope. Classify unrelated baseline failures and environment blockers separately; record coverage gaps and ask only for decisions needed to proceed or waive required verification.

## 6. Verify and audit the final state

Run relevant checks and inspect their results, including the original symptom, alternative paths, cleanup, and updated docs. Read [AUDIT.md](AUDIT.md) and review the task-attributable final diff, including relevant untracked files. Invoke the routed `code-review` for code changes; never describe self-review as independent.

Do not automatically stage, commit, push, upload, deploy, reset, or discard changes. Separately authorized Git actions must preserve existing user edits and staging intent; file-level staging cannot isolate mixed ownership. If attribution is uncertain, pause that action rather than guessing.

Fix in-scope findings and rerun affected checks after the last repair. If evidence remains unavailable or review stops with open issues, retain an incomplete status instead of claiming success.

## 7. Close or hand off

Update outcome, remaining work, verification, approval, ownership, and the next safe action. Report changes, docs updated, actual checks, limitations, and task/artifact paths. A blocked or partial report is valid; mark `done` only when approved acceptance criteria and required verification are satisfied. Explicitly accepted verification limits remain visible, not relabelled as passes.

## Conditional references

- **Requested PDF:** read [PDF-DELIVERABLE.md](PDF-DELIVERABLE.md) before planning or drafting. Its evidence, language, rendering, and final-version reviews add to this workflow; ordinary work does not load it.
- **Preparing a prompt elsewhere:** use [CHATGPT-PROMPTS.md](CHATGPT-PROMPTS.md). It is optional, not another workflow phase.
