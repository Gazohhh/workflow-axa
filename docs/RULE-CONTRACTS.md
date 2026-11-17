# Rule contracts

For each hard rule of workflow-axa, this file says when it applies, what it covers, what must already be true, what the agent must do, what is excluded, what to do when blocked, and what checks it. It then labels the main rules of each skill. The owner file states each rule in full and wins when the two differ.

## Three kinds of rule

| Kind | Meaning |
|---|---|
| Hard rule | Must always hold. A break is a defect, even when the result looks right. |
| Procedure | The expected order of steps. The agent records a justified deviation. |
| Judgment call | The agent decides with a stated criterion. Two good runs can differ. |

"Checked by" names a hook, a test or "instructions only". A hook runs on matching tool calls in Claude Code. The PreToolUse hook is `approval.py` since 2.9.0; `phase_gate.py` is the legacy checker for tasks in the owner's inventory and a shared library. Both are active only after the session typed, loaded or read the `workflow` router or a phase skill (phase_gate's `scan`, `hooks/phase_gate.py:2369`, which `approval.py` calls). Codex runs no hook from this package (`skills/workflow/SETUP.md`). A test runs on this package's scripts and texts, not on a live session.

## Hard rule contracts

### Agreement (checkpoint label `Agreement (gate one)`)

- Owner: `skills/workflow/VISUAL-REVIEW.md` "The gates"; asked in `workflow-clarify` step 4.
- Applies when: a new goal, feature, behavior fix, architecture change or material scope change.
- Scope: behavior, scope, exclusions, journeys, acceptance, assumptions. Allows tickets and the offer, never code.
- Preconditions: rules ready or a limited exception; task folder exists; journeys traced; no open choice.
- Action: summarize, ask the agreement question, stop. Record the answer on the `Agreement` line and in DECISIONS.
- Exceptions: inspect-only work, docs-only work and PDF deliverables (their own route); a lightweight edit and one-ticket work with no open choice, whose offer carries the agreement (`not required — lightweight` or `not required — one-ticket offer`); an explicit bounded waiver; legacy approval.
- When blocked: wait. Reopened items go back to grilling. Record the blocking question and what can still proceed (`workflow-clarify` "Next").
- Checked by: instructions only for offer tasks; `approval.py` checks the offer, not the `Agreement` line. For a legacy task, hook `phase_gate.py` (since 2.8.0-rc.38), on the two-gate route only. A checkpoint with an `Approval (gate two)` line whose approval is not legacy needs an `Agreement (gate one):` or plain `Agreement:` line that says agreed, waived, legacy or "not required". Until then, project and Git writes are refused after the approval check passes (`agreement_problem` `:1327`, called at `:2072`, patterns `:1322` to `:1324`).
  - The first state word decides: "agreed ..., awaiting approval" passes, but a line that starts with a word such as "pending", "proposed", "awaiting" or "not agreed" is refused. Quoted owner words never decide the state.
  - Not checked: single-gate tasks, legacy approvals, lightweight edits and the small change route.
  - Limit: the hook reads the state word, not whether the agreement covers the work.

  Tests: `tests/test_gate_regressions.py` (`AgreementGateRegressions`); `tests/test_task_report.py` (`task_report.py:71` refuses an approval-ready report without a recorded agreement).

### Implementation approval (the offer; checkpoint line `Offer: #<id>`)

