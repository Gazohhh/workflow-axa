# Approval hook: one broken offer file hides a task, and refusals point the wrong way

## Current checkpoint
- Updated / phase: 2026-11-19; closed (delivered; A4 partial, see Outcome)
- Recipe: bug; no modifiers — the approval hook hides valid offers and gives refusal reasons that send the agent the wrong way; scope: the task; classification question: not asked (the owner said "fix it")
- Rules: READY for this scope / sources: D:\workflow-axa\AGENTS.md, shared START, CORE, READINESS (installed 1.9.0; rules_stamp: NONE, information only) / limits: implementation needs the offer's approval
- Agreement (gate one): not required — settled one-ticket work (the three fixes named in the owner's chat diagnosis, 2026-11-19; owner: "fix it")
- Offer: #1 approved from the summary in the question tool (2026-11-19, DECISIONS D1)
- Implementation: T1 implemented in place (the owner copied the candidate files)
- Verification / owner acceptance: V1–V4 passed; Review S1 passed; completion_check exit 0; owner acceptance of the A4 consequence open
- Blockers: none
- Changed files: hooks/approval.py, tests/test_approval_hook.py, tests/README.md, CHANGELOG.md, docs/plans/2026-11-19-offer-visibility/
- Scope paths: `hooks/approval.py`, `tests/test_approval_hook.py`, `tests/README.md`, `CHANGELOG.md`
- Next safe action: owner decides on the commit; delete .artifacts/2026-11-19-offer-visibility/full.txt after it

## Working context
- Owner: Cem. Repository D:\workflow-axa, branch main at 4791859, local edits only in docs/plans/2026-11-18-bug-reproducer/ (the owner's, untouched).
- The live hook loads from the plugin cache (2.9.0-rc.4, ~/.claude/plugins/cache/gazohhh/workflow-axa/2.9.0-rc.4), not from this checkout, so this checkout is the separate candidate location AGENTS.md asks for. Nothing is installed.
- Test output: `.artifacts/2026-11-19-offer-visibility/` only if a check needs to keep output; removed at delivery.

## Goal and acceptance
A colleague's session had every protected write refused after real approvals (FINDINGS E1). Their offers were handled wrongly (a hand-edited offer file, or the offer shown as text and approved through a separate question); following the corrected steps fixed it (E5). The hook made that hard to see. After this change:
- A1 One offer file whose hash no longer matches stays unusable, but the other offers in its task folder are still seen and can approve writes; the refusal names the broken file and says the owner restores it.
- A2 The "no approved offer" refusal lists the offers of the task the session is on first, then other tasks newest first.
- A3 A click on "Approve from this summary" on a question that did not carry this offer's presentation, while that presentation was open in text, gets a reason that says so and how to ask instead. A question that carries this offer's footer but not its exact presentation gets a reason that says the text differs.
- A4 Nothing that approves today stops approving, and nothing that refuses today starts approving: only which offers are seen and the reasons change. `offers.py` is unchanged, so `offer create` still refuses while a broken file is present (ids stay safe).
- A5 `python -X utf8 -I tools/validate.py` and the test suite pass, failures before the change named.

## Baseline before this change
- 2026-11-19 at 4791859, local diff only in docs/plans/2026-11-18-bug-reproducer/ (owner's) and this task folder; Windows 11, Python 3.14: `cd tests && python -X utf8 -m unittest test_approval_hook test_offers` ran 163, OK (no failures).

## Ticket T1
- Supports: A1–A5.
- Scope: `hooks/approval.py` (project_offers, no_offer, decide reasons); tests in `tests/test_approval_hook.py`; a line in `tests/README.md` and an Unreleased note in `CHANGELOG.md`. Not `skills/workflow/scripts/offers.py`, not hooks.json, not other hooks.
- What should work: A1–A3 as written; A4 holds.
- Test seam: the hook's command-line interface through the existing `ApprovalHookCase.run_hook` with synthetic transcripts and offer files. It misses how a live host writes transcripts (covered by the colleague's live run, E5).
- TDD: yes.
- How to verify: the new tests fail first, then pass; then `test_approval_hook test_offers test_shadow_comparison test_session_failures`, then the full suite and validate.
- Documents: tests/README.md, CHANGELOG.md.
- Rules: D:\workflow-axa\AGENTS.md.


## Outcome
Delivered 2026-11-19 (reconciled by this session, self-performed; the review was independent).

- Asked: fix the approval hook after a colleague's session had every write refused (E1, E5). Built: T1, offer #1, approved from the summary (D1).
- Changed files: hooks/approval.py, tests/test_approval_hook.py, tests/README.md, CHANGELOG.md (Unreleased), plus this task folder. Nothing committed.
- A1 verified (V1, V4): a hand-edited offer file stops only itself; the refusal names offers/offer-N.json and says to put it back; a path only it covered stays refused.
- A2 verified (V1, V4): refusals list the session's own task first, then other tasks newest first, for both approved offers and reasons.
- A3 verified (V1, V4): the reasons for an approve click on a question without the offer, and for a question whose text differs.
- A4 partial: what counts as an approval is unchanged and offers.py is untouched, but an offer a broken sibling used to hide now counts fully, so its task's open rules question can pause a write that another task's offer used to allow (review finding, kept by judgement; reported to the owner).
- A5 verified (V3, V4): validate PASS; full suite on the candidate 1632 ran with two explained failures (the known flaky lock test, passed on rerun; a Git-history test that fails only in the copy and passes in place).
- Reviews: candidate reviews 1 (failed, repaired) and 2 (passed); Review S1 passed on the final files; completion_check exit 0. Blast radius: project_offers has one caller, updated.
- Process gap: the first hook edit was made in the live working tree (E6) and paused writes in every session until the owner copied the finished files in.
- docs_check: 0 blocking; the 2 warnings are older example paths in skills/workflow/SETUP.md and tests/SCENARIOS.md, unrelated.
- Kept evidence: .artifacts/2026-11-19-offer-visibility/full.txt (suite output); remove when this task is committed. Scratch removed: the candidate copy, the red copy, the diffs.
- Next safe action: the owner decides on committing the four files; the installed cache copy and other machines get it only with a release and update.
