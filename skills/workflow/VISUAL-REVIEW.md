# The offer, the one question and the optional plan report

This file owns both approval gates. `workflow-clarify` runs the agreement, `workflow-specify` the offer and the one question.

## The gates

| Gate | The user confirms | Shown as | Allows | Recorded in |
|---|---|---|---|---|
| 1 — Agreement | Behavior, scope, exclusions, journeys, acceptance, assumptions | PLAN `## Agreement` + chat summary | Tickets and the offer; **no code** | Checkpoint `Agreement` line, DECISIONS |
| 2 — Implementation approval | The offer: behavior summary, paths, operations, exclusions and checks | The offer and the one question (the report on *Show review.html first* or when asked) | Code and tests inside the approved offer | Checkpoint `Offer: #<id>`, DECISIONS (the hook reads the answer) |

Both apply to features, behavior fixes, architecture changes and material scope changes. Research and explanation never reach the gates. Docs-only work and PDF deliverables keep their own route ([PDF-DELIVERABLE.md](PDF-DELIVERABLE.md)); a small docs fix is a lightweight edit. A visual-only map authorizes nothing.

- **Agreement is never permission to code.**
- **Legacy**: a task approved under the old single gate holds both, for its recorded scope ("Legacy approval recovery"); don't ask for a retroactive agreement.
- **Agreement waivers** are explicit and bounded: record the user's words, the scope and what still needs approval. Time pressure or "go ahead" on an unseen plan is not a waiver. Implementation approval has no waiver: the hook honours none. A non-interactive session, a request for a finished result or "don't ask me" is never a waiver; stop and ask.
- **No separate agreement** for a lightweight edit, or for one-ticket work when clarification left no open choice (a visible or accessibility choice the user has not made is an open choice, not an "assumption you can reject"): one journey, no new interface, dependency, data migration, security or UI-kit question. This is the default for such work: record Agreement `not required — lightweight` or `not required — one-ticket offer` without asking, then `workflow-specify`. The offer's behavior summary carries the agreement. Multi-ticket work and anything open go through the agreement first.
- **Every implementation approval is an offer with the one question** (workflow-specify step 5): the minimal offer for a lightweight edit (files, check, one-line why), one ticket for one-ticket work, the full ticket list for multi-ticket work. A lightweight offer's question has only *Approve* and *Change something*. The HTML report is built only when the owner answers *Show review.html first*, or asks for it.
- **Don't re-ask** after implementation approval: routine tickets, order, reruns and in-scope repairs proceed.
- **Changes reopen only what they touch**: a material change to behavior, scope, risk, interface, dependency, cost or protected areas reopens the agreement for those items, then implementation approval for their tickets.

The hook enforces the offer's paths, operations and the owner's answer. Whether a change is lightweight or one-ticket work is enforced by instructions only.

## Prepare the report

Only on *Show review.html first* or when the owner asks. Keep descriptive titles separate from the offer id; never silently relabel an approval.

1. Check the agreement is recorded (agreed, legacy, waived or not required) and the tickets exist in TODO. A remaining blocking choice makes the report a **draft**.
2. Run `codebase-map` in compare mode with the task folder, revision and destination (the project's review folder, else `reviews/` in the task folder), including its `task_report` content. It owns the flowchart, screen flow, validation, rendering, the cold-reader check and opening the file. The report shows the real feature flow; the UI screen flow goes into the same full report, and a standalone prototype does not replace the report. The task records stay the source; write its text with [WRITING.md](WRITING.md). Start the JSON from codebase-map's `examples/review.json` (UI: `examples/ui-review/ui-task-review-r2.json`) and TASK-REPORT.md, never from another task's report. Set `write_paths` to the same paths as the offer; the offer, not the report, is what the hook checks.
   Run the renderer's `--validate-input` mode and fix errors in the same JSON. Then record the destination and awaiting-approval checkpoint, check the sources again and render once.
3. Read the rendered report whole by its `docs/plans/<task>/...` path, then give the user that path.
4. The owner asked for this report with *Show review.html first*: present the offer again as `workflow-specify` step 5 says, so the owner can now answer *Approve from this summary* or *Change something* (with the question tool, offer only those two). **STOP.** Until the answer, the proposed scope gets no code, tests, dependencies, migrations or Git actions; only task records and the report change. Unaffected approved work and separately authorized checks continue within their limits.

## Read the answer

The answer to the one question decides; the hook reads it from the conversation. Opening the file, choosing a diagram tab, answering grilling, silence or "looks nice" approves nothing; the HTML has no approve button. Qualified answers, corrections and what to record: `workflow-specify` step 5 owns them. An approval from an earlier session holds for the unchanged offer. A later withdrawal or narrowing ends it: present the offer again (narrowed, if the owner narrowed it). A stop only pauses the work: when the owner says to continue, the approval holds again with no new question. Approving a presented offer (its question's approve button, or `/approve <N>` typed as the answer to its presentation) also counts as continuing. Never build the rejected version.

## Superseded review cleanup

Keep one filename while a draft is unpresented; use the renderer's guarded replacement instead of retry copies. When the owner has accepted a replacement report, read [REPORT-FILES.md](REPORT-FILES.md) "Superseded review cleanup" whole before you ask about, retain or remove any older file.

## Legacy approval recovery

When a task's checkpoint has a `- Approval (gate two):` line or a `legacy` Agreement (a task the owner listed as a pre-offer approval at the upgrade), read [LEGACY-APPROVALS.md](LEGACY-APPROVALS.md) whole before you rely on, reconfirm or record that approval. Every other task uses offers.

## Explicit exceptions and paid evaluation

An exceptional permission needs its own answer: a generic "yes to all recommendations" grants no plain-HTML exception (DESIGN.md rule 4) and settles no spending cap. An agent's recommendation is never the owner's instruction. When you are about to launch a separately paid model or evaluation batch, read [PAID-EVALUATION.md](PAID-EVALUATION.md) first; normal authorized tool calls need no payment question.

## Saved reports are snapshots

A report shows the moment it was made; its "awaiting approval" badge is history, not current status. Never rewrite a presented or approved HTML/JSON file. Until a replacement is accepted, never delete or offer to delete a presented or approved report; afterwards follow "Superseded review cleanup". Current state lives in the checkpoint. When the offer's presentation decision was `html-first`, make a new dated snapshot at implementation approval and at delivery (reuse rule in `workflow-deliver` step 8); otherwise only when the user asks. Never per checkpoint or from `resume` (status). Old reports are not migrated.

## UI work

Put the ui-design mode, mirrored elements (`file:line`, tag, classes), preview and any design-pending release limit in the plan and report fields. The **screen diagram** (codebase-map's `ui_review` screen-flow view in the same full report) shows current and proposed screens with interaction arrows and, per screen, the existing elements it copies (`ui_review` `elements`) with their source files. With a design kit, both are **kit screens** (codebase-map/UI-FLOW.md "Kit screens"). Without one, capture the current screen when safe and sketch the proposed one. A sketch shows structure, not the look. A UI-visible change without the diagram keeps the report a draft. Binding and snapshot checks: codebase-map/UI-FLOW.md. Do not alter the approved report shell. CSS and unmatched elements follow `../rule-maker/rules/DESIGN.md` rules 1 and 4. Designer acceptance is a separate recorded outcome.
