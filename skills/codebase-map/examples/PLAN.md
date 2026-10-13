# Synthetic example — reject negative scores

Revision P1. Awaiting user approval. No implementation has started.

Example request: Reject negative home or away scores in both display paths. Keep all nonnegative formatting unchanged. Do not introduce dependencies, features or configuration.
R1: Reject negatives in web and player paths. R2: Preserve nonnegative output.
A1: Negative home/away values each raise ValueError through shared/web/player entrypoints.
A2: Zero/positive values retain the existing `home - away` output in both paths.
Current evidence E1/E2/E3 is in FINDINGS. Shared formatter is the existing owner; the player bypasses it. Proposed: add validation there, route both paths through it, remove directly superseded helper, verify both behaviors and update the existing README usage note.
Boundaries: no UI redesign, score history, bulk operations, new packages or Git actions.
Approval: pending. This is illustrative fixture content, not an actual user's approval.
