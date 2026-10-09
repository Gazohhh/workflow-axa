# Team setup and dependency checks

This skill uses Matt Pocock's collection as a separate dependency. Installing
`workflow-axa` alone does **not** install it. Keep one collection installation route per
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

`--profile routed` checks the 11 automatic routes; `collection` checks all 27 names.
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

In a disposable project with only the intended workflow version and Matt installation,
request a research/plan task with one genuine decision. Verify the trace shows the
qualified `grilling` specialist actually loaded, facts investigated rather than asked,
and the question batch saved to the existing task record. Approve a bounded code fix
with explicit test seams; verify the diagnosis/TDD/review routes, no repeated approval,
and no stage/commit/push. Terminate mid-step and test cold continuation on another host.

Also test a disabled specialist, same-name duplicate, changed supporting file and
unavailable subagents. Apply [SPECIALISTS.md](SPECIALISTS.md), not guessed aliases or a
simulated “skill executed” log. A read-only file check is not this runtime smoke test.
The package's behavioral scenarios describe the expected observations; perform them
locally before a wider team rollout.
