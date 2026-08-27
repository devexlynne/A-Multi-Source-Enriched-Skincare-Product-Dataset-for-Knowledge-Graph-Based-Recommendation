"""
Ingredients from files we already have

2,578 products have no ingredient list. Before paying anyone to search for
them, every CSV in the Thesis folder is read to see whether the formula is
already sitting in an older file under a slightly different product name.

Two passes
  1. exact: the same brand and the same significant words
  2. close: the same brand, and a name similarity of 88 or above

The second pass only ever compares products of the SAME BRAND, so a CeraVe
lotion can never take its formula from a Nivea one. Within a brand the risk is
a variant, so the threshold is higher than the 90 used for merging whole
records, and size and shade words are stripped first.

Anything accepted records where it came from, so a reader can tell a recovered
formula from a scraped one.

Usage:
    py recover_ingredients_offline.py --dry
    py recover_ingredients_offline.py
"""
import os
import re
import csv
import sys
import glob
import collections
import unicodedata

try:
    from rapidfuzz import fuzz
except ImportError:
    fuzz = None

csv.field_size_limit(10 ** 8)
DATA = 'COMBINED_DATASET.csv'
ROOT = os.path.dirname(os.path.abspath(DATA))
DRY = '--dry' in sys.argv

SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)
PROMO = re.compile(r'buy\s*\d*\s*get\s*\d*|bundle|free gift|new|sale', re.I)
STOP = {'the', 'and', 'for', 'with', 'of', 'de', 'la', 'le', 'du', 'new',
        'pack', 'set', 'kit', 'ml', 'g', 'gr', 'oz', 'fl'}


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()


def bkey(b):
    return re.sub(r'[^a-z0-9]', '', re.sub(r'^(the|by)\s+', '', asc(b).strip()))


def nkey(name):
    s = PROMO.sub(' ', SIZE.sub(' ', asc(name)))
    return ' '.join(sorted(w for w in re.split(r'[^a-z0-9]+', s)
                           if w and w not in STOP))


def looks_like_a_formula(s):
    """The same shape test used everywhere else: a list, not a sentence."""
    t = str(s).strip()
    if len(t) < 40 or t.count(',') < 3:
        return False
    parts = [p.strip() for p in t.split(',') if p.strip()]
    if len(parts) < 5:
        return False
    short = sum(1 for p in parts if len(p) < 46)
    if short / len(parts) < 0.75:
        return False
    CHEM = re.compile(r'\b(aqua|water|glycerin|acid|sodium|extract|oil|alcohol|'
                      r'butter|glycol|phenoxyethanol|tocopherol|parfum|'
                      r'dimethicone|niacinamide|panthenol|xanthan|citrate|'
                      r'seed|leaf|fruit|root|hydroxide|stearate|behenate)\b', re.I)
    if sum(1 for p in parts if CHEM.search(p)) < 3:
        return False
    return True


with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


need = [r for r in D if not g(r, 'ingredients')]
print('=' * 72)
print('  INGREDIENTS FROM FILES WE ALREADY HAVE')
print('=' * 72)
print(f'  {len(D):,} products, {len(need):,} with no formula')

# ---------------------------------------------------- read every other file
bank = collections.defaultdict(list)   # brand key -> [(name key, name, ing, file)]
files = sorted(set(glob.glob(os.path.join(ROOT, '*.csv')) +
                   glob.glob(os.path.join(ROOT, '..', '*.csv')) +
                   glob.glob(os.path.join(ROOT, '..', '*', '*.csv'))))
n_scanned = 0
for path in files:
    base = os.path.basename(path)
    if base in ('COMBINED_DATASET.csv', 'SKINCARE_FINAL.csv'):
        continue
    try:
        with open(path, newline='', encoding='utf-8', errors='replace') as fh:
            rd = csv.DictReader(fh)
            cols = [c for c in (rd.fieldnames or []) if c]
            low = {c.lower(): c for c in cols}
            ic = next((low[c] for c in ('ingredients', 'ingredient_list', 'inci',
                                        'full_ingredients') if c in low), None)
            bc = next((low[c] for c in ('brand', 'brand_name') if c in low), None)
            nc = next((low[c] for c in ('name', 'product_name', 'product',
                                        'title') if c in low), None)
            if not (ic and bc and nc):
                continue
            n_scanned += 1
            for row in rd:
                ing = (row.get(ic) or '').strip()
                if not looks_like_a_formula(ing):
                    continue
                bank[bkey(row.get(bc) or '')].append(
                    (nkey(row.get(nc) or ''), (row.get(nc) or '').strip(),
                     ing, base))
    except Exception:
        continue
print(f'  {n_scanned} other files carried an ingredient column, '
      f'{sum(len(v) for v in bank.values()):,} formulas read')

# ------------------------------------------------------------- match them
n_exact = n_close = 0
from_file = collections.Counter()
examples = []
for r in need:
    bk = bkey(g(r, 'brand'))
    cands = bank.get(bk)
    if not cands:
        continue
    mine = nkey(g(r, 'name'))
    hit = next((c for c in cands if c[0] == mine and c[0]), None)
    how = 'exact'
    if not hit and fuzz and mine:
        best, score = None, 0
        for c in cands:
            if not c[0]:
                continue
            s = fuzz.token_set_ratio(mine, c[0])
            if s > score:
                best, score = c, s
        if score >= 88:
            hit, how = best, f'close, {score:.0f}'
    if not hit:
        continue
    r['ingredients'] = hit[2]
    r['ingredient_count'] = str(len([p for p in re.split(r'[,;]', hit[2])
                                     if p.strip(' .;:-')]))
    r['ingredient_source'] = f'recovered from {hit[3]}'
    from_file[hit[3]] += 1
    if how == 'exact':
        n_exact += 1
    else:
        n_close += 1
    if len(examples) < 4:
        examples.append((g(r, 'brand'), g(r, 'name')[:34], hit[1][:34], how,
                         hit[2][:52]))

got = sum(1 for r in D if g(r, 'ingredients'))
print(f'\n  matched exactly   {n_exact:,}')
print(f'  matched closely   {n_close:,}')
print(f'  ingredients now   {got:,}  ({100*got/len(D):.1f}%)')
print()
for k, v in from_file.most_common():
    print(f'     {v:5,} from {k}')
print('\n  EXAMPLES')
for b, mine, theirs, how, ing in examples:
    print(f'    {b[:16]:18s}{mine}')
    print(f'      matched {how} to: {theirs}')
    print(f'      formula: {ing}...')

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
    sys.exit(f'  came back damaged at byte {e.start:,}, nothing written')
os.replace(tmp, DATA)
print(f'\n  written. now run:  py derive_from_ingredients.py --overwrite')
