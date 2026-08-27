"""
Are lebanese products in a shopping index at all?

This does NOT collect prices. It answers one question, and it is the question
four separate runs have failed to reach.

Why a different script
  Rayobyte is not a shopping API. It is an HTML fetcher: you give it a URL and
  it hands back the page. serper_price.py talks to services that return
  listings already parsed into title, seller and price, and it can trust those
  numbers because somebody else did the parsing.
"""
import os
import re
import sys
import csv
import json
import time
import html
import datetime
import threading
import collections
import urllib.parse
import requests
from concurrent.futures import ThreadPoolExecutor

TOKEN = ''
API = 'http://api.scraping.rayobyte.com/'
DATA = 'COMBINED_DATASET.csv'
OUT = 'lebanon_shopping_presence.csv'
WORKERS = 3
TIMEOUT = 90            # fetching a real page is slower than an API call
TODAY = datetime.date.today().isoformat()

TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 25

csv.field_size_limit(10 ** 8)

# ---------------------------------------------------------------- balance
if '--balance' in sys.argv:
    r = requests.get(API + 'balance', params={'token': TOKEN}, timeout=30)
    print(f'  HTTP {r.status_code}')
    print(f'  {r.text[:400]}')
    sys.exit(0)

# ---------------------------------------------------------------- reading
SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)
PROMO = re.compile(r'buy\s*\d*\s*get\s*\d*|bundle|free gift', re.I)

# "did not match any documents", "No results found for" and their variants.
# These are sentences Google writes, not classes it generates, so they do not
# change when the layout does.
NO_RESULTS = re.compile(
    # Google
    r'did not match any (documents|shopping results)|'
    r'no results (found|containing)|'
    r'your search .{0,60} did not match|'
    r'try different keywords|'
    r'make sure that all words are spelled correctly|'
    # Bing
    r'there are no results for|'
    r'we did(n.t| not) find any results for|'
    r'check your spelling or try different keywords', re.I)

# any price on the page, in the currencies Google Shopping shows for a US search
PRICE = re.compile(r'(?:US\s*)?\$\s?\d[\d,]*(?:\.\d{2})?')

# a page that came back as a consent wall or a robot check is not an answer
BLOCKED = re.compile(
    r'unusual traffic|are you a robot|consent\.google|before you continue|'
    r'enablejs|our systems have detected', re.I)


# BING, NOT GOOGLE, AND HERE IS WHY.
#
# The first run of this script asked Google Shopping and got a consent wall or
# a robot check back 48 times out of 52. Google detects datacentre proxies and
# refuses to answer them, which is the whole reason services like Serper exist:
# they solve the blocking problem and hand back parsed results.
#
# Those 48 were recorded as "unknown" rather than "not listed", which matters.
# Without that check they would have looked like pages with no prices on them,
# and the conclusion would have been that Lebanese products are not sold
# online. That would have been a finding manufactured by my own scraper.
#
# Bing does not block this way, and Rayobyte's own documentation uses bing.com
# as its example. For the question being asked here, whether a product appears
# in any shopping index at all, Bing answers it just as well. It is a weaker
# claim than Google would give, and the thesis should say Bing rather than
# implying Google.
ENGINE = 'bing'
if '--google' in sys.argv:
    ENGINE = 'google'


def shop_url(brand, name):
    n = PROMO.sub(' ', SIZE.sub(' ', str(name)))
    q = f'{brand} {n}'.strip()
    q = re.sub(r'\s+', ' ', q)[:140]
    if ENGINE == 'google':
        return ('https://www.google.com/search?tbm=shop&hl=en&gl=us&q='
                + urllib.parse.quote(q))
    return 'https://www.bing.com/shop?q=' + urllib.parse.quote(q)


_lock = threading.Lock()
_shape = [False]
_stop = threading.Event()


