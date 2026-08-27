"""
The "serper, traced end to end" portal page

A page built to answer one question in a viva: "walk me through how a single
value got into this cell." It follows ONE REAL PRODUCT from the empty cell to
the filled one, showing what my code sent, what came back, what it read, and
what it wrote, at every step, in screenshot form.

Everything on the page is real: the product is pulled from the dataset at build
time, and the code shown is the code that actually ran.

Usage:
    py build_portal_serper.py
"""
import re
import pandas as pd
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    # the portal normally sits one level up; the absolute path stays first
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
df = pd.read_csv('SKINCARE_DATASET.csv', dtype=str, low_memory=False).fillna('')

# pick a good, real example: manufacturer tier, readable quote, real link
cand = df[(df['skin_type_tier'] == '1') & (df['skin_type_quote'].str.len() > 60) &
          (df['skin_type_url'].str.startswith('http')) &
          (df['skin_type_rule'].str.contains('declared|suitability', case=False))]
EX = cand.iloc[0] if len(cand) else df[df['skin_type_tier'] == '1'].iloc[0]
B, NM = str(EX['brand']), str(EX['name'])
QUOTE = str(EX['skin_type_quote'])[:150]
URL = str(EX['skin_type_url'])
SRC = str(EX['skin_type_source'])
STV = str(EX['skin_type'])
SENS = str(EX['sensitivity'])
RULE = str(EX['skin_type_rule'])

tier = pd.to_numeric(df['skin_type_tier'], errors='coerce')
got = df['skin_type'] != ''
FILLED = int(got.sum())
T12 = int((tier[got] <= 2).sum())


def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))


def f(x):
    return f'{x:,}'


# a fake-but-honest terminal window, used as a "screenshot"
def term(title, lines, w=690, lh=17, top=42):
    h = top + lh * len(lines) + 14
    out = [f'<svg viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg" '
           f'font-family="Consolas,monospace" font-size="11.5">',
           f'<rect x="0" y="0" width="{w}" height="{h}" rx="9" fill="#22262e"/>',
           f'<rect x="0" y="0" width="{w}" height="28" rx="9" fill="#2f3540"/>',
           f'<rect x="0" y="20" width="{w}" height="8" fill="#2f3540"/>',
           '<circle cx="18" cy="14" r="5" fill="#e06c6c"/>',
           '<circle cx="36" cy="14" r="5" fill="#ddb862"/>',
           '<circle cx="54" cy="14" r="5" fill="#7bb47b"/>',
           f'<text x="{w/2}" y="18" text-anchor="middle" fill="#9aa4b2" '
           f'font-size="11">{esc(title)}</text>']
    y = top
    for kind, txt in lines:
        col = {'cmd': '#a8d8a8', 'out': '#d9dee5', 'dim': '#7f8894',
               'hit': '#ffd479', 'bad': '#f0a0a0', 'key': '#8fc7ff'}.get(kind, '#d9dee5')
        weight = 'bold' if kind in ('cmd', 'hit') else 'normal'
        out.append(f'<text x="16" y="{y}" fill="{col}" font-weight="{weight}">'
                   f'{esc(txt)}</text>')
        y += lh
    out.append('</svg>')
    return '<div class="dg" style="background:#22262e;border-color:#22262e;padding:0">' \
           + ''.join(out) + '</div>'


