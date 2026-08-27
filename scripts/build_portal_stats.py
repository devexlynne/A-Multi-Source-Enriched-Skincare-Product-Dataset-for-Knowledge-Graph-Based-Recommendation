"""
The "all statistics" portal page

Every distribution in the combined dataset, on one page, so no figure has to be
looked for in a spreadsheet during a meeting. It mirrors sheet 4 STATISTICS of
COMBINED_DATASET.xlsx exactly, and both are computed from the same file.

Usage:
    py build_portal_stats.py
"""
import re
import pandas as pd
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    # the portal normally sits one level up; the absolute path stays first
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
c = pd.read_csv('COMBINED_DATASET.csv', dtype=str, low_memory=False).fillna('')
g = pd.read_csv('SKINCARE_DATASET.csv', dtype=str, low_memory=False).fillna('')
L = pd.read_csv('LEBANESE_RETAIL.csv', dtype=str, low_memory=False).fillna('')

N = len(c)
tier = pd.to_numeric(c['skin_type_tier'], errors='coerce')
got = c['skin_type'] != ''
NGOT = max(int(got.sum()), 1)
T = {t: int((tier[got] == t).sum()) for t in (1, 2, 3, 4)}
T12 = T[1] + T[2]
Lrev = int((L['review_source'] != '').sum())


def f(x):
    return f'{x:,}'


def pc(x, of=None):
    return f'{100*x/(of or N):.1f}%'


def nn(col, fr=None):
    fr = c if fr is None else fr
    return int((fr[col] != '').sum()) if col in fr.columns else 0


def tbl(head, rows):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f"<td class='td'>{x}</td>" for x in r) + '</tr>'
                for r in rows)
    return f'<table><tr>{h}</tr>{b}</table>'


def dist(series, of=None, top=None, label='value'):
    s = series if top is None else series.head(top)
    tot = of or int(series.sum())
    return tbl([label, 'products', 'share'],
               [[str(k) if str(k).strip() else '(blank)', f(v), pc(v, tot)]
                for k, v in s.items()])


COV = ['brand', 'name', 'product_type', 'country', 'skin_type', 'sensitivity',
       'ingredients', 'key_ingredients', 'free_from', 'spf', 'benefits',
       'concerns', 'rating', 'review_count', 'review_source', 'price_usd',
       'skin_type_source', 'skin_type_quote', 'skin_type_url']
cov_rows = []
for col in COV:
    if col not in c.columns:
        continue
    v = nn(col)
    cov_rows.append([f'<code>{col}</code>', f(v), pc(v),
                     '<b style="color:#3f6b48">complete</b>' if v == N
                     else f'{f(N-v)} missing'])

rules = (c.loc[got, 'skin_type_rule'].str.replace(r'\s*\(strength \d\)', '', regex=True)
         .value_counts().head(12))
sites = (c.loc[got, 'skin_type_source'].str.lower().str.replace('www.', '', regex=False)
         .value_counts().head(20))
lb = c[c['retailers'] != ''] if 'retailers' in c.columns else c.iloc[0:0]
shops = {}
for s in ('sohaticare', 'feel22', 'mazenonline', 'zeinacare', 'nexuscare', 'daouk'):
    shops[s] = int(lb['retailers'].str.contains(s, na=False).sum()) if len(lb) else 0

