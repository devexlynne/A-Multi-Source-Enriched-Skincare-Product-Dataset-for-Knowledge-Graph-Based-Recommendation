"""
Tidy up. two small fixes, no search credits spent.

FIX 1.  POSHMARK IS NOT A RETAILER.

  5 products were labelled tier 2 because they were found on poshmark.com.
  Poshmark is a secondhand resale site where the description is written by
  whoever is selling their used bottle, not by the brand and not by a shop
  with a supplier relationship. That is a stranger's opinion in a tier meant
  for shops. Those 5 are demoted to tier 4 so they are never counted in the
  headline figure. Their value and their link stay, so coverage does not move.

FIX 2.  RECOVER THE MISSING QUOTES.

Usage:
    py cleanup_and_quotes.py
"""
import re
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

DATASET = 'SKINCARE_DATASET.csv'
WORKERS = 8
TIMEOUT = 12

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'}

RESALE = re.compile(r'(poshmark|mercari|depop|vinted|carousell|craigslist|'
                    r'facebook|offerup|letgo)', re.I)

TAG = re.compile(r'<[^>]{0,400}>')
JUNK = re.compile(r'(class=|id=|href=|style=|</|/>)', re.I)

# the sentence we want must mention the skin type this row already has
WORD = {'Dry': r'dry', 'Oily': r'oily|acne|oil', 'Combination': r'combination|combo',
        'Normal': r'normal', 'All': r'all skin types?|every skin type|any skin type'}


def readable(q):
    q = re.sub(r'\s+', ' ', TAG.sub(' ', str(q))).strip(' .|•"\'>-')
    if JUNK.search(q):
        return ''
    letters = len(re.findall(r'[a-zA-Z]', q))
    if letters < 20 or letters < 0.6 * max(len(q), 1):
        return ''
    return q[:220]


def sentences(html):
    flat = re.sub(r'\s+', ' ', TAG.sub(' ', re.sub(
        r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', html)))
    return re.split(r'(?<=[.!?])\s+|\s*\|\s*|\s*•\s*', flat)


df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')

# ---------------------------------------------------------------- fix 1
mask = df['skin_type_source'].str.contains(RESALE, na=False) & \
       df['skin_type_tier'].isin(['1', '2'])
n_resale = int(mask.sum())
df.loc[mask, 'skin_type_tier'] = '4'
df.loc[mask, 'skin_type_authority'] = 'resale listing, written by a private seller'
print(f'fix 1  demoted {n_resale} resale-site rows out of the retailer tier')
if n_resale:
    for _, r in df[mask].head(5).iterrows():
        print(f'          {r["brand"][:20]:20s} {r["name"][:40]:40s} {r["skin_type_source"]}')

# ---------------------------------------------------------------- fix 2
need = df[(pd.to_numeric(df['skin_type_tier'], errors='coerce') <= 2) &
          (df['skin_type_quote'] == '') & (df['skin_type_url'] != '') &
          (df['skin_type'] != '')]
print(f'\nfix 2  {len(need):,} strong rows have a link but no readable quote')
print('       re-opening those pages. no search credits are used.\n')

S = requests.Session()
S.headers.update(HEAD)
lock = threading.Lock()
found = {}
n = [0]


def grab(i, url, want):
    pat = re.compile(WORD.get(want, re.escape(str(want).lower())), re.I)
    try:
        r = S.get(url, timeout=TIMEOUT)
        if r.status_code != 200:
            return
        best = ''
        for s in sentences(r.text):
            if 'skin' not in s.lower() or not pat.search(s):
                continue
            c = readable(s)
            if c and (not best or len(c) < len(best)):
                best = c            # the shortest clean sentence reads best
        if best:
            with lock:
                found[i] = best
    except Exception:
        pass
    finally:
        with lock:
            n[0] += 1
            if n[0] % 100 == 0:
                print(f'   {n[0]:,}/{len(need):,}   recovered {len(found):,}', flush=True)


with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = [ex.submit(grab, i, df.at[i, 'skin_type_url'], df.at[i, 'skin_type'])
            for i in need.index]
    for f in as_completed(futs):
        pass

for i, q in found.items():
    df.at[i, 'skin_type_quote'] = q

df.to_csv(DATASET, index=False)

# ---------------------------------------------------------------- report
filled = int((df['skin_type'] != '').sum())
t12 = df[pd.to_numeric(df['skin_type_tier'], errors='coerce') <= 2]
q12 = int((t12['skin_type_quote'] != '').sum())

print('\n' + '=' * 62)
print(f'  quotes recovered                {len(found):,} of {len(need):,}')
print(f'  strong rows (tier 1 or 2)       {len(t12):,}')
print(f'    of those, with a quote        {q12:,}  ({100*q12/max(len(t12),1):.1f}%)')
print(f'    with a link but no quote      {len(t12)-q12:,}')
print(f'  total rows with a skin type     {filled:,}   (unchanged)')
if found:
    print('\n  EXAMPLES OF WHAT WAS RECOVERED')
    for i in list(found)[:5]:
        print(f'    {df.at[i,"brand"][:18]:18s} {df.at[i,"name"][:32]:32s} -> {df.at[i,"skin_type"]}')
        print(f'       {df.at[i,"skin_type_source"]}  "{found[i][:90]}"')
print('\nnow run:  py build_dataset.py')
