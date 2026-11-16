"""Pin, copy and re-check the working tree an interrogation probes.

usage:
  python -X utf8 -I snapshot.py id    <repo>                 print the snapshot id
  python -X utf8 -I snapshot.py copy  <repo> <dest> <id>     make a new isolated copy and verify it has that id
  python -X utf8 -I snapshot.py fill  <repo> <dest> <id>     bring the snapshot into an existing disposable checkout
  python -X utf8 -I snapshot.py check <repo> <id>            exit 0 when the working tree still has that id, 3 when not

The id is "<HEAD sha>:<sha256>". The sha256 runs over one line per path, sorted by the path's UTF-8 bytes:
"<path>\\t<sha256 of the bytes on disk>\\n", or "<path>\\tlink:<target>\\n" for a symbolic link, or
"<path>\\tdeleted\\n". Paths are POSIX-style and relative to the repository root. The paths are every tracked and
untracked, not-ignored file (`git ls-files -co --exclude-standard`) plus every path HEAD has that the working tree
lacks. The bytes are the working tree's as they are on disk, so line-ending settings don't change the id.

`copy` writes nothing into the target's .git: it runs `git clone --shared --no-checkout <repo> <dest>`, gives the
copy the target's core.autocrlf, core.eol and core.symlinks, checks out HEAD detached, then mirrors the snapshot.
It refuses an existing <dest>.

`fill` is for a checkout the host made for this run (a worktree an isolated agent got). It refuses the target
itself, a folder that contains the target, and a checkout whose HEAD differs from the target's. It then mirrors the
snapshot: files the snapshot doesn't list are removed from <dest>'s own listing, and every listed file is written.

Mirroring writes only inside <dest> and never through a symbolic link: a link (or a Windows junction) that sits where
the snapshot needs a folder or a file is removed, not followed. File bytes and the executable bit are copied. Both commands print the
copy's id and exit 3 when it differs from <id>.
"""
from __future__ import annotations

import hashlib
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path


def git(repo: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, encoding="utf-8")
    if done.returncode != 0:
        raise SystemExit(f"snapshot.py: git {' '.join(args)} failed: {done.stderr.strip()}")
    return done.stdout


def listed(repo: Path) -> tuple[list[str], list[str]]:
    present = [p for p in git(repo, "ls-files", "-z", "-co", "--exclude-standard").split("\0") if p]
    head = [p for p in git(repo, "ls-tree", "-r", "-z", "--name-only", "HEAD").split("\0") if p]
    on_disk = {p for p in present if os.path.lexists(repo / p)}
    deleted = sorted({p for p in head + present if p not in on_disk})
    return sorted(on_disk), deleted


def entry(repo: Path, path: str) -> str:
    full = repo / path
    if full.is_symlink():
        return f"link:{os.readlink(full)}"
    return hashlib.sha256(full.read_bytes()).hexdigest()


def snapshot_id(repo: Path) -> str:
    present, deleted = listed(repo)
    lines = [(p, entry(repo, p)) for p in present] + [(p, "deleted") for p in deleted]
    lines.sort(key=lambda item: item[0].encode("utf-8"))
    digest = hashlib.sha256("".join(f"{p}\t{v}\n" for p, v in lines).encode("utf-8")).hexdigest()
    return f"{git(repo, 'rev-parse', 'HEAD').strip()}:{digest}"


def is_link(path: Path) -> bool:
    """A symbolic link, or a Windows junction (which Python doesn't report as a link)."""
    return path.is_symlink() or bool(getattr(os.path, "isjunction", lambda _: False)(path))


def remove(path: Path) -> None:
    """Remove a file, a link or a folder at path itself; a link or junction is removed, never followed."""
    if is_link(path):
        os.rmdir(path) if path.is_dir() and not path.is_symlink() else path.unlink()
    elif path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def real_folder(dest: Path, rel: str) -> Path | None:
    """The folder that holds rel inside dest, made of real folders only: a link or a file on the way is removed and
    replaced by a folder. None when rel would leave dest."""
    current = dest
    for part in Path(rel).parts[:-1]:
        if part in ("..", ""):
            return None
        current = current / part
        if is_link(current) or (current.exists() and not current.is_dir()):
            remove(current)
        if not current.exists():
            current.mkdir()
    return current


def inside(dest: Path, folder: Path) -> bool:
    real, top = os.path.realpath(folder), os.path.realpath(dest)
    return real == top or real.startswith(top + os.sep)


