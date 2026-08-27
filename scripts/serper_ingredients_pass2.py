"""
Ingredients, second pass. resolve the brand site first, then ask it.

Why the first pass left so much
  3,295 products still have no ingredient list. Looking at why, the answer is
  not that the information does not exist:

Usage:
    py serper_ingredients_pass2.py --test 100
    py serper_ingredients_pass2.py
"""
import os
import re
import sys
import csv
import json
import time
import html as htmllib
import unicodedata
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

SERPER_KEYS = [
    '',
                '',
    '',
]
DATA = 'LEBANESE_RETAIL.csv'
DOMAINS = 'brand_domains.json'
PROGRESS = 'serper_ingredients_pass2_progress.csv'
PFIELDS = ['product_id', 'ingredients', 'ingredient_source', 'ingredient_url',
           'ingredient_rule']
WORKERS = 3
PAGES = 6
TIMEOUT = 20
TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 100

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8,de;q=0.7'}

REJECT = re.compile(
    r'(incidecoder|skinsort|skincarisma|cosdna|beautypedia|skinwis|gopicky|'
    r'dermapproved|skinsafeproducts|myskincareregime|cosmeticsandtoiletries|'
    r'ewg\.org|thinkdirty|yuka\.io|allure|byrdie|refinery29|cosmopolitan|'
    r'vogue|glamour|nypost|buzzfeed|poshmark|mercari|depop|vinted|'
    r'instagram|facebook|tiktok|reddit|youtube|pinterest|quora|twitter|'
    r'x\.com|ebay|aliexpress|etsy|dhgate|alibaba|linkedin|blogspot|'
    r'wordpress\.com|medium\.com|wikipedia|google\.)', re.I)

BPRE = re.compile(r'^(the|eau thermale|laboratoires?|labo|by)\s+', re.I)
SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)
STOP = {'the', 'and', 'for', 'with', 'of', 'de', 'la', 'le', 'du', 'new', 'pack',
        'set', 'kit', 'skin', 'face', 'facial', 'ml', 'g', 'duo', 'in', 'to',
        'plus', 'my', 'a', 'x', 'buy', 'get', 'free'}
TAG = re.compile(r'<[^>]+>')
HEADING = re.compile(r'(ingredients?|composition|inci|ingr[ée]dients?|'
                     r'inhaltsstoffe|zutaten|contents|formula)', re.I)
INCI_WORDS = re.compile(
    r'\b(aqua|water|glycerin|glycerine|alcohol denat|butylene glycol|'
    r'propylene glycol|sodium|potassium|cetearyl|stearyl|cetyl|dimethicone|'
    r'phenoxyethanol|tocopherol|parfum|fragrance|citric acid|xanthan|carbomer|'
    r'panthenol|niacinamide|extract|seed oil|butter|acid|polysorbate|laureth|'
    r'glyceryl|caprylic|triglyceride|benzoate|sorbate)\b', re.I)
START_OK = re.compile(r'^\s*\(?(aqua|water|eau|glycerin|alcohol|cyclopenta|'
                      r'dimethicone|butylene|propylene|isododecane|caprylic|'
                      r'cetearyl|paraffinum|petrolatum|zinc oxide|titanium|'
                      r'homosalate|avobenzone|ethylhexyl|olea|cocos|'
                      r'butyrospermum|simmondsia|prunus|helianthus|hydrogenated|'
                      r'squalane|niacinamide|urea|acrylates|centella|vitis)', re.I)
BAD = re.compile(r'(add to (cart|bag)|<script|window\.|cookie|shipping|'
                 r'return policy|newsletter)', re.I)
INSTRUCTION = re.compile(r'\b(apply|rinse|massage|leave on|caution|'
                         r'for external use|avoid contact|patch test)\b', re.I)
LEADIN = re.compile(r'\b(?:full\s+|main\s+|key\s+|active\s+)?'
                    r'(?:ingredients?|inci|composition|inhaltsstoffe|contents)\b'
                    r'\s*[:\-–]?\s*', re.I)


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()


def bkey(s):
    t = asc(s).strip()
    for _ in range(3):
        t = BPRE.sub('', t).strip()
    return re.sub(r'[^a-z0-9]', '', t)


def short_name(name, brand, n=4):
    s = asc(name)
    for w in re.split(r'[^a-z0-9]+', asc(brand)):
        if len(w) > 2:
            s = s.replace(w, ' ')
    s = SIZE.sub(' ', s)
    return ' '.join([w for w in re.sub(r'[^a-z0-9 ]', ' ', s).split()
                     if w not in STOP][:n])


def clean(t):
    return re.sub(r'\s+', ' ', htmllib.unescape(TAG.sub(' ', str(t)))).strip(' :.-•|')


