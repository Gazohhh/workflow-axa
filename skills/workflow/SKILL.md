---
name: workflow
description: "Use for new or existing repository features, fixes, refactors, research, plans, audits and task resumption, including ordinary prompts. Find the right task, inspect current code, use grilling to uncover missing decisions, then show the plan and local flowchart for approval before substantive implementation. Explain-only requests remain read-only."
---

# Workflow

Find the task → inspect current code → uncover missing decisions → prepare the plan and flowchart → get approval → implement → verify. Prior chats and installed instructions are not proof of current understanding.

**Write for someone new to the project.** Explain what changes, why it matters and what decision is needed before technical details. Keep exact terms, paths and checks available underneath. Use [WRITING.md](WRITING.md) for questions, plans, reports and completion messages. Do not equate simpler language with less precise evidence.

## 1. Establish location, mode and task

Read applicable project instructions with the host's precedence. Inspect the actual root, branch/worktree, local changes and directory rules. State the location; preserve user edits. No policy-file changes without setup approval.

Choose the smallest mode: **explain** is read-only; **research/plan/audit** does not authorize implementation; **implement** needs the steps below. A genuinely **lightweight edit** uses a short record and the user's exact, unambiguous low-risk request as authority. Behavior, architecture, dependencies, public interfaces, security or uncertain impact are not lightweight because few files change.

Before creating any task folder, read [TASK-FOLDER.md](TASK-FOLDER.md). Search the established record location; inspect the current/named task and plausible related plans. Reuse a clearly identified task through revisions. Ask whether to extend or separate a plausible ambiguous match; resolve conflicting owners before writes. A new conversation, date or `/workflow` command is not a new task. Only create a folder when no applicable task exists or separation is explicitly chosen.

A brief read-only task search precedes record creation. Save a checkpoint before substantial discovery. No-file requests override persistence; disclose recovery limits. General explanations need no repository scan. Visualization-only requests route to local `codebase-map`, not a new implementation scaffold.

## 2. Inspect facts and capabilities

Use [GROUNDING.md](GROUNDING.md): inspect relevant owners, entrypoints/callers, alternate paths, reuse, tests, data/config and authoritative docs. Scale reads to impact. Record paths/symbols, discrepancies, missing access and static-versus-runtime limits. Before tests/builds/captures, read [ARTIFACTS.md](ARTIFACTS.md): reuse the output parent, protect tool-owned paths and plan bounded retention. Establish authorized baseline checks; do not invent architecture or duplicate existing features. When project terms, ownership or boundaries are unclear, invoke `domain-modeling` before inventing new names or concepts.

Read [SPECIALISTS.md](SPECIALISTS.md). Verify and use Matt's applicable routes and the local visualizer. Installation, availability, use and result verification are separate claims. Recheck changed hosts/dependencies, not every call. Missing required skills block dependent work unless a fallback is explicitly approved. [SETUP.md](SETUP.md) is for approved setup, never automatic installation.

## 3. Check understanding with grilling

For **every new substantive goal or material scope change**, invoke installed `grilling` to discover unstated decisions, not only to format already-noticed questions. Use [QUESTIONS.md](QUESTIONS.md). Reuse current, sourced answers and valid approvals; do not replay an interview for unchanged resumed work. A detailed prompt still gets the decision check; a complete one may need no questions.

Investigate facts yourself. Ask early when a user-owned choice changes the valid direction; otherwise batch currently answerable questions after useful inspection. Persist partial answers and remaining blockers. Code describes current behavior, not user intent; recommendations and silence are not decisions.

Record the understood outcome, relevant decisions and their answer sources or unresolved status. Ordinary local implementation details remain delegated. Do not expand the feature to create questions. Research may finish with open choices; dependent implementation may not.

## 4. Prepare the plan and visual approval

Separate approval, implementation and verification/acceptance in the existing current checkpoint. Keep historical baselines and proposals labelled; follow TASK-FOLDER.md for the revision log and forward-only adoption. Reruns, progress and handoffs are not new plan revisions.

Map each requirement to its user source, current evidence, actual gap, task and acceptance check. Every TODO must serve requested work or a demonstrated prerequisite. Record revision, bounded/protected areas, risks, test strategy, authoritative documentation updates and directly superseded code to remove.

Follow [VISUAL-REVIEW.md](VISUAL-REVIEW.md). For substantive features, behavioral fixes and architecture changes, invoke local `codebase-map` **after writing PLAN/TODO, before executing them**. Show the real current/proposed flow, exclusions, required changes and completion checks in the approved local style. Explain findings in plain language; keep technical evidence available. Material unanswered choices mean draft, not approval-ready.

Validate the report, request local opening when supported, give its path and **STOP for user approval**. Opening, answering grilling, liking a diagram or a generic initial request is not approval of an unseen plan. Record an explicit waiver only when actually given.

Before coding, record the approving response, displayed revision/report, selected choices, scope and exclusions. Reuse valid existing approval. Material behavior/architecture/dependency/interface/cost/destructive/publication changes require renewed approval; routine implementation within the chosen approach does not.

## 5. Execute recoverable units

Before each unit, save intended changes and verification; after it, save actual results and the next safe action. Keep the established task records authoritative; no duplicate handoff or revision-tracking system. Reconcile records with files on resumption.

Use applicable specialists within the approved scope. Before adding a helper, wrapper, service, manager, mapper, fallback, compatibility layer or new configuration surface, run a **necessity check**: name the concrete problem it solves, why existing owners cannot express it clearly, and what complexity would return if it were removed. Prefer the smaller design when behavior stays correct. Keep behavior at its owner; justify normalization and fallback values against real contracts. Comments explain non-obvious reasons, not syntax. Update existing docs and remove directly obsolete callers/config/tests/debug code. Track explicitly approved migration leftovers.

Use subagents only when available and useful, with clear write ownership. Pass each worker the same output parent, ownership and artifact limits. They return evidence to the record owner. Sequential work is valid; self-review is not independent review. Expected regression-test failures are normal; distinguish task-caused, baseline and environment failures before asking for a decision.

## 6. Verify and finish honestly

Use [AUDIT.md](AUDIT.md). Check requested behavior, alternate/error paths, cleanup, records and actual task-attributable staged/unstaged/untracked changes. Invoke `code-review` for code; use `writing-for-agents` for skill/instruction changes. Review helpers and prose against concrete examples, not a vague “no slop” claim. Rerun affected checks after repairs.

For visual changes, compare controlled screenshots against the approved reference and inspect meaning, navigation and readability. Never replace a failed baseline automatically. A screenshot match is not proof of comprehension or correct behavior. Before consequential plans/reports/final explanations, apply the cold-reader check in WRITING.md: a new reader must be able to state what exists, what changes, what stays unchanged, why it matters and how success is checked.

Do not automatically stage, commit, push, upload, deploy, reset or discard. Finish the artifact lifecycle under ARTIFACTS.md: clean only eligible own scratch, preserve required evidence and note unresolved consumers. Report observed results, untested areas and retained artifact paths; no extra cleanup report. Mark done only when acceptance is met or an explicit limit is recorded. Preserve a concise checkpoint for another agent.

## Load only when relevant

Requested PDF: [PDF-DELIVERABLE.md](PDF-DELIVERABLE.md). Preparing a request elsewhere: [CHATGPT-PROMPTS.md](CHATGPT-PROMPTS.md). Evaluating optional maintenance/browser helpers: [OPTIONAL-HELPERS.md](OPTIONAL-HELPERS.md); never prerequisites for normal tasks.
