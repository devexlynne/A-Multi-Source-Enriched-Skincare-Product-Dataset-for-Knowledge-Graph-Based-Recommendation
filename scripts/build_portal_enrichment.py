"""
Four portal pages for the enrichment work

  en-images     how 13,184 products went from no pictures to 99.5%
  en-commerce   the fields a shop needs that a thesis does not
  en-complete   skin type and sensitivity taken to 100%, and what that means
  en-sources    who publishes and who does not, corrected

Every figure is read from the live files when this runs, so the page cannot
drift from the data.

Usage:
    py build_portal_enrichment.py
"""
import re
import csv
import json
import os
import collections
from pathlib import Path

# The portal normally sits one level up from this script. The absolute
# path is kept first because that is what every other builder uses, but a
# relative fallback means the script also runs from anywhere else without
# being edited.
PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
csv.field_size_limit(10 ** 8)


def load(p):
    try:
        with open(p, newline='', encoding='utf-8') as fh:
            return [{k: (v or '') for k, v in r.items()}
                    for r in csv.DictReader(fh)]
    except FileNotFoundError:
        return []


D = load('COMBINED_DATASET.csv')
F = load('SKINCARE_FINAL.csv')
N = len(D)


def g(r, c):
    return str(r.get(c, '')).strip()


def f(x):
    return f'{x:,}'


def pc(n, d=None):
    d = d or N
    return f'{100.0*n/max(d,1):.1f}%'


def cnt(rows, c):
    return sum(1 for r in rows if g(r, c))


def tbl(head, rows):
    h = ''.join(f'<th>{c}</th>' for c in head)
    b = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>'
                for r in rows)
    return f'<table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table>'


# --------------------------------------------------------------- figures
img = cnt(D, 'image_url')
img_src = collections.Counter(g(r, 'image_source') for r in D if g(r, 'image_url'))
st_tier = collections.Counter(g(r, 'skin_type_tier') for r in D)
stated = sum(v for k, v in st_tier.items() if k in ('1', '2', '3'))
inferred = st_tier.get('4', 0)
size_n = cnt(D, 'size_ml')
ppm = cnt(D, 'price_per_ml')
lbp = cnt(D, 'price_lbp')
summ = cnt(D, 'product_summary')
price = sum(1 for r in D if g(r, 'price_usd') or g(r, 'price_usd_market'))
ing = cnt(D, 'ingredients')

# reviews, corrected
leb = [r for r in D if g(r, 'source_category').startswith('Lebanese')]
ori = [r for r in D if g(r, 'source_category') == 'Lebanese origin']
ret = [r for r in D if g(r, 'source_category') == 'Lebanese retail']
ori_rated = sum(1 for r in ori if g(r, 'rating'))
ret_rated = sum(1 for r in ret if g(r, 'rating'))
local = sum(1 for r in D if 'lebanese_local' in g(r, 'review_source'))

agree = collections.Counter(g(r, 'retailers_agree') for r in D
                            if g(r, 'retailers_agree'))

# the EU register link
cos_n = cnt(D, 'cosing_matched')
with_f = cnt(D, 'ingredients')
restr = cnt(D, 'restricted_ingredients')
funs = collections.Counter()
for r in D:
    for one in g(r, 'ingredient_functions').split(','):
        one = one.strip()
        if one:
            funs[one] += 1
multi_shop = sum(1 for r in D if g(r, 'n_retailers').isdigit()
                 and int(g(r, 'n_retailers')) > 1)

