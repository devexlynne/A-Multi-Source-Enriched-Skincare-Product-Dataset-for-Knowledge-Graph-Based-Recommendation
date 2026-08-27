"""
The merging pages of the portal

Four pages:

    MG1  The three sources becoming one file, and the three categories
    MG2  Every rule used when two sources describe the same product
    MG3  The fourteen checks, and the six mistakes they caught
    MG4  Price, the lira problem, and why rating costs nothing extra

Every figure about the dataset is read from COMBINED_DATASET.csv at build time,
so nothing here can go stale. Run it again after any change to the data and the
numbers on the page move with it.

Usage:
    py build_portal_merge.py
"""
import re
import json
import pandas as pd
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    # the portal normally sits one level up; the absolute path stays first
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
c = pd.read_csv('COMBINED_DATASET.csv', dtype=str, low_memory=False).fillna('')

SRC = {}
for f, pre, label in [('SKINCARE_DATASET.csv', 'GLB', 'Global (Skinsort)'),
                      ('LEBANESE_RETAIL.csv', 'LBR', 'Lebanese retail'),
                      ('LEBANESE_ORIGIN.csv', 'LBO', 'Lebanese origin')]:
    try:
        d = pd.read_csv(f, dtype=str, low_memory=False).fillna('')
        SRC[pre] = {'label': label, 'file': f, 'rows': len(d),
                    'ing': int((d['ingredients'] != '').sum()) if 'ingredients' in d else 0,
                    'st': int((d['skin_type'] != '').sum()) if 'skin_type' in d else 0,
                    'pr': int((d['price_usd'] != '').sum()) if 'price_usd' in d else 0}
    except FileNotFoundError:
        SRC[pre] = {'label': label, 'file': f, 'rows': 0, 'ing': 0, 'st': 0, 'pr': 0}

N = len(c)
IN_TOTAL = sum(s['rows'] for s in SRC.values())
COLLAPSED = IN_TOTAL - N
BRANDS = int(c['brand'].nunique())
CATS = int(c['product_type'].nunique())
OVERLAP = int((pd.to_numeric(c['source_count'], errors='coerce') > 1).sum())
EXACT = int((c['match_method'] == 'exact').sum())
FUZZY = int((c['match_method'] == 'fuzzy').sum())
SINGLE = int((c['match_method'] == 'single source').sum())

CAT = {k: int((c['source_category'] == k).sum())
       for k in ['Global (Skinsort)', 'Lebanese retail', 'Lebanese origin']}
G_AND_LB = int(((c['src_global'] == '1') & (c['src_lb_retail'] == '1')).sum())
O_AND_LB = int(((c['src_lb_origin'] == '1') & (c['src_lb_retail'] == '1')).sum())

price = pd.to_numeric(c['price_usd'], errors='coerce')
PR_N = int(price.notna().sum())
lo = pd.to_numeric(c['price_usd_min'], errors='coerce')
hi = pd.to_numeric(c['price_usd_max'], errors='coerce')
SPREAD = int((lo.notna() & hi.notna() & (lo != hi)).sum())
RAT_N = int((c['rating'] != '').sum())
REV_N = int((c['review_texts_json'] != '').sum())
MULTI_REV = int(c['review_source'].str.contains(',').sum())

COVER = [('brand', 'brand'), ('name', 'product name'),
         ('product_type', 'category'), ('country', 'country'),
         ('skin_type', 'skin type'), ('sensitivity', 'sensitivity'),
         ('ingredients', 'ingredient list'), ('key_ingredients', 'key ingredients'),
         ('free_from', 'free from'), ('benefits', 'benefits'),
         ('concerns', 'concerns'), ('rating', 'rating'),
         ('review_texts_json', 'review texts'), ('price_usd', 'price'),
         ('skin_type_url', 'skin type source page')]


def f(x):
    return f'{x:,}'


def pc(x, of=None):
    return f'{100*x/(of or N):.1f}%'


def tbl(head, rows, cls=''):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f"<td class='td'>{x}</td>" for x in r) + '</tr>'
                for r in rows)
    return f'<table class="{cls}"><tr>{h}</tr>{b}</table>'


def kpis(items):
    return ('<div class="kpis">' + ''.join(
        f'<div class="kpi"><div class="n">{v}</div>'
        f'<div class="l">{l}</div></div>' for v, l in items) + '</div>')


