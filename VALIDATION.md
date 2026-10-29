# Validation — 2.6.0

Date: 29 October 2026. Baseline: the owner-supplied workflow-axa(1).zip (plugin 2.5.0), SHA-256 `078537e539e85c957ed24175f2ad0bad814e17284466b7aaf814f870d0ff3af6`. The uploaded archive and user's project documentation are unchanged. Work was done in an isolated package copy, not in an installed host or application repository.

## Observed checks

| Check | Result |
|---|---|
| Uploaded baseline | 178 automated tests ran: 177 passed; one failed because the extra legacy DIAGRAM-DESIGN.md file restored the retired external-provider instructions. The filename is now a safe local compatibility pointer. |
| Candidate tooling suite | PASS: 210 tests, including additive report fields, exact legacy aliases, source checks, authority mismatches, escaped content, unchanged original snapshots, legacy STATUS.md fixtures and existing global-policy safeguards. |
| Package validator | PASS: six skills, manifest/catalogue version alignment, relative references and entrypoint budgets. Main workflow: 1,178 words; codebase-map: 850 words. |
| Offline Chromium | PASS: 19 checks, including original flow controls/geometry plus separate checkpoint states, revision disclosure/source navigation, desktop/mobile layout and no-JavaScript behavior. No external requests or page errors. |
| Flowchart visual carry-forward | PASS: four exact screenshot comparisons against the supplied baseline rendered in the same controlled environment; zero changed pixels in desktop current/proposed/build and mobile proposed panels. The new optional prose/status sections are outside that old flow-panel comparison and were separately inspected. |
| Dependencies and original history | 27 Matt catalogue entries and route definitions preserved. QUESTIONS.md, ARTIFACTS.md, global_policy.py, local design guide, viewer JS, original example sources/HTML and all 24 existing package task-record files are byte-identical. See dependency-preservation.json. |
| Backward compatibility | Old schema-2 input has no new required fields. Existing HTML/source-manifest checks are retained. Schema-1 layout regeneration still requires the existing explicit migration, not an automatic converter. |
| Final distributable | Extracted to a fresh directory; package validator, all 210 tooling tests and the 19 browser checks rerun from those extracted bytes. ZIP integrity checked. |
| Agent evaluations | 31 live-host scenarios are defined, including seven new record-history cases. ALL NOT_RUN. Tool tests do not establish model obedience. |

Evidence files are in tests/evidence: tooling-tests.txt, browser-smoke.json, visual-comparison.json, visual-candidate-manifest.json, dependency-preservation.json and behavioral-results.json. Dated 2.2.x results and visual-negative-control.json are retained historical evidence, not new run claims. The unchanged bundled visual baselines are not replaced with candidate images.

## What the tests mean

The renderer checks supplied structure, references, geometry, exact source bytes and some explicit state contradictions. It does not interpret arbitrary Markdown as truth, authenticate an approving person, verify implementation from a status field, or prove complete repository coverage. A checkpoint remains a dated sourced claim; its approval, code work and acceptance must be reconciled with actual records/worktree by the agent.

Behavioral fixture tests establish what inputs exist, not how Claude/Codex respond. The legacy history fixture contains actual negative-score validation while retaining a prior pending review and historical proposal, so a future evaluator can distinguish progress from authority. Missing historical reviews are deliberately not reconstructed. Owner-removed items are not labelled as passing tests.

## Preservation and scope

No user plans.zip/adr.zip records, project AGENTS/CLAUDE/CONTEXT files, global instructions, application code, Git index/history, third-party skills or existing artifacts were modified. No dependency downloads, external uploads or new external skill requirements were introduced. The distributable excludes .git, caches and local QA output; it retains all original non-Git package file paths, including the legacy diagram pointer.

ARTIFACTS.md and its deployment helper remain revision 2.5.0 because their content and activation are unchanged; that version is independent of the 2.6.0 package. Existing global activation still matches. Its test now checks deployment-to-policy consistency rather than forcing unrelated release numbers to match. The setup safety tests remain in force.

Adoption is forward-only: new tasks use the clarified rules; an authorised continuation minimally reconciles that task. Read-only utilities never silently update files. Local project retention conflicts need an explicit reviewed merge, not a global override. Existing pending review badges remain historical. The optional task-overview is not regenerated on every update and creates no authority or additional plan.

## Environment and limits

Python 3.13, Linux x86_64, existing Playwright and Chromium 144.0.7559.96. No browser installation. Chromium's sandbox bypass was used only in this disposable trusted container; normal commands retain the sandbox. Desktop and mobile overview screenshots were visually inspected.

Direct local file navigation was blocked by the environment policy. The identical HTML was loaded with networking disabled; this tests rendering and controls, not the user's default desktop opener. No complete accessibility audit, multi-browser/Windows pixel guarantee, user-comprehension study or live Claude/Codex invocation/behavior is claimed. Verify host discovery and H01–H07 on the actual team installations before relying on them.
