"""
The fields a shop needs, computed from what is already here

Why these four
  The dataset was built to answer a research question. A recommender that a
  Lebanese retailer actually adopts has to answer a commercial one too, and
  four fields separate the two. None of them needs a new source. All four are
  already implied by data in the file.

      size_ml        how much product you get
      price_lbp      what it costs in the currency the customer pays in
      price_per_ml   whether it is good value
      price_tier     which shelf it sits on

  price_per_ml is the one that matters most and is missing most often from
  retail data. A 30 ml serum at $22 and a 100 ml serum at $30 look like the
  cheap one and the expensive one until the size is taken into account, at
  which point they are the expensive one and the cheap one. A recommender
  without it will systematically push customers toward small packages.

Usage:
    py add_commerce_fields.py --dry     show what it would do, change nothing
    py add_commerce_fields.py           write the columns in
"""
import os
import re
import csv
import sys
import statistics
import collections

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
DRY = '--dry' in sys.argv

# Banque du Liban card settlement rate, fixed since December 2023.
LBP_PER_USD = 89500.0

NEW = ['size_value', 'size_unit', 'size_ml', 'price_lbp', 'price_lbp_rate',
       'price_per_ml', 'price_tier']

# one number, one unit, as a shop writes it
SIZE = re.compile(
    r'(?<![\d.])(\d{1,4}(?:[.,]\d{1,2})?)\s*'
    r'(ml|mls|millilit(?:re|er)s?|cl|l|litres?|liters?|'
    r'g|gr|gm|gms|grams?|kg|mg|'
    r'fl\.?\s?oz|oz|ounces?)\b', re.I)

TO_ML = {
    'ml': 1.0, 'mls': 1.0, 'millilitre': 1.0, 'millilitres': 1.0,
    'milliliter': 1.0, 'milliliters': 1.0,
    'cl': 10.0, 'l': 1000.0, 'litre': 1000.0, 'litres': 1000.0,
    'liter': 1000.0, 'liters': 1000.0,
    # grams are treated as millilitres for creams and balms, whose density is
    # close enough to 1 that the comparison stays fair. This is an assumption
    # and it is recorded in size_unit so a reader can see where it applies.
    'g': 1.0, 'gr': 1.0, 'gm': 1.0, 'gms': 1.0, 'gram': 1.0, 'grams': 1.0,
    'kg': 1000.0, 'mg': 0.001,
    'oz': 29.5735, 'floz': 29.5735, 'fl oz': 29.5735,
    'ounce': 29.5735, 'ounces': 29.5735,
}


PLUS_PRODUCT = re.compile(
    r'\+\s*[^+]{0,40}?\b(cream|serum|gel|lotion|mask|cleanser|toner|balm|'
    r'oil|milk|foam|wash|scrub|shampoo|soap|spray|stick|fluid|essence|'
    r'moisturi[sz]er|sunscreen|spf)\b', re.I)

MULTI = re.compile(r'\b(duo|trio|twin|trip(?:le)?\s*pack|trousse|'
                   r'pack\s*of\s*\d+|set\s*of\s*\d+|\d+\s*pack|x\s?[2-9]\b|'
                   r'\d+\s*pcs?\b|buy\s*\d|\+\s*\d+\s*free)\b', re.I)


def norm_unit(u):
    return re.sub(r'[\s.]', '', u.lower())


def read_size(name):
    """
    The one size this product is sold in, or nothing.

    Nothing is returned when the name shows two or more different sizes,
    because that is a bundle: "Serum 30 ML + Cream 50 ML" is priced as a pair
    and neither number belongs to the price.
    """
    found = []
    for m in SIZE.finditer(str(name)):
        try:
            val = float(m.group(1).replace(',', '.'))
        except ValueError:
            continue
        unit = norm_unit(m.group(2))
        unit = {'mls': 'ml', 'gms': 'g', 'gms': 'g'}.get(unit, unit)
        mult = TO_ML.get(unit)
        if mult is None or val <= 0 or val > 10000:
            continue
        found.append((val, m.group(2).lower().strip(), val * mult))
    if not found:
        return None
    if len(found) > 1:
        # ANY second size means this is a multi-pack, even when the two are
        # identical. "Eau Thermale 300ml + 300ml duo" holds 600 ml, and an
        # earlier version of this accepted 300 because the two numbers agreed.
        # That made the product look twice as expensive per ml as it is,
        # which is the exact error price_per_ml exists to prevent.
        return None
    if PLUS_PRODUCT.search(str(name)):
        # "Serum 30 ML + Hyseac Mat Cream" is two products with one number.
        # Only a + followed by a PRODUCT TYPE counts, because
        # "Niacinamide 10% + Zinc 1%" is a single product and must survive.
        return None
    if MULTI.search(str(name)):
        # "pack of 3", "x2", "duo", "trio" multiply the contents without
        # printing a second number, so the one size on the label is not what
        # the price buys.
        return None
    return found[0]


with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


def as_price(s):
    s = str(s).strip().replace(',', '')
    if not re.fullmatch(r'\d+(\.\d+)?', s):
        return None
    v = float(s)
    return v if v > 0 else None


