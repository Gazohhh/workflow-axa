# The two gates and the HTML plan

This file owns both approval gates. `workflow-clarify` runs gate one, `workflow-specify` runs gate two; `resume-task`, `task-status` and `workflow-deliver` read what was recorded.

## The gates

| Gate | The user confirms | Shown as | Allows | Recorded in |
|---|---|---|---|---|
| 1 — Agreement | Behavior, scope, exclusions, journeys, acceptance, assumptions | PLAN `## Agreement` + chat summary | Tickets, test plan and the HTML report; **no code** | Checkpoint `Agreement` line, DECISIONS |
| 2 — Implementation approval | Tickets, dependencies, test strategy and the HTML report | The codebase-map report | Code and tests inside the approved tickets | Checkpoint `Approval` line, DECISIONS |

Both apply to features, behavior fixes, architecture changes and material scope changes. Research and explanation never reach the gates. A lightweight edit (router) skips both. Docs-only work and PDF deliverables keep their own route ([PDF-DELIVERABLE.md](PDF-DELIVERABLE.md), or a lightweight edit for a small fix), as before. A visual-only map authorizes nothing.

- **Agreement is never permission to code.**
- **Legacy**: a task approved under the old single gate holds both, for its recorded scope. Note that on the next checkpoint; don't ask for a retroactive agreement.
- **Waivers** are explicit and bounded: record the user's words, which gate, the scope and what still needs approval. Time pressure or "go ahead" on an unseen plan is not a waiver; an explicit "I don't need to see the plan, go" is a gate-two waiver for that task: record it and build only the agreed behavior.
- **Every gate-two request comes with a fresh HTML report**, small and combined changes included. Skip it only when the user explicitly says they don't want it; record their words. A plan in chat alone is not enough.
- **Both gates in one message** when clarification left no open choice and the change is small (a visible or accessibility choice the user has not made is an open choice, not an "assumption you can reject"): one journey, no new interface, dependency, data migration, security or UI-kit question. Show the agreement summary, the tickets and the report together and ask: "Agree to this behavior and approve this plan? Say yes to both, or tell me what to change." The report stays a draft, its agreement status `not-approved`, until that answer. Only an explicit yes to both records both lines (same date, same words); anything less is handled gate by gate. The user can always ask to see them separately.
- **Don't re-ask** after gate two: routine tickets, order, reruns and in-scope repairs proceed.
- **Changes reopen only what they touch**: a material change to behavior, scope, risk, interface, dependency, cost or protected areas reopens gate one for those items, then gate two for their tickets. Everything else keeps its approval.

## Prepare the report (gate two)

1. Check gate one is recorded (agreed, legacy or waived), or this is the "Both gates in one message" case, and the tickets exist in TODO. A remaining blocking choice makes the report a **draft**.
2. Run `codebase-map` in compare mode with the task folder, revision and destination (the project's review folder, else `reviews/` in the task folder), including its `task_report` content. It owns the flowchart, UI screen flow, validation, rendering checks, the cold-reader check and opening the file; the report must show the real feature flow; for UI it adds the screen flow with real captures where safe, otherwise a labelled sketch, to the same full report, and a standalone prototype does not replace the report. PLAN/TODO/FINDINGS/DECISIONS stay the source. Write its text with the `simple-english` skill (`../simple-english/SKILL.md`). Start the JSON from codebase-map's `examples/review.json` (UI: `examples/ui-review/ui-task-review-r2.json`) and TASK-REPORT.md, never from another task's report.
3. Give the user the absolute path; a launch request is not proof it displayed.
4. Save `awaiting-approval` (for "Both gates in one message" the report stays a draft, as that rule says) and ask: "This plan implements the behavior we agreed. Approve it to start implementation, or describe what needs changing." **STOP.** Until the answer, the proposed scope gets no code, tests, dependencies, migrations or Git actions; only task records and the report change. Unaffected approved work, authorized baseline checks and separately approved diagnostics continue within their limits.

## Read the answer

A clear "yes, proceed" to this report approves the shown revision. Opening the file, choosing a diagram tab, answering grilling, silence or "looks nice" approves nothing; the HTML has no approve button. Record the answer, date, revision, report path, inclusions and exclusions in PLAN and DECISIONS before coding.

A correction at gate two: behavior or scope goes back to `workflow-clarify` for those items; tickets, tests or presentation stay in `workflow-specify`. Mark the old proposal superseded and present the new revision. Never build the rejected version.

On resume, the recorded approval stands if it still covers the work; don't ask again or re-render without a reason.

## Saved reports are snapshots

A report shows the moment it was made; its "awaiting approval" badge is history, not current status. Never rewrite, delete or offer to delete a presented or approved HTML/JSON file; a replaced report stays as history without asking. Current state lives in the checkpoint. Make a new dated snapshot at gate two, at delivery (rule in `workflow-deliver` step 8) or when the user asks, never per checkpoint or from `task-status`. Old reports are not migrated.

## UI work

Put the ui-design mode, mirrored elements (`file:line`, tag, classes), preview and any design-pending release limit in the plan and report fields. The flowchart explains behavior; the screen diagram (ui-design step 3) shows the screens: a real capture where safe, otherwise a labelled sketch, and for each proposed screen the existing elements it copies (`ui_review` `elements`). A UI-visible change without that diagram keeps the report a draft. Never write CSS or offer it as an option: an element nothing existing matches waits for design.md rule 4's question, and plain HTML needs the user's explicit instruction. Designer acceptance is a separate recorded outcome.
