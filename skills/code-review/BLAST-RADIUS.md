# Blast radius

Write the impact report for a person, as `../workflow/WRITING.md` says.

Find what a change breaks outside itself, and prove the facts its safety rests on by running code. A writeup that sounds right is worth nothing on its own: it reads as convincing whether or not it is true.

Callers are the input, not the result. Anyone can list them with a search. The job is the breakage a search does not show.

This file is read in three places: step 4b of the code review in [SKILL.md](SKILL.md) on a real diff, a planning pass before the diff exists, and a direct question such as "what could this break?". Each use reports only. It edits no project file and no task record; probes and scripts run only where Probes allows. Paths in this file are relative to its folder, `skills/code-review/`; from the repository root, write them from there (`skills/interrogate/scripts/snapshot.py`).

## Steps

1. **Read the change.** The diff, the symbols it adds, changes and deletes, and what it now does differently, including what the diff does not spell out.
2. **Find the safety facts.** Most changes that look risky are safe because of one fact, such as "this call only drops cache entries that nothing reads". Put first the one or two facts that carry the most risk; there is no cap when more facts are material. When a fact holds, many risks clear at once, so spend the time here, not on a long list of maybes.
3. **Look where grep stops** (the list below).
4. **Weigh each risk.** Give it a real likelihood and a real cost. Cite a real `file:line`. A search that finds nothing is an answer too; say what you searched. Never invent a caller or an API.
5. **Prove the facts** as high on the evidence ladder as is cheap (step 5 is the strongest), and say which step it reached.

## Where grep stops

- The library you call: read its source at the pinned version, and check for a local patch.
- When things run: async order, timers, teardown and unmount, retries, shutdown.
- Data that leaves the code: a JSON or API shape, a DB column, a wire or file format, saved data, a cache key.
- Readers in another language or another repository that read the same bytes.
- A config key, an environment variable or a feature flag.
- Text that a tool, test or validator parses: asserted phrases, section headings, counts, links.
- Code two or three hops downstream of the first caller.

## Evidence ladder

For each safety fact, say which step it reached, from weakest (1) to strongest (5):

1. Stated. Worth nothing alone.
2. Pointed at: a real `file:line`, or the library's own source.
3. Walked: the failure traced step by step, and it does not reach.
4. Ran: a test or script that calls the real code and fails loudly if the fact is wrong. Usually one small script that imports what the project ships and calls the function in question.
5. Reproduced in an isolated running instance of the application.

## Probes

A probe follows the standing diagnostic allowance in `../rule-maker/rules/OPERATIONS.md`: what may run before approval, where its output goes (an owned disposable folder), and what stays forbidden. A probe that changes project files runs in an isolated copy: pin the working tree with `python -X utf8 -I ../interrogate/scripts/snapshot.py id <repo>`, then make and verify the copy with its `copy` command, as `../interrogate/SKILL.md` steps 1 and 2 describe. When a probe is not possible or not allowed, mark the fact unproven and name the experiment that would prove it. When the change spans several modules or owners, recommend that the user run `/interrogate`, the adversarial check in `../interrogate/SKILL.md`; never start it yourself.

## Report

- **What it does**: what changed, including the part that is not obvious.
- **Safety facts**: each fact, the ladder step it reached and its proof (the command and what it printed), or "unproven" with the experiment.
- **Risks**: how it breaks, `file:line`, likelihood, cost, and the check that would catch it.
- **Cleared**: what you checked and why it is fine.
- **Before you merge**: the cheapest test or reproduction that catches the real bug, including any script you wrote.

Risks may be "none": nothing outside the change can break. That result counts only with a boundary trace: what the change reads and writes, and why nothing outside it reads that. "It is local" without the trace is not a result.

## Planning, with no diff yet

There is nothing to run yet, so there are no probes. List the safety assumptions the planned change rests on, look where grep stops for each, and write the check that could falsify each assumption. These checks become ticket checks. Step 4b of the code review later proves them against the diff and reopens any assumption that the implementation or new evidence changes or contradicts.

## Asked directly

A question such as "what could renaming this column break?" gets the same report. With a diff, follow the steps above. With only a symbol or an idea and no diff, use the planning form, and let "Before you merge" name the check to run once the change exists. It is an inspection: no task records, no edits.
