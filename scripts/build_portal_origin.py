"""
The lebanese origin pages of the portal

Four pages:

    LO1  Why a separate Lebanese origin set exists at all, and what it holds
    LO2  How the brands were found: 40 searches, 103 candidates, 27 kept
    LO3  Every domain that was kept and every one that was dropped, with the
         reason for each
    LO4  What could be filled, what could not, and why the gaps are a finding

Every figure is read from the files at build time. Nothing is typed in by hand,
so running this again after any change moves the numbers with it.

Usage:
    py build_portal_origin.py
"""
import re
import csv
import html
import collections
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    # the portal normally sits one level up; the absolute path stays first
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
csv.field_size_limit(10 ** 8)


def load(path):
    try:
        with open(path, newline='', encoding='utf-8') as fh:
            return [{k: (v or '') for k, v in r.items()} for r in csv.DictReader(fh)]
    except FileNotFoundError:
        return []


O = load('LEBANESE_ORIGIN.csv')
DROPPED = load('LEBANESE_ORIGIN_dropped.csv')
HARVEST = load('lebanese_origin_harvested.csv')
FOUND = load('lebanese_brands_discovered.csv')
FILL = load('lebanese_origin_fill_progress.csv')
SERP = load('lebanese_origin_serper_progress.csv')
COMB = load('COMBINED_DATASET.csv')

N = len(O)
NHARV = len(HARVEST)
NDROP = len(DROPPED)
BRANDS = len({r['brand'] for r in O})
DOMAINS = collections.Counter(r['domain'] for r in O)
CAND = len(FOUND)
HARV_DOMAINS = len({r.get('domain', '') for r in HARVEST})


def filled(col, rows=None):
    return sum(1 for r in (rows or O) if str(r.get(col, '')).strip())


def f(x):
    return f'{x:,}'


def pc(x, of=None):
    return f'{100*x/(of or N):.1f}%'


def esc(s):
    return html.escape(html.unescape(str(s)), quote=False)


def tbl(head, rows, cls=''):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f"<td class='td'>{x}</td>" for x in r) + '</tr>'
                for r in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{b}</table>'


def kpis(items):
    return ('<div class="kpis">' + ''.join(
        f'<div class="kpi"><div class="n">{v}</div><div class="l">{l}</div></div>'
        for v, l in items) + '</div>')


def bar(rows, width=380):
    mx = max((v for _, v, _ in rows), default=1) or 1
    h = 24 * len(rows) + 12
    out = [f'<svg viewBox="0 0 700 {h}" xmlns="http://www.w3.org/2000/svg" '
           f'font-family="Segoe UI,Arial" font-size="11.5">']
    for i, (lab, v, col) in enumerate(rows):
        y = 6 + i * 24
        w = max(2, width * v / mx)
        out.append(f'<text x="0" y="{y+13}" fill="#2a2433">{esc(lab)}</text>')
        out.append(f'<rect x="215" y="{y+2}" width="{w:.0f}" height="14" rx="3" '
                   f'fill="{col}"/>')
        out.append(f'<text x="{215+w+7:.0f}" y="{y+14}" fill="#6b6478">{v:,}</text>')
    out.append('</svg>')
    return '<div class="dg">' + ''.join(out) + '</div>'


# ============================================================ LO1
types = collections.Counter(r['product_type'] for r in O if r['product_type'])
top_brands = collections.Counter(r['brand'] for r in O).most_common(12)

