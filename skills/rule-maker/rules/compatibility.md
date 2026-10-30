# Compatibility, transitions and recovery

**Applies to:** persisted state, APIs, protocols, migrations, configuration and deployment/rollback. A rule update itself is not permission to migrate data or publish code.

## Required

- Establish which old/new clients, servers, native binaries, data formats and configurations are supported. An existing pin or compatibility check may encode a deliberate constraint; do not remove it because current tests use only the latest pair.
- Consider the transition, not only the two end states. Existing data or a partially rolled-out client may be interpreted differently after a change. Review mixed-version behaviour where it is supported.
- Make material contract changes explicit and approved. Handle unknown values/version mismatches according to that contract; never silently reinterpret them as a convenient default.
- Identify recovery/rollback limits before irreversible writes. Reverting code may not undo a schema or data change. Test transitions using disposable data and authorised tooling; do not run production migrations as verification.
- Retire compatibility paths only when their supported use is deliberately ended. Equally, do not retain speculative adapters forever for imaginary consumers. Track a justified removal condition in existing records.

## Example and defaults

An independently shipped web bundle can be newer than its embedded native player. Successful tests with matching latest builds do not prove that older supported binaries remain compatible. Preserve the project's bridge/version gate and test supported combinations; a mismatch may correctly require rejection rather than a fallback.

Prefer the smallest compatible evolution the established architecture permits. Staged migration patterns are options for actual needs, not mandatory scaffolding around every field rename.

## Verification

Check relevant old/new reads, writes, restoration, restart and supported rollback paths. Separate plan approval, implementation completion, successful checks and owner acceptance. Preserve presented reviews and meaningful decision history; progress and test retries are not new agreements.

Source: [Amazon deployment/rollback safety](https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/). These are adapted transition-review principles, not an authorisation to deploy.
