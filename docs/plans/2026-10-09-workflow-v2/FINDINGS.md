# Findings

- 2026-10-09 — Input inspected: 14 source files plus embedded .git data. The working copy excludes .git; no uploaded Git history was executed or used.
- 2026-10-09 — Original active instructions conflict on question batching, create records after early clarification, mandate subagents, stage entire files, and permit a final fix to retain stale verification. README and prompt helper repeat obsolete behavior. Changes must address references and metadata, not only SKILL.md.
- 2026-10-09 — Original PDF procedure already uses conditional loading; retain reader/evidence/rendering/final-version gates while reusing explicitly approved unchanged terminology.
- 2026-10-09 — Python and Git are available. Claude Code and Codex executables are absent. Package/fixture checks can run locally; host-native validation and live model behavior cannot be claimed. See the final validation report for observed results.

- V1 — 2026-10-09 — `python -X utf8 tools/validate.py` in the package root: exit 0. Manifest/metadata/registration, relative links, separately installable reference closure and core budget passed. This is a package-specific structural check, not Claude host validation.
- V2 — 2026-10-09 — `python -X utf8 -m unittest discover -s tests -p "test_*.py" -v`: 18 tests passed after the final validator/reference-safety change. All seven generator variants were exercised; the clean fixture's three tests pass; the intentionally failing fixture fails for its documented reason.
- 2026-10-09 — Final source self-review added explicit initial diff/index evidence for mixed ownership and an installable-skill reference-closure regression. Active docs and metadata no longer retain mandatory subagents, automatic staging, repeated glossary approval, or a fixed two-pass audit escape. Historical task records remain byte-preserved and non-authoritative.
- UNTESTED — Native Claude/Codex validation, actual model behavior, Windows execution and cross-account recovery; executables/hosts unavailable. No independent subagent review occurred. Scenario protocols must not be reported as executed agent tests.

- V3 — 2026-10-09 — Built a source-only archive with 37 files. ZIP CRC checks and byte equality against source passed; .git and generated caches/fixtures were absent. Extracted it into a fresh directory and reran structural validation successfully.
- 2026-10-09 — Two combined archive-check invocations were interrupted by the execution tool's timeout while the suite was running; they are not counted as passes. A clean-fixture spot check passed, then an instrumented run of the same full extracted unittest suite passed all 18 tests in 7.568 seconds. No assertion failure or reproducible package defect was found; the timeout cause was not established. No test was removed or weakened.
- V4 — 2026-10-09 — Final delivery includes the candidate, local validation results and explicit live-host limitations. Archive integrity/source equality and the extracted test suite are rechecked after final record updates before delivery. No application repository, host installation, global policy or remote was changed.

## R2 baseline inspection — 16 October 2026
- E10: skills/workflow/QUESTIONS.md and SPECIALISTS.md only trigger grilling for identified structured choices. The core lacks a proactive missing-decision review for all new substantive goals.
- E11: TASK-FOLDER.md permits continuation only for an exact goal/scope match. No case table covers extensions, likely matches, completed tasks or ambiguous multiple candidates.
- E12: tools/browser_smoke.py captures images and checks layout but performs no screenshot comparison. The approved CSS/JS and schema-2 renderer need preservation rather than redesign.
- E13: no claude/codex executable found. Browsing upstream documentation is not installed-skill execution. Package/browser tests cannot establish live questioning behavior.
- References consulted: Matt's grilling and writing-for-agents; Claude Code skills; Agent Skills evaluation guidance; official Playwright screenshot/page APIs; Anthropic skill-creator and webapp-testing. These inform bounded integration/testing instructions, not a replacement of the user's methods.

### R2 observed verification
- V10: original 2.2.1 `python -m unittest discover -s tests -v`: 113 passing tests before edits.
- V11: 2.3.0 equivalent command: 141 passing tests, including retained cases, instruction/fixture-input guards, reference integrity and optional pixel checks; no skips here. These are not agent-behavior tests.
- V12: `tools/browser_smoke.py` with existing Chromium: 15 checks pass offline. Direct file navigation blocked; identical content fallback recorded.
- V13: `tools/visual_regression.py capture/compare`: four views match 2.2.1 exactly; changed_pixels=0. Baseline renderer/assets came from the unmodified previous ZIP.
- V14: deliberate font-size change to 19px in a disposable package produces exit 1 and four failed pixel comparisons. The reference/candidate inputs are never rewritten.
- V15: all 27 Matt catalogue records/source metadata preserved; nine non-question/writing route rows unchanged; Q and writing adapters intentionally revised. CSS/JS/example input unchanged; renderer logic unchanged except tool_version.
- V16: package integrity, byte equality after fresh extraction and repeated validation are documented in VALIDATION.md. No source/runtime installation claims are inferred from this.

### Review corrections
- Extended the existing maintenance folder and preserved prior release history.
- Replaced stale README/setup claims that only the design dependency changed; refreshed the prompt template and PDF/shared writing references.
- Changed the screenshot environment probe to fixed reference fonts, so an intentional node font-size regression is a visual FAIL rather than misclassified as a host mismatch.
- Added non-object/missing/corrupt baseline handling; reference absence never creates an auto-approved image.
- Reader/self-review: kept exact technical verification in supporting docs, with UPGRADE.md and the main process explanation first. No independent teammate/agent review is claimed.
