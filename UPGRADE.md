# Upgrade to workflow-axa 2.8.0-rc.1

## From 2.7.0-rc.8 to 2.8.0-rc.1

2.8.0-rc.1 splits the workflow into a router and four phase skills and adds a second approval gate. The strict UI policy, artifact policy and shared rules library (1.6.0) are carried over from rc.8. Sections 2–5 below still apply.

**Replace all twenty folders together**, as one set from the same version: the eight from section 1, `workflow-clarify`, `workflow-specify`, `workflow-execute`, `workflow-deliver`, and the vendored `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling`, `implement-spec` and `retro`. The Claude plugin registers all twenty. If Matt's own copies of those eight are installed in the same host, the plugin's are namespaced (`workflow-axa:<name>`) and are the ones the workflow loads. For direct installations, copy each complete folder as a sibling of `workflow`; the phase skills read its shared policies (RULES, GROUNDING, WRITING, SPECIALISTS, TASK-FOLDER, VISUAL-REVIEW, AUDIT, ARTIFACTS) and stop if that folder is missing. Do not keep an older eight-skill copy active alongside the new set. Run the section 1 checks afterwards and start fresh sessions.

What changes for people using it:

- **Two approvals for substantive work.** First the user agrees what will be built: behavior, scope, exclusions, journeys, acceptance and assumptions, written in PLAN and summarized in chat. That agreement allows the detailed plan but no code. Then the user approves the specification, tickets, test strategy and HTML report; only this second approval allows application code and tests. Gate definitions: VISUAL-REVIEW.md in the workflow folder.
- **Existing tasks keep their authority.** A task approved under the single gate before this version holds both agreement and implementation authority for its recorded scope. The next checkpoint that touches it records that classification; nobody is asked for a retroactive agreement and no old approval or presented report is rewritten. A task paused before its single approval continues at the gate its records show.
- **Lightweight edits are unchanged.** Exact, unambiguous, low-risk requests keep the short route and a short delivery check. A small behavior or architecture change is not lightweight.
- **Writing.** WRITING.md remains the policy for anything a person reads, now with a meaning-preservation table and a reader-reconstruction check. Matt's `writing-for-agents` governs skill and agent-instruction structure. Nothing new is installed.
- **Specialists.** `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling`, `implement-spec` and `retro` now ship with the package as separate skills; the phases load these copies, so no Matt installation is needed for them. Only `research`, `diagnosing-bugs`, `prototype`, `pr` and `wizard` stay optional installs; a missing one blocks only the step that needs it. `workflow-execute` adapts Implement Spec's ticket graph locally and performs no branch, commit, merge or tracker action.
- **Optional central report.** Report schema 2 accepts an additive `task_report` object for a full engineering overview built from the task records (contract: codebase-map TASK-REPORT.md). Existing inputs and saved HTML need no change; reports without the object render as before. Do not hand-maintain a separate specification in the report JSON.

The project routing block template now names both gates. An existing merged block still works, because the installed `workflow` skill applies both gates, but it describes a single approval. Show the owner the updated sentence in `skills/workflow/templates/PROJECT-ROUTING.md` and merge it only with their approval, preserving unrelated rules and line endings. Review rules-readiness after installation as described in section 1; a changed package version in the shared rules manifest can require a refreshed assessment, without a new task or rewritten history.

## From rc.7 to rc.8

rc.8 is rc.7 plus Windows verification fixes to the ui-design kit checkers and one test. Policy, rules (library 1.6.0) and routing are unchanged from rc.7. Replace all eight folders byte for byte, as described in section 1 below. Everything else in this guide applies unchanged.

## rc.7 guidance (applies to rc.8 and 2.8.0-rc.1)

Full replacement of rc.6, with the owner's stricter **no agent-authored application HTML/CSS/inline styles** policy. No additional external skill or UI framework is required. Review the new restrictions before resuming an old UI plan.

## 1. Replace the actual active package

