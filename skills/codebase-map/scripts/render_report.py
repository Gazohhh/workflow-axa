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
    if data.get('schema_version') != 2:
        raise ValueError('New renders require schema_version 2; migrate the layout using REPORT.md. Existing HTML remains checkable with --check.')
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

    graphs = indexed(data.get('graphs'), 'graphs', empty=False)
    if len(graphs) > 6:
        raise ValueError('Use at most six focused views per report')
    kinds = {g.get('kind') for g in graphs.values()}
    expected = {'current', 'proposed'} if mode == 'compare' else {mode}
    if kinds != expected:
        raise ValueError('Graphs must match mode; compare requires current and proposed')
    for graph in graphs.values():
        text(graph.get('title'), 'graph.title')
        nodes = indexed(graph.get('nodes'), 'nodes', empty=False)
        for node in nodes.values():
            text(node.get('label'), 'node.label', 80)
            if node.get('note') != '':
                text(node.get('note'), 'node.note', 112)
        for edge in rows(graph.get('edges'), 'edges'):
            if edge.get('from') not in nodes or edge.get('to') not in nodes:
                raise ValueError('Edge endpoint does not exist')
            if edge.get('label') != '':
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
        validate_geometry(graph, nodes)
        validate_delivery(graph, tasks)
    if data.get('default_view') not in graphs:
        raise ValueError('default_view must identify a graph in this report')
    if mode == 'compare' and (graphs[data['default_view']]['kind'] != 'proposed' or graphs[data['default_view']]['purpose'] != 'flow'):
        raise ValueError('Approval comparison opens with the proposed feature flow, not a build plan or structural map')
    comparison = rows(data.get('comparison'), 'comparison')
    for row in comparison:
        for key in ('label', 'current', 'proposed'):
            text(row.get(key), f'comparison.{key}')
        references(row.get('requirements'), requirements, 'comparison.requirements', required=True)
        references(row.get('evidence'), evidence, 'comparison.evidence', required=True)
        references(row.get('tasks'), tasks, 'comparison.tasks', required=True)
    if mode == 'compare' and not comparison:
        raise ValueError('Comparison needs an evidence-linked current/proposed change summary')
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


def coordinate(value: Any, name: str, lower: int = 0, upper: int = 2400) -> int:
    if type(value) is not int or not lower <= value <= upper or value % 4:
        raise ValueError(f'{name}: use a 4px-grid integer from {lower} to {upper}')
    return value


def boxes_overlap(a: tuple, b: tuple, gap: float = 0) -> bool:
    x, y, w, h = a
    xx, yy, ww, hh = b
    return x < xx + ww + gap and xx < x + w + gap and y < yy + hh + gap and yy < y + h + gap


def segment_hits_box(a: list, b: list, box: tuple, inset: float = 0) -> bool:
    x, y, w, h = box
    if a[0] == b[0]:
        return x + inset < a[0] < x + w - inset and max(min(a[1], b[1]), y + inset) < min(max(a[1], b[1]), y + h - inset)
    return y + inset < a[1] < y + h - inset and max(min(a[0], b[0]), x + inset) < min(max(a[0], b[0]), x + w - inset)


def segments_meet(a: list, b: list, c: list, d: list) -> bool:
    if a[0] == b[0] and c[0] == d[0]:
        return a[0] == c[0] and max(min(a[1], b[1]), min(c[1], d[1])) <= min(max(a[1], b[1]), max(c[1], d[1]))
    if a[1] == b[1] and c[1] == d[1]:
        return a[1] == c[1] and max(min(a[0], b[0]), min(c[0], d[0])) <= min(max(a[0], b[0]), max(c[0], d[0]))
    if a[0] != b[0]:
        a, b, c, d = c, d, a, b
    return min(c[0], d[0]) <= a[0] <= max(c[0], d[0]) and min(a[1], b[1]) <= c[1] <= max(a[1], b[1])


