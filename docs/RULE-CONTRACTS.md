# Rule contracts

For each hard rule of workflow-axa, this file says when it applies, what it covers, what must already be true, what the agent must do, what is excluded, what to do when blocked, and what checks it. It then labels the main rules of each skill. The owner file states each rule in full and wins when the two differ.

## Three kinds of rule

| Kind | Meaning |
|---|---|
| Hard rule | Must always hold. A break is a defect, even when the result looks right. |
| Procedure | The expected order of steps. The agent records a justified deviation. |
| Judgment call | The agent decides with a stated criterion. Two good runs can differ. |

"Checked by" names a hook, a test or "instructions only". A hook runs on matching tool calls in Claude Code. `phase_gate.py` is active only after the session typed, loaded or read the `workflow` router or a phase skill (`hooks/phase_gate.py:2369`). Codex runs no hook from this package (`skills/workflow/SETUP.md`). A test runs on this package's scripts and texts, not on a live session.

## Hard rule contracts

### Agreement (checkpoint label `Agreement (gate one)`)

- Owner: `skills/workflow/VISUAL-REVIEW.md` "The gates"; asked in `workflow-clarify` step 4.
- Applies when: a new goal, feature, behavior fix, architecture change or material scope change.
- Scope: behavior, scope, exclusions, journeys, acceptance, assumptions. Allows tickets and the plan report, never code.
- Preconditions: rules ready or a limited exception; task folder exists; journeys traced; no open choice.
- Action: summarize, ask the agreement question, stop. Record the answer on the `Agreement` line and in DECISIONS.
- Exceptions: inspect-only work, docs-only work and PDF deliverables (their own route), lightweight edit, small change, "Both gates in one message", an explicit bounded waiver, legacy single-gate approval.
- When blocked: wait. Reopened items go back to grilling. Record the blocking question and what can still proceed (`workflow-clarify` "Next").
- Checked by: hook `phase_gate.py` (since 2.8.0-rc.38), on the two-gate route only. A checkpoint with an `Approval (gate two)` line whose approval is not legacy needs an `Agreement (gate one):` or plain `Agreement:` line that says agreed, waived, legacy or "not required". Until then, project and Git writes are refused after the approval check passes (`agreement_problem` `:1327`, called at `:2072`, patterns `:1322` to `:1324`).
  - The first state word decides: "agreed ..., awaiting approval" passes, but a line that starts with a word such as "pending", "proposed", "awaiting" or "not agreed" is refused. Quoted owner words never decide the state.
  - Not checked: single-gate tasks, legacy approvals, lightweight edits and the small change route.
  - Limit: the hook reads the state word, not whether the agreement covers the work.

  Tests: `tests/test_gate_regressions.py` (`AgreementGateRegressions`); `tests/test_task_report.py` (`task_report.py:71` refuses an approval-ready report without a recorded agreement).

### Implementation approval (checkpoint label `Approval (gate two)`)

- Owner: `skills/workflow/VISUAL-REVIEW.md` "Prepare the report" and "Read the answer"; asked in `workflow-specify` step 5.
- Applies when: before application code, tests, dependencies, migrations or Git writes in a workflow task.
- Scope: the tickets, their checks, the plan report and its `write_paths`. The owner's own "no report" removes the report, never the approval.
- Preconditions: agreement recorded (or the combined case); tickets in TODO; report rendered, read whole, path in the question.
- Action: ask, stop, record the owner's whole answer in quotes with the revision and report.
- Exceptions: lightweight edit; small change; an explicit "I don't need to see the plan" (the hook does not accept it yet: hook candidate 6); legacy approval.
- When blocked: wait; only task records and the report change. Fix a hook refusal by recording the owner's real words or through `resume-task`, never by editing or disabling the hook.
- Checked by: hook `phase_gate.py`:
  - no `Approval` line: `:1810`; not approving, or "proposed": `:1815`, `:1817`;
  - no quoted words, or a quoted refusal: `:1845`, `:1846`;
  - each quote must be a whole user message after the plan was presented: `:1862`, `:1885`;
  - an `.html` report must exist unless the quote declines one: `:1907`, `:1899`, decline words at `:89`;
  - a write outside the report's `write_paths`: `:2078`; a stopped or paused task: `:2381`;
  - the checkpoint is the section under the first heading of any level whose text starts "Current checkpoint", up to the next heading of the same or a higher level (`:1345`); a `# ` line inside a fenced code block also ends it;
  - task records and `.artifacts` stay writable: `:65`, `:264`, `:2354`; bulk deletes there are refused (Artifact cleanup).

  Tests: `tests/test_phase_gate_hook.py`, `tests/test_gate_regressions.py`.

