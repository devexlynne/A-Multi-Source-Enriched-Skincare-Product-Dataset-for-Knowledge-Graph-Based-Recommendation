"""
Pass 3, the last 1,186. maximum effort per product.

These are the products where two searches and up to nine pages found no
statement. This pass throws everything at them.

What is different
  1. THREE QUERIES PER PRODUCT instead of one.
        "<brand> <name>"                          the plain product page
        "<brand> <name> for dry oily sensitive skin"
        "<brand> <name> review skin type"
     The first is the important one: it finds the product page itself rather
     than a page that happens to discuss skin types.

  2. TEN PAGES OPENED, up to.

Usage:
    py serper_pass3.py
    py serper_apply3.py
    py mark_not_applicable.py
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
from concurrent.futures import ThreadPoolExecutor, as_completed

SERPER_KEYS = _keys_from_env()

DATASET = 'SKINCARE_DATASET.csv'
OUT = 'serper_pass3_results.csv'
WORKERS = 3          # 6 workers x 3 queries dropped connections
PAGES = 10
TIMEOUT = 15

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'}

FIELDS = ['product_id', 'brand', 'name', 'skin_type', 'sensitivity', 'universal_claim',
          'skin_type_tier', 'skin_type_authority', 'skin_type_source',
          'skin_type_rule', 'skin_type_quote', 'skin_type_url',
          'search_rank', 'pages_opened', 'status']

BLOCK = re.compile(r'(instagram|facebook|tiktok|reddit|pinterest|lemon8|quora|twitter|'
                   r'x\.com|ebay|aliexpress|dhgate|alibaba|tripadvisor|linkedin)', re.I)
RETAILER = re.compile(r'(sephora|ulta|boots|douglas|lookfantastic|cultbeauty|dermstore|'
                      r'feelunique|notino|amazon|walmart|target|superdrug|beautybay|'
                      r'yesstyle|stylevana|oliveyoung|jolse|iherb|sokoglam|watsons|'
                      r'skinsociety|sohaticare|feel22|nexuscare|zeinacare|mazenonline|'
                      r'nykaa|flipkart|shopee|lazada|douglas|dm\.de|rossmann)', re.I)
ANALYSIS = re.compile(r'(incidecoder|skincarisma|cosdna|beautypedia|paulaschoice|'
                      r'byrdie|allure|dermstore|skinsort)', re.I)

TYPE_WORDS = {'dry': 'Dry', 'oily': 'Oily', 'oil': 'Oily', 'combination': 'Combination',
              'combo': 'Combination', 'normal': 'Normal', 'acne': 'Oily'}
UNIVERSAL = re.compile(r'\b(all skin types?|every skin type|any skin type|universal)\b', re.I)

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
     re.compile(r'\b(?:suitable|suited|recommended|formulated|designed|ideal|perfect|great'
                r'|made|created|developed)\s+(?:for|to)\s+([a-z ,/&+-]{3,70}?)\s*skin\b', re.I)),
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
     re.compile(r'\b(?:good|great|works?|helps?|benefits?|targets?|treats?|effective|gentle'
                r'|safe|kind)\s+(?:for|on|with)?\s*([a-z ,/&+-]{3,70}?)\s*skin\b', re.I)),
    # LAST RESORT. any mention at all of "<type> skin" on the page.
    (4, 'mentioned on the page',
     re.compile(r'\b(dry|oily|combination|normal|sensitive|acne[- ]prone|irritated)\s+skin\b', re.I)),
]


def n_types(p):
    t = str(p).lower()
    return sum(bool(re.search(r'\b' + w, t))
               for w in ('dry', 'oil', 'combination', 'normal', 'sensitiv'))


def parse_types(text):
    t = str(text).lower()
    f = {lab for w, lab in TYPE_WORDS.items() if re.search(r'\b' + re.escape(w), t)}
    sens = 'Sensitive' if re.search(r'\b(sensitiv|irritated|reactive|delicate|compromised)', t) else ''
    if 'Dry' in f and 'Oily' in f:
        return 'Combination', sens
    if 'Combination' in f:
        return 'Combination', sens
    for lab in ('Oily', 'Dry', 'Normal'):
        if lab in f:
            return lab, sens
    return '', sens


def sentence(flat, a, b):
    i = max(flat.rfind('.', 0, a), flat.rfind('|', 0, a), flat.rfind('•', 0, a), 0)
    j = min([x for x in (flat.find('.', b), flat.find('|', b)) if x != -1] or [len(flat)])
    return flat[i:j + 1].strip(' .|•').strip()


def extract(text, allow_last_resort=True):
    flat = re.sub(r'\s+', ' ', re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', text))
    for strength, rule, pat in PATTERNS:
        if strength == 4 and not allow_last_resort:
            continue
        for m in pat.finditer(flat):
            phrase = m.group(1)
            quote = sentence(flat, m.start(), m.end())
            if len(quote) > 400:
                quote = flat[max(0, m.start() - 100):m.end() + 120]
            if n_types(phrase) >= 4 or n_types(quote) >= 4 \
                    or UNIVERSAL.search(phrase) or UNIVERSAL.search(quote):
                return dict(skin_type='', sensitivity='', universal_claim='1',
                            skin_type_rule=rule + ' (all skin types)',
                            skin_type_quote=quote[:220], _s=strength)
            st, sn = parse_types(phrase)
            if st or sn:
                return dict(skin_type=st, sensitivity=sn, universal_claim='',
                            skin_type_rule=rule, skin_type_quote=quote[:220], _s=strength)
    return None


# ------------------------------------------------------------------ serper
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
            print(f'\n  key ...{k[-6:]} finished ({why}). {left} left.' if left
                  else f'\n  key ...{k[-6:]} finished ({why}). NO KEYS LEFT.')


def serper(q):
    for _ in range(len(SERPER_KEYS) + 1):
        k = current_key()
        if not k:
            _stop.set()
            return [], 'no keys left'
        r = None
        for attempt in range(3):          # a dropped connection is not a failure
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
            return [(o.get('link', ''), o.get('title', ''), o.get('snippet', ''))
                    for o in r.json().get('organic', [])], 200
        except Exception:
            return [], 'bad json'
    return [], 'exhausted'


def bkey(b):
    return re.sub(r'[^a-z0-9]', '', str(b).lower())


def tier_of(url, brand):
    host = url.split('/')[2].lower() if '://' in url else ''
    if not host or BLOCK.search(host):
        return 0, ''
    k = bkey(brand)
    if k and len(k) > 3 and k in re.sub(r'[^a-z0-9]', '', host):
        return 1, 'manufacturer'
    if RETAILER.search(host):
        return 2, 'retailer'
    if ANALYSIS.search(host):
        return 3, 'analysis'
    return 4, 'other'


def do(row):
    pid, brand, name = row['product_id'], row['brand'], row['name']
    rec = {k: '' for k in FIELDS}
    rec.update(product_id=pid, brand=brand, name=name, status='no answer', pages_opened='0')

    # FREE: the product name itself often says it
    hit = extract(name, allow_last_resort=True)
    if hit:
        st = hit.pop('_s')
        rec.update(hit)
        rec.update(skin_type_tier='1', skin_type_authority='product name',
                   skin_type_source='product name', skin_type_url='',
                   skin_type_rule='stated in the product name', status='found')
        return rec

    seen_urls = set()
    opened = 0
    for qi, q in enumerate((f'{brand} {name}',
                            f'{brand} {name} for dry oily sensitive skin',
                            f'{brand} {name} review skin type'), 1):
        results, code = serper(q)
        if code != 200:
            rec['status'] = f'serper {code}'
            if 'keys' in str(code).lower():
                return rec
            continue
        ranked = []
        for i, (u, t, sn) in enumerate(results, 1):
            if u in seen_urls:
                continue
            tr, auth = tier_of(u, brand)
            if tr:
                ranked.append((tr, i, u, t, sn, auth))
        ranked.sort(key=lambda x: (x[0], x[1]))
        for tr, rank, url, title, snip, auth in ranked[:PAGES]:
            seen_urls.add(url)
            hit = extract(snip, allow_last_resort=False) if snip else None
            if not hit:
                opened += 1
                try:
                    r = S.get(url, timeout=TIMEOUT)
                    if r.status_code != 200:
                        continue
                    body = re.sub(r'[^a-z0-9]', '', r.text[:200000].lower())
                    if bkey(brand) not in body:
                        continue
                    hit = extract(r.text, allow_last_resort=True)
                except Exception:
                    continue
            if hit:
                strength = hit.pop('_s')
                rec.update(hit)
                rec.update(skin_type_tier=str(max(tr, strength)) if strength == 4 else str(tr),
                           skin_type_authority=auth, skin_type_source=url.split('/')[2],
                           skin_type_url=url, search_rank=f'q{qi}r{rank}', status='found')
                rec['pages_opened'] = str(opened)
                return rec
        if _stop.is_set():
            break
    rec['pages_opened'] = str(opened)
    return rec


def main():
    d = list(csv.DictReader(open(DATASET, encoding='utf-8')))
    todo = [r for r in d
            if not r.get('skin_type') and not r.get('sensitivity')
            and r.get('universal_claim') != '1'
            and r.get('skin_type_status') != 'not applicable']
    done = set()
    if os.path.exists(OUT):
        done = {r['product_id'] for r in csv.DictReader(open(OUT, encoding='utf-8'))}
        print(f'resuming, {len(done):,} done')
    todo = [r for r in todo if r['product_id'] not in done]
    print(f'{len(todo):,} products left to fill')
    print(f'up to 3 searches each, so up to {len(todo)*3:,} credits (usually far fewer,\n'
          f'it stops at the first query that answers)\n')

    new = not os.path.exists(OUT)
    f = open(OUT, 'a', newline='', encoding='utf-8')
    w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction='ignore')
    if new:
        w.writeheader()

    found = 0
    tiers = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(do, r): r for r in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                rec = fut.result()
            except Exception as e:
                r = futs[fut]
                rec = {k: '' for k in FIELDS}
                rec.update(product_id=r['product_id'], brand=r['brand'],
                           name=r['name'], status='error ' + str(e)[:40])
            # a technical failure is not an answer. do not write it, or the row
            # would be skipped on the next run and lost for good.
            if re.search(r'keys|error|serper', str(rec['status']), re.I):
                continue
            w.writerow(rec)
            f.flush()
            if rec['skin_type'] or rec['sensitivity'] or rec['universal_claim'] == '1':
                found += 1
                tiers[rec['skin_type_tier']] = tiers.get(rec['skin_type_tier'], 0) + 1
            if _stop.is_set() and i % 25 == 0:
                print('\n  >>> OUT OF CREDITS. stopped cleanly, nothing lost.\n')
                break
            if i % 25 == 0 or i == len(todo):
                print(f'  {i:5,}/{len(todo):,}  filled {found:,} ({100*found/i:.0f}%)  '
                      f'brand {tiers.get("1",0)} shop {tiers.get("2",0)} '
                      f'analysis {tiers.get("3",0)} other/loose {tiers.get("4",0)}  '
                      f'| {rec["brand"][:14]:14s} {rec["skin_type"] or rec["status"][:12]}')
    f.close()

    res = list(csv.DictReader(open(OUT, encoding='utf-8')))
    got = [r for r in res if r['skin_type'] or r['sensitivity'] or r['universal_claim'] == '1']
    print('\n' + '=' * 62)
    print(f'  attempted  {len(res):,}')
    print(f'  filled     {len(got):,}  ({100*len(got)/max(len(res),1):.1f}%)')
    LAB = {'1': 'the brand / product name', '2': 'a retailer',
           '3': 'an analysis site', '4': 'other or loose match'}
    for t in ('1', '2', '3', '4'):
        c = sum(1 for r in got if r['skin_type_tier'] == t)
        if c:
            print(f'     tier {t}  {LAB[t]:26s}{c:5,}')
    print('\nnext:  py serper_apply3.py')


if __name__ == '__main__':
    main()