def port_side(node: dict, point: list) -> str:
    x, y, w, h = (node[k] for k in ('x', 'y', 'width', 'height'))
    px, py = point
    if node['shape'] == 'decision':
        for side, port in (('top', [x+w/2, y]), ('right', [x+w, y+h/2]), ('bottom', [x+w/2, y+h]), ('left', [x, y+h/2])):
            if point == port:
                return side
    else:
        if py == y and x+16 <= px <= x+w-16: return 'top'
        if py == y+h and x+16 <= px <= x+w-16: return 'bottom'
        if px == x and y+16 <= py <= y+h-16: return 'left'
        if px == x+w and y+16 <= py <= y+h-16: return 'right'
    raise ValueError('Connector endpoint must attach to an allowed node boundary port')


def outward(side: str, point: list, adjacent: list) -> bool:
    return {'top': adjacent[1] < point[1] and adjacent[0] == point[0],
            'bottom': adjacent[1] > point[1] and adjacent[0] == point[0],
            'left': adjacent[0] < point[0] and adjacent[1] == point[1],
            'right': adjacent[0] > point[0] and adjacent[1] == point[1]}[side]


def edge_label_box(edge: dict) -> tuple:
    x, y = edge['label_position']
    width = 16 + len(edge['label']) * 7
    return x - width/2, y - 15, width, 22


