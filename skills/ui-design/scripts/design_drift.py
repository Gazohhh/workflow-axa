"""Read-only design drift check: tracked/untracked UI changes since the reviewed Git baseline.

No crawling every page, code execution, rewriting DESIGN.md or implied design approval.
Usage: python -X utf8 design_drift.py --root /repo [--baseline 40-char-sha] [--policy DESIGN.md]
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
from pathlib import Path

BASELINE = re.compile(r'<!--\s*workflow-axa-design-baseline:\s*([a-fA-F0-9]{40,64})\s*-->')
CSS_EXT = {'.css','.scss','.sass','.less'}
UI_EXT = {'.html','.htm','.jsx','.tsx','.vue','.svelte','.astro'}


def git(root: Path, *args: str, check: bool = True) -> bytes:
    proc = subprocess.run(['git', '-C', str(root), *args], capture_output=True, timeout=20)
    if check and proc.returncode:
        raise ValueError((proc.stderr or b'Git command failed').decode('utf-8', 'replace').strip())
    return proc.stdout if not proc.returncode else b''


def read_baseline(root: Path, policy: str) -> str | None:
    target = (root / policy).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        return None
    match = BASELINE.search(target.read_text(encoding='utf-8'))
    return match.group(1).lower() if match else None


def category(file: str) -> str | None:
    path = Path(file)
    lower = file.replace('\\','/').lower()
    if path.suffix.lower() in CSS_EXT:
        return 'shared-style' if any(s in lower for s in ('global.', 'theme/', 'variables.', 'tokens/', 'styles/')) else 'stylesheet'
    if path.suffix.lower() in UI_EXT:
        return 'component-or-template'
    if re.search(r'(?:component|page|screen|story|stories)\.(?:ts|js)$', lower):
        return 'framework-component'
    if lower.endswith(('.tokens.json','.theme.json')):
        return 'shared-style'
    return None


def scan(root: Path, baseline: str | None = None, policy: str = 'DESIGN.md') -> dict:
    root = Path(root).resolve()
    repo = Path(git(root, 'rev-parse','--show-toplevel').decode().strip()).resolve()
    if repo != root:
        # Callers may pass a subfolder; Git paths remain rooted at the actual checkout.
        root = repo
    head = git(root,'rev-parse','HEAD').decode().strip()
    baseline = baseline or read_baseline(root, policy)
    valid = bool(isinstance(baseline,str) and re.fullmatch(r'[a-fA-F0-9]{40,64}',baseline))
    if valid:
        valid = subprocess.run(['git','-C',str(root),'cat-file','-e',baseline+'^{commit}'],
                               capture_output=True,timeout=20).returncode == 0
    if valid:
        # A baseline from a different branch cannot stand in for an agreed review.
        valid = subprocess.run(['git','-C',str(root),'merge-base','--is-ancestor',baseline,'HEAD'],
                               capture_output=True,timeout=20).returncode == 0
    changed = []
    if valid:
        changed = [x.decode('utf-8','replace') for x in git(root,'diff','--name-only','-z','--no-renames',baseline,'--').split(b'\0') if x]
    else:
        # Only current working-tree changes are known. Committed drift is UNKNOWN.
        changed = [x.decode('utf-8','replace') for x in git(root,'diff','--name-only','-z','--no-renames','HEAD','--').split(b'\0') if x]
    untracked = [x.decode('utf-8','replace') for x in git(root,'ls-files','--others','--exclude-standard','-z').split(b'\0') if x]
    matched = [{'path':path,'type':category(path),'untracked':path in untracked}
               for path in sorted(set(changed+untracked)) if category(path)]
    broad = any(x['type']=='shared-style' for x in matched)
    return {'status': ('needs-reconciliation' if matched else 'no-drift-found') if valid else 'baseline-unknown',
            'baseline': baseline if valid else None, 'head':head,
            'changed_ui_files': matched, 'shared_style_changed':broad,
            'guidance': ('Inspect affected consumers and shared patterns, not just individual components.' if broad
                         else 'Inspect affected components/templates and their existing examples.' if matched
                         else 'No affected UI files detected since the reviewed baseline.' if valid
                         else 'Baseline missing/unavailable: cannot rule out older committed changes; run a targeted initial inventory.'),
            'approval': 'Not determined. Git changes never grant design approval.',
            'limitations': 'Path-level Git changes, not a selector dependency graph; generated files and runtime states require separate verification.'}


def main(argv=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',required=True,type=Path)
    parser.add_argument('--baseline')
    parser.add_argument('--policy',default='DESIGN.md')
    args=parser.parse_args(argv)
    try:
        print(json.dumps(scan(args.root,args.baseline,args.policy),indent=2,ensure_ascii=False))
    except (ValueError,OSError,subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status':'unavailable','reason':str(exc)}))
        return 2
    return 0


if __name__=='__main__':
    raise SystemExit(main())
