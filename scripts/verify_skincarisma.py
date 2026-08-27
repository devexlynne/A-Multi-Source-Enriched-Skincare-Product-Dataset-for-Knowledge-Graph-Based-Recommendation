"""
Repair + verify the skincarisma results

Two jobs
 1. REPAIR. My scraper appended results in chunks, and each chunk only carried
    the columns that happened to be found in it, so the CSV has rows with
    different numbers of fields and pandas refuses to read it. This reads it
    line by line instead, tolerating the mess, and rebuilds a clean table.

 2. VERIFY - the part you actually asked about. "Found 4,495" only means a page
    loaded. It does NOT mean it was YOUR product, because when the direct URL
    failed the scraper fell back to site search and took the first result with
    no similarity check.

    So every match is re-checked with the thesis-wide rule:
        token_set_ratio(my brand+name, the page's URL slug) >= 95
    Same metric as the Amazon matching (Cohen 2003), same threshold logic
    (Fellegi & Sunter 1969). Below 95 is rejected and written out so you can
    read the failures yourself.

Usage:
    py verify_skincarisma.py
"""
import csv, re, sys
import pandas as pd
from rapidfuzz import fuzz

THRESHOLD = 95
# prefer the re-scraped file (fixed column schema); fall back to the original
import os
RAW = ('skincarisma_skintype_v2.csv' if os.path.exists('skincarisma_skintype_v2.csv')
       else 'skincarisma_skintype.csv')
print('reading', RAW)

# ---------------------------------------------------------------- 1. REPAIR
rows, header, bad = [], None, 0
with open(RAW, encoding='utf-8', errors='replace', newline='') as fh:
    for parts in csv.reader(fh):
        if not parts:
            continue
        if parts[0] == 'product_id':                 # a header line (repeated)
            if header is None or len(parts) > len(header):
                header = parts                       # keep the widest header
            continue
        rows.append(parts)
if header is None:
    sys.exit('could not find a header row in ' + RAW)

recs = []
for parts in rows:
    if len(parts) < 4:
        bad += 1
        continue
    recs.append(dict(zip(header, parts + [''] * (len(header) - len(parts)))))
sc = pd.DataFrame(recs).drop_duplicates('product_id')
print(f'rows recovered      : {len(sc):,}   (unreadable lines skipped: {bad})')

sc = sc[sc['sc_url'].fillna('').str.startswith('http')]
print(f'rows with a page URL: {len(sc):,}')

# ---------------------------------------------------------------- 2. VERIFY
def slug_of(url):
    tail = str(url).rstrip('/').split('/products/')[-1]
    return re.sub(r'[^a-z0-9]+', ' ', tail.lower()).strip()

def mine_of(brand, name):
    return re.sub(r'[^a-z0-9]+', ' ', f'{brand} {name}'.lower()).strip()

sc['page_slug']   = sc['sc_url'].map(slug_of)
sc['my_product']  = [mine_of(b, n) for b, n in zip(sc['brand'], sc['name'])]
sc['match_score'] = [round(fuzz.token_set_ratio(a, b))
                     for a, b in zip(sc['my_product'], sc['page_slug'])]
sc['verified']    = sc['match_score'] >= THRESHOLD

ok  = int(sc['verified'].sum())
no  = int((~sc['verified']).sum())
print('\n' + '=' * 66)
print('ARE THE MATCHES CORRECT?')
print('=' * 66)
print(f'pages the scraper found          : {len(sc):,}')
print(f'VERIFIED (score >= {THRESHOLD})           : {ok:,}  ({100*ok/len(sc):.1f}%)')
print(f'REJECTED (wrong product)         : {no:,}  ({100*no/len(sc):.1f}%)')

print('\nscore distribution:')
bins = [(100,100,'perfect'), (95,99,'verified'), (80,94,'close but rejected'),
        (50,79,'different product'), (0,49,'completely different')]
for lo, hi, lab in bins:
    c = int(((sc['match_score'] >= lo) & (sc['match_score'] <= hi)).sum())
    print(f'   {lo:3d}-{hi:3d}  {lab:22s} {c:6,}  ({100*c/len(sc):5.1f}%)')

print('\n--- 8 ACCEPTED (these look right) ---')
for _, r in sc[sc['verified']].head(8).iterrows():
    print(f"  {r['match_score']:3d} | {r['my_product'][:44]:44s} -> {r['page_slug'][:44]}")

print('\n--- 8 REJECTED (thrown out, and you can see why) ---')
for _, r in sc[~sc['verified']].sort_values('match_score').head(8).iterrows():
    print(f"  {r['match_score']:3d} | {r['my_product'][:44]:44s} -> {r['page_slug'][:44]}")

sc.to_csv('skincarisma_verified.csv', index=False)
sc[~sc['verified']].to_csv('skincarisma_rejected.csv', index=False)
print('\nwrote skincarisma_verified.csv  (all rows, with a match_score column)')
print('wrote skincarisma_rejected.csv  (only the failures, for your review)')
print(f'\n>>> USE {ok:,} PRODUCTS. Run:  py merge_skincarisma.py')
