"""
Ingredients from the lebanese shop pages. costs nothing.

The situation
  4,696 of the 7,212 Lebanese products have no ingredient list. The cell is not
  empty, which is worse: it contains the literal string "Not available", so
  every coverage count treated it as filled. That is the same species of error
  as the review_source column containing the word "none".

  This script blanks those placeholders and then tries to fill them properly.

Usage:
    py scrape_lebanese_ingredients.py              all of them
    py scrape_lebanese_ingredients.py --test 100   try 100 first, write nothing
"""
import re
import sys
import time
import html as htmllib
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

DATA = 'LEBANESE_RETAIL.csv'
WORKERS = 8
TIMEOUT = 18
TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 100

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'}

PLACEHOLDER = re.compile(r'^(not available|not specified|n/?a|none|unknown|-|'
                         r'not comparable|no information)$', re.I)

# headings that introduce an ingredient list, in the languages these shops use
HEADING = re.compile(
    r'(ingredients?|composition|inci|ingr[ée]dients?|contents|formula|'
    r'what.s inside|full ingredient list|المكونات|تركيبة)', re.I)

# vocabulary that only appears in a real INCI list
INCI_WORDS = re.compile(
    r'\b(aqua|water|glycerin|glycerine|alcohol denat|butylene glycol|'
    r'propylene glycol|sodium|potassium|cetearyl|stearyl|cetyl|dimethicone|'
    r'phenoxyethanol|tocopherol|parfum|fragrance|citric acid|xanthan|'
    r'carbomer|panthenol|niacinamide|extract|seed oil|butter|acid|'
    r'polysorbate|laureth|glyceryl|caprylic|triglyceride|benzoate|sorbate)\b',
    re.I)
START_OK = re.compile(r'^\s*(aqua|water|eau|glycerin|alcohol|cyclopenta|'
                      r'dimethicone|butylene|propylene|isododecane|'
                      r'caprylic|cetearyl|paraffinum|petrolatum|zinc oxide|'
                      r'titanium dioxide|homosalate|avobenzone|ethylhexyl)', re.I)
BAD = re.compile(r'(add to (cart|bag)|<script|function\s*\(|window\.|cookie|'
                 r'shipping|delivery|return policy|©|sign in|newsletter)', re.I)

TAG = re.compile(r'<[^>]+>')


def clean(t):
    t = htmllib.unescape(TAG.sub(' ', t))
    return re.sub(r'\s+', ' ', t).strip(' :.-•|')


def looks_like_inci(t):
    """The shape test. A heading is not enough; the text has to behave like a
    formula. Wrong ingredients are worse than none, so this is deliberately
    strict."""
    if not t or len(t) < 60 or len(t) > 6000:
        return False
    if BAD.search(t):
        return False
    if t.count(',') < 3:
        return False
    hits = len(INCI_WORDS.findall(t))
    if hits < 3:
        return False
    # a formula is mostly short comma-separated names, not sentences
    parts = [p.strip() for p in t.split(',') if p.strip()]
    if len(parts) < 4:
        return False
    long_parts = sum(1 for p in parts if len(p.split()) > 6)
    if long_parts > len(parts) * 0.4:
        return False
    return bool(START_OK.match(t)) or hits >= 6


# Prose that gets glued to the front of a list when the word "ingredients"
# appears inside a sentence, e.g. "Main ingredients : Water, Glycerin...".
# Without trimming, the stored value began with usage instructions.
INSTRUCTION = re.compile(
    r'\b(apply|rinse|massage|peel it off|leave on|use (?:morning|daily|twice)|'
    r'caution|for external use|avoid contact|keep out of reach|patch test|'
    r'discontinue|shake well|store in)\b', re.I)
# where a formula actually begins
LEADIN = re.compile(r'\b(?:full\s+|main\s+|key\s+|active\s+|other\s+)?'
                    r'(?:ingredients?|inci|composition|contents)\b\s*[:\-–]?\s*', re.I)


def trim_to_formula(t):
    """Cut everything before the list actually starts.

    Two ways in, tried in order:
      1. a lead-in label inside the text  ("Main ingredients : Water, ...")
      2. the first classic formula opener ("Aqua", "Water", "Glycerin", ...)

    Returns '' if neither is found, because a chunk with no identifiable
    starting point is prose that merely mentions ingredients.
    """
    if not t:
        return ''
    best = ''
    for m in LEADIN.finditer(t):
        cand = t[m.end():].strip(' :.-–•|')
        if len(cand) > len(best) and looks_like_inci(cand):
            best = cand
            break
    if not best:
        m = START_OK.search(t)
        if m:
            cand = t[m.start():].strip(' :.-–•|')
            if looks_like_inci(cand):
                best = cand
    if not best:
        return ''
    # the list ends where the page moves on to something else
    best = re.split(r'\b(?:how to use|directions|how to apply|benefits|reviews|'
                    r'description|shipping|caution|warning|for external use|'
                    r'related products|you may also like)\b',
                    best, maxsplit=1, flags=re.I)[0].strip(' :.-–•|')
    # instructions inside the first stretch mean we never found the list
    if INSTRUCTION.search(best[:120]):
        return ''
    return best if looks_like_inci(best) else ''


