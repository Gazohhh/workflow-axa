# Project routing block — merge during approved setup only

This file is a template, not automatically loaded project policy. Merge the following small block into the host's applicable existing instructions once; preserve other rules. Resolve actual skill names from the host, not a guessed alias. For the Claude plugin they are normally `workflow-axa:workflow` and `workflow-axa:codebase-map`; standalone skill names are `workflow` and `codebase-map`. Do not paste duplicate blocks into nested instruction files.

```markdown
## Repository workflow
Before substantive planning or changes, load the installed workflow RULES.md and its local rule-maker shared references. Check project-rule adequacy even if rule-maker never ran. Missing coverage: stop and ask for minimal setup, a specific one-task exception, read-only work or stop; unknown safety/authority conflicts are not waived. Existing adequate rules need no migration. Setup approval is not application approval. Revalidate on relevant changes, resumption and delegation.
For repository feature requests, fixes, refactors and task resumption, load the installed workflow skill before proposing or implementing changes, even when the user did not name it. Verify the relevant current code and local edits; prior chat or a plan is not current evidence. Map requested requirements to code evidence, the actual gap, tasks and acceptance. Do not add unrequested features or silently choose user-owned decisions.
Before creating task records, inspect current/named/related plans. Continue a clear existing task through revisions; ask about an ambiguous match or ownership. A new invocation is not a new folder. For every new substantive goal or material scope change, invoke the installed grilling specialist to uncover missing decisions, reuse sourced answers, and block dependent work on unanswered choices. Do not restart unchanged approved interviews.
Write for a reader new to the project: concrete behavior and consequences first, exact technical evidence underneath.
Before tests/builds/device checks, read the installed workflow ARTIFACTS.md/global policy. Reuse the task output parent, keep needed evidence and clean only eligible own scratch; protect project/tool-owned/live outputs. Do not create additional reports or silently change retention scripts.
For substantive implementation, prepare PLAN/TODO and a current/proposed HTML flowchart review using the installed local codebase-map skill and its bundled flowchart guide, show the understood behavior and scope, open/provide the report, and STOP for explicit approval before application changes. Reuse settled answers and valid existing approval; follow the documented lightweight and explicitly waived cases.
Repository-specific explanations require relevant inspection but no writes. Explicit visualization-only requests use codebase-map and authorize only their report artifacts, never application changes. General questions do not launch repository work.
If a required skill is unavailable or cannot be loaded, disclose it; use only an already approved fallback or ask for setup/fallback. Never claim it ran. Respect no-file requests, preserve user changes, and perform no unapproved installs, staging, commits, pushes or deployment.
```

Codex uses applicable `AGENTS.md`/overrides; Claude Code uses applicable `CLAUDE.md`/project rules. Do not assume Claude automatically loads a file merely because Codex uses it. One shared policy with deliberate host-supported references is valid when verified. Record actual file location, scope and runtime discovery in setup evidence. [Codex project instructions](https://developers.openai.com/codex/guides/agents-md/) · [Claude memory/project instructions](https://code.claude.com/docs/en/memory)

Test in a fresh session: an ordinary feature request must load workflow and inspect code before proposals; a diagram-only request must load codebase-map without implementation; a general conceptual question must not create task files. Inventory presence and this template passing file checks do not prove any of those behaviors.

## Optional record-history clarification — reviewed merge only

During this upgrade, merge the following into the authoritative task/review policy rather than adding a contradictory second rule. Project-specific preservation, approval and publishing rules still apply.

```markdown
Keep one concise current checkpoint in the task's established record, separating approval, implementation and verification/owner acceptance. Label earlier baselines and proposals as history. Record meaningful scope revisions and their reasons in the existing PLAN/DECISIONS; progress, test retries and agent handoffs do not create plan revisions. Preserve paths, IDs, heading links and presented/approved HTML/JSON snapshots; later approval is recorded in the task record, not by rewriting old reviews. Apply the structure to new work and minimally to tasks actually resumed; do not migrate closed tasks or create extra state/revision files. Resolve conflicting local retention instructions explicitly; never delete history automatically.
```

## Application UI (merge, do not duplicate shared standards)

For application UI, load the installed shared design.md and local ui-design before dependent planning/edits, even without `/workflow`. Default to functionality-only unless scoped approval establishes kit/design authority. Preserve existing presentation; do not infer approved designs from arbitrary classes or folders. Record preview and pending design/release state in the existing task. Backend work needs no kit; normal workflow reports keep their approved local renderer. Resolve conflicts with existing project rules instead of overwriting them.
