"""
Fill the last gaps in lebanese origin, with search

Where things stand after the free pass
  Reading the brands' own pages took ingredients from 36% to 60% and skin type
  from 40% to 46%. What is left needs searching.

Two parts, and the first is free
  PART 1, NO CREDITS.  Complete the sensitivity axis.
      sensitivity sits at 6%, which is not a gap, it is an oversight. The rule
      used everywhere else in this thesis is that a product which has been
      searched and carries no sensitive-skin claim is RESISTANT, because a
      brand advertises that claim when it has one. Applying the same rule here
      takes sensitivity from 6% to match skin type exactly. It is free and it
      makes this source consistent with the other two.

  PART 2, PAID.  One search per product, used for BOTH missing fields.
      A product missing ingredients and a product missing a skin type are
      usually the same product, and the answer to both is usually on the same
      page. So the page is fetched once and read for both, rather than paying
      twice.

Usage:
    py serper_lebanese_origin.py --free-only    part 1 only, costs nothing
    py serper_lebanese_origin.py --test 100     measure part 2, write nothing
    py serper_lebanese_origin.py                everything
"""
import os
import re
import sys
import csv
import json
import html as htmllib
import unicodedata
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

SERPER_KEYS = [
    '',
            '',
    '',
    '',
]
DATA = 'LEBANESE_ORIGIN.csv'
DOMAINS = 'brand_domains.json'
PROGRESS = 'lebanese_origin_serper_progress.csv'
PFIELDS = ['product_id', 'ingredients', 'ingredient_source', 'ingredient_url',
           'skin_type', 'sensitivity', 'skin_type_rule', 'skin_type_quote',
           'skin_type_source', 'skin_type_url', 'skin_type_tier']
WORKERS = 3
PAGES = 6
TIMEOUT = 20
FREE_ONLY = '--free-only' in sys.argv
TEST = 0
if '--test' in sys.argv:
    i = sys.argv.index('--test')
    TEST = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 100

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8,ar;q=0.7'}

REJECT = re.compile(
    r'(incidecoder|skinsort|skincarisma|cosdna|beautypedia|skinwis|gopicky|'
    r'dermapproved|skinsafeproducts|ewg\.org|thinkdirty|yuka\.io|allure|byrdie|'
    r'vogue|glamour|cosmopolitan|nypost|buzzfeed|poshmark|mercari|depop|vinted|'
    r'instagram|facebook|tiktok|reddit|youtube|pinterest|quora|twitter|x\.com|'
    r'ebay|aliexpress|etsy|dhgate|alibaba|linkedin|blogspot|wordpress\.com|'
    r'medium\.com|wikipedia|google\.)', re.I)

TAG = re.compile(r'<[^>]+>')
JUNK_PIECE = re.compile(r'(app store|google play|add to cart|checkout|©|http|'
                        r'shipping|newsletter|\blogin\b)', re.I)
KNOWN = re.compile(
    r'\b(aqua|water|eau|glycerin|glycerine|sodium|potassium|calcium|zinc|'
    r'titanium|cetearyl|cetyl|stearyl|lauryl|laureth|dimethicone|'
    r'phenoxyethanol|tocopherol|parfum|fragrance|limonene|linalool|xanthan|'
    r'carbomer|panthenol|niacinamide|retinol|ascorbic|hyaluron|salicylic|'
    r'glycolic|lactic|citric|benzoic|sorbic|caprylic|capric|triglyceride|'
    r'polysorbate|peg-|butylene|propylene|pentylene|hexanediol|urea|allantoin|'
    r'bisabolol|squalane|shea|olea|cocos|butyrospermum|simmondsia|prunus|'
    r'helianthus|aloe|centella|camellia|chamomilla|lavandula|rosa|vitis|citrus|'
    r'mineral oil|paraffinum|petrolatum|lanolin|beeswax|cera alba|laurus|'
    r'ethylhexyl|homosalate|avobenzone|edta|paraben|benzyl|caffeine|adenosine|'
    r'arbutin|kojic|azelaic|ceramide|collagen|keratin|hydroxyethyl|'
    r'hydroxypropyl|polyquaternium|acrylates|copolymer|ethanol|isopropyl|'
    r'isododecane|dicaprylyl|coco-|decyl|myristate|palmitate|oleate|honey|'
    r'propolis)', re.I)
