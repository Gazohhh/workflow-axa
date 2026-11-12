# Rule contracts

For each hard rule of workflow-axa, this file says when it applies, what it covers, what must already be true, what the agent must do, what is excluded, what to do when blocked, and what checks it. It then labels the main rules of each skill. The owner file states each rule in full and wins when the two differ.

## Three kinds of rule

| Kind | Meaning |
|---|---|
| Hard rule | Must always hold. A break is a defect, even when the result looks right. |
| Procedure | The expected order of steps. The agent records a justified deviation. |
| Judgment call | The agent decides with a stated criterion. Two good runs can differ. |

"Checked by" names a hook, a test or "instructions only". A hook runs on matching tool calls in Claude Code. `phase_gate.py` is active only after the session typed, loaded or read the `workflow` router or a phase skill (`hooks/phase_gate.py:2278`). Codex runs no hook from this package (`skills/workflow/SETUP.md`). A test runs on this package's scripts and texts, not on a live session.

## Hard rule contracts

### Agreement (checkpoint label `Agreement (gate one)`)

- Owner: `skills/workflow/VISUAL-REVIEW.md` "The gates"; asked in `workflow-clarify` step 4.
- Applies when: a new goal, feature, behavior fix, architecture change or material scope change.
- Scope: behavior, scope, exclusions, journeys, acceptance, assumptions. Allows tickets and the plan report, never code.
- Preconditions: rules ready or a limited exception; task folder exists; journeys traced; no open choice.
- Action: summarize, ask the agreement question, stop. Record the answer on the `Agreement` line and in DECISIONS.
- Exceptions: inspect-only work, docs-only work and PDF deliverables (their own route), lightweight edit, small change, "Both gates in one message", an explicit bounded waiver, legacy single-gate approval.
- When blocked: wait. Reopened items go back to grilling. Record the blocking question and what can still proceed (`workflow-clarify` "Next").
- Checked by: no hook; `phase_gate.py` has no pattern for the `Agreement` line. Test: `tests/test_task_report.py` (`task_report.py:71` refuses an approval-ready report without a recorded agreement).

### Implementation approval (checkpoint label `Approval (gate two)`)

- Owner: `skills/workflow/VISUAL-REVIEW.md` "Prepare the report" and "Read the answer"; asked in `workflow-specify` step 5.
- Applies when: before application code, tests, dependencies, migrations or Git writes in a workflow task.
- Scope: the tickets, their checks, the plan report and its `write_paths`. The owner's own "no report" removes the report, never the approval.
- Preconditions: agreement recorded (or the combined case); tickets in TODO; report rendered, read whole, path in the question.
- Action: ask, stop, record the owner's whole answer in quotes with the revision and report.
- Exceptions: lightweight edit; small change; an explicit "I don't need to see the plan" (the hook does not accept it yet: hook candidate 6); legacy approval.
- When blocked: wait; only task records and the report change. Fix a hook refusal by recording the owner's real words or through `resume-task`, never by editing or disabling the hook.
- Checked by: hook `phase_gate.py`:
  - no `Approval` line: `:1726`; not approving, or "proposed": `:1731`, `:1733`;
  - no quoted words, or a quoted refusal: `:1761`, `:1762`;
  - each quote must be a whole user message after the plan was presented: `:1778`, `:1801`;
  - an `.html` report must exist unless the quote declines one: `:1823`, `:1815`, decline words at `:87`;
  - a write outside the report's `write_paths`: `:1988`; a stopped or paused task: `:2288`;
  - task records and `.artifacts` stay writable: `:63`, `:219`, `:2263`.

  Tests: `tests/test_phase_gate_hook.py`, `tests/test_gate_regressions.py`.

### Small change

