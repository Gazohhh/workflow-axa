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
| Documentation and recovery | Existing authoritative docs match; task state, decisions, TODO evidence and next step allow a fresh agent to continue. |
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
