# Project routing block — merge during approved setup only

This file is a template, not automatically loaded project policy. Merge the following small block into the host's applicable existing instructions once; preserve other rules. Resolve actual skill names from the host, not a guessed alias. For the Claude plugin they are normally `workflow-axa:workflow` and `workflow-axa:codebase-map`; standalone skill names are `workflow` and `codebase-map`. Do not paste duplicate blocks into nested instruction files.

```markdown
## Repository workflow
For repository feature requests, fixes, refactors and task resumption, load the installed workflow skill before proposing or implementing changes, even when the user did not name it. Verify the relevant current code and local edits; prior chat or a plan is not current evidence. Map requested requirements to code evidence, the actual gap, tasks and acceptance. Do not add unrequested features or silently choose user-owned decisions.
For substantive implementation, prepare PLAN/TODO and a current/proposed HTML flowchart review using the installed codebase-map skill and its diagram-design route, show the understood behavior and scope, open/provide the report, and STOP for explicit approval before application changes. Reuse settled answers and valid existing approval; follow the documented lightweight and explicitly waived cases.
Repository-specific explanations require relevant inspection but no writes. Explicit visualization-only requests use codebase-map and authorize only their report artifacts, never application changes. General questions do not launch repository work.
If a required skill is unavailable or cannot be loaded, disclose it; use only an already approved fallback or ask for setup/fallback. Never claim it ran. Respect no-file requests, preserve user changes, and perform no unapproved installs, staging, commits, pushes or deployment.
```

Codex uses applicable `AGENTS.md`/overrides; Claude Code uses applicable `CLAUDE.md`/project rules. Do not assume Claude automatically loads a file merely because Codex uses it. One shared policy with deliberate host-supported references is valid when verified. Record actual file location, scope and runtime discovery in setup evidence. [Codex project instructions](https://developers.openai.com/codex/guides/agents-md/) · [Claude memory/project instructions](https://code.claude.com/docs/en/memory)

Test in a fresh session: an ordinary feature request must load workflow and inspect code before proposals; a diagram-only request must load codebase-map without implementation; a general conceptual question must not create task files. Inventory presence and this template passing file checks do not prove any of those behaviors.