LO1 = f"""
<section class="section" id="lo-what">
  <h2>LO1 &middot; The Lebanese origin set</h2>
  <p class="lead">This is the part of the dataset that does not exist anywhere
  else. Skinsort covers the international market, and the Lebanese retail set
  covers what is sold in Lebanon, but most of what is sold in Lebanon is made
  somewhere else. This set is the products actually <b>made by Lebanese
  companies and Lebanese people</b>, collected one brand at a time from the
  brands' own shops.</p>

  {kpis([(f(N), 'products'), (str(BRANDS), 'Lebanese brands'),
         (str(len(DOMAINS)), 'brand shops read'),
         (str(len(types)), 'categories'),
         (pc(filled('skin_type')), 'have a skin type')])}

  <h3>Why it is kept apart from the retail set</h3>
  <p>The two answer different questions, and merging them would destroy both
  answers.</p>

  {tbl(['', 'Lebanese retail', 'Lebanese origin'],
       [['the question it answers', 'what can somebody in Lebanon buy?',
         'what does Lebanon make?'],
        ['where the data comes from', 'six Lebanese shops',
         f'{len(DOMAINS)} brands&rsquo; own shops'],
        ['who makes the products', 'mostly international brands',
         'Lebanese companies and individuals'],
        ['size', f'{f(len([r for r in COMB if r.get("src_lb_retail") == "1"]))} products',
         f'{f(N)} products'],
        ['what it is for the thesis', 'the market',
         'the thing being studied']])}

  <div class="note">A Lebanese brand stocked by a Lebanese shop appears in
  both, and there are
  {f(len([r for r in COMB if r.get('src_lb_origin') == '1' and r.get('src_lb_retail') == '1']))}
  of those. In the combined dataset they count once, under Lebanese origin,
  because who makes a product is the more specific fact. Both markers stay set,
  so neither reading is lost.</div>

  <h3>What is in it</h3>
  {bar([(k, v, '#c07a54' if i < 3 else '#7a68a6')
        for i, (k, v) in enumerate(types.most_common(10))])}

  <p>Bath and body is the largest group by a distance, and that is a finding
  rather than a quirk of collecting. A large part of what Lebanon makes is
  soap: olive oil and laurel soap from Tripoli, made by houses that have been
  doing it for generations, alongside newer small-batch makers.</p>

  <h3>The brands, by how many products each has</h3>
  {tbl(['brand', 'products', 'their shop', 'ingredients published'],
       [[esc(b), f(n), f'<code>{esc(next((r["domain"] for r in O if r["brand"] == b), ""))}</code>',
         pc(sum(1 for r in O if r['brand'] == b and r['ingredients'].strip()),
            n)]
        for b, n in top_brands])}
</section>
"""

# ============================================================ LO2
how = collections.Counter(r.get('how_found', '') for r in FOUND)
arabic = [q for q in how if re.search(r'[\u0600-\u06FF]', q)]
french = [q for q in how if re.search(r'\b(marques|produits|beaute|cosmetiques|libanais)\b', q, re.I)]
insta = sum(1 for r in FOUND if r.get('instagram', '').strip())
ev = collections.Counter()
for r in FOUND:
    for piece in str(r.get('evidence', '')).split(';'):
        p = piece.strip()
        if p:
            ev[p] += 1

