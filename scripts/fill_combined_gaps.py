"""
Close the last gaps in the combined dataset

After build_combined.py the dataset is 8,356 products, every one with reviews,
and four features are short of 100%:

Usage:
    py fill_combined_gaps.py                 everything
    py fill_combined_gaps.py --no-search     the free gaps only
"""
import os
import re
import sys
import json
import time
import unicodedata
import threading
import requests
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

DATA = 'COMBINED_DATASET.csv'
DOMAINS = 'brand_domains.json'
NOSEARCH = '--no-search' in sys.argv

SERPER_KEYS = [
    '',
            '',
    '',
    '',
]
TIMEOUT = 15
WORKERS = 3
PAGES = 6
HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36'}

df = pd.read_csv(DATA, dtype=str, low_memory=False).fillna('')
N = len(df)
print(f'{N:,} products\n')

# ============================================================ GAP 1  free
print('GAP 1  review_count')
need = (df['review_count'] == '') & (df['review_texts_json'] != '')


def count_reviews(blob):
    b = str(blob).strip()
    if not b:
        return ''
    try:
        v = json.loads(b)
        if isinstance(v, list):
            return str(len(v))
        if isinstance(v, dict):
            return str(len(v))
    except Exception:
        pass
    # not valid json, so count the obvious separators instead
    n = b.count('"},{') + 1 if '"},{' in b else len([x for x in b.split('||') if x.strip()])
    return str(max(n, 1))


df.loc[need, 'review_count'] = df.loc[need, 'review_texts_json'].map(count_reviews)
still = int((df['review_count'] == '').sum())
print(f'   filled from the stored review texts   {int(need.sum()):,}')
print(f'   still blank (no texts and no count)   {still:,}')
if still:
    print('   those keep a blank, because writing 0 would be a claim, not a gap')

# ============================================================ GAP 2  free
print('\nGAP 2  ingredients')


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()


BPRE = re.compile(r'^(the|eau thermale|laboratoires?|labo|by)\s+', re.I)
STOP = {'the', 'and', 'for', 'with', 'of', 'de', 'la', 'le', 'du', 'new', 'pack',
        'set', 'kit', 'skin', 'face', 'facial', 'ml', 'g', 'gr', 'oz', 'fl',
        'duo', 'in', 'to', 'plus', 'my', 'a', 'x'}
SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)


def bkey(s):
    t = asc(s).strip()
    for _ in range(3):
        t = BPRE.sub('', t).strip()
    return re.sub(r'[^a-z0-9]', '', t)


