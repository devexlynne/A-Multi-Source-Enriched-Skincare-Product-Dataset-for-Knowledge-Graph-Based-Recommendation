"""
Ratings and reviews from the shop's own page

Why this exists
  Rating is the weakest column in the dataset, 48.3%. The Lebanese half is
  where nearly all of the gap sits: 5,005 Lebanese retail and 920 Lebanese
  origin products have no rating.

Usage:
    py fetch_reviews_from_pages.py --test 60     try 60, write nothing
    py fetch_reviews_from_pages.py               the Lebanese products
    py fetch_reviews_from_pages.py --apply       write what was found
"""
import os
import re
import csv
import sys
import json
import time
import queue
import threading
import collections

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
CACHE = 'page_reviews.json'
WORKERS = 8
GAP = 1.2
APPLY = '--apply' in sys.argv
TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 60

# The browser headers from the image script, but NOT its fetcher.
#
# fetch_head stops after 96 KB because og:image is in the page head. Reviews
# are not. A review widget sits near the bottom of the page, well past that
# cut, so the first version of this script was throwing the reviews away
# before it ever looked at them and then reporting that the shops publish
# none. That is the whole reason it returned 1%.
_img = open('fetch_product_images.py', encoding='utf-8').read()
_ns = {}
exec(compile(_img.split('# ====================================================='
                        '================ data')[0], 'f', 'exec'), _ns)
browser_headers = _ns['browser_headers']

import ssl
import gzip
import zlib
import urllib.request

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE
FULL_BYTES = 3_000_000        # the whole page, because reviews live at the end


def fetch_full(url):
    req = urllib.request.Request(url, headers=browser_headers(url))
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
        raw = r.read(FULL_BYTES)
        enc = (r.headers.get('Content-Encoding') or '').lower()
    if enc == 'deflate':
        try:
            raw = zlib.decompress(raw)
        except Exception:
            try:
                raw = zlib.decompressobj(-zlib.MAX_WBITS).decompress(raw)
            except Exception:
                return ''
    elif enc == 'gzip' or raw[:2] == b'\x1f\x8b':
        try:
            raw = gzip.decompress(raw)
        except Exception:
            try:
                raw = zlib.decompressobj(zlib.MAX_WBITS | 16).decompress(raw)
            except Exception:
                return ''
    return raw.decode('utf-8', 'replace')


# The review apps Shopify shops actually run. Each publishes its numbers in
# its own data attributes, which are structured values the app wrote, not
# stars to be counted out of the markup. Reading these is as safe as reading
# JSON-LD and it is where most Lebanese shops keep their reviews.
APPS = [
    ('Judge.me', re.compile(
        r'data-average-rating=["\']([\d.]+)["\'][^>]*'
        r'data-number-of-reviews=["\'](\d+)["\']', re.I)),
    ('Judge.me', re.compile(
        r'data-number-of-reviews=["\'](?P<c>\d+)["\'][^>]*'
        r'data-average-rating=["\'](?P<v>[\d.]+)["\']', re.I)),
    ('Loox', re.compile(
        r'data-rating=["\']([\d.]+)["\'][^>]*data-raters=["\'](\d+)["\']',
        re.I)),
    ('Yotpo', re.compile(
        r'data-average-score=["\']([\d.]+)["\'][^>]*'
        r'data-number-of-reviews=["\'](\d+)["\']', re.I)),
    ('Stamped', re.compile(
        r'data-rating=["\']([\d.]+)["\'][^>]*data-count=["\'](\d+)["\']',
        re.I)),
    ('Okendo', re.compile(
        r'data-oke-star-rating[^>]*data-oke-reviews-rating=["\']([\d.]+)["\']'
        r'[^>]*data-oke-reviews-count=["\'](\d+)["\']', re.I)),
    ('Shopify metafield', re.compile(
        r'"rating"\s*:\s*\{\s*"value"\s*:\s*"?([\d.]+)"?[^}]*\}[^}]*'
        r'"rating_count"\s*:\s*"?(\d+)"?', re.I)),
]

LD = re.compile(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',
                re.I | re.S)


def walk(node):
    """Every dict inside a JSON-LD block, however deeply nested."""
    stack = [node]
    while stack:
        n = stack.pop()
        if isinstance(n, list):
            stack.extend(n)
        elif isinstance(n, dict):
            yield n
            stack.extend(n.values())


def as_num(v):
    try:
        return float(str(v).strip().replace(',', ''))
    except Exception:
        return None


