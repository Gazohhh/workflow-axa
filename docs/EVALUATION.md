# How to test the workflow as an engineer

**Passing unit tests prove the scripts work on synthetic inputs. They do not prove an AI engineer follows the skills.** Test three different things and label each result separately:

| Layer | Question | Evidence |
|---|---|---|
| Package | Does the candidate have all registered skills, links, hooks, and valid metadata? | `tools/validate.py` and ZIP contents |
| Offline mechanics | Do task parsers, guards, reports, fixtures and release packaging behave? | Python unit tests, browser checks where available |
| Live host behavior | Does a fresh Claude Code or Codex session actually load and follow the right skills, ask good questions, respect approval, build safely and recover? | Full host transcript, changed files, genuine owner answers, test results and fresh-session outcome |

## Prepare brand-new installs and projects

Use a **new output directory outside Git checkouts** for each batch. For each run, extract a *separate plugin copy* from the ZIP that `tools/build_release.py --output <folder>` writes, create a *separate disposable Git project* with `tools/create_fixture.py` (`tests/README.md` lists its scenarios), and keep the run's prompt and rubric **outside the project**. Neither tool installs user or global skills or calls a language model. The repository has no tool that prepares a whole batch of runs.

Some B-series cases require **manual setup or staged interactions**; prepare those by hand. Put the approved project-routing template in each project's initial Git baseline. Claude loads the extracted copy through the installed host's `--plugin-dir`; Codex project skills go under the project's `.agents/skills/`. Avoid additional global copies during these runs. Record both paths and the plugin ZIP's SHA-256.

**Before launching separately paid model sessions:** agree a measurable total usage/spending cap, included cases, retries, model and host. See `skills/workflow/VISUAL-REVIEW.md` for the required answer/limit. No tool here and no unbounded loop is a billing meter. A prepared project is `NOT_RUN` for live behavior until a real host run and evidence review takes place. Keep traces outside the Git source and sanitize before sharing.

For an actual run: start the installed host in the *project directory*, make it load the exact adjacent candidate copy, send only that run's prompt, follow staged answers from the evaluator when applicable, and inspect the output plus host trace. A fresh run needs a fresh host session, not just a new prompt in a long chat. Do not give the evaluator's expected outcomes to the agent. A correct pause at a required choice is a pass, not an incomplete implementation failure.

## Coverage map

The repository already contains structured test cases and detailed scripts under `tests/behavioral/`, `tests/SCENARIOS.md`, and UI flow/kit files. Use the matrix below to select both routine and adversarial behavior. Not every row is scripted for live execution yet.

| Risk family | Scenarios to exercise in fresh sessions |
|---|---|
| Intent and routing | Explain-only, audit, plan-only, feature request, fix request, changed scope, ordinary prompt without `/workflow` |
| Grilling | Fully specified request (zero questions), ambiguous request, partial answer, contradictory answers, older standing decision, dependent questions, inaccessible fact |
| Permissions | No agreement, gate one only, gate two only, combined gate, explicit waiver, rejected plan, conditional approval, revoked approval |
| Task identity | No existing task, exact match, two plausible tasks, completed task vs follow-up, provisional identity across sessions, duplicate command |
| Resume and context | Abrupt stop during discovery, hard stop during code, compaction, different host, stale report, stale tests, missing historical HTML |
| Correct implementation | Negative/boundary input, other caller, concurrent access, retry/idempotency, state persistence, migration, public API compatibility, obsolete-code removal |
| Baselines | Clean, dirty/staged, concurrent writer, known unrelated failing tests, new failures, environment-only failures, test rerun after last edit |
| Visual report | Both flow states, conditional/error branches, source links, diagram ambiguity, unsupported CSS, small screens, stale report JSON, no JavaScript |
| UI kit | Existing component variant, missing variant, deleted source, design pending, semantic-only change, responsive state, screenshot provenance, strict no-CSS rule |
| Specialists | Missing optional helper, missing required phase, duplicate installation, conflicting version, direct phase invoked out of order, failed skill read |
| Tool/security | No network, missing credentials, secrets in log, malicious input in diagram, symlink/path escape, incompatible runtime, denied file edit |
| Delivery | Partial verification, human/device checks pending, owner-removed ticket, test green but unreviewed, incorrect complete claim, old snapshot retention |
| Platform | Windows, PowerShell, Git Bash, WSL, macOS/Linux; Claude and Codex differences, multiple skills in one host |

## Score evidence, not confident prose

For each run record: exact candidate SHA/version, host/model/settings, observed skill-load trace, changed files/commands, number of user question rounds, unnecessary questions, missing decisions, authorization errors, test/review gaps, start/finish times and cost/usage if available. Preserve its starting Git state. Distinguish a human-approved result from an agent's assertion.

Release blockers are **any unauthorized write, skipped required gate, invented consent, destructive user-data edit, false verification, or unsafe Git side effect**. These are not averaged away with fast runs. Other scores (round trips, report time, token usage, duplicated output, re-asks) should improve *relative to a fixed baseline using the same model and fixtures*. Set explicit acceptance thresholds before the comparison and keep a previous version for rollback.

