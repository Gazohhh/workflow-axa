# Candidate review: workflow-axa 2.8.0-rc.4

## Final result, 2026-11-05

The isolated candidate implementation is complete. Final local checks and independent Standards and Spec reviews pass. Verification remains partial because a positive model-driven write and write-after-restart were not observed. No installation is requested or authorized by this report.

Direct owner instruction "fix all of it" after the audit authorized these isolated fixes. It did not approve an r4 HTML plan. The current [PLAN](docs/plans/2026-11-03-audit-hardening/PLAN.md) records that distinction and preserves the original r1 authority/history. The presented progress-r4 report remains unchanged.

## Ranked defect matrix

High means a wrong approval identity or retained consent can permit a write. Medium means valid work is blocked or evidence is overstated. Severity describes the reproduced risk before repair, not a remaining open defect.

| Severity / origin | Reproduction | Root cause | Fix | Test result and evidence |
|---|---|---|---|---|
| High: original audit, workspace approval | Copy an approved task/report to a sibling worktree, then request its write | Consent was keyed by task/report without presentation workspace | Bind presentation and consent to the actual workspace | PASS: [session tests](tests/test_session_recovery.py), final suite. Different-byte target report covered. Live positive write remains unverified. |
| High: follow-up review, waiver replay | Approve a no-report revision in one workspace, then present it in another | A later workspace value replaced presentation history | Preserve timestamped workspace history and use the presentation before each answer | PASS: [waiver regression](tests/test_session_recovery.py), final suite and Spec re-review. |
| High: follow-up review, withdrawal | Withdraw approval, then reuse its earlier answer | Same-session consent and sibling fallback did not consistently apply withdrawal | Reject revoked consent for that task until a new real approval | PASS: [withdrawal regressions](tests/test_session_recovery.py). Another task's withdrawal does not revoke this task. |
| High: candidate regression, link identity | Put a local report path inside nested labels/titles or present repo[other] beside repo[] | Candidate parsing confused label/title text with destinations or rewrote bracket identity | Consume each link atomically. Preserve exact destination identity. Reject unsupported syntax | PASS: nested/title/bracket/suffix regressions and final Standards/Spec re-review. This was found during candidate review, not independently reproduced on original rc.3. |
| Medium: original audit, revision parsing | Include requirement R7 or D4-R6 in a checkpoint | Case-insensitive revision matching treated requirement IDs as revisions | Parse explicit revisions and lowercase rN notation separately | PASS: requirement identifiers accepted, real newer revisions denied in [session tests](tests/test_session_recovery.py). |
| Medium: original audit, mixed registration | Run the new gate with an old hook registration and missing fingerprint events | Updated scripts ran beneath cached registrations | Add protocol compatibility denial and precise restart guidance | PASS: unknown/missing protocol cases. Live installation was not changed. |
| Medium: original audit, question presentation | Deliver the report through a question with a matching successful host answer | Only assistant text counted as presentation | Count the matched completed question. Ignore thinking, failed calls and unrelated answers | PASS: completed-question and negative cases in [session tests](tests/test_session_recovery.py). |
| Medium: follow-up review, reply fingerprint | Present a sibling-worktree report with different bytes | Reply hashing still read the original checkout | Hash the report in the presented workspace, preserving case | PASS: different-byte sibling test, final suite and review. |
| Medium: original audit plus review, whole-read evidence | Use partial/failed reads or a skipped conditional cat followed by successful output | Call text and combined success were mistaken for completed whole reads | Match successful results, reject truncation/partial reads and conditional chains | PASS: [eight read-evidence tests](tests/test_read_evidence.py), ten existing Stop-hook tests, final suite. Legacy ID-less evidence remains best effort. |
| Medium: original audit, waiting loops | End with Waiting on you while host goal feedback asks for another turn | External goal feedback and workflow Stop corrections had separate continuation paths | Emit no workflow Stop feedback while waiting. Document bounded goals and host recovery | PASS: synthetic silence checks. Live trial observed 30 seconds idle. Other hooks remain outside this hook's control. |
| Medium: candidate regression, file URI | Replay the saved host Markdown file:///D:/ report link | New workspace parser interpreted part of file: as a drive prefix | Decode supported local file URIs before path matching and invalidate old caches | PASS: red host-derived replay followed by corrected-record and sibling-session replay. Regenerated hook output is offline evidence, not live restart proof. |