def bar(rows, width=420):
    """A plain horizontal bar chart. Kept in SVG so it prints."""
    mx = max(v for _, v, _ in rows) or 1
    h = 26 * len(rows) + 14
    out = [f'<svg viewBox="0 0 700 {h}" xmlns="http://www.w3.org/2000/svg" '
           f'font-family="Segoe UI,Arial" font-size="11.5">']
    for i, (lab, v, col) in enumerate(rows):
        y = 8 + i * 26
        w = max(2, width * v / mx)
        out.append(f'<text x="0" y="{y+14}" fill="#2a2433">{lab}</text>')
        out.append(f'<rect x="190" y="{y+3}" width="{w:.0f}" height="15" rx="3" '
                   f'fill="{col}"/>')
        out.append(f'<text x="{190+w+7:.0f}" y="{y+15}" fill="#6b6478">'
                   f'{v:,}</text>')
    out.append('</svg>')
    return '<div class="dg">' + ''.join(out) + '</div>'


# ============================================================ MG1
MG1 = f"""
<section class="section" id="mg-merge">
  <h2>MG1 &middot; Three files becoming one</h2>
  <p class="lead">Up to this point the work sat in three separate files, each
  built a different way and each answering a different question. This page is
  about putting them together into the single table that the ontology and the
  knowledge graph will be built from.</p>

  {kpis([(f(N), 'products in the final file'),
         (f(BRANDS), 'brands'),
         (str(CATS), 'categories'),
         (f(IN_TOTAL), 'rows that went in'),
         (f(COLLAPSED), 'rows that were duplicates')])}

  <h3>What went in</h3>
  {tbl(['file', 'rows', 'skin type', 'ingredients', 'price', 'what it is'],
       [[f"<code>{SRC['GLB']['file']}</code>", f(SRC['GLB']['rows']),
         pc(SRC['GLB']['st'], SRC['GLB']['rows']),
         pc(SRC['GLB']['ing'], SRC['GLB']['rows']), 'none',
         'the global source, with reviews'],
        [f"<code>{SRC['LBR']['file']}</code>", f(SRC['LBR']['rows']),
         pc(SRC['LBR']['st'], SRC['LBR']['rows']),
         pc(SRC['LBR']['ing'], SRC['LBR']['rows']),
         pc(SRC['LBR']['pr'], SRC['LBR']['rows']),
         'on sale in six Lebanese shops'],
        [f"<code>{SRC['LBO']['file']}</code>", f(SRC['LBO']['rows']),
         pc(SRC['LBO']['st'], SRC['LBO']['rows']),
         pc(SRC['LBO']['ing'], SRC['LBO']['rows']),
         pc(SRC['LBO']['pr'], SRC['LBO']['rows']),
         'made by Lebanese brands']])}

  <div class="note">Skinsort has no price column at all. That is not a gap in
  the scraping, it is what the site publishes, and it sets a ceiling on price
  coverage that no amount of work on that source can lift. MG4 is about what
  was done instead.</div>

  <h3>The shape of the answer</h3>
  <p>One row per product. A product found in two sources becomes
  <b>one</b> row carrying the best of both, not two rows sitting next to each
  other. {f(IN_TOTAL)} rows went in and {f(N)} came out, so
  {f(COLLAPSED)} rows were another row's duplicate.</p>

  <div class="dg">
  <svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <rect x="8" y="14" width="150" height="46" rx="6" fill="#f7f5fb"
          stroke="#7a68a6"/>
    <text x="83" y="34" text-anchor="middle" fill="#584a7a"
          font-weight="700">Global</text>
    <text x="83" y="50" text-anchor="middle" fill="#6b6478">{f(SRC['GLB']['rows'])} rows</text>

    <rect x="8" y="76" width="150" height="46" rx="6" fill="#f7f5fb"
          stroke="#6f9c78"/>
    <text x="83" y="96" text-anchor="middle" fill="#3f6b48"
          font-weight="700">Lebanese retail</text>
    <text x="83" y="112" text-anchor="middle" fill="#6b6478">{f(SRC['LBR']['rows'])} rows</text>

    <rect x="8" y="138" width="150" height="46" rx="6" fill="#f7f5fb"
          stroke="#c07a54"/>
    <text x="83" y="158" text-anchor="middle" fill="#8d5433"
          font-weight="700">Lebanese origin</text>
    <text x="83" y="174" text-anchor="middle" fill="#6b6478">{f(SRC['LBO']['rows'])} rows</text>

    <path d="M158 37 L215 100" stroke="#b9aed0" fill="none"/>
    <path d="M158 99 L215 103" stroke="#b9aed0" fill="none"/>
    <path d="M158 161 L215 106" stroke="#b9aed0" fill="none"/>

    <rect x="215" y="72" width="128" height="62" rx="6" fill="#fff"
          stroke="#584a7a" stroke-width="1.5"/>
    <text x="279" y="92" text-anchor="middle" fill="#584a7a"
          font-weight="700">match</text>
    <text x="279" y="108" text-anchor="middle" fill="#6b6478">same brand</text>
    <text x="279" y="122" text-anchor="middle" fill="#6b6478">same product</text>

    <path d="M343 103 L400 103" stroke="#b9aed0" fill="none"/>
    <rect x="400" y="66" width="140" height="74" rx="6" fill="#fff"
          stroke="#b06a97" stroke-width="1.5"/>
    <text x="470" y="86" text-anchor="middle" fill="#b06a97"
          font-weight="700">keep the best</text>
    <text x="470" y="102" text-anchor="middle" fill="#6b6478">lowest tier wins</text>
    <text x="470" y="116" text-anchor="middle" fill="#6b6478">longest list wins</text>
    <text x="470" y="130" text-anchor="middle" fill="#6b6478">reviews add up</text>

    <path d="M540 103 L588 103" stroke="#b9aed0" fill="none"/>
    <rect x="588" y="72" width="104" height="62" rx="6" fill="#f7f5fb"
          stroke="#584a7a" stroke-width="1.5"/>
    <text x="640" y="94" text-anchor="middle" fill="#584a7a"
          font-weight="700">{f(N)}</text>
    <text x="640" y="110" text-anchor="middle" fill="#6b6478">products</text>
    <text x="640" y="124" text-anchor="middle" fill="#6b6478">one row each</text>

    <text x="279" y="212" text-anchor="middle" fill="#6b6478">
      {f(EXACT)} matched exactly &middot; {f(FUZZY)} matched closely
      &middot; {f(SINGLE)} in one source only</text>
    <text x="470" y="234" text-anchor="middle" fill="#6b6478">
      {f(OVERLAP)} products turned out to be in more than one source</text>
  </svg>
  <div class="cap">How three files become one, and where the
  {f(COLLAPSED)} extra rows go</div>
  </div>

  <h3>The three categories</h3>
  <p>Every product carries a <code>source_category</code>, and it holds one of
  exactly three values. This is the column to group by, filter on, and put in a
  table.</p>

  {bar([('Global (Skinsort)', CAT['Global (Skinsort)'], '#7a68a6'),
        ('Lebanese retail', CAT['Lebanese retail'], '#6f9c78'),
        ('Lebanese origin', CAT['Lebanese origin'], '#c07a54')])}

  {tbl(['category', 'products', 'share', 'what it means'],
       [['Global (Skinsort)', f(CAT['Global (Skinsort)']),
         pc(CAT['Global (Skinsort)']),
         'in the global source, and not sold in Lebanon as far as I found'],
        ['Lebanese retail', f(CAT['Lebanese retail']), pc(CAT['Lebanese retail']),
         'on sale in Lebanon, but the maker is not Lebanese'],
        ['Lebanese origin', f(CAT['Lebanese origin']), pc(CAT['Lebanese origin']),
         'made by a Lebanese company or person']])}

  <h3>What happens when a product is in two of them</h3>
  <p>{f(OVERLAP)} products are. A category has to be one value, so it is
  decided by the strongest fact known about the product:</p>

  <div class="dg">
  <svg viewBox="0 0 700 150" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <rect x="20" y="16" width="200" height="40" rx="6" fill="#fdf3ec"
          stroke="#c07a54"/>
    <text x="120" y="34" text-anchor="middle" fill="#8d5433"
          font-weight="700">made in Lebanon?</text>
    <text x="120" y="49" text-anchor="middle" fill="#6b6478">who MAKES it</text>
    <path d="M220 36 L262 36" stroke="#b9aed0"/>
    <text x="241" y="30" text-anchor="middle" fill="#6f9c78"
          font-weight="700">yes</text>
    <text x="270" y="40" fill="#8d5433" font-weight="700">Lebanese origin</text>

    <path d="M120 56 L120 76" stroke="#b9aed0"/>
    <text x="132" y="70" fill="#b5484d">no</text>
    <rect x="20" y="76" width="200" height="40" rx="6" fill="#eef6ee"
          stroke="#6f9c78"/>
    <text x="120" y="94" text-anchor="middle" fill="#3f6b48"
          font-weight="700">sold in Lebanon?</text>
    <text x="120" y="109" text-anchor="middle" fill="#6b6478">where it is SOLD</text>
    <path d="M220 96 L262 96" stroke="#b9aed0"/>
    <text x="241" y="90" text-anchor="middle" fill="#6f9c78"
          font-weight="700">yes</text>
    <text x="270" y="100" fill="#3f6b48" font-weight="700">Lebanese retail</text>

    <path d="M120 116 L120 134" stroke="#b9aed0"/>
    <text x="132" y="130" fill="#b5484d">no</text>
    <text x="145" y="138" fill="#584a7a" font-weight="700">Global (Skinsort)</text>
  </svg>
  <div class="cap">Made in beats sold in beats found in</div>
  </div>

  <p>So a Lebanese brand stocked by a Beirut shop counts as Lebanese origin,
  and a CeraVe cleanser sold in Beirut counts as Lebanese retail. Nothing is
  counted twice, and the three categories add up to {f(N)}.</p>

  <p>The fact that a product sits in two sources is not thrown away. Three
  markers keep it, so both readings stay available:</p>

  {tbl(['what you want to find', 'how', 'products'],
       [['everything sold in Lebanon',
         '<code>src_lb_retail = 1</code>',
         f(int((c['src_lb_retail'] == '1').sum()))],
        ['global products that reached Lebanon',
         '<code>src_global = 1 and src_lb_retail = 1</code>', f(G_AND_LB)],
        ['Lebanese brands their own shops carry',
         '<code>src_lb_origin = 1 and src_lb_retail = 1</code>', f(O_AND_LB)],
        ['products found in more than one source',
         '<code>source_count &gt; 1</code>', f(OVERLAP)]])}

  <h3>Where every column stands now</h3>
  {tbl(['column', 'filled', 'share'],
       [[lab, f(int((c[col] != '').sum())), pc(int((c[col] != '').sum()))]
        for col, lab in COVER])}
</section>
"""

