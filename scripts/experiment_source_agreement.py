"""
Experiment: do the skin-type sources agree with each other?

The question
  My dataset now carries skin types from three kinds of source:
      declared:amazon        a manufacturer stated it
      declared:<retailer>    a shop tagged it
      derived:skincarisma    computed from the ingredient list
  Are they measuring the same thing? If they agree closely, they are
  interchangeable. If they do not, they are answering different questions and
  must be kept separate - which is exactly what my dataset does.

Why a new scrape is needed
  In the dataset Amazon always wins, so SkinCarisma only ever filled products
  where Amazon was silent. That means ZERO overlap, and no way to compare them.
  This script deliberately looks up SkinCarisma for a SAMPLE of products that
  already have an Amazon value, purely to create the overlap needed for the
  comparison. Nothing here is written back into the dataset.

What it reports
  - agreement per skin type between Amazon (declared) and SkinCarisma (derived)
  - the same for Mazen (retailer) where products overlap
  - real disagreement examples, so the pattern can be read rather than guessed

Usage:
    py experiment_source_agreement.py       (~10 min for a 300-product sample)
"""
import re, time, random
import pandas as pd
import requests
from bs4 import BeautifulSoup
from rapidfuzz import fuzz, process

SAMPLE = 300
PAUSE  = 0.5
HEAD   = {'User-Agent': 'Mozilla/5.0 (academic thesis data collection)'}
BASE   = 'https://www.skincarisma.com'


def norm(s): return re.sub(r'[^a-z0-9]', '', str(s).lower())
def slug(s):
    import unicodedata
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()
    return re.sub(r'-+', '-', re.sub(r'[^a-zA-Z0-9]+', '-', s.lower()).strip('-'))


def fetch_skincarisma(brand, name):
    b, n = slug(brand), slug(name)
    for url in (f'{BASE}/products/{b}/{b}-{n}', f'{BASE}/products/{b}/{n}'):
        try:
            r = requests.get(url, headers=HEAD, timeout=25)
            if r.status_code == 200 and 'Ingredients Related to Skin Types' in r.text:
                return r.text
        except requests.RequestException:
            pass
        time.sleep(0.3)
    return None


def parse(html):
    text = BeautifulSoup(html, 'html.parser').get_text(' ', strip=True)
    out = {}
    for label, key in (('Dry Skin', 'dry'), ('Oily/Acne-Prone Skin', 'oily'),
                       ('Sensitive Skin', 'sensitive')):
        m = re.search(re.escape(label) + r'\s*(\d+)\s*/\s*(\d+)', text)
        if m:
            out[key] = 1 if int(m.group(1)) > int(m.group(2)) else 0
    return out or None


def parse_amazon(raw):
    s = str(raw).lower()
    f = dict(dry=0, oily=0, sensitive=0)
    if re.search(r'\ball\b', s):
        return dict(dry=1, oily=1, sensitive=1)
    if 'dry' in s: f['dry'] = 1
    if 'oil' in s or 'acne' in s: f['oily'] = 1
    if 'sensitive' in s: f['sensitive'] = 1
    return f


def main():
    import os
    SRC = next(f for f in ('Skincare_Reviewed_FINAL_v14.csv',
                           'Skincare_Reviewed_FINAL_v13.csv',
                           'Skincare_Reviewed_FINAL_v10.csv') if os.path.exists(f))
    print('reading', SRC)
    df = pd.read_csv(SRC, low_memory=False, dtype=str)
    amz = pd.read_csv('amazon_skintype.csv', dtype=str)
    m = pd.read_csv('acc19k_matches.csv', low_memory=False, dtype=str)
    m['k'] = m['brand'].map(norm) + '|' + m['name'].map(norm)
    df['k'] = df['brand'].map(norm) + '|' + df['name'].map(norm)
    df['asin'] = df['k'].map(dict(zip(m['k'], m['am_asin'])))
    df['amz_raw'] = df['asin'].map(dict(zip(amz['asin'], amz['amazon_skin_type_raw'])))

    pool = df[df['amz_raw'].notna()].copy()
    # drop the uninformative "All" - it agrees with everything by construction
    pool = pool[~pool['amz_raw'].str.strip().str.lower().eq('all')]
    print(f'products with a SPECIFIC Amazon skin type: {len(pool):,}')
    random.seed(42)
    take = pool.sample(min(SAMPLE, len(pool)), random_state=42)
    print(f'sampling {len(take)} of them and looking each up on SkinCarisma\n')

    rows = []
    for i, (_, p) in enumerate(take.iterrows(), 1):
        html = fetch_skincarisma(p['brand'], p['name'])
        if html:
            sc = parse(html)
            if sc:
                a = parse_amazon(p['amz_raw'])
                rows.append(dict(brand=p['brand'], name=str(p['name'])[:45],
                                 amazon_raw=str(p['amz_raw'])[:35],
                                 a_dry=a['dry'], a_oily=a['oily'], a_sens=a['sensitive'],
                                 s_dry=sc.get('dry', 0), s_oily=sc.get('oily', 0),
                                 s_sens=sc.get('sensitive', 0)))
        if i % 25 == 0:
            print(f'  {i}/{len(take)}  overlap found so far: {len(rows)}')
        time.sleep(PAUSE)

    r = pd.DataFrame(rows)
    r.to_csv('experiment_amazon_vs_skincarisma.csv', index=False)
    print(f'\n{"="*68}\nAMAZON (declared) vs SKINCARISMA (ingredient-derived)')
    print(f'products in both: {len(r)}\n{"="*68}')
    if r.empty:
        print('no overlap found'); return
    print(f"{'axis':12s}{'agreement':>11s}{'amazon yes':>12s}{'skincarisma yes':>17s}{'both':>7s}")
    for lab, a, s in (('dry', 'a_dry', 's_dry'), ('oily', 'a_oily', 's_oily'),
                      ('sensitive', 'a_sens', 's_sens')):
        x, y = r[a] == 1, r[s] == 1
        print(f'{lab:12s}{100*(x==y).mean():10.1f}%{x.sum():12d}{y.sum():17d}{(x&y).sum():7d}')

    print('\n--- where they disagree (read these, the pattern is the finding) ---')
    dis = r[(r.a_dry != r.s_dry) | (r.a_oily != r.s_oily) | (r.a_sens != r.s_sens)]
    print(dis[['brand', 'name', 'amazon_raw', 's_dry', 's_oily', 's_sens']].head(10).to_string(index=False))
    print(f'\nwrote experiment_amazon_vs_skincarisma.csv')


if __name__ == '__main__':
    main()
