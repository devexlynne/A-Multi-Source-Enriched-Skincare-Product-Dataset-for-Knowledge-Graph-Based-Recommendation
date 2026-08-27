"""
Remove the skin type completely, and start again

WHY

Usage:
    py strip_skin_type.py
"""
import re
import pandas as pd

PAIRS = [('OPTION_A_mixed_sources.csv', 'OPTION_A_mixed_sources.csv'),
         ('OPTION_B_single_source.csv', 'OPTION_B_single_source.csv')]
ARCHIVE = 'ARCHIVE_old_skin_type.csv'

CLEAR = ['skin_type', 'sensitivity', 'skin_type_source', 'sensitivity_source',
         'universal_claim', 'skin_normal', 'skin_dry', 'skin_oily',
         'skin_combination', 'skin_sensitive',
         'skin_type_MIXED', 'sensitivity_MIXED', 'skin_type_source_MIXED',
         'amazon_skin_type_raw', 'amazon_asin']
DROP_PAT = re.compile(r'^sc_', re.I)          # everything carried from SkinCarisma

first = True
for src, out in PAIRS:
    df = pd.read_csv(src, low_memory=False, dtype=str).fillna('')
    n = len(df)
    print(f'\n{src}   {n:,} rows, {df.shape[1]} columns')

    # keep a copy of what is being removed, once, from the mixed dataset
    if first and 'skin_type' in df.columns:
        keep = ['product_id', 'brand', 'name'] + [c for c in CLEAR if c in df.columns] \
               + [c for c in df.columns if DROP_PAT.match(c)]
        df[[c for c in keep if c in df.columns]].to_csv(ARCHIVE, index=False)
        print(f'  archived the old values to {ARCHIVE}')
        first = False

    before = int((df['skin_type'] != '').sum()) if 'skin_type' in df.columns else 0

    cleared = []
    for c in CLEAR:
        if c in df.columns:
            df[c] = ''
            cleared.append(c)
    dropped = [c for c in df.columns if DROP_PAT.match(c)]
    df = df.drop(columns=dropped)

    df.to_csv(out, index=False)
    after = int((df['skin_type'] != '').sum()) if 'skin_type' in df.columns else 0
    print(f'  cleared {len(cleared)} columns : {", ".join(cleared)}')
    print(f'  dropped {len(dropped)} SkinCarisma columns')
    print(f'  skin_type filled  {before:,} -> {after:,}')
    print(f'  rows {len(df):,}, columns {df.shape[1]}   (products, ingredients, reviews untouched)')

print('\nthe skin type is now empty in both datasets, by design.')
print('next: rebuild it from the manufacturer, one brand at a time.')
