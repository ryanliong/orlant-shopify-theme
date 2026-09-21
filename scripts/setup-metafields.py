#!/usr/bin/env python3
"""Create the Orlant metaobject + metafield definitions on a Shopify store.

Idempotent: re-running reports existing definitions as "exists" and leaves
them alone. Safe to run against the client's production store at handover.

Usage:
    SHOP=orlant-gujfiai0.myshopify.com \
    TOKEN_FILE=~/.orlant-admin-token \
    python3 scripts/setup-metafields.py

Requires Admin API scopes: write_products, write_metaobject_definitions.
Never hard-code the token here - this file is committed to a public repo.
"""
import json, os, sys, urllib.request

SHOP = os.environ.get('SHOP')
API = os.environ.get('API_VERSION', '2026-07')
TOKEN_FILE = os.path.expanduser(os.environ.get('TOKEN_FILE', '~/.orlant-admin-token'))

if not SHOP:
    sys.exit('SHOP env var required, e.g. SHOP=orlant-gujfiai0.myshopify.com')
try:
    TOKEN = open(TOKEN_FILE).read().strip()
except OSError as e:
    sys.exit(f'Cannot read token file {TOKEN_FILE}: {e}')
if not TOKEN:
    sys.exit(f'Token file {TOKEN_FILE} is empty.')