def looks_like_inci(t):
    if not t or len(t) < 50 or len(t) > 6000 or BAD.search(t):
        return False
    seps = t.count(',') + len(re.findall(r'\.\s+', t)) + len(re.findall(r'\s[-–]\s', t))
    if seps < 3:
        return False
    hits = len(INCI_WORDS.findall(t))
    if hits < 3:
        return False
    return bool(START_OK.match(t)) or hits >= 5


def extract_inci(page):
    body = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', page)
    for m in HEADING.finditer(body):
        chunk = clean(body[m.end():m.end() + 4000])
        chunk = re.split(r'(?:how to use|directions|benefits|reviews|description|'
                         r'shipping|anwendung|utilisation)', chunk,
                         maxsplit=1, flags=re.I)[0]
        for cand in (chunk, LEADIN.sub('', chunk, count=1)):
            cand = cand.strip(' :.-–•|')
            if looks_like_inci(cand) and not INSTRUCTION.search(cand[:110]):
                return cand[:4000], 'under an ingredients heading'
    for block in re.split(r'</p>|</div>|</li>|<br\s*/?>', body):
        t = clean(block)
        if looks_like_inci(t) and not INSTRUCTION.search(t[:110]):
            return t[:4000], 'a formula-shaped block'
    return None, ''


S = requests.Session()
S.headers.update(HEAD)
_i, _lock = [0], threading.Lock()
_spent = [0]
_stop = threading.Event()


def serper(q):
    while True:
        with _lock:
            if _i[0] >= len(SERPER_KEYS):
                _stop.set()
                return [], 'no keys'
            k = SERPER_KEYS[_i[0]]
        try:
            r = requests.post('https://google.serper.dev/search',
                              headers={'X-API-KEY': k, 'Content-Type': 'application/json'},
                              data=json.dumps({'q': q, 'num': 10}), timeout=TIMEOUT)
        except Exception:
            return [], 'network'
        if r.status_code in (400, 401, 402, 403, 429):
            with _lock:
                if _i[0] < len(SERPER_KEYS) and SERPER_KEYS[_i[0]] == k:
                    print(f'   key ...{k[-6:]} exhausted (HTTP {r.status_code})')
                    _i[0] += 1
            continue
        if r.status_code != 200:
            return [], r.status_code
        with _lock:
            _spent[0] += 1
        try:
            return [o.get('link', '') for o in r.json().get('organic', [])], 200
        except Exception:
            return [], 'bad json'


df = pd.read_csv(DATA, dtype=str, low_memory=False).fillna('')
N = len(df)
for c in ('ingredient_source', 'ingredient_url', 'ingredient_rule', 'ingredients_raw'):
    if c not in df.columns:
        df[c] = ''

SITES = json.load(open(DOMAINS)) if os.path.exists(DOMAINS) else {}

# fold in anything a previous run of this script already found
already = set()
if os.path.exists(PROGRESS):
    try:
        p = pd.read_csv(PROGRESS, dtype=str).fillna('')
        byid = {v: k for k, v in df['product_id'].items()}
        n_res = 0
        for _, r in p.iterrows():
            already.add(r['product_id'])
            i = byid.get(r['product_id'])
            if i is not None and not df.at[i, 'ingredients'] and r['ingredients']:
                df.at[i, 'ingredients'] = r['ingredients']
                df.at[i, 'ingredients_raw'] = r['ingredients']
                df.at[i, 'ingredient_source'] = r['ingredient_source']
                df.at[i, 'ingredient_url'] = r['ingredient_url']
                df.at[i, 'ingredient_rule'] = r['ingredient_rule']
                n_res += 1
        if n_res:
            df.to_csv(DATA, index=False)
        print(f'resuming: {len(already):,} already attempted, {n_res:,} restored\n')
    except Exception as e:
        print(f'(progress unreadable: {e})\n')

need = df[(df['ingredients'] == '') & (~df['product_id'].isin(already))]
if TEST:
    need = need.sample(min(TEST, len(need)), random_state=17)

# ==================================================== PHASE A, the brand sites
brands = sorted({r['brand'] for _, r in need.iterrows()
                 if bkey(r['brand']) and bkey(r['brand']) not in SITES})
print(f'{len(need):,} products need an ingredient list')
print(f'{len(brands):,} of their brands have no known website\n')


def resolve(brand):
    links, code = serper(f'{brand} official website skincare')
    if code != 200:
        return None
    toks = [w for w in re.split(r'[^a-z0-9]+', asc(brand)) if len(w) >= 3]
    for url in links:
        h = url.split('/')[2].lower().replace('www.', '') if '://' in url else ''
        if not h or REJECT.search(h):
            continue
        hs = re.sub(r'[^a-z0-9]', '', h)
        if bkey(brand) in hs or any(t in hs for t in toks):
            return h
    return None


