# Task records

Where a task's records live, what goes in each file, and how to pick a task up again. The records (PLAN, TODO, FINDINGS, DECISIONS) are the source of truth; reports and chat are projections of them.

## Find the task before creating one

A task follows the user's goal, not the chat, date or `/workflow` call. A related scope extension is not automatically a separate task. Search the established task location and any named record first; read the goal, checkpoint and outcome, not just filenames.

| Situation | Do this before writing |
|---|---|
| User names a record or clearly continues the current task | Reuse it after checking files, scope and ownership. Don't ask again. |
| A related task exists but intent is unclear | Ask: extend it or start separate work? Explain the link, recommend one. Save that question round in a new folder named for your recommendation, its checkpoint `identity pending (vs <related task>)`; if the user picks the existing task, move the saved round there and remove the new folder. |
| Several plausible tasks | Show their goals and status; ask. Don't pick the newest. |
| Clear extension of the active task | Keep the folder; add the requirement as a proposed revision; reopen only what it affects. |
| Related task is complete | Unless the user said which, `workflow-clarify` asks "new revision of it or separate task?" with its first questions. |
| The task's checkpoint names another worktree than the current one | Stop and ask which worktree is meant; write nothing here. |
| No relevant record, or user asks for separate work | Create the project's established location, else `docs/plans/YYYY-MM-DD-<slug>/`. |
| Location unreadable or ownership contested | Say so and ask. Unreadable is not "no match". |

A match is not permission: it doesn't approve new behavior or let you take over someone else's edits. A stale timestamp is not a handoff. Report the path you chose and why, then save a checkpoint **before** long discovery or an interview.

## What goes where

| File | Holds |
|---|---|
| `PLAN.md` | Checkpoint, goal, scope, agreement, approval, outcome |
| `TODO.md` | Tickets: dependencies, state, evidence pointer |
| `FINDINGS.md` | Evidence (E), journeys (J), questions (Q), check results (V), blockers, failed attempts |
| `DECISIONS.md` | Material choices with reason, status and who made them (`by: user` or `by: agent`); created on the first one |

A lightweight edit uses only PLAN with short Work and Evidence sections; if it grows, move those sections into the normal files and leave pointers in PLAN. Existing tasks keep their layout (including legacy `STATUS.md`); don't add missing template files for conformity. Records are project docs, not permission to commit them. No `HANDOFF.md` or other duplicate of the checkpoint.

## PLAN.md

Leave out what doesn't apply; write `unknown` rather than inventing.

```markdown
# <Task>

## Current checkpoint
- Updated / phase: <date; investigating, awaiting agreement, specifying, awaiting approval, implementing, verifying, blocked, closed>
- Agreement (gate one): <agreed/waived/legacy/not required — lightweight/pending; revision and record>
- Approval (gate two): <approved/waived/legacy/not approved; revision, report and record>
- Implementation: <not started/in progress/implemented/partial>
- Verification / owner acceptance: <not run/passed/limited/blocked; evidence and what is outstanding>
- Blockers: <ticket IDs, open questions, interrupted work>
- Next safe action: <last result and the specific next step>

## Working context
- Owner (a name, never an email address); repository / branch / worktree; task identity and why
- Decision check (FINDINGS ref); specialists; test output folder and cleanup condition

## Goal and acceptance
## Baseline before this change
## Approach and scope
## Agreement
<Gate one: behavior, journeys, scope, exclusions, acceptance, assumptions; the user's answer and date.>
## Approval
<Gate two: revision, report, the user's answer and date, included tickets, exclusions, what needs re-approval.>
## Outcome
```

`Approval` means implementation authority; `Agreement` never does (gates: [VISUAL-REVIEW.md](VISUAL-REVIEW.md)). The checkpoint holds the current summary, TODO the item states, FINDINGS the detail, DECISIONS the reasons; don't repeat totals across them. Mark an unapproved revision "proposed"; it doesn't replace the last approved one.

## TODO and evidence

Before touching shared files, record `git status` and enough diff to tell existing edits from yours.

IDs: requirement R, evidence E, acceptance A, ticket T, journey J, question Q, check result V. Every ticket supports a requirement or a demonstrated prerequisite and is small enough for another agent to finish.

