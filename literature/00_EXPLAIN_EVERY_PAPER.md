# How to explain every paper, out loud, without getting stuck

One file. Everything in it. Read it once before the meeting and you will be
able to walk through the whole field without opening anything else.

**How this is built.** Part 1 is the vocabulary, so no word can catch you out.
Part 2 is the ten papers, one section each, each with a script you can say
aloud, then the detail underneath it. Part 3 is the comparison and the gap.
Part 4 is our plan. Part 5 is every question they might ask and the answer.

---

# CONTENTS

| Part | What |
|---|---|
| 0 | The sixty second version, if you only get one minute |
| 1 | Every word and every tool, explained |
| 2 | The ten papers, one at a time |
| 3 | The comparison table and the gap |
| 4 | What we build, and in what order |
| 5 | Every question they might ask, with the answer |

---

# PART 0. THE SIXTY SECOND VERSION

Say this if they ask you to summarise everything.

> I looked for every ontology built for skincare or cosmetics. There are about
> ten. Only two of them can be downloaded. None of them connects ingredients to
> any regulator. None of them records who made a claim about a product. None of
> them checks whether the product can actually be bought where the user lives.
>
> The one knowledge graph that does connect cosmetic ingredients to European
> law was published in an Oxford journal this year, and it has no products in it
> at all. Every skincare ontology has products and no law.
>
> Our work is the intersection of those two: real products, real law, and a
> record of where every claim came from, built for the Lebanese market.

---

# PART 1. EVERY WORD AND EVERY TOOL

If a supervisor stops you on a word, this is where the answer is.

## 1.1 The basic ideas

**Ontology.** A formal description of what kinds of thing exist in a subject
and how they relate. Think of it as the empty form: it says a Product can have
Ingredients, without listing any actual products.

**Knowledge graph.** The ontology plus the actual facts. The filled-in forms.
Our 12,629 products turned into a graph would be the knowledge graph; the rules
about what a Product is would be the ontology.

**Triple.** The unit everything is made of. Three parts: subject, predicate,
object.

```
Cetaphil Lotion     contains        Phenoxyethanol
    subject         predicate           object
```

A million triples make a graph. There are no tables and no columns.

**Class.** A kind of thing. `Product`, `Ingredient`, `Shop`.

**Individual, or instance.** One actual thing. `Cetaphil Moisturizing Lotion`
is an individual of the class `Product`.

**Object property.** A link between two things. `hasIngredient` links a Product
to an Ingredient.

**Data property.** A link from a thing to a plain value. `price` links an Offer
to the number 8.66.

**Domain and range.** The two ends of a property. `hasIngredient` has domain
Product and range Ingredient, meaning only Products can have ingredients and
only Ingredients can be had.

**Taxonomy.** A tree of classes, each one a kind of the one above it. Serum is a
kind of Treatment is a kind of Product.

**Axiom.** A statement in the ontology that the software treats as true and can
reason from.

## 1.2 The languages

**RDF.** Resource Description Framework. The standard that says data is made of
triples. It is a data model, not a file format.

**Turtle, `.ttl`.** The readable way of writing RDF. This is what our ontology
file is written in.

**OWL.** Web Ontology Language. RDF plus real logic. It lets you say things like
"nothing can be both a Product and an Ingredient" or "a SensitiveSafeProduct is
any product with no allergens in it", and have software work out the
consequences.

**SPARQL.** The query language for graphs. It is SQL for RDF. You write a
pattern with question marks for the unknowns and it returns everything that
fits. **Pronounced "sparkle".**

**SWRL.** Semantic Web Rule Language. If-then rules for the things OWL cannot
express. "If a product contains a declarable allergen, then it is not
recommended for sensitive skin."

**SHACL.** Shapes Constraint Language. Validation. OWL says what can be
concluded; SHACL says what must be true or the data is wrong. "Every product
must have exactly one brand."

**IRI.** A globally unique name that looks like a web address. Instead of
calling something "phenoxyethanol", you call it
`http://ourontology.org/ingredient/Phenoxyethanol`, so two people can talk about
the same thing without having agreed in advance.

## 1.3 The machinery

**Reasoner.** A program that reads the ontology and works out what follows. Two
jobs: it decides which class everything belongs to, and it finds contradictions.
The named ones you will hear:

| Reasoner | Note |
|---|---|
| **HermiT** | comes with Protégé, our default |
| **Pellet** | supports SWRL rules. Hansanie and Silva used it |
| **Openllet** | the maintained version of Pellet |
| **ELK** | very fast, but handles only a simple subset of OWL |

**Triple store.** A database for triples with SPARQL on the front.
**GraphDB**, **Apache Jena Fuseki**, **Stardog**, **Virtuoso**.

**Endpoint.** A web address you send SPARQL queries to.

**Protégé.** The free desktop editor from Stanford where you build an ontology
by clicking. Everyone in this field uses it.

**Owlready2.** A Python library for loading an ontology, adding facts and
running a reasoner from code.

**Named graph.** A labelled box inside a triple store holding one set of
triples. Instead of one pile, you have one box per data source, so you always
know where a fact came from and you can reload one source without touching the
rest.

## 1.4 Getting data into a graph

**Population.** The step where your spreadsheet becomes triples.

**R2RML.** A W3C standard for describing how a database becomes RDF. A file that
says "this column becomes this property".

**RML.** The same idea extended to CSV, JSON and XML files.

**YARRRML.** RML written in YAML so a human can read it.

**Morph-KGC.** The Python engine that reads an RML or YARRRML mapping and
produces the triples. This is what we will use.

**OntoRefine.** A point-and-click tool inside GraphDB that does the same job.
Abesova's team used it.

**Why a mapping file rather than a script.** A script produces the same triples
but nobody can audit it, it cannot go in an appendix, and a reviewer cannot
rerun it. A mapping file is one page, readable, and rebuilds the whole graph
with one command.

## 1.5 Reusable vocabularies

Rather than inventing every term, you reuse ones other people already defined.

| Vocabulary | What it gives us |
|---|---|
| **schema.org** | `Product`, `Offer`, `price`, `brand`, `seller`. Google understands it |
| **PROV-O** | `wasAttributedTo`, `wasDerivedFrom`, `generatedAtTime`. A W3C standard for saying where information came from. This is our evidence levels in a standard language |
| **SKOS** | `prefLabel`, `altLabel`, `broader`. For lists of words that are not really objects, like our benefits, where "Hydrating" and "Hydration" are one concept with two labels |
| **Dublin Core** | `title`, `creator`, `licence`. The bookkeeping that makes a dataset citable |

**DBpedia and Wikidata.** Wikipedia turned into a graph. You link to them and
get facts for free instead of typing them.

## 1.6 Methods for building an ontology

**METHONTOLOGY.** An older, thorough method built around producing a series of
documents: a glossary, taxonomies, relation diagrams, a concept dictionary.

**Middle out.** Start with the concepts you are certain of, then work in both
directions, towards the general and towards the specific.

**Top down.** Start with the most general class and split downwards.

**LOT, Linked Open Terms.** A modern lightweight method in four activities:
requirements, implementation, publication, maintenance. Built around reusing
published terms and publishing your result. **This is one of ours.**

**MOMo, Modular Ontology Modeling.** A modern method built around modules and
reusable design patterns, with graphical diagrams as the way you elicit
knowledge. **This is our other one.**

**Ontology Development 101.** Noy and McGuinness, 2001. The seven-step teaching
guide everybody cites.

## 1.7 Checking your work

| Tool | What it does |
|---|---|
| **OOPS!** | a free website that checks your ontology against 41 known design mistakes, graded critical, important, minor |
| **FOOPS!** | a free website that scores how FAIR your ontology is: Findable, Accessible, Interoperable, Reusable |
| **OntoMetrics** | structural numbers: depth, breadth, richness |
| **WIDOCO** | generates a readable documentation page from the ontology file itself |

