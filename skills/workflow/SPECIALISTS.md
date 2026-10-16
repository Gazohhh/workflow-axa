# Specialist routing

The workflow coordinates; installed specialists supply the task discipline. Use the
applicable route below, not a home-made substitute. Load only the current specialist
and references its branch needs. Installation is not invocation, and invocation is not
proof of a correct result. The host's permissions and instruction precedence still apply.

## Preflight

After resolving and creating or resuming the minimal task record, check the current host's actual skill inventory.
At team setup verify the collection in [specialists.json](specialists.json); during work
verify only routes needed by the next phase. Recheck after a host/account switch, reload,
installation change or revised route—not before every tool call.

Resolve the source, installed identifier/path, revision or content fingerprint, enabled
state, model-invocation policy, required references/tools and project configuration.
Use the qualified identifier advertised by the host, especially for generic names such
as `research`, `tdd` and `code-review`. An unrelated skill with the same name is not the selected provider's.
Do not infer absence from a user-facing slash menu alone; model-only skills can be hidden.

The read-only [checker](scripts/check_specialists.py) helps inventory explicitly supplied
local roots; see [SETUP.md](SETUP.md). It cannot establish the host's registry, permissions,
source authenticity or successful execution. Record those separately. Do not bypass a
host-disabled skill by reading its files as a workaround. On a host whose documented
skill mechanism is reading files, that is a valid load—not a simulated tool invocation.

Record a compact capability entry in FINDINGS (or the lightweight record): host/version,
resolved source/identifier/fingerprint, availability evidence, applicable routes, adapters,
exceptions and output references. A team-approved installation snapshot can be linked.
Do not copy full skill bodies into task records. If a selected dependency changes, pause
its dependent phase for compatibility review; never silently approve a new baseline.

Missing, disabled, ambiguous, incompatible or unverified selected skills: report once,
record the blocked phase, and continue only independent authorized work. Use an already
approved fallback or ask once to approve setup/fallback. Creating the checkpoint and
asking how to resolve a missing skill do not require that missing skill. Do not install,
update, enable or rewrite specialist files without explicit setup authority.

## Routes and call contract

Before each call provide: task/approval paths, precise question or work unit, settled
answers, allowed writes, relevant files/diff, required output location and the applicable
adapter below. Invoke/load through the host's real skill mechanism; inspect the result
and record its contribution. Reuse a loaded reference in the same phase; do not repeatedly
invoke it for every TODO or comment. Nested specialist calls use these same boundaries.

| Trigger | Invoke | Required contribution / adapter |
|---|---|---|
| Every new substantive goal, material scope change, or requested grilling; also newly uncovered consequential decisions | `grilling` | Inspect for missing decisions even when none were initially noticed; reuse sourced settled branches; Q adapter. No question quota or repeated interview for an unchanged approved resume. |
| External technical research, documentation/API checks or source investigation | `research` | Primary-source findings and citations into the existing task evidence; R adapter. Local code inspection alone need not launch research. |
| A bug, failing behavior or performance regression needs diagnosis | `diagnosing-bugs` | Symptom-specific feedback loop, evidence, causal diagnosis and cleanup; D adapter. Stop before an unauthorized fix. |
| Test-first feature/fix work or integration tests at agreed observable interfaces | `tdd` | One behavioral test and implementation slice at a time; T adapter. Propose seams during planning and reuse their approval. |
| Module interfaces, abstractions or test boundaries need design review | `codebase-design` | Apply its design reference to the bounded choice; no new architecture interview when the design is settled. |
| Project terminology, glossary or an architecture decision is being changed | `domain-modeling` | Clarify terms and capture approved changes at their authoritative location; M adapter. Merely reading a glossary does not trigger it. |
| Creating/revising skills, agent instructions or the structure of agent-facing records | `writing-for-agents` | Apply its writing/reference mechanics plus the local plain-language policy; ordinary checkpoint updates need no new invocation. |
| Task code changes are ready for review, or a code review is requested | `code-review` | Separate Standards and Spec findings on the actual task changes; C adapter. Docs-only work still gets the workflow audit. |
| The user authorizes a throwaway prototype to settle a design question | `prototype` | Evidence and a bounded disposable artifact; P adapter. Research approval alone does not authorize prototype code. |
| A pull-request description is requested | `pr` | Draft from real evidence; do not open, publish or merge a PR without separate authorization. |
| An approved procedure requires human-only setup/migration steps | `wizard` | A reviewed human-run procedure using its template; W adapter. Not for work the agent can perform itself. |

### Explicit adapters

These are team-approved integration changes, not a blanket “workflow wins” rule. Pass
them in the call brief. If the host cannot apply the contract without conflicting
instructions, do not invoke the specialist unchanged: record incompatibility and use
an approved fallback. Never edit an installed upstream skill to hide the conflict.

