"""
Ingredients and skin type, read off the product's own page

Why this and not a paid search
  Every product still missing an ingredient list already has a URL in the
  dataset. That URL is the page the product was collected from. Asking a
  search API to find a page we are already holding the address of would be
  paying for something we have.

Usage:
    py fill_gaps_from_pages.py --test 40      look at 40 pages, change nothing
    py fill_gaps_from_pages.py                the whole backlog
    py fill_gaps_from_pages.py --apply        write what was found into the data
"""
import os
import re
import csv
import sys
import ssl
import json
import time
import html
import gzip
import queue
import threading
import collections
import urllib.request
import urllib.error
import unicodedata

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
CACHE = 'page_fill_cache.json'
READER_VERSION = 3        # raise this whenever the reading rules below change
WORKERS = 16
TIMEOUT = 20

# MEASURED. At 32 workers starting at 0.15s, 2,050 of 3,349 pages were never
# fetched at all: the shops began refusing, each burned through its strike
# limit within seconds, and was abandoned for the rest of the run. The
# slowdown below could not save a shop because the strike limit fired first.
#
# So the limit is now high enough that a shop is only given up on when it is
# genuinely unreachable, and the gap it starts at is one a small shop can
# actually take. Slower per request, but it reads the pages instead of
# skipping two thirds of them.
MAX_STRIKES = 40          # a domain that fails this often is left alone

# The pace is set PER SHOP and it adjusts itself.
#
# A fixed gap has to be chosen for the most fragile shop in the list, which
# then punishes every sturdy one. Since a single shop, sohaticare, holds a
# quarter of all the pages, that one choice decided the whole runtime.
#
# So each shop starts fast. A failed request doubles that shop's gap, a run of
# successes eases it back down. A shop that cannot take the pace slows itself
# and nothing else slows with it.
# The Shopify shortcut is fast but it only sees the product description. If a
# shop keeps its formula somewhere else on the page, the shortcut will miss it
# and report the product as having none, which is the worst kind of wrong: it
# looks like an answer. check_shopify_json.py asks the same pages both ways
# and says which is happening. Set this to False if it says the shortcut loses.
# MEASURED AND TURNED OFF. check_shopify_json.py asked 8 pages both ways. On
# the single page of the 8 that publishes a formula, the full page found it
# and the JSON did not. The description field these shops fill in does not
# contain the formula, so the shortcut was reporting "no ingredients" for
# products that do list them. Speed is not worth an answer that is wrong.
USE_SHOPIFY_JSON = False

GAP_START = 0.4
GAP_MIN = 0.25
GAP_MAX = 4.0
EASE_AFTER = 10           # consecutive successes before speeding back up

APPLY = '--apply' in sys.argv

# --peek saves the pages that gave nothing, so the reason can be looked at
# instead of guessed at. A low hit rate has several possible causes and they
# need different fixes: the shop may build the page in the browser so there is
# nothing in the HTML at all, or it may publish the formula under a heading
# this script does not recognise, or it may simply not publish one. Those look
# identical from the outside. This mode tells them apart.
PEEK = 0
if '--peek' in sys.argv:
    i = sys.argv.index('--peek')
    PEEK = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 12
PEEK_DIR = 'peek_pages'
peeked = collections.Counter()

TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 40

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE   # some Lebanese shops have expired certs


# ---------------------------------------------------------------- helpers
def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode()


def domain_of(url):
    m = re.match(r'https?://([^/]+)', str(url).strip(), re.I)
    return m.group(1).lower().replace('www.', '') if m else ''


CHEM = re.compile(
    r'\b(aqua|water|glycerin|glycerine|acid|sodium|potassium|extract|oil|'
    r'alcohol|butter|glycol|phenoxyethanol|tocopherol|parfum|fragrance|'
    r'dimethicone|niacinamide|panthenol|xanthan|citrate|benzoate|sorbate|'
    r'seed|leaf|fruit|root|hydroxide|stearate|behenate|cetearyl|ceteareth|'
    r'polysorbate|carbomer|allantoin|squalane|ci\s?\d{5})\b', re.I)


