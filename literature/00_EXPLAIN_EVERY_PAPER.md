# How to explain every paper in the spreadsheet

This follows `PAPERS_TABLE.xlsx` exactly. Same 28 papers, same four groups,
same order. Each section runs through the spreadsheet columns left to right, so
if a supervisor points at a cell, the paragraph explaining it is here.

**Every paper has a box marked "Say this".** That is the version to speak out
loud. Everything under it is for follow-up questions.

---

# CONTENTS

| Part | What |
|---|---|
| 0 | The one minute version |
| 1 | Every word and tool, so nothing catches you out |
| 2 | Group A. The seven skincare and cosmetics ontologies |
| 3 | Group B. The eight papers on ingredients, regulation and skin conditions |
| 4 | Group C. The seven ontology recommenders from other fields |
| 5 | Group D. Reviews, evaluation, and the two alternatives |
| 6 | The tab called 7ad ba3ed |
| 7 | The tab called My ontology, explained |
| 8 | What I dropped from the spreadsheet, and why |
| 9 | Questions they might ask, with answers |

---

# PART 0. THE ONE MINUTE VERSION

> I read every ontology built for skincare or cosmetics. There are about ten.
> Two can be downloaded. None connects ingredients to a regulator. None records
> who made a claim about a product. None checks whether you can actually buy
> the thing where you live.
>
> The one knowledge graph that does connect cosmetic ingredients to EU law,
> published in an Oxford journal this year, has no products in it at all.
>
> So everyone has products and no law, or law and no products. We are the
> intersection, built for Lebanon, on 12,629 products.

---

# PART 1. EVERY WORD AND TOOL

The Tools tab in the spreadsheet has all of these with links and whether we use
them. This is the same list, grouped the same way, in slightly more words.

## The basic ideas

**Ontology.** A formal description of what kinds of thing exist in a subject and
how they relate. The empty form. It says a Product can have Ingredients without
listing any actual products.

**Knowledge graph.** The ontology plus the actual facts. The filled-in forms.

**Triple.** The unit everything is made of. Three parts.

```
Cetaphil Lotion     contains        Phenoxyethanol
    subject         predicate           object
```

A million of these make a graph. No tables, no columns. To add a new kind of
fact you add a triple, you never change a schema.

**Class.** A kind of thing. `Product`, `Ingredient`, `Shop`.

**Individual.** One actual thing. The Cetaphil lotion is an individual of the
class Product.

**Object property.** A link between two things. `hasIngredient` links a Product
to an Ingredient.

**Data property.** A link from a thing to a plain value. `price` links an Offer
to 8.66.

**Defined class.** A class described by a rule instead of a list. You write
"a SensitiveSafeProduct is any product with no declarable allergen" once, and
the software finds the members. **This is the single most important idea in the
whole review**, and it comes from the Abesova student project.

## The languages

**RDF.** The rule that data is made of triples.

**Turtle, `.ttl`.** The readable way of writing RDF. Our ontology file.

**OWL.** RDF plus logic. Lets you write defined classes and have software reason.

**SPARQL.** The query language. SQL for graphs. Say "sparkle".

**SWRL.** If-then rules for what OWL cannot express. OntoCosmetic uses it.

**SHACL.** Validation. OWL says what follows, SHACL says what must be true.

**R2RML, RML, YARRRML.** A file saying "this column becomes this property".
TOXIN used R2RML. We will use RML written as YARRRML.

## The machinery

**Reasoner.** Reads the ontology, works out what follows, finds contradictions.
HermiT ships with Protégé. Pellet runs SWRL rules too. Hansanie used Pellet.

**Triple store.** A database for triples. GraphDB, Apache Jena Fuseki, Stardog.

**Protégé.** The free desktop editor from Stanford. Everyone uses it.

**Owlready2.** Python library to load an ontology and run a reasoner from code.

**Morph-KGC.** The Python engine that reads our mapping file and writes the
triples.

**OntoRefine.** A point-and-click tool inside GraphDB that does the same.
Abesova used it.

**Named graph.** A labelled box inside the store, one per data source. TOXIN
does this so you can always trace where a fact came from.

## Vocabularies we reuse instead of inventing

| | Gives us |
|---|---|
| **schema.org** | Product, Offer, price, brand, seller |
| **PROV-O** | wasAttributedTo, wasDerivedFrom, generatedAtTime. Our evidence levels in a standard language |
| **SKOS** | prefLabel, altLabel, broader. For benefits, which are labels not classes |
| **Dublin Core** | title, creator, licence, date |

## Outside data we link to

**CosIng.** The EU Commission's cosmetic ingredient register, 28,573 entries.
**DermO.** 3,000 skin disease terms written by dermatologists, on BioPortal.
**Wikidata.** Wikipedia's facts as a graph. Knows who owns each brand.
**DBpedia.** Older cousin of Wikidata. Abesova used it.

## Methods

**METHONTOLOGY.** Older, document-heavy. The default in this field: three of
the Indonesian papers use it, and Moe & Aung follow it without naming it.
**MOMo.** Modular Ontology Modeling. Build in modules, draw before writing. Ours.
**LOT.** Linked Open Terms. Requirements, build, publish, maintain. Ours.
**Competency questions.** Questions the ontology must answer, written before
building. They become our SPARQL queries, which become our evaluation.

## Checking and publishing

**OOPS!** Free website, 41 known design mistakes, graded.
**FOOPS!** Free website, scores how FAIR your ontology is.
**WIDOCO.** Makes a documentation page from the ontology file.
**w3id.org.** A permanent address. **Zenodo.** A DOI per release.

## Words that only appear in the papers

**CCBR.** Conversational case-based reasoning. Narrow a problem by asking
questions like a doctor. Moe & Aung.
**Ford-Fulkerson.** A maximum flow algorithm. Water through pipes. Moe & Aung.
**CNN.** Convolutional neural network, reads images. Hansanie & Silva.
**AHP.** Analytic Hierarchy Process. Weigh several criteria by comparing them
in pairs. Formultools.
**AttrakDiff, SUS.** Standard user experience questionnaires.
**SCCS.** The EU Scientific Committee on Consumer Safety. Its opinions sit
behind the CosIng annexes.
**INCI.** The standard ingredient naming on every label. **In concentration
order**, down to one percent.
**The EU 26.** Twenty-six fragrance allergens that must be named on the label.
**ICD-10.** The WHO disease list every hospital uses.
**SMILES.** A text way of writing a molecule. TOXIN uses it.
**Graph attention network.** A neural net that passes messages between
connected nodes. HaCKG.

---

# PART 2. GROUP A. THE SKINCARE AND COSMETICS ONTOLOGIES

These are the ones doing what we are doing. The direct competitors.

---

## A1. Moe & Aung (2014)

### Say this

> Two researchers in Myanmar built two separate ontologies, one describing skin
> problems as a tree of questions, one describing cosmetics. The system asks
> you questions until "I have acne" becomes "papules", then treats the link
> between problem and products as water through pipes and scores each product
> by how much flow reaches it. We take their eight-step construction checklist
> and their idea of keeping price and place separate from the product. Their
> ingredients are just text with no regulator behind them, which is our gap.

### The paper

| | |
|---|---|
| Who | Hla Hla Moe, University of Technology Yatanarpon Cyber City; Win Thanda Aung, University of Computer Studies Yangon. Myanmar |
| Where | International Journal of Information Technology and Computer Science, 6(6), 33 to 39, May 2014 |
| Notes | Weak journal. I cite it for the method, not the standing |
| Cited | 3 for the 2014 version, 8 for a 2016 reprint |
| Link | doi.org/10.5815/ijitcs.2014.06.05 |
| Did I read it | The whole PDF. It is in our repo |

### The problem

Recommender systems normally work inside one domain. Amazon recommends books to
book buyers. But sometimes your problem lives in one world and the fix lives in
another. Your problem is a skin condition; the fix is a cosmetic. No public
dataset links the two. So they said: we will build both worlds as ontologies,
then build a bridge.

### Their data

