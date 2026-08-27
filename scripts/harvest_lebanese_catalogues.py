"""
Pull the whole catalogue from every discovered lebanese brand

COSTS NOTHING. No search credits are used here at all. Discovery found the
websites; this reads them.

Three ways in, tried in order
  1. THE SHOPIFY PRODUCT FEED.  <site>/products.json?limit=250&page=N
     Most small Lebanese brands run Shopify, and every Shopify store exposes
     this endpoint publicly. It is not scraping HTML, it is a documented JSON
     feed, and it returns 250 products per request with

         title, vendor, product_type, tags, variants[].price
         body_html   which very often contains the full ingredient list

Usage:
    py harvest_lebanese_catalogues.py
    py harvest_lebanese_catalogues.py --limit 5    try the first 5 sites only
"""
import os
import re
import csv
import sys
import json
import html as htmllib
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

BRANDS = 'lebanese_brands_discovered.csv'
OUT = 'lebanese_origin_harvested.csv'
WORKERS = 6
TIMEOUT = 25
LIMIT = 0
if '--limit' in sys.argv:
    i = sys.argv.index('--limit')
    LIMIT = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 5

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'}
FIELDS = ['brand', 'name', 'product_type', 'price', 'currency', 'product_url',
          'ingredients', 'skin_type', 'description', 'domain', 'method']

TAG = re.compile(r'<[^>]+>')
INCI_WORDS = re.compile(
    r'\b(aqua|water|glycerin|glycerine|alcohol denat|butylene glycol|'
    r'propylene glycol|sodium|potassium|cetearyl|stearyl|cetyl|dimethicone|'
    r'phenoxyethanol|tocopherol|parfum|fragrance|citric acid|xanthan|carbomer|'
    r'panthenol|niacinamide|extract|seed oil|butter|acid|polysorbate|laureth|'
    r'glyceryl|caprylic|triglyceride|benzoate|sorbate|olea europaea|'
    r'laurus nobilis|rosa damascena)\b', re.I)
START_OK = re.compile(r'^\s*(aqua|water|eau|glycerin|alcohol|olea|cocos|butyrospermum|'
                      r'simmondsia|prunus|helianthus|sodium|potassium|cetearyl|'
                      r'dimethicone|butylene|propylene|caprylic|zinc oxide|'
                      r'titanium dioxide|laurus|olive oil|shea)', re.I)
LEADIN = re.compile(r'\b(?:full\s+|main\s+|key\s+|active\s+)?'
                    r'(?:ingredients?|inci|composition|contents|مكونات)\b\s*[:\-–]?\s*', re.I)
INSTRUCTION = re.compile(r'\b(apply|rinse|massage|leave on|caution|for external use|'
                         r'avoid contact|patch test|shake well|store in)\b', re.I)
BAD = re.compile(r'(add to (cart|bag)|<script|window\.|cookie|shipping|'
                 r'return policy|newsletter)', re.I)
SKINTYPE = re.compile(r'\b(dry|oily|combination|normal|sensitive|all)[\s-]*skin',
                      re.I)
PRODUCT_URL = re.compile(r'/(products?|product|shop|item|p)/[a-z0-9\-_%]{3,}', re.I)


def clean(t):
    return re.sub(r'\s+', ' ', htmllib.unescape(TAG.sub(' ', str(t)))).strip(' :.-•|')


def looks_like_inci(t):
    if not t or len(t) < 40 or len(t) > 6000 or BAD.search(t) or t.count(',') < 2:
        return False
    hits = len(INCI_WORDS.findall(t))
    if hits < 2:
        return False
    parts = [p.strip() for p in t.split(',') if p.strip()]
    if len(parts) < 3:
        return False
    if sum(1 for p in parts if len(p.split()) > 7) > len(parts) * 0.45:
        return False
    return bool(START_OK.match(t)) or hits >= 4


