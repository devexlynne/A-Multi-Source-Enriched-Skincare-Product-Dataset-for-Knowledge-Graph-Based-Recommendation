"""
Price from google shopping (serper or talordata)

Two services, one script
  Serper and Talordata both sell Google Shopping results. They are different
  companies with different URLs, different authentication and different field
  names, so a key from one will not work on the other. The key format decides
  which is used, and both can sit in the same list:
"""
import os
import re
import sys
import csv
import json
import time
import threading
import datetime
import statistics
import unicodedata
import requests

# NO PANDAS ON PURPOSE.
#
# This script used to import pandas for one read_csv. Twice now that import has
# failed on this machine with "bad marshal data", which is a corrupted bytecode
# cache inside pandas, usually left behind when a long run is interrupted. That
# is a bad dependency for the ONE script that gets run over and over, and it
# stops work for reasons that have nothing to do with the work.
#
# The csv module is in the standard library, cannot be corrupted by an
# interrupted run, and does everything needed here. The merge script still uses
# pandas, because it genuinely needs it.
from concurrent.futures import ThreadPoolExecutor

# ------------------------------------------------------------------- settings
# TWO DIFFERENT COMPANIES, TWO DIFFERENT APIS.
#
# The keys in this project are not interchangeable, and putting a Talordata key
# in the Serper list would have failed on the first request:
#
#   Serper      40 hex characters       google.serper.dev/shopping
#               header  X-API-KEY: <key>
#               JSON body, results come back under "shopping"
#
#   Talordata   starts with sk_         serpapi.talordata.net/serp/v1/request
#               header  Authorization: Bearer <key>
#               FORM body, engine=google_shopping, json=1
#
# Both return Google Shopping listings, so the rest of this script does not
# care which one answered. The key format decides where the question goes, so
# you can mix them in one list and the script sorts it out.
# ORDER MATTERS, AND THE DOUBTFUL KEYS GO FIRST.
#
# A key that has already run out costs ONE refused request to discover, and a
# refused request is not billed by either service. So there is nothing to lose
# by trying an old key first, and a whole allowance to gain if it turns out to
# have something left. The known-good allowance is kept for last.
# THE KEYS COME FROM THE ENVIRONMENT.
#
# They used to be written out here, with a comment beside each one saying
# which service it belonged to and whether it was spent. That was genuinely
# useful while the work was going on and it is exactly what must not be
# committed: git keeps history, so a key deleted later stays readable in the
# earlier commit for as long as the repository exists.
#
# Set them once, comma separated, newest first. Mixing services is still fine
# because provider_of() below decides where each question goes by the shape of
# the key, not by the order.
#
#     set SERPER_KEYS=serper_key1,serper_key2,sk_talordata_key
#
# or put that line in a file called .env, which .gitignore excludes.
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
            '\n  No API keys found.\n'
            '  Set SERPER_KEYS before running, for example:\n'
            '      set SERPER_KEYS=your_key_here\n'
            '  or put SERPER_KEYS=your_key_here in a file called .env\n')
    return keys


KEYS = _keys_from_env()
SERPER_KEYS = KEYS          # old name, kept so nothing else breaks


def provider_of(key):
    """Which service a key belongs to, decided by its shape.

    THREE services are now in play, and the rule used to be "starts with sk_
    means Talordata, anything else means Serper". That would have sent the
    32-character ScraperAPI key to Serper, which refuses it with HTTP 400 and
    looks exactly like an exhausted key. Length tells them apart:

        starts with sk_   Talordata
        40 characters     Serper
        32 characters     ScraperAPI
    """
    k = str(key).strip()
    if k.startswith('sk_'):
        return 'talordata'
    if len(k) == 32:
        return 'scraperapi'
    if re.fullmatch(r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-'
                    r'[0-9a-f]{4}-[0-9a-f]{12}', k, re.I):
        # Rayobyte / Scraping Robot hands out keys in this shape. Recognised
        # here so it can never be posted to Serper by mistake, which would
        # return HTTP 400 and read as an exhausted key rather than a wrong
        # address. The request itself is not written yet.
        return 'rayobyte'
    return 'serper'

DATA = 'COMBINED_DATASET.csv'
PROGRESS = 'price_progress.csv'
WORKERS = 4
TIMEOUT = 20
MAX_OFFERS = 8
MIN_PRICE = 0.50
MAX_PRICE = 500.0
TODAY = datetime.date.today().isoformat()

TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 200
APPLY = '--apply' in sys.argv

# ------------------------------------------------------------------- matching
SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)
PROMO = re.compile(r'buy\s*\d*\s*get\s*\d*|bundle|free gift', re.I)
MULTIPACK = re.compile(
    r'\b(\d+\s*[- ]?\s*pack|pack of \d+|case of \d+|set of \d+|'
    r'bundle|twin pack|value pack|lot of \d+|\d+\s*x\s*\d+\s*(ml|oz|g)\b)', re.I)
