"""
The simple validation

Same products, both sources, one question: do they agree or not?

 Sheet 1  RESULT             the headline answer and the funnel
 Sheet 2  Full statistics    every breakdown
 Sheet 3  SkinCarisma raw    what i scraped from SkinCarisma, untouched
 Sheet 4  Amazon raw         what Amazon declared for those SAME products
 Sheet 5  Side by side       one row per product, the two answers next to
                             each other, and AGREE or DISAGREE

Usage:
    py build_simple_validation.py   ->  VALIDATION_simple.xlsx
"""
import re
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

OUT = 'VALIDATION_simple.xlsx'
norm = lambda s: re.sub(r'[^a-z0-9]', '', str(s).lower())

# ------------------------------------------------------------------ load
sc = pd.read_csv('skincarisma_ALL_products.csv', low_memory=False, dtype=str).fillna('')
sc = sc[sc['found'] == '1'].drop_duplicates('product_id')
ds = pd.read_csv('OPTION_A_mixed_sources.csv', low_memory=False, dtype=str).fillna('')
amz = pd.read_csv('amazon_skintype.csv', dtype=str).fillna('')
mp = pd.read_csv('acc19k_matches.csv', low_memory=False, dtype=str).fillna('')

mp['_k'] = mp['brand'].map(norm) + '|' + mp['name'].map(norm)
ds['_k'] = ds['brand'].map(norm) + '|' + ds['name'].map(norm)
ds['asin'] = ds['_k'].map(dict(zip(mp['_k'], mp['am_asin'])))
ds['amazon_skin_type'] = ds['asin'].map(dict(zip(amz['asin'], amz['amazon_skin_type_raw']))).fillna('')

ids = ds[['product_id', 'brand', 'name', 'asin', 'amazon_skin_type']]
d = sc.drop(columns=[c for c in ('brand', 'name') if c in sc.columns]) \
      .merge(ids, on='product_id', how='inner').fillna('')

# keep only products that BOTH sources say something about
d = d[d['amazon_skin_type'] != ''].reset_index(drop=True)
print(f'products where both sources speak: {len(d):,}')


# ------------------------------------------------- SkinCarisma one label
def sc_label(r):
    dry, oily = r['sc_dry'] == '1', r['sc_oily'] == '1'
    if dry and oily:
        return 'Combination'
    if oily:
        return 'Oily'
    if dry:
        return 'Dry'
    return 'Normal'


d['skincarisma_skin_type'] = d.apply(sc_label, axis=1)

# ------------------------------------------------------------ the rule
# Both sides are first turned into ONE of the same four words. Then the check is
# simply: is it the same word?
#
# Comparing the raw strings does not work. Amazon writing "Oily, Dry" IS
# Combination, so a plain text match would score that as a disagreement when the
# two sources actually said the same thing.
UNIVERSAL = re.compile(r'^\s*(all|all skin types?|universal|any)\s*$', re.I)


def amazon_label(raw):
    """the declared Amazon text, reduced to the same four words."""
    s = str(raw).lower()
    if UNIVERSAL.match(str(raw).strip()):
        return ''                                   # no answer given
    dry = 'dry' in s
    oily = 'oil' in s or 'acne' in s
    if 'combination' in s or (dry and oily):
        return 'Combination'
    if oily:
        return 'Oily'
    if dry:
        return 'Dry'
    if 'normal' in s:
        return 'Normal'
    return ''                                       # only said Sensitive, Mature, etc


def n_types(raw):
    s = str(raw).lower()
    return sum(t in s for t in ('dry', 'oil', 'combination', 'normal', 'sensitiv'))


d['amazon_label'] = d['amazon_skin_type'].map(amazon_label)

def compare(r):
    if UNIVERSAL.match(str(r['amazon_skin_type']).strip()):
        return 'set aside: Amazon said only "All"'
    if n_types(r['amazon_skin_type']) >= 4:
        return 'set aside: Amazon listed every type'
    if r['amazon_label'] == '':
        return 'set aside: Amazon named no skin type'
    return 'AGREE' if r['amazon_label'] == r['skincarisma_skin_type'] else 'DISAGREE'


d['RESULT'] = d.apply(compare, axis=1)

# ------------------------------------------------------------- sheets
# no 0/1 flags anywhere. words only, plus the ingredient counts written the way
# SkinCarisma shows them on the page.
def counts(r, axis):
    g, b = r.get(f'sc_{axis}_good', ''), r.get(f'sc_{axis}_bad', '')
    return f'{g} good / {b} bad' if g != '' and b != '' else 'no reading'


d['SENSITIVE'] = d['sc_sensitive'].map({'1': 'Sensitive', '0': 'Not sensitive'}).fillna('no reading')
for a in ('dry', 'oily', 'sensitive'):
    d[f'{a} ingredients'] = d.apply(lambda r, a=a: counts(r, a), axis=1)

