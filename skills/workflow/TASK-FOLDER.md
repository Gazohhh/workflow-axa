# Task records and recovery

## Resolve identity before creating records

A task follows the user's goal, not the conversation, date or `/workflow` invocation. Start with a brief read-only lookup in the established task location and any named/current record. Inspect goal, latest checkpoint, outcome, ownership and decisions for plausible candidates; filenames and recency alone are not enough. A related scope extension is not automatically a separate task.

| Situation | Action before writes |
|---|---|
| User names a record or clearly continues the current task | Read and reuse it after checking current files, scope and ownership. Do not ask the same identity question again. |
| A likely related task is found but intent is unclear | Ask whether to extend it or create separate work; explain the connection and recommend an option. Do not create a provisional duplicate folder while waiting. |
| Several plausible tasks | Show their goals/status briefly and ask which applies. Do not choose the newest. |
| Clear extension of the same active task | Keep its folder, add the new requirement as a proposed revision, and reopen only affected decisions/approval. |
| Related task is complete | An explicit correction/reopening can reuse it, preserving the completed outcome. Otherwise clarify reopening versus a linked follow-up before creating either. |
| No relevant record after checking, or user explicitly requests separate work | Create at the repository's established location, otherwise `docs/plans/YYYY-MM-DD-<slug>/`. Link a relevant earlier task when useful. |
| Record location unavailable or ownership contested | Explain the limitation and ask; do not equate an unreadable location with no match. |

Example: “I found the graphics-settings plan. Is this another requirement for that work, or a separate task? I recommend extending it because it changes the same settings flow.” Do not ask the user to search folders the agent can inspect.

Identity is not authority: a match does not approve new behavior or allow taking another person's edits. A stale timestamp or in-progress checkbox does not establish a handoff. Resolve unclear ownership before writing the record or shared files. Read related tasks without mutating them unless assigned.

Once resolved, report the reused/new path and reason; create or update a small checkpoint **before substantial discovery or a lengthy interview**. Save unknown scope honestly. The folder then remains stable through sessions and approved revisions. A conflicting explicitly requested destination needs clarification, not silent relocation.

## Scale the record

| File | Authoritative content |
|---|---|
| `PLAN.md` | Current checkpoint, goal, approach, scope, acceptance, approval, outcome. |
| `TODO.md` | Actionable work items, dependencies, state, and completion evidence. |
| `FINDINGS.md` | Evidence, investigative history, failed approaches, verification and blockers. |
| `DECISIONS.md` | Material choices, their reasons, and proposed/approved/superseded status. Create on the first such choice. |

For a genuinely lightweight edit, use only `PLAN.md` with short Work and Evidence sections instead of three mostly empty files. Promote to the normal layout when the work expands; move the authoritative sections and leave pointers, not competing copies. Do not grow a permanent `HANDOFF.md` duplicating the checkpoint.

For an existing task, read its established record layout, including legacy `STATUS.md` or inline decisions; do not create missing template files merely for conformity. New-task defaults below are not a migration requirement.

Records are reviewable project documentation; creating them does not authorize committing them. Preserve meaningful history. Keep the current checkpoint concise, append corrections to findings, and mark superseded choices rather than making old decisions look current. Link existing architecture decisions/glossaries; update their authoritative location within approved scope rather than copying them into every task.

## PLAN.md starting structure

Omit irrelevant fields for lightweight work; use `unknown` or `not applicable` rather than fabricating values.

```markdown
# <Task>

## Current checkpoint
- Updated / phase: <known date/time; investigating, awaiting approval, implementing, verifying, blocked, paused or closed>
- Approval: <approved/waived/not approved/unknown; exact revision, scope and record>
- Implementation: <not started/in progress/implemented/partial/unknown; task references>
- Verification / owner acceptance: <not run/in progress/blocked/passed/limited/unknown; evidence and outstanding acceptance>
- Selected review: <exact plan revision, report/source path, or actual waiver; a snapshot, not live status>
- Active tasks / blockers: <TODO IDs, unanswered decisions or interrupted work>
- Last result / next safe action: <short observed result and specific next step with prerequisites>
- History: <revision-log section in the established record; omit before needed>

## Working context
<Keep stable setup details here, not repeatedly inside the progress summary.>
- Owner and ownership: <session/person; active, handed-off or released>
- Repository / branch / worktree: <actual locations>
- Task identity: <reused/new; related record and reason or user answer>
- Decision check: <FINDINGS reference, confirmed answer sources and unresolved Q-IDs>
- Current understanding / evidence: <R/E/A mapping, inspected state and limits>
- Specialists: <shared capability record; selected routes and approved exceptions>
- Test output, when needed: <existing parent, owner, retained proof, active consumers and cleanup condition>

## Goal and acceptance
<Observable outcome, constraints, and how it will be checked.>

## Baseline before this change
<What the inspected sources established at the stated time; not a claim about today's implementation.>

## Approach and scope
<Chosen/proposed approach; bounded areas; protected areas; cleanup;
required existing doc updates; verification strategy.>

## Approval
<Revision, visual report reference or explicit exemption/waiver, approving user response and date, selected decision options,
included work, exclusions, and what requires renewed approval.>

## Outcome
<Pending, verified result, or partial result and limitations.>
```