```markdown
- [ ] T1 — <work>; supports R1, A1; depends on: none; verify: <check>.
- [x] T2 — <work>; verified: FINDINGS V2.
```

`workflow-specify` adds scope, test seam and TDD choice per ticket (a table is fine). Ticket states: not started, ready, in progress, implemented — verification pending, review findings open, verified, blocked, superseded, removed, not applicable. **Terminal** states are verified, blocked, superseded, removed and not applicable; the last three need the decision that caused them, never test evidence. A checked box needs a V-ID; without one it counts as unverified. Removed, superseded or waived is never a passed test.

A V entry records the command, folder, versions, result, which state of the files it ran on (commit plus local diff), and what it didn't cover (`UNTESTED — <scope and reason>`). Reading a file is not a passed test. An agent saying "done" is a claim until you check its results.

Specialist use: record the resolved skill, where it came from and whether it was actually invoked ([SPECIALISTS.md](SPECIALISTS.md)). Installed is not used; a missing specialist doesn't authorize a homemade replacement.

## Checkpoint as you go

Before each unit of work, save what it is, the files it will touch and its check. After it, save what changed, the result and the next step. This is the recovery mechanism; an end-of-session summary is only a bonus. Use `scripts/record.py` (new, append, replace-section, set-line, tick with evidence, batch for several exact edits) instead of ad-hoc edit scripts or `node -e`/`sed` replaces that fail silently; it keeps each file's line endings. Write any script or JSON with the file-write tool, never a shell heredoc: heredocs mangle backslashes. At session start, read `scripts/open_items.py --task <folder>` instead of every record file; it also flags broken encoding and mixed line endings. Test output goes to `.artifacts/<task-folder>/` even when that folder is not git-ignored (say so in the plan; never change `.gitignore` or use a session scratchpad). A script or file that a recorded check names is evidence: keep it until the owner accepts. Only the task owner writes records; subagents return evidence. Parallel workers need non-overlapping files.

## Resume

Run `resume-task`; it owns the procedure. These records are what it reads.

## Revisions

| Event | Record |
|---|---|
| Material change to behavior, approach, risk or protected scope | New proposed revision showing the delta; reopen gate one, then gate two, for the affected parts only |
| Progress, blocker, rerun, account or agent switch | Update the checkpoint and items. No new plan revision, folder or report |
| Correction to an unpresented draft | Reuse the draft; never bypass the renderer's no-overwrite guard |
| Superseding an agreement | Keep its scope and reason; point to what replaced which part |

An earlier revision that skipped a step is not a precedent: each new revision follows the current rules. Keep existing IDs (C3, P1-r1, review-r5) exactly and phase names separate from revision IDs; don't renumber. Keep one short revision log (in DECISIONS, or PLAN for small tasks): revision, report, change, why, outcome.

## Forward-only adoption

New structure applies forward. On a resumed old task, update only the checkpoint, directly contradictory current wording and needed links; mark old text historical instead of rewriting its meaning. Do not bulk rewrite closed tasks, migrate old JSON, renumber IDs or reconstruct missing reviews. If an original review is missing, record that and use the remaining approval and decision records; its absence proves neither approval nor refusal. Escalate only authority you can't establish. Presented and approved HTML/JSON files are immutable snapshots.

## Also record

- **Rules**: one readiness note in the checkpoint (RULES.md); an exception records the user's words, scope and expiry. No separate status file.
- **UI**: one checkpoint entry: area and mode, approving source, allowed components, preview, exceptions, design acceptance and release state (ui-design).
- **Test output**: follow [ARTIFACTS.md](ARTIFACTS.md); reuse the recorded output folder (default `.artifacts/<task-folder-name>/`); record retained proof and the cleanup condition in the checkpoint. No manifests or cleanup logs.
- **Privacy**: never copy credentials, tokens, personal data or production records into records, prompts or screenshots. Redact first.
- **ADRs**: offer one only when `domain-modeling`'s criteria hold; a reversal is a new superseding ADR. Proposed ADRs are not accepted because time passed. Task progress stays in task records.
