---
name: resume-task
description: "Resume an existing task across sessions. Reconcile records, files, approval and specialist availability before continuing."
---

# Resume task

Continue existing work; do not reconstruct progress from memory.

1. Apply the installed workflow RULES.md readiness gate before continuation, even if rule-maker never ran. Revalidate limited exceptions and changed inputs. Read project rules and the supplied/named task records. If the task identity is ambiguous, ask before writing.
2. Confirm repository, worktree and ownership: "continue this task" from the user authorizes a takeover; record it and make sure nobody else is still writing. On another machine the records are not the code; move working changes only by an approved method. Read the existing workflow task-record rules. Support PLAN/TODO/FINDINGS/DECISIONS, legacy STATUS.md and inline decisions without demanding missing templates. Reconcile current branch/worktree, uncommitted changes, relevant files, verification evidence and specialist availability. Treat interrupted work as uncertain until inspected.
3. Separate agreement, implementation approval, implementation and verification/owner acceptance; an approved plan is not a completed task. A legacy single plan approval counts as both for its recorded scope. Resolve conflicting current/historical statements from evidence, not timestamps or revision numbers. Old reports are history: never edit or offer to edit an old report. Restate in plain language what the task is, what is already approved, what appears complete, what changed since the checkpoint, unresolved decisions and the next safe action.
4. Reuse valid answers, agreement and approval for the same presented revision. Follow workflow/VISUAL-REVIEW.md "Legacy approval recovery" for older formats; reconcile evidence rather than fabricate authority or bypass the hook. Do not restart grilling or either gate merely because the agent/session changed. Never rewrite the original `- Approval:` quote. An earlier session's small change needs a new yes (workflow/VISUAL-REVIEW.md "Small change"). If scope materially changed or authority evidence is invalid/stale, reopen only the affected part: behavior through `workflow-clarify`, tickets through `workflow-specify`. A task awaiting either gate stays paused.
5. If the next unit is already approved, continue with the phase skill `workflow` routes to (normally `workflow-execute`, or `workflow-deliver` once tickets are done): checkpoint it, execute, verify and update the existing task records. Update only this resumed task as needed; preserve paths, IDs, anchors, earlier outcomes and presented reports. No new plan revision for a rerun, progress update or handoff; no bulk migration or duplicate handoff system.
6. Git and publishing follow workflow SKILL.md "Always"; never discard changes unless explicitly authorized.

Before producing output, follow ARTIFACTS.md/global policy; reconcile output ownership, consumers, retained proof and interrupted scratch. Reuse that parent; a new agent is not a new artifact root. Clean only verified owned disposable output under existing authority, never unknown files from the interrupted session.

For resumed application UI, reload shared DESIGN.md and local ui-design. Reconcile mode, authority, kit revision, preview, exceptions and pending design acceptance before affected work. Preserve valid decisions; do not infer new styling permission from an old generic plan approval or a newly discovered kit. Legacy tasks gain only the necessary forward-looking checkpoint, not a bulk redesign.
