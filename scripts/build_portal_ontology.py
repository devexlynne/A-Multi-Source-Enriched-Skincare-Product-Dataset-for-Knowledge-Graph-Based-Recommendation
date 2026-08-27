"""
The ontology pages of the portal

Three pages:

    O1  What has to be true before a dataset can become an ontology,
        and whether mine is
    O2  The ontology I propose: classes, why each one is there, and what
        column in my file it comes from
    O3  How I will check it is right

Every figure about the dataset is read from COMBINED_DATASET.csv at build time.
The citations are fixed and are listed on the page.

Usage:
    py build_portal_ontology.py
"""
import re
import pandas as pd
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    # the portal normally sits one level up; the absolute path stays first
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
try:
    c = pd.read_csv('COMBINED_DATASET.csv', dtype=str, low_memory=False).fillna('')
except FileNotFoundError:
    c = pd.read_csv('SKINCARE_DATASET.csv', dtype=str, low_memory=False).fillna('')

N = len(c)
tier = pd.to_numeric(c['skin_type_tier'], errors='coerce')
got = c['skin_type'] != ''
NGOT = max(int(got.sum()), 1)
T12 = int((tier[got] <= 2).sum())
BRANDS = int(c['brand'].nunique())
CATS = int(c['product_type'].nunique())
ING = int((c['ingredients'] != '').sum())
QUOTE = int((c['skin_type_quote'] != '').sum())
URL = int((c['skin_type_url'] != '').sum())


def f(x):
    return f'{x:,}'


def pc(x, of=None):
    return f'{100*x/(of or N):.1f}%'


def tbl(head, rows):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f"<td class='td'>{x}</td>" for x in r) + '</tr>'
                for r in rows)
    return f'<table><tr>{h}</tr>{b}</table>'


