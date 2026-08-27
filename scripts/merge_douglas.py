"""
Match the Douglas skin-type labels to my products and fold them in.

Uses the SAME matching method as everywhere else in the thesis, so the
methodology stays consistent:
   block by brand  (Papadakis 2020)
   score with token_set_ratio  (Cohen 2003)
   accept at >= 95  (Fellegi & Sunter 1969)

Douglas categorised the product itself, so this is RETAILER-DECLARED evidence:
it is written as 'declared:douglas' and it never overwrites Amazon.
Run after scrape_douglas.py.
"""
import re
import pandas as pd
from rapidfuzz import fuzz, process

def norm(s): return re.sub(r'[^a-z0-9]', '', str(s).lower())

# start from whichever version exists: v7 (skincarisma done) else v6
import os
SRC = 'Skincare_Reviewed_FINAL_v7.csv' if os.path.exists('Skincare_Reviewed_FINAL_v7.csv') \
      else 'Skincare_Reviewed_FINAL_v6.csv'
print('starting from', SRC)

df  = pd.read_csv(SRC, low_memory=False, dtype=str)
dg  = pd.read_csv('douglas_skintype.csv', dtype=str)

# one row per Douglas product, collecting every skin type it was listed under
dg['k'] = dg['brand'].map(norm) + '|' + dg['name'].map(norm)
types = dg.groupby('k')['douglas_skin_type'].apply(lambda s: set(s)).to_dict()
info  = dg.drop_duplicates('k').set_index('k')[['brand', 'name']].to_dict('index')

# brand-blocked index of Douglas products
idx = {}
for k, v in info.items():
    idx.setdefault(norm(v['brand']), []).append((k, v['name']))

filled = 0
for i, row in df.iterrows():
    if row['skin_type_source'] not in ('not declared',):
        continue                                    # never overwrite a better source
    cands = idx.get(norm(row['brand']), [])
    if not cands:
        continue
    names = [c[1] for c in cands]
    hit = process.extractOne(str(row['name']), names, scorer=fuzz.token_set_ratio)
    if not hit or hit[1] < 95:                      # the thesis-wide threshold
        continue
    t = types[cands[hit[2]][0]]
    dry  = 'dry' in t or 'combination' in t
    oily = 'oily' in t or 'acne' in t or 'combination' in t
    sens = 'sensitive' in t
    df.at[i, 'skin_dry']         = '1' if dry else '0'
    df.at[i, 'skin_oily']        = '1' if oily else '0'
    df.at[i, 'skin_sensitive']   = '1' if sens else '0'
    df.at[i, 'skin_combination'] = '1' if 'combination' in t else '0'
    df.at[i, 'skin_normal']      = '1'
    parts = (['Combination'] if 'combination' in t
             else [p for p, c in (('Oily', oily), ('Dry', dry)) if c])
    if sens: parts.append('Sensitive')
    df.at[i, 'skin_type'] = '/'.join(parts) if parts else 'Normal'
    df.at[i, 'skin_type_source'] = 'declared:douglas'
    df.at[i, 'douglas_categories'] = ', '.join(sorted(t))
    filled += 1

df.to_csv('Skincare_Reviewed_FINAL_v8.csv', index=False)
n = len(df)
print('\n--- COVERAGE ---')
for src, cnt in df['skin_type_source'].value_counts().items():
    print(f'  {src:24s} {cnt:6,}  ({100*cnt/n:.1f}%)')
have = int(df['skin_type_source'].ne('not declared').sum())
print(f'\nTOTAL WITH A SKIN TYPE: {have:,} of {n:,} = {100*have/n:.1f}%')
print(f'Douglas added this run : {filled:,}')
print('wrote Skincare_Reviewed_FINAL_v8.csv')
