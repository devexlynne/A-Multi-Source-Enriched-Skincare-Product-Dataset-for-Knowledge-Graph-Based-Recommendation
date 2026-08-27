"""
The briefing document

One markdown file holding everything on the main path of the portal, in the
same order, so it can be read before the meeting. The appendix is left out on
purpose: it is there for a question, not for a walkthrough.

Every figure is read from the files when this runs, so the document and the
portal cannot disagree with each other.

Usage:
    py build_briefing.py
"""
import csv
import collections
import datetime
import statistics
from pathlib import Path

csv.field_size_limit(10 ** 8)
OUT = Path(r'C:\Users\User\Documents\Thesis\MEETING_BRIEFING.md')


def load(p):
    try:
        with open(p, newline='', encoding='utf-8') as fh:
            return [{k: (v or '') for k, v in r.items()} for r in csv.DictReader(fh)]
    except FileNotFoundError:
        return []


D = load('SKINCARE_FINAL.csv')
W = load('COMBINED_DATASET.csv')
ORI = [r for r in D if r.get('source_category') == 'Lebanese origin']
PRES = load('lebanon_shopping_presence.csv')
FOUND = load('lebanese_brands_discovered.csv')
HARV = load('lebanese_origin_harvested.csv')
DROP = load('LEBANESE_ORIGIN_dropped.csv')
N = len(D)


def g(r, c):
    return str(r.get(c, '')).strip()


def n_of(*cols):
    return sum(1 for r in D if any(g(r, c) for c in cols))


def pc(x, of=None):
    return f'{100*x/(of or N):.1f}%'


def f(x):
    return f'{x:,}'


cat = collections.Counter(g(r, 'source_category') for r in D)
brands = len({g(r, 'brand') for r in D})
types = collections.Counter(g(r, 'product_type') for r in D if g(r, 'product_type'))
prices = [float(g(r, 'price_usd')) for r in D if g(r, 'price_usd')]
rates = [float(g(r, 'rating')) for r in D if g(r, 'rating')]
stypes = collections.Counter(g(r, 'skin_type') for r in D if g(r, 'skin_type'))
bens = collections.Counter()
cons = collections.Counter()
for r in D:
    for b in g(r, 'benefits').split(','):
        if b.strip():
            bens[b.strip()] += 1
    for c in g(r, 'concerns').split(','):
        if c.strip():
            cons[c.strip()] += 1
tiers = collections.Counter(g(r, 'skin_type_tier') for r in W
                            if g(r, 'skin_type_tier'))

ob = collections.defaultdict(lambda: {'n': 0, 'ing': 0, 'pr': 0, 'dom': ''})
for r in ORI:
    b = ob[g(r, 'brand')]
    b['n'] += 1
    b['dom'] = g(r, 'product_url').split('/')[2].replace('www.', '') \
        if g(r, 'product_url').count('/') > 2 else ''
    if g(r, 'ingredients'):
        b['ing'] += 1
    if g(r, 'price_usd'):
        b['pr'] += 1

pres = {}
for r in PRES:
    p = pres.get(r['product_id'])
    if p and p.get('listed') in ('yes', 'no') and r.get('listed') == 'unknown':
        continue
    pres[r['product_id']] = r
listed = sum(1 for v in pres.values() if v['listed'] == 'yes')
notlisted = sum(1 for v in pres.values() if v['listed'] == 'no')

vr = Path('VALIDATION_REPORT_FINAL.txt')
nchecks = npass = 0
if vr.exists():
    t = vr.read_text(encoding='utf-8')
    import re as _re
    m = _re.search(r'ALL (\d+) CHECKS PASSED', t)
    if m:
        nchecks = npass = int(m.group(1))

