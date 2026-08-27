"""
SCRAPE SKIN TYPE FROM SKINCARISMA  (run this on your laptop)

Why skincarisma
  The 5,218 products with no declared skin type are mostly K-beauty (COSRX,
  innisfree, Missha, Round Lab, Mizon, TONYMOLY, Isntree) and US drugstore
  (Neutrogena, Cetaphil, CeraVe, Eucerin, Olay, Aveeno). Sephora, Douglas and
  Mazen do not stock those. Skincarisma does - it is the reference site for
  exactly this catalogue.
"""
import re, time, json, os, unicodedata
import pandas as pd
import requests
from bs4 import BeautifulSoup

DATA   = 'Skincare_Reviewed_FINAL_v6.csv'
OUT    = 'skincarisma_skintype_v2.csv'

# FIXED COLUMN SCHEMA - every row is written with exactly these fields, in this
# order, whether or not the page contained them.
#
# WHY THIS EXISTS: the first version built each chunk's columns from whatever
# keys happened to be found in those products, and appended with the header
# written only once. Later chunks therefore had a different column order under
# the first chunk's header, and values silently landed in the wrong columns
# (comedogenic ratings ended up in the sentence field, and so on). A fixed
# schema makes that impossible.
FIELDS = ['product_id', 'brand', 'name', 'sc_url',
          'sc_dry', 'sc_dry_good', 'sc_dry_bad',
          'sc_oily', 'sc_oily_good', 'sc_oily_bad',
          'sc_sensitive', 'sc_sensitive_good', 'sc_sensitive_bad',
          'sc_comedogenic', 'sc_fungal_safe', 'sc_origin', 'sc_sentence']
PAUSE  = 1.2                      # be polite, ~1 request per 1.2 s
HEAD   = {'User-Agent': 'Mozilla/5.0 (academic thesis data collection)'}
BASE   = 'https://www.skincarisma.com'


