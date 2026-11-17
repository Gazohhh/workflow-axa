# TODO

T1 is built test first. T2 runs after T1, and only after the owner's OK and a cost cap.

| Ticket | What | Status | Depends on |
|---|---|---|---|
| T1 | /spar text: rules of the spar, owner checkpoints, waiting, owner verdict, with tests | Verified | — |
| T2 | Live replay of a spar with the owner in the loop | Not started | T1 |

### T1 — /spar text: rules of the spar, owner checkpoints, waiting, owner verdict
Status: Verified
Evidence: FINDINGS V1 (test_spar 41 OK, suite 1543 OK, validate PASS), V2; review S2 passed

What needs to happen: R1-R7 in skills/spar/SKILL.md, skills/spar/T3.md (opening, exchange and synthesis briefs; launching and waiting) and skills/spar/SPAR-FILE.md (Owner decisions, the conclusion). Keep SKILL.md short: point to grilling's table and "How to ask" instead of restating them.

What should work: the skill text states the launch rule, the pre-opening grilling frontier, the three checkpoints with what each shows before its question, the waits, the split between binding owner decisions and challengeable owner opinions, the three-party agreement with a zero-launch verdict, and offers no "at the end only" choice.

References: Supports R1-R8. Rules: AGENTS.md; skill files stay LF (Edit tool).

Technical details: Scope skills/spar/SKILL.md, T3.md, SPAR-FILE.md, tests/test_spar.py, tests/behavioral/spar.json (a scenario for the owner checkpoints), tests/README.md (/spar section). Must not change skills/grilling. Test seam: the skill text through tests/test_spar.py, as the existing spar tests do; it catches a removed rule, not whether an agent follows it (T2 covers that). TDD: yes.

Documents: tests/README.md.

How to verify: `cd tests && python -X utf8 -m unittest test_spar` (new tests fail first, then pass); the full suite; `python -X utf8 -I tools/validate.py`.

### T2 — Live replay of a spar with the owner in the loop
Status: Not started

What needs to happen: R8's live replay, after the owner's OK and a cost cap.

What should work: the five R8 observations hold in one real /spar run.

References: Supports R8.

Technical details: a `claude -p` pilot per the live pilot recipe, output under .artifacts/2026-11-17-spar-owner-in-loop/. TDD: no, it is a live observation.

How to verify: Human check: the owner reads the result; each R8 observation is recorded in FINDINGS with its evidence.
