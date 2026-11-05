#!/usr/bin/env python3
"""Record the inputs a baseline ran on, and check whether it may be reused. Read-only on the repository.

usage: python -X utf8 -I baseline_state.py record "<command>" <record-file>
       python -X utf8 -I baseline_state.py check  "<command>" <record-file>

The inputs are the exact check command, working directory, commit, a hash of the local diff (staged, unstaged and untracked) and the
environment (OS, Python, and node/npm/php versions when present). `check` prints REUSE and exits 0 only when all
match; otherwise it names what changed and exits 1, so the check runs again (audit A9). Exit 2 on bad input.
"""
from __future__ import annotations

import hashlib
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


class Blocked(Exception):
    pass


def git(top: Path | None, *args: str) -> bytes:
    """Run git (in the repository top folder when known); a failure is BLOCKED, never an empty answer."""
    try:
        done = subprocess.run(['git', *(['-C', str(top)] if top else []), *args], capture_output=True, check=False)
    except OSError as exc:
        raise Blocked(f'git cannot run ({exc.__class__.__name__})') from exc
    if done.returncode != 0:
        raise Blocked('git failed: ' + done.stderr.decode('utf-8', 'replace').strip().splitlines()[0]
                      if done.stderr.strip() else f'git {args[0]} failed')
    return done.stdout


def tool_version(name: str) -> str:
    path = shutil.which(name)
    if not path:
        return ''
    try:
        out = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return 'unknown'
    return (out.stdout or out.stderr).strip().splitlines()[0] if (out.stdout or out.stderr).strip() else 'unknown'


def state(command: str, record: Path) -> dict[str, str]:
    """Inputs of the check for the whole repository, from any subfolder (review of V10: a subfolder saw only itself,
    and untracked files counted by name only)."""
    top = Path(git(None, 'rev-parse', '--show-toplevel').decode().strip())
    # Task records, check output and the record file change all the time and are not inputs of the check.
    skip = [':(top,exclude)docs/plans', ':(top,exclude).artifacts']
    try:
        skip.append(':(top,exclude)' + record.resolve().relative_to(top.resolve()).as_posix())
    except ValueError:
        pass
    digest = hashlib.sha256(git(top, 'diff', 'HEAD', '--binary', '--', ':/', *skip))
    for name in sorted(git(top, 'ls-files', '--others', '--exclude-standard', '-z', '--', ':/', *skip).split(b'\0')):
        if name:
            digest.update(b'\0' + name + b'\0')
            try:
                digest.update((top / name.decode('utf-8', 'surrogateescape')).read_bytes())
            except OSError:
                digest.update(b'<unreadable>')
    return {
        'command': command,
        'cwd': str(Path.cwd().resolve()),
        'commit': git(top, 'rev-parse', 'HEAD').decode().strip(),
        'diff': digest.hexdigest(),
        'environment': json.dumps({'os': platform.platform(), 'python': platform.python_version(),
                                   'node': tool_version('node'), 'npm': tool_version('npm'),
                                   'php': tool_version('php')}, sort_keys=True),
    }


def main(argv: list[str]) -> int:
    if len(argv) != 4 or argv[1] not in ('record', 'check'):
        print(__doc__)
        return 2
    mode, command, record = argv[1], argv[2], Path(argv[3])
    try:
        now = state(command, record)
    except Blocked as exc:
        print(f'BLOCKED: {exc}; a baseline needs a git repository')
        return 2
    if mode == 'record':
        try:
            record.write_bytes((json.dumps(now, indent=2) + '\n').encode('utf-8'))
        except OSError as exc:
            print(f'BLOCKED: cannot write {record} ({exc.__class__.__name__})')
            return 2
        print(f'RECORDED: {record}')
        return 0
    try:
        before = json.loads(record.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        print(f'BLOCKED: cannot read baseline record {record} ({exc.__class__.__name__}); run the baseline again')
        return 2
    if not isinstance(before, dict):
        print('BLOCKED: the baseline record must be an object; run the baseline again')
        return 2
    try:
        environment = json.loads(now['environment'])
    except (KeyError, TypeError, ValueError):
        print('BLOCKED: environment could not be established; run the baseline again')
        return 2
    if not isinstance(environment, dict) or any(value == 'unknown' for value in environment.values()):
        print('BLOCKED: an environment version is unknown; do not reuse this baseline')
        return 2
    changed = [key for key in now if before.get(key) != now[key]]
    if changed:
        print('RERUN: the baseline no longer matches its inputs: ' + ', '.join(changed))
        for key in changed:
            if key in ('commit', 'environment', 'command', 'cwd'):
                print(f'  {key}: was {before.get(key)!r}, now {now[key]!r}')
        return 1
    print('REUSE: command, working directory, commit, diff and recorded environment match; this is not a new test run')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