def price_of(r):
    """
    The same price the tidy file uses: the Lebanese shop price when there is
    one, otherwise the open market price.

    Reading price_usd alone found 6,679 prices, but the tidy file reports
    12,185, because build_final_dataset.py falls back to price_usd_market.
    Using the narrower column here would have produced lira prices and value
    ratings for barely half the products that have a price, and the two files
    would have disagreed with each other for no visible reason.
    """
    v = as_price(g(r, 'price_usd'))
    if v is not None:
        return v, 'a shop in Lebanon'
    v = as_price(g(r, 'price_usd_market'))
    if v is not None:
        return v, 'the open market'
    return None, ''


print('=' * 74)
print('  COMMERCE FIELDS, COMPUTED FROM WHAT IS ALREADY HERE')
print('=' * 74)
print(f'  {len(D):,} products')

# ------------------------------------------------------------------- size
def slug_text(r):
    """
    The product URL, turned back into words.

    Shops put the size in the address as well as the title:
    .../products/round-lab-1025-dokdo-eye-cream-30ml. 777 products whose name
    carries no size have one here, and it costs nothing to read.

    The URL is tried only AFTER the name, because the name is what the shop
    calls the product today while a URL can outlive a relabelling.
    """
    for c in ('retailer_urls', 'product_url', 'skinsort_url'):
        v = g(r, c)
        if v.startswith('http'):
            u = v.split(',')[0].split(' ')[0]
            tail = u.rstrip('/').split('/')[-1]
            return re.sub(r'[-_]+', ' ', tail)
    return ''


n_size = n_bundle = n_from_url = 0
units = collections.Counter()
examples = []
for r in D:
    got = read_size(g(r, 'name'))
    if got is None and not MULTI.search(g(r, 'name')):
        # the name had none, so try the address. The bundle guard still
        # applies: a URL saying "30ml-duo" is as much a multi-pack as a title
        # saying it, and reading 30 from it would misprice per millilitre.
        alt = slug_text(r)
        if alt:
            got = read_size(alt)
            if got is not None:
                n_from_url += 1
    if got is None:
        if len(list(SIZE.finditer(g(r, 'name')))) > 1:
            n_bundle += 1
        continue
    val, unit, ml = got
    r['_size_value'] = f'{val:g}'
    r['_size_unit'] = unit
    r['_size_ml'] = f'{ml:.2f}'
    units[unit] += 1
    n_size += 1
    if len(examples) < 5:
        examples.append((g(r, 'name')[:52], val, unit, ml))

print(f'\n  1. SIZE, read from the product name')
print(f'     found            {n_size:,} ({100*n_size/len(D):.1f}%)')
print(f'     of those, read from the product URL  {n_from_url:,}')
print(f'     refused, bundle  {n_bundle:,}  (two different sizes in one name)')
print(f'     units seen       {dict(units.most_common(6))}')
for nm, v, u, ml in examples:
    print(f'        "{nm}"  ->  {v:g} {u}  = {ml:.0f} ml')

# ---------------------------------------------------------------- currency
n_lbp = 0
for r in D:
    p, _src = price_of(r)
    if p is None:
        continue
    r['_price_lbp'] = f'{round(p * LBP_PER_USD):,}'.replace(',', '')
    r['_price_lbp_rate'] = f'{LBP_PER_USD:.0f}'
    n_lbp += 1
print(f'\n  2. PRICE IN LIRA at {LBP_PER_USD:,.0f} LBP per USD')
print(f'     converted        {n_lbp:,}')
print(f'     the rate is stored beside each value in price_lbp_rate, so a')
print(f'     converted price can be checked and re-based if the rate moves')

# ------------------------------------------------------------ price per ml
n_ppm = 0
ppm_vals = []
for r in D:
    p, _src = price_of(r)
    ml = r.get('_size_ml')
    if p is None or not ml:
        continue
    v = p / float(ml)
    if not (0 < v < 100):
        continue
    r['_price_per_ml'] = f'{v:.4f}'
    ppm_vals.append(v)
    n_ppm += 1
print(f'\n  3. PRICE PER ML')
print(f'     computed         {n_ppm:,}')
if ppm_vals:
    ppm_vals.sort()
    print(f'     cheapest ${ppm_vals[0]:.4f}/ml   median '
          f'${ppm_vals[len(ppm_vals)//2]:.4f}/ml   dearest '
          f'${ppm_vals[-1]:.2f}/ml')

# -------------------------------------------------------------- price tier
prices = sorted(p for p in (price_of(r)[0] for r in D) if p)
if prices:
    q1 = prices[len(prices) // 4]
    q3 = prices[3 * len(prices) // 4]
    n_tier = 0
    tiers = collections.Counter()
    for r in D:
        p, _src = price_of(r)
        if p is None:
            continue
        t = 'budget' if p <= q1 else ('premium' if p >= q3 else 'mid')
        r['_price_tier'] = t
        tiers[t] += 1
        n_tier += 1
    print(f'\n  4. PRICE TIER, cut on this dataset rather than round numbers')
    print(f'     budget   up to ${q1:.2f}      {tiers["budget"]:,}')
    print(f'     mid      ${q1:.2f} to ${q3:.2f}   {tiers["mid"]:,}')
    print(f'     premium  ${q3:.2f} and up    {tiers["premium"]:,}')

if DRY:
    print('\n  --dry, nothing written.')
    sys.exit(0)

# ------------------------------------------------------------------- write
for c in NEW:
    if c not in FIELDS:
        FIELDS.append(c)
for r in D:
    for c in NEW:
        r[c] = r.pop('_' + c, r.get(c, '')) or ''

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

print(f'\n  written. {len(NEW)} new columns in {DATA}')
print('  now rebuild the tidy file:')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
