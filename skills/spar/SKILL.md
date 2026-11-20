---
name: spar
description: "Spar with a fresh Claude and GPT about an idea or a decision until you can choose a next move. You can keep a SPAR.md, then turn it into a workflow plan or not. Only the user starts it; it never implements."
disable-model-invocation: true
---

# Spar

`/spar <idea or decision> [quick|normal|thorough|N|until agreement <cap>] [<A> vs <B>] [keep a SPAR.md|conversation only]` takes an idea or a decision from the owner and spars about it with two independent models until you can choose a next move. /spar settles what and why; `/workflow` plans how. /spar never implements: no application or test changes, tickets or offers.

/spar owns only the sparring and reuses: discovery from `../workflow-clarify/SKILL.md` step 1, architecture and seams from `../codebase-design/SKILL.md`, terms from `../domain-modeling/SKILL.md`, every owner question from `../grilling/SKILL.md`, and the external specialists `research` (outside facts) and `diagnosing-bugs` (a failure), by the qualified name the host shows (`../workflow/SPECIALISTS.md`), only when installed, read-only, and never to fix anything. Read [T3.md](T3.md) and [SPAR-FILE.md](SPAR-FILE.md) now.

**The start card** asks only what the command did not state, in one question card, each choice lettered with a recommendation:

- the effort: Quick (up to 4 launches) · Normal (up to 8) · Thorough (up to 12) · Until agreement (cap 30, at most the launches left; another cap through Other), with `spar_default_depth` (`python -X utf8 -I ../workflow/scripts/settings.py show`, and its `spar_notice` if any) preselected, never used silently;
- the debaters (T3.md "Who debates"). When only one model can debate, the card says that helpers of the same model tend to agree at once;
- the record: "Keep a SPAR.md" · "Conversation only";
- 3 to 6 proposed success criteria, which "yes" accepts;
- only the open choices that shape the opening brief (outcome, boundaries, trade-offs): a settled brief needs no question, and with "no interview", show labelled options and leave them open.

No card when the command states all three, the success criteria are settled, and nothing that shapes the brief is open. No debater starts before the owner answers.

**Effort** is a budget: quick (openings and 1 exchange), normal (3), thorough (5), or a number of exchanges. One launch rule: two launches per round, the openings included. Count every launch, failed ones and replacements too. That is an explicit launch limit: pass it only with the owner's OK, and before that, say which open issue it would settle. Ask when the effort word is unclear.

**Until agreement** is opt-in: it ends when every decision point is agreed or in deadlock (a point on which two consecutive exchanges brought no new evidence, argument or changed position), at the cap, or by the owner's decision; deadlock and the cap are reported separately. The cap comes from the command or the start card: at least 6, and never more than the owner has left. When fewer launches remain than the next exchange needs, the cap is reached; never past the cap without the owner's OK. A cap limits launches, not money.

## Rules of the spar

The owner decides and judges; the two debaters argue; you moderate, check evidence and never decide for the owner. **No launch whose brief depends on an open owner choice**, and none while continuing would be unsafe. Plain titles for the owner; ids only in the record.

- **Sort and ask** with grilling (`../grilling/SKILL.md`): its table ("Sort what you found") says what you look up and what only the owner decides, "How to ask" how to ask, and "Record answers" what a reply settles. Research what is objective. Ask each owner choice as soon as it becomes askable; never a questionnaire at the end; there is no fixed number of these stops. Each consequential choice ends answered, delegated with limits, deferred by the owner, or blocking; after a deferral only work independent of it continues.
- **Checkpoints.** Show each in a message the owner can read before the question tool opens (`send_to_user` in T3 Code), then ask in plain language and grilling's form:
  - (a) after the openings, always: both opening cases, the disagreement most likely to change the outcome, and an open "your view?", with the decision points; every owner choice that can be asked now is asked in the same message, not one by one afterwards. Wait for the owner's view or an explicit "I have no feedback on the openings" before the next launch; that answer clears this pause only, not an open owner choice.
  - (b) each later owner choice.
  - (c) the verdict, at the ending: the conclusion, then the owner's verdict with the handoff question; it costs no launch.

  Other exchanges show only the progress line. The owner may ask for a pause after every round or waive the optional ones. "Spar with me only" has no debaters, so (a) and (c) don't apply. Ask through the host's question tool or end the turn; silence spends no launches; "carry on" releases an optional pause only.