- Owner: `skills/workflow/VISUAL-REVIEW.md` "The gates" and "Read the answer"; asked in `workflow-specify` step 5.
- Applies when: before application code, tests, dependencies, migrations or Git writes in a workflow task.
- Scope: the offer: behavior summary, allowed and delegable paths and operations, exclusions, conditions and checks. A lightweight edit gets the minimal offer, one-ticket work one ticket, multi-ticket work the full list. The plan report is built only on *Show review.html first* or when the owner asks; the offer, not the report, is what the hook checks.
- Preconditions: agreement recorded or carried by the offer; tickets in TODO for ticketed work; the offer presented from `record.py offer present`.
- Action: present the offer (the text `record.py offer present` prints, as the end of the reply), ask the one question (*Show review.html first*, *Approve from this summary*, *Change something*), stop. The hook reads the answer from the conversation; the checkpoint names `Offer: #<id>`.
- Exceptions: none at the hook. A task in the owner's legacy inventory keeps its `Approval` line, checked by `phase_gate.py`.
- When blocked: wait; only task records and the report change. Fix a hook refusal by presenting the offer again or through the `resume` skill, never by editing or disabling the hook.
- Checked by: hook `approval.py` (contracts C-OFFER-1 to C-OFFER-8 below): a write needs an approved offer that lists its path, in the session's own worktree; Git writes and MCP write tools need their operation named in the offer; a later withdrawal or narrowing ends the approval, and a stop only pauses it; offer records change only through `record.py offer`. Tests: `tests/test_approval_hook.py`, `tests/test_offers.py`.
- Checked for a legacy task: hook `phase_gate.py`, reached through `approval.py`'s dispatch:
  - no `Approval` line: `:1810`; not approving, or "proposed": `:1815`, `:1817`;
  - no quoted words, or a quoted refusal: `:1845`, `:1846`;
  - each quote must be a whole user message after the plan was presented: `:1862`, `:1885`;
  - an `.html` report must exist unless the quote declines one: `:1907`, `:1899`, decline words at `:89`;
  - a write outside the report's `write_paths`: `:2078`; a stopped or paused task: `:2381`;
  - the checkpoint is the section under the first heading of any level whose text starts "Current checkpoint", up to the next heading of the same or a higher level (`:1345`); a `# ` line inside a fenced code block also ends it;
  - task records, `.artifacts` and a spar record (`docs/spar/<folder>/SPAR.md`, that file name only) stay writable: `:65`, `:264`, `:2354`; bulk deletes there are refused (Artifact cleanup).

  Tests: `tests/test_phase_gate_hook.py`, `tests/test_gate_regressions.py`.

### Small change (retired in 2.9.0; legacy tasks only)

The small change route is folded into the one-ticket offer (`skills/workflow/VISUAL-REVIEW.md`). What follows applies only to a task in the owner's legacy inventory with a recorded `Small change:` line.

- Owner (before 2.9.0): `skills/workflow/VISUAL-REVIEW.md` "Small change".
- Applies when: a visible edit to text, order or visibility of existing elements on one screen, in a task folder with no report.
- Scope: exactly the listed existing files.
- Preconditions: a checkpoint line `- Small change: <files> — <what changes>`; no open choice.
- Action: show that line in one message, ask for a yes, end the turn. Record the whole answer, edit only the listed files, test, review once, deliver in short form.
- Exceptions: none for the file list. A changed list or description needs a new offer; a later session needs a `Reconfirmed` line.
- When blocked: growing scope or risk moves to the full route (`workflow-clarify`, then the plan report).
- Checked by: hook `phase_gate.py`: route only without a report `:2052`; files must exist `:1677`; offer required `:1699`, `:1701`; quote is a whole later message `:1705`, `:1708`; deletes `:1751`, moves `:1753`, other or new files `:1755` refused. Contents (since 2.8.0-rc.38): after an Edit, Write or MultiEdit of a listed file, a note names each tag or class the edit adds (`style_notes` `:2534`). The note never refuses the edit. Limits: code such as `Array<string>` gives a false tag note. When `git show` fails, every existing tag and class in a Write counts as new. Tests: `tests/test_gate_regressions.py` (`SmallChangeRoute`), `tests/test_gate_notes.py` (`StyleNotes`). Whether it qualifies: instructions only.

### No CSS while the switch is off, and DESIGN.md rule 4's question