def validate_geometry(graph: dict, nodes: dict) -> None:
    width = coordinate(graph.get('width'), 'graph.width', 400, 1600)
    height = coordinate(graph.get('height'), 'graph.height', 240, 1600)
    if graph.get('purpose') not in ('flow', 'delivery', 'structure', 'technical'):
        raise ValueError('Graph purpose must be flow, delivery, structure or technical')
    for field in ('tab', 'description'):
        text(graph.get(field), f'graph.{field}', 700 if field == 'description' else 36)
    if len(nodes) > 9 or len(graph['edges']) > 12:
        raise ValueError('Split the diagram: at most 9 nodes and 12 connectors per view')
    if sum(n.get('highlight', False) is True for n in nodes.values()) > 2:
        raise ValueError('Use at most two focal nodes per view')
    boxes = {}
    for key, node in nodes.items():
        for field, low, high in (('x', 0, width), ('y', 0, height), ('width', 128, width), ('height', 48, height)):
            coordinate(node.get(field), f'node.{field}', low, high)
        if node.get('shape') not in ('start', 'action', 'decision', 'result', 'group'):
            raise ValueError('Node needs a start/action/decision/result/group shape')
        if 'highlight' in node and type(node['highlight']) is not bool:
            raise ValueError('node.highlight must be boolean')
        box = tuple(node[k] for k in ('x', 'y', 'width', 'height'))
        x, y, w, h = box
        if x+w > width-16 or y+h > height-16 or x < 16 or y < 16:
            raise ValueError('Node exceeds the diagram bounds/padding')
        if any(boxes_overlap(box, other, gap=12) for other in boxes.values()):
            raise ValueError('Overlapping nodes or less than 12px separation')
        boxes[key] = box
        lines = node['label'].split('\n')
        notes = node['note'].split('\n') if node['note'] else []
        available = w * .62 if node['shape'] == 'decision' else w-40
        # Conservative character budgets catch obvious clipping; browser measurements remain required.
        if len(lines) > 2 or any(len(line) * 10 > available for line in lines):
            raise ValueError('Shorten node label or widen its shape; never shrink type')
        if len(notes) > 2 or any(len(line) * 7 > w-40 for line in notes):
            raise ValueError('Shorten node note or move detail below the diagram')
        if node['shape'] == 'decision' and (notes or h < 128):
            raise ValueError('Decision diamond needs >=128px height and no note; detail belongs below')
        items = node.get('items', [])
        if not isinstance(items, list) or len(items) > 9 or (items and node['shape'] != 'group'):
            raise ValueError('Only group nodes have items, at most nine')
        for item in items:
            text(item, 'node.items', 60)
            if len(item) * 8 > w-48:
                raise ValueError('Shorten group item or widen the group')
        needed = 36 + 24*len(lines) + 20*len(notes) + (36*len(items)+12 if items else 0)
        if node['shape'] != 'decision' and h < needed-12:
            raise ValueError('Node height is too small for its text')
    all_segments = []
    ports: dict[str, list[list]] = {}
    masks = []
    for edge in graph['edges']:
        points = edge.get('points')
        if not isinstance(points, list) or not 2 <= len(points) <= 16:
            raise ValueError('Connector needs 2–16 explicit orthogonal points')
        for point in points:
            if not isinstance(point, list) or len(point) != 2:
                raise ValueError('Connector point must be [x, y]')
            coordinate(point[0], 'point.x', 4, width-4)
            coordinate(point[1], 'point.y', 4, height-4)
        segments = list(zip(points, points[1:]))
        for a, b in segments:
            if a == b or (a[0] != b[0] and a[1] != b[1]):
                raise ValueError('Connectors must be orthogonal with distinct consecutive points')
            if abs(a[0]-b[0]) + abs(a[1]-b[1]) < 12:
                raise ValueError('Connector segments need at least 12px for clear elbows')
            for box in boxes.values():
                if segment_hits_box(a, b, box):
                    raise ValueError('Connector crosses a node; route outside boxes')
        for key, point, neighbor in ((edge['from'], points[0], points[1]), (edge['to'], points[-1], points[-2])):
            side = port_side(nodes[key], point)
            if not outward(side, point, neighbor):
                raise ValueError('Connector must leave/enter the node outward, not along its boundary')
            if any(abs(point[0]-p[0]) + abs(point[1]-p[1]) < 12 for p in ports.get(key, [])):
                raise ValueError('Give connectors distinct ports at least 12px apart')
            ports.setdefault(key, []).append(point)
        for i, (a, b) in enumerate(segments):
            if any(segments_meet(a, b, c, d) for c, d in segments[i+2:]):
                raise ValueError('Connector doubles back or crosses itself')
            if any(segments_meet(a, b, c, d) for c, d in all_segments):
                raise ValueError('Connectors cross or share a stroke; reroute or split the view')
        all_segments.extend(segments)
        if edge['label']:
            if len(edge['label']) > 14 or '\n' in edge['label']:
                raise ValueError('Keep connector labels within 14 characters, one line')
            position = edge.get('label_position')
            if not isinstance(position, list) or len(position) != 2:
                raise ValueError('Labelled connectors need label_position [x, baseline_y]')
            for i, value in enumerate(position):
                coordinate(value, 'label_position', 0, width if i == 0 else height)
            mask = edge_label_box(edge)
            mx, my, mw, mh = mask
            if mx < 0 or my < 0 or mx+mw > width or my+mh > height:
                raise ValueError('Connector label falls outside the view')
            if any(boxes_overlap(mask, box, gap=4) for box in boxes.values()):
                raise ValueError('Connector label overlaps a node')
            if any(boxes_overlap(mask, other, gap=4) for other in masks):
                raise ValueError('Connector labels overlap')
            masks.append(mask)
        elif nodes[edge['from']]['shape'] == 'decision':
            raise ValueError('Every decision branch needs an explicit label')
    for mask in masks:
        x, y, w, h = mask
        padded = (x-6, y-6, w+12, h+12)
        if any(segment_hits_box(a, b, padded) for a, b in all_segments):
            raise ValueError('Connector label needs at least a 6px gap from routes')
    for key, node in nodes.items():
        outgoing = [e for e in graph['edges'] if e['from'] == key]
        if node['shape'] == 'decision':
            if not 2 <= len(outgoing) <= 3 or len({e['label'].casefold() for e in outgoing}) != len(outgoing):
                raise ValueError('A decision needs two or three distinctly labelled exits')


