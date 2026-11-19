# Final-state audit

`workflow-execute` applies these categories to each ticket and to the integrated whole; `workflow-deliver` checks that those reviews happened and their findings closed, without repeating them as its own audit. Review the task-attributable changes against the approved goal, scope, project rules, and actual final files. Include relevant untracked files, callers, and documentation outside the edited set. Inspect adjacent code to understand impact, but do not turn pre-existing unrelated issues into an unauthorized refactor. Record those separately when material.

For code changes, use this package's `code-review` skill (`../code-review/SKILL.md`) (its steps 1 and 2 cover the task diff and the spec). Its Standards and Spec reviews complement this workflow audit; neither is a reason to stage, commit, publish a tracker issue or ignore uncommitted work. For agent-document design, apply `writing-for-agents`; do not force a code diff review onto a docs-only task. When a tool, test, validator or other document reads the changed text (asserted phrases, parsed headings, counts, links), that review also follows `../code-review/BLAST-RADIUS.md`.

Prefer a reviewer who did not implement the change. Give them the task record, approval, repository rules, relevant diff/files, and observed verification—not a claim that everything passed. Without an independent reviewer, perform a distinct self-review and identify it as such.

For each category record `PASS`, `ISSUE`, `NOT APPLICABLE` with a reason, or `NOT VERIFIED` with the gap. A checklist tick without inspected evidence is not a pass.

| Category | Check |
|---|---|
| Intent and authority | Does the result meet the approved acceptance criteria without unapproved behavior, dependency, interface, cost, or scope changes? |
| Reach and correctness | Original symptom, normal/edge/error cases, second callers, alternative entrypoints, configuration, data and lifecycle effects. |
| Replacement cleanup | Old implementation/callers/exports/flags/config/tests/assets/docs/debugging scaffolding accounted for; no competing behavior left accidentally. |
| Maintainability | Existing owner, clear data flow, justified helpers, no comments beyond CORE's exceptions, no speculative wrappers or unrelated churn. |
| Verification | Actual commands and outputs, behavioral tests through meaningful interfaces, original reproduction, integration where relevant, final-state evidence. |
| Documentation and recovery | Correct existing task reused or a new one justified; meaningful questions and answer sources recorded; existing authoritative docs match; task state, decisions, TODO evidence and next step allow a fresh agent to continue. |
| Reader clarity | Apply [WRITING.md](WRITING.md): concrete goal/change/consequence first, technical evidence accessible, no concealed material uncertainty or duplicate boilerplate. |
| Specialist integration | Correct resolved skill actually loaded/invoked; selected routes covered, adapters honored, changed/missing dependencies and exceptions explicit, outputs inspected. |
| Worktree and privacy | User edits/index intent preserved, ownership clear, no secrets or unapproved external actions. |

## Practical maintainability criteria

**Necessity check.** Before adding a helper, wrapper, service, manager, mapper, fallback, compatibility layer or new configuration surface, name the concrete problem it solves, why existing owners cannot express it clearly, and what complexity would return if it were removed. Prefer the smaller design when behavior stays correct. Specification, execution and review all apply this same check.

A helper earns its place by expressing a domain operation, hiding substantial detail, establishing a real boundary, or removing worthwhile repetition. A `normalize` function needs an actual input contract and a reason to transform it; the name is not evidence either way. Check that coercion and fallback values do not hide invalid data or alter behavior without approval.

Ask whether removing a wrapper makes the program simpler or merely spreads necessary complexity into its callers. Avoid a new general-purpose system for one local use unless the task needs that boundary. Prefer existing project conventions to a reviewer's personal style.

New code carries no comments except CORE's exceptions (licence headers, an unchangeable constraint with its link, public API doc comments, tool-required text, issue links). Comments are claims, not evidence: check the code, and report a comment that contradicts it as a possible bug (CORE).

Illustrative examples, not samples supplied by the user:
- Weak: a one-use `normalizeEnabled` wrapper that silently converts any missing/invalid value into `true` without an agreed contract.
- Useful: a tested boundary parser implementing the documented formats accepted from a legacy importer.
- Weak: a comment such as `Keep this ID stable: saved playlists reference it.`
- Useful: the name `stablePlaylistId` and a test that saved playlists still resolve.

## Cleanup boundaries

For replacements, trace relevant consumers and remove or update the directly obsolete implementation, exports, flags, scripts, dependencies, tests, comments and documentation within scope. A repository search with no matches is not proof of disuse when reflection, asset references, plugin discovery, generated code or external consumers may apply. Check the applicable mechanisms first.

