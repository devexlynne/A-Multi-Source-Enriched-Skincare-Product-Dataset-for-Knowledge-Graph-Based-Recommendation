"""
The last 241. one more attempt, with different questions.

Who is left
    incidecoder.com        122
    skinsort.com            54     the sources my supervisors questioned
    skincarisma.com         14
    a tail of 51            skinwis, allure, gopicky, mayoclinic, a hiking blog

Why they survived the last pass
  Pass 4 asked two questions: "site:<brandsite> <product name>" and
  "<brand> <product name> buy". Those fail in three specific ways:

    1. THE NAME IS TOO LONG OR TOO DECORATED.
       "Cicapair Tiger Grass Color Correcting Treatment SPF 30" as a site:
       query matches nothing, because the brand's own page title is shorter or
       punctuated differently. Trimming to the first few distinctive words
       usually finds it.

Usage:
    py serper_last241.py
    py rescue_apply.py serper_last241_results.csv
    py build_dataset.py
"""

# KEYS COME FROM THE ENVIRONMENT, NOT FROM THIS FILE.
#
# They used to be written here. That is fine on one machine and dangerous the
# moment this folder is shared or published, because git keeps history: a key
# deleted in a later commit is still readable in the earlier one.
#
# Set them once before running, and never commit the file you set them in:
#
#     Windows    set SERPER_KEYS=key1,key2,key3
#     or put them in a file called .env, which .gitignore excludes
import os as _os


def _keys_from_env(name='SERPER_KEYS'):
    raw = _os.environ.get(name, '')
    if not raw and _os.path.exists('.env'):
        for line in open('.env', encoding='utf-8'):
            if line.strip().startswith(name + '='):
                raw = line.split('=', 1)[1].strip()
                break
    keys = [k.strip() for k in raw.split(',') if k.strip()]
    if not keys:
        raise SystemExit(
            f'\n  No API keys found.\n'
            f'  Set {name} before running, for example:\n'
            f'      set {name}=your_key_here\n'
            f'  or put a line {name}=your_key_here in a file called .env\n')
    return keys

import os
import re
import csv
import json
import time
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

SERPER_KEYS = _keys_from_env()

DATASET = 'SKINCARE_DATASET.csv'
OUT = 'serper_last241_results.csv'
DOMAINS = 'brand_domains.json'
WORKERS = 3
PAGES = 6
TIMEOUT = 15

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'}

FIELDS = ['product_id', 'brand', 'name', 'skin_type', 'sensitivity', 'universal_claim',
          'skin_type_tier', 'skin_type_authority', 'skin_type_source',
          'skin_type_rule', 'skin_type_quote', 'skin_type_url',
          'pages_opened', 'status']

REJECT = re.compile(
    r'(incidecoder|skinsort|skincarisma|cosdna|beautypedia|skinwis|gopicky|'
    r'dermapproved|skinsafeproducts|myskincareregime|fiftyshadesofsnail|'
    r'musingsofamuse|allure|byrdie|refinery29|cosmopolitan|elle\.|vogue|'
    r'glamour|harpersbazaar|nypost|dailymail|buzzfeed|treelinereview|'
    r'poshmark|mercari|depop|vinted|carousell|'
    r'instagram|facebook|tiktok|reddit|youtube|pinterest|lemon8|quora|'
    r'twitter|x\.com|ebay|aliexpress|etsy|wish\.com|dhgate|alibaba|'
    r'tripadvisor|linkedin|blogspot|wordpress\.com|medium\.com|substack|'
    r'wikipedia|pubmed|mayoclinic|google\.|bing\.|yahoo\.)', re.I)

SHOP = re.compile(r'(add[\s_-]?to[\s_-]?(cart|bag|basket)|addtocart|'
                  r'"@type"\s*:\s*"(product|offer)"|itemprop="price"|'
                  r'\bbuy now\b|\bin stock\b|\bout of stock\b|data-product-id)', re.I)

