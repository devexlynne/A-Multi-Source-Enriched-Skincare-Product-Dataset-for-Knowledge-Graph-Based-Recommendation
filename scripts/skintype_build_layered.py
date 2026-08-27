"""
The skin type, built in layers, every value labelled by authority

Why this design
  My supervisors made three criticisms of the old skin-type column:
      1. too many sources, mixed together invisibly
      2. SkinCarisma may not be right
      3. Skinsort's suited_for sentence is not an explicit statement

  Notice that none of them says "use only one source". They say: do not hide
  which source a value came from, and do not let a weak source outrank a strong
  one. So this build keeps the coverage and fixes the actual complaint.

Usage:
    py skintype_build_layered.py
"""
import os
import re
import pandas as pd

DATASET = 'SKINCARE_DATASET.csv'
norm = lambda s: re.sub(r'[^a-z0-9]', '', str(s).lower())

df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')
df['_k'] = df['brand'].map(norm) + '|' + df['name'].map(norm)
N = len(df)
print(f'{N:,} products\n')

OUTCOLS = ['skin_type', 'sensitivity', 'universal_claim', 'skin_type_tier',
           'skin_type_authority', 'skin_type_source', 'skin_type_rule',
           'skin_type_quote', 'skin_type_url']
for c in OUTCOLS:
    df[c] = ''

UNIVERSAL = re.compile(r'\b(all skin types?|all$|every skin type|any skin type|universal)\b', re.I)
TYPES = {'dry': 'Dry', 'oil': 'Oily', 'acne': 'Oily', 'combination': 'Combination',
         'combo': 'Combination', 'normal': 'Normal'}


def n_named(t):
    t = str(t).lower()
    return sum(bool(re.search(r'\b' + w, t))
               for w in ('dry', 'oil', 'combination', 'normal', 'sensitiv'))


def parse(text):
    """any wording -> (sebum, sensitivity, universal)"""
    t = str(text).strip()
    if not t or t.lower() in ('unspecified', 'none', 'nan'):
        return '', '', ''
    if UNIVERSAL.match(t) or n_named(t) >= 4:
        return '', '', '1'
    low = t.lower()
    found = {lab for w, lab in TYPES.items() if re.search(r'\b' + w, low)}
    sens = 'Sensitive' if re.search(r'\bsensitiv', low) else ''
    if 'Dry' in found and 'Oily' in found:
        return 'Combination', sens, ''
    if 'Combination' in found:
        return 'Combination', sens, ''
    for lab in ('Oily', 'Dry', 'Normal'):
        if lab in found:
            return lab, sens, ''
    return '', sens, ''


def apply_layer(rows, tier, authority, label):
    """rows: dict _k -> (sebum, sens, uni, source, rule, quote, url). never overwrites."""
    empty = (df['skin_type'] == '') & (df['universal_claim'] == '')
    n_before = int(empty.sum())
    hits = 0
    for i in df.index[empty]:
        v = rows.get(df.at[i, '_k'])
        if not v:
            continue
        seb, sen, uni, src, rule, quote, url = v
        if not (seb or sen or uni):
            continue
        df.at[i, 'skin_type'] = seb
        df.at[i, 'sensitivity'] = sen
        df.at[i, 'universal_claim'] = uni
        df.at[i, 'skin_type_tier'] = str(tier)
        df.at[i, 'skin_type_authority'] = authority
        df.at[i, 'skin_type_source'] = src
        df.at[i, 'skin_type_rule'] = rule
        df.at[i, 'skin_type_quote'] = quote[:220]
        df.at[i, 'skin_type_url'] = url
        hits += 1
    print(f'  tier {tier}  {label:34s} filled {hits:6,}   (was {n_before:,} empty)')


# ============================================================ TIER 1a: brand sites
rows = {}
for f in ('skintype_search_results.csv', 'skintype_pass2_results.csv',
          'skintype_pass3_results.csv'):
    if not os.path.exists(f):
        continue
    r = pd.read_csv(f, low_memory=False, dtype=str).fillna('')
    r = r[(r['skin_type'] != '') | (r['universal_claim'] == '1')]
    for _, x in r.iterrows():
        k = norm(x['brand']) + '|' + norm(x['name'])
        rows.setdefault(k, (x['skin_type'], x.get('sensitivity', ''), x['universal_claim'],
                            x.get('skin_type_source', ''), x.get('skin_type_rule', ''),
                            x.get('skin_type_quote', ''), x.get('skin_type_url', '')))
print('TIER 1  manufacturer')
apply_layer(rows, 1, 'manufacturer', "the brand's own product page")

# ============================================================ TIER 1b: Amazon field
if os.path.exists('amazon_skintype.csv') and os.path.exists('acc19k_matches.csv'):
    amz = pd.read_csv('amazon_skintype.csv', dtype=str).fillna('')
    mp = pd.read_csv('acc19k_matches.csv', low_memory=False, dtype=str).fillna('')
    mp['_k'] = mp['brand'].map(norm) + '|' + mp['name'].map(norm)
    a = dict(zip(amz['asin'], amz['amazon_skin_type_raw']))
    rows = {}
    for _, x in mp.iterrows():
        raw = a.get(x['am_asin'], '')
        if not raw:
            continue
        seb, sen, uni = parse(raw)
        if seb or sen or uni:
            rows[x['_k']] = (seb, sen, uni, 'amazon.com',
                             'declared field details["Skin Type"]', raw,
                             'https://www.amazon.com/dp/' + str(x['am_asin']))
    apply_layer(rows, 1, 'manufacturer', 'Amazon declared Skin Type field')

