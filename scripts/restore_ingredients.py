"""
Put back the ingredient lists the first validator damaged

What went wrong
  The first version of validate_ingredients.py kept the longest UNBROKEN run of
  ingredient-looking pieces. One unusual name in the middle of a formula broke
  the run, and only the longer half survived:

Usage:
    py restore_ingredients.py
    py scrape_lebanese_ingredients.py     to re-read the shop pages, free
    py validate_ingredients.py            the fixed version
"""
import os
import pandas as pd

DATA = 'LEBANESE_RETAIL.csv'
PROGRESS = 'serper_ingredients_progress.csv'

df = pd.read_csv(DATA, dtype=str, low_memory=False).fillna('')
N = len(df)
before = int((df['ingredients'] != '').sum())

if not os.path.exists(PROGRESS):
    raise SystemExit(f'{PROGRESS} not found, nothing to restore from')

p = pd.read_csv(PROGRESS, dtype=str).fillna('')
p = p[p['ingredients'] != ''].drop_duplicates('product_id').set_index('product_id')
print(f'{len(p):,} original Serper lists available in the progress file\n')

restored = shortened = refilled = 0
for i in df.index:
    pid = df.at[i, 'product_id']
    if pid not in p.index:
        continue
    orig = str(p.at[pid, 'ingredients'])
    cur = str(df.at[i, 'ingredients'])
    if cur == orig:
        continue
    if not cur:
        refilled += 1
    elif len(cur) < len(orig):
        shortened += 1
    df.at[i, 'ingredients'] = orig
    df.at[i, 'ingredient_source'] = p.at[pid, 'ingredient_source']
    df.at[i, 'ingredient_url'] = p.at[pid, 'ingredient_url']
    df.at[i, 'ingredient_rule'] = p.at[pid, 'ingredient_rule']
    restored += 1

df.to_csv(DATA, index=False)
after = int((df['ingredients'] != '').sum())

# what the shop scrape had, and how much of it is now gone
shop_rows = df['ingredient_source'] != ''
shop_empty = int((shop_rows & (df['ingredients'] == '')).sum())
still_missing = int((df['ingredients'] == '').sum())

print('=' * 62)
print('  RESTORED FROM THE SERPER PROGRESS FILE')
print('=' * 62)
print(f'  lists put back              {restored:,}')
print(f'    of which had been emptied {refilled:,}')
print(f'    of which had been trimmed {shortened:,}')
print()
print(f'  ingredient lists  {before:,} -> {after:,}  ({100*after/N:.1f}% of {N:,})')
print(f'  still missing     {still_missing:,}')
print()
if shop_empty:
    print(f'  {shop_empty:,} rows were filled by the shop scrape and are now empty.')
    print('  those have no backup, so read the shop pages again. it is free:')
    print('     py scrape_lebanese_ingredients.py')
else:
    print('  no shop-scraped rows were lost')
print()
print('  then run the FIXED validator, which tolerates a gap of two odd')
print('  pieces inside a formula and will not cut a real list in half:')
print('     py validate_ingredients.py --report-only')
print('     py validate_ingredients.py')
