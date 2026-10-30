# Team setup and dependency checks

This skill uses Matt Pocock's collection as a separate dependency. Installing
`workflow-axa` alone does **not** install that collection. Flowchart design is local to codebase-map. Keep one collection installation route per
agent; plugin plus copied skills can create duplicate names. The catalogue records the
27 names observed on 2026-10-09, including 11 model-invocable routes. Upstream metadata
was 1.3.1; no immutable source commit or live-tested installation is asserted here.
[Upstream setup and catalogue](https://github.com/mattpocock/skills#installation-30-second-setup)

## 1. Install once, with setup permission

Inspect the existing host inventory first. Reuse an approved working installation; do
not download a second one merely because it lives outside this project. Missing or
disabled dependencies require a setup decision, not an automatic fix during a task.

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

## 2. Align repository setup once

**2.6.0 requires this package's six local skills: `workflow`, `codebase-map`, `task-status`, `resume-task`, `workflow-doctor`, and `plan-review`.** The Claude plugin registers all six. Direct installations must copy each complete folder into the host's skill root. They are not Matt catalogue entries, so `check_specialists.py` does not validate their host availability. Verify actual identifiers, enabled state, model invocation and a safe invocation of each. Do not keep old and new copies active together.

For ordinary prompts, merge the small [project routing block](templates/PROJECT-ROUTING.md) into the applicable existing host-loaded policy as an authorized setup change. Preserve existing content and directory overrides; do not overwrite policy files or copy the whole workflow into them. Confirm Codex's applicable AGENTS instructions and Claude's actual CLAUDE/project instructions separately. The template is not active just because it is bundled.

Record the workflow version/source, both resolved local skill identifiers, routing-policy location/scope, actual load evidence and specialist snapshot. Test a plain request **without** `/workflow` or `$workflow`, an explicitly invoked task and a negative trigger. If routing fails, fix setup before relying on implicit use. There is no guarantee of model obedience from Markdown alone.


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

## 3. Check files without changing them

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
python -X utf8 skills/workflow/scripts/check_specialists.py --root "C:\Path\To\Installed\MattSkills" --only grilling research
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

## 4. Review and freeze the local baseline

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
python -X utf8 skills/workflow/scripts/check_specialists.py --root "C:\Path\To\Installed\MattSkills" --only grilling research --baseline "C:\Path\To\Private\approved-inventory.json"
```

Changed content blocks automatic reuse of the affected route until reviewed; new file
names and supporting-file changes count. Hashes are byte-sensitive, so line-ending
changes also need review. A content match does not prove current host availability.
Review new upstream skills intentionally before adding routes/catalogue entries; do
not silently accept `latest` or invent an upstream commit hash from a version string.

## 5. Run a runtime smoke test, then normal tasks

In a disposable project with only the intended workflow version and approved specialist installations,
first make a plain behavioral-change request with no skill name. Verify workflow loaded, code was inspected, requirements/evidence/tasks were mapped and the visual review was shown before application changes. Test rejection/correction and subsequent approval. Then request a research/plan task with one genuine decision. Verify the trace shows the
qualified `grilling` specialist actually loaded, facts investigated rather than asked,
and the question batch saved to the existing task record. Approve a bounded code fix
with explicit test seams; verify the diagnosis/TDD/review routes, no repeated approval,
and no stage/commit/push. Terminate mid-step and test cold continuation on another host.

Also test a disabled specialist, same-name duplicate, changed supporting file and
unavailable subagents. Apply [SPECIALISTS.md](SPECIALISTS.md), not guessed aliases or a
simulated “skill executed” log. A read-only file check is not this runtime smoke test.
The package's behavioral scenarios describe the expected observations; perform them
locally before a wider team rollout.

## Retained local flowchart setup (since 2.2.1)

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
stops before application implementation. Necessary questions still use grilling; actual
research, diagnosis, TDD and review continue to use Matt's installed skills when relevant.
A local Python render does not prove that this host-level behavior passed.


## 2.4.0 runtime check for questions, task reuse and utilities

Update the existing project-routing block once during approved setup; do not append another copy. In a fresh Claude session verify which qualified workflow and grilling identifiers actually load, their source paths/revisions and model/host versions. A slash-menu entry or installed folder alone is insufficient; avoid same-name shadowing. After compaction/account changes, restore the recorded phase and references, not a fresh task folder.

Test a vague feature without asking for an interview, a detailed request with a hidden consequential omission, a partial answer, and an existing related task without providing its path. Check actual grilling load, relevant questions, preserved answers, task selection and no preapproval application writes. Compare with 2.2.1 under the same configuration. If grilling does not load, inspect identity/visibility/tool permission/compaction before blaming prompt length. Do not disable permissions or claim the file checker proves behavior. See the package tests/behavioral protocol for evaluator-only cases.

Keep the existing approved Matt installation. A package version change alone is not a reason to reinstall it. The optional helpers are described in [OPTIONAL-HELPERS.md](OPTIONAL-HELPERS.md); no extra installation is needed for this update.

## Global artifact policy — all projects (2.5.0)

The maintained source is [ARTIFACTS.md](ARTIFACTS.md). During approved setup, the bundled [global policy helper](scripts/global_policy.py) deploys one versioned, byte-checked copy to `~/.workflow-axa/ARTIFACTS.md` and merges a short marked block into each host's global instructions. Do not maintain separate policy bodies per project. Updating the skill alone does not update the deployed copy; rerun this setup when the policy changes.

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

## Shared rules and missing project setup (2.7 candidate)

Install `rule-maker` and `ui-design` with the existing six skills (eight total). Its rules are referenced centrally, not copied into repositories. Run its `scripts/activate_rules.py` preview/apply/check from the final stable installation after approval. Preserve existing artifact activation. The helper changes only managed global reference sections; no automatic hooks, permissions changes or remote updater. New/missing projects trigger readiness even without a setup command. Test the actual installed host/profile; package checks are not live enforcement proof.

## UI boundary integration

Install local ui-design together with the other package skills. It uses the central rule-maker design.md; do not copy that policy into projects or install an external design skill. Verify the route with an ordinary UI request, a backend negative case and an existing report generation. Check the real host registry and global reference, not files alone. No auto-creation of a UI kit/preview, no guessed kit approval and no repeat interview for a valid resumed mode. Update the project routing block only through an approved merge when necessary.

For the optional UI screen-flow report extension, install the entire codebase-map folder including screen_flow.py and ui-review assets. Existing global shared-rule references remain valid at the same path. Plain application UI requests still route through shared design.md → ui-design, not directly to a report prototype. Confirm live invocation separately; files on disk do not prove execution.
