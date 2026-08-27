"""
Is the shopify shortcut losing the formula

The full HTML of these pages gave a formula for 8 of 28 sample pages. The live
run, which reads the small Shopify JSON instead, is finding about 2 percent.

Either the sample was lucky, or the shortcut is reading less of the page than
the page contains. Those need opposite responses, so this asks both ways on
the SAME handful of pages and prints the two answers side by side.

It fetches at most 8 pages. Nothing is written anywhere.

Usage:
    py check_shopify_json.py
"""
import re
import ssl
import sys
import json
import gzip
import urllib.request

src = open('fill_gaps_from_pages.py', encoding='utf-8').read()
head = src.split('# ---------------------------------------------------------'
                 '------ the data')[0]
tail = src.split('SHOPIFY = re.compile')[1].split('def fetch(url):')[0]
ns = {}
exec(compile(head, 'r', 'exec'), ns)
exec(compile('SHOPIFY = re.compile' + tail, 'r', 'exec'), ns)
read_ingredients = ns['read_ingredients']
strip_html = ns['strip_html']
shopify_json_url = ns['shopify_json_url']
text_from_shopify = ns['text_from_shopify']

UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/124.0 Safari/537.36')
CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def fetch(url):
    req = urllib.request.Request(url, headers={
        'User-Agent': UA, 'Accept-Encoding': 'gzip',
        'Accept': 'text/html,application/json'})
    with urllib.request.urlopen(req, timeout=25, context=CTX) as r:
        raw = r.read(3_000_000)
        if r.headers.get('Content-Encoding') == 'gzip':
            raw = gzip.decompress(raw)
    return raw.decode('utf-8', 'replace')


# the pages saved by --peek, which are known to contain a formula in the HTML
URLS = []
import glob
import os
for f in sorted(glob.glob('peek_pages/*.txt')):
    first = open(f, encoding='utf-8').readline()
    if first.startswith('URL: '):
        URLS.append(first[5:].strip())
URLS = [u for u in URLS if shopify_json_url(u)][:8]

if not URLS:
    sys.exit('no peek pages found, run:  py fill_gaps_from_pages.py --test 60 --peek 4')

print('=' * 74)
print('  THE SAME PAGE ASKED BOTH WAYS')
print('=' * 74)
print(f'  {len(URLS)} pages\n')

win_html = win_json = both = neither = 0
for u in URLS:
    try:
        h = read_ingredients(strip_html(fetch(u)))
    except Exception as e:
        h = f'<{type(e).__name__}>'
    try:
        j = read_ingredients(text_from_shopify(fetch(shopify_json_url(u))))
    except Exception as e:
        j = f'<{type(e).__name__}>'
    ok_h = bool(h) and not h.startswith('<')
    ok_j = bool(j) and not j.startswith('<')
    if ok_h and ok_j:
        both += 1
        verdict = 'both'
    elif ok_h:
        win_html += 1
        verdict = 'ONLY THE FULL PAGE'
    elif ok_j:
        win_json += 1
        verdict = 'only the json'
    else:
        neither += 1
        verdict = 'neither'
    print(f'  {verdict}')
    print(f'    {u[:78]}')
    print(f'    full page : {(h or "nothing")[:64]}')
    print(f'    json      : {(j or "nothing")[:64]}')
    print()

print('-' * 74)
print(f'  both ways worked        {both}')
print(f'  ONLY the full page      {win_html}')
print(f'  only the json           {win_json}')
print(f'  neither                 {neither}')
print()
if win_html > both:
    print('  THE SHORTCUT IS LOSING FORMULAS. Turn it off:')
    print('     in fill_gaps_from_pages.py set   USE_SHOPIFY_JSON = False')
    print('  the run gets slower but stops throwing away the answer.')
else:
    print('  The shortcut is not the problem. The pages really do not')
    print('  publish a formula, which is a finding rather than a fault.')
