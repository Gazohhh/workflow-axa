# TODO

- [x] T1 — Rework the core skill, references, metadata, README and changelog — evidence: source inspection; accepted policy mapped in DECISIONS.md; core now 1,080 words.
- [x] T2 — Add local structural tests, safe disposable fixtures, and behavioral scenarios — evidence: two standard-library tools, package/fixture tests, seven fixture variants and 15 scenario protocols plus short regressions.
- [x] T3 — Run package and fixture tests; review active instructions for contradictions and stale defaults — evidence: V1/V2 in FINDINGS.md; 18 tests pass; self-review, not independent/model validation.
- [x] T4 — Package a clean ZIP, check extracted contents, and record exact validation limits — evidence: FINDINGS.md V3/V4; CRC/source equality and extracted-package tests; live-host limits in VALIDATION.md.

## R2 / 2.3.0 maintenance
- [x] T5 — Fix task selection and proactive grilling across the core, adapters, records and routing template; supports R10/R11.
- [x] T6 — Apply plain language and concrete code/document/report quality checks; supports R12.
- [x] T7 — Add read-only visual capture/comparison with controlled references and negative tests; supports R13.
- [x] T8 — Add hidden-gap/task-discovery fixtures and a reproducible live-agent comparison protocol; supports R14.
- [x] T9 — Run original/new tests, compare protected files, update release docs, package and revalidate the extracted ZIP; supports R15.

Evidence for T5/T6: current instruction references and instruction-regression tests; these establish the written contract, not live adherence. Evidence for T7: 16 pixel-tool tests, four zero-difference captures and the deliberate typography defect. Evidence for T8: five additional fixture variants and 14 evaluator-only case definitions validated; actual host sessions NOT RUN. Evidence for T9: VALIDATION.md and tests/evidence, plus clean archive extraction/reruns.