- Owner: `skills/workflow/VISUAL-REVIEW.md` "Small change".
- Applies when: a visible edit to text, order or visibility of existing elements on one screen, in a task folder with no report.
- Scope: exactly the listed existing files.
- Preconditions: a checkpoint line `- Small change: <files> — <what changes>`; no open choice.
- Action: show that line in one message, ask for a yes, end the turn. Record the whole answer, edit only the listed files, test, review once, deliver in short form.
- Exceptions: none for the file list. A changed list or description needs a new offer; a later session needs a `Reconfirmed` line.
- When blocked: growing scope or risk moves to the full route (`workflow-clarify`, then the plan report).
- Checked by: hook `phase_gate.py`: route only without a report `:1968`; files must exist `:1593`; offer required `:1615`, `:1617`; quote is a whole later message `:1621`, `:1624`; deletes `:1667`, moves `:1669`, other or new files `:1671` refused. Test: `tests/test_gate_regressions.py` (`SmallChangeRoute`). Whether it qualifies: instructions only.

### Never write CSS, and DESIGN.md rule 4's question

- Owner: `skills/rule-maker/rules/DESIGN.md` rules 1 to 5; `ui-design` applies them.
- Applies when: any application UI work, ordinary prompts and small edits included. Not backend-only work.
- Scope: stylesheets, `<style>`, `style=""`, CSS-in-JS, theme overrides, visual props, script style changes, new classes or IDs.
- Preconditions: the design kit (if any) and the existing code were searched for an element doing the same job for the same user.
- Action: mirror that element's tag, full class list and context. When nothing matches, stop that element and ask the exact question, listing only same-tag elements. Before finishing, check the diff and name each class's defining file.
- Exceptions: plain unstyled HTML on the user's explicit instruction for the named element, or when the user answers rule 4's question by confirming that no similar element exists; the report renderer's shell and `quick_previews`; internals of reused components.
- When blocked: the element is in mode `blocked` and waits for the answer; independent logic and tests continue (DESIGN.md "Modes").
- Checked by: no hook. `skills/ui-design/scripts/review_ui_diff.py` lists style cues in a diff for review and grants or refuses nothing. Test: `tests/test_ui_design.py` (the cues, and that DESIGN.md holds the rule and the question). In a session: instructions only.

### Artifact cleanup

- Owner: `skills/workflow/ARTIFACTS.md`, installed as `~/.workflow-axa/ARTIFACTS.md`.
- Applies when: tests, builds, device or browser checks, profiling and delegated work, with or without `/workflow`.
- Scope: output the agent places under the task's output parent (default `.artifacts/<task>/`).
- Preconditions: the parent, each file's owner, active consumers and protected paths are known.
- Action: reuse one stable parent; keep the smallest evidence set; delete only the agent's own disposable output from the current work when every listed condition holds; record what stays and the next cleanup condition.
- Exceptions: deliverables, approved reports, baselines, rollback data and tool-owned output are protected. Superseded reports follow VISUAL-REVIEW.md "Superseded review cleanup".
- When blocked: unclear ownership, or older or unknown output: preserve it and ask. No `git clean`, wildcard delete or blanket wipe.
- Checked by: no hook; `phase_gate.py` leaves `.artifacts` writable (`:63`, `:219`), so deletes there pass unchecked. Test: `tests/test_global_policy.py` installs the policy text only. Instructions only.

## Rules per skill

Owner file: `skills/<skill>/SKILL.md` unless named.