def looks_like_a_formula(text):
    """A list of ingredients, not a paragraph about one."""
    t = str(text).strip().strip('.;: ')
    if len(t) < 40 or len(t) > 12000:
        return False
    parts = [p.strip() for p in re.split(r'[,;]', t) if p.strip()]
    if len(parts) < 5:
        return False
    if sum(1 for p in parts if len(p) < 46) / len(parts) < 0.75:
        return False
    if sum(1 for p in parts if CHEM.search(p)) < 3:
        return False
    # a formula is mostly ingredient names, not sentences
    if sum(1 for p in parts if p.count(' ') > 6) > len(parts) * 0.25:
        return False
    return True


# labels a shop puts in front of a formula
ING_LABEL = re.compile(
    r'(?:^|[>\n\r\.\|])\s*'
    r'(?:full\s+)?(?:ingredients?|ingr[eé]dients?|inci|composition|'
    r'what[\'’]?s\s+in\s+it|key\s+ingredients?\s*list)'
    r'\s*[:\-–]?\s*', re.I)

SKIN_LABEL = re.compile(
    r'(?:skin\s*type|skin\s*concern|suitable\s+for|recommended\s+for|'
    r'pour\s+peau|type\s+de\s+peau)\s*[:\-–]\s*([^\.\n\r<\|]{2,70})', re.I)

SKIN_WORDS = {
    'dry': 'Dry', 'dehydrated': 'Dry',
    'oily': 'Oily', 'greasy': 'Oily',
    'combination': 'Combination', 'combo': 'Combination', 'mixte': 'Combination',
    'normal': 'Normal',
    'sensitive': 'Sensitive', 'sensible': 'Sensitive', 'reactive': 'Sensitive',
    'all skin': 'All', 'all types': 'All', 'every skin': 'All',
    'tous types': 'All', 'all': 'All',
}


def strip_html(raw):
    s = re.sub(r'(?is)<(script|style|noscript)[^>]*>.*?</\1>', ' ', raw)
    s = re.sub(r'(?i)<br\s*/?>|</p>|</div>|</li>|</tr>', '\n', s)
    s = re.sub(r'<[^>]+>', ' ', s)
    s = html.unescape(s)
    s = s.replace(' ', ' ')
    return re.sub(r'[ \t]{2,}', ' ', s)


STOP_HEADING = re.compile(
    r'(?i)\b(directions?|how to use|warnings?|caution|benefits?|size|volume|'
    r'made in|shipping|delivery|payment|reviews?|related products?|'
    r'you may also like|add to cart|share this|pickup|refresh|'
    r'about (us|the brand)|why we love|description)\b')


def looks_like_an_ingredient(part):
    """
    One entry in an INCI list, judged on shape.

    An INCI entry is a NAME. It is short, it has few words, and it carries no
    sentence machinery. "Sodium Cocoyl Isethionate" is one. "It gently soothes
    and cleanses upset and irritated skin" is not, and neither is "Free
    Shipping over $30". Judging entries one at a time is what lets the list be
    cut at the exact point the page stops listing and starts selling.
    """
    p = part.strip(' \t.;:-*•·')
    if not (2 <= len(p) <= 70):
        return False
    words = p.split()
    if len(words) > 8:
        return False
    if re.search(r'(?i)\b(the|is|are|was|we|our|your|you|this|that|it|and '
                 r'then|with a|for a|can be|will|please|click|shop|buy|'
                 # instructions sit right next to the formula on most shop
                 # pages, and "Rinse with clean water" is short enough and
                 # plain enough to pass every other test here
                 r'rinse|apply|massage|smooth|spread|leave on|wash|cleanse|'
                 r'avoid|keep out|store|shake|repeat|follow|suitable|ideal|'
                 r'helps?|reduces?|soothes?|hydrates?|protects?)\b', p):
        # "and", "of", "in" are fine inside names like "Oil of Rose", so only
        # pronouns, verbs and instructions are refused
        return False
    if re.search(r'[$€£%]|\d+\s*(ml|g|oz|off|aed|usd|lbp)\b', p, re.I):
        return False
    if STOP_HEADING.search(p):
        return False
    return True


