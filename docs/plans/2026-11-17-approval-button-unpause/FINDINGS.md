# Findings

## Evidence

- E1 Observed 2026-11-17 in this session (transcript a278e242): the owner's messages of 2026-11-16 23:23 and 23:33 contain "Do not implement until I approve …"; `phase_gate.control_intent` returns `pause` for both (verified by running it on the transcript). The owner then answered offer #1 of docs/plans/2026-11-17-spar-skill with the question tool's "Approve from this summary". The next write was refused: "workflow-axa: the owner stopped the work in this session; no write starts until they ask to continue."
- E2 Cause: `paused()` in hooks/approval.py (line 567) changes state only on `user` events, through `control_intent`: `pause` sets it, `resume` clears it. A question-tool answer is an `answer` event, which `paused()` never reads. A typed approval ("approve", "go ahead", "build it") matches `_ASK` in phase_gate.py and returns `resume`, so typing works and the button doesn't.
- E3 The pause is deliberate for "don't implement until …" (phase_gate.py line 986, a plan-only pause) and for "stop", "pause", "cancel", "wait" (lines 990-994). VISUAL-REVIEW.md "Read the answer": a stop only pauses the work; when the owner says to continue, the approval holds again.
- E4 Since 2.9.0-rc.2, workflow-specify step 5 tells agents to use the question tool whenever the host offers one, so button approvals are now the normal path and this refusal will recur.
- E5 `decide()` already treats the same button answer as the approval of the offer (APPROVE_BUTTONS, with "(Recommended)" stripped), so the offer is approved and only the session pause blocks.

- F2 (bug, approval hook, 2026-11-17): rest_of_call() in hooks/approval.py collects offers from the session's project root (project.root, the session cwd D:\workflow-axa) but computes each target's path relative to the target's own worktree (project.root_of(where)). An edit in a linked worktree (D:\workflow-axa-redesign) from a session started in the main checkout therefore never finds the worktree's approved offers: "This project has no offers yet." Workaround here: move the session into the worktree (EnterWorktree with its path). Not in this task's offer (decide() and offer lookup are excluded); recorded for a follow-up.
- F4 (security bug, approval hook, 2026-11-17, found by /spar pilot run 1, see docs/plans/2026-11-17-spar-skill/FINDINGS.md O1): the same mismatch is also a false allow. An offer approved in the main checkout authorises writes in a linked worktree of the same repository, including certain git command forms. Reproduced against the released 2.9.0-rc.2 hook (tests harness with a real linked worktree); control: an unanswered offer is refused. Not fixed; needs its own task and offer.


## Execution

- V1 T1 (2026-11-17): tests/test_approval_hook.py: test_an_offer_approved_by_button_or_slash_command_lifts_the_pause failed first (4 subtests), then passed after paused() read offer answers; 111 OK.
- Review 1: GPT-6 Astra (independent) failed: the withdrawal test never lifted the pause; agent-written markers (fake footer in an option description or text plus /approve 7) lifted a stop; /approve without a fresh presentation cleared paused() but fold() kept the stop.
- V2 repairs: offer_tasks() returns the offer id; read_events emits offer_shown and offer_asked for validated presentations only; paused() lifts on an approve answer to an offer_asked question, or /approve <N> while N's validated presentation is open; docs narrowed (VISUAL-REVIEW "Read the answer", approval.py docstring); new tests test_a_made_up_offer_marker_never_lifts_a_stop and a real withdrawal test; 112 OK.
- Review 2: GPT-6 Astra (independent) failed: a question replacing the text presentation closed it in decide() but not in paused().
- V3 repair: an offer_asked event clears open text presentations in paused(); cross-task regression added (failed first); 112 OK.
- Review 3: GPT-6 Astra (independent) passed: the probe is refused; with the reset removed in memory it lifted again (negative control); 112 OK. Live host behaviour unverified until the release (this session loads hooks from the main checkout).
