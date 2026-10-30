# Audit of the supplied rc.5 and additive UI-report update

Review date: 30 October 2026. Basis: the owner's uploaded `workflow-axa.zip`, supplied `review-r2.html`, and the earlier rc.4 package. This is a local source/package audit, not a new inspection of Altinstar, Cheflabels, T3 profiles or their actual deployment.

## Bottom line

The agent's package changes are substantially sound and were retained. The upload does not establish that the running skills or global references were updated: its own task checkpoint still holds those steps for reviewer approval. The historical report is explicitly stale and unpresented in that checkpoint. An interruption left deployment and acceptance unfinished, not an observed failure of the packaged Windows fixes.

## Findings and disposition

| Finding | Evidence in supplied tree | Result |
|---|---|---|
| rc.5 identity is consistent across package/rule metadata | plugin.json, rules/version.json, specialists.json | Retained, then bumped together for rc.6; no silent rollback to rc.4. |
| CRLF-only copies remain rejected, but get a useful diagnosis | activate_rules.py validate_library; readiness.py snapshot; audit_installation.py inspect | Correct approach for the recorded raw-byte policy. Tests cover actual content changes hidden by CRLF. Retained. |
| Manifest writer now uses UTF-8 bytes | tools/update_rules_manifest.py | Avoids platform newline translation in the generated manifest. Retained. |
| Explicit host roots no longer unnecessarily depend on resolving a home | activate_rules.py profile_roots; global_policy.py implicit_home | Verified with missing-home/explicit-root fixtures; not tested on a real T3 Windows profile here. Retained. |
| Shared “no nested ternaries” policy was intentionally approved | task DECISIONS D2; rules/typescript.md | Applies to new/meaningfully changed TS, with no forced abstraction or retroactive cleanup. Retained byte-for-byte. |
| Windows link-test fallbacks distinguish unsupported privilege from unrelated errors | tests/links_helper.py; test_line_endings.py | Reasonable test portability; skips are explicitly disclosed. Linux execution does not re-prove NTFS behavior. Retained. |
| Installer comparison did not report unexpected files in owned trees | audit_installation.py loop over expected paths only | A documented limitation, but it could leave stale instruction files unnoticed. rc.6 reports `unexpected` as DRIFT while leaving unrelated skills alone and performing no deletion. |
| `skills/** text eol=lf` would also classify future binary UI captures as text | .gitattributes | Kept the scoped LF rule and added binary-extension overrides. No bulk normalization of historical documents. |
| R2 and the latest task checkpoint describe different moments | docs/plans/2026-10-30-rules-audit-design-kit/PLAN.md; supplied review-r2.html | Preserve the old report. Its open F1 questions and incomplete-review statements are historical, not the current checkpoint. Do not overwrite it to pretend deployment passed. |
| G1 runtime replacement and G2 global activation were held | current PLAN; FINDINGS “G1/G2 final plan” | Not performed here; no live profiles or those projects are mounted. Upgrade instructions require checking the actual installed copy and then its effective global route. |
| UI previews were excluded by older report instructions | codebase-map/SKILL.md and ui-design/CONTRACT.md in rc.5 | Replaced this conflict with a bounded optional screen-flow view in the original full report. Normal app design still needs source, preview and implementation authority. |
| Renderer manifests still called the tool 2.6.0 | render_report.py render() | Corrected the tool identity; old manifests remain readable. |
| Source ZIP included Git internals and scratch release files | ZIP inventory: .git and .artifacts entries | Not part of the new installable ZIP. Nothing was deleted from the owner's originals. Existing task records are preserved. |

## What was preserved

The eight-skill arrangement; all Matt specialist catalogue entries and provider information; grilling policy; shared core/engineering rules except the specifically updated UI guidance; the artifact policy; original report.css and report.js; the local editorial theme; historical task/decision/report content. The new UI assets are loaded only for optional UI screen-flow input.

The package does not grant independent reviewers authority to install, implement or approve work. Static checks and hashes remain freshness/structure aids, not evidence of consent or a sandbox. Read-only helpers do not enforce every agent action.

## Scope of the sample

The source R2 task concerns rules loading, not a new application screen. Therefore its additional screen-flow example is marked **illustration outside implementation scope**. It would be incorrect to insert notification-preference tasks into that real plan. A second complete UI-feature report demonstrates the normal application-UI case using an explicitly synthetic fixture and the exact same report shell. Neither is an approved Altinstar/Cheflabels design.

## Remaining limits

No current project rules, design kits or component implementations were supplied beyond historical records. The recorded Cheflabels design approvals are preserved as history; their actual files and current coverage were not independently checked. No live model sessions, user profiles, production requests, game builds or devices were tested. Actual loading/following/enforcement remains separate from on-disk consistency.

Test counts, browser checks and comparison results for this new package are in VALIDATION.md. They are measured results, not proof of universal correctness.