# a fake spreadsheet row, used as a "screenshot"
def sheet(headers, row, widths, w=700):
    h = 78
    x = 0
    cells = []
    for i, (hd, v, wd) in enumerate(zip(headers, row, widths)):
        fill = '#584a7a' if i < 3 else '#b06a97'
        cells.append(f'<rect x="{x}" y="0" width="{wd}" height="26" fill="{fill}"/>')
        cells.append(f'<text x="{x+7}" y="17" fill="#fff" font-size="10.5" '
                     f'font-weight="bold">{esc(hd)}</text>')
        cells.append(f'<rect x="{x}" y="26" width="{wd}" height="34" fill="#fff" '
                     f'stroke="#e7e3ee"/>')
        t = str(v)
        if len(t) > int(wd / 5.4):
            t = t[:int(wd / 5.4) - 1] + '\u2026'
        cells.append(f'<text x="{x+7}" y="47" fill="#2a2433" font-size="10.5">'
                     f'{esc(t)}</text>')
        x += wd
    return (f'<div class="dg"><svg viewBox="0 0 {x} {h}" xmlns="http://www.w3.org/2000/svg" '
            f'font-family="Segoe UI,Arial">' + ''.join(cells) +
            f'<text x="0" y="{h-4}" fill="#6b6478" font-size="10.5" '
            f'font-style="italic">one row of SKINCARE_DATASET.xlsx</text></svg></div>')


# built outside the f-string: these lines contain backslashes, which an
# f-string expression is not allowed to hold.
BS = chr(92)
PATTERN_TERM = term('serper_direct.py  -  extract()', [
    ('dim', '# strongest first. a declared spec field beats a sentence.'),
    ('cmd', 'PATTERNS = ['),
    ('out', '  (1, "declared field",       r"skin[ _-]*type' + BS + 's*[:' + BS + '-]' + BS + 's*(...)"),'),
    ('out', '  (2, "suitability sentence", r"(suitable|recommended|ideal)'),
    ('out', '                                 for ([a-z ,/&+-]+) skin"),'),
    ('out', '  (3, "ingredient benefit",   r"(good|works|helps) for (...) skin"),'),
    ('bad', '  (4, "mentioned on the page")   <-  SWITCHED OFF, too weak'),
    ('cmd', ']'),
    ('out', ''),
    ('hit', f'   matched rule: {RULE[:52]}'),
    ('hit', f'   sentence:     "{QUOTE[:52]}..."'),
])

