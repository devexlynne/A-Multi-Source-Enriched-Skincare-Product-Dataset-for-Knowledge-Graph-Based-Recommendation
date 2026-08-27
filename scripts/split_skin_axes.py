"""
SPLIT SKIN TYPE ONTO THE TWO DERMATOLOGICAL AXES  (Baumann)

The problem i am fixing
  My skin_type column held values like "Combination/Sensitive", which mixes two
  different things into one label.

Usage:
    py split_skin_axes.py        -> writes Skincare_Reviewed_FINAL_v10.csv
"""
import pandas as pd

SRC = 'Skincare_Reviewed_FINAL_v7.csv'
OUT = 'Skincare_Reviewed_FINAL_v10.csv'

df = pd.read_csv(SRC, low_memory=False, dtype=str)
print(f'read {len(df):,} products from {SRC}')
print('\nBEFORE - one mixed column:')
print(df[df['skin_type'].fillna('').ne('')]['skin_type'].value_counts().head(8).to_string())


def sebum_axis(r):
    """The sebum-production type. Combination means it suits both dry and oily."""
    if not str(r.get('skin_type_source') or '') or r['skin_type_source'] == 'not declared':
        return ''
    dry  = str(r.get('skin_dry'))  == '1'
    oily = str(r.get('skin_oily')) == '1'
    if dry and oily:  return 'Combination'
    if oily:          return 'Oily'
    if dry:           return 'Dry'
    if str(r.get('skin_normal')) == '1': return 'Normal'
    return ''


def sensitivity_axis(r):
    """The reactivity axis, kept entirely separate from sebum."""
    if not str(r.get('skin_type_source') or '') or r['skin_type_source'] == 'not declared':
        return ''
    return 'Sensitive' if str(r.get('skin_sensitive')) == '1' else 'Resistant'


df['skin_type']   = df.apply(sebum_axis, axis=1)
df['sensitivity'] = df.apply(sensitivity_axis, axis=1)

# keep the old combined label so nothing is lost and the change is auditable
df['skin_type_combined_old'] = [
    '/'.join([a] + ([b] if b == 'Sensitive' else [])) if a else ''
    for a, b in zip(df['skin_type'], df['sensitivity'])]

cols = list(df.columns)
if 'sensitivity' in cols:
    cols.insert(cols.index('skin_type') + 1, cols.pop(cols.index('sensitivity')))
    df = df[cols]

df.to_csv(OUT, index=False)

n = len(df)
print('\nAFTER - two independent axes:')
print('\n  SEBUM AXIS (skin_type)')
for k, v in df[df['skin_type'].ne('')]['skin_type'].value_counts().items():
    print(f'     {k:14s} {v:6,}  ({100*v/n:5.1f}%)')
print('\n  REACTIVITY AXIS (sensitivity)')
for k, v in df[df['sensitivity'].ne('')]['sensitivity'].value_counts().items():
    print(f'     {k:14s} {v:6,}  ({100*v/n:5.1f}%)')

print('\n  THE TWO AXES CROSSED (this is what one column could never show):')
x = pd.crosstab(df[df['skin_type'].ne('')]['skin_type'],
                df[df['skin_type'].ne('')]['sensitivity'])
print(x.to_string())

have = int(df['skin_type'].ne('').sum())
print(f'\ncoverage unchanged: {have:,} of {n:,} = {100*have/n:.1f}%')
print(f'wrote {OUT}')
