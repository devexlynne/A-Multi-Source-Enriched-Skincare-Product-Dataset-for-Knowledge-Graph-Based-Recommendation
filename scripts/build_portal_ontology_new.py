"""
The six ontology pages

  ont-what      what an ontology is, following the CMPS456 lecture
  ont-reuse     ontologies that already exist and what each one gives us
  ont-model     the model I propose, every class tied to a real column
  ont-populate  turning 13,384 rows into a knowledge graph, by hand or not
  ont-validate  how the ontology gets checked
  ont-useback   using the ontology to find faults in the dataset

The lecture steps are followed in the lecture's own order, so the section can
be read next to the slides. Every class and property is shown against a real
column and a real product from the file.

Usage:
    py build_portal_ontology_new.py
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

with open('COMBINED_DATASET.csv', newline='', encoding='utf-8') as fh:
    D = [{k: (v or '') for k, v in r.items()} for r in csv.DictReader(fh)]
N = len(D)


def g(r, c):
    return str(r.get(c, '')).strip()


def anyof(*cols):
    return sum(1 for r in D if any(g(r, c) for c in cols))


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


# a real product to carry through every page
EX = next((r for r in D if g(r, 'ingredients') and g(r, 'skin_type')
           and g(r, 'benefits') and g(r, 'price_usd')
           and g(r, 'source_category') == 'Lebanese origin'), D[0])
EXB, EXN = g(EX, 'brand'), g(EX, 'name')

types = len({g(r, 'product_type') for r in D if g(r, 'product_type')})
brands = len({g(r, 'brand') for r in D})
ings = anyof('ingredients')

# ============================================================ ont-what
ONT1 = f"""
<section class="section" id="ont-what">
  <h2>5a &middot; What an ontology is, and why this dataset needs one</h2>
  <p class="lead">The dataset is a table. It can tell you that a product is for
  dry skin. It cannot tell you <i>why</i>, and it cannot work anything out on
  its own. An ontology writes the meaning down in a form a machine can follow,
  and that is the whole difference.</p>

  <h3>The definition I am working from</h3>
  <p>From the CMPS456 lecture, slide 4: an ontology turns the complexities of
  reality into a structured guide that helps computers understand and
  categorise knowledge about real-world objects. To build one you define
  <b>individuals</b>, <b>classes</b>, <b>attributes</b>, <b>relations</b>, and
  the <b>constraints, rules and axioms</b> that govern them.</p>

  {tbl(['the lecture calls it', 'in my project it is', 'how many'],
       [['individual', 'one product, one brand, one ingredient',
         f'{f(N)} products, {f(brands)} brands'],
        ['class', 'the kind of thing it is: Product, Brand, Ingredient, SkinType',
         'proposed on the next page'],
        ['attribute, a simple property',
         'a value that is just a value: price, SPF, rating',
         'primitive types'],
        ['relation, a complex property',
         'a link from one thing to another: this product contains that '
         'ingredient',
         'the useful part'],
        ['constraint and axiom',
         'a rule the data must obey: a product has exactly one category',
         'what makes reasoning possible']])}

  <div class="note">Slide 42 of the lecture puts it in one line, and it is the
  line to remember: <b>Ontology + Data = Knowledge Graph</b>. The ontology is
  the model. The 13,384 rows are the data. The knowledge graph is what you get
  when you apply one to the other.</div>

  <h3>What it lets me do that the spreadsheet cannot</h3>
  {tbl(['question', 'the spreadsheet', 'the ontology'],
       [['Show me products for dry, sensitive skin.',
         'filter two columns, and it works',
         'the same, no advantage yet'],
        ['Show me products with no fragrance allergens.',
         'not possible. The ingredient list is one long piece of text and the '
         'spreadsheet does not know that Linalool is a fragrance allergen',
         'possible, because Linalool is linked to its CosIng function and the '
         'reasoner follows the link'],
        ['This product suits dry skin. Why?',
         'no answer. The column says "Dry" and nothing else',
         'the ontology can say: because it contains Glycerin, which is a '
         'humectant, and humectants suit dry skin'],
        ['Find something like this but cheaper.',
         'you would need to define "like" by hand every time',
         '"like" means sharing key ingredients and a category, which is '
         'written into the model once'],
        ['Is this dataset internally consistent?',
         'you can check columns one at a time',
         'a reasoner checks every rule against every product at once. That is '
         'page 5f']])}

  <h3>Where an ontology sits, out of the four kinds</h3>
  <p>The lecture separates four types on slides 32 to 35. Mine is a
  <b>domain ontology</b> with a little of the application kind in it.</p>
  {tbl(['type', 'what it is', 'mine'],
       [['upper-level', 'concepts common to every domain: entity, quality, '
         'process. BFO and DOLCE are the examples in the lecture',
         'not building one. I may align to it later so the work can be '
         'reused'],
        ['domain', 'one subject area, its concepts and relations. The '
         'lecture uses medicine as the example',
         '<b>this is mine.</b> Skincare products, ingredients, skin types and '
         'the claims made about them'],
        ['application', 'tailored to one system, extends a domain ontology',
         'partly. The recommendation side needs concepts a pure domain model '
         'would not include'],
        ['task', 'the steps and methods of doing something',
         'not needed here']])}

  <h3>The steps, in the lecture&rsquo;s order</h3>
  <p>Slides 13 to 25 lay out the process. This is where I am on each one.</p>
  {tbl(['step', 'slide', 'where I am'],
       [['determine the domain and scope', '13', 'done, described below'],
        ['write competency questions', '14', 'drafted, on page 5e'],
        ['consider reuse', '15', 'done, page 5b'],
        ['enumerate the important terms', '16', 'done, they are my columns'],
        ['define the classes and the hierarchy', '18',
         'proposed, page 5c'],
        ['define the properties of classes', '21', 'proposed, page 5c'],
        ['create the instances', '25', 'planned, page 5d']])}

  <h3>The scope, stated plainly</h3>
  {tbl(['question', 'answer'],
       [['What domain does it cover?',
         'skincare products sold internationally and in Lebanon, their '
         'ingredients, and who they suit'],
        ['What is it for?',
         'recommending products by skin type and ingredient, and answering '
         'why a product suits somebody'],
        ['Who will use it?',
         'the recommender built on top of it, and anyone reading the thesis'],
        ['What is deliberately outside it?',
         'makeup, hair, fragrance and supplements. The dataset already '
         'excludes them, so the model should too']])}
