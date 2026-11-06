# Upgrade to workflow-axa 2.8.0-rc.12

## Safe adoption of this candidate

Review the candidate and its tests first. Keep the active directory immutable. Use one complete version in a fresh host session; inspect both directory-plugin arguments and marketplace registration. Check the selected cache's hooks and skill files rather than trusting its version label. Preserve the previous working installation and change global settings only with approval.

The new registration passes --hook-protocol=1. An old registration executing a new script blocks gated writes with restart guidance. After restart, verify PostToolUse and UserPromptSubmit fingerprints, present the report in its actual workspace, and obtain the owner's real reconfirmation. Existing source edits and historical approvals remain intact. See skills/workflow/SETUP.md for the contract and limits.

For the observed spinning session, interrupt it and run /goal clear in that session; verify the host acknowledgement. Resuming alone may restore the stale goal. This stops the external retry loop without approving work or marking deferred checks passed. Future goals must be bounded to an authorised phase and allow a legitimate user-input checkpoint.

## Test the candidate before adoption

Use the **source-and-tests ZIP** for Claude's review and local/live tests. It contains all 21 registered skills, hooks, tests, tools and retained task history. The smaller install ZIP omits development tests/history and is not a replacement for the editable repository.

The owner reported the older baseline overwritten. Do not hunt for a mandatory RAR, fabricate an old version, or require installing a candidate just to test it. Record its full SHA-256/content fingerprint, extract into an isolated test copy and confirm which package each session actually loads. No change to `D:\workflow-axa`, real project files, global settings or hooks is authorised by the testing handoff.

## What changed

### Tickets, not another tracker

New nontrivial TODOs use readable labelled blocks; small exact tasks can keep a short checkbox. See `skills/workflow/TASK-FOLDER.md` and `skills/workflow/examples/readable-todo.md`. The latter shows the format (overview table, then tickets with labelled sections) with illustrative states. The table is a summary: each ticket's `Status:` line stays the source, and `open_items.py` reports any row that disagrees.

Existing formats, IDs and presented reports stay valid. On an actual resume, reconcile only affected current records. A repeated old `T3` must be addressed with its existing revision, such as `D4/T3`; the record helper no longer chooses the first match. It can mark a labelled ticket verified only after its explicit outstanding verification/blockers are resolved. This is not proof a test ran. `set-line` still edits its first matching prefix: do not use `set-line Status:` in a multi-ticket TODO. Use an exact section/batch operation, then the qualified `tick` command where appropriate.

Qualified ticket IDs stay in source records. The existing HTML schema uses safe projection aliases (for example `D4-T8`) while the title retains `D4/T8`; REPORT.md describes the mapping. No schema migration or report redesign is required.

### Legacy approval

The old single-gate decision remains usable for its unchanged scope. An older checkpoint lacking a numeric revision may use `legacy` plus one named existing report and the full original answer after reconciliation. The hook still requires accessible genuine-answer/presentation evidence and refuses conflicting current revisions. Missing provenance or report means a focused question, not editing the hook or inventing an approval. Never alter historical snapshots or auto-migrate all records.

### Permissions

No agent-recommended plain-HTML fallback; no blanket yes as that exception. No inferred paid-batch cap. Ordinary approval of a shown settled plan still works. The paid-batch ceiling includes child sessions, orchestration and the retro; unobserved categories cannot be called included in the measured total. No billing meter or universal tool-level exception enforcement has been added.

### Windows paths

The advisory partial-read hook now compares canonical paths to its actual package root, not the folder name. Git Bash drive paths, quoted spaces and renamed marketplace caches have regression coverage. Native Windows and the live host still need validation there.

## Install only after adoption

Replace the complete plugin/runtime-owned folders together (all 21 registered skills, hooks and metadata), preserving local uncommitted changes and unrelated skills. Do not overlay the smaller archive onto an editable repository and assume stale files disappeared. Use the existing read-only installation checker to identify unexpected files; deletion needs review.

