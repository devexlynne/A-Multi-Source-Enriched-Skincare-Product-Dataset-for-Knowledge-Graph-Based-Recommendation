"""
The last four things

A full audit of the finished file found four faults that none of the 50 checks
ask about. Each is small to describe and each changes what a reader sees.

  1. ONE BRAND, FIVE SPELLINGS. A-derma, ADERMA, Aderma, A-Derma and aderma
     are all the same company. To a computer they are five brands, so the
     brand count is wrong, grouping by brand splits a maker into pieces, and
     any per-brand figure in the thesis is understated. 104 brands were
     affected.

Usage:
    py final_polish.py --dry
    py final_polish.py
"""
import os
import re
import csv
import sys
import unicodedata
import collections

csv.field_size_limit(10 ** 8)
DATA = 'COMBINED_DATASET.csv'
DRY = '--dry' in sys.argv

with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


print('=' * 72)
print('  THE LAST FOUR THINGS')
print('=' * 72)

# ------------------------------------------------------------- 1. mojibake
# Text that was written as UTF-8 and then read as Latin-1 comes back with
# these signatures. The repair is to reverse exactly that.
FIX = {
    'â„¢': '™', 'â"¢': '™', 'â€™': "'", 'â€œ': '"', 'â€\x9d': '"',
    'â€"': '-', 'â€"': '-', 'â€¦': '...', 'Â®': '®', 'Â': '',
    'Ã©': 'é', 'Ã¨': 'è', 'Ã ': 'à', 'Ã§': 'ç', 'Ã´': 'ô', 'Ã¢': 'â',
    'Ã®': 'î', 'Ã»': 'û', 'Ã¹': 'ù', 'Ã«': 'ë', 'Ã¯': 'ï',
}
BROKEN = re.compile('|'.join(re.escape(k) for k in FIX))
LEFTOVER = re.compile(r'â[^\s\w]{0,2}|Ã.')

n_fix = 0
examples = []
for r in D:
    for c in ('brand', 'name', 'product_summary', 'benefits', 'key_ingredients'):
        v = r.get(c, '')
        if not v or not BROKEN.search(v):
            continue
        old = v
        new = BROKEN.sub(lambda m: FIX[m.group(0)], v)
        new = LEFTOVER.sub('', new)
        new = re.sub(r'\s+', ' ', new).strip()
        if new != old:
            r[c] = new
            n_fix += 1
            if len(examples) < 3 and c == 'name':
                examples.append((old[:44], new[:44]))
print(f'\n  1. BROKEN CHARACTERS')
print(f'     repaired in {n_fix:,} cells')
for a, b in examples:
    print(f'        {a}')
    print(f'     -> {b}')

# ---------------------------------------------------------- 2. brand names
NOT_A_BRAND = re.compile(r'^(kit|set|pack|bundle|the body set|new|sale|'
                         r'offer|gift)\b[:\s]*$', re.I)
n_notbrand = 0
for r in D:
    if NOT_A_BRAND.match(g(r, 'brand')):
        # take the first words of the name instead, or fall back to the domain
        m = re.match(r'^([A-Z][A-Za-z0-9&\'\.\-]{1,18}(?:\s+[A-Z][A-Za-z0-9&\'\.\-]{1,14})?)',
                     g(r, 'name'))
        newb = m.group(1).strip() if m else (g(r, 'domain').split('.')[0].title()
                                             or 'Unknown')
        r['brand'] = newb
        n_notbrand += 1
print(f'\n  2. BRANDS THAT WERE NOT BRANDS')
print(f'     {n_notbrand} corrected')


# ------------------------------------------------------- 3. one spelling
def key(b):
    t = unicodedata.normalize('NFKD', str(b)).encode('ascii', 'ignore').decode()
    t = re.sub(r'^(the|by)\s+', '', t.strip().lower())
    return re.sub(r'[^a-z0-9]', '', t)


def nicer(a, b):
    """Which of two spellings a person would write."""
    def score(x):
        shouty = x.isupper() and len(x) > 3
        quiet = x.islower()
        has_case = any(c.isupper() for c in x) and any(c.islower() for c in x)
        return (not has_case, shouty, quiet, -len(x))
    return a if score(a) < score(b) else b


# THE SPELLING THE SOURCES USE MOST OFTEN WINS.
#
# Picking by how the word looks chose "La Roche Posay" over "La Roche-Posay",
# because the two are the same length and the tie was broken arbitrarily.
# Counting is better: the spelling that appears most in the data is the one
# the shops and the manufacturer actually use. The look test only breaks ties.
counts = collections.Counter()
for r in D:
    if g(r, 'brand'):
        counts[(key(g(r, 'brand')), g(r, 'brand'))] += 1
best = {}
for (k, b), n in sorted(counts.items(), key=lambda x: -x[1]):
    if k not in best:
        best[k] = b
    elif counts[(k, best[k])] == n:
        best[k] = nicer(best[k], b)

groups = collections.defaultdict(set)
for r in D:
    groups[key(g(r, 'brand'))].add(g(r, 'brand'))
multi = {k: v for k, v in groups.items() if len(v) > 1}

n_spell = 0
for r in D:
    k = key(g(r, 'brand'))
    if k in best and best[k] != g(r, 'brand'):
        r['brand'] = best[k]
        n_spell += 1
print(f'\n  3. ONE SPELLING PER BRAND')
print(f'     {len(multi)} brands were written more than one way')
print(f'     {n_spell:,} rows corrected')
shown = 0
for k, v in multi.items():
    if len(v) >= 3 and shown < 4:
        print(f'        {sorted(v)}  ->  {best[k]}')
        shown += 1
before_brands = len(groups)
print(f'     brand count {len(set(groups)) + sum(len(v) - 1 for v in multi.values()):,}'
      f' -> {len({g(r, "brand") for r in D}):,}')

# ------------------------------------------------------------ 4. the price
n_price = 0
for r in D:
    for c in ('price_usd', 'price_usd_min', 'price_usd_max', 'price_usd_market'):
        v = g(r, c)
        if v:
            try:
                if float(v) > 1000:
                    print(f'\n  4. A PRICE NOBODY WOULD DEFEND')
                    print(f'     {g(r, "product_id")}  {g(r, "brand")} '
                          f'{g(r, "name")[:40]}')
                    print(f'     ${float(v):,.2f} for a body product. The shop&#39;s '
                          f'own page is wrong, so the value is removed.')
                    r[c] = ''
                    n_price += 1
            except ValueError:
                r[c] = ''
if not n_price:
    print(f'\n  4. no price above $1,000 left')

print(f'\n  RESULT')
print(f'     {len(D):,} products')
print(f'     {len({g(r, "brand") for r in D}):,} brands, one spelling each')

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
print(f'\n  written. now run:  py build_final_dataset.py')
