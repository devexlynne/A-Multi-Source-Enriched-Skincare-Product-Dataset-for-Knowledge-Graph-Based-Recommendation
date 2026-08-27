"""
All sources, one workbook

Every dataset behind the thesis, in one file, latest version of each, plus the
matching statistics and worked examples.

  0  MAP OF SOURCES        what each source is, how big, what it gave me
  1  Skinsort Global       the global catalogue
  2  Lebanese Retail       6 Lebanese shops
  3  Lebanese Origin       brands founded in Lebanon
  4  Amazon skin type      the manufacturer-declared field
  5  Amazon matches        product -> ASIN, with the match score
  6  SkinCarisma           the ingredient analysis
  7  DATASET A             final, mixed sources
  8  DATASET B             final, SkinCarisma only
  9  MATCHING stats        every matching step with its numbers
 10  EXAMPLES              a worked example of every match and every rule

Usage:
    py build_all_sources_workbook.py   ->  ALL_SOURCES.xlsx
"""
import os
import re
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

WB = '/sessions/dreamy-cool-maxwell/mnt/uploads/Thesis_Unified_Dataset_Workbook (1) (version 1).xlsx'
OUT = 'ALL_SOURCES.xlsx'
CAP = 20000          # rows per sheet, Excel stays openable

norm = lambda s: re.sub(r'[^a-z0-9]', '', str(s).lower())


def rd(path, sheet=None, **kw):
    if str(path).endswith('.xlsx'):
        return pd.read_excel(path, sheet_name=sheet, dtype=str, **kw).fillna('')
    return pd.read_csv(path, low_memory=False, dtype=str, **kw).fillna('')


# ----------------------------------------------------------------- the sources
print('reading sources...')
glob_ = rd(WB, '1 · Skinsort Global')
leb_r = rd(WB, '2 · Lebanese Retail')
leb_o = rd(WB, '3 · Lebanese Origin')
amz_t = rd('amazon_skintype.csv')
amz_m = rd('acc19k_matches.csv')
skinc = rd('skincarisma_ALL_products.csv')
dsA = rd('OPTION_A_mixed_sources.csv')
dsB = rd('OPTION_B_single_source.csv')

skinc_found = skinc[skinc['found'] == '1'].drop_duplicates('product_id')

# the columns worth showing per source, in reading order
KEEP = {
    'glob': ['brand', 'name', 'type', 'country', 'rating', 'review_count',
             'ingridients', 'afterUse', 'product_summary', 'skinsort_url'],
    'lebr': ['brand_name', 'product_name', 'category_unified', 'price_usd', 'skin_type',
             'skin_concern', 'source', 'source_country', 'rating', 'review_count',
             'leb_review_count', 'match_global_name', 'match_score', 'match_rule',
             'ingredients_raw', 'product_url'],
    'lebo': ['brand_name', 'product_name', 'product_category', 'brand_country', 'market',
             'availability_status', 'skin_type', 'skin_concerns', 'spf', 'price_usd',
             'ingredients', 'key_ingredients', 'benefits', 'product_url'],
    'dsA': ['product_id', 'brand', 'name', 'product_type', 'country', 'skin_type',
            'sensitivity', 'skin_type_source', 'rating', 'review_count', 'review_source',
            'ingredient_count', 'spf', 'skinsort_url'],
}
KEEP['dsB'] = KEEP['dsA']


def cut(df, key):
    cols = [c for c in KEEP[key] if c in df.columns]
    return df[cols] if cols else df


sheets = [
    ('1 Skinsort Global', cut(glob_, 'glob')),
    ('2 Lebanese Retail', cut(leb_r, 'lebr')),
    ('3 Lebanese Origin', cut(leb_o, 'lebo')),
    ('4 Amazon skin type', amz_t),
    ('5 Amazon matches', amz_m),
    ('6 SkinCarisma', skinc_found[['product_id', 'brand', 'name', 'sc_dry', 'sc_dry_good',
                                   'sc_dry_bad', 'sc_oily', 'sc_oily_good', 'sc_oily_bad',
                                   'sc_sensitive', 'sc_sensitive_good', 'sc_sensitive_bad',
                                   'sc_comedogenic', 'sc_url']]),
    ('7 DATASET A mixed', cut(dsA, 'dsA')),
    ('8 DATASET B skincarisma', cut(dsB, 'dsB')),
]

