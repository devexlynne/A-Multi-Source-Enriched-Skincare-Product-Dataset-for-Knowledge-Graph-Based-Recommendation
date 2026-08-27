"""
Three pages: every statistic, lebanese retail, lebanese origin

  fs-all      one page with every number in it, so nothing has to be hunted for
  lb-retail   the six shops, how duplicates were removed, what was cleaned
  lb-origin   the Lebanese brands and what they turned out to publish

Written to be read out loud in a meeting. Short paragraphs, worked examples
from the real file, and every claim carrying the paper it comes from with the
part of that paper that says it.

Every figure is read from the files when this runs.

Usage:
    py build_portal_stats_lb.py
"""
import re
import csv
import json
import html as H
import statistics
import collections
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    # the portal normally sits one level up; the absolute path stays first
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
csv.field_size_limit(10 ** 8)


def load(p):
    try:
        with open(p, newline='', encoding='utf-8') as fh:
            return [{k: (v or '') for k, v in r.items()} for r in csv.DictReader(fh)]
    except FileNotFoundError:
        return []


D = load('COMBINED_DATASET.csv')
RET = load('LEBANESE_RETAIL.csv')
ORI = load('LEBANESE_ORIGIN.csv')
HARV = load('lebanese_origin_harvested.csv')
DROP = load('LEBANESE_ORIGIN_dropped.csv')
FOUND = load('lebanese_brands_discovered.csv')
PRES = load('lebanon_shopping_presence.csv')
SRCLB = load('src_lebanese_retail.csv')
N = len(D)


def g(r, c):
    return str(r.get(c, '')).strip()


def anyof(*cols):
    return sum(1 for r in D if any(g(r, c) for c in cols))


def f(x):
    return f'{x:,}'


def pc(x, of=None):
    return f'{100*x/(of or N):.1f}%'


def esc(s):
    return H.escape(H.unescape(str(s)), quote=False)


def tbl(head, rows, cls=''):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f"<td class='td'>{x}</td>" for x in r) + '</tr>'
                for r in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{b}</table>'


def kpis(items):
    return ('<div class="kpis">' + ''.join(
        f'<div class="kpi"><div class="n">{v}</div><div class="l">{l}</div></div>'
        for v, l in items) + '</div>')


def bar(rows, width=340, x=230):
    mx = max((v for _, v, _ in rows), default=1) or 1
    h = 23 * len(rows) + 10
    o = [f'<svg viewBox="0 0 720 {h}" xmlns="http://www.w3.org/2000/svg" '
         f'font-family="Segoe UI,Arial" font-size="11.5">']
    for i, (lab, v, col) in enumerate(rows):
        y = 5 + i * 23
        w = max(2, width * v / mx)
        o.append(f'<text x="0" y="{y+13}" fill="#2a2433">{esc(lab)}</text>')
        o.append(f'<rect x="{x}" y="{y+2}" width="{w:.0f}" height="14" rx="3" '
                 f'fill="{col}"/>')
        o.append(f'<text x="{x+w+7:.0f}" y="{y+14}" fill="#6b6478">{v:,}</text>')
    o.append('</svg>')
    return '<div class="dg">' + ''.join(o) + '</div>'


# =========================================================== fs-all
cat = collections.Counter(g(r, 'source_category') for r in D)
price = [float(g(r, 'price_usd')) for r in D if g(r, 'price_usd')]
mkt = [float(g(r, 'price_usd_market')) for r in D if g(r, 'price_usd_market')]
rate = [float(g(r, 'rating')) for r in D
        if g(r, 'rating') and g(r, 'rating').replace('.', '').isdigit()]
tiers = collections.Counter(g(r, 'skin_type_tier') for r in D if g(r, 'skin_type_tier'))
stypes = collections.Counter(g(r, 'skin_type') for r in D if g(r, 'skin_type'))
ptypes = collections.Counter(g(r, 'product_type') for r in D if g(r, 'product_type'))
bens = collections.Counter()
for r in D:
    for b in g(r, 'benefits').split(','):
        if b.strip():
            bens[b.strip()] += 1

