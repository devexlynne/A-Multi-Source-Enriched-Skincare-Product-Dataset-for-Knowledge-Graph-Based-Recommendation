"""
The cross-check, in full

Run after scrape_skincarisma_ALL.py.

Two questions this answers
  1. If i took EVERY skin type from one source (SkinCarisma) instead of mixing
     sources, how much coverage would i have, and would it be better?
"""
import re
import pandas as pd

df = pd.read_csv('Skincare_Reviewed_FINAL_v14.csv', low_memory=False, dtype=str)
sc = pd.read_csv('skincarisma_ALL_products.csv', low_memory=False, dtype=str)
sc = sc[sc['found'] == '1'].drop_duplicates('product_id')
n = len(df)

print('=' * 70)
print('PART 1 - WHAT IF EVERY SKIN TYPE CAME FROM ONE SOURCE?')
print('=' * 70)
print(f'products in the dataset          : {n:,}')
print(f'found on SkinCarisma             : {len(sc):,}  ({100*len(sc)/n:.1f}%)')
have_mixed = int(df['skin_type'].fillna('').ne('').sum())
print(f'current MIXED-source coverage    : {have_mixed:,}  ({100*have_mixed/n:.1f}%)')
print(f'single-source coverage would be  : {len(sc):,}  ({100*len(sc)/n:.1f}%)')

print('\n' + '=' * 70)
print('PART 2 - THE CROSS-CHECK: DO THE SOURCES AGREE?')
print('=' * 70)

# rebuild the Amazon raw values
amz = pd.read_csv('amazon_skintype.csv', dtype=str)
m = pd.read_csv('acc19k_matches.csv', low_memory=False, dtype=str)
norm = lambda s: re.sub(r'[^a-z0-9]', '', str(s).lower())
m['_k'] = m['brand'].map(norm) + '|' + m['name'].map(norm)
df['_k'] = df['brand'].map(norm) + '|' + df['name'].map(norm)
df['asin'] = df['_k'].map(dict(zip(m['_k'], m['am_asin'])))
df['amz_raw'] = df['asin'].map(dict(zip(amz['asin'], amz['amazon_skin_type_raw'])))

j = df.merge(sc[['product_id', 'sc_dry', 'sc_oily', 'sc_sensitive']],
             on='product_id', how='inner')
j = j[j['amz_raw'].notna()]
# EXCLUDE "All" - it agrees with everything and would inflate the result
j = j[~j['amz_raw'].str.strip().str.lower().eq('all')]
print(f'products with BOTH a specific Amazon value and a SkinCarisma analysis: {len(j):,}')

def amz_flag(raw, axis):
    s = str(raw).lower()
    if axis == 'dry':  return int('dry' in s)
    if axis == 'oily': return int('oil' in s or 'acne' in s)
    return int('sensitive' in s)

if len(j):
    print(f"\n{'axis':12s}{'agreement':>11s}{'amazon yes':>12s}{'skincarisma yes':>17s}{'both':>7s}{'recall':>9s}")
    rows = []
    for axis, col in (('dry', 'sc_dry'), ('oily', 'sc_oily'), ('sensitive', 'sc_sensitive')):
        a = j['amz_raw'].map(lambda r: amz_flag(r, axis)) == 1
        s = j[col].fillna('0').astype(str).eq('1')
        agree = (a == s).mean() * 100
        rec = (s[a]).mean() * 100 if a.sum() else 0
        print(f'{axis:12s}{agree:10.1f}%{a.sum():12d}{s.sum():17d}{(a & s).sum():7d}{rec:8.1f}%')
        rows.append(dict(axis=axis, n_compared=len(j), agreement_pct=round(agree, 1),
                         amazon_yes=int(a.sum()), skincarisma_yes=int(s.sum()),
                         both_yes=int((a & s).sum()), recall_pct=round(rec, 1)))
    pd.DataFrame(rows).to_csv('crosscheck_results.csv', index=False)

    print('\n--- disagreement examples (the pattern is the finding) ---')
    a_dry = j['amz_raw'].map(lambda r: amz_flag(r, 'dry')) == 1
    s_dry = j['sc_dry'].fillna('0').astype(str).eq('1')
    dis = j[a_dry != s_dry][['brand', 'name', 'amz_raw', 'sc_dry', 'sc_oily', 'sc_sensitive']]
    print(dis.head(10).to_string(index=False))
    dis.to_csv('crosscheck_disagreements.csv', index=False)
    print('\nwrote crosscheck_results.csv and crosscheck_disagreements.csv')
else:
    print('no overlap yet - run scrape_skincarisma_ALL.py first')