CHEM_END = re.compile(
    r'(ate|ite|ide|ine|one|ol|oic acid|ic acid|yl|ene|ose|an|um|ium|extract|'
    r'oil|butter|wax|water|acid|glycol|glycerin|alcohol|gum|powder|seed|leaf|'
    r'root|fruit|flower|juice|ferment|protein|peptide|ceramide|vitamin|silica|'
    r'mica|dioxide|oxide)$', re.I)
VERB = re.compile(r'\b(is|are|was|were|be|has|have|helps?|works?|leaves?|'
                  r'makes?|gives?|provides?|reduces?|improves?|designed|'
                  r'formulated|apply|rinse|use|our|your|we |this |that )\b', re.I)
BENEFIT = re.compile(r'\s*(hydrating|moisturi[sz]ing|brightening|anti[- ]?ag\w+|'
                     r'soothing|calming|firming|smoothing|nourishing|'
                     r'purifying|exfoliating|cleansing|radiance|glow)\s*', re.I)
INSTRUCTION = re.compile(r'\b(apply|rinse|massage|leave on|caution|patch test|'
                         r'for external use|avoid contact)\b', re.I)
SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)
STOP = {'the', 'and', 'for', 'with', 'of', 'de', 'la', 'le', 'du', 'new', 'set',
        'kit', 'skin', 'face', 'ml', 'g', 'in', 'to', 'a', 'x', 'buy', 'free'}
GAP = 2
TYPE_W = {'dry': 'Dry', 'oily': 'Oily', 'oil': 'Oily', 'combination': 'Combination',
          'combo': 'Combination', 'normal': 'Normal', 'acne': 'Oily'}
UNIV = re.compile(r'\b(all skin types?|every skin type|tous types de peaux?)\b', re.I)
CLAIM = [
    (1, 'declared field',
     re.compile(r'skin[\s_-]*type[^a-z0-9]{0,4}\s*[:\-]\s*([A-Za-z ,/&+-]{3,60})', re.I)),
    (2, 'suitability sentence',
     re.compile(r'\b(?:suitable|suited|recommended|formulated|designed|ideal|'
                r'perfect|great|made|convient)\s+(?:for|to|aux?)\s+'
                r'([a-z ,/&+-]{3,70}?)\s*(?:skin|peaux?)\b', re.I)),
    (2, 'reversed phrase',
     re.compile(r'\b([a-z ,/&+-]{3,50}?)\s*skin\s*types?\b', re.I)),
    (2, 'soothing wording',
     re.compile(r'\b(?:soothe?s?|soothing|calm(?:s|ing)?|gentle|non[- ]irritating|'
                r'fragrance[- ]free|hypoallergenic)\b[^.]{0,60}?'
                r'\b(irritated|reactive|delicate|sensitive)\b', re.I)),
]


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()


def bkey(s):
    return re.sub(r'[^a-z0-9]', '', re.sub(r'^the\s+', '', asc(s)))


def clean(t):
    return re.sub(r'\s+', ' ', htmllib.unescape(TAG.sub(' ', str(t)))).strip(' :.-•|')


def is_ing(p):
    q = p.strip(' .;:•|*-()[]')
    if not q or len(q) > 70 or JUNK_PIECE.search(q) or VERB.search(q):
        return False
    w = q.split()
    if len(w) > 7 or q.count('.') > 1:
        return False
    if KNOWN.search(q):
        return True
    last = re.sub(r'[^A-Za-z]', '', w[-1]) if w else ''
    if len(last) >= 3 and CHEM_END.search(last):
        return True
    return len(w) <= 5 and bool(re.fullmatch(r"[^\W\d_][\w \-/()'.&%+]*", q, re.UNICODE))


