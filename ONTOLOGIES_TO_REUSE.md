# Ontologies worth reusing

Searched August 2026. Everything below is real, reachable, and checked against
the 33 columns now in `SKINCARE_FINAL.csv`.

The rule that matters: **do not invent a property that already exists.** Do not
write `hasProductName` when `schema:name` is there. Reviewers notice invented
vocabulary, and reused vocabulary is what makes the dataset joinable to other
people's work later.

---

## 1. The closest published work to your thesis

**Personalized Skincare Recommendation System Based on Ontology and User
Preferences** (2025)

This one matters more than any other item on this page, because **it scraped
Skinsort, the same source you did.**

- twelve core classes: Product, Ingredient, Skin Type, Skin Concern, and others
- more than twenty-five object properties
- built with the Methontology method
- populated by scraping Sociolla, Beautyhaul and **Skinsort**
- 3,800 products and 28,000 ingredients
- user states skin type, concerns and sensitivities; these become RDF triples
  and SPARQL rules return the recommendation
- evaluated with ten respondents, 4.5 of 5 overall, 4.8 for relevance

Your class structure is already close to theirs, which is good evidence your
model is reasonable rather than idiosyncratic.

**Where you are stronger, and it is worth saying out loud in the meeting:**

| | that paper | yours |
|---|---|---|
| products | 3,800 | 13,184 |
| market | Indonesian | Lebanese |
| local availability | not modelled | `shops_in_lebanon`, 0 to 6 |
| local price | not modelled | `price_lbp` at the BDL rate |
| value for money | not modelled | `price_per_ml` |
| provenance of each claim | not described | tier 1 to 4, every claim sourced |
| validation | 10 respondents | 87 automated checks |

Their evaluation is with users, which yours does not yet have. That is the
honest gap to acknowledge, and it is also your obvious next step.

---

## 2. OntoCosmetic — the cosmetic domain ontology

<https://github.com/ERPI-UL/OntoCosmetic>

Open source OWL, from ERPI at Université de Lorraine. Built for the design of
emulsion-based cosmetic products, structured on OntoCAPE, a large chemical
process engineering ontology.

Four main concepts: **ingredients, formulations, properties, design
heuristics.**

Honest assessment: it is built for people FORMULATING a cosmetic, not for
people RECOMMENDING one. Its heuristics are about substituting an emulsifier,
not about matching a customer to a moisturiser.

**What is still worth taking:** its ingredient and formulation classes, and the
fact that it encodes expert rules as SWRL rules in Protégé. Your six concern
rules are exactly that kind of heuristic, currently written in Python. Turning
them into SWRL is a clean way to move logic you already have into the ontology
layer, which is precisely what the ontology phase of your thesis is for.

Paper: *An ontology for the design of emulsion-based cosmetic products*,
Computers & Chemical Engineering, 2023.

---

## 3. CosIng-KG — the EU ingredient database as RDF

<https://github.com/biobricks-ai/cosing-kg>

The European Commission's Cosmetic Ingredient Database turned into RDF.
**24,094 ingredients**, each with its INCI name, CAS and EC numbers, declared
function (preservative, UV filter, surfactant, skin conditioning) and any
regulatory restriction, under Regulation 1223/2009.

This is the single most useful external resource for your dataset, because your
`ingredients` column holds INCI names and this gives every one of them a stable
identifier and an official function.

Concretely, it lets you say **why** a rule fires. At the moment your dataset
says a product may worsen dryness. With CosIng joined in, it can say the
product contains Alcohol Denat, whose CosIng function is *solvent*, and cite
the EU entry. That is the difference between an assertion and a justified
assertion, and it is the kind of thing an examiner asks about.

You already have `COSING_Ingredients-Fragrance_Inventory_v2.csv` in your
uploads folder, so the source data is on your machine already.

---

## 4. TOXIN knowledge graph — safety evidence

<https://academic.oup.com/database/article/doi/10.1093/database/baae121/7989333>
Published January 2025, *Database: The Journal of Biological Databases and
Curation*.

Built for animal-free risk assessment of cosmetics under the EU testing ban.
Uses the ToXic Process Ontology and draws on Scientific Committee on Consumer
Safety opinions from 2009 to 2019.

Only **88 ingredients**, so it will not cover your dataset. Cite it as evidence
that knowledge graphs are the accepted representation for cosmetic safety
information, and as the natural place your `concerns` column would connect to
if the work were extended toward safety rather than recommendation.

---

## 5. schema.org and GoodRelations — the commercial half

<https://schema.org/Product> · <https://schema.org/Offer> ·
<http://www.heppnetz.de/ontologies/goodrelations/v1>

GoodRelations is the OWL vocabulary for products, prices, shops and offers. It
was folded into schema.org in November 2012 and is now the official e-commerce
core of schema.org.

