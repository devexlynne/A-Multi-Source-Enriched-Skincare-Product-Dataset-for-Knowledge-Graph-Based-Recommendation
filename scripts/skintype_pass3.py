"""
PASS 3:  products.json FIRST, THEN robots.txt, THEN THE WHOLE SITEMAP TREE

WHAT THE DIAGNOSTIC SHOWED, and why pass 2 only reached 10%

  I ran _test_sitemap.py against five brands that were failing. Three separate
  bugs, all mine:

Usage:
    py -m pip install requests rapidfuzz
    py skintype_pass3.py
"""
import os
import re
import csv
import json
import gzip
import threading
import requests
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor, as_completed
from rapidfuzz import fuzz

DATASET = 'SKINCARE_DATASET.csv'
PRIOR = ['skintype_search_results.csv', 'skintype_pass2_results.csv']
OUT = 'skintype_pass3_results.csv'
CACHE = 'brand_sources_cache.json'
WORKERS = 10
TIMEOUT = 15
TITLE_ACCEPT, URL_ACCEPT = 82, 78

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'}

FIELDS = ['product_id', 'brand', 'name', 'skin_type', 'sensitivity', 'universal_claim',
          'skin_type_source', 'skin_type_authority', 'skin_type_strength',
          'skin_type_rule', 'skin_type_quote', 'skin_type_url', 'matched_title',
          'match_score', 'route', 'status', 'failure_reason']

# --------------------------------------------------------------- the rule
TYPE_WORDS = {'dry': 'Dry', 'oily': 'Oily', 'oil': 'Oily', 'combination': 'Combination',
              'combo': 'Combination', 'normal': 'Normal', 'acne': 'Oily'}
UNIVERSAL = re.compile(r'\b(all skin types?|every skin type|any skin type|universal)\b', re.I)
FIELD_PAT = [
    re.compile(r'skin[\s_-]*type[^a-z0-9]{0,4}\s*[:\-]\s*([A-Za-z ,/&+-]{3,60})', re.I),
    re.compile(r'<t[hd][^>]*>\s*skin\s*type\s*</t[hd]>\s*<t[hd][^>]*>\s*([^<]{3,60})', re.I | re.S),
]
SUIT_PAT = re.compile(r'\b(?:suitable|suited|recommended|formulated|designed|ideal|perfect'
                      r'|great|made)\s+(?:for|to)\s+([a-z ,/&+-]{3,70}?)\s*skin\b', re.I)
BENEFIT_PAT = re.compile(r'\b(?:good|great|works?|helps?|benefits?|targets?|treats?|effective'
                         r'|beneficial)\s+(?:for|on|with)?\s*([a-z ,/&+-]{3,70}?)\s*skin\b', re.I)


def n_types(p):
    t = p.lower()
    return sum(bool(re.search(r'\b' + w, t))
               for w in ('dry', 'oil', 'combination', 'normal', 'sensitiv'))


def parse_types(text):
    t = text.lower()
    f = {lab for w, lab in TYPE_WORDS.items() if re.search(r'\b' + re.escape(w), t)}
    sens = 'Sensitive' if re.search(r'\bsensitiv', t) else ''
    if 'Dry' in f and 'Oily' in f:
        return 'Combination', sens
    if 'Combination' in f:
        return 'Combination', sens
    for lab in ('Oily', 'Dry', 'Normal'):
        if lab in f:
            return lab, sens
    return '', sens


def sent_around(flat, a, b):
    i = max(flat.rfind('.', 0, a), flat.rfind('|', 0, a), flat.rfind('•', 0, a), 0)
    j = min([x for x in (flat.find('.', b), flat.find('|', b)) if x != -1] or [len(flat)])
    return flat[i:j + 1].strip(' .|•').strip()


def build(phrase, quote, strength, rule):
    if (n_types(phrase) >= 4 or n_types(quote) >= 4
            or UNIVERSAL.search(phrase) or UNIVERSAL.search(quote)):
        return dict(skin_type='', sensitivity='', universal_claim='1',
                    skin_type_strength=str(strength),
                    skin_type_rule=rule + ' (all types)', skin_type_quote=quote[:220])
    st, sn = parse_types(phrase)
    if not (st or sn):
        return None
    return dict(skin_type=st, sensitivity=sn, universal_claim='',
                skin_type_strength=str(strength), skin_type_rule=rule,
                skin_type_quote=quote[:220])


def extract(html):
    flat = re.sub(r'\s+', ' ', re.sub(r'<script[\s\S]*?</script>|<style[\s\S]*?</style>', ' ', html))
    for pat in FIELD_PAT:
        m = pat.search(flat)
        if m:
            v = m.group(1).strip(' .,:;-')
            if len(v) <= 60:
                r = build(v, flat[max(0, m.start() - 20):m.end() + 20].strip(), 1, 'declared field')
                if r:
                    return r
    for pat, st, rule in ((SUIT_PAT, 2, 'suitability sentence'),
                          (BENEFIT_PAT, 3, 'ingredient benefit')):
        for m in pat.finditer(flat):
            s = sent_around(flat, m.start(), m.end())
            if len(s) > 400:
                s = flat[max(0, m.start() - 120):m.end() + 160]
            r = build(s, s, st, rule)
            if r:
                return r
    return None