The final code is [phase_gate.py](hooks/phase_gate.py), [plain_reply.py](hooks/plain_reply.py) and [hook registration](hooks/hooks.json). Recovery guidance lives in [SETUP](skills/workflow/SETUP.md), [TASK-FOLDER](skills/workflow/TASK-FOLDER.md) and workflow-doctor. STATE_VERSION 14 invalidates older parser cache entries.

## Current evidence

The [final suite log](docs/plans/2026-11-03-audit-hardening/evidence/rc4-full-suite.txt) records 886 tests, zero failures/errors, 14 skips, 171.116 seconds and exit 0. Validator PASS with 699 core words followed the final code freeze. Independent Standards and Spec reviews passed after all reported repairs. Twenty-two session-recovery tests passed. Earlier 878-test evidence predates the URI repairs.

The [final offline replay](docs/plans/2026-11-03-audit-hardening/evidence/rc4-replay-final.json) allows corrected-record approval and same-workspace sibling-transcript recovery. It regenerates owner-reply hook output. The original host transcript and source value remain unchanged. The earlier [red replay](docs/plans/2026-11-03-audit-hardening/evidence/rc4-replay-red.json) records the URI failure.

The pre-existing UI-lite snapshot mismatch was independently reproduced in the original checkout. Its expectation now includes frame-src none while retaining full output equality. Existing UI-lite implementation and report styling remain preserved. Original tracked diff SHA-256 remains 2f11292dd0d1a64c1b93c1bf9fe0a16305e7c90c5455c3abdfb840f4da3dcd72.

## Live evidence and limits

Four Claude processes ran across two approved bounded batches. Waiting stayed idle for 30 seconds, rejection kept source unchanged, and a read-only resume reconciled prior answers. Host dontAsk and sensitive plugin-path protections blocked writes in the first fixtures. The outside-plugin fixture wrote malformed approval wording, so the gate correctly denied the requested source edit.

The first batch's cumulative reported list-price total was USD 0.0819966. Replacement processes reported USD 0.041869 and USD 0.0479224. Combined reported total: USD 0.171788. These are CLI counters, not invoice metering. No more paid calls are planned.

Live positive write and live write-after-restart remain unverified. Fourteen native/environment cases were skipped. No fresh POSIX suite ran for these final changes. The hook does not interpret all language or shell code, stop every external host loop, or protect unhooked hosts.

## Separate Cheflabels completion

The owner accepted the repaired runtime result and final transfer. The original project contains the verified application/docs files and task evidence. Runtime checks reported zero page/console errors. The disposable worktree was removed, with no commit or push. Its [final delivery report](D:/Cheflabels-labeler-V2/docs/plans/2026-11-05-kit-confirm-sheet/reviews/delivery-2026-11-05.html) preserves native-device and remote-translation limits.

## Delivery and retention

This delivers the tested source candidate and its evidence. Parent packaging reserves .artifacts/2026-11-03-audit-hardening/release/workflow-axa-2.8.0-rc.4.zip and workflow-axa-2.8.0-rc.4-source.zip. Archive creation, archive validation and SHA256SUMS.txt remain the parent handoff step. Reserved filenames are not a claim that archives already exist.

Keep the small D:/wfaxa-pilot/workflow-host-fixture-rc4 fixture because replay resolves its report and PLAN bytes. It has no build or dependencies. Keep selected regression logs, offline replay and reports under the existing task output parent. Raw live traces/caches stay available for review but remain outside release archives. Private original session logs remain untouched. No unknown output was deleted.

Historical D7-D10 agent decisions remain visible and are not newly accepted by this delivery. No installation, policy acceptance or transfer approval question is attached.

## Previous rc.3 review: historical

# Candidate review — workflow-axa 2.8.0-rc.3

