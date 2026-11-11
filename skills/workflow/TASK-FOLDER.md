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
| A fresh worktree has no installed dependencies (no `node_modules`, `vendor`) | Never install on your own. Ask with the plan: the owner installs in the worktree, or you link the main checkout's install at the same lockfile. In a workspace (monorepo) install the linked packages point into the main checkout, so prefer the owner's install there. Remove a link as a link (`rmdir` on Windows, `rm` without `-r`); a recursive delete through it deletes the main checkout's files. |
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

A lightweight edit or small change uses only PLAN with short Work and Evidence sections; if it grows, move those sections into the normal files and leave pointers in PLAN. Existing tasks keep their layout (including legacy `STATUS.md`); don't add missing template files for conformity. Records are project docs, not permission to commit them. No `HANDOFF.md` or other duplicate of the checkpoint.

## PLAN.md

Leave out what doesn't apply; write `unknown` rather than inventing.

```markdown
# <Task>

## Current checkpoint
- Updated / phase: <date; investigating, awaiting agreement, specifying, awaiting approval, implementing, verifying, blocked, paused, stopped, cancelled, closed>
- Agreement (gate one): <agreed/waived/legacy/not required — lightweight or small change/pending; revision ("agreement N") and record>
- Approval (gate two): <approved/waived/legacy/not approved, or `small change approved <date>: "<answer>"` (VISUAL-REVIEW.md "Small change"); revision rN, the report file or the user's recorded "no report", and the user's exact words in quotes (the whole answer, including restrictions, from a real message after the named plan was shown)>. `waived` needs the user's own words skipping this approval; a non-interactive session, a request for a finished result or "don't ask me" about something else is never a waiver: stop and ask
- Lightweight edit (only when nothing a user or caller can notice changes): <files> — <why>; it allows `git commit` of only those files when the owner's latest message asks to commit, and no other git write
- Small change: <existing files, comma-separated> — <what changes>
- Implementation: <not started/in progress/implemented/partial>
- Verification / owner acceptance: <not run/passed/limited/blocked; evidence and what is outstanding>
- Blockers: <ticket IDs, open questions, interrupted work>
- Changed files: <paths this task changed so far, or none>
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
<Implementation approval: revision, report, the user's answer and date, included tickets, exclusions, what needs re-approval.>
## Outcome
```

`Approval` means implementation authority; `Agreement` never does (gates: [VISUAL-REVIEW.md](VISUAL-REVIEW.md)). The checkpoint holds the current summary, TODO the item states, FINDINGS the detail, DECISIONS the reasons; don't repeat totals across them. Mark an unapproved revision "proposed"; it doesn't replace the last approved one. Write an agreement revision as "agreement N", never `rN`, because the gate reads any `rN` in the checkpoint as a plan revision. The `Small change:` line and its Approval line follow [VISUAL-REVIEW.md](VISUAL-REVIEW.md) "Small change".

## TODO and evidence

Before touching shared files, record `git status` and enough diff to tell existing edits from yours.

IDs: requirement R, evidence E, acceptance A, ticket T, journey J, question Q, check result V. Keep existing IDs. When an older TODO restarts T1 under each revision, address it as `D4/T1` or `D3/T1`; never guess which T1 a short reference means. New cross-revision references use that qualified identity. Do not renumber old records.

The HTML renderer uses safe local IDs without `/`. Keep a qualified source ID such as `D4/T8` in the report task title; use a unique projection alias such as `D4-T8` in JSON references. This does not rename the source ticket. See codebase-map REPORT.md; check aliases for collisions rather than blindly replacing punctuation.

**Current open work first.** Give each nontrivial ticket an action title and labeled sections, not a paragraph of semicolons inside a checkbox. The ticket explains the next action; test history and old attempts live in FINDINGS, reasons in DECISIONS. Completed or superseded history stays clearly labeled behind the current work. No file per ticket.

