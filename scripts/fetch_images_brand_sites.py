"""
Product images from the brand's own site

Why this exists
  Skinsort refuses automated requests. Every one of 5,793 remaining products
  points at skinsort and nowhere else, so reading its pages is not available.

  Those products are global brands, and the brand publishes the same
  photograph on its own site. So the brand is asked instead. This is the same
  move that took skin type from 6.6% to 98% and Lebanese ingredients from 27%
  to 76%: when the aggregator will not answer, go to the manufacturer.

Why this is also safer
  The block happened because one site was asked for 5,793 pages. Here the same
  5,793 products are spread over roughly 1,100 brand sites, so no single site
  is asked for more than a handful. The thing that caused the problem is gone
  by construction, not by tuning.

Usage:
    py fetch_images_brand_sites.py --dry     show the matches, fetch nothing
    py fetch_images_brand_sites.py           collect
    py fetch_images_brand_sites.py --apply   write them in
"""
import os
import re
import csv
import sys
import json
import time
import queue
import random
import threading
import collections

try:
    from rapidfuzz import fuzz
except ImportError:
    sys.exit('  needs rapidfuzz:   py -m pip install rapidfuzz')

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
DOMAINS = 'brand_domains.json'
SITEMAP_CACHE = 'sitemap_urls.json'
CACHE = 'brand_site_images.json'
WORKERS = 16
GAP = 0.5              # per brand site, and each site gets very few requests
NAME_FLOOR = 86
MAX_SITEMAPS = 25

DRY = '--dry' in sys.argv
APPLY = '--apply' in sys.argv
TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 60

# ---------------------------------------- borrowed, so nothing is duplicated
_img = open('fetch_product_images.py', encoding='utf-8').read()
_ns = {}
exec(compile(_img.split('# ====================================================='
                        '================ data')[0], 'imgreader', 'exec'), _ns)
read_image = _ns['read_image']
fetch_head = _ns['fetch_head']
usable = _ns['usable']
domain_of = _ns['domain_of'] if 'domain_of' in _ns else None

_sm = open('fill_ingredients_sitemaps.py', encoding='utf-8').read()
_ns2 = {}
_head = _sm.split('# ===================================================='
                  '================= data')[0]
_head = _head.replace(
    "_src = open('fill_gaps_from_pages.py', encoding='utf-8').read()", "_src=''")
_head = _head.replace("_ns = {}", "_ns = {'read_ingredients': 0, "
                                  "'looks_like_a_formula': 0, "
                                  "'read_skin_type': 0, 'strip_html': 0}")
_head = _head.replace("exec(compile(_src.split(_marker)[0], 'reader', 'exec'), _ns)",
                      "pass")
exec(compile(_head, 'matcher', 'exec'), _ns2)
words = _ns2['words']
similarity = _ns2['similarity']
slug_of = _ns2['slug_of']
bkey = _ns2['bkey']
fetch_page = _ns2['fetch']

# These three live below the data section in fill_ingredients_sitemaps.py, so
# the slice above does not reach them and importing them silently returned
# nothing. Defined here rather than reaching further into that file, because a
# slice that has to cut around the middle of a script is a slice that will
# break the next time either file is edited.
LOC = re.compile(r'<loc>\s*([^<\s]+)\s*</loc>', re.I)
PRODUCTISH = re.compile(r'/(product|products|p|item|shop|produit|produkt)/', re.I)
CANDIDATES = [
    '/sitemap.xml', '/sitemap_index.xml', '/sitemap-index.xml',
    '/wp-sitemap.xml', '/sitemap/sitemap.xml', '/product-sitemap.xml',
    '/sitemap-products.xml', '/sitemap1.xml',
]


def dom_of(u):
    m = re.match(r'https?://([^/]+)', str(u), re.I)
    return m.group(1).lower().replace('www.', '') if m else ''


# ===================================================================== data
with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


SITES = json.load(open(DOMAINS, encoding='utf-8')) \
    if os.path.exists(DOMAINS) else {}
smap = json.load(open(SITEMAP_CACHE, encoding='utf-8')) \
    if os.path.exists(SITEMAP_CACHE) else {}
cache = json.load(open(CACHE, encoding='utf-8')) \
    if os.path.exists(CACHE) else {}

need = [r for r in D
        if not g(r, 'image_url') and g(r, 'product_id') not in cache]
by_brand = collections.defaultdict(list)
for r in need:
    by_brand[g(r, 'brand')].append(r)

reachable = {b: rs for b, rs in by_brand.items() if bkey(b) in SITES}

print('=' * 76)
print('  PRODUCT IMAGES FROM THE BRAND\'S OWN SITE')
print('=' * 76)
print(f'  products with no image        {len(need):,}')
print(f'  brands                        {len(by_brand):,}')
print(f'  brands with a known site      {len(reachable):,}')
print(f'  products those cover          {sum(len(v) for v in reachable.values()):,}')
print(f'  sitemaps already read         {len(smap):,}')
print()

# ------------------------------------------------- step 1, read the sitemaps
lock = threading.Lock()
last_hit = collections.defaultdict(float)


def sitemap_urls(domain):
    with lock:
        if domain in smap:
            return smap[domain]
    roots = []
    for scheme in ('https://', 'http://'):
        try:
            robots = fetch_page(scheme + domain + '/robots.txt')
            roots = re.findall(r'(?im)^\s*sitemap:\s*(\S+)', robots)
            break
        except Exception:
            continue
    tried = list(roots[:6]) + [f'https://{domain}{p}' for p in CANDIDATES[:8]]
    seen, out, pending = set(), [], tried
    while pending and len(seen) < MAX_SITEMAPS:
        u = pending.pop(0)
        if u in seen:
            continue
        seen.add(u)
        try:
            body = fetch_page(u)
        except Exception:
            continue
        locs = LOC.findall(body)
        if not locs:
            continue
        is_index = '<sitemapindex' in body[:3000].lower()
        for loc in locs:
            if is_index or loc.lower().endswith(('.xml', '.xml.gz')):
                pending.append(loc)
            else:
                out.append(loc)
    prod = [u for u in out if PRODUCTISH.search(u)]
    keep = list(dict.fromkeys(prod if len(prod) >= 20 else out))[:60000]
    with lock:
        smap[domain] = keep
    return keep


