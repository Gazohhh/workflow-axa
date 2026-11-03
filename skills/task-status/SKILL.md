---
name: task-status
description: "Inspect an existing workflow task and report where it really stands. Reconcile PLAN/TODO/FINDINGS/DECISIONS with the current worktree; do not implement or silently create a new task."
---

# Task status

Report the real state of an existing workflow task without implementing it. Write for someone new to the project.

1. Read project rules and locate the named/current task. If several plausible tasks match, show the smallest useful distinction and ask which one; do not choose silently. If none exists, say so rather than creating one.
2. For an overview of all tasks, run the workflow folder's `scripts/open_items.py <tasks-root>` first: it lists open, blocked and unbacked ticked items. Read PLAN/TODO/FINDINGS/DECISIONS and relevant artifacts; reconcile claims with the worktree, local changes and recorded verification. A checked TODO is not proof after its files changed.
3. Read the established current checkpoint (PLAN or legacy STATUS.md) and distinguish **agreement**, **implementation approval**, **implementation**, and **verification/owner acceptance**; a legacy single approval covers both gates for its scope. Name the phase skill that would come next. Classify work as verified complete, implemented but needs re-verification, in progress, blocked, not started, removed by owner, superseded, not applicable, or unknown. Removed work is not a passed test. A saved review's pending badge is historical. Preserve prior history; do not rewrite records merely to make status look clean.
4. Explain in plain language: goal, current status, completed work with evidence, open work, unresolved user decisions, stale records, risks and **next safe action**. Keep exact paths/checks below. Explain revision/phase/review aliases from actual records; preserve them, never infer authority from the highest number. Report unresolved contradictions without editing or silently resolving them.
5. No application edits, new plan folders, approval changes, staging, commits or dependency installs. If the user asks to continue after seeing status, route that separate request to `resume-task` or `workflow`.

Read the active workflow/global artifact policy when assessing output. Treat unknown files as unknown, not disposable. Mention relevant retained evidence, active consumers or outstanding scratch cleanup in chat; do not run tests, generate screenshots, save another status report or delete artifacts merely to report status.

Report missing or stale applicable rules as a blocker to the next affected action, without demanding setup merely to give read-only status. A continued task goes through the workflow rules-readiness gate; an old approval does not silently waive new rule gaps.

For UI work, report the recorded mode/reference, behaviour verification, design acceptance, preview/release boundary and missing evidence separately. Do not mark design-pending work release-ready because code/tests are complete. Unknown UI authority blocks the next affected change, not this read-only status response; do not create another UI report.
