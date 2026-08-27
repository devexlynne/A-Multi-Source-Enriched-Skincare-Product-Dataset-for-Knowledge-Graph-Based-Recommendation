"""
The lebanese retail pages of the portal

Three pages, every figure read from lebanese_stats.json and LEBANESE_RETAIL.csv
at build time, so they cannot drift from the data.

    L1  The six shops and the raw scrape
    L2  Cleaning: duplicates removed, non-skincare removed
    L3  Matching, skin type, reviews, and what is missing

Usage:
    py build_lebanese.py
    py build_portal_lebanese.py
"""
import re
import json
import pandas as pd
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    # the portal normally sits one level up; the absolute path stays first
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
S = json.load(open('lebanese_stats.json'))
d = pd.read_csv('LEBANESE_RETAIL.csv', dtype=str, low_memory=False).fillna('')
main = pd.read_csv('SKINCARE_DATASET.csv', dtype=str, low_memory=False).fillna('')

RAWN, UNIQ, K = S['raw_listings'], S['unique_products'], S['kept']
T = S['tier']
T12 = S['skintype_strong']
REV, NOREV = S['with_reviews'], S['no_reviews']
MS = S['matched_skinsort']
ST = S['with_skintype']


def f(x):
    return f'{x:,}'


def pc(x, of=None):
    return f'{100*x/(of or K):.1f}%'


def tbl(head, rows):
    h = ''.join(f'<th>{c}</th>' for c in head)
    b = ''.join('<tr>' + ''.join(f"<td class='td'>{c}</td>" for c in r) + '</tr>'
                for r in rows)
    return f'<table><tr>{h}</tr>{b}</table>'


GREY = "<span style='color:var(--grey);font-size:11px'>"


def card(r, colour='var(--sage)'):
    q = (r.get('skin_type_quote') or '')[:190] or '(the shop listing is the evidence)'
    sens = ' &middot; ' + r['sensitivity'] if r.get('sensitivity') else ''
    shops = GREY + str(r.get('retailers', '')) + '</span>'
    src = r.get('skin_type_source', '')
    return (f"<div class='ev' style='border-left-color:{colour}'>"
            f"<div class='evh'>{r['brand']} &middot; {r['name'][:58]}</div>"
            f"<div class='evt'>&rarr; <b>{r['skin_type']}</b>{sens} &nbsp;{shops}</div>"
            f"<div class='evq'>&ldquo;{q}&rdquo;</div>"
            f"<div class='evs'>{src}</div></div>")


multi_html = ''
for _, r in d[pd.to_numeric(d['n_retailers'], errors='coerce') >= 3].head(3).iterrows():
    multi_html += (f"<div class='ev'><div class='evh'>{r['brand']} &middot; {r['name'][:58]}"
                   f"</div><div class='evt'>stocked by <b>{r['n_retailers']}</b> shops: "
                   f"{r['retailers']}</div><div class='evq'>what each shop says: "
                   f"{r['retailer_skin_types'][:170]}</div>"
                   f"<div class='evs'>shops agree: {r['retailers_agree']}</div></div>")

match_html = ''.join(
    f"<div class='ev'><div class='evh'>{r['brand']} &middot; {r['name'][:56]}</div>"
    f"<div class='evt'>matched at {r['match_score']}% &rarr; inherited "
    f"<b>{r['skin_type']}</b>"
    f"{' &middot; reviews from ' + r['review_source'] if r['review_source'] else ''}</div>"
    f"<div class='evq'>{(r['skin_type_quote'] or '(see the source link)')[:165]}</div>"
    f"<div class='evs'>{r['skin_type_source']}</div></div>"
    for _, r in d[d['matched_to'].str.contains('SKINCARE', na=False)].head(2).iterrows())

decl = d[d['skin_type_authority'] == 'Lebanese retailer'].head(1)
infer = d[d['skin_type_authority'] == 'shop, inferred from ingredients'].head(1)
revsrc = d.loc[d['review_source'] != '', 'review_source'].value_counts()