brands = sorted(reachable, key=lambda b: -len(reachable[b]))
if TEST:
    brands = brands[:max(3, TEST // 20)]

print('  READING SITEMAPS')
sq = queue.Queue()
for b in brands:
    sq.put(b)
brand_index = {}
n_done = [0]


def smworker():
    while True:
        try:
            b = sq.get_nowait()
        except queue.Empty:
            return
        try:
            dom = SITES.get(bkey(b), '')
            try:
                urls = sitemap_urls(dom)
            except Exception:
                urls = []
            idx = [(words(slug_of(u), b), u) for u in urls]
            idx = [(w, u) for w, u in idx if w]
            with lock:
                if idx:
                    brand_index[b] = idx
                n_done[0] += 1
                if n_done[0] % 50 == 0:
                    print(f'    {n_done[0]:5,} / {len(brands):,} brands, '
                          f'{len(brand_index):,} with a catalogue', flush=True)
                    json.dump(smap, open(SITEMAP_CACHE, 'w', encoding='utf-8'))
        finally:
            sq.task_done()


ts = [threading.Thread(target=smworker, daemon=True) for _ in range(WORKERS)]
try:
    for t in ts:
        t.start()
    for t in ts:
        t.join()
except KeyboardInterrupt:
    print('\n  stopped.')
json.dump(smap, open(SITEMAP_CACHE, 'w', encoding='utf-8'))
print(f'    {len(brand_index):,} of {len(brands):,} brands gave a catalogue')

# ------------------------------------------------------ step 2, match offline
jobs, pairs, unmatched = [], [], 0
for b, rows in reachable.items():
    idx = brand_index.get(b)
    if not idx:
        unmatched += len(rows)
        continue
    for r in rows:
        mine = words(g(r, 'name'), b)
        if not mine:
            continue
        best, score = None, 0
        for w, u in idx:
            s = similarity(mine, w)
            if s > score or (s == score and best and len(u) < len(best)):
                best, score = u, s
        if best and score >= NAME_FLOOR:
            jobs.append((g(r, 'product_id'), best))
            pairs.append((b, g(r, 'name'), best, score))
        else:
            unmatched += 1

print(f'\n  MATCHING')
print(f'    matched to a page   {len(jobs):,}')
print(f'    no good enough URL  {unmatched:,}')

if pairs:
    random.seed(5)
    print('\n  TEN MATCHES, READ THESE BEFORE ANYTHING IS FETCHED')
    print('  ' + '-' * 72)
    for b, nm, u, s in random.sample(pairs, min(10, len(pairs))):
        print(f'    {b}  (similarity {s:.0f})')
        print(f'      product : {nm[:66]}')
        print(f'      page    : {u[:86]}')

if DRY:
    print('\n  --dry, nothing fetched, nothing written.')
    sys.exit(0)

# --------------------------------------------------- step 3, read the pages
counts = collections.Counter()
why = collections.Counter()
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
                time.sleep(min(wait, 0.3))
            try:
                body = fetch_head(url)
            except Exception as e:
                with lock:
                    why[type(e).__name__] += 1
                    counts['could not reach'] += 1
                    counts['done'] += 1
                continue
            img, _ = read_image(body, url)
            with lock:
                cache[pid] = {'image_url': img, 'url': url, 'domain': d}
                counts['found an image' if img else 'no usable image'] += 1
                counts['done'] += 1
                n = counts['done']
            if n % 100 == 0:
                with lock:
                    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
                print(f'    {n:6,} / {len(jobs):,}   images '
                      f"{counts['found an image']:,}", flush=True)
        finally:
            q.task_done()


print('\n  READING THE MATCHED PAGES')
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
print(f'\n  {counts["done"]:,} pages read in {(time.time()-started)/60:.1f} min')
for k, v in counts.most_common():
    if k != 'done':
        print(f'     {v:6,}  {k}')
print(f'  hit rate {100*counts["found an image"]/n:.0f}%')
if why:
    print('  failures:', dict(why.most_common(5)))

hits = [c for c in cache.values() if c.get('image_url')]
print(f'\n  {len(hits):,} images collected')
for c in hits[:3]:
    print(f'     {c["image_url"][:88]}')

if not APPLY:
    print('\n  write them in with:  py fetch_images_brand_sites.py --apply')
    sys.exit(0)

# ------------------------------------------------------------------- apply
for c in ('image_url', 'image_source'):
    if c not in FIELDS:
        FIELDS.append(c)
by_id = {g(r, 'product_id'): r for r in D}
n_w = 0
for pid, c in cache.items():
    r = by_id.get(pid)
    img = (c or {}).get('image_url', '')
    if not r or not img or g(r, 'image_url'):
        continue
    if img.startswith('http://'):
        img = 'https://' + img[len('http://'):]
    if not usable(img):
        continue
    r['image_url'] = img
    r['image_source'] = "the brand's own site"
    n_w += 1

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

tot = sum(1 for r in D if g(r, 'image_url'))
print(f'\n  written {n_w:,} images')
print(f'  images now {tot:,} of {len(D):,} ({100*tot/len(D):.1f}%)')
print('\n  now rebuild the tidy file:')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
