# Decisions

## Answers to question round 1 (owner, 2026-11-11, pasted message "Use the following decisions for Q1–Q20 ...")
- D1 Q1 A: one coordinated task with independent ticket groups. Parallel only when files and dependencies do not conflict.
- D2 Q2 A: American English consistently.
- D3 Q3 A: standardize terminology, avoid unnecessary renaming.
- D4 Q4 A: consolidate repeated explanations, keep actionable warnings.
- D5 Q5 A: current instructions free of historical release details.
- D6 Q6 A: project purpose belongs in project context documentation.
- D7 Q7 A: inspect evidence before asking. State assumptions explicitly.
- D8 Q8 B: do not invent missing product intent for UI decisions. Ask when missing information materially affects implementation.
- D9 Q9 A: purpose awareness for user-facing changes.
- D10 Q10 A: reuse existing fields unless more structure gives measurable value.
- D11 Q11 B modified: no rigid headings. Standardize responsibilities, discoverability, references and required coverage.
- D12 Q12 A: coverage checks are advisory. Critical violations of explicitly enforced rules may block.
- D13 Q13 A: read-only audit of accessible repositories, one migration proposal each, no rewrite without approval.
- D14 Q14 A modified: AGENTS.md is the canonical entry point. CLAUDE.md references it with a mechanism verified to work in Claude Code.
- D15 Q15 A modified: a lightweight route for genuinely small changes. Keeps approval, relevant tests and evidence. Escalates automatically when scope or risk grows.
- D16 Q16 A: single source of truth, references instead of copies.
- D17 Q17 A: hook improvements in an isolated test environment, existing protections verified.
- D18 Q18 B: detect and explain conflicts with superpowers or other overlapping skills. Never disable plugins automatically.
- D19 Q19 B modified: reasonable size budgets and duplication checks. No one-in-one-out sentence rule.
- D20 Q20 A: archive obsolete working documents after checking their references.
- D21: the four stated assumptions stand (vendored text byte for byte, renamed phrases change with their tests, the report patch is not redone, both approval gates stay).

## New requirements (owner, same message)
- D22: redesign rule-maker for a lightweight documentation architecture: AGENTS.md as a short entry point and index, documents with one responsibility each, documentation kept accurate as part of each task, discovery without loading everything, incremental checks in the workflow, a full audit only on request, only critical conditions block, tested read-only against the accessible repositories and in disposable test repositories with negative tests. The owner asked: "challenge this proposal yourself. If a simpler, more reliable architecture achieves the same outcome, explain it and recommend that instead."
- D23: questioning behavior: research first, resolve plain engineering choices as stated assumptions, ask only what changes product intent, architecture, risk or irreversible outcomes, group related decisions, recommend with trade-offs, never take silence as approval.

## Earlier decisions this task reopens
- D11 and D22 replace, for new setups and approved migrations, the stance in docs/plans/2026-10-29-rules-readiness/PLAN.md D1 and D4 and in skills/rule-maker (no template, no migration). Reason: the owner observed inconsistent, oversized and scattered rule files across repositories (FINDINGS part 4). Existing valid rules still pass. Migration only through an approved per-repository proposal.


## Agreement (owner, 2026-11-11)
The owner's answer to the gate-one question on r1: "I agree with the revised architecture, with the following adjustments before creating the detailed implementation plan." Recorded as agreement on revision r2 = r1 plus these adjustments:
- D24 [adj 1]: AGENTS.md stays the primary entry point, with shallow nested indexes. Not every document in the root index.
- D25 [adj 2]: common build and test commands in AGENTS.md, complex setup and environment details in referenced documents.
- D26 [adj 3]: "Preserve ALL existing approval gates, safety hooks, and blocking protections." The two documentation blocking conditions add to them and replace nothing.
- D27 [adj 4]: Covers hints optional, directory-level patterns, automatically discovered relationships. No hand-kept mapping of every source file.
- D28 [adj 5, C1]: "C1: Choose B. Run up to 5 fresh headless Claude sessions with a total budget of $5, but only if the budget can be reliably enforced. Otherwise, ask before incurring costs." Deterministic tests first, then agent runs, then manual host checks.
- D29 [adj 6]: adversarial tests: missing and stale documentation, conflicting instructions, broken references, interrupted sessions, resumed tasks, incorrect approval states, attempts to bypass hooks.
- D30 [adj 7]: verify `@AGENTS.md` in a fresh Claude Code session. Global import behavior is not proof of project-local behavior.
- D31 [adj 8]: the real-repository trial stays read-only.
- D32 [adj 9]: an ADR only for a lasting trade-off not already documented in DECISIONS.md.
- D33: "documentation validation must be meaningful. A passing link checker does not mean documentation is accurate. Verify affected code-related claims against implementation evidence, and explicitly report what was and was not verified."
- D34: the owner asked: "Update the agreement and prepare the detailed plan. Do not modify implementation files until I approve that plan."

