"""
Skin type, per product, without a search engine

Why this design
  My first version searched DuckDuckGo for each product. It returned nothing.
  A diagnostic (_test_search.py) showed why, and it is not a bug in my code:

      DuckDuckGo html/lite   ConnectTimeout, never opened a connection
      Bing                   200 but a captcha challenge, 0 results
      Mojeek                 200 but a captcha, 0 results
      Startpage              200 "Startpage Blocked", 0 results

Usage:
    py -m pip install requests rapidfuzz
    py skintype_search.py      ->  skintype_search_results.csv
"""
import os
import re
import csv
import json
import time
import threading
import requests
from urllib.parse import quote_plus, urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed
from rapidfuzz import fuzz

DATASET = 'SKINCARE_DATASET.csv'
OUT = 'skintype_search_results.csv'
DOMCACHE = 'brand_domain_cache.csv'
WORKERS = 8
TIMEOUT = 12
NAME_ACCEPT = 80          # reject a site hit below this similarity
SERPER_KEY = ''           # optional. https://serper.dev  free tier 2,500 queries

HEAD = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9'}

FIELDS = ['product_id', 'brand', 'name', 'skin_type', 'sensitivity', 'universal_claim',
          'skin_type_source', 'skin_type_authority', 'skin_type_strength',
          'skin_type_rule', 'skin_type_quote', 'skin_type_url',
          'matched_title', 'name_score', 'status']

RETAILERS = [('www.sephora.com', '/search?keyword={q}'),
             ('www.ulta.com', '/search?Ntt={q}'),
             ('incidecoder.com', '/search?query={q}')]

# ------------------------------------------------------------------ the rule
TYPE_WORDS = {'dry': 'Dry', 'oily': 'Oily', 'oil': 'Oily', 'combination': 'Combination',
              'combo': 'Combination', 'normal': 'Normal', 'acne': 'Oily',
              'acne-prone': 'Oily', 'blemish-prone': 'Oily'}
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
    i = max(flat.rfind('.', 0, a), flat.rfind('!', 0, a),
            flat.rfind('|', 0, a), flat.rfind('•', 0, a), 0)
    j = min([x for x in (flat.find('.', b), flat.find('!', b), flat.find('|', b))
             if x != -1] or [len(flat)])
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
            val = m.group(1).strip(' .,:;-')
            if len(val) <= 60:
                r = build(val, flat[max(0, m.start() - 20):m.end() + 20].strip(),
                          1, 'declared field')
                if r:
                    return r
    for pat, strength, rule in ((SUIT_PAT, 2, 'suitability sentence'),
                                (BENEFIT_PAT, 3, 'ingredient benefit')):
        for m in pat.finditer(flat):
            sent = sentence_around(flat, m.start(), m.end())
            if len(sent) > 400:
                sent = flat[max(0, m.start() - 120):m.end() + 160]
            r = build(sent, sent, strength, rule)
            if r:
                return r
    return None


# -------------------------------------------------- brand domain, cached once
_dom, _lock = {}, threading.Lock()
S = requests.Session()
S.headers.update(HEAD)


def slugs(brand):
    b = re.sub(r"[''`]", '', str(brand).strip().lower()).replace('&', 'and')
    plain = re.sub(r'[^a-z0-9]', '', b)
    hyph = re.sub(r'[^a-z0-9]+', '-', b).strip('-')
    out, seen = [], set()
    for st in (plain, hyph):
        if st and st not in seen and len(st) > 2:
            seen.add(st)
            for tld in ('.com', '.co.uk', '.fr', '.co.kr'):
                out.append(st + tld)
    return out[:8]


def brand_key(b):
    return re.sub(r'[^a-z0-9]', '', str(b).lower())


def domain_for(brand):
    k = brand_key(brand)
    with _lock:
        if k in _dom:
            return _dom[k]
    found = ''
    for cand in slugs(brand):
        try:
            r = S.get('https://' + cand, timeout=TIMEOUT)
            if r.status_code >= 400:
                continue
            body = re.sub(r'<[^>]+>', ' ', r.text[:80000]).lower()
            if k and len(k) > 3 and k in re.sub(r'[^a-z0-9]', '', body):
                found = r.url.split('/')[2]
                break
        except Exception:
            continue
    with _lock:
        _dom[k] = found
    return found


# --------------------------------------------------------- the site's own search
PROD_LINK = re.compile(r'href="([^"]*/(?:products?|p|shop|item)/[^"?#]+)"', re.I)


