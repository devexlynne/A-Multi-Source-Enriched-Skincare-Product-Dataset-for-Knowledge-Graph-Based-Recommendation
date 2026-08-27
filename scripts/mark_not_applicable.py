"""
Mark the products that cannot have a facial skin type

WHY

  An empty skin_type cell currently means two very different things:

      "we searched and found nothing"        a gap in the data
      "this question does not apply"         a lip balm

Usage:
    py mark_not_applicable.py
"""
import re
import pandas as pd

DATASET = 'SKINCARE_DATASET.csv'

FACE = re.compile(r'\bface|facial\b', re.I)
NOFACE = re.compile(r'\blip\b|lip balm|lip mask|lip oil|lip treatment|lip cream|'
                    r'\bhand\b|hand cream|\bfoot\b|\bnail\b|cuticle|'
                    r'\bhair\b|shampoo|conditioner|scalp|'
                    r'deodorant|antiperspirant|\bbrush\b|\btool\b|device|roller|gua sha|'
                    r'headband|toothpaste|perfume|candle', re.I)

df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')
n = len(df)
# ALWAYS recompute from scratch. The previous version only wrote a status
# where the cell was empty, so after the first run it never updated again and
# kept reporting the old coverage even after 1,182 more products were filled.
df['skin_type_status'] = ''

blob = df['product_type'] + ' ' + df['name']
not_face = blob.str.contains(NOFACE, na=False) & ~blob.str.contains(FACE, na=False)

df.loc[not_face, 'skin_type_status'] = 'not applicable'
# universal_claim was folded into skin_type = 'All' by finalise_skin_type.py
# and the column no longer exists, so guard against it.
has = (df['skin_type'] != '') | (df['sensitivity'] != '')
if 'universal_claim' in df.columns:
    has = has | (df['universal_claim'] == '1')
df.loc[has & ~not_face, 'skin_type_status'] = 'found'
df.loc[~has & ~not_face, 'skin_type_status'] = 'searched, not stated'

df.to_csv(DATASET, index=False)

applicable = n - int(not_face.sum())
found = int((df['skin_type_status'] == 'found').sum())
missing = int((df['skin_type_status'] == 'searched, not stated').sum())

print(f'products                          {n:,}')
print(f'  not applicable (lip, hand, hair) {int(not_face.sum()):,}')
print(f'  facial products                  {applicable:,}')
print()
print(f'  found                            {found:,}  ({100*found/applicable:.1f}% of facial products)')
print(f'  searched, brand does not state   {missing:,}  ({100*missing/applicable:.1f}%)')
print()
print('  what was excluded:')
print(df.loc[not_face, 'product_type'].value_counts().head(8).to_string())
print()
print('  KEPT even though they mention lip or body, because they are facial:')
kept = df[blob.str.contains(NOFACE, na=False) & blob.str.contains(FACE, na=False)]
print(f'     {len(kept):,} products, e.g.')
for _, x in kept.head(4).iterrows():
    print(f'       {x["brand"][:18]:18s} {x["name"][:52]}')
print('\nnow run:  py build_dataset.py')