An intentionally staged migration may retain old code only with a recorded reason, ownership, and removal condition/task. Do not add a fallback or compatibility layer just to avoid deciding whether it is required. Unrelated dead code is a separate finding, not free cleanup authority.

## Verification and repairs

Separate expected regression-test failures before the fix, failures caused by this task, unrelated baseline failures, and unavailable environments. Red before green follows `tdd`; a missing import alone does not establish reproduction. Never weaken tests or acceptance criteria to manufacture a green result.

Repair task-caused defects under the existing approval when behavior and scope remain agreed; re-review follows `code-review`. Stop with a documented blocker when new authority, missing infrastructure or a genuine limit prevents completion; do not loop indefinitely or reuse stale proof. User acceptance of a coverage limit remains `NOT VERIFIED`, even when the task can close under that explicit exception.

## Grounding and visual approval

Verify requirement → current evidence → actual gap → task → acceptance traceability. Check existing/partial features were reused, not duplicated; no optional product ideas entered scope. For substantive implementation confirm the agreement (or its recorded `not required` for a lightweight edit or a one-ticket offer) and an approved offer, verified from its presentation and the owner's answer (for a legacy task, its recorded Approval line), both before application writes. Compare delivered behavior and relevant error/permission paths to that offer. Renderer output and opening success are not approval evidence. A drift warning requires reconciliation, not automatic approval revocation or dismissal.

## Report and visualizer changes

When a change touches report or visualizer code, the renderer or how a report or UI screen renders, also read [AUDIT-REPORTS.md](AUDIT-REPORTS.md) whole and apply it.

## Evidence of no-slop

Use the examples above and in WRITING.md. Reject duplicate task folders for the same continuing work, empty copied sections, unnecessary helper layers, silent coercion and comments that restate syntax. Preserve useful contracts, boundary parsers and comments explaining non-obvious constraints. Do not invent a numeric comment ratio or ban a function name. Label synthetic examples; add real team-approved examples only when supplied.

## Test-output lifecycle

Apply [ARTIFACTS.md](ARTIFACTS.md). Check whether tests created redundant whole builds, per-task tools, unnecessary captures or another root for retries. Finish eligible own scratch cleanup and retain necessary results, failures and reference images. Cleanup prerequisites are in ARTIFACTS.md. Record the retained paths and unresolved lifetime in existing findings or chat, not another report. A tool without retention needs an approved producer fix, not a global sweep.

## Current-state and history consistency

Check the current summary against TODO and actual evidence; distinguish agreement, implementation approval, performed implementation, verification and owner acceptance. Flag a current paragraph that still says “not implemented” when later evidence records implementation, without changing the historical proposal itself. Check revision/phase/review mappings and the recorded reason/authority for material changes. Removed/superseded work is not verified work. A historical pending review can legitimately coexist with later approval. Preserve its bytes.

Update only the active task within scope; no closure-time bulk migration, renamed links, duplicate state files or generated report per checkpoint. If evidence is incomplete or contradictory, state the specific unknown and next safe action rather than manufacture a clean status.

## Rules readiness and policy integrity

Confirm the final scope still matches the applicable rules and any bounded exception. Check for new scoped files, dependency/host changes and unapproved policy weakening. Readiness is distinct from implementation authority, passing tests and safety enforcement. Unknown or missing prerequisites stop affected completion claims. Never let a self-authored readiness record count as independent proof of user consent.

## Risk-specific engineering review

Use the installed rule-maker ENGINEERING.md selection, not every rule on every task. Check relevant state/units/error boundaries, partial cleanup and stale results, bounded retries and duplicate effects, trusted authorization and safe diagnostics, measured runtime cost, and supported version/data transitions. Tests must establish the agreed contract rather than repeat the implementation. Project-specific error, ownership, build and measurement rules still apply. No failure is resolved by hiding diagnostics, updating a baseline without authority, or introducing speculative infrastructure. Selected modules and sources inform the existing review; do not create another audit workflow or compliance file.

## Application UI boundary

For application UI, resolve local ui-design and apply its VERIFY.md to task-attributable changes and the recorded mode. Check actual approved components/variants/patterns rather than accepting arbitrary legacy classes. Review new/deleted markup, styles, visual props, assets and renderer/native configuration. Include shared component impact, functional IDs, accessible states and production exposure of previews. No invisible CSS-in-JS/utility/SVG/native bypass; no automatic stripping of old styles. Scan cues supplement, never replace, semantic/visual review. Behavior tests passed, design accepted and release ready are separate outcomes. Missing device/browser evidence remains unverified. Keep records/evidence in existing approved locations, not another UI report.