def harvest(seq):
    """Walk parts, keep listing, stop when the page stops listing."""
    kept, misses = [], 0
    for part in seq:
        if looks_like_an_ingredient(part):
            kept.append(part.strip(' \t.;:-*•·'))
            misses = 0
        else:
            misses += 1
            if misses >= 2 and len(kept) >= 5:
                break          # two non-entries in a row: the list has ended
            if misses >= 4:
                break
    return kept


def read_ingredients(text):
    """
    Take the text after an "Ingredients" heading and walk it entry by entry.

    Three things about real shop pages forced this shape:

      Some shops separate entries with FULL STOPS, not commas. feel22 prints
      "WATER (AQUA). GLYCERIN. CETEARETH-60 MYRISTYL GLYCOL." with no comma
      anywhere, so a comma-only reader saw no list at all.

      Pages pad their markup, so the text after a heading often begins with
      blank lines. Cutting the block at the first blank line therefore
      returned an empty string and threw the formula away.

      The formula is usually followed by shipping banners and review widgets
      with no separator of any kind, so there is no boundary to cut at. The
      list has to be ended by noticing that the entries stopped being
      entries.
    """
    best = []
    for m in ING_LABEL.finditer(text):
        tail = re.sub(r'\s+', ' ', text[m.end(): m.end() + 8000]).strip()
        if not tail:
            continue
        # Which mark separates the entries cannot be decided by counting,
        # because prose sitting just before the formula brings its own commas
        # and full stops with it. Counting the head of the tail picked commas
        # for a feel22 page whose formula is separated by full stops, and the
        # whole list collapsed into one over-long entry and was thrown away.
        # So both are tried and the one that actually yields entries wins.
        for sep in (r'[,;]', r'[.;]', r'[,;.]'):
            kept = harvest(re.split(sep, tail))
            if len(kept) > len(best):
                best = kept
    if best:
        out = ', '.join(best)
        if looks_like_a_formula(out):
            return out
    # some shops print the formula with no heading in front of it at all
    for para in re.split(r'\n\s*\n', text):
        para = re.sub(r'\s+', ' ', para).strip()
        if re.match(r'(?i)^(aqua|water|ingredients)\b', para):
            kept = harvest(re.split(r'[,;]' if para.count(',') >= 4
                                    else r'[,;.]', para))
            out = ', '.join(kept)
            if looks_like_a_formula(out):
                return out
    return ''


def read_skin_type(text):
    """Only from a labelled field. A passing mention is not a claim."""
    for m in SKIN_LABEL.finditer(text):
        said = m.group(1).lower()
        found = []
        for word, label in SKIN_WORDS.items():
            if word == 'all':
                continue
            if re.search(r'\b' + re.escape(word), said):
                found.append(label)
        if re.search(r'\ball\s+(skin|types)', said) or 'tous types' in said:
            found.append('All')
        found = sorted(set(found))
        if found:
            return 'All' if found == ['All'] else ', '.join(
                f for f in found if f != 'All') or 'All'
    return ''


# --------------------------------------------------------------- the data
with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


URLCOLS = ['product_url', 'retailer_urls', 'skinsort_url', 'skin_type_url',
           'ingredient_url']


def first_url(r):
    for c in URLCOLS:
        v = g(r, c)
        if v.startswith('http'):
            return v.split(',')[0].split(' ')[0].strip()
    return ''


jobs = []
for r in D:
    want_ing = not g(r, 'ingredients')
    want_skin = not g(r, 'skin_type')
    if not (want_ing or want_skin):
        continue
    u = first_url(r)
    if u:
        jobs.append((g(r, 'product_id'), u, want_ing, want_skin))

