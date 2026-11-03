# Central engineering task report

Use optional `task_report` in schema 2 when the user requests a full engineering overview, or workflow-specify/workflow-deliver prepares one. Keep the existing flowchart, screen flow, comparison, scope and traceability. The bundled task_report.py helper validates and renders the added content; its scoped CSS leaves old reports unchanged.

PLAN, TODO, FINDINGS and DECISIONS (or their established equivalents) remain authoritative. Generate the JSON projection from those records, cite its source IDs and exact sections, and compare the projection to those records before presentation. Update records first; never hand-maintain an independent specification in HTML/JSON. A source hash proves byte identity, not that the agent interpreted the source correctly. Preserve every presented/approved HTML and JSON snapshot.

## Fields

`task_report` has `phase` (planning/progress/delivery), `agreement`, `sections`, `tickets`, `checks` and `acceptance_results`. Delivery also requires `completion` (complete/partial/blocked). An awaiting-approval or approved plan requires `screen_change`: `visible` when users see any change on screen (order, text, which rows show, layout), which also requires an application `ui_review` screen diagram ([UI-FLOW.md](UI-FLOW.md)), otherwise `none`. Never copy a sibling task's report without checking this. Unknown keys inside these new objects fail validation; older top-level extension behavior is unchanged.

Every sourced object uses `source` (an existing supplied source ID) and `locator` (the specific record heading, line or result). Text is escaped; no Markdown, raw HTML, scripts or executable commands are evaluated. Paragraph breaks and line breaks remain readable. Write every prose field with the `simple-english` skill (`../simple-english/SKILL.md`, Plain mode and its workflow-axa adaptation) and run its self-check before rendering; keep exact commands, identifiers and contractual terms.

| Object | Fields and meaning |
|---|---|
| `agreement` | `status`: approved/waived/legacy/not-required/not-approved/unknown; `summary`. Approved/waived needs exact `revision`, actual `response`, `source`, `locator`. Legacy (a pre-2.8 single-gate approval) and not-required (a lightweight edit) cite their record with `source`/`locator`, may name a `revision`, and never carry an invented `response`. Unapproved/unknown may cite a source but must not claim an approved revision/response. This is behavior/scope authority, separate from checkpoint.approval, which continues to mean implementation-plan authority. |
| `sections[]` | `id`, `title`, `text`, `source`, `locator`. IDs: request, agreement, specification, decisions, risks, testing, optional milestones, and delivery when applicable. All except milestones/delivery are required for a central overview. Put the original request and objectives in request; exclusions/edge cases in agreement; assumptions/unresolved questions in risks; implementation order in milestones. Split paragraphs for readability. |
| `tickets[]` | `task`, `specification`, `expected`, `source`, `locator`. Exactly one specification for each existing tasks[].id; existing task relationships, acceptance links, affected files and outcome remain in tasks. Describe implementation responsibility and expected behavior here, not another task status. |
| `checks[]` | `id`, `title`, `kind` (test/review/inspection), `status` (passed/failed/red/stale/limited/blocked/not-run; red = failed before the change, as the test-first plan expects, shown as "Failed before the change, as expected" and never cited as acceptance evidence; stale = passed on files that changed since), `expected`, `actual`, `limits`, `source`, `locator`; optional exact `command`. Name the relevant source/runtime identity in locator/limits. Reviews keep Standards and Spec findings distinct, with links to their fixes/rechecks. |
| `acceptance_results[]` | `acceptance` (existing acceptance ID), `status` (verified/partial/failed/unverified/waived/superseded), `checks` (check IDs), `note`, `source`, `locator`. Verified needs at least one passed check and no failed/unrun evidence among its references. Failed needs a failed check. Waiver and superseded (descoped) must cite the actual decision in note/source and are not a pass; superseded cites no checks. These are the report values of workflow-deliver's verdicts. |

During planning, checks/results may be empty. An approval-ready implementation report requires recorded approved/waived behavior agreement; neither field authenticates the user or grants authority. A draft may honestly show an unresolved agreement. A new implementation plan still follows the normal real-response approval gate.

## Layout

A report with `task_report` uses the owner's report design (`assets/report-style.css` and `assets/report-extra.js`, used unchanged; `report-style-compat.css` maps the older token names the screen diagram uses) and states each fact once. The page has a masthead, a header with the title, the understanding line, a status tag with one status sentence and an at-a-glance row (revision, tickets, checks verified, open questions, as-of date), then a sticky numbered contents list beside the sections. The contents list highlights the section being read, and a diagram that fits at 60% size or more starts on Fit. Reports without `task_report` keep the earlier layout unchanged.

1. Header: title, the `understanding` summary and one plain status sentence built from the agreement status and the phase (planning: plan state such as "Waiting for your OK on this plan"; progress: checkpoint implementation/verification and next action; delivery: "Delivered: complete/partial/blocked").
2. What you're approving (planning) or What was agreed: agreement summary, request, agreement, boundaries ("What stays the same") and decisions.
3. How it works: the flow views. Tabs read "After the change", "Today" and "Work order" (proposed flow, current flow, delivery view); other views keep their `tab`. Zoom controls are labelled separately.
4. What changes: the comparison rows as situation, today and after the change, without traceability links.
5. The work: specification, milestones and delivery sections, then one card per ticket with specification, expected result, dependencies by title, the verification of its acceptance items and any outcome.
6. How we'll know it works: the testing section, each acceptance item once with its verification and result, then each check once (status, expected, observed, limits, command).
7. Risks and open questions: the risks section, open_decisions and evidence limits.
8. Technical details (collapsed): provenance note, agreement record and response, plan approval record, checkpoint, revision history, requirements, traceability tables, source attribution for every sourced object, evidence, node/edge records and source fingerprints.

A numbered contents list links sections 2 to 7.

## Progress and delivery

Use `report_kind: task-overview` with the existing sourced checkpoint for delivery. Include every acceptance result, the final delivery section and an explicit completion state. Complete is permitted only with implemented work, applicable agreement/plan authority (approved, waived, legacy or not-required), every acceptance verified or superseded with at least one verified, every recorded check passed including at least one review, every task outcome terminal (verified/removed/superseded/not-applicable), every requirement covered by an acceptance item, no open decision and checkpoint verification passed. Partial/blocked output is valid and must explain unfinished or unverified work. An owner waiver, unavailable environment or known limitation cannot be disguised as verified completion.

The delivery section explains requested/agreed/implemented work, completed and open tickets, changed files/components, check and review outcomes, known limitations and follow-ups. Link exact evidence through checks and acceptance_results. Actual UI design acceptance and release readiness remain separate when relevant; reuse the existing UI screen-flow and kit source contract.

Generate snapshots at the gate-two review, at delivery (rule in workflow-deliver step 8) or when requested, not on every checkpoint. Progress updates normally remain in the records. Plan revision changes only when the agreement changes; a new dated progress snapshot may project the same plan revision. Do not overwrite a historical review to make its status look current. Before you show a report, keep one file name: finish the records first, then render, and re-render into that same file with `--replace-unpresented` (no `-v2`/`-v3` copies). Once the user has seen it, a change gets a new file.

## Verification

Validate through render_report.py and its freshness check. Inspect actual rendering at desktop and narrow widths, section navigation and long content. Check every displayed claim against its cited record and actual execution. Renderer tests establish structure, escaping and consistency; they do not prove test execution, completeness of requirements, reliable model behavior or human understanding.
