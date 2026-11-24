# Final-state audit

`workflow-execute` applies these categories to each ticket and to the integrated whole; `workflow-deliver` checks those reviews happened and their findings closed, without repeating them. Review the task's changes against the approved goal, scope, project rules and final files, including relevant untracked files, callers and documentation outside the edited set. Record material pre-existing unrelated issues separately instead of refactoring them.

For code changes, use this package's `code-review` skill (`../code-review/SKILL.md`); it sets the reviewer count and what counts as a finding, and it is never a reason to stage, commit, publish a tracker issue or ignore uncommitted work. For agent-document design, apply `writing-for-agents`; do not force a code diff review onto a docs-only task. When a tool, test, validator or other document reads the changed text (asserted phrases, parsed headings, counts, links), that review also follows `../code-review/BLAST-RADIUS.md`.

Prefer a reviewer who did not implement the change. Give them the task record, approval, repository rules, relevant diff/files and observed verification, not a claim that everything passed. Without an independent reviewer, perform a distinct self-review and label it.

For each category record `PASS`, `ISSUE`, `NOT APPLICABLE` with a reason, or `NOT VERIFIED` with the gap. A checklist tick without inspected evidence is not a pass. An `ISSUE` needs a finding as code-review defines it; anything else is a note and starts no repair.

| Category | Check |
|---|---|
| Intent and authority | Does the result meet the approved acceptance criteria without unapproved behavior, dependency, interface, cost, or scope changes? |
| Reach and correctness | Original symptom, normal/edge/error cases, second callers, alternative entrypoints, configuration, data and lifecycle effects. |
| Replacement cleanup | Old implementation/callers/exports/flags/config/tests/assets/docs/debugging scaffolding accounted for; no competing behavior left accidentally. |
| Maintainability | Existing owner, clear data flow, justified helpers, no comments beyond CORE's exceptions, no speculative wrappers or unrelated churn. |
| Verification | Actual commands and outputs, behavioral tests through meaningful interfaces, original reproduction, integration where relevant, final-state evidence. |
| Documentation and recovery | Correct existing task reused or a new one justified; meaningful questions and answer sources recorded; existing authoritative docs match; task state, decisions, TODO evidence and next step allow a fresh agent to continue. |
| Reader clarity | Apply [WRITING.md](WRITING.md), its "Cited sources" included: concrete goal/change/consequence first, technical evidence accessible, no concealed material uncertainty or duplicate boilerplate. |
| Specialist integration | Correct resolved skill actually loaded/invoked; selected routes covered, adapters honored, changed/missing dependencies and exceptions explicit, outputs inspected. |
| Worktree and privacy | User edits/index intent preserved, ownership clear, no secrets or unapproved external actions. |

## Output read

When the reviewed work creates or changes the content of a message, report, dashboard or document for a person (not agent instructions, not a rewording that keeps the content), this comes before any review against the plan or the diff. Give a fresh reviewer only the finished output and who reads it: no plan, spec, diff or conversation. The reviewer returns, for each part, which question it answers for that reader (or "none"), then the obvious questions this reader would ask that no part answers.

Only then compare that list with the spec. A left-out question that the agreement with the owner excludes in words (its approved offer included) is closed. Every other one goes to the owner as an open choice before delivery, all in one question, most important first: never a note, and not a finding either, because only the owner can settle what the output must answer. In a task, record the result in FINDINGS and the answer in DECISIONS.

Run it once per finished output, and again only when its content changes. A plan or an idea has no finished output: read the current output it changes or a sample, else record `NOT VERIFIED`. Without subagents, read the output yourself before you reopen the plan, labeled self-check.

## Necessity check

Before adding a helper, wrapper, service, manager, mapper, fallback, compatibility layer or new configuration surface, name the concrete problem it solves, why existing owners cannot express it clearly, and what complexity would return if it were removed. Prefer the smaller design when behavior stays correct. Specification, execution and review all apply this check.

A helper earns its place by expressing a domain operation, hiding substantial detail, establishing a real boundary, or removing worthwhile repetition; its name is not evidence. Coercion and fallback values must not hide invalid data or alter behavior without approval. Prefer project conventions to a reviewer's personal style.

New code carries no comments except CORE's exceptions (licence headers, an unchangeable constraint with its link, public API doc comments, tool-required text, issue links). Comments are claims, not evidence: check the code, and report a comment that contradicts it as a possible bug (CORE). Illustrative examples, not supplied by the user:
- Weak: a one-use `normalizeEnabled` wrapper that silently turns any missing or invalid value into `true`.
- Useful: a tested boundary parser for the documented formats a legacy importer accepts.
- Weak: a comment such as `Keep this ID stable: saved playlists reference it.`
- Useful: the name `stablePlaylistId` and a test that saved playlists still resolve.

Reject duplicate task folders for continuing work, empty copied sections and comments that restate syntax. Do not invent a numeric comment ratio or ban a function name.

## Cleanup boundaries

For replacements, trace consumers and remove or update what the change made obsolete within scope. A search with no matches is not proof of disuse when reflection, asset references, plugin discovery, generated code or external consumers may apply. A staged migration may keep old code only with a recorded reason, owner and removal condition. Do not add a fallback just to avoid deciding whether it is required. Unrelated dead code is a separate finding, not cleanup authority.

## Verification and repairs

Separate expected failures before the fix, failures this task caused, unrelated baseline failures and unavailable environments. Red before green follows `tdd`. Never weaken tests or acceptance criteria to manufacture a green result.

Repair task-caused findings under the existing approval while behavior and scope stay agreed; re-review follows `code-review`. Stop with a documented blocker when new authority, missing infrastructure or a genuine limit prevents completion; never loop or reuse stale proof. A user-accepted coverage limit stays `NOT VERIFIED`.

## Grounding and approval

Trace requirement → evidence → gap → task → acceptance; existing features reused, no optional ideas in scope. Substantive implementation needs the agreement (or its recorded `not required` for a lightweight edit or a one-ticket offer) and an approved offer, verified from its presentation and the owner's answer (for a legacy task, its recorded Approval line), both before application writes. Compare delivered behavior and error/permission paths to that offer. Renderer output is not approval evidence; a drift warning needs reconciliation, not automatic revocation or dismissal.

## Report and visualizer changes

When a change touches report or visualizer code, the renderer or how a report or UI screen renders, also read [AUDIT-REPORTS.md](AUDIT-REPORTS.md) whole and apply it.

## Test output

Apply [ARTIFACTS.md](ARTIFACTS.md); record retained paths and unresolved lifetimes in existing findings or chat.

## Current state and history

Check the current summary against TODO and evidence; keep agreement, implementation approval, implementation, verification and owner acceptance distinct. Flag a current paragraph that later evidence contradicts; leave historical proposals and pending reviews unchanged. Removed or superseded work is not verified work. If evidence is incomplete or contradictory, state the unknown and the next safe action.

## Rules readiness

Confirm the final scope still matches the applicable rules and any bounded exception; check for new scoped files, dependency or host changes and policy weakening. Readiness is distinct from implementation authority, passing tests and safety enforcement, and a self-authored readiness record never proves user consent.

## Risk-specific engineering review

Use the installed rule-maker ENGINEERING.md selection, not every rule on every task. Tests establish the agreed contract rather than repeat the implementation. No failure is resolved by hiding diagnostics, updating a baseline without authority or adding speculative infrastructure.

## Application UI

For application UI, apply local ui-design VERIFY.md to the task's changes and the recorded mode. Behavior tests passed, design accepted and release ready are separate outcomes; missing device/browser evidence stays unverified.