- D35 (by: user, 2026-11-11): plan r1 (reviews/plan-r1.html) approved, together with agreement r3 (A12 to A15), with "go". Tickets H1 to H6, D1 to D3, W1a to W1c, L1, L3, L4, T2a1, T2a2, T2b, T2c, T2d, T3, X1, V1, V2. The question about the spending method was asked in the same message and the owner did not say "no paid runs". Because spending is consequential, the agent confirms once more before the first paid call in V2. No commit or push included.

- D36 (by: user, 2026-11-11, Q-H3, question tool): "Both fixes (Recommended)". Git commands that write files (git apply, git checkout -- <file>, git restore) are checked against the approved file list like an Edit, and the gate recognizes record writes made through a shell variable. Approvals only get narrower. Changes ticket H3.
- D37 (by: user, 2026-11-11, Q-REV, question tool): "Keep the gate (Recommended)". The gate keeps treating any higher rN in the checkpoint as a newer plan. The task-record template writes agreement revisions as "agreement N" instead of "rN". Added to ticket W1a (TASK-FOLDER.md).

- 2026-11-11, L3 ceilings (by: agent): reference-file word ceilings start at each file's size plus 10 percent, rounded up to 10, instead of today's size. Reason: with no headroom, every ticket that grows a reference file had to edit tools/validate.py while another worker was editing it (review 1 of L3). T3 lowers them to the final size plus 5 percent. Rejected: exact sizes now (forces shared edits) and no ceilings until T3 (growth goes unseen during the work).

## Agent decisions collected at the whole-feature review (2026-11-11)

These choices were made by the agent during the work and were first recorded only in FINDINGS. Each is listed here so delivery shows them to the owner.

- H2 (by: agent): the write gate still turns on when a phase SKILL.md is read whole; only the Stop hook's read demands were narrowed to real phase starts. Reason: the owner's "Preserve ALL existing approval gates, safety hooks, and blocking protections". This is narrower than R12's wording. FINDINGS: H2 review entries.
- H3 (by: agent): `git apply --check` and `git apply --stat` stay approval-only, although they write nothing. Reason: keeps an existing refusal. FINDINGS: H3 entries.
- H4 (by: agent): on the small change route, deletions and moves are refused; git actions other than a commit follow the lightweight commit rule; an AskUserQuestion offer counts like a chat offer. Reason: smallest route that the gate can still check. FINDINGS: H4 entries.
- L1 (by: agent): on the small change route one quoted yes stands for both approvals (Agreement "not required — lightweight or small change"). Reason: R11 "keeps the owner's quoted yes". FINDINGS: L1 build.
- D1 and D2 (by: agent): a cycle is reported only between index documents; documents under docs/plans and docs/archive are related but not fact-checked (history); the root AGENTS.md is always related as "entry point" when changed files are given. FINDINGS: D1 and D2 entries.
- D3 (by: agent): audit proposals for real repositories go under .artifacts (Git-ignored); the claim review samples the affected claims named in DOCS.md. FINDINGS: D3 entries.
- W1a (by: agent): a contradiction is "unsafe to build on" only when the evidence cannot tell which side is right and a wrong guess changes behavior, data, money, security, permissions, an external contract or the task's acceptance; when the document is the contract, agreeing code and tests do not make it wrong. FINDINGS: W1a review entries.
- E41 (by: agent): the gate keeps only the first owner-reply mark after each owner message, uncapped, instead of the last 50 marks. Reason: a pre-existing cap dropped the mark recorded at the owner's "go" after many subagent hand-backs. Built test-first in the candidate, reviewed (V-E41), attached to H6.
- Whole-feature review repairs (by: agent): a small change approved in an earlier session continues by showing the same offer again and recording the new yes on a separate `Reconfirmed (gate two): small change` line; the original Approval quote is never changed.

