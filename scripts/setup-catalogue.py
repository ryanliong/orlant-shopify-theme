#!/usr/bin/env python3
"""Load the real Orlant catalogue: one product per model and size.

Reads specs from 00-docs/specs.csv (H2 catalogue, authoritative; brochure fills gaps) and images from the prepared web folder.
Replaces the invented sample products from the first build.

  * One product per size (M6S and M6L separate), linked through
    orlant.size_sibling so each page can switch to the other size.
  * Colour is a variant only where a model has a real choice (M5).
  * Products without a confirmed price are created as drafts and never
    published — the script refuses to publish anything priced at zero.
  * Descriptions and taglines use only facts from the brochure.
  * Feature icons are listed per model, leaving out any icon that is wrong
    or unverified for that model (see comments).

Idempotent: products are upserted by handle. Media is only added to a
product that has none; pass --refresh-media to replace it.

Usage:
    SHOP=orlant-gujfiai0.myshopify.com python3 scripts/setup-catalogue.py
"""
import csv, json, os, subprocess, sys, urllib.request

SHOP = os.environ.get('SHOP')
API = os.environ.get('API_VERSION', '2026-07')
ASSETS = os.path.expanduser(os.environ.get('ASSETS', '~/Documents/shopify/orlant-assets'))
TOKEN = open(os.path.expanduser(os.environ.get('TOKEN_FILE', '~/.orlant-admin-token'))).read().strip()
REFRESH = '--refresh-media' in sys.argv
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


def rest(method, path, payload=None):
    req = urllib.request.Request(f'https://{SHOP}/admin/api/{API}/{path}',
        data=json.dumps(payload).encode() if payload is not None else None,
        headers={'X-Shopify-Access-Token': TOKEN, 'Content-Type': 'application/json'}, method=method)
    with urllib.request.urlopen(req) as r:
        return json.load(r)


SPECS = {r['model']: r for r in csv.DictReader(open(f'{ASSETS}/00-docs/specs.csv'))}

# Feature icons per model, in display order. Omitted on purpose:
#   * "Plasma sterilisation" (M6, D6): no icon supplied; the UV icon would be wrong.
#   * "Aluminium" (M5, M6, D6): the client's "Aluminium" file reads 304 Stainless Steel.
#   * Pole-extend icons where none matches the spec, or the figure is disputed
#     (M6S, X6S — client questions 16 and 17; M5 "x4+5" has no icon).
COMMON_LIFT = ['lifting-height-control', 'one-touch-rising']
# Per the H2 catalogue (authoritative, client-confirmed 31 Oct 2026). Eco mode
# is not listed for any model in the catalogue, so its icon is not shown.
# M6 poles are "x6", which no pole-extend icon matches, so none is shown.
FEATURES = {
    'M6L': ['ec-blowers-high-speed', 'ec-blowers-6', 'cross-flow-wind', 'ptc-heater-4', 'double-layer-frame',
            'uv-disinfection', 'negative-oxygen-anion', *COMMON_LIFT, 'overweight-alarm-55kg', 'voice-control',
            'app-monitoring', 'led-panel-light-3-tone'],
    'M6S': ['ec-blowers-high-speed', 'ec-blowers-4', 'cross-flow-wind', 'ptc-heater-4', 'double-layer-frame',
            'uv-disinfection', 'negative-oxygen-anion', *COMMON_LIFT, 'overweight-alarm-55kg', 'voice-control',
            'app-monitoring', 'led-panel-light-3-tone'],
    'M5L': ['ec-blowers-high-speed', 'ec-blowers-6', 'cross-flow-wind', 'ptc-heater-4', 'double-layer-frame',
            'uv-disinfection', 'negative-oxygen-anion', *COMMON_LIFT, 'overweight-alarm-45kg', 'app-monitoring',
            'led-panel-light'],
    'M5S': ['ec-blowers-high-speed', 'ec-blowers-4', 'cross-flow-wind', 'ptc-heater-4', 'double-layer-frame',
            'uv-disinfection', 'negative-oxygen-anion', *COMMON_LIFT, 'overweight-alarm-45kg', 'app-monitoring',
            'led-panel-light'],
    'D6L': ['ec-blowers-high-speed', 'ec-blowers-4', 'cross-flow-wind', 'poles-2-3m-4-plus-3', 'ptc-heater-4',
            'double-layer-frame', 'negative-oxygen-anion', *COMMON_LIFT, 'overweight-alarm-45kg',
            'drying-indicator-light', 'led-panel-light'],
    'D6S': ['ec-blowers-high-speed', 'ec-blowers-4', 'cross-flow-wind', 'poles-2-0m-4-plus-3', 'ptc-heater-4',
            'double-layer-frame', 'negative-oxygen-anion', *COMMON_LIFT, 'overweight-alarm-45kg',
            'drying-indicator-light', 'led-panel-light'],
    # Not in the H2 catalogue (client question 5); brochure data kept for now.
    'X6S': ['ec-blowers-high-speed', 'ec-blowers-6', 'double-layer-frame', 'cross-flow-wind',
            'stainless-steel-304', 'ptc-heater-4', 'negative-oxygen-anion', 'uv-disinfection', *COMMON_LIFT,
            'eco-mode', 'overweight-alarm-45kg', 'voice-control', 'app-monitoring', 'led-panel-light'],
    'X6L': ['ec-blowers-4', 'ptc-heater-4', 'stainless-steel-304', 'double-layer-frame'],
}
# Merchandising badges, in the client's own words from their current site.
BADGES = {'D6L': 'New', 'D6S': 'New', 'X6L': 'Space-saving', 'X6S': 'Space-saving',
          'M6L': '2026 Bestseller', 'M6S': '2026 Bestseller'}
