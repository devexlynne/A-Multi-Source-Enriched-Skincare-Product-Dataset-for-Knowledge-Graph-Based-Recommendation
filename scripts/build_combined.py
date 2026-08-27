"""
One dataset. global + lebanese, every product with reviews.

The decision this implements
  Keep only products that have reviews.

  This is not a new idea and it is not a compromise. It is STEP 0 of the
  cleaning pipeline already applied to the global source, which took 19,059
  products down to 7,595 for exactly this reason. Applying the same rule to the
  Lebanese source is what makes the two comparable rather than merely stacked.

  The justification is that the thesis analyses reviews. A product with no
  review contributes nothing to that analysis, and carrying it forward only
  dilutes every coverage figure that gets quoted.

Usage:
    py build_lebanese.py
    py build_combined.py
"""
import json
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

MAIN = 'SKINCARE_DATASET.csv'
LEB = 'LEBANESE_RETAIL.csv'
OUT_C = 'COMBINED_DATASET.csv'
OUT_X = 'COMBINED_DATASET.xlsx'
STATS = 'combined_stats.json'

RETAIL = ['retailers', 'n_retailers', 'price_usd', 'retailer_urls',
          'retailer_skin_types', 'retailers_agree']

m = pd.read_csv(MAIN, dtype=str, low_memory=False).fillna('')
d = pd.read_csv(LEB, dtype=str, low_memory=False).fillna('')
S = {}

# ------------------------------------------------- step 0, the same rule twice
S['lebanese_all'] = len(d)
rev = d[d['review_source'] != ''].copy()
S['lebanese_reviewed'] = len(rev)
S['lebanese_dropped_no_reviews'] = len(d) - len(rev)
print(f'step 0  keep only products with reviews')
print(f'        global source   {len(m):,}  (already filtered at 19,059 -> 7,595)')
print(f'        Lebanese source {len(d):,} -> {len(rev):,} '
      f'({S["lebanese_dropped_no_reviews"]:,} removed)')

# ------------------------------------------------------------- the 845 overlap
inboth = rev['matched_to'].str.contains('SKINCARE', na=False)
overlap = rev[inboth]
newrows = rev[~inboth].copy()
S['overlap'] = len(overlap)
S['new_from_lebanon'] = len(newrows)
print(f'\nstep 1  {len(overlap):,} Lebanese products are already in the global set')
print(f'        they ENRICH those rows, they are not added again')
print(f'        {len(newrows):,} are genuinely new and get added')

for c in RETAIL + ['source']:
    if c not in m.columns:
        m[c] = ''
m['source'] = 'global (Skinsort)'

# write the Lebanese retail facts onto the matching global rows
import re
import unicodedata
BPRE = re.compile(r'^(the|eau thermale|laboratoires?|labo|by)\s+', re.I)
STOP = {'the', 'and', 'for', 'with', 'of', 'de', 'la', 'le', 'du', 'new', 'pack',
        'set', 'kit', 'skin', 'face', 'facial', 'ml', 'g', 'gr', 'oz', 'fl',
        'duo', 'in', 'to', 'plus', 'my', 'a', 'x'}
SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()


def bkey(s):
    t = asc(s).strip()
    for _ in range(3):
        t = BPRE.sub('', t).strip()
    return re.sub(r'[^a-z0-9]', '', t)