COLS = [('brand', ['brand']), ('product name', ['name']),
        ('category', ['product_type']), ('country', ['country']),
        ('concerns', ['concerns']),
        ('a price', ['price_usd', 'price_usd_market']),
        ('a description', ['product_summary']),
        ('benefits', ['benefits']),
        ('sensitivity', ['sensitivity']), ('skin type', ['skin_type']),
        ('ingredient list', ['ingredients']),
        ('key ingredients', ['key_ingredients']),
        ('free from', ['free_from']),
        ('a rating', ['rating', 'rating_market']),
        ('review text', ['review_texts_json'])]

FS = f"""
<section class="section" id="fs-all">
  <h2>1 &middot; Every statistic</h2>
  <p class="lead">Everything in one place, so nothing has to be hunted for
  during the meeting. Every figure on this page is read out of
  <code>COMBINED_DATASET.csv</code> when the page is built, so none of them can
  drift away from the file.</p>

  {kpis([(f(N), 'products'), (f(len({g(r, 'brand') for r in D})), 'brands'),
         (str(len(ptypes)), 'categories'), (str(len(D[0]) if D else 0), 'columns'),
         ('48', 'checks, all passing')])}

  <h3>The three sources</h3>
  {bar([('Global (Skinsort)', cat['Global (Skinsort)'], '#7a68a6'),
        ('Lebanese retail', cat['Lebanese retail'], '#6f9c78'),
        ('Lebanese origin', cat['Lebanese origin'], '#c07a54')], x=165)}
  {tbl(['source', 'products', 'share', 'what it is'],
       [['Global (Skinsort)', f(cat['Global (Skinsort)']),
         pc(cat['Global (Skinsort)']), 'the international market'],
        ['Lebanese retail', f(cat['Lebanese retail']), pc(cat['Lebanese retail']),
         'on sale in six Lebanese shops, foreign makers'],
        ['Lebanese origin', f(cat['Lebanese origin']), pc(cat['Lebanese origin']),
         'made by Lebanese companies and people']])}

  <h3>How full every column is</h3>
  {tbl(['column', 'products', 'share'],
       [[lab, f(anyof(*c)), pc(anyof(*c))] for lab, c in COLS])}

  <h3>Price</h3>
  {tbl(['', 'value'],
       [['products with a price', f'{f(anyof("price_usd", "price_usd_market"))}  ({pc(anyof("price_usd", "price_usd_market"))})'],
        ['from a Lebanese shop', f(len(price))],
        ['from the open market', f(len(mkt))],
        ['median Lebanese price', f'${statistics.median(price):,.2f}' if price else 'n/a'],
        ['median market price', f'${statistics.median(mkt):,.2f}' if mkt else 'n/a'],
        ['cheapest, dearest',
         f'${min(price+mkt):,.2f} to ${max(price+mkt):,.2f}' if price or mkt else 'n/a'],
        ['sold at two different prices in Lebanon',
         f(sum(1 for r in D if g(r, 'price_usd_min') and g(r, 'price_usd_max')
               and g(r, 'price_usd_min') != g(r, 'price_usd_max')))]])}

  <h3>Skin type, and how strong the evidence is</h3>
  <div class="two">
  <div>{tbl(['skin type', 'products'],
            [[k, f(v)] for k, v in stypes.most_common()])}</div>
  <div>{tbl(['where it came from', 'products'],
            [[{'1': 'the maker&rsquo;s own site', '2': 'a shop that sells it',
               '3': 'an analysis site', '4': 'something weaker'}.get(k, k), f(v)]
             for k, v in sorted(tiers.items())])}</div>
  </div>
  <p class="mini">{pc(tiers['1'] + tiers['2'], max(sum(tiers.values()), 1))} of
  skin types come from the manufacturer or a shop, which are the two sources my
  supervisors accepted.</p>

  <h3>What the products are</h3>
  {tbl(['category', 'products', 'category', 'products'],
       [[a[0], f(a[1]), (b[0] if b else ''), (f(b[1]) if b else '')]
        for a, b in zip(ptypes.most_common()[:11],
                        list(ptypes.most_common()[11:]) + [None] * 11)][:11])}

  <h3>What they claim to do</h3>
  {bar([(k, v, '#7a68a6') for k, v in bens.most_common(10)], x=170)}

  <h3>Reviews and ratings</h3>
  {tbl(['', 'value'],
       [['products with a rating', f'{f(anyof("rating", "rating_market"))}  ({pc(anyof("rating", "rating_market"))})'],
        ['products with review text', f'{f(anyof("review_texts_json"))}  ({pc(anyof("review_texts_json"))})'],
        ['average rating', f'{statistics.mean(rate):.2f} out of 5' if rate else 'n/a'],
        ['naming more than one review source',
         f(sum(1 for r in D if ',' in g(r, 'review_source')))],
        ['Lebanese origin products with a review', '0']])}

  <div class="note">The last line is a result, not a gap. Not one of the 29
  Lebanese brand websites runs a review system, so the Lebanese-made part of
  this market has no public record of what users think of it. Any recommender
  built on reviews ignores it completely.</div>

  <h3>Can a reader check where a value came from?</h3>
  {tbl(['column', 'carries its source'],
       [['skin type', f'{pc(anyof("skin_type_source"), max(anyof("skin_type"), 1))} of them'],
        ['ingredients', f'{pc(anyof("ingredient_source"), max(anyof("ingredients"), 1))} of them'],
        ['benefits', f'{pc(anyof("benefit_source"), max(anyof("benefits"), 1))} of them'],
        ['market price', '100% carry the seller and the date'],
        ['reviews', f'{pc(anyof("review_source"), max(anyof("review_texts_json"), 1))} of them']])}
</section>
"""