def extract_inci(page):
    """Look for a list under a heading first, then anywhere on the page.

    Every candidate is trimmed to where the formula really begins. An earlier
    version stored whatever followed the word "ingredients", which captured
    usage instructions and marketing copy.
    """
    body = re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', page)

    # 1. text following an ingredients heading
    for m in HEADING.finditer(body):
        chunk = clean(body[m.end():m.end() + 4000])
        chunk = re.split(r'(?:how to use|directions|benefits|reviews|'
                         r'description|shipping|related products)', chunk,
                         maxsplit=1, flags=re.I)[0]
        got = trim_to_formula(chunk)
        if got:
            return got[:4000], 'under an ingredients heading'

    # 2. any block on the page that behaves like a formula
    for block in re.split(r'</p>|</div>|</li>|<br\s*/?>', body):
        got = trim_to_formula(clean(block))
        if got:
            return got[:4000], 'a formula-shaped block on the page'
    return None, ''


S = requests.Session()
S.headers.update(HEAD)
lock = threading.Lock()
done = [0]
found = {}
where = {}
how = {}

df = pd.read_csv(DATA, dtype=str, low_memory=False).fillna('')
N = len(df)

# ---- blank the placeholders first, so nothing counts them as data again
for col in ('ingredients', 'key_ingredients', 'free_from', 'benefits'):
    if col in df.columns:
        mask = df[col].str.strip().str.match(PLACEHOLDER, na=False)
        df.loc[mask, col] = ''
print(f'{N:,} Lebanese products')
print(f'placeholders blanked, real ingredient coverage is now '
      f'{int((df["ingredients"] != "").sum()):,} ({100*(df["ingredients"] != "").sum()/N:.1f}%)\n')

for c in ('ingredient_source', 'ingredient_url'):
    if c not in df.columns:
        df[c] = ''

# --refresh-shops re-reads rows that ALREADY have a shop-sourced list.
# Needed once, because the first validator trimmed 1,804 lists and some of
# those trims cut real ingredients off the front. A row that still holds text
# is not "missing", so the normal run skips it and the damage stays.
REFRESH = '--refresh-shops' in sys.argv
if REFRESH:
    need = df[(df['ingredient_source'] != '') & (df['retailer_urls'] != '')]
    print(f'REFRESH: re-reading {len(need):,} rows that were scraped from a shop,')
    print('to undo the trimming the first validator did\n')
else:
    need = df[(df['ingredients'] == '') & (df['retailer_urls'] != '')]

if TEST:
    need = need.sample(min(TEST, len(need)), random_state=11)
    print(f'TEST MODE: trying {len(need)} products, nothing will be saved\n')
elif not REFRESH:
    print(f'{len(need):,} products need an ingredient list and have a shop URL\n')


def work(i):
    urls = [u for u in str(df.at[i, 'retailer_urls']).split(' | ')
            if u.startswith('http')][:3]      # try up to 3 shops for the product
    for url in urls:
        try:
            r = S.get(url, timeout=TIMEOUT)
            if r.status_code != 200:
                continue
            ing, method = extract_inci(r.text)
            if ing:
                host = url.split('/')[2].replace('www.', '')
                with lock:
                    found[i] = (ing, host, url)
                    where[host] = where.get(host, 0) + 1
                    how[method] = how.get(method, 0) + 1
                return
        except Exception:
            continue
    return


with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    futs = [ex.submit(work, i) for i in need.index]
    for fut in as_completed(futs):
        with lock:
            done[0] += 1
            if done[0] % 100 == 0:
                print(f'   {done[0]:,}/{len(need):,}   found {len(found):,}'
                      f'   ({100*len(found)/max(done[0],1):.0f}%)', flush=True)

rate = 100 * len(found) / max(len(need), 1)
print(f'\n   attempted {len(need):,}   found {len(found):,}   ({rate:.1f}%)')
if where:
    print('\n   which shops publish ingredients:')
    for h, n in sorted(where.items(), key=lambda x: -x[1]):
        print(f'      {h:22s}{n:6,}')
    print('\n   how they were found:')
    for k, v in sorted(how.items(), key=lambda x: -x[1]):
        print(f'      {k:38s}{v:6,}')

print('\n   EXAMPLES')
for i in list(found)[:5]:
    ing, host, url = found[i]
    print(f'      {df.at[i,"brand"][:16]:16s} {df.at[i,"name"][:34]:34s} [{host}]')
    print(f'         {ing[:100]}...')

if TEST:
    print('\n' + '=' * 62)
    print(f'  TEST ONLY, nothing written.')
    n_need = int(((df['ingredients'] == '') & (df['retailer_urls'] != '')).sum())
    print(f'  hit rate {rate:.0f}%  ->  a full run would find about '
          f'{int(n_need*rate/100):,} of {n_need:,}')
    print('  run without --test to do it for real')
    raise SystemExit

for i, (ing, host, url) in found.items():
    df.at[i, 'ingredients'] = ing
    df.at[i, 'ingredient_source'] = host
    df.at[i, 'ingredient_url'] = url

df.to_csv(DATA, index=False)
n_now = int((df['ingredients'] != '').sum())
print('\n' + '=' * 62)
print(f'  ingredient coverage   {n_now:,} of {N:,}  ({100*n_now/N:.1f}%)')
print(f'  still missing         {N-n_now:,}')
print('=' * 62)
print('\nnow run:  py serper_ingredients.py    for what the shops did not publish')
