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
        'name': 'Feature',
        'type': 'orlant_feature',
        'description': 'One product feature with its icon, e.g. "PTC heater x4".',
        'displayNameKey': 'label',
        'fieldDefinitions': [
            {'name': 'Label', 'key': 'label', 'type': 'single_line_text_field',
             'required': True, 'description': 'Shown under the icon.'},
            {'name': 'Icon', 'key': 'icon', 'type': 'file_reference',
             'required': True, 'description': 'White-on-transparent PNG. The theme tints it.',
             'validations': [{'name': 'file_type_options', 'value': '["Image"]'}]},
        ],
    },
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
    d('features', 'Features', 'list.metaobject_reference',
      'Feature icons shown on the product page, in display order.',
      [{'name': 'metaobject_definition_id', 'value': mo_ids['orlant_feature']}]),
    # --- Structured specifications ------------------------------------------
    # One source for the spec tab, the comparison table and search filters,
    # so the three cannot drift apart. Numbers are stored bare; the theme adds
    # units.
    d('size', 'Size', 'single_line_text_field', 'S or L.'),
    d('size_sibling', 'Other size', 'product_reference',
      'The same model in the other size, e.g. M6S on the M6L page.'),
    d('colour', 'Colour', 'single_line_text_field',
      'Finish, for models sold in one colour. Models with a colour choice use a variant instead.'),
    d('host_length_mm', 'Unit length (mm)', 'number_integer', 'Length of the ceiling unit.'),
    d('host_width_mm', 'Unit width (mm)', 'number_integer', 'Width of the ceiling unit.'),
    d('host_height_mm', 'Unit height (mm)', 'number_integer', 'Height of the ceiling unit.'),
    d('pole_min_mm', 'Pole length, retracted (mm)', 'number_integer', 'Shortest pole length.'),
    d('pole_max_mm', 'Pole length, extended (mm)', 'number_integer', 'Longest pole length.'),
    d('lifting_height_mm', 'Lifting height (mm)', 'number_integer', 'How far the rack lowers.'),
    d('load_kg', 'Load capacity (kg)', 'number_integer', 'Maximum load.'),
    d('power_w', 'Power consumption (W)', 'number_integer', 'Total power draw.'),
    d('led_power_w', 'LED power (W)', 'number_integer', 'Light panel power.'),
    d('ec_blowers', 'EC blowers', 'number_integer', 'Number of EC blowers.'),
    d('ptc_heaters', 'PTC heaters', 'number_integer', 'Number of PTC heaters.'),
    d('sterilisation', 'Sterilisation', 'single_line_text_field', 'e.g. "Plasma" or "UV".'),
    d('voice_control', 'Voice control', 'boolean', 'Works with voice commands.'),
    d('app_control', 'App control', 'boolean', 'Controllable from the phone app.'),
    d('eco_mode', 'Eco mode', 'boolean', 'Has an energy-saving mode.'),
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


# --- Retired definitions ---------------------------------------------------
# Placeholder comparison fields from the first build, replaced by the
# structured specs above. Heating and lighting are on every real model, so as
# comparison rows they were a column of ticks. Deleting a definition also
# deletes its values, so this only ever lists fields known to be obsolete.
RETIRED = ['compare_heating', 'compare_sterilisation', 'compare_lighting',
           'compare_app_control', 'compare_max_load', 'compare_drying_poles']

MF_DELETE = '''
mutation($id: ID!) {
  metafieldDefinitionDelete(id: $id, deleteAllAssociatedMetafields: true) {
    deletedDefinitionId
    userErrors { field message code }
  }
}'''

print('\nRetired definitions')
print('-' * 62)
all_defs = gql('''query { metafieldDefinitions(first: 100, ownerType: PRODUCT, namespace: "orlant") {
  nodes { id key } } }''')['metafieldDefinitions']['nodes']
by_key = {n['key']: n['id'] for n in all_defs}
for key in RETIRED:
    if key not in by_key:
        print(f'  gone     orlant.{key}'); continue
    res = gql(MF_DELETE, {'id': by_key[key]})['metafieldDefinitionDelete']
    if res['userErrors']:
        sys.exit(f'  FAILED   orlant.{key}: {res["userErrors"]}')
    print(f'  deleted  orlant.{key}')

print(f'\n{created} created, {exists} already present, {len(METAFIELDS)} total.')
