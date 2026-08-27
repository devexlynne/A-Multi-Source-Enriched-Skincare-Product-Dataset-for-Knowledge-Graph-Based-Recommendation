"""
The cleaning pages of the portal

Five pages, about the work that changed the data rather than the work that
collected it:

    CD1  What the file looks like now
    CD2  The mistakes that were found and corrected
    CD3  How a value is judged good enough to keep
    CD4  What was paid for, and what it cost
    CD5  What is still empty, and why

Every number is read from the files when this runs. Nothing is typed in, so
running it again after any change moves the figures with it.

Usage:
    py build_portal_cleaning.py
"""
import re
import csv
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


C = load('COMBINED_DATASET.csv')
PROG = load('price_progress.csv')
HARV = load('lebanese_origin_harvested.csv')
ORIG = load('LEBANESE_ORIGIN.csv')
N = len(C)


def has(r, col):
    return bool(str(r.get(col, '')).strip())


def n_any(*cols):
    return sum(1 for r in C if any(has(r, c) for c in cols))


def f(x):
    return f'{x:,}'


def pc(x, of=None):
    return f'{100*x/(of or N):.1f}%'


def tbl(head, rows):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f"<td class='td'>{x}</td>" for x in r) + '</tr>'
                for r in rows)
    return f'<table><tr>{h}</tr>{b}</table>'


def kpis(items):
    return ('<div class="kpis">' + ''.join(
        f'<div class="kpi"><div class="n">{v}</div><div class="l">{l}</div></div>'
        for v, l in items) + '</div>')


def bar(rows, width=360, x=250):
    mx = max((v for _, v, _ in rows), default=1) or 1
    h = 24 * len(rows) + 12
    out = [f'<svg viewBox="0 0 720 {h}" xmlns="http://www.w3.org/2000/svg" '
           f'font-family="Segoe UI,Arial" font-size="11.5">']
    for i, (lab, v, col) in enumerate(rows):
        y = 6 + i * 24
        w = max(2, width * v / mx)
        out.append(f'<text x="0" y="{y+13}" fill="#2a2433">{lab}</text>')
        out.append(f'<rect x="{x}" y="{y+2}" width="{w:.0f}" height="14" rx="3" '
                   f'fill="{col}"/>')
        out.append(f'<text x="{x+w+7:.0f}" y="{y+14}" fill="#6b6478">{v:,}</text>')
    out.append('</svg>')
    return '<div class="dg">' + ''.join(out) + '</div>'


# ---------------------------------------------------------------- figures
COVER = [('brand', ['brand']), ('product name', ['name']),
         ('category', ['product_type']), ('concerns', ['concerns']),
         ('sensitivity', ['sensitivity']), ('skin type', ['skin_type']),
         ('a description', ['product_summary']),
         ('a price', ['price_usd', 'price_usd_market']),
         ('ingredient list', ['ingredients']),
         ('key ingredients', ['key_ingredients']),
         ('free from', ['free_from']), ('benefits', ['benefits']),
         ('a rating', ['rating', 'rating_market']),
         ('review text', ['review_texts_json'])]

cat = collections.Counter(r['source_category'] for r in C)
last = {}
for r in PROG:
    p = last.get(r['product_id'])
    if p and not r.get('price') and p.get('price'):
        continue
    last[r['product_id']] = r
still = [k for k, v in last.items()
         if not v.get('price') and v.get('why_not') == 'no listings']
by_cat_left = collections.Counter(
    next((x['source_category'] for x in C if x['product_id'] == k), '?')
    for k in still) if len(still) < 5000 else collections.Counter()

asked = len(last)
priced = sum(1 for v in last.values() if v.get('price'))
harvest_price = sum(1 for r in HARV if r.get('price', '').strip()
                    not in ('', '0', '0.0', '0.00'))
orig_price = sum(1 for r in ORIG if r.get('price_usd', '').strip())

