"""
Fix: "all skin types" is a tolerance claim, not a skin type

What was wrong
  When a source said "All" I set all five skin flags to 1. Because dry=1 and
  oily=1 together mean Combination, and sensitive=1 means Sensitive, those
  products came out labelled "Combination / Sensitive". So 751 products - 31.9%
  of everything Amazon declared - were carrying a specific skin-type claim that
  nobody ever made.

Usage:
    py fix_universal_claims.py      ->  Skincare_Reviewed_FINAL_v13.csv
"""
import re
import pandas as pd

SRC = 'Skincare_Reviewed_FINAL_v12.csv'
OUT = 'Skincare_Reviewed_FINAL_v13.csv'
FLAGS = ['skin_normal', 'skin_dry', 'skin_oily', 'skin_combination', 'skin_sensitive']

df = pd.read_csv(SRC, low_memory=False, dtype=str)
print(f'read {len(df):,} products')


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


# ---- recover the raw Amazon wording so we can spot the universal claims ----
amz = pd.read_csv('amazon_skintype.csv', dtype=str)
m = pd.read_csv('acc19k_matches.csv', low_memory=False, dtype=str)
m['_k'] = m['brand'].map(norm) + '|' + m['name'].map(norm)
df['_k'] = df['brand'].map(norm) + '|' + df['name'].map(norm)
df['amazon_asin'] = df['_k'].map(dict(zip(m['_k'], m['am_asin'])))
df['amazon_skin_type_raw'] = df['amazon_asin'].map(
    dict(zip(amz['asin'], amz['amazon_skin_type_raw'])))

# ---- which products rest on a universal claim rather than a real skin type --
UNIVERSAL = re.compile(r'^\s*(all|all skin types?|universal|any|suitable for all)\s*$', re.I)
raw = df['amazon_skin_type_raw'].fillna('')
is_universal = raw.str.match(UNIVERSAL)

print(f'\nproducts whose declared value is only a universal claim: {int(is_universal.sum()):,}')
print('what they are currently labelled:')
print('   skin_type  :', df.loc[is_universal, 'skin_type'].value_counts().to_dict())
print('   sensitivity:', df.loc[is_universal, 'sensitivity'].value_counts().to_dict())

# ---- apply the fix ---------------------------------------------------------
df['universal_claim'] = ''
idx = df.index[is_universal]
df.loc[idx, 'universal_claim']  = '1'
df.loc[idx, 'skin_type']        = ''          # no sebum evidence was given
df.loc[idx, 'sensitivity']      = ''          # no reactivity evidence was given
for f in FLAGS:
    df.loc[idx, f] = ''                       # the five flags are cleared too
df.loc[idx, 'skin_type_source'] = 'claim:universal(amazon)'

# products that carry a universal claim ALONGSIDE a specific type keep the type
also = df['amazon_skin_type_raw'].fillna('').str.contains(r'\ball\b', case=False) & ~is_universal
df.loc[also, 'universal_claim'] = '1'
print(f'products with a universal claim AND a specific type (type kept): {int(also.sum()):,}')

df = df.drop(columns=['_k'])
df.to_csv(OUT, index=False)

# ---- report ----------------------------------------------------------------
n = len(df)
print('\n' + '=' * 68)
print('COVERAGE AFTER THE FIX')
print('=' * 68)
for s, c in df['skin_type_source'].value_counts().items():
    print(f'  {s:32s} {c:6,}  ({100*c/n:5.1f}%)')

real = df['skin_type'].fillna('').ne('').sum()
sens = df['sensitivity'].fillna('').ne('').sum()
uni  = df['universal_claim'].eq('1').sum()
none = n - real - int(is_universal.sum())
print(f'\n  sebum axis (a real skin type) : {real:,}  ({100*real/n:.1f}%)')
print(f'  sensitivity axis              : {sens:,}  ({100*sens/n:.1f}%)')
print(f'  universal claim only          : {int(is_universal.sum()):,}  ({100*is_universal.mean():.1f}%)')
print(f'  nothing at all                : {none:,}')
print(f'\n  any information at all        : {n-none:,}  ({100*(n-none)/n:.1f}%)')
print(f'\nwrote {OUT}')
print('\nNOTE: headline coverage falls, and that is the point. Those 751 products')
print('never had a skin type - they had a marketing claim, and it is now recorded')
print('as one (Vendruscolo et al. 2025, Dermatological Reviews 6:e70045).')