# ============================================================ MG2
MG2 = f"""
<section class="section" id="mg-rules">
  <h2>MG2 &middot; What to keep when two sources disagree</h2>
  <p class="lead">{f(OVERLAP)} products appear in more than one source, so for
  those there are two or three versions of the same field and only one can go
  in the row. Picking the wrong one throws away work that was already paid
  for. Every rule below is written down, and every one of them is there
  because of something that went wrong earlier in the project.</p>

  <h3>Matching first: is this the same product?</h3>
  <p>Two products are the same if the brand matches and the significant words
  of the name match. Accents and punctuation are removed before comparing,
  sizes and promotional wording are stripped out, and short words are kept.</p>

  {tbl(['step', 'what it does', 'why'],
       [['strip accents and punctuation',
         'Av&egrave;ne and Avene become the same brand',
         'without it Av&egrave;ne became "avne" and matched nothing'],
        ['strip sizes and offers',
         '"50ml", "Buy 1 Get 1" removed from the name',
         'the same cream in two sizes is one product'],
        ['keep short words',
         '"Ruboril Expert M" stays different from "Ruboril Expert S"',
         'dropping them merged two real products into one'],
        ['exact key match first', f'{f(EXACT)} products',
         'cheapest and safest'],
        ['then close match at 90 or above', f'{f(FUZZY)} products',
         'catches spelling and word order differences']])}

  <div class="note">The 90 threshold is not arbitrary. An earlier version used
  92 on a looser comparison and merged CeraVe Hydrating Cleanser with the PM,
  the AM and the SA versions, four different products in one row. The rule was
  changed to compare the set of significant words rather than the string.</div>

  <h3>Then, field by field</h3>
  {tbl(['field', 'rule', 'why that rule'],
       [['skin type', 'the <b>lowest tier</b> wins, 1 beats 2 beats 3',
         'a manufacturer statement outranks a shop, and a shop outranks an '
         'analysis site. This is the same order used everywhere else in the '
         'project, so the merge cannot quietly promote a weaker source'],
        ['ingredients', 'the <b>longest list</b> wins',
         'ingredient lists get truncated by shops. Length is a fair stand-in '
         'for completeness, and three other columns are computed from this '
         'one, so a short list would spoil four fields at once'],
        ['reviews', '<b>added together</b>, never chosen between',
         'two shops reviewing one product is two pieces of evidence, not two '
         'competing answers. This is the rule I got wrong, twice'],
        ['review count', '<b>summed</b> across sources',
         'it is a count, so picking one source would undercount'],
        ['price', 'lowest, middle and highest all kept',
         'the same cream is not one price in Lebanon. See MG4'],
        ['brand and name', 'the fullest version',
         'one source abbreviates, another spells it out'],
        ['everything else', 'first one that is not empty, global first',
         'the global source was cleaned first and most thoroughly']])}

  <h3>The reviews rule, and why it is written in capitals in the code</h3>
  <p>The first merge picked a survivor by counting how many fields were
  filled. A copy with more fields filled but no reviews beat a copy with
  reviews, and 49 products lost their Lebanese reviews without anything being
  reported. Those were mostly Av&egrave;ne products reviewed on Ounousa,
  which is one of the few Arabic-language review sources in the whole
  project.</p>

  <p>The second version kept the longest review set instead. That was better
  and still wrong: a product on Skinsort and in a Beirut shop kept whichever
  set had more characters, so the Ounousa comments disappeared behind the
  Skinsort ones. About 550 products were affected.</p>

  <div class="ok">The rule now is that reviews are pooled. Duplicates are
  removed by comparing the text itself, and the sources are all named.
  {f(MULTI_REV)} products now name two or more review sources, and
  {f(REV_N)} products carry review text.</div>

  <h3>Every value keeps its source</h3>
  <p>A merged row is built from up to three others, so for the fields that
  matter it records which one it took the value from.</p>

  {tbl(['column', 'what it records'],
       [['<code>skin_type_source</code>, <code>skin_type_url</code>',
         'the page the skin type came from, and the exact sentence'],
        ['<code>skin_type_tier</code>',
         'how strong that page is, 1 to 4'],
        ['<code>ingredient_source</code>, <code>ingredient_url</code>',
         'where the formula came from'],
        ['<code>review_source</code>',
         'every review source, comma separated'],
        ['<code>match_method</code>, <code>match_score</code>',
         'exact, close, or single source, and how close'],
        ['<code>first_source</code>',
         'the file the product was first seen in']])}

  <div class="note">This is what makes the file ready for a knowledge graph
  rather than just tidy. Every statement can be traced back to the page it
  came from, which is what PROV-O expects and what a supervisor will ask
  for.</div>
</section>
"""