SIBLING = {'M5L': 'M5S', 'M5S': 'M5L', 'M6L': 'M6S', 'M6S': 'M6L',
           'X6L': 'X6S', 'X6S': 'X6L', 'D6L': 'D6S', 'D6S': 'D6L'}
COLOUR_VARIANTS = {'M5L': ['Titanium Grey', 'Bright White'], 'M5S': ['Titanium Grey', 'Bright White']}
INVENTED = ['orlant-x1-smart-drying-rack', 'orlant-m2-smart-drying-rack',
            'orlant-d3-smart-drying-rack', 'orlant-e5-smart-drying-rack']
INVENTED_FAQ = ['fits-false-ceiling', 'install-time', 'hdb-permission', 'power-supply']

def num(v): return int(v) if v not in ('', None) else None
def yes(v): return v == 'yes'

def short_steril(v):
    return 'Plasma' if v.lower().startswith('plasma') else 'UV' if v.lower().startswith('uv') else ''

def tagline(m, s):
    parts = []
    if num(s['load_kg']): parts.append(f"{s['load_kg']} kg load")
    if num(s['ec_blowers']): parts.append(f"{s['ec_blowers']} EC blowers")
    if yes(s['voice_control']) and yes(s['app_control']): parts.append('voice and app control')
    elif yes(s['app_control']): parts.append('app control')
    elif short_steril(s['sterilisation']): parts.append('UV disinfection' if short_steril(s['sterilisation']) == 'UV' else 'plasma sterilisation')
    elif yes(s.get('ionizer')): parts.append('ioniser')
    if m == 'X6L': parts = ['4 EC blowers', '4 PTC heaters', '304 stainless frame']
    return ' · '.join(parts)

def description(m, s):
    if m == 'X6L':
        return ('<p>The X6L has a 304 stainless steel double-layer frame, '
                'four EC blowers and four PTC heaters.</p>')
    ctrl = ('Control it by voice or from the app.' if yes(s['voice_control']) and yes(s['app_control'])
            else 'Control it from the app.' if yes(s['app_control']) else 'Controlled by remote.')
    steril = {'Plasma': 'plasma sterilisation', 'UV': 'UV disinfection'}.get(short_steril(s['sterilisation']), '')
    if yes(s.get('ionizer')):
        steril = f'{steril} and an ioniser' if steril else 'an ioniser'
    return (f"<p>Ceiling-mounted smart drying rack with a double-layer frame. "
            f"Poles extend from {s['pole_min_mm']} to {s['pole_max_mm']} mm and the rack carries up to "
            f"{s['load_kg']} kg.</p>"
            f"<p>{s['ec_blowers']} EC blowers and {s['ptc_heaters']} PTC heaters dry the load"
            f"{', with ' + steril if steril else ''}. {ctrl}</p>")

