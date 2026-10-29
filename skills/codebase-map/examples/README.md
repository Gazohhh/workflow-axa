# Synthetic report example

`review.json` and `review.html` show the 2.2 flowchart-first renderer using the small bundled scoreboard fixture. No actual application change is approved or implemented. The example contains current behavior, the proposed branching feature flow, and a separate delivery-dependency view. A settings tree is not added when the request does not need it.

The styling follows the owner-approved second diagram-design sample; this fixture does not claim a live specialist invocation. Source documents and code are illustrative. Render commands and schema migration are in [REPORT.md](../REPORT.md). Use a new output path, not the bundled review.html. Runtime/generated hashes identify only the supplied fixture bytes.

## Current state without rewriting a saved review

`task-overview.json` uses the same flow geometry and baseline sources as `review.json`. Its additional STATUS.md is a synthetic legacy record with later fixture approval, separate implementation/verification, and an inline revision log. This is an example only; the workflow does not add STATUS.md to new real tasks just for a report. The original review.html intentionally remains a prior presentation snapshot, including its original pending state and renderer version.

Render the overview from this directory using the same renderer, with a new output path. It has no approval action. Do not refresh it on every task update; ordinary status belongs in existing records and chat.
