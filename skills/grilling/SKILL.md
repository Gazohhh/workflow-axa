---
name: grilling
description: "Find the decisions nobody mentioned, after reading the code. Use through workflow-clarify or to stress-test a plan. Asks only choices that change behavior, scope, safety or compatibility."
---

Find the decisions nobody mentioned and reach a shared understanding with the user. Map this as a **design tree**: every decision branches into the decisions that hang off it.

`workflow-clarify` runs this as its step 2; any phase that finds a new consequential choice comes back here for that branch only.

## When

Grill for every new substantive goal and every material change, even when the prompt is detailed or the owner obvious. Skip it for lightweight edits, explanations and single access questions. If the user says "no interview", record that and offer labeled options instead of deciding protected matters yourself.

When everything is settled, ask none and record why; there is no minimum question count or round limit.

**Ask only what the user must decide**: choices that change product intent (what users get or notice), architecture (a new dependency, interface, data shape or owner), risk (safety, permissions, compatibility) or an irreversible outcome (deleted or migrated data). Settle each plain engineering choice yourself: follow the project's convention, or pick one and state it as an assumption the user can reject at the agreement.

## Before the first round

Finding _facts_ is your job, never the user's. Research first. Derive questions from `workflow-clarify` journeys, not a checklist, and settle whatever code, tests and docs already answer. Research directly; use a subagent only when one is permitted and useful. A lookup still running is an unsettled prerequisite: only the questions that depend on it wait.

### Sort what you found

| Item | What it is | Settled by |
|---|---|---|
| **Fact** | How things work today | Code, command output, primary docs. Look it up yourself; ask only when a needed fact is inaccessible, saying what you checked |
| **Requirement** | Behavior the user asked for | The user's words or a recorded answer |
| **Assumption** | A belief not yet confirmed | Stated in the agreement so the user can reject it |
| **Open choice** | A user decision that changes what gets built | A numbered question (How to ask); never an option the rules forbid (for UI: new CSS) |
| **Recommendation** | Your proposal | Never counts as a decision |
| **Delegated detail** | An implementation choice inside agreed scope that nobody using the product could notice | Project convention, a recorded delegation, or a stated assumption |

A change to what users already see (layout, spacing, wording, timing, defaults), or a visible detail of new output that product intent, risk or an agreed result depends on, is an open choice, never a delegated detail or a stated assumption, unless a decision, approved policy or explicit bounded delegation already settles it; other new-output details are plain engineering choices. Record each choice you made in DECISIONS marked `by: agent`.

Code shows current behavior, not intent. A diagram, silence or a half-answered batch is not a decision. A behavior the request deliberately changes is the point of the work; an unexplained conflict between request, code and docs is a question.

Before asking, check standing answers: earlier DECISIONS and AGENTS.md "Standing answers". Don't ask again what the user already settled for good; when they say "always", offer to record it there.

## Rounds

Work the tree in **rounds**. The **frontier** is every open choice whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the frontier in one round, grouping related questions, then wait for the answers. Each answer reshapes the tree: settled decisions unblock the questions that depended on them, so recompute the frontier for the next round. A question whose answer depends on another question still open in this round belongs to a later round. Ask early, and pause dependent work, when the answer changes what is safe or useful next; label immaterial unknowns instead of inventing values.

### How to ask

Every decision question is multiple choice with two to four options, lettered in order; recommend by letter ("Recommended: a"); the user may answer in their own words. Number each question and word it so "yes" accepts your recommendation:

```
❓ **Q1** - **<question title>**: <what happens today, what depends on the answer>
a. <option>  b. <option>

➡️ Recommended: a, <its trade-off>
```

Ask a fact or access request plainly, and DESIGN.md rule 4's question in its exact wording, with its same-tag list and no recommendation. Ask through the host's structured multiple-choice question tool when it has one, otherwise as the same lettered list in chat, never in the background, where answers can't reach it. Write each question for someone new to the project (`../workflow/WRITING.md`).

## Break it before stopping

An empty frontier means no *known* question remains. For each journey, name one realistic input, state or caller that would make the draft wrong: a second caller, empty or huge data, old saved data, a permission edge, an interrupted run, concurrent use. Settle each with a fact, a requirement, a stated assumption or a new question.

For complex work, cover actor/caller, outcome, failure, state/timing, compatibility, and decision source. Mark unexamined material paths open. For a simple change, one break-it note suffices.

**Stop when all hold**:

- every journey has an observable result for success and its relevant failures;
- every caller and compatibility dependency found belongs to a journey or is explicitly excluded;
- every choice blocking the next work is answered, delegated with limits, or deferred by the user;
- the break-it pass left nothing material open.

Escalate instead of looping when only the user can decide, two rounds bring nothing new, a capability is missing or the budget is reached. Research may end with open choices written down; implementation may not.

## Record answers

The task owner saves answers as they arrive, so a partial reply survives an interruption: a short decision check in FINDINGS (journey or area, item, answer and source, or open question) and material choices in DECISIONS. Save every open question **before you send it, with its exact options, letters and recommendation**, so a later session can read a reply like "Q1 a" without the chat. Changed a question while writing? Update the saved copy first: saved and sent options and recommendations match exactly. No transcript and no separate questions file.

A partial reply settles only addressed items. A bare "yes" or "yes to all recommendations" accepts only the recommendations actually shown. A generic "go" settles nothing unshown. A bounded delegation is recorded as a delegation, not as the user picking an option.

## Shared understanding

Don't act on the result until the user confirms the shared understanding: that confirmation is the agreement request in `workflow-clarify` step 4. Don't add an empty "did I understand?" round before it.
