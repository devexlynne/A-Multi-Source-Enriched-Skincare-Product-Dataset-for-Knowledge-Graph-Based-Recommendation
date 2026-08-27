"""
The dataset, one file

Option A and Option B existed only because the skin type came from different
places. The skin type has been removed, so the two are now identical and the
choice is gone. There is one dataset again.

  SKINCARE_DATASET.xlsx / .csv     7,569 products, every one with reviews

The skin-type columns are present but EMPTY, waiting to be filled from the
manufacturer's own product page:

  skin_type          Dry / Normal / Oily / Combination
  sensitivity        Sensitive / Resistant
  skin_type_source   the brand domain the value came from
  skin_type_quote    the exact sentence on the page that says it
  skin_type_url      the page itself, so any value can be checked

The last two columns are new, and they are the point. Every future value will
carry its own evidence.

Usage:
    py build_dataset.py
"""
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

SRC = 'SKINCARE_DATASET.csv'   # was OPTION_A, which would have wiped the fill
CSV = 'SKINCARE_DATASET.csv'
XLS = 'SKINCARE_DATASET.xlsx'

KEEP = ['product_id', 'brand', 'name', 'product_type', 'country',
        'skin_type', 'sensitivity', 'skin_type_status',
        'skin_type_tier', 'skin_type_authority', 'skin_type_source',
        'skin_type_rule', 'skin_type_quote', 'skin_type_url',
        'ingredients', 'ingredient_count', 'key_ingredients', 'free_from', 'spf',
        'benefits', 'concerns',
        'rating', 'review_count', 'review_source', 'review_texts_json',
        'product_summary', 'skinsort_url']

WIDTH = {'product_id': 11, 'brand': 22, 'name': 44, 'product_type': 18, 'country': 15,
         'skin_type': 14, 'sensitivity': 13, 'skin_type_status': 20,
         'skin_type_tier': 8, 'skin_type_authority': 20, 'skin_type_source': 22,
         'skin_type_rule': 32, 'skin_type_quote': 46, 'skin_type_url': 40,
         'ingredients': 60, 'ingredient_count': 9, 'key_ingredients': 32,
         'free_from': 24, 'spf': 7, 'benefits': 42, 'concerns': 32,
         'rating': 8, 'review_count': 10, 'review_source': 13,
         'review_texts_json': 44, 'product_summary': 44, 'skinsort_url': 38}

df = pd.read_csv(SRC, low_memory=False, dtype=str).fillna('')

# the three evidence columns the new approach needs
for c in ('skin_type_quote', 'skin_type_url'):
    if c not in df.columns:
        df[c] = ''

df = df[[c for c in KEEP if c in df.columns]]
if 'review_texts_json' in df.columns:
    df['review_texts_json'] = df['review_texts_json'].str.slice(0, 2000)

df.to_csv(CSV, index=False)

try:
    open(XLS, 'a').close()
except PermissionError:
    import datetime
    XLS = XLS.replace('.xlsx', datetime.datetime.now().strftime('_%H%M%S.xlsx'))
    print(f'workbook open in Excel, writing {XLS}')

with pd.ExcelWriter(XLS, engine='openpyxl') as w:
    df.to_excel(w, sheet_name='Dataset', index=False)
    ws = w.sheets['Dataset']
    for c in ws[1]:
        v = str(c.value)
        # the empty skin-type block is highlighted so it is obviously a gap
        c.fill = PatternFill('solid', fgColor='B5484D' if v.startswith('skin_type') or v == 'sensitivity'
                             else '584A7A')
        c.font = Font(bold=True, color='FFFFFF', size=10)
        c.alignment = Alignment(vertical='center', horizontal='left')
        ws.column_dimensions[get_column_letter(c.column)].width = WIDTH.get(v, 16)
    ws.row_dimensions[1].height = 22
    ws.freeze_panes = 'D2'
    ws.auto_filter.ref = ws.dimensions

n = len(df)
print(f'{XLS}')
print(f'   {n:,} rows x {df.shape[1]} columns')
print()
for c in ('product_type', 'country', 'ingredients', 'benefits', 'concerns',
          'rating', 'review_count', 'spf', 'skin_type', 'sensitivity'):
    if c in df.columns:
        f = int((df[c] != '').sum())
        print(f'   {c:18s}{f:6,}  ({100*f/n:5.1f}%)')

# where the skin type came from, so the number is never quoted without its source
if 'skin_type_tier' in df.columns:
    got = df[df['skin_type'] != '']
    print('\n   skin type by tier')
    LAB = {'1': 'manufacturer', '2': 'retailer',
           '3': 'ingredient analysis', '4': 'derived (weakest)'}
    for t in ('1', '2', '3', '4'):
        c = int((got['skin_type_tier'] == t).sum())
        if c:
            print(f'      tier {t}  {LAB[t]:22s}{c:6,}  ({100*c/n:5.1f}%)')
    import pandas as _pd
    for t, lab in ((1, 'manufacturer only'), (2, 'declared sources only'),
                   (3, 'all but the weakest tier'), (4, 'everything')):
        c = int((_pd.to_numeric(df['skin_type_tier'], errors='coerce') <= t).sum())
        print(f'      filter tier <= {t}  {lab:26s}{c:6,}  ({100*c/n:5.1f}%)')
    # A row can have ONLY sensitivity ("recommended for sensitive skin") and
    # that is a complete answer, not a gap. Counting those as empty overstated
    # the gap by 1,066 products.
    has = (df['skin_type'] != '')
    print(f'   HAS SOMETHING                     {int(has.sum()):6,}  ({100*has.mean():5.1f}%)')
    print(f'   truly empty                       {int((~has).sum()):6,}  ({100*(~has).mean():5.1f}%)')
    if 'skin_type_status' in df.columns and (df['skin_type_status'] != '').any():
        print('\n   by status')
        for k, v in df['skin_type_status'].replace('', '(not set)').value_counts().items():
            print(f'      {k:24s}{v:6,}  ({100*v/n:5.1f}%)')
        appl = int((df['skin_type_status'] != 'not applicable').sum())
        f2 = int((df['skin_type_status'] == 'found').sum())
        print(f'\n   coverage of FACIAL products only  {f2:,} of {appl:,}  ({100*f2/appl:.1f}%)')
