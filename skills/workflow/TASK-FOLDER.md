# Task records

Write every record for a person, as `WRITING.md` says.

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
| A fresh worktree has no installed dependencies (no `node_modules`, `vendor`) | Never install on your own. When dependencies are missing, read [WORKTREE-DEPENDENCIES.md](WORKTREE-DEPENDENCIES.md) before you ask. |
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

Leave out what doesn't apply; write `unknown` rather than inventing. `workflow/SKILL.md` §3 owns the recipe pick. Store each classification question and answer in FINDINGS (PLAN for lightweight work), linked from the Recipe line, and record the question before sending it so a resume can't reset its allowance; with no task folder yet, record both once the folder exists. Keep earlier references when the pick changes. Inspect and status-only requests write no records; an *Only investigate* answer to a recorded question is recorded as its answer, and nothing else.

```markdown
# <Task>

## Current checkpoint
- Updated / phase: <date; investigating, awaiting agreement, specifying, awaiting approval, implementing, verifying, blocked, paused, stopped, cancelled, closed>
- Recipe: <name; modifiers or none> — <reason>; scope: <the task, or the revision it belongs to; proposed when not yet agreed>; classification question: <not asked / pending at <reference> / answered at <reference> / unknown — legacy record>
- Agreement (gate one): <agreed/waived/legacy/not required — lightweight or one-ticket offer/pending; revision ("agreement N") and record>
- Offer: #<id> <draft/approved/superseded/revoked>, the states `offers.py` stores. `approval.py` derives "pending" from a verified presentation and reads the owner's answer from the conversation, so never write an approval yourself; approval has no waiver ([VISUAL-REVIEW.md](VISUAL-REVIEW.md) "The gates"). Legacy tasks the owner listed at the upgrade keep their `- Approval (gate two):` line unchanged
- Lightweight edit (only when nothing a user or caller can notice changes): <files> — <why>; its minimal offer lists those files. `git commit` of only those files only when the offer names that operation, and no other git write
- Implementation: <not started/in progress/implemented/partial>
- Verification / owner acceptance: <not run/passed/limited/blocked; evidence and what is outstanding>
- Blockers: <ticket IDs, open questions, interrupted work>
- Changed files: <paths this task changed so far, or none>
- Scope paths: <optional: backticked root-relative files or folders (`src/finance/`) the task may touch; a project's scoped required reads use it>.
- Next safe action: <last result and the specific next step>

## Working context
- Owner (a name, never an email address); repository / branch / worktree; task identity and why
- Decision check (FINDINGS ref); specialists; test output folder and cleanup condition

## Goal and acceptance
## Baseline before this change
<Per check: exact command, working directory, commit plus diff hash, environment (OS, runtime and tool versions), and each failing test's name with its first error line. Reuse it only while all of these still match (`scripts/baseline_state.py record` when it runs, `check` before reuse); otherwise run it again.>
## Approach and scope
## Agreement
<Agreement: behavior, journeys, scope, exclusions, acceptance, assumptions; the user's answer and date.>
<For a change a user sees on screen, the purpose statement; each line names its source (CONTEXT.md, code, the user's answer) or `unknown`:>
- Who: <the people who use this screen>
- Situation: <when and where they use it>
- Goal: <what they are trying to get done>
- Must stand out: <what they need to see first>
## Approval
<Legacy tasks only: implementation approval: revision, report, the user's answer and date, included tickets, exclusions, what needs re-approval. Offer tasks record the offer id in the checkpoint and the answer in DECISIONS.>
## Outcome
```

An approved offer means implementation authority; `Agreement` never does (gates: [VISUAL-REVIEW.md](VISUAL-REVIEW.md)). The checkpoint holds the current summary, TODO the item states, FINDINGS the detail, DECISIONS the reasons; don't repeat totals across them. Mark an unapproved revision "proposed"; it doesn't replace the last approved one. Write an agreement revision as "agreement N", never `rN`, because the gate reads any `rN` in the checkpoint as a plan revision.

## TODO and evidence