- Owner: `skills/rule-maker/rules/DESIGN.md` rules 1 to 5; `ui-design` applies them. The machine CSS switch (`~/.workflow-axa/settings.json`, off by default) decides whether styling may be written at all; reuse comes first either way.
- Applies when: any application UI work, ordinary prompts and small edits included. Not backend-only work.
- Scope: stylesheets, `<style>`, `style=""`, CSS-in-JS, theme overrides, visual props, script style changes, new classes or IDs.
- Preconditions: the design kit (if any) and the existing code were searched for an element doing the same job for the same user.
- Action: mirror that element's tag, full class list and context. When nothing matches, stop that element and ask the exact question, listing only same-tag elements. Before finishing, check the diff and name each class's defining file.
- Exceptions: plain unstyled HTML on the user's explicit instruction for the named element, or when the user answers rule 4's question by confirming that no similar element exists; the report renderer's shell and `quick_previews`; internals of reused components.
- When blocked: the element is in mode `blocked` and waits for the answer; independent logic and tests continue (DESIGN.md "Modes").
- Checked by: hook `approval.py` refuses a styling write while the CSS switch is off, and a change of the switch without the owner's Yes to that exact question (C-CSS-1, C-CSS-2; `tests/test_approval_hook.py`, `tests/test_settings.py`). With the switch on, styling stays inside the offer's paths. The older note that never blocks stays (`phase_gate.py` PostToolUse, since 2.8.0-rc.38): in an active session, after an Edit, Write or MultiEdit of an application file, the gate adds a note when the edit adds styling (`style_notes` `:2534`, added to the PostToolUse output at `:2622`). The note asks for rule 4's question or the name of the existing class.
  - Application file: any project file except Markdown, `docs/plans`, `.artifacts` and test files.
  - Styling: the inline-style and CSS-in-JS cues of `skills/ui-design/scripts/review_ui_diff.py`, and a stylesheet rule in a `.css`, `.scss`, `.sass`, `.less` or `.styl` file. "Adds" means more matches after the edit than before. For Write, the committed file is the before.
  - Limits: the hook reads cues only and cannot see design kit authority. Shell writes get no note. Texts over 4,000,000 characters are skipped. When `git show` fails, every existing style in a Write counts as new.

  `review_ui_diff.py` itself still lists cues for review and grants or refuses nothing. Tests: `tests/test_gate_notes.py` (`StyleNotes`), `tests/test_ui_design.py` (the cues, and that DESIGN.md holds the rule and the question). Whether the agent asked the question: instructions only.

### Artifact cleanup

- Owner: `skills/workflow/ARTIFACTS.md`, installed as `~/.workflow-axa/ARTIFACTS.md`.
- Applies when: tests, builds, device or browser checks, profiling and delegated work, with or without `/workflow`.
- Scope: output the agent places under the task's output parent (default `.artifacts/<task>/`).
- Preconditions: the parent, each file's owner, active consumers and protected paths are known.
- Action: reuse one stable parent; keep the smallest evidence set; delete only the agent's own disposable output from the current work when every listed condition holds; record what stays and the next cleanup condition.
- Exceptions: deliverables, approved reports, baselines, rollback data and tool-owned output are protected. Superseded reports follow VISUAL-REVIEW.md "Superseded review cleanup".
- When blocked: unclear ownership, or older or unknown output: preserve it and ask. No `git clean`, wildcard delete or blanket wipe.
- Checked by: hook `approval.py`, calling phase_gate's `bulk_delete` (in `phase_gate.py` since 2.8.0-rc.38), bulk forms only, in an active session. The check runs before the `.artifacts` write exemption (`bulk_delete` `:180`, called at `:2352`, refusal at `:2378`).
  - `git clean` is refused unless it has `-n` or `--dry-run`. It is read from the parsed command words (`git_clean_called` `:154`), also inside `bash -c`, `powershell -Command` and `cmd /c`. The words "git clean" in a commit message, an echo or a heredoc do not count.
  - A delete of `.artifacts` itself, and a wildcard delete under `.artifacts`, are refused.
  - Named files and folders under `.artifacts` stay deletable. Their ownership and consumers stay instructions only.
  - Limits: `find -delete`, `shutil.rmtree` and other script deletes, `rm -rf .art*` and combined shell flags such as `zsh -lc` are not seen. A `[` in a folder name counts as a wildcard.

  Tests: `tests/test_gate_regressions.py` (`BulkArtifactDeletes`); `tests/test_global_policy.py` installs the policy text.

