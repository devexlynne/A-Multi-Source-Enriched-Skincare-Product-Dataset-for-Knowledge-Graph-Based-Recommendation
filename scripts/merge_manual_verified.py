"""
Merge the manually verified 730

What lynne did by hand
  730 products that no automated source could label. Worked brand by brand from
  named sources, each with an evidence link.

  Result:  447 filled (61%)   283 "Not stated" (39%)
  Of the 447, 282 say "All" and 165 give a specific skin type.

How each value is treated
  "All"          -> universal_claim = 1, skin_type BLANK
                    (Vendruscolo et al. 2025: "all skin types" is a tolerance
                    testing claim, not a position on the sebum axis)
  "Not stated"   -> stays blank, source recorded as 'searched:none found'
                    This is a REAL result: it means a human looked and no named
                    source publishes a skin type for this product.
  A real type    -> written to skin_type, source 'manual:verified'
  Multi-value    -> "Normal, Dry, Combination" sets each flag, and the readable
                    label follows the same rule as everywhere else
"""
import re
import pandas as pd

SRC  = 'Skincare_Reviewed_FINAL_v13.csv'
WORK = '../../uploads/Skin_Type_VERIFIED_FINAL_730.xlsx'
OUT  = 'Skincare_Reviewed_FINAL_v14.csv'

df = pd.read_csv(SRC, low_memory=False, dtype=str)
w  = pd.read_excel(WORK, dtype=str).fillna('')
print(f'dataset {len(df):,} products | manual sheet {len(w):,} rows')

for c in ('universal_claim', 'sensitivity', 'skin_type'):
    if c not in df.columns:
        df[c] = ''

by_id = w.set_index('product_id')
FLAGS = {'dry': 'skin_dry', 'oily': 'skin_oily', 'normal': 'skin_normal',
         'combination': 'skin_combination'}

n_type = n_uni = n_none = n_sens = 0
for i, row in df.iterrows():
    pid = str(row['product_id'])
    if pid not in by_id.index:
        continue
    r = by_id.loc[pid]
    st  = str(r.get('skin_type', '')).strip()
    sen = str(r.get('sensitivity', '')).strip()
    link = str(r.get('evidence_link', '')).strip()

    # ---------- the sebum axis ----------
    if st.lower() == 'all':
        # a universal claim, NOT a skin type - kept in its own column
        df.at[i, 'universal_claim']  = '1'
        df.at[i, 'skin_type']        = ''
        for f in FLAGS.values(): df.at[i, f] = ''
        df.at[i, 'skin_type_source'] = 'claim:universal(manual)'
        n_uni += 1
    elif st.lower() in ('not stated', 'not found', ''):
        # a human searched and found nothing. that IS the finding.
        df.at[i, 'skin_type_source'] = 'searched:none found'
        n_none += 1
    else:
        parts = [p.strip().lower() for p in st.split(',') if p.strip()]
        for key, col in FLAGS.items():
            df.at[i, col] = '1' if key in parts else '0'
        # readable label: combination wins, else oily/dry, else normal
        if 'combination' in parts or ('dry' in parts and 'oily' in parts):
            lab = 'Combination'
        elif 'oily' in parts: lab = 'Oily'
        elif 'dry' in parts:  lab = 'Dry'
        elif 'normal' in parts: lab = 'Normal'
        else: lab = ''
        df.at[i, 'skin_type']        = lab
        df.at[i, 'skin_type_source'] = 'manual:verified'
        n_type += 1

    # ---------- the sensitivity axis (independent of the above) ----------
    if sen.lower() == 'sensitive':
        df.at[i, 'sensitivity']    = 'Sensitive'
        df.at[i, 'skin_sensitive'] = '1'
        n_sens += 1
    elif sen.lower() in ('resistant',):
        df.at[i, 'sensitivity']    = 'Resistant'
        df.at[i, 'skin_sensitive'] = '0'

    if link and link.lower() != 'open evidence':
        df.at[i, 'manual_evidence_url'] = link

df.to_csv(OUT, index=False)

n = len(df)
print(f'\nmerged from the manual sheet:')
print(f'  specific skin type      {n_type:5,}')
print(f'  universal claim ("All")  {n_uni:5,}')
print(f'  searched, none found     {n_none:5,}')
print(f'  sensitivity recorded     {n_sens:5,}')

print('\n--- COVERAGE ---')
for s, c in df['skin_type_source'].value_counts().items():
    print(f'  {s:30s} {c:6,}  ({100*c/n:5.1f}%)')
seb  = int(df['skin_type'].fillna('').ne('').sum())
sens = int(df['sensitivity'].fillna('').ne('').sum())
uni  = int(df['universal_claim'].fillna('').eq('1').sum())
print(f'\n  sebum axis filled      {seb:6,}  ({100*seb/n:.1f}%)')
print(f'  sensitivity filled     {sens:6,}  ({100*sens/n:.1f}%)')
print(f'  universal claim        {uni:6,}  ({100*uni/n:.1f}%)')
print(f'\nwrote {OUT}')
