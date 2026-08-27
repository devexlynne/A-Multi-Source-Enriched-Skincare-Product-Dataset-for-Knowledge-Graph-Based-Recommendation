"""
MERGE SKINCARISMA  -  with match verification

Why the verification step matters
  The scraper found a page for 4,495 products, but "found a page" is not the
  same as "found the RIGHT page". It tried two things:

    1. a direct URL built from brand+name   -> safe, the whole name had to match
    2. if that 404'd, a site SEARCH and it took the first result -> RISKY,
       because a search for "Hydrating Cleanser" can return a different brand's
       hydrating cleanser and the script would have accepted it.

  So before trusting any of it I re-check every match the same way I check the
  Amazon matches, using the thesis-wide rule:

        token_set_ratio(my brand+name, the URL slug) >= 95      (Cohen 2003)
        accept only above the threshold                (Fellegi & Sunter 1969)

  Anything below 95 is reported but NOT used. That keeps one consistent
  standard of evidence across the whole thesis.

PRIORITY, never overwritten downwards:
    declared:amazon       a manufacturer stated it
    derived:skincarisma   an independent expert site estimated it from ingredients
    not declared          nobody said anything, left blank
"""
import re
import pandas as pd
from rapidfuzz import fuzz

THRESHOLD = 95            # the same cut-off used everywhere else in the thesis

df = pd.read_csv('Skincare_Reviewed_FINAL_v6.csv', low_memory=False, dtype=str)
# read the REPAIRED + already-scored file produced by verify_skincarisma.py
try:
    sc = pd.read_csv('skincarisma_verified.csv', low_memory=False, dtype=str)
except FileNotFoundError:
    raise SystemExit('Run  py verify_skincarisma.py  first - it repairs the '
                     'raw CSV and scores every match.')
sc = sc[sc['sc_url'].fillna('').ne('')].drop_duplicates('product_id')
print(f'pages found by the scraper : {len(sc):,}')


def slug_of(url):
    """The product part of a Skincarisma URL, turned back into words.
    .../products/cosrx/cosrx-advanced-snail-92-all-in-one-cream
        -> 'cosrx advanced snail 92 all in one cream'"""
    tail = str(url).rstrip('/').split('/products/')[-1]
    return re.sub(r'[^a-z0-9]+', ' ', tail.lower()).strip()


def mine_of(brand, name):
    return re.sub(r'[^a-z0-9]+', ' ', f'{brand} {name}'.lower()).strip()


# ---- VERIFY every scraped match ------------------------------------------
sc['_slug']  = sc['page_slug']  if 'page_slug'  in sc.columns else sc['sc_url'].map(slug_of)
sc['_mine']  = sc['my_product'] if 'my_product' in sc.columns else \
               [mine_of(b, n) for b, n in zip(sc['brand'], sc['name'])]
sc['_score'] = pd.to_numeric(sc['match_score'], errors='coerce').fillna(0).astype(int) \
               if 'match_score' in sc.columns else \
               [round(fuzz.token_set_ratio(a, b)) for a, b in zip(sc['_mine'], sc['_slug'])]
sc['_ok']    = sc['_score'] >= THRESHOLD

ok, bad = int(sc['_ok'].sum()), int((~sc['_ok']).sum())
print(f'verified at token_set_ratio >= {THRESHOLD} : {ok:,}')
print(f'rejected as probably the wrong product     : {bad:,}')
print('\nexamples of REJECTED matches (kept out of the dataset):')
for _, r in sc[~sc['_ok']].head(5).iterrows():
    print(f"   score {r['_score']:3d} | mine: {r['_mine'][:48]:48s} | page: {r['_slug'][:48]}")
sc[~sc['_ok']].to_csv('skincarisma_rejected_matches.csv', index=False)

good = sc[sc['_ok']].set_index('product_id')

# ---- fold the verified ones in -------------------------------------------
filled = 0
for i, row in df.iterrows():
    if row['skin_type_source'] != 'not declared':
        continue                                     # never overwrite Amazon
    pid = row['product_id']
    if pid not in good.index:
        continue
    r = good.loc[pid]
    if all(pd.isna(r.get(c)) for c in ('sc_dry', 'sc_oily', 'sc_sensitive')):
        continue
    dry  = str(r.get('sc_dry', '')) == '1'
    oily = str(r.get('sc_oily', '')) == '1'
    sens = str(r.get('sc_sensitive', '')) == '1'
    df.at[i, 'skin_dry']         = '1' if dry else '0'
    df.at[i, 'skin_oily']        = '1' if oily else '0'
    df.at[i, 'skin_sensitive']   = '1' if sens else '0'
    df.at[i, 'skin_combination'] = '1' if (dry and oily) else '0'
    com = pd.to_numeric(r.get('sc_comedogenic'), errors='coerce')
    df.at[i, 'skin_normal']      = '0' if (pd.notna(com) and com >= 3) else '1'
    parts = (['Combination'] if (dry and oily)
             else [p for p, c in (('Oily', oily), ('Dry', dry)) if c])
    if sens: parts.append('Sensitive')
    df.at[i, 'skin_type']         = '/'.join(parts) if parts else 'Normal'
    df.at[i, 'skin_type_source']  = 'derived:skincarisma'
    df.at[i, 'skincarisma_url']   = r['sc_url']
    df.at[i, 'skincarisma_score'] = r['_score']
    filled += 1

df.to_csv('Skincare_Reviewed_FINAL_v7.csv', index=False)

n = len(df)
print('\n' + '=' * 60)
print('COVERAGE AFTER MERGING SKINCARISMA')
print('=' * 60)
for src, cnt in df['skin_type_source'].value_counts().items():
    print(f'  {src:24s} {cnt:6,}  ({100*cnt/n:.1f}%)')
have = int(df['skin_type_source'].ne('not declared').sum())
print(f'\nTOTAL WITH A SKIN TYPE : {have:,} of {n:,} = {100*have/n:.1f}%')
print(f'still honestly blank   : {n-have:,} ({100*(n-have)/n:.1f}%)')
print('\nwrote Skincare_Reviewed_FINAL_v7.csv')
print('wrote skincarisma_rejected_matches.csv (the ones the check threw out)')
