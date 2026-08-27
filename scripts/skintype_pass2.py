"""
Pass 2: sitemap instead of search box

WHY PASS 1 ONLY REACHED 11%

Usage:
    py -m pip install requests rapidfuzz
    py skintype_pass2.py
"""
import os
import re
import csv
import gzip
import time
import threading
import requests
from io import BytesIO
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from rapidfuzz import fuzz

DATASET = 'SKINCARE_DATASET.csv'
PASS1 = 'skintype_search_results.csv'
OUT = 'skintype_pass2_results.csv'
WORKERS = 12
TIMEOUT = 15
URL_ACCEPT = 78

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'}

FIELDS = ['product_id', 'brand', 'name', 'skin_type', 'sensitivity', 'universal_claim',
          'skin_type_source', 'skin_type_authority', 'skin_type_strength',
          'skin_type_rule', 'skin_type_quote', 'skin_type_url',
          'url_score', 'status', 'failure_reason']

# ---------------------------------------------------------- the rule (same)
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


def n_types_named(p):
    t = p.lower()
    return sum(bool(re.search(r'\b' + w, t))
               for w in ('dry', 'oil', 'combination', 'normal', 'sensitiv'))


def parse_types(text):
    t = text.lower()
    found = {lab for w, lab in TYPE_WORDS.items() if re.search(r'\b' + re.escape(w), t)}
    sens = 'Sensitive' if re.search(r'\bsensitiv', t) else ''
    if 'Dry' in found and 'Oily' in found:
        return 'Combination', sens
    if 'Combination' in found:
        return 'Combination', sens
    for lab in ('Oily', 'Dry', 'Normal'):
        if lab in found:
            return lab, sens
    return '', sens


def sentence_around(flat, a, b):
    i = max(flat.rfind('.', 0, a), flat.rfind('|', 0, a), flat.rfind('•', 0, a), 0)
    j = min([x for x in (flat.find('.', b), flat.find('|', b)) if x != -1] or [len(flat)])
    return flat[i:j + 1].strip(' .|•').strip()


