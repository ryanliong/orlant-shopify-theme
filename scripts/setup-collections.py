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
    ('all-models', 'All models',
     'Every Orlant smart drying rack, from the entry-level E5 to the flagship X1.',
     'Smart Drying Rack'),
    ('x-series', 'X Series',
     'The flagship range. Highest airflow, PTC heating and UV-C sterilisation, '
     'for households drying a full load every day.', 'X Series'),
    ('m-series', 'M Series',
     'Heating and sterilisation for everyday family loads, sized for a typical '
     'four-room flat.', 'M Series'),
    ('d-series', 'D Series',
     'Heated drying and app control in a slimmer housing, for shorter balcony '
     'runs and two-bedroom homes.', 'D Series'),
    ('e-series', 'E Series',
     'Motorised lift and LED lighting without a heating element — for airy '
     'service yards.', 'E Series'),
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
    if gql(BY_HANDLE % handle)['collectionByHandle']:
        print(f'  exists   {handle}')
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