- **Owner input.** An owner decision binds and goes into the next briefs as a decision. The owner's reasoning and opinions reach both from the first exchange on, never into the opening brief; the debaters say what they change and may push back with reasons. An owner's factual claim goes into the briefs from the first exchange on, marked "not yet checked"; the debaters check it or say they could not.

A credible safety, security or data-loss finding goes to the owner at once, with its evidence and uncertainty.

## 1. Understand and gather the evidence

**Evidence, before the openings.** Gather the facts the idea rests on, outside sources included (yourself, or the `research` specialist when installed), into the existing record: SPAR.md "Evidence", or the chat when conversation only. Then verify the decisive claim yourself before it counts. A claim only a prototype can settle stays open with the observation that would falsify it and the cheapest check, for "Investigate first". Scale this to the idea's risk; passing tests show behaviour, not that the architecture is right. A check you run follows the standing diagnostic allowance in `../rule-maker/rules/OPERATIONS.md`, every condition of it; otherwise report the hypothesis and the check it needs.

Show the frame as a receipt that needs no reply, sent in the same turn as the first launch and before it: **Spar:** <idea> · effort <effort> (at most <n> launches) · <A> vs <B>, where <n> is the cap for until agreement.

## 2. Explore

Brief both debaters with T3.md's opening brief; neither sees the other's opening, and each must challenge the framing: doing nothing, a simpler way, or whether the need is real. Record the options (SPAR-FILE.md) and the decision points: the few disagreements that could change the outcome, as short statements. Then hold checkpoint (a).

## 3. Challenge

Each exchange (T3.md's exchange brief) works on the decision points, not on everything said so far. Use a pre-mortem when it helps: the idea failed; why?

Each debater answers each decision point agree, disagree or mis-framed, and may split a point or add one, with one line in its own words; the conclusion shows both lines quoted verbatim. Label a point "both debaters agree" only when both answered agree to the identical point text and neither quote adds a condition the other lacks; otherwise show the two quotes without a label. To reconcile quotes that look compatible, restate the point and send it back to both, inside an exchange the budget or cap still allows; when none remains, the point stays unresolved. The owner's verdict is separate and always explicit.

Then:

- check the cited evidence yourself before an objection counts as settled;
- agreement without evidence is not agreement: send the gap back in the next brief;
- show one progress line: Round <n>/<budget or cap>: <what moved>. In T3 Code, send it with `send_to_user` or end the turn with it.

Your working proposal is labelled "coordinator's synthesis"; its parts reach the debaters as decision points. An unreviewed synthesis stays labelled unreviewed, and objections to it stay visible.

## 4. Decide

Name the uncertainty most likely to change the decision, and the cheapest credible test for it, or "no material uncertainty".

A bounded spar ends when the owner can choose a next move (proceed, investigate, defer or abandon); dissent is a valid ending. Otherwise a cancel, a provider failure and a spent budget are each reported as themselves; a spent budget gives a partial conclusion and a recommended next move. The owner may instead choose a direction over both debaters, with their dissent recorded. An owner rejection records the objection and starts another exchange only with a concrete issue and launches left for it. Disagreement may remain: report each side's reasons, and never fake agreement.

A cancel stops the debaters and asks nothing more (T3.md "Launching and waiting").

## 5. Conclusion and handoff

Show the conclusion first (SPAR-FILE.md "The conclusion"), written as `../workflow/WRITING.md` says. Then ask one question card: the owner's verdict (accept the recommendation, or choose another direction) and the next move; only after the answer does SPAR.md say "agreed by both debaters and the owner". The next moves: "Turn this into a workflow plan" · "Investigate <the uncertainty> first" · "Continue sparring" · "Leave it here".

- **Turn this into a workflow plan**: after a conversation-only spar, write SPAR.md first, since the plan links it. Outside a task: start `/workflow` with a new task in `docs/plans/` whose PLAN links the SPAR.md revision; it takes its Approach from the Handoff brief. During a task (SPAR-FILE.md "Where it lives"): continue that task's workflow-clarify with the Handoff brief, and change its checkpoint only as SPAR-FILE.md says. Assumptions stay assumptions. This authorizes planning only.
- **Investigate first**: write a bounded investigation brief into SPAR.md (in the conversation when conversation only): what to check, how, its cost, and which result changes what; running it needs its own approval.
- **Continue sparring**: ask for more effort or a new cap with the start card's choices; an effort's launches come on top of those spent, a cap counts every launch so far; show a new frame line, then go on. A new cap must exceed the launches used.
- **Leave it here**: SPAR.md stays as it is.