def build(phrase, quote, strength, rule):
    if (n_types_named(phrase) >= 4 or n_types_named(quote) >= 4
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
            s = sentence_around(flat, m.start(), m.end())
            if len(s) > 400:
                s = flat[max(0, m.start() - 120):m.end() + 160]
            r = build(s, s, st, rule)
            if r:
                return r
    return None


# ------------------------------------------------ brand domain + sitemap cache
S = requests.Session()
S.headers.update(HEAD)
_cache, _lock = {}, threading.Lock()
BAD_URL = re.compile(r'/(blog|article|news|press|about|contact|careers|faq|help|policy|'
                     r'terms|privacy|account|cart|login|store-locator|ingredient)', re.I)


def bkey(b):
    return re.sub(r'[^a-z0-9]', '', str(b).lower())


def find_domain(brand):
    b = re.sub(r"[''`.]", '', str(brand).strip().lower()).replace('&', 'and')
    plain, hyph = re.sub(r'[^a-z0-9]', '', b), re.sub(r'[^a-z0-9]+', '-', b).strip('-')
    cands = []
    for stem in dict.fromkeys([plain, hyph, plain.replace('the', '', 1)]):
        if stem and len(stem) > 2:
            cands += [stem + t for t in ('.com', '.co.uk', '.co.kr', '.fr', '.de')]
    k = bkey(brand)
    for c in cands[:12]:
        try:
            r = S.get('https://' + c, timeout=TIMEOUT)
            if r.status_code >= 400:
                continue
            body = re.sub(r'[^a-z0-9]', '', re.sub(r'<[^>]+>', ' ', r.text[:80000]).lower())
            if k and len(k) > 3 and k in body:
                return r.url.split('/')[2]
        except Exception:
            continue
    return ''


def read_sitemap(url, depth=0, seen=None):
    """returns every <loc> in this sitemap and its children"""
    seen = seen if seen is not None else set()
    if url in seen or depth > 2 or len(seen) > 60:
        return []
    seen.add(url)
    try:
        r = S.get(url, timeout=TIMEOUT)
        if r.status_code != 200:
            return []
        txt = r.text
        if url.endswith('.gz') or r.content[:2] == b'\x1f\x8b':
            txt = gzip.GzipFile(fileobj=BytesIO(r.content)).read().decode('utf-8', 'ignore')
    except Exception:
        return []
    locs = re.findall(r'<loc>\s*([^<\s]+)\s*</loc>', txt)
    out, children = [], []
    for u in locs:
        (children if re.search(r'\.xml(\.gz)?$', u) else out).append(u)
    # prefer child sitemaps that sound like products
    children.sort(key=lambda u: 0 if re.search(r'product|item|shop', u, re.I) else 1)
    for c in children[:8]:
        out += read_sitemap(c, depth + 1, seen)
    return out


def product_urls(domain):
    """cached, once per brand"""
    with _lock:
        if domain in _cache:
            return _cache[domain]
    urls = []
    for p in ('/sitemap.xml', '/sitemap_index.xml', '/sitemap_products_1.xml',
              '/sitemap.xml.gz', '/robots.txt'):
        try:
            if p == '/robots.txt':
                r = S.get('https://' + domain + p, timeout=TIMEOUT)
                for sm in re.findall(r'(?i)sitemap:\s*(\S+)', r.text)[:4]:
                    urls += read_sitemap(sm)
            else:
                urls += read_sitemap('https://' + domain + p)
        except Exception:
            pass
        if len(urls) > 200:
            break
    keep, seen = [], set()
    for u in urls:
        if BAD_URL.search(u) or u in seen:
            continue
        seen.add(u)
        keep.append(u)
    keep = keep[:6000]
    with _lock:
        _cache[domain] = keep
    return keep


def slug_words(u):
    tail = u.rstrip('/').split('/')[-1]
    tail = re.sub(r'\.(html?|php|aspx)$', '', tail)
    return re.sub(r'[^a-z0-9]+', ' ', tail.lower()).strip()


def best_url(urls, name):
    n = re.sub(r'[^a-z0-9 ]', ' ', str(name).lower())
    best, score = '', 0
    for u in urls:
        s = fuzz.token_set_ratio(n, slug_words(u))
        if s > score:
            best, score = u, s
    return best, score


# ------------------------------------------------------------------ one product
def do(row):
    pid, brand, name = row['product_id'], row['brand'], row['name']
    rec = {k: '' for k in FIELDS}
    rec.update(product_id=pid, brand=brand, name=name,
               status='not found', failure_reason='')

    dom = find_domain(brand) if bkey(brand) not in _cache else _cache[bkey(brand)]
    with _lock:
        _cache[bkey(brand)] = dom
    if not dom:
        rec['failure_reason'] = 'no domain'
        return rec

    urls = product_urls(dom)
    if not urls:
        rec['failure_reason'] = 'no sitemap'
        rec['skin_type_source'] = dom
        return rec

    url, score = best_url(urls, name)
    rec['url_score'] = str(int(score))
    rec['skin_type_source'] = dom
    if score < URL_ACCEPT:
        rec['failure_reason'] = 'name not matched'
        return rec

    try:
        r = S.get(url, timeout=TIMEOUT)
        if r.status_code != 200:
            rec['failure_reason'] = 'page not fetched'
            return rec
    except Exception:
        rec['failure_reason'] = 'page not fetched'
        return rec

    hit = extract(r.text)
    if not hit:
        rec['failure_reason'] = 'no skin type on page'
        rec['skin_type_url'] = url
        return rec

    rec.update(hit)
    rec.update(skin_type_authority='manufacturer', skin_type_url=url, status='found')
    return rec


# ---------------------------------------------------------------------- main
def main():
    rows = list(csv.DictReader(open(DATASET, encoding='utf-8')))
    answered = set()
    if os.path.exists(PASS1):
        for r in csv.DictReader(open(PASS1, encoding='utf-8')):
            if r.get('skin_type') or r.get('universal_claim') == '1':
                answered.add(r['product_id'])
        print(f'pass 1 answered {len(answered):,} products, they are skipped')
    if os.path.exists(OUT):
        for r in csv.DictReader(open(OUT, encoding='utf-8')):
            answered.add(r['product_id'])
        print(f'resuming pass 2')

    todo = [r for r in rows if r['product_id'] not in answered]
    todo.sort(key=lambda r: r['brand'])
    print(f'{len(todo):,} products to try, {WORKERS} workers')
    print('reading sitemaps, not search boxes. one sitemap per brand, then no '
          'network at all for the name match.\n')

    new = not os.path.exists(OUT)
    f = open(OUT, 'a', newline='', encoding='utf-8')
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new:
        w.writeheader()

    found = 0
    reasons = {}
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
            if rec['status'] == 'found':
                found += 1
            else:
                reasons[rec['failure_reason']] = reasons.get(rec['failure_reason'], 0) + 1
            if i % 25 == 0 or i == len(todo):
                top = sorted(reasons.items(), key=lambda x: -x[1])[:2]
                print(f'  {i:6,}/{len(todo):,}  found {found:,} ({100*found/i:.0f}%)  '
                      f'| {"; ".join(f"{k} {v}" for k, v in top)}  '
                      f'| {rec["brand"][:15]:15s} {rec["skin_type"] or rec["failure_reason"][:20]}')
    f.close()

    print('\n' + '=' * 64)
    print(f'  attempted            {len(todo):,}')
    print(f'  found                {found:,}  ({100*found/max(len(todo),1):.1f}%)')
    print('\n  WHY THE REST FAILED, this is what tells us the next fix')
    for k, v in sorted(reasons.items(), key=lambda x: -x[1]):
        print(f'     {k or "(blank)":24s}{v:6,}')
    print(f'\nwrote {OUT}\nnext:  py skintype_apply.py')


if __name__ == '__main__':
    main()
