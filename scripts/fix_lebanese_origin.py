"""
Taking the things out of lebanese origin that do not belong there

Lebanese origin is supposed to mean one thing: a product MADE by a Lebanese
company or a Lebanese person. AloeLab, Khan El Kaser, Senteurs d'Orient. You
spotted that it does not mean that at the moment, and you were right.

What was wrong, in order of how bad
  XIRAN, 271 products, the largest "Lebanese brand" in the whole set.
  xiranskincare.com is Guangzhou Xiran Cosmetics Co., Ltd, a 20,000 square
  metre factory in Baiyun District, Guangzhou, China. Their own About page
  says so. Every product is titled "Private Label" or "OEM" because they
  manufacture for other companies, which is also why not one of the 271 had a
  price: there is no retail price on a factory listing.

Usage:
    py fix_lebanese_origin.py --dry     say what would change
    py fix_lebanese_origin.py           do it
"""
import os
import re
import csv
import sys
import collections

csv.field_size_limit(10 ** 8)
DATA = 'COMBINED_DATASET.csv'
DRY = '--dry' in sys.argv

# ------------------------------------------------------ the judgements
# Each one carries the evidence, because these are decisions and a reader is
# entitled to disagree with them.
NOT_LEBANESE = {
    'xiranskincare.com': (
        'Guangzhou Xiran Cosmetics Co., Ltd, Baiyun District, Guangzhou, '
        'China. Their own About page. Products are titled "Private Label" '
        'and "OEM" because they manufacture for other companies'),
}
IS_A_SHOP = {
    'duft-lb.com': 'a Lebanese shop. 23 of its 37 products are La Roche-Posay '
                   'or A-Derma',
    'sbrandsofficial.com': 'a Lebanese shop selling COSRX, BYOMA, NACIFIC, '
                           'The Body Shop and Victoria&#39;s Secret',
    'bashrati.care': 'a Lebanese shop. Five different brand names sat on this '
                     'one domain',
}

# When a shop's row is moved, the real brand is usually the first words of the
# product name. "La Roche-Posay Effaclar Duo" belongs to La Roche-Posay.
KNOWN_BRANDS = [
    'La Roche-Posay', 'La Roche Posay', 'A-Derma', 'Avene', 'Avène',
    'Bioderma', 'Vichy', 'Eucerin', 'CeraVe', 'COSRX', 'BYOMA', 'NACIFIC',
    'The Body Shop', "Victoria's Secret", 'Victoria’s Secret', 'Uriage',
    'SVR', 'Ducray', 'Klorane', 'Mustela', 'Sebamed', 'Nuxe', 'Caudalie',
    'Filorga', 'Isispharma', 'ISIS Pharma', 'Neutrogena', 'Cetaphil',
    'Garnier', 'L’Oreal', "L'Oreal", 'Nivea', 'Dove', 'Olay', 'Beesline',
    'Cosmaline', 'Dali', 'Clipp', 'Diana', 'Yves Morel', 'Skin1004',
    'Some By Mi', 'Anua', 'Beauty of Joseon', 'Torriden', 'Round Lab',
]


def brand_from_name(name, fallback):
    n = re.sub(r'\s+', ' ', str(name)).strip()
    for b in KNOWN_BRANDS:
        if n.lower().startswith(b.lower()):
            return b
    # "COSRX - Full Fit Propolis" gives a brand. "Sunscreen SPF 50 - 50 ML"
    # does not, and the first version happily wrote "Sunscreen SPF 50" into
    # the brand column. Anything made of product words is refused.
    PRODUCT_WORD = re.compile(
        r'\b(sunscreen|spf|cream|serum|lotion|gel|foam|mask|cleanser|toner|'
        r'oil|balm|scrub|wash|soap|shampoo|butter|water|mist|essence|kit|set|'
        r'pack|bundle|ml|gr|kids|face|body|hair|hand|lip|eye|day|night|'
        r'moisturizer|moisturiser|sunblock|peeling|treatment)\b', re.I)
    m = re.match(r'^([A-Za-z0-9&\'’\.\- ]{2,26}?)\s*[-|–]\s+\S', n)
    if m:
        cand = m.group(1).strip()
        if (len(cand.split()) <= 4 and not PRODUCT_WORD.search(cand)
                and not cand.isdigit()):
            return cand
    return fallback


with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


print('=' * 76)
print('  FIXING WHAT COUNTS AS LEBANESE ORIGIN')
print('=' * 76)
before = collections.Counter(g(r, 'source_category') for r in D)
print(f'  starting with {len(D):,} products')
for k, v in before.most_common():
    print(f'     {k:24s}{v:7,}')

# ------------------------------------------------------ 1. not Lebanese
drop = [r for r in D if g(r, 'domain') in NOT_LEBANESE]
print(f'\n  1. NOT LEBANESE AT ALL, LEAVING THE DATASET')
for dom, why in NOT_LEBANESE.items():
    rows = [r for r in D if g(r, 'domain') == dom]
    if rows:
        print(f'     {dom}  {len(rows):,} products')
        print(f'        {why}')
        print(f'        with a price: {sum(1 for r in rows if g(r, "price_usd"))}')
        print(f'        example: {g(rows[0], "name")[:60]}')