# ------------------------------------------------------------- 0 MAP OF SOURCES
nA = len(dsA)
amz_in_ds = 0
if 'brand' in dsA.columns:
    amz_m['_k'] = amz_m['brand'].map(norm) + '|' + amz_m['name'].map(norm)
    dsA['_k'] = dsA['brand'].map(norm) + '|' + dsA['name'].map(norm)
    dsA['asin'] = dsA['_k'].map(dict(zip(amz_m['_k'], amz_m['am_asin'])))
    dsA['amazon'] = dsA['asin'].map(dict(zip(amz_t['asin'], amz_t['amazon_skin_type_raw']))).fillna('')
    amz_in_ds = int((dsA['amazon'] != '').sum())

MAP = [
    ['SOURCE', 'WHAT IT IS', 'ROWS', 'WHAT IT GAVE THE THESIS', 'SHEET'],
    ['Skinsort Global', 'global product catalogue with ingredient lists',
     f'{len(glob_):,}', 'the base: brand, name, type, country, ingredients, ratings', '1'],
    ['Lebanese Retail', '6 Lebanese online shops (sohaticare, feel22, mazenonline, zeinacare, nexuscare, daouk)',
     f'{len(leb_r):,}', 'the Lebanese market: local availability, price in USD, local reviews', '2'],
    ['Lebanese Origin', 'brands founded in Lebanon (Beesline, Khan El Kaser, Ecladerm, AloeLab, Helwe...)',
     f'{len(leb_o):,}', '11 Lebanese brands, the local-origin subset', '3'],
    ['Amazon Reviews 2023', 'Hou et al., arXiv 2403.03952. product metadata + reviews',
     f'{len(amz_t):,}', 'reviews, and the manufacturer-declared Skin Type field', '4, 5'],
    ['SkinCarisma', 'ingredient analysis site, good vs bad ingredient counts per skin type',
     f'{len(skinc_found):,}', 'the skin type for 87.6% of the final dataset', '6'],
    ['EU CosIng', 'European Commission official INCI inventory (~28,700 names)',
     '28,710', 'ingredient name standardisation, 99.95% of tokens resolved', 'not a sheet'],
    ['', '', '', '', ''],
    ['FINAL DATASET A', 'skin type from the best source available per product',
     f'{nA:,}', 'skin type 74.4%, sensitivity 81.5%', '7'],
    ['FINAL DATASET B', 'skin type from SkinCarisma only, one rule for every product',
     f'{len(dsB):,}', 'skin type 87.6%, sensitivity 87.6%', '8'],
]
map_df = pd.DataFrame(MAP[1:], columns=MAP[0])

# ------------------------------------------------------------ 9 MATCHING stats
d = skinc_found.drop(columns=[c for c in ('brand', 'name') if c in skinc_found.columns]) \
    .merge(dsA[['product_id', 'brand', 'name', 'asin', 'amazon']], on='product_id', how='inner').fillna('')
both = d[d['amazon'] != ''].copy()


def sc_label(r):
    dry, oily = r['sc_dry'] == '1', r['sc_oily'] == '1'
    return 'Combination' if (dry and oily) else 'Oily' if oily else 'Dry' if dry else 'Normal'


both['skincarisma'] = both.apply(sc_label, axis=1)
both['match'] = [('MATCH' if s.lower() in a.lower() else 'NO MATCH')
                 for s, a in zip(both['skincarisma'], both['amazon'])]
nb, mb = len(both), int((both['match'] == 'MATCH').sum())

M = [
    ['MATCH 1 · Lebanese retail to the global base', '', ''],
    ['Raw retail rows from 6 sites', '21,109', ''],
    ['After removing non-skincare', '20,757', ''],
    ['After removing exact brand+name duplicates', '19,791', '966 removed'],
    ['After removing fuzzy ingredient duplicates (name >=90 AND Jaccard >=0.85)', '14,823', '4,968 removed'],
    ['Matched to the global base (token_set_ratio >=85 AND product-type gate)', '1,167', '7.9% match rate'],
    ['', '', ''],
    ['MATCH 2 · Products to Amazon, for the reviews', '', ''],
    ['Comparisons without blocking', '20 billion', 'infeasible'],
    ['Comparisons after blocking on brand', '128,734', 'Papadakis et al. 2020'],
    ['Matches found', '4,495', ''],
    ['Verified at token_set_ratio >=95', '4,494', '99.98%'],
    ['', '', ''],
    ['MATCH 3 · The Amazon skin-type field', '', ''],
    ['Products matched to an Amazon ASIN', f'{int(dsA["asin"].notna().sum()):,}', ''],
    ['ASINs where the seller filled in Skin Type', f'{amz_in_ds:,}', ''],
    ['', '', ''],
    ['MATCH 4 · SkinCarisma lookup', '', ''],
    ['Products looked up', f'{len(skinc):,}', ''],
    ['Found on SkinCarisma', f'{len(skinc_found):,}', f'{100*len(skinc_found)/len(skinc):.1f}%'],
    ['', '', ''],
    ['VALIDATION · SkinCarisma vs Amazon', '', ''],
    ['SkinCarisma reading', f'{len(skinc_found):,}', ''],
    ['Amazon skin type', f'{amz_in_ds:,}', ''],
    ['BOTH, the comparison set', f'{nb:,}', 'check: 6,627 + 2,351 - 2,132 = 6,846 = union'],
    ['MATCH', f'{mb:,}', f'{100*mb/nb:.1f}%'],
    ['NO MATCH', f'{nb-mb:,}', f'{100*(nb-mb)/nb:.1f}%'],
]
for t in ['Dry', 'Oily', 'Combination', 'Normal']:
    s = both[both['skincarisma'] == t]
    mm = int((s['match'] == 'MATCH').sum())
    M.append([f'   SkinCarisma said {t}', f'{len(s):,}', f'{mm} matched ({100*mm/len(s):.1f}%)' if len(s) else '-'])
