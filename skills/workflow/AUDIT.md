# Final-state audit

Review the task-attributable changes against the approved goal, scope, project rules, and actual final files. Include relevant untracked files, callers, and documentation outside the edited set. Inspect adjacent code to understand impact, but do not turn pre-existing unrelated issues into an unauthorized refactor. Record those separately when material.

For code changes, invoke installed `code-review` with the C adapter in [SPECIALISTS.md](SPECIALISTS.md). Its Standards and Spec reviews complement this workflow audit; neither is a reason to stage, commit, publish a tracker issue or ignore uncommitted work. For agent-document design, apply `writing-for-agents`; do not force a code diff review onto a docs-only task.

Prefer a reviewer who did not implement the change. Give them the task record, approval, repository rules, relevant diff/files, and observed verification—not a claim that everything passed. Without an independent reviewer, perform a distinct self-review and identify it as such.

For each category record `PASS`, `ISSUE`, `NOT APPLICABLE` with a reason, or `NOT VERIFIED` with the gap. A checklist tick without inspected evidence is not a pass.

| Category | Check |
|---|---|
| Intent and authority | Does the result meet the approved acceptance criteria without unapproved behavior, dependency, interface, cost, or scope changes? |
| Reach and correctness | Original symptom, normal/edge/error cases, second callers, alternative entrypoints, configuration, data and lifecycle effects. |
| Replacement cleanup | Old implementation/callers/exports/flags/config/tests/assets/docs/debugging scaffolding accounted for; no competing behavior left accidentally. |
| Maintainability | Existing owner, clear data flow, justified helpers, useful comments, no speculative wrappers or unrelated churn. |
| Verification | Actual commands and outputs, behavioral tests through meaningful interfaces, original reproduction, integration where relevant, final-state evidence. |
| Documentation and recovery | Correct existing task reused or a new one justified; meaningful questions and answer sources recorded; existing authoritative docs match; task state, decisions, TODO evidence and next step allow a fresh agent to continue. |
| Reader clarity | Apply [WRITING.md](WRITING.md): concrete goal/change/consequence first, technical evidence accessible, no concealed material uncertainty or duplicate boilerplate. |
| Specialist integration | Correct resolved skill actually loaded/invoked; selected routes covered, adapters honored, changed/missing dependencies and exceptions explicit, outputs inspected. |
| Worktree and privacy | User edits/index intent preserved, ownership clear, no secrets or unapproved external actions. |

## Practical maintainability criteria

A helper earns its place by expressing a domain operation, hiding substantial detail, establishing a real boundary, or removing worthwhile repetition. A `normalize` function needs an actual input contract and a reason to transform it; the name is not evidence either way. Check that coercion and fallback values do not hide invalid data or alter behavior without approval.

Ask whether removing a wrapper makes the program simpler or merely spreads necessary complexity into its callers. Avoid a new general-purpose system for one local use unless the task needs that boundary. Prefer existing project conventions to a reviewer's personal style.

Comments explain constraints, intent, externally required quirks, or surprising behavior. They need not narrate syntax, repeat good names, preserve deleted code, or restate the task ticket. Document public contracts or safety constraints when needed; do not enforce an arbitrary comment-to-code ratio.

Illustrative examples, not samples supplied by the user:
- Weak: a one-use `normalizeEnabled` wrapper that silently converts any missing/invalid value into `true` without an agreed contract.
- Useful: a tested boundary parser implementing the documented formats accepted from a legacy importer.
- Weak comment: `Increment the counter.`
- Useful comment: `Keep this ID stable: saved playlists reference it.`

## Cleanup boundaries

For replacements, trace relevant consumers and remove or update the directly obsolete implementation, exports, flags, scripts, dependencies, tests, comments and documentation within scope. A repository search with no matches is not proof of disuse when reflection, asset references, plugin discovery, generated code or external consumers may apply. Check the applicable mechanisms first.

An intentionally staged migration may retain old code only with a recorded reason, ownership, and removal condition/task. Do not add a fallback or compatibility layer just to avoid deciding whether it is required. Unrelated dead code is a separate finding, not free cleanup authority.

## Verification and repairs

Separate expected regression-test failures before the fix, failures caused by this task, unrelated baseline failures, and unavailable environments. A new test should fail for the intended reason before a bug fix when feasible; a missing import alone does not establish reproduction. Never weaken tests or acceptance criteria to manufacture a green result.

