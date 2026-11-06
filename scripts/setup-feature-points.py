#!/usr/bin/env python3
"""Create and fill the catalogue feature fields used by the point-form list.

Round 2 change I. Adds six product metafield definitions (PUBLIC_READ) and
sets them from orlant-assets/00-docs/specs.csv for each model, without
touching anything else on the product. Re-runnable: definitions that exist
are left alone and values are overwritten with the sheet's.

Usage:
    SHOP=orlant-gujfiai0.myshopify.com python3 scripts/setup-feature-points.py

Requires Admin API scope: write_products.
"""
import csv, json, os, sys, urllib.request

SHOP = os.environ.get('SHOP') or sys.exit('SHOP env var required.')
API = os.environ.get('API_VERSION', '2026-07')
TOKEN = open(os.path.expanduser(os.environ.get('TOKEN_FILE', '~/.orlant-admin-token'))).read().strip()
ASSETS = os.path.expanduser(os.environ.get('ASSETS', '~/Documents/shopify/orlant-assets'))


def gql(q, v=None):
    req = urllib.request.Request(
        f'https://{SHOP}/admin/api/{API}/graphql.json',
        data=json.dumps({'query': q, 'variables': v or {}}).encode(),
        headers={'X-Shopify-Access-Token': TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        out = json.load(r)
    if 'errors' in out:
        sys.exit('GraphQL error: ' + json.dumps(out['errors'], indent=2))
    return out['data']


FIELDS = [
    ('pole_count', 'Number of poles', 'single_line_text_field', 'As the catalogue writes it, e.g. "6" or "4+3".'),
    ('bidirectional_protection', 'Bidirectional resistance protection', 'boolean', 'Catalogue row "Bidirectional resistance protection".'),
    ('function_display', 'Function display', 'boolean', 'Catalogue row "Function display".'),
    ('multiple_support', 'Multiple support', 'boolean', 'Catalogue row "Multiple support" (meaning to be confirmed by the client).'),
    ('led_panel', 'LED panel light', 'single_line_text_field', 'e.g. "LED panel light" or "3-tone LED panel light". Blank if none.'),
    ('ultra_thin_cm', 'Ultra-thin body (cm)', 'number_integer', 'Retracted body depth, for models sold as ultra-thin.'),
]

print('Definitions')
for key, name, typ, desc in FIELDS:
    res = gql('''mutation($d:MetafieldDefinitionInput!){metafieldDefinitionCreate(definition:$d){
      createdDefinition{id} userErrors{code message}}}''', {'d': {
        'name': name, 'namespace': 'orlant', 'key': key, 'ownerType': 'PRODUCT', 'type': typ,
        'description': desc, 'access': {'storefront': 'PUBLIC_READ'}}})['metafieldDefinitionCreate']
    errs = res['userErrors']
    if errs and not any(e['code'] == 'TAKEN' for e in errs):
        sys.exit(f'  FAILED {key}: {errs}')
    print(f"  {'exists ' if errs else 'created'}  orlant.{key}")

print('\nValues')
rows = list(csv.DictReader(open(f'{ASSETS}/00-docs/specs.csv')))
for r in rows:
    p = gql('query($h:String!){productByHandle(handle:$h){id}}', {'h': r['model'].lower()})['productByHandle']
    if not p:
        print(f"  skip     {r['model']} (no product)"); continue
    sets, clears = [], []
    for key, _, typ, _ in FIELDS:
        raw = (r.get(key) or '').strip()
        if typ == 'boolean':
            val = 'true' if raw == 'yes' else None
        else:
            val = raw or None
        if val is None:
            clears.append({'ownerId': p['id'], 'namespace': 'orlant', 'key': key})
        else:
            sets.append({'ownerId': p['id'], 'namespace': 'orlant', 'key': key, 'type': typ, 'value': val})
    if sets:
        errs = gql('''mutation($m:[MetafieldsSetInput!]!){metafieldsSet(metafields:$m){userErrors{field message}}}''',
                   {'m': sets})['metafieldsSet']['userErrors']
        if errs:
            sys.exit(f"  FAILED {r['model']}: {errs}")
    if clears:
        gql('''mutation($m:[MetafieldIdentifierInput!]!){metafieldsDelete(metafields:$m){userErrors{message}}}''',
            {'m': clears})
    print(f"  {r['model']:<5} set {', '.join(s['key'] for s in sets) or '-'}")