STOP = {'the', 'la', 'le', 'dr', 'st', 'and', 'by', 'of', 'co', 'lab', 'labs',
        'beauty', 'skin', 'skincare', 'health', 'paris', 'london', 'new', 'york',
        'clean', 'natural', 'organic', 'cosmetics', 'cosmetic', 'shop', 'store',
        'official', 'usa', 'global', 'company', 'group', 'care', 'products',
        'cream', 'serum', 'gel', 'lotion', 'with', 'for', 'and'}

TYPE_WORDS = {'dry': 'Dry', 'oily': 'Oily', 'oil': 'Oily', 'combination': 'Combination',
              'combo': 'Combination', 'normal': 'Normal', 'acne': 'Oily'}
UNIVERSAL = re.compile(r'\b(all skin types?|every skin type|any skin type)\b', re.I)

PATTERNS = [
    (1, 'declared field',
     re.compile(r'skin[\s_-]*type[^a-z0-9]{0,4}\s*[:\-]\s*([A-Za-z ,/&+-]{3,60})', re.I)),
    (1, 'declared field',
     re.compile(r'<t[hd][^>]*>\s*skin\s*type\s*</t[hd]>\s*<t[hd][^>]*>\s*([^<]{3,60})', re.I | re.S)),
    (1, 'labelled "for"',
     re.compile(r'\bfor\s*[:\-]\s*([a-z ,/&+-]{3,50}?)\s*skin\b', re.I)),
    (1, 'skin concern field',
     re.compile(r'skin\s*concerns?\s*[:\-]\s*([A-Za-z ,/&+-]{3,60})', re.I)),
    (2, 'suitability sentence',
     re.compile(r'\b(?:suitable|suited|recommended|formulated|designed|ideal|perfect'
                r'|great|made|created|developed)\s+(?:for|to)\s+([a-z ,/&+-]{3,70}?)\s*skin\b', re.I)),
    (2, 'reversed phrase',
     re.compile(r'\b([a-z ,/&+-]{3,50}?)\s*skin\s*types?\b', re.I)),
    (2, 'bullet or bare phrase',
     re.compile(r'(?:[••\-\*]|\bfor\b)\s*((?:dry|oily|combination|normal|sensitive|'
                r'acne[- ]prone)(?:[ ,/&+and-]{1,8}(?:dry|oily|combination|normal|sensitive))*)'
                r'\s*skin\b', re.I)),
    (2, 'soothing wording',
     re.compile(r'\b(?:soothe?s?|soothing|calm(?:s|ing)?|gentle|non[- ]irritating|'
                r'fragrance[- ]free|hypoallergenic|dermatologist[- ]tested)\b[^.]{0,60}?'
                r'\b(irritated|reactive|delicate|sensitive|compromised)\b', re.I)),
    (3, 'ingredient benefit',
     re.compile(r'\b(?:good|great|works?|helps?|benefits?|targets?|treats?|effective'
                r'|gentle|safe|kind)\s+(?:for|on|with)?\s*([a-z ,/&+-]{3,70}?)\s*skin\b', re.I)),
]

TAG = re.compile(r'<[^>]{0,400}>')
JUNK = re.compile(r'(class=|id=|href=|style=|</|/>)', re.I)


