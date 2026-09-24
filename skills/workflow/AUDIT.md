# Audit

Audit only what this task changed. Pre-existing code is out of scope unless the user asks. Give every check a verdict.

1. Other places that use the changed functionality and were not updated.
2. The same functionality reached another way — a second call path, an alternative helper, a duplicate implementation.
3. Edge cases and dependencies the change did not account for.
4. Best practice for the frameworks actually in use.
5. Whether the code is clear, efficient, and maintainable.
6. Complexity or duplication the change introduced.
7. Docs that no longer match the code — architecture, flows, diagrams, `CONTEXT.md`, ADRs, READMEs — edited or not. And whether the diff delivers the goal in `PLAN.md`.