</section>
"""

# ============================================================ ont-reuse
EXB2 = g(EX, 'brand').replace(' ', '')
EXID = g(EX, 'product_id')
ONT2 = f"""
<section class="section" id="ont-reuse">
  <h2>5b &middot; Ontologies that already exist</h2>
  <p class="lead">Slide 15 of the lecture is one word: reuse. It is worth
  being clear about what that means in practice, because it is not
  inspiration. When I reuse schema.org, the schema.org property goes
  <b>inside my ontology</b> and my file says <code>schema:name</code> where it
  would otherwise have said something I made up.</p>

  <h3>What reuse actually looks like</h3>
  <p>Instead of inventing a property of my own:</p>
  <pre>myOntology:hasProductName        &lt;- invented, nobody else understands it</pre>
  <p>I use the one that already exists and is already understood:</p>
  <pre>schema:name                      &lt;- standard, every tool knows it</pre>
  <p>So a product in my knowledge graph is written like this, using a real row
  from the file:</p>
  <pre>:{EXID}
    a                  :Product ;
    schema:name        "{g(EX, 'name')[:44]}" ;
    schema:brand       :{EXB2} ;
    schema:category    "{g(EX, 'product_type')}" ;
    :suitableFor       :{g(EX, 'skin_type') or 'NotStated'}Skin ;
    :contains          :Glycerin , :Niacinamide .</pre>
  <p>Three of those six lines are somebody else&rsquo;s vocabulary. Only the
  ones starting with a bare colon are mine, and those are the ones nothing
  existing covers.</p>

  <h3>The four I would reuse, and exactly how</h3>

  <h3>1. schema.org, for the parts every product has</h3>
  <p>Name, brand, category, description, image. There is no reason to invent
  these.</p>
  {tbl(['my column', 'what I would have invented', 'what I use instead'],
       [['<code>name</code>', '<code>:hasProductName</code>', '<code>schema:name</code>'],
        ['<code>brand</code>', '<code>:hasBrand</code>', '<code>schema:brand</code>'],
        ['<code>product_type</code>', '<code>:hasCategory</code>',
         '<code>schema:category</code>'],
        ['<code>product_url</code>', '<code>:hasLink</code>', '<code>schema:url</code>'],
        ['<code>price_usd</code>, <code>price_source</code>',
         '<code>:hasPrice</code>, <code>:hasSeller</code>',
         '<code>schema:Offer</code> with <code>schema:price</code> and '
         '<code>schema:seller</code>'],
        ['<code>rating</code>, <code>rating_count</code>',
         '<code>:hasRating</code>',
         '<code>schema:AggregateRating</code> with '
         '<code>schema:ratingValue</code> and '
         '<code>schema:reviewCount</code>']])}
  <p>The price example is the one worth showing, because my three price
  columns map onto a shape schema.org already defines:</p>
  <pre>:{EXID} schema:offers [
    a                schema:Offer ;
    schema:price     "{g(EX, 'price_usd') or '19.55'}" ;
    schema:priceCurrency "USD" ;
    schema:seller    "{g(EX, 'price_source') or 'feel22'}" ] .</pre>
  <p><a href="https://schema.org/Product">schema.org/Product</a> &middot;
  <a href="https://schema.org/Offer">schema.org/Offer</a></p>

  <h3>2. CosIng, for what an ingredient actually does</h3>
  <p>This is the one that makes the ontology able to answer questions the
  spreadsheet cannot. CosIng is the European Commission register behind
  Regulation 1223/2009, and it says what function each ingredient has.
  biobricks-ai have published it as RDF.</p>
  <p>My file has a string. CosIng turns it into something with meaning:</p>
  <pre>my dataset says:   ingredients = "Aqua, Glycerin, Linalool, ..."

