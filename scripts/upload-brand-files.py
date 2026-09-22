#!/usr/bin/env python3
"""Upload brand files (favicon, logo) to Content > Files and report their URLs.

Idempotent by filename: an existing file with the same name is reused rather
than duplicated, so re-running does not litter the Files library.

Usage:
    SHOP=orlant-gujfiai0.myshopify.com FILE=/tmp/orlant-brand/orlant-favicon.png \
    python3 scripts/upload-brand-files.py

Requires Admin API scope: write_files.
"""
import json, os, subprocess, sys, urllib.request

SHOP = os.environ.get('SHOP')
API = os.environ.get('API_VERSION', '2026-07')
PATH = os.environ.get('FILE')
TOKEN = open(os.path.expanduser(os.environ.get('TOKEN_FILE', '~/.orlant-admin-token'))).read().strip()
if not (SHOP and PATH):
    sys.exit('SHOP and FILE env vars required.')


def gql(q, v=None):
    body = json.dumps({'query': q, 'variables': v or {}}).encode()
    req = urllib.request.Request(
        f'https://{SHOP}/admin/api/{API}/graphql.json', data=body,
        headers={'X-Shopify-Access-Token': TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        out = json.load(r)
    if 'errors' in out:
        sys.exit('GraphQL error: ' + json.dumps(out['errors'], indent=2))
    return out['data']


name = os.path.basename(PATH)
size = os.path.getsize(PATH)
ext = name.rsplit('.', 1)[-1].lower()
mime = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
        'svg': 'image/svg+xml', 'webp': 'image/webp'}.get(ext, 'application/octet-stream')

existing = gql('query($q:String!){files(first:5,query:$q){nodes{id ... on MediaImage{image{url}}}}}',
               {'q': f'filename:{name}'})['files']['nodes']
if existing and existing[0].get('image'):
    print(f'  exists   {name}\n  url      {existing[0]["image"]["url"]}')
    sys.exit(0)

st = gql('''mutation($i:[StagedUploadInput!]!){stagedUploadsCreate(input:$i){
             stagedTargets{url resourceUrl parameters{name value}} userErrors{message}}}''',
         {'i': [{'resource': 'FILE', 'filename': name, 'mimeType': mime,
                 'httpMethod': 'POST', 'fileSize': str(size)}]})['stagedUploadsCreate']
if st['userErrors']:
    sys.exit(st['userErrors'])
t = st['stagedTargets'][0]

cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'POST', t['url']]
for p in t['parameters']:
    cmd += ['-F', f'{p["name"]}={p["value"]}']
cmd += ['-F', f'file=@{PATH}']
code = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
if code not in ('200', '201', '204'):
    sys.exit(f'upload failed HTTP {code}')

res = gql('''mutation($f:[FileCreateInput!]!){fileCreate(files:$f){
             files{id fileStatus ... on MediaImage{image{url}}} userErrors{message}}}''',
          {'f': [{'originalSource': t['resourceUrl'], 'contentType': 'IMAGE',
                  'alt': 'Orlant placeholder brand mark'}]})['fileCreate']
if res['userErrors']:
    sys.exit(res['userErrors'])
print(f'  uploaded {name}  status={res["files"][0]["fileStatus"]}')