def validate_delivery(graph: dict, tasks: dict) -> None:
    if graph['purpose'] != 'delivery':
        return
    if graph['kind'] != 'proposed':
        raise ValueError('Delivery view describes proposed work, not current application behavior')
    nodes = {n['id']: n for n in graph['nodes']}
    task_nodes, approvals = {}, []
    for node in nodes.values():
        if node.get('precondition') == 'approval':
            if node['shape'] != 'start' or node['tasks']:
                raise ValueError('Approval precondition is a start node, not a task or recorded approval')
            approvals.append(node['id'])
        else:
            task = node.get('task_id')
            if task not in tasks or node['tasks'] != [task] or task in task_nodes:
                raise ValueError('Delivery nodes need a unique task_id matching their task reference')
            task_nodes[task] = node['id']
    if len(approvals) != 1:
        raise ValueError('Delivery view needs exactly one explicit approval precondition')
    selected = set(task_nodes)
    external = {dep for key in selected for dep in tasks[key]['depends_on'] if dep not in selected}
    declared = graph.get('external_dependencies', [])
    references(declared, tasks, 'external_dependencies')
    if set(declared) != external:
        raise ValueError('Partial delivery view must declare external_dependencies; do not hide prerequisites')
    expected = {(task_nodes[dep], task_nodes[key]) for key in selected for dep in tasks[key]['depends_on'] if dep in selected}
    roots = {task_nodes[key] for key in selected if not set(tasks[key]['depends_on']) & selected}
    expected |= {(approvals[0], key) for key in roots}
    actual = [(edge['from'], edge['to']) for edge in graph['edges']]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError('Delivery edges must match the task dependencies and approval precondition')


def graph_records(graph: dict) -> str:
    details = []
    for node in graph['nodes']:
        details.append(f'<li><strong>{esc(node["id"])} — {esc(node["label"])}</strong>: {esc(node["note"])} '
                       f'({esc(node["basis"])}, {esc(node["change"])}) {esc(node.get("uncertainty", ""))} '
                       f'Evidence {links(node["evidence"], "e")}; tasks {links(node["tasks"], "t")}.</li>')
    for edge in graph['edges']:
        details.append(f'<li><strong>{esc(edge["from"])} → {esc(edge["to"])}</strong>: {esc(edge["label"] or "continues")} '
                       f'({esc(edge["basis"])}, {esc(edge["change"])}) {esc(edge.get("uncertainty", ""))} '
                       f'Evidence {links(edge["evidence"], "e")}; tasks {links(edge["tasks"], "t")}.</li>')
    return f'<details><summary>{esc(graph["tab"])} — nodes and relationships</summary><ol>{"".join(details)}</ol></details>'


def elbow_path(points: list) -> str:
    result = f'M {points[0][0]} {points[0][1]}'
    for i in range(1, len(points)-1):
        previous, corner, following = points[i-1:i+2]
        length_in = abs(corner[0]-previous[0]) + abs(corner[1]-previous[1])
        length_out = abs(following[0]-corner[0]) + abs(following[1]-corner[1])
        radius = min(8, length_in/2, length_out/2)
        before = [corner[j] + (previous[j]-corner[j])/length_in*radius for j in (0, 1)]
        after = [corner[j] + (following[j]-corner[j])/length_out*radius for j in (0, 1)]
        result += f' L {before[0]:g} {before[1]:g} Q {corner[0]} {corner[1]} {after[0]:g} {after[1]:g}'
    return result + f' L {points[-1][0]} {points[-1][1]}'


