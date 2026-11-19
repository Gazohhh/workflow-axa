# Findings

## Evidence
- E1: Router plus always-read references cost about 12.3k words; a bug fix reads about 25k (minimum) to 33k words before code (cost-map subagent, word counts with wc).
- E2: hooks/approval.py:886 parses the whole transcript (read_events, no cache) before the empty-target check at :1018, so read-only Bash/PowerShell calls pay a growing parse.
- E3: hooks/hooks.json PostToolUse runs phase_gate.py on Bash|PowerShell|Read|Edit|Write|MultiEdit|AskUserQuestion; importing approval+phase_gate takes about 260 ms against about 180 ms for bare Python (3 runs each, this machine).
- E4: START.md and CORE.md load through global CLAUDE.md and again through skills/workflow/RULES.md.
- E5: Repeated rules: "lightweight" 13 files, "one question" 14, blast radius 14, Unslop 8, CSS switch 12.
- E6: Already present: one-ticket work may skip the separate agreement (VISUAL-REVIEW "No separate agreement"); grilling already asks the whole frontier in one round. Items 9 and 10 therefore tighten existing rules rather than add new ones.

## Questions
Round 1 (saved before sending, 2026-11-19):

Q1 - Item 15, no offer for small reversible changes: today the hook refuses every project write without an approved offer, a lightweight edit included.
a. Keep the offer for every change; make the lightweight offer a single short message (files, check, why) with only Approve / Change something.
b. Let lightweight edits skip the offer entirely; the hook allows them and delivery shows the diff.
Recommended: a, the hook keeps one enforced rule and the stop costs one click.

Q2 - Live claude -p pilots: offline tests cannot show real wall-clock time of a full flow.
a. Allow pilots with a total cap of 20 USD for the whole task (before and after runs).
b. No live pilots; offline measurements only (word counts, hook milliseconds, stop counts).
Recommended: a, one baseline and one after-run per phase prove the speed-up on the real host.

Q3 - Git in the worktree: AGENTS.md needs explicit permission for commits.
a. Commit on branch speed/2.10 in D:\workflow-axa-speed after each green round; no push, no merge into main until you approve.
b. No commits; leave the changes uncommitted in the worktree.
Recommended: a, each round can be reverted on its own.

Q4 - Branch: main at 1a0d523 is the newest branch and equals origin/main.
a. Start speed/2.10 from main 1a0d523.
b. Another base (name it).
Recommended: a.

Q5 - Hook changes go live when merged, because sessions run hooks from D:\workflow-axa.
a. Build and test hooks only in the worktree; you copy them into D:\workflow-axa (or approve the merge) when all tests pass.
b. I merge into main myself once tests pass.
Recommended: a, a half-applied hook change breaks every running session.

Round 1 answers (owner, 2026-11-19): Q1 a; Q2 asked for an explanation with a simple sample (still open); Q3 a; Q4 a ("start from main yes"); Q5 a.

Q2 owner answer (2026-11-19): "no cap". AGENTS.md requires an explicit total usage or spending cap for paid host evaluations, so an uncapped pilot conflicts with a project rule. Follow-up Q2b (saved before sending):
a. Pilots allowed with a cap of 50 USD total; I report the running total after each pair of runs.
b. No live pilots; offline measurements only.
c. A different total cap (name it).
Recommended: a.

Q2b owner answer (2026-11-19): "for now 50 than" = a, total cap 50 USD.


