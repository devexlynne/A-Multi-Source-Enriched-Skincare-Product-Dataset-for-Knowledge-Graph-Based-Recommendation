"""
Merge pass 2 into the dataset. A weaker tier can NEVER overwrite a stronger one.

  py serper_apply2.py
  py build_dataset.py
"""
import pandas as pd

DATASET = 'SKINCARE_DATASET.csv'
RESULTS = 'serper_pass3_results.csv'
COLS = ['skin_type', 'sensitivity', 'universal_claim', 'skin_type_tier',
        'skin_type_authority', 'skin_type_source', 'skin_type_rule',
        'skin_type_quote', 'skin_type_url']

df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')
rs = pd.read_csv(RESULTS, low_memory=False, dtype=str).fillna('').drop_duplicates('product_id')
n = len(df)
R = {r['product_id']: r for _, r in rs.iterrows()}
filled = 0

for i, row in df.iterrows():
    s = R.get(row['product_id'])
    if s is None or not (s['skin_type'] or s['sensitivity'] or s['universal_claim'] == '1'):
        continue
    if row['skin_type'] or row['sensitivity'] or row['universal_claim'] == '1':
        continue                       # already answered by a stronger pass
    for c in COLS:
        df.at[i, c] = s[c]
    filled += 1

df.to_csv(DATASET, index=False)
nothing = df[(df['skin_type'] == '') & (df['sensitivity'] == '') & (df['universal_claim'] != '1')]
print(f'  recovered by pass 2   {filled:,}')
print('=' * 56)
print(f'  sebum type       {int((df["skin_type"]!="").sum()):6,}  ({100*int((df["skin_type"]!="").sum())/n:5.1f}%)')
print(f'  sensitivity      {int((df["sensitivity"]!="").sum()):6,}  ({100*int((df["sensitivity"]!="").sum())/n:5.1f}%)')
print(f'  universal claim  {int((df["universal_claim"]=="1").sum()):6,}')
print(f'  HAS SOMETHING    {n-len(nothing):6,}  ({100*(n-len(nothing))/n:5.1f}%)')
print(f'  still nothing    {len(nothing):6,}  ({100*len(nothing)/n:5.1f}%)')
print('\n  by tier')
got = df[(df['skin_type'] != '') | (df['sensitivity'] != '') | (df['universal_claim'] == '1')]
LAB = {'1': 'manufacturer', '2': 'retailer', '3': 'analysis site', '4': 'other (weakest)'}
for t in ('1', '2', '3', '4'):
    c = int((got['skin_type_tier'] == t).sum())
    if c:
        print(f'     tier {t}  {LAB[t]:18s}{c:6,}  ({100*c/n:5.1f}%)')
nothing[['product_id', 'brand', 'name']].to_csv('skintype_still_empty.csv', index=False)
print(f'\n  wrote skintype_still_empty.csv ({len(nothing):,})')
print('\nnow run:  py build_dataset.py')
