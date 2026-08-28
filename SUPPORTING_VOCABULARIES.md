# Supporting vocabularies, and why I am using them

I kept reading advice to reuse SKOS, PROV-O, ChEBI and the Product Types
Ontology, and for a long time I did not understand what any of them would
actually do for me. My columns are already clean. My tier system already
works. Nothing was broken. So what was I supposed to be gaining?

This page is the answer I eventually arrived at, written the way I wish it had
been explained to me. The short version is that these vocabularies do not do
any work. They give the thing I already built a name that other people already
recognise. Whether that is worth anything depends entirely on what I want the
ontology to be, and I go through that honestly below.

---

## The question I had to answer first

For every one of these I asked the same thing: **what can I not do by hand?**

I can type out 22 product types in an afternoon. I can write my own property
called `hasSkinTypeTier` in about four seconds. Nothing is stopping me. So the
argument for reuse has to be better than "it is good practice", or it is not
an argument at all.

There turned out to be three situations where reuse genuinely earns its place,
and only three:

1. **Somebody else's data has to meet mine.** If I invent my own term for
   price, nobody else's tools know what it means. If I use the standard one,
   they do, at no extra cost to me.
2. **A query needs to walk a hierarchy.** If I want "show me all moisturisers"
   to include night moisturisers without listing them by hand, something has
   to know Night Moisturizer is a kind of Moisturizer. That is a statement I
   have to store somewhere, and there is already a standard way to store it.
3. **Somebody asks whether I made it up.** "I used the W3C provenance
   standard" and "I invented a tier column" are different sentences in a viva,
   even when the underlying data is identical.

If none of those three apply, the vocabulary is overhead. I say so below where
I think that is the case.

---

## SKOS, for my closed lists

<https://www.w3.org/TR/skos-reference/>
Turtle file: <https://www.w3.org/2009/08/skos-reference/skos.rdf>

**What it is.** A tiny W3C standard for controlled lists of terms. It has
maybe six things in it that anybody uses.

**What I have that fits.** Five closed lists, and they are already tidy:

| list | values |
|---|---|
| product types | 22, from General Moisturizer at 2,192 products down to Emulsion at 25 |
| benefits | 14, led by Hydrating at 9,504 |
| concerns | 7, led by May Worsen Eczema at 6,396 |
| free-from claims | 7, led by Parabens at 9,718 |
| skin types | 5, plus sensitivity as Sensitive or Resistant |

**Why not just do it manually.** I genuinely could, and mostly I already have.
The cleaning was the hard part and it is finished. What SKOS adds is small and
specific.

Right now `General Moisturizer` is a piece of text. Two things follow from
that. It cannot be labelled in Arabic without becoming a different string, and
nothing anywhere records that `Night Moisturizer` and `Day Moisturizer` are
kinds of moisturiser. I have those three as separate values with no
relationship between them.

With SKOS each value becomes a concept with an identifier, and then:

```turtle
:NightMoisturizer  a skos:Concept ;
    skos:prefLabel   "Night Moisturizer"@en ;
    skos:altLabel    "مرطب ليلي"@ar ;
    skos:broader     :Moisturizer .
```

That `skos:broader` line is the one that pays. Once it exists, a query for
moisturisers returns all three types without me hard-coding the list, and if I
add a sixth moisturiser type later, every query that already existed picks it
up. That is the difference between a list and a hierarchy, and it is the only
reason I am bothering.

The `altLabel` line matters more here than it would elsewhere. This is a
Lebanese dataset and Arabic labels are a real requirement, not a hypothetical
one. SKOS gives me a place to put them that does not mean duplicating every
row.

**My verdict: worth it, and cheap.** Maybe 55 concepts total. An afternoon.

---

## PROV-O, for the tier system

<https://www.w3.org/TR/prov-o/>
Turtle file: <https://www.w3.org/ns/prov.ttl>

This is the one I care about most, because it is attached to the part of the
dataset I am proudest of.

**What I have.** Every claim in this dataset records where it came from and
how much that source is worth. Skin type is graded tier 1 to 4. There are four
separate `*_source` columns, and 13,184 of them are filled for skin type
alone, across 1,277 distinct sources.

**The problem.** `skin_type_tier = 1` means something specific to me and
nothing at all to anybody else. It is a private convention. If a second
researcher merges this dataset with theirs, my tier column is a number in a
spreadsheet that they have to read my documentation to decode.

**What PROV-O changes.** Three properties do nearly all of the work:

| property | what it says |
|---|---|
| `prov:wasDerivedFrom` | this claim came from that page |
| `prov:wasAttributedTo` | this agent stated it, a manufacturer or a shop |
| `prov:generatedAtTime` | this was true on this date |

Here is a real row from my data. `LBR-00033`, Cetaphil Gentle Exfoliating
Salicylic Acid Moisturizing Lotion. Skin type Dry, sensitivity Sensitive, tier
1, authority `manufacturer`, read from `www.cetaphil.com`, and the exact page
URL is stored alongside it.

