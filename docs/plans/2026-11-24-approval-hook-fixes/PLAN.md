# Approval hook: host messages, refusal reason, read-only offer commands

## Current checkpoint

- Updated / phase: 2026-11-24; closed (delivered, committed and pushed)
- Recipe: bug; Compatibility (the hook runs live for every session from this checkout) — three wrong refusals reproduced from a real transcript; scope: the task; classification question: not asked (the request states the outcome)
- Agreement (gate one): agreed (agreement 2, 2026-11-24, owner: "approve"; DECISIONS D3)
- Offer: #3 approved (supersedes #2 and #1; DECISIONS D7)
- Implementation: implemented; T1-T5 verified (TODO)
- Verification / owner acceptance: passed (V8-V11); the owner asked for the commit and push after delivery (D6)
- Blockers: none
- Changed files: hooks/phase_gate.py, hooks/approval.py, tests/test_approval_hook.py, tests/test_offers.py, tests/README.md, skills/workflow-execute/SKILL.md; records: this folder, docs/spar/2026-11-24-approval-hook-fixes/SPAR.md
- Rules: READY / AGENTS.md, CLAUDE.md, tests/README.md, rule-maker START, CORE, READINESS / this task / rules 1.9.0
- Test output: .artifacts/2026-11-24-approval-hook-fixes/ (candidate copy: scratch, removable now; baseline-main.log, after-copy.log, replay-offer6.txt: kept as evidence until the owner accepts)
- Next safe action: none required; release and the Codex copies' refresh only on request.

## Working context
- Owner: Cem. Requested through the T3 thread a3a3f191 (an agent relaying a retrospective of the workflow-paperclip session).
- Repository D:\workflow-axa, branch main, clean at 8a56c42 (2.10.0 release records).
- Rules: READY / AGENTS.md, CLAUDE.md, tests/README.md, rule-maker START, CORE, READINESS / this task / rules 1.9.0 / rules_stamp NONE (no stamp line; information only).
- Read-only on D:\workflow-paperclip and its transcript.
- Output folder: .artifacts/2026-11-24-approval-hook-fixes/ (ignored). Hook candidates are built and tested there first, because hooks/ runs live for every session (memory: live hook is this checkout).

## Goal and acceptance
An approval the owner gave stays valid while delegated results, host notices and question answers arrive; a refusal names the live offer's real reason; read-only `record.py offer` commands are never refused as writes.

## Agreement

Agreement 2, proposed 2026-11-24, replacing agreement 1 after the spar (docs/spar/2026-11-24-approval-hook-fixes/SPAR.md, revision 1, Handoff brief S3). Evidence in FINDINGS (E1-E6) and SPAR.md.

Requirements:
- R1 (request item 1; E1, E2): a message the host writes is never an owner message that narrows, withdraws, stops or answers an offer: a T3 delegated result in its real shape (`Delegated task node:… (title) in child thread … [completed]:`), a task notification, an AskUserQuestion tool result (the chosen label is the answer; the quoted question is not the owner speaking), a `Context handoff (…)` message and a `Note: the T3 server restarted…` notice. For the last two, only a `User message:` inside them is read, as the owner's words.
- R2 (request item 2; E4): a refusal for want of an approved offer leads with the newest live offer of the session's task and its reason; superseded and revoked offers are left out; approved offers for other files come after; "no current offer" when every offer is superseded or revoked.
- R3 (request item 3; E5): `record.py offer` `--help`, `present`, `show` and `list` write nothing and pass, also through a shell variable and with output redirected outside the project. Offer writes touch only their task's records. `offer derive` keeps its parent check, taken from the gate's own command parse (owner decision); a derive whose task folder or parent can't be resolved is refused. Offer writes don't change the legacy gate's current task.
- R4 (request; E6): a builder brief requires the test runner's verbatim summary line(s) (for unittest, `Ran N tests … OK`) for every test count and a file:line for every claim about existing behaviour.

