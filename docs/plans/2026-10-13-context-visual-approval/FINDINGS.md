# Findings
F1: 2.0.0 core asks to inspect owners/callers/tests, but readiness does not require requirement-to-evidence-to-task traceability. Explain mode has no explicit evidence requirement.
F2: 2.0.0 setup checks specialists but lacks a small host-loaded ordinary-prompt routing block. Existing scenarios primarily use explicit invocation.
F3: The package registers exactly one skill; validators and installation docs enforce that and must change together.
F4: Matt's linked architecture command presents refactoring candidates then grills; its HTML reference loads Tailwind/Mermaid from CDNs and is not an offline board. New renderer will be original stdlib HTML/SVG, not a copied CDN template or a Miro service integration.
F5: Local tooling: Python, Git, Chromium and Python Playwright are available. Claude/Codex executables were not found. Browser tests can run; live agent behavior cannot be established here.
F6: Existing specialist catalogue is a historical 2026-10-09 snapshot. Preserve that date and claims; this work does not assert a newly verified full upstream inventory.

## Verification
V1 — From the candidate package root: `python -X utf8 tools/validate.py`, exit 0. Two registered skills, portable references, version consistency; core 1,004 words and map 620 words.
V2 — `python -X utf8 -m unittest discover -s tests -p "test_*.py" -v`, exit 0: 76 tests passed. Includes original specialist/fixture regression tests and new report/tooling cases. Log: tests/evidence/tooling-tests.txt.
V3 — Optional browser_smoke runner with installed Chromium in the isolated test container, exit 0: 7 checks passed; no requests/errors. Output: tests/evidence/browser-smoke.json. Desktop/current/proposed/mobile views inspected visually.
V4 — Bundled example `--check`, exit 0: named source/input bytes match. This is not semantic approval verification.
V5 — Final ZIP integrity plus fresh extraction: rerun validator, all 76 unit tests, example source check and 7 browser checks; all passed. No application/Git publication actions.

## Limitations and final audit
Direct file navigation was blocked by managed browser policy. Browser tests therefore used rendered content directly with network offline; default desktop opening and live agent behaviors are unverified. Neither Claude nor Codex executables were available. The 31 behavioral cases require the user's local pilot, especially implicit activation and cold approval-state recovery.
Reviewed active docs for obsolete one-skill registration, old approval ordering and stale prompt examples. Updated both-skill installation, setup, validation and routing consistently; historical task records remain explicitly historical. Matt inventory provenance was not silently refreshed. The offline report is original local HTML/SVG code, not an external board or copied upstream execution flow.

