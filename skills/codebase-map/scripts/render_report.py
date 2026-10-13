#!/usr/bin/env python3
"""Render an offline evidence-linked HTML/SVG review; check supplied-source freshness.

This validates a report projection, not code semantics or user authorization.
Python 3.10+, standard library only. No repository writes except the requested HTML.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import sys
import textwrap
import webbrowser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ASSETS = Path(__file__).resolve().parents[1] / 'assets'
ID = re.compile(r'[A-Za-z][A-Za-z0-9_-]{0,47}\Z')
MAX_BYTES = 8 * 1024 * 1024
STATES = {'draft', 'awaiting-approval', 'approved', 'inspection', 'superseded'}
CHANGE = {'unchanged', 'added', 'modified', 'removed'}
BASIS = {'observed', 'inferred', 'unknown', 'proposed'}


def text(value: Any, name: str, limit: int = 2000) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f'{name}: expected nonempty text, at most {limit} characters')
    if any(ord(c) < 32 and c not in '\n\t\r' for c in value):
        raise ValueError(f'{name}: unsupported control character')
    return value


def rows(value: Any, name: str, *, empty: bool = True) -> list[dict]:
    if not isinstance(value, list) or any(not isinstance(v, dict) for v in value):
        raise ValueError(f'{name}: expected an array of objects')
    if not empty and not value:
        raise ValueError(f'{name}: must not be empty')
    return value


def indexed(value: Any, name: str, *, empty: bool = True) -> dict[str, dict]:
    result: dict[str, dict] = {}
    for row in rows(value, name, empty=empty):
        key = text(row.get('id'), f'{name}.id', 48)
        if not ID.fullmatch(key) or key in result:
            raise ValueError(f'{name}: invalid or duplicate id {key!r}')
        result[key] = row
    return result


def references(value: Any, allowed: dict, name: str, *, required: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(v, str) for v in value):
        raise ValueError(f'{name}: expected an array of identifiers')
    if required and not value:
        raise ValueError(f'{name}: at least one reference is required')
    if len(value) != len(set(value)) or any(v not in allowed for v in value):
        raise ValueError(f'{name}: unknown or duplicate reference')
    return value


def safe_source(root: Path, relative: Any) -> Path:
    relative = text(relative, 'source path', 500)
    # Root-relative POSIX paths keep the projection portable across Windows and Unix.
    if '\\' in relative or ':' in relative or '?' in relative or '#' in relative:
        raise ValueError(f'Unsupported source path: {relative}')
    part = Path(relative)
    if part.is_absolute() or '..' in part.parts or '.git' in part.parts:
        raise ValueError(f'Source path must stay inside root: {relative}')
    path = (root / part).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f'Missing or outside-root source: {relative}')
    if path.stat().st_size > MAX_BYTES:
        raise ValueError(f'Source exceeds 8 MiB limit: {relative}')
    return path


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('Input exceeds 8 MiB limit')
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError('Input must be a JSON object')
    return value


def validate(data: dict, root: Path) -> dict[str, dict]:
    if data.get('schema_version') != 1:
        raise ValueError('schema_version must be 1')
    for key in ('title', 'revision', 'understanding'):
        text(data.get(key), key)
    mode, state = data.get('mode'), data.get('state')
    if mode not in ('current', 'proposed', 'compare') or state not in STATES:
        raise ValueError('Invalid mode or state')
    if mode == 'current' and state != 'inspection':
        raise ValueError('Current-only maps must use inspection state')
    if mode != 'current' and state == 'inspection':
        raise ValueError('Inspection state is current-only')
    snapshot = data.get('snapshot')
    if not isinstance(snapshot, dict):
        raise ValueError('snapshot must be an object')
    for key in ('repository', 'basis'):
        text(snapshot.get(key), f'snapshot.{key}')
    if 'branch' in snapshot:
        text(snapshot['branch'], 'snapshot.branch')
    for field in ('boundaries', 'open_decisions'):
        if not isinstance(data.get(field), list):
            raise ValueError(f'{field} must be an array')
        for item in data[field]:
            text(item, field)

    sources = indexed(data.get('sources'), 'sources', empty=False)
    for row in sources.values():
        text(row.get('role'), 'source.role', 80)
        safe_source(root, row.get('path'))
    requirements = indexed(data.get('requirements'), 'requirements')
    for row in requirements.values():
        text(row.get('text'), 'requirement.text')
        text(row.get('origin'), 'requirement.origin')
    evidence = indexed(data.get('evidence'), 'evidence')
    for row in evidence.values():
        text(row.get('claim'), 'evidence.claim')
        if row.get('kind') not in ('static', 'runtime', 'design'):
            raise ValueError('Evidence kind must be static, runtime or design')
        references(row.get('sources'), sources, 'evidence.sources', required=True)
        text(row.get('locator'), 'evidence.locator')
        text(row.get('limits'), 'evidence.limits')
    acceptance = indexed(data.get('acceptance'), 'acceptance')
    for row in acceptance.values():
        text(row.get('text'), 'acceptance.text')
        text(row.get('verification'), 'acceptance.verification')
        references(row.get('requirements'), requirements, 'acceptance.requirements', required=True)
    tasks = indexed(data.get('tasks'), 'tasks')
    for row in tasks.values():
        text(row.get('title'), 'task.title')
        text(row.get('reason'), 'task.reason')
        if row.get('kind') not in ('requested', 'prerequisite'):
            raise ValueError('Task kind must be requested or prerequisite')
        references(row.get('requirements'), requirements, 'task.requirements', required=True)
        references(row.get('evidence'), evidence, 'task.evidence', required=True)
        references(row.get('acceptance'), acceptance, 'task.acceptance', required=True)
        references(row.get('depends_on'), tasks, 'task.depends_on')
        if row['id'] in row['depends_on']:
            raise ValueError('Task cannot depend on itself')
        if not isinstance(row.get('areas'), list) or not row['areas']:
            raise ValueError('task.areas must name at least one area')
        for area in row['areas']:
            text(area, 'task.area')
    pending = {k: set(v['depends_on']) for k, v in tasks.items()}
    while pending:
        ready = {k for k, v in pending.items() if not v}
        if not ready:
            raise ValueError('Task dependency cycle')
        pending = {k: v - ready for k, v in pending.items() if k not in ready}

    graphs = rows(data.get('graphs'), 'graphs', empty=False)
    kinds = [g.get('kind') for g in graphs]
    expected = {'current', 'proposed'} if mode == 'compare' else {mode}
    if set(kinds) != expected or len(kinds) != len(expected):
        raise ValueError('Graphs must match mode, without duplicates')
    for graph in graphs:
        text(graph.get('title'), 'graph.title')
        nodes = indexed(graph.get('nodes'), 'nodes', empty=False)
        if len(nodes) > 16:
            raise ValueError('Split maps with more than 16 nodes into focused views')
        cells: set[tuple[int, int]] = set()
        groups: dict[int, str] = {}
        for node in nodes.values():
            text(node.get('label'), 'node.label', 64)
            text(node.get('note'), 'node.note', 112)
            text(node.get('group'), 'node.group', 40)
            if len(textwrap.wrap(node['label'], width=28)) > 2 or len(textwrap.wrap(node['note'], width=36)) > 4:
                raise ValueError('Shorten node label/note; move detail to evidence')
            for coord in ('col', 'row'):
                if type(node.get(coord)) is not int or not 0 <= node[coord] <= 8:
                    raise ValueError('Node row/col must be integers from 0 to 8')
            cell = node['col'], node['row']
            if cell in cells:
                raise ValueError('Overlapping node positions')
            cells.add(cell)
            if node['row'] in groups and groups[node['row']] != node['group']:
                raise ValueError('Use one group label per row')
            groups[node['row']] = node['group']
        for edge in rows(graph.get('edges'), 'edges'):
            if edge.get('from') not in nodes or edge.get('to') not in nodes:
                raise ValueError('Edge endpoint does not exist')
            text(edge.get('label'), 'edge.label', 48)
        for item in list(nodes.values()) + graph['edges']:
            if item.get('basis') not in BASIS or item.get('change') not in CHANGE:
                raise ValueError('Each node/edge needs valid basis and change')
            basis = item['basis']
            references(item.get('evidence'), evidence, 'graph.evidence', required=basis in ('observed', 'inferred'))
            references(item.get('tasks'), tasks, 'graph.tasks', required=item['change'] != 'unchanged')
            if basis in ('observed', 'inferred'):
                if not any(evidence[e]['kind'] in ('static', 'runtime') for e in item['evidence']):
                    raise ValueError('Observed/inferred code needs static or runtime evidence')
            if basis == 'unknown' and not item.get('uncertainty'):
                raise ValueError('Unknown relationships must explain uncertainty')
            if 'uncertainty' in item:
                text(item['uncertainty'], 'graph.uncertainty')
            if graph['kind'] == 'current' and (basis == 'proposed' or item['change'] != 'unchanged'):
                raise ValueError('Current flow cannot contain future behavior/change labels')
            if graph['kind'] == 'proposed' and item['change'] in ('added', 'modified') and basis != 'proposed':
                raise ValueError('Added/modified future behavior must be marked proposed')

    if state in ('awaiting-approval', 'approved'):
        if mode != 'compare' or data['open_decisions']:
            raise ValueError('Approval-ready reviews need compare mode and no blocking decisions')
        roles = {s['role'] for s in sources.values()}
        if not {'plan', 'todo', 'findings'}.issubset(roles):
            raise ValueError('Approval-ready reviews need plan, todo and findings sources')
        if not requirements or not tasks or not acceptance or not evidence:
            raise ValueError('Approval-ready reviews need requirements, tasks, acceptance and evidence')
        covered = {r for a in acceptance.values() for r in a['requirements']}
        planned = {r for task in tasks.values() for r in task['requirements']}
        if set(requirements) - covered or set(requirements) - planned:
            raise ValueError('Every requirement needs acceptance and planned work')
    if state == 'approved':
        approval = data.get('approval')
        if not isinstance(approval, dict) or approval.get('revision') != data['revision']:
            raise ValueError('Approved state needs matching recorded approval revision')
        for field in ('record', 'response'):
            text(approval.get(field), f'approval.{field}')
    return sources


def esc(value: Any) -> str:
    return html.escape(str(value), quote=True)


def links(ids: list[str], prefix: str) -> str:
    return ' '.join(f'<a href="#{prefix}-{esc(v)}">{esc(v)}</a>' for v in ids) or '—'


def svg_lines(value: str, x: float, y: float, width: int, css: str, line_height: int) -> str:
    lines = textwrap.wrap(value, width=width, break_long_words=True, break_on_hyphens=False)
    return f'<text class="{css}" x="{x}" y="{y}">' + ''.join(
        f'<tspan x="{x}" dy="{0 if i == 0 else line_height}">{esc(line)}</tspan>'
        for i, line in enumerate(lines)) + '</text>'


def graph_html(graph: dict) -> str:
    kind = graph['kind']
    nodes = {n['id']: n for n in graph['nodes']}
    xstep, ystep, w, h = 348, 242, 254, 184
    pos = {k: (70 + n['col'] * xstep, 70 + n['row'] * ystep) for k, n in nodes.items()}
    width = max(x for x, _ in pos.values()) + w + 70
    height = max(y for _, y in pos.values()) + h + 45
    parts = [f'<svg class="map" viewBox="0 0 {width} {height}" data-original="0 0 {width} {height}" '
             f'role="img" tabindex="0" aria-label="{esc(graph["title"])}. Use toolbar to zoom and fit.">',
             f'<defs><marker id="arrow-{kind}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z"/></marker></defs>']
    for row in sorted({n['row'] for n in nodes.values()}):
        label = next(n['group'] for n in nodes.values() if n['row'] == row)
        y = 70 + row * ystep
        parts.append(f'<rect class="lane" x="28" y="{y-36}" width="{width-56}" height="{h+62}" rx="18"/>')
        parts.append(f'<text class="lane-title" x="48" y="{y-13}">{esc(label)}</text>')
    for edge in graph['edges']:
        x1, y1 = pos[edge['from']]; x2, y2 = pos[edge['to']]
        if x2 > x1 and y1 == y2:
            a, b = (x1+w, y1+h/2), (x2, y2+h/2)
            d = f'M {a[0]} {a[1]} L {b[0]} {b[1]}'
            tx, ty = (a[0]+b[0])/2, a[1]-24
        elif y2 > y1:
            a, b = (x1+w/2, y1+h), (x2+w/2, y2)
            middle = (a[1]+b[1])/2
            d = f'M {a[0]} {a[1]} C {a[0]} {middle}, {b[0]} {middle}, {b[0]} {b[1]}'
            tx, ty = (a[0]+b[0])/2+10, middle-10
        elif y2 < y1:
            a, b = (x1, y1+h/2), (x2, y2+h/2)
            bend = min(x1,x2)-25
            d = f'M {a[0]} {a[1]} C {bend} {a[1]}, {bend} {b[1]}, {b[0]} {b[1]}'
            tx, ty = bend, (a[1]+b[1])/2
        else:
            a, b = (x1+w/2, y1), (x2+w/2, y2)
            top = min(y1,y2)-25
            d = f'M {a[0]} {a[1]} C {a[0]} {top}, {b[0]} {top}, {b[0]} {b[1]}'
            tx, ty = (a[0]+b[0])/2, top-2
        parts.append(f'<path class="edge {edge["basis"]} {edge["change"]}" d="{d}" marker-end="url(#arrow-{kind})"><title>{esc(edge["label"])} · {esc(edge["basis"])} · evidence {esc(", ".join(edge["evidence"]))}</title></path>')
        parts.append(svg_lines(edge['label'], tx, ty, 17, 'edge-label', 14))
    for key, node in nodes.items():
        x,y = pos[key]
        parts.append(f'<g class="node {node["change"]}"><title>{esc(key)}: {esc(node["label"])}. {esc(node["note"])}. {esc(node["basis"])}</title><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12"/>')
        parts.append(f'<text class="node-meta" x="{x+16}" y="{y+23}">{esc(node["change"].upper())} · {esc(node["basis"])}</text>')
        parts.append(svg_lines(node['label'], x+16, y+49, 28, 'node-title', 19))
        parts.append(svg_lines(node['note'], x+16, y+98, 36, 'node-note', 15))
        parts.append(f'<text class="node-refs" x="{x+16}" y="{y+h-12}">{esc(key)} · {esc(" ".join(node["evidence"] + node["tasks"]))}</text></g>')
    parts.append('</svg>')
    details=[]
    for node in graph['nodes']:
        details.append(f'<li><strong>{esc(node["id"])} — {esc(node["label"])}</strong>: {esc(node["note"])} '
                       f'<span class="muted">{esc(node["basis"])} / {esc(node["change"])}</span> '
                       f'{esc(node.get("uncertainty", ""))} Evidence {links(node["evidence"],"e")}; work {links(node["tasks"],"t")}.</li>')
    for edge in graph['edges']:
        details.append(f'<li><strong>{esc(edge["from"])} → {esc(edge["to"])}</strong>: {esc(edge["label"])} '
                       f'({esc(edge["basis"])}, {esc(edge["change"])}) {esc(edge.get("uncertainty", ""))} '
                       f'Evidence {links(edge["evidence"],"e")}; work {links(edge["tasks"],"t")}.</li>')
    return f'<section class="graph-card"><div class="graph-heading"><h2>{esc(graph["title"])}</h2><div class="toolbar"><button type="button" data-action="out" aria-label="Zoom out">−</button><button type="button" data-action="in" aria-label="Zoom in">+</button><button type="button" data-action="fit">Fit view</button></div></div><div class="canvas">{"".join(parts)}</div><details><summary>Evidence and relationships · {len(nodes)} nodes</summary><ul class="detail-list">{"".join(details)}</ul></details></section>'


def render(data: dict, root: Path, input_path: Path) -> str:
    sources = validate(data, root)
    input_path = input_path.resolve()
    if not input_path.is_relative_to(root.resolve()):
        raise ValueError('Input JSON must be inside the supplied source root')
    if data != load_json(input_path):
        raise ValueError('Projection data must match saved input JSON before rendering')
    records = [{'id':k, 'role':v['role'], 'path':v['path'], 'sha256':digest(safe_source(root,v['path']))} for k,v in sources.items()]
    records.append({'id':'report-input','role':'projection','path':input_path.relative_to(root.resolve()).as_posix(),'sha256':digest(input_path)})
    manifest = {'schema_version':1, 'tool_version':'2.1.0', 'revision':data['revision'],
                'generated_utc':datetime.now(timezone.utc).isoformat(), 'sources':records}
    raw_manifest = json.dumps(manifest,ensure_ascii=True).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
    css = (ASSETS/'report.css').read_text(encoding='utf-8')
    js = (ASSETS/'report.js').read_text(encoding='utf-8')
    script_hash = base64.b64encode(hashlib.sha256(js.encode('utf-8')).digest()).decode('ascii')
    state = data['state']
    status = {'draft':'DRAFT — decisions or review still pending', 'awaiting-approval':'AWAITING USER APPROVAL — implementation not authorized',
              'approved':'APPROVAL RECORDED — verify the task record before continuing', 'inspection':'CURRENT STATE — inspection only, no implementation authority',
              'superseded':'SUPERSEDED — not authority for new implementation'}[state]
    req=''.join(f'<li id="r-{esc(r["id"])}"><strong>{esc(r["id"])}.</strong> {esc(r["text"])}<small>Source: {esc(r["origin"])}</small></li>' for r in data['requirements'])
    bounds=''.join(f'<li>{esc(b)}</li>' for b in data['boundaries']) or '<li>No additional boundaries recorded.</li>'
    task_rows=''.join(f'<tr id="t-{esc(t["id"])}"><td><strong>{esc(t["id"])}</strong></td><td><strong>{esc(t["title"])}</strong><small>{esc(t["kind"])}: {esc(t["reason"])}<br>Areas: {esc(", ".join(t["areas"]))}</small></td><td>{links(t["requirements"],"r")}<br>{links(t["evidence"],"e")}<br>{links(t["acceptance"],"a")}</td><td>{links(t["depends_on"],"t")}</td></tr>' for t in data['tasks'])
    acceptance=''.join(f'<li id="a-{esc(a["id"])}"><strong>{esc(a["id"])} — {esc(a["text"])}</strong><small>Verify: {esc(a["verification"])} · {links(a["requirements"],"r")}</small></li>' for a in data['acceptance'])
    ev=''.join(f'<article id="e-{esc(e["id"])}" class="evidence"><strong>{esc(e["id"])} · {esc(e["kind"])} — {esc(e["claim"])}</strong><p>{esc(e["locator"])}</p><small>Sources: {links(e["sources"],"s")}<br>Limits: {esc(e["limits"])}</small></article>' for e in data['evidence'])
    source_rows=''.join(f'<tr id="s-{esc(s["id"])}"><td>{esc(s["id"])}</td><td><code>{esc(s["path"])}</code></td><td>{esc(s["role"])}</td><td><code>{s["sha256"][:16]}…</code></td></tr>' for s in records)
    issues=''.join(f'<li>{esc(v)}</li>' for v in data['open_decisions'])
    issues = f'<section class="warning"><h2>Unresolved decisions — not approval-ready</h2><ul>{issues}</ul></section>' if issues else ''
    if state == 'awaiting-approval':
        gate=f'<section class="approval"><h2>Confirm the understanding before code changes</h2><p>Does this match what you want built? Approve this plan in the agent conversation, or describe what needs changing.</p><p><strong>Plan revision: {esc(data["revision"])}</strong></p><p>Opening or interacting with this report does not approve anything. There is no approve button, agent connection or background implementation.</p></section>'
    elif state == 'approved':
        gate=f'<section class="approval"><h2>Recorded approval reference</h2><p>{esc(data["approval"]["record"])}</p><blockquote>{esc(data["approval"]["response"])}</blockquote><p>This renderer does not authenticate the approving user or grant permission. Reconcile with the actual task record.</p></section>'
    else:
        gate='<section class="approval"><h2>No implementation permission</h2><p>This view alone authorizes no code changes. Resolve any decisions and use the workflow approval gate before substantive implementation.</p></section>'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'sha256-{script_hash}'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; font-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>{esc(data['title'])}</title><style>{css}</style></head><body><main>
<header><p class="eyebrow">WORKFLOW AXA · VISUAL REVIEW</p><h1>{esc(data['title'])}</h1><p class="status {state}">{esc(status)}</p><p class="meta">Plan {esc(data['revision'])} · {esc(data['snapshot']['repository'])} · {esc(data['snapshot'].get('branch','No branch recorded'))}</p><p class="muted">{esc(data['snapshot']['basis'])}</p></header>
<section class="understanding"><p class="eyebrow">WHAT I UNDERSTOOD</p><p class="lead">{esc(data['understanding'])}</p></section>
<div class="two-col"><section><h2>Requested outcome</h2><ul class="plain">{req or '<li>No implementation requirements in this inspection.</li>'}</ul></section><section><h2>What will not change</h2><ul>{bounds}</ul></section></div>
{issues}<div class="legend"><span>Unchanged</span><span class="added">Added</span><span class="modified">Modified</span><span class="removed">Removed</span><small>Observed = inspected code, not necessarily runtime-tested. Dashed arrows = inference, unknown or proposed.</small></div>
{''.join(graph_html(g) for g in data['graphs'])}
<section><h2>Changes and mapped tasks</h2><div class="table-scroll"><table><thead><tr><th>Task</th><th>Work and affected areas</th><th>Traceability</th><th>Depends on</th></tr></thead><tbody>{task_rows or '<tr><td colspan="4">Inspection only; no implementation tasks.</td></tr>'}</tbody></table></div></section>
<section><h2>How completion will be checked</h2><ul class="plain">{acceptance or '<li>No implementation acceptance criteria for this inspection.</li>'}</ul></section>
{gate}<section><h2>Evidence and limits</h2>{ev}</section>
<details class="snapshot"><summary>Inspected snapshot and supplied-source fingerprints</summary><p>Generated {esc(manifest['generated_utc'])}. Hashes cover only these supplied files, including their current local contents. They do not prove complete code coverage or correctness. This is a saved view, not a live repository map.</p><div class="table-scroll"><table><thead><tr><th>ID</th><th>Source</th><th>Role</th><th>SHA-256 prefix</th></tr></thead><tbody>{source_rows}</tbody></table></div></details>
<footer>Local HTML + SVG · no external assets, uploads or approval actions · source JSON remains editable · verify against authoritative task records</footer>
</main><script type="application/json" id="report-manifest">{raw_manifest}</script><script>{js}</script></body></html>'''


def check_report(path: Path, root: Path) -> list[str]:
    if path.stat().st_size > MAX_BYTES:
        raise ValueError('Report exceeds 8 MiB limit')
    content = path.read_text(encoding='utf-8')
    match = re.search(r'<script type="application/json" id="report-manifest">(.*?)</script>',content,re.S)
    if not match:
        raise ValueError('No supported report manifest found')
    manifest = json.loads(match[1])
    if not isinstance(manifest, dict) or manifest.get('schema_version') != 1:
        raise ValueError('Unsupported report manifest')
    changes=[]
    for source in rows(manifest.get('sources'),'manifest.sources',empty=False):
        value=source.get('sha256')
        if not isinstance(value,str) or not re.fullmatch(r'[0-9a-f]{64}',value):
            raise ValueError('Invalid manifest source hash')
        relative=text(source.get('path'),'manifest.path',500)
        try:
            if digest(safe_source(root,relative)) != value:
                changes.append(f'CHANGED: {relative}')
        except ValueError:
            changes.append(f'MISSING OR UNSAFE: {relative}')
    return changes


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True,help='Repository/source root; read-only.')
    parser.add_argument('--input',type=Path,help='JSON projection inside root.')
    parser.add_argument('--output',type=Path,help='New HTML file; existing files are never overwritten.')
    parser.add_argument('--open',action='store_true',help='Request default-browser opening; not proof of display.')
    parser.add_argument('--check',type=Path,help='Check an existing HTML against its supplied sources; no writes.')
    args=parser.parse_args()
    try:
        root=args.root.resolve(strict=True)
        if not root.is_dir():
            raise ValueError('--root must be a directory')
        if args.check:
            if args.input or args.output or args.open:
                raise ValueError('--check cannot be combined with render arguments')
            changes=check_report(args.check,root)
            print('\n'.join(changes) if changes else 'MATCH: supplied source bytes match; this is not semantic or approval verification.')
            return 1 if changes else 0
        if not args.input or not args.output:
            raise ValueError('Rendering requires --input and --output')
        if not args.input.resolve().is_relative_to(root):
            raise ValueError('Input JSON must be inside the supplied source root')
        if args.output.suffix.lower() not in ('.html', '.htm'):
            raise ValueError('Output must use .html or .htm extension')
        result=render(load_json(args.input),root,args.input)
        # Exclusive creation protects earlier reviewed revisions and unrelated files.
        with args.output.open('x',encoding='utf-8',newline='\n') as out:
            out.write(result)
        print(f'RENDERED: {args.output.resolve()}')
        print('Artifact creation does not approve or start implementation.')
        if args.open:
            try:
                accepted=webbrowser.open(args.output.resolve().as_uri(),new=2)
                print('OPEN REQUEST ACCEPTED; display not verified.' if accepted else 'OPEN REQUEST NOT ACCEPTED; use the file path manually.')
            except (OSError,webbrowser.Error) as exc:
                print(f'OPEN REQUEST FAILED: {exc}; report is still available at the path above.')
        return 0
    except (OSError,ValueError,TypeError,KeyError,UnicodeError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        return 2


if __name__=='__main__':
    raise SystemExit(main())