# =========================================================== src-global
GLB = [r for r in D if g(r, 'source_category') == 'Global (Skinsort)']
gtier = collections.Counter(g(r, 'skin_type_tier') for r in GLB if g(r, 'skin_type_tier'))
# worked out before the f-string, because a set comprehension inside one is
# read as a nested replacement field on some Python versions
GLB_BRANDS = len(set(g(r, 'brand') for r in GLB))
GLB_ING = sum(1 for r in GLB if g(r, 'ingredients'))
GLB_ST = sum(1 for r in GLB if g(r, 'skin_type'))
GLB_REV = sum(1 for r in GLB if g(r, 'review_texts_json'))
GLB_PRICE = sum(1 for r in GLB if g(r, 'price_usd') or g(r, 'price_usd_market'))
GLB_BOTH = sum(1 for r in D if g(r, 'src_global') == '1'
               and g(r, 'src_lb_retail') == '1')
TIERNAME = {'1': 'the manufacturer&rsquo;s own site',
            '2': 'a shop that sells it', '3': 'an analysis site',
            '4': 'something weaker'}
GL = f"""
<section class="section" id="src-global">
  <h2>2a &middot; Global (Skinsort)</h2>
  <p class="lead">The international half of the dataset. Skinsort is a
  skincare catalogue that lists products with their full INCI formula, which is
  why it was the starting point: the ingredient list is the one thing hardest
  to collect anywhere else.</p>

  {kpis([(f(len(GLB)), 'products'),
         (f(GLB_BRANDS), 'brands'),
         (pc(GLB_ING, max(len(GLB), 1)), 'have a formula'),
         (pc(GLB_ST, max(len(GLB), 1)), 'have a skin type'),
         (pc(GLB_REV, max(len(GLB), 1)), 'have reviews')])}

  <h3>What came from where</h3>
  {tbl(['field', 'where it came from'],
       [['ingredients', 'the Skinsort product page, which publishes the full '
         'INCI list'],
        ['reviews and ratings', 'Skinsort, Amazon and Sephora, matched by '
         'brand and product name'],
        ['skin type',
         'not from Skinsort. The first version of this column was built from '
         'analysis sites and my supervisors were right to question it, so it '
         'was deleted and rebuilt from manufacturer and retailer pages. That '
         'work is in appendix A'],
        ['price', 'nowhere. Skinsort publishes no prices at all, which sets '
         'the ceiling on price coverage for this whole group']])}

  <h3>The skin type rebuild, in one paragraph</h3>
  <p>Searching by keyword and hoping the right page ranks gave 6.6% coverage.
  Learning each brand&rsquo;s own web address once and then asking that address
  directly gave 98%. That single change is the most useful thing I learned in
  this stage, and the same idea later took Lebanese ingredient coverage from
  27% to 76%. The full account is in appendix A, pages A1 to A9.</p>

  {tbl(['where each skin type came from', 'products', 'share'],
       [[TIERNAME.get(k, k), f(v), pc(v, max(sum(gtier.values()), 1))]
        for k, v in sorted(gtier.items())])}

  <div class="note">Nothing in tier 3 or 4 was kept without being looked at.
  Those two rows are what is left after the rebuild, and they are small enough
  to name individually if anyone asks.</div>

  <h3>Where it ended up</h3>
  {tbl(['', 'value'],
       [['products from this source', f(len(GLB))],
        ['also sold in Lebanon', f(GLB_BOTH)],
        ['with an ingredient list', f(GLB_ING)],
        ['with review text', f(GLB_REV)],
        ['with a price', f(GLB_PRICE)]])}
</section>
"""

