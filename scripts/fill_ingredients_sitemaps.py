"""
Formulas from the brand's own site, with no search API at all

The idea
  The paid search API was only ever being used for one thing: to find out
  which page on the brand's site holds a given product.

  A brand does not need to be asked that. Nearly every commerce site publishes
  a sitemap listing every product URL it has, because search engines require
  it. Reading that sitemap gives the whole catalogue in one or two requests,
  and the matching can then be done here, offline, for nothing.

Usage:
    py fill_ingredients_sitemaps.py --dry      show the matches, change nothing
    py fill_ingredients_sitemaps.py           fetch and collect
    py fill_ingredients_sitemaps.py --apply   write what was found into the data
"""
import os
import re
import csv
import ssl
import sys
import json
import gzip
import time
import queue
import threading
import collections
import urllib.request
import urllib.error
import unicodedata

try:
    from rapidfuzz import fuzz
except ImportError:
    sys.exit('  needs rapidfuzz:   py -m pip install rapidfuzz')

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
DOMAINS = 'brand_domains.json'
CACHE = 'sitemap_ingredients.json'
SITEMAP_CACHE = 'sitemap_urls.json'
WORKERS = 24              # safe, because the queue below is spread over ~200 sites
TIMEOUT = 25
GAP = 0.5                 # per brand site
NAME_FLOOR = 86
MAX_SITEMAPS = 40         # per brand, so a huge index cannot run away

DRY = '--dry' in sys.argv
APPLY = '--apply' in sys.argv

# SCOPE IS NOW ANY BRAND WITH A KNOWN SITE, NOT A LIST OF 26.
#
# This was a hand written list of large international brands, chosen when the
# only resolved domains were the ones from the skin type work. brand_domains
# has since grown to 1,130 sites and their catalogues are already cached in
# sitemap_urls.json, so restricting to 26 names now throws away most of the
# reach for no reason. The image pass proved it: widened the same way, it
# matched products across 855 brands.
#
# A brand qualifies if a domain is known for it. That is the only test that
# matters, because a brand with no site cannot be read whatever its size.
IN_SCOPE = None

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# ------------------------------------------- the reader, imported not copied
_src = open('fill_gaps_from_pages.py', encoding='utf-8').read()
_marker = '# --------------------------------------------------------------- the data'
_ns = {}
exec(compile(_src.split(_marker)[0], 'reader', 'exec'), _ns)
read_ingredients = _ns['read_ingredients']
looks_like_a_formula = _ns['looks_like_a_formula']
read_skin_type = _ns['read_skin_type']
strip_html = _ns['strip_html']


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore') \
        .decode().lower()


def bkey(b):
    return re.sub(r'[^a-z0-9]', '', asc(b))


SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|mls|g|gr|gm|oz|fl|l|kg|mg|pcs?)\b', re.I)
NOISE = re.compile(r'\b(new|sale|promo|offer|pack|set|kit|bundle|gift|'
                   r'free|buy|x\d+)\b', re.I)
STOP = {'the', 'and', 'for', 'with', 'of', 'de', 'la', 'le', 'du', 'a', 'an',
        'en', 'et', 'html', 'php', 'aspx', 'index', 'products', 'product'}


def words(s, brand=''):
    """
    Turn a product name or a URL slug into comparable words.

    Three things had to be handled, each found by testing real pairs:

      The product name carries the brand and the slug does not, so
      "La Roche-Posay Effaclar Duo+" scored 83 against "effaclar-duo-plus"
      and was refused. The brand is removed first.

      "Duo+" and "duo-plus" are the same product written two ways, so + is
      spelled out before the punctuation is stripped.

      Slugs often end in a catalogue number, "...-serum-100436", which is
      noise that pulls the score down. Long digit runs are dropped, while
      short numbers are kept because "10%" and "SPF 50" are part of the name.
    """
    s = asc(s)
    if brand:
        b = asc(brand)
        s = s.replace(b, ' ')
        for piece in re.split(r'[^a-z0-9]+', b):
            if len(piece) > 2:
                s = re.sub(r'\b' + re.escape(piece) + r'\b', ' ', s)
    s = s.replace('+', ' plus ').replace('&', ' and ')
    s = NOISE.sub(' ', SIZE.sub(' ', s))
    out = []
    for w in re.split(r'[^a-z0-9]+', s):
        if not w or w in STOP or len(w) < 2:
            continue
        if w.isdigit() and len(w) > 4:      # catalogue number, not a strength
            continue
        out.append(w)
    return ' '.join(sorted(out))


