# Visual understanding and implementation approval

## When it applies

For substantive feature work, behavioral fixes and architectural changes, prepare the HTML review after research, necessary questions and PLAN/TODO/acceptance preparation, and before application implementation. “End of TODO” means after writing the task list, not executing it. Pure research, explanation, docs-only/PDF delivery and genuinely lightweight edits retain their appropriate routes. An explicitly requested visual-only map does not authorize implementation.

Prior explicit approval of the same presented revision remains valid, including on resumption. A new bare feature request or generic “go ahead” is not approval of an unseen plan. A user may explicitly waive this review for a bounded task; record the waiver, scope and remaining decision boundaries. Do not use initial general authorization or time pressure as an implied waiver.

## Prepare and show

1. Complete the proactive grilling decision check and resolve choices affecting the implementation scope. Reuse a still-valid check for unchanged approved work; do not use the diagram to bypass questions. Keep unknowns visible. A remaining blocking choice makes this a **draft**, not approval-ready.
2. Invoke the installed `codebase-map` in compare mode with the task location/revision, requirement/evidence/task IDs, current-code snapshot, allowed artifact directory and audience. For new code, the current panel can show the verified existing integration point or absence of the requested capability; do not invent an old implementation.
3. `codebase-map` reads its bundled FLOWCHART-DESIGN.md and uses the local renderer with the approved editorial style; no external diagram skill is required. The actual feature flowchart opens first; never substitute wireflow cards or a generic implementation checklist. Separate build dependencies and settings/ownership structure where useful. Use typed start/action/decision/result shapes, labelled branches and uncluttered orthogonal connectors. Keep technical references in the appendix, but exclusions, material uncertainties and acceptance visible. Render the requested feature/user/data flow, not merely this workflow's research-plan-code phases. Show understood outcome, current flow, proposed behavior, unchanged/added/modified/removed areas, scope exclusions, mapped tasks/cleanup and acceptance checks. Proposed relationships are proposals, not observed code.
4. Apply [WRITING.md](WRITING.md): check that a new reader can explain the change and decision without prior chat, while technical evidence remains accessible. Save revisioned report/source artifacts in the task's artifact directory. PLAN/TODO/FINDINGS/DECISIONS remain authoritative; JSON/HTML are derived projections, not competing specifications. Validate traceability, explicit geometry, actual rendered label fit, desktop/mobile scrolling and supplied-source freshness. Never force-fit a tall diagram into a fixed-height panel. Style changes alone do not approve the application plan or resolve open source questions. Human/agent inspection must judge semantic fidelity; script validation cannot.
5. Request opening the local file through the host's available opener. A successful launch request is not proof it displayed. State the absolute path and report actual result. With no GUI, provide the artifact; do not claim it opened or use an external upload. A viewer problem never waives approval.
6. Save `awaiting-approval` and the next safe action. Ask: “Does this match what you want built? Approve this plan to proceed, or describe what needs changing.” **Stop.** Do not start tests/code changes in parallel while waiting.

Before approval, only permitted investigation and task artifacts may be written. No application code, new test implementation, installed dependencies, migrations, glossary edits, production probes or Git actions are authorized by the preview. Read-only inspections and already authorized baseline checks remain valid. Explicitly approved diagnostic/prototype work stays limited to its separate scope.

## Interpret and persist approval

An unambiguous “yes, proceed” answering this review approves the identified revision without magic syntax. Opening the file, choosing a diagram mode, answering grilling, silence, or “looks nice” does not. No HTML control approves work or sends anything to the agent.

Record the user's response, date/context, revision, report reference, selected options, inclusions and exclusions in PLAN/DECISIONS before implementation. The approved plan—not a renderer state field—provides authority. A stored approval response must be real, not generated example text.

When the user corrects the understanding, revise requirements, PLAN/TODO, decisions and diagram together; mark earlier proposals superseded and present the new revision. Do not implement the rejected version. A changed outcome, architecture or protected scope needs renewed approval. Routine implementation details and expected progress do not.

A resumed agent verifies the approval record and reconciles the worktree before continuing. It need not regenerate the report or ask again when the same approval remains applicable. Supplied-source hashes expose drift, including uncommitted files, but cannot detect omitted files or prove semantic completeness. A status-only record update may legitimately change a hash without changing approval.
