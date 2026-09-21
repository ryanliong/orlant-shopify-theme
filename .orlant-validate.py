#!/usr/bin/env python3
"""Validate JSON template / section-group settings against each section's {% schema %}.

Theme Check does not catch settings ids that no longer exist in a section
schema, or range values off the allowed step - Shopify silently drops them.
Run after editing any templates/*.json or sections/*-group.json.
"""
import json, re, sys, glob, os

MISSING = object()

def schema_of(section_type):
    p = f'sections/{section_type}.liquid'
    if not os.path.exists(p):
        return MISSING
    m = re.search(r'\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}', open(p).read(), re.S)
    # Schema-less sections (e.g. main-404) are legal and carry no settings.
    return json.loads(m.group(1)) if m else None

def index(schema):
    out = {}
    for s in schema.get('settings', []):
        if 'id' in s: out[s['id']] = s
    return out

def block_index(schema):
    out = {}
    for b in schema.get('blocks', []):
        if 'type' in b:
            out[b['type']] = {s['id']: s for s in b.get('settings', []) if 'id' in s}
    return out

problems = []

def check(where, defs, settings):
    for k, v in (settings or {}).items():
        d = defs.get(k)
        if d is None:
            problems.append(f'{where}: unknown setting "{k}"')
            continue
        if d.get('type') == 'range' and isinstance(v, (int, float)):
            mn, mx, st = d['min'], d['max'], d['step']
            if v < mn or v > mx or round((v - mn) / st, 6) % 1 != 0:
                near = mn + round((v - mn) / st) * st
                problems.append(f'{where}: "{k}"={v} off range (min {mn} max {mx} step {st}) -> {near}')
        if d.get('type') == 'select' and v is not None:
            allowed = [o['value'] for o in d.get('options', [])]
            if v not in allowed:
                problems.append(f'{where}: "{k}"={v!r} not in {allowed}')

files = sorted(set(glob.glob('templates/**/*.json', recursive=True) + glob.glob('sections/*-group.json')))
for f in files:
    try:
        doc = json.load(open(f))
    except Exception as e:
        problems.append(f'{f}: invalid JSON - {e}'); continue
    for sid, sec in (doc.get('sections') or {}).items():
        st = sec.get('type')
        schema = schema_of(st)
        if schema is MISSING:
            problems.append(f'{f} [{sid}]: no section file sections/{st}.liquid'); continue
        if schema is None:
            if sec.get('settings') or sec.get('blocks'):
                problems.append(f'{f} [{sid}]: sections/{st}.liquid has no schema but settings were given')
            continue
        check(f'{f} [{sid}]', index(schema), sec.get('settings'))
        bdefs = block_index(schema)
        for bid, blk in (sec.get('blocks') or {}).items():
            bt = blk.get('type')
            if bt == '@app': continue
            if bt not in bdefs:
                problems.append(f'{f} [{sid}/{bid}]: unknown block type "{bt}"'); continue
            check(f'{f} [{sid}/{bid} {bt}]', bdefs[bt], blk.get('settings'))

print('\n'.join(problems) if problems else 'OK - all template settings valid')
sys.exit(1 if problems else 0)