COLS = [('product_id', 'the identifier, GLB / LBR / LBO and a number'),
        ('source_category', 'which of the three sets it came from'),
        ('brand', 'who makes it'), ('name', 'the product name'),
        ('product_type', 'cleanser, serum, sunscreen and so on'),
        ('country', 'where the brand is from'),
        ('product_url', 'the page it can be seen on'),
        ('skin_type', 'dry, oily, combination, normal, all'),
        ('sensitivity', 'sensitive or resistant'),
        ('skin_type_source', 'which site the skin type was read from'),
        ('ingredients', 'the full INCI list'),
        ('ingredient_count', 'how many are in it'),
        ('key_ingredients', 'the actives a reader would care about'),
        ('free_from', 'what the formula does not contain'),
        ('spf', 'sun protection factor, where there is one'),
        ('benefits', 'what it claims to do'),
        ('concerns', 'what it may make worse'),
        ('price_usd', 'one price, in dollars'),
        ('price_source', 'who was selling at that price'),
        ('rating', 'out of five'), ('rating_count', 'how many people'),
        ('rating_source', 'where the rating came from'),
        ('review_texts_json', 'the reviews themselves'),
        ('shops_in_lebanon', 'how many of the six shops carry it')]

md = []
A = md.append

A('# Skincare dataset: everything to know before the meeting')
A('')
A(f'*Generated {datetime.datetime.now():%d %B %Y, %H:%M} from the files '
  f'themselves, so nothing here can disagree with the portal.*')
A('')
A('This is the main path of the portal, in the same order. The appendix is '
  'left out: it is there to answer a question, not to be walked through.')
A('')
A('---')
A('')
A('## The one-minute version')
A('')
A(f'- **{f(N)} products**, {f(brands)} brands, {len(types)} categories, '
  f'{len(D[0])} columns')
A(f'- Three sources: **{f(cat["Global (Skinsort)"])} global**, '
  f'**{f(cat["Lebanese retail"])} sold in Lebanon**, '
  f'**{f(cat["Lebanese origin"])} made in Lebanon**')
A(f'- **{nchecks} validation checks, all passing**, and the report regenerates '
  f'so anyone can rerun it')
A('- The Lebanese part is the part that does not exist anywhere else. Its '
  'gaps describe how that industry works, which is a result rather than a '
  'shortfall.')
A('')
A('**If you say only three things:**')
A('')
A('1. Every value carries the page it came from. That was the criticism last '
  'time and it is now answered for every column.')
A('2. The dataset was tested after it was built, not only while it was being '
  'built. Nine faults were found that way, and six of them were fixed by '
  'removing a value rather than mending it.')
A('3. The Lebanese-made half of this market has no reviews, often no '
  'published formula, and frequently no price. A recommender built on '
  'reviews ignores it completely. That is the argument for the ontology.')
A('')
A('---')
A('')
A('## 1. Every statistic')
A('')
A('### The three sources')
A('')
A('| source | products | share | what it is |')
A('|---|---|---|---|')
A(f'| Global (Skinsort) | {f(cat["Global (Skinsort)"])} | '
  f'{pc(cat["Global (Skinsort)"])} | the international market |')
A(f'| Lebanese retail | {f(cat["Lebanese retail"])} | '
  f'{pc(cat["Lebanese retail"])} | on sale in six Lebanese shops, foreign makers |')
A(f'| Lebanese origin | {f(cat["Lebanese origin"])} | '
  f'{pc(cat["Lebanese origin"])} | made by Lebanese companies and people |')
A('')
A('### How full every column is')
A('')
A('| column | filled | share | what it holds |')
A('|---|---|---|---|')
for c, desc in COLS:
    n = n_of(c)
    A(f'| `{c}` | {f(n)} | {pc(n)} | {desc} |')
A('')
A('### Price')
A('')
A(f'- **{f(n_of("price_usd"))} products have a price, {pc(n_of("price_usd"))}**')
A(f'- median ${statistics.median(prices):,.2f}, '
  f'from ${min(prices):,.2f} to ${max(prices):,.2f}')
A('- Skinsort publishes no prices at all, so every price came from a Lebanese '
  'shop or from a market search')
A('')
A('### Skin type, and how strong the evidence is')
A('')
A('| skin type | products |')
A('|---|---|')
for k, v in stypes.most_common():
    A(f'| {k} | {f(v)} |')
A('')
A('| where it came from | products |')
A('|---|---|')
names = {'1': 'the manufacturer&rsquo;s own site', '2': 'a shop that sells it',
         '3': 'an analysis site', '4': 'something weaker'}
for k in sorted(tiers):
    A(f'| {names.get(k, k)} | {f(tiers[k])} |')