## Check results
- V1 (2026-11-19, round 1: T0-T3, worktree D:/workflow-axa-speed on 1a0d523 plus uncommitted round-1 diff): tools/validate.py exit 0 (one NOTE: verify-app word ceiling, pre-existing). Full suite: Ran 1658, failures=1, skipped=14; the failure is test_record_safety.test_parallel_appends_lose_nothing (FINDINGS.md.lock), the intermittent failure tests/README.md documents; rerun of test_record_safety alone: OK (17 tests). Baseline tree (1a0d523, extracted with git archive, not a git checkout): Ran 1632, errors=1 (test_cutover rc39 rollback needs a git checkout; environment, not code). Logs: .artifacts/2026-11-19-workflow-speed/r1-suite.log, baseline-suite.log.
- V2 measurements (tools/measure_speed.py, repeat 5; baseline.json vs r1.json): words router 14,536 -> 9,826; bug 28,726 -> 24,116; lightweight 26,163 -> 21,528. Hook ms (median, warm) bash_read_only 1k/5k/20k: 354/371/537 -> 337/331/359 (A2: 20k within 22 ms of 1k); read: 169/159/180 -> 133/125/126; edit: 386/482/613 -> 465/464/552 (1k edit within noise on a busy machine: a 9-run recheck gave 492 baseline vs 521 candidate). Stops: 3 -> 3.
- E7 (T2 worker): Read stays in the PostToolUse matcher: legacy report_check needs a report fingerprint, which a Read of the report can create (pinned by test_the_gate_records_fingerprints_when_a_report_is_used_and_when_the_owner_answers); 7 legacy inventory files exist on this machine. Instead phase_gate.py exits before heavy imports when an event can produce no output.
- E8 (T1 worker): run_legacy already started only for inventoried legacy tasks (item 4 needed no change). read_events cache stores only transcript-derived records; offer files are checked on every call. Old vs new read_events identical on 75 local transcripts.
- E9 (T3 worker): bug path still above 10k; remaining big files: TASK-FOLDER 2,894, WRITING 2,360, VISUAL-REVIEW 1,806, READINESS 1,624, code-review 1,586, router 1,484, specify 1,383, DOCS 1,326, grilling 1,319. Sections pinned by tests were left in place.

- V3 (2026-11-19, round 2: approval fast path and lightweight offer field, T4 text, T5 text, deeper T3 split, on 122b2aa plus round-2 diff): tools/validate.py exit 0. Full suite: Ran 1677, failures=2 (test_stage_candidate pins two AUDIT.md sentences the review worker shortened); both sentences restored word for word, test_stage_candidate then OK (2 tests). Log: .artifacts/2026-11-19-workflow-speed/r2-suite.log.
- V4 measurements (r2.json, repeat 5): words router 9,085; bug (whole path incl. review and delivery) 21,831; lightweight 19,465. Hook ms bash_read_only 1k/5k/20k: 210/199/196 (baseline 354/371/537); read 112/111/112 (baseline 169/159/180); edit 384/407/468 (baseline 386/482/613). Stops 3.
- V5 baseline live pilot (T0, baseline tree 1a0d523, opus-5-5, Claude Code 2.1.327, fixture D:/workflow-axa-pilots/2026-11-19-workflow-speed/base-fixture): 273 s wall clock, 2.20 USD, 72 tool calls, 4 owner stops where 1 was needed, bug fixed, tests green. Evidence: .artifacts/2026-11-19-workflow-speed/pilot/baseline/, runbook pilot/RUNBOOK.md. Pilot spend so far: 2.20 of 50 USD.
- E10 (pilot): the 3 extra stops came from (a) the agent printing the --question form of the offer as plain text in -p mode, which the hook did not accept as a presentation, and (b) a typed "Approve from this summary" not counting as an answer, while a typed "approve" did.
- E11 (round-2 hook worker): on a three-answer offer, "Approve" typed through Other now counts only if it was one of the options; before it approved. This narrows today's behaviour and is to be reverted in round 3 (agreement: existing approvals keep working).
- E12 (review worker): "modest diff" for one reviewer set at about 300 changed lines in git diff --stat (agent choice). completion_check.py already accepted one reviewer; unchanged.
- E13 (source check by a separate research agent): items 1-4, 6, 9 and 11 are our own findings or judgement, not taken from Matt Pocock or pstack files; 7 and 16 are grounded in both; 5, 10, 13 in Matt's files; 8, 12, 14 in pstack's. Matt's .out-of-scope/lazy-load-writing-for-agents.md warns against deferring text a decision needs.

