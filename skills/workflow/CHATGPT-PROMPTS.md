# Optional prompt preparation

A prompt prepared in another assistant does not replace investigation, approval, or the task record. Use the invocation supported by the installation: Claude Code plugin `/workflow-axa:workflow`, standalone Claude skill `/workflow`, or Codex `$workflow`.

## Start a task

```text
/workflow-axa:workflow Investigate <problem> in <repository/area>. Goal: <observable outcome>. Constraints/protected areas: <limits>. Read the existing code and project rules first; find and reuse a related existing task before creating records; ask when identity is unclear. Establish the record before substantial discovery. Map callers, alternatives, cleanup, tests, and affected docs. Verify and invoke the relevant installed specialists using SPECIALISTS.md. Use grilling to uncover missing decisions even in a detailed request; reuse sourced answers. Batch nonblocking decisions; ask early only where a decision blocks useful progress. Map my requirements to existing-code evidence and the actual gap, then prepare PLAN/TODO and open the current/proposed HTML review. Stop for approval before application implementation.
```

Replace placeholders with known information, not assumptions. Do not invent a solution merely to make the prompt look prepared. Include a reproduction and expected behavior when known. For research-only work, explicitly say that no implementation is authorized.

## Approve and execute

```text
/workflow-axa:workflow Continue <task-folder>. Approve the presented visual review and plan R2, and the recommendations for Q1 and Q2. Implement the agreed scope, including its tests, docs, direct replacement cleanup and task-caused fixes. Keep checkpoints current. Ask again only for new reserved decisions or scope changes. Do not stage, commit, push or deploy.
```

Use the actual revision and question IDs; "finish without check-ins" does not authorize new behavior, architecture decisions, or dependencies outside the approval.

## Resume after an interruption

```text
/workflow-axa:workflow Continue <task-folder> in <repository>. The previous session is stopped; take ownership. Read the records and existing approval, reconcile them with the actual worktree and interrupted step, then continue the next approved action. Preserve unrelated edits and staging. Recheck specialist availability in this host and update the checkpoint before coding.
```

Only say the other session stopped when true. Transfer the working changes as well as the records when moving to another environment.

## Audit without changing code

```text
/workflow-axa:workflow Audit the task-attributable changes for <task-folder> against its approval and AUDIT.md. Include relevant untracked files, alternative callers, replacement leftovers, verification freshness and existing docs. Record findings; do not implement fixes or change Git staging.
```

To prohibit all file writes, explicitly say "read-only; report in the conversation only." For a requested reader PDF, provide the audience/purpose/language and point to any approved glossary; use the same workflow, not a separate PDF workflow skill.


## Ordinary requests after project routing is configured

```text
Fix negative-score handling in both display paths. Keep current output for valid scores and add no dependencies.
```

This must load workflow, inspect the actual code, and present a visual review before substantive implementation. Do not rely on implicit invocation until the setup smoke test passes.

## Visualization only

```text
/workflow-axa:codebase-map current Show the score-display flow and both callers. No application edits.
/workflow-axa:codebase-map proposed Visualize the design in <task-folder>; mark it as a draft if choices remain open.
/workflow-axa:codebase-map compare <task-folder> Show current versus the selected plan revision for approval.
```

Standalone Claude uses `/codebase-map`; Codex uses `$codebase-map`. The mode words are instructions interpreted by the skill, not separate executable CLIs. A map request is not permission to implement or refactor.


## Continue without knowing the folder path

```text
/workflow-axa:workflow Continue the graphics-settings work. Find its existing task records, check the current files, and tell me which task you are resuming. Ask only when the match or ownership is unclear.
```

You do not need to include all these reminders every time; the workflow itself carries the rules. A prepared prompt can settle decisions, but cannot disable the required proactive check just by being long.
