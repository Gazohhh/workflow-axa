---
name: workflow
description: "Use for repository features, fixes, refactors, research, plans, audits and task resumption, including ordinary prompts. Find the task, check rules, route to the phase skill its records require: clarify, specify, execute or deliver. Explain-only stays read-only."
---

# Workflow

Route by intent and authority. **Invoke the phase skill §3 selects for changes; inspection stays read-only.** Ask only readiness blockers here. Write for someone new to the project ([WRITING.md](WRITING.md)).

## 1. Check rules readiness

Read [RULES.md](RULES.md) before planning or writing; check adequacy even if rule-maker never ran. If missing: offer setup, limited exception, read-only inspection or stop. Inspection can report rules gaps without setup. UI plans read `../ui-design/SKILL.md`. Never write or offer new CSS; record approved sources and preview/release limits.

## 2. Find the task

1. State repository, branch and local changes; protect user edits.
2. Intent: **Inspect** (explain, research, diagnose, audit, review) is read-only with no gates or new records. **Plan** needs agreement and specification, never code. **Change** or later "fix it" uses the gates. **Resume** reconciles existing authority.
3. Before creating any task folder or Plan, Change or Resume records, follow [TASK-FOLDER.md](TASK-FOLDER.md). A new chat is not a new task. When related work might match, invoke `workflow-clarify`, which asks "separate task or revision?" with its first questions. Provisional identity is not approval.
4. Checkpoint before lengthy discovery; without files disclose what cannot survive.
5. A message that does not clearly belong to the active task: answer a question without touching records. Before any change, ask "part of <task>, or separate?", checkpoint and offer a fresh session.

## 3. Route

Inspect with read-only tools and relevant available specialists: `code-review`, `codebase-map` (cold-reader check), `domain-modeling`, `task-status`, `research`, `diagnosing-bugs`. Report evidence and uncertainty, then stop. Otherwise read checkpoint Agreement and Approval. Legacy approval covers only its recorded scope. Take the first matching row:

| Task state | Next skill | Permission |
|---|---|---|
| Owner stops, pauses or cancels | `workflow-deliver` partial route | Handoff only; no new implementation or review loop |
| New goal, changed scope, agreement pending, or new request on existing work | `workflow-clarify` | Investigate and agree behavior; no application edits |
| Small change approved, same request, undelivered | Edit listed files, then short `workflow-deliver` | Only those files |
| Agreed; tickets or plan report unapproved | `workflow-specify` | Prepare records/report; stop for approval |
| Stopped work handed off, or all tickets terminal; no delivery yet | `workflow-deliver` | Reconcile and report; no fixes |
| Approved ready ticket, or explicit continuation after Resume recheck | `workflow-execute` | Only the approved scope |
| Delivery recorded | Report it | No new work |


Invoke with the skill tool (`workflow-axa:<name>`) or read its SKILL.md whole. The table routes; it does not replace a phase. Missing skills block only their phase.

**Lightweight edit**: exact, low-risk, no observable behavior, architecture, interface, dependency or security change. A visible behavior change, however small and fully specified, is not lightweight: use a small change or both gates (possibly combined). Verify, review per [AUDIT.md](AUDIT.md), then short `workflow-deliver`.

**Small change**: a visible change to listed existing files, approved by one quoted owner yes without a plan report ([VISUAL-REVIEW.md](VISUAL-REVIEW.md) "Small change"). Unlike a lightweight edit, a user can notice it, so the owner approves it first.

## 4. The two gates

Defined in [VISUAL-REVIEW.md](VISUAL-REVIEW.md):

1. **Agreement** on behavior and scope. Permits the detailed plan, not code.
2. **Implementation approval** of tickets, tests and the plan report. STOP for user approval before application code.

Answering grilling questions is not agreement, and a generic "go" is not approval of an unseen plan.

## Always

- Questions: `grilling`. Evidence: [GROUNDING.md](GROUNDING.md). Specialists: [SPECIALISTS.md](SPECIALISTS.md) ([SETUP.md](SETUP.md)). Reviews and necessity check: [AUDIT.md](AUDIT.md). Output: [ARTIFACTS.md](ARTIFACTS.md).
- Never stage, commit, push, branch, reset, deploy or publish unasked.
- Pass workers the output folder, write scope, rules and UI authority. Read applicable instructions whole; do not load unrelated references.
- Approval waits: present once, end the turn; no polling. Host goals: TASK-FOLDER.md "Approval waits and host goals". End with **Running**, **Waiting on you** or **Done**; do not end running work unless the host will wake you.
- Write requested handoffs from the checkpoint ([CHATGPT-PROMPTS.md](CHATGPT-PROMPTS.md)).
- When needed: PDF-DELIVERABLE.md, OPTIONAL-HELPERS.md.