cache = {}
if os.path.exists(CACHE):
    try:
        cache = json.load(open(CACHE, encoding='utf-8'))
    except Exception:
        cache = {}

# A page that gave nothing was judged by the reader as it stood that day. When
# the reader is improved, that judgement is out of date: the formula may have
# been on the page all along and simply not been recognised. So a "nothing"
# from an older reader is thrown away and the page is read again, while a
# page that DID give something is kept, because a hit does not go stale.
stale = [pid for pid, c in cache.items()
         if c.get('ok') and c.get('v', 0) < READER_VERSION
         and not c.get('ingredients') and not c.get('skin_type')]
for pid in stale:
    del cache[pid]
if stale:
    print(f'  the reader improved since the last run, so {len(stale):,} pages '
          f'that gave nothing will be read again')

todo = [j for j in jobs if j[0] not in cache]

# --worth-it: stop asking shops that have already been measured to publish
# nothing.
#
# The last full run read 948 pages and found 48 formulas. That average hides
# the real shape: some shops publish formulas and some publish none at all,
# and re-reading the second group is where nearly all the time went.
#
# So every shop already read enough times to judge is scored on what it
# actually gave, and the ones that gave nothing are dropped. A shop not yet
# sampled properly is always kept, because "no evidence" and "evidence of
# nothing" are different and only the second is a reason to stop.
if '--worth-it' in sys.argv:
    seen = collections.Counter()
    won = collections.Counter()
    for c in cache.values():
        if not c.get('ok'):
            continue
        d = c.get('domain', '')
        seen[d] += 1
        if c.get('ingredients') or c.get('skin_type'):
            won[d] += 1
    ENOUGH = 40          # pages before a shop can be judged at all
    FLOOR = 0.03         # below this it is not worth the time
    dead = {d for d, n in seen.items()
            if n >= ENOUGH and won[d] / n < FLOOR}
    before = len(todo)
    todo = [j for j in todo if domain_of(j[1]) not in dead]
    print(f'  --worth-it: {len(dead)} shops measured to publish nothing, '
          f'{before - len(todo):,} pages skipped')
    for d in sorted(dead, key=lambda x: -seen[x])[:8]:
        print(f'     dropped  {d:30s} {won[d]:3d} of {seen[d]:4d} pages gave '
              f'anything')
    keep = collections.Counter(domain_of(j[1]) for j in todo)
    print('  still asking:', ', '.join(
        f'{d} {n:,}' for d, n in keep.most_common(6)) or '(nothing left)')

if TEST:
    todo = todo[:TEST]

print('=' * 72)
print('  INGREDIENTS AND SKIN TYPE FROM THE PRODUCT PAGE ITSELF')
print('=' * 72)
print(f'  products in the file        {len(D):,}')
print(f'  with a gap and a URL        {len(jobs):,}')
print(f'  already fetched before      {len(cache):,}')
print(f'  to fetch now                {len(todo):,}')
if TEST:
    print(f'  (test run, {TEST} pages, nothing is written to the dataset)')
print(f'  {len(set(domain_of(j[1]) for j in todo)):,} different shops, each '
      f'starting at one request every {GAP_START}s and finding its own pace')
print()

if APPLY and not todo:
    pass
elif not todo:
    print('  nothing left to fetch. run with --apply to write it in.')

# ------------------------------------------------------------- the fetching
lock = threading.Lock()
last_hit = collections.defaultdict(float)
gap = collections.defaultdict(lambda: GAP_START)
good_run = collections.Counter()
strikes = collections.Counter()
counts = collections.Counter()
q = queue.Queue()
for j in todo:
    q.put(j)


SHOPIFY = re.compile(r'^(https?://[^/]+/(?:collections/[^/]+/)?products/[^/?#]+)',
                     re.I)