### Small change

- Owner: `skills/workflow/VISUAL-REVIEW.md` "Small change".
- Applies when: a visible edit to text, order or visibility of existing elements on one screen, in a task folder with no report.
- Scope: exactly the listed existing files.
- Preconditions: a checkpoint line `- Small change: <files> — <what changes>`; no open choice.
- Action: show that line in one message, ask for a yes, end the turn. Record the whole answer, edit only the listed files, test, review once, deliver in short form.
- Exceptions: none for the file list. A changed list or description needs a new offer; a later session needs a `Reconfirmed` line.
- When blocked: growing scope or risk moves to the full route (`workflow-clarify`, then the plan report).
- Checked by: hook `phase_gate.py`: route only without a report `:2052`; files must exist `:1677`; offer required `:1699`, `:1701`; quote is a whole later message `:1705`, `:1708`; deletes `:1751`, moves `:1753`, other or new files `:1755` refused. Contents (since 2.8.0-rc.38): after an Edit, Write or MultiEdit of a listed file, a note names each tag or class the edit adds (`style_notes` `:2534`). The note never refuses the edit. Limits: code such as `Array<string>` gives a false tag note. When `git show` fails, every existing tag and class in a Write counts as new. Tests: `tests/test_gate_regressions.py` (`SmallChangeRoute`), `tests/test_gate_notes.py` (`StyleNotes`). Whether it qualifies: instructions only.

### Never write CSS, and DESIGN.md rule 4's question

- Owner: `skills/rule-maker/rules/DESIGN.md` rules 1 to 5; `ui-design` applies them.
- Applies when: any application UI work, ordinary prompts and small edits included. Not backend-only work.
- Scope: stylesheets, `<style>`, `style=""`, CSS-in-JS, theme overrides, visual props, script style changes, new classes or IDs.
- Preconditions: the design kit (if any) and the existing code were searched for an element doing the same job for the same user.
- Action: mirror that element's tag, full class list and context. When nothing matches, stop that element and ask the exact question, listing only same-tag elements. Before finishing, check the diff and name each class's defining file.
- Exceptions: plain unstyled HTML on the user's explicit instruction for the named element, or when the user answers rule 4's question by confirming that no similar element exists; the report renderer's shell and `quick_previews`; internals of reused components.
- When blocked: the element is in mode `blocked` and waits for the answer; independent logic and tests continue (DESIGN.md "Modes").
- Checked by: a hook note that never blocks (`phase_gate.py`, since 2.8.0-rc.38). In an active session, after an Edit, Write or MultiEdit of an application file, the gate adds a note when the edit adds styling (`style_notes` `:2534`, added to the PostToolUse output at `:2622`). The note asks for rule 4's question or the name of the existing class.
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
- Checked by: hook `phase_gate.py` (since 2.8.0-rc.38), bulk forms only, in an active session. The check runs before the `.artifacts` write exemption (`bulk_delete` `:180`, called at `:2352`, refusal at `:2378`).
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

Hard rules with instructions only, or with a known hook gap. Release 2.8.0-rc.38 built candidates 2 to 5. Candidates 1 and 6 stay unchanged by owner decision (2026-11-12, Q6 c of task 2026-11-12-approval-gate-false-refusals). Candidate 7 is partly built in 2.8.0-rc.39; candidate 8 is not built.