def similarity(a, b):
    """
    How close two product names are.

    token_set_ratio was used at first and it scored "Huile Prodigieuse"
    against "Huile Prodigieuse Riche" at 87, above the threshold, because it
    ignores words that appear in only one of the two strings. Those extra
    words are exactly what separates one variant of a product from another,
    so ignoring them is the one thing this comparison must not do.

    token_sort_ratio keeps them and penalises them, which sends that pair to
    85 and refuses it, while an identical product written in a different word
    order still scores 100.
    """
    return fuzz.token_sort_ratio(a, b)


def slug_of(url):
    p = urllib_path(url).rstrip('/')
    seg = p.split('/')[-1] if p else ''
    seg = re.sub(r'\.(html?|php|aspx)$', '', seg)
    return seg


def urllib_path(url):
    m = re.match(r'https?://[^/]+(/[^?#]*)', str(url))
    return m.group(1) if m else ''


def fetch(url, limit=6_000_000):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA, 'Accept-Encoding': 'gzip',
        'Accept': 'text/html,application/xml,text/xml,*/*'})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
        # 400 KB is past the end of essentially every product page. Reading
        # 6 MB from the handful of enormous ones was holding a worker for
        # seconds at a time for nothing.
        raw = r.read(min(limit, 400_000))
        enc = (r.headers.get('Content-Encoding') or '').lower()
    if enc == 'gzip' or raw[:2] == b'\x1f\x8b':
        try:
            raw = gzip.decompress(raw)
        except Exception:
            pass
    return raw.decode('utf-8', 'replace')


# ===================================================================== data
with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


SITES = json.load(open(DOMAINS, encoding='utf-8')) \
    if os.path.exists(DOMAINS) else {}
cache = json.load(open(CACHE, encoding='utf-8')) \
    if os.path.exists(CACHE) else {}

# Anything missing a formula OR a skin type, from a brand whose site is known.
# Skin type is included because the same page answers both and the fetch is
# already being paid for in time.
need = [r for r in D
        if (not g(r, 'ingredients') or not g(r, 'skin_type'))
        and bkey(g(r, 'brand')) in SITES]
by_brand = collections.defaultdict(list)
for r in need:
    by_brand[g(r, 'brand')].append(r)

print('=' * 76)
print('  FORMULAS FROM THE BRAND SITEMAPS, NO API KEY')
print('=' * 76)
print(f'  products with no formula, in scope   {len(need):,}')
print(f'  brands                               {len(by_brand)}')
print(f'  already collected before             {len(cache):,}')
print()

# ------------------------------------------------- step 1, read the sitemaps
smap = json.load(open(SITEMAP_CACHE, encoding='utf-8')) \
    if os.path.exists(SITEMAP_CACHE) else {}

# A domain cached as EMPTY was a failure to find the sitemap, not a finding
# that the brand has no catalogue. Keeping those would make every future run
# repeat the first run's blind spot, and the discovery below has since been
# widened. Empty entries are dropped so they are looked for again. Domains
# that did yield URLs are kept, because those cost real requests.
_stale = [] if APPLY else [d for d, v in smap.items() if not v]
for d in _stale:
    del smap[d]
if _stale:
    print(f'  {len(_stale)} brands previously found nothing and will be '
          f'looked for again with the wider search')

LOC = re.compile(r'<loc>\s*([^<\s]+)\s*</loc>', re.I)
PRODUCTISH = re.compile(r'/(product|products|p|item|shop|produit|produkt)/', re.I)


