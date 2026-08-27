"""
Fold your manually-filled worklist back into the dataset.

Run this whenever you like - after 50 rows or after all 766. It only takes rows
where you actually filled something in, so it is safe to run repeatedly.

Every manual value is written as source 'manual:<what you typed in source>',
e.g. manual:manufacturer, and the URL you pasted is kept alongside it, so each
label stays checkable - the same standard as the automated sources.
"""
import os
import pandas as pd

SRC  = 'Skincare_Reviewed_FINAL_v10.csv'
WORK = 'Skin_Type_Worklist.xlsx'
OUT  = 'Skincare_Reviewed_FINAL_v12.csv'

df = pd.read_csv(SRC, low_memory=False, dtype=str)
w  = pd.read_excel(WORK, sheet_name='Worklist', dtype=str).fillna('')

filled = w[(w['skin_type'].str.strip() != '') | (w['sensitivity'].str.strip() != '')]
print(f'rows you filled in: {len(filled):,} of {len(w):,}')
if filled.empty:
    raise SystemExit('nothing filled in yet - open the worklist and add some rows first')

VALID_TYPE = {'dry', 'normal', 'oily', 'combination'}
VALID_SENS = {'sensitive', 'resistant'}
by_id = filled.set_index('product_id')

added, skipped = 0, []
for i, row in df.iterrows():
    pid = row['product_id']
    if pid not in by_id.index or row['skin_type_source'] != 'not declared':
        continue
    r = by_id.loc[pid]
    st = str(r['skin_type']).strip().title()
    sn = str(r['sensitivity']).strip().title()
    if st and st.lower() not in VALID_TYPE:
        skipped.append((pid, 'bad skin_type: ' + st)); continue
    if sn and sn.lower() not in VALID_SENS:
        skipped.append((pid, 'bad sensitivity: ' + sn)); continue

    if st:
        df.at[i, 'skin_type']        = st
        df.at[i, 'skin_dry']         = '1' if st in ('Dry', 'Combination') else '0'
        df.at[i, 'skin_oily']        = '1' if st in ('Oily', 'Combination') else '0'
        df.at[i, 'skin_combination'] = '1' if st == 'Combination' else '0'
        df.at[i, 'skin_normal']      = '1' if st == 'Normal' else '0'
    if sn:
        df.at[i, 'sensitivity']    = sn
        df.at[i, 'skin_sensitive'] = '1' if sn == 'Sensitive' else '0'

    src = str(r.get('source', '')).strip().lower() or 'unspecified'
    df.at[i, 'skin_type_source'] = f'manual:{src}'
    df.at[i, 'manual_source_url'] = str(r.get('source_url', '')).strip()
    added += 1

df.to_csv(OUT, index=False)
n = len(df)
print(f'merged: {added:,}')
if skipped:
    print(f'skipped {len(skipped)} rows with values outside the allowed list:')
    for pid, why in skipped[:8]:
        print('   ', pid, why)

print('\n--- COVERAGE ---')
for s, c in df['skin_type_source'].value_counts().items():
    print(f'  {s:24s} {c:6,}  ({100*c/n:5.1f}%)')
have = int(df['skin_type_source'].ne('not declared').sum())
print(f'\n  TOTAL {have:,} of {n:,} = {100*have/n:.1f}%')
print(f'  still to do: {n-have:,}')
print(f'\nwrote {OUT}')