1. Report decline words (seen on 2026-11-12). Owner decision: unchanged. The agent asks for "no report" words when needed. `hooks/phase_gate.py:89` `NO_REPORT` matches "no report", "no plan report", "no html report" and "without a report", but not the owner's own "no review.html is needed", so the gate refused an approved task. A hook could also accept a whole quoted answer that declines the report by file name or by "no ... needed". Limit: a wider pattern can read "no code review needed" as a report waiver.
2. Agreement before approval. Done in 2.8.0-rc.38: the hook refuses project and Git writes, not the `Approval` line itself, while the `Agreement` line of a two-gate task is not agreed, waived, legacy or not required (Agreement contract above). Limit: it checks the state word, not whether the agreement covers the work.
3. No new CSS. Done in 2.8.0-rc.38 as a note that never blocks (owner Q8 a), because the cues also match legitimate code (contract "Never write CSS" above). Limit: the hook cannot see design kit authority, and shell writes get no note.
4. Bulk artifact deletes. Done in 2.8.0-rc.38: `git clean`, a delete of `.artifacts` itself and wildcard deletes under it are refused (Artifact cleanup contract above). Limit: it cannot judge ownership or consumers, so it catches only bulk forms.
5. Small change contents. Done in 2.8.0-rc.38 as a note that never blocks: a new tag or class in a listed file (Small change contract above). Limit: a heuristic; text edits inside markup are hard to separate from new elements.
6. Plan waiver. Owner decision: unchanged. VISUAL-REVIEW.md accepts an explicit "I don't need to see the plan, go" as a waiver of implementation approval, but the hook still asks for a report or a "no report" quote (`hooks/phase_gate.py:1899`, `:1907`). A hook could accept a recorded `waived` Approval line whose quote declines seeing the plan. Limit: the same wording risk as candidate 1.
7. Approval answers the gate cannot match (seen on 2026-11-12). Bold or italic typed answers: done in 2.8.0-rc.39 (`bare` at `:880`; only the quote comparison ignores the markers). Still open: in T3 Code (observed 2026-11-12) the visible text of an assistant message that also calls a tool is not stored in the session log, so a plan presented in such a message, then answered in the question box, does not count; a hook could count an answered question whose own text names the plan, the task path and the revision. A one-word "Approve" cannot be recorded for a task without a report, because the quote must then decline the report ("no report"). A hook could accept those forms. Limit: looser matching can count a reply that is not an approval.
8. Approvals in linked worktrees (seen on 2026-11-12, E10 and E11). A linked worktree never borrows the main checkout's approval, and a subagent in a linked worktree cannot see the main session's transcript, so its first write is refused. Release 2.8.0-rc.38 only names the two differing PLAN copies in the refusal (`worktree_copy_note` `:2400`). A hook could accept an approval recorded for the same task in the main checkout. Limit: that weakens the rule that approval evidence is bound to its workspace.

## Known gaps

No check covers these:

- Whether a change qualifies as a small change or a lightweight edit.
- What an approval means. The hook matches the owner's whole message after the presentation, not its intent.
- Whether the built result matches the agreement; `workflow-deliver` reconciles it by review only.
- Every rule in sessions where neither the router nor a phase skill was typed, loaded or read (`hooks/phase_gate.py:2369`), and on Codex.
- Shell writes the gate cannot parse; its docstring calls command-text filtering advice, not a security boundary.
- Whether rule 4's question was asked word for word, and whether a plain-HTML exception came from an explicit instruction.
- Whether a delete of named files or folders under `.artifacts` was authorized. The hook refuses only bulk forms.
- Whether the recorded agreement covers the work. The hook reads only the state word on the `Agreement` line.
- Styling or markup that the cues do not match (computed styles, shell writes), and what the agent did after a note. Notes never block.