## Rules per skill

Owner file: `skills/<skill>/SKILL.md` unless named.

| Skill | Hard rules | Procedures | Judgment calls |
|---|---|---|---|
| workflow | Inspect stays read-only; no Git writes unasked; changes pass the gates | Rules readiness; find the task; first matching route row | Intent; whether a message belongs to the task |
| workflow-clarify | No code; stop for agreement; never offer CSS | Trace journeys; grill; write the agreement | Which question blocks; when tracing is done |
| workflow-specify | No code or tests; stop for the answer to the one question | Vertical tickets; bigger checks; the offer; the plan report only when asked | When plan-review runs; where behavior belongs |
| workflow-execute | Approval first; never weaken a test; never install | Ticket loop; whole-feature review | Small route or worker; what is material |
| workflow-deliver | Never fixes or approves; no checks after a stop | Freeze state; verdict per requirement; Outcome and report | Which contradiction is unsafe |
| codebase-map | Never implements or approves; no invented markup | Choose the view; validate, render, open | Mode and geometry |
| resume | status changes nothing (a badge is not authority); continue never rewrites an Approval quote or bypasses the hook; handoff writes only when asked | `open_items.py`; reconcile records and the worktree; readiness before continuing | Status of each item; whether scope changed materially |
| rule-maker diagnose | Changes nothing | Package, hooks, policy and rules checks | The PASS, WARNING or BLOCKED grade |
| plan-review | Never implements or approves | Authority; traceability; necessity check | What is unnecessary scope |
| rule-maker | Apply only an approved proposal; shared library read-only | Audit; apply; check | Which claims to sample; severity |
| ui-design | DESIGN.md rules (owner `rule-maker/rules/DESIGN.md`) | Pick a mode; record the mirrored element; screen diagram | Which element does the same job |
| grilling | Never offer a forbidden option; rule 4's question word for word | Research first; rounds; save each question before sending (in the conversation when there are no task records) | Ask only what the user must decide; when to stop |
| tdd | Report only what ran; test only at agreed seams | Red, green, refactor; one slice at a time | Spotting anti-patterns |
| code-review | The Standards and Spec axes stay separate; blast radius reports only; probes within the diagnostic allowance, writes only in a verified isolated copy | Pin the diff; find sources; run and aggregate; step 4b follows BLAST-RADIUS.md when anything outside the diff reads what changed | Whether each baseline smell applies; which safety facts carry the most risk |
| writing-for-agents | None | Context pointers; information hierarchy | No-op test; when to split; pruning |
| codebase-design | Project ownership and approved rules win | Deletion test before a new layer | Depth; seam placement |
| domain-modeling | A new glossary or ADR needs approval | Record a term in DECISIONS, then the glossary | Whether an ADR is worth offering |
| interrogate | User-invoked; reports only; probes within the diagnostic allowance, writes only in a verified isolated copy | Restate; pin the snapshot; two adversaries; confirm on a pristine copy; three lists; stale when the target changed | What counts as a concrete failure; when a concern is worth an experiment |
| no-comments | User-invoked; one approved offer before any change; behavior unchanged; unverified constraints and tool-read annotations kept | Reviewer verdicts; check each one; offer; apply; tests and type check; report | Whether a comment is stale, a contract or a constraint |
| wait-what | No new work, no tool call beyond CONTEXT.md, SIMPLE-ENGLISH.md and `record.py offer present` for a pending offer, no offer or decision change; never an answer | Context; the point in plain words; the pending question unchanged | What context the reader lacks |
| spar | User-invoked; never implements, no tickets or offers; debaters only read; agreement only when both accept the exact text of one proposal with evidence, never faked; never a silent model substitute; the coordinator's recommendation labelled apart from the debaters' and the owner's; SPAR.md is the record when the owner chooses to keep one ("conversation only" writes nothing); a workflow plan only by the owner's handoff choice, planning only | Understand (intent, criteria, evidence; the frame line before any launch); explore (blind openings that challenge the framing); challenge (outcome-changing disagreements, labelled synthesis); decide (the uncertainty and its cheapest test); conclusion first, then the four-way handoff | When a premise is weak; which objections belong to the owner; whether a round made progress |
| SIMPLE-ENGLISH.md (reference text, formerly simple-english) | Never change code, quotes or rule 4's question | Document rules; self-check; the Unslop tells | When plain words lose the meaning |
| WRITING.md Unslop check | Runs before the cold-reader check; "Keep the meaning" wins; never changes application UI copy, error messages or translations | The listed texts, after drafting | Which tells apply to a sentence |