STOP = {'the', 'and', 'for', 'with', 'of', 'de', 'la', 'le', 'du', 'new',
        'skin', 'face', 'facial', 'ml', 'g', 'gr', 'oz', 'fl', 'in', 'to',
        'plus', 'a', 'x', 'cream', 'serum'}
MONEY = re.compile(r'(\d[\d,]*\.?\d*)')


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()


def words(s):
    return {w for w in re.split(r'[^a-z0-9]+', asc(s)) if w and w not in STOP and len(w) > 1}


def query_for(brand, name):
    """The search string. Size and promo wording are stripped because they push
    Google towards the wrong listing: 'Buy 1 Get 1' returns bundle sellers."""
    n = PROMO.sub(' ', SIZE.sub(' ', str(name)))
    n = re.sub(r'\s+', ' ', n).strip()
    b = str(brand).strip()
    q = f'{b} {n}' if asc(b) not in asc(n) else n
    return re.sub(r'\s+', ' ', q).strip()[:140]


def to_number(txt):
    """'$16.08' -> 16.08. Returns None for anything that is not one number.

    Talordata may hand back a plain number in extracted_price rather than a
    string with a currency symbol, so a bare float is accepted as dollars.
    A STRING without a dollar sign is still refused, because that is how a
    euro or a pound price arrives.
    """
    if isinstance(txt, (int, float)):
        return float(txt)
    t = str(txt).replace(',', '')
    if '$' not in t and 'usd' not in t.lower():
        return None                      # a euro or pound price is not a USD one
    m = MONEY.search(t.replace('$', ' $').replace('$', ''))
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


# SECONDHAND MARKETPLACES ARE REFUSED.
#
# The first real run found prices for 1,137 products, and 256 of them, 22.5%,
# came from eBay, Mercari, Poshmark, Whatnot and Depop. Those are resale
# listings: one person selling one used or unwanted item at whatever they hope
# to get. That is not a retail price, and the median from those sellers was
# $19.50 against $22.73 from actual shops, so it drags the column down.
#
# POSHMARK IN PARTICULAR. It is the source my supervisors already made me
# remove once, from the skin type column. Letting it back into the dataset
# through a different column would be exactly the kind of thing that gets
# noticed, and the same argument I used to keep INCIDecoder out of the
# ingredients applies here.
#
# The listing is skipped entirely rather than merely demoted, so it cannot
# influence the median either.
RESALE = re.compile(
    r'\b(ebay|mercari|poshmark|whatnot|depop|vinted|tradesy|thredup|'
    r'aliexpress|wish\.com|shpock|craigslist|facebook marketplace|'
    r'kijiji|gumtree|carousell|offerup|letgo)\b', re.I)

# A listing that adds one of these words is a DIFFERENT PRODUCT, not the one
# asked about. "CeraVe Hydrating Cleanser" and "CeraVe Hydrating Cleanser Bar"
# share every word, so the overlap test passes them both, and the bar's price
# lands on the cleanser. Same for the travel size, the refill, and the gift set.
VARIANT = re.compile(
    r'\b(bar|wipes?|spray|mist|mini|travel size|refill|foam|stick|patches|'
    r'kit|set|duo|trio|sample|sachet|tester|gift|for men|shampoo|body wash|'
    r'sunscreen|deodorant|toothpaste)\b', re.I)


def offer_ok(title, brand, name):
    """Is this listing actually the product we asked about?"""
    t = asc(title)
    # Compared with punctuation removed as well. "L'Oreal" in a shop title and
    # "L'Oreal" in the dataset are the same brand, but one keeps the apostrophe
    # and one does not, and a plain substring test says they are different.
    tflat = re.sub(r'[^a-z0-9]', '', t)
    bw = words(brand)
    if bw and not any(w in t or w in tflat for w in bw):
        return False, 'different brand'
    if MULTIPACK.search(title):
        return False, 'multipack'
    nw = words(name) - words(brand)
    if nw:
        hit = sum(1 for w in nw if w in t or w in tflat)
        if hit / len(nw) < 0.5:
            return False, 'name does not match'
    # a variant word in the listing that is NOT in our product name
    extra = {w.lower() for w in VARIANT.findall(title)} - {w.lower() for w in
                                                          VARIANT.findall(str(name))}
    if extra:
        return False, f'variant ({sorted(extra)[0]})'
    return True, ''


# --------------------------------------------------------------- serper calls
_lock = threading.Lock()
_i = [0]
_spent = [0]      # credits, as reported by the service
_requests = [0]   # questions asked
_stop = threading.Event()
_shape_checked = [False]
# A key that has run out does not always say so. On the big run, one returned
# HTTP 200 with an empty list 3,800 times in a row, and the script recorded
# every one as "this product has no listings" and moved on. The hit rate went
# 60% -> 0% at a single point and stayed there. Those 4,641 products were
# marked as asked without ever being asked.
#
# So consecutive empty replies are counted. Real empties are scattered: before
# the cliff the worst 500 products contained 155 empties, but never more than a
# handful in a row. Sixty in a row is not a property of the data.
_empty_streak = [0]
EMPTY_STREAK_LIMIT = 60
_reason = ['keys']   # which stop fired: shape, rate, or keys