**Competency question.** A question your ontology must be able to answer. You
write them before you build and test against them afterwards. They turn "is my
ontology any good" into something measurable.

**Defined class.** A class described by a rule rather than by a list. Instead of
tagging four thousand products as suitable for oily skin, you write the rule
once and the reasoner works out the membership. **This is the single most
important idea in the whole review.**

## 1.8 Words from the papers

**CCBR, Conversational Case Based Reasoning.** Solving a problem by finding the
most similar past case, gathering the information through a conversation rather
than a form.

**Ford-Fulkerson.** A classical algorithm for maximum flow in a network. Think
water through pipes.

**SCCS.** Scientific Committee on Consumer Safety. The EU body whose opinions
sit behind the CosIng annexes.

**CosIng.** The European Commission's official cosmetic ingredient database,
28,573 entries, kept under Regulation (EC) 1223/2009.

**INCI.** International Nomenclature of Cosmetic Ingredients. The standard
naming system printed on every product. **Ingredients are listed in order of
concentration**, down to one percent, which makes position meaningful.

**Annex.** A list attached to the EU regulation. Annex II is banned substances,
III restricted, IV colorants, V preservatives, VI UV filters.

**The EU 26.** Twenty-six fragrance allergens that must be named on the label
when present above a threshold.

**OBO Foundry.** A community of biomedical ontologies built to shared
principles.

**BioPortal.** The main public repository where biomedical ontologies are
published.

---

# PART 2. THE TEN PAPERS

Each one has a **say this** box at the top. That is the version to speak. The
detail underneath is for when they ask a follow-up.

---

## B1. Moe and Aung (2014)

### Say this

> They built two separate ontologies, one describing skin problems as a tree of
> questions, one describing cosmetics. The system asks the user questions until
> a vague complaint like "I have acne" becomes a specific diagnosis. Then it
> treats the link between the problem and the products as a flow network and
> uses a maximum flow algorithm to score which products match best, giving a
> ranked list. We take their eight-step construction checklist and their idea of
> keeping price and place separate from the product itself.

### The facts

| | |
|---|---|
| Authors | Hla Hla Moe and Win Thanda Aung, two universities in Myanmar |
| Published | International Journal of Information Technology and Computer Science, 6(6), pages 33 to 39, 2014 |
| DOI | 10.5815/ijitcs.2014.06.05 |
| Venue quality | Low barrier journal. **Say this plainly if asked.** We cite it for the method, not the standing |
| Downloadable ontology | No. It exists only as figures in the paper |
| I read | The full PDF, it is in our repo |

### The problem they set out to solve

Recommender systems normally work inside one domain. Amazon recommends books to
book buyers. But sometimes the problem lives in one world and the solution lives
in another. Your problem is a skin condition; the fix is a cosmetic. No public
dataset links the two. So they said: we will build both worlds ourselves as
ontologies, then build a bridge between them.

### What they built, ontology one: problems

Not a list of diseases. **A tree of questions and answers.**

Classes: `Questions`, `Answers` (splitting into `YesNoAnswers` and
`ConceptAnswers`), `QApairs`, `Problems`, `Solutions`.

Properties: `hasQuestion`, `hasAnswer`, `hasProblem`, `hasSolution`, and the
important one, **`isNextRelatedTo`**, which says which question to ask after
which.

Data properties: `hasQDescription`, `hasADescription`, `hasProblemName`.

### What they built, ontology two: cosmetics

Product classes: `FacialFoam`, `Toner`, `CleansingCream`, `MilkyLotion`.

Data properties: `hasIngredients`, `hasIngredientsValue`, `hasName`.

And separately a class called **`ContextualFeatures`** holding `PlaceZone`,
`AgeLevel`, `CosmeticsBrand`, `Season`, `PriceRange`, with an object property
`consistsOfPlaceZone` linking PlaceZone to Country.

Both built in **Protégé**.

### How the questioning works, in detail

This is the part to be ready for, because it is the cleverest thing in the
paper.

**Where the questions come from.** They are written by hand and stored in the
ontology as individuals of the class `Questions`. The system never invents a
question. It only chooses which stored one to ask next.

**What a case is.** A case is one complete diagnosis: a bundle of
question-answer pairs with the answer at the end. For example the Papules case
holds six question-answer pairs and the conclusion "Papules". All the cases
together are the **case base**, and somebody built it by hand.

**How it narrows.** Every case starts as a candidate. Each answer the user gives
scores every case. Cases that contradict the answer sink; cases that agree rise.
The next question shown is the highest-ranked question that appears in the
surviving top cases and has not been answered yet.

**Their actual worked example**, from Table 1 of the paper. The user types
"I have acnes on my face":

| | System asks | User answers |
|---|---|---|
| 1 | Are they white spots? | No |
| 2 | Are they flat spots with a dark centre? | No |
| 3 | Are they inflammation? | Slight |
| 4 | Which size are they? | Small |
| 5 | Are they pink? | Yes |
| 6 | Are you just before or during your menstrual cycle? | Yes |

Six questions and the system concludes: **Papules**.

Each answer eliminates candidates. "No" to white spots removes whiteheads. "No"
to dark centres removes blackheads. "Slight" inflammation removes the severe
forms. "Pink" separates papules from pustules.

**Their similarity formula**, in plain words:

```
1                        if the two concepts are the same
(n - 1 - m)/(n - 1 + m)  if one sits under the other
0                        otherwise
```

`n` is how many steps from the concept up to the top of the tree, `m` is how
many steps between the two concepts. **The further apart in the tree, the less
similar.** This is why the vague opening "I have acnes" is still useful: it is
near the answer in the tree, so it pushes all the acne cases up before a single
question is asked.

### How the recommendation is produced

Three stages.

1. **Narrow.** The conversation above. Vague complaint becomes definite problem.
2. **Join.** Problem and products go into a weighted directed graph, the problem
   at the top and products at the bottom.
3. **Score.** They apply the **Ford-Fulkerson maximum flow algorithm**, quoting
   Kirchhoff's Law that "everything that leaves the source must eventually get
   to the sink". Turn a tap on at the problem, see how much water reaches each
   product.

```
W(vᵢ) = Σ f(k,i)
```

The weight of a product is the total flow into it.

**Note carefully: no reasoner and no SPARQL anywhere.** An ontology paper that
never actually reasons. The semantics sit in the graph structure and the scoring
is a classical algorithm on top.

### Their results

Ten products with flow weights from their Table 2:

| Rank | Product | Weight |
|---|---|---|
| 1 | 8 | **0.70** |
| 2 | 7 | 0.60 |
| 3 | 9 | 0.60 |
| 4 | 4 | 0.58 |
| 5 | 3 | 0.53 |
| 6 | 5 | 0.52 |
| 7 | 2 | 0.45 |
| 8 | 1 | 0.38 |
| 9 | 10 | 0.37 |
| 10 | 6 | 0.32 |

They add a cut-off called **alpha**: only products above it get recommended. Set
alpha low and you recommend everything, catching all the good ones and a lot of
rubbish, which is high recall and low precision. Set it high and the opposite.
So they use **F-measure**, which balances both, and run an experiment to pick
the alpha that maximises it.

### The eight-step checklist, which is what we take

| Task | Produces |
|---|---|
| 1 | A glossary of terms: every term, its definition, its synonyms and acronyms |
| 2 | Concept taxonomies |
| 3 | Relation diagrams, including links to other ontologies |
| 4 | A concept dictionary: instances, attributes, relations per concept |
| 5 | A description of every binary relation |
| 6 | A description of every instance attribute |
| 7 | A description of every class attribute |
| 8 | A constants table |

This is METHONTOLOGY whether they name it or not. **Task 1 alone fixes a real
problem in our data**: our benefits column has "Hydrating" and "Hydration" as
two separate strings.

