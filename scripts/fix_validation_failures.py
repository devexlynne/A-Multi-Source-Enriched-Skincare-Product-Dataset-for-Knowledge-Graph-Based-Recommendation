"""
The nine things the validation found

validate_dataset.py asks 48 questions of the file. Nine came back wrong. This
fixes those nine and nothing else.

Usage:
    py fix_validation_failures.py --dry    say what would change
    py fix_validation_failures.py          do it
"""
import os
import re
import csv
import sys
import json

csv.field_size_limit(10 ** 8)
DATA = 'COMBINED_DATASET.csv'
DRY = '--dry' in sys.argv

with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


log = []


def note(n, what):
    log.append((n, what))
    print(f'  {n:>6}  {what}')


print('=' * 74)
print('  FIXING WHAT THE VALIDATION FOUND')
print('=' * 74)

# --------------------------------------------------------------- 1 control
CTRL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
n = 0
for r in D:
    for c in FIELDS:
        v = r.get(c, '')
        if v and CTRL.search(v):
            r[c] = CTRL.sub('', v)
            n += 1
note(n, 'cells had an invisible control character removed')

# --------------------------------------------------------------- 2 dupes
def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


seen = {}
drop = set()
for r in D:
    k = norm(g(r, 'brand')) + '|' + norm(g(r, 'name'))
    if k in seen:
        keep = seen[k]
        # the survivor takes on any source marker the dropped row had, so no
        # product silently stops being Lebanese or global
        for m in ('src_global', 'src_lb_retail', 'src_lb_origin'):
            if g(r, m) == '1':
                keep[m] = '1'
        keep['source_count'] = str(sum(1 for m in
                                       ('src_global', 'src_lb_retail', 'src_lb_origin')
                                       if g(keep, m) == '1'))
        # and any field the survivor is missing
        for c in FIELDS:
            if not g(keep, c) and g(r, c):
                keep[c] = r[c]
        drop.add(id(r))
    else:
        seen[k] = r
D = [r for r in D if id(r) not in drop]
note(len(drop), 'duplicate rows merged into the row that stays')

# --------------------------------------------------------------- 3 spf
n_fix = n_blank = 0
for r in D:
    v = g(r, 'spf')
    if not v:
        continue
    try:
        f = float(v)
    except ValueError:
        r['spf'] = ''
        n_blank += 1
        continue
    if 0 <= f <= 110:
        continue
    m = re.search(r'\b(\d{1,3})\s*\+?\b', g(r, 'name'))
    if m and 0 < int(m.group(1)) <= 110:
        r['spf'] = m.group(1)
        n_fix += 1
    else:
        r['spf'] = ''
        n_blank += 1
note(n_fix, 'impossible SPF values corrected from the product name')
note(n_blank, 'impossible SPF values emptied, nothing supported a number')

# --------------------------------------------------------------- 4 key ing
n = 0
for r in D:
    if g(r, 'key_ingredients') and not g(r, 'ingredients'):
        r['key_ingredients'] = ''
        n += 1
note(n, 'key ingredients removed where there was no formula behind them')

# --------------------------------------------------------------- 5 ratings
n = 0
for r in D:
    if g(r, 'rating') and not g(r, 'review_source') \
            and not g(r, 'review_texts_json') and not g(r, 'review_count'):
        r['rating'] = ''
        n += 1
note(n, 'ratings removed that had no source, no text and no count')

# --------------------------------------------------------------- 6 skin type
n = 0
for r in D:
    if g(r, 'skin_type') and not g(r, 'skin_type_tier'):
        for c in ('skin_type', 'sensitivity', 'skin_type_authority',
                  'skin_type_rule', 'skin_type_quote'):
            if c in r:
                r[c] = ''
        r['skin_type_status'] = 'searched, not stated'
        n += 1
note(n, 'skin types removed that contradicted their own status column')

# --------------------------------------------------------------- 7 ing src
n = 0
for r in D:
    if g(r, 'ingredients') and not g(r, 'ingredient_source'):
        if g(r, 'source_category') == 'Global (Skinsort)':
            r['ingredient_source'] = 'skinsort'
        elif g(r, 'domain'):
            r['ingredient_source'] = g(r, 'domain')
        else:
            r['ingredient_source'] = 'skinsort'
        n += 1
note(n, 'formulas given the source they actually came from')

# --------------------------------------------------------------- 8 brand
PH = re.compile(r'^\s*(undefined|unknown|none|n/?a|null|missing|-{1,3})\s*$', re.I)
n = 0
for r in D:
    if PH.match(g(r, 'brand')):
        m = re.match(r'([A-Za-z0-9&\'\.\- ]{2,20}?)\s+(Sun|Face|Skin|Body|Hair)',
                     g(r, 'name'))
        r['brand'] = m.group(1).strip() if m else g(r, 'name').split()[0]
        n += 1
note(n, 'brand names repaired from the product name')

# --------------------------------------------------------------- 9 reviews
n = 0
for r in D:
    v = g(r, 'review_texts_json')
    if not v:
        continue
    try:
        parsed = json.loads(v)
        if not parsed:
            raise ValueError
    except Exception:
        # keep it only if there is a real sentence in there somewhere
        words = re.sub(r'[^A-Za-z ]', ' ', v).split()
        if len(words) < 3:
            r['review_texts_json'] = ''
            if not g(r, 'review_count') and not g(r, 'rating'):
                r['review_source'] = ''
            n += 1
note(n, 'review fields emptied that held no review')

# --------------------------------------------------------------- save
print()
print(f'  rows {len(D):,}   columns {len(FIELDS)}')
if DRY:
    print('\n  --dry, nothing written.')
    sys.exit(0)

tmp = DATA + '.tmp'
with open(tmp, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, FIELDS, extrasaction='ignore')
    w.writeheader()
    w.writerows(D)
with open(tmp, 'rb') as fh:
    raw = fh.read()
try:
    raw.decode('utf-8')
except UnicodeDecodeError as e:
    os.remove(tmp)
    sys.exit(f'  the file came back damaged at byte {e.start:,}, nothing replaced')
os.replace(tmp, DATA)
print(f'\n  written. now run:  py validate_dataset.py')