# ============================================================ O1
O1 = f"""
<section class="section" id="on-ready">
  <h2>O1 &middot; From the dataset to the ontology</h2>
  <p class="lead">A dataset is a table. An ontology is a description of what
  the things in that table are and how they relate to each other. This page is
  about what has to be true of the table first, what the literature says the
  steps are, and whether my file is ready.</p>

  <h3>What an ontology adds that a spreadsheet cannot do</h3>
  <p>My file can already tell you that a product is for dry skin. It cannot
  tell you <i>why</i>, or work anything out on its own. An ontology can, because
  the meaning is written down in a form a machine can follow.</p>
  {tbl(['question', 'the spreadsheet', 'the ontology'], [
    ['is this product for dry skin?', 'yes, read the cell', 'yes'],
    ['which products suit dry <b>and</b> sensitive skin?',
     'yes, filter two columns', 'yes'],
    ['this product has an ingredient that is a known allergen, so who should avoid it?',
     '<b>no</b>, the link between ingredient and skin is not written anywhere',
     'yes, it follows from the rules'],
    ['two products have different names but the same formula, are they the same thing?',
     '<b>no</b>', 'yes, if the formula is modelled as its own thing'],
    ['this claim came from the brand and that one from a shop, does it matter?',
     'only if a human reads the tier column',
     'yes, evidence strength can be part of the reasoning']])}

  <h3>The steps the literature agrees on</h3>
  <p>I looked at four methods that are commonly used. They differ in detail but
  the order is the same in all of them.</p>
  {tbl(['method', 'who', 'what it is useful for here'], [
    ['<b>Ontology Development 101</b>', 'Noy &amp; McGuinness, 2001',
     'the plainest guide to defining classes, a hierarchy, and properties. good for a first ontology, and it is where competency questions are introduced as the way to fix the scope.'],
    ['<b>METHONTOLOGY</b>', 'Fern&aacute;ndez-L&oacute;pez et al., 1997',
     'a fuller life cycle: specification, conceptualisation, formalisation, implementation, maintenance. the skincare recommendation ontology I found in the literature used exactly this.'],
    ['<b>NeOn</b>', 'Su&aacute;rez-Figueroa et al., 2015',
     'the one that takes reuse seriously. it assumes you will build on existing ontologies rather than start from nothing, which is my situation.'],
    ['<b>Competency questions</b>', 'Gr&uuml;ninger &amp; Fox, 1995',
     'write the questions the ontology must answer before building it, then test it against them at the end. this is the part I care about most, because it stops the ontology growing classes nobody needs.']])}

  <div class="dg">
  <svg viewBox="0 0 700 210" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11.5">
    <text x="350" y="18" text-anchor="middle" font-weight="700" fill="#584a7a" font-size="13">the order of work, the same in every method I read</text>
    <rect x="14" y="34" width="126" height="52" rx="8" fill="#f4f0fa" stroke="#7a68a6"/>
    <text x="77" y="54" text-anchor="middle" font-weight="700" fill="#584a7a">1. scope</text>
    <text x="77" y="70" text-anchor="middle" fill="#6b6478">competency questions</text>
    <path d="M140 60 L166 60" stroke="#b9aed0" stroke-width="2"/><polygon points="166,60 158,55 158,65" fill="#b9aed0"/>
    <rect x="172" y="34" width="126" height="52" rx="8" fill="#f4f0fa" stroke="#7a68a6"/>
    <text x="235" y="54" text-anchor="middle" font-weight="700" fill="#584a7a">2. reuse</text>
    <text x="235" y="70" text-anchor="middle" fill="#6b6478">what already exists</text>
    <path d="M298 60 L324 60" stroke="#b9aed0" stroke-width="2"/><polygon points="324,60 316,55 316,65" fill="#b9aed0"/>
    <rect x="330" y="34" width="126" height="52" rx="8" fill="#f4f0fa" stroke="#7a68a6"/>
    <text x="393" y="54" text-anchor="middle" font-weight="700" fill="#584a7a">3. classes</text>
    <text x="393" y="70" text-anchor="middle" fill="#6b6478">and the hierarchy</text>
    <path d="M456 60 L482 60" stroke="#b9aed0" stroke-width="2"/><polygon points="482,60 474,55 474,65" fill="#b9aed0"/>
    <rect x="488" y="34" width="126" height="52" rx="8" fill="#f4f0fa" stroke="#7a68a6"/>
    <text x="551" y="54" text-anchor="middle" font-weight="700" fill="#584a7a">4. properties</text>
    <text x="551" y="70" text-anchor="middle" fill="#6b6478">how they connect</text>
    <path d="M551 86 L551 106" stroke="#b9aed0" stroke-width="2"/><polygon points="551,106 546,98 556,98" fill="#b9aed0"/>
    <rect x="488" y="110" width="126" height="52" rx="8" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="551" y="130" text-anchor="middle" font-weight="700" fill="#3f6b48">5. fill it</text>
    <text x="551" y="146" text-anchor="middle" fill="#6b6478">from my dataset</text>
    <path d="M488 136 L462 136" stroke="#6f9c78" stroke-width="2"/><polygon points="462,136 470,131 470,141" fill="#6f9c78"/>
    <rect x="330" y="110" width="126" height="52" rx="8" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="393" y="130" text-anchor="middle" font-weight="700" fill="#3f6b48">6. check it</text>
    <text x="393" y="146" text-anchor="middle" fill="#6b6478">reasoner + questions</text>
    <rect x="14" y="176" width="600" height="26" rx="6" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="314" y="194" text-anchor="middle" fill="#8d5433">step 5 is the only one that needs the dataset. steps 1 to 4 are design, and they come first.</text>
  </svg>
  <div class="cap">Design first, data second. Building classes around whatever
  columns happen to exist is how you end up with an ontology that is just a
  spreadsheet with extra steps.</div></div>

  <h3>What the dataset has to be before it can fill an ontology</h3>
  <p>These are the conditions I found repeated across the reading. Next to each
  one is where my file stands.</p>
  {tbl(['requirement', 'why it matters', 'my dataset'], [
    ['<b>every row is one real thing</b>',
     'if two rows are the same product, the ontology creates two individuals for one object and every count after that is wrong',
     f'<b>done.</b> duplicates removed in both sources, 644 in the Lebanese one'],
    ['<b>every column means one thing</b>',
     'a column holding four kinds of claim cannot become one property. this is exactly why the old skin type column had to go',
     '<b>done.</b> that is what the whole skin type rebuild was for'],
    ['<b>the values are from a fixed list</b>',
     'a class needs known members. free text cannot become a class',
     f'<b>done.</b> skin type has 5 values, sensitivity 2, category {CATS}'],
    ['<b>the vocabulary is standardised</b>',
     'Water and Aqua must be one thing, or the ingredient class splits in two',
     '<b>done.</b> ingredients standardised against EU CosIng, 99.95% official'],
    ['<b>missing is marked as missing</b>',
     'a placeholder like "Not available" becomes a real individual in the ontology, which is a lie in machine-readable form',
     '<b>done, and it was a real problem.</b> 4,696 cells said "Not available" and were counted as filled'],
    ['<b>every fact can be traced</b>',
     'an ontology states things as true. it should be possible to see where each one came from',
     f'<b>done.</b> {f(URL)} values carry a source link and {f(QUOTE)} carry the sentence'],
    ['<b>identifiers are stable</b>',
     'each individual needs a name that does not change between versions',
     '<b>done.</b> every row has a product_id']])}

  <div class="ok"><b>Where that leaves me.</b> The dataset satisfies the
  conditions. That is not a coincidence: most of the cleaning work, and all of
  the skin type rebuild, was doing exactly what this stage needs. The 11
  cleaning steps, the INCI standardisation and the evidence columns are the
  preparation for this chapter, not separate from it.</div>

  <h3>The questions the ontology has to answer</h3>
  <p>Following Gr&uuml;ninger and Fox, I wrote these before designing anything.
  If a class does not help answer one of them, it does not belong.</p>
  {tbl(['#', 'competency question'], [
    ['1', 'Which products suit dry and sensitive skin at the same time?'],
    ['2', 'Which products are suitable for a given skin type <i>and</i> can be bought in Lebanon?'],
    ['3', 'Which products contain an ingredient that a person must avoid?'],
    ['4', 'What does a product contain that makes it suitable for oily skin?'],
    ['5', 'Which claims come from the manufacturer, and which only from a shop?'],
    ['6', 'Which products are made by a Lebanese brand rather than only sold here?'],
    ['7', 'Which two products have the same function and the closest formula?'],
    ['8', 'For a concern such as acne, which products address it and what do reviewers say?'],
    ['9', 'Which ingredients appear most often in products for sensitive skin?'],
    ['10', 'Where a shop and the manufacturer disagree about skin type, which products are affected?'],
    ['11', 'Which products are fragrance free and also suitable for sensitive skin?'],
    ['12', 'What is the price range in Lebanon for products that suit a given skin type?']])}
  <p class="small">Questions 2, 6 and 12 are only answerable because of the
  Lebanese work. Questions 5 and 10 are only answerable because of the evidence
  columns. Those two groups are what make this ontology different from the ones
  already published.</p>

  <h3>What is already published, and what I would be adding</h3>
  {tbl(['existing work', 'what it did', 'what mine adds'], [
    ['Skincare recommendation ontology (2025)',
     'METHONTOLOGY, 12 classes including Product, Ingredient, Skin Type, Skin Concern. filled by scraping Sociolla, Beautyhaul and Skinsort. about 3,800 products.',
     'evidence and provenance as part of the model, and a local market'],
    ['Body moisturiser ontology (2024)',
     '1 main class, 8 subclasses, 159 individuals, 14 object properties. built in Prot&eacute;g&eacute;, checked with HermiT.',
     'a much wider scope than one product category'],
    ['OntoCosmetic',
     'cosmetic emulsions for formulation and product design, verified with SWRL rules',
     'mine is about choosing a product, not designing one'],
    ['<b>this thesis</b>', '&mdash;',
     '<b>every claim carries its source, its strength and the sentence it came from, and the Lebanese market is modelled alongside the global one</b>']])}
</section>
"""