### How we use it

| We take | Why |
|---|---|
| The eight-step checklist | It is a literal to-do list for building the ontology properly |
| `ContextualFeatures` | Price and place describe a product *as sold somewhere*, not the product itself. Our `price_tier`, `sold_by_shops`, `country` and `source_category` all belong there |
| Reporting how a threshold was chosen | Rather than asserting a cut-off, show the experiment |
| The tree makes vagueness usable | If someone says "marks on my face", our concern hierarchy narrows it before we ask anything |

| We leave | Why |
|---|---|
| Ford-Fulkerson | Our products already carry availability, price and evidence level, so a weighted filter does the same work with less machinery |
| The conversational questioning | It needs a hand-built case base and a dermatologist. We have neither, and our contribution is the product side |

### Their weak point

Ingredients are `hasIngredients` and `hasIngValue`, free text and a number, with
nothing behind them. **Nothing in their model can say an ingredient is
regulated.** Ours can, for 99.2 percent of products with a formula.

Also: no dataset size, no product count, no baseline, and a claim to be "more
accurate than the other related works" with no comparison table anywhere.

**One oddity worth knowing.** Page one contains a whole paragraph about
recognising handwritten Chinese calligraphy. It has nothing to do with skincare
and looks like text pasted in and never removed. It tells you how carefully the
journal reviewed it.

### The outside-the-box idea

Their throwaway `Season` class. Beirut summer is humid and coastal, winter is
dry. A gel cleanser right for August is wrong in January. **Nobody in the entire
review models climate, and Lebanon has a genuinely seasonal skin problem.** A
Season and Climate axis over our existing product types costs almost nothing and
a Lebanese pharmacy chain would understand it instantly.

---

## B2. OntoCosmetic: Serna et al. (2021) and Gabriel et al. (2023)

### Say this

> This is the only cosmetics ontology in the literature you can actually
> download. But it is built for the wrong user. It helps a chemist design a
> cream that does not separate, using classes like droplet size and rheology.
> It cannot help a person choose a product in a pharmacy. We take their
> ingredient function names and their idea of recording where each rule came
> from, and we leave the entire chemistry branch.

### The facts

| | |
|---|---|
| Paper 1 | Serna et al., "Towards an ontology-based decision support system for the design of emulsion-based cosmetic products", 13th European Congress of Chemical Engineering, 2021. HAL hal-04674074 |
| Paper 2 | Gabriel et al., "Decision making software for cosmetic product design based on an ontology", ESCAPE-33, pages 1987 to 1992, 2023. DOI 10.1016/B978-0-443-15274-0.50316-4 |
| Institutions | Université de Lorraine, France, with Universidad Nacional de Colombia |
| Downloadable | **YES.** `purl.org/ontocosmetic` |
| I read | Both PDFs plus the OWL file itself |

### What is in the file, counted not quoted

| | |
|---|---|
| Classes | 116 |
| Object properties | 26 |
| Data properties | 20 |
| Individuals | 279 |

Representative classes: `HLB`, `DropletSize`, `Rheology`, `AqueousThickeners`,
`OWCosmeticEmulsion`, `HeuristicForSurfactant`, `MeltingPoint`,
`Emollient_Dosage`.

**HLB** means hydrophilic-lipophilic balance, a number describing how much an
emulsifier prefers water or oil. **Rheology** is how a substance flows. If they
ask what these are, that is the answer, and the point is that manufacturers
never publish any of it.

### Paper 1: how they built the knowledge base

Four kinds of material, combined deliberately:

| Building block | Holds | Their example |
|---|---|---|
| General subproblems | physical properties to promote or limit | achieving shear thinning behaviour |
| General solution strategies | a route to a goal, not tied to a compound | implementing a steric surfactant system |
| Ingredient databases | typed by function | emollients, surfactants, preservatives, actives |
| Heuristics | rules connecting ingredients to the above | |

The heuristics are written as **SWRL rules inside Protégé**, each carrying
`hasHeuristicHighThreshold`, `hasHeuristicLowThreshold` and
**`hasHeuristicSource`**.

**That last property is the one to point at.** It records where each rule came
from. That is provenance applied to rules rather than to facts, and nobody else
in the review does it.

### Paper 2: the application

They turned it into a phone app called Formultools, and that paper is more
rigorous than the first:

| Step | What they did |
|---|---|
| Design method | five planes user-centred design, Garrett 2011 |
| Who was involved | co-design between cosmetics experts and computer scientists |
| How it developed | iteratively, with usability tests between rounds |
| How each round was measured | the **AttrakDiff** questionnaire, a standard user experience instrument |
| When they stopped | when non-expert testers stopped finding problems |

The app does three things: screen ingredients by property, select ingredients
against several criteria at once, and check a proposed formula against the
heuristics. They cite the **Analytic Hierarchy Process** (Saaty, 1987) for
handling several criteria together.

### How they populated it

**By hand, by experts. 279 individuals typed in.** No mapping, no scraping, no
automation. That is fine at 279 and impossible at 12,629, which is exactly the
difference between their project and ours.

### Their evaluation

Neither paper evaluates against ground truth. Paper 1 is a case study, the
design of a moisturising cream. Paper 2 states in its own conclusion that
testing with experts was still future work.

**So the most technically serious cosmetics ontology in the literature was never
validated with experts.** That belongs in our gap analysis.

### How we use it

| We take | Why |
|---|---|
| The ingredient type names: Emollient, Surfactant, Thickener, Active, Preservative, UvFilter, Humectant, Antioxidant, Stabilizer, PHRegulator | We hold ingredient functions from CosIng on 92.7 percent of products. Though since CosIng is the Commission and OntoCosmetic is secondary, taking names straight from CosIng is the cleaner argument, and we note the alignment |
| Splitting product properties from ingredient properties | `spf` and `size_ml` belong to the product. Function and restriction belong to the ingredient and are inherited from the register |
| `hasOrigin`, natural or synthetic | Consumers ask constantly. Our `free_from` is a crude version |
| `hasHeuristicSource` | Provenance on rules, not just on facts |
| SWRL for what OWL cannot say | Their formulation heuristics are structurally identical to our concern rules |

| We leave | Why |
|---|---|
| The whole emulsion chemistry branch | HLB, droplet size, rheology, dosage. Manufacturers never publish it |
| Importing the file | 116 classes to use ten of them |

### The outside-the-box idea

Invert their direction. They answer "given a goal, what goes in the cream". We
can answer **"given what is in the cream, what was the formulator trying to
do"**. We have 295,991 ingredient mentions with functions attached.
Co-occurrence across 11,802 formulas would let us infer formulation strategies
from the market rather than from a textbook, then check them against their
heuristics. That is a paper on its own, and it uses their ontology as the
evaluation target rather than as an import.

---

## B3. Hansanie and Silva (2024)

### Say this

> They combined a neural network with an ontology. A photo of your face goes to
> a network which grades how severe your acne is, that grade is written into the
> ontology as a fact about you, and then the ontology picks the products. The
> important design choice is that they split the ontology into three separate
> files and merged them, because the three parts change at completely different
> speeds. We are copying that structure exactly.

### The facts

| | |
|---|---|
| Authors | Maduri Hansanie and Thushari Silva, University of Moratuwa, Sri Lanka |
| Published | IEEE International Conference on Image Processing and Robotics, 2024 |
| DOI | 10.1109/ICIPRoB62548.2024.10543444 |
| Cited | 2 times |
| Downloadable | No link given |
| I read | The full PDF |

### How they got their vocabulary

They started from people, not from a spreadsheet.

| Step | What they did |
|---|---|
| 1 | Interviewed dermatologists and health professionals |
| 2 | Surveyed 21 people aged 21 to 30 about routines and buying habits |
| 3 | Wrote the results into a spreadsheet |
| 4 | Turned the spreadsheet into classes, working **top down** |
| 5 | Split the result into three ontologies rather than one |