- V6 (2026-11-19, round 3 at 8e3b87e): tools/validate.py exit 0; full suite Ran 1689, OK (skipped=14). Log: .artifacts/2026-11-19-workflow-speed/r3-suite.log.
- V7 reviews of 1a0d523..8e3b87e (two fresh reviewers, Standards and Spec; probes kept in .artifacts/2026-11-19-workflow-speed/review/):
  - Standards F1 (low, fixed): the read-only fast path took commands with a backslash inside an option name (`git diff --out\put=x`, `find -de\lete`), which bash runs as the writing option. Fix: backslash added to FAST_UNSAFE (hooks/approval.py); three cases added to tests/test_hook_speed.py FAST; the HEAD version allowed two of them, the fixed version refuses all three; test_hook_speed OK.
  - Standards F2 (low, not fixed, owner decision): an agent that writes the events cache under %TEMP%/workflow-axa-gate/events/ can forge an owner answer; the same was already possible by writing the transcript or the older offer-history cache, so no new capability. Closing it needs the hook to deny writes to its cache and transcript folders.
  - Spec 1 (fixed): skills/rule-maker/DIAGNOSE.md pointed at a renamed section; now points to workflow/HOST-GOALS.md.
  - Spec 2 (fixed): workflow-deliver step 5 lost the condition "when it was briefed with those checks" for counting a one-ticket review as the whole-feature review; restored.
  - Spec 3 (deviation, recorded): R2 is partly delivered: the router still reads RULES.md (then READINESS.md) and TASK-FOLDER.md before records exist; A1 not met (17,779 words before code on 8e3b87e, target 10,000).
  - Spec 4 (deviation, owner decision): offers gained an optional "lightweight" field (needed for D1). Old offer hashes are unchanged, but an older offers.py (the live checkout, installed copies, Codex) refuses an offer that has the field. Release must update all copies together.
  - Notes: A2 partly met (read-only hook time flat across 1k-20k events; Read still starts a hook, E7). A6 not yet observed live.
- V8 (after the fixes): validate.py exit 0; test_approval_hook, test_shadow_comparison, test_docs_consistency, test_cutover, test_new_skills, test_stop_and_baseline, test_rules, test_rules_audit, test_hook_speed OK.
- E14 (T7): CHANGELOG top entry is "Unreleased (next minor release candidate)" because test_docs_consistency treats the top section as the current version's; plugin.json unchanged.


## Hooqd approval bug report (owner, 2026-11-19)

Request: the owner forwarded a bug report from the Hooqd session (task docs/plans/2026-11-19-verify-map-bugs in D:\Hooqd): a git commit needed three refused approval attempts. Suggested fixes (a) real refusal reasons for git/MCP operations, (b) drop "or ask them for this one step" and state how to present, (c) buttons as the default presentation and send_to_user not a presentation, (d) owner decision on "/approve N" plus extra text. Test-first in tests/test_approval_hook.py.

- E15: hooks/approval.py:1190 (git operations) and :1196 (MCP tools) return a fixed "no approved offer lists …" text and drop the per-offer reasons `why` that validated() computed at :1160-1164; the path branch at :1177 passes `why` to no_offer(). SLASH at :121 matches only a whole message "/approve N". Round 3 on this branch already accepts a typed "Approve from this summary" and the --question form shown as text.

Round 2 questions (saved before sending, 2026-11-19):

Q6 - Where this fix goes: speed/2.10 already changes approval.py heavily (rounds 1-4); main (2.9.2) is what runs live.
a. A revision of this task (agreement 2) on speed/2.10: one branch, no conflicting edits; it reaches live sessions when you merge 2.10.
b. A separate hotfix task from main (2.9.3): reaches live sessions sooner, but its approval.py edits conflict with speed/2.10 and must be merged twice.
Recommended: a, the 2.10 branch is close to done and the same lines change.

Q7 - "/approve 1" followed by more text: today only a message that is exactly "/approve N" counts.
a. Keep it exact; when "/approve N" starts a longer message, the refusal says the extra text may narrow the approval and asks for "/approve N" alone or a button click.
b. Count "/approve N" at the start of a message whatever follows.
Recommended: a, extra words can be a condition ("approve 1 but not the push") that the hook can't read.

