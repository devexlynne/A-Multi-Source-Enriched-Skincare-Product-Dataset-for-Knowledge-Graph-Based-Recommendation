"""
Find every lebanese skincare brand that exists online

Why this is a separate problem
  The 332 Lebanese-origin products came from 11 brands somebody had already
  listed. That is not the market, that is a sample of it. Lebanon has a real
  cosmetics industry: pharmacy brands, soap makers, olive oil and laurel
  traditions, and a large number of small Instagram-first labels that never
  appear in a retail catalogue.

Usage:
    py discover_lebanese_brands.py
    py discover_lebanese_brands.py --queries-only   see the query list, spend nothing
"""
import os
import re
import csv
import sys
import json
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

SERPER_KEYS = [
    '',
            '',
    '',
]
OUT = 'lebanese_brands_discovered.csv'
WORKERS = 3
TIMEOUT = 20
HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'}

QUERIES = [
    # directories and lists, the highest yield per credit
    'list of Lebanese skincare brands',
    'Lebanese cosmetics brands made in Lebanon',
    'best Lebanese beauty brands to support',
    'homegrown Lebanese skincare labels',
    'Lebanese owned skincare brand directory',
    'marques de cosmetiques libanaises',
    'ماركات العناية بالبشرة اللبنانية',
    'منتجات تجميل لبنانية صنع لبنان',
    # made in Lebanon, by category
    'made in Lebanon skincare shop online',
    'made in Lebanon natural soap brand',
    'made in Lebanon face cream brand',
    'made in Lebanon facial serum brand',
    'made in Lebanon sunscreen brand',
    'made in Lebanon body care brand',
    'Lebanese organic skincare brand online shop',
    'Lebanese handmade cosmetics brand',
    'Lebanese natural beauty products company',
    'Lebanese artisanal soap company olive laurel',
    'savon d alep libanais marque',
    'Lebanese rose water skincare brand',
    'Lebanese olive oil skincare brand',
    'Lebanese aloe vera skincare brand',
    'Lebanese clean beauty startup',
    'Lebanese dermocosmetics laboratory brand',
    'Lebanese pharmacy own brand skincare',
    'Beirut based skincare brand',
    'Beirut cosmetics manufacturer skincare',
    'Lebanese skincare brand shopify store',
    'Lebanese beauty brand online store LBP',
    # instagram, for discovery only
    'instagram Lebanese skincare brand Beirut',
    'instagram lebanese handmade skincare shop',
    'instagram lebanon natural cosmetics small business',
    'instagram lebanon soap handmade brand',
    'instagram beirut beauty brand skincare shop now',
    'instagram lebanon organic skincare delivery',
    # product-category sweeps
    'Lebanese brand face serum buy online lebanon',
    'Lebanese brand moisturizer buy online lebanon',
    'Lebanese brand cleanser buy online lebanon',
    'Lebanese brand face mask buy online lebanon',
    'Lebanese brand body butter buy online lebanon',
    'Lebanese brand lip balm buy online lebanon',
    'Lebanese brand hair and skin oil lebanon',
    'Lebanese brand toner buy online lebanon',
    'Lebanese brand scrub exfoliator lebanon',
    # the ones we already know, to find their competitors
    'brands like Beesline Lebanon skincare',
    'Lebanese alternatives to Beesline',
    'Khan El Kaser similar Lebanese brands',
    'Ecladerm Lebanon skincare brand',
    'AloeLab Lebanon products',
    'Helwe Lebanon skincare',
    'Atelier Beautanique Lebanon',
    'Cosmaline Lebanon products',
    # trade and press, good for finding manufacturers
    'Lebanese cosmetics manufacturers association members',
    'Lebanon cosmetics industry export brands',
    'Lebanese beauty brand feature article Beirut',
    'Lebanese skincare brand founder interview',
    'Lebanese cosmetics factory private label',
    'produits de beaute fabriques au liban',
    'صناعة مستحضرات التجميل في لبنان',
    'lebanese skincare brand souk el tayeb market',
]

