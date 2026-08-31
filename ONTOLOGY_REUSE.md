# Ontologies to reuse, and the papers behind the decision

This is the plan for the ontology phase of the thesis. It has three parts: the
papers I read and what I am taking from each, the four vocabularies I am
reusing rather than inventing, and the classes I am proposing for my own
ontology, derived from the 12,629 products I actually have rather than from a
diagram.

I have cut this down. An earlier version listed nine vocabularies with reasons
to consider each one. That was me being thorough in the wrong direction — a
long list of possibilities is not a plan. What follows is only what earns its
place.

---

## Part 1 — The papers, and what I am taking from them

### Hansanie and Kumara (2024), *Ontology based Machine Learning Approach for Facial Skincare Products Recommendation*
IEEE ICIPRoB 2024, DOI [10.1109/ICIPRoB62548.2024.10543444](https://doi.org/10.1109/iciprob62548.2024.10543444)

**What they did.** They built a facial skincare recommender that puts a machine
learning model and an ontology side by side rather than choosing between them.
A CNN reads a photograph of the user's face and grades acne severity. That
grade, plus the user's stated skin type, concerns and ingredient allergies,
goes into an ontology built in Protégé, and the ontology does the matching. The
system was tested on 24 participants and reported 87.5% accuracy. Users can
rate what they were shown, and those ratings feed back in.

**Their schema.** Three areas of concepts with hierarchical relations between
them:

| Area | Holds |
|---|---|
| User profile | skin type, concerns, acne severity, allergy ingredients, feedback |
| Skincare information | the domain knowledge — what suits what, what to avoid |
| Skincare product information | products and their ingredients |

The recommendation is a semantic similarity between the user profile area and
the product area, computed across the middle one.

**What I am adopting.** The three-area split, because it separates things that
change at different speeds. Products change when the market changes. A user
profile changes per person. The knowledge in the middle — that salicylic acid
suits oily skin — changes rarely and is the part a dermatologist would review.
Keeping them apart means my supervisor can check the middle layer without
reading 12,629 product rows.

**What I am not adopting.** The CNN. I have no facial images and no ethical
approval to collect any, and my dataset's contribution is on the product side,
not the diagnosis side. If the acne grading were added later it would plug into
the user profile area without touching anything else, which is itself an
argument for their separation.

**Where they are weaker than me, and I should say so carefully.** Their
ingredient knowledge is internal to the ontology. Mine is linked to the EU
CosIng register, so a statement like "this contains a restricted ingredient"
cites Regulation (EC) 1223/2009 rather than an assertion I typed. And their
products have no provenance — a claim in their ontology does not record who
made it. Both differences come from the dataset, not from being cleverer.

---

### *Personalized Skincare Recommendation System Based on Ontology and User Preferences* (2025)
ResearchGate [394583703](https://www.researchgate.net/publication/394583703_Personalized_Skincare_Recommendation_System_Based_on_Ontology_and_User_Preferences)

**What they did.** They built the ontology properly, using Methontology, and
populated it by scraping three platforms — Sociolla, Beautyhaul and Skinsort —
which gave them over 3,800 products and around 28,000 ingredient records.

**Their schema.** Twelve core classes and more than twenty-five object
properties. The classes named in the paper include:

`Product` · `Ingredient` · `SkinType` · `SkinConcern` · `Formulation` ·
`ApplicationFrequency`

The point they make about this list, which I think is right, is that the
classes correspond to the decisions a person or a clinician actually makes.
Nobody chooses a moisturiser by its molecular descriptors; they choose by skin
type, by concern, by texture, and by how often they are willing to apply it.

**What I am adopting.**

`Formulation` — I do not have this and I should. It is the texture and delivery
form: cream, gel, serum, foam, oil, stick, ampoule. My `product_type` column
mixes two different ideas, function and form. "Day Moisturizer" is a function.
"Essence" is closer to a form. Separating them lets a user say *I want a gel,
not a cream* independently of what the product is for, and it is a very common
thing for people to want.

`ApplicationFrequency` — morning, evening, twice daily, weekly. I do not hold
it, but a routine builder needs it, and much of it is recoverable from the
`product_summary` text I already store.

`SkinConcern` as a class in its own right, not a string on the product. I
currently store `concerns` as seven text values. Making it a class means a
concern can carry its own relations — which ingredients help it, which worsen
it — instead of that knowledge living in code.

**One thing I would do differently.** They scraped Skinsort, as I did, but they
merged their three sources into one pool. I kept mine separate and recorded
which source each product came from, which is what lets me say that 519
products appear in both the global catalogue and Lebanese retail. Merging first
loses that permanently.

**And the honest comparison on size:** they have 3,800 products; I have 12,629.
But they have around 28,000 ingredient records to my 13,699 distinct ingredient
names, so their ingredient depth per product is comparable. Size is not the
argument I should make. Provenance, regulatory linkage and local availability
are.

---

### Moe and Aung (2014), *Building Ontologies for Cross-domain Recommendation on Facial Skin Problem and Related Cosmetics*
IJITCS 6(6):33-39, DOI [10.5815/ijitcs.2014.06.05](https://doi.org/10.5815/ijitcs.2014.06.05)

**What they did.** They built **two separate ontologies** in Protege and then a
bridge between them. One holds the user's *problem*, the other holds
*cosmetics*, and a recommendation is a path from a node in the first to a node
in the second.

Getting from a vague complaint to a definite problem is done by conversation.
They use Taxonomic Conversational Case-Based Reasoning: the user gives a rough
query, the system ranks and asks questions, the user answers some, and this
repeats until a specific problem is identified. Then they run the
Ford-Fulkerson maximum-flow algorithm over a weighted directed graph joining
the two domains, and the products carrying the most flow are recommended.

**Their schema, in full, because it is the most concrete of the three papers.**

*Problems domain (source):*

| | |
|---|---|
| Classes | `QApairs`, `Questions`, `Answers`, `Problems`, `Solutions` |
| Subclasses | `YesNoAnswers`, `ConceptAnswers` (under `Answers`) |
| Object properties | `hasQuestion`, `hasAnswer`, `hasProblem`, `hasSolution`, `isNextRelatedTo` |
| Data properties | `hasQDescription`, `hasADescription`, `hasProblemName`, `hasIngredients`, `hasIngValue` |

*Cosmetics domain (target):*

| | |
|---|---|
| Product subclasses | `FacialFoam`, `Toner`, `CleansingCream`, `MilkyLotion`, ... |
| Data properties | `hasIngredients`, `hasIngredientsValue`, `hasName` |
| `ContextualFeatures` subclasses | `PlaceZone`, `AgeLevel`, `CosmeticsBrand`, `Season`, `PriceRange` |
| Object property | `consistsOfPlaceZone`, linking `PlaceZone` to `Country` |

**What I am adopting, and this one changed my mind about my own design.** Their
`ContextualFeatures` class is exactly the thing I have been treating as
ordinary columns. `PriceRange`, `PlaceZone` and `CosmeticsBrand` are not
properties of a product in the abstract - they are properties of *a product in
a context*, and a product in Beirut is in a different context from the same
product in a global catalogue. I have `price_tier` (3 values), `sold_by_shops`
(9 retailers) and `country` (55 values) sitting flat in the CSV. Modelling them
as contextual features is closer to what my data actually means, and it is the
natural home for `source_category` too.

**The two-domain split with an explicit bridge** is also worth taking. My
`SkinConcern` and my `Product` currently sit in one graph joined by
`addresses`. Separating them makes the join explicit and inspectable, which
matters because my supervisor should be able to review the concern-to-product
knowledge without reading 12,629 product rows.

**What I am not taking.** The conversational question-asking, because I have no
user-facing system yet and no user study. And Ford-Fulkerson, which suits their
graph but is heavier than I need: my products are already scored on
availability, price and evidence tier, and a weighted filter does the same job.

**The honest weakness in their paper.** Ingredients are stored as
`hasIngredients` and `hasIngValue` - free text and a number. There is no link
to any register, so nothing in their ontology can tell you an ingredient is
restricted under EU law. That is exactly the gap my CosIng linkage fills.

---

### Serna, Rivera-Gil, Arrieta-Escobar, Boly, Falk and Narvaez Rincon (2021), *Towards an ontology-based decision support system for the design of emulsion based cosmetic products*
13th European Congress of Chemical Engineering, HAL [hal-04674074](https://hal.inrae.fr/hal-04674074v1)

**What they did.** This is the paper that introduces **OntoCosmetic**. They are
not recommending products to consumers - they are helping a formulator *design*
one. Their knowledge base has four building blocks:

- **General subproblems in emulsion formulation** - physicochemical phenomena
  or properties to be promoted or limited, for example achieving shear-thinning
  or thixotropic behaviour.
- **General solution strategies** - routes to a goal not yet tied to a specific
  compound, for example implementing a steric surfactant system.
- **Databases of cosmetic ingredient types** - emollients, surfactants,
  preservatives, actives and others.
- **Heuristics and the interrelations** between ingredients and the above.

They demonstrate it by designing a moisturising cream, and list the intended
uses: analysing solution strategies, supporting reformulation and ingredient
substitution, designing a new product, and representing a design graphically.

**Why it matters to me even though I am not formulating anything.** Their
ingredient typology - emollient, surfactant, thickener, active, preservative -
is a *functional* classification, and I already hold exactly that, from CosIng,
in `ingredient_functions`. I had been treating that column as descriptive
metadata. This paper is the argument for treating it as structure: if
ingredients are typed by function, then a rule like *this is a
surfactant-heavy cleanser and may worsen dryness* becomes a query rather than
something I hard-code.

---

### Gabriel, Serna, Plantard-Wahl, Le Jemtel, Boly and Falk (2023), *Decision making software for cosmetic product design based on an ontology*
ESCAPE-33, Elsevier, pp. 1987-1992, DOI [10.1016/B978-0-443-15274-0.50316-4](https://doi.org/10.1016/B978-0-443-15274-0.50316-4), HAL [hal-04189021](https://hal.science/hal-04189021v1)

**What they did.** They turned OntoCosmetic into a working cross-platform
application called **Formultools**, designed with a user-centred method (the
five-planes approach) and tested iteratively with non-expert users using the
AttrakDiff usability instrument. The tool supports three decisions: screening
ingredients, selecting ingredients against multiple criteria (performance,
origin, price), and evaluating a candidate formulation against design
heuristics.

**OntoCosmetic's structure, as stated here.** Four main concepts and their
interrelations:

| Concept | Holds |
|---|---|
| `Ingredient` | emollients, surfactants, thickeners, actives, others (stabilisers, preservatives) |
| `Formulation` | a list of ingredients with their composition (dosage) |
| `Property` | product properties and ingredient properties; quantitative (HLB) and qualitative (origin: natural or synthetic) |
| `DesignHeuristic` | rules relating the above |

Their emollient property table shows the level of detail: CAS number, INCI
name, chemical class (ester, fatty alcohol, hydrocarbon, silicone,
triglyceride, fatty acid), polarity, viscosity, spreading, emollience,
after-feel, physical state, biodegradability.

**What I am adopting.** Two things, both small and both real.

`Property` split into *product properties* and *ingredient properties*. I have
been mixing them: `spf` and `size_ml` are product properties, while an
ingredient's function and restriction status are ingredient properties. They
behave differently - one is measured once per product, the other is inherited
from a register.

**Origin as a first-class ingredient property.** Their qualitative
natural/synthetic distinction is something users ask about constantly, and my
`free_from` column is a crude version of the same idea.

**What I am explicitly not doing, and I should say this before anyone asks.**
OntoCosmetic is built for **formulation design**, not **product
recommendation**. It models HLB values, rheology and surfactant systems so a
chemist can invent a cream. I model published products so a person can choose
one. The concepts overlap on ingredients and diverge everywhere else, so I am
citing it as the closest cosmetics ontology and borrowing its
ingredient-property structure - not importing it. Importing would bring in
emulsion science I have no data for: I hold no HLB values, no dosages and no
rheological measurements, and I never will, because manufacturers do not
publish them.

---

### What these three add up to for my design

Reading them together changed three things:

1. **Context is a class, not a column.** From Moe and Aung. `PriceRange`,
   `Retailer`, `Country` and `source_category` belong under a
   `ContextualFeature` class, because they describe the product *as available
   here*, not the product itself. This is the single most useful idea I took
   from the three.

2. **Ingredient function is structure, not description.** From Serna et al.
   `ingredient_functions` already holds a CosIng-backed functional
   classification for 91.5% of my products. Typing ingredients by function
   turns several of my hard-coded rules into queries.

3. **Separate product properties from ingredient properties.** From Gabriel et
   al. They are populated differently and should be modelled differently.

And one thing all three share that I can genuinely claim to improve on: **none
of them links ingredients to a regulatory register.** Moe and Aung store
ingredients as text. Serna and Gabriel hold rich physicochemical properties
from supplier data. None can answer *is this ingredient restricted under
Regulation (EC) 1223/2009*. Mine can, for 99.2% of the products holding a
formula.

---

### Noy and McGuinness (2001), *Ontology Development 101*
Stanford KSL Technical Report KSL-01-05

Both papers above cite this, and so should I. It is the standard guide to
building a first ontology, and its central advice is the one I keep coming back
to: **check whether someone has already built what you need before you build
it.** That is the whole reason this document exists.

---

### On the Academia.edu link

I could not open it. The URL you sent returns 404 without your logged-in
session, so I have not read that specific paper and I am not going to
summarise something I have not seen. If you can export the PDF I will read it
properly and add it here. In the meantime the two papers above are the closest
published work I could reach in full.

---

## Part 2 — The four vocabularies I am reusing

I am reusing four, and only four. Each one is here because it does a job I
would otherwise have to do badly by hand.

### 1. CosIng — the EU ingredient register *(already done)*

Not an OWL ontology; a register of 28,573 ingredient names maintained by the
European Commission under Regulation (EC) 1223/2009. Every ingredient in my
dataset is matched against it.

**Why it matters more than anything else on this list:** it turns my ingredient
column from a string into a reference. 11,550 of the 11,645 products with a
formula link to it — 99.2% — covering 96.6% of 292,419 individual ingredient
mentions, with a median per-product coverage of 100%.

**What it gave me:** `ingredient_functions`, `cosing_matched`,
`cosing_coverage`, `restricted_ingredients`. And one finding I was not looking
for: 587 products marked suitable for sensitive skin declare one of the 26
fragrance allergens the EU requires to be labelled by name.

**Status:** done. It is in the dataset now.

---

### 2. schema.org — the commercial half

**The distinction that makes it worth using:** a `Product` is the thing. An
`Offer` is one shop selling that thing at one price on one date. Without that
split I cannot represent a product sold by four Beirut shops at four prices
without either inventing four products or throwing away three prices.

I have a real example: the same Cetaphil lotion is $8.66 at one shop and $32.36
at another. One Product, two Offers. That is not a data quality problem, it is
the market, and schema.org already has the shape for it.

**What I use:** `schema:Product`, `schema:Offer`, `schema:Brand`,
`schema:AggregateRating`, `schema:Review`, `schema:Organization`, with
`schema:name`, `schema:brand`, `schema:price`, `schema:priceCurrency`,
`schema:seller`, `schema:availability`.

**Why not invent it:** because every search engine and every retailer already
speaks it, so anything I publish is readable without a translation layer.

---

### 3. PROV-O — the tier system

**What it is:** the W3C standard for saying where something came from.

**Why I need it:** the whole point of my provenance work. Skin type is 100%
complete, but only 86.7% of it was stated by an identifiable source — tier 1 a
manufacturer (4,460), tier 2 a retailer (4,539), tier 3 a weaker source
(1,954), tier 4 my own inference from the formula (1,676). A recommender that
treats a manufacturer's claim and my inference as the same kind of fact will
make confident statements it cannot support.

**Three properties do nearly all the work:**

| Property | Says |
|---|---|
| `prov:wasDerivedFrom` | this value came from that page |
| `prov:wasAttributedTo` | this claim was made by that party |
| `prov:generatedAtTime` | it was read on that date |

That last one is not decoration. Lebanese prices move, and `price_seen_date`
is already in the file.

**Why not invent it:** because "this claim came from somewhere and somebody
said it" is not a skincare problem, and PROV-O has been the answer since 2013.

---

### 4. SKOS — the closed lists

**What it is:** the standard for controlled vocabularies — a way of saying
*this is a term, here is its label, here is how it relates to other terms*.

**Why I need it:** several of my columns are small fixed vocabularies, and
right now they are strings, which means `Hydrating` and `Hydration` are two
different things to a machine.

| Column | Distinct values |
|---|---|
| `benefits` | 14 |
| `concerns` | 7 |
| `free_from` | 7 |
| `key_ingredients` | 56 |
| `product_type` | 22 |
| `skin_type` | 5 |
| `sensitivity` | 2 |
| `price_tier` | 3 |

**What I use:** `skos:Concept` for each value, `skos:prefLabel` for its name,
`skos:altLabel` for the spellings the shops used, `skos:broader` and
`skos:narrower` where one term sits under another, `skos:ConceptScheme` for
each list.

**The thing that made this click for me:** without SKOS each of those values is
a piece of text floating in the air. With it, each becomes an identifier that
can be pointed at, so "Acne Fighting" is one thing with several spellings
rather than several things.

---

### What I dropped, and why

I had ChEBI, OntoCosmetic, CHEMINF, OBI, eNanoMapper, OntoCAPE, SNOMED CT,
UMLS, GS1 GPC, DermO and SPO on the list. All are gone.

The reasoning is the same for all of them: **import surface has a cost, and
none of these pays for it in my thesis.** ChEBI would let me reason about
chemical similarity, which I would need if I were finding substitute
ingredients — I am not. SNOMED CT has 360,000 clinical concepts and a licence
to negotiate, to express my seven concern values, which I can map by hand in an
afternoon. GS1 GPC classifies retail products, and I have 22 product types.
DermO and SPO are both unmaintained, and building on an unmaintained dependency
is a decision I would have to defend later.

**OntoCosmetic is worth reading and not importing.** It is the closest published
cosmetics ontology to what I am doing, and its class structure is a useful
sanity check on mine. But it was built for a different question and importing
it would bring in more than it gives back. I will cite it and move on.

---

## Part 3 — The classes I am proposing

Derived from the 42 columns I actually have, and from what the two papers
above got right.

### Core

| Class | Instances I have | Comes from |
|---|---|---|
| `Product` | 12,629 | the dataset |
| `Brand` | 1,463 | `brand` |
| `Ingredient` | 13,699 distinct names | `ingredients`, linked to CosIng |
| `ProductType` | 22 | `product_type` |
| `SkinType` | 5 (All, Dry, Combination, Oily, Normal) | `skin_type` |
| `SkinConcern` | 7 | `concerns` — promoted from string to class, per the 2025 paper |
| `Benefit` | 14 | `benefits` |
| `Offer` | one per shop per product | `price_usd`, `sold_by_shops`, `price_seen_date` |
| `Retailer` | 9 Lebanese shops | `sold_by_shops` |

### Provenance

| Class | What it holds |
|---|---|
| `Claim` | a single assertion about a product, e.g. "suits dry skin" |
| `EvidenceTier` | 1–4, the strength of the source behind a Claim |
| `Source` | the page a Claim was read from, with the date |

### Regulatory

| Class | What it holds |
|---|---|
| `CosIngEntry` | the registered ingredient, its functions, CAS number, restriction |
| `RestrictedIngredient` | subclass — the 9,487 products naming one are reachable through it |
| `DeclarableAllergen` | the EU 26; 2,223 products declare at least one |

### Proposed but not yet in the data

| Class | Why | Where it would come from |
|---|---|---|
| `Formulation` | texture and form (cream, gel, serum, oil, stick) — the 2025 paper's idea, and `product_type` currently confuses form with function | derivable from `name` and `product_summary` |
| `ApplicationFrequency` | morning, evening, twice daily, weekly — a routine builder needs it | partly recoverable from `product_summary` |
| `UserProfile` | skin type, concerns, sensitivity, allergies, budget | not collected yet; needed before any evaluation |

### The relations that matter most

```
Product      hasIngredient        Ingredient
Product      suitableFor          SkinType
Product      addresses            SkinConcern
Product      mayWorsen            SkinConcern
Product      hasBenefit           Benefit
Product      hasBrand             Brand
Product      hasFormulation       Formulation
Offer        offersProduct        Product
Offer        soldBy               Retailer
Claim        aboutProduct         Product
Claim        hasEvidenceTier      EvidenceTier
Claim        prov:wasDerivedFrom  Source
Ingredient   registeredAs         CosIngEntry
Ingredient   isDeclarableAllergen DeclarableAllergen
UserProfile  hasSkinType          SkinType
UserProfile  avoidsIngredient     Ingredient
```

`mayWorsen` is deliberately separate from `addresses`. A product can help one
concern and aggravate another, and collapsing both into a single "related to"
loses exactly the information a recommender needs to avoid harm.

---

## What this adds up to

Reuse four vocabularies, define one small ontology on top. CosIng gives
ingredients a regulator. schema.org gives products, prices and shops a shape
that already exists. PROV-O gives every claim a source and a strength. SKOS
turns eight columns of loose text into eight controlled lists.

What is genuinely mine is the middle: the classes connecting a skin type to a
concern to an ingredient to a product that somebody in Beirut can actually buy,
with a record of who said each part and how much that source is worth.

Both papers I read built the recommender and treated the data as a means to it.
I have spent this phase on the data, and the result is that my ontology can
make claims neither of theirs can — that a product is available here, at this
price, and that this particular suitability claim came from the manufacturer
rather than from me.

**Next step:** build the four vocabularies as a small OWL file in Protégé,
populate it from `SKINCARE_FINAL.csv` and `COMBINED_EVIDENCE.csv`, and test it
against a handful of real questions — *a hydrating serum under $30, sold in
Beirut, with no declarable allergen, where the suitability claim came from the
manufacturer.* If it can answer that, the structure is right.

---

## References

1. Hansanie, M. and Kumara, B.T.G.S. (2024). *Ontology based Machine Learning
   Approach for Facial Skincare Products Recommendation.* IEEE ICIPRoB.
   DOI: 10.1109/ICIPRoB62548.2024.10543444

2. *Personalized Skincare Recommendation System Based on Ontology and User
   Preferences* (2025). ResearchGate publication 394583703.

3. Noy, N.F. and McGuinness, D.L. (2001). *Ontology Development 101: A Guide
   to Creating Your First Ontology.* Stanford KSL-01-05.

7. European Commission (2009). *Regulation (EC) No 1223/2009 on cosmetic
   products.* Official Journal of the European Union L342.

8. W3C (2013). *PROV-O: The PROV Ontology.* W3C Recommendation.

9. W3C (2009). *SKOS Simple Knowledge Organization System Reference.* W3C
   Recommendation.