def shopify_json_url(url):
    """
    Most of these shops run Shopify, and Shopify serves the same product as
    JSON at the same address with .js on the end.

    This matters for speed more than anything else in the script. A sohaticare
    product page is 670 KB of HTML carrying a navigation menu, a brand list
    and a review widget, out of which a few hundred bytes are wanted. The .js
    version is a few KB and contains the description with the formula in it.

    It is also steadier to read, because it is the shop's own data rather than
    a rendered page whose layout can change.
    """
    m = SHOPIFY.match(str(url).strip())
    return m.group(1) + '.js' if m else ''


def text_from_shopify(raw):
    d = json.loads(raw)
    bits = [d.get('description') or d.get('body_html') or '']
    for v in (d.get('variants') or [])[:1]:
        bits.append(str(v.get('title') or ''))
    return strip_html('\n\n'.join(b for b in bits if b))


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,fr;q=0.7',
        'Accept-Encoding': 'gzip',
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as resp:
        raw = resp.read(3_000_000)
        if resp.headers.get('Content-Encoding') == 'gzip':
            raw = gzip.decompress(raw)
    return raw.decode('utf-8', 'replace')


def worker():
    while True:
        try:
            pid, url, want_ing, want_skin = q.get_nowait()
        except queue.Empty:
            return
        dom = domain_of(url)
        try:
            if strikes[dom] >= MAX_STRIKES:
                # NOT cached. If the shop was down, or my own connection
                # dropped, every product of that shop would otherwise be
                # written off permanently on one bad afternoon. Leaving it
                # uncached means the next run tries it again.
                with lock:
                    counts['shop was down, will retry next run'] += 1
                continue

            # hold the slot for this shop, at whatever pace this shop is on
            while True:
                with lock:
                    wait = last_hit[dom] + gap[dom] - time.time()
                    if wait <= 0:
                        last_hit[dom] = time.time()
                        break
                time.sleep(min(wait, 0.5))

            try:
                text = None
                jurl = shopify_json_url(url) if USE_SHOPIFY_JSON else ''
                if jurl:
                    # try the small JSON first, fall back to the page itself
                    try:
                        text = text_from_shopify(fetch(jurl))
                        if len(text) < 60:
                            text = None
                        else:
                            with lock:
                                counts['read as shopify json'] += 1
                    except Exception:
                        text = None
                    if text is None:
                        with lock:
                            last_hit[dom] = time.time()
                try:
                    page = '' if text is not None else fetch(url)
                except Exception:
                    # A failure is read as "too fast for this shop", because
                    # that is what it nearly always was: 180 of 300 pages
                    # failed at the old pace and the shops were plainly up.
                    # So this shop is slowed down, then the page is asked for
                    # once more rather than being written off.
                    with lock:
                        gap[dom] = min(gap[dom] * 2, GAP_MAX)
                        good_run[dom] = 0
                        backed_off = gap[dom]
                    time.sleep(min(backed_off * 2, 5))
                    with lock:
                        last_hit[dom] = time.time()
                    page = fetch(url)
            except Exception as e:
                # A 404 is a real answer: that page is gone, never ask again.
                # A timeout or a refused connection is not an answer about the
                # product, it is an answer about the network, so it is not
                # cached and the next run asks again.
                gone = isinstance(e, urllib.error.HTTPError) and \
                    e.code in (404, 410)
                with lock:
                    strikes[dom] = 0 if gone else strikes[dom] + 1
                    if gone:
                        cache[pid] = {'ok': False, 'why': 'page is gone'}
                        counts['page is gone'] += 1
                    else:
                        counts['could not reach, will retry next run'] += 1
                continue

            with lock:
                strikes[dom] = 0
                good_run[dom] += 1
                if good_run[dom] >= EASE_AFTER and gap[dom] > GAP_MIN:
                    gap[dom] = max(gap[dom] * 0.7, GAP_MIN)
                    good_run[dom] = 0
            if text is None:
                text = strip_html(page)
            rec = {'ok': True, 'url': url, 'domain': dom, 'v': READER_VERSION}
            if want_ing:
                ing = read_ingredients(text)
                if ing:
                    rec['ingredients'] = ing
            if want_skin:
                st = read_skin_type(text)
                if st:
                    rec['skin_type'] = st
            with lock:
                cache[pid] = rec
                if 'ingredients' in rec:
                    counts['found a formula'] += 1
                if 'skin_type' in rec:
                    counts['found a skin type'] += 1
                if 'ingredients' not in rec and 'skin_type' not in rec:
                    counts['page had neither'] += 1
                    rec['text_len'] = len(text)
                    rec['had_the_word'] = bool(ING_LABEL.search(text))
                    # keep a few, per shop, to look at afterwards
                    if PEEK and peeked[dom] < PEEK:
                        peeked[dom] += 1
                        os.makedirs(PEEK_DIR, exist_ok=True)
                        safe = re.sub(r'[^a-z0-9]+', '_', dom)
                        with open(os.path.join(
                                PEEK_DIR, f'{safe}_{peeked[dom]}.txt'),
                                'w', encoding='utf-8') as fh:
                            fh.write(f'URL: {url}\n')
                            fh.write(f'HTML BYTES: {len(page):,}\n')
                            fh.write(f'READABLE TEXT: {len(text):,}\n')
                            fh.write('=' * 70 + '\n')
                            fh.write(text[:20000])
        finally:
            q.task_done()
            with lock:
                counts['done'] += 1
                n = counts['done']
            if n % 100 == 0:
                with lock:
                    snap = dict(counts)
                    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
                print(f'    {n:6,} / {len(todo):,}   '
                      f"formulas {snap.get('found a formula', 0):,}   "
                      f"skin types {snap.get('found a skin type', 0):,}   "
                      f"nothing {snap.get('page had neither', 0):,}   "
                      f"dead {snap.get('page would not load', 0):,}", flush=True)