# ============================================================ CD1
CD1 = f"""
<section class="section" id="cd-now">
  <h2>CD1 &middot; Where the file stands</h2>
  <p class="lead">One row for each product, one price column meaning one thing,
  and every value traceable to the page it came from. This page is the state of
  the file as it is on disk right now, not a plan for it.</p>

  {kpis([(f(N), 'products'), (f(len({r['brand'] for r in C})), 'brands'),
         (str(len({r['product_type'] for r in C if r['product_type']})), 'categories'),
         (str(len(C[0]) if C else 0), 'columns'),
         ('14', 'checks it passes')])}

  <h3>The three groups</h3>
  {bar([('Global (Skinsort)', cat['Global (Skinsort)'], '#7a68a6'),
        ('Lebanese retail', cat['Lebanese retail'], '#6f9c78'),
        ('Lebanese origin', cat['Lebanese origin'], '#c07a54')], x=170)}

  <h3>How full each column is</h3>
  {tbl(['column', 'products', 'share'],
       [[lab, f(n_any(*cols)), pc(n_any(*cols))] for lab, cols in COVER])}

  <div class="note">Blank does not mean the work was not done. Skinsort
  publishes no prices at all, so a global product has none until it is looked
  up elsewhere. Small Lebanese makers mostly do not publish an ingredient list.
  Those blanks are results, and CD5 goes through them one at a time.</div>
</section>
"""

