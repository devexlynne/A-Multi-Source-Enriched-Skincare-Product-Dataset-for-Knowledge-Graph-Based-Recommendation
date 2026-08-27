"""
Apply the search results to the dataset

Takes skintype_search_results.csv and writes the values onto the dataset.

There is NO MATCHING in this step, and that is the point. The search was run
FOR a specific product_id, so the answer already belongs to that row. It is a
straight join on product_id. Nothing can be mismatched.

RUN
  py skintype_apply.py     ->  SKINCARE_DATASET.csv updated
  then                         py build_dataset.py
"""
import pandas as pd

DATASET = 'SKINCARE_DATASET.csv'
RESULTS = 'skintype_search_results.csv'

COLS = ['skin_type', 'sensitivity', 'universal_claim', 'skin_type_source',
        'skin_type_authority', 'skin_type_strength', 'skin_type_rule',
        'skin_type_quote', 'skin_type_url']

df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')
rs = pd.read_csv(RESULTS, low_memory=False, dtype=str).fillna('')
rs = rs.drop_duplicates('product_id')
n = len(df)
print(f'dataset {n:,} products   search results {len(rs):,}')

for c in COLS:
    if c in df.columns:
        df = df.drop(columns=[c])

df = df.merge(rs[['product_id'] + COLS], on='product_id', how='left').fillna('')

got = int((df['skin_type'] != '').sum())
uni = int((df['universal_claim'] == '1').sum())
sen = int((df['sensitivity'] != '').sum())

df.to_csv(DATASET, index=False)

# what is still empty, ranked by brand so the next pass is efficient
miss = df[(df['skin_type'] == '') & (df['universal_claim'] != '1')]
miss[['product_id', 'brand', 'name']].to_csv('skintype_still_missing.csv', index=False)
miss.groupby('brand').size().sort_values(ascending=False) \
    .reset_index(name='products_missing').to_csv('skintype_missing_by_brand.csv', index=False)

print('\n' + '=' * 60)
print(f'  skin type filled      {got:,}  ({100*got/n:.1f}%)')
print(f'  sensitivity filled    {sen:,}  ({100*sen/n:.1f}%)')
print(f'  universal claim       {uni:,}  ({100*uni/n:.1f}%)')
print(f'  still empty           {len(miss):,}  ({100*len(miss)/n:.1f}%)')

if got:
    print('\n  who answered')
    for k, v in df.loc[df['skin_type'] != '', 'skin_type_authority'].value_counts().items():
        print(f'     {k:16s}{v:6,}  ({100*v/got:.1f}%)')
    print('\n  how strongly')
    for k, v in df.loc[df['skin_type'] != '', 'skin_type_strength'].value_counts().sort_index().items():
        print(f'     strength {k}      {v:6,}')
    print('\n  strength 1 + 2 only (if strength 3 is rejected):',
          f'{int(df["skin_type_strength"].isin(["1","2"]).sum()):,}')
    print('\n  an example row')
    ex = df[df['skin_type'] != ''].iloc[0]
    for c in ('brand', 'name', 'skin_type', 'sensitivity', 'skin_type_source',
              'skin_type_authority', 'skin_type_strength', 'skin_type_quote', 'skin_type_url'):
        print(f'     {c:20s}{str(ex[c])[:86]}')

print('\n  wrote skintype_still_missing.csv and skintype_missing_by_brand.csv')
print('\nrebuild the workbook:  py build_dataset.py')