The global activation helpers and stable references are unchanged. If the source path is unchanged, the references can remain; verify effective profiles and real resolution in a fresh session:

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
python -X utf8 skills/workflow/scripts/global_policy.py --check
```

No `--apply` is authorised by a test-only instruction. Standalone skill copies do not automatically install Claude hooks; Claude results do not establish Codex/T3 parity.

## Testing handoff

Read `CLAUDE-TEST-PROMPT.txt` and `RC3-CASES.md`. Safe local tests first; obtain an explicit full-batch cap before any live batch. No assumed $40, no automatic retries, one read-only retro after the authorised batch, then report and wait. A recognised stop blocks new writes but is not a universal cancellation mechanism for an already-running tool. C4 is only tested when the stop actually arrives while the tool is running.

## Previous candidate instructions (2.8.0-rc.2) — historical, not current test authority

### Trial first

This is a comparison candidate for the supplied post-hardening tree, not acceptance of its delivery. The screenshot's Accept/Simplify/Release answers, D7–D10 and the proposed paid run budget remain unapproved. Preserve the original baseline; test this copy in isolation. No project, global profile or installed plugin has been changed here.

Use the **source-and-tests ZIP** for review and tests. It includes the 21 complete skills, package helpers, tests and retained task documents, but excludes Git internals, raw evaluation artifacts and caches. The separate **install ZIP** contains only registered runtime folders and user-facing documentation. Do not replace an editable repository with the smaller install archive.

The actual inventory lives in `.claude-plugin/plugin.json`; update complete owned folders together only after adoption. Review local changes and unexpected stale files; never delete unrelated skills. Keep the baseline available for rollback through your existing installation process.

### Compatibility

No application/project rules are rewritten. Matt's pinned specialist files, report rendering/assets, artifact policy, UI D14 and existing task history remain unchanged. `RULES.md` and `CHATGPT-PROMPTS.md` remain compatibility entries; the latter still contains the handoff template. Setup history is below, not a competing current procedure. `resume-task` remains unchanged (D10 is not approved on the owner's behalf).

Approval checkpoints must preserve the **whole** real answer, including conditions. Legacy prefix-only quotes may need reconciliation with the original transcript; never guess or invent replacement words. Short complete answers can count after the named report is visibly presented. A report waiver must be the user's explicit words after the task/revision plan is shown in chat. Opening a phase or writing HTML is not presentation. Repeated links to the same immutable report do not revoke approval; a newly named report needs its own answer.

Recognised direct stop/pause/cancel requests block dependent edits and suppress further forced-read rounds. Handoff records stay writable. Other language, scope changes, revocations in a separate host and arbitrary shell effects still require the workflow instructions and host permissions. Explicit resumption reuses unchanged valid authority; it does not approve changed scope.

Baselines captured before the new cwd/exact-command signature naturally report different inputs. Capture a fresh one only after the corresponding authorised checks, not to erase failures. Empty/unknown environment facts are not proof of a stable environment.

### Installation and verification after adoption

Do not globally activate a test candidate. For an adopted complete installation at its stable path, run the existing read-only checks:

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
python -X utf8 skills/workflow/scripts/global_policy.py --check
```

Verify supported arguments first if your installation differs. Missing/moved references require a reviewed setup change; no automatic apply is authorised. Plugin-only Claude hooks are not silently installed by copying standalone skill folders. Codex and T3 may use other profiles or omit these hooks. Confirm actual resolution in fresh sessions.

For source-copy checks, use `python -X utf8 -I tools/validate.py` and the unittest command in VALIDATION.md. Read CLAUDE-TEST-PROMPT.txt for bounded live comparisons. No paid runs or host-level claims have been made here.


## Historical upgrade instructions (2.8.0-rc.1 and earlier)

Retained source material, not current installation or UI authority. In conflicts use the candidate guidance above and the actual shared policy; never replay obsolete setup automatically.

### Upgrade to workflow-axa 2.8.0-rc.1

#### From 2.7.0-rc.8 to 2.8.0-rc.1

2.8.0-rc.1 splits the workflow into a router and four phase skills and adds a second approval gate. The strict UI policy and artifact policy are carried over from rc.8. The shared rules library 1.8.0 replaces 1.6.0; `skills/rule-maker/rules/CHANGES.md` lists what a project must check. Sections 2–5 below still apply.

**Replace all 21 skill folders together** (the list in `.claude-plugin/plugin.json`), as one set from the same version: the original eight (section 1), `workflow-clarify`, `workflow-specify`, `workflow-execute`, `workflow-deliver`, and the vendored `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling`, `implement-spec`, `retro` and `simple-english`. The Claude plugin registers all of them. If Matt's own copies of those vendored skills are installed in the same host, the plugin's are namespaced (`workflow-axa:<name>`) and are the ones the workflow loads. For direct installations, copy each complete folder as a sibling of `workflow`; the phase skills read its shared policies (RULES, GROUNDING, WRITING, SPECIALISTS, TASK-FOLDER, VISUAL-REVIEW, AUDIT, ARTIFACTS) and stop if that folder is missing. Do not keep an older eight-skill copy active alongside the new set. Run the section 1 checks afterwards and start fresh sessions.

What changes for people using it:

- **Two approvals for substantive work.** First the user agrees what will be built: behavior, scope, exclusions, journeys, acceptance and assumptions, written in PLAN and summarized in chat. That agreement allows the detailed plan but no code. Then the user approves the specification, tickets, test strategy and HTML report; only this second approval allows application code and tests. Gate definitions: VISUAL-REVIEW.md in the workflow folder.
- **Existing tasks keep their authority.** A task approved under the single gate before this version holds both agreement and implementation authority for its recorded scope. The next checkpoint that touches it records that classification; nobody is asked for a retroactive agreement and no old approval or presented report is rewritten. A task paused before its single approval continues at the gate its records show.
- **Lightweight edits are unchanged.** Exact, unambiguous, low-risk requests keep the short route and a short delivery check. A small behavior or architecture change is not lightweight.
- **Writing.** WRITING.md remains the policy for anything a person reads, now with a meaning-preservation table and a reader-reconstruction check. Matt's `writing-for-agents` governs skill and agent-instruction structure. Nothing new is installed.
- **Specialists.** `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling`, `implement-spec`, `retro` and `simple-english` now ship with the package as separate skills; the phases load these copies, so no Matt installation is needed for them. Only `research`, `diagnosing-bugs`, `prototype`, `pr` and `wizard` stay optional installs; a missing one blocks only the step that needs it. `workflow-execute` adapts Implement Spec's ticket graph locally and performs no branch, commit, merge or tracker action.
- **Audit hardening (same version).** After `/workflow`, the phase-gate hook allows code edits and git writes only with the current task's recorded approval or a Lightweight edit line naming the file; a task approved earlier keeps its recorded Approval line. Record edits are atomic and refuse concurrent changes. "Stop" now ends in a partial delivery. Details: CHANGELOG.md.
- **Optional central report.** Report schema 2 accepts an additive `task_report` object for a full engineering overview built from the task records (contract: codebase-map TASK-REPORT.md). Existing inputs and saved HTML need no change; reports without the object render as before. Do not hand-maintain a separate specification in the report JSON.

The project routing block template now names both gates. An existing merged block still works, because the installed `workflow` skill applies both gates, but it describes a single approval. Show the owner the updated sentence in `skills/workflow/templates/PROJECT-ROUTING.md` and merge it only with their approval, preserving unrelated rules and line endings. Review rules-readiness after installation as described in section 1; a changed package version in the shared rules manifest can require a refreshed assessment, without a new task or rewritten history.

#### From rc.7 to rc.8

rc.8 is rc.7 plus Windows verification fixes to the ui-design kit checkers and one test. Policy, rules (library 1.6.0) and routing are unchanged from rc.7. Replace all eight folders byte for byte, as described in section 1 below. Everything else in this guide applies unchanged.

#### rc.7 guidance (applies to rc.8 and 2.8.0-rc.1)

Full replacement of rc.6, with the owner's stricter **no agent-authored application HTML/CSS/inline styles** policy. No additional external skill or UI framework is required. Review the new restrictions before resuming an old UI plan.

#### 1. Replace the actual active package

Update the complete plugin, or all sibling skill folders of the version you install: for 2.8.0-rc.1 every folder listed in `.claude-plugin/plugin.json` (21 skill folders); for rc.7/rc.8 only workflow, codebase-map, task-status, resume-task, workflow-doctor, plan-review, rule-maker and ui-design. Keep the stable canonical installation path. Do not merge a few files and leave stale instructions. Review local modifications first and retain a safe previous copy under the existing installation process; do not delete unrelated skills. Matt's 27 catalogue entries are unchanged.

