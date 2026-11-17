# Decisions

- D1 (by: user, 2026-11-17) Q1 a: a new user-invoked skill `/spar` that owns only the cross-model debate and plugs into `workflow-clarify`; grilling, the agreement and the handoff are reused.
- D2 (by: user, 2026-11-17) Q2 a: without GPT through T3, use a fresh Claude subagent labelled "same model, fresh context".
- D3 (by: user, 2026-11-17) Q3 a: only the owner starts it by typing `/spar`; the workflow may recommend it for high-stakes work, never runs it.
- D4 (by: user, 2026-11-17) Q4 a: the result goes into the task's agreement in PLAN.md as an "Approach" part (chosen approach, rejected alternatives and why, trade-offs, risks, open decisions); the debate rounds go to FINDINGS.

- D5 (by: user, 2026-11-17) Q5 a: always two fresh debaters, a fresh Claude subagent and GPT; the coordinator only frames, compares and records.
- D6 (by: user, 2026-11-17) Q6 a: until-agreement has no pauses and no ceiling: a progress line per round; it stops on no progress, repeated arguments, missing evidence, an open owner decision or the owner's stop. Custom N gives a budget when wanted.
- D7 (by: user, 2026-11-17) Q7 a: without GPT through T3, a fresh helper of the host's own model, labelled "single model, fresh context, not cross-model" (extends D2 to any host, Codex included).
- D8 (by: user, 2026-11-17) Q8 a: the blind opening always runs; depth counts the exchanges after it (quick 1, standard 3, deep 5, N, until-agreement); default standard, saved as `spar.default_depth` in ~/.workflow-axa/settings.json through settings.py; the invocation overrides it without saving.

- D9 (by: user, 2026-11-17) Agreement 2 agreed with four additions: the coordinator is neutral but active (validates objections itself, challenges unsupported consensus, prevents premature agreement); foundation checks separate verified facts, unverified assumptions and contradictions, passing tests don't prove the architecture right, and refactoring or investigation is recommended when needed; research and foundation checking scale with the decision's complexity and risk, independently of the debate depth; tests cover false consensus, stagnation, unresolved objections, missing GPT integration and a questionable existing architecture, not only the happy path. Keep the skill small and composable (Matt Pocock and pstack philosophy), no extra abstractions or duplicated skills. Proceed with the detailed plan; no implementation before that plan is approved. Owner's words: "I approve agreement 2 with three final adjustments … Incorporate these changes into agreement 2 and proceed with the detailed implementation plan. Do not implement until I approve that plan."

- D10 (by: user, 2026-11-17) Answer to Q9, neither a nor b: /spar is an interactive sparring skill, not a decision engine, and the owner is the third participant. Research and verify objective technical questions; challenge the assumptions of both models; when requirements, priorities, trade-offs or acceptable risk are unclear, grill the owner instead of guessing; never refactor questionable architecture automatically, present the evidence and alternatives and involve the owner when the choice changes scope or priorities; don't dismiss unresolved objections, separate technical disagreements from the owner's decisions; before declaring stagnation, check whether a targeted owner question could unblock the debate; when GPT is unavailable, ask the owner how to proceed instead of substituting another model. Tests check the decision process, not predetermined conclusions: the skill recognises uncertainty, asks relevant questions when needed, uses the answers and revises its position; no forced questions when evidence settles a point, no forced agreement when real disagreement remains. Supersedes D2 and D7 (the automatic same-model fallback becomes a choice the owner makes when GPT is unavailable). Owner's words begin: "I disagree with treating the five failure cases as fixed outcomes with predetermined correct answers."

- D11 (by: user, 2026-11-17) Offer #1 (b0b0fa425dd9a16c) answered "Approve from this summary" in the question tool; this also agrees to agreement 3 (the offer says so). The report was recommended and not chosen.

