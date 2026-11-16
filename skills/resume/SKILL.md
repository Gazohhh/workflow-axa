---
name: resume
description: "Pick up an existing workflow task: report where it really stands (status), continue it safely after a session, account or agent switch (continue), or write a handoff into its records (handoff). Reconciles PLAN/TODO/FINDINGS/DECISIONS with the worktree; never silently creates a new task."
---

# Resume

Work from the records and the code, not from memory. Write for someone new to the project. Pick the mode from the request: **status** ("where are we?"), **continue** ("continue", "pick up", "resume"), **handoff** ("write a handoff"). No mode stated: status.

## Find and reconcile (every mode)

1. Read project rules and locate the named or current task. If several plausible tasks match, show the smallest useful distinction and ask which one; do not choose silently. If none exists, say so rather than creating one. For an overview of all tasks, run the workflow folder's `scripts/open_items.py <tasks-root>` first: it lists open, blocked, paused and conflicting or unbacked completion claims. Closed or removed items are not test passes.
2. Read PLAN/TODO/FINDINGS/DECISIONS (or legacy STATUS.md and inline decisions, without demanding missing templates) and the relevant artifacts. Reconcile them with the branch or worktree, uncommitted changes, recorded verification and specialist availability. A checked TODO is not proof after its files changed; interrupted work is uncertain until inspected.
3. Separate **agreement**, **implementation approval**, **implementation** and **verification or owner acceptance**. Approval is the task's approved offer. `record.py offer list <task-folder>` shows its cached state only, never authority by itself: the hook re-checks the presentation, the owner's answer and any later withdrawal, narrowing or stop from the conversation history before each write. On a host without the hook, check that evidence yourself in the transcripts before continuing. A task the owner listed as a pre-offer approval at the upgrade keeps its Approval line for its recorded scope. Resolve conflicting statements from evidence, not timestamps or revision numbers. Old reports are history: never edit or offer to edit an old report.

## status (read-only)

Explain in plain language: goal, current status, completed work with evidence, open work, unresolved owner decisions, stale records, risks and the **next safe action**, with the phase skill that would come next. Classify work as verified complete, implemented but needs re-verification, in progress, blocked, not started, removed by owner, superseded, not applicable or unknown. Removed work is not a passed test; a saved report's pending badge is historical. Report contradictions without resolving them.

No edits of any kind: no application or record changes, plan folders, approvals, staging, commits or installs; no tests, screenshots or saved status reports just to report status. Report missing or stale rules, unknown UI authority or design-pending work as a blocker to the next affected action, not to this answer. To go on, the owner asks for continue.

## continue

1. Apply the installed workflow RULES.md readiness gate first, even if rule-maker never ran. Revalidate a recorded *Skip for this task* (its named gaps) and changed inputs; an unchanged skip is not asked again. If the task identity is ambiguous, ask before writing.
2. "Continue this task" from the owner authorizes a takeover: record it and make sure nobody else is still writing. On another machine the records are not the code; move working changes only by an approved method.
3. An unchanged scope keeps its approval: the approved offer holds across sessions until a withdrawal, narrowing or stop, so do not restart grilling or either gate because the agent or session changed. A changed scope is a revised offer (`record.py offer revise`) and the one question again. If scope materially changed or authority evidence is invalid, reopen only the affected part: behavior through `workflow-clarify`, tickets through `workflow-specify`. A task awaiting an answer stays paused. For legacy tasks follow workflow/VISUAL-REVIEW.md "Legacy approval recovery"; never rewrite an Approval quote.
4. If the next unit is approved, continue with the phase skill `workflow` routes to (normally `workflow-execute`, or `workflow-deliver` once tickets are done) and update only this task's records. Keep paths, IDs, anchors, earlier outcomes and presented reports; no new revision for a rerun or progress update, and no bulk migration of older records.
5. Git and publishing follow workflow SKILL.md "Always"; never discard changes unless explicitly authorized. For resumed UI work, reload shared DESIGN.md and local ui-design and reconcile mode, authority, kit revision, preview and pending design acceptance before affected work; an old approval grants no new styling permission.

Before producing output, follow ARTIFACTS.md: reuse the task's output parent (a new agent is not a new artifact root) and clean only verified owned disposable output, never unknown files from the interrupted session.

## handoff (writes only when asked)

Write one short handoff into the task's own records, never a temp file: `python -X utf8 -I <workflow>/scripts/record.py replace-section <task>/PLAN.md "## Handoff" -` with the text on standard input. It holds the current state, the evidence paths, open owner decisions, what not to repeat, and the next skill by name. Redact secrets, tokens and private paths outside the project. Replace the previous handoff; keep history in FINDINGS and DECISIONS.