def metafields(m, s, feature_ids):
    out = []
    def add(key, typ, val):
        if val not in (None, ''):
            out.append({'namespace': 'orlant', 'key': key, 'type': typ, 'value': str(val)})
    add('series', 'single_line_text_field', f"{s['series']} Series")
    add('size', 'single_line_text_field', s['size'])
    add('card_tagline', 'single_line_text_field', tagline(m, s))
    add('badge', 'single_line_text_field', BADGES.get(m))
    if m not in COLOUR_VARIANTS:
        add('colour', 'single_line_text_field', s['colours'])
    for key in ('host_length_mm', 'host_width_mm', 'host_height_mm', 'pole_min_mm', 'pole_max_mm',
                'lifting_height_mm', 'load_kg', 'led_power_w', 'ec_blowers', 'ptc_heaters'):
        add(key, 'number_integer', num(s[key]))
    add('power_w', 'number_integer', num(s['power_w']))
    add('sterilisation', 'single_line_text_field', short_steril(s['sterilisation']))
    for key in ('voice_control', 'app_control', 'eco_mode', 'ionizer'):
        if s.get(key):
            add(key, 'boolean', 'true' if yes(s[key]) else 'false')
    add('features', 'list.metaobject_reference', json.dumps([feature_ids[h] for h in FEATURES[m]]))
    return out


def stage(path):
    mime = 'image/png' if path.endswith('.png') else 'image/jpeg'
    st = gql('''mutation($i:[StagedUploadInput!]!){stagedUploadsCreate(input:$i){
                stagedTargets{url resourceUrl parameters{name value}} userErrors{message}}}''',
             {'i': [{'resource': 'IMAGE', 'filename': os.path.basename(path), 'mimeType': mime,
                     'httpMethod': 'POST', 'fileSize': str(os.path.getsize(path))}]})['stagedUploadsCreate']
    t = st['stagedTargets'][0]
    cmd = ['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}', '-X', 'POST', t['url']]
    for p in t['parameters']: cmd += ['-F', f'{p["name"]}={p["value"]}']
    cmd += ['-F', f'file=@{path}']
    if subprocess.run(cmd, capture_output=True, text=True).stdout.strip() not in ('200', '201', '204'):
        sys.exit(f'upload failed: {path}')
    return t['resourceUrl']


def alt(title, fname):
    if 'installed' in fname: return f'{title} installed in a home'
    if 'drawing' in fname: return f'{title} dimension drawing'
    return f'{title}'


# ---------------------------------------------------------------------------
print('Removing invented sample data')
print('-' * 62)
for h in INVENTED:
    p = gql('query($h:String!){productByHandle(handle:$h){id}}', {'h': h})['productByHandle']
    if p:
        gql('mutation($i:ProductDeleteInput!){productDelete(input:$i){deletedProductId}}', {'i': {'id': p['id']}})
        print(f'  deleted  product {h}')
spec_rows = gql('{metaobjects(type:"orlant_spec_row",first:100){nodes{id handle}}}')['metaobjects']['nodes']
faqs = gql('{metaobjects(type:"orlant_faq_item",first:50){nodes{id handle}}}')['metaobjects']['nodes']
for mo in [n for n in spec_rows if n['handle'].startswith('orlant-')] + [n for n in faqs if n['handle'] in INVENTED_FAQ]:
    gql('mutation($id:ID!){metaobjectDelete(id:$id){deletedId}}', {'id': mo['id']})
print(f'  deleted  {len([n for n in spec_rows if n["handle"].startswith("orlant-")])} spec rows, '
      f'{len([n for n in faqs if n["handle"] in INVENTED_FAQ])} FAQ items')

feature_ids = {n['handle']: n['id'] for n in
               gql('{metaobjects(type:"orlant_feature",first:100){nodes{id handle}}}')['metaobjects']['nodes']}
missing = {h for f in FEATURES.values() for h in f} - set(feature_ids)
if missing: sys.exit(f'feature entries missing, run setup-features.py: {missing}')

PRODUCT_SET = '''mutation($id:ProductSetIdentifiers,$input:ProductSetInput!){
  productSet(identifier:$id,input:$input,synchronous:true){
    product{id handle mediaCount{count}} userErrors{field message code}}}'''