Nothing stated. No source, no size, no product count. This is the paper's
biggest weakness and I say so.

### Their ontology

**Method.** Not named, but they list eight tasks in order, and that is
METHONTOLOGY in all but name:

| Task | Produces |
|---|---|
| 1 | A glossary of every term, its definition, its synonyms and acronyms |
| 2 | Concept taxonomies |
| 3 | Relation diagrams, including links to other ontologies |
| 4 | A concept dictionary: instances, attributes, relations per concept |
| 5 | A description of every relation |
| 6 | A description of every instance attribute |
| 7 | A description of every class attribute |
| 8 | A constants table |

**Classes, problem side.** `Questions`, `Answers` (splitting into
`YesNoAnswers` and `ConceptAnswers`), `QApairs`, `Problems`, `Solutions`.

**Classes, cosmetics side.** `FacialFoam`, `Toner`, `CleansingCream`,
`MilkyLotion`, plus **`ContextualFeatures`** holding `PlaceZone`, `AgeLevel`,
`CosmeticsBrand`, `Season`, `PriceRange`.

**Properties.** `isNextRelatedTo` (which question to ask after which),
`hasQuestion`, `hasAnswer`, `hasProblem`, `hasSolution`, `hasIngredients`,
`hasIngValue`, `consistsOfPlaceZone`.

**Rules.** None. **Downloadable.** No. Only figures in the paper.

### How they built it

**Data in.** Not reported. Almost certainly typed by hand in Protégé.

**Tools.** Protégé. **No reasoner, no SPARQL, no outside data.** An ontology
paper that never actually reasons.

**How it recommends, step by step.** This is the part to be ready for.

*Where the questions come from.* They are written by hand and stored in the
ontology as individuals of `Questions`. The system never invents a question; it
only chooses which stored one to ask next.

*What a case is.* One complete diagnosis: a bundle of question-answer pairs with
the conclusion at the end. The Papules case holds six pairs and the word
"Papules". All the cases together are the case base. Somebody built it by hand.

*How it narrows.* Every case starts as a candidate. Each answer scores every
case: contradict and it sinks, agree and it rises. The next question shown is
the top unanswered question inside the surviving top cases.

*Their real example, from Table 1.* The user types "I have acnes on my face."

| | System asks | User says | What that eliminates |
|---|---|---|---|
| 1 | Are they white spots? | No | whiteheads |
| 2 | Flat spots with a dark centre? | No | blackheads |
| 3 | Are they inflammation? | Slight | the severe forms |
| 4 | Which size? | Small | nodules, cysts |
| 5 | Are they pink? | Yes | pustules |
| 6 | Just before your period? | Yes | confirms |

Six questions. Conclusion: **Papules.** (The elimination column is my reading of
what must be happening. They never publish the case base.)

*Their similarity formula, in words.* Two concepts score 1 if identical,
`(n-1-m)/(n-1+m)` if one sits under the other (n = steps to the top of the
tree, m = steps between them), 0 otherwise. **Further apart in the tree, less
similar.** So the vague "I have acnes" already pushes all acne cases up before a
single question, because it is near them in the tree.

*Then the bridge.* Papules at the top, products at the bottom, ingredient links
between. They quote Kirchhoff's Law, "everything that leaves the source must
eventually get to the sink", and run **Ford-Fulkerson**. Turn a tap on at the
problem, see how much reaches each product.

```
W(vᵢ) = Σ f(k,i)      weight of a product = total flow into it
```

### Did it work

**Tested with** precision, recall and F-measure against a cut-off they call
alpha. Low alpha recommends everything (high recall, low precision), high alpha
recommends two products (the reverse). F-measure balances them.

**Their numbers.** Ten products, from Table 2:

| Rank | Product | Weight |
|---|---|---|
| 1 | 8 | 0.70 |
| 2, 3 | 7, 9 | 0.60 |
| 4 | 4 | 0.58 |
| 5 | 3 | 0.53 |
| 6 | 5 | 0.52 |
| 7 | 2 | 0.45 |
| 8 | 1 | 0.38 |
| 9 | 10 | 0.37 |
| 10 | 6 | 0.32 |

**Does it hold up?** No. No dataset size, no baseline, and they claim to be
"more accurate than the other related works" with no comparison table anywhere.
One oddity: page one contains a paragraph about handwritten Chinese calligraphy.
Nothing to do with skincare. Looks pasted in and never removed.

### For us

**Take.** The eight-task checklist, especially task 1, a glossary of every term
with its synonyms (ya3ne our unified schema). Our benefits column has
"Hydrating" and "Hydration" as two strings. Also `ContextualFeatures`: price
and place describe a product *as sold somewhere*, not the product itself. Our
`price_tier`, `sold_by_shops`, `country`, `source_category` belong there.

**Leave.** Ford-Fulkerson. Our products already carry availability, price and
evidence level, so a weighted filter does the same job. And the questioning,
since it needs a hand-built case base and a dermatologist.

**They can't.** Say an ingredient is regulated. Theirs is text with a number.
Ours links to CosIng on 99.2 percent of products with a formula.

**My idea.** Their throwaway `Season` class. Beirut summer is humid and coastal,
winter is dry. A gel cleanser right in August is wrong in January. Nobody in the
whole review models climate.

---

## A2. OntoCosmetic (2021 and 2023)

### Say this

> The only cosmetics ontology you can actually download. But it is for the
> wrong user. It helps a chemist design a cream that does not separate, with
> classes like droplet size and rheology. Two papers: 2021 builds the ontology,
> 2023 turns it into a phone app called Formultools. We take their ingredient
> function names and their idea of recording where each rule came from. We
> leave the entire chemistry branch. And they admit in their own conclusion
> that experts never tested it.

### The paper

| | |
|---|---|
| 2021 | J. Serna, V. Falk, P. Perré, M. Camargo, S. Morel, "Towards an ontology-based decision support system for the design of emulsion-based cosmetic products", 13th European Congress of Chemical Engineering. HAL hal-04674074 |
| 2023 | A. Gabriel, M. Camargo, S. Morel, J. Serna, "Decision making software for cosmetic product design based on an ontology", ESCAPE-33, pp 1987 to 1992. DOI 10.1016/B978-0-443-15274-0.50316-4 |
| Who | Université de Lorraine, France, with Universidad Nacional de Colombia |
| Notes | Respectable chemical engineering venues |
| Link | purl.org/ontocosmetic |
| Did I read it | Both PDFs and the OWL file itself |

### The problem

Formulating an emulsion is hard and the knowledge is scattered across textbooks
and experts' heads. Put it in one place a chemist can query at the early design
stage. Then (2023) make it a tool a formulator will actually use.

### Their data

Four kinds of material, combined on purpose:

| Building block | Holds | Their example |
|---|---|---|
| General subproblems | physical properties to promote or limit | shear thinning, thixotropic behaviour |
| General solution strategies | a route to a goal, not tied to a compound | a steric surfactant system |
| Ingredient databases | typed by function | emollients, surfactants, preservatives, actives |
| Heuristics | rules connecting ingredients to the above | with thresholds |

279 individuals in the published file.

### Their ontology

**Method.** 2021: none named. 2023: five planes user-centred design (Garrett
2011), co-design between cosmetics experts and computer scientists, iterative
with usability tests between rounds.

**Size, counted from the file.** 116 classes, 26 object properties, 20 data
properties, 279 individuals.

**Classes.** `HLB`, `DropletSize`, `Rheology`, `AqueousThickeners`,
`OWCosmeticEmulsion`, `HeuristicForSurfactant`, `MeltingPoint`,
`Emollient_Dosage`. Ingredient types: `Emollient`, `Surfactant`, `Thickener`,
`Active`, `Preservative`, `UvFilter`, `Humectant`, `Antioxidant`, `Stabilizer`,
`PHRegulator`.

If asked: **HLB** is hydrophilic-lipophilic balance, a number for how much an
emulsifier likes water versus oil. **Rheology** is how a substance flows.
Manufacturers never publish either.

**Properties.** `hasHeuristicHighThreshold`, `hasHeuristicLowThreshold`,
**`hasHeuristicSource`**, `hasOrigin` (natural or synthetic).

