---
name: workflow-deliver
description: "Reconcile a finished or stopped workflow task against its evidence before reporting it done: map every agreed requirement, check, changed file and review finding to current proof, mark stale or missing proof, and write the final delivery record and report. Use when implementation ends or someone asks whether the task is really finished."
---

# Workflow deliver

Reconcile what was asked, built and verified, then report it, gaps included. Deliver never fixes, builds or approves; defects go back to their phase, and after a fix you reconcile again.

Read shared policies from `../workflow/` from this SKILL.md (missing: stop and say so; never another skills root's copy). Its "Always" list applies here too.

**Before you start**, check: the PLAN checkpoint names the agreement and approval, or the lightweight request (if not, report what's missing; don't reconstruct authority); no worker is still writing; execute recorded the whole-feature review (else hand back to `workflow-execute`; never run it here); rules cover any check you rerun (`workflow/RULES.md`), else that check stays not verified.

With subagents, run the reconciliation in a fresh one that didn't build the work; otherwise say it is self-performed. TODO ticks, "done" messages and earlier summaries are claims to test.

## 1. Freeze the state

Read-only: record HEAD and staged, unstaged and untracked changes; compare with the starting `git status`. Every verdict refers to this state.

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

For every required check: did it run, on which state, with what result? A stale or missing check that is approved, safe and within `workflow/ARTIFACTS.md` limits may be rerun under a new V-ID; otherwise it stays not verified. Never skip or weaken a required check to finish.

## 4. Files

Map every changed file to a ticket; report unexplained changes, promised files left unchanged and leftover scaffolding. The user's earlier edits stay theirs.

## 5. Reviews

Each ticket review and the whole-feature review exist, cover Standards and Spec, ran on the final files, and have every finding closed or limited; report a missing or self-only review.

## 6. Records

TODO states, the checkpoint and your ledger agree (`workflow/scripts/open_items.py` lists unevidenced ticks). List every DECISIONS entry marked `by: agent` so the user sees the choices made for them. Both gates are recorded, or classified legacy, waived or lightweight. Test output follows ARTIFACTS.md.

## 7. Send defects back

Each mismatch becomes a finding with an owner: code, test or review defects to `workflow-execute`, agreement gaps to `workflow-clarify`, ticket gaps to `workflow-specify`. Don't fix them here. If the user wants it delivered as is, it is delivered as partial.

Done when every requirement, required check, changed file and review has a verdict on the frozen state.

## 8. Write the delivery

Write PLAN `## Outcome` (`workflow/scripts/record.py replace-section`) and update the checkpoint: asked, agreed and built; tickets and states; changed files; checks and results; both review axes; acceptance verdicts; for UI, each class used with the file that defines it and "no CSS added" checked in the diff; limitations; kept evidence and remaining scratch; next safe action. 

Then tell the user, written with `../simple-english/SKILL.md`: what works now, what doesn't or wasn't checked, what they still need to accept; then the evidence. Cold-reader check: could someone who missed the conversation say the goal, what changed, what stayed, what you ask of them and how it was checked? Say it ran. Owner or design acceptance is the user's to record.

Done when all three exist: the PLAN Outcome; a new dated delivery snapshot made with `codebase-map` from these records (start its JSON with `codebase-map/scripts/task_report.py scaffold <approved review.json> <new delivery.json>` then fill every `FILL:` text and set each status (acceptance, checks, completion, checkpoint, screens) from the records; for a change a user can see, its screen diagram uses real captures of the built result whenever the screen can be opened safely, e.g. with codebase-map's `scripts/screenshot_report.py --height 900`) (saved beside earlier reports, never overwriting one) whenever the task has any HTML report, or the user's recorded "no snapshot"; and the chat report. Give the snapshot path in the chat report.

**Lightweight edit**: the same at its real size: one ledger row with its check, its one review and changed files, and a short report. No ticket or whole-feature reviews, no HTML snapshot.

Never stage, commit, push, deploy or publish.