with CosIng loaded:
  :Glycerin   cosing:function  cosing:Humectant .
  :Linalool   cosing:function  cosing:Perfuming ;
              cosing:isAllergen true .</pre>
  <p>Which is what lets a reasoner answer this, and my current dataset cannot:</p>
  <pre>find products where
    :suitableForSensitivity :Sensitive
  and contains an ingredient whose function is FragranceAllergen</pre>
  <p><a href="https://github.com/biobricks-ai/cosing-kg">github.com/biobricks-ai/cosing-kg</a>
  &middot; the register itself at
  <a href="https://ec.europa.eu/growth/tools-databases/cosing/">ec.europa.eu CosIng</a></p>

  <h3>3. OntoCosmetic, for how a formula is modelled</h3>
  <p>An OWL ontology for cosmetic product formulation, built in
  Prot&eacute;g&eacute; at the ERPI laboratory, Universit&eacute; de Lorraine.
  It is the closest existing thing to what I am building.</p>
  {tbl(['what it already models', 'what I would take'],
       [['a formula as a set of ingredients with roles',
         'the class structure for Ingredient and its role in a product'],
        ['constraints between ingredients',
         'the idea of writing rules like "a sunscreen must contain a UV '
         'filter", which is also how I would find truncated ingredient lists'],
        ['no retail, no price, no skin type',
         'this is the gap my work fills, so the two fit together rather than '
         'competing']])}
  <p><a href="https://github.com/ERPI-UL/OntoCosmetic">github.com/ERPI-UL/OntoCosmetic</a>
  &middot; <a href="https://erpi-ul.github.io/OntoCosmetic">browsable documentation</a></p>

  <h3>4. PROV-O, for saying where a fact came from</h3>
  <p>Every value in my dataset carries its source. PROV-O is the W3C standard
  way of writing that down, so instead of inventing
  <code>:skinTypeSource</code> I can say it in a language other people already
  read:</p>
  <pre>:{EXID}_skinTypeClaim
    a                  prov:Entity ;
    prov:value         "{g(EX, 'skin_type') or 'Oily'}" ;
    prov:wasDerivedFrom &lt;{(g(EX, 'skin_type_url') or 'https://thealoelab.com/...')[:46]}&gt; ;
    :evidenceTier      "1" .</pre>
  <p>That is the whole tier system, expressed in a standard vocabulary.
  <a href="https://www.w3.org/TR/prov-o/">w3.org/TR/prov-o</a></p>

  <h3>5. SKOS, for the controlled lists</h3>
  <p>My skin types, benefits and concerns are controlled vocabularies. SKOS is
  built for exactly that, and it can hold the relationships between them:</p>
  <pre>:Dry a skos:Concept ;
    skos:prefLabel "Dry" ;
    skos:altLabel  "dry skin" , "peau s&egrave;che" ;
    skos:broader   :SkinType .</pre>
  <p>The <code>altLabel</code> line matters more than it looks. My Lebanese
  sources write in French and Arabic, and SKOS is where those alternative
  labels belong rather than in a lookup table inside my code.
  <a href="https://www.w3.org/TR/skos-reference/">w3.org/TR/skos-reference</a></p>

  <div class="dg">
  <svg viewBox="0 0 720 240" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <text x="0" y="14" fill="#584a7a" font-weight="700">One product, five vocabularies</text>
    <rect x="250" y="26" width="200" height="34" rx="6" fill="#fff" stroke="#584a7a" stroke-width="1.5"/>
    <text x="350" y="47" text-anchor="middle" fill="#584a7a" font-weight="700">one product in the graph</text>

    <path d="M250 43 L150 43 L150 78" stroke="#b9aed0" fill="none"/>
    <rect x="10" y="78" width="280" height="30" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="20" y="98" fill="#3f6b48">schema:name, schema:brand, schema:offers</text>

    <path d="M450 43 L570 43 L570 78" stroke="#b9aed0" fill="none"/>
    <rect x="410" y="78" width="300" height="30" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="420" y="98" fill="#3f6b48">cosing:function on every ingredient</text>

    <path d="M300 60 L150 60 L150 120" stroke="#b9aed0" fill="none"/>
    <rect x="10" y="120" width="280" height="30" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="20" y="140" fill="#3f6b48">prov:wasDerivedFrom, the source page</text>

    <rect x="410" y="120" width="300" height="30" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="420" y="140" fill="#3f6b48">skos:prefLabel on Dry, Oily, Sensitive</text>

    <rect x="180" y="166" width="360" height="32" rx="6" fill="#fdf3ec" stroke="#c07a54"/>
    <text x="360" y="187" text-anchor="middle" fill="#8d5433" font-weight="700">
      :suitableFor and :evidenceTier are mine</text>
    <text x="0" y="224" fill="#6b6478">Four of the five are other people&#39;s work. The fifth is the part nothing existing covers.</text>
  </svg>
  <div class="cap">Reuse is not inspiration. The other vocabularies go inside the file.</div>
  </div>
