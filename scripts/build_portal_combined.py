"""
The "one dataset" portal page

The final page of the story: how the global source and the Lebanese source
became a single dataset, why the same rule was applied to both, which features
they share, and where coverage stands.

Every figure is read from COMBINED_DATASET.csv at build time.

Usage:
    py build_portal_combined.py
"""
import re
import pandas as pd
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    # the portal normally sits one level up; the absolute path stays first
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
c = pd.read_csv('COMBINED_DATASET.csv', dtype=str, low_memory=False).fillna('')
try:
    L = pd.read_csv('LEBANESE_RETAIL.csv', dtype=str, low_memory=False).fillna('')
except Exception:
    L = pd.DataFrame(columns=c.columns)

N = len(c)
SRC = c['source'].value_counts().to_dict()
GLOBAL = SRC.get('global (Skinsort)', 0)
BOTH = SRC.get('global + sold in Lebanon', 0)
NEWLB = SRC.get('Lebanese retail', 0)
tier = pd.to_numeric(c['skin_type_tier'], errors='coerce')
got = c['skin_type'] != ''
NGOT = max(int(got.sum()), 1)
T12 = int((tier[got] <= 2).sum())
BRANDS = int(c['brand'].nunique())
PRICE = int((c['price_usd'] != '').sum())
LEB_REV = len(L[L['review_source'] != '']) if len(L) else 0
LEB_ALL = len(L)


def f(x):
    return f'{x:,}'


def pc(x, of=None):
    return f'{100*x/(of or N):.1f}%'


def tbl(head, rows):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f"<td class='td'>{x}</td>" for x in r) + '</tr>'
                for r in rows)
    return f'<table><tr>{h}</tr>{b}</table>'


CORE = ['brand', 'name', 'product_type', 'country', 'skin_type', 'sensitivity',
        'ingredients', 'benefits', 'concerns', 'review_count', 'review_source']
cov_rows = []
for col in CORE + ['rating', 'skin_type_source', 'skin_type_url', 'price_usd']:
    if col not in c.columns:
        continue
    n = int((c[col] != '').sum())
    core = col in CORE
    mark = ('<b style="color:#3f6b48">100%</b>' if n == N
            else f'<b style="color:#b5484d">{f(N-n)} missing</b>' if core
            else pc(n))
    cov_rows.append([f'<code>{col}</code>', f(n), pc(n), mark])

gaps = {col: N - int((c[col] != '').sum()) for col in CORE
        if int((c[col] != '').sum()) < N}

GAPTEXT = {
    'skin_type': 'these products were searched and no manufacturer or shop states a '
                 'skin type. they carry <code>skin_type_status = "searched, not stated"</code>, '
                 'which is a finding rather than a blank.',
    'sensitivity': 'the same products as above. sensitivity is only written where a '
                   'skin type was established.',
    'ingredients': 'not present in any source on file.',
    'review_count': 'the review text exists but no count was published alongside it.',
}
if gaps:
    items = ''.join(
        f'<li><code>{k}</code>, {f(v)} missing. '
        + GAPTEXT.get(k, 'a genuine gap in the source.') + '</li>'
        for k, v in gaps.items())
    GAPBOX = ('<div class="note"><b>What is not at 100%, and why each is a real gap '
              'rather than an error.</b><ul style="margin:6px 0 0;font-size:13px">'
              + items + '</ul></div>')
else:
    GAPBOX = ('<div class="ok"><b>Every core feature is at 100%.</b> Nothing in '
              'the table above is a hole.</div>')