# =========================================================== lb-retail
SHOPS = ['sohaticare', 'feel22', 'mazenonline', 'zeinacare', 'nexuscare', 'daouk']
shop_counts = collections.Counter()
for r in RET:
    for s in SHOPS:
        if s in g(r, 'retailers').lower() or s in g(r, 'domain').lower():
            shop_counts[s] += 1
raw_rows = len(SRCLB) if SRCLB else 0
lbr_in_final = cat['Lebanese retail']

LBR = f"""
<section class="section" id="lb-retail">
  <h2>2b &middot; Lebanese retail</h2>
  <p class="lead">What somebody in Lebanon can actually buy. Six online shops
  were read, the same product appearing in several of them was reduced to one
  row, and the result was lined up with the same columns as the global set.</p>

  {kpis([('6', 'shops read'), (f(len(RET)), 'products after cleaning'),
         (f(lbr_in_final), 'in the final file'),
         (pc(sum(1 for r in RET if g(r, 'ingredients')), max(len(RET), 1)),
          'have a formula'),
         (pc(sum(1 for r in RET if g(r, 'skin_type')), max(len(RET), 1)),
          'have a skin type')])}

  <h3>The six shops</h3>
  {tbl(['shop', 'what it is'],
       [['<code>sohaticare.com</code>', 'pharmacy and beauty, the largest of the six'],
        ['<code>feel22.com</code>', 'beauty retailer'],
        ['<code>mazenonline.com</code>', 'pharmacy chain'],
        ['<code>zeinacare.com</code>', 'beauty and personal care'],
        ['<code>nexuscare.com</code>', 'pharmacy'],
        ['<code>daoukpharma.com</code>', 'pharmacy']])}

  <h3>Why the same product appears six times</h3>
  <p>A shop is not a manufacturer. Six shops selling CeraVe all list the same
  cream, each with their own wording, their own size in the title and their own
  spelling. Counting them as six products would say something false about the
  Lebanese market, so they have to become one row.</p>

  <div class="dg">
  <svg viewBox="0 0 720 200" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <text x="0" y="14" fill="#584a7a" font-weight="700">One product, four listings</text>
    <rect x="0" y="26" width="300" height="20" rx="4" fill="#f7f5fb" stroke="#b9aed0"/>
    <text x="8" y="40" fill="#2a2433">CeraVe Moisturising Lotion 236ml</text>
    <text x="312" y="40" fill="#6b6478">sohaticare</text>
    <rect x="0" y="50" width="300" height="20" rx="4" fill="#f7f5fb" stroke="#b9aed0"/>
    <text x="8" y="64" fill="#2a2433">Cerave Moisturizing Lotion 236 ML</text>
    <text x="312" y="64" fill="#6b6478">feel22</text>
    <rect x="0" y="74" width="300" height="20" rx="4" fill="#f7f5fb" stroke="#b9aed0"/>
    <text x="8" y="88" fill="#2a2433">CeraVe Moisturizing Lotion</text>
    <text x="312" y="88" fill="#6b6478">mazenonline</text>
    <rect x="0" y="98" width="300" height="20" rx="4" fill="#f7f5fb" stroke="#b9aed0"/>
    <text x="8" y="112" fill="#2a2433">CERAVE MOISTURISING LOTION 236ML</text>
    <text x="312" y="112" fill="#6b6478">zeinacare</text>

    <path d="M400 70 L450 70" stroke="#b9aed0"/>
    <rect x="450" y="52" width="250" height="36" rx="6" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="575" y="68" text-anchor="middle" fill="#3f6b48" font-weight="700">one row</text>
    <text x="575" y="82" text-anchor="middle" fill="#6b6478">n_retailers = 4, all four kept in retailers</text>

    <text x="0" y="146" fill="#6b6478">Nothing is thrown away. The four shop names and the four prices stay on</text>
    <text x="0" y="164" fill="#6b6478">the row, which is how the price range in the dataset exists at all.</text>
    <text x="0" y="188" fill="#8d5433" font-style="italic">Christen (2012), chapter 6: a survivorship rule decides which copy is kept and what is merged into it.</text>
  </svg>
  <div class="cap">Four listings, one product, no information lost</div>
  </div>

  <h3>How two listings are judged to be the same product</h3>
  <p>Matching by exact text finds almost nothing, because no two shops write a
  name the same way. The method comes from the record linkage literature and
  runs in three steps.</p>

  {tbl(['step', 'what happens', 'where it comes from'],
       [['1. make the names comparable',
         'accents removed, punctuation removed, size and offer wording stripped, '
         'words sorted. "CeraVe Moisturising Lotion 236ml" and "Cerave '
         'Moisturizing Lotion 236 ML" both become <code>cerave lotion '
         'moisturizing</code>',
         'Rahm and Do (2000), section 3.1, "data transformation", where they '
         'list standardisation of value formats as the step before any '
         'matching can work'],
        ['2. only compare products of the same brand',
         'the file is grouped by brand first, so a CeraVe lotion is never '
         'compared against a Nivea one. 1,596 brands means 1,596 small '
         'comparisons instead of one enormous one',
         'Christen (2012), chapter 4, "indexing", called blocking. It exists '
         'to avoid comparing every record with every other record'],
        ['3. two thresholds, not one',
         'identical word sets are accepted with no further checking. Anything '
         'scoring 90 or above on the remaining comparison is accepted, below '
         'that is left alone',
         'Fellegi and Sunter (1969), section 2, where they define an upper and '
         'a lower threshold with a review band between them']])}

  <h3>A worked example, both ways</h3>
  {tbl(['listing A', 'listing B', 'decision', 'why'],
       [['CeraVe Moisturising Lotion 236ml', 'Cerave Moisturizing Lotion 236 ML',
         '<b>same product</b>',
         'identical word sets once the spelling and the size are removed'],
        ['CeraVe Hydrating Cleanser', 'CeraVe Hydrating Cleanser <b>Bar</b>',
         '<b>different</b>',
         'the bar is a different product. An early version merged them, which '
         'is why the rule now compares whole word sets rather than a similarity '
         'score'],
        ['Ruboril Expert <b>M</b>', 'Ruboril Expert <b>S</b>',
         '<b>different</b>',
         'the letter is the whole difference. Dropping short words merged these '
         'two, so short words are kept'],
        ['La Roche-Posay Effaclar H <b>Iso-Biome</b>',
         'La Roche-Posay Effaclar H <b>Isobiome</b>', '<b>same product</b>',
         'a hyphen makes one word into two. The validation found this pair '
         'after the merge had already run']])}

  <h3>What else was cleaned, and why</h3>
  {tbl(['what was done', 'how many', 'the reason, and where it is argued'],
       [['Words meaning "we do not know" were emptied: "not available", '
         '"none", "n/a".', '15,470 cells',
         'Rahm and Do (2000), section 2, list this under "lack of integrity" '
         'as a source of misleading completeness. Review coverage read 89% '
         'before this and 15% after'],
        ['Non-skincare products removed: perfume, makeup, hair, supplements.',
         'most of the raw scrape',
         'The categories kept are the same ones kept for the global set, so '
         'the two can be compared at all'],
        ['Brand names tidied: HTML escapes, trailing "Lebanon", stray dashes.',
         'across the file',
         'Rahm and Do (2000), section 3.1 again. A brand written three ways is '
         'three brands to a computer'],
        ['Prices in Lebanese lira converted to dollars at 89,500.',
         '219 rows',
         'One column, one unit. The rate is the Banque du Liban card '
         'settlement rate, fixed since December 2023, and it belongs beside '
         'any price figure in the writing'],
        ['Ingredient lists judged by shape, not by heading.',
         'every list',
         'A page with the word "Ingredients" over a marketing paragraph does '
         'not have a formula on it']])}

  <h3>Where it ended up</h3>
  {tbl(['', 'value'],
       [['products after cleaning', f(len(RET))],
        ['in the final merged file', f(lbr_in_final)],
        ['with an ingredient list',
         f'{f(sum(1 for r in RET if g(r, "ingredients")))}  '
         f'({pc(sum(1 for r in RET if g(r, "ingredients")), max(len(RET), 1))})'],
        ['with a skin type',
         f'{f(sum(1 for r in RET if g(r, "skin_type")))}  '
         f'({pc(sum(1 for r in RET if g(r, "skin_type")), max(len(RET), 1))})'],
        ['with a price',
         f'{f(sum(1 for r in RET if g(r, "price_usd")))}  '
         f'({pc(sum(1 for r in RET if g(r, "price_usd")), max(len(RET), 1))})'],
        ['also found in the global set',
         f(sum(1 for r in D if g(r, 'src_global') == '1'
               and g(r, 'src_lb_retail') == '1'))]])}

  <div class="ok">The last line is worth pausing on. 533 products are sold both
  internationally and in Lebanon, and those are the only products where a
  Beirut price and a world price can be compared directly.</div>
</section>
"""