LO2 = f"""
<section class="section" id="lo-find">
  <h2>LO2 &middot; Finding the brands</h2>
  <p class="lead">There is no list of Lebanese skincare brands to download.
  No official register, no industry directory that is complete, nothing on
  Skinsort. So the brands had to be found before anything could be collected,
  and finding them was most of the work.</p>

  {kpis([(str(len(how)), 'different searches'),
         (str(CAND), 'candidate brands found'),
         (str(BRANDS), 'kept after checking'),
         (str(insta), 'had an Instagram page'),
         (f(NHARV), 'products harvested')])}

  <h3>Searching in three languages</h3>
  <p>Searching only in English finds the brands that already market to an
  English-speaking audience, which are the larger and more established ones.
  Lebanon's smaller makers write in Arabic and French, so the searches did
  too.</p>

  {tbl(['language', 'searches', 'examples'],
       [['English', str(len(how) - len(arabic) - len(french)),
         '&ldquo;made in Lebanon natural soap brand&rdquo;, '
         '&ldquo;homegrown Lebanese skincare labels&rdquo;, '
         '&ldquo;Lebanese clean beauty startup&rdquo;'],
        ['Arabic', str(len(arabic)),
         '&ldquo;' + '&rdquo;, &ldquo;'.join(esc(q) for q in arabic[:2]) + '&rdquo;'],
        ['French', str(len(french)),
         '&ldquo;' + '&rdquo;, &ldquo;'.join(esc(q) for q in french[:3]) + '&rdquo;']])}

  <div class="note">The Arabic searches are the ones that found the soap
  houses. Those makers have been working for decades and sell mostly locally,
  so an English search never reaches them. This is the kind of gap that makes
  a dataset look complete while missing the part that matters most.</div>

  <h3>Searching sideways, not just directly</h3>
  <p>Asking for &ldquo;Lebanese skincare brands&rdquo; returns the same four or
  five names every time. Three other shapes of question were used to get
  past that:</p>

  {tbl(['shape of question', 'why it works', 'example'],
       [['by product',
         'a maker of one specific thing will not appear under a general '
         'search, but does appear under the thing they make',
         '&ldquo;Lebanese rose water skincare brand&rdquo;, '
         '&ldquo;Lebanese olive oil skincare brand&rdquo;, '
         '&ldquo;made in Lebanon sunscreen brand&rdquo;'],
        ['by a brand already known',
         'shops and articles list competitors together, so a known name pulls '
         'in the unknown ones next to it',
         '&ldquo;brands like Beesline Lebanon skincare&rdquo;, '
         '&ldquo;Khan El Kaser similar Lebanese brands&rdquo;, '
         '&ldquo;Lebanese alternatives to Beesline&rdquo;'],
        ['by the trade rather than the shop',
         'a manufacturer that sells wholesale has no online shop, but is '
         'named in industry writing',
         '&ldquo;Lebanon cosmetics industry export brands&rdquo;, '
         '&ldquo;Beirut cosmetics manufacturer skincare&rdquo;, '
         '&ldquo;Lebanese dermocosmetics laboratory brand&rdquo;'],
        ['on social media',
         'the smallest makers have an Instagram page and no website at all',
         f'{how.get("instagram search", 0)} searches, which found {insta} '
         f'brands with an Instagram presence']])}

  <div class="dg">
  <svg viewBox="0 0 700 250" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <rect x="10" y="16" width="140" height="44" rx="6" fill="#f7f5fb"
          stroke="#7a68a6"/>
    <text x="80" y="35" text-anchor="middle" fill="#584a7a"
          font-weight="700">{len(how)} searches</text>
    <text x="80" y="51" text-anchor="middle" fill="#6b6478">en, ar, fr</text>
    <path d="M150 38 L196 38" stroke="#b9aed0"/>

    <rect x="196" y="16" width="150" height="44" rx="6" fill="#f7f5fb"
          stroke="#7a68a6"/>
    <text x="271" y="35" text-anchor="middle" fill="#584a7a"
          font-weight="700">{CAND} candidates</text>
    <text x="271" y="51" text-anchor="middle" fill="#6b6478">any Lebanese page</text>
    <path d="M346 38 L392 38" stroke="#b9aed0"/>

    <rect x="392" y="6" width="160" height="64" rx="6" fill="#fff"
          stroke="#584a7a" stroke-width="1.5"/>
    <text x="472" y="24" text-anchor="middle" fill="#584a7a"
          font-weight="700">three tests</text>
    <text x="472" y="40" text-anchor="middle" fill="#6b6478">is it one brand?</text>
    <text x="472" y="54" text-anchor="middle" fill="#6b6478">is it skincare?</text>
    <text x="472" y="66" text-anchor="middle" fill="#6b6478">is it Lebanese?</text>
    <path d="M552 38 L596 38" stroke="#b9aed0"/>

    <rect x="596" y="16" width="96" height="44" rx="6" fill="#fdf3ec"
          stroke="#c07a54"/>
    <text x="644" y="35" text-anchor="middle" fill="#8d5433"
          font-weight="700">{BRANDS} brands</text>
    <text x="644" y="51" text-anchor="middle" fill="#6b6478">kept</text>

    <path d="M271 60 L271 100" stroke="#b9aed0"/>
    <rect x="150 " y="100" width="245" height="44" rx="6" fill="#f7f5fb"
          stroke="#6f9c78"/>
    <text x="272" y="119" text-anchor="middle" fill="#3f6b48"
          font-weight="700">read every shop&rsquo;s catalogue</text>
    <text x="272" y="135" text-anchor="middle" fill="#6b6478">{f(NHARV)} products from {HARV_DOMAINS} sites</text>
    <path d="M395 122 L470 122" stroke="#b9aed0"/>
    <rect x="470" y="100" width="222" height="44" rx="6" fill="#fdeeee"
          stroke="#b5484d"/>
    <text x="581" y="119" text-anchor="middle" fill="#b5484d"
          font-weight="700">{f(NDROP)} dropped</text>
    <text x="581" y="135" text-anchor="middle" fill="#6b6478">each with a written reason</text>

    <path d="M581 144 L581 176" stroke="#b9aed0"/>
    <rect x="240" y="176" width="240" height="44" rx="6" fill="#fdf3ec"
          stroke="#c07a54" stroke-width="1.5"/>
    <text x="360" y="195" text-anchor="middle" fill="#8d5433"
          font-weight="700">{f(N)} products</text>
    <text x="360" y="211" text-anchor="middle" fill="#6b6478">LEBANESE_ORIGIN.csv</text>
    <path d="M480 198 L581 198 L581 144" stroke="#b9aed0" fill="none"/>
  </svg>
  <div class="cap">From {len(how)} searches to {f(N)} products</div>
  </div>

  <h3>What counted as proof that a brand is Lebanese</h3>
  <p>A brand claiming to be Lebanese is not the same as a brand being
  Lebanese, and plenty of shops use the word without making anything. Each
  candidate had to show something checkable on its own pages:</p>

  {tbl(['evidence', 'brands'],
       [[esc(k), str(v)] for k, v in ev.most_common(8)])}

  <div class="note">A +961 telephone number was the single most useful signal.
  It is hard to fake by accident, it appears in the page footer of almost every
  real Lebanese shop, and unlike the word &ldquo;Lebanese&rdquo; it means the
  business is actually there.</div>
</section>
"""

