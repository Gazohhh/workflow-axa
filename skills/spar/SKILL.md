---
name: spar
description: "Spar with a fresh Claude and GPT about an idea or a decision until you can choose a next move. You can keep a SPAR.md, then turn it into a workflow plan or not. Only the user starts it; it never implements."
disable-model-invocation: true
---

# Spar

`/spar <idea or decision> [quick|normal|thorough|N|until agreement <cap>] [<A> vs <B>] [keep a SPAR.md|conversation only]` takes an idea or a decision from the owner and spars about it with two independent models until you can choose a next move. /spar settles what and why; `/workflow` plans how. /spar never implements: no application or test changes, tickets or offers.

/spar owns only the sparring and reuses: discovery from `../workflow-clarify/SKILL.md` step 1, architecture and seams from `../codebase-design/SKILL.md`, terms from `../domain-modeling/SKILL.md`, every owner question from `../grilling/SKILL.md`, and the external specialists `research` (outside facts) and `diagnosing-bugs` (a failure), by the qualified name the host shows (`../workflow/SPECIALISTS.md`), only when installed, read-only, and never to fix anything. Read [T3.md](T3.md) and [SPAR-FILE.md](SPAR-FILE.md) now.

**The start card** asks only what the command did not state, in one question card, each choice lettered with a recommendation: the effort, Quick (up to 6 launches) · Normal (up to 10) · Thorough (up to 14) · Until agreement (cap 30, at most the launches left; another cap through Other); the debaters (T3.md "Who debates"); and the record, "Keep a SPAR.md" · "Conversation only". The effort from `spar_default_depth` (`python -X utf8 -I ../workflow/scripts/settings.py show`, with its `spar_notice` if any) is preselected, never used silently. No card when the command states all three. No debater starts before the owner answers.

**Effort** is a budget: quick (openings and 1 exchange), normal (3), thorough (5), or a number of exchanges; standard and deep mean normal and thorough. Each budget has an explicit launch limit: two launches for the openings, two per exchange, and two for one synthesis check. Never go past it without the owner's OK; before spending more, say which open issue it would settle. When the effort word is invalid or unclear, ask the owner.

**Until agreement**. The cap comes from the command or the start card: 20 · 30 · 50 or a number, at least 6, and never more than the owner has left. Until agreement ends only on agreement, deadlock or the cap, the owner's own direction (dissent recorded), a cancel, or a debater that can't continue. Agreement, deadlock (two consecutive exchanges in which neither debater brings new evidence, a new argument or a changed position) and the cap are each reported as itself. Start another exchange only while at least four launches remain; the last two go to a synthesis check of the current best proposal, labelled S<n>, unless both already accepted the same proposal id. Count every launch, failed ones and replacements too. When fewer launches remain than the next step needs, the cap is reached; never past the cap without the owner's OK. A cap limits launches, not money.

## Rules of the spar

The owner decides and judges; the two debaters argue; you moderate, check evidence and never decide for the owner. **No launch whose brief depends on an open owner choice**, and none while continuing would be unsafe.

- **Sort and ask** with grilling (`../grilling/SKILL.md`): its table ("Sort what you found") says what you look up and what only the owner decides, "How to ask" how to ask, and "Record answers" what a reply settles. Research what is objective. Ask each owner choice as soon as it becomes askable, saying who holds the recommendation; never a questionnaire at the end; there is no fixed number of these stops. Each consequential choice ends answered, delegated with limits, deferred by the owner, or blocking; after a deferral only work independent of it continues.
- **Checkpoints.** Show each in a message the owner can read before the question tool opens (`send_to_user` in T3 Code), then ask in plain language and grilling's form ((a)'s open "your view?" excepted):
  - (a) after the openings, always: both opening cases, the disagreement most likely to change the outcome, and an open "your view?". Wait for the owner's view or an explicit "I have no feedback on the openings" before the next launch; that answer clears this pause only, not an open owner choice.
  - (b) each owner choice, as above.
  - (c) the verdict: the exact proposal both debaters accepted, in full, with any remaining dissent.

  Other exchanges show only the progress line. The owner may ask for a pause after every round or waive the optional ones. "Spar with me only" has no debaters, so (a) and (c) don't apply.
- **Waiting.** Ask through the host's question tool or end the turn; silence spends no launches; "carry on" releases an optional pause only.
- **Owner input.** An owner decision binds and goes into the next briefs as a decision. The owner's reasoning, opinions and claims go to both from the first exchange on, never into the opening brief: the debaters say what they change and which objection still stands, and may push back with reasons; a factual claim of the owner is checked like any other.