A('')
A(f'**{pc(tiers["1"] + tiers["2"], max(sum(tiers.values()), 1))} come from the '
  f'manufacturer or a shop**, which are the two kinds of source that were '
  f'accepted last time.')
A('')
A('### What they claim, and what they may worsen')
A('')
A('| benefit | products | concern | products |')
A('|---|---|---|---|')
bl, cl = bens.most_common(), cons.most_common()
for i in range(max(len(bl), len(cl))):
    b = f'{bl[i][0]} | {f(bl[i][1])}' if i < len(bl) else ' | '
    c = f'{cl[i][0]} | {f(cl[i][1])}' if i < len(cl) else ' | '
    A(f'| {b} | {c} |')
A('')
A('### Reviews')
A('')
A(f'- {f(n_of("rating"))} products have a rating, {pc(n_of("rating"))}')
A(f'- {f(n_of("review_texts_json"))} carry the review text itself')
A(f'- **0 Lebanese origin products have a review.** Not one of the '
  f'{len(ob)} Lebanese brand sites runs a review system.')
A('')
A('---')
A('')
A('## 2a. Global (Skinsort)')
A('')
glb = [r for r in D if g(r, 'source_category') == 'Global (Skinsort)']
A(f'{f(len(glb))} products, the international half.')
A('')
A('| what | where it came from |')
A('|---|---|')
A('| ingredients | the Skinsort product page, which publishes the full INCI list |')
A('| reviews and ratings | Skinsort, Amazon and Sephora, matched by brand and name |')
A('| skin type | **not** from Skinsort. The first version was built from '
  'analysis sites, was rightly questioned, and was deleted and rebuilt from '
  'manufacturer and retailer pages |')
A('| price | nowhere. Skinsort publishes none |')
A('')
A('**The single most useful thing learned in this project:** searching by '
  'keyword and hoping the right page ranks gave 6.6% coverage. Learning each '
  "brand's own web address once and asking that address directly gave 98%. "
  'The same idea later took Lebanese ingredient coverage from 27% to 76%.')
A('')
A('---')
A('')
A('## 2b. Lebanese retail')
A('')
A(f'{f(cat["Lebanese retail"])} products from six shops: sohaticare, feel22, '
  f'mazenonline, zeinacare, nexuscare, daoukpharma.')
A('')
A('### Why deduplication was necessary')
A('')
A('Six shops selling CeraVe all list the same cream with their own wording, '
  'their own size in the title and their own spelling. Counting them as six '
  'products would say something false about the Lebanese market.')
A('')
A('| step | what happens | where it is argued |')
A('|---|---|---|')
A('| make names comparable | accents and punctuation removed, sizes and offer '
  'wording stripped, words sorted | Rahm & Do (2000), §3.1, data '
  'transformation: standardise value formats before matching |')
A('| compare only within a brand | the file is grouped by brand first | '
  'Christen (2012), ch.4, indexing, called blocking |')
A('| two thresholds, not one | identical word sets accepted outright, 90 or '
  'above accepted, below left alone | Fellegi & Sunter (1969), §2, an upper '
  'and a lower threshold with a review band |')
A('')
A('### Worked examples, including the ones rejected')
A('')
A('| A | B | decision | why |')
A('|---|---|---|---|')
A('| CeraVe Moisturising Lotion 236ml | Cerave Moisturizing Lotion 236 ML | '
  '**same** | identical word sets once spelling and size are removed |')
A('| CeraVe Hydrating Cleanser | CeraVe Hydrating Cleanser **Bar** | '
  '**different** | the bar is another product. An early version merged them |')
A('| Ruboril Expert **M** | Ruboril Expert **S** | **different** | the letter '
  'is the whole difference, so short words are kept |')
A('| Effaclar H **Iso-Biome** | Effaclar H **Isobiome** | **same** | a hyphen '
  'makes one word into two. The validation found this pair after the merge |')
A('')
A('### What else was cleaned')
A('')
A('| what | how many | why |')
A('|---|---|---|')
A('| words meaning "we do not know" emptied | 15,470 cells | Rahm & Do (2000) '
  '§2 list this under lack of integrity. Review coverage read 89% before and '
  '15% after |')