def find_listings(body):
    """Pull the list of shop listings out of whatever shape came back.

    Serper calls it "shopping". Talordata is a SerpApi-compatible service and
    its documented example wraps everything in search_metadata / spider_
    parameter, but it does not publish the shopping key name. Rather than
    guess once and be wrong 6,000 times, every likely name is tried, and if
    none of them is there the run stops and prints what the reply actually
    contained.
    """
    # AN EMPTY LIST IS A REAL ANSWER.
    #
    # The reply {"shopping": [], "credits": 2} means "Google Shopping has
    # nothing for this product", which is true of genuinely obscure items. An
    # earlier version required the list to be non-empty before it recognised
    # the shape, so the very first product of a run happening to have no
    # listings looked like an unknown reply format and stopped everything.
    # The question is whether the KEY is present, not whether it has anything
    # in it.
    for key in ('shopping', 'shopping_results', 'shopping_result', 'results',
                'products', 'organic_results', 'items', 'data'):
        v = body.get(key)
        if isinstance(v, list):
            return v, key
    # one level down, e.g. {"data": {"shopping_results": [...]}}
    for outer in ('data', 'result', 'response'):
        inner = body.get(outer)
        if isinstance(inner, dict):
            got, key = find_listings(inner)
            if got:
                return got, f'{outer}.{key}'
    return [], ''


def read_offer(o):
    """One listing as (title, seller, price text, rating, rating count).

    The two services spell these differently. Serper uses price / source /
    ratingCount, SerpApi-style services use extracted_price / seller /
    reviews. Both spellings are read, so neither has to be guessed correctly.
    """
    title = o.get('title') or o.get('name') or ''
    seller = (o.get('source') or o.get('seller') or o.get('merchant') or
              o.get('store') or '')
    price = (o.get('price') or o.get('extracted_price') or
             o.get('price_str') or o.get('current_price') or '')
    rating = o.get('rating') or o.get('stars') or None
    rating_n = (o.get('ratingCount') or o.get('rating_count') or
                o.get('reviews') or o.get('review_count') or 0)
    return str(title), str(seller), price, rating, rating_n