def graph_html(graph: dict) -> str:
    key = graph['id']
    start = min(graph['nodes'], key=lambda node: (node['shape'] != 'start', node['y'], node['x']))
    start_id = f'node-{len(key)}-{key}-{start["id"]}'
    parts = [f'<svg class="map" xmlns="http://www.w3.org/2000/svg" width="{graph["width"]}" height="{graph["height"]}" '
             f'viewBox="0 0 {graph["width"]} {graph["height"]}" role="img" aria-labelledby="{key}-title {key}-desc">'
             f'<title id="{key}-title">{esc(graph["title"])}</title><desc id="{key}-desc">{esc(graph["description"])}</desc>'
             f'<defs><marker id="arrow-{key}" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="9" markerHeight="7" orient="auto">'
             '<path d="M 0 0 L 10 4 L 0 8 Z"/></marker></defs>']
    for edge in graph['edges']:
        parts.append(f'<path class="connector {edge["basis"]}" data-from="{esc(edge["from"])}" data-to="{esc(edge["to"])}" '
                     f'data-points="{esc(json.dumps(edge["points"]))}" d="{elbow_path(edge["points"])}" marker-end="url(#arrow-{key})"/>' )
    for edge in graph['edges']:
        if edge['label']:
            x, y, w, h = edge_label_box(edge)
            cx, baseline = edge['label_position']
            parts.append(f'<g class="arrow-label"><rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}"/>'
                         f'<text class="edge-label" text-anchor="middle" x="{cx}" y="{baseline}">{esc(edge["label"].upper())}</text></g>')
    for node in graph['nodes']:
        x, y, w, h = (node[v] for v in ('x', 'y', 'width', 'height'))
        cx, cy = x+w/2, y+h/2
        shape = node['shape']
        classes = f'node {shape} {node["basis"]} {"focal" if node.get("highlight") else ""}'
        parts.append(f'<g id="node-{len(key)}-{key}-{esc(node["id"])}" class="{classes}" data-id="{esc(node["id"])}" data-box="{x},{y},{w},{h}">'
                     f'<title>{esc(node["label"])}. {esc(node["basis"])} / {esc(node["change"])}. '
                     f'{esc(node.get("uncertainty", ""))}</title>')
        if shape == 'decision':
            parts.append(f'<polygon class="node-shape" points="{cx:g},{y} {x+w},{cy:g} {cx:g},{y+h} {x},{cy:g}"/>')
        else:
            radius = 20 if shape in ('start', 'result') else 6
            parts.append(f'<rect class="node-shape" x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}"/>')
        lines = node['label'].split('\n')
        notes = node['note'].split('\n') if node['note'] else []
        items = node.get('items', [])
        tx = x+24 if shape == 'group' else cx
        anchor = 'start' if shape == 'group' else 'middle'
        baseline = y+36 if shape == 'group' else cy-(len(lines)-1)*12-len(notes)*10+6
        for i, line in enumerate(lines):
            parts.append(f'<text class="node-title" x="{tx:g}" y="{baseline+i*24:g}" text-anchor="{anchor}">{esc(line)}</text>')
        for i, line in enumerate(notes):
            parts.append(f'<text class="node-note" x="{tx:g}" y="{baseline+len(lines)*24+i*20:g}" text-anchor="{anchor}">{esc(line)}</text>')
        for i, line in enumerate(items):
            iy = baseline + len(lines)*24 + len(notes)*20 + 20+i*36
            parts.append(f'<text class="node-item" x="{x+24}" y="{iy:g}">{esc(line)}</text>')
        parts.append('</g>')
    parts.append('</svg>')
    shapes = {n['shape'] for n in graph['nodes']}
    legend = []
    for shape, label in (('start', 'Start / result'), ('action', 'Action'), ('decision', 'Decision'), ('group', 'Group')):
        if shape in shapes or (shape == 'start' and 'result' in shapes):
            legend.append(f'<span><i class="legend-{shape}" aria-hidden="true"></i>{label}</span>')
    if any(n.get('highlight') for n in graph['nodes']):
        legend.append('<span><i class="legend-focus" aria-hidden="true"></i>Focus of the change</span>')
    external_note = f'<p>Other required tasks outside this view: {links(graph["external_dependencies"], "t")}</p>' if graph.get('external_dependencies') else ''
    return (f'<figure class="panel" id="panel-{key}"><div class="figure-head"><h2>{esc(graph["title"])}</h2>'
            f'<span>{esc(graph["kind"])} · {esc(graph["purpose"])}</span></div><p class="figure-description">{esc(graph["description"])}</p>'
            f'<p class="hint">Scroll sideways to explore. <a href="#{start_id}">Go to start</a>. Fit is an optional overview.</p>'
            f'<div class="canvas" tabindex="0" role="region" aria-label="{esc(graph["tab"])} diagram, scroll to explore" '
            f'data-start-id="{start_id}" style="--board-width:{graph["width"]}px">{"".join(parts)}</div>'
            f'<figcaption><div class="legend">{"".join(legend)}</div>'
            f'{external_note}<span class="muted">Dashed outlines indicate inference or unknowns; details and evidence are below. Proposed is not implemented.</span></figcaption></figure>')


