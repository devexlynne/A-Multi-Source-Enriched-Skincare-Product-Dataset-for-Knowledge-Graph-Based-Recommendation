"""
SKINCARISMA RE-SCRAPE  -  FAST VERSION  (~15-20 minutes, not 4 hours)

Why this is so much faster than the first run
  The first run was slow for two reasons, and both are now gone:
"""
import re, time, csv, os, threading
from concurrent.futures import ThreadPoolExecutor
import pandas as pd
import requests
from bs4 import BeautifulSoup

DATA    = 'Skincare_Reviewed_FINAL_v6.csv'
URLS    = 'skincarisma_verified.csv'          # the URLs found in the first run
OUT     = 'skincarisma_skintype_v2.csv'
WORKERS = 8
PAUSE   = 0.35                                 # per worker
HEAD    = {'User-Agent': 'Mozilla/5.0 (academic thesis data collection)'}

FIELDS = ['product_id', 'brand', 'name', 'sc_url',
          'sc_dry', 'sc_dry_good', 'sc_dry_bad',
          'sc_oily', 'sc_oily_good', 'sc_oily_bad',
          'sc_sensitive', 'sc_sensitive_good', 'sc_sensitive_bad',
          'sc_comedogenic', 'sc_fungal_safe', 'sc_origin', 'sc_sentence']

lock = threading.Lock()
counter = {'done': 0, 'hit': 0}


def parse(html):
    """Read the skin-type evidence off a Skincarisma product page."""
    text = BeautifulSoup(html, 'html.parser').get_text(' ', strip=True)
    out = {}
    for label, key in (('Dry Skin', 'dry'),
                       ('Oily/Acne-Prone Skin', 'oily'),
                       ('Sensitive Skin', 'sensitive')):
        m = re.search(re.escape(label) + r'\s*(\d+)\s*/\s*(\d+)', text)
        if m:
            good, bad = int(m.group(1)), int(m.group(2))
            out[f'sc_{key}_good'] = good
            out[f'sc_{key}_bad']  = bad
            out[f'sc_{key}'] = 1 if good > bad else 0      # more good than bad
    m = re.search(r'looks well-suited to\s+([^.]{3,90})\.', text, re.I)
    if m:
        s = m.group(1).lower()
        out['sc_sentence'] = m.group(1).strip()[:90]
        if 'dry' in s:                 out.setdefault('sc_dry', 1)
        if 'oily' in s or 'acne' in s: out.setdefault('sc_oily', 1)
        if 'sensitive' in s:           out.setdefault('sc_sensitive', 1)
    m = re.search(r'Comedogenic\s*(\d)\s*/\s*5', text)
    if m: out['sc_comedogenic'] = int(m.group(1))
    out['sc_fungal_safe'] = 0 if 'Has triggers' in text else 1
    m = re.search(r'Origin\s+([A-Z][A-Za-z ]{3,20})\s+Data updated', text)
    if m: out['sc_origin'] = m.group(1).strip()
    return out


def work(job, writer, total):
    pid, brand, name, url = job
    rec = {k: '' for k in FIELDS}
    rec.update(product_id=pid, brand=brand, name=name, sc_url=url)
    try:
        r = requests.get(url, headers=HEAD, timeout=25)
        if r.status_code == 200 and 'Ingredients Related to Skin Types' in r.text:
            got = parse(r.text)
            rec.update({k: v for k, v in got.items() if k in FIELDS})
            with lock: counter['hit'] += 1
    except requests.RequestException:
        pass
    with lock:
        writer.writerow(rec)
        counter['done'] += 1
        d = counter['done']
        if d % 100 == 0:
            el = time.time() - counter['t0']
            left = (total - d) / max(d / el, .01) / 60
            print(f'  {d:,}/{total:,}  values found {counter["hit"]:,}  '
                  f'~{left:.0f} min left')
    time.sleep(PAUSE)


def main():
    df = pd.read_csv(DATA, low_memory=False, dtype=str)
    todo = df[df['skin_type_source'].eq('not declared')]

    v = pd.read_csv(URLS, low_memory=False, dtype=str)
    urls = {r['product_id']: r['sc_url'] for _, r in v.iterrows()
            if isinstance(r['sc_url'], str) and r['sc_url'].startswith('http')}
    print(f'products needing a skin type : {len(todo):,}')
    print(f'URLs known from the first run: {len(urls):,}')

    already = set()
    if os.path.exists(OUT):
        already = set(pd.read_csv(OUT, dtype=str)['product_id'].dropna())
        print(f'already done this run        : {len(already):,} (resuming)')

    jobs = [(p['product_id'], p['brand'], p['name'], urls[p['product_id']])
            for _, p in todo.iterrows()
            if p['product_id'] in urls and p['product_id'] not in already]
    print(f'to fetch now                 : {len(jobs):,}\n')
    if not jobs:
        print('nothing to do'); return

    first = not os.path.exists(OUT)
    fh = open(OUT, 'a', newline='', encoding='utf-8')
    writer = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction='ignore')
    if first: writer.writeheader()

    counter['t0'] = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        for j in jobs:
            pool.submit(work, j, writer, len(jobs))
    fh.close()

    mins = (time.time() - counter['t0']) / 60
    print(f'\nDONE in {mins:.0f} min. values found for {counter["hit"]:,} products')
    print(f'-> {OUT}')
    print('next:  py verify_skincarisma.py   (then the Mazen comparison)')


if __name__ == '__main__':
    main()