def get_html(url):
    """One fetch. Returns (html, note)."""
    try:
        r = requests.post(API, params={'token': TOKEN},
                          headers={'Content-Type': 'application/json'},
                          data=json.dumps({'url': url,
                                           'module': 'HtmlRequestScraper'}),
                          timeout=TIMEOUT)
    except Exception as e:
        return '', f'network ({type(e).__name__})'
    if r.status_code != 200:
        return '', f'http {r.status_code}'
    try:
        body = r.json()
    except Exception:
        return r.text, ''          # some setups return the page directly

    # THE FIRST REPLY IS INSPECTED, NOT ASSUMED.
    # Their documentation shows the request but not the response, so the shape
    # is discovered from the first answer and printed once. If nothing in it
    # looks like a page, the run stops rather than recording 977 blanks.
    with _lock:
        if not _shape[0]:
            _shape[0] = True
            print(f'  reply keys: {sorted(body.keys())[:10]}')

    # A short reply is still a reply. The first version demanded 200
    # characters before it would accept a page, which threw away every real
    # answer in testing and would have thrown away a genuine "no results" page
    # too, since those are small.
    for k in ('result', 'html', 'body', 'content', 'data', 'response'):
        v = body.get(k)
        if isinstance(v, str) and v.strip():
            return v, ''
        if isinstance(v, dict):
            for k2 in ('html', 'content', 'body', 'result', 'text'):
                v2 = v.get(k2)
                if isinstance(v2, str) and v2.strip():
                    return v2, ''
    return '', f'no page in reply: {sorted(body.keys())[:8]}'


def judge(page, brand, name):
    """listed yes / no / unknown, how many prices, and why."""
    if not page:
        return 'unknown', 0, 'nothing came back'
    if BLOCKED.search(page):
        return 'unknown', 0, 'blocked or consent page'
    text = html.unescape(re.sub(r'<script.*?</script>|<style.*?</style>', ' ',
                                page, flags=re.S | re.I))
    text = re.sub(r'<[^>]+>', ' ', text)
    if NO_RESULTS.search(text):
        return 'no', 0, f'{ENGINE} says there are no results'
    prices = PRICE.findall(text)
    if not prices:
        return 'no', 0, 'no price appears anywhere on the page'
    # the brand has to appear too, or the prices belong to something else
    bw = [w for w in re.split(r'[^A-Za-z0-9]+', str(brand)) if len(w) > 2]
    if bw and not any(re.search(re.escape(w), text, re.I) for w in bw):
        return 'no', len(prices), 'prices on the page, but not for this brand'
    return 'yes', len(prices), ''


# ---------------------------------------------------------------- products
with open(DATA, newline='', encoding='utf-8') as fh:
    rows = [{k: (v or '') for k, v in r.items()} for r in csv.DictReader(fh)]

