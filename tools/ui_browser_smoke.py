#!/usr/bin/env python3
"""Check the additive UI screen-flow report with an already installed browser.

Only trusted bundled fixtures are rendered. No tool installation, app execution,
network, rule activation, approval or existing-output replacement.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
import struct
import sys
import tempfile
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def tiny_png() -> bytes:
    """Small synthetic image, not an application capture or approved design."""
    def chunk(kind: bytes, value: bytes) -> bytes:
        return struct.pack('>I', len(value)) + kind + value + struct.pack('>I', zlib.crc32(kind + value) & 0xffffffff)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 4, 4, 8, 6, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress((b'\0' + b'\x80\x80\x80\xff' * 4) * 4)) + chunk(b'IEND', b''))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--no-sandbox', action='store_true', help='Only in a trusted disposable container that requires it.')
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error('Choose a new output directory; existing evidence is never overwritten.')
    if not args.browser.is_file():
        parser.error('Supply an already installed Chromium executable.')
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('NOT RUN: Playwright is unavailable. No installation attempted.', file=sys.stderr)
        return 2
    spec = importlib.util.spec_from_file_location('ui_smoke_renderer', ROOT/'skills/codebase-map/scripts/render_report.py')
    renderer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(renderer)
    args.output.mkdir(parents=True)
    checks, errors, requests = [], [], []
    result = {'status': 'NOT_VERIFIED', 'checks': checks, 'limits': [
        'No real application, designer acceptance, human usability study or live Claude/Codex run.',
        'These fixtures demonstrate report rendering, not that a project kit exists or its design is approved.',
        'No operating-system default opener or native Windows installation was tested.']}
    try:
        example = ROOT/'skills/codebase-map/examples/ui-review'
        data = renderer.load_json(example/'ui-task-review-r2.json')
        content = renderer.render(data, ROOT, example/'ui-task-review-r2.json')
        output = args.output/'ui-task-review-r2.html'
        output.write_text(content, encoding='utf-8', newline='\n')
        assert renderer.check_report(output, ROOT) == []
        checks.append('Complete synthetic feature report has matching source/input fingerprints')
        additive = renderer.render(renderer.load_json(example/'review-r2.json'), ROOT, example/'review-r2.json')
        (args.output/'review-r2.html').write_text(additive, encoding='utf-8', newline='\n')
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(executable_path=str(args.browser), headless=True,
                args=['--no-sandbox'] if args.no_sandbox else [])
            result['browser'] = browser.version
            context = browser.new_context(viewport={'width':1440,'height':1100}, offline=True)
            def instrument(page):
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.on('request', lambda request: requests.append(request.url))
                return page
            page = instrument(context.new_page())
            try:
                page.goto(output.resolve().as_uri(), wait_until='load', timeout=15000)
                direct = True
            except Exception as exc:
                result['limits'].append('Direct file:// navigation blocked: '+str(exc).splitlines()[0]+'. Identical bytes loaded with networking disabled.')
                page.close(); page = instrument(context.new_page())
                page.set_content(content, wait_until='load'); direct = False
            result['direct_file_navigation'] = direct
            checks.append('Report loaded offline '+('through file://' if direct else 'from identical HTML content'))
            assert page.locator('#panel-ui-preview').is_visible()
            for text in ('What changes','What will not change','Changes and cleanup','How completion will be checked','Technical evidence and task details'):
                assert text in page.locator('body').inner_text()
            assert page.locator('.view-tabs label').count() == 4
            checks.append('UI-first feature sample retains current, proposed, build and all full-report sections')
            assert page.locator('.ui-screen-node').count() == 4
            assert page.locator('.ui-routes .connector').count() == 4
            assert page.locator('.ui-decision').count() == 2
            assert not page.locator('.ui-review button,.ui-review form,.ui-review input,.ui-review iframe').count()
            checks.append('Four inert screen states, four transitions and two owner decisions; no app form or approval action')
            page.screenshot(path=str(args.output/'desktop-top.png'), full_page=False)
            page.locator('.ui-canvas').screenshot(path=str(args.output/'ui-flow.png'))
            # Inspect SVG text in its own screen coordinates, including enlarged disclosures later.
            assert page.locator('.ui-screen-node svg').evaluate_all('''els => els.every(svg => [...svg.querySelectorAll('text')].every(t => {
                const b=t.getBBox();return b.x>=0 && b.y>=0 && b.x+b.width<=svg.viewBox.baseVal.width && b.y+b.height<=svg.viewBox.baseVal.height;
            }))''')
            checks.append('Screen labels remain within readable screen bounds without clipping')
            node = page.locator('.ui-screen-node').first
            width = node.bounding_box()['width']
            page.locator('label[for="zoom-125"]').click()
            assert abs(node.bounding_box()['width']-width*1.25) < 1
            page.locator('label[for="zoom-150"]').click()
            assert abs(node.bounding_box()['width']-width*1.5) < 1
            page.locator('label[for="zoom-100"]').click()
            checks.append('Shared 100/125/150 percent controls scale screen flow without resizing application controls')
            page.locator('.ui-canvas').focus(); page.locator('.ui-canvas').press('f')
            page.wait_for_timeout(50)
            assert page.locator('#zoom-fit').is_checked()
            assert page.locator('.ui-scaled').bounding_box()['width'] <= page.locator('.ui-canvas').bounding_box()['width']+1
            page.locator('.ui-canvas').press('0')
            assert page.locator('#zoom-100').is_checked()
            checks.append('Keyboard Fit and native-size restoration work for the new view')
            page.locator('.ui-inspect').first.click()
            assert page.locator('.ui-screen-index').get_attribute('open') is not None
            detail = page.locator('.ui-screen-detail').first
            assert detail.get_attribute('open') is not None and detail.locator('svg').is_visible()
            checks.append('Inspect screen opens the same screen and sources inside native disclosures')
            detail.locator('a[href="#ui-decision-D1"]').click()
            assert page.url.endswith('#ui-decision-D1')
            assert page.locator('#ui-decision-D1').is_visible()
            checks.append('Decision markers navigate to the relevant choice without submitting approval')
            page.locator('label[for="view-current"]').click()
            assert page.locator('#panel-current').is_visible() and not page.locator('#panel-ui-preview').is_visible()
            page.locator('label[for="view-proposed"]').click()
            assert page.locator('#panel-proposed').is_visible()
            page.locator('label[for="view-build"]').click()
            assert page.locator('#panel-build').is_visible()
            page.locator('label[for="view-ui-preview"]').click()
            checks.append('All original graph views remain available beside UI screens')
            page.set_viewport_size({'width':390,'height':844}); page.wait_for_timeout(100)
            assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
            canvas=page.locator('.ui-canvas')
            assert canvas.evaluate('el=>el.scrollWidth>el.clientWidth')
            canvas.scroll_into_view_if_needed()
            assert canvas.evaluate('el=> {const r=el.getBoundingClientRect(),n=document.getElementById(el.dataset.startId).getBoundingClientRect();return n.right>r.left&&n.left<r.right;}')
            page.screenshot(path=str(args.output/'mobile-ui.png'), full_page=False)
            canvas.focus(); canvas.press('ArrowRight'); page.wait_for_timeout(100)
            assert canvas.evaluate('el=>el.scrollLeft')>0
            checks.append('Mobile keeps readable screens in a scrollable board without document overflow')
            page.locator('label[for="zoom-fit"]').click();page.wait_for_timeout(100)
            assert page.locator('.ui-scaled').bounding_box()['width'] <= canvas.bounding_box()['width']+1
            page.locator('label[for="zoom-100"]').click()
            page.evaluate('scrollTo(0,0)'); page.screenshot(path=str(args.output/'mobile-top.png'))
            checks.append('Mobile Fit is optional and full-size view is recoverable')
            # The supplied rules report retains its original default view and sections.
            restored=instrument(context.new_page());restored.set_content(additive, wait_until='load')
            assert restored.locator('#view-proposed').is_checked()
            assert restored.locator('#panel-proposed').is_visible()
            assert not restored.locator('#panel-ui-preview').is_visible()
            assert restored.locator('h1').inner_text()=='Shared rules load in every ordinary session, both projects'
            assert restored.locator('.warning').count()>=2
            checks.append('Additive R2 sample preserves original heading, draft warnings and proposed default view')
            restored.locator('label[for="view-ui-preview"]').click()
            assert 'outside this report' in restored.locator('.ui-notice').inner_text()
            assert 'pending' in restored.locator('.ui-authority').inner_text()
            checks.append('UI illustration is explicitly outside the historical rules-task scope and remains unapproved')
            # Native controls still work with scripts disabled.
            nojs_context=browser.new_context(java_script_enabled=False,offline=True,viewport={'width':390,'height':844})
            nojs=instrument(nojs_context.new_page());nojs.set_content(content, wait_until='load')
            assert nojs.locator('#panel-ui-preview').is_visible()
            nojs.locator('label[for="zoom-125"]').click()
            assert abs(nojs.locator('.ui-screen-node').first.bounding_box()['width']-width*1.25)<1
            nojs.locator('label[for="zoom-100"]').click()
            nojs.locator('.ui-screen-index>summary').click();nojs.locator('.ui-screen-detail>summary').first.click()
            assert nojs.locator('.ui-screen-detail').first.locator('svg').is_visible()
            nojs.locator('label[for="view-current"]').click();assert nojs.locator('#panel-current').is_visible()
            assert nojs.evaluate('document.documentElement.scrollWidth <= innerWidth')
            checks.append('Without JavaScript, tabs, fixed zoom and screen disclosures remain usable')
            nojs_context.close()
            page.emulate_media(media='print')
            assert page.locator('.panel:visible').count()==4
            assert page.locator('.ui-screen-node').first.evaluate('el=>getComputedStyle(el).position')=='static'
            page.emulate_media(media='screen')
            checks.append('Print includes every flow and a non-overlapping screen-card layout')
            # The capture path uses a generated tiny PNG fixture, not real project content.
            with tempfile.TemporaryDirectory() as tmp:
                temp=Path(tmp);(temp/'proof.md').write_text('Synthetic capture rendering test only.')
                (temp/'capture.png').write_bytes(tiny_png())
                captured=copy.deepcopy(data)
                captured['sources']=[{**s,'path':'proof.md'} for s in captured['sources']]
                captured['sources'].append({'id':'CAPTURE','role':'ui-capture','path':'capture.png'})
                for screen in captured['ui_review']['screens']:
                    screen.pop('content',None);screen.update(representation='capture',capture='CAPTURE',sources=['CAPTURE'])
                    screen['markers']=[{'decision':screen['decisions'][0],'position':[0.5,0.5]}] if screen['decisions'] else []
                inp=temp/'input.json';inp.write_text(json.dumps(captured))
                captured_html=renderer.render(captured,temp,inp)
                capture_page=instrument(context.new_page());capture_page.set_content(captured_html,wait_until='load')
                capture_page.locator('.ui-inspect').first.click()
                img=capture_page.locator('.ui-capture-detail').first
                assert img.evaluate('el=>el.complete&&el.naturalWidth===4&&el.naturalHeight===4')
                assert capture_page.locator('.ui-screen-node image').count()==4
                assert capture_page.locator('.ui-screen-node a[aria-label^="Review decision"]').count()==4
                checks.append('Local PNG capture path renders original pixels and links source-backed decision markers offline')
                capture_page.close()
            assert not errors, errors
            checks.append('No JavaScript exceptions in rendered examples')
            external=[u for u in requests if u.startswith(('http:','https:','ws:','wss:'))]
            assert not external, external
            checks.append('No external network requests, application calls or uploads')
            browser.close()
        result['status']='PASS'
        print(f'PASS: {len(checks)} targeted UI/report browser checks. No application or agent validation claimed.')
        code=0
    except Exception as exc:
        result['status']='FAIL';result['error']=str(exc);result['error_type']=type(exc).__name__
        print('FAIL: '+repr(exc),file=sys.stderr);code=1
    result['page_errors']=errors
    (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    return code


if __name__=='__main__':
    raise SystemExit(main())