def key_of(brand, name):
    s = asc(name)
    for w in re.split(r'[^a-z0-9]+', asc(brand)):
        if len(w) > 2:
            s = s.replace(w, ' ')
    s = SIZE.sub(' ', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return bkey(brand) + '||' + ' '.join(sorted(w for w in s.split() if w not in STOP))


m['_k'] = [key_of(b, n) for b, n in zip(m['brand'], m['name'])]
ov = overlap.copy()
ov['_k'] = [key_of(b, n) for b, n in zip(ov['brand'], ov['name'])]
ov = ov.drop_duplicates('_k').set_index('_k')
n_enriched = 0
for i in m.index:
    k = m.at[i, '_k']
    if k in ov.index:
        for c in RETAIL:
            m.at[i, c] = ov.at[k, c]
        m.at[i, 'source'] = 'global + sold in Lebanon'
        n_enriched += 1
S['enriched_global_rows'] = n_enriched
print(f'        {n_enriched:,} global rows gained a Lebanese price and shop list')

newrows['source'] = 'Lebanese retail'
COLS = [c for c in m.columns if c != '_k']
for c in COLS:
    if c not in newrows.columns:
        newrows[c] = ''

combined = pd.concat([m[COLS], newrows[COLS]], ignore_index=True)
combined['product_id'] = ['P' + str(i + 1).zfill(5) for i in range(len(combined))]
N = len(combined)
S['total'] = N
print(f'\nstep 2  ONE DATASET  {N:,} products, every one with reviews')

# ------------------------------------------------------------------- coverage
S['coverage'] = {}
CORE = ['brand', 'name', 'product_type', 'country', 'skin_type', 'sensitivity',
        'ingredients', 'benefits', 'concerns', 'review_count', 'review_source']
print('\nFEATURE COVERAGE')
for c in CORE + ['rating', 'skin_type_source', 'skin_type_url', 'price_usd']:
    if c in combined.columns:
        n = int((combined[c] != '').sum())
        S['coverage'][c] = n
        flag = '' if n == N else ('  <- not 100%' if c in CORE else '')
        print(f'   {c:20s}{n:6,}  ({100*n/N:5.1f}%){flag}')

gaps = {c: N - S['coverage'].get(c, 0) for c in CORE if S['coverage'].get(c, 0) < N}
S['gaps'] = gaps
S['by_source'] = combined['source'].value_counts().to_dict()
S['tier'] = {t: int((pd.to_numeric(combined['skin_type_tier'], errors='coerce') == int(t)).sum())
             for t in '1234'}
S['review_source'] = combined['review_source'].value_counts().to_dict()
S['types'] = combined['product_type'].value_counts().head(22).to_dict()
S['brands'] = int(combined['brand'].map(bkey).nunique())
S['with_price'] = int((combined['price_usd'] != '').sum())

print('\nBY SOURCE')
for k, v in S['by_source'].items():
    print(f'   {k:28s}{v:6,}  ({100*v/N:5.1f}%)')

if gaps:
    print('\nWHAT IS NOT YET 100%')
    for c, g in gaps.items():
        print(f'   {c:20s}{g:5,} missing')
    print('   run  py fill_combined_gaps.py  to close these')
else:
    print('\nEVERY CORE FEATURE IS AT 100%')

combined.to_csv(OUT_C, index=False)

W = {'product_id': 10, 'brand': 22, 'name': 46, 'product_type': 18, 'country': 16,
     'source': 24, 'skin_type': 13, 'sensitivity': 12, 'retailers': 28,
     'price_usd': 10, 'ingredients': 55, 'skin_type_quote': 44, 'skin_type_url': 36,
     'review_texts_json': 40, 'retailer_urls': 34, 'retailer_skin_types': 32}
with pd.ExcelWriter(OUT_X, engine='openpyxl') as w:
    combined.to_excel(w, sheet_name='COMBINED', index=False)
    ws = w.sheets['COMBINED']
    for c in ws[1]:
        v = str(c.value)
        col = ('6f9c78' if v in RETAIL + ['source'] else
               'b06a97' if v.startswith('skin_type') or v == 'sensitivity' else '584A7A')
        c.fill = PatternFill('solid', fgColor=col)
        c.font = Font(bold=True, color='FFFFFF', size=10)
        c.alignment = Alignment(vertical='center', horizontal='left')
        ws.column_dimensions[get_column_letter(c.column)].width = W.get(v, 16)
    ws.row_dimensions[1].height = 22
    ws.freeze_panes = 'D2'
    ws.auto_filter.ref = ws.dimensions

json.dump(S, open(STATS, 'w'), indent=1)
print(f'\nwritten  {OUT_X}   {OUT_C}')
print(f'\n  {N:,} products, {S["brands"]:,} brands, every row has reviews')
print(f'  {S["with_price"]:,} carry a Lebanese price')
