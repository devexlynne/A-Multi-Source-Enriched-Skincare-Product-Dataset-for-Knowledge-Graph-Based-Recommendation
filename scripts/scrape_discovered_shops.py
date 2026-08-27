"""
Scrape skin type from the shops that passed discovery

Why these six
  The discovery run tested 27 candidates on two questions that actually matter:
  does the shop carry MY remaining brands, and does its skin-type field have
  MORE THAN ONE value? (That second test is what zeinacare failed the first
  time round - a tag that always says "combination" carries no information.)

  Six passed:
     nudieglow.com        26 of my brands, 5 skin-type values
     oo35mm.com           26 brands, 5 values
     zeinacare.com        12 brands, 4 values
     www.theskinnerd.com   8 brands, 5 values
     www.feel22.com        6 brands, 5 values
     thedetoxmarket.com    4 brands, 5 values

How it works
  Each is Shopify, so there is a public JSON endpoint - a documented API, not
  scraping. It pulls every product, reads the skin type out of the tags and the
  product description, then matches to my catalogue with the SAME method used
  everywhere else in this thesis:
        block by brand            (Papadakis 2020)
        score with token_set_ratio (Cohen 2003)
        accept at >= 95            (Fellegi & Sunter 1969)

Usage:
    py scrape_discovered_shops.py      (~5 minutes, no browser needed)
"""
import re, json, time
import pandas as pd
import requests
from rapidfuzz import fuzz, process

SRC   = 'Skincare_Reviewed_FINAL_v10.csv'
OUT   = 'Skincare_Reviewed_FINAL_v12.csv'
RAW   = 'discovered_shops_products.csv'
HEAD  = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'}
PAUSE = 0.5

# ordered best-first, so a better shop wins if two describe the same product
SHOPS = ['nudieglow.com', 'oo35mm.com', 'zeinacare.com',
         'www.theskinnerd.com', 'www.feel22.com', 'thedetoxmarket.com']


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def read_skin_type(tags, body, title):
    """Find the skin type in the tags first (most reliable), then the
    description. Returns None when the shop says nothing - a blank is an
    honest answer and better than a guess."""
    tagtext = ' | '.join(str(t).lower() for t in (tags or []))
    body    = re.sub(r'<[^>]+>', ' ', str(body or '')).lower()[:2500]
    f = dict(normal=0, dry=0, oily=0, combination=0, sensitive=0)
    found = False

    # 1. tags - "skin-type-dry", "dry skin", "for oily skin"
    for key, pat in (('dry',         r'skin-type-dry|\bdry skin\b'),
                     ('oily',        r'skin-type-oily|\boily skin\b|skin-type-acne|acne-prone'),
                     ('combination', r'skin-type-combination|\bcombination skin\b'),
                     ('sensitive',   r'skin-type-sensitive|\bsensitive skin\b'),
                     ('normal',      r'skin-type-normal|\bnormal skin\b')):
        if re.search(pat, tagtext):
            f[key] = 1; found = True
    if re.search(r'\ball skin type', tagtext):
        for k in f: f[k] = 1
        found = True

    # 2. only if the tags said nothing, look at the description
    if not found:
        for key, pat in (('dry',         r'\bfor dry skin\b|suitable for dry'),
                         ('oily',        r'\bfor oily skin\b|suitable for oily|acne-prone skin'),
                         ('combination', r'\bfor combination skin\b'),
                         ('sensitive',   r'\bfor sensitive skin\b|suitable for sensitive'),
                         ('normal',      r'\bfor normal skin\b')):
            if re.search(pat, body):
                f[key] = 1; found = True
        if re.search(r'\ball skin types?\b', body):
            for k in f: f[k] = 1
            found = True
    return f if found else None