**Rules.** Yes. SWRL rules in Protégé for the formulation heuristics, each with a
high threshold, a low threshold, and a source. **That source property is the
one to point at.** Every rule records where it came from. That is provenance on
rules, and nobody else in the review does it.

**Downloadable.** YES. purl.org/ontocosmetic. The only one.

### How they built it

**Data in.** By hand, by experts. 279 individuals typed in. (Impossible for us.)

**Tools.** Protégé with SWRL. For the app: AttrakDiff questionnaire between
iterations, and **AHP** for multi-criteria ranking. AHP works in three taps:
pick the properties you care about, say which to maximise and which to
minimise, then compare them in pairs and it computes weights, with a
consistency ratio to catch contradictions.

**How it works.** It does not recommend to a shopper. The app does three things
for a formulator: screen ingredients by property, rank ingredients on several
criteria at once (performance, origin, price) with AHP, and check a proposed
formula against the heuristics.

### Did it work

**2021.** One case study, the design of a moisturising cream. Four intended
uses: analysing strategies, supporting reformulation, designing a new product,
drawing a design.

**2023.** AttrakDiff with non-expert testers between rounds. They stopped when
testers stopped finding problems.

**Does it hold up?** No numbers. And in their own conclusion: *"In a near
future, it will be tested with experts."* So the most serious cosmetics ontology
in the literature was never validated with experts.

### For us

**Take.** The ingredient function names (though since CosIng is the Commission
and OntoCosmetic is secondary, taking them from CosIng is cleaner, and we note
the alignment). Keeping product properties separate from ingredient properties:
`spf` and `size_ml` belong to the product, function and restriction to the
ingredient. `hasOrigin`. `hasHeuristicSource`, the same instinct as our
evidence levels. And they measured user experience with a standard instrument
and reported it. Almost nobody in my review reports any named evaluation
instrument. We can take this maybe.

**Leave.** The whole chemistry branch. Importing the file, 116 classes to use
ten. The mobile app itself.

**They can't.** Say whether you can buy it, what it costs, or who made the
claim on the box.

**My idea.** Flip it. They go from goal to ingredients. We have 295,991
ingredient mentions with functions attached, so we could go from ingredients
back to what the formulator was trying to do, and test it against their rules.

---

## A3. Hansanie & Silva (2024)

### Say this

> A photo of your face goes to a neural network that grades your acne. That
> grade is written into an ontology as a fact about you, and the ontology picks
> the products. The design choice that matters is that they split the ontology
> into three files and merged them, because the three parts change at different
> speeds. We copy that. Their 87.5 percent is satisfaction, not accuracy, and
> quoting it correctly makes us look careful.

### The paper

| | |
|---|---|
| Who | Maduri Hansanie, Thushari Silva. University of Moratuwa, Sri Lanka |
| Where | IEEE International Conference on Image Processing and Robotics, 2024 |
| Notes | IEEE conference |
| Cited | 2 |
| Link | doi.org/10.1109/ICIPRoB62548.2024.10543444 |
| Did I read it | The whole PDF |

### The problem

Choosing skincare is hard and the wrong product makes skin worse. They call
existing approaches "rather inefficient and inaccurate". So read the face with
a machine, then let an ontology do the choosing.

### Their data

Two kinds.

For the vocabulary: interviews with dermatologists and health professionals,
plus a survey of **11 men and 10 women aged 21 to 30** about their skincare
habits.

For the image model: the **ACNE04** dataset (Xiaoping Wu et al.), topped up with
photos from DermNet. Because the data was unbalanced they merged "severe" and
"very severe" into one class, so the network predicts three levels: mild,
moderate, severe.

Product count: never given.

### Their ontology

**Method.** Not named. **Top down**: general classes first, specific underneath.
Then **three ontologies merged** into one skincare domain ontology:

| File | Holds | Changes |
|---|---|---|
| Skincare concepts | skin types, concerns, what suits what | almost never |
| Product information | products and ingredients | weekly |
| User profile | the person, allergies, ratings | per user |

**Classes.** `Person`, `TreatmentProduct` (e.g. AcneControlCleanser),
`SkinType` (e.g. OilySkin), `KeyIngredient` (e.g. SalicylicAcid),
`ProductRecommendation`.

**Properties, from their Tables I and II.**

| Property | From | To |
|---|---|---|
| `suitableFor` | TreatmentProduct | SkinType |
| `hasKeyIngredient` | TreatmentProduct | KeyIngredient |
| `hasProductRecommendation` | TreatmentProduct | ProductRecommendation |
| `hasRating` | ProductRecommendation | a number |
| `hasAge`, `hasGender` | Person | a number, a word |

**Rules.** None reported. Pellet checks consistency. **Downloadable.** No link.

### How they built it

**Data in.** Not clearly reported. The spreadsheet-to-ontology step is
described as design, not automation.

**Tools.** Protégé to build. **Pellet** to check consistency and infer.
**Owlready2** to query from Python. **Tkinter** for the desktop window. And the
CNN: three Conv2D layers with 16, 32 and 16 filters, max pooling between, a
dense output of 3 units with softmax.

**How it works.** Photo in. CNN outputs mild, moderate or severe. That grade is
asserted into the ontology as a fact about the user. Pellet reasons. Owlready2
pulls the products out. **The image model and the knowledge stay separate**, so
either could be swapped.

### Did it work

**Tested with** standard ML metrics for the CNN, then a five-point survey of 24
people who tried the system.

**Numbers.** CNN: accuracy **77.5%**, precision 78.2%, recall 75.1%, F1 76.6%.
Survey: **87.5%** said the products suited them, 91.7% said the interface was
easy, 91.6% were satisfied overall.

**Does it hold up?** Partly. The headline 87.5 is satisfaction, NOT accuracy.
The model scored 77.5. No baseline, no ground truth. Quote it as what it is.

### For us

**Take.** Three separate ontologies merged. A reasoner from day one: we have
spent months finding faults that produced plausible wrong answers instead of
errors, and a reasoner complains loudly. Ratings inside the ontology. Owlready2.

**Leave.** The CNN. No photos, no ethics approval, our contribution is the
product side. Their design means it could be added later.

**They can't.** Say a product is stocked in Beirut, costs $11, and has a
restricted preservative. **But they consulted dermatologists and we have not.**
Say that before they ask. Then say the fix: DermO, row 12.

**My idea.** Their architecture has an empty socket where the camera plugs in.
Plug in a **barcode**. Scan the box in a Beirut pharmacy, ask if it suits you
and whether it is cheaper next door. No ethics approval, no image dataset.

---

## A4. Abesova (VU Amsterdam, 2023)

### Say this

> A student project, not a paper, and I say so. But it contains the single most
> important idea in the review. They never tag a product as suitable for oily
> skin. They write what the phrase means, once, and let the reasoner find the
> products. That is the difference between an ontology and a spreadsheet. And
> their own limitation 3 says ingredient-based rules would be better and they
> did not do it. That sentence is our contribution, sitting in their paper.

### The paper

| | |
|---|---|
| Who | Sara Abesová, Karolína Hajková, Yozlem Ramadan, Małgorzata Zdych |
| Where | Vrije Universiteit Amsterdam, Knowledge and Data course, Group 31, 2023 |
| Notes | A STUDENT PROJECT |
| Cited | 0 |
| Link | In our repo, papers folder |
| Did I read it | The whole PDF |

### The problem

Give someone a full routine from four inputs: skin type, skin tone, country, and
how much effort they will put in. Output: the three best products per
category, plus the Sephora page for their country.

### Their data

A Sephora product and review CSV they found on GitHub, a second CSV of countries
that have Sephora shops, and DBpedia for country data.

### Their ontology

**Method.** Middle out, named. Start with what you are sure of, work outward
both ways. Explicitly iterative:

| Step | What happened |
|---|---|
| 1 | One teammate built a base ontology |
| 2 | The Sephora CSV widened the scope and forced new classes |
| 3 | Classes and properties added to fit |
| 4 | A second CSV, countries, folded in the same way |
| 5 | More properties to join the two |