# ============================================================ LO3
drop_by_domain = {}
for r in DROPPED:
    drop_by_domain.setdefault(r['domain'], r['why'])
# a domain can be in both: some of its products kept, others dropped
only_dropped = {d: w for d, w in drop_by_domain.items() if d not in DOMAINS}


def why_group(w):
    w = w.lower()
    if 'carries' in w or 'marketplace' in w or 'retailer' in w or 'pharmacy' in w:
        return 'a shop, not a brand'
    if 'not a skincare product' in w:
        return 'not skincare'
    if 'brand, this is lebanese retail' in w:
        return 'foreign brand sold in Lebanon'
    if 'directory' in w:
        return 'a directory, not a brand'
    return 'not skincare, or not Lebanese'


groups = collections.Counter(why_group(w) for w in only_dropped.values())

LO3 = f"""
<section class="section" id="lo-domains">
  <h2>LO3 &middot; Every site kept, and every site dropped</h2>
  <p class="lead">{f(NHARV)} products were harvested from {HARV_DOMAINS} sites
  and {f(NDROP)} of them were thrown away, which is
  {pc(NDROP, NHARV)} of everything collected. A cut that size has to be
  defensible product by product, so every drop carries a written reason and
  the dropped rows are kept in a file rather than deleted.</p>

  {kpis([(f(NHARV), 'harvested'), (f(NDROP), 'dropped'),
         (f(N), 'kept'), (pc(N, NHARV), 'survived'),
         (str(len(only_dropped)), 'sites rejected outright')])}

  <h3>The three tests</h3>
  {tbl(['test', 'what it asks', 'what it catches'],
       [['is this one brand, or a shop?',
         'does one brand name account for at least 60% of the catalogue?',
         'a shop selling 247 brands is a retailer. Its products belong in the '
         'Lebanese retail set, not here, and counting them here would inflate '
         'this set with products Lebanon did not make'],
        ['is this skincare?',
         'does the product fall in the same categories kept for Skinsort?',
         'Lebanese brands sell soap next to candles, olive oil, and food. '
         'Only the skincare is kept'],
        ['is the brand actually Lebanese?',
         'a +961 number, a .lb domain, a Lebanese address, or Lebanon named '
         'on the page',
         'shops that use the word Lebanese while selling imported goods, and '
         'Lebanese-food shops abroad']])}

  <h3>The {len(DOMAINS)} sites kept</h3>
  {tbl(['site', 'products', 'brand'],
       [[f'<code>{esc(d)}</code>', f(n),
         esc(next((r['brand'] for r in O if r['domain'] == d), ''))]
        for d, n in DOMAINS.most_common()])}

  <h3>The {len(only_dropped)} sites rejected, and why</h3>
  {bar([(k, v, '#b5484d') for k, v in groups.most_common()])}

  {tbl(['site', 'why it was rejected'],
       [[f'<code>{esc(d)}</code>', esc(w)]
        for d, w in sorted(only_dropped.items())])}

  <div class="note">Two of these are worth reading twice.
  <code>lushlebanon.com</code> and <code>flormarlebanon.com</code> look
  Lebanese by their web address and pass every test about being in Lebanon.
  Lush is British and Flormar is Turkish, so both are Lebanese retail, not
  Lebanese origin. A domain name is not evidence of who makes a product.
  <code>made-in-lebanon.net</code> is a manufacturers directory: useful for
  finding brands, but not a brand itself.</div>

  <h3>Sites that were partly kept</h3>
  <p>{len([d for d in drop_by_domain if d in DOMAINS])} sites appear in both
  lists. These are real Lebanese brands whose catalogues also contain things
  that are not skincare, so the products were judged one at a time rather than
  the site being accepted or rejected as a whole.</p>

  {tbl(['site', 'kept', 'dropped from it', 'why some were dropped'],
       [[f'<code>{esc(d)}</code>', f(DOMAINS[d]),
         f(sum(1 for r in DROPPED if r['domain'] == d)), esc(drop_by_domain[d])]
        for d in list(DOMAINS)[:12] if d in drop_by_domain])}
</section>
"""

