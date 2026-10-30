"""Create the links that link-rejection tests need, honestly per host.

A real symlink is used wherever the host allows it. Windows refuses symlink creation without a privilege
(WinError 1314); only then does a directory link become an NTFS junction, which the helpers must reject too
(real installs use junctions, e.g. ~/.claude/skills), and a file link, which has no unprivileged
equivalent, skips with a reason marking that protection unverified on this host. Any other error is a
fixture bug and propagates.
"""
from __future__ import annotations

import unittest
from pathlib import Path

ERROR_PRIVILEGE_NOT_HELD = 1314


def make_link(link: Path, target: Path, directory: bool = False) -> str:
    try:
        link.symlink_to(target, target_is_directory=directory)
        return 'symlink'
    except OSError as exc:
        if getattr(exc, 'winerror', None) != ERROR_PRIVILEGE_NOT_HELD:
            raise
        if directory:
            import _winapi
            _winapi.CreateJunction(str(target), str(link))
            return 'junction'
        raise unittest.SkipTest('File symlinks need a privilege this host lacks; file-link rejection is unverified here.')