def view_controls(graphs: list, default: str) -> tuple[str, str]:
    inputs, labels, rules = [], [], []
    for graph in graphs:
        key = graph['id']
        inputs.append(f'<input class="sr-radio" type="radio" name="diagram-view" id="view-{key}" aria-label="{esc(graph["tab"])}" '
                      f'aria-controls="panel-{key}" {"checked" if key == default else ""}>')
        labels.append(f'<label for="view-{key}">{esc(graph["tab"])}</label>')
        rules.extend([f'#view-{key}:checked~.figures #panel-{key}{{display:block}}',
                      f'#view-{key}:checked~.viewbar label[for="view-{key}"]{{border-color:var(--accent);color:var(--ink)}}',
                      f'#view-{key}:focus-visible~.viewbar label[for="view-{key}"]{{outline:2px solid var(--accent);outline-offset:4px}}'])
    zooms = []
    for value, label in (('100', '100%'), ('125', '125%'), ('150', '150%'), ('fit', 'Fit')):
        inputs.append(f'<input class="sr-radio" type="radio" name="diagram-zoom" id="zoom-{value}" '
                      f'aria-label="{label} diagram size" {"checked" if value == "100" else ""}>')
        zooms.append(f'<label for="zoom-{value}">{label}</label>')
        rules.extend([f'#zoom-{value}:checked~.viewbar label[for="zoom-{value}"]{{border-color:var(--ink);color:var(--ink)}}',
                      f'#zoom-{value}:focus-visible~.viewbar label[for="zoom-{value}"]{{outline:2px solid var(--accent);outline-offset:4px}}'])
    controls = (''.join(inputs) + '<div class="viewbar"><div class="view-tabs" role="group" aria-label="Diagram views">' +
                ''.join(labels) + '</div><div class="zoom-tabs" role="group" aria-label="Diagram size">' + ''.join(zooms) + '</div></div>')
    return controls, '\n'.join(rules)


