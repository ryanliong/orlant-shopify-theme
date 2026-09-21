#!/usr/bin/env python3
"""Create sample Orlant products, collections and metaobject records.

Test data only, for previewing the theme. Deliberately image-free: Shopify
renders its own placeholder SVG for products with no media, so there is no
stock photography to strip out when the client's real photos arrive.

Idempotent via productSet/metaobjectUpsert on a stable handle - re-running
updates in place rather than duplicating.

Usage:
    SHOP=orlant-gujfiai0.myshopify.com python3 scripts/setup-sample-data.py

Requires Admin API scopes: write_products, write_metaobject_definitions.
"""
import json, os, sys, urllib.request

SHOP = os.environ.get('SHOP')
API = os.environ.get('API_VERSION', '2026-07')
TOKEN_FILE = os.path.expanduser(os.environ.get('TOKEN_FILE', '~/.orlant-admin-token'))
if not SHOP:
    sys.exit('SHOP env var required.')
TOKEN = open(TOKEN_FILE).read().strip()


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


def rich(*paragraphs):
    """Shopify rich_text_field wants its own JSON document schema, not HTML."""
    return json.dumps({
        'type': 'root',
        'children': [
            {'type': 'paragraph', 'children': [{'type': 'text', 'value': p}]}
            for p in paragraphs
        ],
    })


# --- Metaobject records -----------------------------------------------------

UPSERT_MO = '''
mutation($handle: MetaobjectHandleInput!, $mo: MetaobjectUpsertInput!) {
  metaobjectUpsert(handle: $handle, metaobject: $mo) {
    metaobject { id handle }
    userErrors { field message code }
  }
}'''


# Creating metaobject ENTRIES needs write_metaobjects, which is a separate
# scope from write_metaobject_definitions. Without it we still build the
# products - only the Specifications and FAQ tabs go unpopulated, and those
# tabs hide themselves when their metafield is empty.
METAOBJECTS_ALLOWED = True


def upsert_metaobject(mo_type, handle, fields):
    global METAOBJECTS_ALLOWED
    if not METAOBJECTS_ALLOWED:
        return None
    res = gql(UPSERT_MO, {
        'handle': {'type': mo_type, 'handle': handle},
        'mo': {'fields': [{'key': k, 'value': v} for k, v in fields.items()]},
    })['metaobjectUpsert']
    errs = res['userErrors']
    if errs:
        if any(e.get('code') == 'NOT_AUTHORIZED' for e in errs):
            METAOBJECTS_ALLOWED = False
            return None
        sys.exit(f'{mo_type}/{handle}: {errs}')
    return res['metaobject']['id']


SHARED_FAQ = [
    ('fits-false-ceiling', 'Will it work with a false ceiling?',
     'Yes. False ceilings need a mounting plate anchored to the structural slab above. '
     'Our installer checks this on site before drilling and will advise if reinforcement is needed.'),
    ('install-time', 'How long does installation take?',
     'Most installations take 60 to 90 minutes. The installer mounts the unit, tests every '
     'function with you and removes the packaging.'),
    ('hdb-permission', 'Do I need HDB permission?',
     'No permit is required for a ceiling-mounted drying rack in an HDB flat. '
     'We install within HDB guidelines and keep all drilling inside the service balcony or utility area.'),
    ('power-supply', 'What power supply does it need?',
     'A standard 13A Singapore socket within two metres of the unit. '
     'If there is no socket nearby the installer can advise on a licensed electrician.'),
]

print('Metaobject records')
print('-' * 64)
faq_ids = {}
for handle, q, a in SHARED_FAQ:
    mid = upsert_metaobject('orlant_faq_item', handle, {'question': q, 'answer': a})
    if mid:
        faq_ids[handle] = mid
        print(f'  faq      {handle}')
if not METAOBJECTS_ALLOWED:
    print('  SKIPPED  write_metaobjects scope not granted.')
    print('           Products will be created without Specifications or FAQ.')

# --- Products ---------------------------------------------------------------

