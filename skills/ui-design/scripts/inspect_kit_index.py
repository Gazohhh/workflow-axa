#!/usr/bin/env python3
"""Read a local generated Storybook index without running it or granting design authority."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from check_design_kit import Reader, ID, inspect as inspect_catalogue, path_value, text, unique_object, validate

MAX_ENTRIES = 4096
LIMITS = [
    "A generated story index lists examples, not component approval or a complete dependency graph.",
    "Only listed import files and optional selected catalogue inputs are inspected; no code or network runs.",
    "Deleted or renamed exports within a surviving file require the project's actual story/type checks.",
    "Regenerate the index through already authorised project tooling; this helper cannot prove it is current.",
    "Tags, names and hashes do not authenticate consent, screenshots, runtime behaviour or release readiness.",
]


def entries(reader: Reader, name: str) -> tuple[dict, str]:
    raw = reader.read(name)
    data = json.loads(raw.decode('utf-8-sig'), object_pairs_hook=unique_object)
    if (not isinstance(data, dict) or type(data.get('v')) is not int or data['v'] not in (4, 5)
            or not isinstance(data.get('entries'), dict) or len(data['entries']) > MAX_ENTRIES):
        raise ValueError('Supported input: bounded generated index.json v4/v5 with entries; unknown formats need an adapter review.')
    result = {}
    for key, row in data['entries'].items():
        if not ID.fullmatch(text(key, 'story ID')) or not isinstance(row, dict) or row.get('id') != key:
            raise ValueError('Invalid/mismatched story identity.')
        if row.get('type') not in ('story', 'docs'):
            raise ValueError('Unsupported index entry type.')
        for field in ('title', 'name', 'importPath'):
            text(row.get(field), field)
        if row['type'] == 'story':
            result[key] = row
    return result, hashlib.sha256(raw).hexdigest()


def inspect(root: Path, index: str, selected=(), catalogue=None, item=None, scope=None, previous=None) -> dict:
    reader = Reader(root)
    rows, index_hash = entries(reader, index)
    selection = list(dict.fromkeys(selected)) if selected else sorted(rows)
    blockers = []
    if not selection:
        blockers.append('No story entries were found; no component coverage is established.')
    details = []
    for key in selection:
        if key not in rows:
            blockers.append(f'Missing selected story: {key}. No replacement was selected.')
            details.append({'id': key, 'state': 'MISSING'})
            continue
        row = rows[key]
        label = f'{row["title"]} / {row["name"]}'
        source = row['importPath']
        source = source[2:] if source.startswith('./') else source
        try:
            path_value(source)
            digest = hashlib.sha256(reader.read(source)).hexdigest()
            details.append({'id': key, 'label': label, 'state': 'SOURCE_PRESENT', 'source': source,
                            'sha256': digest, 'preview_reference': '?path=/story/' + key})
        except (OSError, ValueError) as exc:
            details.append({'id': key, 'label': label, 'state': 'MISSING_OR_UNSUPPORTED', 'source': source,
                            'problem': str(exc)})
            blockers.append(f'{key}: import source unavailable or unsupported; no fallback.')
    catalogue_result = None
    if catalogue is not None:
        if len(selection) != 1 or not item or not scope:
            raise ValueError('Catalogue binding needs exactly one --story plus --item and --scope.')
        catalogue_result = inspect_catalogue(root, catalogue, [item], [scope])
        data = json.loads(reader.read(catalogue).decode('utf-8-sig'), object_pairs_hook=unique_object)
        selected_item = validate(data)[item]
        if details[0].get('source') not in {r['path'] for r in selected_item['sources']}:
            blockers.append('The selected story source is not covered by this catalogue entry; inspect the designated mapping.')
        if catalogue_result['state'] != 'REVIEW_REQUIRED':
            blockers.append('Selected catalogue coverage is draft, stale, missing or out of scope.')
    elif item is not None or scope is not None:
        raise ValueError('--item/--scope require --catalogue; no implicit catalogue search.')
    delta = None
    if previous is not None:
        old, _ = entries(reader, previous)
        delta = {'added': sorted(set(rows)-set(old)), 'removed': sorted(set(old)-set(rows)),
                 'changed_metadata': sorted(k for k in set(rows)&set(old) if rows[k] != old[k])}
    return {'schema_version': 1, 'state': 'BLOCKED' if blockers else 'REVIEW_REQUIRED',
            'index': index, 'index_sha256': index_hash, 'entries': details, 'delta': delta,
            'catalogue': catalogue_result, 'blockers': blockers, 'approval_authenticated': False,
            'implementation_approved': False, 'runtime_verified': False, 'limits': LIMITS}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--index', required=True, help='Existing local generated Storybook index, relative to root.')
    parser.add_argument('--story', action='append', default=[])
    parser.add_argument('--catalogue')
    parser.add_argument('--item')
    parser.add_argument('--scope')
    parser.add_argument('--previous', help='Optional existing older index for ID changes; never creates snapshots.')
    args = parser.parse_args(argv)
    try:
        out = inspect(args.root, args.index, args.story, args.catalogue, args.item, args.scope, args.previous)
        print(json.dumps(out, ensure_ascii=True, indent=2))
        return 2 if out['state'] == 'BLOCKED' else 0
    except (OSError, ValueError, UnicodeError, TypeError, RecursionError) as exc:
        print(json.dumps({'state': 'BLOCKED', 'reason': str(exc), 'implementation_approved': False}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