# Where sites actually keep their sitemap. The first version only tried three
# of these and 12 of 31 brands came back with nothing, which was my discovery
# being too narrow rather than those brands publishing no sitemap.
CANDIDATES = [
    '/sitemap.xml', '/sitemap_index.xml', '/sitemap-index.xml',
    '/wp-sitemap.xml', '/sitemap/sitemap.xml', '/sitemap/index.xml',
    '/product-sitemap.xml', '/sitemap-products.xml', '/sitemaps/sitemap.xml',
    '/sitemap1.xml', '/media/sitemap.xml', '/sitemap.xml.gz',
    '/en/sitemap.xml', '/us/sitemap.xml',
]


def sitemap_urls(domain, note):
    """
    Every product URL the brand publishes, from its own sitemap.

    note is a list this appends its reasoning to, so a brand that yields
    nothing says why. Without that, "0 product URLs" could mean the site
    blocked us, the sitemap moved, or the brand genuinely has no catalogue,
    and those need different responses.
    """
    if domain in smap:
        note.append('cached')
        return smap[domain]

    roots = []
    for scheme in ('https://', 'http://'):
        try:
            robots = fetch(scheme + domain + '/robots.txt', 300_000)
            roots = re.findall(r'(?im)^\s*sitemap:\s*(\S+)', robots)
            if roots:
                note.append(f'robots.txt named {len(roots)}')
                break
            note.append('robots.txt named none')
            break
        except Exception as e:
            note.append(f'robots {type(e).__name__}')

    tried = list(roots[:10]) + [f'https://{domain}{p}' for p in CANDIDATES]

    seen_maps, out, pending = set(), [], tried
    opened = 0
    while pending and len(seen_maps) < MAX_SITEMAPS:
        u = pending.pop(0)
        if u in seen_maps:
            continue
        seen_maps.add(u)
        try:
            body = fetch(u)
        except Exception:
            continue
        if '<' not in body[:400]:
            continue
        locs = LOC.findall(body)
        if not locs:
            continue
        opened += 1
        is_index = '<sitemapindex' in body[:3000].lower()
        for loc in locs:
            # FOLLOW EVERY CHILD SITEMAP. The first version only followed
            # children whose URL contained "product" or "shop", so a site that
            # names them sitemap-1.xml, sitemap-2.xml lost its whole catalogue.
            if is_index or loc.lower().endswith(('.xml', '.xml.gz')):
                pending.append(loc)
            else:
                out.append(loc)
        time.sleep(0.15)

    if not opened:
        note.append('no readable sitemap at any known path')
    else:
        note.append(f'{opened} sitemap files read')

    # prefer product-looking URLs, but keep everything if the site has no
    # obvious product path, because some brands publish flat URLs
    prod = [u for u in out if PRODUCTISH.search(u)]
    keep = prod if len(prod) >= 20 else out
    keep = list(dict.fromkeys(keep))[:60000]
    smap[domain] = keep
    json.dump(smap, open(SITEMAP_CACHE, 'w', encoding='utf-8'))
    return keep


# --apply WRITES what has already been collected. It reads no sitemaps and
# fetches no pages.
#
# FOURTH time this fault has appeared in this project: fetch_product_images,
# fetch_images_serper and fetch_reviews_from_pages each had it first. Every
# time, --apply went back out and redid the entire collection before writing.
# Here that meant re-reading 316 sitemaps to write 432 cached answers.
#
# Collecting and writing are separate actions. The flag does only the one it
# is named after.
if APPLY:
    print('  --apply only writes what is already collected. No sitemaps are')
    print('  read and no pages are fetched.\n')
# READ THE SITEMAPS IN PARALLEL.
#
# This was a plain for loop, one brand after another. Cached brands returned
# instantly, but any brand not yet cached fetched up to forty sitemap files
# while all 313 others waited their turn. One slow site stalled the whole
# listing, which is what made a mostly cached run still feel like a crawl.
#
# Each brand is an independent site, so there is no reason to do them one at a
# time. Politeness is per site and is unaffected.
brand_index = {}
_sq = queue.Queue()
for _b in ([] if APPLY else sorted(by_brand)):
    _sq.put(_b)
_n_done = [0]
_total_brands = _sq.qsize()
_ilock = threading.Lock()