MODELS = [
    {
        'handle': 'orlant-x1-smart-drying-rack', 'title': 'Orlant X1 Smart Drying Rack',
        'series': 'X Series', 'price': '1299.00', 'compare_at': '1499.00',
        'badge': 'Best seller', 'tagline': '2200 RPM airflow, PTC heating and UV sterilisation',
        'heating': True, 'steril': True, 'lighting': True, 'app': True,
        'load': '35 kg', 'poles': 2,
        'highlights': ['2200 RPM dual-turbine airflow', 'PTC heating to 60°C',
                       'UV-C sterilisation', 'App and voice control', 'Silent lift under 40 dB'],
        'overview': (
            'The X1 is our flagship rack, built for households that dry a full load every day. '
            'Dual turbines move 2200 RPM of air across two full-length poles, so a heavy wash '
            'dries through the night even in Singapore humidity.',
            'A PTC heating element lifts the air to 60°C without scorching delicate fabric, and '
            'the UV-C lamp runs a sterilisation cycle for bedding and baby clothes. Everything is '
            'controlled from the app, a wall remote or your voice assistant.'),
        'specs': [('Motor speed', '2200 RPM'), ('Heating', 'PTC, up to 60°C'),
                  ('Sterilisation', 'UV-C lamp, 30 minute cycle'), ('Max load', '35 kg'),
                  ('Drying poles', '2 full-length'), ('Lift range', '1.3 m'),
                  ('Lighting', 'Dimmable LED panel'), ('Control', 'App, remote and voice'),
                  ('Noise', 'Under 40 dB'), ('Power', '220-240V, 13A socket')],
        'in_the_box': ('One X1 main unit with two drying poles, a ceiling mounting plate and '
                       'fixings, a wall remote with battery, the power adaptor, and the warranty card.',),
    },
    {
        'handle': 'orlant-m2-smart-drying-rack', 'title': 'Orlant M2 Smart Drying Rack',
        'series': 'M Series', 'price': '999.00', 'compare_at': None,
        'badge': '', 'tagline': 'PTC heating and sterilisation for everyday family loads',
        'heating': True, 'steril': True, 'lighting': True, 'app': True,
        'load': '30 kg', 'poles': 2,
        'highlights': ['1800 RPM airflow', 'PTC heating to 55°C', 'UV-C sterilisation',
                       'App and voice control'],
        'overview': (
            'The M2 covers what most four-room flats actually need. It carries a full family wash '
            'on two poles, heats and sterilises, and is controlled from the app.',
            'It trades the X1\'s top-end airflow and silent lift for a lower price, and keeps the '
            'same motor housing and two-year warranty.'),
        'specs': [('Motor speed', '1800 RPM'), ('Heating', 'PTC, up to 55°C'),
                  ('Sterilisation', 'UV-C lamp, 30 minute cycle'), ('Max load', '30 kg'),
                  ('Drying poles', '2 full-length'), ('Lift range', '1.2 m'),
                  ('Lighting', 'LED panel'), ('Control', 'App, remote and voice'),
                  ('Power', '220-240V, 13A socket')],
        'in_the_box': ('One M2 main unit with two drying poles, a ceiling mounting plate and '
                       'fixings, a wall remote with battery, the power adaptor, and the warranty card.',),
    },
    {
        'handle': 'orlant-d3-smart-drying-rack', 'title': 'Orlant D3 Smart Drying Rack',
        'series': 'D Series', 'price': '849.00', 'compare_at': None,
        'badge': '', 'tagline': 'Heated drying and app control for smaller homes',
        'heating': True, 'steril': False, 'lighting': True, 'app': True,
        'load': '25 kg', 'poles': 2,
        'highlights': ['1600 RPM airflow', 'PTC heating to 50°C', 'App control',
                       'Compact housing for shorter balconies'],
        'overview': (
            'The D3 suits two-bedroom flats and condo service yards where the balcony run is short. '
            'The housing is slimmer than the M2 and the poles are proportionally shorter.',
            'It heats and dries on app control, without the UV-C sterilisation lamp.'),
        'specs': [('Motor speed', '1600 RPM'), ('Heating', 'PTC, up to 50°C'),
                  ('Sterilisation', 'Not included'), ('Max load', '25 kg'),
                  ('Drying poles', '2 short-run'), ('Lift range', '1.2 m'),
                  ('Lighting', 'LED panel'), ('Control', 'App and remote'),
                  ('Power', '220-240V, 13A socket')],
        'in_the_box': ('One D3 main unit with two drying poles, a ceiling mounting plate and '
                       'fixings, a wall remote with battery, the power adaptor, and the warranty card.',),
    },
    {
        'handle': 'orlant-e5-smart-drying-rack', 'title': 'Orlant E5 Smart Drying Rack',
        'series': 'E Series', 'price': '699.00', 'compare_at': None,
        'badge': 'New', 'tagline': 'Motorised lift and LED lighting, remote controlled',
        'heating': False, 'steril': False, 'lighting': True, 'app': False,
        'load': '22 kg', 'poles': 2,
        'highlights': ['Motorised lift to 1.2 m', 'Dimmable LED panel',
                       'Wall remote control', 'Airflow drying without heating'],
        'overview': (
            'The E5 is the entry point to the range. It raises and lowers on a motorised lift, '
            'lights the yard and moves air across the load, without a heating element.',
            'It is the right choice for homes that hang washing in an airy service yard and want '
            'the lift and the lighting rather than heated drying.'),
        'specs': [('Motor speed', '1200 RPM'), ('Heating', 'Not included'),
                  ('Sterilisation', 'Not included'), ('Max load', '22 kg'),
                  ('Drying poles', '2 full-length'), ('Lift range', '1.2 m'),
                  ('Lighting', 'Dimmable LED panel'), ('Control', 'Wall remote'),
                  ('Power', '220-240V, 13A socket')],
        'in_the_box': ('One E5 main unit with two drying poles, a ceiling mounting plate and '
                       'fixings, a wall remote with battery, the power adaptor, and the warranty card.',),
    },
]