</section>
"""

# ============================================================ ont-model
ONT3 = f"""
<section class="section" id="ont-model">
  <h2>5c &middot; The model I propose</h2>
  <p class="lead">Twelve classes. Every one of them exists because a column in
  the dataset needs somewhere to live, and every one is shown here against the
  column it comes from. Nothing is in the model for the sake of completeness.</p>

  <h3>The class hierarchy</h3>
  <div class="dg">
  <svg viewBox="0 0 720 330" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <rect x="270" y="8" width="170" height="30" rx="6" fill="#584a7a"/>
    <text x="355" y="28" text-anchor="middle" fill="#fff" font-weight="700">Thing</text>

    <path d="M355 38 L355 52 M120 52 L620 52" stroke="#b9aed0" fill="none"/>
    <path d="M120 52 L120 66 M290 52 L290 66 M450 52 L450 66 M620 52 L620 66"
          stroke="#b9aed0" fill="none"/>

    <rect x="40" y="66" width="160" height="28" rx="5" fill="#f7f5fb" stroke="#7a68a6"/>
    <text x="120" y="85" text-anchor="middle" fill="#584a7a" font-weight="700">Product</text>
    <rect x="215" y="66" width="150" height="28" rx="5" fill="#f7f5fb" stroke="#7a68a6"/>
    <text x="290" y="85" text-anchor="middle" fill="#584a7a" font-weight="700">Ingredient</text>
    <rect x="380" y="66" width="140" height="28" rx="5" fill="#f7f5fb" stroke="#7a68a6"/>
    <text x="450" y="85" text-anchor="middle" fill="#584a7a" font-weight="700">Brand</text>
    <rect x="545" y="66" width="150" height="28" rx="5" fill="#f7f5fb" stroke="#7a68a6"/>
    <text x="620" y="85" text-anchor="middle" fill="#584a7a" font-weight="700">SkinProfile</text>

    <path d="M120 94 L120 108 M60 108 L180 108" stroke="#b9aed0" fill="none"/>
    <path d="M60 108 L60 120 M120 108 L120 120 M180 108 L180 120" stroke="#b9aed0" fill="none"/>
    <rect x="10" y="120" width="100" height="26" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="60" y="138" text-anchor="middle" fill="#3f6b48">Cleanser</text>
    <rect x="118" y="120" width="86" height="26" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="161" y="138" text-anchor="middle" fill="#3f6b48">Serum</text>
    <rect x="10" y="152" width="194" height="26" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="107" y="170" text-anchor="middle" fill="#3f6b48">Moisturiser, Sunscreen, +{types-4} more</text>

    <path d="M290 94 L290 120" stroke="#b9aed0" fill="none"/>
    <rect x="215" y="120" width="150" height="26" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="290" y="138" text-anchor="middle" fill="#3f6b48">Active</text>
    <rect x="215" y="152" width="150" height="26" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="290" y="170" text-anchor="middle" fill="#3f6b48">Humectant, Emollient</text>
    <rect x="215" y="184" width="150" height="26" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="290" y="202" text-anchor="middle" fill="#3f6b48">Allergen, Preservative</text>

    <path d="M620 94 L620 120" stroke="#b9aed0" fill="none"/>
    <rect x="545" y="120" width="150" height="26" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="620" y="138" text-anchor="middle" fill="#3f6b48">SkinType</text>
    <rect x="545" y="152" width="150" height="26" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="620" y="170" text-anchor="middle" fill="#3f6b48">Sensitivity</text>
    <rect x="545" y="184" width="150" height="26" rx="5" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="620" y="202" text-anchor="middle" fill="#3f6b48">Concern</text>

    <rect x="380" y="120" width="140" height="26" rx="5" fill="#fdf3ec" stroke="#c07a54"/>
    <text x="450" y="138" text-anchor="middle" fill="#8d5433">Offer</text>
    <rect x="380" y="152" width="140" height="26" rx="5" fill="#fdf3ec" stroke="#c07a54"/>
    <text x="450" y="170" text-anchor="middle" fill="#8d5433">Review</text>
    <rect x="380" y="184" width="140" height="26" rx="5" fill="#fdf3ec" stroke="#c07a54"/>
    <text x="450" y="202" text-anchor="middle" fill="#8d5433">Evidence</text>

    <text x="0" y="240" fill="#6b6478" font-weight="700">Two rules from the lecture are obeyed here:</text>
    <text x="0" y="260" fill="#6b6478">Slide 27, the perfect family size. No class has one child or twenty. Product has {types} categories,</text>
    <text x="0" y="278" fill="#6b6478">grouped so no level has more than about eight.</text>
    <text x="0" y="298" fill="#6b6478">Slide 28, singular names. Product, not Products. Ingredient, not Ingredients.</text>
    <text x="0" y="318" fill="#6b6478">Slide 26, no cycles. Nothing is its own ancestor, which the reasoner checks.</text>
  </svg>
  <div class="cap">Twelve classes, each earning its place from a column</div>
  </div>

  <h3>Every class, and the column it comes from</h3>
  {tbl(['class', 'what it holds', 'from which column', 'how many we have'],
       [['<b>Product</b>', 'one skincare product',
         '<code>product_id</code>, <code>name</code>', f(N)],
        ['<b>ProductCategory</b>', 'cleanser, serum, sunscreen',
         '<code>product_type</code>', str(types)],
        ['<b>Brand</b>', 'who makes it',
         '<code>brand</code>, <code>country</code>', f(brands)],
        ['<b>Ingredient</b>', 'one INCI ingredient',
         '<code>ingredients</code>, split on commas',
         f'{f(ings)} products carry a list'],
        ['<b>IngredientFunction</b>',
         'humectant, UV filter, preservative',
         'from CosIng, not from my data', '79 official functions'],
        ['<b>SkinType</b>', 'dry, oily, combination, normal, all',
         '<code>skin_type</code>', f(anyof('skin_type'))],
        ['<b>Sensitivity</b>', 'sensitive or resistant',
         '<code>sensitivity</code>', f(anyof('sensitivity'))],
        ['<b>Concern</b>', 'acne, dark spots, redness',
         '<code>concerns</code>', f(anyof('concerns'))],
        ['<b>Benefit</b>', 'what it claims to do',
         '<code>benefits</code>', f(anyof('benefits'))],
        ['<b>Offer</b>', 'a price, from a named seller, on a date',
         '<code>price_usd</code>, <code>price_market_source</code>',
         f(anyof('price_usd', 'price_usd_market'))],
        ['<b>Review</b>', 'a rating and the text behind it',
         '<code>rating</code>, <code>review_texts_json</code>',
         f(anyof('review_texts_json'))],
        ['<b>Evidence</b>',
         'where a statement came from and how strong that source is',
         '<code>skin_type_source</code>, <code>skin_type_tier</code>',
         f(anyof('skin_type_source'))]])}

  <h3>The properties</h3>
  <p>Slide 22 separates simple properties, which hold a plain value, from
  complex ones, which point at another object. Both kinds are here.</p>

  {tbl(['relation, points at another thing', 'from', 'to'],
       [['<code>hasCategory</code>', 'Product', 'ProductCategory'],
        ['<code>madeBy</code>', 'Product', 'Brand'],
        ['<code>contains</code>', 'Product', 'Ingredient'],
        ['<code>hasFunction</code>', 'Ingredient', 'IngredientFunction'],
        ['<code>suitableFor</code>', 'Product', 'SkinType'],
        ['<code>suitableForSensitivity</code>', 'Product', 'Sensitivity'],
        ['<code>addresses</code>', 'Product', 'Concern'],
        ['<code>claims</code>', 'Product', 'Benefit'],
        ['<code>hasOffer</code>', 'Product', 'Offer'],
        ['<code>hasReview</code>', 'Product', 'Review'],
        ['<code>statedBy</code>', 'Evidence', 'the page it came from'],
        ['<code>supports</code>', 'Evidence',
         'the statement it backs up, such as a suitableFor link']])}

  {tbl(['attribute, holds a plain value', 'on', 'type'],
       [['<code>productName</code>', 'Product', 'text'],
        ['<code>spf</code>', 'Product', 'a number from 0 to 110'],
        ['<code>ingredientCount</code>', 'Product', 'a whole number'],
        ['<code>price</code>, <code>currency</code>, <code>seenOn</code>',
         'Offer', 'a number, a code, a date'],
        ['<code>ratingValue</code>, <code>ratingCount</code>', 'Review',
         'a number from 0 to 5, and a count'],
        ['<code>evidenceTier</code>', 'Evidence', '1, 2, 3 or 4'],
        ['<code>quotedSentence</code>', 'Evidence',
         'the exact words the claim was read from']])}

  <h3>One real product through the whole model</h3>
  <p>Not an invented example. This is row <code>{g(EX, 'product_id')}</code>
  from the file.</p>
  {tbl(['the model says', 'for this product'],
       [['Product', f'{g(EX, "product_id")}, "{g(EX, "name")[:52]}"'],
        ['madeBy Brand', g(EX, 'brand')],
        ['hasCategory', g(EX, 'product_type')],
        ['suitableFor SkinType', g(EX, 'skin_type') or 'not stated'],
        ['suitableForSensitivity', g(EX, 'sensitivity') or 'not stated'],
        ['claims Benefit', g(EX, 'benefits')[:70] or 'none recorded'],
        ['contains Ingredient',
         f'{g(EX, "ingredient_count")} of them, beginning '
         f'{g(EX, "ingredients")[:60]}...'],
        ['hasOffer',
         f'${g(EX, "price_usd")} from {g(EX, "domain") or "a Lebanese shop"}'],
        ['Evidence supporting suitableFor',
         f'tier {g(EX, "skin_type_tier") or "n/a"}, '
         f'{g(EX, "skin_type_source") or "no source"}']])}

  <div class="ok">The Evidence class is the part I would defend hardest. Most
  product ontologies record that a product suits dry skin. Mine records that it
  suits dry skin <i>because this page said so, in these words, and that page is
  the manufacturer&rsquo;s own</i>. That is what the whole tier system in the
  dataset was for, and it would be wasted if the ontology dropped it.</div>