## Basis and authority

Based on the available rc.2 source ZIP, SHA-256 `d0426dc7162d28c071ff9bd516c95038a3f42795bb01f8145de8e49d33a6f3c6`. No fresh dump of the owner's installed tree or raw trial traces was supplied. The owner's quoted Claude report is reported evidence, not an independently rerun session. The Windows finding was reproduced with literal Git Bash paths; native Windows is still untested here.

Owner authorised the targeted package changes: "Alright make the changes give me a new version and tell me what i need to tell claude so it can test." That is not acceptance of D7–D10, deployment permission, a paid-run cap, authority to alter the real Altinstar TODO, or a whole-codebase cleanup.

Inputs also include the supplied graphics TODO and AI Ticket Creation Protocol. Adopt action titles, testable acceptance, dependencies and evidence; do not impose Epic/Story metadata or a second lifecycle on every small task. Original project documents remain untouched.

## Changes and limits

| Issue | Change | What this does not prove |
|---|---|---|
| One checkbox mixes the action, status, attempts and history | Labelled blocks with qualified IDs; current open work first; attempts in FINDINGS and reasons in DECISIONS | Automatic interpretation of all historical prose |
| A checkbox plus one V-ID can conceal a missing required check | Shared read-only parser flags explicit incomplete evidence; tick refuses ambiguous IDs, closed outcomes and unresolved verification | That a cited test actually ran or covered every acceptance criterion |
| C5 recommended plain HTML and treated a blanket yes as exception permission | Remove that recommendation; exact element-specific instruction/confirmation and whole question/answer required | Universal semantic enforcement by the hook |
| Evaluator inferred a $40 cap; reported cost excluded overhead/retro | Explicit full-batch ceiling and accounting scope; placeholders/vague answers are not authority; no hard-coded default budget | Provider spend metering, preemption or enforcement outside supported host controls |
| C6 old approval lacked numeric revision | Explicit reconciled legacy identity may be one existing report with full genuine answer after presentation; otherwise a narrow recovery question, never bypass advice | Authenticity of arbitrary agent-written records or semantic equivalence of scope |
| Windows partial reads depended on basename | Compare actual installed root, normalise Git Bash drive form, support quoted spaces and resolve relative paths | Complete shell parsing or native-Windows execution |

A bare `legacy` marker, report existence or words copied from tool output never suffices for the new recovery path. A current conflicting revision remains blocked. Gate errors now distinguish missing/unrecognised evidence from proof the owner never approved. Full approval is recorded before edits; a blocked edit should not be a permission probe.

## Preservation

No new skill or external dependency; no vendor changes, report redesign or historical task rewrite. Existing current D14 remains a reuse policy rather than a return to strict-kit-only. It still forbids CSS. Only its ambiguous fallback recommendation/consent path changes. Global artifact policy and activation helpers are unchanged.

The record parser is deliberately conservative about explicit pending/failed/blocked words on a checked legacy item. It raises a record problem, not a verdict that the implementation is defective. A human/agent reconciles dated historical wording from actual evidence; the parser never deletes it. Record tick is not an approval or test-attestation mechanism.

## Boundaries left unchanged

The phase hook remains best-effort transcript/command matching, not a complete sandbox. It does not meter spend or classify every user statement, constrain every path to a ticket, universally enforce Git permissions, stop an in-flight tool, or protect unhooked hosts. Task selection and the earlier pending D7–D10 decisions are not redesigned. These limits must be tested and reported honestly, not hidden behind the test count.

## Test and review loop

Current local results are in VALIDATION.md. The new red tests distinguish missing behavior from a live reproduction. No paid/model trial or installation was run here. Use the six targeted cases and ask for a real all-inclusive cap before launching. No mandatory unavailable baseline, automatic retries, extra paid batch or implementation in the read-only retro. The earlier $17.05 is a reported session subtotal, not the full old batch cost.

## Previous rc.2 review — historical

# Candidate review — workflow-axa 2.8.0-rc.2

## What was actually reviewed