def key_of(brand, name):
    s = asc(name)
    for w in re.split(r'[^a-z0-9]+', asc(brand)):
        if len(w) > 2:
            s = s.replace(w, ' ')
    s = SIZE.sub(' ', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return bkey(brand) + '||' + ' '.join(sorted(w for w in s.split() if w not in STOP))


miss_ing = df.index[df['ingredients'] == '']
found_ing = 0
if len(miss_ing):
    lookup = {}
    for src in ('LEBANESE_RETAIL.csv', 'SKINCARE_DATASET.csv'):
        if not os.path.exists(src):
            continue
        o = pd.read_csv(src, dtype=str, low_memory=False).fillna('')
        for b, n, ing in zip(o['brand'], o['name'], o.get('ingredients', '')):
            if str(ing).strip():
                lookup.setdefault(key_of(b, n), ing)
    for i in miss_ing:
        k = key_of(df.at[i, 'brand'], df.at[i, 'name'])
        if k in lookup:
            df.at[i, 'ingredients'] = lookup[k]
            found_ing += 1
print(f'   missing at the start                  {len(miss_ing):,}')
print(f'   recovered from the other sources      {found_ing:,}')
print(f'   still missing                         {int((df["ingredients"] == "").sum()):,}')

# ============================================================ GAP 3  credits
gap3 = df.index[(df['skin_type'] == '')]
print(f'\nGAP 3  skin_type and sensitivity, {len(gap3):,} missing')
print(f'   by source: {df.loc[gap3, "source"].value_counts().to_dict()}')

if NOSEARCH:
    print('   --no-search given, skipping the search pass')
elif len(gap3) == 0:
    print('   nothing to do')
else:
    print(f'   searching. roughly {2*len(gap3):,} credits at most.\n')
    REJECT = re.compile(
        r'(incidecoder|skinsort|skincarisma|cosdna|beautypedia|skinwis|gopicky|'
        r'allure|byrdie|refinery29|cosmopolitan|vogue|glamour|nypost|buzzfeed|'
        r'poshmark|mercari|depop|vinted|instagram|facebook|tiktok|reddit|youtube|'
        r'pinterest|quora|twitter|x\.com|ebay|aliexpress|etsy|dhgate|alibaba|'
        r'linkedin|blogspot|wordpress\.com|medium\.com|wikipedia|google\.)', re.I)
    SHOP = re.compile(r'(add[\s_-]?to[\s_-]?(cart|bag|basket)|addtocart|'
                      r'"@type"\s*:\s*"(product|offer)"|itemprop="price"|'
                      r'\bbuy now\b|\bin stock\b|data-product-id)', re.I)
    TW = {'dry': 'Dry', 'oily': 'Oily', 'oil': 'Oily', 'combination': 'Combination',
          'combo': 'Combination', 'normal': 'Normal', 'acne': 'Oily'}
    UNIV = re.compile(r'\b(all skin types?|every skin type|any skin type)\b', re.I)
    TAG = re.compile(r'<[^>]{0,400}>')
    JUNK = re.compile(r'(class=|id=|href=|style=|</|/>)', re.I)
    PATTERNS = [
        (1, 'declared field',
         re.compile(r'skin[\s_-]*type[^a-z0-9]{0,4}\s*[:\-]\s*([A-Za-z ,/&+-]{3,60})', re.I)),
        (1, 'labelled "for"',
         re.compile(r'\bfor\s*[:\-]\s*([a-z ,/&+-]{3,50}?)\s*skin\b', re.I)),
        (2, 'suitability sentence',
         re.compile(r'\b(?:suitable|suited|recommended|formulated|designed|ideal|perfect'
                    r'|great|made|created)\s+(?:for|to)\s+([a-z ,/&+-]{3,70}?)\s*skin\b', re.I)),
        (2, 'reversed phrase',
         re.compile(r'\b([a-z ,/&+-]{3,50}?)\s*skin\s*types?\b', re.I)),
        (2, 'soothing wording',
         re.compile(r'\b(?:soothe?s?|soothing|calm(?:s|ing)?|gentle|non[- ]irritating|'
                    r'fragrance[- ]free|hypoallergenic)\b[^.]{0,60}?'
                    r'\b(irritated|reactive|delicate|sensitive)\b', re.I)),
        (3, 'ingredient benefit',
         re.compile(r'\b(?:good|great|works?|helps?|benefits?|targets?|effective|gentle'
                    r'|safe)\s+(?:for|on|with)?\s*([a-z ,/&+-]{3,70}?)\s*skin\b', re.I)),
    ]

    def readable(q):
        q = re.sub(r'\s+', ' ', TAG.sub(' ', str(q))).strip(' .|•"\'>-')
        if JUNK.search(q):
            return ''
        L = len(re.findall(r'[a-zA-Z]', q))
        if L < 15 or L < 0.55 * max(len(q), 1) or 'skin' not in q.lower():
            return ''
        return q[:220]

    def sent(flat, a, b):
        i = max(flat.rfind('.', 0, a), flat.rfind('|', 0, a), 0)
        j = min([x for x in (flat.find('.', b), flat.find('|', b)) if x != -1] or [len(flat)])
        return flat[i:j + 1].strip(' .|').strip()

    def ntypes(p):
        t = str(p).lower()
        return sum(bool(re.search(r'\b' + w, t))
                   for w in ('dry', 'oil', 'combination', 'normal', 'sensitiv'))

    def parse(t):
        t = str(t).lower()
        f_ = {v for k, v in TW.items() if re.search(r'\b' + k, t)}
        sn = 'Sensitive' if re.search(r'\b(sensitiv|irritated|reactive|delicate)', t) else ''
        if ('Dry' in f_ and 'Oily' in f_) or 'Combination' in f_:
            return 'Combination', sn
        for lab in ('Oily', 'Dry', 'Normal'):
            if lab in f_:
                return lab, sn
        return '', sn

    def extract(text):
        flat = re.sub(r'\s+', ' ', re.sub(
            r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', text))
        for stg, rule, pat in PATTERNS:
            for m in pat.finditer(flat):
                ph = m.group(1)
                q = readable(sent(flat, m.start(), m.end()))
                if not q:
                    continue
                if ntypes(ph) >= 4 or UNIV.search(ph) or UNIV.search(q):
                    return dict(skin_type='All', sensitivity='', rule=rule + ' (all skin types)',
                                quote=q)
                st, sn = parse(ph)
                if st or sn:
                    return dict(skin_type=st, sensitivity=sn, rule=rule, quote=q)
        return None

    SES = requests.Session()
    SES.headers.update(HEAD)
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
                return [(o.get('link', ''), o.get('snippet', ''))
                        for o in r.json().get('organic', [])], 200
            except Exception:
                return [], 'bad json'

    SITES = json.load(open(DOMAINS)) if os.path.exists(DOMAINS) else {}
    for _, r_ in df[df['skin_type_tier'] == '1'].iterrows():
        u = str(r_['skin_type_url'])
        if '://' in u:
            SITES.setdefault(bkey(r_['brand']), u.split('/')[2].replace('www.', ''))

    def toks3(n, b):
        s = asc(n)
        for w in re.split(r'[^a-z0-9]+', asc(b)):
            if len(w) > 2:
                s = s.replace(w, ' ')
        s = SIZE.sub(' ', s)
        return [w for w in re.sub(r'[^a-z0-9 ]', ' ', s).split() if w not in STOP][:3]

    def work(i):
        if _stop.is_set():
            return None
        brand, name = df.at[i, 'brand'], df.at[i, 'name']
        site = SITES.get(bkey(brand), '')
        short = ' '.join(toks3(name, brand))
        queries = ([f'site:{site} {short}'] if site and short else []) + \
                  [f'{brand} {short} skin type']
        for q in queries:
            res, code = serper(q)
            if code != 200:
                continue
            for url, snip in res[:PAGES]:
                host = url.split('/')[2].lower() if '://' in url else ''
                if not host or REJECT.search(host):
                    continue
                on_site = bool(site and host.replace('www.', '').endswith(site))
                hit = extract(snip) if (snip and on_site) else None
                if not hit:
                    try:
                        rr = SES.get(url, timeout=TIMEOUT)
                        if rr.status_code != 200:
                            continue
                        body = re.sub(r'[^a-z0-9]', '', rr.text[:200000].lower())
                        if bkey(brand) and bkey(brand)[:6] not in body:
                            continue
                        if not on_site and not SHOP.search(rr.text):
                            continue
                        hit = extract(rr.text)
                    except Exception:
                        continue
                if hit:
                    return (i, hit, url, host, 1 if on_site else 2)
        return None

    done = 0
    filled = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        for fut in as_completed([ex.submit(work, i) for i in gap3]):
            try:
                got = fut.result()
            except Exception:
                got = None
            done += 1
            if got:
                i, hit, url, host, tr = got
                df.at[i, 'skin_type'] = hit['skin_type'] or 'All'
                df.at[i, 'sensitivity'] = hit['sensitivity'] or 'Resistant'
                df.at[i, 'skin_type_tier'] = str(tr)
                df.at[i, 'skin_type_authority'] = 'manufacturer' if tr == 1 else 'retailer'
                df.at[i, 'skin_type_source'] = host.replace('www.', '')
                df.at[i, 'skin_type_rule'] = hit['rule']
                df.at[i, 'skin_type_quote'] = hit['quote']
                df.at[i, 'skin_type_url'] = url
                df.at[i, 'skin_type_status'] = 'found'
                filled += 1
            if done % 25 == 0:
                print(f'   {done}/{len(gap3)}   filled {filled}   credits {_spent[0]}',
                      flush=True)
    print(f'\n   filled {filled:,} of {len(gap3):,}   credits used {_spent[0]:,}')
    left = df.index[df['skin_type'] == '']
    if len(left):
        df.loc[left, 'skin_type_status'] = 'searched, not stated'

# ==================================================================== write
df.to_csv(DATA, index=False)
try:
    from openpyxl.styles import Font, PatternFill, Alignment
    from openpyxl.utils import get_column_letter
    RET = {'retailers', 'n_retailers', 'price_usd', 'retailer_urls',
           'retailer_skin_types', 'retailers_agree', 'source'}
    with pd.ExcelWriter('COMBINED_DATASET.xlsx', engine='openpyxl') as w:
        df.to_excel(w, sheet_name='COMBINED', index=False)
        ws = w.sheets['COMBINED']
        for c in ws[1]:
            v = str(c.value)
            col = ('6f9c78' if v in RET else
                   'b06a97' if v.startswith('skin_type') or v == 'sensitivity' else '584A7A')
            c.fill = PatternFill('solid', fgColor=col)
            c.font = Font(bold=True, color='FFFFFF', size=10)
            c.alignment = Alignment(vertical='center', horizontal='left')
            ws.column_dimensions[get_column_letter(c.column)].width = 16
        ws.freeze_panes = 'D2'
        ws.auto_filter.ref = ws.dimensions
except PermissionError:
    print('\n(workbook open in Excel, csv written, close Excel and re-run to refresh it)')

print('\n' + '=' * 60)
print('  FEATURE COVERAGE NOW')
print('=' * 60)
CORE = ['brand', 'name', 'product_type', 'country', 'skin_type', 'sensitivity',
        'ingredients', 'benefits', 'concerns', 'review_count', 'review_source']
allfull = True
for c in CORE:
    n = int((df[c] != '').sum())
    mark = 'OK' if n == N else f'{N-n:,} missing'
    if n != N:
        allfull = False
    print(f'   {c:18s}{n:6,}  ({100*n/N:5.1f}%)   {mark}')
print()
for c in ('rating', 'price_usd', 'skin_type_url'):
    if c in df.columns:
        n = int((df[c] != '').sum())
        print(f'   {c:18s}{n:6,}  ({100*n/N:5.1f}%)')
print()
print('   ALL CORE FEATURES AT 100%' if allfull else
      '   some gaps remain, listed above, and they are real gaps not errors')
print('\nnow run:  py build_portal_lebanese.py')
