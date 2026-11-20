# /spar rework: argue about ideas, fewer stops, real evidence, every label explained

## Current checkpoint
- Updated / phase: 2026-11-20; closed (delivered; merge and install are the owner's next decision)
- Rules: READY. The AGENTS.md project rules cover the commands, boundaries and approvals. Read: shared START, CORE and READINESS; rules_stamp printed NONE (information only).
- Recipe: docs-tests; modifiers none. Only agent instructions, docs and tests change, and no script behaviour changes. Scope: the task. Classification question: not asked.
- Agreement (gate one): agreed (agreement 1, owner "agree", 2026-11-20)
- Offer: #2 approved (owner, question tool, 2026-11-20; D2)
- Implementation: implemented (T1-T4 verified; T5 live test run, owner pick pending)
- Verification / owner acceptance: suite 1706 OK, validate PASS, live after-test V6 (partial: CLI single model); owner blind pick: no preference (D3)
- Blockers: none
- Changed files: skills/spar/SKILL.md, T3.md, SPAR-FILE.md; skills/workflow/WRITING.md; skills/grilling/SKILL.md; tests/test_spar.py, test_owner_questions.py, test_simple_english.py, behavioral/spar.json, README.md; docs/RULE-CONTRACTS.md
- Next safe action: the owner picks conclusion X or Y (.artifacts/2026-11-19-architecture-review/blind-X.md, blind-Y.md); then merge decision and the grilling follow-up

## Working context
- Owner: Cem. Repository D:/workflow-axa-spar, a git worktree on branch spar/architecture-review at 3972094. The main checkout D:/workflow-axa is never written. Main has since moved to 8a56c42 (2.10.0), which differs from 3972094 only in release records and version strings.
- Linked spar: docs/spar/2026-11-19-architecture-review/SPAR.md, revision 9 (Handoff brief, owner decisions, baseline replay results).
- Test output: .artifacts/2026-11-19-architecture-review/ (git-ignored). The replay fixtures in D:/axa-replay-2026-11-19/ are removed after the after-run is scored.

## Goal and acceptance
/spar helps the owner choose:
- Two AIs disagree and agree on ideas, not on wording.
- Fewer stops.
- A real evidence step.
- Every label shown with its meaning.

The package keeps its architecture. The same replay cases, run before and after the change, prove the result.

## Agreement
Requirements (source: SPAR.md revision 9 Handoff brief, point 12 and the baseline replay; the owner accepted them on 2026-11-19 and 2026-11-20):
- R1 Agreement on ideas: debaters answer each decision point with agree, disagree or mis-framed, in one line of their own words, quoted verbatim. "Both debaters agree" only when both said agree to the identical point and neither quote adds a condition the other lacks. A restatement uses an exchange the budget allows; otherwise the point stays unresolved. Removed: exact-text acceptance, "an accept with amendments is a reject", "any later edit voids the acceptance", the separate synthesis brief and the S-ids.
- R2 Ending: a bounded spar ends when the owner can choose, and dissent is a valid ending. Until agreement stays as an opt-in, slimmed to one rule.
- R3 Stops: one start card (effort, debaters, record, 3-6 success criteria that "yes" accepts, the open choices that shape the opening brief). The frame line is a no-reply receipt. The pause after the openings stays, with no skip setting. Every owner choice that can be asked at that pause is asked in the same message.
- R4 Evidence: an explicit evidence step before the openings, kept in the existing record. The coordinator checks the decisive claim. The owner's factual claims go to the debaters marked "not yet checked".
- R5 Single model: when only one model can debate, the start card says that same-model helpers tend to agree at once.
- R6 Readability: plain titles for the owner. A "what would change my mind" line only while a disagreement is live. The conclusion leads with the decisive trade-off and uses a criteria table only when several criteria separate the options. One launch rule. The skill text drops standard/deep, which settings.py keeps accepting.
- R7 Debater brief: "this brief is your whole task: read only, load no skills, ask no one".
- R8 Labels (package-wide): one rule in skills/workflow/WRITING.md. Every owner-facing message, including commit and pull-request text and HTML reports, shows a label's plain meaning before the label, in the same message. A label seen only earlier, or in a part that failed to send, counts as unseen. Long content is sent in parts, and no question opens until every part has arrived. grilling and SPAR-FILE.md point to the rule instead of repeating it, and the WRITING.md example is fixed.
- R9 Tests: exact-wording pins of removed rules become behaviour cases. The control-intent, safety and justified-disagreement checks stay. Size limits are set to the sizes reached. The /spar row in docs/RULE-CONTRACTS.md is updated.
- R10 Package: no routing or loading change. Count which of the 266 checks in tests/test_verify_skills.py pin removable prose; report only.

What stays the same: the router, phases, recipes, hooks, approval gates, CONTEXT.md terms, the cancel and provider-failure rules, independent openings, "never fake agreement", and settings.py.

Not included: global files (START, CORE, ARTIFACTS); trimming other plugins; a release; merging into main; committing.

Acceptance (observable):
- A1 The full test suite and validate pass.
- A2 The after-run replays the same cases on the candidate (Claude CLI, same fixtures and staged replies, within the remaining $12.57):
  - zero safeguard regressions in the routing cases;
  - in the spar cases, at most 2 blocking stops before the first exchange;
  - no fake "both agree";
  - every label in owner-facing text shown with its meaning;
  - a debater given an unchecked owner claim checks it or names it as unchecked.
- A3 The owner compares the before and after spar conclusions with the version labels hidden and picks one. This is recorded as opinion.

Assumptions the owner can reject: the CLI replay counts as the live test. A GPT-vs-Claude run of the candidate needs the candidate installed, which is a separate approval.


## Outcome

Delivered 2026-11-20. Implemented and checked. The owner's blind pick came back with no preference (D3).

- Asked and agreed: the /spar rework from SPAR.md revision 9 (agreement 1, D1), built under offer #2 (D2), in the worktree D:/workflow-axa-spar. No commit, install or merge.
- Tickets:
  - T1 (label rule): verified, V1.
  - T2 (/spar rework): verified, V5.
  - T3 (docs): verified, S2 and V7.
  - T4 (wording-pin count): verified, V2.
  - T5 (live after-test): verified, V6. The blind pick was inconclusive (D3).
- Changed files:
  - skills/spar/SKILL.md, T3.md and SPAR-FILE.md;
  - skills/workflow/WRITING.md ("Chat replies" rule 7 and the example);
  - skills/grilling/SKILL.md (pointer);
  - tests/test_spar.py, test_owner_questions.py and test_simple_english.py;
  - tests/behavioral/spar.json;
  - tests/README.md;
  - docs/RULE-CONTRACTS.md.
- Verdicts:
  - R1-R8: verified by text tests, plus the live after-test where it reached them (V6).
  - R9 (tests): verified.
  - R10 (pin count, report only): verified.
  - A1 (full suite 1706 OK, validate PASS): verified.
  - A2 (live after-test): partial. Single model through the CLI; one run per case; the failed-send and last-exchange cases were not provoked.
  - A3 (blind pick): done; the owner had no preference (D3), so the opinion check is inconclusive.
- Size: the spar skill went from 3,574 to about 3,480 words, far above the 2,400-word estimate. Kept rules are pinned word for word by tests (see V2 for the same pattern elsewhere).
- Reviews: S1 failed, repaired; S2 passed; S3 failed on spar.json results, repaired; S4 passed; S5 records S3's verdict on the unchanged files. Both axes, Standards and Spec. The completion check reports every change reviewed in its current form.
- Assumption the owner can reject: the owner's verdict and the next move are asked in one card at the end of a spar.
- Found outside the scope: on the baseline, grilling did not ask the restart-retention question (V3). On the candidate it asked two other questions and stated retention as an assumption (V6). Left for later by the owner (D4).
- Evidence kept: .artifacts/2026-11-19-architecture-review/ (traces *.jsonl, suite-baseline.txt, suite-candidate.txt, blind-X.md, blind-Y.md).
- Scratch not removed: D:/axa-replay-2026-11-19/, refused by the removal safety check. The owner can delete it by hand.
- Next safe action: the owner decides whether to merge branch spar/architecture-review into main (2.10.0) and install it; the grilling follow-up waits (D4).