Q8 - "or ask them for this one step" in the git refusal: the hook has no one-step approval, so a plain "Commit and push?" question never counts.
a. Remove the phrase; the refusal says how to ask: buttons with the `offer present <task> <id> --question` output as the question, or that exact text at the end of the reply.
b. Add a real one-step route: a plain question naming the exact command approves that one command.
Recommended: a, one approval route keeps the hook simple and every git write tied to an offer.

Round 2 answers (owner, 2026-11-19, question tool): Q6 a; Q7 a; Q8 a.

- V9 (final, 3972094, worktree D:/workflow-axa-speed, Windows 11, Python 3 from PATH): tools/validate.py PASS (one pre-existing NOTE, verify-app word ceiling). Full suite Ran 1696, failures=1, skipped=14: test_record_safety.test_parallel_appends_lose_nothing (['FINDINGS.md.lock'] != []), the intermittent failure tests/README.md documents; rerun of test_record_safety: OK. Earlier full run on 470e793: Ran 1695, OK. docs_check --changed-from-git: 0 blocking, 0 warning, 9 notes. Logs: .artifacts/2026-11-19-workflow-speed/final2-suite.log, final3-suite.log.
- V10 measurements (final.json on 470e793, repeat 7; baseline.json on 1a0d523): words router 14,536 -> 8,145; bug path (incl. review and delivery) 28,726 -> 20,059; bug before code 17,858 (no baseline value for this key; round-1 estimate ~25.6k); lightweight 26,163 -> 17,746. Hook ms, median warm, 1k/5k/20k events: read-only shell 354/371/537 -> 199/187/188; Read 169/159/180 -> 104/106/108; Edit 386/482/613 -> 363/375/419. Stops counted from skill text: 3 -> 3 (readiness when rules have gaps, the offer, owner acceptance).
- V11 candidate live pilot (T8, 470e793, same fixture bytes, model, prompt and answers as V5): 2 invocations vs 5, 213 s vs 273 s, 2.04 vs 2.20 USD, 65+3 vs 72+6 tool calls, owner stops 1 (needed 1) vs 4 (needed 1), bug fixed and tests green in both. One sample each. Evidence: .artifacts/2026-11-19-workflow-speed/pilot/COMPARISON.md, pilot/candidate/. Pilot spend total 4.24 of 50 USD.
- E16 (pilot): the candidate hit a misleading refusal for a shell chain with variable paths (`mkdir -p "$T" && record.py new "$T/PLAN.md"`): "This project has no offers yet." Not fixed; follow-up.
- V12 review of 8e3b87e..470e793 (one independent reviewer, both axes in sequence): one Standards finding, a refusal naming a superseded offer after `offer revise`; fixed test-first in 3972094 (new test failed before, passes after); Spec: no findings. Review S-final: independent passed after the fix (re-verified by the test run in V9, not re-reviewed).

- Release request (owner, 2026-11-19): "merge and release please". Session moved back to D:/workflow-axa; task records copied here from the worktree (identical, diff -r). Offer #5 covers the merge and the 2.10.0 release.

- R1 release (2026-11-19, offer #5): main fast-forwarded 1a0d523 -> 3972094 (git merge --ff-only speed/2.10); version 2.9.2 -> 2.10.0 in plugin.json, README, the report renderer's RENDERER_VERSION, version.json package_version, four tests/behavioral candidate_version pins; CHANGELOG entry renamed to 2.10.0; UPGRADE.md gains the 2.9.2 -> 2.10.0 section; rules version stays 1.9.0. Evidence copied from the worktree to .artifacts/2026-11-19-workflow-speed/ here (diff -rq identical; the disposable baseline-tree copy left out).
- E17 (release): hook false positive: a shell command whose text only names the report renderer script (a grep, or a record.py append whose text mentions it) is treated as a report render and refused until the report guides are read. Follow-up.