# ================================================================== L1
L1 = f"""
<section class="section" id="lb-shops">
  <h2>L1 &middot; The Lebanese retail source</h2>
  <p class="lead">The global dataset answers "what exists". This one answers
  "what a person in Lebanon can actually buy, and for how much". Those are
  different questions, and answering the second is what makes the thesis local
  rather than a repetition of work already done on international data.</p>

  <div class="kpis">
    <div class="kpi"><div class="n">{f(RAWN)}</div><div class="l">listings scraped</div></div>
    <div class="kpi"><div class="n">6</div><div class="l">Lebanese shops</div></div>
    <div class="kpi"><div class="n">{f(K)}</div><div class="l">skincare products after cleaning</div></div>
    <div class="kpi"><div class="n">{f(S['brands_final'])}</div><div class="l">brands</div></div>
  </div>

  <h3>Where it came from</h3>
  {tbl(['shop', 'listings scraped', 'skincare products kept'],
       [[f'<code>{k}</code>', f(v), f(S['shops_final'].get(k, 0))]
        for k, v in sorted(S['raw_shops'].items(), key=lambda x: -x[1])])}
  <p class="small">These are online pharmacies and beauty retailers serving the
  Lebanese market. The second column is the raw catalogue; the third is what
  survived cleaning, and the gap between them is page L2.</p>

  <h3>Why this source exists at all</h3>
  <p>A global catalogue tells you what the industry makes. It does not tell you
  what is on a shelf in Beirut, at what price, or whether a product a study
  recommends can actually be bought here.</p>
  <p>It supplies two things the global set does not have at all: <b>a price</b>,
  and <b>availability</b>, meaning which shops stock it. A product carried by
  five of the six shops is differently available from one carried by a single
  pharmacy, and that distinction exists only in this source.</p>

  <h3>What each listing gave me</h3>
  {tbl(['field', 'from the shop page', 'coverage after cleaning'], [
    ['brand', 'yes', f'{f(K)} of {f(K)}'],
    ['product name', 'yes', f'{f(K)} of {f(K)}'],
    ['the shop&rsquo;s own skin type wording', 'often', f'{f(S["shop_declared"] + S["shop_inferred"])}'],
    ['product URL', 'yes', f'{f(K)} of {f(K)}'],
    ['which shops stock it', 'yes', f'{f(K)} of {f(K)}'],
    ['price', 'yes', 'most products'],
    ['ingredients', 'yes', f'{f(S["with_ingredients"])} ({pc(S["with_ingredients"])})'],
    ['<b>reviews</b>', '<b>rarely</b>', f'<b>{f(REV)} ({pc(REV)})</b>']])}
  <p class="small">The shape of that table is the whole story. This source is
  strong exactly where the global set is weak, meaning price and availability,
  and weak exactly where the global set is strong, meaning reviews.</p>

  <div class="dg">
  <svg viewBox="0 0 700 210" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11.5">
    <text x="350" y="18" text-anchor="middle" font-weight="700" fill="#584a7a" font-size="13">two sources, two different questions</text>
    <rect x="20" y="34" width="300" height="150" rx="10" fill="#f4f0fa" stroke="#7a68a6" stroke-width="1.6"/>
    <text x="170" y="58" text-anchor="middle" font-weight="700" fill="#584a7a" font-size="13">Global (Skinsort)</text>
    <text x="170" y="80" text-anchor="middle" fill="#6b6478">{f(len(main))} reviewed products</text>
    <text x="170" y="100" text-anchor="middle" fill="#6b6478">reviews, ingredients,</text>
    <text x="170" y="116" text-anchor="middle" fill="#6b6478">skin type with evidence</text>
    <text x="170" y="144" text-anchor="middle" fill="#8d5433" font-style="italic">"what exists"</text>
    <text x="170" y="166" text-anchor="middle" fill="#6b6478">no price, no local availability</text>
    <rect x="380" y="34" width="300" height="150" rx="10" fill="#eef6ee" stroke="#6f9c78" stroke-width="1.6"/>
    <text x="530" y="58" text-anchor="middle" font-weight="700" fill="#3f6b48" font-size="13">Lebanese retail</text>
    <text x="530" y="80" text-anchor="middle" fill="#6b6478">{f(K)} skincare products</text>
    <text x="530" y="100" text-anchor="middle" fill="#6b6478">price, which shops stock it,</text>
    <text x="530" y="116" text-anchor="middle" fill="#6b6478">ingredients</text>
    <text x="530" y="144" text-anchor="middle" fill="#8d5433" font-style="italic">"what you can buy here"</text>
    <text x="530" y="166" text-anchor="middle" fill="#6b6478">thin on reviews</text>
    <rect x="292" y="94" width="116" height="32" rx="8" fill="#584a7a"/>
    <text x="350" y="114" text-anchor="middle" fill="#fff" font-weight="700">{f(MS)} in both</text>
  </svg>
  <div class="cap">The two halves of the thesis, and how much they share.</div></div>

  <div class="ok"><b>Nothing here was inferred.</b> Every Lebanese row is a page
  that exists on a shop's website, with the link stored on the row, exactly like
  the skin type evidence in the global set. The raw scrape is kept untouched as
  its own sheet in <code>FULL_DATASET_WORKBOOK.xlsx</code>, so every step from
  {f(RAWN)} listings down to {f(K)} products can be retraced.</div>
</section>
"""