def find_inci(text):
    t = clean(text)
    t = re.sub(r'\b(full\s+)?(inci\s*(formula|list)?|active ingredients?|'
               r'inactive ingredients?|ingredients?|composition)\s*[:\-–]\s*',
               ', ', t, flags=re.I)
    pieces = re.split(r'[,;]|\.\s+|\.$|\s[-–—]\s|\s•\s', t)
    flags = [is_ing(p) for p in pieces]
    spans, start, gap, last = [], -1, 0, -1
    for i, ok in enumerate(flags + [False] * (GAP + 1)):
        if ok:
            if start < 0:
                start = i
            gap, last = 0, i
        elif start >= 0:
            gap += 1
            if gap > GAP:
                spans.append((start, last, sum(flags[start:last + 1])))
                start, gap = -1, 0
    if not spans:
        return ''
    a, b, good = max(spans, key=lambda s: s[2])
    if good < 5:
        return ''
    kept = ', '.join(p.strip(' .;:•|*-') for p in pieces[a:b + 1] if p.strip(' .;:•|*-'))
    chem = sum(1 for p in pieces[a:b + 1]
               if KNOWN.search(p) or (p.split() and
                                      len(re.sub(r'[^A-Za-z]', '', p.split()[-1])) >= 3 and
                                      CHEM_END.search(re.sub(r'[^A-Za-z]', '', p.split()[-1]))))
    if chem < 3 or INSTRUCTION.search(kept[:120]):
        return ''
    if sum(1 for p in pieces[a:b + 1] if BENEFIT.fullmatch(p.strip(' .;:•|*-'))) >= 3:
        return ''
    return kept[:4000]


def n_types(p):
    t = str(p).lower()
    return sum(bool(re.search(r'\b' + w, t))
               for w in ('dry', 'oil', 'combination', 'normal', 'sensitiv'))


def parse_types(t):
    t = str(t).lower()
    f = {v for k, v in TYPE_W.items() if re.search(r'\b' + k, t)}
    sn = 'Sensitive' if re.search(r'\b(sensitiv|irritated|reactive|delicate)', t) else ''
    if ('Dry' in f and 'Oily' in f) or 'Combination' in f:
        return 'Combination', sn
    for lab in ('Oily', 'Dry', 'Normal'):
        if lab in f:
            return lab, sn
    return '', sn