### The three-file design, which is what we copy

| File | Holds | How fast it changes |
|---|---|---|
| Skincare concepts | skin types, concerns, what suits what | barely ever |
| Product information | products and their ingredients | weekly |
| User profile | the person, allergies, ratings | per user |

Then merged into one, and checked with the **Pellet** reasoner.

**Why this matters to us.** We can hand a dermatologist one small file instead
of 12,629 rows. And when the market changes we rebuild one part without touching
the others.

### Their properties, exactly as printed

| Property | From | To | Means |
|---|---|---|---|
| `suitableFor` | TreatmentProduct, e.g. AcneControlCleanser | SkinType, e.g. OilySkin | this product suits this skin |
| `hasKeyIngredient` | TreatmentProduct | KeyIngredient, e.g. SalicylicAcid | what is in it |
| `hasProductRecommendation` | TreatmentProduct | ProductRecommendation | a user rated it |
| `hasAge`, `hasGender` | Person | a number, a word | who the user is |
| `hasRating` | ProductRecommendation | a number | the score they gave |

### Their tools

**Protégé** to build it, **Pellet** to reason, **Owlready2** to query it from
Python, **Tkinter** for the desktop window.

### How the recommendation happens

The photo goes to the **CNN**, a convolutional neural network, which is a model
that reads images. It outputs an acne severity grade. That grade is asserted
into the ontology as a fact about the user. Pellet classifies. Owlready2 pulls
the answer out.

**The image model and the knowledge stay separate**, which means either could be
replaced without touching the other.

### Their evaluation, and how to quote it correctly

| Measured | Number |
|---|---|
| CNN accuracy grading acne severity | **77.5 percent** |
| Survey participants satisfied with the products shown | **87.5 percent** of 24 people |

**The headline in the paper is 87.5, and that is user satisfaction, not system
accuracy.** The model itself scored 77.5. There is no baseline and no test set
of correct recommendations, so the 87.5 is an opinion poll on 24 people.

Quoting that correctly in our thesis is itself a small mark of quality. Say it
that way and it shows you read carefully.

### How we use it

| We take | Why |
|---|---|
| Three ontologies merged | The three parts change at different speeds |
| A reasoner from day one | We have spent months finding faults that produced plausible wrong answers instead of errors. A reasoner complains loudly, which is what we have been missing |
| Ratings held inside the ontology | A rating becomes a fact about a product with a person attached, not a table to remember to join |
| Owlready2 | Our whole pipeline is Python |

| We leave | Why |
|---|---|
| The CNN | No facial photographs, no ethical approval to collect any, and our contribution is the product side. Their layered design means it could be added later |

**The thing they did that we have not.** They consulted dermatologists. Our skin
type and concern vocabulary came from what retailers publish, checked against the
formula. **Nobody clinical has reviewed it.** Say this before they ask, because
it makes you look honest rather than caught out. Then say the fix: aligning our
concerns to DermO, which dermatologists built.

### The outside-the-box idea

Their architecture has an empty socket where the sensor plugs in. They put a
camera in it. **We could put a barcode in it.** A shopper in a Beirut pharmacy
scans the box and asks "does this suit me, and is it cheaper next door". That
uses our price and availability columns, which no other paper has, and it needs
no ethical approval and no image dataset.

---

## B4. Abesova, Hajkova, Ramadan and Zdych (2023)

### Say this

> This is a student project, not a peer reviewed paper, and I say so when I cite
> it. But it contains the single most important idea in the whole review. They
> never tag a product as suitable for oily skin. They write down what the phrase
> means and let the reasoner work out which products qualify. That one idea is
> the difference between an ontology and a spreadsheet.

### The facts

| | |
|---|---|
| Authors | Sara Abesová, Karolína Hajková, Yozlem Ramadan, Małgorzata Zdych |
| What it is | A Knowledge and Data course project, Vrije Universiteit Amsterdam, Group 31, 2023 |
| Peer reviewed | **No. It is a student project.** Say this when citing |
| Downloadable | Not stated |
| I read | The full PDF |

### Their data

Sephora product and review data scraped to CSV, a second CSV of countries with
Sephora shops, and DBpedia.

### Their method: middle out

They name it. **Middle out** means starting with the concepts you are sure of
and working outward in both directions.

| Step | What happened |
|---|---|
| 1 | One team member built a base ontology with the main classes |
| 2 | A Sephora review CSV was found, which widened the scope and forced new classes |
| 3 | Classes and properties added to fit the new data |
| 4 | A second CSV, on countries, folded in the same way |
| 5 | More properties added to join the two sources |

They describe it as iterative. **That matches our situation exactly.** We did
not know our final columns when we started either, and our scope widened when
the Lebanese origin products arrived.

**Size:** 36 classes, 6 object properties, 6 data properties. Small, and it
still does something.

### Their classes

| Class | Values |
|---|---|
| `Category` | Cleanser, Moisturizer, Treatment. Treatment splits into Exfoliant (Chemical, Physical), Serum, Toner. SPF sits under Moisturizer |
| `Product` | four subclasses: Oily, Dry, Normal, Combination Skin Products |
| `Skin Type` | Oily, Dry, Normal, Combination |
| `Skin Tone` | Porcelain, Fair, Light, Medium, Olive, Tan, Deep, Dark, Ebony |
| `Brand`, `Country`, `Rating Stars`, `Review Id` | |

Object properties: `hasBrand`, `hasCategory`, `hasSkinType`, `hasSkinTone`,
`aboutProduct`, `hasReviewId`.

Data properties: `hasRating`, `hasOilyScore`, `hasDryScore`, `hasNormalScore`,
`hasCombinationScore`, `hasSephoraWebPage`.

### How they populated it, which is the most reusable part

| Tool | Used for |
|---|---|
| **OntoRefine** | turning the scraped CSV into RDF by mapping columns to classes |
| **GraphDB** | holding the graph and running the queries |
| **DBpedia** | via an external SPARQL endpoint. `dbr:Czech_Republic` gave them the country and the latitude and longitude of its capital, for a map |
| **SPARQL** | the recommendation itself is a set of queries, not code |

**The DBpedia step is the one to notice.** They did not type country data. They
linked to something that already had it and got map coordinates free. That is
what vocabulary reuse looks like in practice rather than in theory.

### The defined class, explained properly

They do not write "suits oily skin" on four thousand rows. They write:

```
Oily Skin Products  is equivalent to  hasOilyScore value 5
```

One line. The reasoner then finds every product that qualifies.

| Without it | With it |
|---|---|
| I tag 4,000 rows by hand | I write the rule once |
| If a formula is corrected, the tag stays wrong until I remember to fix it | Membership recalculates itself |
| A reviewer has to trust my tagging | A reviewer reads one line and checks it |

**This is the answer to "why not just use a spreadsheet".** A spreadsheet can
filter. It cannot hold a definition.

Three defined classes are already written into our
`vocabularies/skincare-profile.ttl`: `SensitiveSafeProduct`,
`AvailableInLebanon`, `ManufacturerStatedProduct`.

### Their results and their three limitations

Output is nine recommended products for one user, three per category, plus the
Sephora page for that country. No accuracy, no precision, no user study. They
admit the interface was rushed and shows raw web addresses instead of product
names.

**Their three stated limitations, and two of them are our opening:**

| Their limitation | What it means for us |
|---|---|
| 1. Every product in `Oily Skin Products` has a rating of exactly 5.0, so there is no way to rank inside the class. The same top three come out every time | A defined class puts products in a set but does not order them. We need a separate ranking signal, and availability and price in Lebanon are ours |
| 2. A product with one 1.0 review can be recommended ahead of products known to score 5.0, because the two selection paths are not comparable | Thin evidence beating strong evidence. Our evidence levels exist precisely so a claim with one weak source is not treated as equal to a manufacturer statement |
| 3. **"class restrictions based on ingredients could be developed. This would ensure a more symbolic and chemical approach, compared to the statistical one that is currently employed"** | **This is our contribution, written as future work in their paper** |

