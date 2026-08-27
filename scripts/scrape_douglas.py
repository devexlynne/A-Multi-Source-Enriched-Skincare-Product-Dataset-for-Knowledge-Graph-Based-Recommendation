"""
SCRAPE SKIN TYPE FROM DOUGLAS.DE  (run on your laptop)

THE TRICK: I do not parse product pages at all.

Usage:
    py -m pip install requests beautifulsoup4 pandas
    py scrape_douglas.py
"""
import re, time, json, unicodedata
import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE  = 'https://www.douglas.de'
PAUSE = 2.0
# Douglas returns HTTP 400 to anything that does not look like a real browser.
# A User-Agent alone is not enough - it checks the whole header set, so these
# mirror what Chrome actually sends, and a Session keeps the cookies it hands
# back on the first request.
HEAD = {
 'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'),
 'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,'
            'image/avif,image/webp,*/*;q=0.8'),
 'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
 'Accept-Encoding': 'gzip, deflate, br',
 'Connection': 'keep-alive',
 'Upgrade-Insecure-Requests': '1',
 'Sec-Fetch-Dest': 'document',
 'Sec-Fetch-Mode': 'navigate',
 'Sec-Fetch-Site': 'none',
 'Sec-Fetch-User': '?1',
 'sec-ch-ua': '"Chromium";v="126", "Google Chrome";v="126", "Not-A.Brand";v="99"',
 'sec-ch-ua-mobile': '?0',
 'sec-ch-ua-platform': '"Windows"',
}
# Douglas sits behind bot protection that fingerprints the TLS handshake, which
# plain `requests` cannot fake (it returns 403). cloudscraper is a drop-in
# replacement that handles that handshake. If it is not installed we fall back
# to a normal session so the script still runs.
try:
    import cloudscraper
    SESSION = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True})
    print('using cloudscraper (bot-protection aware)')
except ImportError:
    SESSION = requests.Session()
    print('cloudscraper not installed - falling back to plain requests')
    print('   if you get 403 errors, run:  py -m pip install cloudscraper')
SESSION.headers.update(HEAD)

# the page IS the label
CATEGORIES = [
    ('dry',         '/de/c/gesicht/pflege-nach-hautbeduerfnis/fuer-trockene-haut/120601'),
    ('oily',        '/de/c/gesicht/pflege-nach-hautbeduerfnis/fuer-fettige-haut/120602'),
    ('sensitive',   '/de/c/gesicht/pflege-nach-hautbeduerfnis/fuer-sensible-haut/120603'),
    ('acne',        '/de/c/gesicht/pflege-nach-hautbeduerfnis/fuer-unreine-haut/120604'),
    ('combination', '/de/c/hautpflege/hautzustaende-routinen/mischhaut/99190205'),
]
MAX_PAGES = 40          # Douglas paginates; stop when a page yields nothing new


def products_on(html):
    """Pull (brand, product name) pairs out of a Douglas listing page."""
    found = []
    soup = BeautifulSoup(html, 'html.parser')

    # best case: the page embeds structured JSON-LD
    for tag in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(tag.string or '{}')
        except (json.JSONDecodeError, TypeError):
            continue
        items = data.get('itemListElement') or []
        for it in items:
            node = it.get('item', it)
            nm = node.get('name')
            br = (node.get('brand') or {})
            br = br.get('name') if isinstance(br, dict) else br
            if nm:
                found.append((str(br or '').strip(), str(nm).strip()))

    # fallback 1: product tiles with brand and name as separate elements
    if not found:
        for tile in soup.select('[data-testid*="product"], .product-tile, article'):
            b = tile.select_one('[class*="brand"], [data-testid*="brand"]')
            n = tile.select_one('[class*="name"], [data-testid*="name"]')
            if b and n:
                found.append((b.get_text(' ', strip=True), n.get_text(' ', strip=True)))

    # fallback 2: every product links to /p/<id>, and the link text is
    # "<brand> <product name>" - this is what Douglas actually renders.
    if not found:
        for a in soup.select('a[href*="/p/"]'):
            txt = a.get_text(' ', strip=True)
            if not txt or len(txt) < 6:
                continue
            # strip the leading product-type phrase Douglas prefixes, e.g.
            # "Gesichtscreme für Unisex La Mer The Moisturizers Cream 30 ml"
            txt = re.sub(r'^[\wÄÖÜäöüß&\- ]{3,28}?\s+für\s+\w+\s+', '', txt)
            txt = re.sub(r'\s+\d+([.,]\d+)?\s*(ml|g|l|kg|Stück|St\.?)\b.*$', '', txt)
            txt = re.sub(r'\s+(UVP|ab)\b.*$', '', txt).strip()
            if len(txt.split()) >= 2:
                found.append(('', txt))          # brand unknown, name carries it
    return found


def warm_up():
    """Visit the homepage first so Douglas hands us its cookies, exactly as a
    browser would. Without this the very first category request often 400s."""
    try:
        SESSION.get(BASE + '/de', timeout=30)
        time.sleep(1.5)
    except requests.RequestException:
        pass


def main():
    warm_up()
    rows = []
    for label, path in CATEGORIES:
        print(f'\n=== {label.upper()} : {path}')
        seen_here = set()
        for page in range(MAX_PAGES):
            url = f'{BASE}{path}?page={page}' if page else f'{BASE}{path}'
            r = None
            for attempt in range(3):                 # Douglas 400s sporadically
                try:
                    r = SESSION.get(url, timeout=30)
                    if r.status_code == 200:
                        break
                    print(f'   status {r.status_code}, retry {attempt+1}/3')
                    time.sleep(4 * (attempt + 1))
                except requests.RequestException as e:
                    print('   request failed:', str(e)[:60])
                    time.sleep(4)
            if r is None or r.status_code != 200:
                print(f'   giving up on {label} at page {page}'); break

            got = products_on(r.text)
            new = [(b, n) for b, n in got if (b, n) not in seen_here]
            if not new:
                print(f'   page {page}: nothing new, done with {label}')
                break
            for b, n in new:
                seen_here.add((b, n))
                rows.append({'douglas_skin_type': label, 'brand': b, 'name': n})
            print(f'   page {page}: +{len(new)} products (total {len(seen_here)})')
            time.sleep(PAUSE)

    out = pd.DataFrame(rows).drop_duplicates()
    out.to_csv('douglas_skintype.csv', index=False)
    print(f'\nDONE. {len(out):,} product-labels scraped -> douglas_skintype.csv')
    if out.empty:
        print('\n!! Nothing captured. Douglas renders its listings with JavaScript,')
        print('   so plain requests may return an empty shell. If so, open one of')
        print('   the URLs above in Chrome, press Ctrl+U, and search for a product')
        print('   name: if it is absent from the source, this site needs a browser')
        print('   based scraper (Selenium/Playwright) instead of requests.')
    else:
        print(out['douglas_skin_type'].value_counts().to_string())
        print('\nnext: run merge_douglas.py')


if __name__ == '__main__':
    main()
