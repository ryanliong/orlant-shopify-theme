#!/usr/bin/env python3
"""Attach placeholder images to the sample Orlant products.

Placeholder only — the client supplies real photography later. Three slides
per product so the gallery carousel has something to page through, and each
slide is a different crop so it is obvious whether paging actually worked.

Idempotent: products that already carry media are skipped, so re-running does
not stack duplicates.

Usage:
    SHOP=orlant-gujfiai0.myshopify.com \
    MEDIA_DIR=/tmp/orlant-media \
    python3 scripts/upload-placeholder-media.py
"""
import json, os, subprocess, sys, urllib.request

SHOP = os.environ.get('SHOP')
API = os.environ.get('API_VERSION', '2026-07')
MEDIA_DIR = os.environ.get('MEDIA_DIR', '/tmp/orlant-media')
TOKEN = open(os.path.expanduser(os.environ.get('TOKEN_FILE', '~/.orlant-admin-token'))).read().strip()
if not SHOP:
    sys.exit('SHOP env var required.')


def gql(query, variables=None):
    body = json.dumps({'query': query, 'variables': variables or {}}).encode()
    req = urllib.request.Request(
        f'https://{SHOP}/admin/api/{API}/graphql.json', data=body,
        headers={'X-Shopify-Access-Token': TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        out = json.load(r)
    if 'errors' in out:
        sys.exit('GraphQL error: ' + json.dumps(out['errors'], indent=2))
    return out['data']


STAGED = '''
mutation($input: [StagedUploadInput!]!) {
  stagedUploadsCreate(input: $input) {
    stagedTargets { url resourceUrl parameters { name value } }
    userErrors { field message }
  }
}'''

CREATE_MEDIA = '''
mutation($productId: ID!, $media: [CreateMediaInput!]!) {
  productCreateMedia(productId: $productId, media: $media) {
    media { ... on MediaImage { id } }
    mediaUserErrors { field message }
  }
}'''

PRODUCTS = '''
{ products(first: 20) { nodes { id handle title mediaCount { count } } } }'''


def stage_and_upload(path):
    """Stage one file with Shopify, push the bytes, return the resource URL."""
    name = os.path.basename(path)
    size = os.path.getsize(path)
    res = gql(STAGED, {'input': [{
        'resource': 'IMAGE', 'filename': name, 'mimeType': 'image/jpeg',
        'httpMethod': 'POST', 'fileSize': str(size),
    }]})['stagedUploadsCreate']
    if res['userErrors']:
        sys.exit(f'staging {name}: {res["userErrors"]}')
    target = res['stagedTargets'][0]

    # Shopify's staged target is a plain multipart POST; its parameters must be
    # sent in order, before the file field.
    cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'POST', target['url']]
    for p in target['parameters']:
        cmd += ['-F', f'{p["name"]}={p["value"]}']
    cmd += ['-F', f'file=@{path}']
    code = subprocess.run(cmd, capture_output=True, text=True).stdout.strip()
    if code not in ('200', '201', '204'):
        sys.exit(f'upload of {name} failed with HTTP {code}')
    return target['resourceUrl']


nodes = gql(PRODUCTS)['products']['nodes']
targets = [n for n in nodes if n['handle'].startswith('orlant-')]
if not targets:
    sys.exit('No orlant-* products found. Run setup-sample-data.py first.')

files = sorted(
    os.path.join(MEDIA_DIR, f)
    for f in os.listdir(MEDIA_DIR) if f.lower().endswith(('.jpg', '.jpeg', '.png'))
)
if not files:
    sys.exit(f'No images in {MEDIA_DIR}.')

print(f'{len(files)} image(s) -> {len(targets)} product(s)')
print('-' * 62)

# Stage once and reuse the resource URLs across every product, rather than
# re-uploading the same bytes four times.
resources = []
for f in files:
    resources.append(stage_and_upload(f))
    print(f'  staged   {os.path.basename(f)}')

for p in targets:
    if p['mediaCount']['count'] > 0:
        print(f'  skip     {p["handle"]} (already has {p["mediaCount"]["count"]} media)')
        continue
    media = [
        {'originalSource': url, 'mediaContentType': 'IMAGE',
         'alt': f'{p["title"]} — placeholder view {i + 1}'}
        for i, url in enumerate(resources)
    ]
    res = gql(CREATE_MEDIA, {'productId': p['id'], 'media': media})['productCreateMedia']
    if res['mediaUserErrors']:
        sys.exit(f'  FAILED {p["handle"]}: {res["mediaUserErrors"]}')
    print(f'  ok       {p["handle"]:<34} {len(media)} images')

print('\nPlaceholder media attached. Replace with the client\'s photography before launch.')
