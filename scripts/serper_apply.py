"""
Write the Serper results onto the dataset.

No matching. The search was run FOR a product_id, so the answer already belongs
to that row. It is a straight join. A Serper value only replaces an existing one
if it comes from a STRONGER source, so nothing good is ever overwritten.

  py serper_apply.py
  py build_dataset.py
"""
import pandas as pd

DATASET = 'SKINCARE_DATASET.csv'
RESULTS = 'serper_skintype_results.csv'

df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')
rs = pd.read_csv(RESULTS, low_memory=False, dtype=str).fillna('').drop_duplicates('product_id')
n = len(df)
print(f'dataset {n:,}   serper results {len(rs):,}')

for c in ('skin_type', 'sensitivity', 'universal_claim', 'skin_type_tier',
          'skin_type_authority', 'skin_type_source', 'skin_type_rule',
          'skin_type_quote', 'skin_type_url'):
    if c not in df.columns:
        df[c] = ''

R = {r['product_id']: r for _, r in rs.iterrows()}
filled = upgraded = 0

for i, row in df.iterrows():
    s = R.get(row['product_id'])
    # a row that states ONLY sensitivity is still real information.
    # "Recommended for sensitive skin" says nothing about sebum, and that is
    # fine: Baumann treats the two as separate axes. Requiring a sebum value
    # here silently discarded 893 sensitivity findings.
    if s is None or not (s['skin_type'] or s['sensitivity'] or s['universal_claim'] == '1'):
        continue
    old = pd.to_numeric(row['skin_type_tier'], errors='coerce')
    new = pd.to_numeric(s['skin_type_tier'], errors='coerce')
    had = bool(row['skin_type'] or row['sensitivity'] or row['universal_claim'] == '1')
    # take it if the row was empty, or if this source is stronger
    if had and not (pd.notna(new) and pd.notna(old) and new < old):
        continue
    for c in ('skin_type', 'sensitivity', 'universal_claim', 'skin_type_tier',
              'skin_type_authority', 'skin_type_source', 'skin_type_rule',
              'skin_type_quote', 'skin_type_url'):
        df.at[i, c] = s[c]
    if had:
        upgraded += 1
    else:
        filled += 1

df.to_csv(DATASET, index=False)

seb = int((df['skin_type'] != '').sum())
sen = int((df['sensitivity'] != '').sum())
uni = int((df['universal_claim'] == '1').sum())
empty = int(((df['skin_type'] == '') & (df['universal_claim'] != '1')).sum())

print(f'\n  newly filled rows      {filled:,}')
print(f'  upgraded to a stronger source  {upgraded:,}')
print('\n' + '=' * 56)
print(f'  skin type       {seb:6,}  ({100*seb/n:5.1f}%)')
print(f'  sensitivity     {sen:6,}  ({100*sen/n:5.1f}%)')
print(f'  all-types claim {uni:6,}  ({100*uni/n:5.1f}%)')
print(f'  still empty     {empty:6,}  ({100*empty/n:5.1f}%)')

got = df[(df['skin_type'] != '') | (df['universal_claim'] == '1')]
print('\n  by tier')
LAB = {'1': 'manufacturer', '2': 'retailer', '3': 'analysis site', '4': 'derived'}
for t in ('1', '2', '3', '4'):
    c = int((got['skin_type_tier'] == t).sum())
    if c:
        print(f'     tier {t}  {LAB[t]:16s}{c:6,}  ({100*c/n:5.1f}%)')

df[(df['skin_type'] == '') & (df['universal_claim'] != '1')][['product_id', 'brand', 'name']] \
    .to_csv('skintype_still_empty.csv', index=False)
print(f'\n  wrote skintype_still_empty.csv ({empty:,} rows)')
print('\nnow run:  py build_dataset.py')
