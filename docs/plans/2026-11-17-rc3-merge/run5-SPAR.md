# Spar: do the pstack blast-radius/Unslop work and the /spar work fit together for 2.9.0-rc.3?

## Current position
Revision 5, 2026-11-17. The question: do the pstack blast-radius/Unslop work and the /spar work each hold up, do they fit together, and what must be fixed before the rc.3 merge? Agreed by both debaters: S2 below, accepted as written by A (GPT-6.1 Sol) and B (Claude Opus 5.5) after 10 of 30 launches. The pieces fit. Land /spar as a scoped change set on top of 00ac3ae after fixes F1-F7. Five owner decisions (O1-O5) are open and block the merge. Owner chose "Investigate first" and approved running it; the result confirms S2 (see Investigation result). Next move: the owner answers O1-O5, then the fixes are planned.

## Intent and boundaries
Desired outcome (owner's words): "Are both implemented the right way, and do they fit together: each rule owned in one place, no conflicting edits to the same files (for example workflow-clarify step 3, code-review, README, CONTEXT.md), and no wording that contradicts the other? What should be fixed before we merge?"

Constraints: the spar is read-only. It makes no merge, commit, release bump or edit to either piece of work. Release records (version, CHANGELOG, UPGRADE, VALIDATION) belong to the separate rc.3 step.

Success criteria (proposed by the coordinator, open for the owner to change):
1. Each piece of work is judged against its own agreement and records, including any open items they leave.
2. Each rule that both pieces touch has one owner file, and the other files point to it.
3. Every file both pieces edit is listed with its conflict and the intended resolution.
4. No wording in one piece contradicts the other.
5. A ranked list of fixes needed before the merge, each with the check that proves it.

## Evidence
Facts:
- pstack work is committed, not uncommitted: D:\workflow-axa main = 00ac3ae (cf62e4d, bedafd7, 00ac3ae on top of c5e954b), level with origin/main (github). Its own handoff says main is bedafd7, so it is one commit behind. (git log, git status -sb)
- The /spar work is uncommitted in D:\workflow-axa-redesign, detached at c5e954b (56 changed entries). This checkout (d:\workflow-axa-spar-pilot\run5) is a pilot copy with the same content for the files compared. It also carries `.claude/skills/` duplicates of 19 skills. (diff --strip-trailing-cr)
- The redesign worktree also holds other tasks' uncommitted changes: worktree-guard (hooks/approval.py, C-OFFER-8), approval-button-unpause, question-answer-whitespace, the wait-what contract row, and CRLF-only churn in many files. Merging "the /spar work" brings these along unless they are separated.
- Files edited by both pieces: CONTEXT.md, README.md, docs/RULE-CONTRACTS.md, skills/workflow-clarify/SKILL.md, tests/README.md, tests/test_owned_skills.py, tests/test_package_contract.py. A trial three-way merge (scratch clone, 00ac3ae + redesign changes) conflicts in CONTEXT.md, docs/RULE-CONTRACTS.md and tests/test_owned_skills.py; the other four merge cleanly.
- workflow-clarify: pstack adds step 1 item 7, Safety assumptions (BLAST-RADIUS planning form). /spar adds a step 3 bullet, the Approach part from a linked SPAR.md. Different hunks. /spar's Understand step reuses "discovery from workflow-clarify step 1", so it now inherits item 7.
- Diagnostic allowance: OPERATIONS.md `## Standing diagnostic allowance` is the owner (CHANGES.md:9; BLAST-RADIUS.md:39 and interrogate cite it). spar/SKILL.md:27 cites `../workflow/flows/bug.md` step 1, which restates it.
- WRITING.md `## Unslop` lists the texts it runs on (offers, plans/FINDINGS, delivery report, human-facing docs, review prose, commit/PR text). Neither SPAR.md nor the /spar conclusion is listed. pstack's handoff step 3 asks that the /spar text be checked against Unslop; nothing shows that it was.
- skills/spar/* contains none of the SOURCE_MENTIONS names pstack adds (grep).
- /spar task state: T11 in review, T6 live runs remaining (cap raise needed), verification and owner acceptance not run, D18/D19/D31 proposed for the owner to confirm at delivery, agreements 3-5 "kept where agreement 6 doesn't replace them".
- pstack task state: delivered, owner acceptance pending; suite 1440 OK and validate PASS on its own tree; live L5 FAIL (Unslop not reached), L6 PARTIAL (lightweight route skipped safety assumptions); open follow-ups (a) Unslop reach, (b) lightweight boundary.
- README: pstack keeps "19 skills"; /spar makes it 20; separate hunks merge cleanly.

Assumptions:
- The rc.3 merge carries only the /spar work and pstack, not the other uncommitted tasks (not stated by the owner).

Contradictions:
- The owner described pstack as uncommitted; it is committed and pushed.

- Trial merge (00ac3ae + the whole redesign worktree, conflicts union-resolved): full suite 1511 run, 4 failures, 14 skipped; validate FAIL. All 5 failures are the same known count mismatch, "VALIDATION.md states 19 skills; the package has 20". The /spar task records the same 4 as known (TODO.md:287), because VALIDATION.md is rewritten only in the release step with the owner's OK. No new failure comes from the integration, and no test catches the duplicated rows the union produced.
- CONTEXT.md:70 says turning a spar into a plan "starts a task in docs/plans/". SKILL.md:62 and SPAR-FILE.md continue the existing task's clarify when the spar happens during a task. That rule is D31, still "owner to confirm at delivery". (Checked.)
- /spar TODO T1 (TODO.md:30-31) still names `standard|deep`; settings.py and README use `normal|thorough`. (Checked.)

## Options considered
- **Merge the whole redesign worktree onto 00ac3ae** (rebase all 56 entries). Case: one step, follows pstack's handoff. Objection: it brings in four other tasks (worktree guard C-OFFER-8, approval-button-unpause, question-answer-whitespace, wait-what row), and they are mixed into shared files (hooks/approval.py, tests/test_approval_hook.py, docs/RULE-CONTRACTS.md). Rejected by A1 and B1.
- **Scoped /spar change set on 00ac3ae** (only the /spar task's offer paths and hunks, including phase_gate.py SPAR_RECORD and its tests, without the C-OFFER-8 hunks), with the three conflicts resolved by hand and the listed fixes made. Case: lands exactly what was reviewed. Objection: separating hunks inside shared files takes careful work and its own check. Held by A1 and B1.
- **Do nothing for now**: keep /spar in the worktree until T6 live runs and owner acceptance are done, then rebase. Case: pstack has already shipped, so waiting costs little. Objection: rc.3 slips, or ships without /spar. B1 calls it a real option; A1 says waiting forever buys little.
- **Naive union of the conflicts**: rejected by both. The trial shows it duplicates the wait-what and SIMPLE-ENGLISH rows in RULE-CONTRACTS.md and drops "the Unslop tells" from one of them.

Debater A, A1: hold the merge until four bounded fixes are in: (1) the handoff wording in CONTEXT.md vs SKILL.md/D31; (2) /spar should cite OPERATIONS.md as owner; (3) do pstack's handoff step 3 (an Unslop review of /spar); (4) separate the /spar boundary from the other work, then run validate and the full suite on it, and settle the open live acceptance.
Debater B, B1: build the /spar change set on 00ac3ae. Merge-blocking: resolve the row duplication by hand, move phase_gate SPAR_RECORD with its tests and leave C-OFFER-8 behind, cite OPERATIONS.md. Cheap before merge: a WRITING.md bullet so Unslop covers SPAR.md and the conclusion. Follow-ups: the item 7 inheritance in /spar, the stale `standard|deep` names in TODO T1, and "never HOW" vs "may judge feasibility" in SPECIALISTS.md:20.

Debater A, A2: extract the /spar set onto 00ac3ae and keep the rc.3 bump separate. D18/D19 are superseded by agreement 6 (PLAN.md:112); only D31 is pending. WRITING.md's "anything a person reads" already covers SPAR.md, so no new bullet, but the Unslop review is still required. CONTEXT.md:70 is blocking and depends on D31. No further contradiction with code-review.
Debater B, B2: the same extraction file list (it places offers.py with question-answer-whitespace and VISUAL-REVIEW.md with approval-button-unpause). Merge-blocking: the owner confirms D18/D19/D31, and the owner approves landing phase_gate.py. The CONTEXT.md:70 pointer fix goes in now, whatever D31 becomes. The WRITING.md bullet is "should do". B withdraws its item-7 and "never HOW" points.

Coordinator's synthesis S1 (sent to both for a check; the full text is in the conversation): the scoped extraction (F1), conflicts resolved by hand (F2), the OPERATIONS.md citation (F3), a CONTEXT pointer (F4), the Unslop review plus a WRITING.md bullet (F5), record corrections (F6), verification with the 4 known failures expected (F7); owner decisions O1-O5.

## What changed our thinking
- The trial suite showed no integration failures beyond the known VALIDATION count. The real risk moved from text conflicts to separating the /spar hunks from four other tasks.
- PLAN.md:112: agreement 6 already replaced the D18/D19 labels. B's "confirm D18/D19" became a record correction: the checkpoint at PLAN.md:7 is stale.
- ~/.claude/plugins: running sessions load the cached rc.2 copy (c5e954b), not D:\workflow-axa. Landing phase_gate.py changes no running session; a plugin update or reinstall would, and that needs its own approval. This weakens B2's separate approval for the hook landing.
- The union trial duplicated RULE-CONTRACTS rows and no test caught it, so F2 needs its own grep-count check.

## Owner decisions
Blocking, open: O1 confirm D31 or choose a new task; O2 ship /spar with T6 live runs and acceptance pending (disclosed), or hold it; O3 keep the other uncommitted tasks out (default) or bring them in; O4 merge with the 4 known VALIDATION failures until rc.3, or land together with the rc.3 records; O5 accept pstack L5 FAIL / L6 PARTIAL as disclosed rc limits, or fix first.
- Effort: until agreement, cap 30 (start card).
- Debaters: A = GPT-6.1 Sol (Codex), B = Claude Opus 5.5 (fresh) (start card).
- Record: keep this SPAR.md (start card).

## Open questions and dissent
- Dissent (not a merge condition): should WRITING.md's Unslop list name a kept SPAR.md and the /spar conclusion? B: the list names neither. A: "anything a person reads" and "human-facing docs, such as" already cover them. B accepted leaving it to the WRITING.md owner.
- The uncertainty most likely to change the decision: whether the /spar change set separates cleanly from the four other tasks in shared files (hooks/phase_gate.py, tests/test_approval_hook.py, docs/RULE-CONTRACTS.md, README.md) and then passes with only the 4 known VALIDATION failures. The trial merged the whole worktree, not the extracted set. Cheapest credible test: build the F1 set on 00ac3ae in a scratch clone, resolve per F2, and run the F7 checks (about 8 minutes, no writes outside scratch). Observation that would change the recommendation: a new failure, or a /spar hunk that depends on excluded work, such as the spar hook tests needing C-OFFER-8 fixtures. Either would move toward "hold /spar until the other tasks land".

## Handoff brief
Selected direction (agreed S2):

Verdict: both pieces are sound on their own, and they fit together. The only rule-ownership mismatch between them is /spar's citation of the diagnostic allowance. Neither contradicts code-review/BLAST-RADIUS. Don't merge the redesign worktree as it stands: land /spar as a scoped change set on top of 00ac3ae after the fixes below. pstack needs no code change for the fit, only one record correction.

Pre-merge fixes, in order, each with its check:
F1. Build the /spar-only change set on 00ac3ae in a fresh worktree. Include: skills/spar/*, tests/test_spar.py, tests/behavioral/spar.json, docs/plans/2026-11-17-spar-skill/, the spar registration in .claude-plugin/plugin.json, the spar hunks of README.md, CONTEXT.md, docs/ARCHITECTURE.md, skills/workflow/SPECIALISTS.md, skills/workflow-clarify/SKILL.md, skills/grilling/SKILL.md and tests/README.md, the whole current diffs of skills/workflow/scripts/settings.py, tests/test_settings.py, tests/test_docs_consistency.py, tests/test_package.py, tests/test_ui_design.py, tests/test_owned_skills.py and tests/test_package_contract.py, hooks/phase_gate.py SPAR_RECORD/plain_file only, the two spar tests in tests/test_approval_hook.py, and in docs/RULE-CONTRACTS.md the spar row, the grilling wording and the spar-record bullet. Exclude: skills/workflow/scripts/offers.py, tests/test_offers.py, skills/workflow/VISUAL-REVIEW.md, every hooks/approval.py hunk, C-OFFER-8 text and tests, the wait-what row change, the other tasks' plan folders, and CRLF-only churn. Check: `git diff --name-only 00ac3ae` matches this list; "C-OFFER-8" and "ApprovalsStayInTheirWorktree" do not appear in the diff; the two spar hook tests pass against base approval.py; the README.md and RULE-CONTRACTS.md hunks are read by hand, since a file list proves files, not hunks.
F2. Resolve the three conflicts by hand. CONTEXT.md: pstack's three terms, the Spar term and pstack's three Rule owners rows. RULE-CONTRACTS.md: pstack's code-review, SIMPLE-ENGLISH (with "the Unslop tells") and WRITING rows, the spar row and the base wait-what row. tests/test_owned_skills.py: both sides' tests. Check: each skill row appears exactly once (grep count), and both sides' new tests run.
F3. skills/spar/SKILL.md:27 cites `../rule-maker/rules/OPERATIONS.md` "Standing diagnostic allowance" instead of flows/bug.md step 1. Check: a text pin in test_spar.py.
F4. The Spar term at CONTEXT.md:70 stops restating the handoff. It points to spar SKILL.md step 5 and SPAR-FILE.md "Where it lives", which holds whichever way D31 goes. Check: a text test that the term doesn't say "starts a task".
F5. Do pstack's handoff step 3: an Unslop review of /spar's human-facing text (README /spar line, the CONTEXT term, SPAR-FILE.md's conclusion and section template), recorded in /spar FINDINGS. Skill instruction text stays under writing-for-agents. Check: the FINDINGS entry. Not a merge condition, and recorded as dissent: whether WRITING.md's Unslop list should also name a kept SPAR.md and the /spar conclusion. B holds that the list names neither. A holds that "anything a person reads" (WRITING.md:3) and "human-facing docs, such as" already cover them. The WRITING.md owner may decide it later.
F6. Correct the records. /spar PLAN.md:7 checkpoint: D18 and D19 are superseded by agreement 6 (PLAN.md:112), so only D31 stays pending. /spar TODO.md:30-31: normal/thorough. pstack FINDINGS handoff: main is 00ac3ae, not bedafd7. Check: grep.
F7. Verify the extracted set: targeted test_spar, test_owned_skills, test_settings, test_approval_hook, test_phase_gate_hook, test_simple_english; then validate and the full suite. Expected: only the 4 known "VALIDATION.md states 19 skills" failures, plus validate's FAIL for the same reason. They stay failures, disclosed as such, not a pass, until VALIDATION.md is rewritten in the rc.3 step with the owner's OK.

Owner decisions needed before the merge:
O1 Confirm D31 (a spar held during a task hands off by continuing that task's clarify), or choose a new task instead.
O2 Ship /spar in rc.3 with the T6 live runs not done and no owner acceptance, disclosed in the notes; or hold /spar until T6 is done.
O3 Keep the other uncommitted tasks (worktree guard C-OFFER-8, approval-button-unpause, question-answer-whitespace, wait-what row) out of this merge (default), or bring them in through their own records.
O4 Merge with the 4 known VALIDATION failures until the rc.3 step, or land the merge together with the rc.3 records.
O5 pstack L5 FAIL / L6 PARTIAL and its pending acceptance: accept them as disclosed rc limitations, or fix them first.

Fact on the live hook (coordinator checked ~/.claude/plugins): the gazohhh marketplace is the directory D:\workflow-axa, but running sessions load the cached 2.9.0-rc.2 copy (c5e954b). So landing phase_gate.py in D:\workflow-axa changes no running session. A plugin update or reinstall does, and that needs its own approval (AGENTS.md).

Boundaries: this spar changed nothing in either repository; the fixes, the extraction, any commit, the rc.3 records and any reinstall each need their own approval. Conditions for going ahead: O1-O5 answered. Stays an assumption: that the extracted set behaves like the trial merge.

## Investigation brief
- What to check: whether the F1 /spar-only change set separates cleanly from the four other tasks and passes on 00ac3ae with only the 4 known VALIDATION count failures.
- How: clone D:\workflow-axa (read-only) into the session scratchpad, check out 00ac3ae, copy in only the F1 files and hunks from D:\workflow-axa-redesign (CRLF normalised), resolve the three conflicts as F2 says, then run the F7 checks: the targeted tests (test_spar, test_owned_skills, test_settings, test_approval_hook, test_phase_gate_hook, test_simple_english), `tools/validate.py`, and the full suite. Also grep the diff for "C-OFFER-8" and "ApprovalsStayInTheirWorktree", count the RULE-CONTRACTS rows, and read the README.md and RULE-CONTRACTS.md hunks.
- Cost: about 10 minutes of local CPU, no paid model launches, no writes outside the scratchpad. Neither repository changes. The scratch clone is disposable and is deleted after the result is recorded here.
- Which result changes what: only the 4 known failures, plus clean greps and counts, means S2 holds and planning can start. A new failure, or a /spar hunk that needs excluded work (for example the spar hook tests needing C-OFFER-8 fixtures), moves the recommendation toward holding /spar until the other tasks land, or bringing the needed task in through O3.

## Investigation result
Run 2026-11-17 in a scratch clone, which was deleted afterwards. The /spar-only set (F1) was built from D:\workflow-axa-redesign on c5e954b: 24 files plus the task folder. Excluded: offers.py, VISUAL-REVIEW.md, every approval.py hunk, the C-OFFER-8 lines, the wait-what row and the other tasks' folders. It was then merged onto 00ac3ae.
- Separation: the spar-only diff contains no "C-OFFER-8" or "ApprovalsStayInTheirWorktree". The two spar hook tests sit on the base approval.py and pass. No /spar hunk depended on excluded work.
- Conflicts: the same three files. Resolved as F2 says: in CONTEXT.md, pstack's terms then the Spar term; in RULE-CONTRACTS.md, the spar row, pstack's SIMPLE-ENGLISH row and the WRITING row; in test_owned_skills.py, both sides' tests. Each of the grilling, code-review, wait-what, spar, SIMPLE-ENGLISH and WRITING rows appears exactly once. The README hunks (read by hand) change only the counts and the /spar lines; pstack's paragraphs stay.
- Targeted checks (test_spar, test_owned_skills, test_settings, test_approval_hook, test_phase_gate_hook, test_simple_english): 269 run, OK.
- Full suite: 1477 run, 4 failures, 14 skipped. validate: FAIL. Every failure is the known count mismatch ("VALIDATION.md states 19 skills; the package has 20"). These are disclosed failures until the rc.3 step rewrites VALIDATION.md with the owner's OK.
- Effect: S2 holds. Nothing moves the recommendation toward holding /spar on technical grounds; O2 remains the owner's call.
- Side note, outside S2 (not judged by the debaters): README gives /spar's arguments two ways, `/spar <idea or decision> [quick|normal|thorough|N|until agreement <cap>]` and `/workflow-axa:spar <problem> [depth]`. Aligning them is cheap.