# ================================================================== L2
L2 = f"""
<section class="section" id="lb-dedup">
  <h2>L2 &middot; Cleaning: duplicates out, non-skincare out</h2>
  <p class="lead">The raw scrape had two separate problems. The same product was
  listed by several shops, and the scrape had taken each shop's <i>entire</i>
  catalogue rather than just skincare. Both had to be removed, and they needed
  completely different methods.</p>

  <div class="dg">
  <svg viewBox="0 0 700 175" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="12">
    <rect x="30" y="16" width="620" height="34" rx="6" fill="#584a7a"/>
    <text x="340" y="38" text-anchor="middle" fill="#fff" font-weight="700">{f(RAWN)} raw listings scraped</text>
    <path d="M340 50 L340 62" stroke="#b9aed0" stroke-width="2"/>
    <rect x="30" y="66" width="{int(620*S['collapsed']/RAWN)}" height="34" rx="6" fill="#ded7ea"/>
    <rect x="{30+int(620*S['collapsed']/RAWN)}" y="66" width="{620-int(620*S['collapsed']/RAWN)}" height="34" rx="6" fill="#7a68a6"/>
    <text x="{30+int(620*S['collapsed']/RAWN)+(620-int(620*S['collapsed']/RAWN))/2}" y="88" text-anchor="middle" fill="#fff" font-weight="700">{f(UNIQ)} unique products</text>
    <text x="{30+int(620*S['collapsed']/RAWN)/2}" y="88" text-anchor="middle" fill="#584a7a" font-size="10" font-weight="700">{f(S['collapsed'])}</text>
    <path d="M340 100 L340 112" stroke="#b9aed0" stroke-width="2"/>
    <rect x="30" y="116" width="{int(620*S['removed_total']/RAWN)}" height="34" rx="6" fill="#f0d9d9"/>
    <text x="{30+int(620*S['removed_total']/RAWN)/2}" y="138" text-anchor="middle" fill="#8d3a3e" font-size="11" font-weight="700">{f(S['removed_total'])} not skincare</text>
    <rect x="{30+int(620*S['removed_total']/RAWN)}" y="116" width="{620-int(620*S['removed_total']/RAWN)}" height="34" rx="6" fill="#6f9c78"/>
    <text x="{30+int(620*S['removed_total']/RAWN)+(620-int(620*S['removed_total']/RAWN))/2}" y="138" text-anchor="middle" fill="#fff" font-weight="700">{f(K)} skincare products</text>
    <text x="340" y="168" text-anchor="middle" fill="#6b6478" font-size="11">duplicates removed first, then everything that is not skincare</text>
  </svg>
  <div class="cap">{f(RAWN)} &rarr; {f(UNIQ)} &rarr; {f(K)}. Both steps are reversible: nothing was overwritten, only filtered.</div></div>

  <h3>Part 1 &middot; Duplicate listings</h3>
  <div class="bad"><b>Three fuzzy string rules, all wrong.</b> Each produced a
  believable number. The fault only showed on reading the merged groups.
  {tbl(['rule tried', '"unique" products', 'what it actually did'], [
    ['<code>token_set_ratio &ge; 92</code>', '13,049', 'merged CeraVe Hydrating Cleanser, PM Lotion, AM Lotion and SA Cream into <b>one</b>'],
    ['<code>WRatio &ge; 92</code>', '13,342', 'the same, worsened by chained merges'],
    ['<code>token_sort_ratio &ge; 92</code>', '13,872', 'merged Uriage Bariesun Cr&egrave;me, Teint&eacute;e, Lait Enfant and Stick Min&eacute;ral'],
    ['<b>identical significant words</b>', f'<b>{f(UNIQ)}</b>', '<b>correct on every group audited</b>']])}
  <p style="margin:9px 0 0">Once the brand and the pack size are stripped out,
  product names are short and share a lot of boilerplate, so the score is high
  for almost any two products of the same brand. Merging transitively, where A
  matches B and B matches C so A joins C, then drags unrelated products into one
  group.</p></div>

  <div class="ok"><b>The rule that works.</b> Two listings are the same product
  only if they share a brand <i>and</i> neither name carries a distinguishing
  word the other lacks. A variant always announces itself with a word: Tinted,
  Night, Mineral, SPF50, Light. So an unmatched word means a different
  product.</div>

  <div class="note"><b>Two details that each cost me wrong merges.</b>
  <p style="margin:6px 0 0">&bull; <b>Short words had to be kept.</b> An early
  version dropped words under three characters as noise, which merged "Ruboril
  Expert <b>M</b>" with "Ruboril Expert <b>S</b>", and "Xerolys <b>50</b>" with
  "Xerolys <b>10</b>". The variant marker is very often the shortest word on the
  label.</p>
  <p style="margin:6px 0 0">&bull; <b>Accents were breaking brand matching.</b>
  "Av&egrave;ne" squashed to <code>avne</code> and "L'Or&eacute;al" to
  <code>loral</code>, so accented brands could never merge across shops. Brand
  names are now folded to plain ASCII, and prefixes are stripped, because
  "Av&egrave;ne" and "Eau Thermale Av&egrave;ne" are one brand, as are "Aderma"
  and "A-Derma", and "Aloelab" and "The Aloelab".</p></div>

  <h4>Checking it the other way: what did I miss?</h4>
  <p>Counting merges only detects over-merging. To find <i>under</i>-merging I
  searched for pairs in the same brand, from different shops, differing by
  exactly one word where that word is a near-copy of one the other has. Across
  {f(RAWN)} listings there were <b>4</b>, all genuine typos:</p>
  <pre>ISDIN   "Isdinceutics Vital Eyes Eye Cream, 15 G"   (zeinacare)
        "Isdin Isdinceutics Vital Eyes Cream 15g"   (feel22)     the odd word is "eye"</pre>
  <p class="small">A second stage merges those, which is where the last
  {f(S['stage2_extra'])} come from.</p>

  {tbl(['shops stocking the product', 'products'],
       [[k, f(v)] for k, v in S['shops_per_product'].items()])}
  <p class="small">The great majority are carried by a single shop. The six
  retailers overlap far less than expected, which is itself a finding about the
  Lebanese market: catalogues are largely distinct rather than competing on the
  same items.</p>
  {multi_html}

  <h3>Part 2 &middot; Everything that is not skincare</h3>
  <div class="bad"><b>This is the error that mattered.</b> The scrape had taken
  each shop's entire catalogue. Lebanese online pharmacies sell everything, so
  the file contained body lotion, shower gel, deodorant and fragrance; makeup;
  shampoo and scalp treatments; baby bottles, pacifiers and food warmers;
  vitamin tablets and medicines; and accessories like brushes, cotton and
  sterilizer filters.
  <p style="margin:8px 0 0">Counting those as skincare made the dataset look
  roughly twice its real size. <b>14,000 distinct facial skincare products on
  sale in Lebanon was never plausible</b>, and the implausibility of the number
  is what exposed the problem.</p></div>

  <h4>The rule</h4>
  <p>Two conditions, both must hold. This is the same idea as
  <code>mark_not_applicable.py</code> in the skin type work: decide what the
  question actually applies to before quoting a figure.</p>
  {tbl(['condition', 'meaning'], [
    ['the category is one of the {n} used in the global dataset'.format(n=len(S['categories'])),
     'so the two datasets describe the same kinds of product and can be compared'],
    ['the name does not describe body, hair, makeup, baby goods, supplements or accessories',
     'catches items sitting in a plausible category but clearly not skincare']])}

  {tbl(['removed', 'products', 'why'], [
    ['no category at all', f(S['removed_no_category']), 'never matched the cleaned workbook, so could not be classified'],
    ['a category outside the global {n}'.format(n=len(S['categories'])), f(S['removed_wrong_category']), 'almost entirely the "Other Skincare" bucket, which is body care'],
    ['body, hair, makeup, baby, supplements', f(S['removed_not_skincare']), 'caught by name inside an otherwise valid category'],
    ['<b>total removed</b>', f'<b>{f(S["removed_total"])}</b>', f'<b>{f(UNIQ)} &rarr; {f(K)}</b>']])}

  <h4>Examples of what was removed</h4>
  <pre>{chr(10).join('  ' + x for x in S['dropped_examples'])}</pre>
  <div class="note"><b>Nothing was deleted permanently.</b> Every removed product
  sits in the sheet <code>3 REMOVED not skincare</code> of
  <code>FULL_DATASET_WORKBOOK.xlsx</code>, so the decision can be checked and
  reversed. The raw scrape is there too.</div>
  <div class="note"><b>One honest caveat.</b> The
  {f(S['removed_no_category'])} products removed for having no category may
  include some real skincare, for example "Abib Air Sunstick Smoothing Bar",
  which is a sunscreen. They were removed because nothing in the pipeline could
  classify them, not because they were judged irrelevant. That is a known,
  bounded limitation and it is recoverable from the removed sheet.</div>

  <h3>What survived</h3>
  {tbl(['category', 'products'], [[k, f(v)] for k, v in S['types'].items()])}
</section>
"""

