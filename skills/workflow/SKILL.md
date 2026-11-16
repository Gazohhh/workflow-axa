---
name: workflow
description: "Use for repository features, fixes, refactors, research, plans, audits and task resumption, including ordinary prompts. Find the task, check rules, route to the phase skill its records require: clarify, specify, execute or deliver. Explain-only stays read-only."
---

# Workflow

Route by intent and authority. **Pick the recipe (§3), then invoke the phase skill §4 selects for changes; inspection stays read-only.** Ask readiness blockers first, then §2's identity question and §3's classification question only when they are needed; behaviour questions belong to `workflow-clarify`. Write for someone new to the project ([WRITING.md](WRITING.md)).

## 1. Check rules readiness

Read [RULES.md](RULES.md) before planning or writing; check adequacy even if rule-maker never ran. If rules are missing or weak: name the gaps and ask *Set up rules now* or *Skip for this task*; read-only work continues meanwhile, writes wait for the answer. Inspection can report rules gaps without setup. UI plans read `../ui-design/SKILL.md`. Write or offer new CSS only when the machine CSS switch is on and the project allows it (`rule-maker/rules/DESIGN.md` rule 1); record approved sources and preview/release limits.

## 2. Find the task

1. State repository, branch and local changes; protect user edits.
2. Intent: **Inspect** (explain, research, diagnose, audit, review) is read-only with no gates or new records. **Plan** needs agreement and specification, never code. **Change** or later "fix it" uses the gates. **Resume** reconciles existing authority.
3. Before creating any task folder or Plan, Change or Resume records, follow [TASK-FOLDER.md](TASK-FOLDER.md). A new chat is not a new task. When related work might match, invoke `workflow-clarify`, which asks "separate task or revision?" with its first questions. Provisional identity is not approval.
4. Checkpoint before lengthy discovery; without files disclose what cannot survive.
5. A message that does not clearly belong to the active task: answer a question without touching records. Before any change, ask "part of <task>, or separate?", checkpoint and offer a fresh session.

## 3. Pick the recipe

1. At task entry and for each new request on existing work, use the request, the relevant code and the recorded decisions to settle three things: the outcome wanted, whether a change is requested, and whether existing behaviour is preserved, corrected or replaced. Reuse a pick already made for this same request; a phase transition is not a new request.
2. Match the work to one row of [flows/INDEX.md](flows/INDEX.md), add its modifiers (UI, Security, Compatibility) and read only that recipe. Load `ui-design` only for the ui recipe or the UI modifier. Inspect is a read-only route with no recipe file.
3. **Not sure** means two routes fit that need different behaviour, permissions or acceptance, or the outcome (or whether a change is wanted) isn't stated. Needing several references is not uncertainty. Then ask with the question tool: *Fix something broken · Add or change a feature · Start a new project · Only investigate*, plus Other, recommended answer first with one line why. Ask at most once for the task, and once more for each later revision that changes, or may change, the kind of work. Never ask small versus complex bug. An unanswered classification question stays pending, and a new session does not reset it; until it is answered, only read-only work continues.
4. **Other** with a clear outcome: build the steps from the phases. A vague Other: Inspect first, then ask through `grilling`; never repeat the classification menu.
5. Once the route is settled, show one line before substantive work: `Recipe: <name> (<plain meaning>) — <reason tied to this request>. Say so if you meant something else.` Name modifiers by their effect here, for example `plus Compatibility: saved quotations keep working`. For Inspect: `Route: Inspect — <reason>. Say so if you meant something else.` Show it at task entry, revision entry and resume, lightweight edits included; once per entry, even when the router and clarify both run. Text written before tool calls may reach the owner only as a summary: when the line came before tool calls, repeat it at the top of that turn's final message or first question round. It is a notice, not a question: continue within the current authority. Record the pick and the classification-question reference in the checkpoint ([TASK-FOLDER.md](TASK-FOLDER.md)); Inspect creates no records.
6. On resume, reconcile the recorded pick with the current scope and show it again. An unchanged scope keeps its pick and question history. An older task with no recorded pick: infer it from the records and code; a missing line alone is not uncertainty. A status-only resume stays read-only.
7. When later evidence or the owner's correction changes the pick, show the new line with the evidence, keep the work done and the question history, and add only the steps the new recipe adds. A changed pick grants no new authority; changed scope follows the revision and approval rules.

