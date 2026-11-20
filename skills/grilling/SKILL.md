---
name: grilling
description: "Find the decisions nobody mentioned, after reading the code. Use through workflow-clarify or to stress-test a plan. Asks only choices that change behavior, scope, safety or compatibility."
---

Find the decisions nobody mentioned and reach a shared understanding with the user. Map this as a **design tree**: every decision branches into the decisions that hang off it.

`workflow-clarify` runs this as its step 2; any phase that finds a new consequential choice comes back here for that branch only.

## When

Grill for every new substantive goal and every material change, even when the prompt is detailed. Skip it for lightweight edits, explanations and single access questions. If the user says "no interview", record that and offer labeled options instead of deciding protected matters yourself. When everything is settled, ask none and record why; there is no minimum question count.

**Ask only what the user must decide**: choices that change product intent (what users get or notice), architecture (a new dependency, interface, data shape or owner), risk (safety, permissions, compatibility) or an irreversible outcome (deleted or migrated data). Settle each plain engineering choice yourself: follow the project's convention, or pick one and state it as an assumption the user can reject.

## Before asking

Finding _facts_ is your job, never the user's. Derive questions from the `workflow-clarify` journeys and settle whatever code, tests and docs already answer. Check standing answers (earlier DECISIONS, AGENTS.md "Standing answers") and never ask again what the user settled for good; when they say "always", offer to record it there.

### Sort what you found

| Item | What it is | Settled by |
|---|---|---|
| **Fact** | How things work today | Code, command output, primary docs. Ask only when it is inaccessible, saying what you checked |
| **Requirement** | Behavior the user asked for | The user's words or a recorded answer |
| **Assumption** | A belief not yet confirmed | Stated in the agreement or offer so the user can reject it |
| **Open choice** | A user decision that changes what gets built | A numbered question (How to ask); never an option the rules forbid (for UI: new CSS) |
| **Recommendation** | Your proposal | Never counts as a decision |
| **Delegated detail** | An implementation choice inside agreed scope that nobody using the product could notice | Project convention, a recorded delegation, or a stated assumption |

A change to what users already see (layout, spacing, wording, timing, defaults), or a visible detail of new output that product intent, risk or an agreed result depends on, is an open choice, never a delegated detail or a stated assumption, unless a decision, approved policy or explicit bounded delegation already settles it. Record each choice you made in DECISIONS marked `by: agent`, or, with no task records, when writes aren't allowed or during `/spar` (as Record answers says), state it there instead; during `/spar` it is a coordinator recommendation or an assumption, never an Owner decision.

Code shows current behavior, not intent. A behavior the request deliberately changes is the point of the work; an unexplained conflict between request, code and docs is a question. A diagram, silence or a half-answered batch is not a decision.

### Break it

Before the round, for each journey name one realistic input, state or caller that would make the draft wrong: a second caller, empty or huge data, old saved data, a permission edge, an interrupted run, concurrent use. Settle each with a fact, a requirement or a stated assumption; only a choice the user must make becomes a question in the round. The pass is silent: its notes go to FINDINGS, and the user sees only the questions it adds. For complex work cover actor/caller, outcome, failure, state/timing, compatibility and decision source; for a simple change one note suffices.

## One round

The **frontier** is every open choice whose prerequisites are settled. Ask the whole frontier in one round, each question with your recommendation, and wait. A second round holds only questions whose options depended on those answers. A lookup still running holds back only the questions that depend on it. Label immaterial unknowns instead of inventing values.

### How to ask

Every decision question is multiple choice with two to four options, lettered in order; recommend by letter ("Recommended: a"); the user may answer in their own words. Number each question and word it so "yes" accepts your recommendation:

```
❓ **Q1** - **<question title>**: <what happens today, what depends on the answer>
a. <option>  b. <option>

➡️ Recommended: a, <its trade-off>
```

The title and first sentence carry the meaning: what the owner decides and what each answer does. Codes follow `../workflow/WRITING.md` "Chat replies" rule 7, so the question still makes sense with every code removed.

A fact or access request is asked plainly, without options, and DESIGN.md rule 4's question in its exact wording, with its same-tag list and no recommendation; both make sense without codes. Ask through the host's structured multiple-choice question tool when it has one, otherwise as the same lettered list in chat, never in the background. Write each question for someone new to the project (`../workflow/WRITING.md`).

## Stop

Stop when every journey has an observable result for success and its relevant failures; every caller and compatibility dependency found belongs to a journey or is explicitly excluded; every choice blocking the next work is answered, delegated with limits, or deferred by the user; and the break-it pass left nothing material open.

Escalate instead of looping when only the user can decide, a round brings nothing new, a capability is missing or the budget is reached. Research may end with open choices written down; implementation may not. The user confirms the shared understanding through the agreement request (`workflow-clarify` step 4) or, for one-ticket work, the offer; ask no separate "did I understand?" round.

## Record answers

During `/spar`, questions and answers go into its SPAR.md (Owner decisions; open ones in Open questions), as `../spar/SPAR-FILE.md` says; a "conversation only" spar keeps them in the conversation. Outside `/spar`, when there are no task records or writes aren't allowed (an Inspect request), nothing is written: the questions, with their exact options, letters and recommendation, the answers and their sources stay in the conversation, and a pending question is repeated unchanged. Otherwise (not `/spar`):

Save answers as they arrive: a short decision check in FINDINGS (journey or area, item, answer and source, or open question) and material choices in DECISIONS. Save every open question **before you send it, with its exact options, letters and recommendation**, so a later session can read a reply like "Q1 a" without the chat; saved and sent options and recommendations match exactly. No transcript and no separate questions file.

A partial reply settles only addressed items. A bare "yes" or "yes to all recommendations" accepts only the recommendations actually shown. A generic "go" settles nothing unshown. A bounded delegation is recorded as a delegation, not as the user picking an option.