**Limitation 3 is the single best sentence in the entire review.** Their classes
rest on review scores. Ours rest on the formula, checked against the EU
register. The gap they name is the gap our dataset fills. Say this in the
meeting.

### The outside-the-box idea, worked through properly

They pulled *place* out of DBpedia and got a map for free. We can do the same
trick with **who owns which brand**, out of Wikidata.

#### What Wikidata is

Wikidata is Wikipedia's data, stored as a graph anyone can query. It already
knows that CeraVe is owned by L'Oréal, that L'Oréal is a French company, when
it was founded, and so on. Somebody else maintains all of that. It is free, it
is public, and it has a SPARQL endpoint.

#### The mechanism, in three steps

**Step 1. Say which Wikidata entity each of our brands is.**

One line per brand. `Q1806393` is Wikidata's identifier for CeraVe.

```turtle
skc:brand/CeraVe  owl:sameAs  wd:Q1806393 .
skc:brand/Vichy   owl:sameAs  wd:Q3557584 .
```

`owl:sameAs` means "these two names refer to the same real thing". It is the
standard way of saying it.

**Step 2. Ask Wikidata who owns them.**

Wikidata has a property `P749` meaning "parent organisation". We ask their
endpoint, not our own data:

```sparql
SELECT ?brand ?parentLabel WHERE {
  ?brand wdt:P749 ?parent .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
```

**Step 3. Pull the answer back into our graph.**

Now every product in our dataset carries a parent company, and **we typed none
of it**. That is the whole point of linking rather than copying.

#### The real example, from our own data

I ran this on `SKINCARE_FINAL.csv`. Nine of our brands belong to L'Oréal:

| Brand | Products in our dataset |
|---|---|
| La Roche-Posay | 154 |
| Garnier | 120 |
| Kiehl's | 67 |
| Vichy | 62 |
| SkinCeuticals | 61 |
| CeraVe | 45 |
| Lancôme | 41 |
| L'Oréal Paris | 19 |
| Decléor | 1 |
| **Total** | **570 products** |

Same for other groups: Kenvue owns 215 of our products through Neutrogena,
Aveeno and Clean & Clear. Unilever owns 213 through Dove, Simple, Vaseline,
Paula's Choice and Dermalogica. Beiersdorf owns 145 through Nivea, Eucerin and
Aquaphor.

**The number that makes the point.** Our dataset holds **118 L'Oréal-owned
products that contain niacinamide and are sold in Lebanon.** Their prices run
from:

| | |
|---|---|
| Cheapest | **Vichy Quenching Mineral Mask, $0.51** |
| Dearest | **SkinCeuticals Resveratrol B E Antioxidant Night Serum, $185.58** |

That is a **364 times** price range, for the same active ingredient, from the
same parent company, on shelves in the same city.

#### The three questions this answers

**One. Is there a cheaper equivalent?**

A shopper looks at a $60 SkinCeuticals serum. The system can now say: the same
company makes a CeraVe product with the same active ingredient for a fraction
of that, and here is the shop. **That is the question a Lebanese shopper in a
currency crisis actually asks**, and no cosmetics system in the review can
answer it, because none of them knows who owns whom.

**Two. How concentrated is the Lebanese market really?**

We can say we have 1,463 brands. That sounds like enormous choice. But if a few
multinationals own most of what is actually stocked here, the real choice is
much smaller than the brand count suggests. **That is a finding about the
Lebanese market**, and it comes free from a link.

**Three. Where does what we buy come from?**

Wikidata also holds each company's country. So we could show what share of
skincare on Lebanese shelves is French, American, Korean or locally made. We
have `country` per product already, but company ownership is a different and
more honest picture: a "Korean" brand owned by a French group is a different
fact.

#### Why this is a good idea and not just a nice one

It costs almost nothing. One `owl:sameAs` line per brand, and the brands with
most products are the easy ones to identify. It uses a mechanism a paper in our
own review already demonstrated. And it produces three results that are
interesting to a Lebanese reader specifically, which is exactly the kind of
contribution a local thesis should be looking for.

**The caution.** Wikidata is community-maintained, so ownership can be out of
date or missing for small brands. So we cite Wikidata as the source of that
particular fact rather than asserting it ourselves. Which is, conveniently,
exactly what our evidence-level design is built to do.

---

## B5. The Indonesian paper (2025)

### Say this

> This is our closest competitor and I want to be upfront that I only have the
> abstract so far. They scraped Skinsort, the same global source we used, plus
> two Indonesian shops, and built a skincare ontology using METHONTOLOGY with 12
> classes and over 25 properties, covering 3,800 products. We differ on four
> things: our market, our scale, our link to the EU register, and the fact that
> we model price, availability and where each claim came from.

### The facts

| | |
|---|---|
| Title | Personalized Skincare Recommendation System Based on Ontology and User Preferences |
| Published | *bit-Tech*, Komunitas Dosen Indonesia, 2025 |
| Link | jurnal.kdi.or.id/index.php/bt/article/view/2857 |
| I read | **Only the abstract and the publisher page. I still need the full PDF** |

### What they built

| | |
|---|---|
| Method | **METHONTOLOGY**, named explicitly |
| Classes | **12**: User, Product, Brand, Product Category, Allergen Type, Ingredient, Benefit, Formulation Trait, Key Ingredient, Skin Concern, Skin Type, What It Does |
| Object properties | more than 25 |
| Products | over 3,800 |
| Ingredients | over 28,000 |
| Sources | Sociolla, Beautyhaul, **Skinsort** |
| Querying | **Apache Jena Fuseki** with SPARQL |

Note how close their class list is to our column list. Benefit, Skin Concern,
Skin Type, Key Ingredient, Allergen Type are all columns we already have.

### Where we differ, and we need all four

| Them | Us |
|---|---|
| Indonesian market | **Lebanese market**, six local retailers plus local manufacturers |
| 3,800 products | **12,629** products |
| `Allergen Type` as their own class, presumably hand curated | The **EU 26 declarable allergens** plus the full CosIng register, 28,573 official entries, matched on 96.6 percent of 295,991 ingredient mentions |
| No price or availability mentioned | **Price in two currencies, per shop, with the date seen** |
| No provenance mentioned | **Four evidence levels on every claim** |

**Our one-sentence difference:** they model what a product is; we model what a
product is, whether you can buy it where you live, what it costs there today,
and how much each of those claims is worth.

### The outside-the-box idea

They split `Formulation Trait` from `What It Does`, and we would not have
thought of that. `What It Does` is the marketing claim. `Formulation Trait` is
the physical property. **That split is our evidence problem in class form**: one
is asserted by a seller, the other is derivable from the formula. If we adopt
their two names and attach our evidence levels to the first and our CosIng
derivation to the second, we get a model that states openly which half of a
product description is advertising.

---

## B6. TOXIN knowledge graph (2025)

### Say this

> This is the strongest paper in my whole review by venue, published in an
> Oxford journal. It is a knowledge graph of cosmetic ingredient safety built
> from the official EU safety opinions, so it proves that putting cosmetic
> regulation into a graph is established practice, not something I invented.
> But it has no products in it at all. It has all the law and nothing you can
> buy. That is exactly the space we occupy.

### The facts

| | |
|---|---|
| Authors | Sepehri et al., Vrije Universiteit Brussel |
| Published | *Database: The Journal of Biological Databases and Curation*, Oxford University Press, **2025** |
| DOI | 10.1093/database/baae121 |
| Live at | toxin-search.netlify.app |
| Cited | 4 times |
| I read | The full article text |

*Note: I originally recorded this as 2024. It is 2025. I corrected it and I say
so rather than fixing it quietly.*