def render(data: dict, root: Path, input_path: Path) -> str:
    sources = validate(data, root)
    input_path = input_path.resolve()
    if not input_path.is_relative_to(root.resolve()):
        raise ValueError('Input JSON must be inside the supplied source root')
    if data != load_json(input_path):
        raise ValueError('Projection data must match saved input JSON before rendering')
    records = [{'id': key, 'role': value['role'], 'path': value['path'], 'sha256': digest(safe_source(root, value['path']))}
               for key, value in sources.items()]
    records.append({'id': 'report-input', 'role': 'projection', 'path': input_path.relative_to(root.resolve()).as_posix(), 'sha256': digest(input_path)})
    manifest = {'schema_version': 1, 'tool_version': '2.5.0', 'layout_version': 2, 'style': 'workflow-editorial-v1',
                'revision': data['revision'], 'generated_utc': datetime.now(timezone.utc).isoformat(), 'sources': records}
    raw_manifest = json.dumps(manifest, ensure_ascii=True).replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
    ordered = sorted(data['graphs'], key=lambda graph: graph['id'] != data['default_view'])
    controls, view_css = view_controls(ordered, data['default_view'])
    css = (ASSETS/'report.css').read_text(encoding='utf-8') + '\n' + view_css
    js = (ASSETS/'report.js').read_text(encoding='utf-8')
    script_hash = base64.b64encode(hashlib.sha256(js.encode('utf-8')).digest()).decode('ascii')
    state = data['state']
    status = {'draft': 'DRAFT — decisions or review still pending',
              'awaiting-approval': 'AWAITING USER APPROVAL — implementation not authorized',
              'approved': 'APPROVAL RECORDED — verify the task record before continuing',
              'inspection': 'CURRENT STATE — inspection only, no implementation authority',
              'superseded': 'SUPERSEDED — not authority for new implementation'}[state]
    req = ''.join(f'<li id="r-{esc(r["id"])}"><strong>{esc(r["id"])}.</strong> {esc(r["text"])}<small>Source: {esc(r["origin"])}</small></li>' for r in data['requirements'])
    bounds = ''.join(f'<li>{esc(b)}</li>' for b in data['boundaries']) or '<li>No additional boundaries recorded.</li>'
    task_rows = ''.join(f'<tr id="t-{esc(t["id"])}"><td><strong>{esc(t["id"])}</strong></td><td><strong>{esc(t["title"])}</strong>'
                        f'<small>{esc(t["kind"])}: {esc(t["reason"])}<br>Areas: {esc(", ".join(t["areas"]))}</small></td>'
                        f'<td>{links(t["requirements"], "r")}<br>{links(t["evidence"], "e")}<br>{links(t["acceptance"], "a")}</td>'
                        f'<td>{links(t["depends_on"], "t")}</td></tr>' for t in data['tasks'])
    task_summary = ''.join(f'<li><a href="#t-{esc(t["id"])}">{esc(t["id"])}</a> {esc(t["title"])}'
                           f'<small>Depends on: {esc(", ".join(t["depends_on"]) or "No prior task")}</small></li>' for t in data['tasks'])
    acceptance = ''.join(f'<li id="a-{esc(a["id"])}"><strong>{esc(a["id"])} — {esc(a["text"])}</strong>'
                         f'<small>Verify: {esc(a["verification"])} · {links(a["requirements"], "r")}</small></li>' for a in data['acceptance'])
    ev = ''.join(f'<article id="e-{esc(e["id"])}" class="evidence"><strong>{esc(e["id"])} · {esc(e["kind"])} — {esc(e["claim"])}</strong>'
                 f'<p>{esc(e["locator"])}</p><small>Sources: {links(e["sources"], "s")}<br>Limits: {esc(e["limits"])}</small></article>' for e in data['evidence'])
    source_rows = ''.join(f'<tr id="s-{esc(s["id"])}"><td>{esc(s["id"])}</td><td><code>{esc(s["path"])}</code></td>'
                          f'<td>{esc(s["role"])}</td><td><code>{s["sha256"][:16]}…</code></td></tr>' for s in records)
    issues = ''.join(f'<li>{esc(v)}</li>' for v in data['open_decisions'])
    issues = f'<section class="warning"><h2>Unresolved decisions — not approval-ready</h2><ul>{issues}</ul></section>' if issues else ''
    uncertainty = sorted({item.get('uncertainty', '') for g in data['graphs'] for item in g['nodes'] + g['edges'] if item.get('uncertainty')})
    if uncertainty:
        issues += '<section class="warning"><h2>Evidence limits</h2><ul>' + ''.join(f'<li>{esc(v)}</li>' for v in uncertainty) + '</ul></section>'
    comparison_rows = ''.join(f'<tr><td><strong>{esc(row["label"])}</strong><small>{links(row["requirements"], "r")}</small></td>'
                              f'<td>{esc(row["current"])}<small>{links(row["evidence"], "e")}</small></td>'
                              f'<td>{esc(row["proposed"])}<small>{links(row["tasks"], "t")}</small></td></tr>' for row in data['comparison'])
    comparison = (f'<section class="comparison"><h2>What changes</h2><div class="table-scroll"><table><thead><tr>'
                  '<th>Area</th><th>Current — recorded evidence</th><th>Proposed — not implemented</th></tr></thead>'
                  f'<tbody>{comparison_rows}</tbody></table></div></section>') if comparison_rows else ''
    if state == 'awaiting-approval':
        gate = (f'<section class="approval"><h2>Review before code.</h2><div><p>Does this match what you want built? '
                f'Approve plan {esc(data["revision"])} in the agent conversation, or describe what needs changing.</p>'
                '<p>Opening or interacting with this report does not approve anything. There is no approve button, '
                'agent connection or background implementation.</p></div></section>')
    elif state == 'approved':
        gate = (f'<section class="approval"><h2>Recorded approval reference</h2><div><p>{esc(data["approval"]["record"])}</p>'
                f'<blockquote>{esc(data["approval"]["response"])}</blockquote><p>This renderer does not authenticate the approving '
                'user or grant permission. Reconcile with the actual task record.</p></div></section>')
    else:
        gate = ('<section class="approval"><h2>No implementation permission</h2><div><p>This view alone authorizes no code changes. '
                'Resolve any decisions and use the workflow approval gate before substantive implementation.</p></div></section>')
    viewer_note = ('<p class="muted">System-font mode. No network assets. A saved projection, not a live repository map.</p>')
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; script-src 'sha256-{script_hash}'; style-src 'unsafe-inline'; img-src 'none'; connect-src 'none'; font-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>{esc(data['title'])}</title><style>{css}</style></head><body><main>
<header><div class="mast"><strong>{esc(data['snapshot']['repository'])}</strong><span>Plan {esc(data['revision'])}</span></div>
<h1>{esc(data['title'])}</h1><p class="status {state}">{esc(status)}</p><p class="lead">{esc(data['understanding'])}</p></header>
{issues}<section class="review" aria-label="Flowchart review">{controls}<div class="figures">{''.join(graph_html(g) for g in ordered)}</div></section>
{comparison}<section class="boundaries"><h2>What will not change</h2><ul>{bounds}</ul></section>
<div class="two-col"><section><h2>Changes and cleanup</h2><ul class="plain">{task_summary or '<li>Inspection only; no implementation tasks.</li>'}</ul></section>
<section><h2>How completion will be checked</h2><ul class="plain">{acceptance or '<li>No implementation acceptance criteria for this inspection.</li>'}</ul></section></div>
{gate}<details class="appendix" id="technical-details"><summary>Technical evidence and task details</summary><div class="appendix-body">
<section><h2>Requested outcome</h2><ul class="plain">{req or '<li>No implementation requirements in this inspection.</li>'}</ul></section>
<section><h2>Changes and mapped tasks</h2><div class="table-scroll"><table><thead><tr><th>Task</th><th>Work and affected areas</th><th>Traceability</th><th>Depends on</th></tr></thead><tbody>{task_rows or '<tr><td colspan="4">Inspection only; no implementation tasks.</td></tr>'}</tbody></table></div></section>
<section><h2>Evidence and limits</h2>{ev}</section>{''.join(graph_records(g) for g in data['graphs'])}
<details class="snapshot"><summary>Inspected snapshot and supplied-source fingerprints</summary><p>{esc(data['snapshot']['repository'])} · {esc(data['snapshot'].get('branch', 'No branch recorded'))}</p>
<p>{esc(data['snapshot']['basis'])}</p><p>Generated {esc(manifest['generated_utc'])}. Hashes cover only these supplied files, including local changes. They do not prove complete code coverage or correctness.</p><div class="table-scroll"><table><thead><tr><th>ID</th><th>Source</th><th>Role</th><th>SHA-256 prefix</th></tr></thead><tbody>{source_rows}</tbody></table></div></details>
</div></details>{viewer_note}<footer>Local HTML + SVG · no external assets, uploads or approval actions · edit source JSON and render a new revision</footer>
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