def slug(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()
    s = re.sub(r"[^a-zA-Z0-9]+", '-', s.lower()).strip('-')
    return re.sub(r'-+', '-', s)


def find_product(brand, name):
    """Try the direct URL patterns first, then fall back to site search."""
    b, n = slug(brand), slug(name)
    for url in (f'{BASE}/products/{b}/{b}-{n}', f'{BASE}/products/{b}/{n}'):
        try:
            r = requests.get(url, headers=HEAD, timeout=25)
            if r.status_code == 200 and 'Ingredients Related to Skin Types' in r.text:
                return r.text, url
        except requests.RequestException:
            pass
        time.sleep(0.4)
    # search fallback
    try:
        r = requests.get(f'{BASE}/search', params={'q': f'{brand} {name}'},
                         headers=HEAD, timeout=25)
        a = BeautifulSoup(r.text, 'html.parser').select_one('a[href^="/products/"]')
        if a:
            r2 = requests.get(BASE + a['href'], headers=HEAD, timeout=25)
            if r2.status_code == 200:
                return r2.text, BASE + a['href']
    except requests.RequestException:
        pass
    return None, None


def parse(html):
    """Pull the skin-type evidence out of the page."""
    text = BeautifulSoup(html, 'html.parser').get_text(' ', strip=True)
    out = {}

    # 1. the quantitative scores, e.g. "Dry Skin 6/4"  ->  good=6, caution=4
    for label, key in (('Dry Skin', 'dry'),
                       ('Oily/Acne-Prone Skin', 'oily'),
                       ('Sensitive Skin', 'sensitive')):
        m = re.search(re.escape(label) + r'\s*(\d+)\s*/\s*(\d+)', text)
        if m:
            good, bad = int(m.group(1)), int(m.group(2))
            out[f'sc_{key}_good'] = good
            out[f'sc_{key}_bad']  = bad
            # a type counts as suitable when the good ingredients outweigh the bad
            out[f'sc_{key}'] = 1 if good > bad else 0

    # 2. the plain-language verdict sentence
    m = re.search(r'looks well-suited to\s+([^.]{3,90})\.', text, re.I)
    if m:
        s = m.group(1).lower()
        out['sc_sentence'] = m.group(1).strip()[:90]
        if 'dry' in s:                      out.setdefault('sc_dry', 1)
        if 'oily' in s or 'acne' in s:      out.setdefault('sc_oily', 1)
        if 'sensitive' in s:                out.setdefault('sc_sensitive', 1)

    # 3. extra attributes worth having
    m = re.search(r'Comedogenic\s*(\d)\s*/\s*5', text)
    if m: out['sc_comedogenic'] = int(m.group(1))
    out['sc_fungal_safe'] = 0 if 'Has triggers' in text else 1
    m = re.search(r'Origin\s+([A-Z][A-Za-z ]{3,20})\s+Data updated', text)
    if m: out['sc_origin'] = m.group(1).strip()
    return out or None


def main():
    df = pd.read_csv(DATA, low_memory=False, dtype=str)
    todo = df[df['skin_type_source'].eq('not declared')].copy()
    print(f'products still needing a skin type: {len(todo):,}')

    done = {}
    if os.path.exists(OUT):
        prev = pd.read_csv(OUT, dtype=str)
        done = set(prev['product_id'].dropna())
        print(f'already scraped: {len(done):,}  (resuming)')
        todo = todo[~todo['product_id'].isin(done)]

    # The URL for each product was already discovered in the first run, so reuse
    # it instead of guessing again - that skips the slow search fallback and
    # makes this pass roughly twice as fast.
    known_url = {}
    if os.path.exists('skincarisma_verified.csv'):
        v = pd.read_csv('skincarisma_verified.csv', dtype=str)
        known_url = dict(zip(v['product_id'], v['sc_url']))
        print(f'reusing {len(known_url):,} URLs found in the first run')
    globals()['KNOWN_URL'] = known_url

    # open once, write a header once, then one row at a time - no chunking, so
    # the columns can never drift.
    import csv as _csv
    first_write = not os.path.exists(OUT)
    fh = open(OUT, 'a', newline='', encoding='utf-8')
    writer = _csv.DictWriter(fh, fieldnames=FIELDS, extrasaction='ignore')
    if first_write:
        writer.writeheader()

    hits, t0 = 0, time.time()
    for i, (_, p) in enumerate(todo.iterrows(), 1):
        # fast path: we already know this product's page from the first run
        pre = globals().get('KNOWN_URL', {}).get(p['product_id'], '')
        html = url = None
        if isinstance(pre, str) and pre.startswith('http'):
            try:
                r = requests.get(pre, headers=HEAD, timeout=25)
                if r.status_code == 200 and 'Ingredients Related to Skin Types' in r.text:
                    html, url = r.text, pre
            except requests.RequestException:
                pass
        if html is None:
            html, url = find_product(p['brand'], p['name'])
        rec = {k: '' for k in FIELDS}                 # every field always present
        rec.update({'product_id': p['product_id'], 'brand': p['brand'],
                    'name': p['name'], 'sc_url': url or ''})
        if html:
            got = parse(html)
            if got:
                rec.update({k: v for k, v in got.items() if k in FIELDS})
                hits += 1
        writer.writerow(rec)
        fh.flush()                                    # safe to stop at any moment

        if i % 25 == 0:
            rate = i / max(time.time() - t0, 1)
            left = (len(todo) - i) / max(rate, .01) / 60
            print(f'  {i:,}/{len(todo):,}  found {hits:,}  '
                  f'({100*hits/i:.0f}%)  ~{left:.0f} min left')
        time.sleep(PAUSE)
    fh.close()
    print(f'\nDONE. skin type found for {hits:,} products -> {OUT}')
    print('next: run merge_skincarisma.py to fold these into the dataset')


if __name__ == '__main__':
    main()