## Hook candidates

Hard rules with instructions only, or with a known hook gap. Release 2.8.0-rc.38 built candidates 2 to 5. Candidates 1 and 6 stay unchanged by owner decision (2026-11-12, Q6 c of task 2026-11-12-approval-gate-false-refusals). Candidate 7 is partly built in 2.8.0-rc.39; candidate 8 is not built.

1. Report decline words (seen on 2026-11-12). Owner decision: unchanged. The agent asks for "no report" words when needed. `hooks/phase_gate.py:89` `NO_REPORT` matches "no report", "no plan report", "no html report" and "without a report", but not the owner's own "no review.html is needed", so the gate refused an approved task. A hook could also accept a whole quoted answer that declines the report by file name or by "no ... needed". Limit: a wider pattern can read "no code review needed" as a report waiver.
2. Agreement before approval. Done in 2.8.0-rc.38: the hook refuses project and Git writes, not the `Approval` line itself, while the `Agreement` line of a two-gate task is not agreed, waived, legacy or not required (Agreement contract above). Limit: it checks the state word, not whether the agreement covers the work.
3. No new CSS. Done in 2.8.0-rc.38 as a note that never blocks (owner Q8 a), because the cues also match legitimate code (contract "Never write CSS" above). Limit: the hook cannot see design kit authority, and shell writes get no note.
4. Bulk artifact deletes. Done in 2.8.0-rc.38: `git clean`, a delete of `.artifacts` itself and wildcard deletes under it are refused (Artifact cleanup contract above). Limit: it cannot judge ownership or consumers, so it catches only bulk forms.
5. Small change contents. Done in 2.8.0-rc.38 as a note that never blocks: a new tag or class in a listed file (Small change contract above). Limit: a heuristic; text edits inside markup are hard to separate from new elements.
6. Plan waiver. Owner decision: unchanged. VISUAL-REVIEW.md accepts an explicit "I don't need to see the plan, go" as a waiver of implementation approval, but the hook still asks for a report or a "no report" quote (`hooks/phase_gate.py:1899`, `:1907`). A hook could accept a recorded `waived` Approval line whose quote declines seeing the plan. Limit: the same wording risk as candidate 1. Since 2.9.0-rc.1 this concerns legacy tasks only: an offer task builds a report only on *Show review.html first*, and implementation approval has no waiver.
7. Approval answers the gate cannot match (seen on 2026-11-12). Bold or italic typed answers: done in 2.8.0-rc.39 (`bare` at `:880`; only the quote comparison ignores the markers). Still open: in T3 Code (observed 2026-11-12) the visible text of an assistant message that also calls a tool is not stored in the session log, so a plan presented in such a message, then answered in the question box, does not count; a hook could count an answered question whose own text names the plan, the task path and the revision. A one-word "Approve" cannot be recorded for a task without a report, because the quote must then decline the report ("no report"). A hook could accept those forms. Limit: looser matching can count a reply that is not an approval.
8. Approvals in linked worktrees (seen on 2026-11-12, E10 and E11). A linked worktree never borrows the main checkout's approval, and a subagent in a linked worktree cannot see the main session's transcript, so its first write is refused. Release 2.8.0-rc.38 only names the two differing PLAN copies in the refusal (`worktree_copy_note` `:2400`). A hook could accept an approval recorded for the same task in the main checkout. Limit: that weakens the rule that approval evidence is bound to its workspace.

## Known gaps

No check covers these:

- Whether a change qualifies as a lightweight edit or one-ticket work.
- What an approval means. The hook matches the owner's whole message after the presentation, not its intent.
- Whether the built result matches the agreement; `workflow-deliver` reconciles it by review only.
- Every rule in sessions where neither the router nor a phase skill was typed, loaded or read (phase_gate's `scan`, `hooks/phase_gate.py:2369`, used by `approval.py`), and on Codex.
- Shell writes the gate cannot parse; its docstring calls command-text filtering advice, not a security boundary.
- Whether rule 4's question was asked word for word, and whether a plain-HTML exception came from an explicit instruction.
- Whether a delete of named files or folders under `.artifacts` was authorized. The hook refuses only bulk forms.
- Whether the recorded agreement covers the work. For a legacy task the hook reads only the state word on the `Agreement` line; for an offer task approval.py checks the offer, not the Agreement line.
- Styling or markup that the cues do not match (computed styles, shell writes), and what the agent did after a note. Notes never block.

## Redesign contracts (2.9.0-rc.1)

Task `docs/plans/2026-11-15-workflow-redesign` (plan REDESIGN.md v6) replaces the approval forensics above with the contracts below. Each names its owner section in REDESIGN.md and the test that checks it; "Tn" names the ticket that added the test; every one of them landed by 2.9.0-rc.1. These contracts cite no line numbers: tests and section names are the stable references.

| ID | Contract | Owner (REDESIGN.md) | Checked by |
|---|---|---|---|
| C-OFFER-1 | An offer is an immutable id with canonical fields (behaviour, allowed and delegable paths and operations, exclusions, conditions, checks, parent); state is pending, approved, superseded or revoked; a canonical change creates a new offer | §3.4 | `tests/test_offers.py` (record), `tests/test_approval_hook.py` (hook) |
| C-OFFER-2 | An offer becomes pending only with successful presentation evidence: the exact generated presentation as the end of a visible message (nothing before it that could hide it) or as one question's text (`--question`) with that question's answer; the frozen format 1 block still counts for the same offer; the CSS display line is outside the hash | §3.4 | `tests/test_approval_hook.py` |
| C-OFFER-3 | Approval forms: a button answer, `/approve <id>`, or a whole message from the fixed list; a qualified answer never approves and leads to a narrowed offer confirmed once; scoped answers approve only what was offered by name | §3.4 | `tests/test_approval_hook.py` |
| C-OFFER-4 | Every offer, lightweight edits included, ends with the one question (Show review.html first, Approve from this summary, Change something), asked once per offer | §3.4 | `tests/test_approval_hook.py`, observed T16 |
| C-OFFER-5 | Approval is a cache over a decision reference re-validated on use; failure fails closed with a diagnosis; a validated approval is never asked again | §3.4 | `tests/test_approval_hook.py` |
| C-OFFER-6 | A child's derived offer is a checked subset of the parent's delegable scope and inherits exclusions, conditions and checks | §3.4 | `tests/test_offers.py` ChildOffers, `tests/test_approval_hook.py` ChildrenAndRules |
| C-OFFER-7 | `/wait-what` is a non-answer: it neither approves nor supersedes; its reply re-presents the unchanged offer | §3.4, §3.10 | `tests/test_approval_hook.py` |
| C-OFFER-8 | Offers are read from the session's worktree and authorise writes only there: a write that reaches another worktree of the same repository is refused, judged where each place really lands and, for shell commands, by every path the command names; Git commands the checker can't place, and changes to the set of worktrees without their own approval, are refused; task records and output there stay writable when reached directly; an independent repository keeps its old handling | §3.4 | `tests/test_approval_hook.py` ApprovalsStayInTheirWorktree |
| C-RULES-1 | Rules readiness is always checked; only when gaps exist is the owner asked (set up / skip for this task), and adequate rules need no question; skip waives only the named gaps; silence is not skip; only writes wait | §3.5 | `tests/test_approval_hook.py` (pause); T17 (wording) |
| C-CSS-1 | The machine switch `~/.workflow-axa/settings.json` (missing or invalid means off) is read at each styling write; off blocks styling writes at once; on never widens an offer; a project may only be stricter (`css: never`) | §3.6 | `tests/test_settings.py`, `tests/test_global_policy.py`, `tests/test_approval_hook.py` |
| C-CSS-2 | Changing the switch is a protected operation allowed only by a recorded Yes to the question naming that exact setting and value | §3.6 | `tests/test_approval_hook.py` |
| C-FLOW-1 | Routing signals live only in `flows/INDEX.md`; every index row has a recipe file and the reverse; every skill a recipe uses is registered | §4.0 | `tests/test_flows.py`, `tools/validate.py` flow_index_errors |
| C-CMT-1 | Comments are claims, not evidence: the code establishes what happens, and a mismatch with an intended contract is raised as a possible bug; new code carries no comments outside the exception list; cleanup only in lines an approved change edits; an unverified constraint is removed only when an approved offer names it and any authority the claim names is given; an executable annotation is removed only when the offer justifies its replacement and the relevant check passes without it | §3.9 | `tests/test_rules_pass.py` (rules text); T23 (code-review check) |
| C-FB-1 | A fallback is one line (name, substitute, evidence, remaining limitation) in FINDINGS where task records exist, otherwise in chat; delivery lists only the remaining gaps; only the six listed conditions pause the dependent work | §5 | `tests/test_flows.py` FallbackAndRouterTests |
| C-LEG-1 | Tasks whose `Approval:` line predates the offer model (recorded before the cutover, with no offer record) are checked by the repaired legacy checker from the cutover on and never asked to re-approve because of the format; adding an `Approval:` line later never selects the legacy path | §3.4 "Legacy" | T17, T19 |
| C-SAFE-1 | Kept safeguards: git writes, installs, bulk deletes under `.artifacts`, branch creation; each refusal names one reason and its fix | §7 | existing gate tests; `tests/test_approval_hook.py` |

### Findings mapped to checks

Each confirmed problem of REDESIGN.md §2.3 has a reproduction or a planned check, or is marked not testable offline.

| Finding | Check |
|---|---|
| P1 waiver phrasings | `tests/test_session_failures.py` P1 and ReliefGuards (T7, interim) |
| P2 waiver and approval never combine | same P1 fixture (waiver message before the plan, "Approve" after it) |
| P3 literal revision required | `tests/test_session_failures.py` P3 and its several-revisions guard (T7) |
| P4 report for every approval | C-OFFER-4 (T14; observed T16) |
| P5 small change asked again per session | `tests/test_session_failures.py` SmallChangeRelief (T7) |
| P6 scope and fingerprints read from HTML | C-OFFER-1/2 (T14); removal checked in T19 |
| P7 CSS prohibition copied six times | `tests/test_rules_pass.py` (the prohibition exists only in DESIGN.md) |
| P8 line citations remapped by hand | this section cites none; nothing to remap; no separate test |
| P9 blanket partial-read warning | T20: hook unregistered, contract suite asserts it |
| P10 small route forbids new files | `tests/test_session_failures.py` SmallChangeRelief; `test_gate_regressions` older-report case (T7) |
| N1 generic refusal text | `tests/test_session_failures.py` several-revisions guard names the missing revision (T7; the full rule arrives with C-OFFER refusals) |
| N2 report guides demanded on a no-report route | `tests/test_gate_regressions.py` NoReportStopRegressions (T8) |
| N3 project required reads for every task | `tests/test_required_reads.py` ScopedGateTests (`paths=`) |
| N4 record write switches the task | `tests/test_session_failures.py` N4 and its two guards (T7, git writes; file writes keep the stop until the offer model) |
| N5 a write before a denial | not testable offline (host event ordering); observed in T16 |
| N6 branch authorisation not correlated | not testable offline (owner intent); C-SAFE-1 keeps branch creation protected (T14 case) |
| G1 verification_summary exits 0 on failure | T5 |
| G2 hard-coded skill list | T4 |
| G3 required-read grammar parsed twice | `tests/test_required_reads.py` (one parser, both callers) |
| G4 CONTEXT.md as a parser registry | T4 (synonym bans advisory) |
| G5 hand-added budget lines and REQUIRED lists | T4 with the contract suite |

### Where each check lives after the cutover (T19)

The PreToolUse hook is `hooks/approval.py`. `hooks/phase_gate.py` stays as the retained legacy checker and a shared library; its header lists what approval.py uses from it.

| Check (what phase_gate did) | Where it lives now | Contract | Tests |
|---|---|---|---|
| A write needs the current task's approval | approval.py: an approved offer that lists the path | C-OFFER-2..5 | `test_approval_hook.py` |
| Withdrawal, narrowing, stop and continue after approval | approval.py: facts folded across the project's sessions | C-OFFER-5 | `test_approval_hook.py` OfferStates |
| Git writes and MCP write tools | approval.py: the operation named in the offer | C-SAFE-1 | ProtectedOperations |
| Unresolvable shell targets refused | approval.py, using phase_gate's `targets_of` / `shell_writes` | C-SAFE-1 | ProtectedOperations |
| Package installs and npx-style downloads | approval.py, calling `install_problem` | C-SAFE-1 | ProtectedOperations |
| `git clean`, bulk deletes under `.artifacts` | approval.py, calling `bulk_delete` | C-SAFE-1 | ProtectedOperations |
| Required reads before a phase skill (Skill calls) | approval.py `kept_gate_checks`, calling `required_read_problem` | G3 | RequiredReadsThroughTheOfferChecker (phase_gate's 14 cases) |
| Report guides read before render_report.py | approval.py `kept_gate_checks`, calling `unread_report_guides` | — | RecordWritesThroughTheOfferChecker (phase_gate's three report-guide cases) |
| Canonical task records only through record.py | approval.py `kept_gate_checks` | — | RecordWritesThroughTheOfferChecker |
| Styling notes | approval.py: a refusal while the CSS switch is off; phase_gate's PostToolUse note stays | C-CSS-1/2 | ProtectedOperations, `test_gate_notes.py` |
| Approval line quoting the owner's words, report fingerprints, revisions `rN`, report `write_paths`, small-change and Reconfirmed lines, the lightweight `git commit`, task switches (N4), the report waiver (P1), unnumbered chat plans (P3) | legacy-only: phase_gate, reached through approval.py for a task in the owner's inventory | C-LEG-1 | `test_phase_gate_hook.py`, `test_gate_regressions.py`, `test_session_failures.py`, LegacyDispatch, `test_cutover.py` |

Removed with their hooks at T20:

| Check | Where it lives now | Tests |
|---|---|---|
| Stop: "Done" with code changed after the last review | `workflow-deliver/scripts/completion_check.py check` before Done | `test_completion_check.py` |
| Stop: package phase reads not opened | each phase SKILL.md names its reads; project-declared reads stay enforced at PreToolUse | `test_cutover.py` PhaseReferences, RequiredReadsThroughTheOfferChecker |
| Stop: a BEHIND rules stamp nobody mentioned | `workflow/RULES.md`: give its SAY sentence once (and rules_stamp.py's own output says so) | — (instruction) |
| phase_reads: per-phase read reminders | the phases name them (above); the READS table lives in `hooks/read_evidence.py` | PhaseReferences |
| truncated_read: partial-read warnings | dropped by design (REDESIGN P9: they fired on legitimate inspection) | — |
| duplicate_skills: pausing change skills while a copy exists | diagnose only: the session start note names the copies and the ways to settle them | `test_duplicate_skills_hook.py` |

The read-evidence library (`hooks/read_evidence.py`, formerly part of plain_reply.py) fails closed at the kept required-read and report-guide checks when it's missing or broken.

The offer route never calls the legacy approval functions (`judge`, `approval_problem`, `small_approval_problem`, `approved_write_paths`): OfferRouteNeverUsesLegacyApproval.

**Retirement.** The legacy-only code and the PostToolUse/UserPromptSubmit fingerprint registrations are removed only after at least two releases **and** diagnostics showing that no active task depends on a legacy approval. An inventory that still lists a task does not prove that task is active, and one machine's empty inventories don't prove other workspaces migrated. The shared helpers first move to their own module. Not in this release.
