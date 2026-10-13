# Offline report contract

Python 3.10+ and the standard library are sufficient. Copy this **complete skill directory** including assets/scripts/examples for standalone installation. No Miro account, Mermaid, CDN, server, npm package or renderer installation is required. This is a local pan/zoom viewer, not an editable collaborative whiteboard; edit the JSON source and render a new revision to change the diagram.

## Run

From the plugin root, preview the synthetic example using a **new** output filename:

```powershell
python -X utf8 skills/codebase-map/scripts/render_report.py --root skills/codebase-map/examples --input skills/codebase-map/examples/review.json --output skills/codebase-map/examples/local-preview.html --open
python -X utf8 skills/codebase-map/scripts/render_report.py --root skills/codebase-map/examples --check skills/codebase-map/examples/local-preview.html
```

For real work substitute the actual repository root, task JSON and a new revisioned HTML path. Paths with spaces must be quoted. The input must be within the source root; source references use root-relative forward-slash paths. Output parents must already exist and be authorized. Output must use .html/.htm. Existing output files are never overwritten. The CLI uses your current directory for command arguments; JSON source paths resolve against `--root`.

Exit 0: render/check completed; 1: supplied sources changed/missing in freshness check; 2: invalid input or filesystem error. `--open` makes a browser launch request, not proof of display; failure does not discard the report or approve work. Normal page scroll stays normal; toolbar, focused-map keys (+/−/arrows/F), drag, or Ctrl/Command-wheel control the map.

## Projection schema (version 1)

[examples/review.json](examples/review.json) is the full executable example. Its code and task documents are synthetic fixtures, not claims about a user's repository. Fields:

| Field | Contract |
|---|---|
| `schema_version`, `title`, `revision` | Version 1; plain strings identifying the reviewed task/revision. |
| `mode` / `state` | `current`, `proposed`, `compare`; and `inspection`, `draft`, `awaiting-approval`, `approved`, `superseded`. Current-only uses inspection. |
| `snapshot` | Repository label, optional branch/worktree description, and precise inspection basis/limits. Script adds generation time and supplied-file hashes. Do not claim a clean HEAD snapshot for uncommitted content. |
| `understanding`, `boundaries`, `open_decisions` | Plain-language requested outcome, exclusions, unresolved material decisions. No approval-ready state with open decisions. |
| `sources` | Objects with `id`, root-relative existing `path`, and `role` (e.g. plan/todo/findings/code). Approval-ready compare needs plan/todo/findings sources. No source contents are automatically copied into HTML. |
| `requirements` | `id`, `text`, `origin`: real user request/answer or approved policy reference, not invented intent. |
| `evidence` | `id`, `claim`, `kind` (static/runtime/design), source IDs, `locator` (symbol/lines or test evidence) and `limits`. A design record alone cannot support an observed code relationship. |
| `acceptance` | `id`, observable `text`, requirement IDs and concrete `verification`. |
| `tasks` | `id`, `title`, `kind` (requested/prerequisite), evidence-backed `reason`, affected `areas`, requirement/evidence/acceptance IDs, dependency task IDs. All tasks trace to requirements; prerequisites explain why required. |
| `graphs` | One graph per mode, or current + proposed for compare. Each has kind/title/nodes/edges. |
| Node | `id`, short `label`, short `note`, `group`, integer `col`/`row` (0–8), `basis`, `change`, evidence IDs and task IDs. One group per row, no overlapping cells, max 16 nodes per view. |
| Edge | `from`, `to`, short `label`, `basis`, `change`, evidence IDs and task IDs. Keep routed edges uncluttered; label branch outcomes. |
| Basis / change | Basis: observed/inferred/unknown/proposed; change: unchanged/added/modified/removed. Current graph contains unchanged existing behavior only. Unknowns require `uncertainty`; observed/inferred require code/test evidence. Added/modified future behavior is proposed and maps to tasks. |
| `approval` (approved state only) | Matching revision, real record reference and actual response. The renderer checks structure, not provenance. The authoritative approval remains in PLAN/DECISIONS. |

IDs use letters/digits/underscore/hyphen, start with a letter and are unique per collection. Labels are escaped text, never HTML. Shorten overly long node labels/notes or move detail to evidence. Each current relationship, including edges, needs evidence or an explicit uncertainty; diagrams are not an excuse to invent certainty.

## Source of truth and freshness

Create/update PLAN/TODO/FINDINGS/DECISIONS first, then derive this projection. The JSON is editable diagram source, not a second authoritative specification. Check IDs and meaning against the records before presenting. The renderer verifies that the projection being rendered matches its saved input JSON. Snapshot hashes include that JSON and all supplied source bytes, including uncommitted changes. New/omitted files, incomplete evidence, fabricated claims or an externally edited manifest are not automatically detected. Treat a successful check as byte agreement only.

`--check` is read-only. Source drift requires inspection. An expected checkpoint or implementation update can change a hash without revoking approval; a changed requirement or approach may need a new review. Preserve the HTML shown for each approval and do not regenerate/overwrite history silently.

The report embeds local CSS/SVG and a fixed pan/zoom script with a script-hash content policy. No remote requests, arbitrary URLs, dynamic label HTML, approval callbacks or external fonts. It reads only named existing sources beneath the supplied root, rejects symlink escapes/traversal and limits individual inputs to 8 MiB. It cannot determine whether a permitted source contains secrets: sanitize input/evidence and do not include raw private data. Rendering adds only the explicitly requested HTML.