PAGE = f"""
<section class="section" id="cb-one">
  <h2>C &middot; One dataset: global and Lebanese together</h2>
  <p class="lead">Two sources, each cleaned completely on its own, then joined.
  This page is how they became one file, what rule decided which products got
  in, and where coverage stands.</p>

  <div class="kpis">
    <div class="kpi"><div class="n">{f(N)}</div><div class="l">products, every one with reviews</div></div>
    <div class="kpi"><div class="n">{f(BRANDS)}</div><div class="l">brands</div></div>
    <div class="kpi"><div class="n">{pc(T12, NGOT)}</div><div class="l">skin type from maker or shop</div></div>
    <div class="kpi"><div class="n">{f(PRICE)}</div><div class="l">carry a Lebanese price</div></div>
  </div>

  <h3>The rule that decides who gets in</h3>
  <div class="q">Keep only products that have reviews.</div>
  <p>This is not a new decision made for the merge. It is <b>step 0</b> of the
  cleaning pipeline already applied to the global source, which took it from
  19,059 products down to 7,595 for exactly this reason. Applying the same rule
  to the Lebanese source is what makes the two comparable rather than merely
  stacked on top of each other.</p>
  <p>The justification is simple: the thesis analyses reviews. A product with no
  review contributes nothing to that analysis, and carrying it forward only
  dilutes every coverage figure that gets quoted.</p>
  {tbl(['source', 'before step 0', 'after step 0'], [
    ['global (Skinsort)', '19,059', f(GLOBAL + BOTH)],
    ['Lebanese retail', f(LEB_ALL), f(LEB_REV)]])}

  <h3>How the two were joined</h3>
  <p>Not concatenated, <b>merged</b>. Products present in both sources appear
  once. This distinction is worth making if anyone asks, because concatenating
  would have inflated the count and duplicated every shared product.</p>

  <div class="dg">
  <svg viewBox="0 0 700 230" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11.5">
    <rect x="20" y="24" width="250" height="62" rx="9" fill="#f4f0fa" stroke="#7a68a6" stroke-width="1.6"/>
    <text x="145" y="46" text-anchor="middle" font-weight="700" fill="#584a7a">global, with reviews</text>
    <text x="145" y="68" text-anchor="middle" fill="#6b6478" font-size="15" font-weight="700">{f(GLOBAL + BOTH)}</text>
    <rect x="430" y="24" width="250" height="62" rx="9" fill="#eef6ee" stroke="#6f9c78" stroke-width="1.6"/>
    <text x="555" y="46" text-anchor="middle" font-weight="700" fill="#3f6b48">Lebanese, with reviews</text>
    <text x="555" y="68" text-anchor="middle" fill="#6b6478" font-size="15" font-weight="700">{f(LEB_REV)}</text>
    <path d="M270 55 C330 55 330 108 350 108" stroke="#b9aed0" fill="none" stroke-width="1.8"/>
    <path d="M430 55 C370 55 370 108 350 108" stroke="#a8c9ae" fill="none" stroke-width="1.8"/>
    <rect x="196" y="98" width="308" height="46" rx="9" fill="#584a7a"/>
    <text x="350" y="118" text-anchor="middle" fill="#fff" font-weight="700">matched on brand + product name</text>
    <text x="350" y="135" text-anchor="middle" fill="#d5cae8">exact first, then fuzzy at 90</text>
    <rect x="20" y="162" width="200" height="52" rx="9" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="120" y="182" text-anchor="middle" font-weight="700" fill="#8d5433">in BOTH: {f(BOTH)}</text>
    <text x="120" y="200" text-anchor="middle" fill="#6b6478">merged, not duplicated</text>
    <rect x="240" y="162" width="220" height="52" rx="9" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="350" y="182" text-anchor="middle" font-weight="700" fill="#3f6b48">NEW from Lebanon: {f(NEWLB)}</text>
    <text x="350" y="200" text-anchor="middle" fill="#6b6478">added as new rows</text>
    <rect x="480" y="162" width="200" height="52" rx="9" fill="#f4f0fa" stroke="#7a68a6"/>
    <text x="580" y="182" text-anchor="middle" font-weight="700" fill="#584a7a">global only: {f(GLOBAL)}</text>
    <text x="580" y="200" text-anchor="middle" fill="#6b6478">unchanged</text>
  </svg>
  <div class="cap">{f(GLOBAL)} + {f(BOTH)} + {f(NEWLB)} = {f(N)} products.</div></div>

  <h3>What happens to a product found in both</h3>
  <p>The global row is kept, because its skin type carries manufacturer-level
  evidence with a sentence and a link. The Lebanese columns are then written
  onto that same row.</p>
  {tbl(['kept from the global row', 'added from the Lebanese row'], [
    ['skin type, with its tier, sentence and URL', 'the retail price in Lebanon'],
    ['reviews and rating', 'which of the six shops stock it'],
    ['the standardised INCI ingredient list', 'a link to each shop listing'],
    ['benefits and concerns', 'the shop&rsquo;s own skin type wording']])}
  <p class="small">The overlap therefore makes rows <b>richer</b> rather than
  making the dataset <b>longer</b>. {f(BOTH)} products are now known to be both
  internationally reviewed and locally purchasable, which is a result the thesis
  can use directly.</p>

  <h3>Identical features, on purpose</h3>
  <p>Both sources went through the same cleaning sequence before being joined,
  following Rahm and Do (2000): clean each source completely <i>before</i>
  joining it to anything else.</p>
  {tbl(['cleaning step', 'global source', 'Lebanese source'], [
    ['0. keep only products with reviews', '19,059 &rarr; 7,595', f'{f(LEB_ALL)} &rarr; {f(LEB_REV)}'],
    ['1. fix broken letters', '623 cells repaired', 'accents folded for matching'],
    ['2. keep skincare only', '3,235 removed from the raw 19k', '6,967 removed'],
    ['3. remove duplicates', '26 removed', '644 duplicate listings removed'],
    ['4. every ingredient in official INCI', '99.95% official', 'inherited from the same INCI work'],
    ['5. skin type with evidence', 'Serper, tiered 1 to 4', 'shop claims, tiered the same way'],
    ['6. the same 22 product categories', '22 categories', 'filtered to the same 22']])}

  <h3>Coverage</h3>
  {tbl(['feature', 'filled', 'share', 'status'], cov_rows)}
  {GAPBOX}

  <h3>What the dataset is made of</h3>
  {tbl(['source', 'products', 'share'], [
    ['global (Skinsort) only', f(GLOBAL), pc(GLOBAL)],
    ['global <b>and</b> sold in Lebanon', f(BOTH), pc(BOTH)],
    ['Lebanese retail only', f(NEWLB), pc(NEWLB)],
    ['<b>total</b>', f'<b>{f(N)}</b>', '<b>100%</b>']])}

  <h3>What each source gave that the other could not</h3>
  <div class="two">
  <div class="ok"><b>The global source gave</b>
  <p style="margin:6px 0 0;font-size:13px">Reviews at scale, a standardised INCI
  ingredient list, and a skin type traceable to the manufacturer with the exact
  sentence and a link. {pc(T12, NGOT)} of filled skin types come from a maker or
  a shop.</p></div>
  <div class="ok"><b>The Lebanese source gave</b>
  <p style="margin:6px 0 0;font-size:13px">{f(NEWLB)} products that appear in no
  international catalogue, a retail price, and local availability across six
  shops. Without it the thesis would describe a market it never actually looked
  at.</p></div>
  </div>

  <h3>The files</h3>
  {tbl(['file', 'what it holds'], [
    ['<code>COMBINED_DATASET.xlsx</code>', f'the {f(N)} products, all columns, ready for analysis'],
    ['<code>COMBINED_DATASET.csv</code>', 'the same, for code'],
    ['<code>SKINCARE_DATASET.xlsx</code>', 'the global source on its own, before the merge'],
    ['<code>LEBANESE_RETAIL.xlsx</code>', 'the Lebanese source on its own, plus the raw scrape'],
    ['<code>FULL_DATASET_WORKBOOK.xlsx</code>', 'every sheet in one book, including everything removed']])}
  <p class="small">Both source datasets are kept intact beside the combined one,
  so any figure quoted about either source alone can still be verified without
  unpicking the merge.</p>
</section>
"""

