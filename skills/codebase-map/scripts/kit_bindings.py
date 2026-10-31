"""Resolve UI selections against a local catalogue; no app execution or approval inference."""
from __future__ import annotations

import hashlib
import html
import importlib.util
import json
from pathlib import Path


def kit_api():
    path = Path(__file__).resolve().parents[2] / 'ui-design/scripts/check_design_kit.py'
    if not path.is_file():
        raise ValueError('Install the complete ui-design sibling skill to resolve kit references.')
    spec = importlib.util.spec_from_file_location('workflow_kit_references', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def resolve(ui: dict, root: Path, sources: dict) -> dict | None:
    binding = ui.get('kit_binding')
    if binding is None:
        if any('elements' in s or 'capture_context' in s for s in ui['screens']):
            raise ValueError('Component selections need an explicit kit_binding; no guessed catalogue.')
        return None
    k = kit_api()
    if not isinstance(binding, dict) or set(binding) not in ({'source', 'scope'}, {'source', 'scope', 'projection'}):
        raise ValueError('kit_binding requires one supplied catalogue source and a repository-relative scope.')
    k.text(binding['source'], 'kit_binding.source')
    if binding['source'] not in sources:
        raise ValueError('kit_binding requires an actual supplied source.')
    scope = k.path_value(binding['scope']).as_posix()
    reader = k.Reader(root)
    catalogue_path = sources[binding['source']]['path']
    raw = reader.read(catalogue_path)
    data = binding['projection'] if 'projection' in binding else json.loads(raw.decode('utf-8-sig'), object_pairs_hook=k.unique_object)
    entries = k.validate(data)
    requested = []
    screen_rows = {}
    for screen in ui['screens']:
        elements = screen.get('elements')
        if not isinstance(elements, list) or not 1 <= len(elements) <= 20:
            raise ValueError('Each kit-backed screen needs one to twenty exact element/pattern selections.')
        seen = set()
        for element in elements:
            fields = {'id', 'item', 'role', 'variant', 'state', 'example_source', 'example_locator', 'changes'}
            if not isinstance(element, dict) or set(element) != fields:
                raise ValueError('Unknown/incomplete element reference; raw markup, styles and arbitrary links are prohibited.')
            for field in fields:
                k.text(element[field], 'element.' + field)
            if not k.ID.fullmatch(element['id']) or element['id'] in seen:
                raise ValueError('Element IDs must be unique within the screen.')
            seen.add(element['id'])
            row = entries.get(element['item'])
            if row is None:
                raise ValueError('Selected component/pattern was removed or is unknown; no replacement inferred.')
            if element['variant'] not in (row['variants'] or ['not-applicable']):
                raise ValueError('Selected variant is not declared by the kit entry.')
            if element['state'] not in (row['states'] or ['not-applicable']):
                raise ValueError('Selected state is not declared by the kit entry.')
            example = sources.get(element['example_source'])
            if example is None or example['path'] not in {ref['path'] for ref in row['sources']}:
                raise ValueError('The exact example source must be supplied and covered by its kit entry.')
            requested.append(element['item'])
        if not any(entries[e['item']]['kind'] == 'pattern' for e in elements):
            raise ValueError('A kit screen needs a selected composition pattern, not just approved individual controls.')
        screen_rows[screen['id']] = elements
    try:
        check = k.inspect_data(reader, data, raw, requested, [scope])
    except OSError as exc:
        raise ValueError('Kit selection blocked: a declared source is missing or unreadable: ' + str(exc)) from exc
    if check['state'] != 'REVIEW_REQUIRED':
        raise ValueError('Kit selection blocked: ' + '; '.join(check['blockers'] + check['pending']))
    checked_ids = {row['id'] for row in check['checked_items']}
    references = {catalogue_path: hashlib.sha256(raw).hexdigest()}
    for ref in [data['approval'], data['preview']] + [ref for key in checked_ids for ref in entries[key]['sources'] + [entries[key]['approval']]]:
        if ref is not None:
            references[ref['path']] = ref['sha256']
    # Capture inputs exclude approval prose but include every selected source dependency.
    for screen in ui['screens']:
        context = screen.get('capture_context')
        needed = set()
        def add(key):
            if key not in needed:
                needed.add(key)
                for child in entries[key]['uses']:
                    add(child)
        for e in screen_rows[screen['id']]:
            add(e['item'])
        expected = {ref['path']: ref['sha256'] for key in needed for ref in entries[key]['sources']}
        if screen['representation'] != 'capture':
            raise ValueError('Kit-backed screen requires an actual capture, never an invented schematic.')
        if not isinstance(context, dict) or set(context) != {'source', 'locator', 'summary', 'capture_sha256', 'inputs'}:
            raise ValueError('Each selected screen needs a capture_context tied to existing evidence and captured source hashes.')
        k.text(context['source'], 'capture_context.source')
        if context['source'] not in sources or context['source'] not in screen['sources']:
            raise ValueError('Capture context must name a listed evidence source.')
        for field in ('locator', 'summary'):
            k.text(context[field], 'capture_context.' + field)
        capture_path = sources[screen['capture']]['path']
        if context['capture_sha256'] != hashlib.sha256(reader.read(capture_path)).hexdigest():
            raise ValueError('Capture image differs from its recorded fingerprint.')
        refs = context['inputs']
        if not isinstance(refs, list) or not 1 <= len(refs) <= 256:
            raise ValueError('Capture inputs must be a bounded list of inspected source fingerprints.')
        observed = {}
        for ref in refs:
            k.reference(ref)
            if ref['path'] in observed:
                raise ValueError('Duplicate capture input path.')
            if not reader.match(ref):
                raise ValueError('Capture input changed or disappeared: ' + ref['path'])
            observed[ref['path']] = ref['sha256']
            references[ref['path']] = ref['sha256']
        if any(observed.get(path) != digest for path, digest in expected.items()):
            raise ValueError('Capture context omits a selected component/example/theme dependency or records older bytes.')
    return {'kit': data, 'entries': entries, 'screens': screen_rows, 'references': references,
            'source': binding['source'], 'scope': scope}


def snapshot_records(resolved: dict | None, sources: dict) -> list[dict]:
    if resolved is None:
        return []
    supplied = {row['path'] for row in sources.values()}
    result = []
    for index, (path, digest) in enumerate(sorted(resolved['references'].items()), 1):
        if path not in supplied:
            key = f'kit-input-{index}'
            if key in sources:
                raise ValueError('Reserved kit-input source identity collision.')
            result.append({'id': key, 'role': 'ui-kit-input', 'path': path, 'sha256': digest})
    return result


def selection_html(screen: dict, resolved: dict | None, sources: dict, api) -> str:
    if resolved is None:
        return ('<p class="muted"><strong>Component provenance not established.</strong> '
                'This legacy/illustrative view is not proof of approved-kit reuse.</p>')
    e = html.escape
    paths = {row['path']: key for key, row in sources.items()}
    paths.update({row['path']: row['id'] for row in snapshot_records(resolved, sources)})
    rows = []
    for selection in resolved['screens'][screen['id']]:
        entry = resolved['entries'][selection['item']]
        links = ' '.join(f'<a href="#s-{e(paths[ref["path"]])}"><code>{e(ref["path"])}</code></a>' for ref in entry['sources'])
        rows.append(f'<tr id="ui-element-{e(screen["id"])}-{e(selection["id"])}">'
                    f'<td><strong>{e(selection["id"])} · {e(selection["role"])}</strong></td>'
                    f'<td>{e(entry["name"])}<small>{e(entry["kind"])} · {e(entry["id"])}</small></td>'
                    f'<td>{e(selection["variant"])} / {e(selection["state"])}</td>'
                    f'<td>{api.links([selection["example_source"]],"s")} · {e(selection["example_locator"])}<small>{links}</small></td>'
                    f'<td>{e(selection["changes"])}</td></tr>')
    return ('<section class="ui-elements"><h3>Exactly which kit elements are used</h3>'
            f'<p>Catalogue: {api.links([resolved["source"]],"s")} · {e(resolved["kit"]["kit_id"])} '
            f'· {e(resolved["kit"]["revision"])} · scope <code>{e(resolved["scope"])}</code>.</p>'
            '<p class="muted">Declared approved entries; listed source fingerprints match. '
            'The capture and its evidence still require review: matching hashes do not authenticate consent '
            'or prove these components produced the image.</p>'
            '<p class="hint">Scroll the reference table horizontally on small screens.</p>'
            '<div class="table-scroll appendix"><table><thead><tr><th>On screen</th><th>Kit entry</th>'
            '<th>Variant / state</th><th>Example and actual sources</th><th>Intended changes</th></tr></thead>'
            '<tbody>'+''.join(rows)+'</tbody></table></div></section>')