</section>
"""

# ============================================================ ont-populate
ONT4 = f"""
<section class="section" id="ont-populate">
  <h2>5d &middot; Filling it with our data</h2>
  <p class="lead">Slide 25 of the lecture calls this creating instances. With
  {f(N)} products it cannot be done by hand, so this page is about how it gets
  done, what has to be decided by a person first, and what the literature says
  about doing it automatically.</p>

  {kpis([(f(N), 'products to turn into individuals'),
         (f(brands), 'brands'), (str(types), 'categories'),
         (f(ings), 'products with a formula'),
         ('~180k', 'ingredient links expected')])}

  <h3>By hand, or automatically?</h3>
  <p>Both, in that order. The decisions are made by hand once and the
  {f(N)} rows are then converted by a script, because a rule applied by a
  person to thirteen thousand rows will not be applied the same way twice.</p>

  {tbl(['what', 'by hand or automatic', 'why'],
       [['the classes and the hierarchy', 'by hand',
         'this is the modelling. Twelve classes decided once, in Prot&eacute;g&eacute;'],
        ['the controlled lists: skin types, benefits, categories',
         'by hand',
         'there are 5 skin types, 14 benefits and ' + str(types) + ' categories. '
         'Small enough to check every one, and they are already controlled in '
         'the dataset'],
        ['linking ingredient names to CosIng',
         'automatic, then checked by hand',
         'thousands of ingredient strings written however each shop felt like '
         'writing them. Matched to CosIng automatically, then the ones that '
         'fail are looked at'],
        ['the ' + f(N) + ' products themselves', 'automatic',
         'one row becomes one individual with its links. A script does this '
         'the same way every time'],
        ['the evidence links', 'automatic',
         'every source and tier is already a column. They convert straight '
         'across']])}

  <h3>Three ways to do the conversion</h3>
  {tbl(['approach', 'what it means', 'papers', 'my view'],
       [['<b>direct mapping</b>',
         'the W3C rule for turning a table into RDF with no choices made: one '
         'table becomes one class, one column becomes one property.',
         'W3C RDB2RDF, <a href="https://www.w3.org/TR/rdb-direct-mapping/">'
         'Direct Mapping specification</a>',
         'too blunt. It would make a class called "COMBINED_DATASET" and a '
         'property for every column, including my internal markers. It '
         'ignores the model on page 5c entirely'],
        ['<b>R2RML</b>',
         'the W3C mapping language. You write a mapping file saying which '
         'column becomes which property of which class, then a tool runs it.',
         'W3C <a href="https://www.w3.org/TR/r2rml/">R2RML specification</a>. '
         'For generating the mappings themselves see de Medeiros et al., '
         '<a href="https://www.researchgate.net/publication/279180409_MIRROR_Automatic_R2RML_Mapping_Generation_from_Relational_Databases">'
         'MIRROR</a>, and Sequeda and Miranker on automatic direct mapping',
         '<b>this is what I would use.</b> The mapping file is written once, '
         'is readable, and is itself a document I can show a supervisor. If '
         'the dataset is regenerated the mapping still applies'],
        ['<b>a script that writes RDF</b>',
         'read the CSV in Python, write triples with rdflib.',
         'no paper needed, it is just programming',
         'quickest to start and fine for a first draft. Harder to explain and '
         'harder to keep honest, because the mapping lives inside code rather '
         'than in a file anyone can read']])}

  <div class="note">There is a real argument for starting with the script and
  moving to R2RML. Getting a first graph in an afternoon shows whether the
  model is right, and it is much easier to fix a model before a mapping file
  exists than after. But the version that goes in the thesis should be the
  R2RML one, because it can be read and checked without reading my code.</div>

  <h3>The one hard part: matching ingredients to CosIng</h3>
  <p>Everything else converts cleanly. This does not, and it is worth being
  honest about why.</p>
  {tbl(['problem', 'example', 'what to do'],
       [['the same ingredient, written differently',
         '"Aqua", "Water", "Water (Aqua)", "AQUA/WATER/EAU"',
         'CosIng lists synonyms. Match on the normalised name first, then the '
         'synonym list'],
        ['spelling that came off a web page',
         '"Sodium Hyaluronate" against "Sodium Hyaluronat"',
         'close matching, with a threshold, and everything below the threshold '
         'reported rather than guessed'],
        ['not an ingredient at all',
         'a shop writing "and 25 other ingredients" in the list',
         'the ingredient validator already refuses these. They never reach '
         'the ontology'],
        ['a genuinely new ingredient',
         'a Lebanese maker using a local plant with no INCI name',
         'keep it as an Ingredient with no CosIng link, and say so. Pretending '
         'it matched something would be worse']])}

  <h3>The order I would do it in</h3>
  {tbl(['step', 'what', 'how long'],
       [['1', 'build the twelve classes and their properties in '
         'Prot&eacute;g&eacute;, no data yet', 'a day'],
        ['2', 'load the controlled lists as individuals: 5 skin types, 14 '
         'benefits, ' + str(types) + ' categories', 'an hour, they are already '
         'controlled'],
        ['3', 'load CosIng as the ingredient backbone', 'a day, it is a large '
         'file'],
        ['4', 'match my ingredient strings to it and report what failed',
         'a day, and the report matters more than the match rate'],
        ['5', 'convert ' + f(N) + ' products and their links',
         'a script run, minutes'],
        ['6', 'run the reasoner and the checks on page 5e',
         'and expect it to find things']])}
