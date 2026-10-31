"""Optional, inert UI screen flow inside the existing review. No application code execution.

Input is a bounded screen description or a local PNG capture, never HTML, CSS or a URL.
The main renderer supplies its validation and geometry functions to avoid a second graph engine.
"""
from __future__ import annotations

import base64
import html
import importlib.util
import struct
import zlib
from pathlib import Path

MAX_CAPTURE = 2_000_000
MAX_CAPTURE_TOTAL = 4_000_000
MODES = {'unselected', 'behaviour-only', 'blocked', 'functionality-only', 'approved-kit', 'design-authoring'}
ELEMENTS = {'heading', 'text', 'checkbox', 'input', 'button', 'message'}


def bindings_module():
    spec = importlib.util.spec_from_file_location('workflow_kit_bindings', Path(__file__).with_name('kit_bindings.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def kit_records(ui, root, sources):
    module = bindings_module()
    return module.snapshot_records(module.resolve(ui, root, sources), sources)


def png_bytes(path: Path) -> tuple[bytes, int, int]:
    if path.is_symlink() or path.stat().st_size > MAX_CAPTURE:
        raise ValueError('UI capture must be an ordinary PNG of at most 2 MB')
    raw = path.read_bytes()
    if len(raw) > MAX_CAPTURE or not raw.startswith(b'\x89PNG\r\n\x1a\n'):
        raise ValueError('UI capture is not a supported PNG')
    offset, size, ended, has_pixels = 8, None, False, False
    while offset + 12 <= len(raw):
        length = struct.unpack('>I', raw[offset:offset+4])[0]
        kind = raw[offset+4:offset+8]
        end = offset + 12 + length
        if end > len(raw):
            raise ValueError('Truncated UI capture')
        body = raw[offset+8:offset+8+length]
        crc = struct.unpack('>I', raw[offset+8+length:end])[0]
        if zlib.crc32(kind + body) & 0xffffffff != crc:
            raise ValueError('Invalid UI capture checksum')
        if size is None:
            if kind != b'IHDR' or length != 13:
                raise ValueError('UI capture needs a PNG header')
            size = struct.unpack('>II', body[:8])
            if not all(0 < n <= 8192 for n in size) or size[0]*size[1] > 16_777_216:
                raise ValueError('UI capture dimensions exceed the supported limit')
        elif kind == b'IHDR':
            raise ValueError('Duplicate PNG header')
        if kind == b'IDAT' and length:
            has_pixels = True
        if kind == b'acTL':
            raise ValueError('Use a static UI capture, not an animated image')
        offset = end
        if kind == b'IEND':
            if length or offset != len(raw):
                raise ValueError('Unexpected trailing capture data')
            ended = True
            break
    if not ended or size is None or not has_pixels:
        raise ValueError('Incomplete UI capture')
    return raw, *size


def record(value: object, name: str, sources: dict, api) -> None:
    if not isinstance(value, dict) or value.get('source') not in sources:
        raise ValueError(f'{name} needs an actual supplied source reference')
    for field in ('locator', 'summary'):
        api.text(value.get(field), name + '.' + field)


def validate(data: dict, root: Path, sources: dict, api) -> None:
    ui = data.get('ui_review')
    if ui is None:
        return
    if not isinstance(ui, dict):
        raise ValueError('ui_review must be an object')
    allowed = {'title','summary','kind','mode','authority','preview','acceptance','width','height',
               'screens','transitions','decisions','open_first','limit','kit_binding'}
    if set(ui) - allowed:
        raise ValueError('Unknown UI review fields; raw HTML/CSS/URLs are not supported')
    if any(g['id'] == 'ui-preview' for g in data['graphs']):
        raise ValueError('ui-preview is reserved for the optional screen view')
    for field in ('title','summary','limit'):
        api.text(ui.get(field), 'ui_review.' + field)
    if ui.get('kind') not in ('application','illustration') or ui.get('mode') not in MODES:
        raise ValueError('UI review needs an explicit kind and design mode')
    if type(ui.get('open_first', False)) is not bool:
        raise ValueError('ui_review.open_first must be boolean')
    record(ui.get('authority'), 'UI authority', sources, api)
    if ui['authority'].get('status') not in ('unconfirmed','confirmed'):
        raise ValueError('UI authority needs confirmed/unconfirmed status')
    record(ui.get('preview'), 'Preview authority', sources, api)
    if ui['preview'].get('status') not in ('proposed','authorised'):
        raise ValueError('Preview authority needs proposed/authorised status')
    api.text(ui['preview'].get('destination'), 'preview.destination')
    acceptance = ui.get('acceptance')
    if not isinstance(acceptance, dict) or acceptance.get('status') not in ('pending','accepted'):
        raise ValueError('UI acceptance needs pending/accepted status')
    api.text(acceptance.get('summary'), 'UI acceptance summary')
    if acceptance['status'] == 'accepted':
        record(acceptance, 'UI acceptance', sources, api)
    if ui['kind'] == 'illustration' and acceptance['status'] != 'pending':
        raise ValueError('An illustrative sample cannot claim application design acceptance')
    if ui['mode'] == 'unselected' and ui['authority']['status'] == 'confirmed':
        raise ValueError('An unselected UI mode cannot be confirmed')
    decisions = api.indexed(ui.get('decisions'), 'UI decisions')
    if len(decisions) > 8:
        raise ValueError('Keep at most eight relevant UI decisions in this view')
    screens = api.indexed(ui.get('screens'), 'UI screens', empty=False)
    if len(screens) > 6:
        raise ValueError('Split UI flows with more than six screens')
    for d in decisions.values():
        for key in ('title','question'):
            api.text(d.get(key), 'UI decision.'+key, 500)
        api.references(d.get('screens'), screens, 'decision.screens', required=True)
        options = d.get('options')
        if not isinstance(options,list) or not 2 <= len(options) <= 4 or len(set(options)) != len(options):
            raise ValueError('UI decisions need two to four distinct text options')
        for option in options:
            api.text(option,'decision.option',180)
        if d.get('status') not in ('open','selected','deferred'):
            raise ValueError('UI decision status is invalid')
        if d['status'] == 'selected':
            if d.get('selection') not in options:
                raise ValueError('Selected decision must name one of its options')
            record(d, 'Selected UI decision', sources, api)
        elif 'selection' in d:
            raise ValueError('Unsettled decisions cannot imply a selected option')
        if d['status'] == 'deferred':
            api.text(d.get('reason'), 'Deferred UI decision reason')
    requirements = {r['id']:r for r in data['requirements']}
    evidence = {r['id']:r for r in data['evidence']}
    tasks = {r['id']:r for r in data['tasks']}
    total = 0
    geometry = []
    for key,s in screens.items():
        allowed_screen = {'id','title','description','state','x','y','width','height','representation',
                          'content','capture','sources','requirements','evidence','tasks','decisions','markers','elements','capture_context'}
        if set(s)-allowed_screen:
            raise ValueError('Unknown screen fields; executable markup/styles are prohibited')
        api.text(s.get('title'), 'screen.title', 48)
        api.text(s.get('description'), 'screen.description', 700)
        if s.get('state') not in ('current','proposed'):
            raise ValueError('UI screen needs current/proposed state')
        if data['mode'] == 'current' and s['state'] != 'current':
            raise ValueError('Current inspection cannot include proposed UI screens')
        api.references(s.get('sources'), sources, 'screen.sources', required=True)
        api.references(s.get('decisions'), decisions, 'screen.decisions')
        for field,lookup in [('requirements',requirements),('evidence',evidence),('tasks',tasks)]:
            api.references(s.get(field),lookup,'screen.'+field,
                required=ui['kind']=='application' and (field!='tasks' or s['state']=='proposed'))
        for decision in s['decisions']:
            if key not in decisions[decision]['screens']:
                raise ValueError('Screen decision mapping disagrees with decision.screens')
        for field,low,high in [('width',280,560),('height',280,720)]:
            api.coordinate(s.get(field),'screen.'+field,low,high)
        if len(s['title']) * 8 > s['width'] - 145 or any(c in s['title'] for c in '\n\r'):
            raise ValueError('Screen title does not fit beside Inspect; shorten it or widen the screen')
        if s.get('representation') == 'capture':
            if 'content' in s or s.get('capture') not in s['sources']:
                raise ValueError('Captured screen needs a listed source and no invented controls')
            src = sources[s['capture']]
            if src['role'] != 'ui-capture' or not src['path'].lower().endswith('.png'):
                raise ValueError('Screen capture must reference a local ui-capture PNG source')
            raw,_,_ = png_bytes(api.safe_source(root,src['path']))
            total += len(raw)
            markers = api.rows(s.get('markers', []), 'capture.markers')
            if len(markers) > 8:
                raise ValueError('Use at most eight capture decision markers')
            for marker in markers:
                if not isinstance(marker, dict):
                    raise ValueError('Capture marker must be an object')
                if set(marker) == {'decision', 'position'}:
                    if marker['decision'] not in s['decisions']:
                        raise ValueError('Capture marker must name a mapped decision')
                elif set(marker) == {'element', 'position'}:
                    elements = s.get('elements', [])
                    if not isinstance(elements, list) or marker['element'] not in {e.get('id') for e in elements if isinstance(e, dict)}:
                        raise ValueError('Capture marker must name a selected element')
                else:
                    raise ValueError('Capture marker needs a decision or element and position')
                position = marker['position']
                if (not isinstance(position, list) or len(position) != 2 or
                    any(type(n) not in (int, float) or not 0 <= n <= 1 for n in position)):
                    raise ValueError('Capture marker position uses two fractions from 0 to 1')
        elif s.get('representation') == 'schematic':
            if 'capture' in s or 'markers' in s:
                raise ValueError('Schematic screen cannot claim a captured source')
            content = api.rows(s.get('content'),'screen.content',empty=False)
            if len(content)>6:
                raise ValueError('Use at most six controls/text blocks in one schematic screen')
            if s['height'] < 120 + 48*len(content):
                raise ValueError('Screen height is too small; expand it, do not shrink text')
            for c in content:
                if set(c)-{'kind','label','value','checked','disabled','decision'} or c.get('kind') not in ELEMENTS:
                    raise ValueError('Only structured inert schematic controls are supported')
                api.text(c.get('label'),'control.label',42)
                if any(ch in c['label'] for ch in '\n\r'):
                    raise ValueError('Use a single-line schematic label')
                available = s['width'] - (86 if c.get('decision') else 48) - (26 if c['kind']=='checkbox' else 0)
                estimate = 9 if c['kind']=='heading' else 7
                if len(c['label']) * estimate > available:
                    raise ValueError('Schematic label will not fit; widen or shorten it')
                if c.get('value') is not None:
                    api.text(c['value'],'control.value',42)
                    if any(ch in c['value'] for ch in '\n\r') or len(c['value'])*7 > s['width']-64:
                        raise ValueError('Schematic field value does not fit')
                for flag in ('checked','disabled'):
                    if flag in c and type(c[flag]) is not bool:
                        raise ValueError('Control flags must be boolean')
                if 'decision' in c and c['decision'] not in s['decisions']:
                    raise ValueError('Control decision is not mapped to this screen')
        else:
            raise ValueError('Use a captured PNG or an explicitly labelled schematic')
        geometry.append({**{f:s[f] for f in ('id','x','y','width','height')},
                         'label':s['title'], 'note':'','shape':'group'})
    if total > MAX_CAPTURE_TOTAL:
        raise ValueError('UI captures exceed the 4 MB total report budget')
    for d in decisions.values():
        if any(d['id'] not in screens[s]['decisions'] for s in d['screens']):
            raise ValueError('Decision must be mapped on all referenced screens')
    transitions = api.rows(ui.get('transitions'), 'UI transitions')
    for e in transitions:
        if set(e)-{'from','to','label','points','label_position'}:
            raise ValueError('Unknown UI transition fields')
        if e.get('from') not in screens or e.get('to') not in screens:
            raise ValueError('Unknown UI transition endpoint')
        api.text(e.get('label'),'UI transition label',14)
    graph={'width':ui.get('width'),'height':ui.get('height'),'purpose':'flow',
           'tab':'UI screens','description':ui['summary'], 'nodes':geometry,'edges':transitions}
    api.validate_geometry(graph,{n['id']:n for n in geometry})
    if any(screen['state']=='proposed' for screen in screens.values()) and ui['preview']['status']!='authorised':
        raise ValueError('Proposed screen drawings need explicit preview permission and recorded preview authority, including drafts')
    if ui['mode']=='approved-kit' and any(screen['representation']!='capture' for screen in screens.values()):
        raise ValueError('Approved-kit review needs actual component captures; schematics do not prove its appearance')
    if acceptance['status']=='accepted' and (ui['authority']['status']!='confirmed' or ui['mode']=='unselected'
                                           or any(d['status']!='selected' for d in decisions.values())):
        raise ValueError('An accepted design cannot retain an unselected source or unresolved design decisions')
    if ui['kind']=='application' and data['state'] in ('awaiting-approval','approved'):
        if ui['mode']=='unselected' or ui['authority']['status']!='confirmed' or ui['preview']['status']!='authorised':
            raise ValueError('Approval-ready UI work needs confirmed mode/source and preview authority')
        if any(d['status']=='open' for d in decisions.values()):
            raise ValueError('Resolve blocking UI decisions before approval-ready output')


    resolved = bindings_module().resolve(ui, root, sources)
    if ui['kind']=='application' and (data['state'] in ('awaiting-approval','approved') or acceptance['status']=='accepted'):
        if ui['mode'] != 'approved-kit' or resolved is None:
            raise ValueError('Strict kit-only UI: approval-ready application screens need approved-kit binding and real selected captures; no plain-HTML/design-authoring fallback.')



def screen_svg(screen: dict, root: Path, sources: dict, api, suffix: str) -> str:
    """A static screen view, reused verbatim in overview and enlarged details."""
    e=html.escape
    width,height=screen['width'],screen['height']
    sid='ui-'+suffix+'-'+screen['id']
    parts=[f'<svg class="ui-screen" xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="{sid}-title {sid}-desc">',
           f'<title id="{sid}-title">{e(screen["title"])}</title><desc id="{sid}-desc">{e(screen["description"])}</desc>',
           f'<rect class="ui-screen-paper" x="1" y="1" width="{width-2}" height="{height-2}" rx="6"/>',
           f'<path class="ui-divider" d="M 1 48 H {width-1}"/>',
           f'<text class="ui-screen-caption" x="20" y="30">{e(screen["title"])}</text>']
    if screen['representation']=='capture':
        raw,iw,ih=png_bytes(api.safe_source(root,sources[screen['capture']]['path']))
        value=base64.b64encode(raw).decode('ascii')
        parts.append(f'<image x="8" y="56" width="{width-16}" height="{height-86}" preserveAspectRatio="xMidYMin meet" '
                     f'href="data:image/png;base64,{value}"/>')
        scale = min((width-16)/iw, (height-86)/ih)
        left, top = 8 + (width-16-iw*scale)/2, 56
        for marker in screen.get('markers', []):
            dx,dy=marker['position'];mx=left+dx*iw*scale;my=top+dy*ih*scale
            d=e(marker.get('decision', marker.get('element')))
            target='ui-decision-'+d if 'decision' in marker else 'ui-element-'+e(screen['id'])+'-'+d
            label = "Review decision " if "decision" in marker else "Inspect kit element "
            parts.append(f'<a href="#{target}" aria-label="{label}{d}"><circle class="ui-marker" cx="{mx:g}" cy="{my:g}" r="13"/>'
                         f'<text class="ui-marker-text" x="{mx:g}" y="{my+4:g}" text-anchor="middle">{d}</text></a>')
    else:
        y=86
        for c in screen['content']:
            label=e(c['label']);kind=c['kind'];x=24
            if kind=='heading':
                parts.append(f'<text class="ui-control-heading" x="{x}" y="{y}">{label}</text>')
            elif kind=='checkbox':
                parts.append(f'<rect class="ui-checkbox" x="{x}" y="{y-14}" width="16" height="16" rx="1"/>')
                if c.get('checked'):
                    parts.append(f'<path class="ui-check" d="M {x+3} {y-6} l 4 4 l 6 -9"/>')
                parts.append(f'<text class="ui-control-text" x="{x+26}" y="{y}">{label}</text>')
            elif kind=='input':
                parts.append(f'<text class="ui-control-small" x="{x}" y="{y-8}">{label}</text>'
                             f'<rect class="ui-field" x="{x}" y="{y}" width="{width-48}" height="28" rx="2"/>'
                             f'<text class="ui-control-text" x="{x+8}" y="{y+19}">{e(c.get("value",""))}</text>')
            elif kind=='button':
                button_width=min(width-48,max(120,len(c['label'])*8+32))
                disabled=' ui-disabled' if c.get('disabled') else ''
                parts.append(f'<rect class="ui-button{disabled}" x="{x}" y="{y-20}" width="{button_width}" height="36" rx="3"/>'
                             f'<text class="ui-control-text" text-anchor="middle" x="{x+button_width/2}" y="{y+3}">{label}</text>')
            elif kind=='message':
                parts.append(f'<path class="ui-message-rule" d="M {x} {y-16} V {y+8}"/>'
                             f'<text class="ui-control-text" x="{x+12}" y="{y}">{label}</text>')
            else:
                parts.append(f'<text class="ui-control-small" x="{x}" y="{y}">{label}</text>')
            if c.get('decision'):
                d=e(c['decision']);cx=width-28
                parts.append(f'<a href="#ui-decision-{d}" aria-label="Review decision {d}"><circle class="ui-marker" cx="{cx}" cy="{y-5}" r="13"/>'
                             f'<text class="ui-marker-text" x="{cx}" y="{y-1}" text-anchor="middle">{d}</text></a>')
            y+=48
    caption=('Capture · selected kit references' if screen.get('elements') else 'Capture · kit provenance not established') if screen['representation']=='capture' else 'Layout sketch · not a component capture'
    parts.append(f'<text class="ui-footnote" x="20" y="{height-16}">{caption}</text></svg>')
    return ''.join(parts)


def render(ui: dict, root: Path, sources: dict, api) -> str:
    e=html.escape
    bindings = bindings_module()
    resolved = bindings.resolve(ui, root, sources)
    w,h=ui['width'],ui['height']
    routes=[f'<svg class="ui-routes" width="{w}" height="{h}" viewBox="0 0 {w} {h}" aria-hidden="true">'
            '<defs><marker id="ui-flow-arrow" viewBox="0 0 10 8" refX="9" refY="4" markerWidth="9" markerHeight="7" orient="auto">'
            '<path d="M0 0 L10 4 L0 8 Z"/></marker></defs>']
    for edge in ui['transitions']:
        routes.append(f'<path class="connector" d="{api.elbow_path(edge["points"])}" marker-end="url(#ui-flow-arrow)"/>')
        x,y,bw,bh=api.edge_label_box(edge);cx,baseline=edge['label_position']
        routes.append(f'<g class="arrow-label"><rect x="{x:g}" y="{y:g}" width="{bw:g}" height="{bh:g}"/>'
                      f'<text class="edge-label" x="{cx}" y="{baseline}" text-anchor="middle">{e(edge["label"].upper())}</text></g>')
    routes.append('</svg>')
    cards=[];details=[]
    for s in ui['screens']:
        detail='ui-detail-'+s['id']
        cards.append(f'<article class="ui-screen-node" id="ui-screen-{e(s["id"])}" '
                     f'style="left:{s["x"]}px;top:{s["y"]}px;width:{s["width"]}px;height:{s["height"]}px">'
                     f'{screen_svg(s,root,sources,api,"board")}<a class="ui-inspect" href="#{detail}">Inspect screen ↗</a></article>')
        refs=api.links(s['sources'],'s')
        full_screen=screen_svg(s,root,sources,api,'detail')
        if s['representation']=='capture':
            capture,iw,ih=png_bytes(api.safe_source(root,sources[s['capture']]['path']))
            full_screen=(f'<img class="ui-capture-detail" width="{iw}" height="{ih}" alt="{e(s["description"])}" '
                         f'src="data:image/png;base64,{base64.b64encode(capture).decode("ascii")}"/>')
        details.append(f'<details id="{detail}" class="ui-screen-detail"><summary>{e(s["title"])} — screen and sources</summary>'
                       f'<p>{e(s["description"])}</p>{full_screen}'
                       f'{bindings.selection_html(s, resolved, sources, api)}'
                       f'<p class="ui-evidence">State: {e(s["state"])}. Sources: {refs}. '
                       f'Requirements: {api.links(s["requirements"],"r")}. Tasks: {api.links(s["tasks"],"t")}.</p></details>')
    decisions=[]
    for d in ui['decisions']:
        options=' / '.join(e(o) for o in d['options'])
        state='Open — owner decision needed' if d['status']=='open' else 'Deferred — design remains unfinished' if d['status']=='deferred' else 'Selected: '+e(d['selection'])
        record_text=('<p>'+e(d.get('reason',''))+'</p>') if d['status']=='deferred' else ''
        if d['status']=='selected':
            record_text=f'<p>Recorded at {api.links([d["source"]],"s")}: {e(d["locator"])}. {e(d["summary"])}</p>'
        decisions.append(f'<article id="ui-decision-{e(d["id"])}" class="ui-decision"><h3>{e(d["id"])} · {e(d["title"])}</h3>'
                         f'<p>{e(d["question"])}</p><p>Alternatives: {options}.</p><p><strong>{state}</strong></p>{record_text}</article>')
    illustration=('<p class="ui-notice"><strong>Illustrative UI example — outside this report’s implementation scope.</strong> '
                  'These are fictional screens to demonstrate the report format, not an approved project kit.</p>') if ui['kind']=='illustration' else ''
    authority=ui['authority'];preview=ui['preview']
    legacy_note = ('<p class="ui-notice"><strong>Historical/draft UI mode — not current implementation authority.</strong> '
                   'Strict kit reuse now prohibits agent-authored application HTML, CSS and inline styles. '
                   'No plain-markup or design-authoring fallback is permitted.</p>') if ui['mode'] in {'functionality-only','design-authoring'} else ''
    source_note=f'{e(authority["summary"])} Reference: {api.links([authority["source"]],"s")}, {e(authority["locator"])}.'
    first=ui['screens'][0]['id']
    return (f'<figure class="panel ui-review" id="panel-ui-preview"><div class="figure-head"><h2>{e(ui["title"])}</h2>'
            '<span>screens · interaction · design</span></div>'
            f'<p class="figure-description">{e(ui["summary"])}</p>{illustration}{legacy_note}'
            f'<div class="ui-authority"><p><strong>Design mode:</strong> {e(ui["mode"])} · {e(authority["status"])}.</p>'
            f'<p>{source_note}</p><p><strong>Preview:</strong> {e(preview["destination"])} — {e(preview["status"])}. '
            f'{e(preview["summary"])}</p><p><strong>Design acceptance:</strong> {e(ui["acceptance"]["status"])}. '
            f'{e(ui["acceptance"]["summary"])}</p></div>'
            '<p class="hint">Screen frames are connected by actions. Markers refer to design decisions below. '
            f'<a href="#ui-screen-{e(first)}">Go to first screen</a>. Scroll at readable size; Fit is an overview.</p>'
            '<noscript><p class="hint">Screen Fit needs JavaScript; use normal-size scrolling and the screen details below.</p></noscript>'
            f'<div class="canvas ui-canvas" tabindex="0" role="region" aria-label="UI screen flow, scroll to explore" '
            f'data-start-id="ui-screen-{e(first)}"><div class="ui-scaled" style="--ui-width:{w}px;--ui-height:{h}px">'
            f'<div class="ui-board">{"".join(routes)}{"".join(cards)}</div></div></div>'
            f'<figcaption>{e(ui["limit"])} Selecting or inspecting a screen does not record approval or change the application.</figcaption>'
            '<section class="ui-decisions"><h2>Design decisions attached to the screens</h2>'+''.join(decisions)+'</section>'
            '<details class="ui-screen-index"><summary>Inspect screens and their sources</summary>'+''.join(details)+'</details>'
            '</figure>')