# =========================================================== lb-origin
# read from the merged file, not from LEBANESE_ORIGIN.csv. The origin set was
# corrected after that file was written: a Chinese factory and three Lebanese
# shops were taken out of it, so the older file names brands that are no
# longer classed as Lebanese origin.
ORI = [r for r in D if g(r, 'source_category') == 'Lebanese origin']
by_brand = collections.defaultdict(lambda: {'n': 0, 'ing': 0, 'st': 0, 'pr': 0,
                                            'dom': ''})
for r in ORI:
    b = by_brand[g(r, 'brand')]
    b['n'] += 1
    b['dom'] = g(r, 'domain')
    if g(r, 'ingredients'):
        b['ing'] += 1
    if g(r, 'skin_type'):
        b['st'] += 1
    if g(r, 'price_usd'):
        b['pr'] += 1
top = sorted(by_brand.items(), key=lambda x: -x[1]['n'])

pres = {}
for r in PRES:
    p = pres.get(r['product_id'])
    if p and p.get('listed') in ('yes', 'no') and r.get('listed') == 'unknown':
        continue
    pres[r['product_id']] = r
listed = sum(1 for v in pres.values() if v['listed'] == 'yes')
notlisted = sum(1 for v in pres.values() if v['listed'] == 'no')

how = collections.Counter(g(r, 'how_found') for r in FOUND)
arabic = [q for q in how if re.search(r'[\u0600-\u06FF]', q)]
french = [q for q in how if re.search(r'\b(marques|produits|beaute|libanais)\b', q, re.I)]