</section>
"""

# ============================================================ ont-validate
ONT5 = f"""
<section class="section" id="ont-validate">
  <h2>5e &middot; Checking the ontology</h2>
  <p class="lead">The dataset passes 48 checks. The ontology will need its own,
  and they are a different kind: a dataset is checked for wrong values, an
  ontology is checked for a wrong model. Four methods, and they catch four
  different things.</p>

  <h3>1. Competency questions</h3>
  <p>Slide 14 of the lecture: write the questions the ontology must be able to
  answer <i>before</i> building it, then test it by asking them. Gr&uuml;ninger
  and Fox (1995) introduced this, and the point is that a question you cannot
  answer tells you exactly which class or property is missing.</p>

  {tbl(['question it must answer', 'what it forces into the model', 'can the dataset support it today?'],
       [['Which products suit dry, sensitive skin?',
         'SkinType, Sensitivity, suitableFor',
         f'yes, {anyof("skin_type")} products carry both'],
        ['Which products contain no fragrance allergens?',
         'Ingredient, IngredientFunction, the CosIng link',
         'only after CosIng is loaded. This is the question that justifies '
         'reuse'],
        ['Why does this product suit dry skin?',
         'Evidence, statedBy, quotedSentence',
         f'yes, {anyof("skin_type_quote")} products store the actual sentence'],
        ['What does this cost in Lebanon, and elsewhere?',
         'Offer, seller, seenOn',
         'yes, 6 products carry both prices today, and more after the next run'],
        ['Which Lebanese products have no reviews anywhere?',
         'Review, Brand, country',
         'yes, and the answer is all 1,195 of them'],
        ['Find a cheaper product like this one.',
         'contains, hasCategory, hasOffer together',
         'yes, this is the recommender question']])}

  <h3>2. The reasoner</h3>
  <p>HermiT or Pellet, run inside Prot&eacute;g&eacute;. It checks that the model
  does not contradict itself, and it finds contradictions a person reading the
  file would not.</p>
  {tbl(['what it catches', 'an example from this domain'],
       [['a class that can have no members',
         'if Sunscreen must have an SPF and SPF must be under 110, and I also '
         'wrote a rule saying sunscreens have SPF over 200, the class is empty '
         'and the reasoner says so'],
        ['a cycle in the hierarchy',
         'slide 26. If Moisturiser is a kind of Cream and Cream is a kind of '
         'Moisturiser, nothing works'],
        ['an individual in two classes that exclude each other',
         'a product classified as both Sunscreen and Cleanser when the model '
         'says a product has exactly one category'],
        ['links that should follow but do not',
         'if Glycerin is a Humectant and Humectants suit dry skin, the '
         'reasoner can add "suits dry skin" to every product containing '
         'glycerin, and I can then check whether the dataset agrees']])}

  <h3>3. OOPS!, the pitfall scanner</h3>
  <p>A web tool that reads an ontology and reports common modelling mistakes.
  Poveda-Villal&oacute;n, G&oacute;mez-P&eacute;rez and Su&aacute;rez-Figueroa
  (2014) built a catalogue of 41 pitfalls from an empirical study of 693
  ontologies, rated critical, important or minor, and the tool checks 33 of
  them automatically.</p>
  {tbl(['pitfall it looks for', 'why it would apply to mine'],
       [['P04, creating unconnected elements',
         'a class nobody links to. Easy to leave behind when the model grows'],
        ['P08, missing annotations',
         'a class called Evidence with no description is useless to anybody '
         'but me'],
        ['P11, missing domain or range',
         'a property that could point at anything is not a constraint'],
        ['P19, defining multiple domains',
         'saying <code>contains</code> applies to both Product and Brand '
         'quietly breaks reasoning'],
        ['P41, no licence declared',
         'a small thing, but it is the difference between reusable and not']])}
  <p class="mini">The tool is at
  <a href="https://oops.linkeddata.es/">oops.linkeddata.es</a> and the paper is
  in the <i>International Journal on Semantic Web and Information Systems</i>
  10(2), 7&ndash;34.</p>

  <h3>4. SHACL, for the data rather than the model</h3>
  <p>The reasoner and OOPS! check the model. SHACL checks that the individuals
  obey it: every Product must have exactly one category, every Offer must have
  a price and a date, every suitableFor must have Evidence behind it. These are
  the same rules as my 48 dataset checks, written in a standard language
  instead of in Python.
  <a href="https://www.w3.org/TR/shacl/">w3.org/TR/shacl</a></p>

  <div class="note">This is the neat part. My validation script and a SHACL
  shape would be saying the same thing in two languages. If they ever disagree,
  one of them has a bug, and that is a useful thing to be able to test.</div>