print('\nProducts')
print('-' * 62)
ids = {}
for m, s in SPECS.items():
    handle = m.lower()
    title = f'{m} Smart Drying Rack'
    # Retail price from the H2 catalogue. Whether to show the roadshow
    # promotional price as a sale is client question 32, so no compare-at yet.
    price = s['price_retail_catalogue'] or s['price_sgd_live_site']
    compare = '' if s['price_retail_catalogue'] else s['compare_at_sgd_live_site']
    priced = bool(price) and float(price) > 0
    colours = COLOUR_VARIANTS.get(m)
    if colours:
        options = [{'name': 'Colour', 'values': [{'name': c} for c in colours]}]
        variants = [{'optionValues': [{'optionName': 'Colour', 'name': c}]} for c in colours]
    else:
        options = [{'name': 'Title', 'values': [{'name': 'Default Title'}]}]
        variants = [{'optionValues': [{'optionName': 'Title', 'name': 'Default Title'}]}]
    for v in variants:
        v['price'] = price or '0.00'
        v['inventoryItem'] = {'tracked': False}   # stock tracking pending client question 14
        v['compareAtPrice'] = compare if (compare and price and float(compare) > float(price)) else None
    res = gql(PRODUCT_SET, {'id': {'handle': handle}, 'input': {
        'handle': handle, 'title': title,
        'status': 'ACTIVE' if priced else 'DRAFT',
        'vendor': 'Orlant International', 'productType': 'Smart Drying Rack',
        'tags': [f"{s['series']} Series", 'Smart Drying Rack'] + ([] if priced else ['price-pending']),
        'descriptionHtml': description(m, s),
        'productOptions': options, 'variants': variants,
        'metafields': metafields(m, s, feature_ids),
    }})['productSet']
    if res['userErrors']:
        sys.exit(f'  FAILED {m}: {res["userErrors"]}')
    pid = res['product']['id']; ids[m] = pid

    # productSet adds and updates metafields but never removes them, so clear
    # any spec this model no longer has a value for (e.g. eco mode, which the
    # catalogue does not list, or D6 sterilisation).
    stale = [k for k in ('sterilisation', 'eco_mode', 'voice_control', 'app_control', 'ionizer')
             if not s.get(k)]
    if stale:
        gql('''mutation($m:[MetafieldIdentifierInput!]!){metafieldsDelete(metafields:$m){userErrors{message}}}''',
            {'m': [{'ownerId': pid, 'namespace': 'orlant', 'key': k} for k in stale]})

    media_dir = f'{ASSETS}/web/{handle}'
    files = sorted(os.listdir(media_dir)) if os.path.isdir(media_dir) else []
    have = res['product']['mediaCount']['count']
    if files and (have == 0 or REFRESH):
        if have:
            old = gql('query($id:ID!){product(id:$id){media(first:50){nodes{id}}}}', {'id': pid})['product']['media']['nodes']
            gql('mutation($p:ID!,$m:[ID!]!){productDeleteMedia(productId:$p,mediaIds:$m){deletedMediaIds}}',
                {'p': pid, 'm': [n['id'] for n in old]})
        media = [{'originalSource': stage(f'{media_dir}/{f}'), 'mediaContentType': 'IMAGE', 'alt': alt(title, f)}
                 for f in files]
        r = gql('mutation($p:ID!,$m:[CreateMediaInput!]!){productCreateMedia(productId:$p,media:$m){mediaUserErrors{message}}}',
                {'p': pid, 'm': media})['productCreateMedia']
        if r['mediaUserErrors']: sys.exit(f'  media FAILED {m}: {r["mediaUserErrors"]}')
        media_note = f'{len(files)} images'
    else:
        media_note = f'{have} images (kept)'

    if priced:
        num_id = pid.rsplit('/', 1)[-1]
        rest('PUT', f'products/{num_id}.json', {'product': {'id': int(num_id), 'published': True}})
        state = 'live '
    else:
        state = 'DRAFT'
    print(f'  {state}  {handle:<5} {title:<24} S${price or "—":<6} {media_note}, {len(FEATURES[m])} features')

print('\nSize links')
print('-' * 62)
for m, other in SIBLING.items():
    gql('''mutation($m:[MetafieldsSetInput!]!){metafieldsSet(metafields:$m){userErrors{message}}}''',
        {'m': [{'ownerId': ids[m], 'namespace': 'orlant', 'key': 'size_sibling',
                'type': 'product_reference', 'value': ids[other]}]})
print('  ' + ', '.join(f'{a}<->{b}' for a, b in SIBLING.items() if a < b))
print('\nDone. Draft products have no confirmed price and are not published.')