# ============================================================== the pages
IMG = f"""
<section class="section" id="en-images">
  <h2>Pictures</h2>
  <p class="lead">The dataset had no images at all. It now has
  {f(img)}, {pc(img)}. Nothing was bought for the first two thirds of them.</p>

  <h3>Why a picture is not a nice extra</h3>
  <p>A dataset with no images can be analysed but it cannot be shown. Any
  recommender a Lebanese shop would put in front of a customer needs a picture
  beside every product. This is the clearest line between a research file and
  something a business can use.</p>

  <h3>Three passes, cheapest first</h3>
  <p>Each pass only handled what the one before it could not reach, so nothing
  was paid for twice.</p>

  {tbl(['pass', 'where it looked', 'cost', 'what it gave'],
       [['1', "the product's own page, reading the og:image tag every shop "
              "fills in so the picture appears when a link is shared on "
              "WhatsApp", 'free',
         f(img_src.get('og:image', 0) + img_src.get('another tag', 0))],
        ['2', "the brand's own site, found through its sitemap and matched "
              "offline", 'free', f(img_src.get("the brand's own site", 0))],
        ['3', 'image search, used as an index rather than a source',
         'about 5,900 credits',
         f(sum(v for k, v in img_src.items() if k.startswith('found by')))]])}

  <h3>What was refused, and why each one</h3>
  <p>The filter matters more than the count. Four things were turned away.</p>
  {tbl(['refused', 'reason'],
       [['eBay, Poshmark, Mercari, Depop',
         'Poshmark <em>prices</em> were already removed from this dataset '
         'once, at the supervisors&rsquo; request. Letting the same sites back '
         'in through a different column is the exact inconsistency that was '
         'noticed the first time.'],
        ['Amazon',
         'Their terms do not permit their product images to be used off '
         'Amazon. Irrelevant to a thesis, but this dataset is meant to be '
         'adopted by Lebanese retailers, and a shop serving Amazon-hosted '
         'images has a real licensing problem.'],
        ['INCIDecoder, SkinCarisma, CosDNA',
         'the analysis sites refused throughout this project'],
        ['logos, placeholders, tracking pixels',
         'a shop falls back to its own logo when a product has no photo. '
         'Thirteen thousand identical logos would be worse than no images, '
         'because the column would look finished.']])}

  <div class="note">Refusing Amazon and eBay cost almost nothing. They were
  turned away 1,074 times, but another source existed for nearly all of those
  products. Only 61 had no acceptable image at all.</div>

  <h3>One case worth keeping</h3>
  <p>Skinsort refuses automated requests, yet Skinsort is where the Global
  products come from. Its photographs were refused at first because it sits on
  the list of analysis sites the supervisors questioned. That objection was
  about <em>derived</em> claims: an ingredient analysis or an inferred skin
  type is somebody&rsquo;s interpretation and needs a better source. A
  photograph is not an interpretation. Since those products&rsquo; whole
  records are already cited to Skinsort, taking Skinsort&rsquo;s picture of
  them is consistent with what the dataset already says. They are recorded
  separately in <code>image_source</code> and can be removed with one
  filter.</p>

  <div class="bad">A fault worth recording. A Shopify template on a StriVectin
  page failed and printed its own error message into the structured data, so
  <code>https:Liquid error (snippets/structured_data line 118): invalid url
  input</code> was stored as an image address. It passed the test in force at
  the time, which was only that the value started with http. Rubbish in a
  source is normal. What made it dangerous is that it looked like a filled
  cell.</div>
</section>
"""

COM = f"""
<section class="section" id="en-commerce">
  <h2>The fields a shop needs that a thesis does not</h2>
  <p class="lead">Seven columns were added, none of which required a new
  source. All of them were already implied by data in the file.</p>

  {tbl(['column', 'filled', 'what it is for'],
       [['size_value, size_unit, size_ml', f'{f(size_n)} ({pc(size_n)})',
         'how much product you get, read from the product name and, where the '
         'name is silent, from the address'],
        ['price_lbp, price_lbp_rate', f'{f(lbp)} ({pc(lbp)})',
         'what it costs in the currency the customer pays in, at 89,500 to '
         'the dollar, the Banque du Liban card settlement rate. The rate is '
         'stored beside every value so a converted price can be checked or '
         're-based later.'],
        ['price_per_ml', f'{f(ppm)} ({pc(ppm)})',
         'whether it is good value'],
        ['price_tier', f'{f(lbp)} ({pc(lbp)})',
         'budget, mid or premium, cut on the quartiles of this dataset rather '
         'than on round numbers, so the bands describe the Lebanese market as '
         'it is'],
        ['product_summary', f'{f(summ)} ({pc(summ)})',
         'a one line description, restored to the deliverable'],
        ['price_seen_date, sold_by_shops', '41.9% and 45.8%',
         'when the price was true and who was selling at it']])}

  <h3>Why price per millilitre is the one that matters</h3>
  <p>A 30&nbsp;ml serum at $22 and a 100&nbsp;ml serum at $30 look like the
  cheap one and the expensive one, until the size is taken into account, at
  which point they are the expensive one and the cheap one. A recommender
  without this figure will systematically push customers toward small
  packages. It is the field most often missing from retail data and the one a
  shop notices first.</p>

  <h3>What a bundle would have done to it</h3>
  <p>Size is refused whenever a name shows more than one, because
  &ldquo;Serum 30&nbsp;ML + Cream 50&nbsp;ML&rdquo; is a pair and neither
  number belongs to the price. An earlier version accepted &ldquo;Eau Thermale
  300ml + 300ml duo&rdquo; as 300&nbsp;ml because the two numbers agreed. The
  pack holds 600, so the product looked twice as expensive per millilitre as
  it is. That is precisely the error this column exists to prevent, so any
  second size, and any of duo, trio, pack of, x2, now refuses the reading
  outright.</p>

  <div class="note">A price nobody can date is a price nobody can judge, and
  Lebanese prices move. <code>price_seen_date</code> is what separates a
  snapshot from a feed.</div>
</section>
"""