</section>
"""

# ============================================================ ont-useback
ONT6 = f"""
<section class="section" id="ont-useback">
  <h2>5f &middot; Using the ontology to check the dataset</h2>
  <p class="lead">This is the part I find most interesting, and it runs the
  usual direction backwards. The dataset is built first and the ontology
  second, so the ontology becomes a way of testing the dataset that could not
  have existed while the dataset was being made.</p>

  <h3>Why a reasoner finds things a checking script cannot</h3>
  <p>My 48 checks each look at one thing at a time: is this value in the list,
  is that number in range, does this column agree with that one. A reasoner
  looks at everything at once and follows chains, so it finds faults that only
  appear when three facts are put together.</p>

  {tbl(['a fault only reasoning finds', 'the chain', 'what I would do'],
       [['a product for sensitive skin that contains a known allergen',
         'Product suitableForSensitivity Sensitive, contains Linalool, '
         'Linalool hasFunction FragranceAllergen',
         'check the source page. Either the page is wrong or my reading of it '
         'is, and both are worth knowing'],
        ['a product claiming hydration with no humectant in it',
         'Product claims Hydrating, but no Ingredient with hasFunction '
         'Humectant',
         'either the formula is truncated or the claim is marketing. My '
         'ingredient completeness flag says which'],
        ['a sunscreen with no UV filter',
         'Product hasCategory Sunscreen, contains no Ingredient with '
         'hasFunction UVFilter',
         'almost certainly a truncated ingredient list, and a good way to find '
         'them'],
        ['two products that are the same product',
         'same Brand, same ingredient set, same category, different '
         'product_id',
         'a duplicate my matching missed. Chemical identity is a stronger '
         'test than name similarity']])}

  <div class="dg">
  <svg viewBox="0 0 720 210" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <text x="0" y="14" fill="#584a7a" font-weight="700">The same product, checked two ways</text>

    <rect x="10" y="30" width="330" height="120" rx="8" fill="#f7f5fb" stroke="#7a68a6"/>
    <text x="175" y="50" text-anchor="middle" fill="#584a7a" font-weight="700">what my 48 checks see</text>
    <text x="24" y="72" fill="#6b6478">sensitivity = "Sensitive"</text>
    <text x="24" y="90" fill="#6b6478">ingredients = "Aqua, Glycerin, Linalool..."</text>
    <text x="24" y="108" fill="#6b6478">ingredient_count = 24, matches the list</text>
    <text x="24" y="132" fill="#3f6b48" font-weight="700">every check passes</text>

    <rect x="370" y="30" width="340" height="120" rx="8" fill="#fdeeee" stroke="#b5484d"/>
    <text x="540" y="50" text-anchor="middle" fill="#b5484d" font-weight="700">what a reasoner sees</text>
    <text x="384" y="72" fill="#6b6478">suitableForSensitivity &#8594; Sensitive</text>
    <text x="384" y="90" fill="#6b6478">contains &#8594; Linalool</text>
    <text x="384" y="108" fill="#6b6478">Linalool hasFunction &#8594; FragranceAllergen</text>
    <text x="384" y="132" fill="#b5484d" font-weight="700">flagged: for sensitive skin, contains an allergen</text>

    <text x="0" y="176" fill="#6b6478">Neither is wrong. The checks ask whether each value is sound. The reasoner asks</text>
    <text x="0" y="194" fill="#6b6478">whether the values make sense together, which needs the meaning written down.</text>
  </svg>
  <div class="cap">Checking values, against checking what they mean</div>
  </div>

  <h3>A finding this would let me make</h3>
  <p>Vendruscolo and colleagues (2025) tested 187 products marketed as
  hypoallergenic and found 89% contained at least one known allergen. With the
  ontology loaded I could ask the same question of {f(N)} products instead of
  187, and the answer would be a contribution rather than a data check.</p>

  {tbl(['question', 'what it needs', 'why it is worth asking'],
       [['How many products marketed for sensitive skin contain a fragrance '
         'allergen?',
         'the CosIng function link',
         'directly comparable to a published result, on a much larger sample'],
        ['Do Lebanese products differ from international ones in what they '
         'put in?',
         'Brand country, plus ingredient functions',
         'nobody has asked this, because the dataset did not exist'],
        ['Are "all skin types" claims supported by the formula?',
         'suitableFor, contains, function',
         f'{sum(1 for r in D if g(r, "skin_type") == "All"):,} products claim '
         'all skin types. Vendruscolo argues this is a tolerance claim rather '
         'than a classification']])}

  <h3>What I would do first</h3>
  {tbl(['', 'step'],
       [['1', 'build the model in Prot&eacute;g&eacute; with no data, and run '
         'OOPS! on it. Fix the model before any data goes near it'],
        ['2', 'load CosIng and the controlled lists, then a hundred products '
         'by hand rather than all ' + f(N) + '. A small graph shows model '
         'problems faster than a large one'],
        ['3', 'write the six competency questions as SPARQL and check they '
         'return sensible answers'],
        ['4', 'only then convert the whole dataset'],
        ['5', 'run the reasoner and treat what it flags as a list of things '
         'to check in the data, not as errors to suppress']])}

  <div class="ok">If step 5 finds nothing, either the dataset is in better
  shape than I expect or the model is too loose to catch anything. Neither
  would surprise me, and both are worth knowing before the recommender is
  built on top.</div>