# retailers and marketplaces: excluded, they sell rather than make
RETAIL = re.compile(
    r'(sohaticare|feel22|mazenonline|zeinacare|nexuscare|daouk|amazon|ebay|'
    r'noon\.com|namshi|sephora|ulta|boots|douglas|iherb|lookfantastic|'
    r'aliexpress|etsy|jumia|shein|carrefour|spinneys|shopee|instashop|'
    r'toters|onlinepharmacy|pharmacyonline)', re.I)
JUNK = re.compile(
    r'(wikipedia|tripadvisor|linkedin|indeed|glassdoor|crunchbase|zoominfo|'
    r'yelp|facebook\.com/marketplace|pinterest|youtube|tiktok|reddit|quora|'
    r'google\.|bing\.|blogspot|wordpress\.com/tag|medium\.com|'
    r'alibaba|made-in-china|globalsources|europages|kompass)', re.I)
SOCIAL = re.compile(r'(instagram\.com|facebook\.com)', re.I)

# something has to tie the site to Lebanon
LB_EVIDENCE = [
    (re.compile(r'\.lb(?:/|$|\?)', re.I), 'a .lb domain'),
    (re.compile(r'\+?961[\s\-]?\d', re.I), 'a +961 phone number'),
    (re.compile(r'\b(lebanon|liban|lebanese|beirut|beyrouth|بيروت|لبنان)\b', re.I),
     'Lebanon named on the page'),
    (re.compile(r'\b(LBP|L\.L\.|ل\.ل)\b'), 'prices in Lebanese pounds'),
    (re.compile(r'\b(jounieh|tripoli|saida|byblos|jbeil|zahle|batroun|achrafieh|'
                r'hamra|mar mikhael|gemmayze|dbayeh|antelias|jal el dib)\b', re.I),
     'a Lebanese address'),
]
SKIN = re.compile(
    r'(skin ?care|skincare|cosmetic|beaut|soap|savon|cream|creme|serum|'
    r'moistur|cleanser|lotion|balm|scrub|mask|toner|sunscreen|spf|'
    r'العناية|بشرة|صابون)', re.I)

S = requests.Session()
S.headers.update(HEAD)
_i, _lock = [0], threading.Lock()
_spent = [0]


def serper(q, num=20):
    while True:
        with _lock:
            if _i[0] >= len(SERPER_KEYS):
                return [], 'no keys'
            k = SERPER_KEYS[_i[0]]
        try:
            r = requests.post('https://google.serper.dev/search',
                              headers={'X-API-KEY': k, 'Content-Type': 'application/json'},
                              data=json.dumps({'q': q, 'num': num, 'gl': 'lb'}),
                              timeout=TIMEOUT)
        except Exception:
            return [], 'network'
        if r.status_code in (400, 401, 402, 403, 429):
            with _lock:
                if _i[0] < len(SERPER_KEYS) and SERPER_KEYS[_i[0]] == k:
                    print(f'   key ...{k[-6:]} exhausted (HTTP {r.status_code})')
                    _i[0] += 1
            continue
        if r.status_code != 200:
            return [], r.status_code
        with _lock:
            _spent[0] += 1
        try:
            j = r.json()
            return [(o.get('link', ''), o.get('title', ''), o.get('snippet', ''))
                    for o in j.get('organic', [])], 200
        except Exception:
            return [], 'bad json'


def host_of(u):
    return (u.split('/')[2].lower().replace('www.', '')
            if '://' in u else '')


if '--queries-only' in sys.argv:
    print(f'{len(QUERIES)} discovery queries, in English, French and Arabic:\n')
    for q in QUERIES:
        print('   ', q)
    print(f'\nabout {len(QUERIES)} credits for discovery, plus one per candidate '
          f'domain to verify')
    raise SystemExit

# ============================================================ 1. cast the net
print(f'{len(QUERIES)} discovery queries\n')
candidates = {}      # domain -> dict
insta = {}           # handle -> title


def run_query(q):
    res, code = serper(q)
    if code != 200:
        return q, []
    return q, res