if todo:
    ts = [threading.Thread(target=worker, daemon=True) for _ in range(WORKERS)]
    started = time.time()
    try:
        for t in ts:
            t.start()
        for t in ts:
            t.join()
    except KeyboardInterrupt:
        print('\n  stopped. what was fetched is saved, run again to carry on.')
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
    print(f'\n  {counts["done"]:,} pages read in '
          f'{(time.time() - started) / 60:.1f} minutes')
    for k, v in counts.most_common():
        if k != 'done':
            print(f'     {v:6,}  {k}')

    # why the empty ones were empty
    empties = [c for c in cache.values()
               if c.get('ok') and not c.get('ingredients')
               and not c.get('skin_type')]
    if empties:
        thin = sum(1 for c in empties if c.get('text_len', 9999) < 1200)
        said_word = sum(1 for c in empties if c.get('had_the_word'))
        print(f'\n  OF THE {len(empties):,} PAGES THAT GAVE NOTHING')
        print(f'     {thin:6,}  had almost no readable text, so the shop '
              f'builds the page in the browser')
        print(f'     {said_word:6,}  did print the word ingredients, but what '
              f'followed did not read as a formula')
        print(f'     {len(empties) - thin - said_word:6,}  simply do not '
              f'publish one')
        by_shop = collections.Counter(c.get('domain', '') for c in empties)
        print('     worst shops:', ', '.join(
            f'{d} {n:,}' for d, n in by_shop.most_common(5)))

    hits = [c for c in cache.values() if c.get('ingredients')]
    if hits:
        print('\n  THREE OF THE FORMULAS THAT CAME BACK')
        for c in hits[:3]:
            print(f'    {c.get("domain", "")}')
            print(f'      {c["ingredients"][:110]}...')

# ------------------------------------------------------------------ apply
if not APPLY:
    n_i = sum(1 for c in cache.values() if c.get('ingredients'))
    n_s = sum(1 for c in cache.values() if c.get('skin_type'))
    print(f'\n  waiting to be written in: {n_i:,} formulas, {n_s:,} skin types')
    print('  nothing was changed. when the run finishes:')
    print('     py fill_gaps_from_pages.py --apply')
    sys.exit(0)