Update the complete plugin, or all sibling skill folders of the version you install: for 2.8.0-rc.1 all twenty folders (see the plugin's skill list), for rc.7/rc.8 the eight folders workflow, codebase-map, task-status, resume-task, workflow-doctor, plan-review, rule-maker, ui-design; for 2.8.0-rc.1 those eight plus workflow-clarify, workflow-specify, workflow-execute and workflow-deliver (twelve). Keep the stable canonical installation path. Do not merge a few files and leave stale instructions. Review local modifications first and retain a safe previous copy under the existing installation process; do not delete unrelated skills. Matt's 27 catalogue entries are unchanged.

The global rules/artifact activation helpers are unchanged. Existing references work when they point at the same complete current library. From that installed package:

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
```

Use known `--candidate` paths when checking other installations. The helpers do not discover every cache or prove the host chose this copy. A changed rule-manifest fingerprint after installation must be investigated, not rehashed to conceal an incomplete copy. Existing artifact setup stays in place.

If the global rules reference is absent or moved, preview `activate_rules.py`, review the changes, then use `--apply` and `--check`. Never copy a project's full AGENTS.md into a global profile. Start fresh sessions in each actual T3/Claude/Codex profile and test plain prompts as well as /workflow.

A previous rules-readiness assessment references the previous shared-library fingerprint. Refresh the affected assessment against the new library before dependent work; reuse the same task, history and valid approvals. Do not manufacture a new task or rewrite historical records to pass the check.

## 2. Reconcile project pointers, not duplicated rulebooks

Use the installed shared design.md and ui-design contract. Merge the relevant small PROJECT-ROUTING.md update into existing host-loaded project instructions where necessary; preserve unrelated rules and line endings. Surface conflicting old fallback/design-authoring language rather than silently ignoring it. Do not install a new gallery, Storybook, CSS framework or preview route.

- `functionality-only` from older tasks now means behaviour-only: preserve existing appearance, no new raw markup.
- `approved-kit` needs the task's exact valid component/pattern selection, supported variants/states and safe preview.
- `design-authoring` is historical authority, not a current bypass. Pause dependent writes and explain the changed policy. New presentation is for the designated designer/maintainer unless the owner separately changes policy.
- Existing HTML/CSS is not removed. Unaffected approved work continues. No mass migration of old task records or public screens.

## 3. Connect a real project kit only when authorised

Run `ui-design kit-audit <area>` against designated existing component/preview sources. LIVE-KIT.md explains the code-backed catalogue: components/examples once, generated current references, human approval once, short project pointer. Installing this package does not create or synchronise a React/Angular page in your project.

The optional `inspect_kit_index.py` reads an existing local Storybook index with no writes, network or source execution. It reports missing/deleted imports and selected catalogue coverage. Actual story compilation and runtime capture need the project's tools and execution permission. Unknown index versions/virtual imports require an adapter review; no guessed support. A generic approved Markdown catalogue remains valid.

## 4. New report inputs

The same report shell is retained. New approval-ready application screen flows require `approved-kit`, real PNG captures, `kit_binding`, per-screen `elements` including the composition pattern, and `capture_context` with source/image fingerprints and existing evidence references. UI-FLOW.md documents the data fields. A non-JSON catalogue can be projected in the same report input; do not create an independent inventory.

Legacy draft/schematic support is read-only/historical compatibility, not permission to create new app mockups. Previously presented HTML is not regenerated or renamed. Existing tests/reports remain historical; new kit input validation does not retroactively prove their sources. Do not refresh capture input hashes without actual evidence/recapture.

## 5. Local acceptance

Use disposable fixtures first: missing DESIGN.md/source; existing selected kit; removed component; stale capture; ordinary request without /workflow; subagent; resume; old functionality-only record; proposed CSS/inline-style/plain-HTML bypass. Check actual reads and diffs, not statements of compliance. The first real pilot should use a small existing component reuse task. No live project or host tests were run for you here.

No host-level blocker is installed. The read-only diff helper, catalogue checks and renderer validations complement instructions; they do not prevent every tool action. See VALIDATION.md for observed results and limits.
