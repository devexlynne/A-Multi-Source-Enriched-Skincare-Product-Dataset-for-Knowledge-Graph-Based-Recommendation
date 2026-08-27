"""
Ingredients from the brand's own page, via serper

Why this exists
  The shop pages do not publish an ingredient list for every product. Whatever
  they leave missing is fetched here, the same way the skin type column was
  filled: learn the brand's own domain once, then ask that domain directly.

  Ingredients are worth paying for. Three other columns are COMPUTED from them,
  so a missing ingredient list is really four missing fields:

Usage:
    py serper_ingredients.py                 everything still missing
    py serper_ingredients.py --test 100      measure the hit rate, write nothing
"""
import os
import re
import sys
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
    '',
]

DATA = 'LEBANESE_RETAIL.csv'
DOMAINS = 'brand_domains.json'
WORKERS = 3
PAGES = 6
TIMEOUT = 18
TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 100

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'}

# Analysis sites are refused here for the same reason they are refused for skin
# type: they are the sources my supervisors questioned, and letting them back in
# through the ingredients column would be exactly the kind of inconsistency that
# gets noticed. dermapproved was missing from this list by mistake and appeared
# 3 times in the first test.
#
# An ingredient list is a verbatim copy of the label rather than an inference,
# so a retailer or a specialist stockist repeating it is fine. What is refused
# is a site whose whole purpose is to interpret formulas.
REJECT = re.compile(
    r'(incidecoder|skinsort|skincarisma|cosdna|beautypedia|skinwis|gopicky|'
    r'dermapproved|skinsafeproducts|myskincareregime|paulaschoice-analysis|'
    r'cosmeticsandtoiletries|ewg\.org|thinkdirty|yuka\.io|'
    r'allure|byrdie|refinery29|cosmopolitan|vogue|glamour|nypost|buzzfeed|'
    r'poshmark|mercari|depop|vinted|instagram|facebook|tiktok|reddit|youtube|'
    r'pinterest|quora|twitter|x\.com|ebay|aliexpress|etsy|dhgate|alibaba|'
    r'linkedin|blogspot|wordpress\.com|medium\.com|wikipedia|google\.)', re.I)

PLACEHOLDER = re.compile(r'^(not available|not specified|n/?a|none|unknown|-|'
                         r'not comparable|no information)$', re.I)
HEADING = re.compile(r'(ingredients?|composition|inci|ingr[ée]dients?|contents|'
                     r'formula|what.s inside|full ingredient list)', re.I)
INCI_WORDS = re.compile(
    r'\b(aqua|water|glycerin|glycerine|alcohol denat|butylene glycol|'
    r'propylene glycol|sodium|potassium|cetearyl|stearyl|cetyl|dimethicone|'
    r'phenoxyethanol|tocopherol|parfum|fragrance|citric acid|xanthan|'
    r'carbomer|panthenol|niacinamide|extract|seed oil|butter|acid|'
    r'polysorbate|laureth|glyceryl|caprylic|triglyceride|benzoate|sorbate)\b', re.I)
START_OK = re.compile(r'^\s*(aqua|water|eau|glycerin|alcohol|cyclopenta|dimethicone|'
                      r'butylene|propylene|isododecane|caprylic|cetearyl|paraffinum|'
                      r'petrolatum|zinc oxide|titanium dioxide|homosalate|avobenzone|'
                      r'ethylhexyl)', re.I)
BAD = re.compile(r'(add to (cart|bag)|<script|function\s*\(|window\.|cookie|'
                 r'shipping|delivery|return policy|©|sign in|newsletter)', re.I)
TAG = re.compile(r'<[^>]+>')
SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)
BPRE = re.compile(r'^(the|eau thermale|laboratoires?|labo|by)\s+', re.I)
STOP = {'the', 'and', 'for', 'with', 'of', 'de', 'la', 'le', 'du', 'new', 'pack',
        'set', 'kit', 'skin', 'face', 'facial', 'ml', 'g', 'duo', 'in', 'to',
        'plus', 'my', 'a', 'x'}


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()


def bkey(s):
    t = asc(s).strip()
    for _ in range(3):
        t = BPRE.sub('', t).strip()
    return re.sub(r'[^a-z0-9]', '', t)


def short_name(name, brand):
    s = asc(name)
    for w in re.split(r'[^a-z0-9]+', asc(brand)):
        if len(w) > 2:
            s = s.replace(w, ' ')
    s = SIZE.sub(' ', s)
    return ' '.join([w for w in re.sub(r'[^a-z0-9 ]', ' ', s).split()
                     if w not in STOP][:4])