TIER = {}   # domain -> is this the brand's own site
brand_domains = set()
for r in D:
    b = re.sub(r'[^a-z0-9]', '', asc(g(r, 'brand')).lower())
    if b:
        brand_domains.add(b)


def tier_for(dom, brand):
    b = re.sub(r'[^a-z0-9]', '', asc(brand).lower())
    root = re.sub(r'[^a-z0-9]', '', dom.split('.')[0])
    if b and root and (b in root or root in b):
        return "tier 1, the brand's own site"
    return 'tier 2, a retailer page'


by_id = {g(r, 'product_id'): r for r in D}
n_ing = n_skin = n_ambiguous = 0
for pid, c in cache.items():
    r = by_id.get(pid)
    if not r or not c.get('ok'):
        continue
    if c.get('ingredients') and not g(r, 'ingredients'):
        ing = c['ingredients']
        if not looks_like_a_formula(ing):       # checked again at write time
            continue
        r['ingredients'] = ing
        if 'ingredient_count' in r:
            r['ingredient_count'] = str(len([p for p in re.split(r'[,;]', ing)
                                             if p.strip(' .;:-')]))
        if 'ingredient_source' in r:
            r['ingredient_source'] = f"read from {c.get('domain', 'the product page')}"
        n_ing += 1
    if c.get('skin_type') and not g(r, 'skin_type'):
        # This dataset keeps ONE skin type per product, with sensitivity in
        # its own column. A page often states several, and writing them back
        # joined by commas put "Combination, Oily" into a column whose only
        # legal values are single ones. Two rows got through that way and the
        # validator caught them.
        #
        # So the page's answer is split apart:
        #   Sensitive is not a skin type here, it is the sensitivity column
        #   one base type left  -> use it
        #   two or more left    -> the page did not decide, and neither will
        #                          this. Guessing between Combination and Oily
        #                          would be inventing a fact the source never
        #                          stated.
        parts = [p.strip() for p in str(c['skin_type']).split(',') if p.strip()]
        sensitive = any(p.lower() == 'sensitive' for p in parts)
        base = [p for p in parts if p.lower() != 'sensitive']
        if sensitive and 'sensitivity' in r and not g(r, 'sensitivity'):
            r['sensitivity'] = 'Sensitive'
        if len(base) == 1:
            r['skin_type'] = base[0]
            # EVERY provenance column has to be filled together. Writing
            # skin_type_source but not skin_type_tier left one row with a skin
            # type and no strength recorded against it, which the validator
            # caught. The tier columns are what the whole skin type argument
            # rests on, so a value without them is worse than no value.
            own = tier_for(c.get('domain', ''), g(r, 'brand'))
            is_brand = own.startswith('tier 1')
            if 'skin_type_source' in r:
                r['skin_type_source'] = own
            if 'skin_type_tier' in r:
                r['skin_type_tier'] = '1' if is_brand else '2'
            if 'skin_type_authority' in r:
                r['skin_type_authority'] = ('manufacturer' if is_brand
                                            else 'retailer')
            if 'skin_type_status' in r and not g(r, 'skin_type_status'):
                r['skin_type_status'] = 'stated on the page'
            if 'skin_type_url' in r and not g(r, 'skin_type_url'):
                r['skin_type_url'] = c.get('url', '')
            n_skin += 1
        elif len(base) > 1:
            n_ambiguous += 1

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

tot = len(D)
print(f'\n  written in')
print(f'     {n_ing:,} ingredient lists')
print(f'     {n_skin:,} skin types')
if n_ambiguous:
    print(f'     {n_ambiguous:,} pages named two skin types and were left '
          f'empty rather than guessed at')
print(f'\n  ingredients now  '
      f'{sum(1 for r in D if g(r, "ingredients")):,} / {tot:,}')
print(f'  skin type now    '
      f'{sum(1 for r in D if g(r, "skin_type")):,} / {tot:,}')
print('\n  now rebuild everything computed from the formula:')
print('     py derive_from_ingredients.py')
print('     py fill_from_formula.py')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
