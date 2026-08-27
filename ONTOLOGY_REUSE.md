# Which ontologies to actually reuse

Short version: four, and one of them is already done.

I read the comparative assessment carefully. It is a good survey, but it is
scoped for a **formulation-design or toxicology** thesis. This one is a
**recommender**: it matches a person with a skin type and a budget to a
product they can buy in Beirut. That difference removes most of the list.

The test I applied to every candidate was the one that matters: *if I can do
this by hand in an afternoon, it is not worth importing an ontology for.* Six
of the eight candidates in the report fail that test for this thesis.

The opposite rule also holds, and it is the one with citations behind it:
where a standard term already exists, use it rather than minting your own.
That is W3C Data on the Web Best Practices, Best Practice 15, and FAIR
principle I2, and inventing a duplicate term is catalogued as pitfall P34 by
the OOPS! ontology checker. `WHY_REUSE_VOCABULARY.md` gives the full
references.

---

## Use these four

### 1. CosIng, the EU ingredient register, already done

| | |
|---|---|
| what it is | the European Commission's official list of what may go into a cosmetic |
| download | https://ec.europa.eu/growth/tools-databases/cosing/ |
| status in this project | **done.** 10,876 of 11,050 formulas matched, 98.4% |

This is the one that changed what the dataset can claim. Before it, "may
worsen dryness" was a rule I wrote. Now it names ALCOHOL DENAT., gives the
function the Commission recognises for it (**astringent**, solvent), and
points at register entry 74174.

It also gives ingredients their CAS numbers, which is what makes any later
chemical linking possible.

**What it added to the dataset:** `ingredient_functions`, `cosing_matched`,
`cosing_coverage`, `restricted_ingredients`.

---

### 2. schema.org, the commercial half of the data

| | |
|---|---|
| what it is | the vocabulary Google reads off every shop page on the web |
| download | https://schema.org/version/latest/schemaorg-current-https.ttl |
| documentation | https://schema.org/Product and https://schema.org/Offer |
| licence | Creative Commons Attribution-ShareAlike |

The assessment does not mention schema.org at all, and I think that is its
biggest gap for this thesis. More than half the dataset is commercial: price,
price in lira, image, rating, shop, availability. schema.org is the standard
for exactly that, it is maintained, and Lebanese shops already publish it in
their own pages, which is where the images and ratings in this dataset came
from.

**The classes worth knowing:**

| class | what it means here |
|---|---|
| `schema:Product` | the product itself, one per row |
| `schema:Brand` | who makes it |
| `schema:Offer` | **one shop selling it at one price on one date** |
| `schema:AggregateRating` | the star rating and how many reviews |
| `schema:Review` | one review |
| `schema:Organization` | the shop |

**The properties worth knowing:** `schema:name`, `schema:brand`,
`schema:image`, `schema:category`, `schema:url`, `schema:price`,
`schema:priceCurrency`, `schema:seller`, `schema:availability`,
`schema:aggregateRating`.

**The one distinction to get right.** A Product is the thing. An Offer is one
shop selling it. The 375 products sold by two Beirut shops are not duplicates;
they are one Product with two Offers, each with its own price and date. Get
this wrong and the price comparison becomes meaningless.

GoodRelations, which the report does not mention either, was folded into
schema.org in 2012 and is now its e-commerce core, so using schema.org gets it
for free.

---

### 3. PROV-O, the tier system

| | |
|---|---|
| what it is | the W3C standard for recording where a fact came from |
| download | https://www.w3.org/ns/prov.ttl |
| documentation | https://www.w3.org/TR/prov-o/ |
| licence | W3C, free |

This is the second gap in the assessment, and for this thesis it may be the
most important item on the page. The strongest feature of this dataset is that
**every claim records its source and how strong that source is**: tier 1
manufacturer, tier 2 retailer, tier 3 weaker, tier 4 inferred. Right now that
is a private convention. PROV-O is the standard way of saying it.

**Three properties do almost all the work:**

| property | what it says |
|---|---|
| `prov:wasDerivedFrom` | this skin type came from that page |
| `prov:wasAttributedTo` | the manufacturer stated it, not a shop |
| `prov:generatedAtTime` | the price was true on this date |

`prov:Entity`, `prov:Agent` and `prov:Activity` are the three classes. That is
genuinely all you need. It is a small vocabulary and it turns the tier column
from something a reader has to take on trust into something a reasoner can
filter on.