def site_search(domain, query):
    """ask the site's own search box. returns [(url, title), ...]"""
    hits = []
    # Shopify JSON search: exact, fast, gives titles for free
    try:
        u = (f'https://{domain}/search/suggest.json?q={quote_plus(query)}'
             f'&resources[type]=product&resources[limit]=6')
        r = S.get(u, timeout=TIMEOUT)
        if r.status_code == 200 and 'json' in r.headers.get('Content-Type', ''):
            for p in r.json().get('resources', {}).get('results', {}).get('products', []):
                hits.append((urljoin('https://' + domain, p.get('url', '')), p.get('title', '')))
            if hits:
                return hits
    except Exception:
        pass
    # ordinary search pages
    for path in ('/search?q={q}', '/catalogsearch/result/?q={q}', '/?s={q}', '/search?query={q}'):
        try:
            r = S.get('https://' + domain + path.format(q=quote_plus(query)), timeout=TIMEOUT)
            if r.status_code != 200:
                continue
            urls, seen = [], set()
            for href in PROD_LINK.findall(r.text):
                full = urljoin('https://' + domain, href)
                if full in seen:
                    continue
                seen.add(full)
                urls.append(full)
            if urls:
                return [(u, '') for u in urls[:6]]
        except Exception:
            continue
    return hits


def title_of(html):
    m = re.search(r'<title[^>]*>(.*?)</title>', html, re.S | re.I)
    return re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''


def try_site(domain, brand, name, authority, rec):
    """search one site for one product. fills rec and returns True on success."""
    for url, title in site_search(domain, f'{brand} {name}')[:4]:
        try:
            r = S.get(url, timeout=TIMEOUT)
            if r.status_code != 200:
                continue
            html = r.text
        except Exception:
            continue
        t = title or title_of(html)
        score = fuzz.token_set_ratio(name.lower(), t.lower())
        if score < NAME_ACCEPT:
            continue                                   # wrong product, not guessed
        hit = extract(html)
        if not hit:
            continue
        rec.update(hit)
        rec.update(skin_type_source=domain, skin_type_authority=authority,
                   skin_type_url=url, matched_title=t[:120],
                   name_score=str(int(score)), status='found')
        return True
    return False


def do_product(row):
    pid, brand, name = row['product_id'], row['brand'], row['name']
    rec = {k: '' for k in FIELDS}
    rec.update(product_id=pid, brand=brand, name=name, status='not found')
    if not brand or not name:
        rec['status'] = 'no brand or name'
        return rec

    dom = domain_for(brand)
    if dom and try_site(dom, brand, name, 'manufacturer', rec):
        return rec
    for host, _ in RETAILERS:
        if try_site(host, brand, name, 'retailer', rec):
            return rec
    if not dom:
        rec['status'] = 'brand domain not found'
    return rec


# --------------------------------------------------------------------- main
def main():
    rows = list(csv.DictReader(open(DATASET, encoding='utf-8')))
    done = set()
    if os.path.exists(OUT):
        done = {r['product_id'] for r in csv.DictReader(open(OUT, encoding='utf-8'))}
        print(f'resuming, {len(done):,} products already done')
    todo = [r for r in rows if r['product_id'] not in done]
    # group by brand so the domain cache is hit immediately
    todo.sort(key=lambda r: r['brand'])
    print(f'{len(todo):,} products to do, {WORKERS} workers')
    print('no search engine is used. each brand site is asked directly.\n')

    new = not os.path.exists(OUT)
    f = open(OUT, 'a', newline='', encoding='utf-8')
    w = csv.DictWriter(f, fieldnames=FIELDS)
    if new:
        w.writeheader()

    found = man = 0
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(do_product, r): r for r in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                rec = fut.result()
            except Exception as e:
                r = futs[fut]
                rec = {k: '' for k in FIELDS}
                rec.update(product_id=r['product_id'], brand=r['brand'],
                           name=r['name'], status='error: ' + str(e)[:60])
            w.writerow(rec)
            f.flush()
            if rec['status'] == 'found':
                found += 1
                if rec['skin_type_authority'] == 'manufacturer':
                    man += 1
            if i % 25 == 0 or i == len(todo):
                print(f'  {i:6,}/{len(todo):,}  found {found:,} ({100*found/i:.0f}%)  '
                      f'from the brand {man:,}  domains cached {len(_dom):,}  '
                      f'last: {rec["brand"][:16]:16s} {rec["skin_type"] or rec["status"][:18]}')
    f.close()

    res = list(csv.DictReader(open(OUT, encoding='utf-8')))
    n = len(res)
    got = [r for r in res if r['skin_type']]
    uni = [r for r in res if r['universal_claim'] == '1']
    print('\n' + '=' * 64)
    print(f'  products processed        {n:,}')
    print(f'  skin type found           {len(got):,}  ({100*len(got)/n:.1f}%)')
    print(f'  "all skin types"          {len(uni):,}')
    print(f'  nothing found             {n-len(got)-len(uni):,}')
    if got:
        print('\n  who answered')
        for a in ('manufacturer', 'retailer'):
            c = sum(1 for r in got if r['skin_type_authority'] == a)
            print(f'     {a:16s}{c:6,}  ({100*c/len(got):.1f}%)')
        print('\n  how strongly')
        for k, lab in (('1', 'declared field'), ('2', 'suitability'), ('3', 'ingredient benefit')):
            c = sum(1 for r in got if r['skin_type_strength'] == k)
            print(f'     {k} {lab:22s}{c:6,}')
    print(f'\nwrote {OUT}\nnext:  py skintype_apply.py')


if __name__ == '__main__':
    main()
