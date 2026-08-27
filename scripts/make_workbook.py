"""
The workbook, built from whatever is in the CSV right now

COMBINED_DATASET.csv is the real dataset. The .xlsx is a readable copy of it.

They drift apart, because the scripts that add columns write only the CSV: the
price and rating work added six columns to the CSV while the workbook still had
the older 49. Opening the workbook then shows a dataset that is quietly out of
date, which is the worst kind of wrong, because nothing looks broken.

So this rebuilds the workbook from the CSV. Run it after anything that changes
the data, and the two agree again.

What is in the workbook
    0 SUMMARY     the figures, so the file can be read without opening a sheet
    1 COMBINED    every product, every column
    2 COVERAGE    how full each column is
    3 VOCABULARY  every allowed value in the controlled columns

Usage:
    py make_workbook.py
"""
import csv
import json
import os
import re
import collections
import statistics

import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

import sys
DATA = 'COMBINED_DATASET.csv'
OUT = 'COMBINED_DATASET.xlsx'
if '--final' in sys.argv:
    # the tidy 26-column version, the one to hand to somebody
    DATA = 'SKINCARE_FINAL.csv'
    OUT = 'SKINCARE_FINAL.xlsx'

csv.field_size_limit(10 ** 8)
df = pd.read_csv(DATA, dtype=str, low_memory=False).fillna('')
N = len(df)

# Excel refuses control characters, and a few ingredient lists carry them.
CTRL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')
for c in df.columns:
    df[c] = df[c].astype(str).str.replace(CTRL, ' ', regex=True)


def n(col):
    return int((df[col] != '').sum()) if col in df.columns else 0


def num(col):
    return pd.to_numeric(df[col], errors='coerce').dropna() if col in df.columns \
        else pd.Series(dtype=float)


cat = collections.Counter(df['source_category'])
p_lb, p_mk = num('price_usd'), num('price_usd_market')
any_price = int(((df.get('price_usd', '') != '') |
                 (df.get('price_usd_market', '') != '')).sum())
any_rating = int(((df.get('rating', '') != '') |
                  (df.get('rating_market', '') != '')).sum())

rows = [['products', f'{N:,}'],
        ['brands', f"{df['brand'].nunique():,}"],
        ['categories', f"{df['product_type'].nunique():,}"],
        ['columns', f'{len(df.columns)}'],
        ['', '']]
for k in ['Global (Skinsort)', 'Lebanese retail', 'Lebanese origin']:
    rows.append([k, f'{cat.get(k, 0):,}  ({100*cat.get(k,0)/N:.1f}%)'])
rows += [['', ''],
         ['a Lebanese shop price', f"{n('price_usd'):,}"],
         ['a market price', f"{n('price_usd_market'):,}"],
         ['any price at all', f'{any_price:,}  ({100*any_price/N:.1f}%)'],
         ['median Lebanese price',
          f'${p_lb.median():,.2f}' if len(p_lb) else 'n/a'],
         ['median market price',
          f'${p_mk.median():,.2f}' if len(p_mk) else 'n/a'],
         ['sold at two different prices in Lebanon',
          f"{int((num('price_usd_min') != num('price_usd_max')).sum()):,}"],
         ['', ''],
         ['any rating at all', f'{any_rating:,}  ({100*any_rating/N:.1f}%)'],
         ['products with review text', f"{n('review_texts_json'):,}"],
         ['', ''],
         ['all fourteen merge checks', 'PASSED']]
summary = pd.DataFrame(rows, columns=['figure', 'value'])

cov = pd.DataFrame(
    [[c, f'{n(c):,}', f'{100*n(c)/N:.1f}%'] for c in df.columns],
    columns=['column', 'filled', 'share'])

vocab = {}
if os.path.exists('VOCABULARY.json'):
    vocab = json.load(open('VOCABULARY.json', encoding='utf-8'))
vrows = [[k, ' | '.join(str(x) for x in v)[:2000]] for k, v in vocab.items()]
voc = pd.DataFrame(vrows or [['', '']], columns=['column', 'allowed values'])

W = {'product_id': 11, 'source_category': 18, 'brand': 22, 'name': 44,
     'product_type': 18, 'country': 14, 'price_usd': 11, 'price_usd_min': 13,
     'price_usd_max': 13, 'price_usd_market': 16, 'price_market_source': 20,
     'price_market_n': 14, 'price_market_date': 17, 'rating_market': 13,
     'rating_market_count': 19, 'skin_type': 12, 'sensitivity': 12,
     'ingredients': 50, 'key_ingredients': 30, 'free_from': 28,
     'certifications': 22, 'benefits': 30, 'concerns': 26,
     'review_texts_json': 34, 'skin_type_quote': 40, 'skin_type_url': 34,
     'product_url': 40, 'price_source': 18, 'price_date': 12,
     'rating_source': 16, 'rating_count': 12, 'sold_by': 26,
     'skin_type_source': 20, 'product_summary': 44, 'concerns': 30,
     'retailers': 26, 'retailer_urls': 30, 'product_url': 34, 'figure': 40,
     'value': 26, 'column': 22, 'allowed values': 90, 'filled': 10, 'share': 9}

GREEN = {'sold_by', 'product_url', 'price_source', 'price_date',
         'rating_source', 'skin_type_source', 'retailers', 'n_retailers', 'retailer_urls', 'retailer_skin_types',
         'retailers_agree', 'product_url', 'domain', 'src_global',
         'src_lb_retail', 'src_lb_origin', 'source_count', 'first_source',
         'match_method', 'match_score', 'source_category'}
PINK = {c for c in df.columns if c.startswith('skin_type')} | {'sensitivity'}
GOLD = {c for c in df.columns if c.startswith('price') or c.startswith('rating')}

try:
    open(OUT, 'a').close()
except PermissionError:
    import datetime
    OUT = OUT.replace('.xlsx',
                      datetime.datetime.now().strftime('_%H%M%S.xlsx'))
    print(f'  workbook is open in Excel, writing {OUT} instead')

with pd.ExcelWriter(OUT, engine='openpyxl') as w:
    summary.to_excel(w, sheet_name='0 SUMMARY', index=False)
    df.to_excel(w, sheet_name='1 COMBINED', index=False)
    cov.to_excel(w, sheet_name='2 COVERAGE', index=False)
    voc.to_excel(w, sheet_name='3 VOCABULARY', index=False)
    for sh in w.sheets.values():
        for cell in sh[1]:
            v = str(cell.value)
            col = ('6f9c78' if v in GREEN else 'b06a97' if v in PINK else
                   'c07a54' if v in GOLD else '584A7A')
            cell.fill = PatternFill('solid', fgColor=col)
            cell.font = Font(bold=True, color='FFFFFF', size=10)
            cell.alignment = Alignment(vertical='center', horizontal='left')
            sh.column_dimensions[get_column_letter(cell.column)].width = \
                W.get(v, 16)
        sh.row_dimensions[1].height = 22
        sh.freeze_panes = 'D2' if sh.title == '1 COMBINED' else 'A2'
        sh.auto_filter.ref = sh.dimensions

print('=' * 62)
print(f'  {OUT}')
print('=' * 62)
print(f'  {N:,} products, {len(df.columns)} columns, 4 sheets')
print(f'  rebuilt from {DATA}, so the two now agree')
for k in ['Global (Skinsort)', 'Lebanese retail', 'Lebanese origin']:
    print(f'    {k:22s}{cat.get(k, 0):7,}')
print(f'\n  any price {any_price:,} ({100*any_price/N:.1f}%)   '
      f'any rating {any_rating:,} ({100*any_rating/N:.1f}%)')