def clean(t):
    return re.sub(r'\s+', ' ', htmllib.unescape(TAG.sub(' ', t))).strip(' :.-•|')


def looks_like_inci(t):
    if not t or len(t) < 60 or len(t) > 6000 or BAD.search(t) or t.count(',') < 3:
        return False
    hits = len(INCI_WORDS.findall(t))
    if hits < 3:
        return False
    parts = [p.strip() for p in t.split(',') if p.strip()]
    if len(parts) < 4:
        return False
    if sum(1 for p in parts if len(p.split()) > 6) > len(parts) * 0.4:
        return False
    return bool(START_OK.match(t)) or hits >= 6


# Prose that gets glued to the front of a list when the word "ingredients"
# appears inside a sentence, e.g. "Main ingredients : Water, Glycerin...".
# Without trimming, the stored value began with usage instructions.
INSTRUCTION = re.compile(
    r'\b(apply|rinse|massage|peel it off|leave on|use (?:morning|daily|twice)|'
    r'caution|for external use|avoid contact|keep out of reach|patch test|'
    r'discontinue|shake well|store in)\b', re.I)
LEADIN = re.compile(r'\b(?:full\s+|main\s+|key\s+|active\s+|other\s+)?'
                    r'(?:ingredients?|inci|composition|contents)\b\s*[:\-–]?\s*', re.I)


def trim_to_formula(t):
    """Cut everything before the list actually starts. A chunk with no
    identifiable starting point is prose that merely mentions ingredients."""
    if not t:
        return ''
    best = ''
    for m in LEADIN.finditer(t):
        cand = t[m.end():].strip(' :.-–•|')
        if looks_like_inci(cand):
            best = cand
            break
    if not best:
        m = START_OK.search(t)
        if m:
            cand = t[m.start():].strip(' :.-–•|')
            if looks_like_inci(cand):
                best = cand
    if not best:
        return ''
    best = re.split(r'\b(?:how to use|directions|how to apply|benefits|reviews|'
                    r'description|shipping|caution|warning|for external use|'
                    r'related products|you may also like)\b',
                    best, maxsplit=1, flags=re.I)[0].strip(' :.-–•|')
    if INSTRUCTION.search(best[:120]):
        return ''
    return best if looks_like_inci(best) else ''


def extract_inci(page):
    body = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', page)
    for m in HEADING.finditer(body):
        chunk = clean(body[m.end():m.end() + 4000])
        chunk = re.split(r'(?:how to use|directions|benefits|reviews|description|'
                         r'shipping|related products)', chunk, maxsplit=1, flags=re.I)[0]
        got = trim_to_formula(chunk)
        if got:
            return got[:4000], 'under an ingredients heading'
    for block in re.split(r'</p>|</div>|</li>|<br\s*/?>', body):
        got = trim_to_formula(clean(block))
        if got:
            return got[:4000], 'a formula-shaped block'
    return None, ''


# ------------------------------------------------------------------- serper
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


# ===================================================================== data
df = pd.read_csv(DATA, dtype=str, low_memory=False).fillna('')
N = len(df)
for col in ('ingredients', 'key_ingredients', 'free_from', 'benefits'):
    if col in df.columns:
        df.loc[df[col].str.strip().str.match(PLACEHOLDER, na=False), col] = ''
for c in ('ingredient_source', 'ingredient_url', 'ingredient_rule'):
    if c not in df.columns:
        df[c] = ''

SITES = json.load(open(DOMAINS)) if os.path.exists(DOMAINS) else {}
for _, r_ in df[df['skin_type_tier'] == '1'].iterrows():
    u = str(r_['skin_type_url'])
    if '://' in u:
        SITES.setdefault(bkey(r_['brand']), u.split('/')[2].replace('www.', ''))

# ---------------------------------------------------------------- crash safety
# Everything found is appended to a progress file every 50 products. If the
# machine dies mid-run, the credits already spent are not lost: the next run
# reads this file, skips those products, and carries on. Writing only at the
# end, which is what an earlier version did, meant a crash threw away the whole
# pass along with everything it had cost.
PROGRESS = 'serper_ingredients_progress.csv'
PFIELDS = ['product_id', 'ingredients', 'ingredient_source',
           'ingredient_url', 'ingredient_rule']