# ============================================================ O2
O2 = f"""
<section class="section" id="on-model">
  <h2>O2 &middot; The ontology I propose</h2>
  <p class="lead">Eleven classes. Every one of them exists because a competency
  question needs it and a column in my file can fill it. If neither is true, I
  left it out.</p>

  <div class="dg">
  <svg viewBox="0 0 720 430" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11">
    <rect x="286" y="14" width="150" height="44" rx="9" fill="#584a7a"/>
    <text x="361" y="34" text-anchor="middle" fill="#fff" font-weight="700" font-size="13">Product</text>
    <text x="361" y="49" text-anchor="middle" fill="#d5cae8">{f(N)} individuals</text>

    <rect x="24" y="92" width="132" height="42" rx="8" fill="#f4f0fa" stroke="#7a68a6"/>
    <text x="90" y="110" text-anchor="middle" font-weight="700" fill="#584a7a">Brand</text>
    <text x="90" y="125" text-anchor="middle" fill="#6b6478">{f(BRANDS)}</text>
    <path d="M286 40 L156 106" stroke="#b9aed0" stroke-width="1.4"/>
    <text x="196" y="66" fill="#9990a8" font-size="9.5">madeBy</text>

    <rect x="176" y="92" width="132" height="42" rx="8" fill="#f4f0fa" stroke="#7a68a6"/>
    <text x="242" y="110" text-anchor="middle" font-weight="700" fill="#584a7a">ProductCategory</text>
    <text x="242" y="125" text-anchor="middle" fill="#6b6478">{CATS} types</text>
    <path d="M320 58 L262 92" stroke="#b9aed0" stroke-width="1.4"/>

    <rect x="328" y="92" width="132" height="42" rx="8" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="394" y="110" text-anchor="middle" font-weight="700" fill="#3f6b48">Ingredient</text>
    <text x="394" y="125" text-anchor="middle" fill="#6b6478">INCI names</text>
    <path d="M380 58 L394 92" stroke="#a8c9ae" stroke-width="1.4"/>
    <text x="398" y="76" fill="#9990a8" font-size="9.5">contains</text>

    <rect x="480" y="92" width="132" height="42" rx="8" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="546" y="110" text-anchor="middle" font-weight="700" fill="#8d5433">Offering</text>
    <text x="546" y="125" text-anchor="middle" fill="#6b6478">price, shop</text>
    <path d="M420 52 L520 92" stroke="#e0c3ac" stroke-width="1.4"/>
    <text x="470" y="68" fill="#9990a8" font-size="9.5">soldAs</text>

    <rect x="624" y="92" width="76" height="42" rx="8" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="662" y="110" text-anchor="middle" font-weight="700" fill="#8d5433">Retailer</text>
    <text x="662" y="125" text-anchor="middle" fill="#6b6478">6 shops</text>
    <path d="M612 113 L624 113" stroke="#e0c3ac" stroke-width="1.4"/>

    <rect x="328" y="160" width="132" height="42" rx="8" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="394" y="178" text-anchor="middle" font-weight="700" fill="#3f6b48">IngredientFunction</text>
    <text x="394" y="193" text-anchor="middle" fill="#6b6478">79 CosIng functions</text>
    <path d="M394 134 L394 160" stroke="#a8c9ae" stroke-width="1.4"/>
    <text x="398" y="150" fill="#9990a8" font-size="9.5">hasFunction</text>

    <rect x="24" y="160" width="132" height="42" rx="8" fill="#f9eef4" stroke="#b06a97"/>
    <text x="90" y="178" text-anchor="middle" font-weight="700" fill="#8d4470">SkinType</text>
    <text x="90" y="193" text-anchor="middle" fill="#6b6478">5 values</text>
    <rect x="176" y="160" width="132" height="42" rx="8" fill="#f9eef4" stroke="#b06a97"/>
    <text x="242" y="178" text-anchor="middle" font-weight="700" fill="#8d4470">Sensitivity</text>
    <text x="242" y="193" text-anchor="middle" fill="#6b6478">2 values</text>

    <rect x="150" y="230" width="180" height="46" rx="9" fill="#584a7a"/>
    <text x="240" y="249" text-anchor="middle" fill="#fff" font-weight="700">SuitabilityClaim</text>
    <text x="240" y="265" text-anchor="middle" fill="#d5cae8">the product is for X skin</text>
    <path d="M330 40 C240 40 130 120 172 232" stroke="#b9aed0" fill="none" stroke-width="1.4"/>
    <text x="120" y="222" fill="#9990a8" font-size="9.5">hasClaim</text>
    <path d="M120 202 L180 230" stroke="#dcb6cd" stroke-width="1.4"/>
    <path d="M250 202 L248 230" stroke="#dcb6cd" stroke-width="1.4"/>
    <text x="262" y="220" fill="#9990a8" font-size="9.5">appliesTo</text>

    <rect x="380" y="230" width="190" height="46" rx="9" fill="#6f9c78"/>
    <text x="475" y="249" text-anchor="middle" fill="#fff" font-weight="700">Evidence</text>
    <text x="475" y="265" text-anchor="middle" fill="#dbeadd">source, tier, quote, link</text>
    <path d="M330 253 L380 253" stroke="#6f9c78" stroke-width="2"/>
    <polygon points="380,253 372,248 372,258" fill="#6f9c78"/>
    <text x="336" y="246" fill="#3f6b48" font-size="9.5">supportedBy</text>

    <rect x="596" y="230" width="104" height="46" rx="9" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="648" y="249" text-anchor="middle" font-weight="700" fill="#3f6b48">SourceType</text>
    <text x="648" y="265" text-anchor="middle" fill="#6b6478">tiers 1 to 4</text>
    <path d="M570 253 L596 253" stroke="#a8c9ae" stroke-width="1.4"/>

    <rect x="24" y="304" width="150" height="42" rx="8" fill="#f9eef4" stroke="#b06a97"/>
    <text x="99" y="322" text-anchor="middle" font-weight="700" fill="#8d4470">SkinConcern</text>
    <text x="99" y="337" text-anchor="middle" fill="#6b6478">acne, dryness, ageing</text>
    <path d="M300 58 C160 100 90 220 92 304" stroke="#dcb6cd" fill="none" stroke-width="1.4"/>
    <text x="30" y="290" fill="#9990a8" font-size="9.5">addresses</text>

    <rect x="196" y="304" width="150" height="42" rx="8" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="271" y="322" text-anchor="middle" font-weight="700" fill="#8d5433">Review</text>
    <text x="271" y="337" text-anchor="middle" fill="#6b6478">rating, count, text</text>

    <rect x="368" y="304" width="150" height="42" rx="8" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="443" y="322" text-anchor="middle" font-weight="700" fill="#8d5433">Market</text>
    <text x="443" y="337" text-anchor="middle" fill="#6b6478">Lebanon, global</text>

    <rect x="540" y="304" width="160" height="42" rx="8" fill="#f4f0fa" stroke="#7a68a6"/>
    <text x="620" y="322" text-anchor="middle" font-weight="700" fill="#584a7a">Formulation</text>
    <text x="620" y="337" text-anchor="middle" fill="#6b6478">the ingredient list itself</text>

    <rect x="24" y="368" width="676" height="48" rx="9" fill="#eef6ee" stroke="#6f9c78" stroke-width="1.6"/>
    <text x="362" y="388" text-anchor="middle" fill="#3f6b48" font-weight="700">The two classes in the middle are the point of this design.</text>
    <text x="362" y="406" text-anchor="middle" fill="#6b6478">A claim is a thing in its own right, and it carries its evidence. Most published cosmetic ontologies attach the skin type straight to the product, which loses where it came from.</text>
  </svg>
  <div class="cap">Eleven classes. Colour is only grouping: purple for the
  product side, green for chemistry and evidence, orange for market and
  reviews, pink for skin.</div></div>

  <h3>Every class, why it is there, and where it comes from</h3>
  {tbl(['class', 'why I added it', 'the column it comes from', 'answers'], [
    ['<b>Product</b>',
     'the thing everything else hangs off. one individual per row.',
     '<code>product_id</code>, <code>name</code>', 'all'],
    ['<b>Brand</b>',
     'so I can ask about a maker rather than a product, and separate Lebanese brands from international ones sold here.',
     '<code>brand</code>, <code>country</code>', 'Q6'],
    ['<b>ProductCategory</b>',
     f'a cleanser and a sunscreen are not comparable. {CATS} categories, the same list in both sources.',
     '<code>product_type</code>', 'Q7'],
    ['<b>Ingredient</b>',
     'its own class, not text on the product. an ingredient appears in thousands of products and has properties of its own.',
     '<code>ingredients</code>, standardised to INCI', 'Q3, Q4, Q9'],
    ['<b>IngredientFunction</b>',
     'the official reason an ingredient is in the formula. this is what lets the ontology reason from chemistry to skin instead of just storing a label.',
     'EU CosIng function field, 79 functions', 'Q4, Q9'],
    ['<b>Formulation</b>',
     'the ingredient list as a thing in itself, so two products with different names and one formula can be recognised as the same.',
     'the full <code>ingredients</code> string', 'Q7'],
    ['<b>SkinType</b>',
     'five values: Dry, Oily, Combination, Normal, All.',
     '<code>skin_type</code>', 'Q1, Q2'],
    ['<b>Sensitivity</b>',
     'kept separate from skin type on purpose. a product can be oily and sensitive, or oily and resistant. this follows Baumann.',
     '<code>sensitivity</code>', 'Q1, Q11'],
    ['<b>SkinConcern</b>',
     'what the product is meant to help with. different from skin type: dry skin is a state, acne is a concern.',
     '<code>concerns</code>, <code>benefits</code>', 'Q8'],
    ['<b>SuitabilityClaim</b>',
     '<b>the claim is its own thing, not a value on the product.</b> that is what lets it carry who said it and how strongly.',
     '<code>skin_type</code> + <code>skin_type_rule</code>', 'Q5, Q10'],
    ['<b>Evidence</b>',
     '<b>the source, the tier, the sentence and the link.</b> this is the class that makes the ontology auditable.',
     '<code>skin_type_source</code>, <code>_tier</code>, <code>_quote</code>, <code>_url</code>', 'Q5, Q10'],
    ['<b>Offering</b>',
     'a product sold by a shop at a price. the same product has several offerings, which is exactly the Lebanese situation.',
     '<code>price_usd</code>, <code>retailers</code>', 'Q2, Q12'],
    ['<b>Retailer</b>', 'the six Lebanese shops, so availability can be asked about.',
     '<code>retailers</code>', 'Q2, Q12'],
    ['<b>Market</b>', 'separates "sold in Lebanon" from "made in Lebanon".',
     '<code>source</code>, <code>country</code>', 'Q2, Q6'],
    ['<b>Review</b>', 'ratings and review text, kept as its own class so several reviews can attach to one product.',
     '<code>rating</code>, <code>review_count</code>, <code>review_texts_json</code>', 'Q8']])}

  <h3>Why the claim and the evidence are separate classes</h3>
  <p>This is the one design decision I would defend hardest, so it is worth
  showing rather than describing.</p>
  <div class="dg">
  <svg viewBox="0 0 700 210" xmlns="http://www.w3.org/2000/svg" font-family="Segoe UI,Arial" font-size="11.5">
    <text x="14" y="18" font-weight="700" fill="#8d3a3e">the usual way</text>
    <rect x="14" y="26" width="150" height="38" rx="8" fill="#fdeeee" stroke="#b5484d"/>
    <text x="89" y="50" text-anchor="middle" fill="#8d3a3e" font-weight="700">Product</text>
    <path d="M164 45 L214 45" stroke="#b5484d" stroke-width="1.6"/>
    <polygon points="214,45 206,40 206,50" fill="#b5484d"/>
    <text x="189" y="38" text-anchor="middle" fill="#9990a8" font-size="9.5">hasSkinType</text>
    <rect x="220" y="26" width="110" height="38" rx="8" fill="#fdeeee" stroke="#b5484d"/>
    <text x="275" y="50" text-anchor="middle" fill="#8d3a3e" font-weight="700">Dry</text>
    <text x="346" y="42" fill="#8d3a3e" font-size="11">the source is gone. you cannot ask who said it,</text>
    <text x="346" y="57" fill="#8d3a3e" font-size="11">or whether two sources disagreed.</text>

    <text x="14" y="98" font-weight="700" fill="#3f6b48">the way I propose</text>
    <rect x="14" y="106" width="120" height="38" rx="8" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="74" y="130" text-anchor="middle" fill="#3f6b48" font-weight="700">Product</text>
    <path d="M134 125 L172 125" stroke="#6f9c78" stroke-width="1.6"/>
    <polygon points="172,125 164,120 164,130" fill="#6f9c78"/>
    <text x="153" y="118" text-anchor="middle" fill="#9990a8" font-size="9.5">hasClaim</text>
    <rect x="178" y="106" width="140" height="38" rx="8" fill="#584a7a"/>
    <text x="248" y="124" text-anchor="middle" fill="#fff" font-weight="700">SuitabilityClaim</text>
    <text x="248" y="138" text-anchor="middle" fill="#d5cae8">appliesTo: Dry</text>
    <path d="M318 125 L356 125" stroke="#6f9c78" stroke-width="1.6"/>
    <polygon points="356,125 348,120 348,130" fill="#6f9c78"/>
    <text x="337" y="118" text-anchor="middle" fill="#9990a8" font-size="9.5">supportedBy</text>
    <rect x="362" y="98" width="322" height="54" rx="8" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="374" y="116" fill="#3f6b48" font-weight="700">Evidence</text>
    <text x="374" y="131" fill="#6b6478" font-size="10.5">source: cerave.com &nbsp; tier: 1, the manufacturer</text>
    <text x="374" y="145" fill="#6b6478" font-size="10.5">quote: "suitable for normal to dry skin" &nbsp; url: ...</text>

    <rect x="14" y="166" width="670" height="34" rx="8" fill="#fbf3ec" stroke="#c07a54"/>
    <text x="349" y="187" text-anchor="middle" fill="#8d5433">Two sources that disagree become two claims on the same product, each with its own evidence. Nothing has to be thrown away to make the model work.</text>
  </svg>
  <div class="cap">One extra step in the model, and the whole provenance
  question becomes answerable.</div></div>
  <p>It also solves a problem I already have in the data. 270 Lebanese products
  are stocked by more than one shop and the shops <b>disagree</b> about the skin
  type. In the usual model I would have to pick one and lose the other. Here
  both are kept, each with its own evidence, and question 10 can be asked.</p>

  <h3>What I would reuse rather than invent</h3>
  <p>NeOn is built around reuse, and there is no reason to define a class for a
  price when a standard one exists.</p>
  {tbl(['existing vocabulary', 'what I take from it'], [
    ['<b>schema.org</b>', '<code>Product</code>, <code>Brand</code>, <code>Offer</code>, <code>Review</code>, <code>AggregateRating</code>. widely used and understood.'],
    ['<b>GoodRelations</b> (Hepp, 2008)', 'the offering model: the same product sold by different shops at different prices. this is exactly the Lebanese retail structure.'],
    ['<b>PROV-O</b> (W3C)', 'the standard way to say where a statement came from. my Evidence class is a specialisation of it rather than something new.'],
    ['<b>ChEBI</b>', 'chemical identity for ingredients where an INCI name maps to a known compound.'],
    ['<b>EU CosIng</b>', 'the ingredient list and the 79 official functions. not an ontology, but it is the authority, and it is already in my pipeline.'],
    ['<b>SKOS</b>', 'for the category and concern lists, which are vocabularies rather than strict classes.']])}
  <div class="note">Only <b>SuitabilityClaim</b>, <b>Evidence</b>,
  <b>SkinType</b>, <b>Sensitivity</b> and <b>Formulation</b> would be new. The
  rest is existing work, which is both less effort and easier to defend.</div>

  <h3>The properties</h3>
  {tbl(['property', 'from', 'to'], [
    ['<code>madeBy</code>', 'Product', 'Brand'],
    ['<code>hasCategory</code>', 'Product', 'ProductCategory'],
    ['<code>hasFormulation</code>', 'Product', 'Formulation'],
    ['<code>contains</code>', 'Formulation', 'Ingredient'],
    ['<code>hasFunction</code>', 'Ingredient', 'IngredientFunction'],
    ['<code>hasClaim</code>', 'Product', 'SuitabilityClaim'],
    ['<code>appliesTo</code>', 'SuitabilityClaim', 'SkinType or Sensitivity'],
    ['<code>supportedBy</code>', 'SuitabilityClaim', 'Evidence'],
    ['<code>fromSource</code>', 'Evidence', 'SourceType (tier 1 to 4)'],
    ['<code>addresses</code>', 'Product', 'SkinConcern'],
    ['<code>soldAs</code>', 'Product', 'Offering'],
    ['<code>offeredBy</code>', 'Offering', 'Retailer'],
    ['<code>availableIn</code>', 'Offering', 'Market'],
    ['<code>hasReview</code>', 'Product', 'Review']])}
  <p class="small">Data properties carry the plain values: price, rating,
  review count, SPF, the quote, the URL and the tier number.</p>
</section>
"""