The global rules/artifact activation helpers are unchanged. Existing references work when they point at the same complete current library. From that installed package:

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
```

Use known `--candidate` paths when checking other installations. The helpers do not discover every cache or prove the host chose this copy. A changed rule-manifest fingerprint after installation must be investigated, not rehashed to conceal an incomplete copy. Existing artifact setup stays in place.

If the global rules reference is absent or moved, preview `activate_rules.py`, review the changes, then use `--apply` and `--check`. Never copy a project's full AGENTS.md into a global profile. Start fresh sessions in each actual T3/Claude/Codex profile and test plain prompts as well as /workflow.

A previous rules-readiness assessment references the previous shared-library fingerprint. Refresh the affected assessment against the new library before dependent work; reuse the same task, history and valid approvals. Do not manufacture a new task or rewrite historical records to pass the check.

#### 2. Reconcile project pointers, not duplicated rulebooks

Use the installed shared design.md and ui-design contract. Merge the relevant small PROJECT-ROUTING.md update into existing host-loaded project instructions where necessary; preserve unrelated rules and line endings. Surface conflicting old fallback/design-authoring language rather than silently ignoring it. Do not install a new gallery, Storybook, CSS framework or preview route.

- `functionality-only` from older tasks now means behaviour-only: preserve existing appearance, no new raw markup.
- `approved-kit` needs the task's exact valid component/pattern selection, supported variants/states and safe preview.
- `design-authoring` is historical authority, not a current bypass. Pause dependent writes and explain the changed policy. New presentation is for the designated designer/maintainer unless the owner separately changes policy.
- Existing HTML/CSS is not removed. Unaffected approved work continues. No mass migration of old task records or public screens.

#### 3. Connect a real project kit only when authorised

Run `ui-design kit-audit <area>` against designated existing component/preview sources. LIVE-KIT.md explains the code-backed catalogue: components/examples once, generated current references, human approval once, short project pointer. Installing this package does not create or synchronise a React/Angular page in your project.

The optional `inspect_kit_index.py` reads an existing local Storybook index with no writes, network or source execution. It reports missing/deleted imports and selected catalogue coverage. Actual story compilation and runtime capture need the project's tools and execution permission. Unknown index versions/virtual imports require an adapter review; no guessed support. A generic approved Markdown catalogue remains valid.

#### 4. New report inputs

The same report shell is retained. New approval-ready application screen flows require `approved-kit`, real PNG captures, `kit_binding`, per-screen `elements` including the composition pattern, and `capture_context` with source/image fingerprints and existing evidence references. UI-FLOW.md documents the data fields. A non-JSON catalogue can be projected in the same report input; do not create an independent inventory.

Legacy draft/schematic support is read-only/historical compatibility, not permission to create new app mockups. Previously presented HTML is not regenerated or renamed. Existing tests/reports remain historical; new kit input validation does not retroactively prove their sources. Do not refresh capture input hashes without actual evidence/recapture.

#### 5. Local acceptance

Use disposable fixtures first: missing DESIGN.md/source; existing selected kit; removed component; stale capture; ordinary request without /workflow; subagent; resume; old functionality-only record; proposed CSS/inline-style/plain-HTML bypass. Check actual reads and diffs, not statements of compliance. The first real pilot should use a small existing component reuse task. No live project or host tests were run for you here.

No host-level blocker is installed. The read-only diff helper, catalogue checks and renderer validations complement instructions; they do not prevent every tool action. See VALIDATION.md for observed results and limits.


### Earlier SETUP.md (historical source)

### Team setup and dependency checks

Since 2.8.0 the specialists the workflow procedure needs (`grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling`, plus `implement-spec` and `retro`) ship as this package's own skills, copied from Matt Pocock's collection (VENDORED-SKILLS.md at the package root); nothing below is required for them. Install the package as one set: a separately installed Matt copy with the same name is never what the workflow loads, and keeping both only adds a confusing duplicate to the host's list. Matt Pocock's full collection remains an optional separate install for the other routes (`research`, `diagnosing-bugs`, `prototype`, `pr`, `wizard`) and for personal use. Installing
`workflow-axa` alone does **not** install that collection. Flowchart design is local to codebase-map. Keep one collection installation route per
agent; plugin plus copied skills can create duplicate names. The catalogue records the
27 names observed on 2026-10-09, including 11 model-invocable routes. Upstream metadata
was 1.3.1; no immutable source commit or live-tested installation is asserted here.
[Upstream setup and catalogue](https://github.com/mattpocock/skills#installation-30-second-setup)

#### 1. Install once, with setup permission

Inspect the existing host inventory first. Reuse an approved working installation; do
not download a second one merely because it lives outside this project. Missing or
disabled dependencies require a setup decision, not an automatic fix during a task.

**workflow-axa itself, and where its hooks come from.** The hooks (phase gate, required reads, plain-English replies, partial-read warnings) run only when workflow-axa is installed as a Claude Code plugin, because they use `${CLAUDE_PLUGIN_ROOT}`:

```powershell
claude plugin marketplace add Gazohhh/workflow-axa
claude plugin install workflow-axa@gazohhh
```

`npx skills add Gazohhh/workflow-axa` copies only the skill folders. It installs no hooks, so nothing enforces the gates; use it for Codex, which gets skills and global instructions but no hooks. Using both routes on one machine gives two copies of every skill: run `workflow-doctor`, and keep one route per host. The Matt Pocock skills below are vendored inside workflow-axa now; the upstream commands are only for a separate install.

**What the hooks enforce.** The phase gate (`hooks/phase_gate.py`) starts once a session types or loads `/workflow` or a phase skill, or reads one of their SKILL.md files whole. From then on, a change to a project file or a git write needs the current task's approval. Loading a phase grants nothing. Task records (`docs/plans/`), test output (`.artifacts/`) and files outside the project stay writable.

The current task is the `docs/plans/<task>/` folder the session last wrote into, or the one the user named. If the session moves to another task after the user's last message, the gate stops and asks for the user's word first. The task's PLAN.md checkpoint needs an `- Approval:` line for a revision, such as `revision r1 approved by the owner: "Yes to both"`. No other checkpoint line may name a later revision. The task folder or its `reviews/` folder must hold the HTML plan report, and the very one the Approval line names when it names one. When the user chose to skip the report, the Approval line says "no report" and still quotes the user's words, which pass the quote rule below. A small change with no visible effect can use a `- Lightweight edit: <files> — <why>` line instead, and that line covers only the files it lists.

The quote rule:

- The words in double quotes are at least three words.
- They match a whole message from the user, or the whole answer the user picked in AskUserQuestion, or the start of a user message. Case and end punctuation do not matter.
- When the quoted words contain "no", "not", "don't", "niet" or "nee", they must match the whole message exactly. A refusal word later in the message, after the quoted start, does not void the quote: "Approved. Skip the checks and report them as not run" can be quoted as "Approved. Skip the checks".
- The message comes after the agent presented this task's plan: it named the task's plan report, or loaded workflow-specify or workflow-deliver for the task. An earlier session of the same project counts only when it presented this task's plan the same way.
- These never count: tool output, slash-command arguments, editor context (`<ide_...>` text), subagent reports and system notes.

The quote rule checks who wrote the words: a real user message that the host recorded. It does not check that the words mean yes. If the agent quotes the start of "Yes to both? No, wait" or an answer to a different question, the gate cannot tell. The agent must quote the user's approval of this plan, and the owner can read the Approval line.

**The install guard.** In a session where the gate is active, a package install or a download of a package to run needs the user's latest words to allow it. Those words are the last user message, AskUserQuestion answer or slash-command arguments, never tool output or notifications. They allow it when one clause (split at `.`, `,`, `;`, `!`, `?` and "but") names installing (install, `npm ci`, npx, bunx, dlx, `npm exec`) and has no "no", "not", "don't", "never", "niet" or "nee". So "install it, no need to ask" allows it, and "do not install anything" does not. The guard sees `npm i|install|ci|add`, `yarn add|install|dlx`, `pnpm add|install|i|dlx`, `composer install|require|update`, `pip install`, `pip3 install`, `python -m pip install`, `py -m pip install`, `uv pip install`, and `npx`, `bunx` or `npm exec` of a tool that is not in a `node_modules/.bin` folder at or above the working folder.

What the gate can and cannot see:

- Enforced: the edit tools (Edit, Write, MultiEdit, NotebookEdit) and MCP tools whose name contains create, write, edit, delete, apply, update, import, execute or manage. That name rule also blocks some harmless tools before approval, for example a Unity `manage_` tool that only reads, or a Trello or Docs update. When the host passes a transcript that cannot be read, the edit tools and git writes are blocked. When it passes no transcript, nothing is blocked. If the gate itself fails, the edit tools are blocked and other tools run.
- Advisory: everything the gate learns by reading command text, from the Bash tool and the PowerShell tool alike. This covers the git writes (commit, push, merge, pull, apply, restore, rm, mv, switch, cherry-pick, rebase, revert, `checkout --`, `reset --hard`, bare `stash` and `stash push|save|pop|apply|drop|clear`, `branch -D`, `worktree add`, `clean`, `git -C <folder>`, `-c alias.`) and the common file writes (`>`, `>>`, `tee`, `cp`, `mv`, `rm`, `mkdir`, `sed -i`, `Set-Content` and its relatives, inline Python or Node code). Inline code that writes only task records is allowed. When the gate cannot tell which file inline code writes, it says so and points to `record.py` for records and the Edit or Write tools for other files. Reading command text is advice, not a security boundary: a script file, an unknown variable, a configured git alias or an unusual form can write without the gate seeing it. Git forms it does not see include `checkout <branch>`, `checkout -b`, `branch -d` or `-m`, `tag`, `fetch`, `submodule`, `config`, `update-ref` and `sparse-checkout`. Install forms it does not see include bare `yarn`, `bun install`, `uv add` or `sync`, `poetry`, `cargo`, `gem`, `go install`, `dotnet add` or `restore`, system package managers, and installs run from an npm script.
- Unsupported: edits made outside Claude Code, and Codex, which has no hooks. Subagents are gated like their parent: a subagent's hook call receives the parent session's transcript (measured 2026-11-03; it also carries an `agent_id`), so the parent's task and approval apply. The agent can write the Approval line itself, because records stay writable. The quote rule is what ties approval to the user, since the host writes the user's messages into the transcript. A transcript file the agent forges in the host's folder is not detected.

The gate keeps a small state file per transcript in the system temp folder (`workflow-axa-gate`), so each call reads only the new lines. A file unused for 14 days is removed.

For **Claude Code**, the upstream documented managed installation is:

```powershell
claude plugin install mattpocock-skills@claude-plugins-official
```

Verify the installed CLI supports the command and that the marketplace is available.
Use the host's plugin UI to confirm the source and enabled installation. Managed plugin
updates can change behavior: use the host's documented update controls or a manually
maintained reviewed copy for a stable team pilot. Do not edit a managed cache to pin it.
[Claude plugin management](https://code.claude.com/docs/en/discover-plugins)

For **Codex / editable skills**, one upstream documented alternative is:

```powershell
npx skills@latest add mattpocock/skills -a codex
```

This executes a third-party installer and may download packages; run it only as approved
setup. Select the complete collection, including `setup-matt-pocock-skills`. Choose an
appropriate scope once, and do not also enable the same collection through a plugin.
For a manually reviewed checkout, copying the complete individual skill directories
into `.agents/skills/<name>` is another route; never copy only SKILL.md. Do not overwrite
existing skills with the same name. Codex supports repository-local `.agents/skills`;
verify the names through the running host, and restart if discovery is stale.
[Codex skills](https://developers.openai.com/codex/skills/)

For another host, use the upstream installation section and the host's own discovery
mechanism. Workflow adapters cannot make an unavailable tool or blocked skill executable.
No platform-specific package configuration here pretends that skill-to-skill dependencies
automatically install or authenticate themselves.

#### 2. Align repository setup once

**2.8.0 requires this package's twenty local skills: `workflow`, `codebase-map`, `task-status`, `resume-task`, `workflow-doctor`, `plan-review`, `rule-maker`, `ui-design`, `workflow-clarify`, `workflow-specify`, `workflow-execute`, `workflow-deliver` and the vendored `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling`, `implement-spec` and `retro`.** (2.6.0 had the first six; 2.7 added `rule-maker` and `ui-design`.) The Claude plugin registers all twenty. Direct installations must copy each complete folder into the same host skill root, as siblings from one version: the four phase skills read their shared policies from the installed `workflow` folder and stop when it is missing or from another version. They are not Matt catalogue entries, so `check_specialists.py` does not validate their host availability. Verify actual identifiers, enabled state, model invocation and a safe invocation of each. Do not keep old and new copies active together.

For ordinary prompts, merge the small [project routing block](skills/workflow/templates/PROJECT-ROUTING.md) into the applicable existing host-loaded policy as an authorized setup change. Preserve existing content and directory overrides; do not overwrite policy files or copy the whole workflow into them. Confirm Codex's applicable AGENTS instructions and Claude's actual CLAUDE/project instructions separately. The template is not active just because it is bundled.

Record the workflow version/source, the resolved identifiers of the local skills, routing-policy location/scope, actual load evidence and specialist snapshot. Test a plain request **without** `/workflow` or `$workflow`, an explicitly invoked task and a negative trigger. If routing fails, fix setup before relying on implicit use. There is no guarantee of model obedience from Markdown alone.


Matt's `setup-matt-pocock-skills` is **user-invoked**. Run its actual qualified command when
repository setup is necessary and authorized, not automatically inside every workflow.
It can edit agent policy files and configure tracker labels, including remote writes.
Inspect its proposed changes before approving them. Reuse existing tracker, glossary,
ADR and document conventions rather than accepting defaults that conflict with them.
[Upstream setup skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/setup-matt-pocock-skills/SKILL.md)

For this workflow, local PLAN/TODO/FINDINGS/DECISIONS are sufficient as the spec/task
source. A GitHub/GitLab account, external ticket or second `.scratch` task system is not
required. The code-review adapter receives the approved local PLAN directly. Existing
repository policy can describe this once. Do not run setup only to satisfy an unused
tracker-related skill or rewrite an existing project glossary layout.

#### 3. Check files without changing them

Python 3.10+ is sufficient; no Python dependencies, network, credentials or Git are used
by the checker. Supply the actual collection root or installed skill roots discovered
in your host. It supports a nested collection and flat skill directories. Include all
relevant **active** roots when checking duplicates; do not scan the entire home folder or
all historical plugin caches. An omitted root cannot be checked.

From the extracted workflow package root, with the actual path substituted:

```powershell
python -X utf8 skills/workflow/scripts/check_specialists.py --root "C:\Path\To\Installed\MattSkills" --profile collection
```

For a standalone skill copy, use the same `scripts/check_specialists.py` relative to that
skill directory. To check only the routes needed for the next phase:

```powershell
python -X utf8 skills/workflow/scripts/check_specialists.py --root "C:\Path\To\Installed\MattSkills" --only research diagnosing-bugs
```

`--profile routed` checks 11 automatic Matt routes; `collection` checks the 27 historically recorded Matt names. Local visualization files are validated with the package, not as external specialists.
Repeat `--root` for separate active roots. Overlapping roots pointing to the same physical
files are deduplicated; two physical copies of the same name are reported as ambiguous.
The host inventory must still identify whether two aliases point to one physical copy.

Exit **0** means the requested disk checks passed; **1** means a missing, ambiguous,
incomplete, changed or policy-mismatched entry; **2** means an input/read error.
It checks declared names, invocation flags, known required files and full-tree fingerprints.
It is not a complete YAML parser or a comprehensive validator of all upstream references.
A detected malformed file is reported rather than treated as an available skill.

**ON_DISK is not READY.** Separately verify the actual host-loaded identifier, source,
enabled state, model-invocation permission, required tools and a real smoke invocation.
An unrelated skill called `research` can pass name-based disk inspection; verify its
origin with the host/install record. The checker cannot certify source authenticity,
access to tools, correct invocation or model obedience. Record these distinctions.

#### 4. Review and freeze the local baseline

At approved setup, capture a report to a private local path. PowerShell example:

```powershell
python -X utf8 skills/workflow/scripts/check_specialists.py --root "C:\Path\To\Installed\MattSkills" --json | Set-Content -Encoding utf8 "C:\Path\To\Private\inventory.json"
```

Choose an existing parent directory and a new report filename; the shell redirection
writes that file. The checker itself never saves or installs anything. Report paths can
contain usernames; sanitize paths before sharing. Inspect all statuses, source provenance,
content and runtime smoke results, then record the team's approval of that snapshot.
Generating a report does not approve it. Preserve an earlier approved baseline.

Before resuming after a host switch or collection update:

```powershell
python -X utf8 skills/workflow/scripts/check_specialists.py --root "C:\Path\To\Installed\MattSkills" --only research diagnosing-bugs --baseline "C:\Path\To\Private\approved-inventory.json"
```

Changed content blocks automatic reuse of the affected route until reviewed; new file
names and supporting-file changes count. Hashes are byte-sensitive, so line-ending
changes also need review. A content match does not prove current host availability.
Review new upstream skills intentionally before adding routes/catalogue entries; do
not silently accept `latest` or invent an upstream commit hash from a version string.

#### 5. Run a runtime smoke test, then normal tasks

In a disposable project with only the intended workflow version and approved specialist installations,
first make a plain behavioral-change request with no skill name. Verify workflow loaded and routed to `workflow-clarify`, code was inspected, and the behavior agreement was presented in PLAN and chat (gate one) with no tickets or code yet. After agreeing, verify `workflow-specify` produced tickets with dependencies and test seams and showed the HTML plan report (gate two) before application changes. Test rejection/correction at each gate and subsequent approval; a gate-two correction to behavior must return to clarify. Invoke one phase skill directly on a task missing its prerequisite and verify it refuses and names the earlier phase. Then request a research/plan task with one genuine decision. Verify the trace shows the
qualified `grilling` specialist actually loaded, facts investigated rather than asked,
and the question batch saved to the existing task record. Approve a bounded code fix
with explicit test seams; verify the diagnosis/TDD/review routes, no repeated approval,
and no stage/commit/push. Verify `workflow-execute` reviewed each ticket on Standards and Spec and `workflow-deliver` reported unverified or partial work honestly. Terminate mid-step and test cold continuation on another host; resumption must keep both recorded gates.

Also test a disabled specialist, same-name duplicate, changed supporting file and
unavailable subagents. Apply [SPECIALISTS.md](skills/workflow/SPECIALISTS.md), not guessed aliases or a
simulated “skill executed” log. A read-only file check is not this runtime smoke test.
The package's behavioral scenarios describe the expected observations; perform them
locally before a wider team rollout.

#### Retained local flowchart setup (since 2.2.1)

No additional specialist installation is required for diagrams. Copy the complete
`codebase-map` folder, including FLOWCHART-DESIGN.md, REPORT.md, scripts, assets and
examples. The local renderer uses Python 3.10+ standard library. Local browser checks
are optional when the browser tools already exist; do not install them silently.

For a 2.2.0 upgrade, replace the old package-owned DIAGRAM-DESIGN.md with the bundled
FLOWCHART-DESIGN.md. Preserve unrelated files. Remove any custom project instruction
that explicitly routes our reports to the external diagram-design skill; retain Matt's
instructions and verify the local codebase-map identifier. An existing external diagram
skill may remain for unrelated work; do not uninstall it automatically. This workflow
neither selects nor requires it.

The historical 2.2.1 migration removed the external design entry. In 2.4.0 Matt's 27 records and source snapshot remain unchanged; the package adds local workflow utilities without adding external dependencies. Other providers are retained. Review the package change while preserving the
existing approved Matt fingerprints; do not reinstall or refresh the collection just
because this dependency changed. The checker deliberately rejects inventories with a different workflow_version. Keep
the old approved baseline unchanged. Generate a new candidate inventory, compare Matt's
unchanged fingerprints against the old report as part of the upgrade review, verify the
actual host, and approve the new baseline explicitly. Do not just relabel the old report
or reinstall the collection to make a version check pass.

In a fresh session with no external diagram skill available, request a visual review.
Verify codebase-map loads its local design guide, produces the approved flowchart, and
stops before application implementation. Necessary questions still use the bundled grilling; TDD and review use the
bundled copies; research and diagnosis use Matt's installed skills when relevant.
A local Python render does not prove that this host-level behavior passed.


#### 2.4.0 runtime check for questions, task reuse and utilities

Update the existing project-routing block once during approved setup; do not append another copy. In a fresh Claude session verify which qualified workflow and grilling identifiers actually load, their source paths/revisions and model/host versions. A slash-menu entry or installed folder alone is insufficient; avoid same-name shadowing. After compaction/account changes, restore the recorded phase and references, not a fresh task folder.

Test a vague feature without asking for an interview, a detailed request with a hidden consequential omission, a partial answer, and an existing related task without providing its path. Check actual grilling load, relevant questions, preserved answers, task selection and no preapproval application writes. Compare with 2.2.1 under the same configuration. If grilling does not load, inspect identity/visibility/tool permission/compaction before blaming prompt length. Do not disable permissions or claim the file checker proves behavior. See the package tests/behavioral protocol for evaluator-only cases.

Keep the existing approved Matt installation. A package version change alone is not a reason to reinstall it. The optional helpers are described in [OPTIONAL-HELPERS.md](skills/workflow/OPTIONAL-HELPERS.md); no extra installation is needed for this update.

#### Global artifact policy — all projects (2.5.0)

The maintained source is [ARTIFACTS.md](skills/workflow/ARTIFACTS.md). During approved setup, the bundled [global policy helper](skills/workflow/scripts/global_policy.py) deploys one versioned, byte-checked copy to `~/.workflow-axa/ARTIFACTS.md` and merges a short marked block into each host's global instructions. Do not maintain separate policy bodies per project. Updating the skill alone does not update the deployed copy; rerun this setup when the policy changes.

Run from the package root in Git Bash or a terminal with Python 3.10+:

```bash
python -X utf8 skills/workflow/scripts/global_policy.py
python -X utf8 skills/workflow/scripts/global_policy.py --apply
python -X utf8 skills/workflow/scripts/global_policy.py --check
```

The first command previews without writing; review it and ARTIFACTS.md before `--apply`. Standalone installs run `scripts/global_policy.py` inside their workflow folder. The helper keeps unrelated global-file bytes and newline style, replaces only its marked block, and creates no per-run logs/backups. It does not install skills or touch projects. Malformed markers, modified/unowned policy, downgrade, linked/hard-linked config or stale reads stop the merge for manual review. Writes are atomic per file, not a transaction across files; after an interrupted setup rerun `--check` and complete the reviewed merge.

Default destinations: `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`. CLAUDE_CONFIG_DIR/CODEX_HOME and explicit `--claude-dir`/`--codex-home` absolute overrides select actual profiles. A nonempty Codex AGENTS.override.md receives the same small block because it shadows the base file; no override is created. Preview prints all destinations. Custom instruction discovery, an organization policy, WSL/cloud homes or permission restrictions need separate inspection. Never copy the Altinstar-specific project files into a global location.

Claude's block imports the policy; Codex's instructs the agent to read it before output-producing work. Verify actual loading in fresh sessions, not merely checker success. Each machine/account environment and each teammate needs its own setup. The policy grants no access that the host otherwise denies; no permission changes or hooks are installed. Project protections remain effective, and contradictions require clarification.

References checked 26 October 2026: [Claude instruction scopes/imports](https://code.claude.com/docs/en/memory), [Codex global instructions and overrides](https://developers.openai.com/codex/guides/agents-md/). These support loading locations, not guaranteed model obedience or automatic retention by project scripts.

#### Shared rules and missing project setup (2.7 candidate)

Install `rule-maker` and `ui-design` with the existing six skills (eight total in 2.7; 2.8.0 adds the four phase skills and eight vendored skills for twenty). Its rules are referenced centrally, not copied into repositories. Run its `scripts/activate_rules.py` preview/apply/check from the final stable installation after approval. Preserve existing artifact activation. The helper changes only managed global reference sections; no automatic hooks, permissions changes or remote updater. New/missing projects trigger readiness even without a setup command. Test the actual installed host/profile; package checks are not live enforcement proof.

#### UI boundary integration

Install local ui-design together with the other package skills. It uses the central rule-maker design.md; do not copy that policy into projects or install an external design skill. Verify the route with an ordinary UI request, a backend negative case and an existing report generation. Check the real host registry and global reference, not files alone. No auto-creation of a UI kit/preview, no guessed kit approval and no repeat interview for a valid resumed mode. Update the project routing block only through an approved merge when necessary.

For the optional UI screen-flow report extension, install the entire codebase-map folder including screen_flow.py and ui-review assets. Existing global shared-rule references remain valid at the same path. Plain application UI requests still route through shared design.md → ui-design, not directly to a report prototype. Confirm live invocation separately; files on disk do not prove execution.
