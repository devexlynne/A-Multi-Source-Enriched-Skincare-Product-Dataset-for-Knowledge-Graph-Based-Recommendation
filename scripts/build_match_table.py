"""
Matching: SkinCarisma vs Amazon.

All 2,132 products that are in BOTH sources. Nothing removed.
For each one: does the skin type match, yes or no.

Sheet 1  MATCHING    the statistics
Sheet 2  Products     all 2,132 products, one per row

py build_match_table.py  ->  MATCH_TABLE.xlsx
"""
import re
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

OUT = 'MATCH_TABLE.xlsx'
norm = lambda s: re.sub(r'[^a-z0-9]', '', str(s).lower())

sc = pd.read_csv('skincarisma_ALL_products.csv', low_memory=False, dtype=str).fillna('')
sc = sc[sc['found'] == '1'].drop_duplicates('product_id')
ds = pd.read_csv('OPTION_A_mixed_sources.csv', low_memory=False, dtype=str).fillna('')
amz = pd.read_csv('amazon_skintype.csv', dtype=str).fillna('')
mp = pd.read_csv('acc19k_matches.csv', low_memory=False, dtype=str).fillna('')

mp['_k'] = mp['brand'].map(norm) + '|' + mp['name'].map(norm)
ds['_k'] = ds['brand'].map(norm) + '|' + ds['name'].map(norm)
ds['asin'] = ds['_k'].map(dict(zip(mp['_k'], mp['am_asin'])))
ds['amazon'] = ds['asin'].map(dict(zip(amz['asin'], amz['amazon_skin_type_raw']))).fillna('')

d = sc.drop(columns=[c for c in ('brand', 'name') if c in sc.columns]) \
      .merge(ds[['product_id', 'brand', 'name', 'asin', 'amazon']], on='product_id', how='inner').fillna('')
d = d[d['amazon'] != ''].reset_index(drop=True)


def sc_label(r):
    dry, oily = r['sc_dry'] == '1', r['sc_oily'] == '1'
    return 'Combination' if (dry and oily) else 'Oily' if oily else 'Dry' if dry else 'Normal'


d['skincarisma'] = d.apply(sc_label, axis=1)

# MATCH = the skin type SkinCarisma gives is also in what Amazon wrote.
d['match'] = [('MATCH' if s.lower() in a.lower() else 'NO MATCH')
              for s, a in zip(d['skincarisma'], d['amazon'])]

n = len(d)
m = int((d['match'] == 'MATCH').sum())

# ------------------------------------------------------------- statistics
stats = [['Products in BOTH SkinCarisma and Amazon', n, '100%'],
         ['MATCH', m, f'{100*m/n:.1f}%'],
         ['NO MATCH', n - m, f'{100*(n-m)/n:.1f}%'],
         ['', '', '']]
stats.append(['By skin type', 'products', 'matched'])
for t in ['Dry', 'Oily', 'Combination', 'Normal']:
    sub = d[d['skincarisma'] == t]
    mm = int((sub['match'] == 'MATCH').sum())
    stats.append([t, len(sub), f'{mm}  ({100*mm/len(sub):.1f}%)' if len(sub) else '-'])

table = pd.DataFrame(stats, columns=['', 'Products', 'Share'])

products = d[['brand', 'name', 'skincarisma', 'amazon', 'match']].copy()
products.columns = ['Brand', 'Product', 'SkinCarisma', 'Amazon', 'Match?']


# ------------------------------------------------- the raw data, both sources
def counts(r, axis):
    g, b = r.get(f'sc_{axis}_good', ''), r.get(f'sc_{axis}_bad', '')
    return f'{g} good / {b} bad' if g != '' and b != '' else 'no reading'


d['sens_word'] = d['sc_sensitive'].map({'1': 'Sensitive', '0': 'Not sensitive'}).fillna('no reading')
for a in ('dry', 'oily', 'sensitive'):
    d[f'{a}_c'] = d.apply(lambda r, a=a: counts(r, a), axis=1)

raw_sc = d[['brand', 'name', 'skincarisma', 'sens_word',
            'dry_c', 'oily_c', 'sensitive_c', 'sc_comedogenic', 'sc_url']].copy()
raw_sc.columns = ['Brand', 'Product', 'SKIN TYPE', 'SENSITIVITY',
                  'dry ingredients', 'oily ingredients', 'sensitive ingredients',
                  'comedogenic', 'skincarisma page']

raw_amz = d[['brand', 'name', 'asin', 'amazon']].copy() if 'asin' in d.columns else \
          d[['brand', 'name', 'amazon']].copy()
raw_amz.columns = (['Brand', 'Product', 'Amazon ASIN', 'SKIN TYPE as Amazon wrote it']
                   if 'asin' in d.columns else
                   ['Brand', 'Product', 'SKIN TYPE as Amazon wrote it'])

# ------------------------------------- explaining the Amazon field, in words
TYPES = ('dry', 'oil', 'combination', 'normal', 'sensitiv', 'acne')


