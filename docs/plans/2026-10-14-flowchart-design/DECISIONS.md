# Decisions
- D1 (approved): use the user-approved second flowchart sample, not the rejected UI-card sample.
- D2 (execution detail): package version 2.2.0, keeping exactly workflow and codebase-map as local skills; diagram-design stays an external routed dependency.
- D3 (execution detail): maintain compact workflow core; design integration lives in codebase-map reference. Reuse preapproved offline/system-font style, no brand onboarding or global skill edits.
- D4 (execution detail): explicit schema 2 geometry replaces the old generic grid renderer. Existing HTML manifests stay checkable; old JSON generation fails with migration guidance, never silently invents topology.

- D5 (execution detail): native controls and scrolling remain usable without JavaScript; progressive centering/keyboard/drag improves navigation but cannot grant approval. A no-script start link locates the entry on narrow windows.
- D6 (compatibility): the upstream self-check's canonical script contract applies to its own artifact format. The workflow shell uses its documented source manifest and local viewer contract, with its own security/browser checks; do not misreport upstream success or strip provenance to satisfy a different validator.