D = [r for r in D if g(r, 'domain') not in NOT_LEBANESE]

# ------------------------------------------------------ 2. shops, not makers
moved = 0
rebranded = 0
print(f'\n  2. SHOPS, NOT MAKERS, MOVING TO LEBANESE RETAIL')
for dom, why in IS_A_SHOP.items():
    rows = [r for r in D if g(r, 'domain') == dom]
    if not rows:
        continue
    print(f'     {dom}  {len(rows):,} products')
    print(f'        {why}')
    shown = 0
    for r in rows:
        old_brand = g(r, 'brand')
        new_brand = brand_from_name(g(r, 'name'), old_brand)
        if new_brand != old_brand:
            if shown < 2:
                print(f'        "{g(r, "name")[:44]}"')
                print(f'           brand {old_brand} -> {new_brand}')
                shown += 1
            r['brand'] = new_brand
            rebranded += 1
        r['source_category'] = 'Lebanese retail'
        r['src_lb_origin'] = '0'
        r['src_lb_retail'] = '1'
        r['source_count'] = str(sum(1 for c in ('src_global', 'src_lb_retail',
                                                'src_lb_origin')
                                    if g(r, c) == '1'))
        # the shop is the retailer now, not the maker
        if not g(r, 'retailers'):
            r['retailers'] = dom.replace('.com', '').replace('.care', '')
            r['n_retailers'] = '1'
        moved += 1
print(f'     moved {moved:,} products, corrected {rebranded:,} brand names')

# ------------------------------------------------ 2b. one spelling per brand
# The same maker was written four ways: AloeLab, The Aloelab, Aloelab. To a
# computer that is three brands, so the brand count, the per-brand figures and
# any grouping by brand were all wrong.
def brand_key(b):
    t = re.sub(r'^(the)\s+', '', str(b).strip().lower())
    return re.sub(r'[^a-z0-9]', '', t)


best = {}
for r in D:
    if g(r, 'source_category') != 'Lebanese origin':
        continue
    k = brand_key(g(r, 'brand'))
    cur = best.get(k)
    b = g(r, 'brand')
    # prefer the spelling that is not all capitals and not all lower case
    def score(x):
        return (x.isupper() or x.islower(), -len(x))
    if cur is None or score(b) < score(cur):
        best[k] = b
n_spell = 0
for r in D:
    if g(r, 'source_category') != 'Lebanese origin':
        continue
    k = brand_key(g(r, 'brand'))
    if k in best and best[k] != g(r, 'brand'):
        r['brand'] = best[k]
        n_spell += 1
print(f'\n  2b. ONE SPELLING PER BRAND')
print(f'     {n_spell:,} rows had a brand spelled a different way from its own '
      f'other rows')

# ------------------------------------------------ 3. ids agree with category
print(f'\n  3. PRODUCT IDS THAT DISAGREED WITH THEIR CATEGORY')
PREFIX = {'Global (Skinsort)': 'GLB', 'Lebanese retail': 'LBR',
          'Lebanese origin': 'LBO'}
mismatch = sum(1 for r in D
               if g(r, 'product_id')[:3] != PREFIX[g(r, 'source_category')])
print(f'     {mismatch:,} rows had a prefix that did not match')
counters = collections.Counter()
oldnew = {}
for r in sorted(D, key=lambda x: (PREFIX[g(x, 'source_category')],
                                  g(x, 'product_id'))):
    p = PREFIX[g(r, 'source_category')]
    counters[p] += 1
    new = f'{p}-{counters[p]:05d}'
    oldnew[g(r, 'product_id')] = new
    r['_newid'] = new
for r in D:
    r['product_id'] = r.pop('_newid')
print(f'     renumbered so every prefix agrees')
for p in ('GLB', 'LBR', 'LBO'):
    print(f'        {p}  {counters[p]:6,}')

after = collections.Counter(g(r, 'source_category') for r in D)
print(f'\n  RESULT')
print(f'     {len(D):,} products, {len(before) and ""}'
      f'{sum(before.values()) - len(D):,} removed')
for k in ('Global (Skinsort)', 'Lebanese retail', 'Lebanese origin'):
    arrow = f'{before[k]:,} -> {after[k]:,}'
    print(f'     {k:24s}{arrow}')

brands = sorted({g(r, 'brand') for r in D
                 if g(r, 'source_category') == 'Lebanese origin'})
print(f'\n  THE {len(brands)} BRANDS LEFT IN LEBANESE ORIGIN')
per = collections.Counter(g(r, 'brand') for r in D
                          if g(r, 'source_category') == 'Lebanese origin')
for b, n in per.most_common():
    dom = next((g(r, 'domain') for r in D if g(r, 'brand') == b
                and g(r, 'source_category') == 'Lebanese origin'), '')
    print(f'     {b[:26]:28s}{n:5,}   {dom}')

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
print(f'\n  written {DATA}')
print('  now run:  py derive_benefits.py   then   py build_final_dataset.py')