### Their data

Safety data on annexed cosmetic ingredients, from **SCCS scientific opinions
issued between 2009 and 2019**. That is the same committee whose opinions sit
behind the CosIng annexes we already use.

Loaded with 88 ingredients, of which 53 affect at least one liver toxicity
measure in a 90-day study.

### Their technique, which is a roadmap we can copy line by line

| What they did | Why it matters to us |
|---|---|
| Toxicologists transcribe into Excel. Computer scientists have read-only access and generate the RDF | A clean separation between the domain expert and the graph builder |
| **Excel to RDF using R2RML** | Exactly the step we have not done yet. A declarative mapping, not a script |
| Reuse **TXPO**, the ToXic Process Ontology, from the OBO Foundry | They reused a domain ontology instead of inventing one. TXPO itself pulls in Gene Ontology, ChEBI, Disease Ontology |
| External data linked by **IRI**, giving a distributed graph | They point at other people's identifiers rather than copying data |
| **Named graphs** so that, in their words, users can "easily manage and trace the origins of the information" | **This is our evidence level idea, at the storage layer.** One box per source |
| Automatic integration by comparing labels and IRIs | The same matching problem we solved with token coverage and a synonym map |
| **SMILES** added to standardise chemical identity | The chemistry equivalent of CAS numbers, which we already have from CosIng |

**SMILES** is a text way of writing a molecule's structure, so if they ask, that
is the answer.

### How we use it

| We take | Why |
|---|---|
| **R2RML or RML for population** | The single most important technical decision in our build, and a peer reviewed cosmetics project in a real journal did it this way |
| **Named graphs per source** | `graph:skinsort`, `graph:lb-retail`, `graph:lb-origin`, `graph:cosing`, `graph:inferred`. Reload one without touching the others, and query only sources you trust |
| Linking out by IRI rather than copying | Our CosIng entries should point at Commission identifiers, not duplicate them |
| The citation itself | It lets us argue that cosmetic regulatory data in RDF is established practice with a peer reviewed precedent |

| We leave | Why |
|---|---|
| The toxicology depth: liver mechanisms, KEGG and Reactome pathways, gene products | We model consumer products, not mechanisms of harm |

### The outside-the-box idea

They model the **evidence behind a restriction**. We model only the restriction
itself, as a pointer like `Annex V/29`. If we link our `restricted_ingredients`
to their layer, a product on a Beirut shelf carries a traceable path all the way
to the SCCS opinion that limits phenoxyethanol to one percent. **No consumer
facing system anywhere does that**, and the link is one `owl:sameAs` per
ingredient.

---

## B7. CosIng-KG (biobricks-ai)

### Say this

> This is not a paper, it is a GitHub project. Somebody has already converted
> the EU CosIng register into the exact graph format we need. Before I write a
> single line of ontology I am going to check whether it is usable. If it is,
> our whole ingredient layer is free and we cite them. If it is not, our own
> conversion becomes something we can claim.

### The facts

| | |
|---|---|
| What | The European Commission CosIng database converted to RDF |
| Where | github.com/biobricks-ai/cosing-kg |
| Serves | kg.toxindex.com |
| I read | Only the repository page |

### Why it matters

Both outcomes are good, which is why it is the highest value half hour available
right now.

- **If usable:** we reuse it, cite it, and link our products to their ingredient
  identifiers. Sprint 3 halves.
- **If not usable:** we say why in the thesis, and our own conversion becomes a
  stated contribution rather than an assumption.

**This is an action item before the ontology chapter is written.**

---

## B8. DermO (2016)

### Say this

> This is a medical ontology of skin diseases, built by hand by dermatologists,
> with over three thousand terms lined up with ICD-10 and published openly on
> BioPortal. It has nothing to do with products. But it fixes the one weakness
> in our work that nobody has raised yet: our list of skin concerns is words we
> invented and no clinician has ever checked them. We cannot get a dermatologist
> quickly, but we can align to one that dermatologists already built.

### The facts

| | |
|---|---|
| Published | Journal of Biomedical Semantics, 2016 |
| DOI | 10.1186/s13326-016-0085-x |
| Institution | University of Birmingham |
| Downloadable | **Yes.** GitHub plus BioPortal, in both OBO and OWL 2 formats |
| Size | Over 3,000 terms in 20 upper-level categories |
| Built by | Domain experts, manually |
| Aligned to | **ICD-10**, the international disease classification |
| I read | The abstract and the BioPortal record |

### Why a disease ontology matters to a product thesis

Our concerns column holds acne, dryness, redness, hyperpigmentation. Those are
clinical concepts with existing, expert-built, published identifiers. Right now
they are free text we invented.

| If concerns stay strings | If concerns link to DermO |
|---|---|
| "acne" means whatever we meant | it means an entity a dermatologist can check |
| our vocabulary is ours alone | it is aligned to ICD-10 through DermO |
| a clinician cannot review it | a clinician recognises every term |
| no route into medical literature | a route into biomedical resources |

### What they actually did, step by step

It helps to know how DermO was made, because it is the opposite of how we made
our vocabulary, and that contrast is the whole point.

**They started with dermatologists, not with data.** A group at the University
of Birmingham sat down with clinicians and wrote out the names of skin
diseases. By hand. No scraping, no machine learning. Over 3,000 terms.

**They organised the diseases by their real features, not by name.** Every
disease is filed under a small number of headings, using things like:

| They classify by | Meaning |
|---|---|
| **Anatomical location** | where on the body it happens |
| **Heritability** | whether it runs in families |
| **Affected cell or tissue type** | what part of the skin it involves |
| **Aetiology** | what causes it |

That gives 20 top-level categories with everything else underneath.

**They lined it up with ICD-10.** ICD-10 is the World Health Organization's
international list of diseases, the one hospitals and insurers use everywhere.
So a DermO term is not just a word somebody liked. It connects to the code a
doctor would write on a file.

**They published it properly.** On GitHub and on BioPortal, which is the main
public home for biomedical ontologies, in two formats so anyone can use it. It
is free.

**And they connected it to other medical ontologies**, so it sits inside a whole
network of disease and symptom vocabularies rather than standing alone.

### Why this matters to us more than I first realised

I looked again at our own `concerns` column. It holds six values and **every one
of them names a real disease or a real skin state**:

| Our concern | Products | Is it a real clinical entity |
|---|---|---|
| May Worsen Eczema | 6,901 | **Yes.** Eczema is a diagnosed condition with ICD-10 codes |
| May Worsen Rosacea | 5,871 | **Yes.** Also a diagnosed condition |
| May Worsen Irritation | 5,819 | Yes, contact irritation is clinical |
| May Worsen Oily Skin | 5,514 | A skin state rather than a disease |
| May Worsen Dryness | 4,549 | Clinically, xerosis |
| May Trigger Acne | 4,261 | **Yes.** Acne vulgaris, with ICD-10 codes |

**So we are already making medical statements and we did not fully notice.**
"This product may worsen eczema" is a claim about a disease. We derived it from
the formula ourselves, using our own rules, and no clinician has ever checked
either the rule or the wording.

That is a genuine weakness, and a supervisor could reasonably raise it.

### How we use DermO, in three steps

**Step 1. Point each of our concerns at the matching DermO term.**

Six lines. That is the whole job.

```turtle
skc:MayWorsenEczema   skc:aboutCondition  dermo:Eczema .
skc:MayTriggerAcne    skc:aboutCondition  dermo:AcneVulgaris .
skc:MayWorsenRosacea  skc:aboutCondition  dermo:Rosacea .
```

**Step 2. Say what kind of link it is.** Our concern is not the disease. It is a
statement *about* the disease, so we point at it rather than claiming to be it.
This is the honest modelling choice and it is worth saying out loud.

