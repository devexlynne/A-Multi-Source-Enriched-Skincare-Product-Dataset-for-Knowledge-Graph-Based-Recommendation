"""
Product images, from the pages we already have the address of

WHY

Usage:
    py fetch_product_images.py --test 60     try 60, write nothing
    py fetch_product_images.py               the whole file
    py fetch_product_images.py --apply       write the column in
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

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
CACHE = 'product_images.json'
READER_VERSION = 1
WORKERS = 16       # --gentle drops this to 1
HEAD_BYTES = 96_000        # og:image lives in the head, not the body
TIMEOUT = 10       # a shop that stalls should fail fast, not hold a worker
MAX_STRIKES = 40

GAP_START = 0.4
GAP_MIN = 0.08
GAP_MAX = 4.0
EASE_AFTER = 6

APPLY = '--apply' in sys.argv
# --lebanon does the Lebanese products first. They are the ones a Lebanese
# shop would actually display, and they are 7,349 pages rather than 13,142,
# so the useful half is done in a fraction of the time. The Skinsort products
# can be picked up afterwards by running again without the flag.
LEBANON_FIRST = '--lebanon' in sys.argv

# --gentle is for a shop that has started refusing. One request at a time,
# three seconds apart, and a shop is never given up on. It is slow on purpose:
# the point is to stay under the limit that triggered the refusal rather than
# to get finished quickly.
GENTLE = '--gentle' in sys.argv

# --only <domain> restricts the run to one shop. skinsort holds 5,793 of the
# 8,855 pages left and has never once refused a request, while the Lebanese
# shops block readily. Running them at the same pace means either skinsort
# crawls or the Lebanese shops get blocked, and there is no single setting
# that suits both. Separating them lets each run at the speed it can take.
ONLY = ''
if '--only' in sys.argv:
    i = sys.argv.index('--only')
    ONLY = sys.argv[i + 1].lower().replace('www.', '') if len(sys.argv) > i + 1 else ''

TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 60

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE

# furniture, not a product photo
NOT_A_PRODUCT = re.compile(
    r'(logo|placeholder|no[-_]?image|default|sprite|icon|favicon|avatar|'
    r'banner|spinner|loading|loader|blank|dummy|pixel|1x1|transparent|'
    r'facebook|instagram|whatsapp|tiktok|payment|visa|mastercard|'
    r'flag|badge|arrow|chevron|social)', re.I)

OG = re.compile(
    r'<meta[^>]+(?:property|name)\s*=\s*["\']og:image(?::url)?["\'][^>]*'
    r'content\s*=\s*["\']([^"\']+)["\']', re.I)
OG_REV = re.compile(
    r'<meta[^>]+content\s*=\s*["\']([^"\']+)["\'][^>]*'
    r'(?:property|name)\s*=\s*["\']og:image(?::url)?["\']', re.I)
TW = re.compile(
    r'<meta[^>]+(?:property|name)\s*=\s*["\']twitter:image[^"\']*["\'][^>]*'
    r'content\s*=\s*["\']([^"\']+)["\']', re.I)
IMGSRC = re.compile(
    r'<link[^>]+rel\s*=\s*["\']image_src["\'][^>]*href\s*=\s*["\']([^"\']+)["\']',
    re.I)
LD = re.compile(r'<script[^>]+application/ld\+json[^>]*>(.*?)</script>',
                re.I | re.S)


def absolute(u, page):
    u = (u or '').strip().replace('&amp;', '&')
    if not u:
        return ''
    if u.startswith('//'):
        return 'https:' + u
    if u.startswith('http'):
        return u
    m = re.match(r'(https?://[^/]+)', page)
    if not m:
        return ''
    # the slash is added once, after stripping any the path already had.
    # An earlier version added it only when the path did NOT start with one,
    # then stripped it anyway, which glued host and path together into
    # "sohaticare.commedia/c.jpg".
    return m.group(1) + '/' + u.lstrip('/')


def from_ld(body):
    """The image out of the structured product record, however it is nested."""
    for block in LD.findall(body)[:6]:
        try:
            data = json.loads(block.strip())
        except Exception:
            continue
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, list):
                stack.extend(node)
            elif isinstance(node, dict):
                if 'image' in node:
                    v = node['image']
                    if isinstance(v, str):
                        return v
                    if isinstance(v, list) and v:
                        first = v[0]
                        if isinstance(first, str):
                            return first
                        if isinstance(first, dict) and first.get('url'):
                            return first['url']
                    if isinstance(v, dict) and v.get('url'):
                        return v['url']
                stack.extend(node.values())
    return ''


# A real web address: scheme, a host with a dot in it, and no whitespace.
#
# "starts with http" was the only test at first, and it let through
#   https:Liquid error (snippets/structured_data line 118): invalid url input
# which is a StriVectin page whose Shopify template failed and printed its own
# error message into the structured data. Rubbish in a source is normal. What
# made it dangerous is that it looked like a filled cell.
WELL_FORMED = re.compile(r'^https?://[^\s/?#]+\.[a-z]{2,}(?:[:/][^\s]*)?$', re.I)


def usable(u):
    return bool(u) and bool(WELL_FORMED.match(u)) and not NOT_A_PRODUCT.search(u)


def read_image(body, page_url):
    for rx in (OG, OG_REV, TW, IMGSRC):
        m = rx.search(body)
        if m:
            u = absolute(m.group(1), page_url)
            if usable(u):
                return u, rx is OG or rx is OG_REV
    u = absolute(from_ld(body), page_url)
    if usable(u):
        return u, False
    return '', False


def browser_headers(url):
    """
    The headers a real Chrome sends.

    Sending a Chrome user-agent and nothing else is the oldest tell there is.
    A browser also sends Accept-Language, the Sec-Fetch group, and
    Upgrade-Insecure-Requests, and bot protection of the Cloudflare kind
    checks for exactly that combination. The Lebanese shops are plain Shopify
    and never cared. skinsort refuses every request, which is what a
    protection layer looks like rather than what a rate limit looks like.

    This is not a way around a refusal to be scraped. It is sending an honest
    request properly formed, having previously sent a malformed one.
    """
    m = re.match(r'(https?://[^/]+)', url)
    origin = m.group(1) if m else ''
    return {
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                  'image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'sec-ch-ua': '"Chromium";v="124", "Not:A-Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Referer': origin + '/',
    }


def fetch_head(url):
    req = urllib.request.Request(url, headers=browser_headers(url))
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
        raw = r.read(HEAD_BYTES)
        enc = (r.headers.get('Content-Encoding') or '').lower()
        gz = enc == 'gzip'
    if enc == 'deflate':
        import zlib
        try:
            raw = zlib.decompress(raw)
        except Exception:
            try:
                raw = zlib.decompressobj(-zlib.MAX_WBITS).decompress(raw)
            except Exception:
                return ''
    if gz or raw[:2] == b'\x1f\x8b':
        try:
            raw = gzip.decompress(raw)
        except Exception:
            # a truncated gzip stream still decodes up to the cut
            try:
                d = gzip.zlib.decompressobj(gzip.zlib.MAX_WBITS | 16)
                raw = d.decompress(raw)
            except Exception:
                return ''
    return raw.decode('utf-8', 'replace')


# ===================================================================== data
with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


URLCOLS = ['product_url', 'retailer_urls', 'skinsort_url', 'ingredient_url',
           'skin_type_url']


def first_url(r):
    for c in URLCOLS:
        v = g(r, c)
        if v.startswith('http'):
            return v.split(',')[0].split(' ')[0].strip()
    return ''


def domain_of(u):
    m = re.match(r'https?://([^/]+)', str(u), re.I)
    return m.group(1).lower().replace('www.', '') if m else ''


if GENTLE:
    # WORKERS was 1 here, which was wrong. One worker does not mean "polite",
    # it means every shop waits behind every other shop, so 9,381 pages took
    # eight hours while each individual shop sat idle almost the whole time.
    #
    # Politeness belongs PER SHOP. Eight workers with a two second gap on each
    # shop is gentler on any single shop than the default was, and finishes in
    # about twenty minutes because the eight are working on eight different
    # shops at once.
    #
    # MAX_STRIKES is effectively removed as well. Retiring a shop after 40
    # failures is what turned 394 failed requests into 8,461 pages that were
    # never even tried.
    # GAP_MIN stays LOW. A floor of 1.5s would have held skinsort at that pace
    # too, 5,793 pages for 193 minutes, when skinsort never refused anything
    # and answers happily at a tenth of that. The high start is a cautious
    # opening, not a speed limit: a shop that keeps answering eases down to
    # GAP_MIN, and a shop that refuses is pushed straight to GAP_MAX.
    #
    # So the slow pace lands only on the shops that earned it.
    WORKERS, GAP_START, GAP_MIN, GAP_MAX, MAX_STRIKES = 8, 2.0, 0.1, 8.0, 10 ** 6

cache = json.load(open(CACHE, encoding='utf-8')) \
    if os.path.exists(CACHE) else {}
stale = [k for k, v in cache.items()
         if v.get('v', 0) < READER_VERSION and not v.get('image_url')]
for k in stale:
    del cache[k]

# --apply WRITES. It does not fetch.
#
# It used to do both, so every time the cache was banked the shops were asked
# for thousands more pages first. That is part of why they started refusing:
# an --apply that was meant to take two seconds went back out and hammered
# them again. Collecting and writing are separate actions and the flag now
# does only the one it is named after.
jobs = []
for r in ([] if APPLY else D):
    if g(r, 'image_url'):
        continue
    if LEBANON_FIRST and not g(r, 'source_category').startswith('Lebanese'):
        continue
    u = first_url(r)
    if ONLY and domain_of(u) != ONLY:
        continue
    if u and g(r, 'product_id') not in cache:
        jobs.append((g(r, 'product_id'), u))

# Spread the work across shops instead of hammering one at a time. The queue
# was in file order, which meant every worker sat on the same shop waiting out
# that shop's gap while 238 other shops went untouched. Interleaving lets the
# per-shop pacing run in parallel rather than in series.
_by_dom = collections.defaultdict(list)
for j in jobs:
    _by_dom[domain_of(j[1])].append(j)
_rr, jobs = list(_by_dom.values()), []
while any(_rr):
    for bucket in _rr:
        if bucket:
            jobs.append(bucket.pop())
if TEST:
    jobs = jobs[:TEST]

print('=' * 74)
print('  PRODUCT IMAGES')
print('=' * 74)
print(f'  products                 {len(D):,}')
print(f'  already have an image    {sum(1 for r in D if g(r, "image_url")):,}')
print(f'  cached from a past run   {len(cache):,}')
print(f'  to fetch now             {len(jobs):,}')
if APPLY:
    print('  --apply only writes what is already collected, it fetches nothing')
if ONLY:
    print(f'  restricted to            {ONLY}')
if stale:
    print(f'  {len(stale):,} earlier misses will be tried again')
print(f'  only the first {HEAD_BYTES//1000} KB of each page is downloaded, '
      f'because og:image is in the head')
if TEST:
    print(f'  (test run, nothing written)')
print()

lock = threading.Lock()
last_hit = collections.defaultdict(float)
gap = collections.defaultdict(lambda: GAP_START)
good = collections.Counter()
strikes = collections.Counter()
counts = collections.Counter()
why = collections.Counter()
why_by_shop = collections.defaultdict(collections.Counter)
q = queue.Queue()
for j in jobs:
    q.put(j)


def work():
    while True:
        try:
            pid, url = q.get_nowait()
        except queue.Empty:
            return
        d = domain_of(url)
        try:
            if strikes[d] >= MAX_STRIKES:
                with lock:
                    counts['shop unreachable, will retry next run'] += 1
                continue
            while True:
                with lock:
                    wait = last_hit[d] + gap[d] - time.time()
                    if wait <= 0:
                        last_hit[d] = time.time()
                        break
                time.sleep(min(wait, 0.4))
            try:
                body = fetch_head(url)
            except Exception as e:
                # WHAT KIND of failure this is decides what to do about it,
                # and the first version recorded only that one happened. When
                # every shop went unreachable there was no way to tell a
                # deliberate block from a slow network, so the fix was a
                # guess. The reason is now named.
                if isinstance(e, urllib.error.HTTPError):
                    kind = f'HTTP {e.code}'
                    blocked = e.code in (403, 429, 503)
                    gone = e.code in (404, 410)
                else:
                    kind = type(e).__name__
                    blocked = False
                    gone = False
                with lock:
                    why[kind] += 1
                    why_by_shop[d][kind] += 1
                    if gone:
                        cache[pid] = {'v': READER_VERSION, 'why': 'page gone'}
                        counts['page is gone'] += 1
                    else:
                        # A block needs a long pause, not a slightly longer
                        # one. Doubling from 0.4s cannot climb out of a
                        # refusal inside one run.
                        gap[d] = (GAP_MAX if blocked
                                  else min(gap[d] * 2, GAP_MAX))
                        good[d] = 0
                        strikes[d] += 1
                        counts['could not reach, will retry next run'] += 1
                continue
            with lock:
                strikes[d] = 0
                good[d] += 1
                if good[d] >= EASE_AFTER and gap[d] > GAP_MIN:
                    gap[d] = max(gap[d] * 0.7, GAP_MIN)
                    good[d] = 0
            img, is_og = read_image(body, url)
            with lock:
                cache[pid] = {'v': READER_VERSION, 'image_url': img,
                              'from': 'og:image' if is_og else 'another tag',
                              'domain': d}
                counts['found an image' if img else 'no usable image'] += 1
                counts['done'] += 1
                n = counts['done']
            if n % 50 == 0:
                with lock:
                    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
                with lock:
                    live = sorted(((gap[d2], d2) for d2 in gap
                                   if last_hit[d2]), reverse=True)[:3]
                pace = '  '.join(f'{d2.split(".")[0]} {gp:.2f}s'
                                 for gp, d2 in live)
                print(f'    {n:6,} / {len(jobs):,}   images '
                      f"{counts['found an image']:,}   pace: {pace}",
                      flush=True)
        finally:
            q.task_done()


def heartbeat(total, stop_evt, t0):
    """
    Say something every 15 seconds no matter what.

    Progress was only printed every 200 pages. When a shop stalls, 200 pages
    can take longer than anyone is willing to wait, so the run printed nothing
    at all and looked identical to a crash. A run that is struggling has to be
    able to say so.
    """
    last = -1
    while not stop_evt.wait(15):
        with lock:
            done = counts['done']
            found = counts['found an image']
            fails = counts['could not reach, will retry next run']
            live = sorted(((gap[d2], d2) for d2 in gap if last_hit[d2]),
                          reverse=True)[:3]
            top = dict(why.most_common(3))
        mins = (time.time() - t0) / 60
        rate = done / mins if mins else 0
        left = (total - done) / rate if rate > 0.01 else float('inf')
        pace = '  '.join(f'{d2.split(".")[0]} {gp:.2f}s' for gp, d2 in live)
        eta = f'{left:.0f} min left' if left != float('inf') else 'stalled'
        print(f'    [{mins:5.1f} min]  {done:6,}/{total:,}  images {found:,}  '
              f'failed {fails:,}  {rate:.0f}/min  {eta}', flush=True)
        if pace:
            print(f'               pace: {pace}', flush=True)
        if top and done == last:
            print(f'               nothing is getting through: {top}',
                  flush=True)
        last = done


if jobs:
    started = time.time()
    _stop_hb = threading.Event()
    threading.Thread(target=heartbeat,
                     args=(len(jobs), _stop_hb, started), daemon=True).start()
    ts = [threading.Thread(target=work, daemon=True) for _ in range(WORKERS)]
    try:
        for t in ts:
            t.start()
        for t in ts:
            t.join()
    except KeyboardInterrupt:
        print('\n  stopped, what was read is saved.')
    _stop_hb.set()
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
    n = counts['done'] or 1
    print(f'\n  {counts["done"]:,} pages read in '
          f'{(time.time()-started)/60:.1f} minutes')
    for k, v in counts.most_common():
        if k != 'done':
            print(f'     {v:6,}  {k}')
    print(f'  hit rate {100*counts["found an image"]/n:.0f}%')

    if why:
        print('\n  WHY REQUESTS FAILED')
        for k, v in why.most_common(8):
            meaning = {
                'HTTP 403': 'the shop is refusing this computer',
                'HTTP 429': 'the shop says you are asking too often',
                'HTTP 503': 'the shop is overloaded or shielding itself',
                'timeout': 'no answer in time',
                'TimeoutError': 'no answer in time',
                'socket.timeout': 'no answer in time',
                'URLError': 'could not connect at all',
                'ConnectionResetError': 'the shop cut the connection',
                'RemoteDisconnected': 'the shop hung up',
            }.get(k, '')
            print(f'     {v:6,}  {k:24s} {meaning}')
        blocked = sum(v for k, v in why.items()
                      if k in ('HTTP 403', 'HTTP 429', 'HTTP 503'))
        if blocked > sum(why.values()) * 0.5:
            print('\n  MOST FAILURES ARE REFUSALS, NOT NETWORK TROUBLE.')
            print('  These shops have been asked a great deal today and are')
            print('  now turning this computer away. Waiting an hour or two')
            print('  costs nothing and usually clears it. Running again')
            print('  straight away will not, and only confirms the block.')
            print('  When you do come back, use:  --gentle')
        elif blocked:
            print(f'\n  {blocked:,} of the failures were outright refusals.')

    got = [c for c in cache.values() if c.get('image_url')]
    by_shop = collections.Counter(c.get('domain', '') for c in got)
    if by_shop:
        print('\n  BY SHOP')
        for d, k in by_shop.most_common(8):
            print(f'     {k:6,}  {d}')
    print('\n  THREE OF THE IMAGES')
    for c in got[:3]:
        print(f'     {c["image_url"][:96]}')

if TEST:
    print('\n  test run, nothing written.')
    sys.exit(0)
if not APPLY:
    n_img = sum(1 for c in cache.values() if c.get('image_url'))
    print(f'\n  {n_img:,} images waiting. write them in with:')
    print('     py fetch_product_images.py --apply')
    sys.exit(0)

# ------------------------------------------------------------------- apply
for c in ('image_url', 'image_source'):
    if c not in FIELDS:
        FIELDS.append(c)
by_id = {g(r, 'product_id'): r for r in D}
n_w = n_https = 0
for pid, c in cache.items():
    r = by_id.get(pid)
    img = (c or {}).get('image_url', '')
    if not r or not img or g(r, 'image_url'):
        continue
    if not usable(img):               # checked again at write time
        continue
    # Upgrade http to https.
    #
    # Where a page was served over http and named its image with a relative
    # path, the absolute URL inherited that scheme. An http image on an https
    # page is blocked by every browser as mixed content, so those pictures
    # would silently fail to load in the one setting this column exists for.
    #
    # Done here rather than at collection so that images already gathered are
    # corrected too, without re-fetching a single page.
    if img.startswith('http://'):
        img = 'https://' + img[len('http://'):]
        n_https += 1
    r['image_url'] = img
    r['image_source'] = c.get('from', '')
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
if n_https:
    print(f'  {n_https:,} were upgraded from http to https so they will not '
          f'be blocked as mixed content')
print(f'  images now {tot:,} of {len(D):,} ({100*tot/len(D):.1f}%)')
print('\n  now rebuild the tidy file:')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