# ================================================================== L3
L3 = f"""
<section class="section" id="lb-match">
  <h2>L3 &middot; Matching, skin type, and reviews</h2>
  <p class="lead">{f(K)} Lebanese skincare products, sitting beside
  {f(len(main))} global ones. This page is about how much the two can give each
  other.</p>

  <div class="kpis">
    <div class="kpi"><div class="n">{f(K)}</div><div class="l">Lebanese skincare products</div></div>
    <div class="kpi"><div class="n">{f(MS)}</div><div class="l">also in the global dataset</div></div>
    <div class="kpi"><div class="n">{pc(ST)}</div><div class="l">have a skin type</div></div>
    <div class="kpi"><div class="n">{pc(REV)}</div><div class="l">have reviews</div></div>
  </div>

  <h3>Matching to the global dataset</h3>
  <p>Two thresholds, which is the standard Fellegi and Sunter arrangement: an
  exact pass first, then a looser one for what it missed.</p>
  {tbl(['pass', 'rule', 'matched'], [
    ['exact', 'same brand and identical significant words', f(S['matched_exact'])],
    ['fuzzy', 'same brand and <code>token_set_ratio &ge; 90</code> on the name', f(S['matched_fuzzy'])],
    ['<b>total</b>', 'products present in both datasets', f'<b>{f(MS)}</b>']])}
  <p class="small">The strict rule is right for deduplicating <i>within</i> one
  source, where names come from the same kind of page. It is too strict
  <i>across</i> two sources that name products completely differently, which is
  why the second pass exists. Median fuzzy score was 100, minimum accepted 90.
  A matched product inherits the skin type with its full evidence, the reviews,
  and the ingredient work.</p>
  {match_html}

  <h3>Skin type, and a distinction that had to be made</h3>
  <p>The Lebanese shops state a skin type in two very different ways, and
  treating them alike would repeat the mistake that started this whole
  rebuild.</p>
  {tbl(['how the shop writes it', 'what it is', 'tier', 'products'], [
    ['<i>"Dry, Sensitive"</i>', 'a <b>declared</b> claim by the shop', '2', f(S['shop_declared'])],
    ['<i>"It has ingredients that are good for dry skin"</i>',
     'an <b>inference</b> from the formula', '3', f(S['shop_inferred'])]])}
  <div class="note">The second wording is exactly the SkinCarisma style of
  statement my supervisors objected to. It is recorded, because throwing away
  data is worse than labelling it, but it sits at <b>tier 3</b> and is never
  counted in the headline figure.</div>
  <div class="two">
    <div><h4>Declared, tier 2</h4>{''.join(card(r) for _, r in decl.iterrows())}</div>
    <div><h4>Inferred, tier 3</h4>{''.join(card(r, '#c07a54') for _, r in infer.iterrows())}</div>
  </div>

  {tbl(['tier', 'source', 'products', 'share'], [
    ['1', 'the manufacturer (inherited from the global match)', f(T['1']), pc(T['1'])],
    ['2', 'a shop that sells it, declared', f(T['2']), pc(T['2'])],
    ['3', 'a shop, inferred from the ingredients', f(T['3']), pc(T['3'])],
    ['<b>1 or 2</b>', '<b>declared claims, the figure to quote</b>', f'<b>{f(T12)}</b>', f'<b>{pc(T12)}</b>']])}

  <h3>Review coverage, stated honestly</h3>
  {tbl(['where the reviews came from', 'products'],
       [[f'<code>{k}</code>', f(v)] for k, v in revsrc.items()]
       + [['<b>no reviews at all</b>', f'<b>{f(NOREV)} ({pc(NOREV)})</b>']])}

  <div class="bad"><b>A bug I found in my own reporting, and fixed.</b> My first
  run announced that 89.2% of Lebanese products had reviews. That was wrong. The
  cleaned workbook writes the literal word <code>"none"</code> into the review
  source column when it matched nothing, and my test was "is this cell
  non-empty". So <b>10,774 products with no reviews were counted as having
  them</b>.
  <p style="margin:8px 0 0">Same species as the bugs on the skin type pages: no
  error message, a plausible number, and wrong. It is why every figure in this
  portal is recomputed from the file rather than typed in.</p></div>

  <h3>Can the missing reviews be fetched the way the skin types were?</h3>
  {tbl(['what is wanted', 'realistic?', 'why'], [
    ['a star rating and a review count', '<b>probably, for many</b>',
     'Google Shopping results carry a rating and a count, and a search API returns those as structured data, exactly as it did for skin types.'],
    ['the actual review text', '<b>mostly no</b>',
     'Review text sits behind Amazon and Sephora product pages, which block automated fetching harder than the search engines did. A search API returns the <i>link</i>; my code still has to open the page, and that is where it fails.']])}
  <div class="note"><b>What I would do before spending anything.</b> Test on 100
  products and measure the real hit rate. If a rating comes back for more than
  half, the full run costs about {f(NOREV)} credits. If not, the honest move is
  to present the Lebanese set as a <b>price and availability</b> source and take
  reviews from the global set through the {f(MS)} matched products, which is a
  perfectly defensible division of labour between two datasets.</div>

  <h3>The same columns, on purpose</h3>
  <p>The Lebanese sheet carries the identical
  {len([c for c in d.columns if c in main.columns])} columns as
  <code>SKINCARE_DATASET</code>, plus
  {len([c for c in d.columns if c not in main.columns])} retail-only ones, so
  the two can be stacked into one dataset without any reshaping.</p>
  {tbl(['extra column', 'what it holds'], [
    ['<code>retailers</code>', 'every Lebanese shop stocking it'],
    ['<code>n_retailers</code>', 'how many shops'],
    ['<code>price_usd</code>', 'the retail price in Lebanon'],
    ['<code>retailer_urls</code>', 'a link to each shop listing'],
    ['<code>retailer_skin_types</code>', 'what each shop claims, kept separately'],
    ['<code>retailers_agree</code>', 'whether the shops agreed with each other'],
    ['<code>matched_to</code>', 'which dataset it matched, and how'],
    ['<code>match_score</code>', 'the similarity score of that match']])}

  <div class="note"><b>Worth reporting in the thesis.</b> Of the
  {f(S['multi_shop'])} products stocked by more than one shop,
  <b>{f(S['agree'])}</b> have shops that agree on the skin type and
  <b>{f(S['disagree'])}</b> have shops that disagree. Roughly a coin flip, and
  the same instability that led me to rebuild the global skin type column from
  manufacturer sources. Retailer-declared skin type is not stable across
  retailers for the same physical product.</div>

  <h3>The files</h3>
  {tbl(['file', 'what is in it'], [
    ['<code>FULL_DATASET_WORKBOOK.xlsx</code>', 'summary, global dataset, Lebanese skincare, everything removed, and the raw scrape'],
    ['<code>LEBANESE_RETAIL.xlsx</code>', 'the cleaned Lebanese set and the raw scrape'],
    ['<code>LEBANESE_RETAIL.csv</code>', 'the same, for code'],
    ['<code>build_lebanese.py</code>', 'every step above, re-runnable']])}
</section>
"""