Repair task-caused defects under the existing approval when behavior and scope remain agreed. After each material repair, rerun affected checks and re-inspect affected audit categories. Stop with a documented blocker when new authority, missing infrastructure or a genuine limit prevents completion; do not loop indefinitely or reuse stale proof. User acceptance of a coverage limit remains `NOT VERIFIED`, even when the task can close under that explicit exception.

## Grounding and visual approval

Verify requirement → current evidence → actual gap → task → acceptance traceability. Check existing/partial features were reused, not duplicated; no optional product ideas entered scope. For substantive implementation confirm a real user approval of the presented visual revision (or recorded explicit exception), before application writes. Compare delivered behavior and relevant error/permission paths to that revision. Renderer output and opening success are not approval evidence. A drift warning requires reconciliation, not automatic approval revocation or dismissal.

## Visual-review regression

For changed reports/visualizer code, verify that the actual feature flow remains primary (not cards or generic workflow phases), branches preserve source meaning, build dependencies and containment are separate, source ambiguities stay visible, and no style approval grants application authority. Check that codebase-map uses its bundled FLOWCHART-DESIGN.md and actual browser geometry/readability when available; no external diagram skill is required. Retain evidence/acceptance/exclusions and safe offline behavior. Native-size overflow must stay within the diagram wrapper; Fit is optional.


## Evidence of no-slop and visual fidelity

Use the examples above and in WRITING.md. Reject duplicate task folders for the same continuing work, empty copied sections, unnecessary helper layers, silent coercion and comments that restate syntax. Preserve useful contracts, boundary parsers and comments explaining non-obvious constraints. Do not invent a numeric comment ratio or ban a function name. Label synthetic examples; add real team-approved examples only when supplied.

When report/UI rendering changes, compare stable screenshots against a reviewed reference in the same environment. The package maintenance tools capture and compare images without replacing a baseline. Missing references or incompatible environments are NOT VERIFIED, not passes. A deliberate visual change needs the user's review before a new baseline is adopted. A passing comparison does not replace branch/meaning checks, manual accessibility review or a cold-reader check. Keep an application's own design system; the report theme is not permission to redesign the app.

## Test-output lifecycle

Apply [ARTIFACTS.md](ARTIFACTS.md). Check whether tests created redundant whole builds, per-task tools, unnecessary captures or another root for retries. Finish eligible own scratch cleanup and retain necessary results, failures and reference images. Verify active consumers and protected/tool-owned output before any removal. No deletion based only on age, ignore status or missing citations; no broad cleanup of earlier work. Record the retained paths and unresolved lifetime in existing findings or chat, not another report. A tool without retention needs an approved producer fix, not a global sweep.

## Current-state and history consistency

Check the current summary against TODO and actual evidence; distinguish scope approval, performed implementation, verification and owner acceptance. Flag a current paragraph that still says “not implemented” when later evidence records implementation, without changing the historical proposal itself. Check revision/phase/review mappings and the recorded reason/authority for material changes. Removed/superseded work is not verified work. A historical pending review can legitimately coexist with later approval. Preserve its bytes.

Update only the active task within scope; no closure-time bulk migration, renamed links, duplicate state files or generated report per checkpoint. If evidence is incomplete or contradictory, state the specific unknown and next safe action rather than manufacture a clean status.

## Rules readiness and policy integrity

Confirm the final scope still matches the applicable rules and any bounded exception. Check for new scoped files, dependency/host changes and unapproved policy weakening. Readiness is distinct from implementation authority, passing tests and safety enforcement. Unknown or missing prerequisites stop affected completion claims. Never let a self-authored readiness record count as independent proof of user consent.

## Risk-specific engineering review

Use the installed rule-maker ENGINEERING.md selection, not every rule on every task. Check relevant state/units/error boundaries, partial cleanup and stale results, bounded retries and duplicate effects, trusted authorisation and safe diagnostics, measured runtime cost, and supported version/data transitions. Tests must establish the agreed contract rather than repeat the implementation. Project-specific error, ownership, build and measurement rules still apply. No failure is resolved by hiding diagnostics, updating a baseline without authority, or introducing speculative infrastructure. Selected modules and sources inform the existing review; do not create another audit workflow or compliance file.