| Skill | Hard rules | Procedures | Judgment calls |
|---|---|---|---|
| workflow | Inspect stays read-only; no Git writes unasked; changes pass the gates | Rules readiness; find the task; first matching route row | Intent; whether a message belongs to the task |
| workflow-clarify | No code; stop for agreement; never offer CSS | Trace journeys; grill; write the agreement | Which question blocks; when tracing is done |
| workflow-specify | No code or tests; stop for approval | Vertical tickets; bigger checks; plan report | When plan-review runs; where behavior belongs |
| workflow-execute | Approval first; never weaken a test; never install | Ticket loop; whole-feature review | Small route or worker; what is material |
| workflow-deliver | Never fixes or approves; no checks after a stop | Freeze state; verdict per requirement; Outcome and report | Which contradiction is unsafe |
| codebase-map | Never implements or approves; no invented markup | Choose the view; validate, render, open | Mode and geometry |
| task-status | Read-only; a badge is not authority | `open_items.py`; reconcile records | Status of each item |
| resume-task | Never rewrite the Approval quote or bypass the hook | Readiness; reconcile worktree; continue the routed phase | Whether scope changed materially |
| workflow-doctor | Changes nothing | Package, hooks, policy and rules checks | The PASS, WARNING or BLOCKED grade |
| plan-review | Never implements or approves | Authority; traceability; necessity check | What is unnecessary scope |
| rule-maker | Apply only an approved proposal; shared library read-only | Audit; apply; check | Which claims to sample; severity |
| ui-design | DESIGN.md rules (owner `rule-maker/rules/DESIGN.md`) | Pick a mode; record the mirrored element; screen diagram | Which element does the same job |
| grilling | Never offer a forbidden option; rule 4's question word for word | Research first; rounds; save each question before sending | Ask only what the user must decide; when to stop |
| tdd | Report only what ran; test only at agreed seams | Red, green, refactor; one slice at a time | Spotting anti-patterns |
| code-review | The Standards and Spec axes stay separate | Pin the diff; find sources; run and aggregate | Whether each baseline smell applies |
| writing-for-agents | None | Context pointers; information hierarchy | No-op test; when to split; pruning |
| codebase-design | Project ownership and approved rules win | Deletion test before a new layer | Depth; seam placement |
| domain-modeling | A new glossary or ADR needs approval | Record a term in DECISIONS, then the glossary | Whether an ADR is worth offering |
| implement-spec | Reference only; never run as written | None | None |
| retro | Only the user starts one; fixes need approval | Digest sessions; categories; ranked candidates | Severity; mechanical versus judgment |
| simple-english | Never change code, quotes or rule 4's question | Document rules; self-check | When plain words lose the meaning |

## Hook candidates

Hard rules with instructions only, or with a known hook gap. None of these is built yet.

1. Report decline words (seen on 2026-11-12). `hooks/phase_gate.py:87` `NO_REPORT` matches "no report", "no plan report", "no html report" and "without a report", but not the owner's own "no review.html is needed", so the gate refused an approved task. A hook could also accept a whole quoted answer that declines the report by file name or by "no ... needed". Limit: a wider pattern can read "no code review needed" as a report waiver.
2. Agreement before approval. A hook could refuse an `Approval` line while the `Agreement` line is not agreed, waived, legacy or not required. Limit: it checks the label, not whether the agreement covers the work.
3. No new CSS. While the gate is active, a hook could run the `review_ui_diff.py` cues on edits to application files and refuse a new stylesheet rule, `<style>` or `style=""`. Limit: cues also match legitimate code, the hook cannot see design kit authority, and shell writes are read best effort.
4. Bulk artifact deletes. A hook could refuse `git clean`, a recursive delete of `.artifacts` itself, and wildcard deletes under it. Limit: it cannot judge ownership or consumers, so it catches only bulk forms.
5. Small change contents. A hook could compare the listed files before and after and refuse a new tag, class or attribute. Limit: a heuristic; text edits inside markup are hard to separate from new elements.
6. Plan waiver. VISUAL-REVIEW.md accepts an explicit "I don't need to see the plan, go" as a waiver of implementation approval, but the hook still asks for a report or a "no report" quote (`hooks/phase_gate.py:1815`, `:1823`). A hook could accept a recorded `waived` Approval line whose quote declines seeing the plan. Limit: the same wording risk as candidate 1.

## Known gaps

No check covers these:

- Whether a change qualifies as a small change or a lightweight edit.
- What an approval means. The hook matches the owner's whole message after the presentation, not its intent.
- Whether the built result matches the agreement; `workflow-deliver` reconciles it by review only.
- Every rule in sessions where neither the router nor a phase skill was typed, loaded or read (`hooks/phase_gate.py:2278`), and on Codex.
- Shell writes the gate cannot parse; its docstring calls command-text filtering advice, not a security boundary.
- Whether rule 4's question was asked word for word, and whether a plain-HTML exception came from an explicit instruction.
- Whether an artifact cleanup was authorized.
