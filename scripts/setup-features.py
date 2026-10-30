#!/usr/bin/env python3
"""Upload the client's feature icons and create one orlant_feature entry each.

Each entry pairs an icon file with a label. The labels are baked into the
icon artwork, so the theme uses `label` as alt text rather than printing it;
it also makes entries readable in admin.

Idempotent: files are reused by name, entries upserted by handle.

Usage:
    SHOP=orlant-gujfiai0.myshopify.com \
    ICON_DIR=~/Documents/shopify/orlant-assets/web/icons \
    python3 scripts/setup-features.py
"""
import json, os, subprocess, sys, time, urllib.request

SHOP = os.environ.get('SHOP')
API = os.environ.get('API_VERSION', '2026-07')
ICON_DIR = os.path.expanduser(os.environ.get('ICON_DIR', '~/Documents/shopify/orlant-assets/web/icons'))
TOKEN = open(os.path.expanduser(os.environ.get('TOKEN_FILE', '~/.orlant-admin-token'))).read().strip()
if not SHOP:
    sys.exit('SHOP env var required.')


def gql(q, v=None):
    body = json.dumps({'query': q, 'variables': v or {}}).encode()
    req = urllib.request.Request(f'https://{SHOP}/admin/api/{API}/graphql.json', data=body,
        headers={'X-Shopify-Access-Token': TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        out = json.load(r)
    if 'errors' in out:
        sys.exit('GraphQL error: ' + json.dumps(out['errors'], indent=2))
    return out['data']


# source file (after "orlant-feature-") -> (handle, label matching the artwork)
FEATURES = {
    # The client's file is named "Aluminium" but the artwork reads
    # "304 Stainless Steel". Named for what it shows, so it is never picked
    # for an aluminium model.
    'aluminium.png':                  ('stainless-steel-304', '304 stainless steel'),
    'app-monitoring.png':             ('app-monitoring', 'Monitoring with app'),
    'cross-flow-wind-6-5m.png':       ('cross-flow-wind', 'Cross-flow wind'),
    'double-layer-frame.png':         ('double-layer-frame', 'Double-layer frame'),
    'drying-indicator-light.png':     ('drying-indicator-light', 'Drying indicator light'),
    'ec-blowers-1.png':               ('ec-blowers', 'EC blowers'),
    'ec-blowers-4.png':               ('ec-blowers-4', 'EC blowers x4'),
    'ec-blowers-6.png':               ('ec-blowers-6', 'EC blowers x6'),
    'ec-blowers-high-speed.png':      ('ec-blowers-high-speed', 'High-speed EC blowers, 2200 RPM'),
    'eco-mode.png':                   ('eco-mode', 'Eco mode'),
    'led-panel-light-3-tone.png':     ('led-panel-light-3-tone', '3-tone LED panels'),
    'led-panel-light.png':            ('led-panel-light', 'LED panel light'),
    'lifting-height-control.png':     ('lifting-height-control', 'Lifting height control'),
    'negative-oxygen-anion.png':      ('negative-oxygen-anion', 'Negative oxygen anion'),
    'one-touch-rising.png':           ('one-touch-rising', 'One-touch rising'),
    'overweight-alarm.png':           ('overweight-alarm', 'Overweight alarm'),
    'overweight-alarm-45kg.png':      ('overweight-alarm-45kg', 'Overweight alarm, 45 kg'),
    'overweight-alarm-55kg.png':      ('overweight-alarm-55kg', 'Overweight alarm, 55 kg'),
    'poles-1-7m-4-extend.png':        ('poles-1-7m-4', 'Poles extend to 1.7 m, x4'),
    'poles-1-9m-4-plus-3-extend.png': ('poles-1-9m-4-plus-3', 'Poles extend to 1.9 m, 4 + 3'),
    'poles-2-0m-4-plus-3-extend.png': ('poles-2-0m-4-plus-3', 'Poles extend to 2.0 m, 4 + 3'),
    'poles-2-2m-4-plus-3-extend.png': ('poles-2-2m-4-plus-3', 'Poles extend to 2.2 m, 4 + 3'),
    'poles-2-3m-4-plus-3-extend.png': ('poles-2-3m-4-plus-3', 'Poles extend to 2.3 m, 4 + 3'),
    'ptc-heater-1.png':               ('ptc-heater', 'PTC heater'),
    'ptc-heater-4.png':               ('ptc-heater-4', 'PTC heater x4'),
    'ultra-thin-design.png':          ('ultra-thin-design', 'Ultra-thin design'),
    'uv-disinfection.png':            ('uv-disinfection', 'UV disinfection'),
    'voice-control.png':              ('voice-control', 'Voice control'),
}


def existing_file(name):
    nodes = gql('query($q:String!){files(first:5,query:$q){nodes{id fileStatus ... on MediaImage{image{url}}}}}',
                {'q': f'filename:{name}'})['files']['nodes']
    return nodes[0]['id'] if nodes else None


def upload(path, name, alt):
    st = gql('''mutation($i:[StagedUploadInput!]!){stagedUploadsCreate(input:$i){
                stagedTargets{url resourceUrl parameters{name value}} userErrors{message}}}''',
             {'i': [{'resource': 'IMAGE', 'filename': name, 'mimeType': 'image/png',
                     'httpMethod': 'POST', 'fileSize': str(os.path.getsize(path))}]})['stagedUploadsCreate']
    if st['userErrors']: sys.exit(st['userErrors'])
    t = st['stagedTargets'][0]
    cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'POST', t['url']]
    for p in t['parameters']: cmd += ['-F', f'{p["name"]}={p["value"]}']
    cmd += ['-F', f'file=@{path}']
    if subprocess.run(cmd, capture_output=True, text=True).stdout.strip() not in ('200', '201', '204'):
        sys.exit(f'upload failed: {name}')
    res = gql('''mutation($f:[FileCreateInput!]!){fileCreate(files:$f){files{id} userErrors{message}}}''',
              {'f': [{'originalSource': t['resourceUrl'], 'contentType': 'IMAGE',
                      'filename': name, 'alt': alt}]})['fileCreate']
    if res['userErrors']: sys.exit(res['userErrors'])
    return res['files'][0]['id']


UPSERT = '''mutation($h:MetaobjectHandleInput!,$m:MetaobjectUpsertInput!){
  metaobjectUpsert(handle:$h,metaobject:$m){metaobject{id handle} userErrors{field message code}}}'''

print('Feature icons')
print('-' * 62)
for src, (handle, label) in FEATURES.items():
    path = f'{ICON_DIR}/orlant-feature-{src}'
    if not os.path.exists(path):
        sys.exit(f'missing icon: {path} (run prepare-web.py first)')
    name = f'orlant-feature-{handle}.png'
    fid = existing_file(name)
    state = 'reused '
    if not fid:
        fid = upload(path, name, label); state = 'uploaded'
    res = gql(UPSERT, {'h': {'type': 'orlant_feature', 'handle': handle},
                       'm': {'fields': [{'key': 'label', 'value': label},
                                        {'key': 'icon', 'value': fid}]}})['metaobjectUpsert']
    if res['userErrors']:
        # A just-created file can take a moment before it can be referenced.
        time.sleep(3)
        res = gql(UPSERT, {'h': {'type': 'orlant_feature', 'handle': handle},
                           'm': {'fields': [{'key': 'label', 'value': label},
                                            {'key': 'icon', 'value': fid}]}})['metaobjectUpsert']
        if res['userErrors']: sys.exit(f'  FAILED {handle}: {res["userErrors"]}')
    print(f'  {state} {handle:<26} {label}')
print(f'\n{len(FEATURES)} features ready.')