def find_inci(text):
    """Trim to where the formula begins. Prose that merely mentions
    ingredients is rejected rather than stored."""
    t = clean(text)
    for m in LEADIN.finditer(t):
        cand = t[m.end():].strip(' :.-–•|')
        cand = re.split(r'\b(?:how to use|directions|benefits|caution|warning|'
                        r'shipping|reviews)\b', cand, maxsplit=1, flags=re.I)[0]
        if looks_like_inci(cand) and not INSTRUCTION.search(cand[:110]):
            return cand[:4000]
    m = START_OK.search(t)
    if m:
        cand = t[m.start():]
        cand = re.split(r'\b(?:how to use|directions|benefits|caution|warning)\b',
                        cand, maxsplit=1, flags=re.I)[0]
        if looks_like_inci(cand) and not INSTRUCTION.search(cand[:110]):
            return cand[:4000]
    return ''


def find_skintype(text):
    t = clean(text)
    hits = {m.group(1).title() for m in SKINTYPE.finditer(t)}
    if not hits:
        return ''
    if 'All' in hits or len(hits) >= 4:
        return 'All'
    order = ['Combination', 'Oily', 'Dry', 'Normal', 'Sensitive']
    return ', '.join([h for h in order if h in hits])


S = requests.Session()
S.headers.update(HEAD)
lock = threading.Lock()
rows = []
stats = {'shopify': 0, 'sitemap': 0, 'html': 0, 'failed': 0}
per_site = {}


def get(url):
    try:
        r = S.get(url, timeout=TIMEOUT)
        return r if r.status_code == 200 else None
    except Exception:
        return None


# ------------------------------------------------------- 1. the Shopify feed
def try_shopify(domain):
    out = []
    for page in range(1, 9):                  # up to 2,000 products
        r = get(f'https://{domain}/products.json?limit=250&page={page}')
        if not r:
            break
        try:
            prods = r.json().get('products', [])
        except Exception:
            break
        if not prods:
            break
        for p in prods:
            body = p.get('body_html', '') or ''
            tags = ' '.join(p.get('tags', []) if isinstance(p.get('tags'), list)
                            else [str(p.get('tags', ''))])
            price, cur = '', ''
            for v in (p.get('variants') or [])[:1]:
                price = str(v.get('price', '') or '')
            out.append(dict(
                brand=(p.get('vendor') or '').strip(),
                name=(p.get('title') or '').strip(),
                product_type=(p.get('product_type') or '').strip(),
                price=price, currency=cur,
                product_url=f"https://{domain}/products/{p.get('handle','')}",
                ingredients=find_inci(body),
                skin_type=find_skintype(tags + ' ' + body),
                description=clean(body)[:400],
                domain=domain, method='shopify products.json'))
        if len(prods) < 250:
            break
    return out


# ------------------------------------------------------------ 2. the sitemap
def try_sitemap(domain):
    urls = set()
    for sm in (f'https://{domain}/sitemap.xml', f'https://{domain}/sitemap_index.xml'):
        r = get(sm)
        if not r:
            continue
        locs = re.findall(r'<loc>\s*([^<]+?)\s*</loc>', r.text)
        subs = [u for u in locs if 'product' in u.lower() and u.endswith('.xml')]
        for s in subs[:6]:
            rr = get(s)
            if rr:
                urls.update(re.findall(r'<loc>\s*([^<]+?)\s*</loc>', rr.text))
        urls.update(u for u in locs if PRODUCT_URL.search(u))
        if urls:
            break
    return read_product_pages(domain, list(urls)[:400], 'sitemap')


# ------------------------------------------------------ 3. the category pages
def try_html(domain):
    urls = set()
    for path in ('', '/shop', '/products', '/collections/all', '/store',
                 '/product-category/skincare', '/en/shop'):
        r = get(f'https://{domain}{path}')
        if not r:
            continue
        for href in re.findall(r'href=["\']([^"\']+)["\']', r.text):
            if PRODUCT_URL.search(href):
                if href.startswith('/'):
                    href = f'https://{domain}{href}'
                if domain in href:
                    urls.add(href.split('?')[0])
        if len(urls) > 30:
            break
    return read_product_pages(domain, list(urls)[:400], 'product pages')