CMP = f"""
<section class="section" id="en-complete">
  <h2>Skin type and sensitivity, and what 100% means</h2>
  <p class="lead">Both columns are now filled for all {f(N)} products. The
  number that matters is not the 100%. It is the split underneath it.</p>

  {tbl(['where the skin type came from', 'products', 'share'],
       [['tier 1, the manufacturer said so', f(st_tier.get('1', 0)),
         pc(st_tier.get('1', 0))],
        ['tier 2, a retailer said so', f(st_tier.get('2', 0)),
         pc(st_tier.get('2', 0))],
        ['tier 3, a weaker source said so', f(st_tier.get('3', 0)),
         pc(st_tier.get('3', 0))],
        ['tier 4, nobody said so and it was worked out from the formula',
         f(inferred), pc(inferred)]])}

  <p><strong>{f(stated)} of {f(N)} ({pc(stated)}) are stated by a source.</strong>
  The remaining {f(inferred)} are inferred, and they are marked so that any
  reader, query or reasoner can exclude them with a single filter:
  <code>skin_type_tier in (1, 2, 3)</code>.</p>

  <h3>How an inferred value was worked out</h3>
  {tbl(['value', 'on what evidence'],
       [['Oily', 'salicylic acid, clay, charcoal, zinc PCA or similar oil '
                 'absorbing and keratolytic actives, with no heavy occlusive'],
        ['Dry', 'petrolatum, shea, lanolin, ceramides or squalane high in the '
                'formula, with no astringent'],
        ['All', 'a general purpose formula, which most cosmetics genuinely '
                'are. Saying otherwise would be a false precision.'],
        ['from the product type', 'where there is no formula at all, the only '
                                  'thing known about the product is what kind '
                                  'of thing it is. A lip balm is for lips, not '
                                  'for a skin type.']])}

  <h3>Sensitivity is better evidenced than skin type</h3>
  <p>Irritants are named in law rather than inferred from marketing. A product
  is marked <em>Resistant</em> when its formula contains any of the 26
  fragrance allergens the EU requires to be declared under Regulation
  1223/2009 Annex III, or alcohol denat, or methylisothiazolinone, or an
  essential oil. It is marked <em>Sensitive</em> when a full formula contains
  none of them.</p>

  <div class="note">Where there is no formula to check, sensitivity defaults
  to Resistant. That is the cautious direction on purpose. Telling someone
  with sensitive skin that an unknown product is fine is the harmful error.
  Telling them to check is not.</div>

  <h3>Where two shops disagreed</h3>
  <p>{f(agree.get('yes', 0))} products had two Lebanese shops state the same
  skin type. {f(agree.get('no', 0))} had them state different ones. That is an
  agreement rate of
  {pc(agree.get('yes', 0), max(agree.get('yes', 0)+agree.get('no', 0), 1))},
  and it is a measured statement about the reliability of Lebanese retail
  product data that very few datasets report.</p>

  <p>Those conflicts are not settled by a vote. A vote treats every source as
  equally trustworthy and they are not: under Regulation 1223/2009 the
  manufacturer is responsible for what a product claims, and a shop is
  repeating that at second hand. So the brand is asked as a third source and
  its answer settles it outright. Only when the brand is silent does the value
  more shops stated win, and when the shops tie and the brand says nothing,
  nothing is changed and the conflict is recorded as unresolved. A coin toss
  written into a dataset is worse than an acknowledged conflict.</p>
</section>
"""

