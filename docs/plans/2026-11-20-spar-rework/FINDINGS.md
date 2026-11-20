# Findings

## Journeys
- J1 The owner runs /spar in T3 Code (GPT vs Claude through delegate_task). Owner: skills/spar/SKILL.md, T3.md and SPAR-FILE.md. Today it shows a start card, a frame, a pause after the openings, owner choices one at a time, exchanges, a synthesis check, an exact-text verdict, the conclusion and the handoff question. Failure paths: a debater fails (T3.md menu), cancel, the budget is spent, a send_to_user message over 4,000 characters is refused (seen 2026-11-19).
- J2 The owner runs /spar without T3 (the Claude CLI): single-model helpers through the host subagent. Baseline replay: the helpers agreed from their openings in both cases.
- J3 Spar handoff: "Turn this into a workflow plan" leads to workflow-clarify step 3, which reads the SPAR.md Handoff brief and its Owner decisions (workflow-clarify/SKILL.md step 3; grilling "Record answers" names SPAR.md).
- J4 Every skill that writes to the owner reads skills/workflow/WRITING.md. 36 skill files point to it, the router among them (workflow/SKILL.md:8).
- J5 Settings: settings.py maps standard/deep to normal/thorough (OLD_DEPTHS, line 36); unchanged.
- J6 The approval hook lets docs/spar/<date-topic>/SPAR.md be written without an offer (tests/test_approval_hook.py:1275); unchanged.

## Evidence
- E1 Readers of the changed text:
  - tests/test_spar.py: pins wording; the exact-text pins are at 240-246, and test_r44 is at 248.
  - tests/test_owner_questions.py:66-74 and 133-137: pins the grilling and SPAR-FILE wording.
  - tests/test_owned_skills.py:60-69: grilling "Record answers".
  - tests/test_writing_mentions.py:77: files that must mention WRITING.md.
  - tests/test_simple_english.py:126.
  - tests/behavioral/spar.json: 482 lines.
  - docs/RULE-CONTRACTS.md:126: the /spar row says "exact text".
  - tools/validate.py: reads CONTEXT.md, counts and versions.
- E2 The baseline replay ($7.43): SPAR.md revision 9, "Baseline replay results". Traces are in .artifacts/2026-11-19-architecture-review/.
- E3 The main checkout moved to 8a56c42 (2.10.0). Its diff from 3972094 is release records and version strings only.

## Safety assumptions
- S-none-outside: the change touches no script, hook or schema. Its readers are the tests listed in E1 and the agent instructions that point to WRITING.md. Check: the full suite plus validate.

## Owner request during execution
- Q-grill (owner, 2026-11-20): "check if the grilling still works". Added to the T5 live test as one more check within the same $20 cap: a decision-gap fixture case (create_fixture.py --scenario decision-gap), run on both the baseline and the candidate. Existing evidence from the baseline replay: the history-screen case asked two grilling questions; the separator case asked none and stated one rejectable assumption instead.

## Checks
- V1 (T1) Red: test_simple_english.test_a_label_follows_its_meaning_in_every_owner_message failed before the edit (AssertionError: not found). Green after: test_simple_english 14 OK, test_owner_questions 13 OK, test_writing_mentions 4 OK, validate PASS (worker report; files: skills/workflow/WRITING.md "Chat replies" rule 7, the line-136 example, skills/grilling/SKILL.md:54 pointer, tests/test_simple_english.py).
- V2 (T4) Count of tests/test_verify_skills.py text pins (377 counted with loop items, lines 25-577): 162 guard a contract, 84 guard rewritable wording, 131 unclear; 67 of the 84 are in ReproduceBugOrder (lines 57-189). Report only, no change.
- V3 (grilling check, baseline 3972094, $0.99): the decision-gap prompt (Low and High beside Auto, apply immediately) left open whether the choice survives a restart. The agent asked no question, decided "memory for this process only" itself, and put it in the offer. Grilling says state/timing is an open choice for the user, and cases.json B02 expects it asked. Result: FAILED on baseline. A fix is outside offer #2 (grilling behaviour), so it goes to the owner as a new decision.
- Baseline suite: the first run lost its unittest summary (tail cut); rerun on a clean 3972094 tree into .artifacts/2026-11-19-architecture-review/suite-baseline.txt.

- V4 Baseline suite on a clean 3972094 extract (no .git): 1696 tests, 4 errors, 15 skipped. All 4 errors need git in the tree: test_cutover.RollbackToRc39 (git archive bfc18fd) and three test_writing_mentions.OldFileMentions tests (git calls). They count as environment-only errors; the candidate suite runs inside the worktree, where git is present. Output: .artifacts/2026-11-19-architecture-review/suite-baseline.txt

- V5 (T2) Red on the old text: test_spar 48 tests, 58 failures; test_owner_questions 1 failure. Green after: test_spar 48 OK, test_owner_questions 13 OK, test_owned_skills 13 OK, test_settings 9 OK, test_writing_mentions 4 OK, test_simple_english 14 OK, test_package_contract 9 OK, validate PASS (worker report).
  - Words before and after: SKILL.md 1,691 to 1,677; T3.md 1,171 to 1,060; SPAR-FILE.md 712 to 737; 3,574 to 3,474 in total. Far above the estimates (about 2,400), because kept rules are pinned word for word by tests. Size ceilings are set to 1700, 1100 and 760.
  - Builder choices for review: start-card launch limits 6/10/14 become 4/8/12 (no synthesis check); the owner verdict is asked in the same card as the handoff question.
