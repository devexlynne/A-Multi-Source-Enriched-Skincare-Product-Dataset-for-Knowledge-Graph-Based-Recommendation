"""
Match the Lebanese Shopify skin-type tags to my products and fold them in.

Same matching method as the rest of the thesis, so nothing new needs defending:
    block by brand            (Papadakis 2020)
    score with token_set_ratio (Cohen 2003)
    accept at >= 95            (Fellegi & Sunter 1969)

Priority order, never overwritten downwards:
    declared:amazon         manufacturer said it
    declared:lebanese_shop  a retailer tagged it        <- this script
    derived:skincarisma     an expert site estimated it
    not declared            nobody said anything
"""
import os, re
import pandas as pd
from rapidfuzz import fuzz, process

def norm(s): return re.sub(r'[^a-z0-9]', '', str(s).lower())

SRC = next(f for f in ('Skincare_Reviewed_FINAL_v7.csv',
                       'Skincare_Reviewed_FINAL_v6.csv') if os.path.exists(f))
print('starting from', SRC)
df = pd.read_csv(SRC, low_memory=False, dtype=str)
sh = pd.read_csv('lebanese_shopify_skintype.csv', low_memory=False, dtype=str)
sh = sh[sh['has_skin_type'] == '1']
print(f'shop products carrying a skin type: {len(sh):,}')

idx = {}
for _, r in sh.iterrows():
    idx.setdefault(norm(r['brand']), []).append(r)

filled = 0
for i, row in df.iterrows():
    if row['skin_type_source'] != 'not declared':
        continue                                   # never overwrite a better source
    cands = idx.get(norm(row['brand']), [])
    if not cands:
        continue
    names = [str(c['name']) for c in cands]
    hit = process.extractOne(str(row['name']), names, scorer=fuzz.token_set_ratio)
    if not hit or hit[1] < 95:                     # the thesis-wide threshold
        continue
    c = cands[hit[2]]
    dry  = str(c['sh_dry']) == '1'
    oily = str(c['sh_oily']) == '1'
    sens = str(c['sh_sensitive']) == '1'
    comb = str(c['sh_combination']) == '1'
    df.at[i, 'skin_dry']         = '1' if dry else '0'
    df.at[i, 'skin_oily']        = '1' if oily else '0'
    df.at[i, 'skin_sensitive']   = '1' if sens else '0'
    df.at[i, 'skin_combination'] = '1' if comb else '0'
    df.at[i, 'skin_normal']      = '1' if str(c['sh_normal']) == '1' else '0'
    parts = (['Combination'] if comb
             else [p for p, x in (('Oily', oily), ('Dry', dry)) if x])
    if sens: parts.append('Sensitive')
    df.at[i, 'skin_type'] = '/'.join(parts) if parts else 'Normal'
    df.at[i, 'skin_type_source'] = 'declared:lebanese_shop'
    df.at[i, 'shop_source'] = c['shop']
    df.at[i, 'shop_match_score'] = hit[1]
    filled += 1

df.to_csv('Skincare_Reviewed_FINAL_v9.csv', index=False)
n = len(df)
print('\n--- COVERAGE ---')
for src, cnt in df['skin_type_source'].value_counts().items():
    print(f'  {src:26s} {cnt:6,}  ({100*cnt/n:.1f}%)')
have = int(df['skin_type_source'].ne('not declared').sum())
print(f'\nTOTAL WITH A SKIN TYPE: {have:,} of {n:,} = {100*have/n:.1f}%')
print(f'Lebanese shops added   : {filled:,}')
print('wrote Skincare_Reviewed_FINAL_v9.csv')