def read_rating(body):
    """
    aggregateRating out of the page's structured data.

    Only from JSON-LD. A visible star widget with nothing behind it is not
    read, because counting filled stars in markup is guesswork and this number
    will be shown to a customer and used to rank products.
    """
    for block in LD.findall(body)[:8]:
        try:
            data = json.loads(block.strip())
        except Exception:
            continue
        for node in walk(data):
            ar = node.get('aggregateRating')
            if not isinstance(ar, dict):
                continue
            val = as_num(ar.get('ratingValue'))
            cnt = as_num(ar.get('reviewCount') or ar.get('ratingCount'))
            best = as_num(ar.get('bestRating')) or 5.0
            if val is None or cnt is None:
                # a rating with nothing behind it cannot be checked
                continue
            if best and best != 5 and best > 0:
                val = val * 5.0 / best      # some shops rate out of 10
            if not (0 <= val <= 5) or cnt < 1:
                # count of zero is what an empty review widget emits, and it
                # would otherwise become a real looking score backed by nothing
                continue
            return round(val, 2), int(cnt), 'structured data'
    # JSON-LD had nothing. Try the review apps themselves.
    for app, rx in APPS:
        m = rx.search(body)
        if not m:
            continue
        gd = m.groupdict()
        if gd.get('v') is not None:
            val, cnt = as_num(gd['v']), as_num(gd['c'])
        else:
            val, cnt = as_num(m.group(1)), as_num(m.group(2))
        if val is None or cnt is None:
            continue
        if 0 <= val <= 5 and cnt >= 1:
            return round(val, 2), int(cnt), app
    return None, None, ''


def read_reviews(body, limit=8):
    """Individual review bodies, from the same structured data."""
    out = []
    for block in LD.findall(body)[:8]:
        try:
            data = json.loads(block.strip())
        except Exception:
            continue
        for node in walk(data):
            revs = node.get('review')
            if isinstance(revs, dict):
                revs = [revs]
            if not isinstance(revs, list):
                continue
            for rv in revs:
                if not isinstance(rv, dict):
                    continue
                text = (rv.get('reviewBody') or rv.get('description') or '')
                text = re.sub(r'\s+', ' ', str(text)).strip()
                if len(text) < 15:
                    continue
                rr = rv.get('reviewRating')
                stars = as_num(rr.get('ratingValue')) if isinstance(rr, dict) \
                    else None
                out.append({'text': text[:1200],
                            'rating': stars,
                            'source': 'the shop page'})
                if len(out) >= limit:
                    return out
    return out


# ===================================================================== data
with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


URLCOLS = ['product_url', 'retailer_urls', 'ingredient_url', 'skin_type_url']


def first_url(r):
    for c in URLCOLS:
        v = g(r, c)
        if v.startswith('http') and 'skinsort.com' not in v:
            return v.split(',')[0].split(' ')[0].strip()
    return ''


def dom_of(u):
    m = re.match(r'https?://([^/]+)', str(u), re.I)
    return m.group(1).lower().replace('www.', '') if m else ''


cache = json.load(open(CACHE, encoding='utf-8')) \
    if os.path.exists(CACHE) else {}

# The first run read only the first 96 KB of each page and so never reached
# the reviews. Every "nothing here" it recorded was a page that was never
# fully looked at, so those answers are discarded and asked again. The pages
# that DID give a rating are kept, because a hit does not go stale.
_stale = [] if APPLY else [
    k for k, v in cache.items() if not (v or {}).get('rating')]
for k in _stale:
    del cache[k]
if _stale:
    print(f'  {len(_stale):,} pages were cut short by the old reader and will '
          f'be read again in full')

# --apply WRITES. It does not fetch.
#
# Third time this fault has appeared in this project. In the image scripts it
# quietly spent credits; here it re-scraped 5,705 pages and the shops blocked
# it, 2,153 refusals and nothing gained. Collecting and writing are separate
# actions and the flag does only the one it names.
jobs = []
for r in ([] if APPLY else D):
    if not g(r, 'source_category').startswith('Lebanese'):
        continue
    if g(r, 'rating'):
        continue
    u = first_url(r)
    if u and g(r, 'product_id') not in cache:
        jobs.append((g(r, 'product_id'), u))

# spread across shops rather than finishing one at a time
_by = collections.defaultdict(list)
for j in jobs:
    _by[dom_of(j[1])].append(j)
_rr, jobs = list(_by.values()), []
while any(_rr):
    for b in _rr:
        if b:
            jobs.append(b.pop())
if TEST:
    jobs = jobs[:TEST]

print('=' * 74)
print('  RATINGS AND REVIEWS FROM THE SHOP\'S OWN PAGE')
print('=' * 74)
leb = [r for r in D if g(r, 'source_category').startswith('Lebanese')]
print(f'  Lebanese products         {len(leb):,}')
print(f'  already have a rating     {sum(1 for r in leb if g(r, "rating")):,}')
print(f'  asked in an earlier run   {len(cache):,}')
print(f'  to read now               {len(jobs):,}')
print(f'  {len(_by):,} shops, one request each every {GAP}s, none given up on')
if TEST:
    print(f'  (test run, nothing written)')
print()

