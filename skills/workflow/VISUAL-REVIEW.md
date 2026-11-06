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

Name numbered revisions `r1`, `r2`, and so on in both the report and checkpoint. The Claude gate recognizes this form. Keep descriptive titles separate. For an approved report with another label, preserve its bytes and use resume-task to reconcile its identity with the owner's explicit answer. Never silently relabel an approval.

1. Check gate one is recorded (agreed, legacy or waived), or this is the "Both gates in one message" case, and the tickets exist in TODO. A remaining blocking choice makes the report a **draft**.
2. Run `codebase-map` in compare mode with the task folder, revision and destination (the project's review folder, else `reviews/` in the task folder), including its `task_report` content. It owns the flowchart, UI screen flow, validation, rendering checks, the cold-reader check and opening the file; the report must show the real feature flow; for UI it adds the screen flow with real captures where safe, otherwise a labelled sketch, to the same full report, and a standalone prototype does not replace the report. PLAN/TODO/FINDINGS/DECISIONS stay the source. Write its text with the `simple-english` skill (`../simple-english/SKILL.md`). Start the JSON from codebase-map's `examples/review.json` (UI: `examples/ui-review/ui-task-review-r2.json`) and TASK-REPORT.md, never from another task's report. Set `write_paths` to the repository files (or folders ending in `/`) the plan may change; after approval the phase gate blocks other file writes.
   Before recording the final report path, use the renderer's `--validate-input` mode. Fix schema and wording errors in the same JSON. Then record the destination and awaiting-approval checkpoint (or draft for the combined-gates case), check the final sources again and render once. The preflight writes no report or Python cache and opens no browser. It does not prove approval or semantic accuracy. Preserve every presented or approved snapshot.

3. Read the rendered report whole by its `docs/plans/<task>/...` path (the hook records its fingerprint), then give the user that path; a launch request is not proof it displayed.
4. Ask: "This plan implements the behavior we agreed. Approve it to start implementation, or describe what needs changing." **STOP.** Until the answer, the proposed scope gets no code, tests, dependencies, migrations or Git actions; only task records and the report change. Unaffected approved work, authorized baseline checks and separately approved diagnostics continue within their limits.

## Read the answer

A clear "yes, proceed" to this report approves the shown revision. Opening the file, choosing a diagram tab, answering grilling, silence or "looks nice" approves nothing; the HTML has no approve button. Record the answer, date, revision, report path, inclusions and exclusions in PLAN and DECISIONS before coding.

An approval with a condition that changes which files may change (for example "but nothing in tests/") is a correction: update the tickets and `write_paths` in a new revision, present it and get it approved before implementation.

A correction at gate two: behavior or scope goes back to `workflow-clarify` for those items; tickets, tests or presentation stay in `workflow-specify`. Mark the old proposal superseded and present the new revision. Never build the rejected version.

On resume, the recorded approval stands if it still covers the work; don't ask again or re-render without a reason.

## Superseded review cleanup

Keep one filename while a draft is unpresented; use the renderer's guarded replacement instead of making retry copies. When a new review revision is ready, inspect older HTML/JSON pairs and associated captures in this task. Ask once, separately from plan approval: "Delete these superseded review files after the replacement is accepted, or retain them?" Name the exact files and recommend removing only redundant, unneeded revisions. Silence preserves files; a plan approval is not deletion approval.

Before offering deletion, identify active approval/fingerprint dependencies, needed comparisons, rollback proof and explicit retention instructions. Keep needed evidence and state its concrete reason in the current task record. Label retained older revisions as superseded in that record, with the replacement link; do not rewrite their historical contents. If retiring a report would invalidate active approval, reconcile approval to the replacement first. After explicit file-scoped permission, update current links and remove only the selected unused files. Preserve the approval decision and explain that its retired artifact is unavailable; never invent proof from a saved hash. No bulk cleanup, automatic archiving, or changes to another checkout. Reuse the existing task record rather than creating a cleanup report.


## Legacy approval recovery

A format mismatch does not cancel valid approval. `resume-task` first reconciles the same task/worktree, original report, complete real user answer, restrictions and changes since that answer. Preserve the old report and IDs. An unchanged single-gate scope still holds both gates; do not fabricate a revision just to satisfy a parser.

The hook accepts an explicit `legacy` Approval line with **one named existing report** even without a numbered revision when its presentation and the full owner answer are found in accessible current/earlier project transcripts and the checkpoint names no conflicting revision. This checks provenance, not semantic scope. Any approval found in an earlier session carries over only for the unchanged report, with no later revocation, no stop without a continuation since, and no later restriction missing from the checkpoint; otherwise show the same report again, ask whether it still holds, and add the owner's exact answer on a separate `- Reconfirmed (gate two): r<N>, <date>: "<words>"` line. The original Approval quote stays unchanged. Record `legacy` only after the scope comparison. No transcript, missing report, contradictory scope or uncertain authority means a focused clarify/specify question, not automatic trust or a complete restarted interview. Never suggest editing, disabling or bypassing the hook to continue. Record established approval before the first edit attempt; do not use a blocked edit to discover whether permission is recorded.

## Explicit exceptions and paid evaluation

Ordinary clear approval of a shown plan remains valid. Exceptional permissions need a separately identifiable answer: a generic "yes to all recommendations" does not grant a plain-HTML exception or resolve an unanswered spending cap. Use design.md rule 4 for UI. Retain all conditions and the question they answer; an agent's recommendation is never the owner's instruction.

Before **launching a separately paid model/evaluation batch**, present its cases, allowed sessions/subagents/retries, model/settings, hard total ceiling with units/currency, included work and how usage is bounded. A suggested cap, `$[AMOUNT]`, "don't worry too much about costs", silence or a previous batch's limit is not approval. Ask for the actual cap (or a specific proposed-cap option that the owner deliberately selects). Include orchestration, child sessions, retries and the single retro in the limit. Zero authorises no paid calls. This rule does not require another payment question for each already-authorised normal tool call.

Use a provider-enforced limit or conservative reservations/observable usage so in-flight calls cannot silently exceed the agreed ceiling; never schedule the nominal cap and hope the final cost fits. If full spend cannot be observed/bounded, disclose which parts are unknown and agree a measurable session/token limit instead before launch. Record budget, actual answer and usage in the existing evaluator record, not another required manifest. A per-session subtotal is not the whole batch. Stop at the agreed boundary or an actual safety violation; no automatic retry or subsequent batch. This policy is guidance: the package does not meter provider billing or enforce arbitrary paid API calls.

## Saved reports are snapshots

A report shows the moment it was made; its "awaiting approval" badge is history, not current status. Never rewrite, delete or offer to delete a presented or approved HTML/JSON file; a replaced report stays as history without asking. Current state lives in the checkpoint. Make a new dated snapshot at gate two, at delivery (rule in `workflow-deliver` step 8) or when the user asks, never per checkpoint or from `task-status`. Old reports are not migrated.

## UI work

Put the ui-design mode, mirrored elements (`file:line`, tag, classes), preview and any design-pending release limit in the plan and report fields. The flowchart explains behavior; the screen diagram (ui-design step 3) shows the screens: a real capture where safe, otherwise a labelled sketch, and for each proposed screen the existing elements it copies (`ui_review` `elements`). A UI-visible change without that diagram keeps the report a draft. Never write CSS or offer it as an option: an element nothing existing matches waits for design.md rule 4's question, and plain HTML needs the user's explicit instruction. Designer acceptance is a separate recorded outcome.
