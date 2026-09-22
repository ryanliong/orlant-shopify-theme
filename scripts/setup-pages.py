#!/usr/bin/env python3
"""Create the Orlant supporting pages and attach their theme templates.

Placeholder copy throughout — the client supplies the real words. The point is
that every page exists, is styled, and is linkable, so navigation and the
footer can be wired before content lands.

Idempotent: existing pages are left alone apart from re-attaching the template
suffix, which is what binds a page to templates/page.<suffix>.json.

Usage:
    SHOP=orlant-gujfiai0.myshopify.com python3 scripts/setup-pages.py
"""
import json, os, sys, urllib.request

SHOP = os.environ.get('SHOP')
API = os.environ.get('API_VERSION', '2026-07')
TOKEN = open(os.path.expanduser(os.environ.get('TOKEN_FILE', '~/.orlant-admin-token'))).read().strip()
if not SHOP:
    sys.exit('SHOP env var required.')


def rest(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(
        f'https://{SHOP}/admin/api/{API}/{path}', data=data,
        headers={'X-Shopify-Access-Token': TOKEN, 'Content-Type': 'application/json'},
        method=method)
    with urllib.request.urlopen(req) as r:
        return json.load(r)


PLACEHOLDER = '<p><em>Placeholder copy — to be replaced with content from the client.</em></p>'

PAGES = [
    ('about', 'About Orlant', 'about',
     PLACEHOLDER + '<p>Orlant designs and installs smart drying racks for Singapore homes. '
     'Every rack is fitted by our own technicians and backed by a two-year warranty.</p>'),
    ('contact', 'Contact', 'contact',
     PLACEHOLDER + '<p>Opening hours, address and phone number go here. '
     'The form below reaches the Singapore team.</p>'),
    ('faq', 'Frequently asked questions', 'faq',
     PLACEHOLDER + '<p>Answers to the questions we are asked most often about ordering, '
     'installation and warranty.</p>'),
    ('compatibility', 'System compatibility', 'compatibility',
     PLACEHOLDER + '<p>Which ceilings, flats and service yards suit which model.</p>'),
]

existing = {p['handle']: p for p in rest('GET', 'pages.json?limit=250')['pages']}

print('Pages')
print('-' * 62)
for handle, title, suffix, body in PAGES:
    payload = {'page': {
        'handle': handle, 'title': title,
        'body_html': body,
        # Binds the page to templates/page.<suffix>.json.
        'template_suffix': suffix,
        'published': True,
    }}
    if handle in existing:
        pid = existing[handle]['id']
        payload['page']['id'] = pid
        res = rest('PUT', f'pages/{pid}.json', payload)['page']
        print(f'  updated  /pages/{res["handle"]:<16} template: page.{res["template_suffix"]}')
    else:
        res = rest('POST', 'pages.json', payload)['page']
        print(f'  created  /pages/{res["handle"]:<16} template: page.{res["template_suffix"]}')

print('\nCopy is placeholder. Replace in Content > Pages when the client supplies it.')