# ============================================================ O3
O3 = f"""
<section class="section" id="on-check">
  <h2>O3 &middot; How I will check the ontology is right</h2>
  <p class="lead">Two different things have to be checked, and they are often
  confused. Whether it is <b>logically sound</b>, and whether it is
  <b>useful</b>. A perfectly consistent ontology that cannot answer any of my
  questions is a failure.</p>

  {tbl(['check', 'tool', 'what it catches'], [
    ['<b>consistency</b>', 'HermiT reasoner in Prot&eacute;g&eacute;',
     'contradictions. for example a class defined so that nothing could ever belong to it.'],
    ['<b>common mistakes</b>', 'OOPS! (Poveda-Villal&oacute;n et al.)',
     'a published list of pitfalls: missing inverse properties, classes with no definition, circular hierarchies, unused elements.'],
    ['<b>does it answer the questions</b>', 'the 12 competency questions, written as SPARQL',
     'the real test. each question becomes a query, and it either returns sensible results or the model is missing something.'],
    ['<b>does it match the data</b>', 'counts from the ontology against counts from the file',
     f'if the ontology says a different number of products from the {f(N)} in my dataset, something was lost when it was filled.']])}

  <h3>A competency question as a query</h3>
  <p>Question 1: <i>which products suit dry and sensitive skin at the same
  time?</i></p>
  <pre>SELECT ?product ?brand ?tier WHERE {{
    ?product  :hasClaim      ?c1 , ?c2 ;
              :madeBy        ?brand .
    ?c1       :appliesTo     :Dry .
    ?c2       :appliesTo     :Sensitive .
    ?c1       :supportedBy   ?e .
    ?e        :fromSource    ?tier .
}}</pre>
  <p class="small">The reason this is worth showing: the query can ask for the
  <b>evidence tier</b> in the same breath as the answer. A reader can require
  manufacturer-level evidence and get a smaller, stronger answer, or accept
  everything and get a bigger, weaker one. That choice is the same one the
  dataset already offers through the tier column, carried into the ontology.</p>

  <h3>What I expect to go wrong</h3>
  {tbl(['likely problem', 'what I will do'], [
    ['ingredient names that did not map to CosIng',
     'they stay as their own individuals, marked as unmapped, rather than being dropped or guessed at'],
    [f'the {f(N - int(got.sum()))} products with no skin type',
     'they get no SuitabilityClaim at all. an ontology should not invent a claim nobody made'],
    ['products with no ingredient list',
     'no Formulation. the product still exists and can still be asked about in other ways'],
    ['the shops disagreeing about skin type',
     'two claims, two pieces of evidence. this is handled by the design rather than being a problem to fix'],
    ['the ontology growing beyond what anyone needs',
     'the 12 questions are the limit. a class that answers none of them does not go in']])}

  <h3>References</h3>
  {tbl(['reference', 'used for'], [
    ['Noy, N. &amp; McGuinness, D. (2001). <i>Ontology Development 101: A Guide to Creating Your First Ontology.</i> Stanford.',
     'the basic steps, and defining classes and properties'],
    ['Fern&aacute;ndez-L&oacute;pez, M., G&oacute;mez-P&eacute;rez, A. &amp; Juristo, N. (1997). METHONTOLOGY: From Ontological Art Towards Ontological Engineering. <i>AAAI Symposium.</i>',
     'the life cycle, and the method used by the published skincare ontology'],
    ['Su&aacute;rez-Figueroa, M.C., G&oacute;mez-P&eacute;rez, A. &amp; Fern&aacute;ndez-L&oacute;pez, M. (2015). The NeOn Methodology framework. <i>Applied Ontology</i> 10(2).',
     'reuse of existing ontologies rather than building from nothing'],
    ['Gr&uuml;ninger, M. &amp; Fox, M. (1995). Methodology for the Design and Evaluation of Ontologies. <i>IJCAI Workshop.</i>',
     'competency questions, used to fix the scope and to test the result'],
    ['Poveda-Villal&oacute;n, M., G&oacute;mez-P&eacute;rez, A. &amp; Su&aacute;rez-Figueroa, M.C. OOPS! (OntOlogy Pitfall Scanner!).',
     'checking for common modelling mistakes'],
    ['Glimm, B. et al. HermiT: A Highly-Efficient OWL Reasoner.',
     'checking the ontology is consistent'],
    ['Hepp, M. (2008). GoodRelations: An Ontology for Describing Products and Services Offers on the Web. <i>EKAW.</i>',
     'the offering model for price and availability'],
    ['W3C (2013). PROV-O: The PROV Ontology.',
     'the standard way to record where a statement came from'],
    ['Baumann, L. <i>The Skin Type Solution.</i>',
     'skin type and sensitivity as two separate axes'],
    ['Vendruscolo et al. (2025). <i>Dermatological Reviews</i> 6:e70045.',
     '"all skin types" is a tolerance claim, not a classification'],
    ['EU Regulation 1223/2009, Article 33; CosIng database.',
     'the ingredient list and the 79 official ingredient functions'],
    ['Rahm, E. &amp; Do, H. (2000). Data Cleaning: Problems and Current Approaches.',
     'clean each source before joining, which is what made this stage possible'],
    ['Fellegi, I. &amp; Sunter, A. (1969). A Theory for Record Linkage. <i>JASA.</i>',
     'the two-threshold matching used to join the sources']])}
</section>
"""

