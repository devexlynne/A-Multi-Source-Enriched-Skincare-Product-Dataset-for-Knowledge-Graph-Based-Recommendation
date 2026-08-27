"""
One workbook, every sheet

COMBINED_DATASET.xlsx becomes the single file to open in a meeting:

    0 SUMMARY            every headline figure, on one screen
    1 COMBINED           the 7,761 products, the dataset used for analysis
    2 GLOBAL only        the Skinsort source on its own, before the merge
    3 LEBANESE only      the Lebanese source on its own, before the merge
    4 STATISTICS         every distribution: category, country, tier, source,
                         skin type, sensitivity, reviews, price
    5 REMOVED no reviews the rows dropped for having a review label and no data

Why keep the sources separately
  Any figure quoted about one source alone has to be verifiable without
  unpicking the merge. If a supervisor asks "how many products did the Lebanese
  scrape actually contribute", the answer is a sheet, not a filter someone has
  to reconstruct.

Usage:
    py build_combined_workbook.py
"""
import os
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

OUT = 'COMBINED_DATASET.xlsx'
RETAIL = {'retailers', 'n_retailers', 'price_usd', 'retailer_urls',
          'retailer_skin_types', 'retailers_agree', 'source'}
WIDTH = {'product_id': 10, 'brand': 22, 'name': 46, 'product_type': 18,
         'country': 16, 'source': 24, 'skin_type': 13, 'sensitivity': 12,
         'skin_type_status': 20, 'skin_type_tier': 8, 'skin_type_authority': 20,
         'skin_type_source': 22, 'skin_type_rule': 30, 'skin_type_quote': 46,
         'skin_type_url': 38, 'ingredients': 55, 'key_ingredients': 30,
         'free_from': 22, 'benefits': 38, 'concerns': 30, 'retailers': 28,
         'retailer_urls': 34, 'retailer_skin_types': 32, 'price_usd': 10,
         'review_texts_json': 40, 'product_summary': 40, 'skinsort_url': 34,
         'figure': 46, 'value': 16, 'group': 30, 'count': 12, 'share': 12}

c = pd.read_csv('COMBINED_DATASET.csv', dtype=str, low_memory=False).fillna('')
g = pd.read_csv('SKINCARE_DATASET.csv', dtype=str, low_memory=False).fillna('')
L = pd.read_csv('LEBANESE_RETAIL.csv', dtype=str, low_memory=False).fillna('')
removed = (pd.read_csv('REMOVED_no_review_data.csv', dtype=str, low_memory=False).fillna('')
           if os.path.exists('REMOVED_no_review_data.csv') else pd.DataFrame())

N = len(c)
tier = pd.to_numeric(c['skin_type_tier'], errors='coerce')
got = c['skin_type'] != ''
NGOT = max(int(got.sum()), 1)
T = {t: int((tier[got] == t).sum()) for t in (1, 2, 3, 4)}
T12 = T[1] + T[2]
Lrev = int((L['review_source'] != '').sum())


def n(col, frame=None):
    fr = c if frame is None else frame
    return int((fr[col] != '').sum()) if col in fr.columns else 0


def pcs(x, of=None):
    return f'{100*x/(of or N):.1f}%'