**Step 3. Inherit everything DermO already knows.** Once linked, our products
connect through DermO to ICD-10, to the body site, and to the wider network of
medical vocabularies. **We wrote six lines and got all of that.**

### What it buys us

| Before | After |
|---|---|
| "Eczema" means whatever we meant by it | It means a specific entity a dermatologist recognises |
| Our vocabulary is ours alone | Our vocabulary reaches ICD-10, which every clinician uses |
| No doctor could review our concerns | A doctor opens DermO and checks every term in minutes |
| Our medical claims rest on our own authority | They rest on an ontology built by clinicians and published in a peer reviewed journal |

**This is the fix for the weakness in B3.** Hansanie and Silva interviewed
dermatologists and we did not. We cannot get a dermatologist quickly. But we can
align to one that dermatologists already built, and say so.

### The outside-the-box idea: body site

Here is the part nobody in cosmetics has done.

DermO knows **where on the body** each disease happens. Our product types
already imply a body site, but only as retail labels with no meaning behind
them. Counting our own data:

| Body site | Our products | Which types |
|---|---|---|
| Eye area | **637** | Eye Moisturizer 597, Eye Mask 40 |
| Lips | **550** | Lip Moisturizer 509, Lip Mask 41 |
| Body | **676** | Bath & Body |
| Hands | **62** | Hand Care |
| Face, general | the remaining ~10,700 | cleansers, serums, moisturisers, masks |

Right now "Eye Moisturizer" is just a shop category. If we connect it to an
actual anatomical entity through DermO, three things become possible that a
retail taxonomy cannot do.

**One. Ask a question about a place, not a category.** "Show me everything for
the eye area" currently means matching two product type strings and hoping we
guessed them all. With a body site linked properly, the reasoner finds them,
including any type we add later, without us updating a list.

**Two. Find the gap in a routine.** A person buys a cleanser, a serum and a
moisturiser. All face. The system can say: **you have nothing for the eye area
and nothing for your lips.** That is a genuinely useful thing to tell somebody,
and it is impossible without knowing that products occupy places on a body.

**Three. Catch a site mismatch.** A product intended for the body carrying a
concern that belongs to a facial condition is worth flagging. Right now nothing
in our data would notice.

**Nobody in cosmetics modelling connects a product to a body site through a
clinical ontology.** Every system reviewed treats product type as a flat shop
category. Six lines of linking plus a body site property turns it into anatomy.

### Say this if it comes up

> Our concerns column already makes medical statements. It says a product may
> worsen eczema or trigger acne, and those are real diagnosed conditions. We
> derived those from the formula with our own rules and no clinician has
> reviewed them. DermO is 3,000 skin disease terms written by dermatologists,
> organised by body site and cause, aligned to ICD-10 and published free on
> BioPortal. Six lines of alignment give our vocabulary clinical standing that
> we could not otherwise obtain, and open up a body site dimension that no
> cosmetics system has.

---

## B9. D3X (2024)

### Say this

> A dermatology ontology linking dermoscopic patterns to diagnoses, published in
> a proper medical informatics journal last year. I include it for one reason:
> its evaluation design. Ontologies in this area are judged by expert review and
> usability studies, not by precision and recall. Knowing that stops me
> promising an evaluation I cannot deliver.

### The facts

| | |
|---|---|
| Title | Dermoscopy Differential Diagnosis Explorer (D3X) Ontology |
| Published | JMIR Medical Informatics, 12:e49613, 2024 |
| I read | The abstract |

### What we take

The **evaluation design**. Competency questions plus a usability study, not
accuracy figures. That is the shape our evaluation chapter should take, and
being able to point at a 2024 example in a real medical journal justifies it.

---

## B10. The halal flavouring ontology (2024)

### Say this

> This is about food flavourings, not cosmetics, but structurally it is exactly
> our problem. An ingredient has a regulatory status granted by an authority,
> and a product inherits its status from its ingredients. Swap halal
> certification for EU annex restriction and the model is the same shape. I take
> their three-part pattern: ingredient, authority, status, with the authority as
> a thing in its own right.

### The facts

| | |
|---|---|
| Title | Development of Flavouring Ontology for Recommending the Halal Status of Flavours |
| Published | Journal of Information Science Theory and Practice, 12(2), 2024 |
| Where | Malaysia, with domain experts from JAKIM, the Department of Islamic Development |
| I read | The abstract |

### What we take

The **three-part pattern**, with the authority modelled as a first-class entity
rather than an attribute. That lets us say:

> `Phenoxyethanol` has status `RestrictedAnnexV/29` **according to** the
> European Commission

and it leaves room for a second authority later. **For Lebanon that is
realistic**, since local regulation is not identical to EU regulation. One
design choice future-proofs the entire regulatory layer.

### The outside-the-box idea

Lebanon has a Muslim majority and a real halal cosmetics market. Our dataset
holds full INCI lists, and alcohol and animal-derived ingredients are
identifiable from INCI. A halal suitability layer over our formulas would be
commercially meaningful here.

**Be honest though.** A 2025 IEEE Access paper called HaCKG already built a
cosmetics knowledge graph with a neural network for halal prediction. So this is
no longer novel on its own. Our angle is that they *predict* with a model, which
gives a probability and no reason, while we would *derive* from the ingredient
list and cite the derivation.

---

# PART 3. THE COMPARISON AND THE GAP

## The table

| | Moe & Aung 2014 | OntoCosmetic | Hansanie 2024 | Abesova 2023 | Indonesian 2025 | TOXIN 2025 | **US** |
|---|---|---|---|---|---|---|---|
| Peer reviewed | weak venue | yes | yes | **no, student** | yes | yes | to be |
| Ontology downloadable | no | **yes** | no | no | unknown | **yes** | **planned** |
| Named method | 8 tasks, unnamed | none | none | middle out | METHONTOLOGY | none | **MOMo + LOT** |
| Products | never stated | 279 | never stated | Sephora subset | 3,800 | **none** | **12,629** |
| Ingredients tied to a regulator | no | no | no | no | own class | **yes, SCCS** | **yes, CosIng** |
| How data got in | never stated | by hand | never stated | **OntoRefine** | scraping | **R2RML** | **RML** |
| Reasoner | **none** | SWRL | Pellet | class rules | Fuseki | not stated | **HermiT + SHACL** |
| SPARQL | no | no | via Owlready2 | **yes** | **yes** | yes | **yes** |
| Links to outside data | no | no | no | **DBpedia** | no | **IRIs, OBO** | **Wikidata, CosIng, DermO** |
| Records who claimed what | no | rules only | no | no | no | **named graphs** | **4 levels, PROV-O** |
| Price or availability | a class only | a criterion | no | shop link | no | no | **2 currencies, per shop, dated** |
| Local market | no | no | no | no | Indonesia | no | **LEBANON** |
| Tested on ground truth | **no** | **no** | partly | **no** | unclear | n/a | **planned** |

**The row nobody else fills:** regulator-linked ingredients, plus provenance,
plus availability, plus published. Four cells, one row, one thesis.

## The five gaps

1. **No ingredient layer with legal standing.** Every skincare ontology treats
   ingredients as strings or a small hand-built list. Only TOXIN links to a
   regulator, and TOXIN has no products.
2. **No provenance.** Nobody records who said a claim and how much that source
   is worth. Every claim is presented as equally true.
3. **No availability.** Every system assumes the product can be bought. In
   Lebanon that fails, and it fails differently for a global brand than for a
   local maker.
4. **No evaluation against ground truth.** Two report user satisfaction on small
   samples, one is a case study, one admits expert testing never happened.
5. **Almost nothing is published.** One published ontology out of six. The field
   cannot build on itself.

**We address one, two, three and five directly, and four with competency
questions.**

## The finding that shaped everything

A systematic review of 28 ontology-based recommender systems (Rahayu et al.,
2022, 137 citations) found they *"seldom use the methodology of building
ontologies"* and that *"none of the primary studies described ontology
evaluation methodologies"*.