if brands and not TEST:
    print('PHASE A  learning where each brand lives, one query per brand\n')
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(resolve, b): b for b in brands}
        n = 0
        for fut in as_completed(futs):
            b = futs[fut]
            n += 1
            try:
                h = fut.result()
            except Exception:
                h = None
            if h:
                SITES[bkey(b)] = h
            if n % 20 == 0:
                print(f'   {n}/{len(brands)}   resolved '
                      f'{sum(1 for x in brands if bkey(x) in SITES)}', flush=True)
            if _stop.is_set():
                break
    json.dump(SITES, open(DOMAINS, 'w'), indent=1)
    got = sum(1 for b in brands if bkey(b) in SITES)
    print(f'\n   resolved {got:,} of {len(brands):,} brand sites, '
          f'credits {_spent[0]:,}\n')

# ======================================================== PHASE B, the products
found, where, how = {}, {}, {}
pending, done = [], [0]
lk = threading.Lock()


def flush(force=False):
    global pending
    if not pending or (len(pending) < 40 and not force):
        return
    new = not os.path.exists(PROGRESS)
    with open(PROGRESS, 'a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=PFIELDS)
        if new:
            w.writeheader()
        w.writerows(pending)
    pending = []


def work(i):
    if _stop.is_set():
        return
    brand, name = df.at[i, 'brand'], df.at[i, 'name']
    site = SITES.get(bkey(brand), '')
    sn = short_name(name, brand)
    queries = []
    if site and sn:
        queries.append(f'site:{site} {sn} ingredients')
    queries.append(f'"{brand} {sn}" INCI composition')
    queries.append(f'{brand} {sn} full ingredient list')

    for q in queries:
        links, code = serper(q)
        if code != 200:
            continue
        for url in links[:PAGES]:
            host = url.split('/')[2].lower().replace('www.', '') if '://' in url else ''
            if not host or REJECT.search(host):
                continue
            try:
                r = S.get(url, timeout=TIMEOUT)
                if r.status_code != 200:
                    continue
                body = re.sub(r'[^a-z0-9]', '', r.text[:200000].lower())
                if bkey(brand) and bkey(brand)[:6] not in body:
                    continue
                ing, method = extract_inci(r.text)
                if ing:
                    on_site = bool(site and host.endswith(site))
                    auth = 'manufacturer' if on_site else 'retailer'
                    with lk:
                        found[i] = (ing, host, url, method, auth)
                        where[host] = where.get(host, 0) + 1
                        how[method] = how.get(method, 0) + 1
                        if not TEST:
                            pending.append(dict(
                                product_id=df.at[i, 'product_id'], ingredients=ing,
                                ingredient_source=host, ingredient_url=url,
                                ingredient_rule=f'{auth}, {method}'))
                    return
            except Exception:
                continue


print(f'PHASE B  {len(need):,} products, up to 3 queries each\n')
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = [ex.submit(work, i) for i in need.index]
    for fut in as_completed(futs):
        with lk:
            done[0] += 1
            if not TEST:
                flush()
            if done[0] % 25 == 0:
                print(f'   {done[0]:,}/{len(need):,}   found {len(found):,}'
                      f'   ({100*len(found)/max(done[0],1):.0f}%)'
                      f'   credits {_spent[0]:,}', flush=True)
if not TEST:
    flush(force=True)

rate = 100 * len(found) / max(len(need), 1)
print(f'\n   attempted {len(need):,}   found {len(found):,}   ({rate:.1f}%)'
      f'   credits {_spent[0]:,}')
if where:
    print('\n   where they came from:')
    for h, n in sorted(where.items(), key=lambda x: -x[1])[:15]:
        print(f'      {h:28s}{n:6,}')
print('\n   EXAMPLES')
for i in list(found)[:5]:
    ing, host, url, method, auth = found[i]
    print(f'      {df.at[i,"brand"][:16]:16s} {df.at[i,"name"][:30]:30s} [{auth}, {host}]')
    print(f'         {ing[:92]}...')

if TEST:
    n_need = int((df['ingredients'] == '').sum())
    print('\n' + '=' * 62)
    print('  TEST ONLY, nothing written.')
    print(f'  hit rate {rate:.0f}%  ->  a full run would find about '
          f'{int(n_need*rate/100):,} of {n_need:,}')
    print('  NOTE: phase A was skipped in test mode, so the real rate will be')
    print('  HIGHER once the brand websites are resolved.')
    raise SystemExit

for i, (ing, host, url, method, auth) in found.items():
    df.at[i, 'ingredients'] = ing
    df.at[i, 'ingredients_raw'] = ing
    df.at[i, 'ingredient_source'] = host
    df.at[i, 'ingredient_url'] = url
    df.at[i, 'ingredient_rule'] = f'{auth}, {method}'

df.to_csv(DATA, index=False)
now = int((df['ingredients'] != '').sum())
print('\n' + '=' * 62)
print(f'  ingredient coverage   {now:,} of {N:,}  ({100*now/N:.1f}%)')
print(f'  still missing         {N-now:,}')
print(f'  credits used          {_spent[0]:,}')
print('=' * 62)
print('\nnow run:  py validate_ingredients.py')