- D12 (by: user, 2026-11-17) After approving offer #1, the owner asked to see the plan before the build ("also let me first see the plan before we build") and asked for the approval-hook bug F1 to be fixed ("That bug needs fixing"). The plan report is built and the offer asked again; F1 becomes a separate task. Note on D9: the owner's words say "three final adjustments" and list three plus one more requirement (the tests), recorded as four additions.

- D13 (by: user, 2026-11-17) After seeing reviews/plan-r1.html, the owner answered offer #1 again: "Approve from this summary" (question tool, only Approve and Change offered).

- D14 (by: user, 2026-11-17) Offer #2 (aba658ef64337b8b, revising #1 with tests/test_docs_consistency.py and tests/test_ui_design.py) answered "Approve from this summary (Recommended)" in the question tool.

- D15 (by: user, 2026-11-17) T6 batch 1 approved: run 1, a real decision at quick depth ("fix the hook bug F2 now or after the next release"), in a T3 Code thread the owner opens on the pilot project, at most 4 debater launches; run 7, the missing-GPT check in a Claude Code CLI session in the same project, no debater launch.

- D16 (by: user, 2026-11-17) After pilot run 1: "It does the sparring but shouldn't it ask to save the spar session / findings … in a document … so I could say workflow continue with this doc if I agree … when done … you can now start the implementation if you want or start a new session", plus "Any more good ideas … together with gpt?" and "You do not have to agree with me; I want both legitimate answers." Then "Yes … continue the spar skill". Agreement 4 additions R15-R24, A6 (FINDINGS S7).

- D17 (by: user, 2026-11-17) Offer #3 (92c59dc67a5d0617, agreement 4, T7-T9) answered "Approve from this summary (Recommended)" in the question tool.

- D18 (by: agent, 2026-11-17, owner to confirm at delivery) Wording of R16, R20 and R21 adjusted after reviews S5/S6: "End sparring" and "End with this result" replace "stop" and "Stop here" (the hook reads those as a stop); a matching task gets a `Spar result <date>` FINDINGS entry instead of a PLAN. Same behaviour; see PLAN "Proposed wording revision".

- D19 (by: agent, 2026-11-17, owner to confirm at delivery) R15 detail: when no debater returned a position (nothing was debated), /spar ends without the save question. Review S7.

- D20 (by: user, 2026-11-17) T6 batch 2 approved ("lets do the live run so you can check its transcript afterwards"), before rc.3: one standalone debate in a new pilot project on the revised candidate, then a second thread that continues from the saved task. Budget after it: at most 6 more debater launches and 2 sessions (totals 10 of 26 and 4 of 8).

- D21 (by: user, 2026-11-17) After run 2a: "I am not happy with it yet. There are still decisions left; where is the sparring saved? and why do I see this on top? The goal is to have a sparring session done with a result: argue together with GPT to see where this could be improved, why and how, and start implementing where needed." Agreement 5 additions R25-R30, A7 (FINDINGS S11).

- D22 (by: user, 2026-11-17) Offer #4 (005f8aa031fc5792, agreement 5, T10) answered "Approve from this summary (Recommended)" in the question tool.

- D23 (by: user, 2026-11-17) Run live test 3 on the agreement-5 candidate before rc.3, testing /spar only (the /workflow continuation is checked after rc.3 is installed, when the duplicate-skill block is gone). Budget after it: at most 16 of 26 debater launches and 4 of 8 sessions.

- D24 (by: user, 2026-11-17) "Isn't it better to have a spar.md instead of the plan.md etc.? There is no structure of what has been sparred, and then asking if you want to turn this into a workflow plan. Spar with GPT; think out of the box. I want the best general sparring skill there is: sparring with agents about an idea to get it into reality." Answers: save SPAR.md automatically (Recommended); the coordinator may give a labelled recommendation (Recommended); rebuild around SPAR.md (Recommended). Agreement 6 (FINDINGS S14). Location docs/plans/<date>-<topic>/ instead of docs/spar/: the approval hook already treats that folder as records, and PLAN.md joins it when the owner turns the spar into a plan.

