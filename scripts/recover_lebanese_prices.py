"""
The lebanese prices that were scraped and then dropped

What went wrong
  The Lebanese brand shops were scraped properly. 35,364 of the 38,835
  harvested rows carry a price, and on the 27 sites that were kept there are
  2,588 of them.

  Only 278 reached LEBANESE_ORIGIN.csv.

Usage:
    py recover_lebanese_prices.py --dry     show what would change, write nothing
    py recover_lebanese_prices.py           do it
"""
import os
import re
import csv
import sys
import statistics
import collections

csv.field_size_limit(10 ** 8)

HARVEST = 'lebanese_origin_harvested.csv'
ORIGIN = 'LEBANESE_ORIGIN.csv'
COMBINED = 'COMBINED_DATASET.csv'
LBP_PER_USD = 89500.0
DRY = '--dry' in sys.argv


def load(path):
    with open(path, newline='', encoding='utf-8') as fh:
        rd = csv.DictReader(fh)
        return list(rd.fieldnames or []), [
            {k: (v or '') for k, v in r.items()} for r in rd]


def to_usd(raw):
    """A harvested price as dollars, or None.

    Some are written "23.00," with a trailing comma, so the number is pulled
    out rather than the whole string being converted. Anything over 10,000 is
    lira: no skincare product costs ten thousand dollars, and Lebanese shops
    that price in lira produce figures like 1,540,000.
    """
    m = re.findall(r'\d[\d,]*\.?\d*', str(raw).replace(',', ''))
    if not m:
        return None
    try:
        v = float(m[0])
    except ValueError:
        return None
    if v >= 10000:
        v = v / LBP_PER_USD
    return round(v, 2) if 0 < v < 10000 else None


# ------------------------------------------------------------------ harvest
_, harvest = load(HARVEST)
by_url = {}
for r in harvest:
    u = r.get('product_url', '').strip()
    p = to_usd(r.get('price', ''))
    if u and p:
        by_url.setdefault(u, p)
print('=' * 70)
print('  RECOVERING THE LEBANESE PRICES')
print('=' * 70)
print(f'  harvested rows                     {len(harvest):,}')
print(f'  distinct pages with a usable price {len(by_url):,}')

# ------------------------------------------------------------------ origin
of, origin = load(ORIGIN)
had = sum(1 for r in origin if r['price_usd'].strip())

# THE PRICES THAT WERE ALREADY THERE ARE ALSO CHECKED.
#
# The 278 that survived came from the original workbook and some of them are
# in lira, not dollars, in a column called price_usd. The dearest was written
# as 1,950,000, which is $21.79. The merge script converts these on its way
# through, so the combined file was right, but the source file was not, and
# anybody opening LEBANESE_ORIGIN.csv saw a two million dollar face cream.
fixed_old = 0
for r in origin:
    cur = r['price_usd'].strip()
    if not cur:
        continue
    v = to_usd(cur)
    if v is None:
        r['price_usd'] = ''
        fixed_old += 1
    elif f'{v:.2f}' != cur:
        r['price_usd'] = f'{v:.2f}'
        fixed_old += 1

filled = 0
lira = 0
for r in origin:
    if r['price_usd'].strip():
        continue
    u = r.get('product_url', '').strip()
    if u in by_url:
        r['price_usd'] = f'{by_url[u]:.2f}'
        filled += 1
        raw = next((h['price'] for h in harvest
                    if h.get('product_url', '').strip() == u), '')
        if re.findall(r'\d[\d,]*', str(raw).replace(',', '')) and \
                float(re.findall(r'\d[\d,]*\.?\d*',
                                 str(raw).replace(',', ''))[0]) >= 10000:
            lira += 1
now = sum(1 for r in origin if r['price_usd'].strip())

print()
print(f'  {ORIGIN}')
print(f'    products                         {len(origin):,}')
print(f'    had a price                      {had:,}  ({100*had/len(origin):.1f}%)')
print(f'    recovered                        {filled:,}')
print(f'    now                              {now:,}  ({100*now/len(origin):.1f}%)')
if lira:
    print(f'    of those, priced in lira         {lira:,}  (divided by 89,500)')
if fixed_old:
    print(f'    existing prices corrected        {fixed_old:,}  (lira, or unusable)')

vals = [float(r['price_usd']) for r in origin if r['price_usd'].strip()]
if vals:
    print(f'    cheapest ${min(vals):,.2f}   median ${statistics.median(vals):,.2f}'
          f'   dearest ${max(vals):,.2f}')

