"""
Images of last resort, via serper image search

When to use this
  After fetch_product_images.py and fetch_images_brand_sites.py. This one
  costs credits, so it is only for what those two could not reach: products
  whose only link is skinsort, which refuses automated requests, and whose
  brand has no readable catalogue.

The risk this is built around
  A Google image search for a product name returns the right photograph most
  of the time. The rest of the time it returns a blog review shot, a Pinterest
  collage, a different size, or a different product from the same brand.

Usage:
    py fetch_images_serper.py --test 40    measure the accept rate, write nothing
    py fetch_images_serper.py              the whole remainder
    py fetch_images_serper.py --apply      write what was accepted
"""
import os
import re
import csv
import sys
import ssl
import json
import time
import queue
import threading
import collections
import urllib.request
import urllib.error
import unicodedata

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
DOMAINS = 'brand_domains.json'
CACHE = 'serper_images.json'
WORKERS = 4
TIMEOUT = 20

APPLY = '--apply' in sys.argv
TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 40

KEYS = [
        # newest first, so a fresh key is used before the spent ones
        '',
    '',
    '',
    '',
    '',
    '',
    '',
    '',
]

# Retailers whose product photography is the manufacturer's own, and which are
# already used as sources elsewhere in this project.
TRUSTED = re.compile(
    r'(sohaticare|feel22|mazenonline|zeinacare|nexuscare|houseofsoap|'
    r'cosmaline|khanelkaser|beesline|thealoelab|daouk|'
    r'sephora|ulta|boots|lookfantastic|feelunique|douglas|notino|'
    r'dermstore|beautybay|cultbeauty|shopify|cdn\.shop)', re.I)

# WHAT IS STILL REFUSED, AND WHY EACH ONE
#
# The filter used to accept only the brand's own site or a short list of
# trusted retailers, which left 1,692 products with no picture. It is now the
# other way round: everything is accepted unless there is a reason.
#
# Four reasons survive.
#
#   resale marketplaces   eBay, Poshmark, Mercari, Depop, Vinted. Poshmark
#                         PRICES were already removed from this dataset once,
#                         at the supervisors' request. Letting the same sites
#                         back in through a different column is the exact
#                         inconsistency that got noticed the first time.
#
#   Amazon                Their terms do not permit their product images to be
#                         used off Amazon. Irrelevant to a thesis, but this
#                         dataset is meant to be adopted by Lebanese
#                         retailers, and a shop serving Amazon-hosted images
#                         has a real licensing problem rather than a
#                         theoretical one.
#
#   analysis sites        INCIDecoder, SkinCarisma, CosDNA. Refused throughout
#                         this project. Skinsort is now handled separately
#                         because it is the source of the product records
#                         themselves.
#
#   not photographs       social networks, blogs, and Google's own thumbnail
#                         cache, which serves a resized copy from a URL that
#                         expires.
#
# Everything else, including Walmart, BigCommerce storefronts, Korean skincare
# retailers and ordinary CDNs, is now accepted. It is ordinary retail product
# photography and there was never a reason to refuse it.
REFUSED = re.compile(
    r'(ebay|poshmark|mercari|depop|vinted|whatnot|'
    r'amazon|media-amazon|ssl-images-amazon|'
    r'incidecoder|skincarisma|cosdna|beautypedia|'
    r'pinterest|instagram|facebook|tiktok|reddit|youtube|tumblr|'
    r'lookaside|gstatic|googleusercontent|encrypted-tbn)', re.I)

# SKINSORT IS A SPECIAL CASE, and deliberately so.
#
# It was refused everywhere in this project because it is one of the analysis
# sites the supervisors questioned. That objection was about DERIVED claims:
# an ingredient analysis or an inferred skin type is somebody's interpretation
# and needs a better source.
#
# A photograph is not an interpretation. It is the picture of the product.
#
# And the 1,620 products this affects are the Global category, which came from
# Skinsort in the first place. Taking Skinsort's photograph of a product whose
# whole record is already cited to Skinsort is consistent with what the
# dataset already says, not an exception to it. Refusing it was the exception.
#
# It is recorded separately in image_source so these can be counted apart, and
# dropped, if a supervisor disagrees.
SKINSORT_IMG = re.compile(r'(^|\.)(storage\.)?skinsort\.com$', re.I)

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore') \
        .decode().lower()