A TODO of labeled tickets starts with an overview table: Ticket, What needs to happen, Status, Dependencies. The table is a summary for readers, not a second status system: each ticket's single `Status:` line is the source. `open_items.py` reports every row whose Status or Dependencies differ from the ticket, a row naming a missing, repeated or ambiguous ticket, and a ticket with no row; correct the table from the ticket, never the reverse. In a file that repeats an ID, the table uses the qualified ID (`D4/T3`). `record.py tick` sets the ticket and its row to Verified together and refuses while the row disagrees.

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

A small exact task can remain `- [ ] T1 — <action>; verify: <check>`. Do not force Epic, Story, priority, owner or empty template sections onto every edit; add metadata only when it changes coordination. Scope, acceptance, dependencies and evidence must still be clear. Sample: [readable-todo.md](examples/readable-todo.md). A layout tidy changes layout, not state: keep a checkbox line as it is, or convert it only to a listed state that records the same fact, and keep contradictions visible. Run `open_items.py --task` before and after; any changed ticket state means the tidy changed content.

Ticket states remain: not started, ready, in progress, implemented — verification pending, review findings open, verified, blocked, paused, cancelled, superseded, removed, not applicable. **Ready is not implementation permission.** `verified` requires all current acceptance checks after the last relevant repair, including required device/human checks. Implementation, verification and owner acceptance are different facts. A missing device or failed environment blocks verification; it does not prove an implementation defect. A task-caused failure returns that work to repair.

Verified is a passed terminal outcome. Cancelled, superseded, removed and not applicable are closed **without** a test pass and need the decision that caused them. Blocked/paused are waiting states, not terminal success; execution may deliver partial when nothing authorized is runnable. When the owner stops or pauses work, unfinished tickets become `Status: paused` with the reason on its own line (`Paused: owner stop, <date>: "<words>"`); keep their Verification as it was. Never call a waived or owner-removed check passed. A checked box plus some V-ID is insufficient while required verification remains missing. Flag contradictions instead of selecting the most convenient sentence.

`record.py tick` supports labeled blocks and legacy checkboxes, refuses ambiguous IDs and explicit outstanding verification, and preserves endings/history. Update the actual verification result first; then tick with its evidence. It is a record editor, not a test runner or proof of acceptance. `open_items.py` reads both formats, flags explicit incomplete results and reports an unlisted or conflicting Status as not recognized (neither open nor verified); it does not certify natural-language completeness or evidence freshness.

A V entry records the command, folder, versions, result, which state of the files it ran on (commit plus local diff), and what it didn't cover (`UNTESTED — <scope and reason>`). Reading a file is not a passed test. An agent saying "done" is a claim until you check its results.

Specialist use: record the resolved skill, where it came from and whether it was actually invoked ([SPECIALISTS.md](SPECIALISTS.md)). Installed is not used; a missing specialist doesn't authorize a homemade replacement.

## Checkpoint as you go

Before each unit of work, save what it is, the files it will touch and its check. After it, save what changed, the result and the next step. This is the recovery mechanism; an end-of-session summary is only a bonus. Use `scripts/record.py` (new, append, replace-section, set-line, tick with evidence, batch for several exact edits) instead of ad-hoc edit scripts or `node -e`/`sed` replaces that fail silently; it keeps each file's line endings. Prefer the file-write tool for scripts/JSON; a shell writer needs correct quoting, encoding and an authorized target. At session start, use `scripts/open_items.py --task <folder>` as an index, then read the relevant checkpoint, authority and evidence; it also flags broken encoding and mixed line endings. Test output and scratch follow ARTIFACTS.md and stricter project rules. If the intended output location is public or not ignored where privacy is required, resolve that before writing. Keep cited evidence until its recorded retention condition is met. Only the task owner writes records; subagents return evidence. Parallel workers need non-overlapping files.

## Stop, pause and cancel

