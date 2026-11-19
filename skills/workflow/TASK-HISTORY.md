# Task history: revisions, older records and tidying

Read this when a plan changes after agreement, when you resume or tidy an older task, when an older TODO repeats ticket IDs across revisions, or when you record UI state or an ADR. [TASK-FOLDER.md](TASK-FOLDER.md) owns where records live, what goes in each file and the checkpoint format.

## Qualified IDs

When an older TODO restarts T1 under each revision, address it as `D4/T1` or `D3/T1`; never guess which T1 a short reference means. New cross-revision references use that qualified identity. Do not renumber old records. In a file that repeats an ID, the overview table uses the qualified ID (`D4/T3`).

A report needs IDs without `/`: read [REPORT-FILES.md](REPORT-FILES.md) "Renderer ID aliases" when you put a qualified ID into report JSON.

## Tidying a TODO layout

A layout tidy changes layout, not state: keep a checkbox line as it is, or convert it only to a listed state that records the same fact, and keep contradictions visible. Run `open_items.py --task` before and after; any changed ticket state means the tidy changed content.

## Revisions

| Event | Record |
|---|---|
| Material change to behavior, approach, risk or protected scope | New proposed revision showing the delta; reopen the agreement, then implementation approval, for the affected parts only |
| Progress, blocker, rerun, account or agent switch | Update the checkpoint and items. No new plan revision, folder or report |
| Correction to an unpresented draft | Re-render into the same file with `--replace-unpresented`. The renderer refuses once the task records name the file or the report is approved; then render a new file |
| Superseding an agreement | Keep its scope and reason; point to what replaced which part |

An earlier revision that skipped a step is not a precedent: each new revision follows the current rules. Keep existing IDs (C3, P1-r1, review-r5) exactly and phase names separate from revision IDs; don't renumber. Keep one short revision log (in DECISIONS, or PLAN for small tasks): revision, report, change, why, outcome.

## Forward-only adoption

New structure applies forward. On a resumed old task, update only the checkpoint, directly affected current tickets, contradictory current wording and needed links; mark old text historical instead of rewriting its meaning. Do not bulk rewrite closed tasks, migrate old JSON, renumber IDs or reconstruct missing reviews. If an original review is missing, record that and use the remaining approval and decision records; its absence proves neither approval nor refusal. Escalate only authority you can't establish. Presented and approved HTML/JSON files are immutable snapshots.

## UI and ADR records

- **UI**: one checkpoint entry: area and mode, approving source, allowed components, preview, exceptions, design acceptance and release state (ui-design).
- **ADRs**: offer one only when `domain-modeling`'s criteria hold; a reversal is a new superseding ADR. Proposed ADRs are not accepted because time passed. Task progress stays in task records.