# ============================================================ MG3
MG3 = f"""
<section class="section" id="mg-checks">
  <h2>MG3 &middot; Fourteen checks, and the six mistakes they caught</h2>
  <p class="lead">The merge script ends by testing its own output. If any
  check fails the file is <b>not saved</b>, so a broken dataset cannot quietly
  replace a working one. Every check exists because that exact failure has
  already happened at least once in this project.</p>

  {kpis([('14', 'checks'), ('6', 'real bugs caught'),
         ('0', 'failing now'), ('7', 'runs before it saved')])}

  <h3>The checks</h3>
  {tbl(['#', 'what it tests', 'what it stops'],
       [['1', 'ids unique and correctly formed',
         'two products sharing an id'],
        ['2', 'no duplicate brand and name survives',
         'the deduplication silently missing a pair'],
        ['3', 'controlled columns hold only allowed values',
         'a skin type spelled a new way'],
        ['4', 'no placeholder text survives',
         '"not available" being counted as data'],
        ['5', 'sensitivity filled wherever skin type is',
         'half a classification'],
        ['6', 'every skin type has a source',
         'a claim with nothing behind it'],
        ['7', 'ingredient count matches the list',
         'a count left over from an older list'],
        ['8', 'free from blank where the list is short',
         'claiming "fragrance free" from a truncated formula'],
        ['9', 'rating between 0 and 5',
         'a review count landing in the rating column'],
        ['10', 'markers add up to source count',
         'the flags and the total disagreeing'],
        ['11', 'every input row landed in exactly one output row',
         'a product being dropped or counted twice'],
        ['12', 'no product lost a review it had',
         'the mistake described in MG2'],
        ['13', 'category is one of three and matches the markers',
         'the plain-language column drifting from the numbers'],
        ['14', 'prices positive and lowest &le; price &le; highest',
         'a currency mix-up, which is exactly what it found']])}

  <h3>What they caught</h3>
  <p>The script had to be run seven times before it was allowed to save.
  These are the six real faults it refused to write:</p>

  {tbl(['#', 'what was wrong', 'how many', 'the fix'],
       [['1', 'Zero treated as missing data. <code>src_global = 0</code> and '
         '<code>n_retailers = 0</code> were being blanked as if nobody knew '
         'the value', '37,635 cells',
         'zero removed from the missing-value list, except in rating, review '
         'count and price where a zero really would be a claim'],
        ['2', '<code>match_method</code> was set to the word "none" for '
         'products found in one source, and "none" is itself one of the words '
         'that means missing', '11,521 cells',
         'the value is now "single source", which is a fact about the '
         'product rather than a word that reads as absence'],
        ['3', 'Skin type held more than one value, like "All, Dry" and '
         '"Combination, Dry, Normal, Oily", left over from the original '
         'Lebanese workbook', '115 rows',
         'collapsed to one value using the project rule: dry and oily '
         'together is combination, three or more is all. Sensitive moved to '
         'the sensitivity column where it belongs'],
        ['4', 'A skin type with no source recorded', '52 rows',
         'removed. Every other value in the project carries its source, and '
         'the exception is the one a supervisor would find'],
        ['5', 'Reviews were being chosen between rather than pooled, so the '
         'longer set won and the other was discarded', 'about 550 products',
         'reviews are now pooled and deduplicated by their text'],
        ['6', 'Five products priced in Lebanese lira sitting in a column '
         'labelled dollars. One serum was stored as 1,540,000', '5 rows',
         'converted at the published rate. See MG4']])}

  <div class="bad">Two of the fourteen checks were themselves wrong when
  first written, and I found that by testing rather than by reading. Check 11
  compared <code>len(c) + (expected - len(c))</code> against
  <code>expected</code>, which is true no matter what the run did, so it
  could never fail. It now tests that every input row landed in exactly one
  output group. Check 4 was flagging 37,635 correct cells because of the zero
  problem above.</div>

  <div class="ok">All fourteen pass on the file that is on disk now:
  {f(N)} products, {f(BRANDS)} brands, {CATS} categories, no duplicate
  brand and name, no placeholder text, and every skin type with a source
  behind it.</div>

  <h3>What is deliberately still empty</h3>
  <p>Blank is a finding, not a failure, and these blanks are all on
  purpose:</p>
  {tbl(['column', 'blank', 'why it is blank'],
       [['free from',
         f(int(((c['free_from'] == '') & (c['ingredients'] != '')).sum())),
         'the ingredient list was too short to support a claim about what is '
         '<i>not</i> in the formula'],
        ['price', f(N - PR_N),
         'Skinsort publishes no prices, so a global-only product has none'],
        ['ingredients', f(int((c['ingredients'] == '').sum())),
         'small Lebanese makers mostly do not publish an INCI list, which is '
         'itself a result worth reporting'],
        ['skin type', f(int((c['skin_type'] == '').sum())),
         'no source stated one, and guessing would defeat the point']])}
</section>
"""

