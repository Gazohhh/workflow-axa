# Team setup and actual enforcement

Setup needs explicit permission. Ordinary tasks do not install, update or replace skills. The registered list in `.claude-plugin/plugin.json` is authoritative; copy complete folders from one version, not selected SKILL.md files.

## 1. Select the actual runtime copy

Choose one installation route per host. The Claude plugin includes `hooks/hooks.json`; a standalone skills copy does not install those hooks. Codex uses the shared instructions and skills but this package ships no equivalent Codex hook enforcement. Do not claim identical protection.

For a candidate, prefer an isolated source copy and a temporary Claude `--plugin-dir` session after checking the installed CLI's help. Keep the current installation as baseline. Do not install the candidate globally merely to test it. A full source bundle includes tests/tools; the smaller installable ZIP does not. Use the source bundle for this validation, then install only after the pilot is accepted.

Bundled specialists are pinned in the package. Do not additionally install duplicate copies of grilling, tdd, code-review or the other bundled names. `SPECIALISTS.md` owns the routes; `specialists.json` lists optional external providers. A missing optional dependency blocks only its dependent work. Do not fetch it automatically.

## 2. Activate shared instructions once, with approval

From the final stable package location, preview the rule-maker's `scripts/activate_rules.py` and this skill's `scripts/global_policy.py`. Each supports `--apply` and `--check`; inspect help before using custom profile paths. Preserve unrelated global instructions and the existing artifact policy. Do not put project-specific AGENTS.md in a global home.

The rule activation references the central START/CORE library, not copied framework rulebooks. The artifact helper maintains one shared output policy. Neither grants tool access, configures a remote updater or changes application files. Claude imports and Codex read instructions differ: validate actual loading in the host, including global overrides. Apply setup separately in each real machine/profile environment.

Merge the small [project routing block](templates/PROJECT-ROUTING.md) into existing instructions only when authorised; preserve local constraints. Shared readiness is owned by rule-maker's READINESS.md, not a marker claiming setup ran. The local `ui-design` and `codebase-map` must be siblings from the same package. No external diagram-design dependency or automatic preview app is required.

## 3. Check installation, then behavior

Use `workflow-doctor` and rule-maker's read-only `scripts/audit_installation.py --check-global`; supply known candidate roots to compare duplicate installations. Use `scripts/check_specialists.py --help` for optional external specialists. Check files, paths, fingerprints and actual invocation separately. Missing `python`, an unsupported hook host or a stale installation is a reported limit, not a claimed pass.

A fresh ordinary task without a slash command must load the shared core and applicable modules. Also test missing project rules, a resumed task, a backend-only task and a UI task without styling authority. Inspect tool traces and results, not only the agent's claim that rules loaded. Keep the same host/model/effort and fixtures for comparisons.

## 4. What the hooks enforce

### Updating sessions safely

Keep each running session's plugin directory immutable. Stage a complete candidate at a separate stable location, validate it, then switch the chosen plugin source only after approval and restart the affected host. Do not update scripts underneath cached hook registrations. Inspect enabled directory plugins and marketplace cache registrations; an old cache directory alone does not prove it is loaded. Preserve unknown caches and unrelated settings.

The phase-gate registrations pass `--hook-protocol=1`. Missing or unknown protocol on a gated write produces a compatibility denial and restart guidance. Record/read-only access stays available. This token checks the registration/script contract, not package authenticity; compare the actual roots, versions and bytes as well. Scripts predating this check cannot enforce it retroactively. A fresh host must load one complete version and demonstrate both fingerprint events before a resumed approval is accepted.

Missing report fingerprints are an evidence/registration problem, not proof that the owner refused. Inspect PostToolUse and UserPromptSubmit registrations before asking again. Preserve the original answer; after recovery, present the unchanged report in its actual workspace and record the genuine reconfirmation. Never synthesize fingerprints or copy another worktree's approval. A stale, edited, forged or wrong-workspace report stays blocked.