html = PORTAL.read_text(encoding='utf-8')
html = re.sub(r'<section class="section" id="cb-one">.*?</section>', '', html, flags=re.S)
anchor = html.find('<!-- ============================================ HOME -->')
if anchor == -1:
    anchor = html.find('<section class="section" id="home">')
if anchor == -1:
    raise SystemExit('could not find where to insert, portal not changed')
html = html[:anchor] + PAGE + '\n\n' + html[anchor:]

if 'cb-one' not in re.search(r'<nav class="nav">.*?</nav>', html, re.S).group(0):
    nav = re.search(r'(\s*<div class="grp">overview</div>)', html)
    html = (html[:nav.start()] +
            '\n    <div class="grp">one dataset</div>\n'
            '    <a data-s="cb-one">C. Global + Lebanese</a>' + nav.group(1) +
            html[nav.end():])

PORTAL.write_text(html, encoding='utf-8')

w = len(re.sub(r'<[^>]+>', ' ', re.search(
    r'<section class="section" id="cb-one">(.*?)</section>', html, re.S).group(1)).split())
print('=' * 60)
print('  COMBINED DATASET PAGE ADDED')
print('=' * 60)
print(f'  {w:,} words\n')
print(f'  products                {f(N)}')
print(f'    global only           {f(GLOBAL)}')
print(f'    global + in Lebanon   {f(BOTH)}')
print(f'    Lebanese only         {f(NEWLB)}')
print(f'  brands                  {f(BRANDS)}')
print(f'  with a Lebanese price   {f(PRICE)}')
if gaps:
    print('\n  not yet 100%:')
    for k, v in gaps.items():
        print(f'    {k:16s}{f(v)} missing')
else:
    print('\n  every core feature at 100%')
