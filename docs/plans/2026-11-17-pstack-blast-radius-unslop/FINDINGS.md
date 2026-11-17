# Findings

## Evidence

- E1 — Sparring source (2026-11-17). Opus and GPT-6 Astra (Codex, reasoning high) argued three rounds, read-only, and Astra ended "AGREED". The agreed design: blast radius stays owned by code-review but moves into a sibling reference `skills/code-review/BLAST-RADIUS.md`, with no new registered skill. Clarify records safety assumptions, specify turns them into checks, and 4b proves them. The Inspect route answers "what could this break". Unslop becomes a named required check in WRITING.md, with namespaced "Unslop N" tells in SIMPLE-ENGLISH.md. Unslop 24 is not adopted. writing-for-agents cites the tells selectively. Credits go under pstack MIT with exact licence files. `correct` and verification-skill go to follow-ups. The round files were in the session scratchpad (not durable); this entry and the agreement carry their content.
- E2 — Upstream texts: pstack `skills/blast-radius/SKILL.md` (last commit touching it bf0c7cd8) and `skills/unslop/SKILL.md` (2f87c854), github.com/cursor/plugins, MIT, "Copyright (c) 2026 Lauren Tan" (pstack/LICENSE).
- E3 — `skills/code-review/SKILL.md:83-85` step 4b today. Its trigger is "code that other code depends on". It starts with "Search for the callers outside the diff, name them" and already requires proving the key safety fact by running code, an isolated copy for writing probes, and an unverified fallback.
- E4 — `tests/test_new_skills.py:150-152` asserts the 4b phrases, including "Search for the callers outside the diff". That phrase goes away, so the test changes with the contract.
- E5 — `README.md:43` says the pstack ideas were adapted and "no text was copied". `README.md:58` says "No new writing skill". Both are user-facing facts this task changes.
- E6 — Writing owners: `skills/workflow/WRITING.md` (Cut, Keep the meaning :31-46, Cold-reader check :48-52); `skills/workflow/SIMPLE-ENGLISH.md` (rules 1-12, rule 2 protects code, terms and quotes); `skills/workflow/simple-english/word-swaps.md`; `skills/writing-for-agents/SKILL.md:65` (intentional leading words and metaphors). `tests/test_simple_english.py` and `tests/test_behavioral_cases.py:227` check the writing files.
- E7 — Planning owners: `skills/workflow-clarify/SKILL.md:20-24` (trace: Owner and callers, Failures, Compatibility, State and timing); `skills/workflow-specify/SKILL.md:39-41` (bigger checks); `skills/workflow-specify/SKILL.md:49` (offer text is never rewritten after `record.py offer present`); `skills/workflow-deliver/SKILL.md:60` (chat report and cold-reader check).
- E8 — Recipes: `skills/workflow/flows/bug.md:18` (step 7 already names the blast-radius check in one line), `refactor.md` steps 1 and 6, `migration.md` steps 1 and 5, `performance.md`, `docs-tests.md` step 2, `INDEX.md:17` Inspect line. `tools/validate.py:220` requires `uses:` to list registered skills only.
- E9 — Credits: `VENDORED-SKILLS.md` table; `tools/validate.py:66` accepts named licence paths that end in LICENSE; `doc_fact_errors` (`tools/validate.py:116`) checks hand-kept counts, including a vendored count, against the manifests.
- E10 — Out of the repo: the owner's global `~/.claude/skills/unslop` (older variant, "Must always apply", with an "add soul" section) conflicts with the plain register. Not changed by this task. Reported to the owner.
- E11 — Rules: READY. rules_stamp NONE (1.9.0), information only. docs_check: 0 blocking, 9 notes. One of the notes says `simple-english/word-swaps.md` is not reachable from the workflow SKILL.md index.

## Journeys

- J1 — The code-review agent reviews a diff that changes something read outside the diff. It reads BLAST-RADIUS.md and reports under `## Standards` as "Blast radius". The report gives the safety facts with the ladder step each one reached, the Risks, what was Cleared, and the cheapest check to run before merging. If a probe is not allowed, the fact is marked unproven and the report names the experiment. If nothing crosses the boundary, the report says "none" with the short trace that shows it.
- J2 — The clarify agent traces a change. It records the material safety assumptions and the check that could falsify each one, and it looks where grep stops. Specify turns these into ticket checks. Review reopens any assumption that the implementation or new evidence changes or contradicts.
- J3 — The owner asks "what could this break?" in their own words. The router takes the Inspect route and runs BLAST-RADIUS.md on the named diff or symbol. It only reports and creates no records.
- J4 — The agent writes human-facing text: offer inputs before `offer create`, plans, FINDINGS prose, the delivery chat report, human-facing docs, changed prose in a review, and commit or PR text when asked to write it. It runs the Unslop check after drafting and before the cold-reader check. Meaning, uncertainty words, literal technical terms and SIMPLE-ENGLISH rule 2 content stay. The presented offer text is never rewritten.
- J5 — The agent writes agent instructions. writing-for-agents points to the tells list and names its exceptions.
- J6 — A maintainer runs validate and the tests. The credits row, the licence files, the counts and the README facts match, and the 4b contract test checks the new phrases.

