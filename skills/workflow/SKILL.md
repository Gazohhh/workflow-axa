---
name: workflow
description: "Use for repository feature requests, bug fixes, refactors, research, planning, audits and task resumption, including ordinary requests without a skill name. Inspect current code before proposals; prepare an evidence-backed visual review and wait for approval before substantive implementation. Explanation-only requests stay read-only."
---

# Workflow

Establish current facts, show the requested change back to the user, obtain approval, then execute within it. Keep recoverable records. Installed instructions and past conversation are not proof of current repository understanding.

## 1. Establish context and mode

Read applicable repository instructions and required references with the host's precedence. Inspect the actual root, branch/worktree, staged/unstaged/untracked changes and relevant directory rules. State the working location. Preserve user edits; other repositories are outside scope. Never create policy files without setup approval.

Choose the smallest mode:
- **Explain:** repository-specific claims require relevant code inspection; no scaffolding or mutations. General explanations need no repository scan.
- **Research / plan / audit only:** investigate and record; no implementation or automatic fixes.
- **Implement:** investigate, clarify, prepare the plan and visual approval review, then stop before implementation.
- **Lightweight edit:** an explicit, unambiguous low-risk request authorizes that exact edit after a short record. Behavior, architecture, dependencies, public interfaces, security or uncertain impact require the normal route. Small file count is not an exemption.

Explicit no-file instructions override persistence: disclose the limitation and provide a continuation summary. A visual-only request authorizes report artifacts, not application edits; route it to the installed `codebase-map` without creating an implementation project.

## 2. Establish the record and capabilities

Read [TASK-FOLDER.md](TASK-FOLDER.md). Before substantial discovery or implementation, create or claim the exact goal/scope task at the established location, otherwise `docs/plans/YYYY-MM-DD-<slug>/`. Resolve ambiguous ownership before writes. One owner maintains records; interrupted work is uncertain until inspected.

Save the goal, constraints, unknowns, active unit and next safe action. Reconcile resumed records, approval and evidence with actual files, not checkboxes. Sanitize evidence. Read [SPECIALISTS.md](SPECIALISTS.md); verify and use the applicable installed routes, including the local visualizer, rather than pretending they ran. Recheck after host/account or dependency changes. [SETUP.md](SETUP.md) is for authorized setup, not automatic installation.

**Ready:** task, owner, checkpoint and next phase's capabilities are known.

## 3. Ground the request before designing

Read [GROUNDING.md](GROUNDING.md). Inspect existing owners, behavior, entrypoints/callers, alternate paths, reusable implementations, tests/runner, relevant data/configuration and authoritative docs. Scale inspection to impact. Record file/symbol evidence, contradictions, missing access and static-versus-runtime limits. Establish a useful test baseline without unauthorized installs or diagnostic writes.

State the understood outcome in plain language. Map requirements to their user source, current evidence, actual gap and acceptance criteria. Find existing/partial capabilities before adding another implementation. Every proposed task must serve a requested requirement or demonstrated prerequisite; attractive extras are not prerequisites. No speculative features in the plan.

Investigate discoverable facts independently. Read [QUESTIONS.md](QUESTIONS.md): batch nonblocking user decisions; ask early for direction blockers. Use `grilling` for structured unresolved choices, reuse answered questions, and persist answers. Research may finish with open choices; dependent implementation may not.

**Ready:** explain what exists, what the user wants, what must change, evidence and remaining boundaries—not merely “code reviewed.”

## 4. Prepare the visual review and obtain approval

Record a revisioned PLAN, acceptance criteria, approach, bounded/protected areas, risks, verification, existing doc updates and directly superseded code to remove. TODOs reference requirements, evidence, acceptance and dependencies. Resolve decisions material to the next implementation scope.

Read [VISUAL-REVIEW.md](VISUAL-REVIEW.md) and its flowchart-first `diagram-design` route. For substantive features, behavioral fixes and architecture changes, invoke `codebase-map` after PLAN/TODO preparation, not after executing tasks. Generate the current/proposed HTML review, validate its evidence and source freshness, request local opening when supported, report its path and **STOP for user approval**. Opening, rendering, answering questions or liking the diagram is not implementation permission. A blocked draft cannot masquerade as approval-ready.

Record the approving response, exact revision, report reference, selected options, included work and exclusions before coding. Reuse approval of the same already presented scope; do not replay the gate on every TODO or handoff. Never assume a blanket request waived an unseen review. An explicit user waiver is recorded, not invented.

User-owned choices include changed behavior, material architecture, dependencies/services/costs, schema/public interfaces, destructive actions and publication. Delegate ordinary local details, established placement, required callers/tests/docs, scoped cleanup and task-caused fixes. Material changes require a revised review and approval; independent already-approved work may continue.

**Ready:** each next implementation step has valid recorded authority and no blocking choice or material unresolved mismatch.

## 5. Execute recoverable work units

Before each unit, checkpoint its task, intended change and verification. Afterwards save actual changes, results and next action; do not wait for credits to run out. Use applicable specialists with the approved scope, evidence, allowed writes and output contract.

Keep behavior at its owner. Helpers must express a real operation or remove meaningful duplication; `normalize` is neither banned nor automatically justified. Comments explain non-obvious reasons, not syntax. Avoid speculative layers, fallbacks and unrelated refactors. Update authoritative docs; remove superseded callers/config/tests/debug code within scope. Track approved temporary migration leftovers explicitly.

Use available subagents only for useful independent work with clear write ownership. They return evidence to the record owner. Sequential work is valid; never label self-review independent. Expected failing regression tests are normal; fix task-caused failures within scope, separate baseline/environment failures, and ask only for a needed decision or verification waiver.

## 6. Verify, audit and close

Read [AUDIT.md](AUDIT.md). Check the original symptom, alternate paths, requirements, cleanup and docs; inspect task-attributable staged/unstaged/untracked changes. Invoke routed `code-review` for code changes. Repair in-scope findings and rerun affected checks after the last repair. Missing coverage is not a pass.

Do not automatically stage, commit, push, upload, deploy, reset or discard. Separately authorized Git actions preserve user edits and staging intent; file-level staging cannot isolate mixed ownership. Pause uncertain attribution.

Update outcome, acceptance evidence, remaining work, ownership, approval and next safe action. Report actual checks and artifact paths. Mark done only when acceptance and required verification are satisfied; partial/blocked reports are valid. Retain explicitly accepted limits.

## Conditional references

- Requested PDF: read [PDF-DELIVERABLE.md](PDF-DELIVERABLE.md); preserve its reader/language/rendering reviews without adding an irrelevant code-flow gate.
- Preparing a request elsewhere: [CHATGPT-PROMPTS.md](CHATGPT-PROMPTS.md).
