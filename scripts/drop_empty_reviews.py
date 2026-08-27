"""
Remove the rows that claim reviews but have none

The problem
  595 rows carry a review_source of "amazon" or "sephora" but contain

      no rating
      no review count
      no review text

  They have a LABEL saying where reviews would come from, and nothing behind
  it. They picked that label up in an earlier merge without the data.

Usage:
    py drop_empty_reviews.py
"""
import pandas as pd

DATA = 'COMBINED_DATASET.csv'
OUT = 'REMOVED_no_review_data.csv'

df = pd.read_csv(DATA, dtype=str, low_memory=False).fillna('')
N = len(df)

cnt = pd.to_numeric(df['review_count'], errors='coerce').fillna(0)
has = (df['rating'] != '') | (cnt > 0) | (df['review_texts_json'].str.len() > 10)

gone = df[~has]
keep = df[has].reset_index(drop=True)
keep['product_id'] = ['P' + str(i + 1).zfill(5) for i in range(len(keep))]

gone.to_csv(OUT, index=False)
keep.to_csv(DATA, index=False)

try:
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    RET = {'retailers', 'n_retailers', 'price_usd', 'retailer_urls',
           'retailer_skin_types', 'retailers_agree', 'source'}
    with pd.ExcelWriter('COMBINED_DATASET.xlsx', engine='openpyxl') as w:
        keep.to_excel(w, sheet_name='COMBINED', index=False)
        ws = w.sheets['COMBINED']
        for c in ws[1]:
            v = str(c.value)
            col = ('6f9c78' if v in RET else
                   'b06a97' if v.startswith('skin_type') or v == 'sensitivity' else '584A7A')
            c.fill = PatternFill('solid', fgColor=col)
            c.font = Font(bold=True, color='FFFFFF', size=10)
            c.alignment = Alignment(vertical='center', horizontal='left')
            ws.column_dimensions[get_column_letter(c.column)].width = 16
        ws.freeze_panes = 'D2'
        ws.auto_filter.ref = ws.dimensions
except PermissionError:
    print('(workbook open in Excel, csv written, close Excel and re-run to refresh)')

M = len(keep)
print('=' * 62)
print('  ROWS WITH A REVIEW LABEL BUT NO REVIEW DATA')
print('=' * 62)
print(f'  before                {N:,}')
print(f'  removed               {len(gone):,}')
print(f'  AFTER                 {M:,}')
print()
print('  what was removed, by the label they carried:')
print(gone['review_source'].value_counts().to_string())
print()
print('  by source:')
print(gone['source'].value_counts().to_string())
print(f'\n  written to {OUT}, so this is reversible')
print()
print('  COVERAGE NOW')
CORE = ['brand', 'name', 'product_type', 'country', 'skin_type', 'sensitivity',
        'ingredients', 'benefits', 'concerns', 'review_count', 'review_source']
ok = True
for c in CORE:
    n = int((keep[c] != '').sum())
    if n != M:
        ok = False
    print(f'    {c:18s}{n:6,}  ({100*n/M:5.1f}%)   {"OK" if n == M else f"{M-n:,} missing"}')
print()
for c in ('rating', 'price_usd', 'skin_type_url'):
    n = int((keep[c] != '').sum())
    print(f'    {c:18s}{n:6,}  ({100*n/M:5.1f}%)')
print()
print('  EVERY CORE FEATURE AT 100%' if ok else '  remaining gaps are listed above')
print()
print('  by source')
print(keep['source'].value_counts().to_string())
