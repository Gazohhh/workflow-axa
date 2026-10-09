# Findings and verification

## F1 — Source review
Current upstream manifest observed as 1.3.1, listing 27 skills. Rechecked the 11
model-invocable specialist entrypoints, the grilling wrapper, setup, selected manual
workflows, and writing-for-agents/SKILL-MECHANICS.md through public web retrieval.
This is a targeted integration review, not a new live execution audit of all 27 skills.
Primary source links are recorded in the dependency catalogue and SETUP.md.

## F2 — Integration conflicts
Upstream grilling/research/code-review request subagents; code-review targets a
committed comparison and tracker; TDD asks for pre-agreed seams. Prototype and wizard
include commit instructions. Domain-modeling writes glossary/ADR decisions inline.
The integration explicitly bounds these actions instead of copying a competing workflow.

## F3 — Environment limits
Git clone failed due to unavailable DNS and archive/raw-byte download was unavailable.
Web-readable primary files remained accessible. No upstream commit or upstream byte hash
is asserted. The checker fingerprints actual local installations when run by a teammate.
No teammate installation or host runtime was accessed by this packaging task.

## Verification
## V1 — Package structure
Command: `python -X utf8 tools/validate.py`, from the extracted package root.
Observed exit 0, one skill, links closed within standalone skill, catalogue/version aligned,
core 1,127 words. This is structural verification, not host behavior.

## V2 — Tooling test suite
Command: `python -X utf8 -m unittest discover -s tests -p "test_*.py" -v`, package root.
Observed 39 tests, all passed, exit 0 on Python 3.13.5 / Git 2.47.3 / Linux.
Tests include 21 new deterministic specialist-checker cases and 18 retained package/fixture
cases. Skill files in these tests are clearly synthetic. No actual specialist invocation.

## V3 — Source and active-policy inspection
Reviewed final package changes against R1. Verified one entrypoint, all 11 explicit routes,
27 catalogue entries, manual wrapper separation, documented adapters, no silent setup,
selected-phase blocking, existing approval and record reuse, and preserved Git boundaries.
Removed obsolete optional-interview claims from active documentation. All four original
2026-10-07 task docs remain byte-identical. Self-review only.

## V4 — Final archive
Created a source-only archive, checked CRC integrity and byte equality for every member,
then extracted into a fresh directory and ran V1/V2 there. Package validation exited 0;
all 39 tests passed again (3.535 seconds on the observed run). The archive contains 46
source/document files under one workflow-axa root, no Git metadata, caches or fixtures
created during testing. Final delivery rebuild repeats these checks after closing records.
No runtime host checks have been performed.