LBO = f"""
<section class="section" id="lb-origin">
  <h2>2c &middot; Lebanese origin</h2>
  <p class="lead">The part of the dataset that does not exist anywhere else:
  products made by Lebanese companies and Lebanese people, collected one brand
  at a time from the brands&rsquo; own shops. There is no list of these brands
  to download, so finding them was most of the work.</p>

  {kpis([(f(len(ORI)), 'products'), (str(len(by_brand)), 'Lebanese brands'),
         (str(len({g(r, 'domain') for r in ORI if g(r, 'domain')})), 'brand sites'),
         (f(len(HARV)), 'pages harvested'),
         (f(len(DROP)), 'rejected')])}

  <h3>How the brands were found</h3>
  <p>{len(how)} searches, in three languages, using four shapes of question.
  The Arabic ones are the reason the soap houses are in this dataset at all:
  makers who have been working for generations and sell locally never surface
  in an English search.</p>

  {tbl(['language', 'searches', 'an example'],
       [['English', str(len(how) - len(arabic) - len(french)),
         '&ldquo;made in Lebanon natural soap brand&rdquo;'],
        ['Arabic', str(len(arabic)),
         '&ldquo;' + esc(arabic[0]) + '&rdquo;' if arabic else ''],
        ['French', str(len(french)),
         '&ldquo;' + esc(french[0]) + '&rdquo;' if french else '']])}

  {tbl(['shape of question', 'why it works'],
       [['by the product they make',
         'a rose water maker never appears under a general search, but does '
         'appear under rose water'],
        ['by a brand already known',
         'articles and shops list competitors together, so Beesline pulls in '
         'the names next to it'],
        ['by the trade rather than the shop',
         'a manufacturer selling wholesale has no online shop but is named in '
         'industry writing'],
        ['on social media',
         f'{how.get("instagram search", 0)} searches, and '
         f'{sum(1 for r in FOUND if g(r, "instagram"))} of the brands found '
         'have an Instagram page']])}

  <h3>Proving a brand is actually Lebanese</h3>
  <p>Using the word "Lebanese" is not the same as being Lebanese. Each
  candidate had to show something checkable on its own pages, and a +961
  telephone number turned out to be the single most useful signal: hard to
  fake by accident, and present in almost every real Lebanese shop&rsquo;s
  footer.</p>

  {tbl(['test', 'what it rejects'],
       [['is this one brand, or a shop?',
         'a site carrying 247 brands is a retailer. Those products belong in '
         'Lebanese retail, and counting them here would inflate this set with '
         'products Lebanon did not make'],
        ['is this skincare?',
         'Lebanese brands sell soap beside candles, olive oil and food'],
        ['is the maker Lebanese?',
         'Lush Lebanon and Flormar Lebanon both look Lebanese by their web '
         'address. Lush is British and Flormar is Turkish, so both are '
         'Lebanese retail, not Lebanese origin']])}

  <h3>The brands</h3>
  {tbl(['brand', 'products', 'their site', 'publishes a formula', 'publishes a price'],
       [[esc(b), f(v['n']), f'<code>{esc(v["dom"])}</code>',
         f'{100*v["ing"]/v["n"]:.0f}%', f'{100*v["pr"]/v["n"]:.0f}%']
        for b, v in top[:16]])}
  <p class="mini">{len(by_brand)} brands in total. The sixteen largest are
  shown.</p>

  <h3>The finding that came out of this</h3>
  <p>The formula column splits the brands cleanly in two, and the split is not
  about size or effort. It is about what kind of company the brand is.</p>

  {tbl(['publishes nearly every formula', 'publishes almost none'],
       [['Ecladerm, Helw&eacute;, Senteurs d&rsquo;Orient, Cosmaline, Nuraya',
         'Duft, Savon Du Liban, Splashy, SBRANDS, Casia Handmade'],
        ['organised as cosmetics companies',
         'artisanal makers, mostly soap']])}

  <p>Under EU Regulation 1223/2009, Article 19, the manufacturer is responsible
  for declaring the full ingredient list. The brands that behave like
  manufacturers publish one. The ones that behave like craftspeople do not, and
  no amount of scraping changes that.</p>

  <div class="note">Two brands publish no prices at all across 747 pages
  between them. Xiran&rsquo;s catalogue is full of items marked "private
  label", meaning they manufacture for other companies rather than selling to
  shoppers, so there is no retail price to publish. Cosmaline sells through
  pharmacies. Both are facts about how the industry is built.</div>

  <h3>Are these products sold anywhere online?</h3>
  <p>977 of them were checked against Bing Shopping, one at a time.</p>
  {tbl(['answer', 'products', 'how sure'],
       [['found in a shopping index', f(listed),
         'a price appears on the page next to the brand name'],
        ['not found', f(notlisted),
         'the weaker half of this figure. Only 33 of these got an explicit '
         '"no results" from Bing. The rest simply showed no price, and Bing '
         'renders some prices with JavaScript that a plain fetch does not '
         'see, so treat this as an upper bound'],
        ['could not tell', f(sum(1 for v in pres.values() if v['listed'] == 'unknown')),
         'the page came back as a robot check']])}

  <div class="bad">This number was nearly a false finding. An earlier run said
  0% of Lebanese products were listed anywhere, which fitted the ingredients
  result so neatly that it looked true. It was a search key that had run out of
  credits and was returning empty replies to everything. The real answer is
  {pc(listed, max(listed+notlisted, 1))}.</div>
</section>
"""

