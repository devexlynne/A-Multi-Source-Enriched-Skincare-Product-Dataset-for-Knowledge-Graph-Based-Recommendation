"""
Formulas from the brand's own site

Why this one is different from the last three attempts
  Reading the retailer's page failed because roughly half of Lebanese shop
  listings carry no ingredient declaration. Borrowing from a twin row in the
  dataset failed because the merge had already found the real twins.

  Both of those asked a SHOP. This asks the MANUFACTURER, which is the party
  legally responsible for the ingredient declaration under EU Regulation
  1223/2009 Article 19. L'Oreal publishes the formula for a L'Oreal product
  even when the Lebanese pharmacy reselling it does not.

Usage:
    py fill_ingredients_brand_sites.py --test 40    measure the hit rate, write nothing
    py fill_ingredients_brand_sites.py              the whole 545
    py fill_ingredients_brand_sites.py --apply      write what was found into the data
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
import ssl
import sys
import json
import gzip
import time
import queue
import threading
import collections
import urllib.request
import unicodedata

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
DOMAINS = 'brand_domains.json'
PROGRESS = 'brand_site_ingredients.csv'
WORKERS = 4
TIMEOUT = 20

APPLY = '--apply' in sys.argv
TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 40

# ---------------------------------------------------------------- the keys
# These are the keys already in the project. A spent key is detected and the
# next one is used. If they are all spent the run says so plainly rather than
# reporting every product as having no formula, which is the failure that
# once produced a false finding about Lebanese products.
KEYS = _keys_from_env()

REJECT = re.compile(
    r'(incidecoder|skinsort|skincarisma|cosdna|beautypedia|skinwis|gopicky|'
    r'dermapproved|skinsafeproducts|ewg\.org|thinkdirty|yuka\.io|'
    r'allure|byrdie|refinery29|cosmopolitan|vogue|glamour|buzzfeed|'
    r'poshmark|mercari|depop|vinted|instagram|facebook|tiktok|reddit|youtube|'
    r'pinterest|quora|twitter|x\.com|ebay|aliexpress|etsy|dhgate|alibaba|'
    r'linkedin|blogspot|wordpress\.com|medium\.com|wikipedia|google\.)', re.I)

IN_SCOPE = re.compile(
    r"(?i)^(l'?or[eé]al|garnier|uriage|nuxe|lierac|shiseido|vichy|la roche|"
    r"bioderma|avene|av[eè]ne|eucerin|cerave|neutrogena|nivea|olay|clinique|"
    r"est[eé]e|lanc[oô]me|revuele|soskin|the ordinary|cetaphil|svr|ducray|"
    r"filorga|caudalie|klorane|mustela|isdin|sesderma|noreva|topicrem|a-derma)")

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


# --------------------------------------------- the reader, borrowed not copied
# Imported from fill_gaps_from_pages.py by slicing out its function section, so
# there is exactly one definition of what counts as a formula in this project.
# Copying it would let the two drift apart, and a change to one would silently
# stop applying to the other.
_src = open('fill_gaps_from_pages.py', encoding='utf-8').read()
_head = _src.split('# ------------------------------------------------------'
                   '--------- the data')[0]
_ns = {}
exec(compile(_head, 'reader', 'exec'), _ns)
read_ingredients = _ns['read_ingredients']
looks_like_a_formula = _ns['looks_like_a_formula']
strip_html = _ns['strip_html']


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore') \
        .decode().lower()


def bkey(b):
    return re.sub(r'[^a-z0-9]', '', asc(b))


SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)


def clean_name(n):
    return re.sub(r'\s{2,}', ' ', SIZE.sub(' ', str(n))).strip(' -,')


# ------------------------------------------------------------------- serper
_ki, _lock = [0], threading.Lock()
_spent = [0]
_dead = threading.Event()


def serper(q):
    while True:
        with _lock:
            if _ki[0] >= len(KEYS):
                _dead.set()
                return []
            k = KEYS[_ki[0]]
        body = json.dumps({'q': q, 'num': 10}).encode()
        req = urllib.request.Request(
            'https://google.serper.dev/search', data=body,
            headers={'X-API-KEY': k, 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
                data = json.loads(r.read().decode('utf-8', 'replace'))
        except urllib.error.HTTPError as e:
            if e.code in (400, 401, 402, 403, 429):
                with _lock:
                    if _ki[0] < len(KEYS) and KEYS[_ki[0]] == k:
                        print(f'   key ...{k[-6:]} is spent (HTTP {e.code}), '
                              f'moving to the next one', flush=True)
                        _ki[0] += 1
                continue
            return []
        except Exception:
            return []
        with _lock:
            _spent[0] += 1
        return [o.get('link', '') for o in data.get('organic', []) if o.get('link')]


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA, 'Accept-Encoding': 'gzip',
        'Accept': 'text/html,application/xhtml+xml'})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=CTX) as r:
        raw = r.read(3_000_000)
        if r.headers.get('Content-Encoding') == 'gzip':
            raw = gzip.decompress(raw)
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

done = {}
if os.path.exists(PROGRESS):
    with open(PROGRESS, newline='', encoding='utf-8') as fh:
        for row in csv.DictReader(fh):
            done[row['product_id']] = row

need = [r for r in D
        if not g(r, 'ingredients') and IN_SCOPE.match(g(r, 'brand'))
        and g(r, 'product_id') not in done]

print('=' * 74)
print('  FORMULAS FROM THE BRAND\'S OWN SITE')
print('=' * 74)
print(f'  products with no formula, in scope   {len(need):,}')
print(f'  already asked in an earlier run      {len(done):,}')
brands = collections.Counter(g(r, 'brand') for r in need)
have_dom = sum(1 for b in brands if bkey(b) in SITES)
print(f'  brands                               {len(brands)}, '
      f'{have_dom} with a domain already resolved')
if TEST:
    need = need[:TEST]
    print(f'  (test run, {TEST} products, nothing is written to the dataset)')
print()

pf = open(PROGRESS, 'a', newline='', encoding='utf-8')
pw = csv.DictWriter(pf, ['product_id', 'ingredients', 'ingredient_source',
                         'ingredient_url'])
if pf.tell() == 0:
    pw.writeheader()

counts = collections.Counter()
q = queue.Queue()
for r in need:
    q.put(r)


def resolve_domain(brand):
    bk = bkey(brand)
    with _lock:
        if bk in SITES:
            return SITES[bk]
    for link in serper(f'{brand} official site skincare'):
        if REJECT.search(link):
            continue
        m = re.match(r'https?://([^/]+)', link)
        if m:
            d = m.group(1).replace('www.', '')
            with _lock:
                SITES[bk] = d
            return d
    return ''


def work():
    while True:
        try:
            r = q.get_nowait()
        except queue.Empty:
            return
        try:
            if _dead.is_set():
                return
            brand, name = g(r, 'brand'), clean_name(g(r, 'name'))
            dom = resolve_domain(brand)

            links = []
            if dom:
                links = serper(f'site:{dom} {name} ingredients')
            if not links:
                links = [u for u in serper(f'{brand} {name} ingredients INCI')
                         if not REJECT.search(u)]
            links = [u for u in links if not REJECT.search(u)][:3]

            found, src = '', ''
            for u in links:
                try:
                    txt = strip_html(fetch(u))
                except Exception:
                    continue
                ing = read_ingredients(txt)
                if ing and looks_like_a_formula(ing):
                    found, src = ing, u
                    break

            with _lock:
                if found:
                    counts['found'] += 1
                    on_brand = dom and dom in src
                    pw.writerow({
                        'product_id': g(r, 'product_id'),
                        'ingredients': found,
                        'ingredient_source':
                            "the brand's own site" if on_brand
                            else 'a retailer repeating the label',
                        'ingredient_url': src})
                else:
                    counts['nothing'] += 1
                counts['done'] += 1
                n = counts['done']
                if n % 25 == 0:
                    pf.flush()
                    print(f'    {n:5,} / {len(need):,}   found '
                          f"{counts['found']:,}   credits {_spent[0]:,}",
                          flush=True)
        finally:
            q.task_done()


started = time.time()
ts = [threading.Thread(target=work, daemon=True) for _ in range(WORKERS)]
try:
    for t in ts:
        t.start()
    for t in ts:
        t.join()
except KeyboardInterrupt:
    print('\n  stopped. everything found so far is saved.')
pf.flush()
pf.close()
json.dump(SITES, open(DOMAINS, 'w', encoding='utf-8'))

n = counts['done'] or 1
print(f'\n  {counts["done"]:,} products asked in '
      f'{(time.time() - started) / 60:.1f} minutes')
print(f'  found a formula   {counts["found"]:,}  '
      f'({100 * counts["found"] / n:.0f}%)')
print(f'  credits spent     {_spent[0]:,}')
if _dead.is_set():
    print('\n  EVERY KEY IS SPENT. The products asked after that point were')
    print('  not really asked, so do not read them as having no formula.')

if TEST:
    print('\n  test run, nothing written. if the rate is worth it, run again')
    print('  without --test.')
    sys.exit(0)
if not APPLY:
    print(f'\n  {len(done) + counts["found"]:,} formulas are waiting in '
          f'{PROGRESS}')
    print('  write them in with:   py fill_ingredients_brand_sites.py --apply')
    sys.exit(0)

# ------------------------------------------------------------------- apply
got = {}
with open(PROGRESS, newline='', encoding='utf-8') as fh:
    for row in csv.DictReader(fh):
        if row.get('ingredients'):
            got[row['product_id']] = row

n_w = 0
for r in D:
    row = got.get(g(r, 'product_id'))
    if not row or g(r, 'ingredients'):
        continue
    ing = row['ingredients']
    if not looks_like_a_formula(ing):     # checked again at write time
        continue
    r['ingredients'] = ing
    if 'ingredient_count' in r:
        r['ingredient_count'] = str(len([p for p in re.split(r'[,;]', ing)
                                         if p.strip(' .;:-')]))
    if 'ingredient_source' in r:
        r['ingredient_source'] = row.get('ingredient_source', '')
    if 'ingredient_url' in r:
        r['ingredient_url'] = row.get('ingredient_url', '')
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

tot = sum(1 for r in D if g(r, 'ingredients'))
print(f'\n  written {n_w:,} formulas')
print(f'  ingredients now {tot:,} of {len(D):,} ({100 * tot / len(D):.1f}%)')
print('\n  now rebuild what is computed from the formula:')
print('     py derive_from_ingredients.py')
print('     py fill_from_formula.py')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