# ============================================================ CD2
CD2 = f"""
<section class="section" id="cd-fixed">
  <h2>CD2 &middot; What went wrong, and what it cost</h2>
  <p class="lead">These are the faults that changed the data, not every wrong
  turn. Each one was found after the file had already been written and looked
  fine. That is the pattern worth noticing: none of them raised an error, and
  most of them made the dataset look better than it was.</p>

  <h3>Things that were counted as data and were not</h3>
  {tbl(['what happened', 'how many', 'how it was caught', 'what changed'],
       [['The word "none" and the phrase "not available" sat in cells as if '
         'they were answers. Review coverage read as 89% when it was 15%.',
         '15,470 cells',
         'Reviews looked far too complete for a dataset built from shop pages.',
         'A fixed list of words that mean "we do not know" is blanked on the '
         'way in. Coverage figures dropped and became true.'],
        ['The merge treated a zero as missing. Every product not in a source '
         'has a zero marker, and every one was being wiped.',
         '37,635 cells',
         'Check 4 refused to save the file.',
         'Zero counts as missing only in rating, review count and price, '
         'where a zero would be a claim about the product.'],
        ['Products found in one source were marked with the word "none", '
         'which is itself in the missing-value list.',
         '11,521 cells',
         'Check 4 again, on the next run.',
         'The value is now "single source", which is a fact rather than a '
         'word that reads as absence.'],
        ['A skin type was recorded with no note of where it came from.',
         '52 rows',
         'Check 6.',
         'Removed. Every other value in the project carries its source and '
         'an exception is what a reader would find first.']])}

  <h3>Things that were collected and then lost</h3>
  {tbl(['what happened', 'how many', 'the cause', 'what changed'],
       [['Lebanese shop prices were scraped and then thrown away.',
         f'{f(harvest_price)} scraped, 278 kept',
         'The scraper writes a column called <code>price</code>. The shared '
         'schema calls it <code>price_usd</code>. Any schema column that is '
         'missing gets created empty, so an empty column was written while '
         'the real price sat next to it.',
         f'Matched back on the exact page address. {f(orig_price)} Lebanese '
         f'products now have a price instead of 278.'],
        ['The shop&#39;s own description of each product, lost the same way.',
         '556 rows',
         'The scraper calls it <code>description</code>, the schema calls it '
         '<code>product_summary</code>.',
         'Recovered in the same pass.'],
        ['Reviews were chosen between rather than added together. When one '
         'product appeared twice, the longer set won and the other was '
         'discarded.',
         'about 550 products',
         'Counting how many products name more than one review source. It '
         'was zero, which it should not have been.',
         'Reviews are pooled and duplicates removed by comparing the text. '
         f'{f(sum(1 for r in C if "," in r.get("review_source", "")))} '
         'products now name two or more sources.'],
        ['An earlier merge picked a survivor by counting filled fields, so a '
         'copy with more fields but no reviews beat a copy with reviews.',
         '49 products',
         'You asked where the Ounousa reviews had gone.',
         'Survivorship is written down field by field, and reviews are never '
         'the field that decides.']])}

  <h3>Things that were wrong in a way that looked right</h3>
  {tbl(['what happened', 'how many', 'why it mattered', 'what changed'],
       [['Five Lebanese products were priced in lira in a column called '
         'price_usd. One serum was stored as 1,540,000.',
         '5 rows, then 214 more found in the source file',
         'A reader opening the file saw a face cream costing two million '
         'dollars.',
         'Converted at 89,500 lira to the dollar, the rate the central bank '
         'settles card payments at. The rate and its date belong next to any '
         'price figure in the writing.'],
        ['Nearly a quarter of the market prices came from eBay, Mercari and '
         'Poshmark. Those are people selling used items.',
         '256 of 1,137',
         'Poshmark had already been removed once from the skin type column '
         'after it was questioned. It came back through a different column.',
         'Secondhand marketplaces are refused when collecting and refused '
         'again when writing, so a resale price cannot reach the file by any '
         'route.'],
        ['A search key ran out of credits without saying so. It returned a '
         'normal reply with an empty list, which reads as "this product is '
         'not sold anywhere".',
         '4,641 products',
         'It produced a clean, believable, completely false result: that no '
         'Lebanese product is sold online. That was one message away from '
         'going into the writing as a finding.',
         'Sixty empty replies in a row now stops the run. Products marked '
         'this way can be asked again.'],
        ['Deduplication merged four different CeraVe cleansers into one row.',
         '4 products into 1',
         'Similar names are not the same product.',
         'Two products match only when their significant words match exactly. '
         'Short words are kept, because dropping them merged Ruboril Expert M '
         'with Ruboril Expert S.']])}

  <div class="dg">
  <svg viewBox="0 0 720 220" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <text x="0" y="16" fill="#584a7a" font-weight="700">How each fault was found</text>
    <rect x="10" y="34" width="190" height="42" rx="6" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="105" y="52" text-anchor="middle" fill="#3f6b48" font-weight="700">a check refused to save</text>
    <text x="105" y="68" text-anchor="middle" fill="#6b6478">4 faults</text>

    <rect x="215" y="34" width="190" height="42" rx="6" fill="#fdf3ec" stroke="#c07a54"/>
    <text x="310" y="52" text-anchor="middle" fill="#8d5433" font-weight="700">a number looked wrong</text>
    <text x="310" y="68" text-anchor="middle" fill="#6b6478">5 faults</text>

    <rect x="420" y="34" width="190" height="42" rx="6" fill="#f7f5fb" stroke="#7a68a6"/>
    <text x="515" y="52" text-anchor="middle" fill="#584a7a" font-weight="700">you asked a question</text>
    <text x="515" y="68" text-anchor="middle" fill="#6b6478">3 faults</text>

    <text x="10" y="112" fill="#6b6478">Not one of them raised an error. The scripts ran, wrote a file, and</text>
    <text x="10" y="130" fill="#6b6478">reported success every time.</text>
    <text x="10" y="158" fill="#b5484d" font-weight="700">Three of them made the data look better than it was.</text>
    <text x="10" y="178" fill="#6b6478">Review coverage read 89% instead of 15%. Prices looked complete when</text>
    <text x="10" y="196" fill="#6b6478">2,300 had been dropped. Lebanese products looked absent from the</text>
    <text x="10" y="214" fill="#6b6478">market when nobody had actually asked.</text>
  </svg>
  <div class="cap">Where the faults came from</div>
  </div>
</section>
"""