# ------------------------------------------------------------------ plumbing
S = requests.Session()
S.headers.update(HEAD)
_lock = threading.Lock()
_src = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}
BAD = re.compile(r'/(blog|article|news|press|about|contact|careers|faq|help|policy|terms|'
                 r'privacy|account|cart|login|store-locator|sitemap|search)', re.I)


def bkey(b):
    return re.sub(r'[^a-z0-9]', '', str(b).lower())


def get(u, **kw):
    try:
        return S.get(u, timeout=TIMEOUT, **kw)
    except Exception:
        return None


def find_domain(brand):
    b = re.sub(r"[''`.]", '', str(brand).strip().lower()).replace('&', 'and')
    plain, hyph = re.sub(r'[^a-z0-9]', '', b), re.sub(r'[^a-z0-9]+', '-', b).strip('-')
    cands = []
    for stem in dict.fromkeys([plain, hyph]):
        if stem and len(stem) > 2:
            cands += ['www.' + stem + '.com', stem + '.com', stem + '.co.uk',
                      stem + '.co.kr', stem + '.fr']
    k = bkey(brand)
    for c in cands[:10]:
        r = get('https://' + c)
        if not r or r.status_code >= 400:
            continue
        body = re.sub(r'[^a-z0-9]', '', re.sub(r'<[^>]+>', ' ', r.text[:80000]).lower())
        if k and len(k) > 3 and k in body:
            return r.url.split('/')[2]
    return ''


def read_sitemap(url, seen, depth=0):
    """follow the WHOLE tree. child sitemaps may live on another domain."""
    if url in seen or depth > 3 or len(seen) > 120:
        return []
    seen.add(url)
    r = get(url)
    if not r or r.status_code != 200:
        return []
    txt = r.text
    if url.endswith('.gz') or r.content[:2] == b'\x1f\x8b':
        try:
            txt = gzip.GzipFile(fileobj=BytesIO(r.content)).read().decode('utf-8', 'ignore')
        except Exception:
            return []
    locs = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', txt)
    pages = [u for u in locs if not re.search(r'\.xml(\.gz)?$', u)]
    kids = [u for u in locs if re.search(r'\.xml(\.gz)?$', u)]
    # product-named children first, image/video ones last
    kids.sort(key=lambda u: (0 if re.search(r'product|item|shop|catalog', u, re.I) else
                             2 if re.search(r'image|video|blog|news', u, re.I) else 1))
    for k in kids[:20]:
        pages += read_sitemap(k, seen, depth + 1)
    return pages


def shopify_products(dom):
    """every product with its TITLE. best possible case."""
    out = []
    for page in range(1, 8):
        r = get(f'https://{dom}/products.json?limit=250&page={page}')
        if not r or r.status_code != 200 or 'json' not in r.headers.get('Content-Type', ''):
            break
        try:
            ps = r.json().get('products', [])
        except Exception:
            break
        if not ps:
            break
        for p in ps:
            out.append([p.get('title', ''), f'https://{dom}/products/{p.get("handle","")}'])
        if len(ps) < 250:
            break
    return out


def sources_for(brand):
    """
    {'domain':..,'route':'shopify'|'sitemap'|'','items':[[title,url],..] or [[ '',url],..]}
    cached to disk, computed once per brand
    """
    k = bkey(brand)
    with _lock:
        if k in _src:
            return _src[k]
    rec = {'domain': '', 'route': '', 'items': []}
    dom = find_domain(brand)
    rec['domain'] = dom
    if dom:
        sp = shopify_products(dom)
        if sp:
            rec['route'], rec['items'] = 'shopify', sp
        else:
            seen = set()
            pages = []
            r = get(f'https://{dom}/robots.txt')            # robots FIRST
            if r and r.status_code == 200:
                for sm in re.findall(r'(?i)sitemap:\s*(\S+)', r.text)[:6]:
                    pages += read_sitemap(sm, seen)
            if not pages:                                    # fallback guesses
                for p in ('/sitemap.xml', '/sitemap_index.xml', '/sitemap_products_1.xml'):
                    pages += read_sitemap(f'https://{dom}{p}', seen)
            keep, s2 = [], set()
            for u in pages:
                if BAD.search(u) or u in s2:
                    continue
                s2.add(u)
                keep.append(['', u])
            if keep:
                rec['route'], rec['items'] = 'sitemap', keep[:12000]
    with _lock:
        _src[k] = rec
        if len(_src) % 20 == 0:
            json.dump(_src, open(CACHE, 'w', encoding='utf-8'))
    return rec