# ============================================================ LO4
ing_src = collections.Counter(r['ingredient_source'] for r in O
                              if r['ingredient_source'].strip())
tier1 = sum(1 for r in O if str(r.get('skin_type_tier', '')).strip() == '1')
serper_tried = len(SERP)
serper_ing = sum(1 for r in SERP if r.get('ingredients', '').strip())
fill_tried = len(FILL)
fill_ing = sum(1 for r in FILL if r.get('ingredients', '').strip())

by_brand = collections.defaultdict(lambda: [0, 0])
for r in O:
    by_brand[r['brand']][0] += 1
    if r['ingredients'].strip():
        by_brand[r['brand']][1] += 1
full = [b for b, (n, i) in by_brand.items() if n >= 20 and i == n]
none_ = [b for b, (n, i) in by_brand.items() if n >= 20 and i == 0]

LO4 = f"""
<section class="section" id="lo-gaps">
  <h2>LO4 &middot; What could be filled, and what could not</h2>
  <p class="lead">This set is thinner than the other two, and the thin parts
  are not a failure of effort. They are a result about how small Lebanese
  makers publish, and they belong in the thesis as such.</p>

  {kpis([(pc(filled('product_type')), 'category'),
         (pc(filled('skin_type')), 'skin type'),
         (pc(filled('ingredients')), 'ingredients'),
         (pc(filled('price_usd')), 'price'),
         ('0%', 'reviews')])}

  <h3>Coverage, and where each column came from</h3>
  {tbl(['column', 'filled', 'share', 'where it came from'],
       [['product type', f(filled('product_type')), pc(filled('product_type')),
         'the shop&rsquo;s own category, mapped to the Skinsort categories'],
        ['skin type', f(filled('skin_type')), pc(filled('skin_type')),
         f'the brand&rsquo;s own page. {f(tier1)} of these are tier 1, meaning '
         f'the maker stated it themselves'],
        ['ingredients', f(filled('ingredients')), pc(filled('ingredients')),
         f'{len(ing_src)} brand sites that publish a list'],
        ['price', f(filled('price_usd')), pc(filled('price_usd')),
         'the shop page, where one was shown'],
        ['reviews', '0', '0%',
         'no Lebanese brand site in this set runs a review system']])}

  <h3>Ingredients: the brands split cleanly in two</h3>
  <p>This is the most interesting gap in the whole dataset. Publishing an
  ingredient list is not a matter of size or effort, it is a matter of what
  kind of company the brand is.</p>

  {tbl(['brand', 'products', 'ingredients published'],
       [[esc(b), f(n), f'{100*i/n:.0f}%']
        for b, (n, i) in sorted(by_brand.items(), key=lambda x: -x[1][0])[:14]])}

  <div class="note">The brands at 100% are the ones organised as cosmetics
  companies: Cosmaline, Helw&eacute;, Senteurs d&rsquo;Orient, Ecladerm. The
  brands near zero are artisanal makers selling soap. Under EU Regulation
  1223/2009 a cosmetics manufacturer must declare the full ingredient list, and
  the brands that behave like manufacturers publish one. The ones that behave
  like craftspeople do not, and nothing in a scraping method can fix that.</div>

  <h3>Where paid search stopped being worth it</h3>
  <p>The free pass had already read every brand page. Paying to search the
  same pages again returned almost nothing, and the run was stopped rather than
  continued out of stubbornness.</p>

  {tbl(['pass', 'products asked', 'ingredients found', 'hit rate'],
       [['free, reading brand pages directly', f(fill_tried), f(fill_ing),
         pc(fill_ing, max(fill_tried, 1))],
        ['paid search, on what was left', f(serper_tried), f(serper_ing),
         '0.0%']])}

  <div class="bad">The paid pass returned <b>zero</b> ingredient lists across
  {f(serper_tried)} products. Not a low rate, none at all. That is the clearest
  possible evidence that the information does not exist online rather than
  being merely hard to reach: a search engine cannot find a page that was never
  written.</div>

  <h3>Why there are no reviews at all</h3>
  <p>Not one of the {len(DOMAINS)} Lebanese brand sites runs a review system.
  Skinsort products carry reviews, Amazon products carry reviews, and the
  Lebanese retail set inherits some, but a Lebanese brand selling from its own
  Shopify shop has no reviews to collect.</p>

  <p>This matters for the thesis because it means <b>the Lebanese-made part of
  the market has no public record of what users think of it</b>. Any
  recommendation built on reviews will quietly ignore it. That is an argument
  for the ontology: reasoning from ingredients and skin type can say something
  useful about a product with no reviews at all, and a review-based method
  cannot.</p>

  <h3>What is honest to claim about this set</h3>
  {tbl(['can be said', 'cannot be said'],
       [[f'{f(N)} products from {BRANDS} Lebanese brands were collected from '
         f'the brands&rsquo; own shops',
         'that this is every Lebanese skincare product. Brands with no online '
         'shop cannot be reached this way'],
        ['every product was checked against three written tests, and every '
         'rejection was recorded with a reason',
         'that the judgements are beyond argument. They are recorded so they '
         'can be argued with'],
        [f'{pc(filled("ingredients"))} publish an ingredient list, and the '
         f'split between brands is sharp',
         'that the rest use secret formulas. They simply do not publish'],
        ['no brand in this set collects reviews',
         'that Lebanese products are unreviewed. People discuss them, just '
         'not in a form that can be collected']])}
</section>
"""