def shopping(q):
    """Ask whichever service the current key belongs to. Rotate when spent."""
    while True:
        if _stop.is_set():
            return [], 'stopped'
        with _lock:
            if _i[0] >= len(KEYS):
                _stop.set()
                return [], 'no keys'
            k = KEYS[_i[0]]
        who = provider_of(k)
        try:
            if who == 'rayobyte':
                # NOT IMPLEMENTED YET, on purpose.
                #
                # Rayobyte's scraping API is a different shape again: it takes
                # a URL and a module name rather than a search query, and I
                # could not read their documentation to find out whether a
                # Google Shopping module exists or what it returns.
                #
                # Guessing would burn credits discovering the answer. The key
                # is recognised so it cannot be misrouted, and the run says so
                # plainly instead of failing in a way that looks like an
                # exhausted key.
                with _lock:
                    if _i[0] < len(KEYS) and KEYS[_i[0]] == k:
                        print(f'   rayobyte key ...{k[-6:]} SKIPPED: their API '
                              f'is not wired up yet.')
                        print('   paste me the example request from their '
                              'get-started page and it will be.')
                        _i[0] += 1
                continue
            if who == 'scraperapi':
                # ScraperAPI's structured endpoint takes everything in the
                # query string and answers with GET, not POST like the other
                # two. Its Google Shopping results come back under
                # "shopping_results", which find_listings already looks for.
                r = requests.get(
                    'https://api.scraperapi.com/structured/google/shopping',
                    params={'api_key': k, 'query': q, 'country': 'us'},
                    timeout=max(TIMEOUT, 70))   # it is slower than the others
            elif who == 'talordata':
                r = requests.post(
                    'https://serpapi.talordata.net/serp/v1/request',
                    headers={'Authorization': f'Bearer {k}',
                             'Content-Type': 'application/x-www-form-urlencoded'},
                    data={'engine': 'google_shopping', 'q': q, 'gl': 'us',
                          'hl': 'en', 'num': '10', 'json': '1'},
                    timeout=TIMEOUT)
            else:
                r = requests.post(
                    'https://google.serper.dev/shopping',
                    headers={'X-API-KEY': k, 'Content-Type': 'application/json'},
                    # num=10 rather than 40, because at most 8 offers are ever
                    # used and the rest are paid for and thrown away.
                    #
                    # It does NOT halve the bill. I assumed it would, because a
                    # reply carrying num=40 reported "credits": 2. Asking for 10
                    # still reports 2. Serper charges two credits for a shopping
                    # query whatever the size, so a key labelled 2,500 answers
                    # about 1,250 questions. That is not the key being short,
                    # which is what it looked like the first time.
                    data=json.dumps({'q': q, 'gl': 'us', 'num': 10}),
                    timeout=TIMEOUT)
        except Exception:
            return [], 'network'

        if r.status_code in (400, 401, 402, 403, 429):
            with _lock:
                if _i[0] < len(KEYS) and KEYS[_i[0]] == k:
                    print(f'   {who} key ...{k[-6:]} exhausted or refused '
                          f'(HTTP {r.status_code})')
                    if r.status_code in (401, 403):
                        print(f'   note: {r.text[:160]}')
                    _i[0] += 1
            continue
        if r.status_code != 200:
            return [], r.status_code
        try:
            body = r.json()
        except Exception:
            return [], 'bad json'

        # WHAT A REQUEST ACTUALLY COSTS.
        #
        # This used to count one credit per request. Serper's reply carries
        # the real figure, and it is not always one: asking for 40 results
        # costs 2. So a key labelled 2,500 credits answers about 1,250
        # questions, which is exactly what happened to the first key, and it
        # looked like the key was short-changing us.
        #
        # The real number is read from the reply now, so the counter on screen
        # matches what the account is actually being charged.
        with _lock:
            _requests[0] += 1
            try:
                _spent[0] += int(body.get('credits', 1) or 1)
            except (TypeError, ValueError):
                _spent[0] += 1

        # Talordata reports failures inside a 200 reply, so the status has to
        # be read from the body rather than from the HTTP code alone.
        meta = body.get('search_metadata') or {}
        if isinstance(meta, dict):
            st = str(meta.get('status', '')).lower()
            if st and st not in ('success', 'ok', 'done', 'completed'):
                return [], f'reply status {st}'

        offers, where = find_listings(body)

        # THE FIRST REPLY IS INSPECTED, NOT ASSUMED.
        #
        # Cost of a wrong assumption about the reply: one credit, not all of
        # them. This mattered more once two services were involved, because
        # only one of them documents its shopping field names.
        with _lock:
            if not _shape_checked[0]:
                _shape_checked[0] = True
                # judged on whether the LIST WAS FOUND, not whether it had
                # anything in it. An obscure product with no listings is a
                # normal answer, and the first product of a run being obscure
                # should not look like a broken API.
                if not where:
                    print('\n  ' + '!' * 60)
                    print(f'  STOPPING. No list of listings in the {who} reply.')
                    print(f'  Top-level keys: {sorted(body.keys())[:12]}')
                    print(f'  First 300 characters: {str(body)[:300]}')
                    print('  One credit spent. Send me this and I will correct')
                    print('  the script before you spend more.')
                    print('  ' + '!' * 60)
                    _reason[0] = 'shape'
                    _stop.set()
                    return [], 'unexpected shape'
                print(f'  {who}: reply understood, listings found under '
                      f'"{where}" ({len(offers)} in the first answer)')
                if offers:
                    print(f'  fields present: {sorted(offers[0].keys())[:10]}')
                print()
        # a key that quietly stopped working looks exactly like a run of
        # products that happen to have no listings, so the streak is watched
        with _lock:
            if offers:
                _empty_streak[0] = 0
            else:
                _empty_streak[0] += 1
                if _empty_streak[0] >= EMPTY_STREAK_LIMIT and not _stop.is_set():
                    print('\n  ' + '!' * 62)
                    print(f'  STOPPING. {_empty_streak[0]} replies in a row came'
                          f' back with no listings at all.')
                    print(f'  The {who} key ...{k[-6:]} has almost certainly run'
                          f' out without saying so.')
                    print('  It returns HTTP 200 and an empty list, which reads')
                    print('  exactly like "this product is not sold anywhere".')
                    print()
                    print('  Nothing collected is lost. Put a working key at the')
                    print('  top of KEYS, then run:')
                    print('     py serper_price.py --retry-empty')
                    print('  which re-asks every product that came back empty.')
                    print('  ' + '!' * 62)
                    _reason[0] = 'silent'
                    _stop.set()
        return offers, 200


REASONS = {}