# ONLY A DEFINITE ANSWER COUNTS AS DONE.
#
# The first run recorded 52 products as "unknown", because Google served a
# consent page instead of results. Treating those as answered would leave them
# permanently unresolved: the file would say the question was asked, and it
# was, but nothing came back. An unknown is re-asked.
done = {}
if os.path.exists(OUT):
    with open(OUT, newline='', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            if r.get('listed') in ('yes', 'no'):
                done[r['product_id']] = r

# THE RIGHT 977 PRODUCTS, NOT EVERY LEBANESE ONE.
#
# The first version took every Lebanese product with no market price, which is
# 5,800 of them: nearly all Lebanese RETAIL products already carry a Beirut
# shop price and were never asked about Google Shopping at all. Asking about
# those answers a question nobody posed.
#
# The products that matter are the ones whose recorded answer is "no listings",
# because that is the answer a dead key gave. They are read from
# price_progress.csv, the same place serper_price.py --retry-empty reads.
PROGRESS = 'price_progress.csv'
asked = {}
if os.path.exists(PROGRESS):
    with open(PROGRESS, newline='', encoding='utf-8') as fh:
        for r in csv.DictReader(fh):
            prev = asked.get(r['product_id'])
            if prev and not r.get('price') and prev.get('price'):
                continue
            asked[r['product_id']] = r
empty = {k for k, v in asked.items()
         if not v.get('price') and v.get('why_not') == 'no listings'}

need = [r for r in rows
        if r.get('source_category', '').startswith('Lebanese')
        and r['product_id'] in empty
        and r['product_id'] not in done]
if not os.path.exists(PROGRESS):
    sys.exit('price_progress.csv not found, so there is nothing to re-check.')
if TEST:
    need = need[:TEST]

print('=' * 72)
print('  ARE LEBANESE PRODUCTS IN A SHOPPING INDEX AT ALL?')
print('=' * 72)
print(f'  asking                 {ENGINE}')
print(f'  products to check      {len(need):,}')
print(f'  already checked        {len(done):,}')
if TEST:
    print(f'  TEST RUN of {len(need)}')
print()

new = not os.path.exists(OUT)
fh_out = open(OUT, 'a', newline='', encoding='utf-8')
wr = csv.writer(fh_out)
if new:
    wr.writerow(['product_id', 'source_category', 'brand', 'name', 'listed',
                 'n_prices', 'why', 'date'])

count = collections.Counter()
_whys = []
seen = [0]
t0 = time.time()


def work(r):
    if _stop.is_set():
        return
    page, note = get_html(shop_url(r['brand'], r['name']))
    if note:
        listed, n_p, why = 'unknown', 0, note
    else:
        listed, n_p, why = judge(page, r['brand'], r['name'])
    with _lock:
        count[listed] += 1
        if listed == 'unknown':
            _whys.append(why)
        seen[0] += 1
        wr.writerow([r['product_id'], r.get('source_category', ''), r['brand'],
                     r['name'], listed, n_p, why, TODAY])
        fh_out.flush()
        if TEST or seen[0] % 25 == 0 or seen[0] == len(need):
            el = time.time() - t0
            left = (len(need) - seen[0]) * el / max(seen[0], 1)
            print(f'  {seen[0]:5,}/{len(need):,}  '
                  f'listed {count["yes"]:4,}  not listed {count["no"]:4,}  '
                  f'unknown {count["unknown"]:4,}   {int(left//60)}m left')
        if TEST:
            print(f'        {r["brand"][:20]:22s}{r["name"][:34]:36s}'
                  f'{listed:8s}{why}')
        # if nothing at all is coming back, stop rather than fill the file
        if seen[0] >= 25 and count['unknown'] == seen[0] and not _stop.is_set():
            why_common = collections.Counter(
                w for w in _whys).most_common(1)
            print(f'\n  STOPPING. All {seen[0]} replies were unusable.')
            if why_common:
                print(f'  Reason: {why_common[0][0]}')
                if 'blocked' in why_common[0][0]:
                    print('  The search engine is refusing the proxy rather')
                    print('  than answering. Nothing is wrong with the products.')
                    if ENGINE == 'bing':
                        print('  Bing is blocking too, so this approach is done.')
                    else:
                        print('  Run without --google to ask Bing instead.')
            _stop.set()


with ThreadPoolExecutor(WORKERS) as ex:
    list(ex.map(work, need))
fh_out.close()

# ---------------------------------------------------------------- report
# the file is append-only, so a product re-asked after a blocked reply is in
# it twice. The latest definite answer wins, so the summary reports what is
# actually known rather than counting the blocked attempt again.
latest = {}
with open(OUT, newline='', encoding='utf-8') as fh:
    for r in csv.DictReader(fh):
        prev = latest.get(r['product_id'])
        if prev and prev.get('listed') in ('yes', 'no') \
                and r.get('listed') == 'unknown':
            continue
        latest[r['product_id']] = r
allr = list(latest.values())
tot = len(allr)
by = collections.Counter(r['listed'] for r in allr)
usable = by['yes'] + by['no']

print()
print('=' * 72)
print('  RESULT')
print('=' * 72)
print(f'  products checked       {tot:,}')
for k, lab in [('yes', f'found on {ENGINE} shopping'),
               ('no', 'not there'),
               ('unknown', 'could not tell')]:
    v = by[k]
    print(f'  {lab:24s}{v:6,}' + (f'   ({100*v/tot:.1f}%)' if tot else ''))
if usable:
    print(f'\n  of the {usable:,} that gave a clear answer, '
          f'{100*by["yes"]/usable:.1f}% are listed')

if by['no']:
    print('\n  WHY NOT, in their own words')
    for k, v in collections.Counter(
            r['why'] for r in allr if r['listed'] == 'no').most_common(5):
        print(f'    {k[:52]:54s}{v:6,}')

if by['yes']:
    print('\n  BRANDS THAT ARE LISTED')
    b = collections.Counter(r['brand'] for r in allr if r['listed'] == 'yes')
    for k, v in b.most_common(10):
        print(f'    {k[:30]:32s}{v:5,}')
    print('\n  these should go back through serper_price.py for real prices,')
    print('  because this script deliberately does not read prices')

print(f'\n  written to {OUT}')
print('  nothing was written into COMBINED_DATASET.csv. This is evidence,')
print('  collected to answer a question, not a column of data.')
