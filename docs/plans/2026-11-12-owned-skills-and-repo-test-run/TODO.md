# Tickets (r1)

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Merge the 9 copied skills into owned single texts | Verified | none |
| T2 | Remove source mentions from the rest of skills/ | Verified | T1 |
| T3 | Replace the hash checks with LICENSE and no-mention checks; retire the copy tool | Verified | T1 |
| T4 | Update repository docs and the version | Verified | T2, T3, T5, T6, T7 |
| T5 | Write the rule contracts and labels | Verified | T2 |
| T6 | Find and fix the missing skill descriptions | implemented — verification pending | T1, T2 |
| T7 | docs_check skips git-ignored and third-party folders | Verified | none |
| T8 | Verify, publish, reinstall and run the after-test on the 7 repos | implemented — verification pending | T4 |

## Tickets

### T1 — Merge the 9 copied skills into owned single texts
Status: Verified
Evidence: V3, V4, V6

What needs to happen: grilling, tdd, code-review, writing-for-agents, codebase-design, domain-modeling, implement-spec, retro and simple-english each become one text. The adaptation section's rules are folded in where they belong; source lines they contradict (for example grilling's "interview relentlessly", tdd's "refactoring is not part of the loop") are dropped. The "Bundled with" banner goes.

What should work:
- Each SKILL.md reads top to bottom with no "the section below overrides the text above".
- Every rule of the old adaptation section is still present, or FINDINGS lists it with the DECISIONS entry that removed it.
- Frontmatter name and disable-model-invocation stay as they are (descriptions change only in T6).

