"""
FIX: 178 SENSITIVITY VALUES THAT STILL CAME FROM "suited_for"

What my audit caught
  When my supervisor rejected the afterUse / suited_for derivation i rebuilt the
  skin type from scratch. The SEBUM axis was rebuilt correctly - no product gets
  its dry/oily/normal/combination value from those tags any more.

  But the SENSITIVITY axis was not fully rebuilt. 178 products kept a
  sensitivity value that traces back to suited_for, and nothing else:
"""
import pandas as pd

SRC = 'Skincare_Reviewed_FINAL_v14.csv'
OUT = 'Skincare_Reviewed_FINAL_v15.csv'

df = pd.read_csv(SRC, low_memory=False, dtype=str).fillna('')
print(f'read {len(df):,} products from {SRC}')

before_sens = int((df['sensitivity'] != '').sum())

# ---- the two contradictory groups ------------------------------------------
bad = df['skin_type_source'].isin(['claim:universal(manual)', 'searched:none found']) \
      & (df['sensitivity'] != '')

print('\nrows carrying a sensitivity value they cannot justify:')
for s, c in df.loc[bad, 'skin_type_source'].value_counts().items():
    print(f'   {s:28s}{c:5,}')
print(f'   {"TOTAL":28s}{int(bad.sum()):5,}')

# proof, for the write-up: every one of them traces to the suited_for sentence
if 'suited_for' in df.columns:
    n_from_sf = int(df.loc[bad, 'suited_for'].str.contains('sensitive skin', case=False).sum())
    print(f'\n   of those, {n_from_sf:,} have "sensitive skin" inside their suited_for text')
    print(f'   and {int(bad.sum()) - n_from_sf:,} do not even have that - inconsistent with their own source')

# ---- apply ------------------------------------------------------------------
df.loc[bad, 'sensitivity'] = ''
if 'skin_sensitive' in df.columns:
    df.loc[bad, 'skin_sensitive'] = ''

# ---- drop the raw column so it can never leak back --------------------------
if 'suited_for' in df.columns:
    df = df.drop(columns=['suited_for'])
    print('\ndropped the raw suited_for column')

df.to_csv(OUT, index=False)

# ---- report -----------------------------------------------------------------
n = len(df)
after_sens = int((df['sensitivity'] != '').sum())
seb = int((df['skin_type'] != '').sum())

print('\n' + '=' * 68)
print('AFTER THE FIX')
print('=' * 68)
print(f'  sebum axis      {seb:,}  ({100*seb/n:.1f}%)   unchanged - was never affected')
print(f'  sensitivity     {before_sens:,} -> {after_sens:,}  ({100*after_sens/n:.1f}%)')
print(f'  removed         {before_sens - after_sens:,} values that had no evidence behind them')
print('\n  sensitivity now comes ONLY from:')
sub = df[df['sensitivity'] != '']
for s, c in sub['skin_type_source'].value_counts().items():
    print(f'     {s:30s}{c:6,}')
print(f'\nwrote {OUT}')
print('\nNOTE: coverage drops slightly, and that is correct. Those 178 products')
print('never had sensitivity evidence - they had a benefits sentence.')