sheet1 = d[['product_id', 'brand', 'name',
            'skincarisma_skin_type', 'SENSITIVE',
            'dry ingredients', 'oily ingredients', 'sensitive ingredients',
            'sc_url']].copy()
sheet1.columns = ['product_id', 'brand', 'name',
                  'SKIN TYPE', 'SENSITIVITY',
                  'dry ingredients', 'oily ingredients', 'sensitive ingredients',
                  'skincarisma page']

sheet2 = d[['product_id', 'brand', 'name', 'asin', 'amazon_skin_type']].copy()
sheet2.columns = ['product_id', 'brand', 'name', 'amazon ASIN',
                  'SKIN TYPE as Amazon wrote it']

# ONE column per source. the raw Amazon wording lives on sheet 3.
sheet3 = d[['product_id', 'brand', 'name',
            'skincarisma_skin_type', 'amazon_label', 'RESULT']].copy()
sheet3.columns = ['product_id', 'brand', 'name',
                  'SKINCARISMA says', 'AMAZON says', 'RESULT']

# ------------------------------------------------------------- result
n = len(d)
vc = d['RESULT'].value_counts()
agree = int(vc.get('AGREE', 0))
disagree = int(vc.get('DISAGREE', 0))
scored = agree + disagree
aside = n - scored

TOTAL = 7569
N_SC = 6627
n_all = int(vc.get('set aside: Amazon said only "All"', 0))
n_every = int(vc.get('set aside: Amazon listed every type', 0))
n_none = int(vc.get('set aside: Amazon named no skin type', 0))

res = pd.DataFrame([
    ['THE FUNNEL, from the whole dataset down to what can be compared', '', ''],
    ['Products in the dataset', TOTAL, '100.0%'],
    ['Products SkinCarisma returned a reading for', N_SC, f'{100*N_SC/TOTAL:.1f}%'],
    ['Of those, Amazon ALSO has something in its Skin Type field', n, f'{100*n/TOTAL:.1f}%'],
    ['   this is the 2,132 on sheets 2, 3 and 4', '', ''],
    ['', '', ''],
    ['Now remove the Amazon entries that are not a skin type:', '', ''],
    ['   minus  Amazon said only "All"', -n_all, ''],
    ['   =      products with a specific Amazon value', n - n_all, ''],
    ['          (this is the 1,454 quoted in the earlier cross-check)', '', ''],
    ['   minus  Amazon listed every type at once', -n_every, ''],
    ['   minus  Amazon named no skin type (only "Sensitive", "Mature", etc)', -n_none, ''],
    ['', '', ''],
    ['PRODUCTS ACTUALLY COMPARED', scored, f'{100*scored/TOTAL:.1f}% of the dataset'],
    ['   AGREE', agree, f'{100*agree/scored:.1f}%'],
    ['   DISAGREE', disagree, f'{100*disagree/scored:.1f}%'],
    ['', '', ''],
    ['THE ANSWER', f'the two sources agree on {100*agree/scored:.1f}% of the products compared', ''],
    ['', '', ''],
    ['WHAT "SET ASIDE" MEANS', 'Amazon has text in the field, but the text does not name one skin type, so there is nothing to compare it against. The product is shown in full on every sheet, it is just not scored.', ''],
    [f'   set aside in total', aside, f'{100*aside/n:.1f}% of the 2,132'],
    ['', '', ''],
    ['THE RULE', 'both sides are reduced to ONE of the same four words (Dry, Oily, Combination, Normal). they agree if it is the same word.', ''],
    ['   why not compare the raw text',
     'Amazon writing "Oily, Dry" IS Combination. a plain text match would score that as a disagreement when the two sources actually said the same thing.', ''],
    ['   why "All" is set aside',
     'it is not a skin type, it is a claim that the product suits everyone (Vendruscolo et al. 2025, Dermatological Reviews 6:e70045)', ''],
    ['   why "listed every type" is set aside',
     'a product declared Oily AND Combination AND Sensitive AND Dry AND Normal has not been classified either', ''],
    ['', '', ''],
    ['Sheet 3  SkinCarisma raw', 'what SkinCarisma gave for these products, in words, with the ingredient counts behind each call', ''],
    ['Sheet 4  Amazon raw', 'the SAME products in the SAME order, showing the skin type exactly as Amazon wrote it', ''],
    ['Sheet 5  Side by side', 'one column per source and the verdict. the Amazon column here is the raw wording on sheet 3 reduced to one word, using the rule above', ''],
], columns=['', 'Value', 'Share'])