def find_claim(page):
    flat = re.sub(r'\s+', ' ', clean(
        re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', page)))
    for strength, rule, pat in CLAIM:
        for m in pat.finditer(flat):
            phrase = m.group(1)
            i = max(flat.rfind('.', 0, m.start()), 0)
            j = min([x for x in (flat.find('.', m.end()),) if x != -1] or [len(flat)])
            q = flat[i:j + 1].strip(' .')
            if len(q) < 12 or len(q) > 300 or JUNK_PIECE.search(q):
                continue
            if n_types(phrase) >= 4 or UNIV.search(phrase) or UNIV.search(q):
                return 'All', '', rule + ' (all skin types)', q[:220]
            st, sn = parse_types(phrase)
            if st or sn:
                return st, sn, rule, q[:220]
    return '', '', '', ''


# ===================================================================== part 1
df = pd.read_csv(DATA, dtype=str, low_memory=False).fillna('')
N = len(df)
print(f'{N:,} Lebanese origin products\n')

print('PART 1  complete the sensitivity axis.  free.')
before = int((df['sensitivity'] != '').sum())
mask = (df['skin_type'] != '') & (df['sensitivity'] == '')
df.loc[mask, 'sensitivity'] = 'Resistant'
after = int((df['sensitivity'] != '').sum())
print(f'   sensitivity {before:,} -> {after:,}   ({int(mask.sum()):,} set to Resistant)')
print('   same rule as the global dataset: a brand advertises a sensitive-skin')
print('   claim when it has one, so its absence after searching is the answer.\n')
df.to_csv(DATA, index=False)

if FREE_ONLY:
    for c in ('ingredients', 'skin_type', 'sensitivity'):
        n = int((df[c] != '').sum())
        print(f'   {c:14s}{n:6,}  ({100*n/N:5.1f}%)')
    raise SystemExit

# ===================================================================== part 2
S = requests.Session()
S.headers.update(HEAD)
_i, _lock = [0], threading.Lock()
_spent = [0]
_stop = threading.Event()


def serper(q):
    while True:
        with _lock:
            if _i[0] >= len(SERPER_KEYS):
                _stop.set()
                return [], 'no keys'
            k = SERPER_KEYS[_i[0]]
        try:
            r = requests.post('https://google.serper.dev/search',
                              headers={'X-API-KEY': k, 'Content-Type': 'application/json'},
                              data=json.dumps({'q': q, 'num': 10}), timeout=TIMEOUT)
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
            return [o.get('link', '') for o in r.json().get('organic', [])], 200
        except Exception:
            return [], 'bad json'


SITES = json.load(open(DOMAINS)) if os.path.exists(DOMAINS) else {}
for _, r_ in df.iterrows():
    if r_['domain']:
        SITES.setdefault(bkey(r_['brand']), r_['domain'])

already = set()
if os.path.exists(PROGRESS):
    try:
        p = pd.read_csv(PROGRESS, dtype=str).fillna('')
        byid = {v: k for k, v in df['product_id'].items()}
        for _, r in p.iterrows():
            already.add(r['product_id'])
            i = byid.get(r['product_id'])
            if i is None:
                continue
            for c in PFIELDS[1:]:
                if r.get(c, '') and not df.at[i, c]:
                    df.at[i, c] = r[c]
        df.to_csv(DATA, index=False)
        print(f'resuming: {len(already):,} already attempted\n')
    except Exception as e:
        print(f'(progress unreadable: {e})\n')

need = df[((df['ingredients'] == '') | (df['skin_type'] == '')) &
          (~df['product_id'].isin(already))]
if TEST:
    need = need.sample(min(TEST, len(need)), random_state=9)
    print(f'TEST MODE: {len(need)} products, nothing saved\n')
else:
    print(f'PART 2  {len(need):,} products still missing ingredients or a skin type')
    print(f'        {sum(1 for _, r in need.iterrows() if bkey(r["brand"]) in SITES):,} '
          f'have a known brand site\n')

found_i, found_s, pending, done = {}, {}, [], [0]
lk = threading.Lock()


def flush(force=False):
    global pending
    if not pending or (len(pending) < 40 and not force):
        return
    new = not os.path.exists(PROGRESS)
    with open(PROGRESS, 'a', newline='', encoding='utf-8') as fh:
        w = csv.DictWriter(fh, fieldnames=PFIELDS)
        if new:
            w.writeheader()
        w.writerows(pending)
    pending = []


def short(name, brand, n=4):
    s = asc(name)
    for w in re.split(r'[^a-z0-9]+', asc(brand)):
        if len(w) > 2:
            s = s.replace(w, ' ')
    s = SIZE.sub(' ', s)
    return ' '.join([w for w in re.sub(r'[^a-z0-9 ]', ' ', s).split()
                     if w not in STOP][:n])


def work(i):
    if _stop.is_set():
        return
    brand, name = df.at[i, 'brand'], df.at[i, 'name']
    site = SITES.get(bkey(brand), '')
    sn_ = short(name, brand)
    need_i = not df.at[i, 'ingredients']
    need_s = not df.at[i, 'skin_type']
    queries = []
    if site and sn_:
        queries.append(f'site:{site} {sn_}')
    queries.append(f'"{brand} {sn_}" ingredients')
    if need_s:
        queries.append(f'{brand} {sn_} skin type')

    seen = set()
    for q in queries:
        if not (need_i or need_s):
            break
        links, code = serper(q)
        if code != 200:
            continue
        for url in links[:PAGES]:
            host = url.split('/')[2].lower().replace('www.', '') if '://' in url else ''
            if not host or host in seen or REJECT.search(host):
                continue
            seen.add(host + url[-20:])
            try:
                r = S.get(url, timeout=TIMEOUT)
                if r.status_code != 200:
                    continue
                page = r.text[:300000]
                body = re.sub(r'[^a-z0-9]', '', page.lower())
                if bkey(brand) and bkey(brand)[:6] not in body:
                    continue
            except Exception:
                continue
            if need_i:
                ing = find_inci(page)
                if ing:
                    with lk:
                        found_i[i] = (ing, host, url)
                    need_i = False
            if need_s:
                st, sens, rule, quote = find_claim(page)
                if st or sens:
                    on_site = bool(site and host.endswith(site))
                    with lk:
                        found_s[i] = (st or 'All', sens or 'Resistant', rule, quote,
                                      host, url, '1' if on_site else '2')
                    need_s = False
            if not (need_i or need_s):
                break

    with lk:
        done[0] += 1
        rec = {'product_id': df.at[i, 'product_id']}
        if i in found_i:
            ing, host, url = found_i[i]
            rec.update(ingredients=ing, ingredient_source=host, ingredient_url=url)
        if i in found_s:
            st, sens, rule, quote, host, url, tier = found_s[i]
            rec.update(skin_type=st, sensitivity=sens, skin_type_rule=rule,
                       skin_type_quote=quote, skin_type_source=host,
                       skin_type_url=url, skin_type_tier=tier)
        if len(rec) > 1 and not TEST:
            pending.append({k: rec.get(k, '') for k in PFIELDS})
            flush()
        if done[0] % 25 == 0:
            print(f'   {done[0]:,}/{len(need):,}   ingredients {len(found_i):,}'
                  f'   skin type {len(found_s):,}   credits {_spent[0]:,}', flush=True)


with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    list(ex.map(work, need.index))
if not TEST:
    flush(force=True)

print(f'\n   attempted {len(need):,}   credits {_spent[0]:,}')
print(f'   ingredients found  {len(found_i):,}')
print(f'   skin types found   {len(found_s):,}')

if TEST:
    r_i = len(found_i) / max(len(need), 1)
    r_s = len(found_s) / max(len(need), 1)
    n_i = int((df['ingredients'] == '').sum())
    n_s = int((df['skin_type'] == '').sum())
    print('\n' + '=' * 60)
    print('  TEST ONLY, nothing written.')
    print(f'  a full run would add about {int(n_i*r_i):,} ingredient lists '
          f'and {int(n_s*r_s):,} skin types')
    print(f'  and cost roughly {int(_spent[0]*(len(df[(df["ingredients"]=="")|(df["skin_type"]=="")])/max(len(need),1))):,} credits')
    raise SystemExit

for i, (ing, host, url) in found_i.items():
    df.at[i, 'ingredients'] = ing
    df.at[i, 'ingredients_raw'] = ing
    df.at[i, 'ingredient_source'] = host
    df.at[i, 'ingredient_url'] = url
    df.at[i, 'ingredient_count'] = str(len([x for x in ing.split(',') if x.strip()]))
for i, (st, sens, rule, quote, host, url, tier) in found_s.items():
    df.at[i, 'skin_type'] = st
    df.at[i, 'sensitivity'] = sens
    df.at[i, 'skin_type_rule'] = rule
    df.at[i, 'skin_type_quote'] = quote
    df.at[i, 'skin_type_source'] = host
    df.at[i, 'skin_type_url'] = url
    df.at[i, 'skin_type_tier'] = tier
    df.at[i, 'skin_type_authority'] = 'manufacturer' if tier == '1' else 'retailer'
    df.at[i, 'skin_type_status'] = 'found'
df.loc[(df['skin_type'] != '') & (df['sensitivity'] == ''), 'sensitivity'] = 'Resistant'
df.loc[df['skin_type'] == '', 'skin_type_status'] = 'searched, not stated'

df.to_csv(DATA, index=False)
try:
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    EXTRA = {'brand_country', 'market', 'price_usd', 'product_url', 'domain',
             'harvest_method', 'origin_evidence'}
    with pd.ExcelWriter('LEBANESE_ORIGIN.xlsx', engine='openpyxl') as w:
        df.to_excel(w, sheet_name='Lebanese origin', index=False)
        ws = w.sheets['Lebanese origin']
        for c in ws[1]:
            v = str(c.value)
            c.fill = PatternFill('solid', fgColor='6f9c78' if v in EXTRA else '584A7A')
            c.font = Font(bold=True, color='FFFFFF', size=10)
            c.alignment = Alignment(vertical='center', horizontal='left')
            ws.column_dimensions[get_column_letter(c.column)].width = 18
        ws.freeze_panes = 'D2'
        ws.auto_filter.ref = ws.dimensions
except PermissionError:
    print('(workbook open in Excel, csv written)')

print('\n' + '=' * 60)
print('  LEBANESE ORIGIN, FINAL')
print('=' * 60)
for c in ('brand', 'name', 'product_type', 'ingredients', 'skin_type',
          'sensitivity', 'price_usd', 'product_url'):
    n = int((df[c] != '').sum())
    print(f'   {c:16s}{n:6,}  ({100*n/N:5.1f}%)')
print(f'\n   {N:,} products, {df["brand"].nunique()} brands, credits {_spent[0]:,}')