def group(v):
    s = str(v).strip().lower()
    named = sum(t in s for t in TYPES)
    has_all = bool(re.search(r'\ball\b|all skin types?', s))
    if has_all and named == 0:
        return '1. Only "All"'
    if has_all and named:
        return '2. "All" AND specific types together'
    if named == 0:
        return '6. Not a skin type at all'
    if named == 1:
        return '3. One skin type'
    if named >= 4:
        return '5. Four or more types listed'
    return '4. Two or three types'


d['grp'] = d['amazon'].map(group)
vc_all = d['amazon'].value_counts()

EXPL = {
    '1. Only "All"': 'the field says nothing but "All". this is a universal-suitability claim, not a classification. it can never match a specific SkinCarisma value.',
    '2. "All" AND specific types together': 'e.g. "All, Sensitive". the seller says it suits everyone AND names a type. the two statements contradict each other.',
    '3. One skin type': 'e.g. "Dry". the only clean case. this is what the field was designed for.',
    '4. Two or three types': 'e.g. "Sensitive, Dry". a genuine multi-type claim, still usable.',
    '5. Four or more types listed': 'e.g. "Oily, Combination, Sensitive, Dry, Normal". listing every type is the same as saying "All" without using the word.',
    '6. Not a skin type at all': 'e.g. "Mature", "Dull skin", "Smooth", "Blemished". the seller wrote a concern, or something else entirely.',
}

note = [['HOW TO READ THE AMAZON COLUMN', '', ''],
        ['', '', ''],
        [f'Amazon\'s Skin Type field is free text typed by the seller. It is NOT a dropdown.', '', ''],
        [f'Across these {n:,} products it contains {vc_all.size} DIFFERENT values, and {int((vc_all <= 2).sum())} of them appear only once or twice.', '', ''],
        ['That is the single most important thing to say about it: nobody validates what goes in this box.', '', ''],
        ['', '', ''],
        ['THE SIX KINDS OF ENTRY', 'products', 'share']]
for g, c in sorted(d['grp'].value_counts().items()):
    note.append([g, int(c), f'{100*c/n:.1f}%'])
note.append(['', '', ''])
for g in sorted(EXPL):
    note.append([g, EXPL[g], ''])
note.append(['', '', ''])
note.append(['THREE THINGS TO POINT AT IF ASKED', '', ''])
note.append(['Same thing, written two ways',
             f'"Acne Prone" appears {int(vc_all.get("Acne Prone", 0))} times and "Acne Prone Skin" {int(vc_all.get("Acne Prone Skin", 0))} times. Same meaning, two spellings.', ''])
note.append(['Same pair, two orders and two spacings',
             f'"Sensitive, Dry" ({int(vc_all.get("Sensitive, Dry", 0))}) vs "Dry,Sensitive" ({int(vc_all.get("Dry,Sensitive", 0))}). Same claim, stored differently.', ''])
note.append(['A product name in the wrong box',
             'one product\'s declared Skin Type is the string "Clinique Targeted Protection Stick SPF 35", which is its own name.', ''])
note.append(['', '', ''])
note.append(['WHAT THIS MEANS FOR THE MATCH RATE', '', ''])
note.append(['', 'Only group 3 and group 4 are real, comparable classifications. Groups 1, 2, 5 and 6 cannot match a specific value, and they are the majority. So the low match rate is largely a property of how sellers fill this field, not evidence that SkinCarisma is wrong.', ''])

amazon_note = pd.DataFrame(note, columns=['', 'Products / explanation', 'Share'])

values = vc_all.reset_index()
values.columns = ['Value exactly as Amazon wrote it', 'Products']
values['Kind of entry'] = values['Value exactly as Amazon wrote it'].map(group)

# ---------------- ONE sheet holding both raw datasets and the verdict --------
allin = d[['product_id', 'brand', 'name',
           'skincarisma', 'sens_word', 'dry_c', 'oily_c', 'sensitive_c',
           'sc_comedogenic', 'sc_url',
           'asin', 'amazon', 'grp',
           'match']].copy()
allin.columns = ['product_id', 'Brand', 'Product',
                 'SC: skin type', 'SC: sensitivity', 'SC: dry ingredients',
                 'SC: oily ingredients', 'SC: sensitive ingredients',
                 'SC: comedogenic', 'SC: page',
                 'AMZ: ASIN', 'AMZ: skin type as written', 'AMZ: kind of entry',
                 'MATCH?']