Before touching shared files, record `git status` and enough diff to tell existing edits from yours.

IDs: requirement R, evidence E, acceptance A, ticket T, journey J, question Q, check result V. Keep existing IDs. When an older TODO repeats an ID across revisions, read [TASK-HISTORY.md](TASK-HISTORY.md) "Qualified IDs" before you refer to one.

**Current open work first.** Give each nontrivial ticket an action title and labeled sections, not a paragraph of semicolons inside a checkbox. The ticket explains the next action; test history and old attempts live in FINDINGS, reasons in DECISIONS. Completed or superseded history stays clearly labeled behind the current work. No file per ticket.

A TODO of labeled tickets starts with an overview table: Ticket, What needs to happen, Status, Dependencies. The table is a summary for readers, not a second status system: each ticket's single `Status:` line is the source. `open_items.py` reports a table that disagrees with its tickets; correct the table from the ticket, never the reverse. `record.py tick` sets the ticket and its row to Verified together.

```markdown
## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| R1/T1 | Remember the selected setting after restart | Not started | none |

## Tickets

### R1/T1 — Remember the selected setting after restart
Status: Not started

What needs to happen: <one or two plain sentences: the change and why>

Purpose: <for a ticket a user sees on screen, the agreement's purpose statement in one line; else omit>

What should work:
- A fresh application instance restores the saved value.
- An invalid saved value follows the agreed failure behavior.

Technical details:
- <files it may change and must not change; test seam and what it misses; TDD: yes, or no and why>

Documents: <the related documents this ticket changes, or none>

How to verify:
- <exact command, where it runs, expected result>
- Human check: <what a person checks, when>

Verification: not run

References:
- Supports: R1, A1
- Depends on: none
- Evidence: none
```

`Status:` holds one listed state, once. `How to verify` lists planned checks only, never results. The result goes on the one `Verification:` line (`not run`, `passed`, `failed: <what>`, `blocked: <why>`) and its pointer on `Evidence:`; the run details go to FINDINGS. A `Human check:` (or `needs human`) under How to verify keeps the ticket unverified until an `Owner acceptance:` line records the person's result (who, date, V-ID). Add `Decision:`, `Blocker:` or `Paused:` lines when they apply; omit a section with nothing to say, and state each fact once.

A small exact task can remain `- [ ] T1 — <action>; verify: <check>`. Do not force Epic, Story, priority, owner or empty template sections onto every edit; add metadata only when it changes coordination. Scope, acceptance, dependencies and evidence must still be clear. Sample: [readable-todo.md](examples/readable-todo.md). When you tidy an existing TODO's layout, read TASK-HISTORY.md "Tidying a TODO layout" first.

Ticket states remain: not started, ready, in progress, implemented — verification pending, review findings open, verified, blocked, paused, cancelled, superseded, removed, not applicable. **Ready is not implementation permission.** `verified` requires all current acceptance checks after the last relevant repair, including required device/human checks. Implementation, verification and owner acceptance are different facts. A missing device or failed environment blocks verification; it does not prove an implementation defect. A task-caused failure returns that work to repair.

Verified is a passed terminal outcome. Cancelled, superseded, removed and not applicable are closed **without** a test pass and need the decision that caused them. Blocked/paused are waiting states, not terminal success; execution may deliver partial when nothing authorized is runnable. When the owner stops or pauses work, unfinished tickets become `Status: paused` with the reason on its own line (`Paused: owner stop, <date>: "<words>"`); keep their Verification as it was. Never call a waived or owner-removed check passed. A checked box plus some V-ID is insufficient while required verification remains missing. Flag contradictions instead of selecting the most convenient sentence.

Update the actual verification result first; then tick with its evidence. `record.py tick` refuses ambiguous IDs and outstanding verification, and `open_items.py` flags incomplete results and unrecognized Status lines; neither runs a test, proves acceptance or certifies evidence freshness.

A V entry records the command, folder, versions, result, which state of the files it ran on (commit plus local diff), and what it didn't cover (`UNTESTED — <scope and reason>`). Reading a file is not a passed test. An agent saying "done" is a claim until you check its results.