What happens:
- Owner approves offer N, a delegated result or host notice arrives, the builder edits a listed file: allowed, no re-approval.
- Owner types "stop", "only the tests" or "I revoke that", directly or inside a handoff's `User message:`: suspends or withdraws as today.
- A write no offer covers: the refusal names the live offer (#6 in the paperclip case) and its reason.
- `$R offer present <task> 5 --question > <scratchpad>/q5.txt 2>&1`: allowed. `$R offer derive <task> <parent>` with an unapproved parent, or with an unresolvable folder: refused.

Stays the same: every other approval form, refusal and pause; the owner's own wording is judged as before; offers change only through `record.py offer`; the legacy gate's task tracking.

Not included: how the owner's own prose is judged (the 22:57 "but" message still counts); `R` set in an earlier shell call stays unexpanded, so no derive check runs then (same as today); release, version bump, commit, push.

Acceptance:
- A1: each real message shape is a test in tests/test_approval_hook.py; the delegated-result and host-notice tests fail before the fix and pass after.
- A2: a read-only replay of the paperclip transcript through the candidate shows #5 and #6 approved with no restrict or revoke fact from a host message.
- A3: superseded #1-#3, suspended #4, approved #5 for another file: the refusal leads with #4's reason and never names #1-#3.
- A4: both real commands from E5 pass; `$R offer derive` with an unapproved or withdrawn parent, an unset folder variable or no parent id is refused, and passes with an approved parent; the existing test that expected a derive with parent `offer.json` to pass drops that case; an offer write leaves the legacy current task unchanged.
- A5: the brief rule is in skills/workflow-execute/SKILL.md "Briefs"; the full suite and tools/validate.py pass.

Assumptions you can reject:
- Derive's parent id travels in the gate's write label; its wording and the one function that reads it back sit together in hooks/phase_gate.py, pinned by a round-trip test (owner chose this over a separate data field; GPT preferred the field).
- Parse caches get new versions: approval ENTRIES_VERSION 3, offer-history key facts-9, phase_gate STATE_VERSION 28.
- Built and tested in .artifacts/2026-11-24-approval-hook-fixes/candidate/; copying into hooks/ happens only with the owner's explicit OK at that moment, since hooks/ is live for every session.

## Outcome
Delivered 2026-11-24 (reconciled by an independent subagent; record gaps it found were fixed: checkpoint, Documents line, blast-radius result, kept replay output).

- Asked: stop approved offers from being suspended by host messages; show the live offer's real reason in refusals; let read-only `record.py offer` commands through; require verbatim test lines and file:line claims in builder briefs. Agreed as agreement 2 after a quick spar (SPAR.md revision 1); built under offer #1.
- Built: hooks/phase_gate.py (T3 delegated-result shape, context-handoff and restart-note envelopes, offer-command parsing with a fail-closed derive, legacy task tracking unchanged, STATE_VERSION 28); hooks/approval.py (derive from the gate's parse, old text matching removed, refusal order, cache versions); tests/test_approval_hook.py (7 new tests, 2 existing tests moved to the new refusal wording, 1 derive case that relied on the old gap removed); tests/README.md; skills/workflow-execute/SKILL.md (one sentence).
- Tickets: T1-T5 verified.
- Verdicts: R1-R4, A1-A5 and the assumptions verified. A5 was partial at first delivery (one existing CSS-dependent test failure); the owner asked to fix it (D6, offer #2): the test now has its own settings file (V10, review S2), and the full suite passes (V11).
- Checks: V1 baseline `Ran 1696 tests` / 1 existing failure; V8 after the copy `Ran 1703 tests in 638.293s` / the same 1 failure; validate.py PASS; V9 replay: offer #6 stays approved.
- Reviews: S1 independent, Standards and Spec plus blast radius, one finding repaired and passed; T4's sentence reviewed with writing-for-agents, no findings. completion_check: every change reviewed in its current form.
- Limits: the derive check can't run when record.py's variable was set in an earlier shell call (as before); no live host run of the new hooks beyond this session; SETUP.md:79 ("the legacy checker takes the last task written or named") is now slightly imprecise for offer writes (note only).
- Kept: .artifacts/2026-11-24-approval-hook-fixes/baseline-main.log, after-copy.log, replay-offer6.txt. Scratch: the candidate/ folder there, removable now.
- Next: committed on main and pushed to origin (offer #2). The Codex copies in ~/.agents/skills are not refreshed (excluded); no version bump or release.