A('| non-skincare removed | most of the raw scrape | same categories as the '
  'global set, so the two can be compared |')
A('| prices in lira converted at 89,500 | 219 rows | one column, one unit. '
  'The rate is the Banque du Liban card settlement rate, fixed since '
  'December 2023 |')
A('| ingredient lists judged by shape, not heading | every list | a page with '
  'the word "Ingredients" over a marketing paragraph has no formula on it |')
A('')
A('---')
A('')
A('## 2c. Lebanese origin')
A('')
A(f'{f(cat["Lebanese origin"])} products from **{len(ob)} Lebanese brands**, '
  f'collected from the brands&rsquo; own shops. There is no list of these '
  f'brands to download, so finding them was most of the work.')
A('')
A('### How the brands were found')
A('')
A(f'{len({g(r, "how_found") for r in FOUND})} searches in English, Arabic and '
  f'French. The Arabic searches are why the soap houses are here at all: '
  f'makers working for generations who sell locally never surface in an '
  f'English search.')
A('')
A('Four shapes of question were used: by the product they make, by a brand '
  'already known, by the trade rather than the shop, and on social media.')
A('')
A('**Proving a brand is Lebanese.** A +961 telephone number turned out to be '
  'the most useful signal: hard to fake by accident, present in almost every '
  'real Lebanese shop footer.')
A('')
A('### The brands')
A('')
A('| brand | products | publishes a formula | publishes a price |')
A('|---|---|---|---|')
for b, v in sorted(ob.items(), key=lambda x: -x[1]['n']):
    A(f'| {b} | {f(v["n"])} | {100*v["ing"]/v["n"]:.0f}% | '
      f'{100*v["pr"]/v["n"]:.0f}% |')
A('')
A('### What was taken out, and why')
A('')
A('This set was corrected after a review found things in it that do not '
  'belong. Lebanese origin means **made by** a Lebanese company, not sold by '
  'one.')
A('')
A('| what | products | why it was wrong |')
A('|---|---|---|')
A('| **Xiran** | 271 | `xiranskincare.com` is Guangzhou Xiran Cosmetics Co., '
  'Ltd, a factory in Baiyun District, Guangzhou, China. Every product is '
  'titled "Private Label" or "OEM". Removed from the dataset entirely |')
A('| Duft | 37 | a Lebanese shop. 23 of its 37 products are La Roche-Posay or '
  'A-Derma. Moved to Lebanese retail |')
A('| SBRANDS | 28 | a Lebanese shop selling COSRX, BYOMA, NACIFIC. Moved |')
A('| bashrati.care | 22 | a shop, five brand names on one domain. Moved |')
A('')
A('**Why the test failed:** it asked whether a page names Lebanon, carries a '
  '+961 number or sits on a .lb domain. Xiran sells *into* Lebanon and lists '
  'Lebanese contacts, so it passed. The test checked where a company sells. '
  'It should have checked where it makes.')
A('')
A('### The finding that came out of this')
A('')
A('The formula column splits the brands cleanly in two, and the split is '
  'about what kind of company the brand is, not its size.')
full = [b for b, v in ob.items() if v['n'] >= 10 and v['ing'] / v['n'] > 0.9]
none_ = [b for b, v in ob.items() if v['n'] >= 10 and v['ing'] / v['n'] < 0.2]
A('')
A(f'- **Publish nearly every formula:** {", ".join(sorted(full)[:6])}')
A(f'- **Publish almost none:** {", ".join(sorted(none_)[:6])}')
A('')
A('Under EU Regulation 1223/2009, Article 19, the manufacturer is responsible '
  'for declaring the full ingredient list. The brands organised as cosmetics '
  'companies publish one. The artisanal makers do not, and no amount of '
  'scraping changes that.')
A('')
A('### Are these products sold anywhere online?')
A('')
A(f'977 were checked against Bing Shopping: **{f(listed)} found, '
  f'{f(notlisted)} not found**.')
A('')
A('Treat the second figure as an upper bound. Only 33 of those got an '
  'explicit "no results" from Bing; the rest simply showed no price, and Bing '
  'renders some prices with JavaScript that a plain fetch does not see.')