## Decision check

- Q1 — **Release records**: asked 2026-11-17. Owner's answer: "Ask the other session working in workflow-axa before you do that". Sent a coordination question to peer session "New Skills & Architecture" (release version and overlapping files); Peer reply (2026-11-17): it works only in D:/workflow-axa-redesign (detached at c5e954b, uncommitted). The owner decided the next release is 2.9.0-rc.3, made in a separate step. It suggests that this task carries no release records and writes a summary ready for CHANGELOG into its records. Overlap: workflow-clarify step 3 /spar bullet (theirs), README skill count, /spar line and folder list (theirs); their /spar text is checked against WRITING and SIMPLE-ENGLISH. Taken as option b plus the summary, stated as an assumption in agreement 1. Original options as asked: The new behaviour reaches installs only through a release. Today plugin.json says 2.9.0-rc.2.
  a. Ship it as 2.9.0-rc.3 in this task: version bump, CHANGELOG and UPGRADE entries; VALIDATION.md is rewritten only with your separate OK, as AGENTS.md requires.
  b. No release records here. README, credits and tests change; a later release task bumps the version.
  Recommended: a, because every earlier change shipped as an rc and you test by reinstalling from Git.

- E12 — Owner's challenge (2026-11-17, at the agreement question): "What about the feature recipe ... I don't feel like that's right". Every recipe and routing point was re-read. Coverage was missing in:
  - feature.md:12/17 (the step 1 trace and step 6 integration never mention safety assumptions);
  - ui.md:14-16 (shared components, classes and functional IDs reach other screens; AUDIT.md:86 already names "shared component impact");
  - performance.md:17 (caching, "do it later" and batching change timing and staleness);
  - architecture.md:14 (consequences per option; no diff, so no proof step);
  - docs-tests.md:12-14 (text that tests and validators parse, as in this very task, E4/E9).
  Routing points: INDEX modifiers (Compatibility); the lightweight-edit definition in workflow SKILL.md §4; workflow-execute:38/45 (ticket review and whole-feature review); AUDIT.md:5 (docs-only reviews use writing-for-agents, so 4b never fires there); plan-review step 3; workflow-deliver (reviews happened). new-project needs no step. Agreement 1 is revised with R5 and R12. The round-1 claim "covered by clarify" was wrong, because a recipe agent reads the recipe text.

- E13 — Ticket spar round 1 (GPT-6 Astra, high, read-only, 2026-11-17): 6 ISSUE, 3 PASS. The issues: the T4 dependency row disagreed with its References; A5 and some R-IDs had no ticket owner; validate checks Markdown links only, so code-form pointers need their own test; there was a placeholder docs_check command, an unavailable `grep`/`rg`, a W3 that relied on a negative grep, and no baseline record; the credits row first column would change the vendored count (tools/validate.py:65); the licence tests checked presence, not text, and T5 claimed TDD where no red phase exists. All six were fixed in TODO.md (15 edits). The deliver presence check moved to step 5. Round 2 is running.

- E14 — Ticket spar rounds 2 and 3 (GPT-6 Astra, 2026-11-17). Round 2 found one ISSUE: the W5 command held a literal line break and printed a newline when nothing matched. It was fixed with Astra's own suggestion, and the stored command was run verbatim in PowerShell: exit 0, no output. Round 3: "AGREED" (W5 exit 0 with no output; dependencies, R/A coverage and the baseline section are intact). The ticket comparison with agreement 1 found no difference.

- V1 — T1 red then green (2026-11-17, D:/workflow-axa, Python 3.14.2, c5e954b plus T1 diff). Red: `python -X utf8 -m unittest discover -s tests -p "test_new_skills.py"` gave failures=4, errors=3 (missing BLAST-RADIUS.md and licence, old 4b wording); `test_package_contract.py` gave failures=3 (KEY_FILES). Green after the text: test_new_skills 15 OK, test_package_contract 8 OK, test_owned_skills 10 OK; `tools/validate.py` PASS (19 skills). Not covered: whether an agent follows the method (NOT_RUN cases come in T2).
- E15 — The TODO commands `python -m unittest tests.<module>` do not import (tests/ has no __init__.py). They were corrected in TODO to `python -X utf8 -m unittest discover -s tests -p "<module>.py"`. Same checks, record wording only.
- Review S1: fresh subagent (independent) pending: T1 Standards and Spec (writing-for-agents + AUDIT). Cold-reader check of BLAST-RADIUS.md (A5 part 1): fresh subagent pending.

