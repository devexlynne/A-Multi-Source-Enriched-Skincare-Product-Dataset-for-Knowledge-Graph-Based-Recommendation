"""
SKIN TYPE FROM LEBANESE (AND OTHER) SHOPIFY SHOPS  -  the easy source

Why this is the best-value scraper i have written
  Douglas blocks automated access at the CDN (Akamai, HTTP 403). These shops do
  the opposite: they run Shopify, and every Shopify store exposes a public JSON
  endpoint:

        https://<shop>/collections/all/products.json?limit=250&page=N

  That is not scraping HTML at all - it is a documented, structured API. No bot
  protection, no parsing guesswork, 250 products per request.
"""
import re, time, json
import requests
import pandas as pd

# Lebanese + regional Shopify shops. Add any others you find: the only test is
# whether  https://<shop>/collections/all/products.json  returns JSON.
SHOPS = [
    'zeinacare.com',
    'www.beesline.com',
    'lebanesebeauty.com',
    'www.sohatipharmacy.com',
    'pharmacyplus.com.lb',
    'www.bassilpharma.com',
    'nexuscare.co',
    'www.feel22.com',
    'daoukpharmacy.com',
]

HEAD  = {'User-Agent': 'Mozilla/5.0 (academic thesis data collection)'}
PAUSE = 0.8
MAX_PAGES = 40              # 40 x 250 = up to 10,000 products per shop


def skin_types_from_tags(tags):
    """Read the skin type out of a Shopify tag list.
    Handles the two patterns seen live: 'skin-type-combination' and
    'all skin type'."""
    joined = ' | '.join(str(t).lower() for t in tags)
    f = dict(normal=0, dry=0, oily=0, combination=0, sensitive=0)
    hit = False
    if re.search(r'\ball skin type', joined):
        for k in f: f[k] = 1
        hit = True
    for key, pat in (('dry', r'skin-type-dry|\bdry skin\b'),
                     ('oily', r'skin-type-oily|\boily skin\b|skin-type-acne'),
                     ('combination', r'skin-type-combination|\bcombination skin\b'),
                     ('sensitive', r'skin-type-sensitive|\bsensitive skin\b'),
                     ('normal', r'skin-type-normal|\bnormal skin\b')):
        if re.search(pat, joined):
            f[key] = 1
            hit = True
    return (f, joined) if hit else (None, joined)


def fetch_shop(shop):
    rows = []
    for page in range(1, MAX_PAGES + 1):
        url = f'https://{shop}/collections/all/products.json'
        try:
            r = requests.get(url, params={'limit': 250, 'page': page},
                             headers=HEAD, timeout=30)
        except requests.RequestException as e:
            print(f'   request failed: {str(e)[:50]}'); break
        if r.status_code != 200:
            print(f'   status {r.status_code} on page {page}'); break
        try:
            prods = r.json().get('products', [])
        except json.JSONDecodeError:
            print('   not a Shopify JSON endpoint'); break
        if not prods:
            break
        for p in prods:
            f, tagtext = skin_types_from_tags(p.get('tags') or [])
            rows.append(dict(
                shop=shop,
                brand=(p.get('vendor') or '').strip(),
                name=(p.get('title') or '').strip(),
                product_type=p.get('product_type') or '',
                tags=tagtext[:200],
                has_skin_type=1 if f else 0,
                sh_normal=f['normal'] if f else '',
                sh_dry=f['dry'] if f else '',
                sh_oily=f['oily'] if f else '',
                sh_combination=f['combination'] if f else '',
                sh_sensitive=f['sensitive'] if f else '',
            ))
        print(f'   page {page}: {len(prods)} products (running total {len(rows)})')
        time.sleep(PAUSE)
    return rows


def main():
    allrows = []
    for shop in SHOPS:
        print(f'\n=== {shop}')
        try:
            got = fetch_shop(shop)
        except Exception as e:
            print('   skipped:', str(e)[:60]); continue
        if got:
            withst = sum(r['has_skin_type'] for r in got)
            print(f'   -> {len(got):,} products, {withst:,} carry a skin type')
            allrows += got
        else:
            print('   -> nothing (not Shopify, or the endpoint is closed)')

    out = pd.DataFrame(allrows).drop_duplicates(['shop', 'brand', 'name'])
    out.to_csv('lebanese_shopify_skintype.csv', index=False)
    print(f'\nDONE. {len(out):,} products total -> lebanese_shopify_skintype.csv')
    if not out.empty:
        st = out[out['has_skin_type'] == 1]
        print(f'with a declared skin type: {len(st):,}')
        print(f'distinct brands: {out["brand"].nunique():,}')
        print('\ntop brands carrying a skin type:')
        print(st['brand'].value_counts().head(15).to_string())
        print('\nnext: py merge_shopify.py')


if __name__ == '__main__':
    main()
