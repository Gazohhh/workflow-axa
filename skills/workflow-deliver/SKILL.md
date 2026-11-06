---
name: workflow-deliver
description: "Reconcile a finished or stopped workflow task against its evidence: map every agreed requirement, check, changed file and review finding to current proof, mark stale or missing proof, then write the delivery record and report. Use when implementation ends or someone asks whether the task is really finished."
---

# Workflow deliver

Report what was requested, built and verified, including gaps. Deliver never fixes, builds or approves; defects go back to their phase.

Read shared policies from sibling `../workflow/` (missing: stop and say so; never another skills root's copy). Its "Always" list applies here too.

**Before you start**, check: the PLAN checkpoint names the agreement and approval, or the lightweight request (if not, report what's missing; don't reconstruct authority); no worker is still writing; execute recorded the whole-feature review, unless the task is stopped, paused, cancelled or lightweight (`workflow/TASK-FOLDER.md`); otherwise hand back to `workflow-execute`, never run it here; rules cover any check you rerun (`workflow/RULES.md`), else that check stays not verified.

With subagents, a fresh one that didn't build the work reconciles; on the small route the ticket's reviewer may, labelled. Otherwise say it is self-performed. TODO ticks and summaries need evidence.

## 1. Freeze the state

Read-only: record HEAD and staged, unstaged and untracked changes against the starting `git status`. Every verdict refers to this state.

## 2. Requirements

For each agreed requirement, acceptance item, per-actor line and assumption, approved changes included, record its tickets, its V-IDs and one verdict. Reading the agreement differently from its words is a gap for `workflow-clarify`, never a verdict:

| Verdict (report value) | Needs |
|---|---|
| Verified (`verified`) | A passed check, actually run, on files unchanged since, with no open review finding |
| Partial (`partial`) | Some of it observed; the gap named |
| Failed (`failed`) | A check that failed |
| Not verified (`unverified`) | No check, a stale check (report the check as `stale`), or no environment; with the reason |
| Waived (`waived`) | A recorded user decision; never shown as passed |
| Superseded or descoped (`superseded`) | The decision that replaced it; no check cited |

## 3. Checks

For every required check: did it run, on which state, with what result? A stale or missing check may be rerun only while work is active and its execution is approved, safe and within `workflow/ARTIFACTS.md` limits. After stop, pause or cancel, start no checks: record the gap. Never skip or weaken a required check.

## 4. Files

Map every changed file to a ticket; report unexplained changes, untouched promised files and leftover scaffolding.

## 5. Reviews

Each ticket review and the whole-feature review exist, cover Standards and Spec, ran on the final files and have every finding closed or limited; report missing or self-only reviews.

## 6. Records

TODO states, the checkpoint and your ledger agree (`workflow/scripts/open_items.py` lists unevidenced ticks). List every DECISIONS entry marked `by: agent` for the user. Both gates are recorded, or classified legacy, waived or lightweight.

## 7. Send defects back

Each mismatch becomes a finding with an owner: code, test or review defects to `workflow-execute`, agreement gaps to `workflow-clarify`, ticket gaps to `workflow-specify`. Don't fix them here; for a stopped, paused or cancelled task, list them as remaining instead. After a code or test fix, reconcile again; after a record-only fix, recheck those records. If the user wants it delivered as is, or stopped it, it is delivered as partial.

Done when every requirement, required check, changed file and review has a verdict on the frozen state.

## 8. Write the delivery

Write PLAN `## Outcome` with `workflow/scripts/record.py` and update the checkpoint: asked, agreed and built; tickets and states; changed files; checks and results; both review axes; acceptance verdicts; for UI, each class used with the file that defines it and "no CSS added" checked in the diff; limitations; kept evidence and remaining scratch; next safe action. 

Then tell the user, written with `../simple-english/SKILL.md`: what works now, what doesn't or wasn't checked, what they still need to accept; then evidence. Cold-reader check: could someone who missed the conversation say the goal, what changed, what stayed, what you ask of them and how it was checked? Owner or design acceptance is the user's to record.

Done when all three exist: the PLAN Outcome; whenever the task has any HTML report, a delivery snapshot or the user's recorded "no snapshot"; and the chat report. Give the snapshot path there. An unchanged reconciliation reuses the existing delivery snapshot; status-only changes stay in the records. A first or materially new outcome (verdict, check, file or completion change) gets a new dated snapshot, never overwriting an earlier one: run `codebase-map/scripts/task_report.py scaffold <approved review.json> <new delivery.json>`, then fill every `FILL:` text and every status from the records; visible changes use real captures of the built result when safe. Retention: `workflow/VISUAL-REVIEW.md`.

**Lightweight edit**: the same at its real size: one ledger row with its check, its one review and changed files, and a short report. No ticket or whole-feature reviews, no HTML snapshot.

Never stage, commit, push, deploy or publish.