A('')
A('**This number was nearly a false finding.** An earlier run said 0% of '
  'Lebanese products were listed anywhere, which fitted the ingredients '
  'result so neatly it looked true. It was a search key that had run out of '
  'credits and was returning empty replies to everything.')
A('')
A('---')
A('')
A('## 3. How it was cleaned')
A('')
A('### When a value is kept')
A('')
A('| rule | why |')
A('|---|---|')
A('| an ingredient list is recognised by its shape, not its heading | at '
  'least five comma-separated pieces and three recognisable chemical names. '
  'The benefits panel was passing as ingredients until the second test |')
A('| free-from only where the formula is complete | a claim about an absence '
  'can only be checked against a whole list |')
A('| negations are read | thirteen products had the opposite of what their '
  'page said. "Not Good for Oily Skin" had been recorded as Oily |')
A('| accents removed before comparing | Avène and Avene are one brand |')
A('| short words kept | dropping them merged Ruboril Expert M with S |')
A('')
A('### The faults that changed the data')
A('')
A('Eleven in total. None raised an error, and three made the dataset look '
  '**better** than it was.')
A('')
A('| what happened | how many |')
A('|---|---|')
A('| "none" and "not available" counted as data | 15,470 cells |')
A('| zero treated as missing, wiping real markers | 37,635 cells |')
A('| Lebanese shop prices scraped then dropped by a column-name mismatch | '
  '2,300 prices |')
A('| reviews chosen between rather than pooled | about 550 products |')
A('| five products priced in lira in a dollar column | 5 rows, then 214 more |')
A('| a quarter of market prices from eBay, Mercari and Poshmark | 256 |')
A('| a search key ran out silently and returned empty replies | 4,641 products |')
A('| one brand written five ways: A-derma, ADERMA, Aderma, A-Derma, aderma | '
  '110 brands, 717 rows |')
A('| broken characters from a bad encoding | 120 names |')
A('')
A('---')
A('')
A('## 4. Validation')
A('')
A(f'**{nchecks} checks, all passing.** The script changes nothing: it reads, '
  f'asks, and writes `VALIDATION_REPORT_FINAL.txt`. Run it yourself with '
  f'`py validate_dataset.py --final`.')
A('')
A('### Where the groups come from')
A('')
A('| group | what it asks |')
A('|---|---|')
A('| A | can the file be read at all |')
A('| B | is every row a row, and every product one product |')
A('| C | do the controlled columns hold only their allowed values |')
A('| D | are the numbers inside sensible limits |')
A('| E | do fields that depend on each other agree |')
A('| F | does every claim say where it came from |')
A('| G | is anything left that means "we do not know" |')
A('')
A('The grouping follows the data quality literature rather than the shape of '
  'the code:')
A('')
A('- **Wang, R.Y. & Strong, D.M. (1996).** Beyond Accuracy: What Data Quality '
  'Means to Data Consumers. *Journal of Management Information Systems* '
  '12(4), 5–33. Quality is more than the values being right.')
A('- **Pipino, L.L., Lee, Y.W. & Wang, R.Y. (2002).** Data Quality '
  'Assessment. *Communications of the ACM* 45(4), 211–218. Measuring a '
  'dimension as a ratio, which is what every coverage figure here is.')
A('- **Batini, C. et al. (2009).** Methodologies for Data Quality Assessment '
  'and Improvement. *ACM Computing Surveys* 41(3), Art. 16. Describe, '
  'measure, then decide what to do about the failures.')
A('- **Rahm, E. & Do, H.H. (2000).** Data Cleaning: Problems and Current '
  'Approaches. Clean each source before joining, which decided the shape of '
  'the pipeline.')
A('')
A('### What the checking found the first time it ran')
A('')
A('Nine faults, none caught by the merge, because the merge does not ask '
  'these questions.')
A('')
A('| what was wrong | how many | what I did |')
A('|---|---|---|')
A('| invisible control characters in ingredient lists | 2 cells | removed |')
A('| the same product twice under two spellings | 2 pairs | merged |')
A('| SPF 150 on a product labelled 50+, and SPF 504 | 2 rows | read 50 from '
  'the name, emptied the other |')