def price_for(brand, name):
    """Return (price, seller, offers used, why not, rating, rating count)."""
    offers, status = shopping(query_for(brand, name))
    if status != 200:
        return None, '', 0, str(status), None, 0
    if not offers:
        return None, '', 0, 'no listings', None, 0
    good, sellers, why = [], [], []
    rates, rate_ns = [], []
    for o in offers[:MAX_OFFERS * 3]:
        title, seller, price_txt, o_rating, o_rating_n = read_offer(o)
        if RESALE.search(seller):
            why.append('secondhand marketplace')
            continue
        ok, reason = offer_ok(title, brand, name)
        if not ok:
            why.append(reason)
            continue

        # RATING COMES FREE.
        #
        # The same reply that carries the price also carries "rating" and
        # "ratingCount" for most listings. It is the same credit, already
        # spent, so a separate rating pass would be paying twice for one
        # answer. Only listings that PASSED the brand and name tests above
        # are read, so a rating can never come from a different product.
        try:
            rv = float(o_rating)
            rn = int(float(str(o_rating_n or 0).replace(',', '')))
            if 0 < rv <= 5 and rn > 0:
                rates.append(rv)
                rate_ns.append(rn)
        except (TypeError, ValueError):
            pass

        v = to_number(price_txt)
        if v is None:
            why.append('price not in USD')
            continue
        if not (MIN_PRICE <= v <= MAX_PRICE):
            why.append('price out of range')
            continue
        good.append(v)
        sellers.append(seller)
        if len(good) >= MAX_OFFERS:
            break

    # the rating is WEIGHTED by how many people left it. A 5.0 from 3 buyers
    # should not outweigh a 4.3 from 12,000, and a plain average does exactly
    # that.
    if rates:
        tot_n = sum(rate_ns)
        rating = round(sum(r * n for r, n in zip(rates, rate_ns)) / tot_n, 2)
        rating_n = tot_n
    else:
        rating, rating_n = None, 0

    if not good:
        return None, '', 0, (why[0] if why else 'no usable offer'), rating, rating_n
    med = statistics.median(good)
    # name the seller whose price is closest to the median we are storing
    seller = sellers[min(range(len(good)), key=lambda j: abs(good[j] - med))]
    return round(med, 2), seller, len(good), '', rating, rating_n


# ===================================================================== data
csv.field_size_limit(10 ** 8)      # review text and ingredient lists are long
with open(DATA, newline='', encoding='utf-8') as fh:
    reader = csv.DictReader(fh)
    FIELDS = list(reader.fieldnames or [])
    rows_all = [{k: (v if v is not None else '') for k, v in r.items()}
                for r in reader]

NEW_COLS = ['price_usd_market', 'price_market_source', 'price_market_n',
            'price_market_date', 'rating_market', 'rating_market_count']
for cname in NEW_COLS:
    if cname not in FIELDS:
        FIELDS.append(cname)
for r in rows_all:
    for cname in NEW_COLS:
        r.setdefault(cname, '')
    r.pop(None, None)


def count_filled(col):
    return sum(1 for r in rows_all if str(r.get(col, '')).strip())


NROWS = len(rows_all)

COLS = ['product_id', 'brand', 'name', 'price', 'seller', 'n_offers', 'date',
        'why_not', 'rating', 'rating_n']

# THE PROGRESS FILE MAY BE AN OLDER SHAPE.
#
# The first real run wrote 8 columns, before rating was being collected. This
# script now writes 10. Appending 10-wide rows under an 8-wide header produces
# a file where every new rating is unreadable: the reader takes the header as
# the truth and drops anything past it. So the file is widened first, keeping
# every row already in it.
if os.path.exists(PROGRESS):
    with open(PROGRESS, newline='', encoding='utf-8') as f:
        head = next(csv.reader(f), [])
    if head and head != COLS:
        with open(PROGRESS, newline='', encoding='utf-8') as f:
            old = list(csv.DictReader(f))
        with open(PROGRESS, 'w', newline='', encoding='utf-8') as f:
            wr = csv.DictWriter(f, COLS, extrasaction='ignore')
            wr.writeheader()
            for r in old:
                wr.writerow({k: r.get(k, '') for k in COLS})
        print(f'  widened {PROGRESS} from {len(head)} to {len(COLS)} columns, '
              f'{len(old):,} rows kept')