For a multi-step plan, retain earlier approval records and describe later changes as a delta. PLAN's checkpoint owns the concise current summary; TODO owns item states; FINDINGS owns detailed evidence; decisions own the reasons. Do not repeat live completion totals across them. Where a legacy task already uses STATUS.md for the checkpoint, preserve that single owner and link it. A checked item is not necessarily accepted: report approval, implementation and verification/owner acceptance separately. Execution order, status updates, or correction of a path inside the same approved area need not reopen approval. Changed intent, risk, protected scope, or a reserved decision does. Label an unapproved revision proposed; it does not replace the last approved authority.

## TODO and evidence

Before touching shared files, capture initial status and enough local diff/index evidence to distinguish existing edits from this task. Keep sensitive diffs in an approved private location rather than copying them into committed records.

Use stable requirement (R), evidence (E), acceptance (A) and task (T) IDs; every implementation task supports a user requirement or an evidenced prerequisite. Use work units that another agent could complete. Name affected areas, dependencies, verification, and ownership when parallel work exists. Include documentation, tests, integration, and replacement cleanup rather than treating them as optional finishing work.

```markdown
- [ ] T1 — <work>; supports: R1; evidence: E1; acceptance: A1; depends on: none; verify: <check>.
- [~] T2 — <work>; owner/lane: <identifier>; next: <step>.
- [x] T3 — <work>; evidence: FINDINGS.md V2, <observed result>.
```

Keep each TODO short: action, state/blocker, dependencies and evidence pointer. Put attempt histories and test details in the existing FINDINGS or evidence section, not a growing paragraph on the checkbox. Distinguish `verified`, `implemented — verification pending`, `removed by owner`, `superseded` and `not applicable`; removal or supersession is not a passed test. Preserve legacy checkbox notation and state the outcome explicitly.

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

1. Read the current checkpoint and linked TODO/findings/decisions, applicable project instructions, and recorded approval. Support legacy STATUS.md and inline decisions. Treat earlier baselines/proposals/reviews as historical unless current evidence says otherwise; do not choose the newest paragraph, filename or checkbox as authority. Do not require the previous conversation.
2. Confirm repository, branch/worktree, and task ownership. A user saying "continue this task" can authorize takeover; record it and establish that overlapping writes are stopped or isolated. Resolve uncertain concurrent ownership before writing.
3. Recheck specialist availability in this host and compare any saved installation fingerprint. An old session's availability is not proof for a new account. Reuse task approval; resolve only changed capability/compatibility.
4. Inspect current staged/unstaged/untracked files and the previously active unit. Preserve unrelated work. Determine what completed, what is partial, and which checks no longer apply.
5. Reconcile approval, implementation, verification and any owner acceptance separately. Resolve contradictions by inspecting their sources; mark unresolved state unknown and ask when it blocks authority or correctness. Reconcile the inspected-code evidence, understood outcome and visual review revision with current files. Classify expected approved progress versus material changes; do not treat a new report or source hash as approval. An awaiting-approval task stays paused for implementation.
6. Reuse the applicable decision check. Run grilling only for new substantive intent, changed material branches or requested further challenge; do not restart an unchanged approved interview.
7. Update the checkpoint and continue the next covered step. Ask only for missing authority, a genuine decision blocker, or an unresolved ownership conflict—not for routine reapproval.

Across accounts on the same worktree, records and edits may already be present. Across machines or cloud environments, documentation alone is not the code: transfer the actual working changes through an explicitly authorized method. Do not silently create commits, push a branch, upload logs, or assume a remote contains uncommitted work. Use separate worktrees for overlapping tasks where available, with coordinated integration and no global index manipulation.

## Evidence privacy

Never copy credentials, access tokens, raw personal data, or unrelated production records into task documents, prompts, screenshots, or committed fixtures. Redact before saving. Store only what supports a finding. Large/private raw artifacts stay outside tracked content in an approved location, with a sanitized reference. Ignore rules reduce accidental tracking; they do not make a file secret or authorize an upload.

## Visual artifacts

For substantive implementation follow [VISUAL-REVIEW.md](VISUAL-REVIEW.md). Keep revisioned report input and HTML at the project's review-page location, otherwise use `reviews/` inside a new task folder. Reuse existing root-level or other review paths for established tasks. Link the selected review from the current checkpoint. This durable approval record is separate from ignored test scratch. They project the authoritative records; do not maintain another task list inside an independent design. Preserve the report shown for each approval and mark later material proposals separately. No unrequested HANDOFF file or remote whiteboard is needed.

## Test output is not another task record

