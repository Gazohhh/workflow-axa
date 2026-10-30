---
name: resume-task
description: "Safely continue an existing workflow task after a session, account or agent switch. Reconcile records, code, approval and specialist availability before taking the next approved action."
---

# Resume task

Continue an existing workflow task safely; do not reconstruct progress from conversation memory.

1. Apply the installed workflow RULES.md readiness gate before continuation, even if rule-maker never ran. Revalidate scoped exceptions and changed inputs; setup permission is not application approval. Read project rules and the supplied/named task records. If the task identity is ambiguous, ask before writing.
2. Read the existing workflow task-record rules. Support PLAN/TODO/FINDINGS/DECISIONS, legacy STATUS.md and inline decisions without demanding missing templates. Reconcile current branch/worktree, uncommitted changes, relevant files, verification evidence and specialist availability. Treat interrupted work as uncertain until inspected.
3. Separate approval, implementation and verification/owner acceptance; an approved plan is not a completed task. Resolve conflicting current/historical statements from evidence, not timestamps or revision numbers. Restate in plain language what the task is, what is already approved, what appears complete, what changed since the checkpoint, unresolved decisions and the next safe action.
4. Reuse valid answers and approval for the same presented revision. Do not restart grilling or visual approval merely because the agent/session changed. If scope materially changed or approval evidence is invalid/stale, return to `workflow` for the necessary questioning/review gate.
5. If the next unit is already approved, checkpoint it before work, execute it using the applicable workflow specialists, verify it, and update the existing task records. Update only this resumed task as needed; preserve paths, IDs, anchors, earlier outcomes and presented reviews. No new plan revision for a rerun, progress update or handoff; no bulk migration or duplicate handoff system.
6. Do not stage, commit, push, deploy, reset or discard unless explicitly authorized.

Before output-producing work, read the active workflow ARTIFACTS.md/global policy and reconcile the recorded output parent, pending consumers, retained proof and interrupted scratch. Reuse that parent; a new agent is not a new artifact root. Clean only verified owned disposable output under existing authority, never unknown files from the interrupted session.

For resumed application UI, reload shared design.md and local ui-design. Reconcile mode, authority, approved reference/kit revision, preview isolation, exceptions and pending design acceptance before the next affected unit. Preserve valid decisions; do not infer new styling permission from an old generic plan approval or a newly discovered kit. Legacy tasks gain only the necessary forward-looking checkpoint, not a bulk redesign.