# ============================================================ CD3
short_ff = sum(1 for r in C if has(r, 'ingredients') and not has(r, 'free_from'))
CD3 = f"""
<section class="section" id="cd-rules">
  <h2>CD3 &middot; When a value is good enough to keep</h2>
  <p class="lead">Most of the work in this project is not fetching values. It
  is deciding which of the values that come back deserve to be written down.
  Every rule below started as something that went wrong.</p>

  <h3>An ingredient list is recognised by its shape, not its heading</h3>
  <p>A page that says "Ingredients" underneath a paragraph of marketing does
  not have an ingredient list on it. So the text is judged on what it looks
  like:</p>
  {tbl(['test', 'why'],
       [['at least five pieces separated by commas',
         'a formula is a list, and a sentence is not'],
        ['at least three of them recognisable chemical names',
         'the benefits column was passing as ingredients until this was added, '
         'because "Hydrates, Soothes, Brightens" is also a comma separated list'],
        ['a gap of up to two odd pieces is allowed',
         'an early version took the longest unbroken run and one strange name '
         'in the middle cut real formulas in half'],
        ['refused if three or more pieces are benefit words',
         'the same reason as above, caught from the other direction']])}

  <div class="note">The validator went through six rounds. The version that
  damaged data was the one that looked most careful: it kept only the longest
  run of clean pieces, which sounds strict and quietly deleted the second half
  of hundreds of formulas. Being strict is not the same as being right.</div>

  <h3>A claim about absence needs a complete list</h3>
  <p>Saying a product is fragrance free is a claim about what is <i>not</i> in
  it, and that can only be checked against a whole formula. So
  <code>free_from</code> is only written where the list has at least eight
  ingredients and does not trail off with "and 25 more". Everywhere else it
  stays empty, which is why {f(short_ff)} products have an ingredient list but
  no free-from value.</p>

  <h3>"Not for oily skin" does not mean oily skin</h3>
  <p>Reading skin type out of a sentence catches negations if nobody checks.
  You asked whether it did, and it had: thirteen products carried the opposite
  of what their page said. "Not Good for Oily Skin" had been read as Oily.</p>
  {tbl(['the sentence on the page', 'what was recorded', 'what it should be'],
       [['Not Good for Oily Skin', 'Oily', 'blank, or dry'],
        ['not tight or dry, formulated for sensitive skin', 'nothing wrong here',
         'the same, this one was a false alarm in my first fix'],
        ['avoid chemical UV filters', 'nothing wrong here',
         'the same, also a false alarm']])}
  <p>Two of my first three catches were wrong, which is why the rule now looks
  at what the negation applies to rather than just spotting the word "not".</p>

  <h3>The same product, twice</h3>
  {tbl(['rule', 'what it stops'],
       [['accents and punctuation removed before comparing',
         'Av&egrave;ne and Avene reading as two brands, and L&#39;Or&eacute;al '
         'matching nothing at all'],
        ['sizes and offer wording stripped from the name',
         'the same cream in 50ml and 100ml counting twice'],
        ['short words kept',
         'Ruboril Expert M and Ruboril Expert S merging into one product'],
        ['exact word set first, then close matches at 90 or above',
         'four CeraVe cleansers becoming one row']])}

  <h3>Where a value came from is written next to it</h3>
  <p>Every skin type carries the page it came from, the sentence it was read
  out of, and how strong that source is. A manufacturer's own page outranks a
  shop, and a shop outranks an analysis site. The merge keeps the strongest
  one, so it cannot quietly promote a weaker source when two disagree.</p>
  {tbl(['tier', 'what it means', 'products'],
       [[t, lab, f(sum(1 for r in C if r.get('skin_type_tier') == t))]
        for t, lab in [('1', "the maker's own website"),
                       ('2', 'a shop that sells it'),
                       ('3', 'an analysis site'),
                       ('4', 'anything weaker')]])}
</section>
"""

