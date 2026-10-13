#!/usr/bin/env python3
"""Optional offline-content smoke test using already installed Playwright/Chromium.

Does not install anything. Direct file-URL/default-browser opening is a separate check.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import tempfile
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--browser',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True,help='New directory for screenshots/results.')
    parser.add_argument('--no-sandbox',action='store_true',help='Only for an explicitly trusted disposable container that requires it; sandbox stays enabled by default.')
    args=parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        parser.error('Choose a new output directory; existing data is never overwritten.')
    if not args.browser.is_file():
        parser.error('Supply an already installed Chromium executable.')
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print('NOT RUN: Python Playwright is not installed. No installation attempted.',file=sys.stderr)
        return 2
    args.output.mkdir(parents=True,exist_ok=False)
    checks=[]
    errors=[]
    requests=[]
    try:
        spec=importlib.util.spec_from_file_location('renderer',ROOT/'skills/codebase-map/scripts/render_report.py')
        renderer=importlib.util.module_from_spec(spec);spec.loader.exec_module(renderer)
        example=ROOT/'skills/codebase-map/examples'
        data=renderer.load_json(example/'review.json')
        content=renderer.render(data,example,example/'review.json')
        with sync_playwright() as p:
            browser=p.chromium.launch(executable_path=str(args.browser),headless=True,args=['--no-sandbox'] if args.no_sandbox else [])
            browser_version=browser.version
            page=browser.new_page(viewport={'width':1440,'height':1000},offline=True)
            page.on('pageerror',lambda e:errors.append(str(e)))
            page.on('request',lambda r:requests.append(r.url))
            page.set_content(content,wait_until='load')
            assert page.locator('svg.map').count()==2
            checks.append('Current and proposed graphs rendered offline')
            assert page.get_by_text('AWAITING USER APPROVAL',exact=False).count()>=1
            assert page.locator('form, input, button[type=submit]').count()==0
            assert page.locator('button').count()==6
            checks.append('Pending state visible; no approval/submission controls')
            card=page.locator('.graph-card').first;svg=card.locator('svg')
            original=svg.get_attribute('viewBox')
            card.locator('[data-action=in]').click();assert svg.get_attribute('viewBox')!=original
            card.locator('[data-action=fit]').click();assert svg.get_attribute('viewBox')==original
            svg.focus();svg.press('ArrowRight');assert svg.get_attribute('viewBox')!=original
            svg.press('f');assert svg.get_attribute('viewBox')==original
            box=svg.bounding_box();page.mouse.move(box['x']+70,box['y']+70);page.mouse.down();page.mouse.move(box['x']+150,box['y']+110);page.mouse.up()
            assert svg.get_attribute('viewBox')!=original
            card.locator('[data-action=fit]').click()
            checks.append('Toolbar zoom/fit, keyboard pan/fit and pointer drag')
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
            page.screenshot(path=str(args.output/'desktop.png'),full_page=True)
            card.screenshot(path=str(args.output/'current-graph.png'))
            page.locator('.graph-card').nth(1).screenshot(path=str(args.output/'proposed-graph.png'))
            checks.append('Desktop layout has no horizontal document overflow')
            card.locator('summary').click()
            card.locator('a[href="#e-E1"]').first.click()
            assert page.locator('#e-E1').is_visible()
            page.locator('#e-E1 a[href="#s-S4"]').click()
            assert page.locator('.snapshot').get_attribute('open') is not None
            checks.append('Evidence/source anchors reveal details')
            page.set_viewport_size({'width':390,'height':844})
            page.screenshot(path=str(args.output/'mobile.png'),full_page=True)
            assert not page.evaluate('document.documentElement.scrollWidth > innerWidth')
            checks.append('Mobile layout has no horizontal document overflow')
            payload='</script><img src="https://invalid.example/x" onerror="window.__injected=true"><script>window.__injected=true</script>'
            data['understanding']=payload
            with tempfile.TemporaryDirectory() as tmp:
                test_root=Path(tmp)/'example'
                shutil.copytree(example,test_root)
                test_input=test_root/'review.json'
                test_input.write_text(json.dumps(data),encoding='utf-8')
                malicious_content=renderer.render(data,test_root,test_input)
            page.set_content(malicious_content,wait_until='load')
            assert page.locator('img').count()==0
            assert page.evaluate('window.__injected === undefined')
            assert '<img' in page.locator('.lead').inner_text()
            assert not requests,requests
            assert not errors,errors
            checks.append('Malicious-looking labels remain inert; no network requests or script errors')
            browser.close()
        result={'status':'PASS','browser':browser_version,'checks':checks,'requests':requests,'errors':errors,
                'limits':['HTML supplied through set_content with network offline, not direct file:// navigation.','Default desktop opener and actual Claude/Codex agent behavior not tested.','Schema/content tests cannot prove diagram semantic completeness or real user approval.']}
        (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(f'PASS: {len(checks)} browser smoke checks; results: {args.output.resolve()}')
        return 0
    except Exception as exc:
        result={'status':'FAIL','checks_completed':checks,'error':str(exc),'script_errors':errors,'requests':requests}
        (args.output/'results.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
        print(f'FAIL: {exc}; partial evidence: {args.output.resolve()}',file=sys.stderr)
        return 1


if __name__=='__main__':
    raise SystemExit(main())