</section>
"""

# ============================================================ write
html = PORTAL.read_text(encoding='utf-8')
before = len(html)
for sid in ('ont-what', 'ont-reuse', 'ont-model', 'ont-populate',
            'ont-validate', 'ont-useback'):
    html = re.sub(r'<section class="section[^"]*" id="' + sid + r'">.*?</section>',
                  '', html, flags=re.S)
anchor = html.find('</main>')
html = html[:anchor] + ONT1 + ONT2 + ONT3 + ONT4 + ONT5 + ONT6 + '\n' + html[anchor:]
PORTAL.write_text(html, encoding='utf-8')

w = {}
for m in re.finditer(r'<section class="section[^"]*" id="(ont-[^"]+)">(.*?)</section>',
                     html, re.S):
    w[m.group(1)] = len(re.sub(r'<[^>]+>', ' ', m.group(2)).split())
print('=' * 64)
print('  ONTOLOGY PAGES')
print('=' * 64)
for k, v in w.items():
    print(f'    {k:14s}{v:6,} words')
allx = (ONT1, ONT2, ONT3, ONT4, ONT5, ONT6)
print(f'\n  {sum(w.values()):,} words, '
      f'{sum(x.count("<table") for x in allx)} tables, '
      f'{sum(x.count("<svg") for x in allx)} diagrams, '
      f'{sum(x.count("<a href") for x in allx)} links')
print(f'  portal {before:,} -> {len(html):,}')
print(f'\n  worked example used: {g(EX, "product_id")}  {g(EX, "brand")} '
      f'{g(EX, "name")[:40]}')