# ------------------------------------------------------------------ summary
SUM = [
    ['THE DATASET', ''],
    ['products, every one with review data', f'{N:,}'],
    ['brands', f"{c['brand'].nunique():,}"],
    ['product categories', f"{c['product_type'].nunique():,}"],
    ['', ''],
    ['WHERE THE PRODUCTS CAME FROM', ''],
] + [[f'   {k}', f'{v:,}  ({pcs(v)})'] for k, v in c['source'].value_counts().items()] + [
    ['', ''],
    ['HOW EACH SOURCE WAS FILTERED', ''],
    ['   global source, raw', '19,059'],
    ['   global, after keeping only reviewed products', f'{len(g):,}'],
    ['   Lebanese, raw listings scraped', '14,823'],
    ['   Lebanese, after removing duplicate listings', '14,179'],
    ['   Lebanese, after removing non-skincare', f'{len(L):,}'],
    ['   Lebanese, after keeping only reviewed products', f'{Lrev:,}'],
    ['   rows dropped for a review label with no data', f'{len(removed):,}'],
    ['', ''],
    ['SKIN TYPE', ''],
    ['   products with a skin type', f"{n('skin_type'):,}  ({pcs(n('skin_type'))})"],
    ['   from the manufacturer (tier 1)', f'{T[1]:,}  ({pcs(T[1], NGOT)} of filled)'],
    ['   from a shop (tier 2)', f'{T[2]:,}  ({pcs(T[2], NGOT)} of filled)'],
    ['   DECLARED, tier 1 or 2, the figure to quote', f'{T12:,}  ({pcs(T12, NGOT)} of filled)'],
    ['   from an analysis site (tier 3)', f'{T[3]:,}'],
    ['   carrying the exact sentence', f"{n('skin_type_quote'):,}"],
    ['   carrying a clickable link', f"{n('skin_type_url'):,}"],
    ['   searched, no source states one', f"{N - n('skin_type'):,}"],
    ['', ''],
    ['REVIEWS', ''],
    ['   products with review data', f'{N:,}  (100.0%)'],
    ['   with a numeric rating', f"{n('rating'):,}  ({pcs(n('rating'))})"],
    ['   with stored review text', f"{int((c['review_texts_json'].str.len() > 10).sum()):,}"],
    ['', ''],
    ['LEBANESE RETAIL', ''],
    ['   products carrying a Lebanese price', f"{n('price_usd'):,}  ({pcs(n('price_usd'))})"],
    ['   shops scraped', '6'],
    ['   products sold in Lebanon AND in the global set', f"{int((c['source'] == 'global + sold in Lebanon').sum()):,}"],
    ['', ''],
    ['OTHER FEATURES', ''],
    ['   ingredients', f"{n('ingredients'):,}  ({pcs(n('ingredients'))})"],
    ['   benefits', f"{n('benefits'):,}  ({pcs(n('benefits'))})"],
    ['   concerns', f"{n('concerns'):,}  ({pcs(n('concerns'))})"],
    ['   country of origin', f"{n('country'):,}  ({pcs(n('country'))})"],
]
summary = pd.DataFrame(SUM, columns=['figure', 'value'])


# --------------------------------------------------------------- statistics
def block(title, series, of=None):
    rows = [[f'--- {title} ---', '', '']]
    tot = of or int(series.sum())
    for k, v in series.items():
        rows.append([str(k) if str(k).strip() else '(blank)', v,
                     f'{100*v/max(tot,1):.1f}%'])
    rows.append(['', '', ''])
    return rows


stats = []
stats += block('PRODUCTS BY SOURCE', c['source'].value_counts())
stats += block('PRODUCT CATEGORY', c['product_type'].value_counts())
stats += block('COUNTRY OF ORIGIN', c['country'].value_counts().head(20))
stats += block('SKIN TYPE', c.loc[got, 'skin_type'].value_counts(), NGOT)
stats += block('SENSITIVITY', c.loc[got, 'sensitivity'].value_counts(), NGOT)
stats += block('SKIN TYPE EVIDENCE TIER',
               pd.Series({'1 manufacturer': T[1], '2 shop': T[2],
                          '3 analysis site': T[3], '4 other': T[4]}), NGOT)
stats += block('SKIN TYPE STATUS', c['skin_type_status'].value_counts())
stats += block('WHICH WORDING RULE MATCHED',
               c.loc[got, 'skin_type_rule'].str.replace(r'\s*\(strength \d\)', '',
                                                        regex=True).value_counts().head(15), NGOT)
stats += block('TOP SOURCE WEBSITES',
               c.loc[got, 'skin_type_source'].str.lower().str.replace(
                   'www.', '', regex=False).value_counts().head(25), NGOT)