When something a recipe needs is missing, use [FALLBACKS.md](FALLBACKS.md).

## 4. Route to the phase

Inspect with read-only tools and relevant available specialists: `code-review`, `codebase-map` (cold-reader check), `domain-modeling`, `resume` (status), `research`, `diagnosing-bugs`. Report evidence and uncertainty, then stop. Otherwise read the checkpoint Agreement and its Offer. A task the owner listed as a pre-offer approval at the upgrade keeps its Approval line, for its recorded scope only. Take the first matching row:

| Task state | Next skill | Permission |
|---|---|---|
| Owner stops, pauses or cancels | `workflow-deliver` partial route | Handoff only; no new implementation or review loop |
| New goal, changed scope, agreement pending, or new request on existing work | `workflow-clarify` | Investigate and agree behavior; no application edits |
| Agreed, or agreement not required; no approved offer for the tickets | `workflow-specify` | Prepare records and the offer; stop for the answer |
| Stopped work handed off, or all tickets terminal; no delivery yet | `workflow-deliver` | Reconcile and report; no fixes |
| Approved ready ticket, or explicit continuation after Resume recheck | `workflow-execute` | Only the approved scope |
| Delivery recorded | Report it | No new work |


Invoke with the skill tool (`workflow-axa:<name>`) or read its SKILL.md whole. The table routes; it does not replace a phase. Missing skills block only their phase.

**Every change** gets an offer and the one question (`workflow-specify` step 5). Make and present it only through `workflow-specify`: it records the offer with `record.py offer create` and shows the presentation `record.py offer present` prints. An offer in your own words, or any other question, can't be approved: the hook refuses the edit that follows. The plan report is built only on *Show review.html first* or when the owner asks for it. One-ticket work, a small visible change included, gets one ticket and its offer.

**Lightweight edit**: exact, low-risk, no observable behavior, architecture, interface, dependency or security change. A visible behavior change, however small and fully specified, is not lightweight: it gets the one-ticket offer. A lightweight edit gets the minimal offer (its files, its check and a one-line why) through `workflow-specify` step 5, and is still asked the one question. After the answer, verify, review once per [AUDIT.md](AUDIT.md), then short `workflow-deliver`.

## 5. The two gates

Agreement, then the offer and the one question: [VISUAL-REVIEW.md](VISUAL-REVIEW.md) owns both. STOP for user approval before application code. Answering grilling questions is not agreement, and a generic "go" is not approval of an unseen plan.

## Always

- Behaviour questions: `grilling`; classification: §3. Evidence: [GROUNDING.md](GROUNDING.md). Specialists: [SPECIALISTS.md](SPECIALISTS.md) ([SETUP.md](SETUP.md)). Reviews and necessity check: [AUDIT.md](AUDIT.md). Output: [ARTIFACTS.md](ARTIFACTS.md).
- Never stage, commit, push, branch, reset, deploy or publish unasked.
- Pass workers the output folder, write scope, rules and UI authority. Read applicable instructions whole; do not load unrelated references.
- Approval waits: present once, end the turn; no polling. Host goals: TASK-FOLDER.md "Approval waits and host goals". End with **Running**, **Waiting on you** or **Done**; do not end running work unless the host will wake you. When an offer waits for the answer, its presentation ends the reply and its question is the state line: put nothing after it.
- Write requested handoffs from the checkpoint ([CHATGPT-PROMPTS.md](CHATGPT-PROMPTS.md)).
- When needed: PDF-DELIVERABLE.md, OPTIONAL-HELPERS.md.