def sq(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def host(u):
    u = str(u)
    return (u.split('/')[2] if '://' in u else u).lower()


def bare(h):
    return host(h).replace('www.', '')


def tokens(s):
    return [w for w in re.split(r'[^a-z0-9]+', str(s).lower())
            if len(w) >= 3 and w not in STOP]


def n_types(p):
    t = str(p).lower()
    return sum(bool(re.search(r'\b' + w, t))
               for w in ('dry', 'oil', 'combination', 'normal', 'sensitiv'))


def parse_types(text):
    t = str(text).lower()
    f = {lab for w, lab in TYPE_WORDS.items() if re.search(r'\b' + re.escape(w), t)}
    sens = 'Sensitive' if re.search(r'\b(sensitiv|irritated|reactive|delicate|compromised)', t) else ''
    if ('Dry' in f and 'Oily' in f) or 'Combination' in f:
        return 'Combination', sens
    for lab in ('Oily', 'Dry', 'Normal'):
        if lab in f:
            return lab, sens
    return '', sens


def sentence(flat, a, b):
    i = max(flat.rfind('.', 0, a), flat.rfind('|', 0, a), flat.rfind('•', 0, a), 0)
    j = min([x for x in (flat.find('.', b), flat.find('|', b)) if x != -1] or [len(flat)])
    return flat[i:j + 1].strip(' .|•').strip()


def readable(q):
    q = re.sub(r'\s+', ' ', TAG.sub(' ', str(q))).strip(' .|•"\'>-')
    if JUNK.search(q):
        return ''
    letters = len(re.findall(r'[a-zA-Z]', q))
    if letters < 15 or letters < 0.55 * max(len(q), 1) or 'skin' not in q.lower():
        return ''
    return q[:220]


def extract(text):
    flat = re.sub(r'\s+', ' ',
                  re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', text))
    for strength, rule, pat in PATTERNS:
        for m in pat.finditer(flat):
            phrase = m.group(1)
            quote = readable(sentence(flat, m.start(), m.end()))
            if not quote:
                continue
            if n_types(phrase) >= 4 or UNIVERSAL.search(phrase) or UNIVERSAL.search(quote):
                return dict(skin_type='All', sensitivity='', universal_claim='1',
                            skin_type_rule=rule + ' (all skin types)',
                            skin_type_quote=quote, _s=strength)
            st, sn = parse_types(phrase)
            if st or sn:
                return dict(skin_type=st, sensitivity=sn, universal_claim='',
                            skin_type_rule=rule, skin_type_quote=quote, _s=strength)
    return None


S = requests.Session()
S.headers.update(HEAD)
_i, _dead, _lock = 0, set(), threading.Lock()
_stop = threading.Event()
_spent = [0]


def current_key():
    with _lock:
        return SERPER_KEYS[_i] if _i < len(SERPER_KEYS) else None


def retire(k, why):
    global _i
    with _lock:
        if k in _dead:
            return
        _dead.add(k)
        if _i < len(SERPER_KEYS) and SERPER_KEYS[_i] == k:
            _i += 1
            left = len(SERPER_KEYS) - _i
            print(f'\n  key ...{k[-6:]} finished ({why}). {left} left.'
                  if left else f'\n  key ...{k[-6:]} finished. NO KEYS LEFT.')


def serper(q):
    for _ in range(len(SERPER_KEYS) + 1):
        k = current_key()
        if not k:
            _stop.set()
            return [], 'no keys left'
        r = None
        for attempt in range(3):
            try:
                r = requests.post('https://google.serper.dev/search',
                                  headers={'X-API-KEY': k, 'Content-Type': 'application/json'},
                                  data=json.dumps({'q': q, 'num': 10}), timeout=TIMEOUT)
                break
            except Exception:
                time.sleep(1.5 * (attempt + 1))
        if r is None:
            return [], 'network error'
        if r.status_code in (400, 401, 402, 403, 429):
            retire(k, f'HTTP {r.status_code}')
            continue
        if r.status_code != 200:
            return [], r.status_code
        with _lock:
            _spent[0] += 1
        try:
            return [(o.get('link', ''), o.get('snippet', ''))
                    for o in r.json().get('organic', [])], 200
        except Exception:
            return [], 'bad json'
    return [], 'exhausted'


def fetch(url):
    try:
        r = S.get(url, timeout=TIMEOUT)
        return r.text if r.status_code == 200 else ''
    except Exception:
        return ''


df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')
todo = df[df['skin_type_tier'].isin(['3', '4']) & (df['skin_type'] != '')].copy()

BRAND_SITE = json.load(open(DOMAINS)) if os.path.exists(DOMAINS) else {}
for _, r in df[df['skin_type_tier'] == '1'].iterrows():
    b, h = sq(r['brand']), bare(r['skin_type_url'] or r['skin_type_source'])
    if b and h and h != 'productname' and not REJECT.search(h):
        BRAND_SITE.setdefault(b, h)

done = set()
if os.path.exists(OUT):
    try:
        done = set(pd.read_csv(OUT, dtype=str)['product_id'])
    except Exception:
        pass
todo = todo[~todo['product_id'].isin(done)]

print(f'{len(todo):,} products left on a weak source')
print(f'{sum(1 for _, r in todo.iterrows() if sq(r["brand"]) in BRAND_SITE):,} '
      f'of them have a known brand site to ask directly\n')

_n = [0, 0]
_lk = threading.Lock()


def do(row):
    pid, brand, name = row['product_id'], row['brand'], row['name']
    site = BRAND_SITE.get(sq(brand), '')
    rec = {k: '' for k in FIELDS}
    rec.update(product_id=pid, brand=brand, name=name,
               status='no official or shop page found', pages_opened='0')
    opened, seen = 0, set()
    short = ' '.join(tokens(name)[:3])          # the distinctive core of the name

    def take(url, auth, tr, h):
        s = h.pop('_s')
        rec.update(h)
        rec.update(skin_type_tier=str(tr), skin_type_authority=auth,
                   skin_type_source=bare(url), skin_type_url=url,
                   pages_opened=str(opened), status='found')
        rec['skin_type_rule'] = f"{rec['skin_type_rule']} (strength {s})"
        return rec

    queries = []
    if site and short:
        queries.append((f'site:{site} {short}', True))
    queries.append((f'"{brand} {name}" ingredients', False))
    queries.append((f'{brand} {name} for which skin type', False))

    for q, is_site in queries:
        if _stop.is_set():
            rec['status'] = 'stopped, no keys'
            return rec
        results, code = serper(q)
        if code != 200:
            if 'key' in str(code).lower():
                rec['status'] = 'stopped, no keys'
                return rec
            continue
        for url, snip in results[:PAGES]:
            h0 = bare(url)
            if not url or url in seen or not h0 or REJECT.search(h0):
                continue
            seen.add(url)
            on_site = bool(site and h0.endswith(site))
            hit = extract(snip) if (snip and on_site) else None
            if not hit:
                opened += 1
                html = fetch(url)
                if not html:
                    continue
                body = sq(html[:200000])
                if not any(t in body for t in tokens(brand)):
                    continue
                if not on_site and not SHOP.search(html):
                    continue
                hit = extract(html)
            if hit:
                return take(url, 'manufacturer' if on_site else 'retailer',
                            1 if on_site else 2, hit)
        rec['pages_opened'] = str(opened)
    return rec


rows = []


def flush(rows):
    if not rows:
        return
    new = not os.path.exists(OUT)
    with open(OUT, 'a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)


with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = [ex.submit(do, r) for _, r in todo.iterrows()]
    for f in as_completed(futs):
        try:
            rec = f.result()
        except Exception:
            continue
        rows.append(rec)
        with _lk:
            _n[0] += 1
            if rec['status'] == 'found':
                _n[1] += 1
            if _n[0] % 20 == 0:
                print(f'  {_n[0]}/{len(todo)}   upgraded {_n[1]}   '
                      f'credits {_spent[0]}', flush=True)
        if len(rows) >= 50:
            flush(rows)
            rows = []
flush(rows)

res = pd.read_csv(OUT, dtype=str).fillna('')
f2 = res[res['status'] == 'found']
print('\n' + '=' * 62)
print(f'  attempted                {len(res):,}')
print(f'  upgraded                 {len(f2):,}')
print(f'    the manufacturer       {int((f2["skin_type_tier"] == "1").sum()):,}')
print(f'    a shop                 {int((f2["skin_type_tier"] == "2").sum()):,}')
print(f'  no official page exists  {int((res["status"] != "found").sum()):,}')
print(f'  credits used             {_spent[0]:,}')
print('\nnow run:  py rescue_apply.py serper_last241_results.csv')