- **Q — Questions:** inspect the bounded goal for unstated consequential decisions, not
  only an already-written question list. Use the decision areas and answer-source checks
  in [QUESTIONS.md](QUESTIONS.md). Research facts; batch nonblocking questions, ask early
  for direction blockers, and reuse sourced settled branches. No invented scope or question
  quota. A detailed prompt is not an exemption; unchanged approved work is not re-interviewed.
  Apply [WRITING.md](WRITING.md) to questions and consequences. The owner persists partial
  answers and returns them to the specialist. Shared understanding and implementation
  approval are confirmed through VISUAL-REVIEW.md, not assumed from interview completion.
- **R — Research:** return cited findings to the owner for FINDINGS.md; no second competing
  report unless requested. A subagent can research in the active host session when useful;
  without that capability, run sequentially and label it. Promise no later/background result.
- **D — Diagnosis:** authorize diagnostic writes/probes in the task scope before running
  them; isolate bisection from user changes. No production probes, destructive commands,
  stress load, fixes or installs beyond approval. Show ranked hypotheses as an update, not
  a new routine approval. If reproduction is unavailable, report the gap rather than a
  verified cause. Record the cause in findings, not an automatic commit/PR.
- **T — Tests:** pass the previously approved seams, expected behavior and test command.
  Ask only for a genuinely new seam/contract decision. Missing infrastructure is a blocker,
  not permission to install a runner, weaken a test or claim the red/green loop happened.
- **M — Domain:** confirm changed meaning; update approved glossary/ADR paths, not a new
  parallel documentation system. Put unresolved proposals in task decisions first. Batch
  nonblocking terminology questions; new policy documents still need approval.
- **C — Review:** supply PLAN.md's approved criteria as the spec and the initial worktree
  checkpoint as the attribution baseline. Include task-attributable staged, unstaged and
  untracked changes; `git diff <base>...HEAD` alone misses uncommitted work. A plain HEAD
  diff is also insufficient when initial user edits exist. Do not invent a merge-base,
  fetch/create an issue, stage or commit just to obtain a diff. Keep Standards and Spec
  distinct, map [AUDIT.md](AUDIT.md) findings to each, and rerun affected review/checks after
  repairs. When attribution is uncertain, resolve it before claiming a complete review.
- **P — Prototype:** agree the branch of the design question rather than guessing when
  ambiguous. Bound files, runtime and cleanup in the plan. Keep evidence in approved task
  artifacts; no automatic capture commit, branch publication or production integration.
- **W — Wizard:** author only the approved stages; inspect before execution, protect secrets,
  and let the human run interactive steps. Bash/WSL availability is a prerequisite. Reuse
  approved stages, but retain actual safety confirmations. No automatic commit, external
  account changes or uploading credentials to task evidence.

All specialists may use useful available subagents; otherwise apply the approved
sequential adapter and identify self-review as such. Only the owner writes task records;
helpers return evidence. This capability adapter does not authorize silently replacing
a missing specialist with an improvised implementation.

## Manual workflows are not automatic dependencies

`grill-me` is a user-facing wrapper around `grilling`, not its automatic invocation alias.
Matt's setup, handoff, spec/ticket, implementation and other user-only workflows are listed
as `manual` in the catalogue. Do not call them automatically, strip their invocation flags,
or chain them into this workflow. `implement` / `implement-spec` are competing execution
workflows; some also commit. `to-spec` / `to-tickets` may publish to a tracker. Existing
PLAN/TODO records remain authoritative; the package does not require a parallel tracker.

When the user explicitly chooses a manual workflow, confirm only unresolved integration
boundaries and use their existing approvals. Installation setup is a separate authorized
operation; [SETUP.md](SETUP.md) explains how to keep its output compatible with this workflow.

## Local visualization route

Invoke this package's **`codebase-map`** for an explicit flowchart/map request and automatically for the substantive preimplementation visual review in [VISUAL-REVIEW.md](VISUAL-REVIEW.md). Resolve its actual qualified identifier and verify availability during setup/handoff. Pass inspected evidence, requirements/tasks/acceptance, mode, revision and artifact permissions. It returns the local source/report paths, freshness result and opener result; it never implements, approves, grills or calls back into workflow. Do not invoke Matt's user-only `improve-codebase-architecture` merely to draw a current flow. Missing visualizer/render capability follows the explicit setup/fallback decision path; never skip approval silently.

The visual design procedure, assets and renderer are local to `codebase-map`. It reads its bundled FLOWCHART-DESIGN.md; no external diagram skill or separate diagram-design preflight is required. Matt's established specialist providers remain; the Q adapter above strengthens decision discovery. A local render is not logged as an external specialist invocation.

## Optional maintenance/browser helpers

[OPTIONAL-HELPERS.md](OPTIONAL-HELPERS.md) covers skill-creator and webapp-testing as opt-in candidates. They are not part of the required Matt catalogue, not installed automatically, and not prerequisites for normal workflow or diagram delivery.