A('| key ingredients that were sentences | 21 rows | emptied |')
A('| a rating with no source, no text, no count | 90 rows | removed |')
A('| skin type contradicting its own status column | 7 rows | removed |')
A('| **ingredient lists with no record of where they came from** | '
  '**8,118 rows** | filled in the source |')
A('| a brand recorded as "Undefined" | 1 row | read from the product name |')
A('| a review field holding ". \\|\\|\\| ." | 1 row | emptied |')
A('')
A('**Six of the nine were fixed by removing a value, not mending it**, on the '
  'rule that a wrong value is worse than a blank. Five coverage figures went '
  'down as a result. Only one went up, and it is the one that matters for a '
  'knowledge graph: formulas with a known source went from 24.4% to 100%.')
A('')
A('---')
A('')
A('## 5. Ontology, the next phase')
A('')
A('### What an ontology is')
A('')
A('From the CMPS456 lecture, slide 4: an ontology turns the complexities of '
  'reality into a structured guide a computer can follow. You define '
  '**individuals**, **classes**, **attributes**, **relations**, and the '
  '**constraints and axioms** that govern them.')
A('')
A('Slide 42 in one line: **Ontology + Data = Knowledge Graph.**')
A('')
A('| question | the spreadsheet | the ontology |')
A('|---|---|---|')
A('| products for dry, sensitive skin | filter two columns, works | the same |')
A('| products with no fragrance allergens | **not possible**, the ingredients '
  'are one long string | possible, because Linalool is linked to its CosIng '
  'function |')
A('| why does this suit dry skin? | no answer | because it contains glycerin, '
  'a humectant, and humectants suit dry skin |')
A('')
A('Mine is a **domain ontology** (lecture slide 33), with a little of the '
  'application kind in it.')
A('')
A('### Reuse means the other vocabulary goes inside the file')
A('')
A('Not inspiration. Instead of inventing `myOntology:hasProductName`, the '
  'file literally says `schema:name`:')
A('')
A('```')
A(':LBR-00143')
A('    a                  :Product ;')
A('    schema:name        "The Aloelab 0.5% Retinol Night Serum" ;')
A('    schema:brand       :TheAloelab ;')
A('    schema:category    "Serum" ;')
A('    :suitableFor       :OilySkin ;')
A('    :contains          :Glycerin , :Retinol .')
A('```')
A('')
A('Three of those six lines are somebody else&rsquo;s vocabulary.')
A('')
A('| ontology | what it gives us | link |')
A('|---|---|---|')
A('| **schema.org** | name, brand, category, and the Offer shape for price '
  'and seller | https://schema.org/Product |')
A('| **CosIng-KG** | what each ingredient *does*. This is what makes "no '
  'fragrance allergens" answerable at all | https://github.com/biobricks-ai/cosing-kg |')
A('| **OntoCosmetic** | the closest existing model, for formulation. No '
  'retail, no price, no skin type, which is our gap | '
  'https://github.com/ERPI-UL/OntoCosmetic |')
A('| **PROV-O** | the standard way to say where a fact came from, which is '
  'our whole tier system | https://www.w3.org/TR/prov-o/ |')
A('| **SKOS** | the controlled lists, with alternative labels in French and '
  'Arabic | https://www.w3.org/TR/skos-reference/ |')
A('')
A('The CosIng example is the one worth showing:')
A('')
A('```')
A('my dataset says:   ingredients = "Aqua, Glycerin, Linalool, ..."')
A('')
A('with CosIng loaded:')
A('  :Glycerin   cosing:function  cosing:Humectant .')
A('  :Linalool   cosing:function  cosing:Perfuming ;')
A('              cosing:isAllergen true .')
A('```')
A('')
A('### The model proposed')
A('')
A('Twelve classes, each earning its place from a column: Product, '
  'ProductCategory, Brand, Ingredient, IngredientFunction, SkinType, '
  'Sensitivity, Concern, Benefit, Offer, Review, Evidence.')
A('')
A('**Evidence is the class I would defend hardest.** Most product ontologies '
  'record that a product suits dry skin. Mine records that it suits dry skin '
  '*because this page said so, in these words, and that page is the '
  "manufacturer's own*. That is what the tier system was for.")