- D25 (by: user, 2026-11-17) Offer #5 (0f6e53e924cb3fa8, agreement 6, T11) answered "Approve from this summary (Recommended)" in the question tool.

- D26 (by: user, 2026-11-17) "Keep in mind spar has nothing to do with workflow; it's a spar session that could be started for a workflow session; spar is a separate skill used to spar over a new X, for whatever reason." Answer: SPAR.md lives in docs/spar/<date>-<topic>/ (Recommended), with a one-line hook change so docs/spar/<folder>/SPAR.md counts as a record (only that file name, to keep the unapproved-write channel narrow). Revises R31 and R39: a workflow plan made from a spar is a normal task folder in docs/plans/ whose PLAN links the SPAR.md; inside a task, SPAR.md still lives in docs/spar/ and the task's FINDINGS links it. Pilot sessions load the installed hook until the release, so a live run before release must use "conversation only" or accept a refused SPAR.md write.

- D27 (by: user, 2026-11-17) Offer #6 (5702687a64422bb4, agreement 6 revised by D26) answered "Approve from this summary (Recommended)" in the question tool.

- D28 (by: user, 2026-11-17) "This is an option: a spar session does not always have to save a SPAR.md, for example sparring something we will not use, just to see the possibilities. Let the decisions be for the owner." Replaces D24's "save automatically": at the start, unless the command says, /spar asks once "Keep a SPAR.md" · "Conversation only". Choosing "Turn this into a workflow plan" after a conversation-only spar writes SPAR.md first, since the plan links it.

- D29 (by: user, 2026-11-17) Offer #7 (433135148806b10f, D28: SPAR.md is the owner's choice) answered "Approve from this summary (Recommended)" in the question tool.

- D30 (by: user, 2026-11-17) Asked "the spar file only gets created when the user asks about it, not by default?"; after the explanation (it is never created by default; one question at the start), chose "Ask me once at the start": the D28 behaviour stays as built.

- D31 (by: agent, 2026-11-17, owner to confirm at delivery) During a workflow task, "Turn this into a workflow plan" continues that task's workflow-clarify instead of starting a new task, and an agreed task's checkpoint changes only after that choice (review S16, V20). PLAN "Proposed wording revision (D31)".

- D32 (by: user, 2026-11-17) Offer #7 re-presented unchanged after a later owner message (the record-choice question) and approved again: "Approve from this summary (Recommended)".

- D33 (by: user, 2026-11-17) Live test run 4 on the rebuilt candidate before rc.3, in conversation-only mode (the pilot loads the installed rc.2 hook, which would refuse a kept SPAR.md). Budget after it: at most 22 of 26 debater launches and 5 of 8 sessions.

- D34 (by: user, 2026-11-17) After run 4 (thread b49db4cd): "I pressed continue sparring to check if they come up with the same conclusion, because if not what's the point. Also I am not asked at the start how many sessions, and models as well. Choosing endless means don't stop until both agree. Did all this happen?" Not all of it: effort defaulted silently, the coordinator picked the models, until-agreement no longer existed, and S3 was shown as agreed unreviewed. Answers: until agreement stops at a launch cap the owner chooses each time; the start card asks the models with a recommended default; check the changes with GPT first (Recommended).

- D35 (by: user, 2026-11-17) Agreement 7 (FINDINGS S21, Claude and GPT-6.1 Sol agree) answered "Yes, build agreement 7 (Recommended)": start card, until agreement with the owner's cap, strict "agreed", three separate endings, two launches kept for the final check, a cross-maker pair by default, cap options 20/30/50 or the owner's number.

- D36 (by: user, 2026-11-17) "Yes, let's do the live run before release." Run 5 on the agreement-7 candidate, with 20 more debater launches ("20 more (Recommended)"): the T6 cap becomes 46 launches, 25 used before run 5.
