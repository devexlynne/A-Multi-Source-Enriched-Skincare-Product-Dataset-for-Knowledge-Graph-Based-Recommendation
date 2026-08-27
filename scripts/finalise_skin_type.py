"""
Finalise the skin type columns

Two columns, no gaps, no extra flags.

    skin_type     Dry / Oily / Combination / Normal / All
    sensitivity   Sensitive / Resistant

What changes
  1. "All skin types" becomes a VALUE, not a separate column.
     2,251 products where the brand said "suitable for all skin types" had a
     blank skin_type and a universal_claim flag. That is the same statement,
     so it now reads skin_type = 'All' and the flag is dropped.

Usage:
    py finalise_skin_type.py
    py build_dataset.py
"""
import pandas as pd

DATASET = 'SKINCARE_DATASET.csv'
df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')
n = len(df)

before_type = int((df['skin_type'] != '').sum())
before_sens = int((df['sensitivity'] != '').sum())
uni = int((df['universal_claim'] == '1').sum())

# 1 + 2. "all skin types", and sensitivity-only rows, become skin_type = 'All'
mask_all = (df['skin_type'] == '') & (
    (df['universal_claim'] == '1') | (df['sensitivity'] != ''))
df.loc[mask_all, 'skin_type'] = 'All'
n_all = int(mask_all.sum())

# 3. complete the sensitivity axis
mask_res = (df['sensitivity'] == '') & (df['skin_type'] != '')
df.loc[mask_res, 'sensitivity'] = 'Resistant'
n_res = int(mask_res.sum())

# 4. drop the flag
if 'universal_claim' in df.columns:
    df = df.drop(columns=['universal_claim'])

df.to_csv(DATASET, index=False)

# ------------------------------------------------------------------ report
still = df[df['skin_type'] == '']
na = int((df['skin_type_status'] == 'not applicable').sum())
facial = n - na
filled = int((df['skin_type'] != '').sum())
facial_filled = int(((df['skin_type'] != '') & (df['skin_type_status'] != 'not applicable')).sum())

print('=' * 66)
print('  FINAL SKIN TYPE COLUMNS')
print('=' * 66)
print(f'  products                    {n:,}')
print(f'    facial products           {facial:,}')
print(f'    not applicable            {na:,}   lip balm, hand cream, hair')
print()
print(f'  skin_type    {before_type:,} -> {filled:,} filled in total')
print(f'     of the {facial:,} FACIAL products, {facial_filled:,} filled  ({100*facial_filled/facial:.1f}%)')
print(f'  sensitivity  {before_sens:,} -> {int((df["sensitivity"] != "").sum()):,}')
print()
print(f'    "All" written from a universal claim or a sensitivity-only row  {n_all:,}')
print(f'    "Resistant" written where no sensitivity claim was found        {n_res:,}')
print(f'    universal_claim column removed                                  ({uni:,} flags folded in)')
print()
print('  SKIN TYPE DISTRIBUTION')
for k, v in df.loc[df['skin_type'] != '', 'skin_type'].value_counts().items():
    print(f'     {k:14s}{v:6,}  ({100*v/filled:5.1f}%)')
print()
print('  SENSITIVITY')
for k, v in df.loc[df['sensitivity'] != '', 'sensitivity'].value_counts().items():
    print(f'     {k:14s}{v:6,}')
print()
print('  WHERE THE VALUES CAME FROM')
LAB = {'1': 'the manufacturer', '2': 'a retailer',
       '3': 'an analysis site', '4': 'other source'}
got = df[df['skin_type'] != '']
for t in ('1', '2', '3', '4'):
    c = int((got['skin_type_tier'] == t).sum())
    if c:
        print(f'     tier {t}  {LAB[t]:20s}{c:6,}  ({100*c/filled:5.1f}%)')
print()
print(f'  still blank                 {len(still):,}')
if len(still):
    print(f'     of those, not applicable {int((still["skin_type_status"] == "not applicable").sum()):,}')
    real = still[still['skin_type_status'] != 'not applicable']
    print(f'     genuinely blank          {len(real):,}')

print('\n  AN EXAMPLE ROW')
ex = df[(df['skin_type'] != '') & (df['skin_type_tier'] == '1')].iloc[0]
for c in ('brand', 'name', 'skin_type', 'sensitivity', 'skin_type_source',
          'skin_type_quote', 'skin_type_url'):
    print(f'     {c:18s}{str(ex[c])[:80]}')
print('\nnow run:  py build_dataset.py')
