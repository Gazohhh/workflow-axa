# Check a fix

Use this when a commit is said to fix the report. The commit owns the fix: check it, never change it and never offer a change of your own.

## Name the two commits

- The fix commit: the one the report or the person names. A claim without a commit is not a fix to check; report **Blocked** and ask which commit.
- The commit before the fix: the fix commit's first parent (`<fix>^`), unless the person names another.

Record both, and the backend, account and data both runs use. Both runs use the same backend and the same data; reset the data between them the way the feature map says.

## Run an older commit

The developer's working copy is never touched: no checkout, stash or reset there.

1. Before anything else, run `git worktree list`. A worktree left in `<artifacts>/worktrees/` is removed only when it belongs to an earlier run of this job: a run record (the task's FINDINGS or `<artifacts>/worktrees.md`) names that exact worktree path and commit as made by this job, and no dev server or process is using it (its port is free, no Playwright run is open on it), and `git -C <worktree> status --short --untracked-files=all --ignored` shows nothing besides the dependency link and the build output this job's run record names (an ignored file of anyone else's, such as a `.env.local`, keeps the worktree); then it is removed as step 5 says, link first. A worktree without that proof stays, never forced, and you tell the developer.
2. First check, in the developer's checkout, that `git check-ignore -q <artifacts>/` succeeds (trailing slash included); when it does not, stop and ask the owner for an ignore rule before anything is written there. Then make a separate worktree inside the app's ignored artifacts folder, in its `worktrees/` subfolder so a worktree never takes a run's folder name: `git worktree add --detach <artifacts>/worktrees/<name> <commit>`. Right after it is made, add a line with its exact path, its commit and the run's name to `<artifacts>/worktrees.md` (the artifacts folder itself, never a run folder: the guard claims each run folder fresh), as made by this job; that line is what step 1 of a later run looks for.
3. When every dependency manifest and lockfile (for example `package.json` with `package-lock.json`, `yarn.lock` or `pnpm-lock.yaml`, and those of any workspace package) is byte-identical in that commit and the developer's checkout, and the checkout's installed dependencies match its lockfile, and no installed package is a link into the repository itself (a workspace package, a `file:` or `link:` dependency: check that nothing under the checkout's `node_modules` is a symbolic link or junction pointing inside the checkout but outside its `node_modules` (links that stay inside `node_modules`, such as `.bin`, are normal); through a linked `node_modules` such a package would load from the developer's checkout, not from the commit), link the checkout's installed dependencies into the worktree instead of installing: a directory link (`ln -s` on Linux and macOS; on Windows a junction, `cmd /c mklink /J "<worktree>\node_modules" "<checkout>\node_modules"`). When it differs, stop and ask the developer to install; never install on your own.
4. Run every verify command (Doctor, journeys, the driver) from the developer's checkout root, as for any run; only the dev server starts from the worktree, and Doctor reads the worktree's dev-server settings as files. Run the first part of the verify skill's Doctor for the worktree before it starts: each commit has its own dev-server settings (a proxy target or a server-side backend may differ), so one commit's Doctor never stands for the other. Then start the app from the worktree with the verify skill's Launch, on the verify skill's port and backend. The port must be free first: stop the server of the other commit and check that nothing listens on the port (the verify skill's Launch check) before starting this one, so the run never checks a server left from the other checkout. Then run Doctor's second part on this commit's server before measuring it. A failure in either part is **Blocked** for that commit. The verify skill's settings, guard and the run's journey still come from the developer's checkout and the run's artifacts folder.
5. Afterwards, the dependency link is removed as a link, never through it:
   - Windows: `cmd /c rmdir "<worktree>\node_modules"` (removes the junction only). Never `Remove-Item` on a junction: Windows PowerShell asks for confirmation, and the `-Recurse` retry deletes the developer's installed dependencies through it.
   - Linux and macOS: `rm "<worktree>/node_modules"` (no `-r`).
   Then check the developer's installed dependencies are still there, the worktree holds no link, and `git -C <worktree> status --short --untracked-files=all --ignored` shows nothing besides the build output this run made and recorded (anything else, such as an ignored `.env.local` someone added, keeps the worktree: stop and tell the developer), and run `git worktree remove <artifacts>/worktrees/<name>`. When Git refuses because of build output, and only after that check, run `git worktree remove --force <artifacts>/worktrees/<name>`. Never delete a worktree folder yourself.

## Measure the commit before the fix

Run the report's steps on it as SKILL.md step 3 says: explore once to find the path, then the proof runs on both commits with the same journey. The broken end state must show twice, with video, screenshots and the state check. If it does not, there is no baseline: report **Fix not confirmed** ("no baseline") with what was seen; never claim the fix works.

## Measure the fix commit

Run the same steps on the fix commit, twice, with the same backend and data. Here the second look checks the captures for the correct end state, and the outcome comes only from this file's Report section, never Could not reproduce. SKILL.md step 3's `network.log` rule applies to every run on both commits: a run with a `blocked`, `failed` or `escaped` line for an origin the path needs does not count, and the outcome is **Blocked**, never Fix confirmed or Fix not confirmed. The fix commit runs in its own worktree as "Run an older commit" says, unless it is the developer's current commit and `git status --short --untracked-files=all` shows no change at all; an uncommitted edit must never be credited to the fix. On the developer's checkout, do what step 4 of "Run an older commit" does for a worktree: stop the baseline's server, check nothing listens on the port, run Doctor's first part, start the app with Launch, then Doctor's second part. The broken end state must be gone and the correct end state must show, both times, with the same captures and the same state check.

## Report

- **Fix confirmed**: symptom twice on the commit before the fix, correct end state twice on the fix commit; both state check values given.
- **Fix not confirmed**: the symptom is still there on the fix commit, or the fix commit shows neither end state (another wrong state: describe it), its two runs differ (for example one correct and one stuck loading), or there was no baseline; say which, with what each run showed and the captures. Fix confirmed needs the correct end state on both fix runs.
- **Blocked**: a commit does not start or build against today's backend, the screen is not mapped, or a precondition is missing; say which.
