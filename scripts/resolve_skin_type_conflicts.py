"""
Where two shops disagree, ask a third source

The problem
  174 products have a skin type stated by two Lebanese shops that do not
  match. One says Dry, the other says All Skin Types. Something has to decide,
  and up to now the merge simply took the lower tier.

Usage:
    py resolve_skin_type_conflicts.py --dry     show each decision, change nothing
    py resolve_skin_type_conflicts.py           fetch and decide
    py resolve_skin_type_conflicts.py --apply   write the decisions in
"""
import os
import re
import csv
import sys
import json
import time
import queue
import threading
import collections

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
DOMAINS = 'brand_domains.json'
SITEMAP_CACHE = 'sitemap_urls.json'
CACHE = 'skin_type_third_source.json'
WORKERS = 12
GAP = 0.6
NAME_FLOOR = 86

DRY = '--dry' in sys.argv
APPLY = '--apply' in sys.argv

# ------------------------------------------- borrowed, so nothing is copied
_sm = open('fill_ingredients_sitemaps.py', encoding='utf-8').read()
_head = _sm.split('# ===================================================='
                  '================= data')[0]
_ns = {}
exec(compile(_head, 'matcher', 'exec'), _ns)
words = _ns['words']
similarity = _ns['similarity']
slug_of = _ns['slug_of']
bkey = _ns['bkey']
read_skin_type = _ns['read_skin_type']
strip_html = _ns['strip_html']
fetch = _ns['fetch']

VALID = {'dry', 'oily', 'combination', 'normal', 'all', 'sensitive'}


def clean_stated(text):
    """
    The skin types a shop actually STATED, discarding anything that is not one.

    A shop field reading "It has ingredients that are good for anti aging"
    is an analysis blurb, not a claim about skin type. Comparing a claim to a
    blurb and calling the difference a disagreement would inflate the conflict
    count and then resolve conflicts that were never real.
    """
    out = []
    for piece in re.split(r'[|,/]', str(text)):
        p = piece.strip().lower()
        p = re.sub(r'\s*skin\s*types?\s*$', '', p).strip()
        if not p or len(p) > 14:
            continue
        if p in VALID:
            out.append(p.capitalize())
    return out


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
cache = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}

conflict = [r for r in D if g(r, 'retailers_agree') == 'no']

print('=' * 74)
print('  WHERE TWO SHOPS DISAGREE, ASK A THIRD SOURCE')
print('=' * 74)
print(f'  products flagged as disagreeing      {len(conflict):,}')

real, artefact, settled = [], [], []
for r in conflict:
    if g(r, 'skin_type_tier') == '1':
        settled.append(r)
        continue
    stated = sorted(set(clean_stated(g(r, 'retailer_skin_types'))))
    if len(stated) < 2:
        artefact.append(r)
    else:
        real.append((r, stated))

print(f'  already answered by the manufacturer  {len(settled):,}  '
      f'(nothing to resolve)')
print(f'  not a real disagreement               {len(artefact):,}  '
      f'(one side was an analysis blurb, not a stated skin type)')
print(f'  genuine conflicts to resolve          {len(real):,}')
reachable = [(r, s) for r, s in real if bkey(g(r, 'brand')) in SITES]
print(f'  of those, brand site known            {len(reachable):,}')
print()

if real:
    print('  FIVE GENUINE CONFLICTS')
    for r, s in real[:5]:
        print(f'    {g(r, "brand")[:18]:20s} {g(r, "name")[:34]:36s}')
        print(f'        shops say {s},  currently {g(r, "skin_type")!r} '
              f'(tier {g(r, "skin_type_tier")})')
    print()

# -------------------------------------------------- ask the brand's own site
jobs = []
for r, stated in reachable:
    pid = g(r, 'product_id')
    if pid in cache:
        continue
    dom = SITES.get(bkey(g(r, 'brand')), '')
    urls = smap.get(dom) or []
    if not urls:
        continue
    mine = words(g(r, 'name'), g(r, 'brand'))
    best, score = None, 0
    for u in urls:
        w = words(slug_of(u), g(r, 'brand'))
        if not w:
            continue
        sc = similarity(mine, w)
        if sc > score:
            best, score = u, sc
    if best and score >= NAME_FLOOR:
        jobs.append((pid, best))

print(f'  matched to a page on the brand site   {len(jobs):,}')

if DRY:
    print('\n  --dry, nothing fetched and nothing written.')
    sys.exit(0)

lock = threading.Lock()
last_hit = collections.defaultdict(float)
counts = collections.Counter()
q = queue.Queue()
for j in jobs:
    q.put(j)


def dom_of(u):
    m = re.match(r'https?://([^/]+)', str(u), re.I)
    return m.group(1).lower().replace('www.', '') if m else ''


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
                text = strip_html(fetch(url))
            except Exception:
                with lock:
                    counts['page would not load'] += 1
                continue
            st = read_skin_type(text)
            with lock:
                cache[pid] = {'skin_type': st, 'url': url}
                counts['brand stated one' if st
                       else 'brand said nothing'] += 1
        finally:
            q.task_done()


if jobs:
    ts = [threading.Thread(target=work, daemon=True) for _ in range(WORKERS)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    json.dump(cache, open(CACHE, 'w', encoding='utf-8'))
    for k, v in counts.most_common():
        print(f'     {v:5,}  {k}')

# ------------------------------------------------------------ decide, write
by_id = {g(r, 'product_id'): r for r in D}
n_brand = n_vote = n_tie = 0
log = []
for r, stated in real:
    pid = g(r, 'product_id')
    third = (cache.get(pid) or {}).get('skin_type', '')
    third_base = [p for p in clean_stated(third) if p.lower() != 'sensitive']

    if len(third_base) == 1:
        # a better source settles it outright
        choice, how, tier = third_base[0], \
            'the manufacturer, asked as a third source', '1'
        n_brand += 1
    else:
        tally = collections.Counter(stated)
        top = tally.most_common()
        if len(top) > 1 and top[0][1] == top[1][1]:
            n_tie += 1
            log.append((r, stated, third, 'left alone, shops tied and the '
                                          'brand said nothing'))
            continue
        choice, how, tier = top[0][0], 'the value more shops stated', '2'
        n_vote += 1

    if not APPLY:
        log.append((r, stated, third, f'{choice}  <- {how}'))
        continue
    r['skin_type'] = choice
    if 'skin_type_tier' in r:
        r['skin_type_tier'] = tier
    if 'skin_type_authority' in r:
        r['skin_type_authority'] = ('manufacturer' if tier == '1'
                                    else 'retailer')
    if 'skin_type_source' in r:
        r['skin_type_source'] = how
    if 'retailers_agree' in r:
        r['retailers_agree'] = 'resolved by ' + (
            'the manufacturer' if tier == '1' else 'majority')
    log.append((r, stated, third, f'{choice}  <- {how}'))

print(f'\n  DECISIONS')
print(f'     settled by the manufacturer   {n_brand:,}')
print(f'     settled by what most shops said {n_vote:,}')
print(f'     left alone, genuinely unresolved {n_tie:,}')
print('\n  TEN DECISIONS')
for r, stated, third, note in log[:10]:
    print(f'    {g(r, "brand")[:16]:18s} {g(r, "name")[:30]:32s}')
    print(f'        shops {stated}   brand said {third!r}')
    print(f'        -> {note}')

if not APPLY:
    print('\n  nothing written. run again with --apply to write these in.')
    sys.exit(0)

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
print(f'\n  written. now rebuild:')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