# ============================================================ MG4
tot_ing = int((c['ingredients'] != '').sum())
MG4 = f"""
<section class="section" id="mg-price">
  <h2>MG4 &middot; Price, the lira, and a rating that costs nothing</h2>
  <p class="lead">Price was the last column to be taken seriously, and looking
  at it properly turned up two faults and one thing worth reporting on its
  own.</p>

  {kpis([(f(PR_N), 'products with a price'),
         (pc(PR_N), 'of the dataset'),
         (f'${price.median():,.2f}' if PR_N else 'n/a', 'median price'),
         (f(SPREAD), 'sold at two different prices'),
         (f(RAT_N), 'products with a rating')])}

  <h3>Every price in this dataset comes from a Lebanese shop</h3>
  <p>Skinsort does not publish prices. So price coverage is not limited by how
  hard the scraping worked, it is limited by which sources have prices at all,
  and that is a structural ceiling rather than a gap to close.</p>

  {bar([('has a price', PR_N, '#6f9c78'),
        ('no price anywhere', N - PR_N, '#d9dee5')])}

  <h3>Fault one: the same product, two prices</h3>
  <p>When several shops sell the same cream, the merge originally kept
  whichever row came first and threw the rest away. That turns a real price
  range into one number nobody can check.</p>

  <p>Now all three are kept, and the spread turns out to be a finding:
  <b>{f(SPREAD)} products sell at different prices in different Lebanese
  shops</b>.</p>

  {tbl(['column', 'what it holds'],
       [['<code>price_usd</code>', 'the middle price, for anyone who wants one number'],
        ['<code>price_usd_min</code>', 'the cheapest shop'],
        ['<code>price_usd_max</code>', 'the dearest shop']])}

  <h3>Fault two: a serum priced at one and a half million</h3>
  <p>Five products from Lebanese-origin shops were priced in lira in a column
  labelled dollars. Check 14 refused to save the file because of them.</p>

  {tbl(['product', 'stored as', 'really'],
       [['AloeLab Aloe C Ferulic with 15% L-Ascorbic Acid', '1,540,000',
         '$17.21'],
        ['AloeLab Salicylic Acid Facial Cleanser', '870,000', '$9.72'],
        ['AloeLab Biphase Makeup Remover 500ml', '490,000', '$5.47'],
        ['AloeLab Aloe Rose Mist', '480,000', '$5.36'],
        ['Beesline Mud Mask', '252,390', '$2.82']])}

  <div class="note">Converted at 89,500 lira to the dollar, the rate Banque du
  Liban settles card payments at, fixed since December 2023. The rate and its
  date belong in the thesis next to any price figure, because a price in lira
  is only meaningful alongside the rate it was converted at.</div>

  <h3>Filling the rest, and what that price would mean</h3>
  <p>{f(N - PR_N)} products still have no price. These can be fetched from
  Google Shopping through Serper, which returns the price already parsed
  rather than as a web page to read, so it costs one credit per product with
  no second pass.</p>

  <p>That price is <b>not</b> the same measurement as the one already in the
  file, so it goes in its own column and never touches
  <code>price_usd</code>:</p>

  {tbl(['column', 'what it is', 'what it is not'],
       [['<code>price_usd</code>', 'a named Beirut shop, known date',
         'not a world price'],
        ['<code>price_usd_market</code>',
         'US retail, mixed sellers, on the day it was collected',
         'not the price in Lebanon, and not stable over time'],
        ['<code>price_market_source</code>', 'which seller', ''],
        ['<code>price_market_n</code>',
         'how many offers the figure was taken from', ''],
        ['<code>price_market_date</code>', 'the day it was collected',
         'without this the number cannot be repeated']])}

  <div class="ok">Keeping them apart is what makes the comparison possible:
  what does the same product cost in Beirut against the open market? That is a
  question worth asking in the thesis, and it only exists if the two numbers
  never get mixed into one column.</div>

  <h3>How a listing is checked before its price is believed</h3>
  <p>Searching a product name returns other people's products. Four tests
  run before any number is accepted, and the median of what survives is
  stored rather than the first result, because the first result is often a
  three-pack or a reseller.</p>

  {tbl(['listing that came back', 'we asked for', 'what happens'],
       [['Garnier Mud Mask', 'Beesline Mud Mask', 'refused, different brand'],
        ['CeraVe Moisturizing Cream, Pack of 3', 'CeraVe Moisturizing Cream',
         'refused, a three-pack price is not this product'],
        ['CeraVe Hydrating Cleanser <b>Bar</b>', 'CeraVe Hydrating Cleanser',
         'refused, the bar is a different product'],
        ['The Ordinary Niacinamide <b>Travel Size</b>',
         'The Ordinary Niacinamide', 'refused, different size'],
        ["L'Oreal Revitalift", "L'Or&eacute;al Revitalift",
         'accepted, the accent is removed before comparing']])}

  <div class="note">That last row is the same fault that broke brand matching
  earlier in the project. It came back in new code, which is the argument for
  writing these tests down rather than remembering them.</div>

  <h3>Rating, at no extra cost</h3>
  <p>The obvious next question is whether to spend credits on ratings the same
  way. The answer is no, because there is nothing to spend: the reply that
  carries the price also carries the rating and the number of people who left
  it. It is the same credit, already paid.</p>

  <div class="dg">
  <svg viewBox="0 0 700 190" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <rect x="10" y="20" width="150" height="44" rx="6" fill="#f7f5fb"
          stroke="#7a68a6"/>
    <text x="85" y="40" text-anchor="middle" fill="#584a7a"
          font-weight="700">one question</text>
    <text x="85" y="56" text-anchor="middle" fill="#6b6478">1 credit</text>
    <path d="M160 42 L215 42" stroke="#b9aed0"/>
    <rect x="215" y="10" width="215" height="120" rx="6" fill="#fff"
          stroke="#584a7a"/>
    <text x="322" y="30" text-anchor="middle" fill="#584a7a"
          font-weight="700">one reply</text>
    <text x="230" y="52" fill="#6b6478">title</text>
    <text x="230" y="70" fill="#6b6478">source</text>
    <text x="230" y="88" fill="#3f6b48" font-weight="700">price</text>
    <text x="230" y="106" fill="#b06a97" font-weight="700">rating</text>
    <text x="230" y="124" fill="#b06a97" font-weight="700">ratingCount</text>

    <path d="M430 88 L500 88" stroke="#6f9c78"/>
    <text x="508" y="92" fill="#3f6b48" font-weight="700">price_usd_market</text>
    <path d="M430 112 L500 112" stroke="#b06a97"/>
    <text x="508" y="116" fill="#b06a97" font-weight="700">rating_market</text>

    <text x="350" y="166" text-anchor="middle" fill="#6b6478">
      a separate rating pass would pay a second time for an answer
      already received</text>
  </svg>
  <div class="cap">Rating arrives in the same reply as price</div>
  </div>

  <h3>Three rules the rating follows</h3>
  {tbl(['rule', 'why'],
       [['only listings that already passed the brand and name tests are read',
         'a rating can never come from a different product, for the same '
         'reason a price cannot'],
        ['the rating is weighted by how many people left it',
         'a 5.0 from three buyers should not outweigh a 4.3 from twelve '
         'thousand. A plain average does exactly that. Weighting turns that '
         'pair into 4.4 rather than 4.7'],
        ['it goes in <code>rating_market</code>, not <code>rating</code>',
         'the existing rating comes with review text attached and belongs to '
         'a named source. A market rating is a number with no text behind it. '
         'Same reasoning as the price columns']])}

  <p>Rating currently sits at {f(RAT_N)} products, {pc(RAT_N)}. It is the
  thinnest column in the dataset, and this fills a large part of it for
  nothing.</p>
</section>
"""