---

### 4. SKOS, the closed lists

| | |
|---|---|
| what it is | the W3C standard for controlled vocabularies |
| download | https://www.w3.org/2009/08/skos-reference/skos.rdf |
| documentation | https://www.w3.org/TR/skos-reference/ |
| licence | W3C, free |

The dataset has several closed lists: 22 product types, 14 benefits, 6
concerns, 7 free-from claims, 5 skin types. These are already clean and
consistent, which is the hard part. SKOS just gives each value a proper
identifier instead of a bare string.

**What you use:** `skos:Concept` for each value, `skos:prefLabel` for its name,
`skos:broader` to say Night Moisturizer is a kind of Moisturizer,
`skos:closeMatch` when mapping one of your terms to somebody else's.

`skos:closeMatch` matters more than it looks. When an ingredient is a botanical
extract rather than a single chemical, saying it is *close to* a chemical
entity is honest; saying `owl:sameAs` is not. The assessment makes this point
well and it is right.

---

## Consider one more, only if you go further

### ChEBI, chemical identity

| | |
|---|---|
| download, small version | https://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi_lite.owl |
| documentation | https://www.ebi.ac.uk/chebi/ |
| licence | CC BY 4.0 |

The assessment ranks ChEBI as core. For a chemistry thesis it is. For this one
I would call it **optional**, and here is the honest reason: CosIng already
gives every ingredient a name, an official function, a CAS number and a
regulatory status. ChEBI adds molecular structures, InChI keys and a chemical
class hierarchy. A recommender does not use any of those.

**Take it only if you add ingredient-similarity features** such as finding a
cheaper product with a chemically similar formula. Then structures matter and
ChEBI becomes essential.

If you do take it, take `chebi_lite.owl`, not the full file. The full ChEBI is
over 195,000 entries and this dataset has about 6,400 distinct ingredient
names. Importing the whole thing to use 3% of it would make the graph slow for
no benefit.

---

## Read but do not import: OntoCosmetic

| | |
|---|---|
| download | https://github.com/ERPI-UL/OntoCosmetic/blob/main/OntoCosmetic-30-withoutRules.owl |
| documentation | https://erpi-ul.github.io/OntoCosmetic |
| paper | *An ontology for the design of emulsion-based cosmetic products*, Computers & Chemical Engineering, 2023 |

The assessment scores this five stars on domain fit and it is the closest
cosmetic ontology that exists. But it was built to help somebody **formulate**
a cosmetic, not recommend one. Its heuristics are about substituting an
emulsifier and exploring a formulation space. This thesis never does that.

The repository state also matters: 1 star, 7 commits, no releases, no licence
file. The assessment's own note about "unclear license, weak release
engineering" is accurate, and depending on an unlicensed artifact is a real
risk for a thesis meant to stay reusable.

**What to take from it anyway, and it is worth taking:**

- **The precedent.** Cite it as the existing cosmetic ontology and say why
  yours differs. That is a stronger position than pretending nothing exists.
- **The SWRL pattern.** It encodes expert rules as logic in Protégé. The six
  concern rules in this project are exactly that kind of rule and currently
  live in Python. Moving them into SWRL is the natural ontology-phase step,
  and OntoCosmetic is the precedent for doing it that way.
- **Its sensory concepts** for after-feel, absorption, oiliness and stickiness,
  if consumer attributes ever get modelled here.

---

## Skip these, and why

The assessment lists them fairly. They are simply not this thesis.

| | why not |
|---|---|
| **CHEMINF** | molecular descriptors for QSAR and machine learning on chemical structure. This thesis does no QSAR |
| **OBI** | protocols, instruments, experimental results. There are no experiments here. If a dermatologist evaluation is added later, revisit |
| **eNanoMapper** | toxicology and nanomaterials. Excellent for a safety thesis, a large import surface for this one |
| **OntoCAPE** | manufacturing process engineering. Nothing here is manufactured |
| **SNOMED CT** | 360,000 clinical concepts and a licence to negotiate, to express six concern values. Map those six by hand |
| **UMLS** | a mapping service between clinical vocabularies. Nothing here needs one |
| **GS1 GPC** | retail product classification. There are 22 product types. Mapping them by hand is an afternoon |
| **DermO, SPO** | both stale. The assessment says so and is right. Do not build on an unmaintained dependency |