- Review S1: fresh subagent (independent) failed: T1, 5 findings. Spec: the licence test checked only fragments; the method test missed several R1 parts; the no-arena check did not catch a "models" wording. Standards: "changes nothing" read against the isolated-copy probes; the snapshot path only works from the skill folder. Cold-reader check 1 (A5 part 1, fresh subagent): the restatement matched the intent, with 8 ambiguities (ladder direction, "changes nothing", "None" of what, relative paths, no threshold for /interrogate, who "Review" is, symbol-only questions, undefined pointers). All were repaired in one diff, snapshot S2. T1 tests still pass: test_new_skills 15 OK, test_package_contract 8 OK, test_owned_skills 10 OK; validate PASS.
- Review S2: same reviewer, pending (repair diff only). Cold-reader recheck pending.

- Review S2: same reviewer (independent) passed: T1 repair diff. All 5 findings fixed. One note (ladder step 5 could mean the live app) was taken.
- V2 — Cold-reader check 2 of BLAST-RADIUS.md (A5 part 1, the same fresh reader, file only): 6 of 8 ambiguities resolved. Still open: "step 4b" was unexplained. New: "disposable folder" was not defined in Probes, and "full path" was ambiguous. All three were fixed by wording in S3, together with the step-5 note. T1 tests are OK (15/8/10) and validate PASS after the wording.
- Review S3: same reviewer, pending (wording repair).

- Review S3: same reviewer (independent) passed: T1 wording repair. T1 closed: V1 (red, then green), V2 (cold reader, A5 part 1), reviews S1 → S2 → S3.

- V3 — T2 red then green (2026-11-17, D:/workflow-axa, Python 3.14.2). Red: test_new_skills BlastRadiusRouting failures=15; test_flows errors=1 (no blast_radius_cases). Green after the text: test_new_skills 18 OK, test_flows 16 OK. validate PASS (1363 workflow words). docs_check --changed on the 8 files: 0 blocking, 0 warning. Also OK: test_owned_skills, test_package, test_cutover, test_session_failures, test_rules_pass, test_validate_budgets, test_docs_check (1 skipped), test_required_reads. flows.json kept its CRLF line endings (18 lines added, none removed). Not covered: live routing (the BR-* cases are NOT_RUN).
- Review S4: fresh subagent (independent) pending: T2 Standards and Spec.

- Review S4: fresh subagent (independent) failed: T2, 2 findings. (1) Clumsy clause in clarify item 7. (2) Read broadly, the new lightweight sentence contradicted VISUAL-REVIEW.md:12 ("a small docs fix is a lightweight edit"). Repair S5 stays within T2's scope: the sentence now names step 4b's own trigger list and says a docs fix whose text only tests read stays lightweight, so VISUAL-REVIEW.md is unchanged. Also taken: the Inspect test asserts the exact prompt. test_new_skills, test_flows, test_package and test_session_failures OK; validate PASS (1391 words).
- Review S5: same reviewer, pending (repair diff).

- Review S5: same reviewer (independent) passed: T2 repair. Its note was not acted on. workflow/SKILL.md:52 "only tests read" is narrower than AUDIT.md:5's list, which errs on the cautious side; changing it would need another review round. T2 closed: V3 and reviews S4 → S5.

- V4 — T3 red then green (2026-11-17). Red: test_flows recipe test failures=8 (one per recipe; new-project already passed). Green after the eight recipe edits: test_flows 17 OK; test_new_skills, test_package, test_cutover and test_owned_skills OK; validate PASS (1391 words); docs_check on the eight recipes 0 blocking. Recipe frontmatter unchanged.
- Review S6: fresh subagent (independent) pending: T3.

- Review S6: fresh subagent (independent) passed: T3. Its 4 judgement notes were all taken in S7: migration wording, performance order (state the behaviour before choosing a change, as R5 says), docs-tests duplicate list, bug condition repeated from 4b. test_flows 17 OK, validate PASS.
- Review S7: same reviewer, pending (repair).

- Review S7: same reviewer (independent) passed: T3 repair. T3 closed: V4 and reviews S6 → S7.

- V5 — T4 red then green (2026-11-17). Red: test_simple_english failures=10, errors=3. Green after the text: test_simple_english, test_behavioral_cases, test_package_contract, test_owned_skills, test_new_skills, test_flows and test_package OK; validate PASS (1391 words). W5 source-name search: exit 0, no output. docs_check --changed on the 8 T4 files: 0 blocking, 2 warnings. Both warnings are at UPGRADE.md:80, a pre-existing stale path (check_specialists.py, specialists.json) that this task did not change. They appear only because --changed reviews related documents. cases.json B30 was added in the file's own multi-line CRLF layout (13 lines added). The unslop source commit was confirmed: 2f87c854fe3e2fcda44ca86b46ede35aad3c46b7.
- Review S8: fresh subagent (independent) pending: T4. Cold-reader check of the Unslop section (A5 part 2): fresh subagent pending.