Input: owner-supplied `workflow-axa(1).rar`, SHA-256 `ec25c67dfe0c98cd05bf5df35178dad679905b550bbf90932e308c64f6df3d1b`. Its package declares 2.8.0-rc.1, rules 1.8.0 and 21 skills. This is the post-hardening upload, not the earlier release which failed the previous audit. The supplied tree already had atomic record updates, failure-identity comparison, a small-change route, a release builder and many approval checks. Those were retained.

Baseline freshly reproduced here: validator PASS and 763 unittest tests passed on Linux (0 skips). This does not reproduce the owner's Windows or paid/live session results. The original task's delivery, acceptance and pending D7-D10 were NOT accepted by producing this candidate. Historical records are unchanged. The screenshots' simplification and paid-release options remain proposals, not answers.

## Confirmed fixes

| Issue reproduced against the input | Candidate change | Evidence/check |
|---|---|---|
| Loading specify or writing an HTML file counted as presenting its plan. | Only user-visible report references count; a no-report path requires the user-waived, task/revision-bound plan in chat. | `test_followup_boundaries` plus approval-hook tests. |
| An approval quote could omit the rest of the user's answer. | Match the whole real answer; retain conditions. Recognised direct implementation holds and refusals block dependent writes. | Qualified-answer and whole-answer hold regressions. |
| Agent-added `no report` could bypass the report requirement. | Require the waiver inside the verified complete owner answer, after its task/revision proposal. | Both legitimate waiver and forged-waiver tests. |
| Consent for one report could be reused for a newly named report; short legitimate answers were rejected. | Bind consent to named report presentation and accept complete short answers. Repeated links to the same immutable report remain valid. | New-revision, repeated-link and short-answer cases. |
| A later direct stop did not prevent recognised application edits; the Stop hook could ask for another read/review round. | Narrow direct stop/pause/cancel handling with handoff records allowed and explicit resumption. | Stop, resume, feature prose and stopped-read-loop cases. |
| Baseline signatures collapsed whitespace inside quotes and did not distinguish cwd. | Preserve exact command and cwd. Reject malformed record objects and unknown environment evidence. | Signature and malformed/unknown baseline regressions. |
| Phase hooks copied lengthy procedures and demanded irrelevant reads, while cosmetic wording alone caused another turn. | Short pointers to phase-owned instructions; conditional UI/TDD/code-review reads; cosmetic advice only when a substantive correction is already needed. | Phase-read and Stop-hook tests, negative and positive cases. |

The first regression batch contained 16 checks; against the original it produced 10 failures and 1 error. Those results were diagnostic tests, not live model runs. Later added cases cover legitimate alternatives and conditional guidance. The complete candidate results are in VALIDATION.md, not inferred from that red batch.

## Browser-test corrections

The supplied browser smoke harness failed its own unchanged report because it expected an older approval sentence. The UI harness also expected an older illustration notice and tried to turn a sketch fixture into a captured preview while leaving `preview.status` as `not-needed`. The candidate corrects these test expectations and declares the synthetic capture fixture authorised. It does not relax the renderer's approval validation or authorise a real preview. No renderer layout, CSS or JavaScript asset was changed. The renderer's package-version metadata is the sole rendering-code update.

## Simplification, not a rewrite

The router now uses one compact phase/permission table. READINESS owns the rules entry check; RULES remains a compatibility reference. CHATGPT-PROMPTS keeps its handoff template, not a second master workflow. SETUP contains current installation and enforcement facts; former installation material is explicitly historical in UPGRADE. Planned useful workers/checks replace an indiscriminate concurrency requirement. Prior source D2's small route remains one builder and one independent review; the two gates and grilling remain.

Across these eight changed instruction files, whitespace-delimited words decreased from **10,599 to 7,143** (net **3,456 fewer**): `skills/workflow/SKILL.md`, `skills/workflow/RULES.md`, `skills/workflow/SETUP.md`, `skills/workflow/CHATGPT-PROMPTS.md`, `skills/workflow/TASK-FOLDER.md`, `skills/workflow-execute/SKILL.md`, `skills/workflow-deliver/SKILL.md`, `skills/rule-maker/rules/READINESS.md`. This measures these files only, not prompt tokens, actual simultaneous loading, total repository size or money saved. Setup text retained under upgrade history is not deleted information. We do not claim the screenshot's 6,400-word saving or a speed improvement without live comparisons.