- SP8 (by: agent): a small change's yes binds both the file list and the description; the gate compares the offer's description with the checkpoint line's after normalizing spaces (decoration handling under review, RR1). A changed description needs a new offer and yes.
- SP9 (by: agent): the session-start note names each overlapping superpowers skill and the workflow-axa skill to use instead; its length test was raised from fewer than 50 to fewer than 65 words to fit the names. The 50-word limit was a review choice, not an agreement item; A12 requires the names.
- A14 (by: agent, for the owner): recorded as partial. After three fresh-agent runs the plain engineering choices are stated as assumptions and the product choice is asked, but the agent also asks a visible-change question that the agreed rule requires. The owner can accept this or ask for a rerun with a fixture whose request already names the link.

- D38 (by: user, 2026-11-11): V2 paid runs approved with the planned caps, answering Q-V2 (asked twice; the first answer asked what the cost means and what V2 is for, explained in chat): Sonnet 5.5, at most 5 sessions and 9 invocations, each `--max-budget-usd 0.40`, a cheap probe first that must report its cost, no new invocation unless reported cost plus 0.40 stays at or under 4.00, any invocation over 0.60 stops the batch; worst case about 5.00 estimated. The reported cost is an API-price estimate; on a subscription login it uses the usage allowance, not a separate bill.
- D39 (by: agent, 2026-11-11, X1 path fixes inside the approved ticket): rules/CHANGES.md is the rules history file and grows each release, so its ceiling in tools/validate.py rises to its final size plus 5 percent (T3's rule); the two tests that pin rules_version move from 1.8.5 to 1.8.6 with the same strength; layout_version becomes 3 as the owner asked, and the saved example reports change only that manifest value so test_legacy_example_renders_unchanged keeps comparing everything else.

- Collected at delivery (by: agent, 2026-11-11), choices first recorded only in FINDINGS: V2's sessions 3-5 started from prepared task folders to stay within 9 calls; the V2 worker disabled the installed rc.35 plugin with `--settings` and loaded this checkout with `--plugin-dir` (later a disposable copy, since removed); the AUDIT.md ceiling (970) and DOCS.md ceiling (1340) rose to final size plus 5 percent for rule additions from review (D39's rule); docs_check does not check a changed root CHANGELOG, and DOCS.md:92 instead tells the claim review to treat a changelog entry this task added as current; CORE.md keeps the exact UI question inline (correcting an earlier agent choice, because CHANGES.md 1.8.4/1.8.5 promise it); "record the owner's host choice" in DOCS.md and AUDIT.md is an instruction to future audits, not a recorded owner decision.

- D40 (by: user, 2026-11-11, Q-D3): "Rerun 2 sessions (Recommended)": rerun s2 (small change end to end) and s4 (unsafe document contradiction stops the task) with the project routing block in the test project: at most 4 calls, each `--max-budget-usd 0.40`, stop when the reported total would pass $1.60.
- D41 (by: user, 2026-11-11, Q-D4): "Leave as is": plain prompts stay outside the workflow unless the agent picks it; no routing hook task.

- D42 (by: user, 2026-11-11, Q-D1 asked again with an example): "Keep it (Recommended)": reading a phase skill whole keeps switching the write gate on. Settles the H2 agent decision and R12's wording.
- D43 (by: user, 2026-11-11, Q-D2 asked again with an example): "Accept (Recommended)": A14 counts as met; asking about a visible change on an existing page is the wanted behavior.
- D44 (by: user, 2026-11-11, Q-D5): "Full proposals": apply each repository's reviewed audit proposal in full, including the document moves and link updates it names; no commit, no push (the owner's request).
- Q-D6 answer: "tell me all choices so i can approve them or not": no decision yet; the 14 agent decisions are asked one by one.