with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    for q, res in ex.map(lambda x: run_query(x), QUERIES):
        for url, title, snip in res:
            h = host_of(url)
            if not h or JUNK.search(h):
                continue
            if SOCIAL.search(h):
                m = re.search(r'instagram\.com/([A-Za-z0-9_.]{2,40})', url)
                if m and m.group(1).lower() not in ('p', 'reel', 'explore', 'tv'):
                    insta.setdefault(m.group(1), title[:80])
                continue
            if RETAIL.search(h):
                continue
            if h not in candidates:
                candidates[h] = dict(domain=h, brand='', instagram='', evidence='',
                                     how_found=q[:48], sample_title=title[:70])
        print(f'   searched: {q[:52]:52s} candidates {len(candidates):4d} '
              f'instagram {len(insta):3d}', flush=True)

print(f'\n{len(candidates):,} candidate domains, {len(insta):,} instagram handles')
print(f'credits so far {_spent[0]:,}\n')

# =============================================== 2. verify each candidate site
print('checking each candidate for evidence it is Lebanese and sells skincare\n')
keep = {}
lock2 = threading.Lock()
checked = [0]


def verify(h):
    for scheme in ('https://', 'http://'):
        try:
            r = S.get(scheme + h, timeout=TIMEOUT)
            if r.status_code != 200:
                continue
            page = r.text[:300000]
            ev = [why for pat, why in LB_EVIDENCE if pat.search(page) or pat.search(h)]
            if not ev:
                return
            if not SKIN.search(page):
                return
            title = re.search(r'<title[^>]*>(.*?)</title>', page, re.I | re.S)
            brand = re.sub(r'\s+', ' ', title.group(1)).strip()[:60] if title else h
            brand = re.split(r'\s*[|–\-]\s*', brand)[0][:48]
            ig = re.search(r'instagram\.com/([A-Za-z0-9_.]{2,40})', page)
            with lock2:
                keep[h] = dict(domain=h, brand=brand,
                               instagram=ig.group(1) if ig else '',
                               evidence='; '.join(ev[:3]),
                               how_found=candidates[h]['how_found'],
                               sample_title=candidates[h]['sample_title'])
            return
        except Exception:
            continue


with ThreadPoolExecutor(max_workers=8) as ex:
    futs = [ex.submit(verify, h) for h in candidates]
    for fut in as_completed(futs):
        with lock2:
            checked[0] += 1
            if checked[0] % 25 == 0:
                print(f'   {checked[0]}/{len(candidates)}   confirmed Lebanese '
                      f'{len(keep)}', flush=True)

# instagram handles we could not tie to a website are still worth recording
for handle, title in insta.items():
    if any(handle.lower() in v['instagram'].lower() for v in keep.values() if v['instagram']):
        continue
    keep.setdefault('instagram:' + handle,
                    dict(domain='', brand=title, instagram=handle,
                         evidence='found on instagram, no website resolved',
                         how_found='instagram search', sample_title=title))

rows = sorted(keep.values(), key=lambda r: (r['domain'] == '', r['domain']))
with open(OUT, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, fieldnames=['brand', 'domain', 'instagram', 'evidence',
                                       'how_found', 'sample_title'])
    w.writeheader()
    w.writerows(rows)

sites = [r for r in rows if r['domain']]
only_ig = [r for r in rows if not r['domain']]
print('\n' + '=' * 66)
print('  LEBANESE SKINCARE BRANDS DISCOVERED')
print('=' * 66)
print(f'  candidate domains seen        {len(candidates):,}')
print(f'  confirmed Lebanese + skincare {len(sites):,}')
print(f'  instagram only, no website    {len(only_ig):,}')
print(f'  credits used                  {_spent[0]:,}')
print(f'\n  written to {OUT}')
print('\n  WITH A WEBSITE, ready to harvest:')
for r in sites[:40]:
    print(f'    {r["brand"][:34]:34s} {r["domain"][:30]:30s} {r["evidence"][:34]}')
if len(sites) > 40:
    print(f'    ... and {len(sites)-40} more')
if only_ig:
    print('\n  INSTAGRAM ONLY, recorded but not harvestable:')
    for r in only_ig[:15]:
        print(f'    @{r["instagram"][:24]:24s} {r["brand"][:44]}')
print('\n  review the list, delete anything wrong, then run:')
print('     py harvest_lebanese_catalogues.py')
