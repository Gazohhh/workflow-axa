# UI design boundary

## Current checkpoint

- Scope approval: user said “lets do this” after the functionality-only / approved-kit / design-authoring proposal. This authorises the package update, not changes to any application or installed environment.
- Base: supplied complete workflow-axa 2.7.0-rc.2 archive.
- Implementation: complete within the approved package scope.
- Verification: baseline validator/321 tests passed; candidate validator/370 tests and 19 browser checks passed. Protected files and Matt catalogue preservation checked. Fresh extraction reran all checks successfully. Live Claude/Codex cases remain NOT_RUN.
- Next action: user installs all eight skills and pilots the candidate in actual hosts; code/tests/package work is complete.

## Agreed outcome

Stop agents inventing application presentation during ordinary feature work. Preserve existing interfaces. Allow agreed, minimal semantic markup in an authorised preview when design is pending. Prefer actual approved components/patterns, not arbitrary classes found in legacy code. Designers can later approve a project kit and scoped design-authoring work.

## Scope

Add one local ui-design skill. Route application UI work to it from workflow, shared rules and related review/resume/status utilities. Keep three explicit modes per affected area: functionality-only (default), approved-kit and design-authoring. Keep behaviour verification, design acceptance and release readiness separate in existing records. Add read-only diff triage and negative/positive test cases; it is not an authorisation engine or host blocker.

Keep Matt's catalogue, proactive grilling, rules readiness, artifact policy, local flowchart renderer/assets, version helper, global activation helpers and existing history. No external dependency, application edits, installation, kit creation, global CSS reset, preview server or blanket migration. Approved flowchart generation is exempt only through its existing local renderer; arbitrary application prototypes are not reports.

## Acceptance and verification

- Workflow and ordinary globally routed application requests select design rules; backend-only work does not require a UI kit.
- Missing UI coverage cannot silently authorise styling. Mode/source/preview/acceptance boundaries reuse current records and valid approval.
- New CSS, utility combinations, visual props and other renderers are not loopholes. Existing necessary runtime behaviour is preserved.
- Accessible semantic markup remains allowed within the approved scope. No release claim for design-pending UI.
- Script triages a supplied diff without reading its named files, writing output, installing anything, or self-awarding approval. Ambiguous/malformed/binary inputs stay unresolved.
- Tests exercise prohibited and legitimate changes, backward compatibility, references, release metadata and unchanged dependencies/rendering.
- Existing browser tests run offline; actual agent compliance remains NOT RUN and is reported as such.

## Revision log

R1: approved package-level proposal above. Progress/test retries update this checkpoint, not a new plan revision. Detailed results will be recorded here and in the release validation record; no duplicate task folders.

## Outcome and limits

One local ui-design skill, shared design.md as policy owner, conditional workflow/global routing and updates to the existing review/resume/status/setup paths. Eight skills total; no added external provider. The optional diff helper is intentionally review triage, not a policy authority or universal CSS detector. New live scenarios are authored, not run. No application or user environment was changed. See root VALIDATION.md for exact observed results and installation limits.
