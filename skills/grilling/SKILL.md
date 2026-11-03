---
name: grilling
description: "Grill the user relentlessly about a plan, decision, or idea. Use when the user wants to stress-test their thinking, or uses any 'grill' trigger phrases."
---

> Bundled with workflow-axa from [mattpocock/skills](https://github.com/mattpocock/skills) `skills/productivity/grilling/SKILL.md` at `4ae2317`, MIT ([LICENSE](LICENSE)). The upstream text below is unchanged; the **workflow-axa adaptation** at the end overrides it where they conflict.

Interview the user relentlessly until you reach a shared understanding. Map this as a **design tree**: every decision branches into the decisions that hang off it.

Work the tree in **rounds**. The **frontier** is every decision whose prerequisites are already settled: the questions you can ask _now_ without guessing at answers you haven't heard yet. Ask the whole frontier in one round: number each question and give your recommended answer. Then wait for the user's answers before the next round.

Format a round like so:

```
❓ **Q1** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>

---

❓ **Q2** - **<question title>**: <question body, might be multiple paragraphs, including multiple choices>

➡️ <your recommended answer>
```

Word each question so "yes" accepts your recommended answer.

Each round the user answers reshapes the tree: settled decisions push the frontier outward and unblock questions that depended on them. Recompute the frontier and ask the next round. A question whose answer depends on another question still open in this round belongs to a _later_ round, not this one.

Finding _facts_ is your job, never the user's. When a frontier question needs a fact from the environment (filesystem, tools, etc.), dispatch a sub-agent with a fresh context window to find it; don't ask the user for anything you could look up yourself. Don't block on it: a running exploration is an unsettled prerequisite, so only the questions downstream of it wait for the sub-agent to report; ask the rest of the frontier now. The _decisions_ are the user's: put each to them and wait.

The session is done when the frontier is empty: every branch of the design tree visited, nothing left silently assumed. Do not act on it until the user confirms you have reached a shared understanding.

---

## workflow-axa adaptation

The text above is the method. These rules add to it, and win where they differ. `workflow-clarify` runs this as its step 2; any phase that finds a new consequential choice comes back here for that branch only.

### When

Grill for every new substantive goal and every material change, even when the prompt is long or the code owner looks obvious: the point is finding the decisions nobody mentioned. Skip it for lightweight edits, explanations and single access questions. If the user says "no interview", record that and offer labelled options instead of deciding protected matters yourself.

A complete request may need no questions: record why the choices are settled; there is no minimum question count and no round limit.

### Before the first round

Questions come from the journeys `workflow-clarify` step 1 traced, not from a checklist. Don't ask a question whose answer depends on a caller you haven't traced yet; the trace often makes it moot. Ask direction, access or safety blockers at once and keep tracing the rest.

### Sort what you found

| Item | What it is | Settled by |
|---|---|---|
| **Fact** | How things work today | Code, command output, primary docs. Look it up yourself; ask only when a needed fact is inaccessible, saying what you checked |
| **Requirement** | Behavior the user asked for | The user's words or a recorded answer |
| **Assumption** | A belief not yet confirmed | Stated in the agreement so the user can reject it |
| **Open choice** | A user decision that changes what gets built | A numbered question with options and a recommendation; never an option the rules forbid (for UI: new CSS) |
| **Recommendation** | Your proposal | Never counts as a decision |
| **Delegated detail** | An implementation choice inside agreed scope that nobody using the product could notice | Project convention or a recorded delegation |

Anything a user could see or notice that differs from before this change (layout, spacing, wording, timing, defaults) is an open choice, never a delegated detail, unless an existing decision, approved policy or an explicit bounded delegation from the user already settles it. Record each choice you made yourself in DECISIONS marked `by: agent`; delivery lists them.

Code shows current behavior, not intent. An earlier agent proposal, a diagram, silence or a half-answered batch is not a decision. A behavior the request deliberately changes is the point of the work; an unexplained conflict between request, code and docs is a question.

Before asking, check standing answers: earlier DECISIONS and any "Standing answers" the project keeps in AGENTS.md. Don't ask again what the user already settled for good; when they say "always", offer to record it there.

### How to ask

Ask through the host's structured multiple-choice question tool when it has one, otherwise in chat; never run an interview in the background where answers can't reach it. Write each question for someone new to the project (`../workflow/WRITING.md`): what happens today, the options, your recommendation and its consequence, and what depends on the answer. Ask early, and pause dependent work, when the answer changes what is safe or useful next; batch choices that can wait; label immaterial unknowns instead of inventing values.

### Break it before stopping

"Frontier empty" means no *known* question remains. For each journey, name one realistic input, state or caller that would make the draft wrong: a second caller, empty or huge data, old saved data, a permission edge, an interrupted run, concurrent use. Settle each with a fact, a requirement, a stated assumption or a new question.

**Stop when all hold** (this replaces "the frontier is empty"):

- every journey has an observable result for success and its relevant failures;
- every caller and compatibility dependency found belongs to a journey or is explicitly excluded;
- every choice blocking the next work is answered, delegated with limits, or deferred by the user;
- the break-it pass left nothing material open.

Escalate instead of looping when only the user can decide, two rounds bring nothing new, a capability is missing or the budget is reached. Research may end with open choices written down; implementation may not.

### Record answers

The task owner saves answers as they arrive, so a partial reply survives an interruption: a short decision check in FINDINGS (journey or area, item, answer and source, or open question) and material choices in DECISIONS. Save every open question **before you send it, with its exact options, letters and recommendation**, so a later session can read a reply like "Q1 a" without the chat. Changed a question while writing the message? Update the saved copy first: saved and sent options and recommendations match exactly. No transcript and no separate questions file.

A partial reply settles only addressed items. "Yes to all recommendations" settles the ones actually shown. A generic "go" settles nothing unshown. A bounded delegation is recorded as a delegation, not as the user picking an option.

### Shared understanding

"Confirm you have reached a shared understanding" is gate one: the agreement summary in `workflow-clarify` step 4. Don't add an empty "did I understand?" round before it. Finishing the interview confirms nothing and never authorizes code.