def gql(query, variables=None):
    body = json.dumps({'query': query, 'variables': variables or {}}).encode()
    req = urllib.request.Request(
        f'https://{SHOP}/admin/api/{API}/graphql.json', data=body,
        headers={'X-Shopify-Access-Token': TOKEN, 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as r:
        out = json.load(r)
    if 'errors' in out:
        sys.exit(f'GraphQL error: {json.dumps(out["errors"], indent=2)}')
    return out['data']


# --- Metaobject definitions -------------------------------------------------
# Spec rows and FAQ entries are repeatable structured records. Metaobjects give
# the client real labelled fields in admin instead of hand-edited JSON, where a
# single missing brace silently breaks the spec table.

METAOBJECTS = [
    {
        'name': 'Spec row',
        'type': 'orlant_spec_row',
        'description': 'One row of a product specification table.',
        'displayNameKey': 'label',
        'fieldDefinitions': [
            {'name': 'Label', 'key': 'label', 'type': 'single_line_text_field',
             'required': True, 'description': 'e.g. "Motor speed"'},
            {'name': 'Value', 'key': 'value', 'type': 'single_line_text_field',
             'required': True, 'description': 'e.g. "2200 RPM"'},
        ],
    },
    {
        'name': 'FAQ item',
        'type': 'orlant_faq_item',
        'description': 'One question and answer.',
        'displayNameKey': 'question',
        'fieldDefinitions': [
            {'name': 'Question', 'key': 'question', 'type': 'single_line_text_field',
             'required': True},
            {'name': 'Answer', 'key': 'answer', 'type': 'multi_line_text_field',
             'required': True},
        ],
    },
]

MO_CREATE = '''
mutation($d: MetaobjectDefinitionCreateInput!) {
  metaobjectDefinitionCreate(definition: $d) {
    metaobjectDefinition { id type }
    userErrors { field message code }
  }
}'''

MO_BY_TYPE = '''
query($type: String!) {
  metaobjectDefinitionByType(type: $type) { id type }
}'''

mo_ids = {}
print('Metaobject definitions')
print('-' * 62)
for spec in METAOBJECTS:
    existing = gql(MO_BY_TYPE, {'type': spec['type']})['metaobjectDefinitionByType']
    if existing:
        mo_ids[spec['type']] = existing['id']
        print(f'  exists   {spec["type"]}')
        continue
    payload = dict(spec)
    payload['access'] = {'storefront': 'PUBLIC_READ'}
    res = gql(MO_CREATE, {'d': payload})['metaobjectDefinitionCreate']
    if res['userErrors']:
        sys.exit(f'  FAILED   {spec["type"]}: {res["userErrors"]}')
    mo_ids[spec['type']] = res['metaobjectDefinition']['id']
    print(f'  created  {spec["type"]}')

# --- Product metafield definitions -----------------------------------------
# Order here is the order they appear in admin.

def d(key, name, mtype, desc, validations=None):
    # storefront PUBLIC_READ is required for Liquid and the Storefront API to
    # see the value. Definitions created through the API default to NONE, which
    # renders as an empty tab with no error to explain it. These are public
    # product specs, so PUBLIC_READ is the correct level.
    out = {'name': name, 'namespace': 'orlant', 'key': key, 'ownerType': 'PRODUCT',
           'type': mtype, 'description': desc,
           'access': {'storefront': 'PUBLIC_READ'}}
    if validations:
        out['validations'] = validations
    return out

METAFIELDS = [
    d('series', 'Series', 'single_line_text_field',
      'Series label shown above the product title, e.g. "X Series".'),
    d('card_tagline', 'Card tagline', 'single_line_text_field',
      'One-line spec shown on product cards.'),
    d('badge', 'Card badge', 'single_line_text_field',
      'Short badge on the product card, e.g. "New" or "Best seller". Leave blank for none.'),
    d('highlights', 'Key highlights', 'list.single_line_text_field',
      'Three to five short bullets shown under the buy box.'),
    d('overview', 'Overview', 'rich_text_field',
      'Overview tab. Hidden if empty.'),
    d('specs', 'Specifications', 'list.metaobject_reference',
      'Specification table rows, in display order. Hidden if empty.',
      [{'name': 'metaobject_definition_id', 'value': mo_ids['orlant_spec_row']}]),
    d('in_the_box', "What's in the box", 'rich_text_field',
      "What's in the box tab. Hidden if empty."),
    d('installation', 'Installation & compatibility', 'rich_text_field',
      'Ceiling type, false ceiling notes, installation info. Hidden if empty.'),
    d('warranty', 'Warranty', 'rich_text_field',
      'Warranty tab. Hidden if empty.'),
    d('faq', 'Product FAQ', 'list.metaobject_reference',
      'Product-specific questions, in display order. Hidden if empty.',
      [{'name': 'metaobject_definition_id', 'value': mo_ids['orlant_faq_item']}]),
    # Comparison table columns (brief 4.1.7)
    d('compare_heating', 'Compare: heating', 'boolean', 'Comparison table — PTC heating.'),
    d('compare_sterilisation', 'Compare: sterilisation', 'boolean', 'Comparison table — UV sterilisation.'),
    d('compare_lighting', 'Compare: lighting', 'boolean', 'Comparison table — integrated lighting.'),
    d('compare_app_control', 'Compare: app control', 'boolean', 'Comparison table — app and voice control.'),
    d('compare_max_load', 'Compare: max load', 'single_line_text_field',
      'Comparison table — max load with unit, e.g. "35 kg".'),
    d('compare_drying_poles', 'Compare: drying poles', 'number_integer',
      'Comparison table — number of drying poles.'),
]

MF_CREATE = '''
mutation($d: MetafieldDefinitionInput!) {
  metafieldDefinitionCreate(definition: $d) {
    createdDefinition { id key }
    userErrors { field message code }
  }
}'''

print('\nProduct metafield definitions (namespace: orlant)')
print('-' * 62)
created = exists = 0
for defn in METAFIELDS:
    res = gql(MF_CREATE, {'d': defn})['metafieldDefinitionCreate']
    errs = res['userErrors']
    if errs:
        if any(e.get('code') == 'TAKEN' for e in errs):
            print(f'  exists   orlant.{defn["key"]}')
            exists += 1
            continue
        sys.exit(f'  FAILED   orlant.{defn["key"]}: {errs}')
    print(f'  created  orlant.{defn["key"]:<22} {defn["type"]}')
    created += 1

# Definitions that predate this script (or were made by hand in admin) may
# still be storefront NONE. Repair them rather than leaving a silent failure.
MF_UPDATE = '''
mutation($d: MetafieldDefinitionUpdateInput!) {
  metafieldDefinitionUpdate(definition: $d) {
    updatedDefinition { id key }
    userErrors { field message code }
  }
}'''

MF_LIST = '''
query { metafieldDefinitions(first: 50, ownerType: PRODUCT, namespace: "orlant") {
  nodes { key access { storefront } } } }'''

print('\nStorefront access')
print('-' * 62)
nodes = gql(MF_LIST)['metafieldDefinitions']['nodes']
repaired = 0
for node in nodes:
    if (node.get('access') or {}).get('storefront') == 'PUBLIC_READ':
        continue
    res = gql(MF_UPDATE, {'d': {'namespace': 'orlant', 'key': node['key'],
                                'ownerType': 'PRODUCT',
                                'access': {'storefront': 'PUBLIC_READ'}}})
    err = res['metafieldDefinitionUpdate']['userErrors']
    if err:
        sys.exit(f'  FAILED   orlant.{node["key"]}: {err}')
    print(f'  opened   orlant.{node["key"]} -> PUBLIC_READ')
    repaired += 1
if not repaired:
    print('  all definitions already PUBLIC_READ')

print(f'\n{created} created, {exists} already present, {len(METAFIELDS)} total.')