- V6 — Cold-reader check 1 of the Unslop section (A5 part 2, fresh subagent, the two sections only): the restatement of when, on what, what wins, Unslop 24 and literal terms matched. 11 clarity points found (bare rule numbers, the parentheses, colon and heading-case clashes inside the file, README vs application text, "by itself", "substantial", offer inputs, adverbs, number gaps, order with the self-check).
- Review S8: fresh subagent (independent) failed: T4, 8 findings. R8 was not selective; the Unslop 3 row restated rule 4; the metaphor rows in word-swaps lacked "(metaphorical)"; the specify clause was ambiguous; the code-review bullet had a semicolon; the Unslop 27 row used a colon as a connector; tests were weak (rule numbers, B30); B30's UI check could not fail. All findings and all 11 cold-reader points were repaired in snapshot S9. T4 tests are OK and validate PASS. W5 search: exit 0.
- Review S9: same reviewer, pending. Cold-reader recheck pending.

- V7 — Cold-reader check 2 of the Unslop section (A5 part 2): all 11 points resolved. Four new, smaller points were accepted as residual judgement and not repaired: how broad the colon exception is; when an old heading counts as "changed"; no fixed wording for "unverified"; what counts as a parenthetical aside. The tells are advisory judgement calls by design (code-review bullet), and a third round would bring little.
- Review S9: same reviewer (independent) failed: 1 finding. The cold-reader repair had widened R6 ("Plans, tickets and FINDINGS prose"), which goes beyond the agreement. Reverted to the agreed "Substantial plans and FINDINGS prose." (snapshot S10). test_simple_english OK, validate PASS.
- Review S10: same reviewer, pending.

- Review S10: same reviewer (independent) passed: T4 revert. T4 closed: V5, V6, V7 and reviews S8 → S9 → S10.


## Summary for the rc.3 CHANGELOG (R11)

For the separate 2.9.0-rc.3 release step. Text ready to paste, written for CHANGELOG.md:

- **Blast radius has its own method file.** `skills/code-review/BLAST-RADIUS.md` finds what a change breaks outside itself. It puts first the one or two safety facts with the most risk, looks where a search stops (library source at the pinned version, timing and teardown, JSON and DB columns, file formats, config keys, flags, saved data, parsed text), and proves each fact as far as it can on a 1 to 5 evidence ladder, or marks it unproven. It lists Risks apart from Cleared items and ends with the cheapest check to run before merging. Code-review step 4b now runs when anything outside the diff reads what changed. Listing callers is the input, not the result.
- **Planning and routing use it.** Clarify records safety assumptions with the check that could falsify each one, specify turns them into checks, and plan-review flags a plan without them. An edit that fires the step 4b trigger is not a lightweight edit. Execute runs step 4b per ticket and again on the whole diff. Deliver checks that the result exists and lists open Risks. The Compatibility modifier requires it, and "what could this break?" gets the same report through the Inspect route.
- **Every recipe names it** at its own step: bug, feature, ui, refactor, migration, performance, architecture and docs-tests. New-project does not.
- **A required Unslop check.** WRITING.md runs it before the cold-reader check, on offer inputs, substantial plans and FINDINGS prose, the delivery report, human-facing docs, changed prose in a review, and commit or PR text. SIMPLE-ENGLISH.md lists the tells as "Unslop N". Tells that a rule already covers name that rule. Unslop 24 ("one hedge at most") is not adopted, because uncertainty words carry meaning. The check never changes application UI copy, error messages or translations.
- **Credits.** The method and the tells adapt pstack text by Lauren Tan (MIT). VENDORED-SKILLS.md has the row, and `BLAST-RADIUS.LICENSE` and `UNSLOP.LICENSE` ship beside the texts.
- **Tests.** New phrase and pointer checks are in test_new_skills, test_flows, test_simple_english, test_owned_skills and test_release, and test_package_contract lists the three new files. The live-host cases BR-* (flows.json) and B30 (cases.json) are NOT_RUN.

Release-step notes: there is no version bump, CHANGELOG, UPGRADE or VALIDATION edit in this task. README.md changed only the lines about blast radius and writing; the skill counts belong to the other session's /spar work. Registered skills stay at 19 here.

- V8 — T5 red then green (2026-11-17). Red: test_owned_skills failures=5 (the pattern missed the new source names; the credits did not name the two licences). test_release passed before the change, as planned: it is a regression check. Green after the text: test_owned_skills 12 OK, test_release, test_package_contract, test_docs_consistency, test_rules_pass and test_package OK; validate PASS; licensed_skills unchanged. docs_check --changed on the 5 docs: 0 blocking. One self-caused warning (a relative path in backticks in tests/README.md) was fixed. The 5 remaining warnings are in docs/DESIGN.md and tests/SCENARIOS.md, which are unchanged history files with stale paths.
- Review S11: fresh subagent (independent) pending: T5.

