# workflow-axa

**2.3.0 — stronger questioning, existing-task reuse and clearer reviews.** One team workflow and one local `codebase-map` skill. This archive updates the package, not your installed agent or application. [VALIDATION.md](VALIDATION.md) separates observed tests from untested model behavior.

## What changed

| Improvement | What the agent must now do |
|---|---|
| Proactive grilling | Use Matt's grilling to look for unstated decisions in every new substantive goal or material change, even when the prompt looks complete. Reuse sourced answers; no fixed question quota or repeated interview for an unchanged approved task. |
| Existing work | Search current/named/related task records before creating a folder. Keep a clear continuation in the same folder through revisions; ask about ambiguous matches, completed work or ownership. |
| Clear language | Explain concrete behavior and consequences before technical details in questions, plans, reports and completion messages. Keep exact evidence accessible. |
| No-slop review | Review unnecessary helpers, silent coercion, repetitive comments/docs and unsupported claims against specific examples, not a vague label. |
| Visual protection | Keep the approved flowchart local and unchanged. Compare stable reference screenshots; never automatically replace a failing baseline. |
| Actual-agent tests | New hidden-decision and task-discovery fixtures/protocol compare 2.2.1 with this version. Their results remain NOT_RUN until a real host run is observed. |

Matt's research, diagnosing-bugs, tdd, code-review, grilling and other established specialists remain separately installed. All 27 catalogue entries are retained; the grilling trigger/adapter is strengthened. The local flowchart needs no external diagram-design skill. Optional skill-creator and webapp-testing guidance is available only for approved maintenance/browser work; neither becomes a dependency.

## Workflow behavior

```text
Find the right task → inspect current code → uncover missing decisions with grilling
→ prepare PLAN + TODO + acceptance → show the local flowchart review
→ STOP for approval → implement within scope → verify and leave a checkpoint
```

The HTML is generated after the task list is written, not executed. It shows what the agent understood, current/proposed behavior, changes, cleanup, exclusions and completion checks. Opening it, answering questions or liking its appearance does not authorize implementation. The user's response approves the identified revision. Corrections update records and diagram together.

A new date, session or slash command is not a new task folder. A task match is also not approval of a new requirement: keep the folder and revise the affected decisions/scope. A complete request can need zero extra questions after the decision check. Important unanswered choices still block dependent work.

Substantive features, behavioral fixes and architecture changes retain the visual gate. Lightweight low-risk edits, explanations, PDF/docs-only and visual-only requests keep proportionate routes. Existing approval is reused after checking actual files. No automatic installs, staging, commits, pushes, uploads or deployment.

For a short installation handoff, start with [UPGRADE.md](UPGRADE.md).

## Upgrade checklist — important for plain prompts

**Install both local skills and merge the project routing block once.** Updating a ZIP alone cannot ensure an ordinary prompt enters the workflow.

1. Extract to a separate candidate folder, preserving your previous version and `.git`/unrelated work. For Claude plugin use the root containing `.claude-plugin/plugin.json`; both skills are registered there. For direct Codex/Claude installs copy the **complete** `skills/workflow` and `skills/codebase-map` folders into the appropriate skill root. Do not retain duplicate active copies.
2. **Update, do not duplicate, your existing routing block** so ordinary prompts use the new task-selection and proactive-grilling rules. Follow [SETUP.md](skills/workflow/SETUP.md), including the small [project-routing template](skills/workflow/templates/PROJECT-ROUTING.md). Merge it into existing applicable host instructions as an approved setup change; do not replace your AGENTS/CLAUDE files. Verify in a fresh session that both local skills actually load.
3. Keep Matt Pocock's collection separately installed and verified. Existing [specialist routes](skills/workflow/SPECIALISTS.md) remain explicit, including `grilling`. The read-only checker inventories Matt’s historically recorded 27 names/11 reusable routes; disk presence does not prove host availability or invocation. This ZIP neither bundles nor silently installs upstream skills.

4. **No extra skill installation is required by this update.** Keep your reviewed Matt collection and its approved fingerprints. Update both complete local skill folders while preserving unrelated custom files. When upgrading from 2.2.0, remove its retired package-owned DIAGRAM-DESIGN.md reference; later releases already use FLOWCHART-DESIGN.md. Do not uninstall unrelated external skills automatically.
5. No report-schema migration is needed from 2.2.1; the same schema-2 JSON and approved assets are retained. Older schema-1 inputs use the existing [migration guide](skills/codebase-map/REPORT.md). Keep previously reviewed HTML. Complete the new [live-host pilot](tests/behavioral/README.md) before team-wide reliance on the changed interviewing behavior.

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

Substitute real paths and check installed CLI help when needed. Python/Git fixture tests create one local baseline commit only in a **new synthetic repository**, not in your project; they never create a remote. The browser smoke test is separate and optional, using already installed Playwright/Chromium. [Testing guide](tests/README.md). [Visual comparisons](tests/VISUAL-REGRESSION.md) use optional installed Playwright/Pillow, not new application dependencies.

Test a **plain request with no skill name**, then inspect the trace: workflow loaded, current-code evidence read, no expanded features, visual report shown, implementation paused. Reject/correct the plan, then approve the revised view. Test hard interruption and fresh-agent continuation. Also test explicit invocation and general-question/diagram-only negative triggers. [Behavioral scenarios](tests/SCENARIOS.md) and the [new evaluator-only cases](tests/behavioral/README.md) are authored test cases, not evidence that model behavior has passed. Keep expected answers outside the agent workspace.

## Records and retained behavior

`PLAN.md` owns goal/checkpoint/approval; `TODO.md` owns tasks; `FINDINGS.md` owns evidence; `DECISIONS.md` owns material choices. HTML/JSON are revisioned views of those records, not competing specifications. Documentation precedes substantial work and each work unit is checkpointed. Resumption reconciles current files, source drift, approval and capabilities; a new machine needs uncommitted changes transferred through an authorized method as well as the docs.

Question batching, user-owned decision boundaries, optional subagent fallback, maintainability rules, scoped replacement cleanup, task-attributable review and PDF language approval reuse are retained. The workflow does not equate matching hashes, green structural tests or pretty diagrams with genuine understanding or authorization.

After the local host pilot, a maintainer may publish/tag through the team's authorized process. This archive is not installed, published, tagged or pushed. [Changes](CHANGELOG.md) · [design/source notes](docs/DESIGN.md) · [prompt examples](skills/workflow/CHATGPT-PROMPTS.md).
