# Verification and operation authority

Load before tests/builds, device runs, profiling, external-service checks or operations whose outputs/side effects matter. This supplements project commands and permissions; it does not authorise execution by itself.

## Know what the command actually does

Inspect the relevant script/configuration and prerequisites before treating a familiar name as safe. A test gate can build players, open an editor, change generated files, install dependencies, sync native projects or contact a backend. Separate inspection, isolated tests, full builds, device installation, publication, migrations and deletion. Approval for one does not automatically authorise the others. Reuse an already explicit bounded approval; no repetitive consent for unchanged authorised checks.

Establish the effective environment and data isolation. "staging", "dev" or "test" in a hostname/script is not proof of a safe target. Check mocks, configuration selection, credentials scope and possible writes without dumping secrets. Never perform a production mutation or destructive operation under generic test permission. If a required gate depends on a protected/unapproved operation, report the blocker and request the necessary decision; do not bypass the gate or trigger the prerequisite silently.

For profiling/benchmarking, observe the project's quiet-host/exclusivity rules. Stop or schedule independent agents/builds through authorised coordination; do not kill unknown processes. Device, build identity, workload and quality must match the evidence claim. Every change needs an impact assessment; actual measurement requirements follow the approved project policy, not an agent's preference to skip it.

## Report observations, not obligations as facts

A rule that requires GREEN is not evidence that the result is GREEN. Use current observed proof: passing, failing, stale, not run, blocked or not applicable, with source/time and relevant code identity. Verify cached proof is current before reusing it. Never hand-edit a generated verdict to satisfy a build.

Compare actual diagnostics/tests, not just totals. An old baseline or an unchanged count can hide a new regression. Preserve expected failing regression tests and distinguish baseline/environment failures from introduced ones. No automatic weakening, skip flags, fixture replacement or baseline acceptance.

Retain concise results and necessary evidence in existing task records. Follow the artifact policy; do not copy entire builds as proof or clean another process's output. A report of untested work must remain untested through handoffs and project-status summaries.

This is team operating policy. Framework-specific testing guidance remains in the selected modules and the project's real commands; there is no generic command safe for every project.