Read [ARTIFACTS.md](ARTIFACTS.md) before generating output. Reuse the already recorded output parent; default only when absent to the project's convention or `.artifacts/<full-existing-task-folder-name>/` in this worktree. Create only needed children. Do not create new top-level folders for phases, retries or dates. Tool-owned output paths remain unchanged.

Record retained proof and the current scratch/consumer state in the existing checkpoint/findings. No new per-run manifests, cleanup logs, backups or HANDOFF documents. On resume, reconcile ownership and active consumers before reusing or removing output; an interrupted run is not automatically disposable. A read-only status/doctor/review can return findings in chat without saving anything.

## Revisions are changed agreements, not attempts

| Event | Record action |
|---|---|
| Material change to requested behavior, chosen approach, risk or protected scope | New proposed plan revision; show the delta and resolve required approval. Retain the last valid authority for independent unchanged work. |
| Task progress, blocker, corrected progress summary, rerun or account/agent switch | Update the existing checkpoint/item/evidence. No new plan revision, folder or review merely for this event. |
| Unpresented draft correction | Reuse that draft when ownership and tool protections allow. Never bypass the renderer's no-overwrite guard. |
| New visual presentation of unchanged agreed scope, explicitly requested | Distinguish presentation identity from the unchanged plan revision; no new application approval implied. |
| Revoking/superseding an agreement | Preserve its scope and reason; point to the replacing decision and affected portions. A newer proposal does not itself revoke approval. |

For new tasks prefer R1, R2, R3; keep phase names separate. Existing C3, P1-r1, review-r5 and similar identifiers remain exact. Do not renumber or infer a mapping from filenames. Record known aliases explicitly; leave unestablished relationships unknown.

Keep one compact revision log in existing DECISIONS, or PLAN for a smaller task:

| Plan revision | Review/phase alias | Change | Why | Authority/outcome and source |
|---|---|---|---|---|
| R2 | review-r2.html | Earlier agreed approach | Recorded reason | Approved then superseded by D4; original review retained |
| R3 | review-r3.html | Correct only the affected behavior | Observed failure V7 | D4 approval; implementation complete; device acceptance pending V8 |

The example is illustrative, not an approval. Record the actual changed agreement, constraints, reason, authority and links; a hash is not preserved content. Do not copy the complete PLAN/TODO/FINDINGS/DECISIONS set per revision or create CURRENT/REVISION/HANDOFF duplicates. The log may be absent until a meaningful revision occurs. Preserve old approval text and enough old scope to understand what was approved; later progress need not be an append-only diary.

## Forward-only adoption

Apply the clearer structure to new tasks. On an authorised resume, update only the current summary, directly contradictory current wording and necessary links within that task. Mark old descriptions as historical instead of silently rewriting their meaning. Keep existing paths, IDs, headings/anchors, review filenames and valid approvals; add a historical note below an old heading when renaming would break links. If inspection cannot resolve a contradiction, report it rather than inventing a reconciliation. Read-only status/review requests make no edits.

Do not bulk rewrite closed tasks, generate missing template files, migrate old JSON, renumber ADRs, move maintained guides from dated folders, or reconstruct missing historic reviews. Mark an unavailable original review and cite the remaining actual approval/decision record; its absence does not prove either approval or nonapproval. Escalate only the authority that cannot be established.

Presented/approved HTML and JSON are immutable snapshots by default; an old `awaiting-approval` badge can correctly describe the moment shown. Later approval lives in the task record, not a rewritten snapshot. Project policies that require asking about retention remain in force until their conflict with this new default is explicitly resolved during setup. No automatic deletion.

## Architecture decisions

Keep task progress in task records. An ADR preserves an important decision, its context and consequences. For a material reversal, create a linked superseding ADR within authorised scope, stating whether it replaces all or only part of the earlier decision. Preserve earlier reasoning; labelled factual corrections/clarifications are not silent reversals. Proposed ADRs are not accepted just because a date passed. Keep established reference/runbook paths; link rather than copy them into each task.

## Rules checkpoint (forward-only)

Before creating records use RULES.md. Once an existing or authorised task record is selected, keep one short readiness/source/scope note in its current checkpoint; a known exception includes the actual response, omissions, allowed work and expiry. No extra RULES-STATUS.md or new task per check. Legacy tasks need no setup marker. Reconcile affected inputs on resume; do not replay valid consent or promote historical exceptions to blanket authority.

## UI context, only when relevant

In the established current checkpoint add one compact UI entry: affected area and mode; approving source/reference revision; allowed components/variants/patterns; preview destination/access; exact exceptions; functionality checks; design acceptance and release state. No UI manifest or new folder by default. Design-pending functionality may be implemented/tested without being a finished interface. An approved-kit directory appearing later, task handoff or test retry does not silently approve design or create a new revision. Reconcile old tasks forward at the next affected unit; do not rewrite historical reviews. Refer to the installed local ui-design contract for details.