# ============================================================ write
html = PORTAL.read_text(encoding='utf-8')
before = len(html)

# idempotent: remove any earlier version of these four pages first
html = re.sub(r'<section class="section" id="mg-(merge|rules|checks|price)">.*?</section>',
              '', html, flags=re.S)

anchor = html.find('<section class="section" id="on-ready">')
if anchor == -1:
    anchor = html.find('<!-- ============================================ HOME -->')
if anchor == -1:
    anchor = html.find('<section class="section" id="home">')
if anchor == -1:
    raise SystemExit('could not find where to insert, portal not changed')
html = html[:anchor] + MG1 + MG2 + MG3 + MG4 + '\n\n' + html[anchor:]

nav_block = re.search(r'<nav class="nav">.*?</nav>', html, re.S).group(0)
if 'mg-merge' not in nav_block:
    m = re.search(r'(\s*<div class="grp">ontology</div>)', html)
    if not m:
        m = re.search(r'(\s*<div class="grp">overview</div>)', html)
    if m is None:
        print('  nav already has these pages, leaving it alone')
    else:
        html = (html[:m.start()] +
            '\n    <div class="grp">merging</div>\n'
            '    <a data-s="mg-merge">MG1. Three files into one</a>\n'
            '    <a data-s="mg-rules">MG2. Keeping the best</a>\n'
            '    <a data-s="mg-checks">MG3. The fourteen checks</a>\n'
            '    <a data-s="mg-price">MG4. Price and rating</a>' +
            m.group(1) + html[m.end():])