lock = threading.Lock()
last_hit = collections.defaultdict(float)
counts = collections.Counter()
why = collections.Counter()
by_shop = collections.Counter()
how_found = collections.Counter()
q = queue.Queue()
for j in jobs:
    q.put(j)


def work():
    while True:
        try:
            pid, url = q.get_nowait()
        except queue.Empty:
            return
        d = dom_of(url)
        try:
            while True:
                with lock:
                    wait = last_hit[d] + GAP - time.time()
                    if wait <= 0:
                        last_hit[d] = time.time()
                        break
                time.sleep(min(wait, 0.5))
            try:
                body = fetch_full(url)
            except Exception as e:
                with lock:
                    why[type(e).__name__] += 1
                    counts['could not reach, will retry next run'] += 1
                    counts['done'] += 1
                continue
            val, cnt, how = read_rating(body)
            revs = read_reviews(body)
            with lock:
                cache[pid] = {'rating': val, 'count': cnt, 'how': how,
                              'reviews': revs, 'domain': d}
                if val is not None:
                    counts['found a rating'] += 1
                    by_shop[d] += 1
                    how_found[how] += 1
                elif revs:
                    counts['review text but no rating'] += 1
                else:
                    counts['page had neither'] += 1
                counts['done'] += 1
                n = counts['done']
            if n % 100 == 0:
                with lock:
                    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
                print(f'    {n:6,} / {len(jobs):,}   ratings '
                      f"{counts['found a rating']:,}", flush=True)
        finally:
            q.task_done()


if jobs:
    started = time.time()
    ts = [threading.Thread(target=work, daemon=True) for _ in range(WORKERS)]
    try:
        for t in ts:
            t.start()
        for t in ts:
            t.join()
    except KeyboardInterrupt:
        print('\n  stopped, what was read is saved.')
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
    n = counts['done'] or 1
    print(f'\n  {counts["done"]:,} pages read in '
          f'{(time.time()-started)/60:.1f} min')
    for k, v in counts.most_common():
        if k != 'done':
            print(f'     {v:6,}  {k}')
    print(f'  hit rate {100*counts["found a rating"]/n:.0f}%')
    if how_found:
        print('\n  WHERE THE RATING WAS PUBLISHED')
        for k, v in how_found.most_common():
            print(f'     {v:5,}  {k}')
    if by_shop:
        print('\n  RATINGS BY SHOP')
        for d, v in by_shop.most_common(10):
            print(f'     {v:5,}  {d}')
    if why:
        print('  failures:', dict(why.most_common(4)))
    ex = [c for c in cache.values() if c.get('rating')]
    if ex:
        print('\n  THREE THAT CAME BACK')
        for c in ex[:3]:
            print(f'     {c["domain"]}  {c["rating"]} from {c["count"]} reviews')

if TEST:
    print('\n  test run, nothing written.')
    sys.exit(0)
if not APPLY:
    got = sum(1 for c in cache.values() if c.get('rating'))
    print(f'\n  {got:,} ratings waiting. write them in with:')
    print('     py fetch_reviews_from_pages.py --apply')
    sys.exit(0)

# ------------------------------------------------------------------- apply
by_id = {g(r, 'product_id'): r for r in D}
n_r = n_t = 0
for pid, c in cache.items():
    r = by_id.get(pid)
    if not r or not c:
        continue
    val, cnt = c.get('rating'), c.get('count')
    if val is not None and cnt and not g(r, 'rating'):
        if 0 <= float(val) <= 5 and int(cnt) >= 1:   # checked again on write
            r['rating'] = f'{float(val):g}'
            if 'review_count' in r and not g(r, 'review_count'):
                r['review_count'] = str(int(cnt))
            if 'review_source' in r:
                have = g(r, 'review_source')
                r['review_source'] = (have + ', ' if have else '') + \
                    'lebanese_local'
            n_r += 1
    revs = c.get('reviews') or []
    if revs and g(r, 'review_texts_json') in ('', '[]'):
        r['review_texts_json'] = json.dumps(revs, ensure_ascii=False)
        n_t += 1

tmp = DATA + '.tmp'
with open(tmp, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, FIELDS, extrasaction='ignore')
    w.writeheader()
    w.writerows(D)
with open(tmp, 'rb') as fh:
    raw = fh.read()
try:
    raw.decode('utf-8')
except UnicodeDecodeError as e:
    os.remove(tmp)
    sys.exit(f'  the file came back damaged at byte {e.start:,}, nothing written')
os.replace(tmp, DATA)

tot = sum(1 for r in D if g(r, 'rating'))
print(f'\n  written {n_r:,} ratings and {n_t:,} sets of review text')
print(f'  rating now {tot:,} of {len(D):,} ({100*tot/len(D):.1f}%)')
print('\n  every one records lebanese_local in review_source, so a rating read')
print('  from the shop page can be told apart from one inherited by a match.')
print('\n  now rebuild the tidy file:')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
