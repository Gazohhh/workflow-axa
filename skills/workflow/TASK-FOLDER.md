# Task records and recovery

## Claim and scale

Use the repository's established task-record location, otherwise `docs/plans/YYYY-MM-DD-<slug>/` with the current date. Inspect candidate records before writing. Continue only an exact goal/scope match that is unowned, handed off, or explicitly assigned by the user. A stale timestamp or in-progress checkbox does not prove that another owner stopped. When ownership is ambiguous, ask before changing that task or its files.

Create a small record before substantial discovery; it can honestly say that scope or answers are unknown. Do not finish a long interview and only then save its conclusions. Report the task path once established.

| File | Authoritative content |
|---|---|
| `PLAN.md` | Current checkpoint, goal, approach, scope, acceptance, approval, outcome. |
| `TODO.md` | Actionable work items, dependencies, state, and completion evidence. |
| `FINDINGS.md` | Evidence, investigative history, failed approaches, verification and blockers. |
| `DECISIONS.md` | Material choices, their reasons, and proposed/approved/superseded status. Create on the first such choice. |

For a genuinely lightweight edit, use only `PLAN.md` with short Work and Evidence sections instead of three mostly empty files. Promote to the normal layout when the work expands; move the authoritative sections and leave pointers, not competing copies. Do not grow a permanent `HANDOFF.md` duplicating the checkpoint.

Records are reviewable project documentation; creating them does not authorize committing them. Preserve meaningful history. Keep the current checkpoint concise, append corrections to findings, and mark superseded choices rather than making old decisions look current. Link existing architecture decisions/glossaries; update their authoritative location within approved scope rather than copying them into every task.

## PLAN.md starting structure

Omit irrelevant fields for lightweight work; use `unknown` or `not applicable` rather than fabricating values.

```markdown
# <Task>

## Current checkpoint
- Status: investigating | awaiting-approval | implementing | verifying | blocked | paused | done
- Owner: <session/person identifier>; ownership: active | handed-off | released
- Updated: <date/time with timezone when known>
- Repository / branch / worktree: <actual locations>
- Approved revision and scope: <revision or not approved>
- Active tasks: <TODO IDs, or the lightweight work item>
- Specialists: <capability evidence / selected routes / approved adapters or exceptions>
- Last completed step and observed evidence: <reference>
- Next safe action: <specific step and prerequisites>
- Blocked decisions / interrupted work: <IDs and affected work>

## Goal and acceptance
<Observable outcome, constraints, and how it will be checked.>

## Approach and scope
<Chosen/proposed approach; bounded areas; protected areas; cleanup;
required existing doc updates; verification strategy.>

## Approval
<Revision, approving user response and date, selected decision options,
included work, exclusions, and what requires renewed approval.>

## Outcome
<Pending, verified result, or partial result and limitations.>
```

For a multi-step plan, retain earlier approval records and describe later changes as a delta. Execution order, status updates, or correction of a path inside the same approved area need not reopen approval. Changed intent, risk, protected scope, or a reserved decision does. Label an unapproved revision proposed; it does not replace the last approved authority.

## TODO and evidence

Before touching shared files, capture initial status and enough local diff/index evidence to distinguish existing edits from this task. Keep sensitive diffs in an approved private location rather than copying them into committed records.

Use stable IDs and work units that another agent could complete. Name affected areas, dependencies, verification, and ownership when parallel work exists. Include documentation, tests, integration, and replacement cleanup rather than treating them as optional finishing work.

```markdown
- [ ] T1 — <work>; depends on: none; verify: <check>.
- [~] T2 — <work>; owner/lane: <identifier>; next: <step>.
- [x] T3 — <work>; evidence: FINDINGS.md V2, <observed result>.
```

Mark blocked work with a reason and decision ID, not a misleading completion mark. A waived requirement records the explicit user decision; it is not a passed test. Reopen an item when later changes invalidate its evidence. An agent's completion message is a claim until the owner inspects its artifacts/results.

Give verification entries IDs such as V1. Record the exact command, working directory, relevant environment/version, result/exit status, checked state, and coverage limits. Identify the state by a commit plus local diff or another practical snapshot reference; a commit alone is insufficient with uncommitted edits. Prefer concise results over copied logs. Mark missing coverage `UNTESTED — <scope and reason>`. Files and lines can support an inspection, but are not proof that a runtime test passed.

Keep questions and discoveries in findings; reserve decision records for meaningful choices. Each decision records options, recommendation, approved answer or pending status, and what depends on it. Ordinary variable names do not need decision entries.

## Specialist evidence

Follow [SPECIALISTS.md](SPECIALISTS.md). Record host/version, resolved qualified identifier,
source/path/fingerprint, availability evidence, invocation/load evidence, output reference,
and approved adapters/exceptions. `ON DISK`, `AVAILABLE IN HOST`, `USED`, and `RESULT
VERIFIED` are distinct claims. A checker report supports only the first and change
comparison. Store a shared approved inventory once and link it; do not duplicate skill
bodies or absolute private user paths across team docs. Sanitize paths when sharing.

An installed skill that has not been invoked is not a completed workflow step. A missing
specialist does not authorize an improvised replacement. Keep a blocked entry until setup
or a documented fallback is approved. No dependency download/upgrade at every task start.

## Checkpoint timing

Before each bounded discovery or implementation unit, save its purpose, active task, expected affected area, and next verification. After it, save findings, actual modifications, result, and next action. Persist a newly blocking decision when it is discovered. This before/after pattern is the recovery mechanism; a graceful end-of-session summary is only an additional convenience.

Only the task owner updates these records. Subagents return findings and evidence. Assign non-overlapping write ownership, join dependent work explicitly, and inspect integrated results. Do not claim simultaneous work is isolated merely because lane names differ; shared files, generated artifacts, and Git index operations can still overlap.

## Resume safely

1. Read the checkpoint and linked TODO/findings/decisions, applicable project instructions, and recorded approval. Do not require the previous conversation.
2. Confirm repository, branch/worktree, and task ownership. A user saying "continue this task" can authorize takeover; record it and establish that overlapping writes are stopped or isolated. Resolve uncertain concurrent ownership before writing.
3. Recheck specialist availability in this host and compare any saved installation fingerprint. An old session's availability is not proof for a new account. Reuse task approval; resolve only changed capability/compatibility.
4. Inspect current staged/unstaged/untracked files and the previously active unit. Preserve unrelated work. Determine what completed, what is partial, and which checks no longer apply.
5. Update the checkpoint and continue the next covered step. Ask only for missing authority, a genuine decision blocker, or an unresolved ownership conflict—not for routine reapproval.

Across accounts on the same worktree, records and edits may already be present. Across machines or cloud environments, documentation alone is not the code: transfer the actual working changes through an explicitly authorized method. Do not silently create commits, push a branch, upload logs, or assume a remote contains uncommitted work. Use separate worktrees for overlapping tasks where available, with coordinated integration and no global index manipulation.

## Evidence privacy

Never copy credentials, access tokens, raw personal data, or unrelated production records into task documents, prompts, screenshots, or committed fixtures. Redact before saving. Store only what supports a finding. Large/private raw artifacts stay outside tracked content in an approved location, with a sanitized reference. Ignore rules reduce accidental tracking; they do not make a file secret or authorize an upload.
