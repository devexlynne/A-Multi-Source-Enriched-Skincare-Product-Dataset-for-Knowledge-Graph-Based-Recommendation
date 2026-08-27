"""
Step 2 of 3. re-search the 1,160 weak ones, this time refusing weak sources.

The problem this solves
  1,160 products still get their skin type from an ingredient-analysis site or
  from a site I could not identify. Three of those sources are ones I should
  not be leaning on at all:

      incidecoder.com   713   an independent ingredient analysis, not the brand
      skinsort.com      137   the source my supervisors questioned
      skincarisma.com    40   the other source my supervisors questioned

Usage:
    py serper_rescue.py          ->  serper_rescue_results.csv
    py rescue_apply.py           ->  merges it, weak values only ever improve
"""
import os
import re
import csv
import json
import time
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# Put the freshest key FIRST. When one runs out the next is used automatically.
SERPER_KEYS = [
        '',
    '',
    '',
    '',
]
# ============================================================================

DATASET = 'SKINCARE_DATASET.csv'
OUT = 'serper_rescue_results.csv'
WORKERS = 3
PAGES = 8
TIMEOUT = 15

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'}

FIELDS = ['product_id', 'brand', 'name', 'skin_type', 'sensitivity', 'universal_claim',
          'skin_type_tier', 'skin_type_authority', 'skin_type_source',
          'skin_type_rule', 'skin_type_quote', 'skin_type_url',
          'pages_opened', 'status']

# ----------------------------------------------------- what is NOT acceptable
# analysis sites are named explicitly so they can never sneak back in
REJECT = re.compile(
    r'(incidecoder|skinsort|skincarisma|cosdna|beautypedia|skinwis|gopicky|'
    r'dermapproved|skinsafeproducts|myskincareregime|fiftyshadesofsnail|'
    r'musingsofamuse|allure|byrdie|refinery29|cosmopolitan|elle\.|vogue|'
    r'glamour|harpersbazaar|nypost|dailymail|buzzfeed|treelinereview|'
    r'instagram|facebook|tiktok|reddit|youtube|pinterest|lemon8|quora|'
    r'twitter|x\.com|ebay|aliexpress|etsy|wish\.com|dhgate|alibaba|'
    r'tripadvisor|linkedin|blogspot|wordpress\.com|medium\.com|substack)', re.I)

RETAILER = re.compile(
    r'(sephora|ulta|boots\.com|douglas|lookfantastic|cultbeauty|dermstore|'
    r'feelunique|notino|amazon|walmart|target\.com|superdrug|beautybay|'
    r'yesstyle|stylevana|oliveyoung|jolse|iherb|sokoglam|watsons|nykaa|'
    r'flipkart|shopee|lazada|macys|nordstrom|bluemercury|lovelyskin|spacenk|'
    r'peachandlily|asianbeautyessentials|skinstore|beautylish|revolve|'
    r'saksfifthavenue|harrods|selfridges|johnlewis|cvs\.com|walgreens|riteaid|'
    r'costco|kohls|dillards|neimanmarcus|bloomingdales|thebay|'
    r'shoppersdrugmart|chemistwarehouse|priceline|adorebeauty|meccabeauty|'
    r'sasa\.com|hktvmall|beautyhabit|stylekorean|wishtrend|skinsociety|'
    r'sohaticare|feel22|nexuscare|zeinacare|mazenonline|dm\.de|rossmann|'
    r'escentual|allbeauty|justmylook|beautyplussalon)', re.I)

STOP = {'the', 'la', 'le', 'dr', 'st', 'and', 'by', 'of', 'co', 'lab', 'labs',
        'beauty', 'skin', 'skincare', 'health', 'paris', 'london', 'new', 'york',
        'clean', 'natural', 'organic', 'cosmetics', 'cosmetic', 'shop', 'store'}

TYPE_WORDS = {'dry': 'Dry', 'oily': 'Oily', 'oil': 'Oily', 'combination': 'Combination',
              'combo': 'Combination', 'normal': 'Normal', 'acne': 'Oily'}
UNIVERSAL = re.compile(r'\b(all skin types?|every skin type|any skin type)\b', re.I)

# strengths 1 to 3 only. no "mentioned on the page".
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