- Review S1: fresh subagent (independent) pending: T1 and T2 diff (writing-for-agents + AUDIT, Spec against R1-R9)

- Review S1: fresh subagent (independent) failed: T1 and T2 diff. Defect 1: the conclusion could state the owner's agreement before the combined verdict card. Defect 2: a fully stated command skipped the success criteria. Notes: per-point deadlock, owner claims in the opening brief, the RULE-CONTRACTS and tests/README rows. Launch limits 4/8/12 follow the agreement; the combined verdict plus handoff card is an owner decision, kept as an assumption the owner can reject.
- Repairs: SPAR-FILE.md conclusion item 1 (pending, never the owner's agreement); SKILL.md card skip rule, per-point deadlock, owner claims from the first exchange on; tests/test_spar.py has three new tests and moved pins; test_spar 51 OK.
- T3 docs: docs/RULE-CONTRACTS.md spar and WRITING rows, tests/README.md /spar section.
- Review S2: same subagent (independent) pending: repairs plus T3 docs

- Review S2: same subagent (independent) passed: repairs and T3 docs; two README wording notes applied (tests/README.md:151 "and of the later reworks below", :153 the start-card wording).

- V6 (T5) Live after-test on the candidate (release ZIP 9206687ca1ec): the same prompts, fixtures and flags as the baseline (3972094, ZIP b04d9ec177c5); Claude CLI 2.1.327, Opus 5.5, plugin only. Traces are after-*.jsonl in .artifacts/2026-11-19-architecture-review/. One run per case.

  | Case | Before | After |
  |---|---|---|
  | Explain-only | no skill, nothing written, $0.37 | no skill, nothing written, $0.17 |
  | Separator change | feature recipe, offer, no code, $0.74 | feature recipe, offer, no code, $0.85 |
  | History screen with saved data | feature + Compatibility, 2 grilling questions, $0.57 | feature + Compatibility, 2 grilling questions, $0.65 |
  | Changed rule on resume | revision, new offer, no code, $0.99 | resume, then a new offer for the changed scope, no code, $0.70 |
  | Grilling check (decision gap) | 0 questions; restart retention decided silently in the offer, $0.99 | 2 questions; restart retention stated as an assumption you can reject, not asked, $0.57 |
  | Spar A: stops before the first exchange | 3 (card, pause, a separate owner choice); 5 replies in all; no exchange, straight to a synthesis | 2 (card, pause with the choices); 3 replies in all; one real exchange |
  | Spar B: stops before the first exchange | 3; 6 replies in all | 2; 3 replies in all |
  | Spar cost | A $1.24, B $1.59 | A $1.38, B $1.26 |
  | Fake "both agree" | 0 | 0. Where the details differed: "Not labelled, because each debater adds a different detail" |
  | The owner's unchecked claim ("users keep asking") | adopted: both moved "later" to "now" on it | held out of the openings, marked "not yet checked", then "Neither helper could find any trace of it in the repo"; the helpers moved on the owner's concrete answers |
  | Single-model warning | none | shown on the start card |
  | Labels without their meaning (owner text) | 1 minor ("S1 is agreed" before its meaning) | 0 found by the reader. Verbatim debater quotes keep "DP1" inside the quotes |
  | Writes before approval | 0 | 0 (git status: only docs/plans records) |

  Safeguards: no regression found. Limits:
  - one run per case;
  - the CLI, not T3, so single model only;
  - the failed-send and restatement-at-the-last-exchange cases were not provoked;
  - the grilling difference has n=1 per side and may be chance (the T1 change to grilling is only a pointer).

  One minor wording point: spar B's last line says "you, Helper A and Helper B all agree", while helper A answered one point "mis-framed". Both still recommended the same build.
- Live-test spend: before $7.43; after-run $5.59; grilling baseline $0.99. Total $14.01 of the $20 cap.
- V7 Full suite on the candidate in the worktree: 1706 tests, OK (14 skipped). validate PASS. The two README wording notes were applied after this run, and validate passes after them.

- Whole-feature review: S1 (T1 and T2) and S2 (repairs and T3 docs) together cover every changed file in its current form. The one exception is the later T5 records change in tests/behavioral/spar.json: results and evidence for six cases, checked by test_spar (51 OK) and validate PASS.
- Blind check prepared: .artifacts/2026-11-19-architecture-review/blind-X.md and blind-Y.md (spar B conclusions before the verdict; the key is kept outside the repo until the owner picks).
- Cleanup not done: the removal safety check refused rm -rf D:/axa-replay-2026-11-19 (fixtures, plugin copies, ZIPs, the base-tree extract; all this task's disposable output). The owner can delete that folder by hand.

- Review S3: same subagent (independent) failed: the whole diff passes except three live results in tests/behavioral/spar.json recorded as OBSERVED without full evidence (one-model, same-model-helpers, budget-spent). Repaired to PARTIAL with what was not exercised; incompatible-agree evidence now cites the after-sb-4 counter-observation; test_spar OK.
- Review S4: same subagent (independent) pending: tests/behavioral/spar.json repair

- Review S4: same subagent (independent) passed: the tests/behavioral/spar.json repair.

- Review S5: same subagent (independent) passed: the ten files other than spar.json, unchanged since the S3 snapshot. S3 judged them as a whole, in its words "The skill text, the tests and the docs pass as one change"; S3 failed only on spar.json, which S4 passed. No new review ran; this line records S3's verdict on those files, file by file.

- Owner acceptance result (T5 human check): "don't know" (D3). An inconclusive opinion; the measured results in V6 stand on their own.
