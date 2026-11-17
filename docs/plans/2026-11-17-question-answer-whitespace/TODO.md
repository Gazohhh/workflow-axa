# TODO

| Ticket | What | Status | Depends on |
|---|---|---|---|
| T1 | Keep an answer whose key lost the question's surrounding whitespace | Verified | — |

### T1 — Keep an answer whose key lost the question's surrounding whitespace
Status: Verified
Evidence: FINDINGS V1 V2 S2 S3; test_approval_hook and test_offers 163 OK; GPT-6.1 Sol review PASS (round 2)

What needs to happen: PLAN "Fix".

How to verify: `python -X utf8 -m unittest discover -s tests -p "test_approval_hook.py"` (the new tests fail first), the offer tests, then the full suite; a review by GPT-6.1 Sol.
