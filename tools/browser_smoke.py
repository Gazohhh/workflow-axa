#!/usr/bin/env python3
"""Optional local report checks using already installed Playwright and Chromium.

Never installs a browser or modifies a user's repository. Outputs to a new QA directory.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--no-sandbox', action='store_true', help='Only for a trusted disposable container that requires it.')
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error('Choose a new output directory.')
    if not args.browser.is_file():
        parser.error('Supply an already installed Chromium executable.')
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('NOT RUN: Playwright not installed; no installation attempted.', file=sys.stderr)
        return 2
    args.output.mkdir(parents=True)
    checks, errors, requests = [], [], []
    limits = ['Default desktop opener and Claude/Codex skill invocation/behavior were not tested.',
              'Geometry and browser assertions do not prove semantic completeness, real approval or a complete accessibility audit.']
    try:
        spec = importlib.util.spec_from_file_location('qa_renderer', ROOT/'skills/codebase-map/scripts/render_report.py')
        renderer = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(renderer)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)/'fixture'
            shutil.copytree(ROOT/'skills/codebase-map/examples', source)
            data = renderer.load_json(source/'review.json')
            content = renderer.render(data, source, source/'review.json')
            html = args.output/'tested-report.html'
            html.write_text(content, encoding='utf-8')
            assert renderer.check_report(html, source) == []
            checks.append('Supplied source/input fingerprints match before browser inspection')
            with sync_playwright() as p:
                browser = p.chromium.launch(executable_path=str(args.browser), headless=True, args=['--no-sandbox'] if args.no_sandbox else [])
                version = browser.version
                context = browser.new_context(viewport={'width':1440,'height':1100}, offline=True)
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('request', lambda request: requests.append(request.url))
                try:
                    page.goto(html.resolve().as_uri(), wait_until='load', timeout=15000)
                    direct_file = True
                    checks.append('Direct local file:// report navigation succeeded offline')
                except Exception as exc:
                    page.close()
                    page = context.new_page()
                    page.on('pageerror', lambda error: errors.append(str(error)))
                    page.on('request', lambda request: requests.append(request.url))
                    page.set_content(content, wait_until='load')
                    direct_file = False
                    limits.append('Direct local navigation unavailable; identical HTML tested through set_content: '+str(exc)[:160])
                assert page.locator('.panel:visible').get_attribute('id') == 'panel-proposed'
                assert page.locator('.map').count() == 3
                assert page.locator('form, button[type=submit], input[type=submit]').count() == 0
                assert 'implementation not authorized' in page.locator('.status').inner_text()
                checks.append('Feature flow is default; pending approval is visible and no approval controls exist')
                assert page.evaluate('document.querySelector("#technical-details").open === false')
                assert page.get_by_role('heading', name='What will not change').is_visible()
                assert page.get_by_role('heading', name='How completion will be checked').is_visible()
                checks.append('Technical details are secondary; exclusions and acceptance stay visible')
                for view in ('proposed','current','build'):
                    page.locator(f'label[for="view-{view}"]').click()
                    assert page.locator('.panel:visible').count() == 1
                    panel = page.locator(f'#panel-{view}')
                    assert panel.is_visible()
                    geometry_errors = panel.locator('.node').evaluate_all('''nodes => nodes.flatMap(node => {
                      const shape = node.querySelector('.node-shape');
                      const box = shape.getBBox();
                      return [...node.querySelectorAll('text')].filter(text => {
                        const b=text.getBBox();
                        if(b.x<box.x || b.y<box.y || b.x+b.width>box.x+box.width || b.y+b.height>box.y+box.height) return true;
                        if(shape.tagName==='polygon') return [[b.x,b.y],[b.x+b.width,b.y],[b.x,b.y+b.height],[b.x+b.width,b.y+b.height]].some(p => !shape.isPointInFill(new DOMPoint(...p)));
                        return false;
                      }).map(text => ({node:node.dataset.id,text:text.textContent}));
                    })''')
                    assert not geometry_errors, geometry_errors
                    accessible = panel.locator('svg').evaluate('''svg => svg.firstElementChild.tagName==='title' && svg.getAttribute('role')==='img' && svg.getAttribute('aria-labelledby').split(' ').every(id => document.getElementById(id)?.textContent.trim())''')
                    assert accessible
                    panel.screenshot(path=str(args.output/f'{view}.png'))
                checks.append('All three views switch correctly and every rendered label fits its node/diamond')
                checks.append('Each SVG has a nonempty accessible title/description and unique IDs')
                duplicate_ids = page.evaluate('''() => { const ids=[...document.querySelectorAll('[id]')].map(e=>e.id); return ids.filter((id,i)=>ids.indexOf(id)!==i); }''')
                assert not duplicate_ids, duplicate_ids
                page.locator('label[for="view-proposed"]').click()
                canvas = page.locator('#panel-proposed .canvas')
                scale = page.locator('#panel-proposed svg').evaluate('svg => svg.getScreenCTM().a')
                assert abs(scale-1) < .01, scale
                font = page.locator('#panel-proposed .node-title').first.evaluate('text=>getComputedStyle(text).fontSize')
                assert font == '18px', font
                checks.append('Default diagram uses natural size with 18px node titles, not fixed-height fit')
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                page.screenshot(path=str(args.output/'desktop.png'), full_page=True)
                page.locator('.review').screenshot(path=str(args.output/'flowchart.png'))
                checks.append('Desktop report has no document-wide horizontal overflow')
                canvas.focus()
                canvas.press('+')
                assert page.locator('#zoom-125').is_checked()
                canvas.press('f')
                assert page.locator('#zoom-fit').is_checked()
                canvas.press('0')
                assert page.locator('#zoom-100').is_checked()
                page.locator('label[for="zoom-150"]').click()
                assert page.locator('#zoom-150').is_checked()
                page.locator('label[for="zoom-100"]').click()
                checks.append('Native zoom controls and progressive keyboard shortcuts operate')
                page.locator('.comparison a[href="#e-E3"]').first.click()
                assert page.locator('#technical-details').get_attribute('open') is not None
                assert page.locator('#e-E3').is_visible()
                page.locator('#e-E3 a[href="#s-S4"]').click()
                assert page.locator('.snapshot').get_attribute('open') is not None
                checks.append('Evidence and source links reveal the relevant nested details')
                page.locator('#technical-details > summary').click()
                page.set_viewport_size({'width':390,'height':844})
                page.locator('.review').scroll_into_view_if_needed()
                assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
                assert canvas.evaluate('el=>el.scrollWidth > el.clientWidth')
                page.wait_for_timeout(100)
                assert canvas.evaluate('el=> {const n=document.getElementById(el.dataset.startId).getBoundingClientRect();const c=el.getBoundingClientRect();return n.right>c.left && n.left<c.right;}')
                checks.append('Narrow-screen initial view shows the entry node instead of empty canvas')
                canvas.focus(); canvas.press('ArrowRight'); page.wait_for_timeout(100)
                assert canvas.evaluate('el=>el.scrollLeft') > 0
                canvas.evaluate('el=>el.scrollLeft=0')
                box = canvas.bounding_box()
                page.mouse.move(box['x']+260, box['y']+90)
                page.mouse.down(); page.mouse.move(box['x']+100, box['y']+90); page.mouse.up()
                assert canvas.evaluate('el=>el.scrollLeft') > 0
                checks.append('Narrow viewport scrolls only the diagram; keyboard and mouse pan preserve readable text')
                page.locator('label[for="zoom-fit"]').click()
                assert page.locator('#panel-proposed svg').bounding_box()['width'] <= 351
                page.locator('label[for="zoom-100"]').click()
                page.wait_for_timeout(100)
                assert canvas.evaluate('el=> {const n=document.getElementById(el.dataset.startId).getBoundingClientRect();const c=el.getBoundingClientRect();return n.right>c.left && n.left<c.right;}')
                page.screenshot(path=str(args.output/'mobile.png'), full_page=True)
                checks.append('Fit is optional on mobile and 100% restores the readable canvas')
                page.emulate_media(media='print')
                assert page.locator('.panel:visible').count() == 3
                page.emulate_media(media='screen')
                checks.append('Print presentation includes every diagram, not only the selected tab')
                nojs_context = browser.new_context(java_script_enabled=False, offline=True, viewport={'width':1024,'height':900})
                nojs = nojs_context.new_page()
                if direct_file:
                    nojs.goto(html.resolve().as_uri(), wait_until='load')
                else:
                    nojs.set_content(content, wait_until='load')
                assert nojs.locator('#panel-proposed').is_visible()
                nojs.locator('label[for="view-current"]').click()
                assert nojs.locator('#panel-current').is_visible()
                nojs.locator('label[for="zoom-125"]').click()
                assert nojs.locator('#zoom-125').is_checked()
                nojs.locator('#technical-details > summary').click()
                assert nojs.locator('#e-E1').is_visible()
                nojs.set_viewport_size({'width':390,'height':844})
                nojs.locator('#panel-current .hint a').click()
                assert nojs.locator('#panel-current .canvas').evaluate('el=> {const n=document.getElementById(el.dataset.startId).getBoundingClientRect();const c=el.getBoundingClientRect();return n.right>c.left && n.left<c.right;}')
                nojs_context.close()
                checks.append('With JavaScript disabled, diagram selection, zoom and technical disclosure still work')
                payload = '</script><img src="https://invalid.example/x" onerror="window.__injected=true"><script>window.__injected=true</script>'
                data['understanding'] = payload
                (source/'review.json').write_text(json.dumps(data), encoding='utf-8')
                hostile = renderer.render(data, source, source/'review.json')
                page.close()
                page = context.new_page()
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('request', lambda request: requests.append(request.url))
                page.set_content(hostile, wait_until='load')
                assert page.locator('img').count() == 0
                assert page.evaluate('window.__injected === undefined')
                assert '<img' in page.locator('.lead').inner_text()
                network = [url for url in requests if url.startswith(('http:', 'https:'))]
                assert not network, network
                assert not errors, errors
                checks.append('Script-like input remains inert; no external requests or page errors')
                browser.close()
        result = {'status':'PASS', 'browser':version, 'checks':checks, 'direct_file_navigation':direct_file,
                  'external_requests':network, 'page_errors':errors, 'limits':limits}
        (args.output/'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        print(f'PASS: {len(checks)} browser checks; evidence: {args.output.resolve()}')
        return 0
    except Exception as exc:
        result = {'status':'FAIL', 'checks_completed':checks, 'error':str(exc), 'page_errors':errors}
        (args.output/'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
        print(f'FAIL: {exc}; evidence: {args.output.resolve()}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
