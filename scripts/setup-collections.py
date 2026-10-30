#!/usr/bin/env python3
"""Create the Orlant series collections.

One collection per series, each an automated collection matching the series
tag, plus an "All models" collection. Automated rather than manual so the
client only has to tag a new product correctly and it files itself.

Idempotent: existing collections are left alone.

Usage:
    SHOP=orlant-gujfiai0.myshopify.com python3 scripts/setup-collections.py
"""
import json, os, sys, urllib.request

SHOP = os.environ.get('SHOP')
API = os.environ.get('API_VERSION', '2026-07')
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


COLLECTIONS = [
    # Descriptions state only what the brochure supports. The first build's
    # copy ("the flagship range", "slimmer housing") was invented and is gone.
    ('all-models', 'All models',
     'Every Orlant smart drying rack, in short (S) and long (L) sizes.',
     'Smart Drying Rack'),
    ('m-series', 'M Series',
     'The M5 and M6. App control and eco mode across the series; the M6 adds '
     'voice control and a 55 kg load.', 'M Series'),
    ('x-series', 'X Series',
     'The X6. A 304 stainless steel double-layer frame.', 'X Series'),
    ('d-series', 'D Series',
     'The D6. Four EC blowers, four PTC heaters and plasma sterilisation, '
     'with a drying indicator light.', 'D Series'),
]

BY_HANDLE = '{ collectionByHandle(handle: "%s") { id handle } }'

CREATE = '''
mutation($input: CollectionInput!) {
  collectionCreate(input: $input) {
    collection { id handle title }
    userErrors { field message }
  }
}'''

print('Collections')
print('-' * 62)
for handle, title, description, tag in COLLECTIONS:
    found = gql(BY_HANDLE % handle)['collectionByHandle']
    if found:
        gql('''mutation($i:CollectionInput!){collectionUpdate(input:$i){userErrors{message}}}''',
            {'i': {'id': found['id'], 'title': title, 'descriptionHtml': f'<p>{description}</p>'}})
        print(f'  updated  {handle}')
        continue
    res = gql(CREATE, {'input': {
        'handle': handle,
        'title': title,
        'descriptionHtml': f'<p>{description}</p>',
        'ruleSet': {
            'appliedDisjunctively': False,
            'rules': [{'column': 'TAG', 'relation': 'EQUALS', 'condition': tag}],
        },
    }})['collectionCreate']
    if res['userErrors']:
        sys.exit(f'  FAILED {handle}: {res["userErrors"]}')
    # collectionCreate does not publish to the Online Store, so a new
    # collection 404s on the storefront until this runs. The REST endpoint
    # accepts `published` under write_products; the GraphQL publish mutation
    # would need the extra write_publications scope.
    cid = res['collection']['id'].split('/')[-1]
    req = urllib.request.Request(
        f'https://{SHOP}/admin/api/{API}/smart_collections/{cid}.json',
        data=json.dumps({'smart_collection': {'id': int(cid), 'published': True}}).encode(),
        headers={'X-Shopify-Access-Token': TOKEN, 'Content-Type': 'application/json'},
        method='PUT')
    with urllib.request.urlopen(req) as r:
        published = json.load(r)['smart_collection']['published_at']
    print(f'  created  {handle:<14} rule: tag = "{tag}"  published {published[:10]}')

print('\nCollections are automated — tag a product with its series and it files itself.')
