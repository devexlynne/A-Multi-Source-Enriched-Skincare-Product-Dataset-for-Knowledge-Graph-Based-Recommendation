"""
Find which retailer sites actually carry my brands *and* publish skin type

Why a discovery tool instead of another scraper
  I have burned time on sites that turned out to be dead ends:
     Douglas       - blocked by Akamai (403), and only ~5% brand overlap
     zeinacare     - has a skin-type tag, but every value is "combination"
     Amazon        - worked, 2,351 products
     SkinCarisma   - worked, 4,452 products

  So before writing another scraper I test candidates properly and measure two
  things that decide everything:
"""
import re, json, time
import requests
import pandas as pd

SRC = 'Skincare_Reviewed_FINAL_v10.csv'
HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36'}

# Candidates chosen for the brands I still need: K-beauty (TONYMOLY, innisfree,
# Missha, Dr. Jart+), French derma (La Roche-Posay, Bioderma, Caudalie) and US
# mass market (Neutrogena, Cetaphil, CeraVe, Garnier).
# NOTE: the big chains (Ulta, Sephora, Dermstore, YesStyle, StyleKorean) run
# custom platforms with no open API, so they cannot be probed this way. Shopify
# is used mostly by INDEPENDENT retailers and direct-to-consumer brands, so the
# list below leans that way - those are the ones that can actually be read.
CANDIDATES = [
    # --- K-beauty retailers that tend to run Shopify
    'skinsider.co.uk', 'thekbeautyshop.co.uk', 'kbeauty.com', 'nudieglow.com',
    'beautybarn.in', 'www.thekoreanbeauty.co.uk', 'kollectionk.com',
    'seoulskin.co.uk', 'oo35mm.com', 'stylestory.com.au',
    # --- clean / indie beauty retailers (Shopify heavy)
    'thedetoxmarket.com', 'credobeauty.com', 'www.theskinnerd.com',
    'beautyheroes.com', 'artofsport.com', 'shopmoisturize.com',
    # --- pharmacy / derma
    'nexuscare.co', 'www.feel22.com', 'zeinacare.com',
    'skinessentials.ie', 'www.pharmacyonline.co.uk', 'www.careskin.co.uk',
    # --- broad retailers worth a try
    'www.beautybay.com', 'www.cultbeauty.co.uk', 'lookfantastic.com',
]

SKIN_WORDS = ['dry', 'oily', 'combination', 'sensitive', 'normal',
              'peau sèche', 'peau grasse', 'peau mixte', 'peau sensible']


def my_brands():
    df = pd.read_csv(SRC, low_memory=False, dtype=str)
    todo = df[df['skin_type_source'] == 'not declared']
    return {re.sub(r'[^a-z0-9]', '', str(b).lower()) for b in todo['brand'].dropna()}, len(todo)


def probe(shop, mine):
    """Pull a sample from the Shopify JSON API and measure the two things."""
    out = dict(shop=shop, shopify='no', products_sampled=0,
               my_brands_found=0, skin_values_found=0, distinct_values='', verdict='')
    got = []
    for path in ('/products.json', '/collections/all/products.json',
                 '/collections/skincare/products.json'):
        for host in (shop, shop.replace('www.', '')):
            try:
                r = requests.get(f'https://{host}{path}', params={'limit': 250},
                                 headers=HEAD, timeout=20)
                # do NOT insist on the Content-Type header - some shops send
                # text/html for JSON. Just try to parse it.
                if r.status_code == 200:
                    got = json.loads(r.text).get('products', [])
                    if got:
                        out['shopify'] = 'yes'
                        break
            except Exception:
                continue
        if got:
            break
    if not got:
        out['verdict'] = 'not Shopify / no open API'
        return out

    out['products_sampled'] = len(got)
    brands, values = set(), set()
    for p in got:
        v = re.sub(r'[^a-z0-9]', '', str(p.get('vendor', '')).lower())
        if v in mine:
            brands.add(v)
        blob = (' '.join(str(t) for t in (p.get('tags') or [])) + ' ' +
                str(p.get('body_html', ''))[:1500]).lower()
        for w in SKIN_WORDS:
            if re.search(r'\b' + re.escape(w) + r'\b(?:\s*skin)?', blob):
                values.add(w)
    out['my_brands_found']   = len(brands)
    out['skin_values_found'] = len(values)
    out['distinct_values']   = ', '.join(sorted(values))[:60]

    if out['my_brands_found'] >= 3 and out['skin_values_found'] >= 3:
        out['verdict'] = 'PROMISING - worth scraping'
    elif out['skin_values_found'] <= 1:
        out['verdict'] = 'no usable skin type (one value or none)'
    elif out['my_brands_found'] == 0:
        out['verdict'] = 'does not carry my brands'
    else:
        out['verdict'] = 'weak'
    return out


def main():
    mine, n = my_brands()
    print(f'brands still needing a skin type: {len(mine):,}  ({n:,} products)\n')
    rows = []
    for shop in CANDIDATES:
        print(f'testing {shop:32s} ', end='', flush=True)
        r = probe(shop, mine)
        rows.append(r)
        print(f"{r['shopify']:4s} brands={r['my_brands_found']:3d} "
              f"values={r['skin_values_found']}  {r['verdict']}")
        time.sleep(0.6)

    res = pd.DataFrame(rows).sort_values(
        ['my_brands_found', 'skin_values_found'], ascending=False)
    res.to_csv('site_discovery_results.csv', index=False)

    print('\n' + '=' * 74)
    print('WORTH SCRAPING (carries my brands AND has real skin-type variety)')
    print('=' * 74)
    good = res[res['verdict'].str.startswith('PROMISING')]
    print(good.to_string(index=False) if len(good) else
          '  none of these - tell me and I will test another list')
    print('\nwrote site_discovery_results.csv')
    print('send me that file and I will write the scraper for whatever scored well')


if __name__ == '__main__':
    main()