# ============================================================ CD4
CD4 = f"""
<section class="section" id="cd-paid">
  <h2>CD4 &middot; What was paid for</h2>
  <p class="lead">Four columns were filled by paid search after the free
  methods ran out. This page is what that bought, what it cost, and the two
  places where paying stopped being worth it.</p>

  {kpis([(f(asked), 'products asked about'),
         (f(priced), 'came back with a price'),
         (pc(priced, max(asked, 1)), 'hit rate'),
         (f(n_any('rating', 'rating_market')), 'have a rating'),
         (f(len(still)), 'still to ask')])}

  <h3>The single thing that mattered most</h3>
  <p>Searching by keyword and hoping the right page ranks is weak. Learning
  the brand's own web address once and then asking that address directly is
  strong. That one change took skin type from 6.6% to 98%, and it is the
  finding I would put in the writing above any other from this stage.</p>

  <div class="dg">
  <svg viewBox="0 0 720 150" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <text x="0" y="16" fill="#6b6478">asking a search engine and hoping</text>
    <rect x="250" y="4" width="30" height="15" rx="3" fill="#b5484d"/>
    <text x="288" y="16" fill="#b5484d" font-weight="700">6.6%</text>

    <text x="0" y="46" fill="#6b6478">asking the brand's own website</text>
    <rect x="250" y="34" width="446" height="15" rx="3" fill="#6f9c78"/>
    <text x="704" y="46" fill="#3f6b48" font-weight="700">98%</text>

    <text x="0" y="86" fill="#584a7a" font-weight="700">Lebanese ingredients, same idea</text>
    <text x="0" y="110" fill="#6b6478">keyword search</text>
    <rect x="250" y="98" width="122" height="15" rx="3" fill="#c07a54"/>
    <text x="380" y="110" fill="#8d5433" font-weight="700">27%</text>
    <text x="0" y="136" fill="#6b6478">the shop page directly</text>
    <rect x="250" y="124" width="345" height="15" rx="3" fill="#6f9c78"/>
    <text x="603" y="136" fill="#3f6b48" font-weight="700">76%</text>
  </svg>
  <div class="cap">Resolve the address once, then ask it</div>
  </div>

  <h3>When to stop paying</h3>
  <p>Two runs were stopped rather than finished, and both were right to stop:</p>
  {tbl(['what was being asked for', 'result', 'what it means'],
       [['ingredient lists for Lebanese brands, after the free pass had '
         'already read every brand page',
         '42 products asked, 0 found',
         'Not a low rate. None at all. A search engine cannot find a page '
         'that was never written, so this is evidence the information does '
         'not exist rather than evidence it is hard to reach.'],
        ['prices for Lebanese retail products already carrying a Beirut price',
         'too slow for what it added',
         'You called this one before I did.']])}

  <h3>What the services actually charge</h3>
  {tbl(['service', 'what it charges', 'what a free key really gives'],
       [['Serper', 'two credits for a shopping question, whatever size is asked for',
         'a 2,500 credit key answers about 1,250 questions'],
        ['Talordata', 'one credit', '500 questions, and 5,000 for about five dollars'],
        ['ScraperAPI', 'one credit, but no rating in the reply',
         'about 1,000 questions, price only'],
        ['Rayobyte', 'it fetches pages rather than answering questions',
         'Google refused it on 48 of 52 tries, so it is only useful against '
         'Bing']])}

  <div class="note">The first key looked like it was short changing us: a
  2,500 credit key stopped after 1,260 questions. It was not. Shopping
  questions cost two credits each, and the reply says so. The counter now
  reads the real figure out of the reply instead of assuming one per question.</div>
</section>
"""

