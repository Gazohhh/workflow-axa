# workflow-axa

**2.0.0 — specialist-integrated package.** One team workflow for research, planning, implementation, review and recovery. Documents precede substantial work; user decisions stay explicit; approved implementation does not need permission for every step.

This ZIP changes workflow defaults, not your application. It has not been published or installed. Host/model behavior still needs the local pilot below; see [VALIDATION.md](VALIDATION.md) for checks actually run.

## What changed

The core no longer mandates subagents, interrupts for every unknown, or stages files. It separates discoverable facts from user decisions, records the approved scope, checkpoints interrupted work, and checks directly superseded code and documentation. Small explicit low-risk edits use a short record instead of skipping documentation. Unchanged approved PDF language can be reused.

Implementation details inside an agreed approach are delegated. Changed behavior, material architecture choices, new dependencies/services/costs, schema/public-interface changes, destructive actions and publication remain user-owned. The agent must not silently reinterpret "finish the task" as permission to expand it.

The [core skill](skills/workflow/SKILL.md) defines the process. [Recordkeeping](skills/workflow/TASK-FOLDER.md), [questions](skills/workflow/QUESTIONS.md), [audit](skills/workflow/AUDIT.md) and [PDF delivery](skills/workflow/PDF-DELIVERABLE.md) contain the details. Only one workflow skill is registered. [SPECIALISTS.md](skills/workflow/SPECIALISTS.md)
explicitly routes applicable work to Matt Pocock's installed specialists, including
`grilling` for structured questions. His user-facing `grill-me` wrapper is not an automatic
alias. Eleven reusable routes are defined; manual upstream workflows are not chained.

## Specialist setup

**Matt's collection remains a separate installation. This ZIP does not install it on your
machine.** Follow [SETUP.md](skills/workflow/SETUP.md) once per host/repository as needed.
It covers the full 27-skill inventory, installed-source/host checks, duplicate avoidance,
local fingerprint baselines and a real runtime smoke test. No invisible downloads,
updates or policy-file changes are authorized by an ordinary workflow task.

The bundled read-only checker can inspect the full collection or just selected routes.
It detects missing files, duplicate copies, invocation-policy changes and changed support
files. A successful disk check does **not** mean a skill is enabled or actually invoked;
verify that in the host. Missing selected skills block only dependent work, unless an
explicit fallback was already approved. Unavailable subagents have a documented sequential
adapter, not a fabricated independent review.

## Test locally before pushing

Extract the ZIP and move or rename its top-level `workflow-axa` folder to a separate location, for example `C:\Dev\workflow-axa-candidate`. Use the folder containing `.claude-plugin/plugin.json` as the plugin root. Do not overwrite your only previous copy or an installed plugin cache. Python 3.10+ and Git are required for the bundled fixture checks; no Python packages are required.

From the extracted plugin root:

```powershell
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
python -X utf8 tools/create_fixture.py --output "C:\Dev\workflow-sandbox" --scenario clean
```

Complete the specialist setup/readiness check before live workflow tests. Use a new output path outside existing Git checkouts. The generator refuses existing destinations and repository ancestors. It creates a **synthetic disposable repository with its own local baseline commit**, never a remote or a commit in your project. Other scenarios are listed by `--help`. These checks validate the package and fixture tooling, not model obedience.

### Claude Code plugin

In a shell, substitute the actual extracted root and sandbox paths:

```powershell
claude plugin validate "C:\Dev\workflow-axa-candidate" --strict
cd "C:\Dev\workflow-sandbox"
claude --plugin-dir "C:\Dev\workflow-axa-candidate"
```

In that session:

```text
/workflow-axa:workflow Fix negative-score handling in both display paths. Inspect the current code and docs, then present a bounded plan before implementation. No new dependencies and no Git staging.
```

The namespaced command is for the plugin installation. `--plugin-dir` loads the local candidate for the session; no Git push is needed. Check the installed CLI's help when a flag is unavailable. Host validation is separate from the bundled structural checks. [Claude plugin documentation](https://code.claude.com/docs/en/plugins/create)

### Codex

Copy the entire `skills/workflow` folder into the disposable repository's `.agents/skills/workflow`, then start a fresh Codex session there and use `$workflow` with the same request. Preserve all supporting files; copying only `SKILL.md` is incomplete. Use only one workflow copy per comparison. [Codex skill discovery](https://developers.openai.com/codex/skills/)

## Behavior tests and team pilot

[tests/SCENARIOS.md](tests/SCENARIOS.md) provides staged prompts, fixture choices and pass conditions for approval, batching, abrupt interruption, shared-file staging, cleanup and PDF reuse. [tests/README.md](tests/README.md) explains baseline/candidate comparisons and optional host-native evals. Inspect traces and diffs, not only the final answer.

Compare the previous version and 2.0.0 separately against fresh identical fixtures with the same model, permissions and approved specialist installation. Reproduce a hard stop without first requesting a handoff. Pilot a cold continuation with another teammate. Do not average away unauthorized changes or leaked secrets with good formatting scores.

For an existing Git checkout of this skill, review the candidate's changed files locally and preserve your `.git` and unrelated edits. Historical task records are retained as history, not active workflow rules. Keep a working previous version for rollback. The requested version is already 2.0.0 in this archive. After a successful pilot, a human
may publish/tag it; this archive has not been installed, published or tagged. The version
number is not evidence that live host tests passed.

## Everyday use

A prepared request still gets investigation and an approval boundary for unresolved choices. A bare goal receives useful discovery and only necessary questions. A clear low-risk edit receives a lightweight record and verification. "Research only" does not authorize code changes. "Read-only; do not write files" keeps the record in the conversation and explicitly gives up persistent recovery for that session.

Normal task records live under `docs/plans/YYYY-MM-DD-<slug>/` unless the project already defines a location. `PLAN.md` holds the current checkpoint and approval, `TODO.md` the work, `FINDINGS.md` the evidence, and `DECISIONS.md` material choices. One owner updates them. A new agent reconciles them with actual files before resuming; cross-machine handoff must transfer uncommitted changes as well as documents.

PDF requests use the same workflow with the conditional reader procedure. Existing approved audience/language/terminology can be reused when applicable; new meaning needs approval. Evidence, editable source, rendering and final-version reviews remain required.

Git staging, commits, pushes, deployment and external publication are not automatic. Explicit authorization for one does not authorize the others. Markdown instructions also do not replace the host's permission controls.

## Installation after the pilot

Choose one route. A repository-local direct skill lives in `.agents/skills/workflow` for Codex or `.claude/skills/workflow` for standalone Claude Code; invoke `$workflow` or `/workflow` respectively. For the Claude plugin, load its root and invoke `/workflow-axa:workflow`. Once a maintainer has actually published 2.0.0 to the existing marketplace, the existing marketplace/install route remains available; do not assume the remote contains this ZIP.

Full [change history](CHANGELOG.md), [design/source notes](docs/DESIGN.md) and [prompt examples](skills/workflow/CHATGPT-PROMPTS.md) are included. The root Python tools belong to package maintenance/testing. The portable checker lives
inside the skill so direct skill copies retain dependency checking; run it at setup or
when relevant capability/content changes, not on every tool call.