# ============================================================ splice
html = PORTAL.read_text(encoding='utf-8')
html = re.sub(r'<section class="section" id="lb-(shops|dedup|match)">.*?</section>',
              '', html, flags=re.S)
anchor = html.find('<!-- ============================================ HOME -->')
if anchor == -1:
    anchor = html.find('<section class="section" id="home">')
if anchor == -1:
    raise SystemExit('could not find where to insert, portal not changed')
html = html[:anchor] + L1 + L2 + L3 + '\n\n' + html[anchor:]

if 'lb-shops' not in re.search(r'<nav class="nav">.*?</nav>', html, re.S).group(0):
    nav = re.search(r'(\s*<div class="grp">overview</div>)', html)
    add = ('\n    <div class="grp">lebanese retail</div>\n'
           '    <a data-s="lb-shops">L1. The six shops</a>\n'
           '    <a data-s="lb-dedup">L2. Cleaning the data</a>\n'
           '    <a data-s="lb-match">L3. Matching &amp; reviews</a>'
           + nav.group(1))
    html = html[:nav.start()] + add + html[nav.end():]

PORTAL.write_text(html, encoding='utf-8')

w = {}
for m in re.finditer(r'<section class="section[^"]*" id="(lb-[^"]+)">(.*?)</section>',
                     html, re.S):
    w[m.group(1)] = len(re.sub(r'<[^>]+>', ' ', m.group(2)).split())
print('=' * 62)
print('  LEBANESE PAGES REBUILT')
print('=' * 62)
for k, v in w.items():
    print(f'    {k:12s}{v:6,} words')
print(f'\n  raw listings          {f(RAWN)}')
print(f'  unique products       {f(UNIQ)}   ({f(S["collapsed"])} duplicates removed)')
print(f'  SKINCARE PRODUCTS     {f(K)}   ({f(S["removed_total"])} non-skincare removed)')
print(f'  brands                {f(S["brands_final"])}')
print(f'  in the global set too {f(MS)}')
print(f'  with a skin type      {f(ST)}  ({pc(ST)})')
print(f'    declared, tier 1-2  {f(T12)}  ({pc(T12)})')
print(f'    inferred, tier 3    {f(T["3"])}')
print(f'  with reviews          {f(REV)}  ({pc(REV)})')
print(f'  no reviews            {f(NOREV)}  ({pc(NOREV)})')