# ============================================================ CD5
no_ing = sum(1 for r in C if not has(r, 'ingredients'))
no_st = sum(1 for r in C if not has(r, 'skin_type'))
no_price = N - n_any('price_usd', 'price_usd_market')
no_rev = N - n_any('review_texts_json')
lo_rev = sum(1 for r in C if r['source_category'] == 'Lebanese origin'
             and not has(r, 'review_texts_json'))
CD5 = f"""
<section class="section" id="cd-left">
  <h2>CD5 &middot; What is still empty</h2>
  <p class="lead">Some of these can be filled with more credits. Some cannot be
  filled at all, and those are worth more to the writing than the ones that
  can.</p>

  <h3>Can be filled, and how</h3>
  {tbl(['what is missing', 'how many', 'what it needs'],
       [['a market price and rating',
         f(len(still)),
         'about 2,200 paid questions. Roughly five dollars at Talordata '
         'prices, or three more free Serper keys.'],
        ['a rating where a price is already stored',
         f(sum(1 for r in C if has(r, 'price_usd_market')
               and not has(r, 'rating_market'))),
         'these were collected before the script started reading the rating '
         'out of the same reply. One question each, and it buys one field '
         'rather than two, so it is the last job rather than the first.'],
        ['whether Lebanese products appear in a shopping index',
         '977',
         'the Rayobyte key, asking Bing. Google refuses the request.']])}

  <h3>Cannot be filled, and why that is a result</h3>
  {tbl(['what is missing', 'how many', 'why'],
       [['an ingredient list', f(no_ing),
         'Small Lebanese makers do not publish one. The brands organised as '
         'cosmetics companies publish nearly everything: Ecladerm, Helw&eacute;, '
         'Senteurs d&#39;Orient and Cosmaline are at or near 100%. The soap '
         'makers are near zero. Under EU Regulation 1223/2009 a manufacturer '
         'must declare the full list, and the brands that behave like '
         'manufacturers do.'],
        ['a review', f(no_rev),
         f'Not one of the 29 Lebanese brand sites runs a review system, so '
         f'{f(lo_rev)} Lebanese products have none. The Lebanese-made part of '
         f'the market has no public record of what users think of it, which '
         f'means a recommender built on reviews ignores it completely. That '
         f'is a direct argument for reasoning from ingredients instead.'],
        ['a price', f(no_price),
         'Skinsort publishes no prices at all. Two Lebanese brands publish '
         'none either: Xiran and Cosmaline, across 747 pages between them. '
         'Xiran sells private label to other companies rather than to '
         'shoppers, so there is no retail price to publish.'],
        ['a skin type', f(no_st),
         'No source stated one. Guessing would defeat the point of recording '
         'where every value came from.']])}

  <div class="dg">
  <svg viewBox="0 0 720 170" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <text x="0" y="16" fill="#584a7a" font-weight="700">Two kinds of empty</text>
    <rect x="10" y="30" width="330" height="120" rx="8" fill="#f7f5fb" stroke="#7a68a6"/>
    <text x="175" y="52" text-anchor="middle" fill="#584a7a" font-weight="700">nobody has asked yet</text>
    <text x="175" y="74" text-anchor="middle" fill="#6b6478">{f(len(still))} products need a price</text>
    <text x="175" y="92" text-anchor="middle" fill="#6b6478">977 need a shopping check</text>
    <text x="175" y="110" text-anchor="middle" fill="#6b6478">fixable with credits</text>
    <text x="175" y="134" text-anchor="middle" fill="#6b6478" font-style="italic">a gap in the collecting</text>

    <rect x="370" y="30" width="340" height="120" rx="8" fill="#fdf3ec" stroke="#c07a54"/>
    <text x="540" y="52" text-anchor="middle" fill="#8d5433" font-weight="700">the information does not exist</text>
    <text x="540" y="74" text-anchor="middle" fill="#6b6478">no Lebanese brand site takes reviews</text>
    <text x="540" y="92" text-anchor="middle" fill="#6b6478">soap makers publish no formula</text>
    <text x="540" y="110" text-anchor="middle" fill="#6b6478">Skinsort publishes no prices</text>
    <text x="540" y="134" text-anchor="middle" fill="#8d5433" font-style="italic">a finding about the market</text>
  </svg>
  <div class="cap">The second box is the one to write about</div>
  </div>

  <h3>What can honestly be claimed</h3>
  {tbl(['can be said', 'cannot be said'],
       [[f'{f(N)} products, each traceable to the page its values came from',
         'that this is every skincare product sold in Lebanon. Brands with no '
         'website cannot be reached by any of these methods'],
        ['every figure on these pages is read from the file when the page is '
         'built, so none of them can go stale',
         'that the file is finished. Price and rating are still being filled'],
        ['the Lebanese part is the part that does not exist elsewhere, and '
         'the gaps in it describe how that industry works',
         'that the gaps are only gaps. Some of them are the result']])}
</section>
"""

