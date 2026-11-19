# Report files

Read this when you put qualified ticket IDs into a report's JSON, or after the owner accepts a replacement for a presented review or delivery report. [TASK-FOLDER.md](TASK-FOLDER.md) and [VISUAL-REVIEW.md](VISUAL-REVIEW.md) send you here.

## Renderer ID aliases

The HTML renderer uses safe local IDs without `/`. Keep a qualified source ID such as `D4/T8` in the report task title; use a unique projection alias such as `D4-T8` in JSON references. This does not rename the source ticket. See codebase-map REPORT.md; check aliases for collisions rather than blindly replacing punctuation.

## Superseded review cleanup

This is the one retention rule for presented review and delivery reports. Keep one filename while a draft is unpresented; use the renderer's guarded replacement instead of making retry copies.

After the owner accepts a replacement, inspect the exact older HTML/JSON files and associated captures in this task. Ask once, separately from plan approval: "Delete these superseded files, or retain them?" Name the exact files, leaving out the protected ones below, and recommend deleting only demonstrably redundant ones. Record the answer in the task record; a recorded retain or delete choice stands, so do not ask again. Silence retains. A plan approval is not deletion approval.

Retain, with its concrete reason in the task record, any file that an active approval or `write_paths` depends on, or a legacy approval's fingerprint; recovery, rollback or comparison evidence; anything under explicit retention; and anything another session or checkout still uses. Such a file stays even when the owner chose deletion; say which and why. Label retained older revisions superseded in the record, with the replacement link; their bytes stay unchanged.

Before an owner-authorized removal, reconcile the real approval authority: a replacement holds approval only through its own recorded approval, and relinking or a saved hash never transfers approval to changed bytes. Preserve the decision, mark each retired file unavailable in the record and update current links. Then remove only the exact selected files. Reuse the existing task record; no automatic deletion or archiving, history rewrite, bulk cleanup, change to another checkout or cleanup report.