**None of twenty-eight.** So naming a method and reporting an evaluation is not
tidiness in this field. It is a contribution, and a cheap one.

---

# PART 4. WHAT WE BUILD

## The method

**MOMo** for design, **LOT** for publication. Both are published, both are
evaluated, and together they answer the two questions the Rahayu review says
nobody answers.

## The four modules

| Module | Holds | Changes |
|---|---|---|
| `skincare-core` | skin types, concerns, benefits, ingredient functions, regulatory status | rarely |
| `skincare-product` | Product, Brand, Ingredient, Offer, Shop | with the market |
| `skincare-evidence` | Claim, EvidenceLevel, Source. **The contribution** | our own design |
| `skincare-user` | Person, profile, allergies, needs | future |

Plus `skincare-lb` which imports all four and adds the Lebanon specifics.

## The two modelling decisions to be able to defend

**IngredientListing.** A triple has three slots, so `Product hasIngredient X`
has nowhere to put **the position in the INCI list**. Position is concentration
order, the only concentration signal a consumer ever gets. So we make the
listing its own entity. This is the **n-ary relation design pattern**, and
calling it that shows we know the literature.

**Claim.** Same problem. `Product suitableFor OilySkin` has nowhere to put who
said so. So a Claim is its own entity carrying the source, the exact sentence,
the date and the evidence level, built on PROV-O. We keep the simple triple
alongside it so easy queries stay easy.

## The six defined classes and their predicted sizes

| Defined class | Rule | Expect |
|---|---|---|
| `SensitiveSafeProduct` | no ingredient is a declarable allergen | ~9,537 |
| `AvailableInLebanon` | at least one offer from a Lebanese shop | ~11,937 |
| `ManufacturerStatedProduct` | claim at evidence level 1 | ~4,460 |
| `RegulatedProduct` | at least one restricted ingredient | ~9,613 |
| `FullyIdentifiedProduct` | coverage 100 percent | ~9,032 |
| `NaturalClaimProduct` | marketed as natural, for testing | to measure |

**Predicting the number before running the reasoner and then checking is a real
validation step.** If SensitiveSafeProduct does not come out near 9,537, the
model is wrong and we want to know before publishing.

## The six steps

| Step | What | Why here |
|---|---|---|
| 1 | Write the requirements and 15 competency questions | Everything downstream is checked against them. Three pages, no code |
| 2 | Reuse audit on all 42 columns. Check CosIng-KG, DermO, Wikidata | Could save weeks. Do it before writing any Turtle |
| 3 | Build the four modules, drawing each one first | Diagrams are the figures the chapter needs anyway |
| 4 | YARRRML mapping, Morph-KGC, load as named graphs | This is what makes it a method rather than a script |
| 5 | Defined classes, HermiT, SHACL, OOPS!, FOOPS! | Predict, then check |
| 6 | w3id address, WIDOCO docs, Zenodo DOI, answer every question in SPARQL | The answers are the evaluation chapter |

## The evaluation, four layers, none needing users

| Layer | Method |
|---|---|
| Structural | OOPS!, FOOPS!, OntoMetrics |
| Functional | 15 competency questions as SPARQL queries |
| Logical | HermiT consistency, plus predicted versus actual class sizes |
| Comparative | the table in Part 3 |

## The five contribution claims, ranked by safety

1. Ingredient layer grounded in the EU register, on 12,629 products. **Safest**
2. Provenance as a first-class part of the model. **Strong**
3. Availability and price for a real national market. **Strong and unique**
4. A published, documented, versioned artefact. **Easy and rare**
5. Lebanese consumer needs as entities. **Most original, least certain**

**One to four are safe. Deliver those and the thesis is sound.** Five is what
makes it memorable, so attempt it last.

---

# PART 5. EVERY QUESTION THEY MIGHT ASK

## "Why an ontology and not just the spreadsheet?"

A spreadsheet can filter. It cannot hold a definition. With a defined class I
write "a sensitive-safe product is one with no declarable allergen" once, and
membership recalculates itself whenever a formula is corrected. With a
spreadsheet I tag nine thousand rows by hand and they go stale silently.

An ontology also catches contradictions. We have 593 products marketed as
sensitive-safe that contain one of the EU 26. In a spreadsheet that is a note in
a README. In an ontology it is a formal inconsistency the reasoner finds by
itself.

## "Why not just use deep learning?"

Three reasons.

We have no user interaction data to train on. Our dataset is a product resource,
not an interaction log.

A learned model gives a weight, not a reason. In a domain with physical risk and
a legal framework, a recommendation that cannot say why cannot be audited by a
regulator or used by a pharmacist.

And there is evidence. A 2026 clinical study compared three ways of answering
medical questions: ChatGPT-4 scored 37 percent, another model 52 percent, and
grounding the model in an ontology scored 98 percent, cutting hallucination from
63 percent to under 2.

## "Isn't a Lebanese focus a limitation?"

No, and there is precedent. Lahoud et al. published an ontology recommender
evaluated on Lebanese students in a Springer journal in 2022, with 36 citations.
Beyond that, the local focus is the contribution. Every other system assumes you
can buy what it recommends. In Lebanon that assumption fails, and no dataset
outside ours can test it.

## "You have no users. How can this be a recommender?"

That is a scope statement, not a gap. The main survey of knowledge-graph
recommenders classifies methods for *using* a knowledge graph, and assumes one
already exists for the domain. For skincare in a local market, it does not. This
thesis builds it.

## "How will you evaluate it?"

Four ways, none of which needs users. Structural, using two free scanners.
Functional, by answering fifteen stated questions in SPARQL. Logical, by
predicting how many products fall into each computed class and checking against
the reasoner. Comparative, against the table.

And to justify that choice, a 283-citation ACM Computing Surveys paper argues
the evaluation must match the goal. Our goal is verifiable correctness, not
ranking accuracy, so precision and recall are the wrong instruments.

## "Is any of this actually novel?"

Four things, in order of how safe each claim is. Ingredients tied to the EU
register across 12,629 products, which nobody has done because the one project
with the EU link has no products. Provenance modelled properly. Real market
availability. And a published, documented artefact, which only one in six
competitors manages.

## "Has a dermatologist checked your vocabulary?"

No, and that is the real weakness. Our skin type and concern words came from
what retailers publish, checked against the formula. The fix is to align them to
DermO, which has three thousand terms written by dermatologists and lined up
with ICD-10. If either of you knows a dermatologist or pharmacist who could give
me an hour, that would close it properly.

## "How long will this take?"

Six steps. The first two are writing and checking, no code. Step four is one
mapping file. The riskiest is step five, because the reasoner may find problems,
but finding problems is the point.

## "Why those two methodologies and not METHONTOLOGY?"

METHONTOLOGY is thorough but old and document-heavy. MOMo is modern, evaluated
in a specialist journal, and built around modules and design patterns, which
suits a four-module design. LOT is lightweight and built around two things that
are exactly our two criticisms of the field: reusing published terms rather than
inventing, and actually publishing the result.

## "What if the Indonesian paper already did this?"

They model what a product is. We model what a product is, whether you can buy it
where you live, what it costs there today, and how much each claim is worth.
Their allergen list is their own; ours is the EU register, 28,573 entries. Their
scale is 3,800 products; ours is 12,629. I still need their full PDF before
submission and I have flagged that.

## "What is the weakest part of your plan?"

The fifth contribution, modelling Lebanese consumer needs as entities. It is the
most original idea and the least certain, so I plan to attempt it only after the
four safe ones are delivered.

## "Where is all this written down?"

In the repository, under `literature/`. The README there is the shortest route
in. There is a spreadsheet with all 59 papers, a comparison sheet, the full
ontology design with every class and property, the tool choices, and the
related work chapter already compiling in LaTeX.