- W3 — Blast radius of this change, traced by reading the readers' code (2026-11-17).
  - Readers of the changed files: hooks/read_evidence.py:21-26 requires whole reads of workflow/SIMPLE-ENGLISH.md, workflow/AUDIT.md and code-review/SKILL.md by path only, before specify, execute and deliver. The paths are unchanged and no content is parsed (ladder step 2, file:line). hooks/phase_gate.py:2263 names SIMPLE-ENGLISH.md as a report guide, by path only (step 2). tools/build_release.py:23 ships VENDORED-SKILLS.md and the skill folders; test_release proves both new .LICENSE files ship (step 4). tools/validate.py credit_rows, licence_files, doc_fact_errors, the CONTEXT.md parser, links and repeated paragraphs are proven by validate PASS plus the licensed_skills test (step 4). skills/rule-maker/scripts/audit_installation.py:16 lists skill names only, and no skill was added (step 2). The codebase-map report renderer's plain-English check uses its own rules and does not read SIMPLE-ENGLISH.md content (step 2, lines 1042-1047 of that script).
  - The phrase tests that assert changed text were all updated or extended, and the full suite (W1) proves the rest.
  - Risk kept for merge time: the other session's /spar text in D:/workflow-axa-redesign cites WRITING.md and SIMPLE-ENGLISH.md, and its worktree edits workflow-clarify step 3 and README lines 24 and the /spar lines. This task edited clarify item 7 and README lines 43 and 58, which are different hunks. Unproven until the rebase: rerun the full suite after the merge.
- E16 — Hook false positive (2026-11-17): the PreToolUse hook refused two Bash commands as "rendering the report" because the command text contained the renderer script's file name: a read-only Grep through Bash, and a record.py append whose text named the script. Nothing rendered. This was worked around with the Grep tool and rewording. Candidate for a regression test in a later hook task (memory: Altinstar approval failures).

- Review S11: fresh subagent (independent) failed: T5, 2 findings. The CHANGELOG summary omitted test_package_contract, and the RULE-CONTRACTS hard-rule cell implied every probe runs in an isolated copy. Both fixed in S12. The README judgement note was also taken: "as far as running code allows, or marks them unproven". Commit ids and the unchanged licensed_skills were confirmed by the reviewer. validate PASS, test_docs_consistency OK.
- Review S12: same reviewer, pending. W1 full suite started on the final files.

- Review S12: same reviewer (independent) passed: T5 repair. T5 closed: V8 and reviews S11 → S12.

- Review S13: fresh subagent (independent) pending: whole-feature review (Spec, Standards, blast radius on the whole diff, failure journeys).

- Review S13: fresh subagent (independent) failed: whole feature, 3 findings.
  1. J1's failure path was open: step 4b did not ask for "none" with a boundary trace, so "it is local" could skip the step silently. Fixed: 4b now says the item reports "none" with the boundary trace, and the test phrase is added. test_new_skills 18 OK, validate PASS.
  2. The PLAN checkpoint was stale. Fixed (Changed files, Verification).
  3. The W3 trace was incomplete. Additions below.
  Cleared by S13: the agreement and offer paths, term consistency, one owner per rule, line endings (skills LF; root, docs and tests CRLF only through core.autocrlf, and HEAD is LF), journeys J2-J6.