def mirror(repo: Path, dest: Path) -> None:
    present, deleted = listed(repo)
    keep = set(present)
    own, _ = listed(dest)
    for rel in sorted(set(own) - keep, reverse=True) + deleted:
        folder = real_folder_existing(dest, rel)
        if folder is not None and os.path.lexists(folder / Path(rel).name):
            remove(folder / Path(rel).name)
    for rel in present:
        folder = real_folder(dest, rel)
        if folder is None or not inside(dest, folder):
            raise SystemExit(f"snapshot.py: {rel} would be written outside {dest}; stopped")
        source, target = repo / rel, folder / Path(rel).name
        if os.path.lexists(target):
            remove(target)
        if source.is_symlink():
            os.symlink(os.readlink(source), target)
        else:
            shutil.copyfile(source, target)
            if os.stat(source).st_mode & stat.S_IXUSR:
                os.chmod(target, os.stat(target).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def real_folder_existing(dest: Path, rel: str) -> Path | None:
    """The folder that holds rel when every step is a real folder inside dest; None otherwise (nothing to remove
    there without following a link)."""
    current = dest
    for part in Path(rel).parts[:-1]:
        current = current / part
        if part in ("..", "") or is_link(current) or not current.is_dir():
            return None
    return current


def finish(dest: Path, expected: str) -> int:
    actual = snapshot_id(dest)
    print(actual)
    if actual != expected:
        print(f"snapshot.py: the copy has {actual}, not {expected}; it isn't the target", file=sys.stderr)
        return 3
    return 0


def copy(repo: Path, dest: Path, expected: str) -> int:
    if os.path.lexists(dest):
        raise SystemExit(f"snapshot.py: {dest} already exists; choose a new owned path (or `fill` a host checkout)")
    head = git(repo, "rev-parse", "HEAD").strip()
    done = subprocess.run(["git", "clone", "--quiet", "--shared", "--no-checkout", str(repo), str(dest)],
                          capture_output=True, text=True, encoding="utf-8")
    if done.returncode != 0:
        raise SystemExit(f"snapshot.py: git clone failed: {done.stderr.strip()}")
    for key in ("core.autocrlf", "core.eol", "core.symlinks"):
        value = subprocess.run(["git", "-C", str(repo), "config", "--get", key], capture_output=True, text=True)
        if value.returncode == 0 and value.stdout.strip():
            git(dest, "config", key, value.stdout.strip())
    git(dest, "checkout", "--quiet", "--detach", head)
    mirror(repo, dest)
    return finish(dest, expected)


def fill(repo: Path, dest: Path, expected: str) -> int:
    real_repo, real_dest = os.path.realpath(repo), os.path.realpath(dest)
    if real_dest == real_repo or real_repo.startswith(real_dest + os.sep):
        raise SystemExit("snapshot.py: fill needs a separate disposable checkout, not the target or a folder above it")
    if not dest.is_dir() or git(dest, "rev-parse", "--show-toplevel").strip() == "":
        raise SystemExit(f"snapshot.py: {dest} is not a Git checkout")
    if os.path.realpath(git(dest, "rev-parse", "--show-toplevel").strip()) != real_dest:
        raise SystemExit(f"snapshot.py: {dest} is not the top folder of its checkout")
    if real_dest.startswith(real_repo + os.sep):
        ignored = subprocess.run(["git", "-C", str(repo), "check-ignore", "-q", "--", os.path.relpath(real_dest, real_repo)],
                                 capture_output=True)
        if ignored.returncode != 0:
            raise SystemExit("snapshot.py: the checkout sits inside the target and Git doesn't ignore it, so it would "
                             "change the target's own snapshot; ignore that folder or use a checkout outside the target")
    if git(dest, "rev-parse", "HEAD").strip() != git(repo, "rev-parse", "HEAD").strip():
        raise SystemExit("snapshot.py: the checkout's HEAD differs from the target's; check out the target's HEAD first")
    mirror(repo, dest)
    return finish(dest, expected)


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[0] == "id":
        print(snapshot_id(Path(argv[1]).resolve()))
        return 0
    if len(argv) == 4 and argv[0] in ("copy", "fill"):
        command = copy if argv[0] == "copy" else fill
        return command(Path(argv[1]).resolve(), Path(os.path.abspath(argv[2])), argv[3])
    if len(argv) == 3 and argv[0] == "check":
        actual = snapshot_id(Path(argv[1]).resolve())
        print(actual)
        return 0 if actual == argv[2] else 3
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