# ============================================================ TIER 2: retailers
if os.path.exists('src_lebanese_retail.csv'):
    r = pd.read_csv('src_lebanese_retail.csv', low_memory=False, dtype=str).fillna('')
    r = r[r['skin_type'].str.strip() != '']
    rows = {}
    for _, x in r.iterrows():
        seb, sen, uni = parse(x['skin_type'])
        if seb or sen or uni:
            k = norm(x['brand_name']) + '|' + norm(x['product_name'])
            rows.setdefault(k, (seb, sen, uni, x.get('source', 'lebanese retail'),
                                'retailer skin-type field', x['skin_type'],
                                x.get('product_url', '')))
    print('\nTIER 2  retailer')
    apply_layer(rows, 2, 'retailer', 'Lebanese retail skin-type field')

# ============================================================ TIER 3: SkinCarisma
if os.path.exists('skincarisma_ALL_products.csv'):
    sc = pd.read_csv('skincarisma_ALL_products.csv', low_memory=False, dtype=str).fillna('')
    sc = sc[sc['found'] == '1'].drop_duplicates('product_id')
    pid2k = dict(zip(df['product_id'], df['_k']))
    rows = {}
    for _, x in sc.iterrows():
        k = pid2k.get(x['product_id'])
        if not k:
            continue
        dry, oily = x['sc_dry'] == '1', x['sc_oily'] == '1'
        seb = 'Combination' if (dry and oily) else 'Oily' if oily else 'Dry' if dry else 'Normal'
        sen = 'Sensitive' if x['sc_sensitive'] == '1' else 'Resistant'
        q = (f"dry {x.get('sc_dry_good','')} good / {x.get('sc_dry_bad','')} bad; "
             f"oily {x.get('sc_oily_good','')}/{x.get('sc_oily_bad','')}; "
             f"sensitive {x.get('sc_sensitive_good','')}/{x.get('sc_sensitive_bad','')}")
        rows[k] = (seb, sen, '', 'skincarisma.com',
                   'ingredient analysis, good vs bad counts', q, x.get('sc_url', ''))
    print('\nTIER 3  ingredient analysis')
    apply_layer(rows, 3, 'ingredient analysis', 'SkinCarisma good vs bad counts')

# ============================================================ TIER 4: derived
if os.path.exists('src_workbook_final.csv'):
    r = pd.read_csv('src_workbook_final.csv', low_memory=False, dtype=str).fillna('')
    r = r[(r['skin_type'].str.strip() != '') & (r['skin_type'] != 'Unspecified')]
    rows = {}
    for _, x in r.iterrows():
        seb, sen, uni = parse(x['skin_type'])
        if seb or sen or uni:
            k = norm(x['brand_name']) + '|' + norm(x['product_name'])
            rows.setdefault(k, (seb, sen, uni, 'skinsort afterUse',
                                'derived from afterUse tags (weakest tier)',
                                x['skin_type'], x.get('product_url', '')))
    print('\nTIER 4  derived, used only where nothing above exists')
    apply_layer(rows, 4, 'derived', 'Skinsort afterUse tags')

# ==================================================================== report
df = df.drop(columns=['_k'])
df.to_csv(DATASET, index=False)

seb = int((df['skin_type'] != '').sum())
sen = int((df['sensitivity'] != '').sum())
uni = int((df['universal_claim'] == '1').sum())
none = int(((df['skin_type'] == '') & (df['universal_claim'] == '')).sum())

print('\n' + '=' * 68)
print('  COVERAGE')
print(f'    sebum axis            {seb:6,}  ({100*seb/N:5.1f}%)')
print(f'    sensitivity           {sen:6,}  ({100*sen/N:5.1f}%)')
print(f'    universal claim only  {uni:6,}  ({100*uni/N:5.1f}%)')
print(f'    nothing at all        {none:6,}  ({100*none/N:5.1f}%)')

print('\n  WHERE EVERY VALUE CAME FROM')
got = df[(df['skin_type'] != '') | (df['universal_claim'] == '1')]
for t in ('1', '2', '3', '4'):
    g = got[got['skin_type_tier'] == t]
    if len(g):
        auth = g['skin_type_authority'].iloc[0]
        print(f'    tier {t}  {auth:22s}{len(g):6,}  ({100*len(g)/N:5.1f}% of catalogue)')

print('\n  WHAT A SUPERVISOR CAN FILTER TO, in one line')
for t, lab in ((1, 'manufacturer only'), (2, 'declared sources only (tier 1 + 2)'),
               (3, 'everything except the weakest tier'), (4, 'everything')):
    c = int((pd.to_numeric(df['skin_type_tier'], errors='coerce') <= t).sum())
    print(f'    tier <= {t}   {lab:36s}{c:6,}  ({100*c/N:5.1f}%)')

print('\n  SEBUM DISTRIBUTION')
for k, v in df.loc[df['skin_type'] != '', 'skin_type'].value_counts().items():
    print(f'    {k:14s}{v:6,}')

print('\n  AN EXAMPLE ROW FROM EACH TIER')
for t in ('1', '2', '3', '4'):
    g = got[got['skin_type_tier'] == t]
    if not len(g):
        continue
    x = g.iloc[0]
    print(f'\n    tier {t}')
    for c in ('brand', 'name', 'skin_type', 'sensitivity', 'skin_type_source',
              'skin_type_rule', 'skin_type_quote'):
        print(f'      {c:20s}{str(x[c])[:84]}')

df[(df['skin_type'] == '') & (df['universal_claim'] == '')][['product_id', 'brand', 'name']] \
    .to_csv('skintype_still_empty.csv', index=False)
print(f'\n  wrote skintype_still_empty.csv  ({none:,} rows)')
print('\nrebuild the workbook:  py build_dataset.py')