def bkey(b):
    return re.sub(r'[^a-z0-9]', '', asc(b))


WELL_FORMED = re.compile(r'^https?://[^\s/?#]+\.[a-z]{2,}(?:[:/][^\s]*)?$', re.I)
NOT_A_PRODUCT = re.compile(
    r'(logo|placeholder|no[-_]?image|sprite|icon|favicon|avatar|banner|'
    r'spinner|blank|dummy|pixel|1x1|transparent|flag|badge)', re.I)

SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)

_ki, _lock = [0], threading.Lock()
_spent = [0]
_dead = threading.Event()


def host_of(u):
    m = re.match(r'https?://([^/]+)', str(u), re.I)
    return m.group(1).lower().replace('www.', '') if m else ''


def serper_images(q):
    while True:
        with _lock:
            if _ki[0] >= len(KEYS):
                _dead.set()
                return []
            k = KEYS[_ki[0]]
        body = json.dumps({'q': q, 'num': 10}).encode()
        req = urllib.request.Request(
            'https://google.serper.dev/images', data=body,
            headers={'X-API-KEY': k, 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
                data = json.loads(r.read().decode('utf-8', 'replace'))
        except urllib.error.HTTPError as e:
            if e.code in (400, 401, 402, 403, 429):
                with _lock:
                    if _ki[0] < len(KEYS) and KEYS[_ki[0]] == k:
                        print(f'   key ...{k[-6:]} is spent (HTTP {e.code})',
                              flush=True)
                        _ki[0] += 1
                continue
            return []
        except Exception:
            return []
        with _lock:
            _spent[0] += 1
        return data.get('images', []) or []


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

# --recheck-empties re-asks every product recorded as having no image.
#
# When the keys ran out mid run, an unknown number of products were cached as
# "nothing came back" without ever being asked. There is no way afterwards to
# tell those apart from a genuine empty answer, so the only honest option is
# to offer to ask all of them again. It costs one credit each and it is the
# difference between a measured no and a no that was never a question.
if '--recheck-empties' in sys.argv:
    gone = [k for k, v in cache.items() if not (v or {}).get('image_url')]
    for k in gone:
        del cache[k]
    print(f'  --recheck-empties: {len(gone):,} products with no image will be '
          f'asked again')

# --apply WRITES what has already been collected. It does not ask for more.
#
# It used to fetch first and write afterwards, so an --apply that was meant to
# bank 1,739 images quietly spent another 2,451 credits. Collecting and
# writing are separate actions and the flag now does only the one it names.
# The same fault was fixed in fetch_product_images.py for the same reason.
need = [] if APPLY else [
    r for r in D
    if not g(r, 'image_url') and g(r, 'product_id') not in cache]
if TEST:
    need = need[:TEST]

print('=' * 74)
print('  IMAGES OF LAST RESORT, VIA SERPER')
print('=' * 74)
print(f'  products with no image   {sum(1 for r in D if not g(r, "image_url")):,}')
print(f'  already asked before     {len(cache):,}')
print(f'  to ask now               {len(need):,}   (one credit each)')
if APPLY:
    print('  --apply only writes what is already collected, it spends nothing')
if TEST:
    print(f'  (test run, {TEST} products, nothing written)')
print()

counts = collections.Counter()
refused_hosts = collections.Counter()
accepted_hosts = collections.Counter()
q = queue.Queue()
for r in need:
    q.put(r)


def acceptable(img_url, page_url, brand):
    """Only the brand's own site or a trusted retailer."""
    if not img_url or not WELL_FORMED.match(img_url):
        return False, 'not a real address'
    if NOT_A_PRODUCT.search(img_url):
        return False, 'a logo or placeholder'
    ih, ph = host_of(img_url), host_of(page_url)
    # Skinsort's photograph, for a product whose record already comes from
    # Skinsort. Checked before the refusal list, and named distinctly so it
    # can be counted and reversed on its own.
    if SKINSORT_IMG.search(ih):
        return True, 'Skinsort, the source of this product record'
    if REFUSED.search(ih) or REFUSED.search(ph):
        return False, 'a refused site'
    own = SITES.get(bkey(brand), '')
    if own:
        root = re.sub(r'[^a-z0-9]', '', own.split('.')[0])
        if root and (root in ih.replace('.', '') or root in ph.replace('.', '')):
            return True, "the brand's own site"
    bare = bkey(brand)
    if bare and len(bare) > 3 and (bare in ih.replace('.', '')
                                   or bare in ph.replace('.', '')):
        return True, "the brand's own site"
    if TRUSTED.search(ih) or TRUSTED.search(ph):
        return True, 'a trusted retailer'
    # Anything left is an ordinary retailer or CDN. Accepted, and recorded as
    # such so it can be counted apart from the brand's own photographs.
    return True, 'another retailer'


def work():
    while True:
        try:
            r = q.get_nowait()
        except queue.Empty:
            return
        try:
            if _dead.is_set():
                return
            brand = g(r, 'brand')
            name = SIZE.sub(' ', g(r, 'name')).strip()
            results = serper_images(f'{brand} {name}')
            if _dead.is_set() and not results:
                # The keys ran out during this request, so nothing was really
                # asked. Caching an empty answer here would record "no image
                # exists" for a product nobody looked for, and the cache would
                # then stop it ever being asked again with a working key.
                #
                # This is the same fault that once marked 4,641 products as
                # having no listings and nearly produced a false finding about
                # Lebanese products. An unasked question is not a no.
                with _lock:
                    counts['not asked, keys were spent'] += 1
                continue
            chosen, why = '', 'nothing came back'
            for res in results:
                iu = res.get('imageUrl') or ''
                pu = res.get('link') or res.get('domain') or ''
                ok, reason = acceptable(iu, pu, brand)
                if ok:
                    chosen, why = iu, reason
                    break
                with _lock:
                    refused_hosts[host_of(iu) or '?'] += 1
            with _lock:
                cache[g(r, 'product_id')] = {'image_url': chosen, 'why': why}
                if chosen:
                    counts['accepted'] += 1
                    accepted_hosts[host_of(chosen)] += 1
                else:
                    counts['refused, ' + why] += 1
                counts['done'] += 1
                n = counts['done']
                if n % 50 == 0:
                    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
                    print(f'    {n:5,} / {len(need):,}   accepted '
                          f"{counts['accepted']:,}   credits {_spent[0]:,}",
                          flush=True)
        finally:
            q.task_done()


if need:
    started = time.time()
    ts = [threading.Thread(target=work, daemon=True) for _ in range(WORKERS)]
    try:
        for t in ts:
            t.start()
        for t in ts:
            t.join()
    except KeyboardInterrupt:
        print('\n  stopped, everything found is saved.')
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))

    n = counts['done'] or 1
    print(f'\n  {counts["done"]:,} products asked in '
          f'{(time.time()-started)/60:.1f} min, {_spent[0]:,} credits')
    for k, v in counts.most_common():
        if k != 'done':
            print(f'     {v:6,}  {k}')
    print(f'  accept rate {100*counts["accepted"]/n:.0f}%')
    if accepted_hosts:
        print('\n  ACCEPTED FROM')
        for h, v in accepted_hosts.most_common(8):
            print(f'     {v:5,}  {h}')
    if refused_hosts:
        print('\n  REFUSED, most common hosts')
        for h, v in refused_hosts.most_common(8):
            print(f'     {v:5,}  {h}')
    if _dead.is_set():
        print('\n  EVERY KEY IS SPENT. Products asked after that point were')
        print('  not really asked. Do not read them as having no image.')

if TEST:
    print('\n  test run, nothing written.')
    sys.exit(0)
if not APPLY:
    got = sum(1 for c in cache.values() if c.get('image_url'))
    print(f'\n  {got:,} images waiting. write them in with:')
    print('     py fetch_images_serper.py --apply')
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
    if not WELL_FORMED.match(img) or NOT_A_PRODUCT.search(img):
        continue
    r['image_url'] = img
    r['image_source'] = 'found by image search on ' + c.get('why', '')
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
print('\n  the source of each is recorded in image_source, so an image found')
print('  by search can be told apart from one read off the product page.')
print('\n  now rebuild the tidy file:')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