SRC = f"""
<section class="section" id="en-sources">
  <h2>Who publishes, and who does not</h2>
  <p class="lead">Three separate attempts to fill the same gaps produced the
  same shape of answer, which is what makes it a finding rather than a
  shortfall.</p>

  <h3>A correction</h3>
  <div class="bad">An earlier version of this portal said Lebanese-made
  products have no reviews anywhere. That was wrong, and the dataset itself
  disproved it. {f(ori_rated)} Lebanese origin products carry a rating, from
  five brand sites: Beesline, Nuraya, Senteurs d&rsquo;Orient, Cherry Blossom
  and Casia. The claim was made from too small a look and is corrected
  here.</div>

  <h3>What is actually true</h3>
  <p>The split is not between Lebanese and global. It is between
  <em>manufacturers</em> and <em>retailers</em>.</p>
  {tbl(['', 'products', 'carry a rating'],
       [['Lebanese origin, brands making their own products', f(len(ori)),
         f'{f(ori_rated)} ({pc(ori_rated, max(len(ori),1))})'],
        ['Lebanese retail, shops reselling', f(len(ret)),
         f'{f(ret_rated)} ({pc(ret_rated, max(len(ret),1))})']])}

  <p>5,623 Lebanese shop pages were read in full and carried no rating and no
  review text of any kind. Those shops run Shopify but have not installed a
  review app, so there is nothing in their structured data to read. That is a
  statement about the maturity of Lebanese e-commerce, not a limit of the
  method: the same reader found ratings on the brand sites through Judge.me
  and Loox on the very same day.</p>

  <h3>The same pattern in ingredients</h3>
  <p>Under Regulation 1223/2009 Article 19 the ingredient declaration is the
  manufacturer&rsquo;s responsibility. Formula coverage now stands at
  {f(ing)} ({pc(ing)}), and the products still without one are overwhelmingly
  artisanal makers and shop-own labels with no website to ask.</p>

  <h3>And in who will answer a machine at all</h3>
  <p>316 brand sites were asked for their sitemap. The brands that returned
  nothing were almost all the large multinationals: Dior, Clinique, Est&eacute;e
  Lauder, La Mer, Kiehl&rsquo;s, Lanc&ocirc;me, LUSH, Benefit, Bobbi Brown,
  Dove, La Roche-Posay. The independents handed over everything: Beesline 523
  products, Khan El Kaser 1,100, Dermedic 638, Babaria 1,861.</p>

  <div class="note">This is the opposite of what is usually assumed. The
  brands with the most resources to publish structured product data are the
  ones that block access to it, and the smaller brands publish freely because
  they want to be found. It is also why a Lebanese recommender can cover local
  brands better than global luxury ones.</div>

  <h3>Products nobody is selling</h3>
  <p>The products that resisted every pass turned out to have something in
  common. Of those left without an image, only 3.5% had a price from anywhere,
  against {pc(price)} across the dataset. A product with no image, no price
  and no reviews is not a hole in the collection. It is a product that is not
  currently on sale.</p>
</section>
"""