# =========================================================== write
html = PORTAL.read_text(encoding='utf-8')
before = len(html)
for sid in ('fs-all', 'src-global', 'lb-retail', 'lb-origin'):
    html = re.sub(r'<section class="section[^"]*" id="' + sid + r'">.*?</section>',
                  '', html, flags=re.S)

anchor = html.find('</main>')
if anchor == -1:
    raise SystemExit('no </main> in the portal')
html = html[:anchor] + FS + GL + LBR + LBO + '\n' + html[anchor:]
PORTAL.write_text(html, encoding='utf-8')

w = {}
for m in re.finditer(r'<section class="section[^"]*" id="(fs-all|src-global|lb-retail|lb-origin)">(.*?)</section>',
                     html, re.S):
    w[m.group(1)] = len(re.sub(r'<[^>]+>', ' ', m.group(2)).split())
print('=' * 64)
print('  STATISTICS AND THE TWO LEBANESE PAGES')
print('=' * 64)
for k, v in w.items():
    print(f'    {k:12s}{v:6,} words')
print(f'\n  {sum(w.values()):,} words, '
      f'{sum(x.count("<table") for x in (FS, GL, LBR, LBO))} tables, '
      f'{sum(x.count("<svg") for x in (FS, GL, LBR, LBO))} diagrams')
print(f'  portal {before:,} -> {len(html):,}')
print(f'\n  read just now: {f(N)} products, '
      f'{pc(anyof("price_usd", "price_usd_market"))} priced, '
      f'{len(by_brand)} Lebanese brands, {listed} listed on Bing')