def _read_one_brand():
    while True:
        try:
            brand = _sq.get_nowait()
        except queue.Empty:
            return
        try:
            dom = SITES.get(bkey(brand), '')
            if not dom:
                continue
            note = []
            try:
                urls = sitemap_urls(dom, note)
            except Exception:
                urls = []
            idx = [(w, u) for w, u in
                   ((words(slug_of(u), brand), u) for u in urls) if w]
            with _ilock:
                if idx:
                    brand_index[brand] = idx
                _n_done[0] += 1
                if _n_done[0] % 50 == 0 or _n_done[0] == _total_brands:
                    print(f'    {_n_done[0]:4,} / {_total_brands:,} brands, '
                          f'{len(brand_index):,} with a catalogue', flush=True)
        finally:
            _sq.task_done()


if _total_brands:
    print(f'  READING {_total_brands:,} SITEMAPS, {WORKERS} at a time')
    _ts = [threading.Thread(target=_read_one_brand, daemon=True)
           for _ in range(WORKERS)]
    for _t in _ts:
        _t.start()
    for _t in _ts:
        _t.join()
    json.dump(smap, open(SITEMAP_CACHE, 'w', encoding='utf-8'))
    print(f'    {len(brand_index):,} of {_total_brands:,} brands gave a '
          f'catalogue')

# SPREAD THE WORK ACROSS SITES.
#
# jobs is built brand by brand, so every worker took a job from the same brand
# and then queued behind that one site's half second gap. Eight workers were
# doing the work of one while two hundred other sites sat untouched. Exactly
# the fault the image run had.
#
# Round robin by site means the per site pacing runs in parallel rather than
# in series: same politeness to any one shop, many times the throughput.
# ------------------------------------------------------ match, offline, free
print('\n  MATCHING PRODUCTS TO URLS')
jobs, pairs, unmatched = [], [], 0
for brand, rows in by_brand.items():
    idx = brand_index.get(brand)
    if not idx:
        unmatched += len(rows)
        continue
    for r in rows:
        if g(r, 'product_id') in cache:
            continue
        mine = words(g(r, 'name'), brand)
        if not mine:
            continue
        best, score = None, 0
        for w, u in idx:
            sc = similarity(mine, w)
            if sc > score or (sc == score and best and len(u) < len(best)):
                best, score = u, sc
        if best and score >= NAME_FLOOR:
            jobs.append((g(r, 'product_id'), best))
            pairs.append((brand, g(r, 'name'), best, score))
        else:
            unmatched += 1

_dom = re.compile(r'https?://([^/]+)', re.I)
_by = collections.defaultdict(list)
for _j in jobs:
    _m = _dom.match(str(_j[1]))
    _by[_m.group(1).lower().replace('www.', '') if _m else ''].append(_j)
_buckets, jobs = list(_by.values()), []
while any(_buckets):
    for _b in _buckets:
        if _b:
            jobs.append(_b.pop())

print(f'    matched to a URL      {len(jobs):,}')
print(f'    spread over           {len(_by):,} sites, asked in rotation')
print(f'    no good enough URL    {unmatched:,}')

if pairs:
    import random
    random.seed(3)
    print('\n  TEN MATCHES, PICKED AT RANDOM, READ THESE')
    print('  ' + '-' * 72)
    for b, nm, u, s in random.sample(pairs, min(10, len(pairs))):
        print(f'    {b}  (similarity {s:.0f})')
        print(f'      product : {nm[:64]}')
        print(f'      page    : {u[:88]}')
    print()

if DRY:
    print('  --dry, nothing fetched and nothing written.')
    sys.exit(0)

# --------------------------------------------------- step 3, read the pages
last_hit = collections.defaultdict(float)
lock = threading.Lock()
counts = collections.Counter()
q = queue.Queue()
for j in jobs:
    q.put(j)


def dom_of(u):
    m = re.match(r'https?://([^/]+)', u)
    return m.group(1).lower() if m else ''