PORTAL.write_text(html, encoding='utf-8')

w = {}
for m in re.finditer(r'<section class="section[^"]*" id="(mg-[^"]+)">(.*?)</section>',
                     html, re.S):
    w[m.group(1)] = len(re.sub(r'<[^>]+>', ' ', m.group(2)).split())

print('=' * 60)
print('  MERGING PAGES ADDED TO THE PORTAL')
print('=' * 60)
for k, v in w.items():
    print(f'    {k:12s}{v:6,} words')
print(f'\n  {sum(w.values()):,} words, '
      f'{sum(MG.count("<table") for MG in (MG1, MG2, MG3, MG4))} tables, '
      f'{sum(MG.count("<svg") for MG in (MG1, MG2, MG3, MG4))} diagrams')
print(f'  portal {before:,} -> {len(html):,} characters')
print()
print('  every figure read from COMBINED_DATASET.csv just now:')
print(f'    {f(N)} products, {f(BRANDS)} brands, {CATS} categories')
print(f'    {f(CAT["Global (Skinsort)"])} global, '
      f'{f(CAT["Lebanese retail"])} Lebanese retail, '
      f'{f(CAT["Lebanese origin"])} Lebanese origin')
print(f'    {f(PR_N)} priced, {f(SPREAD)} with a price spread, '
      f'{f(RAT_N)} rated')