```turtle
:LBR-00033-skintype
    a                      prov:Entity ;
    :skinType              :Dry ;
    prov:wasAttributedTo   :Cetaphil ;
    prov:wasDerivedFrom    <https://www.cetaphil.com/us/products/.../302993917564.html> .

:Cetaphil  a prov:Agent, schema:Brand .
```

Nothing new is being recorded. Every one of those facts is already in my
files. What changed is that the sentence "the manufacturer said so" is now
written in a form any provenance-aware tool understands without being taught
my conventions.

**Why not do it manually.** I could keep the tier number and write a paragraph
explaining it, and honestly for my own thesis that would work. The reason I am
not is that provenance is the one thing that makes this dataset unusual. Most
product datasets state a skin type and expect you to believe it. Mine records
who said it. If I am going to make that the centrepiece, it should be
expressed in the standard built for exactly that purpose rather than in a
scheme only I understand.

There is also a practical payoff. Once provenance is expressed properly, "give
me only claims a manufacturer made" becomes a query rather than a filter I
have to remember to apply.

**My verdict: the most valuable item on this page.** Three properties, three
classes. Small vocabulary, disproportionate return.

---

## The other half of the same product, and why offers are separate

Same Cetaphil product, `LBR-00033`. It is sold by two Beirut shops, sohaticare
and zeinacare. One asks **$8.66**. The other asks **$32.36**.

That is one product and two prices, and it is the clearest case I have for why
the modelling matters. If price is a property of the product, I have to pick
one of those numbers and throw the other away, or store a range and lose track
of who charges what. Neither is acceptable when the whole point of this
dataset is what things cost in Lebanon.

The standard answer, from schema.org, is that a Product and an Offer are
different things. One Product, two Offers, each with its own price, its own
seller, and its own date. My 375 multi-shop products are not duplicates. They
are one product with two offers each.

Worth saying plainly: this product is an outlier. Across those 375 products
the median gap between cheapest and dearest is 0.0%, so Beirut shops mostly
price identically. But the model has to handle the outlier, and a
product-with-one-price model cannot.

I am counting schema.org as a supporting vocabulary here even though it is not
on the list I was given, because more than half my columns are commercial and
it is the standard for exactly that. It is also already in use: the images and
ratings in this dataset were read out of schema.org markup on shop pages.

---

## ChEBI, and why I am leaving it

<https://www.ebi.ac.uk/chebi/>
Small file: <https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl>

**What it is.** A chemical ontology. Molecular structures, InChI keys, a
chemical class hierarchy.

**Why I am not using it.** CosIng already gave me what I need from an
ingredient: the INCI name, the CAS number, the function the European
Commission recognises, and the regulatory restriction. ChEBI adds structures
and chemical classification on top. A recommender does not use structures.

The size argument is real too. Full ChEBI is over 195,000 entries. My dataset
has about 16,300 distinct ingredient strings, and many of those are botanical
extracts that ChEBI cannot represent as a single molecule anyway. Importing
195,000 entries to use a fraction of them makes the graph slow for no gain.

**When I would change my mind:** if I add ingredient similarity, meaning
"find me a cheaper product with a chemically similar formula". Then structures
are the whole point and ChEBI becomes necessary. I am not doing that.

**Verdict: skip, and say why.** Leaving it out deliberately with a reason is a
stronger position than importing it to look thorough.

---

## Product Types Ontology, and why I am leaving that too

<http://www.productontology.org/>

**What it is.** Product categories generated automatically from Wikipedia
articles, designed to plug into GoodRelations and schema.org.

**Why not.** I have 22 product types. They are curated, they are consistent,
and they cover the whole dataset. This ontology solves the problem of needing a
category for any product that might exist anywhere, which is not a problem I
have.

Its categories also come from Wikipedia rather than from cosmetics practice,
so the fit for skincare specifically is uneven, and the generated identifiers
carry Wikipedia's structure with them.

**Verdict: skip.** SKOS over my own 22 types gives me the hierarchy and the
Arabic labels, which is the entire benefit I would have wanted from it.

---

## Where this leaves me

| vocabulary | using it | reason |
|---|---|---|
| CosIng | done already | 98.4% of formulas matched |
| schema.org | yes | products, offers, prices, ratings |
| PROV-O | yes | the tier system, expressed as a standard |
| SKOS | yes | five closed lists, plus Arabic labels and hierarchy |
| ChEBI | no | CosIng covers what a recommender needs |
| Product Types Ontology | no | my own 22 types are better for this domain |

Two in, two out, and the two I am skipping I can defend.

The thing I had to stop expecting was that these vocabularies would do
something for me. They do not. SKOS will not tidy my product types; they were
already tidy. PROV-O will not find sources; I already found them. What they do
is take work I have already done and state it in terms that are not private to
me. That is worth something when the work is meant to be reused, and worth
very little when it is not, which is why I am taking two of the four rather
than all of them.