# --------------------------------------------------------- full statistics
sub = d[d['RESULT'].isin(['AGREE', 'DISAGREE'])]
COLS = ['A', 'B', 'C', 'D', 'E']
rows = []


def head(t):
    rows.append([t, '', '', '', ''])


def blank():
    rows.append(['', '', '', '', ''])


head('1. WHAT EACH SOURCE SAYS, across all 2,132 products')
rows.append(['skin type', 'SkinCarisma', 'Amazon', '', ''])
scv = d['skincarisma_skin_type'].value_counts()
amv = d['amazon_label'].replace('', 'no skin type named').value_counts()
for k in sorted(set(scv.index) | set(amv.index)):
    rows.append([k, int(scv.get(k, 0)), int(amv.get(k, 0)), '', ''])
blank()

head('2. EVERY OUTCOME, all 2,132 products')
rows.append(['outcome', 'products', 'share', '', ''])
for k, v in d['RESULT'].value_counts().items():
    rows.append([k, int(v), f'{100*v/len(d):.1f}%', '', ''])
blank()

for title, col in (('3. AGREEMENT BY WHAT SKINCARISMA SAID', 'skincarisma_skin_type'),
                   ('4. AGREEMENT BY WHAT AMAZON SAID', 'amazon_label')):
    head(title)
    rows.append(['label', 'compared', 'AGREE', 'DISAGREE', 'agree %'])
    for k, grp in sub.groupby(col):
        a = int((grp['RESULT'] == 'AGREE').sum())
        b = int((grp['RESULT'] == 'DISAGREE').sum())
        rows.append([k, a + b, a, b, f'{100*a/(a+b):.1f}%'])
    blank()

head('5. WHO SAYS WHAT.  rows = SkinCarisma, columns = Amazon.  the diagonal is agreement.')
cm = pd.crosstab(sub['skincarisma_skin_type'], sub['amazon_label'])
rows.append(['SkinCarisma \\ Amazon'] + list(cm.columns) + [''] * (4 - len(cm.columns)))
for idx, r in cm.iterrows():
    rows.append([idx] + [int(x) for x in r] + [''] * (4 - len(cm.columns)))

stats = pd.DataFrame(rows, columns=COLS)

# -------------------------------------------------------------- write
try:
    open(OUT, 'a').close()
except PermissionError:
    import datetime
    OUT = OUT.replace('.xlsx', datetime.datetime.now().strftime('_%H%M%S.xlsx'))
    print(f'the workbook was open in Excel, writing {OUT} instead')

with pd.ExcelWriter(OUT, engine='openpyxl') as w:
    res.to_excel(w, sheet_name='1 RESULT', index=False)
    stats.to_excel(w, sheet_name='2 Full statistics', index=False, header=False)
    sheet1.to_excel(w, sheet_name='3 SkinCarisma raw', index=False)
    sheet2.to_excel(w, sheet_name='4 Amazon raw', index=False)
    sheet3.to_excel(w, sheet_name='5 Side by side', index=False)

    for nm in w.sheets:
        ws = w.sheets[nm]
        for c in ws[1]:
            c.fill = PatternFill('solid', fgColor='584A7A')
            c.font = Font(bold=True, color='FFFFFF', size=10)
            c.alignment = Alignment(vertical='center', wrap_text=True)
        ws.row_dimensions[1].height = 26
        ws.freeze_panes = 'A2'
        ws.auto_filter.ref = ws.dimensions
        for c in ws[1]:
            v = str(c.value)
            wdt = 44 if v == 'name' else 32 if 'AMAZON' in v or 'as Amazon wrote' in v \
                else 26 if 'SKINCARISMA' in v or v == 'RESULT' else 20 if v in ('brand', '') else 14
            ws.column_dimensions[get_column_letter(c.column)].width = wdt

    ws = w.sheets['5 Side by side']
    col = [c.column for c in ws[1] if c.value == 'RESULT'][0]
    L = get_column_letter(col)
    for i in range(2, ws.max_row + 1):
        v = str(ws[f'{L}{i}'].value or '')
        if v == 'AGREE':
            ws[f'{L}{i}'].fill = PatternFill('solid', fgColor='D6EBD6')
        elif v == 'DISAGREE':
            ws[f'{L}{i}'].fill = PatternFill('solid', fgColor='F7DADA')
        else:
            ws[f'{L}{i}'].fill = PatternFill('solid', fgColor='EFEFEF')

print('\n' + '=' * 60)
print(f'  compared   {scored:,} products')
print(f'  AGREE      {agree:,}   {100*agree/scored:.1f}%')
print(f'  DISAGREE   {disagree:,}   {100*disagree/scored:.1f}%')
print(f'  set aside  {aside:,}')
print('=' * 60)
print(f'wrote {OUT}')