SNOMED and GS1 are the two where the assessment and I differ most, so it is
worth being explicit. Both are genuinely good vocabularies. Neither earns its
integration cost against a list of six concerns and 22 product types that are
already clean, closed and consistent. **Map them by hand, cite the standard,
move on.**

---

## How the 42 columns map

Reuse the middle column. Only the ones marked **new** need inventing, and each
of those is genuinely specific to this thesis.

| column | use this |
|---|---|
| product_id | `schema:productID` |
| name | `schema:name` |
| brand | `schema:brand` → `schema:Brand` |
| product_type | `schema:category`, values as `skos:Concept` |
| country | `schema:countryOfOrigin` |
| product_url | `schema:url` |
| image_url | `schema:image` |
| product_summary | `schema:description` |
| price_usd, price_lbp | `schema:price` + `schema:priceCurrency` on an `schema:Offer` |
| price_seen_date | `prov:generatedAtTime` |
| sold_by_shops | `schema:seller` → `schema:Organization` |
| shops_in_lebanon | count of Offers from Lebanese sellers |
| size_value, size_unit | `schema:QuantitativeValue` |
| price_per_ml | `schema:UnitPriceSpecification` |
| rating, rating_count | `schema:aggregateRating` → `schema:AggregateRating` |
| review_texts_json | `schema:review` → `schema:Review` |
| ingredients | list of Ingredient entities, each linked to its CosIng entry |
| ingredient_functions | the EU function, as `skos:Concept` |
| restricted_ingredients | **new** `:hasRestrictedIngredient` |
| key_ingredients | `skos:related` |
| free_from | **new** `:freeFrom`, values as `skos:Concept` |
| benefits | **new** `:hasBenefit`, values as `skos:Concept` |
| concerns | **new** `:mayWorsen`, values as `skos:Concept` |
| skin_type | **new** `:suitableForSkinType` |
| sensitivity | **new** `:suitableForSensitiveSkin` |
| spf | **new** `:spf` |
| skin_type_source | `prov:wasDerivedFrom` |
| skin_type_tier *(in COMBINED_EVIDENCE.csv)* | **new** `:sourceTier`, described with PROV-O |
| price_source, rating_source | `prov:wasAttributedTo` |
| source_category | **new** `:sourceCategory` |

About two thirds reuses published vocabulary. What is left is the
skin-matching layer, which is what this thesis contributes. That split is the
right one: borrow the plumbing, invent only the idea.

---

## A worked example

One real product, `LBR-00011`, Eucerin Sensitive Protect Dry Touch Sun
Gel-Cream SPF50+, sold in Lebanon. Its formula matched CosIng at 100%.

```turtle
:LBR-00011  a schema:Product ;
    schema:name       "Sensitive Protect Dry Touch Sun Gel-Cream SPF50+" ;
    schema:brand      :Eucerin ;
    schema:category   :Sunscreen ;              # a skos:Concept
    :suitableForSkinType :Oily ;
    :sourceTier       1 ;                       # the manufacturer said so
    :mayWorsen        :Dryness ;
    :contains         :AlcoholDenat .

# why the dryness flag is there, and who says so
:AlcoholDenat  a :Ingredient ;
    skos:prefLabel    "ALCOHOL DENAT." ;
    :cosingRef        "74174" ;
    :hasEUFunction    :Astringent, :Solvent .   # the Commission's own words

# one shop selling it, on a known date
:offer_LBR00011_feel22  a schema:Offer ;
    schema:itemOffered  :LBR-00011 ;
    schema:price        "24.00" ;
    schema:priceCurrency "USD" ;
    schema:seller       :Feel22 ;
    prov:generatedAtTime "2026-08-27"^^xsd:date .
```

Every line above is either a standard term or one of the few new ones. Nothing
was invented that already existed.

---

## Where I would start

1. **schema.org for the commercial half.** Cheapest work here, and it is what
   makes the dataset credible to a Lebanese retailer.
2. **PROV-O for the tiers.** Your best feature, currently a private
   convention.
3. **SKOS for the closed lists.** Half a day.
4. **Move the six concern rules into SWRL**, the way OntoCosmetic does. The
   logic is already written and tested in Python.

CosIng is done. ChEBI waits until there is a reason for it.