If assistant text is unavailable in a host transcript, use a report-linked AskUserQuestion and its matching successful host answer. The tool call alone, thinking content, a cancelled question or an unrelated answer grants nothing. Do not inject Stop additionalContext to record presentation: that feedback itself continues the turn. See the [host hook contract](https://code.claude.com/docs/en/hooks).

The Claude phase gate activates after the router or a phase is typed, invoked or read whole. It checks recognised writes in the active project/worktree. It needs the current task's checkpoint, its report and an approval quote matched to the whole real user answer after that named report was presented in assistant text. Loading a phase or writing the report is not presentation. Short exact answers count; prefix quotes that omit conditions do not. A `no report` exception must be in the verified quoted answer, not added by the agent outside it. An unchanged historical approval can be recovered from sibling session transcripts.

| Boundary | Actual implementation and limits |
|---|---|
| Report identity | The gate leaves SHA-256 fingerprints in the transcript as host-recorded hook context: after a tool call that reads, writes or renders a task report by its `docs/plans/` path, and with each owner answer (typed message or AskUserQuestion answer). Approval needs the same bytes before the presentation, at the answer and at the edit or resumed session; timestamps play no part. No fingerprint (an older approval, another machine or account, a host transcript removed, a report produced without a recognised tool call) means focused reconfirmation, never inferred approval. |
| Write paths | A report rendered with `write_paths` bounds file writes after approval to those files and folders; task records and `.artifacts/` stay writable. Reports without `write_paths` keep approval-only behaviour. Git writes, MCP writes without a file path and shell code whose target the gate cannot resolve are not path-checked. Approval wording is not parsed: a condition that changes the files needs a new revision. |
| Recognised edits | Edit/Write/MultiEdit/NotebookEdit and selected MCP names are checked after activation. No transcript path leaves this guard unavailable. A supplied nonexistent or unreadable transcript blocks direct canonical record edits. For other edits, the existing missing-transcript limit remains; an unreadable transcript blocks explicit edit tools and recognised Git writes. Readable inactive sessions keep their existing behavior. |
| Planning | In active workflow sessions, direct Write/Edit/MultiEdit calls to `docs/plans/<task>/PLAN.md`, `TODO.md`, `FINDINGS.md` and `DECISIONS.md` are refused, including initial creation and sibling worktrees. Use the existing `record.py` helper. It remains available before approval and after stop for handoff, subject to normal tool permissions. `new` requires an existing parent directory and a permitted input source; prepare those through normal permissions. Do not bypass a denied helper command. Other task files and `.artifacts/` retain their existing exemptions. This is not a filesystem sandbox or a guard against arbitrary shell writes. |
| Rules setup | Loading rule-maker currently exempts project rule files (recorded prior D20). Scope and setup permission still require model/host controls. |
| Lightweight | The recorded file list permits those paths only and never Git writes. The hook cannot determine whether the change really has no observable behavior. |
| Stops | Recognised direct stop/pause/cancel requests block further recognised nonrecord writes until an explicit continuation. Other natural-language forms and already-running work require the instructions/host. |
| Shell/MCP | Common shell writes, Git changes and named MCP writes are recognised heuristically. Arbitrary scripts, aliases, indirect targets and unnamed external side effects can escape detection or cause false blocks. |
| Installs | Recognised package downloads need installation permission in the latest real user words. Existing local tools can run. This is not a complete registry/network firewall. |
| Scope/consent | The guard checks recorded evidence provenance, not full natural-language meaning, exact per-ticket write scope, cryptographic consent, or separate publication authority. An approval match does not override project Git restrictions. |
| Report guides | Workflow specify/deliver report validation (`--validate-input`) and rendering require the full `codebase-map/FLOWCHART-DESIGN.md` alongside the existing guides. Successful complete reads before phase loading count in the current context. Failed or truncated reads do not count; compaction requires a fresh read. Legacy ID-less evidence remains best effort. Standalone/inactive sessions and missing transcripts retain their existing limits. This does not prove comprehension. |
| Project reads | Optional `<!-- workflow-axa:required-read phases=specify,execute,deliver path="tests/README.md" -->` lines in the project root `AGENTS.md` or `CLAUDE.md` name files to read whole first. A declaration starts its own line; fenced blocks at any indentation, inline code and lines indented four or more spaces are examples. Each declared path must be an existing regular file. The union of both files counts. A Skill call that enters workflow-specify, workflow-execute or workflow-deliver (qualified names too), and report validation or rendering while a declared phase is loaded, waits until each file has a successful complete read with its own result in the current context, matched by exact absolute path in that project root. Failed, partial, truncated, subagent, unanswered or pre-compaction reads do not count. A malformed declaration, an unreadable root rule file or a supplied unreadable transcript blocks the same boundary. No transcript path leaves this guard unavailable. A phase the user types as a slash command (for example `/workflow-execute`) runs no PreToolUse hook, so declarations are checked only at the next phase Skill call or report operation. Undeclared projects keep their existing behavior. Reading files, skills and rules and `record.py` stay available. Shell verification, other scoped rules and imports are not checked. This does not prove comprehension and adds no permission to edit rules. |
| Reading/review | Phase reminders and Stop checks help spot missed relevant reads and missing review signals. They do not prove that the agent understood a file or that a requested review completed successfully. |
| Other hosts | This package's Claude hooks do not protect Codex, unhooked sessions or external filesystem edits. Host permissions remain necessary. |

The current-task heuristic (last task written/named), selected-dialog-answer support and legacy revision handling were agent-made D7–D10 choices in the supplied task. They remain pending owner acceptance. Do not retroactively mark them accepted because this candidate exists.

The guard caches transcript state under the system temp folder and prunes unused cache entries after 14 days. Cache content is an optimisation, not an authority source. The hook still reads the transcript file to verify the cache. Missing/forged host records and semantic ambiguity are not solved by hashes.

## 5. Optional updates and release

Review provider revisions and compatibility before updating dependencies. Do not edit managed plugin caches, silently change invocation policy or replace existing project design decisions. Keep the source of a provider and its reviewed contents together; no assumption that an upstream main branch is immutable.

Use UPGRADE.md in the package root for historical installation changes. Do not reread install history during routine tasks. The candidate test handoff records the allowed budget and stopping condition. A retro can recommend no change; it must not mutate global policy after every run.

Official references: [Claude hooks](https://code.claude.com/docs/en/hooks), [Claude instructions](https://code.claude.com/docs/en/memory), [Codex project instructions](https://developers.openai.com/codex/guides/agents-md). These document host mechanisms, not proof that this candidate behaves correctly on a specific installation.
