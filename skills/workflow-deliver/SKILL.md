---
name: workflow-deliver
description: "Check a finished or stopped task against its evidence and write the delivery record. Use when implementation ends or someone asks whether a task is really done."
---

# Workflow deliver

Report what was requested, built and verified, including gaps. Deliver never fixes, builds or approves.

Read shared policies from sibling `../workflow/`: RULES.md, TASK-FOLDER.md and WRITING.md before step 1; any other file there only when a step below names your case. Stop if missing; never use another skills root's copy.

**Before you start**, check:

- the PLAN checkpoint names the agreement and the approved offer (`Offer: #<id>`), or a legacy task's Approval line; else report what's missing, never reconstructing authority;
- no worker is still writing;
- execute recorded the whole-feature review, unless the task is stopped, paused, cancelled or lightweight (`workflow/TASK-FOLDER.md`); else hand back to `workflow-execute`;
- rules cover any check you rerun (`workflow/RULES.md`), else it stays not verified.

With subagents, a fresh one that didn't build the work reconciles; on execute's small route the ticket's reviewer may, labeled. Otherwise label it self-performed.

## 1. Freeze the state

Read-only: record HEAD and staged, unstaged and untracked changes against the starting `git status`.

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
| Unknown (`unknown`; in a report `unverified`, its note starting "unknown:") | The evidence is missing or can't be read; say so plainly, never guess a verdict |

A review note is not an open review finding (`../code-review/SKILL.md` "What counts as a finding").

## 3. Checks

For every required check: did it run, on which state, with what result? Rerun a stale or missing check only during active work when approved, safe and within `workflow/ARTIFACTS.md` limits. After stop, pause or cancel, start no checks, docs_check included; record the gap. Never skip or weaken a required check.

## 4. Files and documents

Map every changed file to a ticket; report unexplained changes, untouched promised files and leftover scaffolding. While work is active, run docs_check once, on this task's changes only: `python -X utf8 -I ../rule-maker/scripts/docs_check.py <project-root> --changed <files this task changed>`, and review each affected claim (`../rule-maker/DOCS.md`); otherwise list related documents as unreviewed. Unsafe contradictions block the task (DOCS.md "Severity"); others this task caused go to step 7 (`workflow-execute` if the ticket's Documents named it, else `workflow-specify`); report the rest in "Severity" order.

## 5. Reviews

Each ticket review and the whole-feature review (for one ticket, its ticket review when it was briefed with those checks) exist, cover Standards and Spec, ran on the final files and have every finding closed or limited; report missing or self-only reviews. Where code-review's blast-radius trigger fired, the review holds a "Blast radius" result. Before you write Done, run `python -X utf8 -I scripts/completion_check.py check <project-root> <task-folder>`. Exit 1 names each change without a passed review of its current form: back to `workflow-execute`, or report the task partial. Exit 2 (no baseline, no git, damaged record): partial, verification pending, never Done; say why.

## 6. Records

TODO states, the checkpoint and your ledger agree (`workflow/scripts/open_items.py` lists unevidenced ticks). List every DECISIONS entry marked `by: agent` for the user. The Agreement line is agreed, waived, legacy or not required.

## 7. Send defects back

Each mismatch becomes a finding with an owner: code, test or review defects to `workflow-execute`, agreement gaps to `workflow-clarify`, ticket gaps to `workflow-specify`; a stopped task lists them as remaining. After a code or test fix, reconcile again; after a record-only fix, recheck those records. If the user wants it as is, or stopped it, it is delivered as partial.

Done when every requirement, required check, changed file, claim and review has a verdict on the frozen state.

## 8. Write the delivery

Write PLAN `## Outcome` with `workflow/scripts/record.py` and update the checkpoint: asked, agreed and built; tickets and states; changed files and documents; checks and results; both review axes; verdicts; for UI, each class used with its defining file and, with the CSS switch off, "no CSS added" checked in the diff; limitations (`workflow/FALLBACKS.md`: remaining gaps only, plus open Risks and unproven safety facts from the blast-radius result); kept evidence and scratch; next safe action.

Then tell the user (`../workflow/WRITING.md`) what works now, what doesn't or wasn't checked, and what they still need to accept; then evidence. Run its Unslop check, then its cold-reader check. Owner or design acceptance is the user's to record.

Done when these exist: the PLAN Outcome; the chat report; and, only when the offer's presentation decision was `html-first` or the owner asks for one, a delivery snapshot, or the user's recorded "no snapshot". For a snapshot, read `../codebase-map/TASK-REPORT.md`, `../codebase-map/FLOWCHART-DESIGN.md` and, for UI, `../codebase-map/UI-FLOW.md` whole first; an unchanged reconciliation reuses it. A first or materially new outcome gets a new dated one: `codebase-map/scripts/task_report.py scaffold <approved review.json> <new delivery.json>` (with no review.json after a chat approval, first build one for the approved offer as `../workflow/VISUAL-REVIEW.md` "Prepare the report" step 2 describes), then fill every `FILL:` text and status from the records, with real captures of the built result for visible changes when safe. Put its path in the chat report. Retention: `workflow/VISUAL-REVIEW.md`.

**Lightweight edit (minimal offer)**: the same at its real size: one ledger row with its check, one review, changed files, baseline and completion check, a short report.
