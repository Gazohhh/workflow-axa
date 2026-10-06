# Workflow PDF

Opened: 2026-10-07
Status: done

## Goal
Add optional reader-focused PDF mode to the existing /workflow skill, with owner-confirmed audience and terminology before drafting and accuracy, zero-knowledge reader, and product-language validation.

## Scope
One authoritative workflow skill with a conditionally loaded PDF procedure and updated usage documentation. The approved scope revision below lists the exact files.

## Done
Existing workflow retained; each requested PDF requirement enforced by a checkable gate; skill validated and independently audited.

## Unknowns
None currently. Repository packaging verified; no rules file exists; revised plan explicitly approved.

## Outcome
Implemented and verified optional PDF mode in the existing workflow. Frontmatter, baseline preservation, local references, metadata, six scenario checks and both staged audit passes succeeded. No remaining issues. No PDF was requested for this skill-edit task; no commit or push performed.

## Superseded initial proposal (history)
- Add skills/workflow-pdf/SKILL.md, PDF-DELIVERABLE.md, TASK-FOLDER.md, AUDIT.md, CHATGPT-PROMPTS.md, agents/openai.yaml from the reviewed draft.
- Update .claude-plugin/plugin.json to register ./skills/workflow-pdf, preserving the release version.
- Update README.md with installation, invocation, owner terminology confirmation, rendering requirements and PDF review gates.
- Update CHANGELOG.md with an Unreleased addition.
- Do not modify skills/workflow or release, commit, push, or install a duplicate local skill.

## Rules
No AGENTS.md or CLAUDE.md exists. Offer an optional AGENTS.md in batch 1; recommend proceeding without adding unrelated repository policy.

## Verification
Skill validator, exact baseline-body retention, local-reference byte equality, and local Markdown reference closure passed. Independent draft review passed with no blocking defects. Final validation and staged cold audit follow approved implementation.

## Historical draft (removed after integration)
Draft entrypoint: draft/workflow-pdf/SKILL.md
PDF process: draft/workflow-pdf/PDF-DELIVERABLE.md

## Initial gate (resolved by approved revision)
Workflow batch 1 explicit go required before any write outside this task folder. Owner audience and terminology confirmation applies to future PDF tasks, not to prose for this skill creation request.

## Approved scope revision — 2026-10-07
The owner chose optional PDF mode in the existing workflow and explicitly said "do that". This supersedes the separate-skill proposal. Keep one authoritative development workflow; load PDF-DELIVERABLE.md only when a PDF is requested. No workflow-pdf skill or plugin registration is added.

Approved implementation files: skills/workflow/SKILL.md, skills/workflow/PDF-DELIVERABLE.md, skills/workflow/agents/openai.yaml, README.md, CHANGELOG.md. Plugin manifests remain unchanged. No new repository rules file. Task records stay in this claimed folder; superseded draft files were removed after integration.

Acceptance: ordinary workflow behavior preserved; PDF mode adds owner-confirmed audience/terminology, reader-focused evidence and writing, local polished rendering, all three validation passes, and final-version proof. Validate link closure/frontmatter, inspect a normal task and PDF scenario, verify all requirements, and cold-audit staged changes. Do not commit or push.

## Interim draft disposition (superseded by final disposition)
The initial draft is preserved under superseded-proposal as history, with its entrypoint renamed SUPERSEDED-DRAFT.md; it is not a second installed or maintained skill. The approved implementation lives solely in skills/workflow.

## Final draft disposition
Superseded snapshot files were removed individually after integration. The task records preserve proposal/review history without duplicating the skill instructions. Maintain only skills/workflow.
