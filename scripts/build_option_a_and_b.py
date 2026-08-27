"""
Build the two options for the supervisor meeting

The question for the meeting is: where should the skin type come from?

  OPTION A - MIXED SOURCES  (what i built first)
     take the strongest available evidence per product:
        manufacturer declaration  >  retailer  >  ingredient analysis  >  manual
     PRO  every value is the best evidence that exists for THAT product
     CON  the column mixes definitions, so two products may not be comparable

  OPTION B - SINGLE SOURCE  (SkinCarisma only)
     take every product's skin type from one place, computed the same way
     PRO  higher coverage AND every product comparable to every other
     CON  loses the manufacturer-declared evidence from the main column

Both are written out in full so the doctors can see the real data, not a summary.
Nothing is deleted - Option B keeps the Amazon values in a separate column so
they can still be used for validation.

Usage:
    py build_option_a_and_b.py
"""
import re
import pandas as pd

A_SRC = 'Skincare_Reviewed_FINAL_v15.csv'          # option A, already built
SC    = 'skincarisma_ALL_products.csv'             # every product looked up
OUT_A = 'OPTION_A_mixed_sources.csv'
OUT_B = 'OPTION_B_single_source.csv'
CMP   = 'OPTIONS_A_vs_B_comparison.xlsx'

df = pd.read_csv(A_SRC, low_memory=False, dtype=str)
sc = pd.read_csv(SC, low_memory=False, dtype=str)
sc = sc[sc['found'] == '1'].drop_duplicates('product_id')
n = len(df)
print(f'products {n:,} | found on SkinCarisma {len(sc):,} ({100*len(sc)/n:.1f}%)')

# ============================================================ OPTION A
a = df.copy()
a['OPTION'] = 'A - mixed sources'
a.to_csv(OUT_A, index=False)

# ============================================================ OPTION B
b = df.copy()
b['OPTION'] = 'B - single source (SkinCarisma)'

# keep the Amazon evidence, but move it OUT of the main column so it can still
# be used for validation without defining the variable
b = b.rename(columns={'skin_type': 'skin_type_MIXED',
                      'sensitivity': 'sensitivity_MIXED',
                      'skin_type_source': 'skin_type_source_MIXED'})

s = sc.set_index('product_id')
new_type, new_sens, new_src = [], [], []
for _, r in b.iterrows():
    pid = r['product_id']
    if pid in s.index:
        row = s.loc[pid]
        dry  = str(row.get('sc_dry', '')) == '1'
        oily = str(row.get('sc_oily', '')) == '1'
        sens = str(row.get('sc_sensitive', '')) == '1'
        if dry and oily:  t = 'Combination'
        elif oily:        t = 'Oily'
        elif dry:         t = 'Dry'
        else:             t = 'Normal'
        new_type.append(t)
        new_sens.append('Sensitive' if sens else 'Resistant')
        new_src.append('derived:skincarisma')
    else:
        new_type.append(''); new_sens.append(''); new_src.append('not found on SkinCarisma')
b['skin_type'] = new_type
b['sensitivity'] = new_sens
b['skin_type_source'] = new_src

# carry the SkinCarisma detail so the doctors can see HOW each call was made
for c in ('sc_dry_good','sc_dry_bad','sc_oily_good','sc_oily_bad',
          'sc_sensitive_good','sc_sensitive_bad','sc_comedogenic','sc_url'):
    if c in sc.columns:
        b[c] = b['product_id'].map(dict(zip(sc['product_id'], sc[c])))
b.to_csv(OUT_B, index=False)

# ============================================================ COMPARISON
def cov(frame, col):
    return int(frame[col].fillna('').ne('').sum())

rows = [
 ['Products in the dataset', n, n],
 ['Sebum axis filled (dry/normal/oily/combination)',
  f"{cov(a,'skin_type'):,} ({100*cov(a,'skin_type')/n:.1f}%)",
  f"{cov(b,'skin_type'):,} ({100*cov(b,'skin_type')/n:.1f}%)"],
 ['Sensitivity axis filled',
  f"{cov(a,'sensitivity'):,} ({100*cov(a,'sensitivity')/n:.1f}%)",
  f"{cov(b,'sensitivity'):,} ({100*cov(b,'sensitivity')/n:.1f}%)"],
 ['Number of different sources in the column', '6', '1'],
 ['Are two products comparable to each other?',
  'NOT ALWAYS - a marketing claim may be compared against an ingredient analysis',
  'YES - every value produced by the same method'],
 ['Manufacturer-declared evidence',
  'IN the main column (1,600 products)',
  'kept SEPARATELY for validation, not in the main column'],
 ['"All skin types" handling', 'universal_claim column, blank skin type',
  'universal_claim column, blank skin type'],
 ['Products with no value at all',
  f"{n - cov(a,'skin_type'):,}", f"{n - cov(b,'skin_type'):,}"],
]
comp = pd.DataFrame(rows, columns=['Measure', 'OPTION A (mixed)', 'OPTION B (single source)'])

# where do the two options actually differ?
both = a[['product_id','brand','name']].copy()
both['A_skin_type'] = a['skin_type'].fillna('')
both['A_source']    = a['skin_type_source'].fillna('')
both['B_skin_type'] = b['skin_type'].fillna('')
both['B_source']    = b['skin_type_source'].fillna('')
both['SAME?']       = (both['A_skin_type'] == both['B_skin_type']).map({True:'same', False:'DIFFERENT'})
diff = both[both['SAME?'] == 'DIFFERENT']

agree_pct = 100 * (both['SAME?'] == 'same').mean()
summary = pd.DataFrame([
 ['Products where A and B give the SAME skin type', f"{(both['SAME?']=='same').sum():,} ({agree_pct:.1f}%)"],
 ['Products where they DIFFER', f"{len(diff):,} ({100-agree_pct:.1f}%)"],
 ['', ''],
 ['THE DECISION FOR THE MEETING', 'Which column should be the primary skin type?'],
 ['My reading', 'Option B: higher coverage AND internal consistency. Amazon stays as a validation set, where agreement is 49.6-55.2% (n=268).'],
 ['But', 'Option A keeps manufacturer evidence in the main column, which some would argue is the stronger authority per product.'],
], columns=['Point','Detail'])

with pd.ExcelWriter(CMP, engine='openpyxl') as w:
    comp.to_excel(w, sheet_name='A vs B at a glance', index=False)
    summary.to_excel(w, sheet_name='Where they differ', index=False)
    diff.head(3000).to_excel(w, sheet_name='Differences (first 3000)', index=False)
    a.head(2000).to_excel(w, sheet_name='OPTION A sample', index=False)
    b.head(2000).to_excel(w, sheet_name='OPTION B sample', index=False)
    from openpyxl.styles import Font, PatternFill, Alignment
    for nm in w.sheets:
        ws = w.sheets[nm]
        for c in ws[1]:
            c.fill = PatternFill('solid', fgColor='584A7A')
            c.font = Font(bold=True, color='FFFFFF')
            c.alignment = Alignment(vertical='center', wrap_text=True)
        for col in list(ws.columns)[:40]:
            L = max((len(str(x.value)) for x in col[:60] if x.value), default=12)
            ws.column_dimensions[col[0].column_letter].width = min(max(L+2, 14), 60)
        ws.freeze_panes = 'A2'

print(f'\nwrote {OUT_A}, {OUT_B}, {CMP}')
print(comp.to_string(index=False))
print(f"\nA and B give the same skin type for {agree_pct:.1f}% of products")