def squash(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def host(u):
    u = str(u)
    return (u.split('/')[2] if '://' in u else u).lower()


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
    """A quote a supervisor can read. Markup means we failed, so reject it."""
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


# --------------------------------------------------------------- serper keys
S = requests.Session()
S.headers.update(HEAD)
_i, _dead, _lock = 0, set(), threading.Lock()
_stop = threading.Event()


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
            print(f'\n  key ...{k[-6:]} finished ({why}). {left} key(s) left.'
                  if left else f'\n  key ...{k[-6:]} finished ({why}). NO KEYS LEFT.')


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
        try:
            return [(o.get('link', ''), o.get('snippet', ''))
                    for o in r.json().get('organic', [])], 200
        except Exception:
            return [], 'bad json'
    return [], 'exhausted'


# ------------------------------------------- tier: ONLY 1 and 2 are accepted
def tier_of(url, brand):
    h = host(url)
    if not h or REJECT.search(h):
        return 0, ''
    hs = squash(h)
    k = squash(brand)
    if len(k) >= 4 and k in hs:
        return 1, 'manufacturer'
    words = [w for w in re.split(r'[^a-z0-9]+', str(brand).lower())
             if len(w) >= 5 and w not in STOP]
    if any(w in hs for w in words):
        return 1, 'manufacturer'
    if RETAILER.search(h):
        return 2, 'retailer'
    return 0, ''          # everything else is refused


# ================================================== load, and pick the targets
df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')
todo = df[df['skin_type_tier'].isin(['3', '4'])].copy()

# a free head start: the brand's own domain, learned from tier-1 rows elsewhere
known = {}
for _, r in df[df['skin_type_tier'] == '1'].iterrows():
    b = squash(r['brand'])
    h = host(r['skin_type_url'] or r['skin_type_source'])
    if b and h and b not in known:
        known[b] = h

done = set()
if os.path.exists(OUT):
    try:
        done = set(pd.read_csv(OUT, dtype=str)['product_id'])
        print(f'resuming, {len(done):,} already attempted')
    except Exception:
        pass
todo = todo[~todo['product_id'].isin(done)]

print(f'{len(todo):,} products to re-search, manufacturer and retailer pages only')
print(f'{len(known):,} brand domains already known from earlier rows (free lookups)')
print('nothing is deleted. a product only changes if a STRONGER source is found.\n')

_lock2 = threading.Lock()
_n = [0, 0]


def open_page(url, brand):
    try:
        r = S.get(url, timeout=TIMEOUT)
        if r.status_code != 200:
            return None
        body = squash(r.text[:200000])
        if squash(brand) not in body:
            return None
        return extract(r.text)
    except Exception:
        return None


def do(row):
    pid, brand, name = row['product_id'], row['brand'], row['name']
    rec = {k: '' for k in FIELDS}
    rec.update(product_id=pid, brand=brand, name=name,
               status='no strong source found', pages_opened='0')
    opened = 0
    seen = set()

    def take(url, auth, tr, hit):
        s = hit.pop('_s')
        rec.update(hit)
        rec.update(skin_type_tier=str(tr), skin_type_authority=auth,
                   skin_type_source=host(url), skin_type_url=url,
                   pages_opened=str(opened), status='found')
        rec['skin_type_rule'] = f"{rec['skin_type_rule']} (strength {s})"
        return rec

    for qi, q in enumerate((f'{brand} {name} skin type',
                            f'{brand} {name} official site'), 1):
        if _stop.is_set():
            rec['status'] = 'stopped, no keys'
            return rec
        results, code = serper(q)
        if code != 200:
            rec['status'] = f'serper {code}'
            if 'key' in str(code).lower():
                return rec
            continue
        ranked = []
        for i, (u, sn) in enumerate(results, 1):
            if not u or u in seen:
                continue
            tr, auth = tier_of(u, brand)
            if tr:
                ranked.append((tr, i, u, sn, auth))
        ranked.sort(key=lambda x: (x[0], x[1]))
        for tr, rank, url, snip, auth in ranked[:PAGES]:
            seen.add(url)
            hit = extract(snip) if snip else None
            if not hit:
                opened += 1
                hit = open_page(url, brand)
            if hit:
                return take(url, auth, tr, hit)
        rec['pages_opened'] = str(opened)
    return rec


rows = []
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = {ex.submit(do, r): r['product_id'] for _, r in todo.iterrows()}
    for f in as_completed(futs):
        try:
            rec = f.result()
        except Exception:
            continue
        rows.append(rec)
        with _lock2:
            _n[0] += 1
            if rec['status'] == 'found':
                _n[1] += 1
            if _n[0] % 25 == 0:
                print(f'  {_n[0]:,}/{len(todo):,}   upgraded {_n[1]:,}', flush=True)
        if len(rows) % 100 == 0:
            new = not os.path.exists(OUT)
            with open(OUT, 'a', newline='', encoding='utf-8') as fh:
                w = csv.DictWriter(fh, fieldnames=FIELDS)
                if new:
                    w.writeheader()
                w.writerows(rows)
            rows = []

if rows:
    new = not os.path.exists(OUT)
    with open(OUT, 'a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        if new:
            w.writeheader()
        w.writerows(rows)

res = pd.read_csv(OUT, dtype=str).fillna('')
found = res[res['status'] == 'found']
print('\n' + '=' * 64)
print(f'  attempted            {len(res):,}')
print(f'  upgraded to a strong source   {len(found):,}')
if len(found):
    print('    tier 1, manufacturer  ', int((found['skin_type_tier'] == '1').sum()))
    print('    tier 2, retailer      ', int((found['skin_type_tier'] == '2').sum()))
print(f'  no manufacturer or shop stated it   {int((res["status"] != "found").sum()):,}')
print('    those keep the value they already have, nothing is lost')
print('\nnow run:  py rescue_apply.py')