INSTALLATION = (
    'Every rack is installed by an Orlant technician. We mount to the structural ceiling slab, '
    'so concrete ceilings, false ceilings and bulkheads are all workable — a false ceiling needs '
    'a mounting plate anchored through to the slab above.',
    'The installer confirms the drop height, checks the socket is within two metres and tests '
    'every function before leaving. Installation takes 60 to 90 minutes and is included in the price.')

WARRANTY = (
    'Two years from the installation date, covering the motor, control board, heating element '
    'and lift mechanism against manufacturing defects.',
    'Warranty service is carried out on site in Singapore. Accidental damage, overloading past '
    'the rated capacity and unauthorised modification are not covered.')

PRODUCT_SET = '''
mutation($id: ProductSetIdentifiers, $input: ProductSetInput!) {
  productSet(identifier: $id, input: $input, synchronous: true) {
    product { id handle title }
    userErrors { field message code }
  }
}'''

print('\nProducts')
print('-' * 64)
for m in MODELS:
    spec_ids = [
        mid for mid in (
            upsert_metaobject('orlant_spec_row', f'{m["handle"]}-spec-{i}',
                              {'label': label, 'value': value})
            for i, (label, value) in enumerate(m['specs'])
        ) if mid
    ]

    metafields = [
        {'namespace': 'orlant', 'key': 'series', 'type': 'single_line_text_field', 'value': m['series']},
        {'namespace': 'orlant', 'key': 'card_tagline', 'type': 'single_line_text_field', 'value': m['tagline']},
        {'namespace': 'orlant', 'key': 'highlights', 'type': 'list.single_line_text_field',
         'value': json.dumps(m['highlights'])},
        {'namespace': 'orlant', 'key': 'overview', 'type': 'rich_text_field', 'value': rich(*m['overview'])},
        {'namespace': 'orlant', 'key': 'in_the_box', 'type': 'rich_text_field', 'value': rich(*m['in_the_box'])},
        {'namespace': 'orlant', 'key': 'installation', 'type': 'rich_text_field', 'value': rich(*INSTALLATION)},
        {'namespace': 'orlant', 'key': 'warranty', 'type': 'rich_text_field', 'value': rich(*WARRANTY)},

        {'namespace': 'orlant', 'key': 'compare_heating', 'type': 'boolean', 'value': json.dumps(m['heating'])},
        {'namespace': 'orlant', 'key': 'compare_sterilisation', 'type': 'boolean', 'value': json.dumps(m['steril'])},
        {'namespace': 'orlant', 'key': 'compare_lighting', 'type': 'boolean', 'value': json.dumps(m['lighting'])},
        {'namespace': 'orlant', 'key': 'compare_app_control', 'type': 'boolean', 'value': json.dumps(m['app'])},
        {'namespace': 'orlant', 'key': 'compare_max_load', 'type': 'single_line_text_field', 'value': m['load']},
        {'namespace': 'orlant', 'key': 'compare_drying_poles', 'type': 'number_integer', 'value': str(m['poles'])},
    ]
    # An empty list.metaobject_reference is rejected, so omit the metafield
    # entirely when there are no records to point at.
    if spec_ids:
        metafields.append({'namespace': 'orlant', 'key': 'specs',
                           'type': 'list.metaobject_reference',
                           'value': json.dumps(spec_ids)})
    if faq_ids:
        metafields.append({'namespace': 'orlant', 'key': 'faq',
                           'type': 'list.metaobject_reference',
                           'value': json.dumps([faq_ids[h] for h, _, _ in SHARED_FAQ
                                                if h in faq_ids])})
    if m['badge']:
        metafields.append({'namespace': 'orlant', 'key': 'badge',
                           'type': 'single_line_text_field', 'value': m['badge']})

    # Two colourways so the variant picker has something real to render.
    colours = ['Champagne Gold', 'Matte White']
    variants = []
    for c in colours:
        v = {'optionValues': [{'optionName': 'Colour', 'name': c}],
             'price': m['price'],
             'inventoryItem': {'tracked': False}}
        if m['compare_at']:
            v['compareAtPrice'] = m['compare_at']
        variants.append(v)

    res = gql(PRODUCT_SET, {
        'id': {'handle': m['handle']},
        'input': {
            'handle': m['handle'], 'title': m['title'], 'status': 'ACTIVE',
            'vendor': 'Orlant', 'productType': 'Smart Drying Rack',
            'tags': [m['series'], 'Smart Drying Rack'],
            'descriptionHtml': f'<p>{m["tagline"]}.</p>',
            'productOptions': [{'name': 'Colour',
                                'values': [{'name': c} for c in colours]}],
            'variants': variants,
            'metafields': metafields,
        },
    })['productSet']
    if res['userErrors']:
        sys.exit(f'  FAILED {m["handle"]}: {res["userErrors"]}')
    print(f'  ok       {res["product"]["handle"]:<34} {len(spec_ids)} specs, {len(variants)} variants')

print('\nSample data ready. No images uploaded - Shopify renders placeholder SVGs.')
if not METAOBJECTS_ALLOWED:
    print('Add the write_metaobjects scope and re-run to fill Specifications and FAQ.')