PAGE = f"""
<section class="section" id="cb-stats">
  <h2>C2 &middot; Every statistic, on one page</h2>
  <p class="lead">Everything here is computed from
  <code>COMBINED_DATASET.csv</code> when this page is built, and it mirrors
  sheet <b>4 STATISTICS</b> of the workbook exactly. Nothing has to be looked
  up in a spreadsheet during a meeting.</p>

  <div class="kpis">
    <div class="kpi"><div class="n">{f(N)}</div><div class="l">products</div></div>
    <div class="kpi"><div class="n">{f(c['brand'].nunique())}</div><div class="l">brands</div></div>
    <div class="kpi"><div class="n">{f(c['product_type'].nunique())}</div><div class="l">categories</div></div>
    <div class="kpi"><div class="n">{f(c['country'].nunique())}</div><div class="l">countries of origin</div></div>
    <div class="kpi"><div class="n">{pc(T12, NGOT)}</div><div class="l">skin types declared</div></div>
  </div>

  <h3>How each source was filtered down</h3>
  {tbl(['step', 'global (Skinsort)', 'Lebanese retail'], [
    ['raw', '19,059', '14,823 listings'],
    ['after removing duplicates', '&mdash;', '14,179'],
    ['after removing non-skincare', '&mdash;', f'{f(len(L))}'],
    ['after keeping only reviewed products', f'{f(len(g))}', f'{f(Lrev)}'],
    ['<b>contributed to the combined dataset</b>',
     f"<b>{f(int((c['source'] != 'Lebanese retail').sum()))}</b>",
     f"<b>{f(int((c['source'] == 'Lebanese retail').sum()))} new</b>"]])}

  <h3>Products by source</h3>
  {dist(c['source'].value_counts(), N, label='source')}

  <h3>Product category</h3>
  {dist(c['product_type'].value_counts(), N, label='category')}

  <h3>Country of origin</h3>
  {dist(c['country'].value_counts(), N, top=15, label='country')}

  <h3>Skin type</h3>
  {dist(c.loc[got, 'skin_type'].value_counts(), NGOT, label='skin type')}
  <p class="small">Shares are of the {f(NGOT)} products that have a skin type,
  not of all {f(N)}, because a share of the whole would silently count the
  {f(N-NGOT)} unfilled rows as a category.</p>

  <h3>Sensitivity</h3>
  {dist(c.loc[got, 'sensitivity'].value_counts(), NGOT, label='sensitivity')}

  <h3>Where the skin type came from</h3>
  {tbl(['tier', 'source', 'products', 'share of filled'], [
    ['1', 'the manufacturer', f(T[1]), pc(T[1], NGOT)],
    ['2', 'a shop that sells it', f(T[2]), pc(T[2], NGOT)],
    ['3', 'an analysis site', f(T[3]), pc(T[3], NGOT)],
    ['4', 'something else', f(T[4]), pc(T[4], NGOT)],
    ['<b>1 or 2</b>', '<b>declared, the figure to quote</b>',
     f'<b>{f(T12)}</b>', f'<b>{pc(T12, NGOT)}</b>']])}

  <h3>Skin type status</h3>
  {dist(c['skin_type_status'].value_counts(), N, label='status')}

  <h3>Which wording rule matched</h3>
  {dist(rules, NGOT, label='rule')}

  <h3>The websites that answered most often</h3>
  {dist(sites, NGOT, label='domain')}

  <h3>Review source</h3>
  {dist(c['review_source'].value_counts(), N, label='source')}

  <h3>Lebanese shops stocking these products</h3>
  {tbl(['shop', 'products in the combined dataset'],
       [[f'<code>{k}</code>', f(v)] for k, v in
        sorted(shops.items(), key=lambda x: -x[1])])}
  <p class="small">{f(len(lb))} products in the combined dataset are sold in
  Lebanon and carry a price. A product stocked by several shops appears against
  each of them, so these do not sum to {f(len(lb))}.</p>

  <h3>Top 20 brands</h3>
  {dist(c['brand'].value_counts(), N, top=20, label='brand')}

  <h3>Feature coverage</h3>
  {tbl(['feature', 'filled', 'share', 'status'], cov_rows)}

  <div class="note"><b>Reading the two incomplete features.</b>
  <code>skin_type</code> is {pc(nn('skin_type'))}: the missing
  {f(N-nn('skin_type'))} were searched and no manufacturer or shop states one,
  so they carry <code>skin_type_status = "searched, not stated"</code>, which is
  a finding rather than a blank. <code>ingredients</code> is missing for
  {f(N-nn('ingredients'))} products that appear in no source on file.
  <code>rating</code> and <code>price_usd</code> are not expected to be
  complete: a rating exists only where a numeric score was published, and a
  price only for products sold in Lebanon.</div>

  <h3>Where each figure lives in the workbook</h3>
  {tbl(['sheet', 'what it holds'], [
    ['<code>0 SUMMARY</code>', 'every headline figure on one screen'],
    ['<code>1 COMBINED</code>', f'the {f(N)} products used for analysis'],
    ['<code>2 GLOBAL skinsort only</code>', f'the global source alone, {f(len(g))} products'],
    ['<code>3 LEBANESE retail only</code>', f'the Lebanese source alone, {f(len(L))} products'],
    ['<code>4 STATISTICS</code>', 'every distribution on this page, as a sheet'],
    ['<code>5 REMOVED no review data</code>', 'the 595 rows dropped, so the decision is checkable']])}
</section>
"""

html = PORTAL.read_text(encoding='utf-8')
html = re.sub(r'<section class="section" id="cb-stats">.*?</section>', '', html, flags=re.S)
anchor = html.find('<!-- ============================================ HOME -->')
if anchor == -1:
    anchor = html.find('<section class="section" id="home">')
if anchor == -1:
    raise SystemExit('could not find where to insert, portal not changed')
html = html[:anchor] + PAGE + '\n\n' + html[anchor:]

if 'cb-stats' not in re.search(r'<nav class="nav">.*?</nav>', html, re.S).group(0):
    m = re.search(r'(<a data-s="cb-one">.*?</a>)', html)
    if m:
        html = (html[:m.end()] +
                '\n    <a data-s="cb-stats">C2. Every statistic</a>' +
                html[m.end():])
    else:
        nav = re.search(r'(\s*<div class="grp">overview</div>)', html)
        html = (html[:nav.start()] +
                '\n    <div class="grp">one dataset</div>\n'
                '    <a data-s="cb-stats">C2. Every statistic</a>' + nav.group(1) +
                html[nav.end():])

PORTAL.write_text(html, encoding='utf-8')

w = len(re.sub(r'<[^>]+>', ' ', re.search(
    r'<section class="section" id="cb-stats">(.*?)</section>', html, re.S).group(1)).split())
tables = re.search(r'<section class="section" id="cb-stats">(.*?)</section>',
                   html, re.S).group(1).count('<table>')
print('=' * 58)
print('  STATISTICS PAGE ADDED')
print('=' * 58)
print(f'  {w:,} words, {tables} tables')
print(f'  products {f(N)} | brands {f(c["brand"].nunique())} | '
      f'categories {c["product_type"].nunique()} | countries {c["country"].nunique()}')
print(f'  declared skin types {f(T12)} ({pc(T12, NGOT)} of filled)')