def pull(shop):
    rows = []
    for page in range(1, 41):                     # 40 x 250 = up to 10,000
        ok = False
        for path in ('/products.json', '/collections/all/products.json'):
            try:
                r = requests.get(f'https://{shop}{path}',
                                 params={'limit': 250, 'page': page},
                                 headers=HEAD, timeout=25)
                if r.status_code == 200:
                    prods = json.loads(r.text).get('products', [])
                    ok = True
                    break
            except Exception:
                continue
        if not ok or not prods:
            break
        for p in prods:
            st = read_skin_type(p.get('tags'), p.get('body_html'), p.get('title'))
            if not st:
                continue
            rows.append(dict(shop=shop, brand=p.get('vendor') or '',
                             name=p.get('title') or '',
                             **{f'sh_{k}': v for k, v in st.items()}))
        print(f'   page {page}: {len(prods)} products, {len(rows)} with a skin type')
        time.sleep(PAUSE)
    return rows


def main():
    print('=== PULLING FROM THE SIX SHOPS ===')
    allrows = []
    for s in SHOPS:
        print(f'\n{s}')
        try:
            got = pull(s)
        except Exception as e:
            print('   failed:', str(e)[:60]); continue
        print(f'   -> {len(got):,} products carrying a skin type')
        allrows += got
    shop_df = pd.DataFrame(allrows).drop_duplicates(['shop', 'brand', 'name'])
    shop_df.to_csv(RAW, index=False)
    print(f'\ntotal shop products with a skin type: {len(shop_df):,}')
    if shop_df.empty:
        return

    # ---------------- match to my catalogue, brand-blocked ----------------
    print('\n=== MATCHING TO MY PRODUCTS ===')
    df = pd.read_csv(SRC, low_memory=False, dtype=str)
    todo = df['skin_type_source'].eq('not declared')
    print(f'products needing a skin type: {todo.sum():,}')

    idx = {}
    for _, r in shop_df.iterrows():
        idx.setdefault(norm(r['brand']), []).append(r)
    print(f'shop brands available: {len(idx):,}')

    filled = 0
    for i in df.index[todo]:
        row = df.loc[i]
        cands = idx.get(norm(row['brand']), [])
        if not cands:
            continue
        names = [str(c['name']) for c in cands]
        hit = process.extractOne(str(row['name']), names, scorer=fuzz.token_set_ratio)
        if not hit or hit[1] < 95:                # the thesis-wide threshold
            continue
        c = cands[hit[2]]
        dry  = str(c['sh_dry'])  == '1'
        oily = str(c['sh_oily']) == '1'
        sens = str(c['sh_sensitive']) == '1'
        comb = str(c['sh_combination']) == '1' or (dry and oily)
        df.at[i, 'skin_dry']         = '1' if dry else '0'
        df.at[i, 'skin_oily']        = '1' if oily else '0'
        df.at[i, 'skin_sensitive']   = '1' if sens else '0'
        df.at[i, 'skin_combination'] = '1' if comb else '0'
        df.at[i, 'skin_normal']      = '1' if str(c['sh_normal']) == '1' else '0'
        df.at[i, 'skin_type']   = ('Combination' if comb else 'Oily' if oily
                                   else 'Dry' if dry else 'Normal')
        df.at[i, 'sensitivity'] = 'Sensitive' if sens else 'Resistant'
        df.at[i, 'skin_type_source'] = f"declared:{c['shop']}"
        df.at[i, 'shop_match_score'] = hit[1]
        filled += 1

    df.to_csv(OUT, index=False)
    n = len(df)
    print(f'\nmatched and filled: {filled:,}')
    print('\n--- COVERAGE ---')
    for s, c in df['skin_type_source'].value_counts().items():
        print(f'  {s:26s} {c:6,}  ({100*c/n:5.1f}%)')
    have = int(df['skin_type_source'].ne('not declared').sum())
    print(f'\n  TOTAL {have:,} of {n:,} = {100*have/n:.1f}%')
    print(f'  still blank: {n-have:,}')
    print(f'\nwrote {OUT}')


if __name__ == '__main__':
    main()
