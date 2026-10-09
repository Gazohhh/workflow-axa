# Workflow v2 candidate

## Current checkpoint
- Status: done
- Approved plan revision: R1
- Approval: user, 2026-10-09 — "yes to all of it give me a new zip when your done"; applies to the recommendations in the supplied workflow review and preceding response.
- Workspace: extracted copy of the uploaded workflow-axa.zip; no live application repository.
- Branch/worktree: not applicable; embedded Git history deliberately excluded from the working copy and replacement ZIP.
- Owner: current assistant session; ownership released for local pilot; no subagents available.
- Active tasks: none; local candidate delivery complete.
- Last verified step: source and extracted-package validation; 18 unittest cases pass; ZIP integrity and source equality checked. See FINDINGS.md V1–V4 and the timeout note.
- Next safe action: a user/teammate may run the documented Claude Code/Codex pilot in an isolated fixture. Installation, publication and Git actions are not authorized by this delivery.
- Blocking decisions: none for this candidate.

## Goal and scope
Deliver one updated workflow skill in a clean replacement ZIP. Keep clear documentation, actionable plans/TODOs, scoped cleanup, evidence-backed verification, and continuation after abrupt interruption. Reduce conflicting rules rather than optimizing line count alone.

R1 includes skills/workflow, plugin manifests, README, CHANGELOG, a small local test harness and fixture, maintenance documentation, and this task record. Preserve the original historical task records. No changes to application projects, host installations, permissions, Git index/history, remote repositories, or published releases.

## Approved policy choices
See DECISIONS.md: bounded delegated implementation, lightweight authorized edits, purpose-based file scope, one owner and explicit handoff, optional helpers, concrete maintainability criteria, no automatic staging, and reusable approved PDF language. Actual team host versions and private examples of rejected code are not known; do not invent them. Use Claude Code/Codex as documented local test targets and label examples illustrative.

## Acceptance and verification
- One SKILL.md entrypoint and self-contained conditional references; consistent approval, questions, recordkeeping, cleanup, testing, handoff, and Git rules.
- README provides local Claude Code/Codex testing without pushing; no mandatory third-party skills.
- Runnable package/fixture checks and human/agent behavioral scenarios, with actual results kept separate from unexecuted model evaluations.
- Archive excludes .git, credentials, caches, generated fixtures, and old duplicate instruction snapshots.
- Validate final source, final ZIP integrity, and extracted-package checks. Do not label host validation or model behavior tested without execution.

## Outcome
Delivered 2.0.0-rc.1 as a clean source ZIP. Core reduced from 1,363 to 1,080 words; policies, references, metadata and usage docs aligned. Eighteen local tooling tests and extracted-package checks pass. Live host/model evaluations remain unrun, so the output is a local-test candidate, not a claimed production-validated release.