That matches our situation exactly. We did not know our final columns either.

**Size.** 36 classes, 6 object properties, 6 data properties.

**Classes.** `Category` (Cleanser, Moisturizer, Treatment; Treatment splits
into Exfoliant with Chemical and Physical, Serum, Toner; SPF sits under
Moisturizer). `Product` with four skin-type subclasses. `Skin Type`. `Skin
Tone` with nine values. `Brand`, `Country`, `Rating Stars`, `Review Id`.

**Properties.** `hasBrand`, `hasCategory`, `hasSkinType`, `hasSkinTone`,
`aboutProduct`, `hasReviewId`, `hasRating`, `hasOilyScore`, `hasDryScore`,
`hasNormalScore`, `hasCombinationScore`, `hasSephoraWebPage`.

**Rules, and this is the important part.** From their section 7.6:

```
Oily Skin Products         equivalent to   hasOilyScore value 5
Dry Skin Products          equivalent to   hasDryScore value 5
Combination Skin Products  equivalent to   hasCombinationScore value 5
Normal Skin Products       equivalent to   hasNormalScore value 5
skc:Cleanser               equivalent to   rdf:Cleanser
```

The first four are defined classes. The last one merges two vocabularies that
used different names for the same thing.

| Without it | With it |
|---|---|
| tag 4,000 rows by hand | write one line |
| a corrected formula leaves the tag wrong | membership recalculates itself |
| a reviewer must trust your tagging | a reviewer reads one line |

**Downloadable.** No.

### How they built it

**Data in, step by step.** CSV into **OntoRefine**. Map columns to classes.
Build the graphs with SPARQL **CONSTRUCT**. Download **nine Turtle files**.
Import them into **GraphDB** together with the base ontology. Same again for the
countries CSV.

**Tools.** OntoRefine to map. GraphDB to store and reason with class
restrictions. SPARQL for everything. **DBpedia** through an outside endpoint:
`dbr:Czech_Republic` gave the country, then its capital `dbr:Prague`, then
`geo:lat` and `geo:long`, and they drew a map without typing a coordinate.

**How it works.** A set of SPARQL queries, not code. Class restrictions put
products into skin-type classes. Queries pick three per category and add the
Sephora page for your country.

### Did it work

One worked example: 9 products for one user. No metrics. They admit the
interface was rushed and shows raw URIs. **Doesn't hold up as evaluation**, but
that is not why I cite it.

**Their three stated limitations:**

| Their limitation | For us |
|---|---|
| 1. Every product in Oily Skin Products has rating exactly 5.0, so nothing ranks inside the class | A defined class puts things in a set but does not order them. Ranking is separate, and price and availability are ours |
| 2. A product with one 1.0 review can beat products known to score 5.0 | Thin evidence beating strong evidence. Exactly why our evidence levels exist |
| 3. *"class restrictions based on ingredients could be developed. This would ensure a more symbolic and chemical approach, compared to the statistical one that is currently employed"* | **Our contribution, written as their future work** |

### For us

**Take.** THE DEFINED CLASS. OntoRefine as a way in. DBpedia linking for free
facts. **Leave.** Classes resting on review scores; ours rest on the formula.
**They can't.** Limitation 3.

**My idea.** They pulled *place* out of DBpedia. We pull *ownership* out of
Wikidata. One `owl:sameAs` per brand, then ask Wikidata's property P749 (parent
organisation). I ran it on our data: **L'Oréal owns 570 of our products**
across La Roche-Posay 154, Garnier 120, Kiehl's 67, Vichy 62, SkinCeuticals 61,
CeraVe 45, Lancôme 41, L'Oréal Paris 19, Decléor 1. And **118 L'Oréal products
with niacinamide are sold in Lebanon, from $0.51 (Vichy) to $185.58
(SkinCeuticals)**. Same company, same active, 364 times the price. That answers
"is there a cheaper equivalent", which is what a shopper in a currency crisis
actually asks, and no system in the review can answer it.

---

## A5. bit-Tech (2025)

### Say this

> Our closest competitor, and I want to be upfront that I only have the
> abstract. They scraped Skinsort, the same global source we used, plus two
> Indonesian shops, and built a skincare ontology with METHONTOLOGY: 12
> classes, over 25 properties, 3,800 products. We differ on four things: our
> market, our scale, our link to the EU register, and the fact that we model
> price, availability and who made each claim.

### The paper

| | |
|---|---|
| Title | Personalized Skincare Recommendation System Based on Ontology and User Preferences |
| Where | bit-Tech, Komunitas Dosen Indonesia, 2025 |
| Notes | Regional Indonesian journal. Modest standing but directly comparable. **NEED THE FULL PDF** |
| Link | jurnal.kdi.or.id/index.php/bt/article/view/2857 |
| Did I read it | Only the abstract and publisher page |

### The problem

Content-based and collaborative filtering miss the links between skin types,
concerns and ingredients. An ontology captures them.

### Their data

Web scraping of Sociolla, Beautyhaul and **Skinsort**. Over 3,800 products and
over 28,000 ingredients.

### Their ontology

**Method.** METHONTOLOGY, named. **Classes, 12.** User, Product, Brand, Product
Category, Allergen Type, Ingredient, Benefit, Formulation Trait, Key
Ingredient, Skin Concern, Skin Type, What It Does. **Properties.** More than 25
object properties, not detailed. **Downloadable.** Not stated. Check.

Note how close their classes are to our columns. Benefit, Skin Concern, Skin
Type, Key Ingredient, Allergen Type are all things we already hold.

### How they built it

Web scraping into the ontology; whether a mapping language was used is not
stated. **Apache Jena Fuseki** to store and query. SPARQL with reasoning.

### Did it work

Can't tell without the full paper.

### For us

**Take.** Two class names we would not have thought of: **Formulation Trait**
and **What It Does**. That split is our evidence problem in class form. What It
Does is the marketing claim; Formulation Trait is the physical fact. One is
asserted by a seller, the other derivable from the formula.

**Leave.** Their market and their homemade allergen list.

**They can't.**

| Them | Us |
|---|---|
| Indonesia | Lebanon, where availability itself is uncertain |
| 3,800 products | 12,629 |
| an Allergen Type class, presumably hand curated | the EU 26 plus the full CosIng register, 28,573 entries |
| no price, availability or provenance mentioned | all three |

**My idea.** Adopt their two names, attach our evidence levels to What It Does
and our CosIng derivation to Formulation Trait. Then the model says openly
which half of a product description is advertising.

---

## A6. Utari (JELIKU, 2023)

### Say this

> A very small Indonesian cosmetics ontology: three classes, 62 products,
> METHONTOLOGY, tested by running SPARQL queries. It teaches us almost nothing.
> I keep it for one reason: next to our 12,629 it shows the scale without me
> claiming anything.

### The paper

Pengembangan Ontologi Semantik Pada Domain Produk Kosmetik. Utari et al.,
Universitas Udayana, JELIKU, 2023. 0 citations. I read the abstract.

### What they did

Too many products to choose from, so build a semantic ontology. METHONTOLOGY.
3 classes, 5 object properties, 62 individuals. Evaluated by running SPARQL
queries and checking the results looked right.

### For us

Two things only. The scale comparison. And proof that METHONTOLOGY is the
default here, which is why choosing something else needs a stated reason.
Nothing to criticise: it is a proof of concept and does not pretend otherwise.

---

## A7. Mahadewi (JELIKU, 2024)

### Say this

> Another small Indonesian ontology, this time with a collaborative filtering
> algorithm on top. What I take is not the method but the evaluation: two
> named, standard instruments. In a field where a systematic review found
> nobody reports any evaluation method, naming your instruments is a
> differentiator.

### The paper

Body care recommender using Slope One collaborative filtering. Mahadewi et al.,
Universitas Udayana, JELIKU, 2024. 0 citations. I read the abstract.

### What they did