html = PORTAL.read_text(encoding='utf-8')
html = re.sub(r'<section class="section" id="on-(ready|model|check)">.*?</section>',
              '', html, flags=re.S)
anchor = html.find('<!-- ============================================ HOME -->')
if anchor == -1:
    anchor = html.find('<section class="section" id="home">')
if anchor == -1:
    raise SystemExit('could not find where to insert, portal not changed')
html = html[:anchor] + O1 + O2 + O3 + '\n\n' + html[anchor:]

if 'on-ready' not in re.search(r'<nav class="nav">.*?</nav>', html, re.S).group(0):
    nav = re.search(r'(\s*<div class="grp">overview</div>)', html)
    html = (html[:nav.start()] +
            '\n    <div class="grp">ontology</div>\n'
            '    <a data-s="on-ready">O1. Dataset to ontology</a>\n'
            '    <a data-s="on-model">O2. The proposed model</a>\n'
            '    <a data-s="on-check">O3. Checking it</a>' + nav.group(1) +
            html[nav.end():])

PORTAL.write_text(html, encoding='utf-8')

w = {}
for m in re.finditer(r'<section class="section[^"]*" id="(on-[^"]+)">(.*?)</section>',
                     html, re.S):
    w[m.group(1)] = len(re.sub(r'<[^>]+>', ' ', m.group(2)).split())
print('=' * 58)
print('  ONTOLOGY PAGES ADDED')
print('=' * 58)
for k, v in w.items():
    print(f'    {k:12s}{v:6,} words')
print(f'\n  {sum(w.values()):,} words total, 3 diagrams, 12 competency questions')
print(f'  15 classes, 14 object properties, 13 references')
print(f'  dataset figures used: {f(N)} products, {f(BRANDS)} brands, {CATS} categories')