- **The owner says stop or pause**: start nothing new. Signal workers to stop at the next safe interruption point; do not start another unit; its half-written files stay as they are, listed under Changed files as unverified (never reset or discard them). Set the phase to stopped or paused and in-progress tickets to paused. Then `workflow-deliver` records a partial delivery: changed files, what was verified, what remains and the next safe action. That route has no review loop and never goes back to `workflow-execute` on its own. The phase stays stopped or paused, not closed, so when the owner asks to continue, the router sends the task to `workflow-execute` under its existing approval, after the Resume recheck below.
- **The owner cancels**: the same, with the phase and open tickets cancelled. Nothing is reverted unless the owner asks.
- **Blocked**: a ticket waiting on a decision, authority or infrastructure. Other tickets continue. When it unblocks within the approved scope, `workflow-execute` resumes it; a scope change goes to `workflow-clarify`.
- **A reviewer fails twice** (crashes, cannot be started, returns nothing usable): mark the ticket blocked with the reason. Never self-approve while subagents exist.
- **An interrupted worker**: compare its changed files with the ticket scope before trusting anything; uncertain changes stay unverified.
- **A lightweight edit or small change**: deliver's short form, without the whole-feature review.

## Approval waits and host goals

Present the current report and approval question once, save `awaiting approval`, then end the assistant turn. A report remaining open, elapsed time, hook feedback or an automatic goal continuation is not a new owner response. Keep writes gated. Resume on the real answer: rejection stops the proposal; requested changes produce a new revision; approval applies only to the shown task, workspace and report bytes.

Before using a host goal, bound its current authorized phase with an observable result and check. For planning, completion is the reviewable report and one approval request. For implementation, name the approved tickets and verification. Do not use unbounded conditions such as "maximum FPS". Explicitly deferred work stays unverified with its reason; it is not a runnable completion requirement for the current phase. Genuine blockers, waiting for input and an owner's stop each end autonomous work without claiming the whole task passed. Preserve other authorized, independent work.

Claude Code `/goal` is an independent Stop evaluator. If stale goal feedback restarts an approval wait, diagnose it once and hand control back; do not repeat "still waiting", call sleep in a loop, forge a user response or weaken approval checks. The owner can interrupt the loop, inspect `/goal`, and use `/goal clear` in that affected session. Confirm the host reports it cleared; a restart alone may restore the active goal. Clearing that host loop does not approve implementation or mark deferred work complete. Do not silently clear or rewrite a user's goal in another host.

The workflow Stop hook returns without feedback for `Waiting on you` and for a direct owner stop. It cannot cancel another hook's retry decision. Test actual host idleness separately from synthetic hook output. Source: [Claude Code goal documentation](https://code.claude.com/docs/en/goal).

## Resume

Run `resume-task`; it owns the procedure. These records are what it reads. After a resume, a check or review still counts only for files and rules unchanged since it ran (its V entry's state, and `rule-maker/scripts/rules_stamp.py` for the rules).

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

## Also record

- **Rules**: one readiness note in the checkpoint (RULES.md); an exception records the user's words, scope and expiry. No separate status file.
- **Owner acceptance**: set the checkpoint's verification line and add one dated line to `## Outcome` that quotes the owner's words, so the closing record no longer says acceptance is pending. Delivery reports stay unchanged as history.
- **UI**: one checkpoint entry: area and mode, approving source, allowed components, preview, exceptions, design acceptance and release state (ui-design).
- **Test output**: follow [ARTIFACTS.md](ARTIFACTS.md); reuse the recorded output folder (default `.artifacts/<task-folder-name>/`); record retained proof and the cleanup condition in the checkpoint. No manifests or cleanup logs.
- **Privacy**: never copy credentials, tokens, personal data or production records into records, prompts or screenshots. Redact first.
- **ADRs**: offer one only when `domain-modeling`'s criteria hold; a reversal is a new superseding ADR. Proposed ADRs are not accepted because time passed. Task progress stays in task records.