Specialist use: record the resolved skill, where it came from and whether it was actually invoked ([SPECIALISTS.md](SPECIALISTS.md)). Installed is not used; a missing specialist doesn't authorize a homemade replacement.

## Checkpoint as you go

Before each unit of work, save what it is, the files it will touch and its check. After it, save what changed, the result and the next step. This is the recovery mechanism; an end-of-session summary is only a bonus. Use `scripts/record.py` (new, append, replace-section, set-line, tick with evidence, batch for several exact edits) instead of ad-hoc edit scripts or `node -e`/`sed` replaces that fail silently; it keeps each file's line endings. Prefer the file-write tool for scripts/JSON; a shell writer needs correct quoting, encoding and an authorized target. At session start, use `scripts/open_items.py --task <folder>` as an index, then read the relevant checkpoint, authority and evidence; it also flags broken encoding and mixed line endings. Test output and scratch follow ARTIFACTS.md and stricter project rules. Only the task owner writes records; subagents return evidence. Parallel workers need non-overlapping files.

## Stop, pause and cancel

- **The owner says stop or pause**: start nothing new. Signal workers to stop at the next safe interruption point; do not start another unit; its half-written files stay as they are, listed under Changed files as unverified (never reset or discard them). Set the phase to stopped or paused and in-progress tickets to paused. Then `workflow-deliver` records a partial delivery: changed files, what was verified, what remains and the next safe action. That route has no review loop and never goes back to `workflow-execute` on its own. The phase stays stopped or paused, not closed, so when the owner asks to continue, the router sends the task to `workflow-execute` under its existing approval, after the Resume recheck below.
- **The owner cancels**: the same, with the phase and open tickets cancelled. Nothing is reverted unless the owner asks.
- **Blocked**: a ticket waiting on a decision, authority or infrastructure. Other tickets continue. When it unblocks within the approved scope, `workflow-execute` resumes it; a scope change goes to `workflow-clarify`.
- **A reviewer fails twice** (crashes, cannot be started, returns nothing usable): mark the ticket blocked with the reason. Never self-approve while subagents exist.
- **An interrupted worker**: compare its changed files with the ticket scope before trusting anything; uncertain changes stay unverified.
- **A lightweight edit**: deliver's short form, without the whole-feature review.

## Approval waits

Present the offer and the one question once, save `awaiting approval`, then end the assistant turn (the STOP in `workflow-specify` step 5). A report remaining open, elapsed time, hook feedback or an automatic goal continuation is not a new owner response. Keep writes gated. Resume on the real answer: rejection stops the proposal; requested changes produce a revised offer; approval applies only to the shown offer, task and workspace. Read [HOST-GOALS.md](HOST-GOALS.md) before you use a host goal, or when `/goal` feedback restarts a wait.

## Resume

Run `resume`; it owns the procedure. These records are what it reads. After a resume, a check or review still counts only for files and rules unchanged since it ran (its V entry's state, and `rule-maker/scripts/rules_stamp.py` for the rules).

## Revisions and older tasks

A progress update, blocker, rerun, or account or agent switch changes only the checkpoint and items. When a plan changes after agreement, or when you resume or adopt an older task, read [TASK-HISTORY.md](TASK-HISTORY.md) "Revisions" and "Forward-only adoption" first.

## Also record

- **Rules**: one readiness note in the checkpoint (RULES.md); an exception records the user's words, scope and expiry. No separate status file.
- **Owner acceptance**: set the checkpoint's verification line and add one dated line to `## Outcome` that quotes the owner's words, so the closing record no longer says acceptance is pending. Delivery reports stay unchanged as history.
- **Test output**: [ARTIFACTS.md](ARTIFACTS.md) owns the folder and retention rules; record the output folder, retained proof and the cleanup condition in the checkpoint.
- **Privacy**: never copy credentials, tokens, personal data or production records into records, prompts or screenshots. Redact first.
- **UI and ADRs**: when the task changes UI or an ADR may be due, read TASK-HISTORY.md "UI and ADR records".
