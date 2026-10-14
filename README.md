# workflow-axa

**2.2.1 — local flowchart design; Matt specialists retained.** One team workflow plus an on-demand `codebase-map` skill. This ZIP updates the skill package; it does not install itself, configure your project or change application code. [VALIDATION.md](VALIDATION.md) records actual tests and limits.

## What changed in 2.2.1

Only the flowchart dependency changes. `codebase-map` now follows its bundled
[FLOWCHART-DESIGN.md](skills/codebase-map/FLOWCHART-DESIGN.md) and existing local renderer.
No external `diagram-design` install, skill lookup or invocation is needed. The approved
flowchart styling, geometry, separate feature/build/structure views and report schema
are unchanged. Historical source attribution remains informational.

Matt's **research, diagnosing-bugs, tdd, code-review, grilling and other existing routes
remain external and unchanged**. They are not replaced by condensed local methods.
All 27 Matt catalogue entries, eleven reusable routes and their adapters are preserved.
Current-code grounding, questions, checkpoints and user approval still precede coding.

## Workflow behavior

```text
Inspect current code → establish the requested outcome → resolve necessary decisions
→ prepare PLAN + TODO + acceptance → generate/open current-versus-proposed HTML
→ STOP for user approval → record approval → implement and verify within that scope
```

The HTML shows what the agent understood, existing flow, proposed behavior, tasks/cleanup, exclusions, and completion checks. It is generated after the task list is **prepared**, not executed. Opening it or answering grilling does not approve implementation. The user's response in the agent conversation approves the identified plan revision. Corrections update the records and diagram together before coding.

Substantive features, behavioral fixes and architectural changes use the gate automatically. Lightweight low-risk edits, general explanations and PDF/docs-only deliverables keep their proportionate routes. Existing valid approval is reused on handoff; an explicit bounded waiver is recorded, never assumed. No automatic staging, commits, pushes, publication, dependency installs or application changes during preview.

Every repository-specific proposal must connect the request to inspected owners/callers/tests, the actual gap, mapped tasks and acceptance. Existing/partial capabilities are investigated before adding another implementation. New product ideas do not silently enter scope. Read-only explanations still need code evidence when they make repository-specific claims.

## Upgrade checklist — important for plain prompts

**Install both local skills and merge the project routing block once.** Updating a ZIP alone cannot ensure an ordinary prompt enters the workflow.

1. Extract to a separate candidate folder, preserving your previous version and `.git`/unrelated work. For Claude plugin use the root containing `.claude-plugin/plugin.json`; both skills are registered there. For direct Codex/Claude installs copy the **complete** `skills/workflow` and `skills/codebase-map` folders into the appropriate skill root. Do not retain duplicate active copies.
2. Follow [SETUP.md](skills/workflow/SETUP.md), including the small [project-routing template](skills/workflow/templates/PROJECT-ROUTING.md). Merge it into existing applicable host instructions as an approved setup change; do not replace your AGENTS/CLAUDE files. Verify in a fresh session that both local skills actually load.
3. Keep Matt Pocock's collection separately installed and verified. Existing [specialist routes](skills/workflow/SPECIALISTS.md) remain explicit, including `grilling`. The read-only checker inventories Matt’s historically recorded 27 names/11 reusable routes; disk presence does not prove host availability or invocation. This ZIP neither bundles nor silently installs upstream skills.

4. **No flowchart dependency to install.** Replace the complete package-owned codebase-map folder with this version, retaining any unrelated local files separately. Remove its old `DIAGRAM-DESIGN.md` integration reference; `FLOWCHART-DESIGN.md` replaces it. Update any previously added project-routing sentence that explicitly calls the external design skill. Keep Matt's setup and approved fingerprints. An existing external diagram skill can remain for unrelated tasks; this package does not invoke it or uninstall it.
5. Old HTML stays readable and checkable. New report generation uses **schema 2** for explicit layout; migrate old JSON with [REPORT.md](skills/codebase-map/REPORT.md), preserving records and reviewed artifacts. Do not silently reinterpret an old architecture graph as a user flow.

## Local commands

Claude plugin:

```text
/workflow-axa:workflow <feature or fix request>
/workflow-axa:codebase-map current <feature or subsystem>
/workflow-axa:codebase-map proposed <task folder or supplied design>
/workflow-axa:codebase-map compare <task folder>
```

Codex: `$workflow` and `$codebase-map`. Standalone Claude skills: `/workflow` and `/codebase-map`. Explicit commands remain available even after ordinary-prompt routing is configured. A map-only request never starts implementation or Matt's architecture-improvement workflow.

The viewer is local HTML/SVG with native-size scrolling, view selection, zoom/Fit, evidence links and editable JSON source, not a collaborative Miro board. The renderer uses Python 3.10+ standard library; the bundled FLOWCHART-DESIGN.md supplies the approved visual-design procedure. Reports use no CDN, server, font download or external upload. [Open the bundled synthetic example](skills/codebase-map/examples/review.html). [Renderer commands and input contract](skills/codebase-map/REPORT.md).

## Test before pushing

From the extracted plugin root:

```powershell
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p "test_*.py" -v
python -X utf8 tools/create_fixture.py --output "C:\Dev\workflow-sandbox" --scenario clean
claude plugin validate "C:\Dev\workflow-axa-candidate" --strict
cd "C:\Dev\workflow-sandbox"
claude --plugin-dir "C:\Dev\workflow-axa-candidate"
```

Substitute real paths and check installed CLI help when needed. Python/Git fixture tests create one local baseline commit only in a **new synthetic repository**, not in your project; they never create a remote. The browser smoke test is separate and optional, using already installed Playwright/Chromium. [Testing guide](tests/README.md).

Test a **plain request with no skill name**, then inspect the trace: workflow loaded, current-code evidence read, no expanded features, visual report shown, implementation paused. Reject/correct the plan, then approve the revised view. Test hard interruption and fresh-agent continuation. Also test explicit invocation and general-question/diagram-only negative triggers. [Behavioral scenarios](tests/SCENARIOS.md) are authored test cases, not evidence that model behavior has passed.

## Records and retained behavior

`PLAN.md` owns goal/checkpoint/approval; `TODO.md` owns tasks; `FINDINGS.md` owns evidence; `DECISIONS.md` owns material choices. HTML/JSON are revisioned views of those records, not competing specifications. Documentation precedes substantial work and each work unit is checkpointed. Resumption reconciles current files, source drift, approval and capabilities; a new machine needs uncommitted changes transferred through an authorized method as well as the docs.

Question batching, user-owned decision boundaries, optional subagent fallback, maintainability rules, scoped replacement cleanup, task-attributable review and PDF language approval reuse are retained. The workflow does not equate matching hashes, green structural tests or pretty diagrams with genuine understanding or authorization.

After the local host pilot, a maintainer may publish/tag through the team's authorized process. This archive is not installed, published, tagged or pushed. [Changes](CHANGELOG.md) · [design/source notes](docs/DESIGN.md) · [prompt examples](skills/workflow/CHATGPT-PROMPTS.md).