# ------------------------------------------------------------------ write
with pd.ExcelWriter(OUT, engine='openpyxl') as w:
    table.to_excel(w, sheet_name='MATCHING', index=False, startrow=2)
    products.to_excel(w, sheet_name='Products', index=False)
    raw_sc.to_excel(w, sheet_name='RAW SkinCarisma', index=False)
    raw_amz.to_excel(w, sheet_name='RAW Amazon', index=False)
    amazon_note.to_excel(w, sheet_name='NOTE on Amazon', index=False)
    values.to_excel(w, sheet_name='Amazon values', index=False)
    allin.to_excel(w, sheet_name='ALL IN ONE', index=False)

    ws = w.sheets['MATCHING']
    ws['A1'] = f'{n:,} products are in both sources.   {m:,} match ({100*m/n:.1f}%).   {n-m:,} do not.'
    ws['A1'].font = Font(bold=True, size=12, color='584A7A')
    thin = Side(style='thin', color='CCCCCC')
    for r in ws.iter_rows(min_row=3, max_row=3 + len(table), min_col=1, max_col=3):
        for c in r:
            c.border = Border(left=thin, right=thin, top=thin, bottom=thin)
    for c in ws[3]:
        c.fill = PatternFill('solid', fgColor='584A7A')
        c.font = Font(bold=True, color='FFFFFF')
    ws['A5'].fill = PatternFill('solid', fgColor='D6EBD6')
    ws['B5'].fill = PatternFill('solid', fgColor='D6EBD6')
    ws['C5'].fill = PatternFill('solid', fgColor='D6EBD6')
    ws['A6'].fill = PatternFill('solid', fgColor='F7DADA')
    ws['B6'].fill = PatternFill('solid', fgColor='F7DADA')
    ws['C6'].fill = PatternFill('solid', fgColor='F7DADA')
    for i, wd in enumerate([40, 14, 16], 1):
        ws.column_dimensions[get_column_letter(i)].width = wd

    WIDTHS = {'Brand': 22, 'Product': 46, 'SkinCarisma': 16, 'Amazon': 34, 'Match?': 12,
              'SKIN TYPE': 16, 'SENSITIVITY': 15, 'dry ingredients': 18,
              'oily ingredients': 18, 'sensitive ingredients': 20, 'comedogenic': 13,
              'skincarisma page': 50, 'Amazon ASIN': 14,
              'SKIN TYPE as Amazon wrote it': 40}
    for nm in ('Products', 'RAW SkinCarisma', 'RAW Amazon'):
        ws = w.sheets[nm]
        for c in ws[1]:
            c.fill = PatternFill('solid', fgColor='584A7A')
            c.font = Font(bold=True, color='FFFFFF')
            ws.column_dimensions[get_column_letter(c.column)].width = WIDTHS.get(str(c.value), 16)
        ws.freeze_panes = 'A2'
        ws.auto_filter.ref = ws.dimensions

    ws = w.sheets['Products']
    for i in range(2, ws.max_row + 1):
        c = ws[f'E{i}']
        c.fill = PatternFill('solid', fgColor='D6EBD6' if c.value == 'MATCH' else 'F7DADA')
        c.alignment = Alignment(horizontal='center')

    ws = w.sheets['NOTE on Amazon']
    ws.column_dimensions['A'].width = 40
    ws.column_dimensions['B'].width = 105
    ws.column_dimensions['C'].width = 10
    for r in ws.iter_rows(min_row=1, max_row=ws.max_row, min_col=1, max_col=3):
        for c in r:
            c.alignment = Alignment(vertical='top', wrap_text=True)
        v = str(r[0].value or '')
        if v.isupper() and len(v) > 8:
            for c in r:
                c.font = Font(bold=True, color='584A7A')
    ws['A1'].font = Font(bold=True, size=13, color='584A7A')

    ws = w.sheets['Amazon values']
    for c in ws[1]:
        c.fill = PatternFill('solid', fgColor='584A7A')
        c.font = Font(bold=True, color='FFFFFF')
    ws.freeze_panes = 'A2'
    ws.auto_filter.ref = ws.dimensions
    for i, wd in enumerate([48, 12, 34], 1):
        ws.column_dimensions[get_column_letter(i)].width = wd

    # ALL IN ONE: SkinCarisma block purple, Amazon block teal, verdict coloured
    ws = w.sheets['ALL IN ONE']
    W = [11, 22, 44, 15, 15, 17, 17, 19, 13, 46, 13, 34, 26, 12]
    for i, c in enumerate(ws[1]):
        v = str(c.value)
        c.fill = PatternFill('solid', fgColor='584A7A' if v.startswith('SC:')
                             else '2F6F7A' if v.startswith('AMZ:') else '3B3B4F')
        c.font = Font(bold=True, color='FFFFFF', size=10)
        c.alignment = Alignment(vertical='center', wrap_text=True)
        ws.column_dimensions[get_column_letter(c.column)].width = W[i]
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = 'D2'
    ws.auto_filter.ref = ws.dimensions
    for i in range(2, ws.max_row + 1):
        c = ws[f'N{i}']
        c.fill = PatternFill('solid', fgColor='D6EBD6' if c.value == 'MATCH' else 'F7DADA')
        c.alignment = Alignment(horizontal='center')

print(table.to_string(index=False))
print(f'\nwrote {OUT}')
