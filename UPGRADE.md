# Upgrade to 2.6.0

Built from the supplied workflow-axa(1).zip, whose plugin version is 2.5.0. This is a forward-only record/review improvement, not an application refactor or historical-document migration.

## 1. Update the complete package-owned skills

For a plugin, update the root containing .claude-plugin/plugin.json and the six complete skill folders. For standalone installations, update all six complete folders under the host's active skills directory. Preserve your .git directory, unrelated files and local changes; avoid duplicate active copies. Matt's collection is unchanged and needs no new dependency installation. The supplied stale DIAGRAM-DESIGN.md is now a short compatibility pointer to the local guide; keep it when an old reference uses that path.

No archive has been installed on your computer by creating this release. The release deliberately excludes .git and interpreter caches; it does not delete your repository history.

## 2. Resolve the small project-policy difference, once

Merge the record-history clarification from [PROJECT-ROUTING.md](skills/workflow/templates/PROJECT-ROUTING.md) into the authoritative existing instructions, preserving unrelated rules. Do not add a second contradictory policy. In the supplied project's earlier AGENTS/ADR convention, older review pages required asking whether to keep/delete; explicitly agree the new preservation default before changing that project policy. Do not silently override it globally.

Recommended wording:

> Keep one current checkpoint, separating approval, implementation and verification/owner acceptance. Keep revision changes and reasons in existing records; progress, test reruns and handoffs do not make another plan revision. Preserve presented/approved review snapshots, existing paths, identifiers and heading links. Apply the structure to new tasks and only the task actually being resumed. No bulk migration or automatic deletion.

This release does not edit the user's plans.zip, adr.zip, AGENTS.md, CLAUDE.md or CONTEXT.md. Read-only status/review commands must not change those files. During an authorised task continuation, reconcile only that task's current summary and directly affected pointers. Keep unknown/conflicting authority explicit until resolved.

## 3. Existing history and report formats

- Completed tasks not being reopened stay unchanged. Legacy STATUS.md and inline decisions are supported; do not create missing template files.
- Keep old C3/P1-r1/review-r5 names exactly. Record proven mappings in the existing revision log, not a renaming script.
- PLAN's checkpoint is the new-task current summary; an established legacy STATUS.md may remain the owner. TODO owns work items; FINDINGS owns detailed evidence. No new CURRENT.md, REVISION-TRACKER.md, HANDOFF.md or duplicated whole-folder snapshots.
- Presented/approved HTML and JSON retain their original bytes. A pending badge in an earlier review is not proof that approval is still missing. Read the actual task approval record.
- Existing schema-2 inputs render without change. Optional checkpoint/revision fields are additive; schema-1 HTML remains checkable. Regenerating schema-1 layouts still uses the existing explicit migration procedure, never an automatic conversion.
- A requested overview is an as-of snapshot, not a live task database and not another approval gate. Do not generate it for every status update. The renderer still refuses overwriting existing output.
- New tasks default to reviews/ only when the project has no other convention. Existing review paths stay where they are.

## 4. Global artifact setup does not need reinstalling

ARTIFACTS.md and global_policy.py are byte-identical to the uploaded 2.5.0 versions. Their policy/deployment version stays 2.5.0 independently of the 2.6.0 package. Existing global activation remains valid. Read-only verification, from the package root:

```bash
python -X utf8 skills/workflow/scripts/global_policy.py --check
```

A new machine/profile still needs the reviewed preview/apply setup in [SETUP.md](skills/workflow/SETUP.md). Do not copy project-specific instruction files into global locations.

## 5. Pilot in a fresh agent session

Run workflow-doctor, then use task-status on a copied older task: verify no writes and separate approval/implementation/acceptance. Test a legacy STATUS.md resume, a later approved revision whose old HTML is pending, a removed item that must not be called passed, and a new unapproved phase whose review number is higher. Test one ordinary progress/rerun: no new task, plan revision or review should appear.

[Behavioral cases](tests/behavioral/README.md) provide synthetic fixtures. Their input/renderer tests do not prove model behavior. Native Windows, host permissions, and actual Claude/Codex runs must be checked in your installation. See [VALIDATION.md](VALIDATION.md) for observed results and limits.