done = {}
if os.path.exists(PROGRESS):
    with open(PROGRESS, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            prev = done.get(row['product_id'])
            # the file is append-only, so a product re-asked later appears
            # twice. The LAST line wins, unless the last line found nothing
            # and an earlier one did.
            if prev and not row.get('price') and prev.get('price'):
                continue
            done[row['product_id']] = row

# ------------------------------------------------------------------- --apply
if APPLY:
    if not done:
        sys.exit(f'{PROGRESS} is empty or missing. Run without --apply first.')
    n = nr = skipped_resale = 0
    for row in rows_all:
        r = done.get(row['product_id'])
        if not r:
            continue
        # A price from a secondhand marketplace is never written, whatever is
        # in the progress file. The filter above stops new ones being
        # collected; this stops an old one from before the filter existed
        # slipping through on a row the refetch could not improve.
        if r.get('price') and RESALE.search(str(r.get('seller', ''))):
            skipped_resale += 1
            continue
        if r.get('price'):
            row['price_usd_market'] = r['price']
            row['price_market_source'] = r['seller']
            row['price_market_n'] = r['n_offers']
            row['price_market_date'] = r['date']
            n += 1
        # a rating can arrive without a usable price, and is still worth having
        if r.get('rating'):
            row['rating_market'] = r['rating']
            row['rating_market_count'] = r.get('rating_n', '')
            if not row['price_market_date']:
                row['price_market_date'] = r['date']
            nr += 1
    # keep the price columns together, market price just right of the shop price
    cols = list(FIELDS)
    for cname in ('rating_market_count', 'rating_market', 'price_market_date',
                  'price_market_n', 'price_market_source', 'price_usd_market'):
        if cname in cols and 'price_usd_max' in cols:
            cols.remove(cname)
            cols.insert(cols.index('price_usd_max') + 1, cname)

    # Written to a temporary file and renamed only once it is complete. A
    # crash halfway through a direct write would leave the dataset truncated,
    # and this script is run repeatedly on a machine where runs do get
    # interrupted.
    tmp = DATA + '.tmp'
    with open(tmp, 'w', newline='', encoding='utf-8') as fh:
        wr = csv.DictWriter(fh, cols, extrasaction='ignore')
        wr.writeheader()
        wr.writerows(rows_all)
    # read back before replacing the real file. A crash mid-write once put
    # machine code inside COMBINED_DATASET.csv, and nothing noticed until a
    # later script tried to read it.
    with open(tmp, 'rb') as _f:
        _raw = _f.read()
    try:
        _raw.decode('utf-8')
    except UnicodeDecodeError as _e:
        os.remove(tmp)
        raise SystemExit(f'  the file came back damaged at byte {_e.start:,}, '
                         f'nothing was replaced. run it again.')
    os.replace(tmp, DATA)

    got = count_filled('price_usd_market')
    both = sum(1 for r in rows_all
               if str(r.get('price_usd', '')).strip()
               and str(r.get('price_usd_market', '')).strip())
    print(f'  wrote {n:,} market prices into {DATA}')
    if skipped_resale:
        print(f'  refused {skipped_resale:,} prices from secondhand '
              f'marketplaces (eBay, Poshmark, Mercari)')
    print(f'  products with a market price   {got:,}  ({100*got/NROWS:.1f}%)')
    print(f'  products with BOTH prices      {both:,}   <- Lebanon vs world')
    gotr = count_filled('rating_market')
    had = count_filled('rating')
    newr = sum(1 for r in rows_all
               if not str(r.get('rating', '')).strip()
               and str(r.get('rating_market', '')).strip())
    print()
    print(f'  wrote {nr:,} market ratings, at no extra cost')
    print(f'  products with a market rating  {gotr:,}  ({100*gotr/NROWS:.1f}%)')
    print(f'  products that had no rating    {newr:,}  <- newly rated')
    print(f'  rating coverage {had:,} -> {had+newr:,}'
          f'  ({100*(had+newr)/NROWS:.1f}%)')
    print('\n  price_usd is untouched. It still means "a Lebanese shop charged this".')
    sys.exit(0)

# ------------------------------------------------------------------- the run
# By default only products that have NO price at all. A product already priced
# by a Lebanese shop is not urgent, and 6,059 of them would double the bill.
#
# --all includes those too. That is the version worth running later if credits
# allow, because a product with BOTH prices is the only place the Lebanon-
# versus-world comparison can actually be made.
need = [r for r in rows_all
        if not r['price_usd_market'].strip()
        and r.get('brand', '').strip() and r.get('name', '').strip()]
if '--all' not in sys.argv:
    need = [r for r in need if not r.get('price_usd', '').strip()]
# --refetch-resale re-asks only the products whose stored price came from a
# secondhand marketplace. Those rows were collected before the RESALE filter
# existed, so they are the only ones that need paying for twice.
REDO = set()

# --missing-rating re-asks the products that already have a market price but
# no rating. There are 900 of them, and they exist for one reason: they were
# collected before this script started reading the rating out of the reply.
# The price is fine, so this is buying the rating alone.
#
# WORTH KNOWING BEFORE SPENDING ON IT: a plain run costs the same credit and
# returns a price AND a rating, because the products it asks about have
# neither yet. So the plain run is better value per credit, and this mode is
# only for finishing off the ones already half-done.
if '--missing-rating' in sys.argv:
    REDO = {r['product_id'] for r in rows_all
            if r.get('price_usd_market', '').strip()
            and not r.get('rating_market', '').strip()}
    need = [r for r in rows_all if r['product_id'] in REDO]
    print(f'  re-asking {len(REDO):,} products that have a price but no rating')

# --retry-empty re-asks every product whose last answer was "no listings".
#
# Those rows are a mix of two very different things: products that genuinely
# are not sold online, and products that were asked while a key was silently
# dead. There is no way to tell them apart from the file, so all of them are
# asked again. The ones that really have no listings will come back empty a
# second time and cost one credit each to confirm, which is the price of not
# recording a dead key's silence as a fact about Lebanese skincare.
if '--retry-empty' in sys.argv:
    REDO = {k for k, v in done.items()
            if not v.get('price') and v.get('why_not') == 'no listings'}
    need = [r for r in rows_all if r['product_id'] in REDO]
    print(f'  re-asking {len(REDO):,} products that came back with no listings')

if '--refetch-resale' in sys.argv:
    REDO = {k for k, v in done.items()
            if v.get('price') and RESALE.search(str(v.get('seller', '')))}
    print(f'  re-asking {len(REDO):,} products priced by a resale seller')

if REDO:
    # ONLY the resale rows. Cleaning up 255 known-bad prices for 255 credits
    # is a different decision from spending 6,000 on the rest, and running
    # them together would make you commit to both at once.
    need = [r for r in need if r['product_id'] in REDO]
else:
    need = [r for r in need if r['product_id'] not in done]
# --lebanon-first puts the Lebanese products at the front of the queue.
#
# WHY THIS EXISTS. The queue runs in dataset order, so all 6,350 global
# products are asked before the first Lebanese one. Every run so far has run
# out of credits partway through the global block, which means the 965 Lebanese
# origin products have been asked exactly once, during the run where a key had
# silently died. Their answer of "no listings" is worthless.
#
# That leaves the one genuinely interesting question in this column
# unanswered: do Lebanese-made products appear on Google Shopping at all? It is
# 977 requests, it fits inside a single free key, and it is worth more to the
# thesis than 977 more prices for Korean serums.
if '--lebanon-first' in sys.argv:
    lb = [r for r in need if r.get('source_category', '').startswith('Lebanese')]
    rest = [r for r in need if not r.get('source_category', '').startswith('Lebanese')]
    need = lb + rest
    print(f'  Lebanese products moved to the front of the queue: {len(lb):,}')

if TEST:
    import random as _rnd
    _rnd.Random(1).shuffle(need)
    need = need[:TEST]

print('=' * 72)
print('  PRICE FROM GOOGLE SHOPPING')
print('=' * 72)
print(f'  products with no market price yet  {len(need):,}')
print(f'  already collected in {PROGRESS}     {len(done):,}')
# The two services give different amounts away, and the Serper key that was
# meant to hold 2,500 actually stopped at 1,260. So this is labelled as a
# guess rather than printed as if it were a fact.
# What each free tier is worth in QUESTIONS, not credits. Serper charges two
# credits for a shopping query, so its 2,500 answers about 1,250.
FREE = {'serper': 1250, 'talordata': 500, 'scraperapi': 1000,
        'rayobyte': 0}
budget = sum(FREE[provider_of(k)] for k in KEYS)
by_who = {}
for k in KEYS:
    by_who[provider_of(k)] = by_who.get(provider_of(k), 0) + 1
print(f'  keys loaded                        '
      + ', '.join(f'{n} {w}' for w, n in by_who.items()))
print(f'  free allowance, at best            ~{budget:,} requests')
if budget < len(need):
    short = len(need) - budget
    print(f'  SHORT BY ABOUT {short:,}. Talordata sells 5,000 for about $5, '
          f'so finishing\n  the whole job costs roughly '
          f'${max(1, round(short/1000)):,}.')
if TEST:
    print(f'  TEST RUN: {len(need):,} products, nothing will be written')
print()

new_f = not os.path.exists(PROGRESS)
out = None if TEST else open(PROGRESS, 'a', newline='', encoding='utf-8')
writer = None
if out:
    writer = csv.writer(out)
    if new_f:
        writer.writerow(COLS)

hit = [0]
miss = [0]
rated = [0]
t0 = time.time()
rows = need


def work(t):
    if _stop.is_set():
        return
    p, seller, n_off, why, rating, rating_n = price_for(t['brand'], t['name'])
    with _lock:
        if p:
            hit[0] += 1
        else:
            miss[0] += 1
            REASONS[why] = REASONS.get(why, 0) + 1
        if rating:
            rated[0] += 1
        if writer:
            writer.writerow([t['product_id'], t['brand'], t['name'], p or '', seller,
                             n_off, TODAY, why, rating or '', rating_n or ''])
            out.flush()
        d = hit[0] + miss[0]

        # THE STOP RULE, APPLIED AUTOMATICALLY.
        #
        # The same rule used for skin type and for ingredients: below about a
        # quarter, paid search is not worth what it costs. Twice in this
        # project a run was left going that should have been stopped, and once
        # a run "sped through" thousands of products doing nothing while a
        # falling percentage made it look like progress.
        #
        # So the script applies the rule to itself. After 150 answers, if fewer
        # than 15% produced a price, it stops and says why. Nothing collected
        # so far is lost, and starting it again resumes.
        if d == 150 and hit[0] / d < 0.15:
            print('\n  ' + '!' * 60)
            print(f'  STOPPING EARLY. {hit[0]} prices out of the first 150'
                  f' ({100*hit[0]/d:.1f}%).')
            print('  That is below the rate that makes paid search worth it,')
            print('  so the remaining credits are not spent automatically.')
            print('  The most common reasons are listed at the end.')
            print('  ' + '!' * 60)
            _reason[0] = 'rate'
            _stop.set()

        if d % 100 == 0 or d == len(rows):
            rate = 100 * hit[0] / d
            el = time.time() - t0
            left = (len(rows) - d) * el / max(d, 1)
            print(f'  {d:6,}/{len(rows):,}   price {hit[0]:5,} ({rate:4.1f}%)'
                  f'   rating {rated[0]:5,}'
                  f'   credits {_spent[0]:,}'
                  f'   {int(left//60)}m left')


with ThreadPoolExecutor(WORKERS) as ex:
    list(ex.map(work, rows))

if out:
    out.close()

d = hit[0] + miss[0]
print()
print('=' * 72)
print(f'  asked about        {d:,}')
print(f'  price found        {hit[0]:,}  ({100*hit[0]/max(d,1):.1f}%)')
print(f'  rating found       {rated[0]:,}  ({100*rated[0]/max(d,1):.1f}%)   free, same reply')
print(f'  no price           {miss[0]:,}')
print(f'  questions asked    {_requests[0]:,}')
print(f'  credits used       {_spent[0]:,}'
      + (f'   ({_spent[0]/max(_requests[0],1):.1f} per question)'
         if _requests[0] else ''))
if REASONS:
    print('\n  WHY THE REST FAILED')
    for k, v in sorted(REASONS.items(), key=lambda x: -x[1])[:8]:
        print(f'    {str(k):26s}{v:6,}')

if hit[0]:
    vals = []
    src = {}
    if os.path.exists(PROGRESS):
        # The file is append-only, so a product re-asked later is in it twice.
        # Summarising every line counted superseded resale prices alongside the
        # shop prices that replaced them, and listed eBay as a top seller after
        # eBay had just been banned. Only the surviving row for each product
        # counts, and never a resale one.
        latest = {}
        with open(PROGRESS, newline='', encoding='utf-8') as f:
            for r in csv.DictReader(f):
                prev = latest.get(r['product_id'])
                if prev and not r.get('price') and prev.get('price'):
                    continue
                latest[r['product_id']] = r
        for r in latest.values():
            if r.get('price') and not RESALE.search(str(r.get('seller', ''))):
                vals.append(float(r['price']))
                src[r['seller']] = src.get(r['seller'], 0) + 1
    if vals:
        vals.sort()
        print('\n  WHAT CAME BACK')
        print(f'    cheapest   ${vals[0]:,.2f}')
        print(f'    median     ${statistics.median(vals):,.2f}')
        print(f'    dearest    ${vals[-1]:,.2f}')
        print('    sellers    ' + ', '.join(
            f'{k} {v:,}' for k, v in sorted(src.items(), key=lambda x: -x[1])[:5]))

if TEST:
    # WHAT THE FULL JOB ACTUALLY IS.
    #
    # This used to count every product with no MARKET price, which came to
    # 7,672 and invited spending 7,672 credits. But 6,673 of those already
    # have a shop price, and the tidy file uses the shop price first, so
    # buying a market price for them changes nothing anyone will ever see.
    #
    # The number that matters is products with NO price from anywhere.
    no_market = sum(1 for r in rows_all if not r['price_usd_market'].strip())
    no_price = sum(1 for r in rows_all
                   if not r['price_usd_market'].strip()
                   and not r.get('price_usd', '').strip())
    rate = hit[0] / max(d, 1)
    print(f'\n  THE FULL JOB')
    print(f'     {no_price:,} products have no price from anywhere. These are '
          f'the ones worth paying for.')
    print(f'     at this hit rate, roughly {int(no_price*rate):,} prices for '
          f'{no_price*2:,} credits')
    if no_market > no_price:
        print(f'\n     a further {no_market-no_price:,} have no MARKET price '
              f'but DO have a shop price.')
        print(f'     --all would ask about those too, at {(no_market-no_price)*2:,} '
              f'more credits, and')
        print(f'     would not change the price coverage the tidy file '
              f'reports, because it')
        print(f'     uses the shop price first. Worth it only for comparing '
              f'Lebanon against')
        print(f'     the world price, which is a different question.')
    print(f'\n     NOTE the rate above was measured on this sample. Products '
          f'already asked')
    print(f'     once and found nowhere will do worse than a fresh sample '
          f'does.')
    print('\n  nothing was written. drop --test to run it for real.')
elif _stop.is_set():
    # say WHICH stop fired. An earlier version told you the keys ran out
    # whatever had happened, including when the run stopped one credit in
    # because the reply looked wrong.
    print(f'\n  STOPPED. {len(done)+d:,} products are saved in {PROGRESS},')
    print('  and running it again resumes from there. Reason:')
    if _reason[0] == 'silent':
        print('    a key stopped returning results without reporting an error.')
        print('    add a working key and run again with --retry-empty.')
    elif _reason[0] == 'shape':
        print('    the reply did not look like shopping results.')
        print('    send me the keys printed above, do not rerun yet.')
    elif _reason[0] == 'rate':
        print('    too few products were coming back with a price.')
        print('    read WHY THE REST FAILED above before spending more.')
    else:
        print('    every key ran out of credits.')
        print('    add another to SERPER_KEYS and run again.')
else:
    print(f'\n  saved to {PROGRESS}')
    print('  now run:  py serper_price.py --apply')