No skills were removed or added. In particular, `implement-spec` stays bundled/pinned for existing users rather than being deleted because a screenshot proposed dropping it. Ordinary execution already uses the adapted local phase. All nine bundled specialist trees, resume-task, artifact policy, report assets/examples and the current UI policy remain byte-identical to the input; 65 existing task-history files are also unchanged. The renderer changes only its embedded package-version label. This is checked before distribution. The source task-history files are retained unchanged.

## What the screenshots do NOT authorise

- **Accept:** do not select “Accept, including D7-D10” on the owner's behalf. D7 permits real selected-dialog answers, D8 chooses a current task by last written/named task, D9 keeps lightweight Git writes blocked, and D10 leaves resume-task alone. Preserve them provisionally for comparison; their acceptance is still the owner's decision.
- **Simplify:** the current user requested a reviewed candidate. It does not mean every proposed deletion was approved. This candidate consolidates verified duplication and leaves required/pinned material intact.
- **Release/budget:** no 160-session or $280 batch is launched. Those numbers were estimates in a screenshot, not measured here or approved. Start with a bounded paired pilot only after the owner agrees its count and spending/usage cap.

## Limits and deferred risks

The hook remains a heuristic aid, not a complete permission engine. It checks answer provenance, not every meaning, condition or per-ticket edit scope. A matched generic approval does not enforce separate Git/publication permissions; project restrictions and host permissions still apply. Task selection is still the earlier D8 last-written/named heuristic. Path exemptions allow task records, output and certain rule-maker writes. Arbitrary shell code, indirect side effects, external edits, unhooked hosts and sessions without a transcript are not fully covered. Explicit stop recognition is a narrow vocabulary, not a complete natural-language classifier or cancellation of already-running tools. A selected answer still needs the correct question/scope; a prompt label does not prove that.

The Stop hook sees read/review signals, not the completion or quality of a review. A useful follow-up could validate host-completed review events, but it is intentionally NOT replaced by an untested new orchestration platform here. Unavailable tools/hosts and novel cases must remain disclosed.

Baseline reuse is limited to recorded inputs: Git state, exact command/cwd and selected environment facts. It excludes ignored outputs and task records, so it is not sufficient when those are actual test inputs, nor for live services, mutable external state or unrecorded tool/runtime variables. It does not prove a check ran or replace final verification.

No project, account, live installation or global instruction file was changed. No live Claude/Codex/T3 trial ran here. Candidate validation is Linux/static/helper/browser evidence only. The current UI D14 remains: existing matching markup/classes; no new CSS; plain fallback only after the required owner choice. It was not reverted to the older strict-kit-only approach. The flowchart appearance is not redesigned. Four fresh desktop/mobile comparisons against the supplied input showed zero changed pixels in this controlled browser environment.

## Trial and return loop

Use the source-and-tests ZIP and CLAUDE-TEST-PROMPT.txt. Keep the baseline separate; ask for the live budget before launching even the first paid/model session. Run a small paired batch under matching conditions, including correct proceeding and correct stopping. Retro once at the batch boundary, return evidence and at most three recommendations, and wait. Do not auto-patch after each failure or adopt this candidate because its local tests pass. A later held-out/repeated batch needs separate permission.

## Engineering basis (external references, not local evidence)

[Claude hook contract](https://code.claude.com/docs/en/hooks) and [permissions](https://code.claude.com/docs/en/permissions) explain the host boundaries; they do not certify this implementation. [Building effective agents](https://www.anthropic.com/research/building-effective-agents) motivates proportional orchestration. [Evaluating agent runs](https://www.anthropic.com/research/demystifying-evals-for-ai-agents) supports checking actual outcomes, traces and repeated trials rather than treating self-reports as proof. The local reproductions above, not these recommendations, justify the implemented fixes.
