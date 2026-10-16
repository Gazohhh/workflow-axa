# Upgrade to workflow-axa 2.3.0

This updates our two local skills. It does not install itself or change your app.

1. Keep a copy of the currently working package. Extract this ZIP separately. Replace the package-owned `workflow` and `codebase-map` skill folders completely, including their references/scripts/assets; preserve unrelated local customizations and do not merge old duplicate skill bodies. For a Claude plugin, use the root containing `.claude-plugin/plugin.json`.
2. Update the existing host-loaded project routing block using `skills/workflow/templates/PROJECT-ROUTING.md`. Merge it once; do not overwrite unrelated CLAUDE.md/AGENTS.md rules or append duplicate blocks. This is what directs ordinary requests to the workflow's new task-selection and questioning rules.
3. Keep Matt's installed collection. Research, debugging, TDD, review, grilling and the other established routes still use it. No external diagram-design, skill-creator or webapp-testing installation is required.
4. Start a fresh session. Confirm the actual source/version and qualified identifiers of both local skills and grilling, not merely their presence on disk. Avoid stale global/plugin copies. The read-only specialist checker checks files, not actual invocation; see SETUP.md for the reviewed inventory migration after a workflow-version change.
5. Run the package checks and the live-host pilot before broad rollout. The package includes 14 evaluator-only cases, including missing decisions and existing task discovery. Keep expected answers outside the agent's accessible project. Preserve the previous installation as a rollback option.

## Expected everyday behavior

“Add a feature” makes the agent inspect existing code and use grilling to look for missing decisions. A detailed request can still have a gap; a complete request does not need invented questions.

“Continue this work” reuses the identified task and its valid answers/approval. A new `/workflow` command does not create a new folder. When a likely match is ambiguous, the agent asks which task you mean before writing records.

Substantive implementation still waits for your approval of the local flowchart and plan. Documentation/checkpoints, scoped cleanup and no automatic Git actions remain.

## Local checks

From the extracted package root:

```powershell
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -v
```

The visual comparison tool uses optional already-installed Playwright/Chromium and Pillow; normal report generation remains Python standard-library only. Reference captures are platform-specific and are not automatically replaced. See tests/VISUAL-REGRESSION.md.

**Live Claude/Codex behavior has not been tested by this delivery.** Follow tests/behavioral/README.md on your actual host. VALIDATION.md records what was and was not run.