Technical details:
- May change: skills/{grilling,tdd,code-review,writing-for-agents,codebase-design,domain-modeling,implement-spec,retro,simple-english}/SKILL.md and their supporting .md files where they mention the source. Must not change: LICENSE files, other skills, hooks/.
- Test seam: T3's test over skills/ (no source mention, LICENSE present) plus validate.py word budgets. It misses meaning loss; covered by the line-by-line adaptation comparison written to FINDINGS and the T8 review.
- TDD: no (instruction text; the mechanical check is T3's test).

Documents: the 9 SKILL.md files

How to verify:
- Line-by-line comparison old adaptation vs new text, saved in FINDINGS (V entry).
- python -X utf8 -I tools/validate.py (word budgets).

Verification: passed (adaptation comparison V3, V4; review V6; validate.py PASS after repairs)

References:
- Supports: A1, A2; D1
- Depends on: none
- Rules: AGENTS.md (the vendored-content rule changes with D1 in T4), writing-for-agents

### T2 — Remove source mentions from the rest of skills/
Status: Verified
Evidence: V9, V15

What needs to happen: remove the remaining mentions of where the copied skills came from: workflow/SPECIALISTS.md (the "copies of" line, the source catalog paragraph, the source's user-run workflows), workflow/specialists.json (source catalog) and workflow/scripts/check_specialists.py if it only serves that catalog, workflow-doctor/SKILL.md ("Matt specialists"), workflow/AUDIT.md, OPTIONAL-HELPERS.md, WRITING.md, codebase-map/SKILL.md, TASK-REPORT.md, FLOWCHART-DESIGN.md, simple-english/references/use-cases.md, rule-maker/rules/SOURCES.md (the codebase-design source link). Framework documentation links in SOURCES.md stay.

What should work:
- A search under skills/ for the source names, URLs and "upstream" in the copy sense finds nothing (T3's test).
- The workflow still names its bundled specialists by local name; nothing that loads them changes.

Technical details:
- May change: the files listed above; rule-maker/rules/CHANGES.md and version.json (rules 1.8.8). Must not change: hooks/, the 9 SKILL.md files (T1).
- Test seam: T3's test; tests/test_specialists.py for the checker. Misses wording quality; covered by the T8 review.
- TDD: no (docs); a removed or reduced check_specialists.py changes its tests in T3.

Documents: files listed above

How to verify:
- T3's test passes; python -X utf8 -m unittest tests.test_specialists

Verification: passed (V9, V15; test_specialists removed by D17)

References:
- Supports: A1; D1
- Depends on: T1

### T3 — Replace the hash checks with LICENSE and no-mention checks; retire the copy tool
Status: Verified
Evidence: V2, V8, V16

What needs to happen: a new test asserts that no file under skills/ names the source projects and that the 9 folders keep LICENSE. Write it first; it fails before T1/T2. Then retire tools/vendor_specialists.py and tests/test_vendored_specialists.py, and update validate.py, build_release.py and the tests that read VENDORED-SKILLS.md hashes or the source catalog (test_specialists, test_docs_consistency, test_release, test_simple_english, test_task_report, test_validate_budgets, test_docs_check as needed).

What should work:
- The new test fails on today's files and passes after T1 and T2.
- The release ZIP still contains every LICENSE (build_release check).
- No remaining check reads the removed hash tables.

Technical details:
- May change: tools/validate.py, tools/build_release.py, tools/vendor_specialists.py (delete), the tests listed. Must not change: hooks/.
- Test seam: unittest over the files on disk; validate.py output. Misses mentions in a form the pattern does not cover; the pattern list sits in the test with the reason.
- TDD: yes.

Documents: tests/README.md layout line (in T4)

How to verify:
- Red run before T1/T2 recorded; python -X utf8 -m unittest discover -s tests -p "test_*.py" green after; python -X utf8 -I tools/validate.py PASS. Output: .artifacts/2026-11-12-owned-skills-and-repo-test-run/

Verification: passed (red V2; V8; full suite and validate V16)

References:
- Supports: A1, A6; D1, D9
- Depends on: T1 (for the green run)

### T4 — Update repository docs and the version
Status: Verified
Evidence: V16, V17

What needs to happen: VENDORED-SKILLS.md becomes a short credits and licence note (sources, licences, LICENSE locations; no hashes or regeneration steps). AGENTS.md: the vendored rule and its index line follow D1, and the index links docs/RULE-CONTRACTS.md. README (one credits line, D10), CONTEXT.md, docs/ARCHITECTURE.md, docs/DESIGN.md (release history entry), CHANGELOG.md, UPGRADE.md, VALIDATION.md, tests/README.md, tests/SCENARIOS.md mentions; .claude-plugin/plugin.json and the other version fields to 2.8.0-rc.37.

What should work:
- validate.py version and count checks pass; docs_check on workflow-axa shows no new blocking item.

Technical details:
- May change: the files listed. Must not change: docs/plans of other tasks, docs/archive.
- Test seam: validate.py and docs_check. TDD: no (docs).

Documents: listed above

How to verify:
- python -X utf8 -I tools/validate.py; python -X utf8 -I skills/rule-maker/scripts/docs_check.py .

Verification: passed (V16; review V17 and its repairs)

References:
- Supports: A1, A6; D1, D10
- Depends on: T2, T3, T5, T6, T7

### T5 — Write the rule contracts and labels
Status: Verified
Evidence: V11, V15

What needs to happen: new docs/RULE-CONTRACTS.md. For each hard rule (gate one, gate two, small change, no new CSS / DESIGN.md rule 4, artifact cleanup): trigger, scope, preconditions, required action, exceptions, what to do when blocked, and what checks it (named hook, test, or "instructions only"). A per-skill table labels each main rule hard rule, procedure or judgment call. A "hook candidates" list names hard rules checked by instructions only (no hook change, D5). Where an owner file (VISUAL-REVIEW.md, rule-maker/rules/DESIGN.md, workflow/ARTIFACTS.md) lacks the blocked behaviour, add one sentence there.

What should work:
- Every hard rule in CONTEXT.md's owner list appears with its checker.
- A rule named as hook-checked matches the hook code (hooks/phase_gate.py and others), read, not assumed.

Technical details:
- May change: docs/RULE-CONTRACTS.md (new), skills/workflow/VISUAL-REVIEW.md, skills/workflow/ARTIFACTS.md, skills/rule-maker/rules/DESIGN.md, and rule-maker/rules/CHANGES.md after T2. Must not change: hooks/.
- Test seam: validate.py links; docs_check reachability from the AGENTS.md index. Misses accuracy; covered by reading each named hook and the T8 review.
- TDD: no (docs).

Documents: docs/RULE-CONTRACTS.md; AGENTS.md index line (in T4)

How to verify:
- Each "checked by hook" claim cites hook file:line, checked in review.

Verification: passed (V11, V15)

References:
- Supports: A3; D2, D5
- Depends on: T2

### T6 — Find and fix the missing skill descriptions
Status: implemented — verification pending

What needs to happen: find why code-review, codebase-design, domain-modeling, simple-english, tdd and workflow-doctor show without a description in the Claude Code skill list. Check the host's documented skill-listing limits (primary docs) and measure our description lengths against them. Fix in our files (shorter or front-loaded descriptions). If the cause is outside the package (other plugins' share of the budget), document it in docs and tell the owner.

What should work:
- FINDINGS records the cause with its source.
- Human check: in a fresh Claude Code session after T8's reinstall, the skill list shows the descriptions of the 6 skills.

Technical details:
- May change: frontmatter description lines of skills/*/SKILL.md; validate.py description-length check if a limit is found (test first). Must not change: hooks/, skill names.
- Test seam: validate.py (description length). Misses the host's listing behaviour; covered by the human check.
- TDD: yes if a length check is added; else no (frontmatter text).

Documents: docs/ARCHITECTURE.md or README note if the cause is a host limit

How to verify:
- python -X utf8 -I tools/validate.py
- Human check: the owner opens a fresh session after the reinstall and confirms the 6 descriptions show

Verification: passed (cause E6; fix V12, V15; fresh-session listing V23)
Owner acceptance: Gazoh, 2026-11-12, V23: "yes"

References:
- Supports: A4; D2
- Depends on: T1, T2

### T7 — docs_check skips git-ignored and third-party folders
Status: Verified
Evidence: V5, V10, V7, V14

What needs to happen: today docs_check reads only the top-level .gitignore. Ask Git (read-only) which folders are ignored at any depth and prune them. A tracked folder that holds its own LICENSE file and is not linked from the index is reported once as a third-party folder instead of once per document. Without Git, today's behaviour stays.

What should work:
- Altinstar-react: no notes from UnityClient/Library/PackageCache (ignored by a nested .gitignore).
- PletrixV2/core: one note per ckeditor folder instead of one per file.
- A real unreachable document outside such folders is still reported.

Technical details:
- May change: skills/rule-maker/scripts/docs_check.py, tests/test_docs_check.py, skills/rule-maker/DOCS.md if it describes the skip list. Must not change: other rule-maker scripts.
- Test seam: the docs_check CLI and its functions on temporary repositories with a nested .gitignore and a LICENSE folder. Misses unusual ignore setups (global excludes); Git's own answer covers those.
- TDD: yes.

Documents: skills/rule-maker/DOCS.md if affected

How to verify:
- python -X utf8 -m unittest tests.test_docs_check; rerun on Altinstar-react and PletrixV2/core in T8.

Verification: passed (V5, V10; reviews V7, V14)

References:
- Supports: A5; D6
- Depends on: none

### T8 — Verify, publish, reinstall and run the after-test on the 7 repos
Status: implemented — verification pending

What needs to happen: run validate.py and the full suite; code review of the whole change (code-review skill, fresh context); commit and push workflow-axa (only this task's files; the staged 2026-11-11 records stay out unless the owner says otherwise); reinstall Claude and Codex from Git with README's install commands; run rules_stamp, docs_check and readiness inspect with the installed copy on the 7 repos into .artifacts/2026-11-12-owned-skills-and-repo-test-run/after/; write the before/after comparison and the Altinstar and D:\PletrixV2 rule gaps to FINDINGS; offer the rules reviews.

What should work:
- All checks pass; the after-run differs from the baseline only where T7 intended; application repos unchanged (git status before and after compared).

Technical details:
- May change: VALIDATION.md (tools/verification_summary.py --run --write, approved with this plan), task records. Must not change: application repos.
- TDD: no (verification).

Documents: VALIDATION.md, FINDINGS

How to verify:
- python -X utf8 -I tools/validate.py; python -X utf8 -m unittest discover -s tests -p "test_*.py"; git status of each application repo identical before and after.
- Human check: the T6 fresh-session check; owner acceptance.

Verification: passed (V18, V22; published and reinstalled V19; after-run V20; T6 check V23)
Owner acceptance: Gazoh, 2026-11-12, V23: "yes"

References:
- Supports: A6; D3, D4, D7, D8
- Depends on: T4
