#!/usr/bin/env python3
"""Preview/apply rule-library fingerprints during authorised package maintenance only."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--apply', action='store_true')
    args=p.parse_args(argv)
    path=ROOT/'skills/rule-maker/rules/version.json'
    data=json.loads(path.read_text())
    hashes={}
    for name in data['files']:
        if not isinstance(name,str) or Path(name).name!=name:
            raise ValueError('Unsafe library path')
        source=path.parent/name
        if source.is_symlink() or not source.is_file():
            raise ValueError('Missing/linked library file')
        hashes[name]=hashlib.sha256(source.read_bytes()).hexdigest()
    print('Updated files:', ', '.join(n for n,h in hashes.items() if data.get('sha256',{}).get(n)!=h) or 'none')
    if args.apply:
        data['sha256']=hashes
        path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
        print('Manifest updated; run tests before distribution.')
    else:
        print('PREVIEW ONLY. Not a security signature or permission to edit shared rules.')
    return 0
if __name__=='__main__':raise SystemExit(main())