- D45 (by: user, 2026-11-11, Q-AD): all 14 agent decisions approved one by one (AD1 word limits, AD2 git apply checks, AD3 small change limits, AD4 one yes for both, AD5 docs_check scope, AD6 audit output, AD7 unsafe contradiction, AD8 approval memory, AD9 later session, AD10 yes binds the description, AD11 overlap note, AD12 release pins, AD13 live run setup, AD14 changelog check).

- D46 (by: user, 2026-11-11, Q-D7): "Fix them now (Recommended)": the final review's Low items are fixed now (the gate's small-route branch when an Approval line names a missing report file, test-first in the candidate; the wording lines), with a review, before the repository work on workflow-axa itself.
- D47 (by: user, 2026-11-11, Q-D8): "Delete disposables (Recommended)": after the reruns delete candidate/, t2/, the older suite outputs and the runs/ project folders; keep the cost ledger, run JSON, audits, reconciliation and the latest test outputs.

- D48 (by: user, 2026-11-11, Q-R2): "r2 for full proposal (Recommended)": prepare plan revision r2 (with agreement 4, because applying audit proposals goes beyond the original agreement's "not included: rewriting repositories") for the full workflow-axa proposal: AGENTS.md and CLAUDE.md, the README/EVALUATION/tests README lines naming tools that never existed, tools/build_release.py shipping the linked docs, and moving CANDIDATE-REVIEW.md, RC3-CASES.md and CLAUDE-TEST-PROMPT.txt to docs/archive with their validator and test references. Both are asked in one message with a fresh plan report.

- D49 (by: user, 2026-11-11): plan revision r2 (ticket Y1, workflow-axa's own audit proposal) approved without an HTML report, answering the multiple-choice question after the plan was shown in chat: "Approve r2, no report". Agreement 4 agreed with "no need for report i approve already"; the owner added "with report i mean the review.html but documentations are needed". r1 stays approved for its tickets.

- D50 (by: user, 2026-11-11): "Alright skip for now all repos i will do when i will work on them just push when you are done and upper version"; Q-P1 "Keep them (Recommended)": the applied proposals stay as uncommitted changes in the ten other repositories, no further work there now; Q-P2 "2.8.0-rc.36 (Recommended)": release this repository as 2.8.0-rc.36. Commit and push of workflow-axa are requested once the work is done (after Y1's review and the final suite).

- D51 (2026-11-11, by: owner, multiple-choice answers to the FINDINGS repository questions G1-W5; changes stay uncommitted in each repository for the owner to check):
  - G1 yes: stamp line `workflow-axa rules checked: 1.8.6 (2026-11-11)` in each AGENTS.md. G2 "Remove broad entries": remove broad one-liner and inline-style permissions from Tippaa .claude/settings.json and the Pluryn and Cheflabels .claude/settings.local.json (owner-directed edit of permission files).
  - AXA-Retail: A1 "Un-ignore that file" (`!docs/opencart-engineering.md`); A2 read-only scripts free, writing scripts ask; A3 dev.gearlio.com is this machine; A4 add the three DB-writing test scripts to the owner-OK list.
  - Cheflabels-labeler-V2: C1 e2e local only, pletrix.cheflabels.com needs OK; C2 drop features.spec.ts line; C3 mark backend docs "in the backend repository, not verified"; C4 keep Jenkins line marked not verified; C5 fix or remove maestro/README.md:136 link.
  - Hooqd: H1 keep the rule; H2 "Link from README" (link docs/learning from the README); H3 docs/learning intended (project exception to the global /teach folder).
  - Pletrix-Cheflabels: P1 "Now"; pull answer: "stash and reapply and check everything from scratch again" (stash the uncommitted rule changes, pull development/main, reapply the stash, re-audit from scratch; a conflict stops the work); P2 "not sure ask me again after pulling and making the changes"; P3 none, all data-writing commands ask; P4 add acl_subscriptions to the acl:sync boundary.
  - Pluryn: L1 dev.pluryn.com is this machine; L2 keep the identity-provider line; L3 "Production only": reword the admin-session rule to production; L4 no CSS, follow design.md.
  - Tippaa: T1 "check code first" (check whether the root tests/booking tests are current before adding the line); T2 add the operator-only config note; T3 "Move to docs/archive" with links fixed.
  - android-launcher: N1 mark the TV Detox half as upstream text; N2 replace LAN addresses and the local archive path with placeholders.
  - bare-skin: B1 "ask the owner for the current exports"; B2 add .claude/worktrees/ to .gitignore; B3 keep asking; B4 document the code's cron:dev default, no code change; B5 add the required-read marker; B6 "Remove now" the duplicates with docs/ARCHITECTURE.md.
  - workflow-paperclip: W1 keep "ask which host"; W2 add the required-read marker; W3 "Update text now" (no publish); W4 link to AGENTS.md; W5 confirm.
  - workflow-axa Y1 review finding 1: "Edit UPGRADE, annotate VALIDATION" (no generator run).

- D52 (2026-11-11, by: owner): new standing rules and branch choices. Owner message: "D:\Cheflabels-labeler-V2 switch to development main and redo the changes also design.md is lowercase should be capitalized. Always capitalized 1 word like DESIGN.md should be capitalized fix everywhere always sit on all branches on latest branch please before you check and change let me approve first to check if thats the current branch".
  - All D51 workers were stopped before further edits. Only change made: AXA-Retail .gitignore (`docs/` became `docs/*` plus `!docs/opencart-engineering.md`), on master. Pletrix stopped before any stash.
  - After `git fetch --all` (owner chose "Fetch all 10, then show"), branches approved: master for AXA-Retail, Hooqd, Pluryn, Tippaa, android-launcher, bare-skin, workflow-paperclip ("Approve master"); Cheflabels-labeler-V2 and Pletrix-Cheflabels: "Stash, switch, redo" onto development/main; Racing-Edge-Web: "Switch to development", confirmed again after being told development has no commits that feature/storage lacks.
  - Capitals: "Every one-word .md name"; in other repositories "Use git mv" (stages only the renames, no commit). workflow-axa r3: "Approve r3, no report (Recommended)".
  - Saved as standing preferences in memory (repo-branch-approval-first, doc-name-capitalization).

- D53 (2026-11-11, by: owner, multiple-choice answers to FINDINGS F1-F16; changes stay uncommitted in each repository): F1 "1.8.7" for every stamp line; F2 "Capitalize everywhere" (old task records too), then "Only the 10 app repos" (workflow-axa history stays as r3 says); F3 Pletrix old style guide "Restore it whole"; F4 "Move Conventions out"; F5 "Fix both" (Pletrix README:186 and runbook:267 queue restart); F6 "Change it" (../Cheflabels-labeler-V2); F7 "Update comments only"; F8 Cheflabels "\"in the backend repository\""; F9 Pluryn DOMAIN.md:144 "Reword it"; F10 Tippaa "Replace with made-up data"; F11 Racing-Edge "Fix both" (README port, dashboardViews.ts:3 comment); F12 android-launcher "Fix both"; F13 bare-skin "Shorten an entry"; F14 markers "Keep"; F15 paperclip "Update now, ship later"; F16 stashes "Drop them" (the three named workflow-axa backup stashes only).
- Y2 review (independent, axes sequential, 2026-11-11): Spec PASS on A17 except no UPGRADE note on the rename; Standards: Medium, a Windows copy over an old install keeps lowercase names and audit_installation.py flags the right file as unexpected (UPGRADE.md:48 says to look for unexpected files); Low, the docs_check test input wording names a stale library file; Nit, the FINDINGS reason for tools/create_fixture.py was wrong (tools/ is in the r3 list; the file names no module, so nothing changes).

- D54 (2026-11-11, by: owner): "i puyshed cheflabels-labeler-v2 so you know" (the owner committed and pushed f60a2fa there themselves) and "You can push hooqd pluryn and tippa and axa retail for me". Committed and pushed on master, one commit each, only this task's changes (the repositories were clean before D44, except Tippaa's two untracked docs/plans/2026-11-05-* folders, left out): AXA-Retail ebafa0a, Hooqd f10cf663, Pluryn 243c57e, Tippaa 037b455; each in sync with origin/master afterwards. Not pushed (no request): Pletrix-Cheflabels, Racing-Edge-Web, android-launcher, bare-skin, workflow-paperclip, and the D53 edits made in Cheflabels after the owner's push.
- Next after rc.36: PletrixV2 core, modules and clients (FINDINGS), branch approval first.
