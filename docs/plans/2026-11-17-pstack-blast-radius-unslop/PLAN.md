# Adopt pstack blast-radius and unslop

## Current checkpoint
- Updated / phase: 2026-11-17; delivered — awaiting owner acceptance (offer #5 items done)
- Recipe: docs-tests; modifiers none — only agent instructions, reference docs, credits and test fixtures change; no hook or script behaviour; scope: the task (proposed); classification question: not asked
- Agreement (gate one): agreed — agreement 1 as revised (R1–R12), 2026-11-17, owner answered "Agree"; DECISIONS D1
- Offer: #5 (89fff7cf484c6c8b), owner answered "Approve from this summary" 2026-11-17 (DECISIONS D14); supersedes #1-#4
- Implementation: implemented (T1-T5 verified)
- Verification / owner acceptance: verified (full suite 1440 OK; validate PASS); live: L4 PASS (impact question), L5 FAIL (Unslop not reached), L6 PARTIAL (lightweight route skipped the safety assumptions); Codex install DISK_MATCH; owner acceptance pending
- Blockers: none
- Changed files: 34 tracked and 3 new files, all on the offer #1 path list (git diff --name-only HEAD; new: skills/code-review/BLAST-RADIUS.md, skills/code-review/BLAST-RADIUS.LICENSE, skills/workflow/UNSLOP.LICENSE); task records in this folder
- Next safe action: owner decides on follow-ups (a) Unslop reach, (b) the lightweight boundary; the redesign session rebases and does rc.3 (FINDINGS handoff)

## Working context
- Owner: Gazoh; repository D:\workflow-axa, branch main, clean at start (HEAD c5e954b)
- Identity: new task; source is the 2026-11-17 sparring session (Opus vs GPT-6 Astra, three rounds, AGREED). Rounds kept in the session scratchpad (sparring/R1-opus.md … R3-final.md); FINDINGS E1 summarises them because the scratchpad is not durable.
- Rules: READY / AGENTS.md, CONTEXT.md, shared START, CORE, READINESS read; rules_stamp NONE (1.9.0, information only); docs_check 0 blocking / scope: this task / limits: installed copies under ~/.agents/skills are not changed
- Test output: none planned outside the test suite's own temp dirs

## Goal and acceptance
Bring pstack's blast-radius method and unslop writing checks into workflow-axa in the agreed shape: one owner per rule, no new registered skill.

## Baseline before this change
- Command: `python -X utf8 -m unittest discover -s tests -p "test_*.py"`, from D:/workflow-axa, 2026-11-17 during specify.
- State: commit c5e954b3fb2bf91b8e3940997f723882cdcc8163, no tracked changes (only this untracked task folder); Windows 11, Python 3.14.2, git 2.38.0.windows.1.
- Result: Ran 1421 tests in 486.5 s, OK (skipped=14). No failing test. Output kept at the session scratchpad `baseline-unittest.txt` until delivery.
- `python -X utf8 -I tools/validate.py`: PASS (19 local skills, 1346 workflow words); NOT RUN host validation.
- Reuse only while the commit, the tracked diff and these versions still match; otherwise rerun before the first edit (W0).

## Agreement

Agreement 1, proposed 2026-11-17. Source: the sparring design (FINDINGS E1), the owner's request, and Q1 (FINDINGS).

### Requirements
- R1 — New reference `skills/code-review/BLAST-RADIUS.md`, the single owner of the blast-radius method, adapted from pstack. Callers are the input, not the result. It finds the safety facts the change rests on, putting first the one or two that carry the most risk, with no cap on material facts. It follows the 1–5 evidence ladder and says which step each fact reached. It looks where grep stops: library source with its pinned version and local patch, timing, teardown and async order, JSON or API shape, a DB column, a wire or file format, another language, a config key, a feature flag, saved data, and downstream hops. It lists Risks (how the change breaks, file:line, likelihood, cost, check) separately from Cleared items. It ends with "Before you merge", the cheapest test or repro. "None" means no cross-boundary dependency was found, shown by a short boundary trace. The probe limits move with the method: the OPERATIONS diagnostic allowance, an isolated copy through interrogate's snapshot.py, and "unproven" plus the experiment when a probe can't run. There is no arena step. A wide change gets a recommendation of `/interrogate`, which the user starts. (E1, E2, E3)
- R2 — code-review step 4b keeps the step. Its trigger widens to anything outside the diff that reads what changed. It links to BLAST-RADIUS.md, puts its result under `## Standards` as "Blast radius", and only reports. (E3)
- R3 — The clarify trace records the material safety assumptions and the check that could falsify each one, pointing to the method by package-relative path. Only our own lines change: the other session's step 3 `/spar` bullet stays as is. (E7, peer reply)
- R4 — Specify step 3 turns those assumptions into ticket checks. Step 4b reuses them and reopens any assumption that the implementation or new evidence changes or contradicts. (E7)
- R5 — Every recipe was checked (FINDINGS E12). Each recipe names the method where its own steps meet it. `uses:` stays unchanged.
  - bug: step 7 already names it. Name the assumptions and the 4b proof.
  - feature: step 1, when the feature changes existing behaviour, records the safety assumptions for the callers and consumers it changes. Step 6 checks the integration and proves them in review. A purely additive feature records "none" with its boundary trace.
  - ui: step 3 or 4, when a shared component, class, functional ID or text key is edited, names the other screens and code that use it. Step 5 checks at least one of those other screens on screen (ladder step 5).
  - refactor: step 1 "Map the contract" uses the method; step 6 proves it.
  - migration: step 1 "Inventory consumers" uses the where-grep-stops list; step 5 proves it.
  - performance: before step 5, state the behaviour that must not change. A cache, deferral, batching or reorder ("do it once", "do it later") gets the method for stale data, order and teardown risks.
  - architecture: step 3 uses only the where-grep-stops list to find what each option touches. There is no diff yet, so there is no proof step.
  - docs-tests: step 1, when the text is read by a tool, test, validator or other document (parsed sections, asserted phrases, links, counts), names those readers. Step 3 proves them by running them.
  - new-project: no step. Nothing exists outside the change yet.
- R12 — Routing points outside the recipes (FINDINGS E12):
  - The INDEX Inspect line answers "what could this break" by running BLAST-RADIUS.md, report only.
  - The Compatibility modifier requires the method, because its subjects (saved data, public interfaces, versions) are the trigger.
  - A lightweight edit whose 4b trigger fires is not lightweight and gets the one-ticket offer.
  - workflow-execute: the per-ticket review runs 4b when the trigger fires. The whole-feature review runs it again on the whole diff, because tickets can combine into a break that no single ticket shows.
  - Docs-only review: AUDIT.md uses writing-for-agents, not code-review, so 4b never runs there. AUDIT names the method for docs and instruction changes that tools or tests read.
  - plan-review flags a plan that changes something read outside its files but records no safety assumptions and no checks.
  - workflow-deliver checks that a fired trigger has a Blast radius result, and lists open Risks and unproven facts under limitations.
- R6 — WRITING.md gets a named required check, "Unslop". It runs after drafting and before the cold-reader check. It applies to offer inputs before `offer create` (never the presented offer text), substantial plans, FINDINGS prose, the delivery chat report (named in deliver step 8), human-facing docs (docs-tests step 2), changed prose hunks in code-review, and commit or PR text when asked to write it. It never changes application UI copy, error messages or translations by itself. A change to text users see is an open choice for the owner. (E6, E7)
- R7 — SIMPLE-ENGLISH.md owns the tells list. Each tell is numbered "Unslop N" with the upstream number, and numbers that are not adopted leave gaps. Unslop 24 is not adopted because it conflicts with "Keep the meaning". Banned words count only in figurative use: literal technical terms and rule 2 content stay. The new vocabulary goes to word-swaps.md. (E6)
- R8 — writing-for-agents cites the tells list selectively and names its exceptions: intentional leading words and metaphors, at writing-for-agents:65. (E6)
- R9 — Credits. Add a pstack row to VENDORED-SKILLS.md (Lauren Tan, MIT, the commits actually copied), plus `skills/code-review/BLAST-RADIUS.LICENSE` and `skills/workflow/UNSLOP.LICENSE`. Existing licence files stay untouched. In README.md, only the lines about pstack and writing change (around :43 and :58). The skill-count lines belong to the other session. (E5, E9)
- R10 — Tests. The 4b contract test checks the new phrases instead of the removed one. Tests cover the licence files and credits. New behavioural cases, labelled NOT_RUN, cover: a hidden consumer that grep does not find, a denied probe marked unproven, a local change with its boundary trace, natural-language Inspect routing, and an Unslop pass that keeps uncertainty words and literal commands. No new test hard-codes the skill count. (E4, peer reply)
- R11 — A summary ready for CHANGELOG goes in this task's records, for the shared rc.3 release step. (Q1, peer reply)

### What happens
- J1–J6 in FINDINGS describe each actor's success and failure paths.

### Stays the same
- No new registered skill. No change to hooks or scripts. Existing SIMPLE-ENGLISH rules 1–12, WRITING "Keep the meaning", interrogate and no-comments stay. Already-written docs are not swept retroactively.

### Not included
- Release records: plugin.json, marketplace.json, rules version.json, CHANGELOG, UPGRADE and VALIDATION. These are left to the separate rc.3 release step.
- Installed copies under ~/.agents/skills and the owner's global ~/.claude/skills/unslop.
- The pstack `correct` loop in rule-maker (REDESIGN:514 gap) and create-/maintain-verification-skill. These are follow-ups.
- Commits, pushes and installs.

### Acceptance
- A1 — `python -X utf8 -I tools/validate.py` passes.
- A2 — The targeted tests from tests/README.md pass, then the full unit suite. Failures that existed before are named separately.
- A3 — The 4b contract test fails on the old text and passes on the new.
- A4 — Each recipe or skill line named in R3–R8 exists and links to the method or check by a valid path (validate's link checks).
- A5 — A fresh reviewer reads BLAST-RADIUS.md and the Unslop section cold and restates when to use them and what they produce, with no mismatch.
- A6 — The new behavioural cases exist and are labelled NOT_RUN. Live agent behaviour stays unproven until an observed host run.

### Assumptions you can reject
- The rc.3 release step is separate and was already decided by you. This came from the other session's message, not from your own words.
- Merge order: whoever merges second rebases onto the other. The other session's /spar text is re-checked against the new tells list at that point.

## Outcome

Delivered 2026-11-17 (agreement 1, offer #1).

- Asked: fit the pstack blast-radius and unslop skills into the workflow. The design was sparred with GPT-6 Astra (3 rounds, AGREED). After the owner's challenge it covers every recipe, and the tickets were sparred again (3 rounds, AGREED).
- Built: T1-T5, all verified. 34 tracked files changed and 3 new: skills/code-review/BLAST-RADIUS.md, BLAST-RADIUS.LICENSE, skills/workflow/UNSLOP.LICENSE. All are on offer #1's path list, and no excluded file was touched.
- Verdicts: R1-R12 verified. A1 verified (validate PASS). A2 verified (W1: full suite 1437 OK, skipped=14, on the frozen files; baseline 1421 OK). A3, A4 and A5 verified (V1, pointer tests, cold readers V2 and V7). A6 partial: the behavioural cases BR-* and B30 exist, and live agent behaviour is unverified because no host run happened.
- Reviews: every ticket and the whole feature had a fresh independent subagent on both axes, and each ends in a pass (S3, S5, S7, S10, S12; whole feature S14). The blast radius of this change itself is W3 and S13/S14. Reconciliation R1 was done by a fresh subagent.
- Limitations: live behaviour is not run (A6). Installed copies under ~/.agents/skills still have the old text until a release and reinstall. Merge overlap with the other session's worktree D:/workflow-axa-redesign: likely conflicts in CONTEXT.md and docs/RULE-CONTRACTS.md, plus tests/README.md, tests/test_owned_skills.py, tests/test_package_contract.py, the workflow-clarify step 3 neighbourhood and README. That session ended before it could be told. The 4 residual Unslop wording points are accepted as judgement (V7). Existing docs were not swept against the new tells.
- Not done here, by agreement: version bump, CHANGELOG, UPGRADE, VALIDATION (rc.3 step; the summary is in FINDINGS), commit or push, the `correct` loop, the verification skills.
- Evidence kept: the task records. The full-suite outputs are in the session scratchpad only (baseline-unittest.txt, final-unittest.txt) and can be deleted after acceptance, because their results are copied into FINDINGS. No repository scratch was created.
- Hook note: E16, a false positive on the renderer's file name in command text.
- Next safe action: the owner accepts (or asks for changes); then the rc.3 release step and the merge with the redesign worktree, rerunning the full suite after the merge.


### Outcome update — live test and publication (2026-11-17)

- Live runs (FINDINGS L1-L4, $3.08 in total, each run under its own $3 cap).
  - L1 (isolated) and L2 (the owner's real settings) failed: a plain "what could this break?" never loaded the method, because no skill description named impact questions.
  - The routing fix (offer #3, V9, reviews S15 → S16) added this to code-review's description and a new "Impact questions" section.
  - L3 proved the routing: code-review was loaded for the impact question. But my harness lacked --add-dir, so the read of the method was denied.
  - L4 passed P1-P4: it read BLAST-RADIUS.md, reported only with Risks, Cleared, Safety facts with ladder steps and Before you merge, found the hidden player.py path, and left the fixture unchanged.
- A6 is now partly proven live: BR-inspect-question passed in L4. The other BR-* cases and B30 stay NOT_RUN.
- Final checks: full suite 1440 OK (skipped=14), validate PASS, completion_check exits 0.
- Publication: offer #4 (D12). One commit on main and a push to origin/main.


### Outcome update — open items (2026-11-17, offer #5)

- Live L5 (Unslop) FAILED: a writing request that changes no repository file never reaches the workflow, so the Unslop check did not apply, and "may skip" lost its "may". L6 (feature) was PARTIAL: the router ran and chose refactor plus a lightweight edit, so clarify item 7 and BLAST-RADIUS.md were skipped, and no file changed. Spend for offer #5: $3.47 of $6.
- Codex copies reinstalled from bedafd7. The audit reports DISK_MATCH, and the global references MATCH.
- Merge and rc.3 are handed to the redesign session (FINDINGS "Handoff to the redesign session").
- Follow-ups proposed to the owner (not built):
  - (a) how the Unslop check reaches writing requests outside a workflow task;
  - (b) whether an ownership move such as deleting a duplicate formatter may count as a lightweight edit, which would skip the safety-assumption step.