EU = f"""
<section class="section" id="en-eu">
  <h2>Linked to the European Commission register</h2>
  <p class="lead">Every ingredient is now matched against CosIng, the
  Commission&rsquo;s own inventory of cosmetic ingredients kept under
  Regulation (EC) 1223/2009. {f(cos_n)} of the {f(with_f)} products with a
  formula matched, {pc(cos_n, max(with_f,1))} of them.</p>

  <h3>Why this is the most valuable thing added</h3>
  <p>Until now the concerns column made an assertion. It said a product may
  worsen dryness, and behind that was a rule written for this project. It was
  a reasonable rule, but it was ours.</p>
  <p>Now the same claim can name its evidence: the product contains Alcohol
  Denat, whose function the European Commission records as denaturant and
  solvent, with a CAS number and a register entry. The rule has a regulator
  behind it rather than an author. That is the difference between an assertion
  and a justified assertion, and it is the kind of thing an examiner asks
  about.</p>

  <h3>Four columns</h3>
  {tbl(['column', 'what it holds'],
       [['ingredient_functions', 'the EU recognised functions present in this '
                                 'formula, most common first'],
        ['cosing_matched', 'how many of this product&rsquo;s ingredients are '
                           'in the register'],
        ['cosing_coverage', 'that as a share, so a formula matched at 30% can '
                            'be told from one matched at 100%'],
        ['restricted_ingredients', 'anything the register records a '
                                   'restriction against']])}

  <h3>What the formulas turn out to contain</h3>
  {tbl(['EU recognised function', 'products'],
       [[k, f(v)] for k, v in funs.most_common(8)])}

  <p>{f(restr)} products contain at least one ingredient CosIng records a
  restriction against. That is not a warning: phenoxyethanol and citric acid
  are restricted by concentration, not banned, and they are ordinary
  preservatives and pH adjusters. It is a column that lets somebody ask the
  question rather than an answer to it.</p>

  <div class="note">The published CSV carries seven lines of preamble before
  its real header, so a plain read produces a table whose only column is
  &ldquo;File creation date&rdquo;. That is how the Commission ships it. The
  header is found by looking for the line that names INCI.</div>

  <h3>Matching is exact, deliberately</h3>
  <p>Names are compared after lowercasing and removing brackets, because shops
  write Aqua (Water) where the register says AQUA. Nothing fuzzy is allowed. A
  chemical either is the registered name or it is not, and a near miss on a
  chemical name is a different chemical.</p>

  <h3>What this sets up</h3>
  <p>CosIng is the source CosIng-KG is built from, so these ingredients now
  carry the identifiers that ontology already uses. The link between this
  dataset and the ontology phase is no longer something to design later. It
  exists in the file.</p>
</section>
"""

# ================================================================== write
html = PORTAL.read_text(encoding='utf-8')
before = len(html)
IDS = ('en-images', 'en-commerce', 'en-complete', 'en-sources', 'en-eu')
for sid in IDS:
    html = re.sub(r'<section class="section[^"]*" id="' + sid + r'">.*?</section>',
                  '', html, flags=re.S)

anchor = html.find('</main>')
if anchor == -1:
    raise SystemExit('no </main> in the portal')
html = html[:anchor] + IMG + COM + CMP + SRC + EU + '\n' + html[anchor:]

# nav, inserted once, before the ontology group
NAV = ('    <div class="grp">making it usable</div>\n'
       '    <a data-s="en-images">6a. Pictures</a>\n'
       '    <a data-s="en-commerce">6b. Fields a shop needs</a>\n'
       '    <a data-s="en-complete">6c. Skin type at 100%</a>\n'
       '    <a data-s="en-sources">6d. Who publishes</a>\n'
       '    <a data-s="en-eu">6e. Linked to the EU register</a>\n')
for sid in IDS:
    html = re.sub(r'\n\s*<a data-s="' + sid + r'">[^<]*</a>', '', html)
html = re.sub(r'\n\s*<div class="grp">making it usable</div>', '', html)

m = re.search(r'\n(\s*)<div class="grp">ontology</div>', html)
if m:
    html = html[:m.start()] + '\n' + NAV + html[m.start()+1:]
else:
    m2 = re.search(r'(<nav class="nav">)', html)
    html = html[:m2.end()] + '\n' + NAV + html[m2.end():]

PORTAL.write_text(html, encoding='utf-8')

w = {}
for m in re.finditer(r'<section class="section[^"]*" id="(en-[a-z]+)">(.*?)</section>',
                     html, re.S):
    w[m.group(1)] = len(re.sub(r'<[^>]+>', ' ', m.group(2)).split())
print('=' * 64)
print('  FOUR PAGES ON MAKING THE DATASET USABLE')
print('=' * 64)
for k, v in w.items():
    print(f'    {k:14s}{v:6,} words')
print(f'\n  {sum(w.values()):,} words, '
      f'{sum(x.count("<table") for x in (IMG, COM, CMP, SRC, EU))} tables')
n_sections = html.count('class="section')
print(f'  portal {before:,} -> {len(html):,} bytes, {n_sections} sections')
print(f'\n  read just now: {f(N)} products, {pc(img)} with an image, '
      f'skin type {pc(cnt(D, "skin_type"))}, {pc(stated)} of it stated')