A credible safety, security or data-loss finding goes to the owner at once, with its evidence and uncertainty.

## 1. Understand

Get the idea in the owner's words: the desired outcome, what makes it hard, and what a useful outcome today would be. Agree 3 to 6 success criteria. Before the openings, run one grilling round on the frontier of unsettled choices that shape the opening brief (outcome, success criteria, boundaries, trade-offs); a settled brief needs no question. With "no interview", show labelled options and leave them open.

Sort what the idea rests on into facts (with their source), assumptions and contradictions (with their evidence). Scale this to the idea's risk, not to the effort. Passing tests show behaviour, not that the architecture is right. A check you run yourself follows the standing diagnostic allowance in `../rule-maker/rules/OPERATIONS.md`, every condition of it; otherwise report the hypothesis and the check it needs.

Show the frame once, as a normal line: **Spar:** <idea> · effort <effort> (at most <n> launches) · <A> vs <B>, where <n> is the cap for until agreement. No debater starts before this line is shown.

## 2. Explore

Brief both debaters with T3.md's opening brief. Both get the same brief, and neither sees the other's opening. Each returns a recommendation and must challenge the framing: doing nothing, a simpler way, or whether the need is real. Each position gets an id: A1, B1, then A2, B2.

Write the options into SPAR.md (or the conversation), each with its strongest honest case and its strongest objection. Then hold checkpoint (a).

## 3. Challenge

Each exchange (T3.md's exchange brief) works on the few disagreements that could change the outcome, not on everything said so far. Use a pre-mortem when it helps: the idea failed; why?

Then you coordinate:

- check the cited evidence yourself before an objection counts as settled;
- agreement without evidence is not agreement: send the gap back in the next brief;
- write What changed our thinking, Open questions and dissent into SPAR.md (or the conversation);
- show one plain progress line: Round <n>/<budget or cap>: <what moved>. In T3 Code, send it with `send_to_user` or end the turn with it.

You keep the working proposal. You may write a synthesis, labelled "coordinator's synthesis"; a synthesis gets the id S1, S2 and so on. When the budget allows, both debaters assess it with T3.md's synthesis brief. An unreviewed synthesis stays labelled unreviewed, and objections to it stay visible.

## 4. Decide

Name the uncertainty most likely to change the decision, the cheapest credible test for it, and the observation that would change the recommendation. When none remains, write "no material uncertainty".

A bounded effort ends when the owner can choose a next move (proceed, investigate, defer or abandon) or its budget is spent; until agreement ends as above. Agreement: both debaters and the owner accepted the exact text of the same proposal id, without conditions or blockers. Once both debaters accepted it, hold checkpoint (c), even when the last launches are spent; it costs no launch. Until the owner answers, report "both debaters accepted; the owner's verdict is pending". The owner may instead choose a direction over both debaters, with their dissent recorded. An owner rejection records the objection and starts another exchange only with a concrete issue and at least four launches left. An accept with amendments rejects that version. Any later edit voids the acceptance: the edit is an unreviewed synthesis, the last version the debaters accepted is kept, and the owner's verdict is asked again. Disagreement may remain: report it with each side's reasons, and never fake agreement. A spent budget gives a partial conclusion and a recommended next move.

A cancel stops the debaters and asks nothing more (`task_cancel` in T3 Code; a later result is ignored).

## 5. Conclusion and handoff

Show the conclusion first (SPAR-FILE.md "The conclusion"), written as `../workflow/WRITING.md` says. Then ask one question: "Turn this into a workflow plan" · "Investigate <the uncertainty> first" · "Continue sparring" · "Leave it here".

- **Turn this into a workflow plan**: after a conversation-only spar, write SPAR.md first, since the plan links it. Outside a task: start `/workflow` with a new task in `docs/plans/` whose PLAN links the SPAR.md revision; it takes its Approach from the Handoff brief. During a task (SPAR-FILE.md "Where it lives"): continue that task's workflow-clarify with the Handoff brief, and change its checkpoint only as SPAR-FILE.md says. Assumptions stay assumptions. This authorizes planning only.
- **Investigate first**: write a bounded investigation brief into SPAR.md (in the conversation when conversation only): what to check, how, its cost, and which result changes what; running it needs its own approval.
- **Continue sparring**: ask for more effort or a new cap with the start card's choices; an effort's launches come on top of those spent, a cap counts every launch so far; show a new frame line, then go on. A new cap must exceed the launches used.
- **Leave it here**: SPAR.md stays as it is.