Body care information online is often wrong, so put the knowledge in an
ontology and recommend on top. METHONTOLOGY for the ontology, Prototyping for
the system. **Slope One** predicts your rating from the average difference
between items.

### Did it work

**SUS 82.344** (System Usability Scale, ten questions, out of 100; 82 counts as
good). **MAE 0.3556** (Mean Absolute Error, how far predicted ratings are from
real ones; closer to zero is better).

### For us

**Take.** SUS, if we ever build an interface. And the habit of naming
instruments. **Leave.** Slope One, we have no ratings. **They can't.** No
regulator, no provenance, no availability, and an MAE on ratings says nothing
about whether the advice was medically sensible.

---

# PART 3. GROUP B. INGREDIENTS, REGULATION AND SKIN CONDITIONS

Not recommenders. They give our ingredients and concerns a legal or medical
standing that nobody in group A has.

---

## B1. TOXIN KG (2025)

### Say this

> The strongest paper in the review by venue, an Oxford journal. A knowledge
> graph of cosmetic ingredient safety built from the official EU safety
> opinions, so it proves that putting cosmetic regulation into a graph is
> established practice. But it has no products in it. All the law, nothing on
> a shelf. That is exactly where we sit.

### The paper

| | |
|---|---|
| Who | S. Sepehri et al., Vrije Universiteit Brussel |
| Where | Database: The Journal of Biological Databases and Curation, Oxford University Press, **2025** |
| Notes | Strong. Peer reviewed, open access |
| Cited | 4 |
| Link | doi.org/10.1093/database/baae121. Live at toxin-search.netlify.app |
| Did I read it | The whole article |

I first wrote 2024. It is 2025. Corrected, and I say so.

### The problem

The EU banned animal testing for cosmetics but there is no validated
replacement. Make the old safety data reusable so risk can be judged without
animals.

### Their data

Safety data on annexed cosmetic ingredients from **SCCS scientific opinions
2009 to 2019**. That is the same committee whose opinions sit behind the CosIng
annexes we use. Loaded: 88 ingredients, of which 53 affect at least one liver
measure in a 90-day study.

### Their ontology

Reuses **TXPO**, the ToXic Process Ontology, from the OBO Foundry, which itself
pulls in Gene Ontology, ChEBI, Disease Ontology and others. **SMILES** added so
every chemical has one standard identity. **ToxRTool** scores study reliability
automatically. **Downloadable.** YES, live and searchable.

### How they built it

**Data in.** Toxicologists transcribe into Excel. Computer scientists have
read-only access and generate the RDF **using R2RML**. The most useful sentence
in the paper for us.

**Tools and practices, line by line:**

| They did | It matters because |
|---|---|
| R2RML to turn spreadsheets into triples | a mapping file, not a script. Our population method |
| Named graphs, one box per source, so users "can easily manage and trace the origins of the information" | our evidence-level idea at the storage layer |
| Linked out to KEGG, Reactome, UniProt by IRI | point at other people's identifiers, don't copy |
| Matched sources by comparing labels and IRIs | the same matching problem we solved with token coverage and a synonym map |
| Ontodia to draw the graph | a picture for meetings |

**How it works.** Not a recommender. Filter for ingredients linked to liver
toxicity and follow the chain to the harm.

### Did it work

Use cases showing retrieval works. 88 loaded, 53 flagged. Claims to be a
retrieval tool and demonstrates retrieval. No overreach.

### For us

**Take.** Three things that change our plan: R2RML/RML for loading, named
graphs per source (`skinsort`, `lb-retail`, `lb-origin`, `cosing`, `evidence`,
`inferred`), and linking out by IRI. **Leave.** Toxicology depth. **They
can't.** IT HAS NO PRODUCTS.

**My idea.** They model the evidence *behind* a restriction. We model only the
restriction as a pointer like Annex V/29. One `owl:sameAs` per ingredient and a
product on a Beirut shelf traces all the way to the SCCS opinion that limits
phenoxyethanol to one percent. No consumer system does that.

---

## B2. HaCKG (2025)

### Say this

> This paper trimmed one of my ideas, so I raise it myself. They built a
> cosmetics knowledge graph of products and ingredients and trained a graph
> neural network on it to predict whether a product is halal. So a cosmetics
> graph with a neural component already exists. Our angle survives, because
> they predict with a model and we would derive from the ingredient list, but
> it is a smaller claim than I first thought.

### The paper

Halal or Not: Knowledge Graph Completion for Predicting Cultural
Appropriateness of Daily Products. Van Thuy Hoang et al., South Korea. IEEE
Access, 2025. 8 citations. I read the abstract.

### The problem and their data

Halal prediction looks at ingredients one at a time and misses the
relationships between products and ingredients. A cosmetics dataset of
products, ingredients and properties; size not in the abstract.

### How they built it

A **relational graph attention network with residual connections**: a neural
net that learns by passing messages between connected nodes and paying
attention to what kind of link each edge is. Pre-trained on the graph,
fine-tuned to predict halal. Output: a probability, no reason.

### Did it work

Reported as beating state-of-the-art baselines; figures not in the abstract.
Sound for an ML paper, but prediction with no reasoning and no cited authority.

### For us

**Take.** Their own argument: one-ingredient-at-a-time misses the
relationships. That is an argument FOR a graph, made by somebody else in an
IEEE journal. Also proves a cosmetics KG is publishable. **Leave.** The
network. **They can't.** Give a reason. **My idea.** Use them as an evaluation
target: where our derivation and their prediction agree, mutual validation;
where they disagree, that set is a result.

---

## B3. CosIng-KG (GitHub)

### Say this

> Not a paper, a GitHub project. Somebody already converted the EU CosIng
> register into the exact graph format we need. Before I write a line of
> ontology I check whether it is usable. If yes, our whole ingredient layer is
> free and we cite them. If no, our own conversion becomes something we claim.

biobricks-ai/cosing-kg, serving kg.toxindex.com. All 28,573 entries if complete.
I have only read the repository page. **Highest value half hour available right
now. Do it first.**

---

## B4. CCIBP (2023)

### Say this

> A cosmetic ingredient platform in Bioinformatics, a strong journal. Covers
> regulations from several world regions, not only the EU. Two uses: maybe a
> second ingredient source if Lebanon follows anything non-European, and
> another precedent that a resource paper is publishable in a serious venue.

Linlin Gong et al., China. Bioinformatics, OUP, 2023. 2 citations. Live at
design.rxnfinder.org/cosing. I read the abstract.

Holds regulations from major regions, physicochemical properties, human
metabolic pathways, and plant data for natural ingredients. Same shape as
TOXIN: ingredients, no products. Thirty minutes in step 2 to see if it adds
anything CosIng does not.

---

## B5. DermO (2016)

### Say this

> A medical ontology of skin diseases built by hand by dermatologists, over
> three thousand terms, lined up with ICD-10, free on BioPortal. It fixes a
> weakness nobody has raised yet: our concerns column already makes medical
> statements, eczema, rosacea, acne, and no clinician has checked them. We
> cannot get a dermatologist quickly. We can align to one they already built.

### The paper

University of Birmingham. Journal of Biomedical Semantics, 2016. DOI
10.1186/s13326-016-0085-x. On BioPortal and GitHub in OBO and OWL 2. I read the
abstract and the BioPortal record.

### What they did, step by step

Dermatologists wrote out the terms by hand. No scraping, no learning. Over
3,000 terms. Every disease is filed by its real features:

| Filed by | Meaning |
|---|---|
| anatomical location | where on the body |
| heritability | runs in families or not |
| affected cell or tissue | what part of the skin |
| aetiology | what causes it |

Twenty top categories. Lined up with **ICD-10**, the WHO disease list every
hospital uses. Published on GitHub and BioPortal, free. Connected to other
disease and symptom ontologies.

### Why it matters more than I first thought

I looked at our `concerns` column. Six values, every one a real clinical
entity:

| Our concern | Products |
|---|---|
| May Worsen Eczema | 6,901 |
| May Worsen Rosacea | 5,871 |
| May Worsen Irritation | 5,819 |
| May Worsen Oily Skin | 5,514 |
| May Worsen Dryness | 4,549 |
| May Trigger Acne | 4,261 |