# ANYTHING OVER $200 IS SHOWN, NOT SILENTLY ACCEPTED.
#
# Six of the recovered prices are above $200. Most are treatment programmes
# and bundles, which really do cost that. One is a shower gel listed at
# $1,500, which is a mistake on the shop's own page rather than a mistake in
# the reading of it. They are printed so the judgement is yours, and the
# product_url is in the file so each can be checked.
high = sorted(((float(r['price_usd']), r['brand'], r['name'], r['domain'])
               for r in origin if r['price_usd'].strip()
               and float(r['price_usd']) > 200), reverse=True)
if high:
    print()
    print(f'  PRICES OVER $200, worth an eye ({len(high)})')
    for v, b, n, d in high[:8]:
        print(f'    ${v:9,.2f}  {str(b)[:20]:22s}{str(n)[:40]:42s}{d}')

by_brand = collections.defaultdict(lambda: [0, 0])
for r in origin:
    by_brand[r['brand']][0] += 1
    if r['price_usd'].strip():
        by_brand[r['brand']][1] += 1
print()
print('  PRICE COVERAGE BY BRAND, AFTER RECOVERY')
for b, (n, p) in sorted(by_brand.items(), key=lambda x: -x[1][0])[:14]:
    print(f'    {b[:26]:28s}{n:5,}{p:7,}   {100*p/n:5.0f}%')

# ------------------------------------------------- the other dropped column
# price_usd was not the only casualty of the naming mismatch. The harvester
# writes the shop's own blurb as "description"; the schema calls it
# "product_summary". 556 of them were sitting in the harvest unused.
by_url_desc = {}
for r in harvest:
    u = r.get('product_url', '').strip()
    d = re.sub(r'\s+', ' ', str(r.get('description', ''))).strip()
    if u and len(d) > 20:
        by_url_desc.setdefault(u, d[:1500])

desc_filled = 0
for r in origin:
    if r.get('product_summary', '').strip():
        continue
    u = r.get('product_url', '').strip()
    if u in by_url_desc:
        r['product_summary'] = by_url_desc[u]
        desc_filled += 1
ds_now = sum(1 for r in origin if r.get('product_summary', '').strip())
print()
print(f'    product_summary recovered        {desc_filled:,}'
      f'   now {ds_now:,}  ({100*ds_now/len(origin):.1f}%)')

# ---------------------------------------------------------------- combined
cf, comb = load(COMBINED)
c_before = sum(1 for r in comb if r.get('price_usd', '').strip())
price_by_url = {r['product_url'].strip(): r['price_usd']
                for r in origin if r['price_usd'].strip()
                and r.get('product_url', '').strip()}
desc_by_url = {r['product_url'].strip(): r['product_summary']
               for r in origin if r.get('product_summary', '').strip()
               and r.get('product_url', '').strip()}
c_filled = 0
c_desc = 0
for r in comb:
    u = r.get('product_url', '').strip()
    if not r.get('price_usd', '').strip() and u in price_by_url:
        r['price_usd'] = price_by_url[u]
        r['price_usd_min'] = price_by_url[u]
        r['price_usd_max'] = price_by_url[u]
        c_filled += 1
    if not r.get('product_summary', '').strip() and u in desc_by_url:
        r['product_summary'] = desc_by_url[u]
        c_desc += 1
c_after = sum(1 for r in comb if r.get('price_usd', '').strip())
anyp = sum(1 for r in comb if r.get('price_usd', '').strip()
           or r.get('price_usd_market', '').strip())

print()
print(f'  {COMBINED}')
print(f'    shop price   {c_before:,} -> {c_after:,}   (+{c_filled:,})')
print(f'    any price    {anyp:,}  ({100*anyp/len(comb):.1f}%)')
ds = sum(1 for r in comb if r.get('product_summary', '').strip())
print(f'    summary      {ds - c_desc:,} -> {ds:,}   (+{c_desc:,})')

if DRY:
    print('\n  --dry, nothing was written.')
    sys.exit(0)


def save(path, fields, rows):
    tmp = path + '.tmp'
    with open(tmp, 'w', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(rows)
    # read back before replacing the real file. A crash mid-write once put
    # machine code inside COMBINED_DATASET.csv, and nothing noticed until a
    # later script tried to read it.
    with open(tmp, 'rb') as _f:
        _raw = _f.read()
    try:
        _raw.decode('utf-8')
    except UnicodeDecodeError as _e:
        os.remove(tmp)
        raise SystemExit(f'  the file came back damaged at byte {_e.start:,}, '
                         f'nothing was replaced. run it again.')
    os.replace(tmp, path)


save(ORIGIN, of, origin)
save(COMBINED, cf, comb)
print(f'\n  written. now run:  py make_workbook.py')
