"""
The same product, already in the dataset, with its formula

What this is for
  A product sold by a Lebanese shop and the same product on Skinsort are two
  rows in this dataset whenever the merge did not judge them close enough to
  be one row. The Skinsort row often carries a full INCI list and the Lebanese
  row carries none.

  The formula is therefore already in the file. It is sitting one row away
  under a differently worded name.

  When the folder was searched for donor formulas earlier, COMBINED_DATASET
  itself was excluded from the search, so this pool was never looked at. It is
  the largest one: 1,871 of the 2,272 products with no formula belong to a
  brand that already has formulas in this same file.

Usage:
    py borrow_formula_within_dataset.py --dry     show the matches, change nothing
    py borrow_formula_within_dataset.py           write them in
"""
import os
import re
import csv
import sys
import random
import collections
import unicodedata

try:
    from rapidfuzz import fuzz
except ImportError:
    sys.exit('  needs rapidfuzz:   py -m pip install rapidfuzz')

csv.field_size_limit(10 ** 8)
DATA = 'COMBINED_DATASET.csv'
DRY = '--dry' in sys.argv
NAME_FLOOR = 90

SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|mls|g|gr|gm|oz|fl\.?\s*oz|l|kg|mg|'
                  r'pcs?|pieces?|caps?|tabs?)\b', re.I)
COUNT = re.compile(r'\b(pack|set|kit|box)\s*(of)?\s*\d+\b|\bx\s?\d+\b', re.I)
PROMO = re.compile(r'\b(new|sale|bundle|free gift|offer|promo|limited|'
                   r'exclusive|value)\b', re.I)
STOP = {'the', 'and', 'for', 'with', 'of', 'de', 'la', 'le', 'du', 'a', 'an'}

CHEM = re.compile(
    r'\b(aqua|water|glycerin|acid|sodium|extract|oil|alcohol|butter|glycol|'
    r'phenoxyethanol|tocopherol|parfum|dimethicone|niacinamide|panthenol|'
    r'xanthan|citrate|seed|leaf|fruit|root|hydroxide|stearate|cetearyl)\b',
    re.I)


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore') \
        .decode().lower()


def bkey(b):
    return re.sub(r'[^a-z0-9]', '', re.sub(r'^(the|by)\s+', '', asc(b).strip()))


def nkey(name):
    s = PROMO.sub(' ', COUNT.sub(' ', SIZE.sub(' ', asc(name))))
    return ' '.join(sorted(w for w in re.split(r'[^a-z0-9]+', s)
                           if w and w not in STOP))


def looks_like_a_formula(s):
    t = str(s).strip()
    if len(t) < 40 or t.count(',') < 3:
        return False
    parts = [p.strip() for p in t.split(',') if p.strip()]
    if len(parts) < 5:
        return False
    if sum(1 for p in parts if len(p) < 46) / len(parts) < 0.75:
        return False
    return sum(1 for p in parts if CHEM.search(p)) >= 3


with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


donors = collections.defaultdict(list)
for r in D:
    ing = g(r, 'ingredients')
    if looks_like_a_formula(ing):
        donors[bkey(g(r, 'brand'))].append((nkey(g(r, 'name')), r))

need = [r for r in D if not g(r, 'ingredients')]

print('=' * 74)
print('  THE SAME PRODUCT, ALREADY IN THE DATASET, WITH ITS FORMULA')
print('=' * 74)
print(f'  rows in the file              {len(D):,}')
print(f'  rows with no formula          {len(need):,}')
print(f'  rows that can donate one      {sum(len(v) for v in donors.values()):,}')
print(f'  name similarity required      {NAME_FLOOR}')
print()

filled = []
blocked_type = 0
for r in need:
    pool = donors.get(bkey(g(r, 'brand')))
    if not pool:
        continue
    mine = nkey(g(r, 'name'))
    if not mine:
        continue
    best, score = None, 0
    for dk, d in pool:
        if not dk or d is r:
            continue
        s = fuzz.token_set_ratio(mine, dk)
        if s > score:
            best, score = d, s
    if not best or score < NAME_FLOOR:
        continue
    # the two rows must not be different kinds of product
    t1, t2 = asc(g(r, 'product_type')), asc(g(best, 'product_type'))
    if t1 and t2 and t1 != t2:
        blocked_type += 1
        continue
    filled.append((r, best, score))

print(f'  matched                       {len(filled):,}')
print(f'  refused, product type differs {blocked_type:,}')
print()

print('  TWELVE MATCHES, PICKED AT RANDOM, TO BE READ BEFORE ANYTHING IS SAVED')
print('  ' + '-' * 70)
random.seed(7)
for r, d, s in random.sample(filled, min(12, len(filled))):
    print(f'  {g(r, "brand")}   (similarity {s:.0f})')
    print(f'     empty : {g(r, "name")[:62]}')
    print(f'             {g(r, "source_category")}, type "{g(r, "product_type")}"')
    print(f'     donor : {g(d, "name")[:62]}')
    print(f'             {g(d, "source_category")}, type "{g(d, "product_type")}"')
    print(f'     gives : {g(d, "ingredients")[:66]}...')
    print()

if DRY:
    print('  --dry, nothing was written.')
    print('  read the matches above. if they are the same product, run again')
    print('  without --dry.')
    sys.exit(0)

for r, d, s in filled:
    ing = g(d, 'ingredients')
    r['ingredients'] = ing
    if 'ingredient_count' in r:
        r['ingredient_count'] = str(len([p for p in re.split(r'[,;]', ing)
                                         if p.strip(' .;:-')]))
    if 'ingredient_source' in r:
        r['ingredient_source'] = f'borrowed from {g(d, "product_id")}'

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
    sys.exit(f'  the file came back damaged at byte {e.start:,}, nothing written')
os.replace(tmp, DATA)

got = sum(1 for r in D if g(r, 'ingredients'))
print(f'  written. ingredients now {got:,} of {len(D):,} '
      f'({100 * got / len(D):.1f}%)')
print('\n  now rebuild what is computed from the formula:')
print('     py derive_from_ingredients.py')
print('     py fill_from_formula.py')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