def work():
    while True:
        try:
            pid, url = q.get_nowait()
        except queue.Empty:
            return
        try:
            d = dom_of(url)
            while True:
                with lock:
                    wait = last_hit[d] + GAP - time.time()
                    if wait <= 0:
                        last_hit[d] = time.time()
                        break
                time.sleep(min(wait, 0.4))
            try:
                text = strip_html(fetch(url))
            except Exception:
                with lock:
                    counts['page would not load'] += 1
                    counts['done'] += 1
                continue
            ing = read_ingredients(text)
            st = read_skin_type(text)
            rec = {'url': url}
            if ing and looks_like_a_formula(ing):
                rec['ingredients'] = ing
            if st:
                rec['skin_type'] = st
            with lock:
                cache[pid] = rec
                counts['found a formula' if 'ingredients' in rec
                       else 'page had no formula'] += 1
                counts['done'] += 1
                n = counts['done']
            if n % 25 == 0:
                with lock:
                    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
                print(f'    {n:5,} / {len(jobs):,}   formulas '
                      f"{counts['found a formula']:,}", flush=True)
        finally:
            q.task_done()


if APPLY:
    jobs = []                 # nothing to fetch, --apply only writes
if jobs:
    print('  READING THE PAGES')
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
print(f'  hit rate {100*counts["found a formula"]/n:.0f}%')

hits = [c for c in cache.values() if c.get('ingredients')]
for c in hits[:3]:
    print(f'\n    {c["url"][:80]}')
    print(f'      {c["ingredients"][:100]}...')

if not APPLY:
    print(f'\n  {len(hits):,} formulas waiting. write them in with:')
    print('     py fill_ingredients_sitemaps.py --apply')
    sys.exit(0)

# ------------------------------------------------------------------- apply
by_id = {g(r, 'product_id'): r for r in D}
n_i = n_s = n_ambig = 0
for pid, c in cache.items():
    r = by_id.get(pid)
    if not r:
        continue
    ing = c.get('ingredients')
    if ing and not g(r, 'ingredients') and looks_like_a_formula(ing):
        r['ingredients'] = ing
        if 'ingredient_count' in r:
            r['ingredient_count'] = str(len([p for p in re.split(r'[,;]', ing)
                                             if p.strip(' .;:-')]))
        if 'ingredient_source' in r:
            r['ingredient_source'] = "the brand's own site"
        if 'ingredient_url' in r:
            r['ingredient_url'] = c.get('url', '')
        n_i += 1
    st = c.get('skin_type')
    if st and not g(r, 'skin_type'):
        # This dataset keeps ONE skin type per product, with sensitivity in
        # its own column. Writing the page's answer back joined by commas put
        # "Combination, Oily" into a column whose only legal values are single
        # ones, and the validator caught it. Same fault, same fix, applied
        # here before it can happen twice.
        #
        # Two base types means the page did not decide, and neither will this.
        parts = [p.strip() for p in str(st).split(',') if p.strip()]
        sensitive = any(p.lower() == 'sensitive' for p in parts)
        base = [p for p in parts if p.lower() != 'sensitive']
        if sensitive and 'sensitivity' in r and not g(r, 'sensitivity'):
            r['sensitivity'] = 'Sensitive'
        if len(base) == 1:
            r['skin_type'] = base[0]
            # every provenance column filled together. A skin type with no
            # tier recorded against it is worse than no skin type, because the
            # tier is what the whole argument rests on.
            if 'skin_type_source' in r:
                r['skin_type_source'] = "tier 1, the brand's own site"
            if 'skin_type_tier' in r:
                r['skin_type_tier'] = '1'
            if 'skin_type_authority' in r:
                r['skin_type_authority'] = 'manufacturer'
            if 'skin_type_status' in r and not g(r, 'skin_type_status'):
                r['skin_type_status'] = 'stated on the page'
            if 'skin_type_url' in r and not g(r, 'skin_type_url'):
                r['skin_type_url'] = c.get('url', '')
            n_s += 1
        elif len(base) > 1:
            n_ambig += 1

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

tot = sum(1 for r in D if g(r, 'ingredients'))
print(f'\n  written {n_i:,} formulas and {n_s:,} skin types')
if n_ambig:
    print(f'  {n_ambig:,} pages named two skin types and were left empty '
          f'rather than guessed at')
print(f'  ingredients now {tot:,} of {len(D):,} ({100*tot/len(D):.1f}%)')
print('\n  now rebuild what is computed from the formula:')
print('     py derive_from_ingredients.py')
print('     py fill_from_formula.py')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
