# Upgrade to workflow-axa 2.7.0-rc.7

Full replacement of rc.6, with the owner's stricter **no agent-authored application HTML/CSS/inline styles** policy. No additional external skill or UI framework is required. Review the new restrictions before resuming an old UI plan.

## 1. Replace the actual active package

Update the complete plugin, or all eight sibling skill folders: workflow, codebase-map, task-status, resume-task, workflow-doctor, plan-review, rule-maker, ui-design. Keep the stable canonical installation path. Do not merge a few files and leave stale instructions. Review local modifications first and retain a safe previous copy under the existing installation process; do not delete unrelated skills. Matt's 27 catalogue entries are unchanged.

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