def slug(u):
    """
    The product name is not always the last path segment.

        cetaphil.com/us/moisturizers/daily-hydrating-lotion/302993934226.html
                                     ^^^^^^^^^^^^^^^^^^^^^^ the name
                                                            ^^^^^^^^^^^^ a SKU

    Reading only the last segment scored 0 against every Cetaphil product.
    So drop segments that are just digits or a SKU, and keep the last few
    word-bearing ones.
    """
    parts = [p for p in u.rstrip('/').split('/')[3:] if p]
    parts = [re.sub(r'\.(html?|php|aspx)$', '', p) for p in parts]
    words = [p for p in parts if re.search(r'[a-z]{3}', p, re.I)
             and not re.fullmatch(r'[a-z]{0,3}[-_]?\d[\d-]*', p, re.I)]
    tail = ' '.join(words[-3:]) if words else ' '.join(parts[-2:])
    return re.sub(r'[^a-z0-9]+', ' ', tail.lower()).strip()


def clean(n):
    return re.sub(r'\s+', ' ', re.sub(r'[^a-z0-9 ]', ' ', str(n).lower())).strip()


def do(row):
    pid, brand, name = row['product_id'], row['brand'], row['name']
    rec = {k: '' for k in FIELDS}
    rec.update(product_id=pid, brand=brand, name=name, status='not found')

    src = sources_for(brand)
    rec['skin_type_source'] = src['domain']
    rec['route'] = src['route']
    if not src['domain']:
        rec['failure_reason'] = 'no domain'
        return rec
    if not src['items']:
        rec['failure_reason'] = 'no products found on site'
        return rec

    q = clean(name)
    best, score, title = '', 0, ''
    if src['route'] == 'shopify':
        for t, u in src['items']:
            s = fuzz.token_set_ratio(q, clean(t))
            if s > score:
                best, score, title = u, s, t
        thr = TITLE_ACCEPT
    else:
        for _, u in src['items']:
            s = fuzz.token_set_ratio(q, slug(u))
            if s > score:
                best, score = u, s
        thr = URL_ACCEPT

    rec['match_score'] = f'{score:.0f}'
    rec['matched_title'] = title[:120]
    if score < thr:
        rec['failure_reason'] = 'name not matched'
        return rec

    r = get(best)
    if not r or r.status_code != 200:
        rec['failure_reason'] = 'page not fetched'
        return rec
    hit = extract(r.text)
    if not hit:
        rec['failure_reason'] = 'no skin type on page'
        rec['skin_type_url'] = best
        return rec
    rec.update(hit)
    rec.update(skin_type_authority='manufacturer', skin_type_url=best, status='found')
    return rec


# ---------------------------------------------------------------------- main
def main():
    rows = list(csv.DictReader(open(DATASET, encoding='utf-8')))
    answered = set()
    for f in PRIOR:
        if os.path.exists(f):
            for r in csv.DictReader(open(f, encoding='utf-8')):
                if r.get('skin_type') or r.get('universal_claim') == '1':
                    answered.add(r['product_id'])
    print(f'already answered by earlier passes: {len(answered):,}')
    if os.path.exists(OUT):
        for r in csv.DictReader(open(OUT, encoding='utf-8')):
            answered.add(r['product_id'])
        print('resuming pass 3')
    todo = [r for r in rows if r['product_id'] not in answered]
    todo.sort(key=lambda r: r['brand'])
    print(f'{len(todo):,} to try, {WORKERS} workers, {len(_src):,} brands already cached\n')

    new = not os.path.exists(OUT)
    f = open(OUT, 'a', newline='', encoding='utf-8')
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new:
        w.writeheader()

    found = 0
    reasons, routes = {}, {}
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(do, r): r for r in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                rec = fut.result()
            except Exception as e:
                r = futs[fut]
                rec = {k: '' for k in FIELDS}
                rec.update(product_id=r['product_id'], brand=r['brand'], name=r['name'],
                           status='error', failure_reason=str(e)[:60])
            w.writerow(rec)
            f.flush()
            routes[rec['route'] or 'none'] = routes.get(rec['route'] or 'none', 0) + 1
            if rec['status'] == 'found':
                found += 1
            else:
                reasons[rec['failure_reason']] = reasons.get(rec['failure_reason'], 0) + 1
            if i % 25 == 0 or i == len(todo):
                top = sorted(reasons.items(), key=lambda x: -x[1])[:2]
                print(f'  {i:6,}/{len(todo):,}  found {found:,} ({100*found/i:.0f}%)  '
                      f'shopify {routes.get("shopify",0):,}  sitemap {routes.get("sitemap",0):,}  '
                      f'| {"; ".join(f"{k} {v}" for k, v in top)}')
    f.close()
    json.dump(_src, open(CACHE, 'w', encoding='utf-8'))

    print('\n' + '=' * 66)
    print(f'  attempted   {len(todo):,}')
    print(f'  found       {found:,}  ({100*found/max(len(todo),1):.1f}%)')
    print('\n  route used')
    for k, v in sorted(routes.items(), key=lambda x: -x[1]):
        print(f'     {k:22s}{v:6,}')
    print('\n  why the rest failed')
    for k, v in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f'     {k or "(blank)":26s}{v:6,}')
    print(f'\nwrote {OUT}\ncache saved to {CACHE}, a re-run costs nothing')
    print('next:  py skintype_apply.py')


if __name__ == '__main__':
    main()