match_df = pd.DataFrame(M, columns=['Matching step', 'Value', 'Note'])

# ------------------------------------------------------------------ 10 EXAMPLES
ex = both[['brand', 'name', 'skincarisma', 'amazon', 'match']].copy()
ex.columns = ['Brand', 'Product', 'SkinCarisma says', 'Amazon says', 'Result']
head = pd.DataFrame([
    ['HOW A MATCH IS DECIDED', '', '', '', ''],
    ['RULE', 'a product MATCHES if the skin type SkinCarisma gives also appears in what Amazon wrote', '', '', ''],
    ['', '', '', '', ''],
    ['SkinCarisma reads the FORMULA', 'dry 6 good / 2 bad -> 6 beats 2 -> suits dry. dry AND oily = Combination.', '', '', ''],
    ['Amazon reads the LABEL', 'details["Skin Type"], free text typed by the seller, not a dropdown', '', '', ''],
    ['', '', '', '', ''],
    ['WORKED EXAMPLES', '', '', '', ''],
], columns=ex.columns)
picks = pd.concat([
    ex[ex['Result'] == 'MATCH'].head(6),
    ex[(ex['Result'] == 'NO MATCH') & (ex['Amazon says'].str.strip().str.lower() == 'all')].head(3),
    ex[(ex['Result'] == 'NO MATCH') & (ex['Amazon says'].str.strip().str.lower() != 'all')].head(6),
])
tail = pd.DataFrame([
    ['', '', '', '', ''],
    ['ALL 2,132 COMPARED PRODUCTS FOLLOW', '', '', '', ''],
], columns=ex.columns)
examples = pd.concat([head, picks, tail, ex], ignore_index=True)

sheets = [('0 MAP OF SOURCES', map_df)] + sheets + \
         [('9 MATCHING stats', match_df), ('10 EXAMPLES', examples)]

# ------------------------------------------------------------------- write
try:
    open(OUT, 'a').close()
except PermissionError:
    import datetime
    OUT = OUT.replace('.xlsx', datetime.datetime.now().strftime('_%H%M%S.xlsx'))
    print(f'workbook open in Excel, writing {OUT}')

print('writing...')
with pd.ExcelWriter(OUT, engine='openpyxl') as w:
    for nm, df in sheets:
        df.head(CAP).to_excel(w, sheet_name=nm, index=False)
        ws = w.sheets[nm]
        for c in ws[1]:
            c.fill = PatternFill('solid', fgColor='584A7A')
            c.font = Font(bold=True, color='FFFFFF', size=10)
            c.alignment = Alignment(vertical='center', wrap_text=True)
            v = str(c.value)
            ws.column_dimensions[get_column_letter(c.column)].width = \
                46 if v in ('name', 'product_name', 'Product', 'WHAT IT GAVE THE THESIS',
                            'WHAT IT IS', 'Matching step') \
                else 34 if v in ('Amazon says', 'ingredients_raw', 'ingridients', 'ingredients',
                                 'product_url', 'skinsort_url', 'sc_url', 'Note') \
                else 22 if v in ('brand', 'brand_name', 'Brand', 'SOURCE') else 15
        ws.row_dimensions[1].height = 28
        ws.freeze_panes = 'A2'
        ws.auto_filter.ref = ws.dimensions
        print(f'  {nm:26s} {len(df):7,} rows')

    ws = w.sheets['10 EXAMPLES']
    for i in range(2, ws.max_row + 1):
        c = ws[f'E{i}']
        if c.value == 'MATCH':
            c.fill = PatternFill('solid', fgColor='D6EBD6')
        elif c.value == 'NO MATCH':
            c.fill = PatternFill('solid', fgColor='F7DADA')

print(f'\nwrote {OUT}  ({os.path.getsize(OUT)/1e6:.1f} MB)')