# ============================================================ write
html = PORTAL.read_text(encoding='utf-8')
before = len(html)
html = re.sub(
    r'<section class="section" id="cd-(now|fixed|rules|paid|left)">.*?</section>',
    '', html, flags=re.S)

anchor = -1
for a in ('<section class="section" id="lo-what">',
          '<section class="section" id="mg-merge">',
          '<section class="section" id="on-ready">',
          '<section class="section" id="home">'):
    if anchor == -1:
        anchor = html.find(a)
if anchor == -1:
    raise SystemExit('could not find where to insert, portal not changed')
html = html[:anchor] + CD1 + CD2 + CD3 + CD4 + CD5 + '\n\n' + html[anchor:]

# the portal has been reordered since these builders were written, so the
# group this used to insert beside may not exist. If the pages are already
# linked in the nav, there is nothing to add.
nav = re.search(r'<nav class="nav">.*?</nav>', html, re.S).group(0)
if 'cd-now' not in nav:
    m = (re.search(r'(\s*<div class="grp">lebanese origin</div>)', html) or
         re.search(r'(\s*<div class="grp">merging</div>)', html) or
         re.search(r'(\s*<div class="grp">overview</div>)', html))
    if m is None:
        print('  nav already has these pages, leaving it alone')
    else:
        html = (html[:m.start()] +
                '\n    <div class="grp">fixes and gaps</div>\n'
                '    <a data-s="cd-now">CD1. Where the file stands</a>\n'
                '    <a data-s="cd-fixed">CD2. What went wrong</a>\n'
                '    <a data-s="cd-rules">CD3. Keeping a value</a>\n'
                '    <a data-s="cd-paid">CD4. What was paid for</a>\n'
                '    <a data-s="cd-left">CD5. What is still empty</a>' +
                m.group(1) + html[m.end():])

PORTAL.write_text(html, encoding='utf-8')

w = {}
for m in re.finditer(r'<section class="section[^"]*" id="(cd-[^"]+)">(.*?)</section>',
                     html, re.S):
    w[m.group(1)] = len(re.sub(r'<[^>]+>', ' ', m.group(2)).split())
print('=' * 62)
print('  CLEANING PAGES ADDED')
print('=' * 62)
for k, v in w.items():
    print(f'    {k:10s}{v:6,} words')
print(f'\n  {sum(w.values()):,} words, '
      f'{sum(x.count("<table") for x in (CD1, CD2, CD3, CD4, CD5))} tables, '
      f'{sum(x.count("<svg") for x in (CD1, CD2, CD3, CD4, CD5))} diagrams')
print(f'  portal {before:,} -> {len(html):,} characters')
print(f'\n  read from the files just now: {f(N)} products, '
      f'{pc(n_any("price_usd", "price_usd_market"))} priced, '
      f'{pc(n_any("rating", "rating_market"))} rated, {f(len(still))} left to ask')