import csv

already = {}
if os.path.exists(PROGRESS):
    try:
        p = pd.read_csv(PROGRESS, dtype=str).fillna('')
        already = {r['product_id']: r for _, r in p.iterrows()}
        # fold whatever a previous run found back into the dataset first
        byid = {v: k for k, v in df['product_id'].items()}
        restored = 0
        for pid, r in already.items():
            i = byid.get(pid)
            if i is not None and not df.at[i, 'ingredients'] and r['ingredients']:
                for c in PFIELDS[1:]:
                    df.at[i, c] = r[c]
                restored += 1
        if restored:
            df.to_csv(DATA, index=False)
        print(f'resuming: {len(already):,} products already attempted, '
              f'{restored:,} restored into the dataset\n')
    except Exception as e:
        print(f'(progress file unreadable, starting fresh: {e})\n')

need = df[df['ingredients'] == '']
if TEST:
    need = need.sample(min(TEST, len(need)), random_state=13)
    print(f'TEST MODE: {len(need)} products, nothing will be saved\n')
else:
    need = need[~need['product_id'].isin(already)]
    print(f'{len(need):,} of {N:,} products still need an ingredient list')
    print(f'{sum(1 for _, r in need.iterrows() if bkey(r["brand"]) in SITES):,} '
          f'of them have a known brand site to ask directly')
    print(f'progress is saved to {PROGRESS} every 50 products, '
          f'so a crash costs nothing\n')

found, where, how = {}, {}, {}
done = [0]
pending = []
lk = threading.Lock()


def flush_progress(force=False):
    """append what has been found since the last flush"""
    global pending
    if not pending or (len(pending) < 50 and not force):
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
        queries.append((f'site:{site} {sn} ingredients', True))
    queries.append((f'{brand} {sn} ingredients INCI', False))

    for q, on_brand_site in queries:
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
                    is_brand = bool(site and host.endswith(site))
                    auth = 'manufacturer' if is_brand else 'retailer'
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


with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = [ex.submit(work, i) for i in need.index]
    for fut in as_completed(futs):
        with lk:
            done[0] += 1
            if not TEST:
                flush_progress()          # every 50 findings, to survive a crash
            if done[0] % 25 == 0:
                print(f'   {done[0]:,}/{len(need):,}   found {len(found):,}'
                      f'   ({100*len(found)/max(done[0],1):.0f}%)'
                      f'   credits {_spent[0]:,}   saved {len(found)-len(pending):,}',
                      flush=True)
if not TEST:
    flush_progress(force=True)

rate = 100 * len(found) / max(len(need), 1)
print(f'\n   attempted {len(need):,}   found {len(found):,}   ({rate:.1f}%)'
      f'   credits used {_spent[0]:,}')
if where:
    print('\n   where they came from:')
    for h, n in sorted(where.items(), key=lambda x: -x[1])[:15]:
        print(f'      {h:26s}{n:6,}')
print('\n   EXAMPLES')
for i in list(found)[:5]:
    ing, host, url, method, auth = found[i]
    print(f'      {df.at[i,"brand"][:16]:16s} {df.at[i,"name"][:32]:32s} [{auth}, {host}]')
    print(f'         {ing[:96]}...')

if TEST:
    n_need = int((df['ingredients'] == '').sum())
    print('\n' + '=' * 62)
    print(f'  TEST ONLY, nothing written.')
    print(f'  hit rate {rate:.0f}%  ->  a full run would find about '
          f'{int(n_need*rate/100):,} of {n_need:,}')
    print(f'  and would cost roughly {int(n_need*_spent[0]/max(len(need),1)):,} credits')
    print('  run without --test to do it for real')
    raise SystemExit

for i, (ing, host, url, method, auth) in found.items():
    df.at[i, 'ingredients'] = ing
    df.at[i, 'ingredient_source'] = host
    df.at[i, 'ingredient_url'] = url
    df.at[i, 'ingredient_rule'] = f'{auth}, {method}'

df.to_csv(DATA, index=False)
n_now = int((df['ingredients'] != '').sum())
print('\n' + '=' * 62)
print(f'  ingredient coverage   {n_now:,} of {N:,}  ({100*n_now/N:.1f}%)')
print(f'  still missing         {N-n_now:,}')
print(f'  credits used          {_spent[0]:,}')
print('=' * 62)
print('\nnow run:  py derive_from_ingredients.py')
