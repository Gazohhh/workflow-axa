# Decisions: owned skills, document review and repo test run

All from the owner via the question tool, 2026-11-12, unless marked `by: agent`.

- D1 (Q1 a): Merge each of the 9 copied skills into one text we own (fold the adaptation in, drop source lines it contradicts). Remove every source mention under skills/. Keep each LICENSE file. Cut VENDORED-SKILLS.md down to a credits and licence note. Retire the hash tables and tools/vendor_specialists.py.
- D2 (Q2 a): Include rule contracts (trigger, scope, blocked behaviour, checker; label hard rule / procedure / judgment call) for the hard rules, plus the skill-listing description check. No paid evaluation.
- D3 (Q3 a): Test run = read-only checks (rules_stamp, docs_check, readiness inspect) before and after the changes, compared.
- D4 (Q4 a): Use current branches; nothing switched or pulled in the application repos.
- D5 (Q5 a): No hook changes. Rules a hook could check become listed hook candidates.
- D6 (Q6 a): Fix docs_check to skip git-ignored paths and known third-party folders, with a regression test.
- D7 (Q7 a): Altinstar and D:\PletrixV2 rule gaps: report only; offer a rules review per repo afterwards.
- D8 (Q8 a): After validate.py and tests pass: commit and push workflow-axa, reinstall Claude and Codex from Git, run the after-run with the installed copy.
- D9 (by: agent): Tests and validate.py checks that compare the source-text hashes inside SKILL.md are replaced by checks that each formerly copied skill keeps its LICENSE and has no source mention under skills/. This changes the contract; it does not weaken a check of current behaviour.
- D10 (by: agent): README.md keeps a short credits line pointing to VENDORED-SKILLS.md; the owner's request covers skills/ only.

- D11: Agreement 1 agreed 2026-11-12 by the owner: "Sure no need for a review codebase mapping design but do document everything in docs so no review.html is needed". No HTML plan report or codebase map for this task; the plan lives in PLAN.md and TODO.md.

## Revision log
- r1 (2026-11-12): tickets T1 to T8, proposed, awaiting approval; no report (D11).

- D12: r1 approved 2026-11-12 by the owner: "Yes go" (T1 to T8; no report).

- D13 (by: agent): for T7, a folder holding a SKILL.md is a skill package, not a third-party folder, even when it keeps a LICENSE (the formerly copied skills here do); its documents keep today's per-file notes.

- D14: Q9 answered 2026-11-12 by the owner: "Approve r1, no report". Replaces the Approval line quote; earlier "Yes go" (D12) stays as history.

- D15 (by: agent): skills/codebase-map/FLOWCHART-DESIGN.md "Provenance, not a dependency" names a source design project (cathrynlavery/diagram-design) with links. It is a source reference under skills/, so T2 removes it and keeps the sentence that the guide is the workflow's own design contract. No licence applies (nothing copied). Credits move to VENDORED-SKILLS.md (T4).

- D16 (by: agent, review finding 3): codebase-design keeps "where the project already has an established name and it is clearer, keep the project's name". It narrows the old "project vocabulary wins" to match the owner's global CLAUDE.md ("keep a project's established names where they are clearer").

- D17 (Q10 a, owner via question tool, 2026-11-12): remove skills/workflow/specialists.json and skills/workflow/scripts/check_specialists.py. Optional specialists stay named in SPECIALISTS.md and are checked when a step needs one. The disk inventory and baseline comparison of external copies are dropped. Tests that read the catalog change with it (T2/T3).

- D18 (by: agent): T6 adds no description-length check. validate.py already refuses a description over 1024 characters, below the host listing cap of 1536; the total listing budget depends on the host and other plugins, so a package-wide total limit would be an invented number.

- D19 (by: agent, review V17): the name of the design project that inspired the flowchart style (lower-case "diagram-design" in text) is also removed from skills/, extending D15; the compatibility file DIAGRAM-DESIGN.md keeps its name. tests/test_owned_skills.py guards it with a case-sensitive pattern; tests/test_package.py follows the new wording.
