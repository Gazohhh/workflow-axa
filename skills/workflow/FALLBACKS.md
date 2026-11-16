# Fallbacks

When something a recipe needs is missing, don't stop silently and don't pretend. Use the named fallback, say it once, and keep going.

**Say it once:** "Fallback: **<name>**: I'll do X instead; Y stays unverified."
**Record it:** where task records exist, one FINDINGS line `Fallback: <name> — <substitute>; <evidence>; <remaining limitation>`, updated when the gap closes. Without task records it stays in chat. Delivery lists only the gaps that remain, keeping enforcement limits apart from missing verification.

| Missing | Fallback | What happens instead | Blocks? |
|---|---|---|---|
| A runtime reproduction | Static diagnosis | code and log analysis plus the experiments that would confirm it; never claims a reproduction | no |
| A test framework | Direct check | an assertion script, a CLI probe or a scripted manual check; nothing installed | no |
| Figma or design access | Existing-reference design | approved existing components; ask for an export; non-visual tickets continue | no |
| A preview, device or browser | Visual verification pending | build and run the other checks | only the "done" claim, when the visual check is required acceptance; otherwise listed as a gap |
| A reachable integration | Reduced evidence | a stub or contract test; the live check stays pending | only the "done" claim, when the live check is required acceptance; otherwise listed as a gap |
| Hooks (Codex) | Instruction-only enforcement | the same steps followed by instruction, and said so | no |
| A second model (T3) | Single-provider review | a fresh same-model reviewer, else a labelled self-review; a model the owner asked for is never swapped silently | no |
| A working checker or tool | Manual contract check | rerun it once on its own, then inspect its inputs by hand; report what automation couldn't establish | no |
| A clear outcome | Inspect-first | read-only discovery, then the open question through `grilling` | no |
| Access to a dependency (architecture) | Conditional design | the design states its assumptions | no |
| The target hardware | Measurement-limited analysis | numbers labelled with the environment they came from | no |
| Live access (migration) | Offline rehearsal | rehearse on a copy | no |
| A working approval checker | Fail closed + diagnosis | writes pause; a read-only diagnosis names the failed check; an approval that still validates is never asked again | blocks writes |

## What may pause work

Only these, and only the work that depends on them; everything else continues with a fallback:

1. a rules readiness question the owner hasn't answered yet (only writes wait; read-only work continues);
2. missing or conflicting authority for the work;
3. an open owner decision that changes behaviour;
4. unknown safety, identity or data boundaries;
5. a protected operation (install, commit, push, deploy, delete, production) without its own permission;
6. a required acceptance that can't honestly be met, which stops only the "done" claim.
