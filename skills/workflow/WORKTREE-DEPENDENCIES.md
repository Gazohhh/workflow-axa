# Worktree dependencies

Read this when a fresh worktree has no installed dependencies (no `node_modules`, `vendor`). [TASK-FOLDER.md](TASK-FOLDER.md) "Find the task before creating one" sends you here.

Never install on your own. Ask with the plan: the owner installs in the worktree, or you link the main checkout's install at the same lockfile. In a workspace (monorepo) install the linked packages point into the main checkout, so prefer the owner's install there. Remove a link as a link (`rmdir` on Windows, `rm` without `-r`); a recursive delete through it deletes the main checkout's files.
