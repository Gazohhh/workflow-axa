# Synthetic legacy task — current record

This is a fixture, not a real project's approval. It illustrates a legacy STATUS.md checkpoint and inline decisions. The earlier PLAN, TODO, FINDINGS, review.json and review.html remain historical fixture inputs. No application work has actually been run by this example.

## Current checkpoint
- As recorded: 2026-10-29T12:00:00+00:00 (fixed synthetic example time).
- Approval: P1 approved in fixture decision D2 below; both entrypoints and existing output format are covered.
- Implementation: not started. The supplied scoreboard.py still has its original behavior.
- Verification/acceptance: not run for the proposed change. Static inspection of the baseline is not runtime verification.
- Next safe action: add regression coverage for either negative score, then perform the approved change. No additional interview is needed for unchanged fixture scope.
- Reviewed flow: P1 in review.html/review.json; its pending badge records presentation, not this later synthetic checkpoint.

## Inline decisions and revision log
- P0 / old-draft: proposed changing the web path alone. D1 superseded that incomplete proposal; no P0 HTML exists in this fixture and none should be invented.
- P1 / review.html: both web and player callers must reject either negative score. D2 synthetic approval: "Proceed with P1: reject either negative score through both entrypoints; preserve nonnegative output. No dependencies or extra features."
- Reason for the change: the player bypassed the shared formatting owner, so a web-only fix would leave the other caller unchanged.
- No implementation or verification is claimed. A rerun or handoff would update this checkpoint, not create P2.