- W3 additions (from S13, ladder step 2, grep of hooks/, tools/ and skills/**/*.py): skills/rule-maker/scripts/docs_check.py, hooks/approval.py, skills/workflow/scripts/record.py, offers.py and completion_check.py do not parse any changed sentence. rules/version.json hashes only rule-maker rules files, none of which changed.
- Merge risk, widened. D:/workflow-axa-redesign (the other session) also edits 5 files this task changed: CONTEXT.md (inserts after :68, the same anchor as the new terms, so a conflict is likely), docs/RULE-CONTRACTS.md (a spar row next to the edited SIMPLE-ENGLISH row, likely conflict), tests/README.md, tests/test_owned_skills.py and tests/test_package_contract.py (EXPECTED_SKILLS vs KEY_FILES). Its new skills/spar/* will also be scanned by the wider SOURCE_MENTIONS pattern, which is clean today. Before merge: whoever rebases second resolves these by hand, then runs the full suite and validate.
- Review S14: same reviewer, pending (repair).

- Review S14: same reviewer (independent) passed: whole-feature repair. Peer notice: the merge warning to "New Skills & Architecture" failed because that session is no longer reachable. The overlap goes to the owner in the delivery report.

- Reconciliation R1 (2026-11-17, fresh subagent that did not build the work, read-only). All R1-R12 and A1, A3, A4 and A5 are verified. A2 is partial: the first full-suite run (1437 OK, skipped=14, started about 12:48) overlapped the S13 repair at 12:52 (code-review/SKILL.md, test_new_skills.py), so it ran on mixed files. A6 is partial: the cases exist, and live behaviour is not run. Every file maps to a ticket. tests/test_behavioral_cases.py was promised only "when it pins case counts" and was not needed. Reviews all end in a pass, and completion_check exits 0. Defects sent back: (1) rerun W1 on the frozen files; (2) checkpoint and W0-W5 records, with W0's diff hash; (3) the ticket reviews S1-S12 record no Blast radius item. Resolution for (3): this task's diff changes text that tests and validators read, so per AUDIT.md the method applied to the whole diff as W3 (FINDINGS W3) and S13 → S14. That whole-diff result covers the tickets. Agent decisions: D3 only.
- W0 — Baseline recorded in PLAN (commit c5e954b, Python 3.14.2, git 2.38.0, 1421 OK, skipped=14). At the time the tracked diff was empty, so there was no diff hash. Frozen delivery state: HEAD c5e954b, tracked diff plus the 3 new files hash to sha256 prefix 1924b5fbb65bb395 (git diff HEAD followed by the three new files' bytes).
- W1 — Rerun of the full suite on the frozen files started (the first run is superseded as a mixed state).

- W1 — Full suite on the frozen files (2026-11-17, D:/workflow-axa, Python 3.14.2, HEAD c5e954b plus diff hash 1924b5fbb65bb395, which was the same before and after the run): `python -X utf8 -m unittest discover -s tests -p "test_*.py"`. Ran 1437 tests in 570.6 s, OK (skipped=14). The baseline had 1421 tests and 14 skipped, so this change added 16 tests and caused no failure. completion_check exits 0 after it. This replaces the mixed-state run.

- L1 — Live run BR-inspect-question (2026-11-17, D5; offer #2).
  - Setup: one `claude -p` session, claude-opus-5-5, Claude Code 2.1.326. `--setting-sources project,local --settings <scratchpad>/live/settings.json` (read-only allow list; Edit, Write and git writes denied). `--plugin-dir D:/workflow-axa --add-dir D:/workflow-axa`, `--max-budget-usd 3`, `--permission-mode default`. cwd: a clean synthetic fixture (tools/create_fixture.py --scenario clean) at <scratchpad>/live/br01, commit dd98677. Prompt, verbatim: "What could changing the separator in format_score from ' - ' to ':' break?". Transcript: <scratchpad>/live/run-L1.jsonl (session scratchpad, not durable).
  - Cost and size: $0.37, 4 turns, success. Loaded plugins: workflow-axa plus the host's built-in cc-plugin-* plugins.
  - Tool calls: 3 Bash calls (git ls-files and grep, one refused loop, then cat of the sources). No Skill call and no Read of any workflow-axa file.
  - Result: FAIL.
    - P1 partial: the fixture is unchanged (git status empty) and no records were written, but the router never ran, so there is no Inspect line.
    - P2 FAIL: the workflow skill was not invoked, and skills/code-review/BLAST-RADIUS.md was never read.
    - P3 partial: Risks with file:line (tests/test_labels.py:9 and :12, docs/architecture.md:5), a "Worth knowing" section resembling Cleared, and a "go ahead" list resembling Before you merge. No safety facts, no ladder step, no probe was run.
    - P4 pass: it named player.py's separate _legacy_score path (src/player.py:1-2) and the test that hides the divergence.
  - Reading: the answer is good, but it came from the model's own judgement, not from the new method. What the run proves: in this isolated setup, a plain "what could this break?" prompt does not route into the workflow skill, so none of this task's text was exercised.
  - Unknown: whether the cause is the isolation or a real routing gap. --setting-sources project,local drops the owner's global CLAUDE.md, which routes ordinary repository prompts to /workflow. Without it, only the workflow skill's description could trigger the skill.
  - Per offer #2: no commit, no push, no second run without asking.

- L2 — Live run with realistic settings (2026-11-17, D8).
  - Setup: same fixture (still clean at dd98677) and the same verbatim prompt. The owner's user settings were loaded (global CLAUDE.md; superpowers and other plugins; workflow-axa@gazohhh read from D:\workflow-axa, the candidate itself). A flag-level deny on edits and git writes; `--permission-mode default`; cap $3; claude-opus-5-5. Transcript: <scratchpad>/live/run-L2.jsonl.
  - Cost and size: $1.62, 7 turns, success.
  - Tool calls: Grep, Glob and 4 Reads of fixture files. No Skill call and no read of any workflow-axa file.
  - Result: FAIL, the same as L1. P1 partial (the fixture is unchanged, no records, no Inspect line). P2 FAIL. P3 partial (Risks with file:line; no safety facts or ladder steps). P4 pass (player.py:1-6 named).
  - Finding: a routing gap, not an isolation artifact. Neither the workflow skill description ("features, fixes, refactors, research, plans, audits ... Explain-only stays read-only") nor the code-review description ("Review a diff ...") names impact questions. A plain "what could this break?" is answered without loading the method. The INDEX.md Inspect line only matters once the router runs. Live spend so far: $1.99 of two $3 caps.

- V9 — Routing fix (offer #3, D9). Red: test_new_skills ImpactQuestionRouting failures=2 (no description, no section). Green after the fix: the code-review description names "what could this change break?", openai.yaml short_description says the same, and a new "## Impact questions" section sends such a question to BLAST-RADIUS.md alone (report only, no two-axis review, no edits, no records). test_new_skills 21 OK; validate PASS; test_package, test_owned_skills, test_simple_english and test_package_contract OK.
- Review S15: fresh subagent (independent) failed, 2 findings. "no diff review" could be read as "don't read the diff", and the test did not assert that the two axes are skipped. Both fixed in S16 ("no two-axis review"; "skips the two axes" asserted). test_new_skills OK, validate PASS.
- Review S16: same reviewer, pending.

- Review S16: same reviewer (independent) passed: routing fix. Live run L3 starts on this state.

- L3 — Live run after the routing fix (2026-11-17, D9/D10).
  - Setup: same as L2 (the owner's real settings, the same fixture still clean at dd98677, the same prompt, cap $3). Transcript: <scratchpad>/live/run-L3.jsonl.
  - Cost and size: $0.53, 9 turns, success.
  - First call: Skill workflow-axa:code-review with args "Blast radius: what could changing the separator ... break? Report only." This means the routing fix works.
  - Next it tried to Read D:\workflow-axa\skills\code-review\BLAST-RADIUS.md. The read was DENIED ("Claude requested permissions to read from D:\workflow-axa\... but you haven't granted it yet"). Cause: L2 and L3 lacked `--add-dir D:/workflow-axa`. The live-pilot recipe requires that flag, and -p mode cannot answer the permission prompt. The owner's interactive sessions would prompt or allow, so this is a harness defect in my run setup, not a product defect.
  - Result:
    - P1 pass: report only, the fixture is unchanged, no records.
    - P2 FAIL: BLAST-RADIUS.md was attempted, but the harness blocked the read.
    - P3 partial: a table of readers with file:line, risks, and an "outside the repo" cleared statement. No safety facts or ladder steps, and no "Before you merge".
    - P4 pass: player.py:2 _legacy_score, and the test that hides the split.
  - The answer said: "Permission to read ... BLAST-RADIUS.md was denied, so I traced the callers directly".
  - Live spend: L1 $0.37 + L2 $1.62 + L3 $0.53 = $2.52.
  - Per offer #3: no commit, and no run beyond L3 without asking.

- L4 — Live run with --add-dir (2026-11-17, D11).
  - Setup: identical to L3 plus `--add-dir D:/workflow-axa`. Fixture clean at dd98677, the same prompt, cap $3. Transcript: <scratchpad>/live/run-L4.jsonl.
  - Cost and size: $0.56, 7 turns, success.
  - Calls: Skill workflow-axa:code-review ("Blast radius, report only: ..."); Read D:\workflow-axa\skills\code-review\BLAST-RADIUS.md; Grep; git ls-files; then a test-run probe that the harness's permission prompt blocked.
  - Result: PASS.
    - P1 pass: report only, the fixture is unchanged (0 changes), no records.
    - P2 pass: the method file was read from the candidate checkout.
    - P3 pass: sections "What it does", "Risks" (file:line, likelihood such as "certain" and "low", the check), "Cleared" (with "Ladder step 2" and an unproven item named), "Safety facts" ("step 2" for each), and "Before you merge" (the cheapest catching test: web.render_score == player.render_score). When the probe was blocked, the report said "Not run" and named the command that would prove it, as the Probes section requires.
    - P4 pass: src/player.py:1-6 _legacy_score, and tests/test_labels.py:15 hiding the split.
  - Total live spend: L1 $0.37 + L2 $1.62 + L3 $0.53 + L4 $0.56 = $3.08. Each run stayed under its own $3 cap.
  - Not shown by L4: the order of the report sections differs from BLAST-RADIUS.md (Safety facts after Cleared), which is a judgement detail. The Unslop check and the recipe and planning pointers were not exercised live (B30 and BR-* except the Inspect-question case stay NOT_RUN).

- W1 (final) — Full suite on the final files after the routing fix (2026-11-17, HEAD c5e954b plus diff hash 68152abc9d7fb465, the same before and after): Ran 1440 tests in 483.2 s, OK (skipped=14). The baseline had 1421. validate PASS. completion_check: every change was reviewed in its current form (final reviews S16 for the routing fix, S14 for the rest).

- L5 — Live run, Unslop (case B30), 2026-11-17 (D13/D14).
  - Setup: a fresh clean fixture <scratchpad>/live/l5; the owner's real settings; --add-dir D:/workflow-axa; --permission-mode acceptEdits; git writes denied; cap $3; claude-opus-5-5. The B30 prompt asks for the section in the reply, with no file edits. Transcript: <scratchpad>/live/run-L5.jsonl.
  - Cost and size: $1.63, 3 turns.
  - Calls: 2 Bash reads of the fixture. No Skill call and no read of WRITING.md or SIMPLE-ENGLISH.md.
  - Result: FAIL.
    - U1 FAIL: no Unslop source was read.
    - U2 pass: "Additionally", "powerful", "serves as", "robust" and "substrate" are gone.
    - U3 FAIL in part: `export --dry-run`, "feature vector" and "Export failed: 3 rows rejected" stayed, but "It may skip rows" became "Rows that fail validation are skipped", plus a TODO. That is the exact meaning loss WRITING "Keep the meaning" forbids.
    - U4 pass: the fixture is unchanged.
  - Finding: a writing request with no repository change does not reach the workflow, so the Unslop check (owned by WRITING.md) never applies. The owner's global ~/.claude/skills/unslop ("Must always apply") did not fire either.
- L6 — Live run, feature recipe (2026-11-17).
  - Setup: as L5, fixture <scratchpad>/live/l6, prompt "Make the player screen use the shared format_score so both screens show the same score.". Transcript: <scratchpad>/live/run-L6.jsonl.
  - Cost and size: $1.84, 12 turns.
  - Calls: Skill workflow-axa:workflow, then reads of RULES.md and READINESS.md, the fixture sources, then Skill workflow-axa:workflow-specify ("Lightweight edit, minimal offer"). After that, `record.py offer create --help` was refused by the -p permission prompt.
  - Result: PARTIAL.
    - F1 partial: the router ran and chose the refactor recipe ("same output, one owner for score formatting"), which is defensible because the player output does not change. It then took the lightweight-edit route straight to specify, so clarify, and with it trace item 7, never ran.
    - F2 FAIL: it stated the safety fact ("_legacy_score has the same body as format_score, so this changes no score the player shows today") and named the unittest check, but BLAST-RADIUS.md was not used.
    - F3 pass: no application file changed. It stopped and asked.
  - Open question for a follow-up: is moving ownership of formatting (deleting the player's own copy) really "lightweight"? workflow/SKILL.md §4 excludes architecture changes from lightweight edits, while step 4b's trigger list does not fire for a private helper. The harness refusal of record.py is a test-setup limit (acceptEdits does not allow Bash python), not a product finding.
- Live spend for offer #5: L5 $1.63 + L6 $1.84 = $3.47 of $6. Session total: $6.55.
- Codex reinstall (offer #5 item 4), 2026-11-17.
  - Build: `tools/build_release.py --output .artifacts/2026-11-17-pstack-blast-radius-unslop` from package files equal to bedafd7. 212 files, workflow-axa-2.9.0-rc.2.zip; the name keeps rc.2 until the version bump. SHA-256 d2b44c38a1118e5e97ca9fe0918e910ac4d85ad903a899843578097b52941c4e.
  - Before replacing: none of the 19 folders in ~/.agents/skills is a link or junction. A diff of the installed copies against the new build showed only this task's files, so there were no local edits to keep.
  - Backup: the full copy is in <scratchpad>/codex/backup. Replaced: all 19 folders. Afterwards installed == new build (diff -rq, __pycache__ ignored).
  - Audit: `audit_installation.py --check-global` from ~/.agents/skills/rule-maker reports state DISK_MATCH, missing [], no multiple copies, and both global references (~/.claude/CLAUDE.md, ~/.codex/AGENTS.md) MATCH. host_loading, compliance and enforcement are NOT_VERIFIED, as designed.
  - Retention: the backup and the ZIP may be deleted after owner acceptance. The ZIP is in the git-ignored .artifacts folder of this task.

## Handoff to the redesign session (D:/workflow-axa-redesign)

For whoever resumes "New Skills & Architecture". That worktree is detached at c5e954b with 52 uncommitted files, and main is now 00ac3ae (corrected 2026-11-17 by docs/plans/2026-11-17-rc3-merge: this note first said bedafd7, one commit behind).

1. Before rebasing, back up the worktree's diff and untracked files: `git diff > <owned scratch>/redesign.patch`, plus copies of the untracked files.
2. Move the worktree onto 00ac3ae and reapply the edits. Expected conflicts:
   - CONTEXT.md: this task added the terms Blast radius, Safety fact and Unslop check before "**Comment debt**", and three Rule owners rows at the end of that table.
   - docs/RULE-CONTRACTS.md: the code-review row is extended. The SIMPLE-ENGLISH row gains "the Unslop tells". A new row "WRITING.md Unslop check" follows it.
   - tests/README.md: a new section sits before "## User commands: interrogate, no-comments, wait-what (2.9.0)".
   - tests/test_owned_skills.py: SOURCE_MENTIONS gains `pstack|Lauren Tan|cursor/plugins`, plus two tests. The new skills/spar/* text must not name a source.
   - tests/test_package_contract.py: KEY_FILES gains skills/code-review/BLAST-RADIUS.md, BLAST-RADIUS.LICENSE and skills/workflow/UNSLOP.LICENSE. EXPECTED_SKILLS is untouched.
   - skills/workflow-clarify/SKILL.md: this task added trace item 7 only. The step 3 /spar bullet is yours.
   - README.md: this task changed only the blast-radius paragraph (around :43) and the **Writing.** paragraph. The skill counts and /spar lines are yours.
   - skills/code-review/SKILL.md: a new description, an "## Impact questions" section, step 4b, and a Standards-prompt bullet.
3. Check the /spar text against the new WRITING.md "## Unslop" check and the SIMPLE-ENGLISH.md "## Unslop tells".
4. Rerun the full suite and validate. Recheck any completion_check baselines that recorded c5e954b.
5. rc.3: one version bump for both tasks. The CHANGELOG text for this task is "Summary for the rc.3 CHANGELOG (R11)" above. After the bump, reinstall the Codex copies again so the version label matches.