**We are already making medical statements.** "May worsen eczema" is a claim
about a diagnosed disease. We derived it from the formula with our own rules and
nobody clinical has checked the rule or the wording.

### How we use it

Six lines.

```turtle
skc:MayWorsenEczema   skc:aboutCondition  dermo:Eczema .
skc:MayTriggerAcne    skc:aboutCondition  dermo:AcneVulgaris .
skc:MayWorsenRosacea  skc:aboutCondition  dermo:Rosacea .
```

*About* the condition, not *is* the condition. Our concern is a statement about
a disease. That is the honest choice. After that, our products reach ICD-10 and
the medical vocabularies, all inherited.

### My idea: body site

DermO knows where on the body each disease sits. Our types imply a site but
only as shop labels:

| Site | Products |
|---|---|
| Eye area | 637 |
| Lips | 550 |
| Body | 676 |
| Hands | 62 |
| Face | about 10,700 |

Link them to real anatomy and three things become possible: ask about a place
not a category; find the gap in a routine ("you have nothing for your eye
area"); catch a body product carrying a facial concern. Nobody in cosmetics
connects product to body site through a clinical ontology.

---

## B6. The halal flavouring ontology (2024)

### Say this

> About food flavourings, not cosmetics, but structurally it is our problem. An
> ingredient has a status granted by an authority, and a product inherits its
> status from its ingredients. Swap halal certification for EU annex
> restriction and it is the same shape. I take their three-part pattern:
> ingredient, authority, status, with the authority as a thing in its own
> right.

Journal of Information Science Theory and Practice, 12(2), 2024. Malaysia, with
experts from JAKIM, the Department of Islamic Development. I read the abstract.

**What we take.** Because the authority is separate, we can say *Phenoxyethanol
is restricted under Annex V/29 according to the European Commission*, and
leave room for a Lebanese authority later. One choice future-proofs the whole
regulatory layer.

**Be honest.** HaCKG (B2) already built a cosmetics KG for halal prediction, so
a halal layer is no longer novel on its own. Our angle is derivation with a
cited reason, not prediction.

---

## B7. Klaschka (2015)

### Say this

> Not an ontology, and the most immediately useful paper here. She checked every
> natural substance in the INCI list against the EU hazard classification. Of
> the 655 that appear there, 56 percent are classified hazardous and 53 are
> carcinogenic, mutagenic or toxic to reproduction. That gives us a question we
> can answer this week with data we already hold.

### The paper

Ursula Klaschka, Ulm University. Environmental Sciences Europe, 2015. **107
citations.** I read the abstract.

### What she did and found

Took the INCI list, pulled out every natural substance, checked each against
the EU classification and labelling inventory.

| | |
|---|---|
| Natural substances in INCI | 1,358 |
| Of those, in the EU inventory | 655 |
| **Classified hazardous** | **56%** |
| For human health | 38% |
| For skin and eyes | 35% |
| **Carcinogenic, mutagenic or toxic to reproduction** | **53 substances** |

She also flags that the classifications are inconsistent: some food plants are
classed severely, some known sensitisers not at all.

### For us

Peer reviewed proof, 107 citations, that **natural does not mean safe**. That
arms our `free_from` column and every "clean" claim. And a question nobody else
can answer: across 12,629 products, do the ones sold as natural actually
contain fewer hazardous ingredients? We hold the formulas, the claims and the
register. No new data. That is why the plan has a `NaturalClaimProduct` class.

---

## B8. MVFM (2026)

### Say this

> A very small, very new paper with one idea I need. EU law says claims must
> not mislead but does not require them to be backed by the composition. A
> barrier-repair cream need not contain barrier lipids. Their method uses the
> position of ingredients in the INCI list to check. That is why our ontology
> records position, not just presence.

Rusana Plonsak, Journal of Applied Cosmetology, 2026. 0 citations. I read the
abstract.

**The method.** INCI lists are in concentration order down to one percent.
Find the first regulated preservative or fragrance; that is roughly the one
percent line. Score everything above it on Hydration, Lipid, Structural, 0 to 3
each. Compare to the claim.

**Result.** Three products, one evaluator. One product sold as anti-aging
scored H=4, L=7, S=6, a lipid-heavy texture cream, with two regulated allergens
in its active zone. The author says larger validation is still to do.

**For us.** INCI position as a signal is why `IngredientListing` carries a
position number. And we could run their method across 11,802 formulas, which
is the validation they say is missing.

---

# PART 4. GROUP C. ONTOLOGY RECOMMENDERS FROM OTHER FIELDS

Nobody solved our problems in skincare. People solved them in food, shopping
and academic papers. This is where the mechanisms come from.

---

## C1. Middleton (2004)

### Say this

> The highest ranked paper in my review, ACM Transactions on Information
> Systems, cited in the thousands. It established that using an ontology in a
> recommender is a serious research position. Its three findings are my three
> arguments, and the second is my answer to the cold start problem.

Stuart Middleton, Nigel Shadbolt, David De Roure, University of Southampton.
ACM TOIS 22(1), 54 to 88, 2004. doi.org/10.1145/963770.963773.

**What they built.** Two working systems, Quickstep and Foxtrot, recommending
academic papers. The user's interests are described **in terms of a topic
ontology** rather than keywords, built from watching what they read plus asking.

**Three findings, and our use of each:**

| Their finding | Our use |
|---|---|
| Inference up the hierarchy improves profiling | our concerns have a hierarchy: interest in post-acne marks implies hyperpigmentation |
| Outside knowledge bootstraps a cold start | **our cold start answer.** A new Beirut user has no history, but the ontology already knows what suits combination skin |
| Letting users correct their own profile improves accuracy | an interface argument |

**My idea.** Their "watching the user" in Lebanon is not browsing history. It
is **the receipt**. Beirut pharmacies are small, repeat custom is normal. What
somebody re-bought is more honest than what they clicked.

---

## C2. FoodKG (2019 and 2021)

### Say this

> If I read one paper outside skincare, this one. They combined recipes,
> nutrition data from an authority, food taxonomies and links to existing
> ontologies into one graph, then built a service that finds a recipe from
> what is in your kitchen while respecting hard constraints like allergies.
> Swap recipes for products and nutrition for CosIng and that is us. The
> follow-up stops ranking and answers a question with constraints instead,
> which is what we should build.

**2019.** Haussmann, Seneviratne, Chen, Ne'eman, Codella, Chen, McGuinness,
Zaki. Rensselaer and IBM. ISWC 2019, the top semantic web conference. Published
at foodkg.github.io. **2021.** Chen, Subburathinam, Chen, Zaki, WSDM. arXiv
2101.01775.

**The analogy, exactly:**

| FoodKG | Us |
|---|---|
| recipes | products |
| ingredients | INCI ingredients |
| nutrition from an authority | CosIng from the Commission |
| food taxonomies | product type taxonomy |
| allergies as hard constraints | the EU 26 |
| what can I cook with what I have | what can I buy in my pharmacy |

**Four practices to copy.** Present construction as the contribution (a top
venue accepted that). State a maintenance plan. Several apps on one graph.
**Hard constraints, not preferences**: an allergy is a filter, not a score,
and that is exactly where an ontology beats a neural net.

**The 2021 framing.** Turn the user's requirements into constraints and answer
over the graph. Output is the set of things satisfying every requirement, not a
ranked list. For us: "dry skin, under $15, no allergens, buyable in Hamra" is
four real columns. And a constraint is either satisfied or not, which is
checkable without users.

---

## C3. Di Noia / Ostuni (2012 to 2015)

### Say this

> An Italian group who recommend using only the links an item has in public
> data, with no ratings. Two films are similar if they share a director, a
> genre, a period. For us: two products are similar if they share ingredient
> functions, a restriction profile, a concern, a price band. Our rating column
> is half empty and we have no user history, so this is the only similarity
> that uses everything we collected.

Politecnico di Bari. I-SEMANTICS 2012, RecSys 2013, WIMS 2015. Movies, using
DBpedia, Freebase, LinkedMDB.

**Mechanism.** A semantic vector space model. Each item becomes a list of
numbers whose dimensions are its **links**, not words.

**Their open problem, which we measured.** They say matching an item to the
right outside entity is the hard part. We know: fuzzy matching scored a
category page 100 against a full product name, and our database pass had a
19 to 33 percent error rate. Strong paragraph for the thesis.

**My idea.** They enriched thin items. Ours are rich. Enrich the **shops**
instead: Wikidata and OpenStreetMap know where Beirut pharmacies are.
"Available fifteen minutes' walk away" is something no cosmetics system has done.

---

## C4. AliCoCo (2020)

### Say this

> Alibaba, at SIGMOD, one of the very best database venues. Every product
> ontology describes what a product is; shoppers think about what they need.
> So they made needs into entities in their own right. Our concerns column is a
> user need sitting in a product schema pretending to be an attribute. If I
> want one idea that makes this thesis memorable, it is this one.

Xusheng Luo et al., Alibaba and Shanghai Jiao Tong. ACM SIGMOD 2020. Code at
github.com/alicogintel/AliCoCo. Deployed at national scale.

**The idea.** User needs as first-class entities: not "moisturiser" but
"outdoor barbecue", "keeping warm in winter".

| An attribute can | A need entity can |
|---|---|
| attach to one product | be met by a combination of products |
| hold a value | carry a budget |
| be filtered on | carry a season, a place, a constraint |

**My idea.** Lebanese needs are not global needs. "A routine under $20 a
month." "Products that don't need a fridge." "Something for a bride." "A
routine I can buy in one pharmacy." Every one is expressible in our data.
Nobody can copy it without our dataset. Most original claim, least certain, do
it last.

---

## C5. Guo survey (2022)

### Say this

> The main survey of knowledge graph recommenders, IEEE TKDE, over a thousand
> citations. Three families, and all three assume you already have a user
> interaction matrix and a graph for your domain. For skincare in a local
> market no such graph exists. So we sit upstream of the whole survey. We build
> the thing it assumes you already have.

IEEE TKDE 34(8), 3549 to 3568, 2022. Cite the journal version, not the 2020
preprint.

| Family | Uses the graph by | Strength | Weakness |
|---|---|---|---|
| Embedding | turning entities into vectors | scales | reasoning is gone |
| Path | finding paths user to item | explainable | expensive |
| Unified | propagating across the graph | best accuracy | needs lots of interaction data |

**Say this and "you have no users" is answered:** the survey classifies methods
for *using* a knowledge graph and assumes one exists for the domain. For
skincare in a local market it does not. This thesis builds it.

---

## C6. E-Prod (2023), with Alaa (2021)

### Say this

> A Turkish state-funded project that tracks live e-commerce sites and pushes
> products straight into an ontology, continuously. The automated version of
> what we did by hand, with the best evaluation in this group: 250 real users
> and a baseline. Alaa's paper adds the criticism that one-shot ontologies go
> stale, and our named graph design already answers it.

Tiryaki et al., Journal of Organizational Computing and Electronic Commerce,
2023. Alaa et al., Electronics, 2021.

**E-Prod.** Tracks several e-commerce systems in real time, transfers product
info into the ontology continuously, learns preferences by watching behaviour,
matches semantically. Tested with 250+ users against collaborative filtering:
accuracy 92.79%, precision 92.93%, recall 90.58%.

**Alaa.** Everyone builds the ontology once from a snapshot, but the world
moves. Proposes a semi-automatic method with an evolution subsystem.

**For us.** Our six Lebanese retailers could be re-read on a schedule, turning
the dataset from a snapshot into a live resource. Biggest upgrade available, no
new modelling. And reloading `graph:lb-retail` weekly without touching anything
else answers Alaa by construction.

---

## C7. Lahoud (Lebanon, 2022)

### Say this

> A Lebanese team published an ontology recommender in a Springer journal,
> evaluated on Lebanese high school students. So a Lebanon-focused ontology
> recommender is publishable, in a real journal, with 36 citations. That
> answers whether our local scope is a limitation before anybody asks.

Christine Lahoud et al. Education and Information Technologies, Springer, 2022.

Five approaches compared on one case: user-based CF, item-based CF,
demographic, knowledge-based with case-based reasoning, ontology, and hybrids.
The hybrid reached 98% similar cases, 95% personalised, 95% usefulness, 92.5%
satisfaction.

**Three uses.** Local scope is not a weakness. The hybrid beat every pure
approach, backing our future work. And these are Lebanese academics working on
ontology recommenders: possible examiners, reviewers, collaborators. Find out
where they are.

---

# PART 5. GROUP D. REVIEWS, EVALUATION, AND THE ALTERNATIVES

What counts as good, and the two papers that do our problem without an ontology.

---

## D1. Rahayu review (2022)

### Say this

> The most useful single citation in my review, and it is not even about
> skincare. They systematically reviewed 28 ontology-based recommenders and
> found two things: these systems rarely use any named method for building the
> ontology, and not one of the 28 described how they evaluated it. Not one. So
> naming our method and reporting our evaluation is not tidiness. In this field
> it counts as a contribution.

Computers and Education: Artificial Intelligence, 2022. **137 citations.**

The two sentences: *"ontology-based recommender systems seldom use the
methodology of building ontologies"* and *"none of the primary studies
described ontology evaluation methodologies."*

**For us.** One paragraph naming MOMo and LOT, plus one afternoon running OOPS!
and FOOPS!, puts us ahead of a 28-paper sample on the two things it was worst
at. Put this in the introduction.

---

## D2. Tarus (two papers, 2017)

### Say this

> Two papers by the same lead author. The review, cited 451 times, concludes
> that ontologies improve recommendation quality. The hybrid, cited 277 times,
> states that ontological knowledge alleviates cold start and sparsity. That is
> our "why an ontology" and our "cold start" with strong citations attached.

Review: Artificial Intelligence Review, Springer. Hybrid: Future Generation
Computer Systems, Elsevier Q1.

**The hybrid's division of labour** transfers wholesale: the ontology handles
the domain, the learned part handles users. Which means our ontology is the
half that must exist first.

---

## D3. COPPER (2025)

### Say this

> Not about skincare. An ontology for personalised exercise advice, in a Q1
> health journal. I include it because it is the best example I found of what a
> good ontology paper looks like now, and I intend to match its structure.
> Modular, openly published, evaluated by competency questions and use cases
> rather than accuracy.

Braun et al., International Journal of Behavioral Nutrition and Physical
Activity, 2025. 288 classes, 64 object properties, 9 data properties.

**Their structure, which we copy:**

| Phase | What |
|---|---|
| Specification | literature, use cases, decision-tree workshops |
| Conceptualisation | theory, classification systems, users, experts, datasets |
| Formalisation | logic rules, then OWL in Protégé |
| Modules | upper ontology plus profile, planning, activity, context, **barrier**, coping |
| Evaluation 1 | the process against OBO principles |
| Evaluation 2 | the ontology for logical consistency |
| Evaluation 3 | the recommendations with competency questions and use cases |

Openly available is one of their three stated novelty claims.

**My idea.** They have a **barrier** module: what stops a person doing the
activity. Ours is unavailability, price, the currency crisis. "Barrier" is a
better name than "availability" because it covers price, stock, distance and
season in one idea.

---

## D4. FEVR (2022)

### Say this

> A framework for evaluating recommenders, ACM Computing Surveys, 283 citations.
> Its argument is that how you evaluate must follow what you are trying to
> achieve. Our goal is verifiable correctness with a stated reason, not ranking
> accuracy. So precision and recall are the wrong instruments, and this is the
> citation that says so.

Zangerle and Bauer, Austria. This is the answer to "why no precision and
recall". One sentence, fully defended.

---

## D5. Lee (lululab, 2024)

### Say this

> This is the paper that does our problem without an ontology, so we answer it
> directly. A neural network estimates a product's efficacy from its ingredient
> list, combined with AI skin analysis. Same starting point as us. The
> difference is entirely in how ingredients connect to outcomes: learned from
> data for them, derived from the EU register for us. And with enough labelled
> data, a model probably beats rules on accuracy. Our argument is not accuracy.
> It is that a recommendation that cannot say why cannot be used by a
> pharmacist or audited by a regulator.

Jinhee Lee et al., lululab Inc., Seoul. Journal of Cosmetic Dermatology, Wiley,
2024. doi.org/10.1111/jocd.16218. Corporate R&D, proprietary data.

| Them | Us |
|---|---|
| learn ingredient-to-efficacy from data | derive it from CosIng plus stated rules |
| output a weight | output the ingredient, its function, the annex entry |
| need proprietary training data | need none |
| cannot handle an unseen ingredient | it is in the register or we say it is not |
| cite nothing | cite Regulation (EC) 1223/2009 |
| ignore availability | make it core |

**My idea.** Use a model like theirs as a hypothesis generator and our ontology
as the check. Train something small on our 11,802 formulas, take its confident
predictions, test them against CosIng. The disagreement set is a result only we
can compute.

---

## D6. Ali (ontology versus LLM, 2026)

### Say this

> The answer to the question every supervisor asks in 2026: why not just ask an
> LLM. A clinical study compared three ways of answering medical questions.
> ChatGPT-4 got 37 percent right. Grounding the same kind of model in an
> ontology got 98 percent and cut hallucination from 63 percent to under 2.
> Skincare is safety-relevant too, and our ontology is the grounding.

Mohamed Ali et al., Egyptian hospitals. Journal of Biomedical Informatics,
2026. 11 citations.

| Condition | Accuracy | Hallucination |
|---|---|---|
| ChatGPT-4 | 37% | ~63% |
| DeepSeek-R1 | 52% | ~48% |
| **Ontology-grounded** | **98%** (59 of 60) | **1.7%** |

Sixty clinical questions, reference answers from five peer-reviewed hospital
studies. A proper controlled comparison. Put it in the introduction.

---

# PART 6. THE TAB CALLED 7AD BA3ED

Only the skincare ontologies, side by side, with us in the last column. Thirteen
rows. Three are highlighted green:

- **Ingredients tied to EU law.** Only TOXIN, and TOXIN has no products.
- **Records who claimed what.** TOXIN by source. Nobody else at all.
- **Knows if you can buy it.** Nobody.

We tick all three. Say the sentence at the bottom of the tab: *TOXIN has the law
but not one product. Everyone else has products and no law. Nobody writes down
who made a claim. Nobody checks if you can buy it. We are the bit in the
middle.*

---

# PART 7. THE TAB CALLED MY ONTOLOGY

Four pictures, top to bottom.

**Picture 1, the flow.** One CSV row, through a mapping file and Morph-KGC,
into GraphDB with one box per source, through the reasoner, out as an answer to
a SPARQL question. About 1.8 million triples. The mapping file goes in the
appendix so a reviewer can see how every cell became a fact.

**Picture 2, the four modules.** CORE (skin types, concerns, functions,
regulatory status; changes almost never). PRODUCT (product, ingredient,
listing, brand, offer, shop; changes with the market). EVIDENCE (claim, level,
agent; the contribution). LEBANON (shops, needs, the defined classes). Hansanie
split theirs into three for the same reason. MOMo is built around modules.
Handing a dermatologist the CORE file alone is forty lines.

**Picture 3, one real product.** Cetaphil lotion. Two ingredient listings, each
with a position and a CosIng entry: niacinamide at 3, phenoxyethanol at 11 and
restricted under Annex V/29 according to the European Commission. One claim,
"suitable for sensitive skin", said by Cetaphil, level 1, read on cetaphil.com
on a date. Two offers, $8.66 at Sohati and $32.36 at Feel22.

Three things a spreadsheet cannot do here: the ingredient carries its position,
the claim carries who said it, and the price sits on the offer so one product
holds two prices.

**Picture 4, the six defined classes.** Each with its rule and the number we
expect: SensitiveSafe about 9,537, AvailableInLebanon about 11,937,
ManufacturerStated about 4,460, Regulated about 9,613, FullyIdentified about
9,032, NaturalClaim to measure. Predict first, then run the reasoner. If
SensitiveSafe does not land near 9,537 the model is wrong. Expect the 593
sensitive-skin products that contain an allergen to show up as a contradiction.
That is a finding.

---

# PART 8. WHAT I DROPPED, AND WHY

The old spreadsheet had 59 rows. This one has 28. What went, and where it went.

| Dropped | Why | Where the idea lives now |
|---|---|---|
| Formultools as its own row | it is the same ontology as Serna | merged into A2 |
| Constrained QA over FoodKG | a follow-up to FoodKG | merged into C2 |
| Alaa ontology evolution | one idea, maintenance | merged into C6 |
| Tarus hybrid as its own row | same author, same point | merged into D2 |
| Landau INCI guide | background only | Tools tab, INCI |
| D3X | only an evaluation example | COPPER does that job better |
| George and Lal | just a phrase | Tarus covers it |
| OntoCommerce | one metric idea | dropped |
| NCF, Zhang survey | deep learning background | Lee covers the DL argument |
| CKE, RippleNet, KGAT, KPRN, path quality | hybrid neural background | Guo's survey covers the families |
| RDF2Vec, OWL2Vec*, LLMs4OL, Shimizu LLM | future work | not needed for the review |
| Noy 101, LOT, MOMo, XD, ODP book, Grau, MODL | methods | Tools tab |
| R2RML, Morph-KGC, PE-TRE, SWRL, PROV-O, SHACL, OOPS!, FOOPS! | tools | Tools tab |

If a supervisor asks about any of them: *those are background or tooling. They
are in the Tools tab, or they were folded into the row they belong with. The 28
in the table are the ones that shaped the design.*

---

# PART 9. QUESTIONS THEY MIGHT ASK

**Why an ontology and not the spreadsheet?** A spreadsheet can filter. It
cannot hold a definition. With a defined class I write the rule once and
membership recalculates when a formula is corrected. And it catches
contradictions: the 593 products marked sensitive-safe that contain an allergen
become a formal inconsistency the reasoner finds by itself.

**Why not deep learning?** No user data to train on. A model gives a weight
not a reason, and in a domain with physical risk that means no pharmacist can
use it and no regulator can audit it. And Ali 2026: grounding a model in an
ontology took clinical accuracy from 37 to 98 percent.

**Is Lebanon a limitation?** Lahoud published a Lebanon-focused ontology
recommender in Springer with 36 citations. And local scope is the contribution:
every other system assumes you can buy what it recommends.

**You have no users.** A scope statement, not a gap. Guo's survey classifies
methods for using a graph and assumes one exists. For skincare in a local
market it does not. We build it.

**How will you evaluate?** Four ways, none needing users: OOPS! and FOOPS!,
fifteen competency questions as SPARQL, predicted versus actual class sizes,
and the comparison tab. FEVR says match the evaluation to the goal, and our
goal is verifiable correctness.

**Is it novel?** Four safe claims: ingredients tied to the EU register on
12,629 products, provenance modelled, real availability, a published artefact.
Nobody has the first three together. One in six competitors manages the fourth.

**Has a dermatologist checked your vocabulary?** No, and that is the real
weakness. Our concerns are words we derived. The fix is aligning to DermO,
which dermatologists built. If either of you knows a dermatologist or
pharmacist who could give me an hour, that closes it.

**Why MOMo and LOT and not METHONTOLOGY?** METHONTOLOGY is the default here,
thorough but old and document-heavy. MOMo is built for modules, which suits a
four-module design. LOT is built around reusing terms and publishing, which are
the two things this field is worst at.

**What if the Indonesian paper already did this?** They model what a product
is. We model what it is, whether you can buy it, what it costs today, and who
made each claim. Their allergen list is homemade; ours is the EU register.
3,800 against 12,629. And I still need their full PDF, which I have flagged.

**What is the weakest part?** The fifth idea, Lebanese needs as entities. Most
original, least certain. I do it after the four safe ones.
