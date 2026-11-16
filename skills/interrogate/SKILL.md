---
name: interrogate
description: "Ask adversaries to show a concrete failure of a plan or a change, then report reproduced failures, unverified concerns and untested surfaces. Only the user starts it; it reports and changes nothing."
disable-model-invocation: true
---

# Interrogate

The question: **can an adversary show a concrete failure of this plan or change?** Grilling asks the user about decisions, plan-review judges scope, and code-review checks standards and spec. This skill tries to break the thing.

Only the user starts it (`/interrogate <plan file | diff>`). A project may list risk triggers; the workflow then recommends this skill and never runs it unasked.

## 1. Restate and pin the target

Open with one sentence in your own words: what the target is meant to do. Then pin the target.

- **A plan:** the file path and its sha256.
- **A diff:** the snapshot of the working tree as it runs. Get its id with `python -X utf8 -I scripts/snapshot.py id <repo>` (the script sits in this skill's folder, so give its full path when you run it from the repository); never compute it by hand. The id covers tracked and untracked files (ignored ones excluded) and deletions, byte for byte as they are on disk. Probes run the working tree. When `git diff --cached` shows staged content that the working tree has since changed, say so in the report.

## 2. Two adversaries

Brief two adversaries with the target, the restated intent and the budget. Use a different model through T3 `delegate_task` when it is available; otherwise use fresh subagents of the same model. Label each one ("cross-model" or "same model, fresh context"). Each one looks for one concrete failure at a time: an input, a sequence, a state or an environment that breaks the stated intent.

**Budget:** 8 probe commands per adversary, unless the user sets another number. An adversary that runs out reports what it would run next.

**Where probes run.** A probe follows the standing diagnostic allowance in `../rule-maker/rules/OPERATIONS.md`: an owned disposable location, an isolated target, synthetic or authorised inputs, and no protected operation, install, external change, secret or persistent configuration change. A probe that needs more is reported as the named experiment instead of run.

A read-only probe may run on the target. A probe that writes runs in an isolated copy:

1. Use the host's isolation when it requires or offers it (an agent with worktree isolation, a `delegate_task` worktree). That checkout was made for this run, so it is disposable: bring the snapshot into it with `snapshot.py fill <repo> <that checkout> <snapshot id>`. It refuses the target itself, a folder above it and a checkout on another HEAD, and it replaces the checkout's own leftovers.
2. Otherwise run `snapshot.py copy <repo> <new owned .artifacts path> <snapshot id>`. It clones without writing into the target's `.git` and checks out HEAD.
3. Both mirror the working tree byte for byte (line-ending settings can't change it) and never write through a link or junction. Both print the copy's id and exit 3 when it differs from the snapshot id. When it does, stop: the copy isn't the target.

## 3. Confirm each failure

A failure counts as **reproduced** only when an agent other than its finder reruns it on a fresh, pristine copy of the same snapshot (hash checked) and sees the same result. Record the command, the expected result and the actual result.

## 4. Report

Before you report, run `snapshot.py check <repo> <snapshot id>` on the live target (for a plan, compare its sha256 again). If it changed, mark the whole report **stale** and name the snapshot it covers; never present it as current.

Report three lists:

1. **Reproduced failures:** command, expected, actual, and who confirmed it.
2. **Unverified concerns:** each one with the experiment or the decision that would settle it.
3. **Untested surfaces:** what no probe reached.

This skill reports only: no fixes, no offers, no edits to the target. In a task, add one line to the current task's FINDINGS through `record.py`: the snapshot id, the counts per list and where the full report is. Task records stay writable while an offer is pending; a record write never changes which task the session is on.

Remove the copies you created once the report is written; a host-managed copy goes through its owner's cleanup. Keep a copy only as evidence for a reproduced failure, and record its path, the reason and the removal condition in FINDINGS.
