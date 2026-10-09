# Decisions

## D1 — Explicit specialist routing (approved)
Use the applicable model-invocable specialist, not “consider using it”. The workflow owns
approval, task records, question timing, bounded work and final evidence. `grilling` is
the reusable entrypoint behind the user-only `grill-me` wrapper.

## D2 — One collection installation per host (approved)
Verify the complete collection at setup, and only relevant routes during a task. Missing,
disabled, duplicate or changed skills are disclosed. No silent installs/upgrades. A normal
workflow task does not become a mandatory setup exercise for unused specialist skills.

## D3 — No vendored upstream stack (implementation of approved direction)
Keep the upstream collection separate. Record observed source/version and fingerprint a
team's actual local installation. A version label is not a verified content hash. Source
commit could not be established from the accessible web response, so no invented pin.

## D4 — Explicit adaptations and exceptions (approved)
Reuse settled approval and task docs, review uncommitted work, prohibit automatic commits
and publication, and run sequentially when subagents are unavailable. Other missing-skill
fallbacks require recorded approval; no false claim that a specialist executed.