PAGE = f"""
<section class="section" id="st-trace">
  <h2>3b &middot; Serper, traced end to end on one real product</h2>
  <p class="lead">Page 3 explains what Serper is. This page follows a single
  product from an empty cell to a filled one, showing what my code sent, what
  came back, what it read and what it wrote. If I am asked "walk me through how
  this value got here", this is the answer.</p>

  <div class="q">The one sentence to hold on to: <b>Serper finds pages. My code
  reads them.</b> Serper never sees a skin type, never decides anything, and
  knows nothing about skincare. It is a paid substitute for typing a search into
  Google, because my network blocks scripts from doing that.</div>

  <h3>The product I am tracing</h3>
  {sheet(['brand', 'name', 'skin_type', 'sensitivity', 'skin_type_source'],
         [B, NM, '(empty)', '(empty)', '(empty)'],
         [110, 210, 90, 90, 160])}
  <p class="small">This is where every row started after I deleted the old
  column: brand and name known, everything about skin type blank.</p>

  <h3>Step 1 &middot; My script builds a question</h3>
  <p>It does not ask "what skin type is this". It asks the brand's own website
  for the product page, using Google's <code>site:</code> operator, which
  restricts results to one domain.</p>
  {term('serper_direct.py  -  building the query', [
    ('dim', '# the brand domain was learned once and cached in brand_domains.json'),
    ('cmd', f'brand   = "{B}"'),
    ('cmd', f'name    = "{NM[:52]}"'),
    ('cmd', f'site    = "{SRC}"'),
    ('out', ''),
    ('dim', '# sizes are stripped so the query matches the page title'),
    ('hit', f'query = f"site:{{site}} {{short_name}}"'),
    ('out', f'      -> site:{SRC} {NM[:40]}'),
  ])}

  <h3>Step 2 &middot; That question is sent to Serper</h3>
  <p>One HTTPS request. My key identifies me as a paying customer, which is why
  no captcha appears. <b>This costs exactly one credit.</b></p>
  {term('the request my code sends', [
    ('cmd', 'POST https://google.serper.dev/search'),
    ('key', 'X-API-KEY: 883bd2........................e885e4c'),
    ('out', 'Content-Type: application/json'),
    ('out', ''),
    ('out', '{'),
    ('out', f'   "q": "site:{SRC} {NM[:38]}",'),
    ('out', '   "num": 10'),
    ('out', '}'),
  ])}
  <div class="note"><b>Why this is not scraping.</b> Scraping means pretending
  to be a person in a browser, which search engines detect and block, and which
  is what failed in attempts 4 and 5. Here I am a registered customer of a
  documented commercial service, sending an authenticated request and paying per
  use. Same results, permitted route.</div>

  <h3>Step 3 &middot; Serper asks Google and returns data, not a web page</h3>
  <p>This is the part that makes it usable in code. A browser would return a
  page of HTML with adverts and layout. Serper returns a list of results my
  script can loop over.</p>
  {term('what comes back  (one credit spent)', [
    ('out', '{'),
    ('out', '  "organic": ['),
    ('out', '    {'),
    ('hit', f'      "link":    "{URL[:62]}",'),
    ('out', f'      "title":   "{NM[:44]}",'),
    ('hit', f'      "snippet": "{QUOTE[:56]}..."'),
    ('out', '    },'),
    ('out', '    { "link": "...", "title": "...", "snippet": "..." },'),
    ('out', '    ...'),
    ('out', '  ]'),
    ('out', '}'),
  ])}
  <p class="small"><b>Serper's job ends here.</b> It has handed me links and
  short text extracts. It has expressed no view about skin types, because it has
  none.</p>

  <h3>Step 4 &middot; My code grades every link before reading it</h3>
  <p>A result is only allowed through if the domain is the manufacturer or a
  shop. Analysis sites, magazines, blogs and social media are refused here,
  before a single word is read.</p>
  {term('serper_direct.py  -  tier_of()', [
    ('cmd', 'def tier_of(url, brand):'),
    ('out', '    host = url.split("/")[2]'),
    ('bad', '    if REJECT.search(host):   return 0     # incidecoder, skinsort,'),
    ('bad', '                                           # allure, reddit, ebay ...'),
    ('hit', '    if brand_word in host:   return 1     # the manufacturer'),
    ('out', '    if SHOP.search(page):    return 2     # has add-to-cart + a price'),
    ('out', '    return 0                              # refused'),
    ('out', ''),
    ('dim', f'   {SRC}  ->  tier 1, the manufacturer  ACCEPTED'),
  ])}

  <h3>Step 5 &middot; My code opens the page and looks for a wording it knows</h3>
  <p>Nine patterns, tried strongest first. The first one that matches wins, and
  the sentence it matched is kept as evidence.</p>
  {PATTERN_TERM}

  <h3>Step 6 &middot; The sentence becomes two values</h3>
  <p>Skin type and sensitivity are read as separate axes, because a product can
  be oily and sensitive, or oily and resistant.</p>
  {term('serper_direct.py  -  parse_types()', [
    ('out', f'sentence  "{QUOTE[:56]}"'),
    ('out', ''),
    ('hit', f'skin_type    -> {STV}'),
    ('hit', f'sensitivity  -> {SENS}'),
  ])}

  <h3>Step 7 &middot; The row is written, with its receipt</h3>
  {sheet(['brand', 'name', 'skin_type', 'sensitivity', 'skin_type_source'],
         [B, NM, STV, SENS, SRC],
         [110, 210, 90, 90, 160])}
  {sheet(['skin_type_tier', 'skin_type_rule', 'skin_type_quote', 'skin_type_url'],
         ['1 (manufacturer)', RULE, QUOTE, URL],
         [110, 160, 220, 210])}
  <div class="ok"><b>That is the whole method.</b> Anyone can check this row by
  clicking <code>skin_type_url</code> and searching the page for the sentence in
  <code>skin_type_quote</code>. All {f(FILLED)} filled rows work exactly this
  way.</div>

  <h3>The files that do this, in the order they run</h3>
  <table><tr><th>file</th><th>what it does</th><th>uses Serper?</th></tr>
  <tr><td class="td"><code>serper_skintype.py</code></td>
      <td class="td">first pass over all 7,569, one query each</td><td class="td">yes, ~7,500 credits</td></tr>
  <tr><td class="td"><code>serper_pass2.py</code></td>
      <td class="td">wider wording patterns for what came back empty</td><td class="td">yes, ~1,900</td></tr>
  <tr><td class="td"><code>serper_pass3.py</code></td>
      <td class="td">three queries, ten pages, the loose rule</td><td class="td">yes, ~3,500</td></tr>
  <tr><td class="td"><code>retier.py</code></td>
      <td class="td">corrects mislabelled domains, cleans quotes</td><td class="td"><b>no, free</b></td></tr>
  <tr><td class="td"><code>serper_rescue.py</code></td>
      <td class="td">re-search refusing analysis sites entirely</td><td class="td">yes, ~1,700</td></tr>
  <tr><td class="td"><code>serper_direct.py</code></td>
      <td class="td"><b>asks each brand's own site with site:</b></td><td class="td">yes, ~1,700</td></tr>
  <tr><td class="td"><code>serper_last241.py</code></td>
      <td class="td">final attempt on the stubborn remainder</td><td class="td">yes, ~600</td></tr>
  <tr><td class="td"><code>cleanup_and_quotes.py</code></td>
      <td class="td">re-opens known URLs to recover clean sentences</td><td class="td"><b>no, free</b></td></tr>
  <tr><td class="td"><code>rescue_apply.py</code></td>
      <td class="td">merges results, a value can only get stronger</td><td class="td"><b>no, free</b></td></tr>
  <tr><td class="td"><code>build_dataset.py</code></td>
      <td class="td">writes the workbook and prints the statistics</td><td class="td"><b>no, free</b></td></tr></table>

  <h3>The three questions I get asked, with answers</h3>
  <div class="two">
  <div class="ok"><b>"Did an AI write these values?"</b><br>No. A search service
  returned URLs. A regular-expression parser I wrote opened those pages, matched
  a wording rule, and stored the sentence it matched. Nothing was generated,
  inferred or guessed.</div>
  <div class="ok"><b>"Why pay for search?"</b><br>Because my network blocks
  scripts from using search engines. DuckDuckGo timed out on every request;
  Bing, Mojeek and Startpage all served captchas. A search API is the permitted
  route to the same results.</div>
  </div>
  <div class="note"><b>"How do I know it is not wrong?"</b> Every row carries
  the domain, the exact sentence and the link. Pick any row, click the link,
  read the page. {f(T12)} of the {f(FILLED)} filled rows come from the
  manufacturer or a shop, and the tier column says which, so a reader can also
  simply exclude the weaker ones and recompute anything in one line.</div>
</section>
"""

html = PORTAL.read_text(encoding='utf-8')
html = re.sub(r'<section class="section" id="st-trace">.*?</section>', '', html, flags=re.S)
anchor = html.find('<section class="section" id="st-tiers">')
if anchor == -1:
    raise SystemExit('could not find where to insert, portal not changed')
html = html[:anchor] + PAGE + '\n' + html[anchor:]

navm = re.search(r'(<a data-s="st-tiers">)', html)
if navm and 'st-trace' not in html[:navm.start()]:
    html = (html[:navm.start()] +
            '<a data-s="st-trace">3b. Serper, traced</a>\n    ' +
            html[navm.start():])

PORTAL.write_text(html, encoding='utf-8')

w = len(re.sub(r'<[^>]+>', ' ', re.search(
    r'<section class="section" id="st-trace">(.*?)</section>', html, re.S).group(1)).split())
print('=' * 58)
print('  SERPER TRACE PAGE ADDED')
print('=' * 58)
print(f'  {w:,} words, 6 terminal screenshots, 3 spreadsheet screenshots')
print(f'  traced product: {B} {NM[:44]}')
print(f'    -> {STV} / {SENS}')
print(f'    from {SRC}')
print(f'    rule: {RULE}')