This matters because your dataset is no longer only research data. Once it has
price in lira, size, and a shop count, it is commercial data, and there is a
standard vocabulary for exactly that. A Lebanese retailer adopting your system
will already have staff who understand schema.org, because it is what Google
reads off their product pages.

**The distinction to get right, and it is the one people most often get wrong:**
a Product is the thing itself, an Offer is one shop selling it at one price on
one date. Your 5,658 products sold by one shop and 345 sold by two are not
duplicate products. They are one Product with several Offers.

---

## 6. Supporting vocabularies

| ontology | what for | link |
|---|---|---|
| SKOS | your closed lists: 22 product types, 14 benefits, 6 concerns, 7 free-from | <https://www.w3.org/TR/skos-reference/> |
| PROV-O | provenance: your tier 1 to 4 skin type sourcing, and every `*_source` column | <https://www.w3.org/TR/prov-o/> |
| ChEBI | chemical identity for INCI ingredients | <https://www.ebi.ac.uk/chebi/> |
| Product Types Ontology | product categories built from Wikipedia, works with GoodRelations | <http://www.productontology.org/> |

PROV-O deserves particular attention. Your strongest and most unusual feature
is that **every claim records where it came from and how strong that source
was.** PROV-O is the W3C standard for saying that, with `prov:wasDerivedFrom`,
`prov:wasAttributedTo` and `prov:generatedAtTime`. Using it turns your tier
system from a private convention into a standards-based one.

---

## Your columns mapped to existing terms

Reuse the left column. Only invent the ones marked **new**, and each of those
is genuinely local to this thesis.

| your column | reuse this |
|---|---|
| product_id | `schema:productID` |
| name | `schema:name` |
| brand | `schema:brand` → `schema:Brand` |
| product_type | `schema:category`, values as `skos:Concept` |
| country | `schema:countryOfOrigin` |
| product_url | `schema:url` |
| image_url | `schema:image` |
| ingredients | `gr:description` or a list of ChEBI / CosIng entities |
| ingredient_count | **new** `:ingredientCount` |
| key_ingredients | `skos:related` to Ingredient entities |
| free_from | **new** `:freeFrom`, values as `skos:Concept` |
| spf | **new** `:spf` |
| benefits | **new** `:hasBenefit`, values as `skos:Concept` |
| concerns | **new** `:mayWorsen`, values as `skos:Concept` |
| skin_type | **new** `:suitableForSkinType` |
| sensitivity | **new** `:suitableForSensitiveSkin` |
| price_usd, price_lbp | `schema:price` + `schema:priceCurrency` on an `schema:Offer` |
| price_lbp_rate | `prov:value` on the conversion activity |
| size_value, size_unit | `gr:hasEligibleQuantity` / `schema:QuantitativeValue` |
| price_per_ml | `gr:hasUnitPriceSpecification` |
| price_tier | **new** `:priceTier`, values as `skos:Concept` |
| rating, rating_count | `schema:aggregateRating` → `schema:AggregateRating` |
| review_texts_json | `schema:review` → `schema:Review` |
| shops_in_lebanon | count of `schema:Offer` from Lebanese `schema:Organization` |
| source_category | **new** `:sourceCategory` |
| *_source columns | `prov:wasDerivedFrom`, `prov:wasAttributedTo` |
| skin type tier 1 to 4 | **new** `:sourceTier`, described with PROV-O |

Roughly two thirds reuse existing vocabulary. The ones left over are the
skin-matching properties, which is the right answer: those are what this thesis
contributes, and the rest is what it borrows.

---

## Validating whatever you build

| step | tool |
|---|---|
| does it answer the questions it was built for | competency questions, Grüninger & Fox 1995 |
| is it logically consistent | HermiT or Pellet reasoner in Protégé |
| does it contain known modelling errors | OOPS!, <https://oops.linkeddata.es/> |
| do the instances obey the shapes | SHACL, <https://www.w3.org/TR/shacl/> |

OOPS! is worth running and screenshotting. It checks 40-odd known pitfalls,
including three your Lecture 6 slides 26 to 28 warn about: cycles in the
hierarchy, unbalanced class families, and plural class names.

---

## What I would actually do, in order

1. **Reuse schema.org and GoodRelations for the commercial half.** Cheapest
   work on this page and it is what makes the dataset credible to a retailer.
2. **Join CosIng-KG to your ingredients.** Turns your six concern rules from
   assertions into justified assertions with an EU citation behind each one.
3. **Use PROV-O for the tier system.** Your best feature, currently expressed
   in a private convention.
4. **Move the six concern rules into SWRL**, the way OntoCosmetic does. Logic
   you have already written and tested, relocated to the ontology layer.
5. **Cite the 2025 Skinsort paper as your closest comparator** and show the
   table above. Being three times larger, locally grounded and provenance-
   tracked is a strong position, and naming the comparator yourself is better
   than being handed it in the viva.