def read_product_pages(domain, urls, method):
    out = []
    for u in urls:
        r = get(u)
        if not r:
            continue
        page = r.text[:400000]
        t = re.search(r'<title[^>]*>(.*?)</title>', page, re.I | re.S)
        name = re.split(r'\s*[|–]\s*', clean(t.group(1)))[0][:120] if t else ''
        if not name:
            continue
        price = ''
        pm = re.search(r'"price"\s*:\s*"?([\d.,]+)', page)
        if pm:
            price = pm.group(1)
        out.append(dict(brand='', name=name, product_type='', price=price,
                        currency='', product_url=u,
                        ingredients=find_inci(page),
                        skin_type=find_skintype(page),
                        description='', domain=domain, method=method))
    return out


def harvest(rec):
    domain, brand = rec['domain'], rec['brand']
    got = try_shopify(domain)
    method = 'shopify'
    if not got:
        got = try_sitemap(domain)
        method = 'sitemap'
    if not got:
        got = try_html(domain)
        method = 'html'
    for g in got:
        if not g['brand']:
            g['brand'] = brand
    with lock:
        if got:
            stats[method] += 1
            per_site[domain] = len(got)
            rows.extend(got)
        else:
            stats['failed'] += 1
        done = stats['shopify'] + stats['sitemap'] + stats['html'] + stats['failed']
        print(f'   {done:3d}/{total:3d}  {domain[:32]:32s} '
              f'{len(got):4d} products  via {method if got else "nothing found"}',
              flush=True)


if not os.path.exists(BRANDS):
    raise SystemExit(f'{BRANDS} not found. run discover_lebanese_brands.py first.')

bl = pd.read_csv(BRANDS, dtype=str).fillna('')
sites = bl[bl['domain'] != ''].to_dict('records')
if LIMIT:
    sites = sites[:LIMIT]
total = len(sites)
print(f'{total} Lebanese brand websites to harvest. no search credits are used.\n')

with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    list(ex.map(harvest, sites))

# de-duplicate inside the harvest
seen = set()
uniq = []
for r in rows:
    k = (re.sub(r'[^a-z0-9]', '', str(r['brand']).lower()),
         re.sub(r'[^a-z0-9]', '', str(r['name']).lower()))
    if k in seen or not k[1]:
        continue
    seen.add(k)
    uniq.append(r)

with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=FIELDS)
    w.writeheader()
    w.writerows(uniq)

ing = sum(1 for r in uniq if r['ingredients'])
st = sum(1 for r in uniq if r['skin_type'])
pr = sum(1 for r in uniq if r['price'])
print('\n' + '=' * 64)
print('  LEBANESE BRAND CATALOGUES HARVESTED')
print('=' * 64)
print(f'  websites tried            {total}')
print(f'    via the Shopify feed    {stats["shopify"]}')
print(f'    via the sitemap         {stats["sitemap"]}')
print(f'    via category pages      {stats["html"]}')
print(f'    nothing found           {stats["failed"]}')
print()
print(f'  products harvested        {len(rows):,}')
print(f'  after de-duplication      {len(uniq):,}')
print(f'    with ingredients        {ing:,}  ({100*ing/max(len(uniq),1):.1f}%)')
print(f'    with a skin type        {st:,}  ({100*st/max(len(uniq),1):.1f}%)')
print(f'    with a price            {pr:,}  ({100*pr/max(len(uniq),1):.1f}%)')
print(f'\n  written to {OUT}')
if per_site:
    print('\n  biggest catalogues:')
    for dmn, c in sorted(per_site.items(), key=lambda x: -x[1])[:20]:
        print(f'    {dmn[:34]:34s}{c:6,}')
print('\n  the Shopify feed is why this is worth doing: it returns a whole')
print('  catalogue in one request, already structured, at no cost.')