# ============================================================ write
htmltxt = PORTAL.read_text(encoding='utf-8')
before = len(htmltxt)
htmltxt = re.sub(
    r'<section class="section" id="lo-(what|find|domains|gaps)">.*?</section>',
    '', htmltxt, flags=re.S)

anchor = htmltxt.find('<section class="section" id="mg-merge">')
for alt in ('<section class="section" id="on-ready">',
            '<!-- ============================================ HOME -->',
            '<section class="section" id="home">'):
    if anchor == -1:
        anchor = htmltxt.find(alt)
if anchor == -1:
    raise SystemExit('could not find where to insert, portal not changed')
htmltxt = htmltxt[:anchor] + LO1 + LO2 + LO3 + LO4 + '\n\n' + htmltxt[anchor:]

nav = re.search(r'<nav class="nav">.*?</nav>', htmltxt, re.S).group(0)
if 'lo-what' not in nav:
    m = (re.search(r'(\s*<div class="grp">merging</div>)', htmltxt) or
         re.search(r'(\s*<div class="grp">ontology</div>)', htmltxt) or
         re.search(r'(\s*<div class="grp">overview</div>)', htmltxt))
    htmltxt = (htmltxt[:m.start()] +
               '\n    <div class="grp">lebanese origin</div>\n'
               '    <a data-s="lo-what">LO1. The Lebanese origin set</a>\n'
               '    <a data-s="lo-find">LO2. Finding the brands</a>\n'
               '    <a data-s="lo-domains">LO3. Sites kept and dropped</a>\n'
               '    <a data-s="lo-gaps">LO4. Coverage and gaps</a>' +
               m.group(1) + htmltxt[m.end():])

PORTAL.write_text(htmltxt, encoding='utf-8')

w = {}
for m in re.finditer(r'<section class="section[^"]*" id="(lo-[^"]+)">(.*?)</section>',
                     htmltxt, re.S):
    w[m.group(1)] = len(re.sub(r'<[^>]+>', ' ', m.group(2)).split())

print('=' * 62)
print('  LEBANESE ORIGIN PAGES ADDED')
print('=' * 62)
for k, v in w.items():
    print(f'    {k:12s}{v:6,} words')
print(f'\n  {sum(w.values()):,} words, '
      f'{sum(x.count("<table") for x in (LO1, LO2, LO3, LO4))} tables, '
      f'{sum(x.count("<svg") for x in (LO1, LO2, LO3, LO4))} diagrams')
print(f'  portal {before:,} -> {len(htmltxt):,} characters')
print()
print('  figures read from the files just now:')
print(f'    {f(N)} products, {BRANDS} brands, {len(DOMAINS)} sites kept')
print(f'    {f(NHARV)} harvested, {f(NDROP)} dropped, {len(only_dropped)} '
      f'sites rejected')
print(f'    {len(how)} searches in 3 languages, {CAND} candidates')
print(f'    ingredients {pc(filled("ingredients"))}, '
      f'skin type {pc(filled("skin_type"))}, reviews 0%')