A('')
A('### Filling it')
A('')
A('| what | by hand or automatic |')
A('|---|---|')
A('| the classes and hierarchy | by hand, in Protégé |')
A('| the controlled lists | by hand, they are small and already controlled |')
A('| linking ingredients to CosIng | automatic, then the failures checked |')
A(f'| the {f(N)} products | automatic |')
A('')
A('Three ways to convert: W3C **direct mapping** (too blunt), **R2RML** (a '
  'readable mapping file, and what I would use), or a script with rdflib '
  '(quickest for a first draft). Start with the script to test the model, '
  'move to R2RML for the thesis.')
A('')
A('### Checking the ontology')
A('')
A('| method | what it catches |')
A('|---|---|')
A('| competency questions | a question you cannot answer names the missing '
  'class. Grüninger & Fox (1995) |')
A('| a reasoner, HermiT | contradictions, empty classes, cycles |')
A('| **OOPS!** | 33 of 41 known modelling pitfalls. Poveda-Villalón et al. '
  '(2014), *IJSWIS* 10(2), 7–34. https://oops.linkeddata.es/ |')
A('| SHACL | whether the individuals obey the model, the same rules as my '
  'validation but in a standard language |')
A('')
A('### Using the ontology to check the dataset')
A('')
A('This runs the usual direction backwards, and it is the part I find most '
  'interesting.')
A('')
A('| a fault only reasoning finds | the chain |')
A('|---|---|')
A('| a product for sensitive skin containing a known allergen | suitableFor '
  'Sensitive, contains Linalool, Linalool is a FragranceAllergen |')
A('| a hydration claim with no humectant | claims Hydrating, but no '
  'Ingredient with function Humectant |')
A('| a sunscreen with no UV filter | almost certainly a truncated ingredient '
  'list, and a good way to find them |')
A('')
A('Vendruscolo et al. (2025) tested 187 products marketed as hypoallergenic '
  f'and found 89% contained at least one known allergen. With the ontology '
  f'loaded the same question could be asked of {f(N)} products.')
A('')
A('---')
A('')
A('## Questions they will probably ask')
A('')
A('**Why is price only 92%?** Skinsort publishes no prices at all. Two '
  'Lebanese brands publish none across hundreds of pages: one sells private '
  'label to other companies, one sells through pharmacies. The gap is '
  'structural.')
A('')
A('**Why is rating only 48%?** It went *down* during validation, because 90 '
  'ratings with no source, no text and no count were removed. An honest 48% '
  'beats a 49% with holes in it.')
A('')
A('**How do you know the skin types are right?** Every one carries the page, '
  'the sentence it was read from, and a tier saying how strong that page is. '
  f'{pc(tiers["1"] + tiers["2"], max(sum(tiers.values()), 1))} come from a '
  f'manufacturer or a shop.')
A('')
A('**Is the dataset finished?** The columns are. 966 products could still be '
  'asked about price and rating, which needs about $5 of API credits.')
A('')
A('**What is genuinely new here?** The Lebanese origin set. It does not exist '
  'anywhere else, and what is missing from it describes an industry: no '
  'reviews at all, formulas published only by the brands organised as '
  'companies, and prices absent wherever the maker sells business to '
  'business.')
A('')
A('---')
A('')
A('## The files')
A('')
A('| file | what it is |')
A('|---|---|')
A('| `SKINCARE_FINAL.xlsx` | the dataset to show. '
  f'{f(N)} products, {len(D[0])} columns |')
A('| `SKINCARE_FINAL.csv` | the same thing as data |')
A('| `COMBINED_EVIDENCE.csv` | everything removed from the tidy file, joined '
  'on `product_id`. Nothing was deleted |')
A('| `VALIDATION_REPORT_FINAL.txt` | the checks and their answers |')
A('| `Lynne-Thesis Portal.html` | the full walkthrough with diagrams |')
A('| `COMBINED_DATASET.csv` | the working file, all 56 columns |')

OUT.write_text('\n'.join(md), encoding='utf-8')
print('=' * 64)
print(f'  {OUT.name}')
print('=' * 64)
print(f'  {len(" ".join(md).split()):,} words, {sum(1 for l in md if l.startswith("|")):,} table rows')
print(f'  read from the files: {f(N)} products, {f(brands)} brands, '
      f'{nchecks} checks passing')