stats += block('REVIEW SOURCE', c['review_source'].value_counts())
stats += block('TOP 25 BRANDS', c['brand'].value_counts().head(25))
if 'retailers' in c.columns:
    lb = c[c['retailers'] != '']
    if len(lb):
        sh = {}
        for s in ('sohaticare', 'feel22', 'mazenonline', 'zeinacare', 'nexuscare', 'daouk'):
            sh[s] = int(lb['retailers'].str.contains(s, na=False).sum())
        stats += block('LEBANESE SHOPS STOCKING THESE PRODUCTS',
                       pd.Series(sh).sort_values(ascending=False), len(lb))
cov = {col: n(col) for col in
       ['brand', 'name', 'product_type', 'country', 'skin_type', 'sensitivity',
        'ingredients', 'key_ingredients', 'free_from', 'spf', 'benefits',
        'concerns', 'rating', 'review_count', 'review_source', 'price_usd',
        'skin_type_source', 'skin_type_quote', 'skin_type_url']
       if col in c.columns}
stats += block('FEATURE COVERAGE (share of all products)', pd.Series(cov), N)
statdf = pd.DataFrame(stats, columns=['group', 'count', 'share'])


# ------------------------------------------------------------------- write
def style(ws, hi=(), head='584A7A'):
    for cell in ws[1]:
        v = str(cell.value)
        col = ('6f9c78' if v in hi else
               'b06a97' if v.startswith('skin_type') or v == 'sensitivity' else head)
        cell.fill = PatternFill('solid', fgColor=col)
        cell.font = Font(bold=True, color='FFFFFF', size=10)
        cell.alignment = Alignment(vertical='center', horizontal='left')
        ws.column_dimensions[get_column_letter(cell.column)].width = WIDTH.get(v, 16)
    ws.row_dimensions[1].height = 22
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions


try:
    open(OUT, 'a').close()
except PermissionError:
    import datetime
    OUT = OUT.replace('.xlsx', datetime.datetime.now().strftime('_%H%M%S.xlsx'))
    print(f'workbook open in Excel, writing {OUT} instead')

with pd.ExcelWriter(OUT, engine='openpyxl') as w:
    summary.to_excel(w, sheet_name='0 SUMMARY', index=False)
    style(w.sheets['0 SUMMARY'])

    c.to_excel(w, sheet_name='1 COMBINED', index=False)
    style(w.sheets['1 COMBINED'], RETAIL)
    w.sheets['1 COMBINED'].freeze_panes = 'D2'

    g.to_excel(w, sheet_name='2 GLOBAL skinsort only', index=False)
    style(w.sheets['2 GLOBAL skinsort only'])
    w.sheets['2 GLOBAL skinsort only'].freeze_panes = 'D2'

    L.to_excel(w, sheet_name='3 LEBANESE retail only', index=False)
    style(w.sheets['3 LEBANESE retail only'], RETAIL)
    w.sheets['3 LEBANESE retail only'].freeze_panes = 'D2'

    statdf.to_excel(w, sheet_name='4 STATISTICS', index=False)
    style(w.sheets['4 STATISTICS'], head='6f9c78')

    if len(removed):
        removed.to_excel(w, sheet_name='5 REMOVED no review data', index=False)
        style(w.sheets['5 REMOVED no review data'], head='b5484d')

print('=' * 62)
print(f'  {OUT}')
print('=' * 62)
print(f'  0 SUMMARY                 {len(summary):,} figures')
print(f'  1 COMBINED                {len(c):,} products  x {c.shape[1]} columns')
print(f'  2 GLOBAL skinsort only    {len(g):,} products')
print(f'  3 LEBANESE retail only    {len(L):,} products  ({Lrev:,} with reviews)')
print(f'  4 STATISTICS              {len(statdf):,} rows, every distribution')
if len(removed):
    print(f'  5 REMOVED no review data  {len(removed):,} rows')
print()
print(f'  headline: {N:,} products, {c["brand"].nunique():,} brands, '
      f'{pcs(T12, NGOT)} of skin types declared by a maker or a shop')
