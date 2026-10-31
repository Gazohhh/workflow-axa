"""Synthetic selection bytes for tests only; no actual project UI or consent is implied."""
from __future__ import annotations
import copy
import hashlib
import json
import shutil
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def png():
    def chunk(kind, body):
        return struct.pack('>I',len(body))+kind+body+struct.pack('>I',zlib.crc32(kind+body)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',4,4,8,6,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\x80\x80\x80\xff'*4)*4))+chunk(b'IEND',b'')


def fixture(root):
    shutil.copytree(ROOT/'skills/codebase-map/examples',root,dirs_exist_ok=True)
    data=json.loads((root/'review.json').read_text())
    ui=copy.deepcopy(json.loads((ROOT/'skills/codebase-map/examples/ui-review/review-r2.json').read_text())['ui_review'])
    data.update(state='awaiting-approval',open_decisions=[],ui_review=ui)
    sources=[{'id':'UIREF','role':'fixture-evidence','path':'ui-review/README.md'},
             {'id':'KIT','role':'ui-kit','path':'kit.json'},
             {'id':'STORY','role':'ui-example','path':'src/kit.stories.ts'},
             {'id':'CAP','role':'ui-capture','path':'capture.png'}]
    data['sources'].extend(sources)
    def ref(path, contents):
        p=root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(contents.encode())
        return {'path':path,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    button=ref('src/Button.tsx','synthetic component bytes; not a rendered application')
    pattern=ref('src/Settings.tsx','synthetic pattern bytes')
    story=ref('src/kit.stories.ts','synthetic source examples')
    approval=ref('docs/kit-approval.md','Synthetic test declaration, not real owner consent.')
    preview=ref('docs/kit-preview.md','Synthetic offline fixture, not a deployed route.')
    catalogue={'schema_version':1,'kit_id':'synthetic-kit','revision':'R1','status':'approved','scope':['src'],
               'approval':approval,'preview':preview,'items':[]}
    for key,kind,refs,uses in [('primary','component',[button,story],[]),('settings','pattern',[pattern,story],['primary'])]:
        catalogue['items'].append({'id':key,'kind':kind,'name':key,'purpose':'synthetic contract',
             'status':'approved','scope':['src'],'sources':refs,'approval':approval,
             'variants':['default'],'states':['normal'],'uses':uses})
    (root/'kit.json').write_text(json.dumps(catalogue))
    (root/'capture.png').write_bytes(png())
    ui.update(kind='application',mode='approved-kit',kit_binding={'source':'KIT','scope':'src/settings'})
    ui['authority']['status']='confirmed';ui['preview']['status']='authorised'
    for d in ui['decisions']:
        d.update(status='selected',selection=d['options'][0],source='UIREF',locator='synthetic test',summary='Fixture decision only')
    for s in ui['screens']:
        s.pop('content',None)
        s.update(representation='capture',capture='CAP',sources=['UIREF','CAP','STORY'],
                 requirements=[data['requirements'][0]['id']],evidence=[data['evidence'][0]['id']],tasks=[data['tasks'][0]['id']],
                 elements=[{'id':n,'item':item,'role':role,'variant':'default','state':'normal',
                            'example_source':'STORY','example_locator':'Synthetic / '+item,'changes':'Data and event wiring only.'}
                           for n,item,role in [('E1','primary','Save action'),('E2','settings','Page composition')]],
                 capture_context={'source':'UIREF','locator':'Synthetic capture record',
                    'summary':'Test bytes, not a real component capture; supplied for mechanical tests only.',
                    'capture_sha256':hashlib.sha256(png()).hexdigest(),'inputs':[button,pattern,story]})
    return data, copy.deepcopy(catalogue)
