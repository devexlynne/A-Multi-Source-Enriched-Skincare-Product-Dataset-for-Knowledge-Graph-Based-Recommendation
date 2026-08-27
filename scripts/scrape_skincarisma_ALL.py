"""
TRIAL: GET *EVERY* PRODUCT'S SKIN TYPE FROM ONE SOURCE (SkinCarisma)

Why this is methodologically better
  Right now my skin types come from a mixture: Amazon for some products,
  SkinCarisma for others, retailers and manual work for the rest. Each of those
  sources DEFINES skin type differently:
"""
import re, time, csv, os, threading, unicodedata
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests
from bs4 import BeautifulSoup

SRC     = 'Skincare_Reviewed_FINAL_v14.csv'
OUT     = 'skincarisma_ALL_products.csv'
KNOWN   = 'skincarisma_verified.csv'      # URLs already discovered, reused for speed
WORKERS = 8
PAUSE   = 0.35
HEAD    = {'User-Agent': 'Mozilla/5.0 (academic thesis data collection)'}
BASE    = 'https://www.skincarisma.com'

FIELDS = ['product_id', 'brand', 'name', 'sc_url', 'found',
          'sc_dry', 'sc_dry_good', 'sc_dry_bad',
          'sc_oily', 'sc_oily_good', 'sc_oily_bad',
          'sc_sensitive', 'sc_sensitive_good', 'sc_sensitive_bad',
          'sc_comedogenic', 'sc_fungal_safe', 'sc_sentence']

lock = threading.Lock()
count = {'done': 0, 'hit': 0, 't0': 0}


def slug(s):
    s = unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()
    return re.sub(r'-+', '-', re.sub(r'[^a-zA-Z0-9]+', '-', s.lower()).strip('-'))


def get_page(brand, name, known_url=''):
    """Reuse the URL if we already found it, else try the two slug patterns."""
    urls = []
    if isinstance(known_url, str) and known_url.startswith('http'):
        urls.append(known_url)
    b, n = slug(brand), slug(name)
    urls += [f'{BASE}/products/{b}/{b}-{n}', f'{BASE}/products/{b}/{n}']
    for u in urls:
        try:
            r = requests.get(u, headers=HEAD, timeout=25)
            if r.status_code == 200 and 'Ingredients Related to Skin Types' in r.text:
                return r.text, u
        except requests.RequestException:
            pass
    return None, ''


def parse(html):
    text = BeautifulSoup(html, 'html.parser').get_text(' ', strip=True)
    out = {}
    for label, key in (('Dry Skin', 'dry'), ('Oily/Acne-Prone Skin', 'oily'),
                       ('Sensitive Skin', 'sensitive')):
        m = re.search(re.escape(label) + r'\s*(\d+)\s*/\s*(\d+)', text)
        if m:
            g, b = int(m.group(1)), int(m.group(2))
            out[f'sc_{key}_good'] = g
            out[f'sc_{key}_bad']  = b
            out[f'sc_{key}'] = 1 if g > b else 0     # more good than bad
    m = re.search(r'looks well-suited to\s+([^.]{3,90})\.', text, re.I)
    if m: out['sc_sentence'] = m.group(1).strip()[:90]
    m = re.search(r'Comedogenic\s*(\d)\s*/\s*5', text)
    if m: out['sc_comedogenic'] = int(m.group(1))
    out['sc_fungal_safe'] = 0 if 'Has triggers' in text else 1
    return out


def work(job, writer, total):
    pid, brand, name, known = job
    rec = {k: '' for k in FIELDS}
    rec.update(product_id=pid, brand=brand, name=name, found=0)
    html, url = get_page(brand, name, known)
    if html:
        rec['sc_url'] = url
        rec['found'] = 1
        rec.update({k: v for k, v in parse(html).items() if k in FIELDS})
        with lock: count['hit'] += 1
    with lock:
        writer.writerow(rec)
        count['done'] += 1
        d = count['done']
        if d % 100 == 0:
            el = time.time() - count['t0']
            left = (total - d) / max(d / el, .01) / 60
            print(f'  {d:,}/{total:,}  found {count["hit"]:,} '
                  f'({100*count["hit"]/d:.0f}%)  ~{left:.0f} min left')
    time.sleep(PAUSE)


def main():
    df = pd.read_csv(SRC, low_memory=False, dtype=str)
    known = {}
    if os.path.exists(KNOWN):
        v = pd.read_csv(KNOWN, dtype=str)
        known = dict(zip(v['product_id'], v['sc_url']))
        print(f'reusing {len(known):,} URLs already discovered')

    already = set()
    if os.path.exists(OUT):
        already = set(pd.read_csv(OUT, dtype=str)['product_id'].dropna())
        print(f'already done: {len(already):,} (resuming)')

    jobs = [(p['product_id'], p['brand'], p['name'], known.get(p['product_id'], ''))
            for _, p in df.iterrows() if p['product_id'] not in already]
    print(f'products to look up: {len(jobs):,} of {len(df):,}\n')
    if not jobs:
        print('nothing to do'); return

    first = not os.path.exists(OUT)
    fh = open(OUT, 'a', newline='', encoding='utf-8')
    writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction='ignore')
    if first: writer.writeheader()

    count['t0'] = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for j in jobs:
            pool.submit(work, j, writer, len(jobs))
    fh.close()

    mins = (time.time() - count['t0']) / 60
    print(f'\nDONE in {mins:.0f} min')
    print(f'found on SkinCarisma: {count["hit"]:,} of {len(jobs):,}')
    print(f'-> {OUT}')
    print('\nnext:  py compare_single_source.py')


if __name__ == '__main__':
    main()