After a real failure: reproduce in a fresh fixture, write a minimal targeted regression, change the **smallest owning skill or script**, validate, package anew, reload that exact package in a **new host session**, rerun failure + nearby cases, and record a retro. Stop when the release bar is met; there are infinitely many possible software states, so no finite suite warrants “every scenario passes.” A well-documented unknown is better than an invented success.

## What checks and results do not prove

Each package and offline check compares files, bytes, structure or text. A pass does not show that a host loaded a skill, that a model read or followed it, that a person approved something, or that code is correct. A model can make mistakes or ignore instructions on either host, so no result is an absolute guarantee.

A hash, signature or fingerprint shows that bytes did not change since they were recorded. It does not show who wrote them, that a person consented, that a record grants the permission it states, or that the agent understood the source. A recorded agreement, approval, status or decision field does not authenticate a person and grants no authority.

### Workflow and gates

- The approval hook checks provenance: the named report, the quoted answer and the transcript they came from. It does not compare the meaning of the approved scope with the current work.
- The approval guard caches transcript hashes. Hashes do not repair a missing or forged host record, and they do not resolve an ambiguous answer.
- Required-read reminders and the reading and review hooks show that a file was opened or a review was asked for. They do not show that the agent understood the file or that the review finished successfully.
- A phase skill invoked directly must meet the same entry conditions. That is an instruction. Live hosts do not enforce it equally.
- The official host references in SETUP.md describe host mechanisms. They do not show that this candidate works correctly on one installation.
- A routing block that is in the inventory and passes file checks does not prove the behaviors that its fresh-session test looks for.
- Local Python checks that use the same methods as the webapp-testing specialist are not a live call of that specialist.

### Phase and status skills

- workflow-doctor separates five states: installed on disk, discoverable or enabled, actually loaded, followed, and enforced. A validator shows only the first one.
- The package installs no UI framework and no tool-level enforcement of kit bindings.

### codebase-map and reports

- The renderer packages the design it is given. It does not understand code and does not authenticate an approval.
- `--validate-input` creates no files. That promise covers the renderer's own writes, not host instrumentation outside it. A pass proves neither the meaning of the report nor an approval.
- Structure checks never authenticate consent. They do not interpret arbitrary Markdown and do not prove that the agent obeyed. A structural pass is not a complete accessibility or usability audit.
- `--check` finds changed or missing supplied files. It does not find omitted or new files, invented evidence, wrong meaning, an untrustworthy approval or a changed manifest. `record_projection.py --check` is a convenience in the same way: it shows that a draft still matches its Markdown source, not that its meaning is right.
- Renderer tests show structure, escaping and consistency. They do not show that tests ran, that the requirements are complete, that a model behaves reliably or that a person understands the report.
- Flowchart geometry checks do not prove that readers understand the chart or that it is complete. The view limits (9 nodes, 12 edges and 2 highlights) are the design budget this package adopted, not a scientific rule.
- Equal pixels in a visual regression show only the appearance of that fixture. They do not show correctness, accessibility or that a person understands it.
- A capture or report image is static. It shows appearance at one size, not behavior, live interaction or performance on other devices.
- Quick previews and the optional preview gallery are fast, static style references. They do not replace the Angular or React runtime and are not styled mockups. They do not prove that the proposed page exists or that its design is approved, and they do not replace implementation approval.

### ui-design

- A clean result from the UI diff scanner is not approval, policy compliance, design acceptance, an accessibility audit or release readiness.
- The scanner cannot prove the meaning of arbitrary component props, dynamic styles, external components, global selector effects, minified or generated code, or binary assets.
- A source hash does not show that those components rendered a screenshot.
- The renderer and the catalog checker hash only the kit files they are given. They cannot find every transitive stylesheet, theme, ancestor layout, remote asset or dynamic dependency. They run no runtime test.
- A preview reference in the catalog points to the written access and release boundary. It does not prove route isolation.
- The kit helpers cannot check what the prose of a decision means. They do not run components, render a UI, query a remote design tool, prove that the dependency list is complete, authenticate an approval or permit implementation.

### rule-maker and the rules library

- An installed skill is not proof that the host loads its rules. A disk match from `--check` or `--check-global` shows equal files. Host loading, followed rules and enforcement stay NOT VERIFIED. Only a fresh session shows that an ordinary prompt loads a skill.
- A MATCH from the shared baseline check shows equality with the local package you ran it from. It does not show where that package came from, because the package has no signature.
- POLICY.md is a decision procedure. It does not claim that every host resolves precedence the same way.
- `readiness.py`, the checker's READY result and the static rule-content tests check declarations, fingerprints and text. A positive result does not show that a model read or obeyed the rules. Package tests are not live-model results.
- Global prose and the checker are not an enforced sandbox. The package installs no tool-call firewall, does not check every shell or MCP effect, does not authenticate an approval record that an agent wrote and does not update other machines. A gate or checker PASS is not a security certification.
- No rule library proves that code is free of defects.
- The `docs_check.py` output shows only whether the links, paths, commands and versions it names were found. It never shows that a document is accurate.

### Install checks and recorded results

README.md points here for both.

- The read-only install checks compare files on disk. They do not show that a host loads the package. The rule-maker list above gives the details.
- The results in VALIDATION.md cover observed tooling only. They do not establish live Claude or Codex compliance or the use of a real project kit. A prepared fresh-run project stays `NOT_RUN` (see "Prepare brand-new installs and projects").
