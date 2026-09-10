# -*- coding: utf-8 -*-
"""
The text for the three new tabs. Kept apart from the layout code so I can fix
a sentence without touching the drawing.

Plain words, short sentences, first person.
"""

# ------------------------------------------------------------------- the gap
GAP_COLS = [
    ("#", 5),
    ("Paper", 22),
    ("What they did", 46),
    ("What is missing in it", 46),
    ("What I do instead", 46),
    ("What they have that I do not", 34),
]

GAP = [
 ("A", "Skincare and cosmetics ontologies",
  "My direct competitors. The gap has to be stated against these seven."),

 ("1", "Moe & Aung 2014",
  "Two ontologies, one for cosmetics and one for skin problems. Six questions narrow you "
  "down, then a max-flow algorithm scores what is left.",
  "No reasoner. No SPARQL. No outside data. They never say how many products. Nothing can "
  "be downloaded.",
  "12,629 real products with real prices. A reasoner that runs. Every ingredient tied to "
  "the EU database.",
  "Their question-and-eliminate interaction is better than anything I have. I only have queries."),

 ("2", "OntoCosmetic 2021/23",
  "Helps a chemist formulate a cream. SWRL rules with a high and a low threshold per "
  "ingredient function. Published and downloadable.",
  "It is for the person making the product, not the person buying it. No shopper, no price, "
  "no availability, no skin type.",
  "The same chemistry idea, pointed at the buyer. Their rule shape is what I copy for my "
  "defined classes.",
  "They publish their OWL file at a permanent address and I have not. They also ran user "
  "testing across iterations."),

 ("3", "Hansanie & Silva 2024",
  "A photo goes into a small CNN, the grade comes out, the ontology picks products. Pellet "
  "checks consistency.",
  "The ontology is small and never released. No SPARQL, no outside data. The CNN does the "
  "work and the ontology is decoration.",
  "No photos. The reasoning is the contribution, not an add-on. My ingredient layer is the "
  "part theirs does not have.",
  "They have a working app with an interface, and 24 people tested it. I have no interface."),

 ("4", "Abesova 2023 (VU)",
  "Student project. Sephora review CSV to RDF with OntoRefine, GraphDB, defined classes "
  "like 'OilyScore = 5', then SPARQL picks 9 products.",
  "Not peer reviewed. It recommends from review scores only and never looks inside the "
  "product. They admit one property was implemented wrong.",
  "The same defined-class method, but driven by ingredients instead of star ratings. That "
  "is their third limitation.",
  "They link to DBpedia for a live map, and they have a working country-to-shop link. My "
  "Lebanon layer does that for one country."),

 ("5", "bit-Tech 2025",
  "METHONTOLOGY, Apache Jena Fuseki, SPARQL with reasoning, about 3,800 products. My "
  "closest competitor on paper.",
  "I only have the abstract. No ingredients, no regulation link, no provenance mentioned.",
  "Ingredients tied to EU law, four levels of evidence, and real shop availability. None of "
  "which they claim.",
  "3,800 products, in a published venue, with a named method, already finished. I need the "
  "full PDF before I can say more."),

 ("6", "Utari 2023",
  "METHONTOLOGY on 62 products, evaluated with SPARQL queries.",
  "62 products is a demonstration, not a system. No tools stated. Nothing downloadable.",
  "12,629 products, and every one has a source and a date.",
  "Nothing I can see."),

 ("7", "Mahadewi 2024",
  "Slope One collaborative filtering, measured with SUS and MAE.",
  "Not an ontology. It needs a ratings matrix, and it cannot explain why it recommended "
  "anything.",
  "Reasoning that can show its working. Cold start is not a problem for me.",
  "Two named evaluation instruments and real numbers. My evaluation is still on paper."),

 ("B", "Ingredients, regulation and skin conditions",
  "Not recommenders. These give my ingredient and concern layers a standing nobody in group A has."),

 ("8", "TOXIN KG 2025",
  "A toxicology graph. R2RML from spreadsheets, TXPO as the ontology, named graphs so every "
  "fact keeps its source.",
  "Toxicology, not cosmetics. No consumer anywhere in it.",
  "I take the named-graph idea. One graph per source: Skinsort, Amazon, the six Lebanese shops.",
  "Their provenance is further along than mine, and they score study reliability automatically."),

 ("9", "HaCKG 2025",
  "A neural graph network that predicts halal status from a knowledge graph.",
  "The reasoning sits inside a neural net, so it cannot explain itself. No rules.",
  "Rules I can print. Anyone can check a single decision by hand.",
  "It beats rule systems on accuracy, and it handles cases no rule covers."),

 ("10", "CosIng-KG",
  "CosIng already turned into RDF and published on GitHub.",
  "Not a paper, and I have not checked yet whether it works.",
  "If it is usable I reuse it and save weeks. If not, I build the ingredient layer myself.",
  "It may already hold a cleaner version of my whole ingredient layer."),

 ("11", "CCIBP 2023",
  "A chemical and biological database of cosmetic ingredients.",
  "A resource, not a system. No recommendation, no consumer.",
  "I use it to cross-check my ingredient names.",
  "Chemoinformatics depth I do not have."),

 ("12", "DermO 2016",
  "3,000 skin disease terms written by dermatologists, on BioPortal.",
  "A terminology. It does not recommend anything.",
  "I align my six concern values to it. Six lines of code, and my medical claims stop being "
  "my own invention.",
  "Clinical authority. Mine is borrowed from them."),

 ("13", "Halal flavouring 2024",
  "Ingredient to status to authority, with the certifying body as a real entity in the graph.",
  "Food, not cosmetics.",
  "I copy that three-part shape for CosIng annex status and for evidence levels.",
  "They consulted the certifying body. I have consulted nobody."),

 ("14", "Klaschka 2015",
  "Counts how many cosmetic ingredients carry hazard classifications under REACH and CLP.",
  "An analysis, not a tool.",
  "It gives me the sentence that justifies why a regulation link matters at all.",
  "Nothing structural."),

 ("15", "MVFM 2026",
  "A framework tested on three products by hand.",
  "Three products. No tools, no ontology file.",
  "Scale, and everything automated.",
  "Nothing."),

 ("C", "Ontology recommenders in other fields",
  "Nobody solved my problems in skincare. People solved them in food and shopping."),

 ("16", "Middleton 2004",
  "The paper that shows an ontology in a recommender is a reasonable choice. ACM TOIS, "
  "thousands of citations.",
  "Academic papers, not products. It predates SPARQL.",
  "I cite it first in the chapter. Its cold-start argument is my cold-start argument.",
  "Real deployments with real users over years. Mine is a dataset."),

 ("17", "FoodKG 2019/21",
  "Recipes, ingredients, nutrition from an authority, allergies as hard constraints. A "
  "SPARQL service on top. Published.",
  "Food. And they have no regulator the way I have CosIng.",
  "Almost the same shape as mine. Recipes are products, nutrition data is CosIng, allergies "
  "are the EU allergen list.",
  "Nearly everything. They publish, they state a maintenance plan, and they built several "
  "applications on one graph. This is my model."),

 ("18", "Di Noia / Ostuni",
  "Similarity computed from links in the graph, not from words. No ratings needed.",
  "Movies. And they say entity matching is the hard part.",
  "I can compute product similarity with no user history, which is my situation.",
  "Offline benchmarks against baselines."),

 ("19", "AliCoCo 2020",
  "Alibaba's own concept net, running at real scale.",
  "Internal, closed, and very large. Nothing reusable.",
  "I work at a size one person can check.",
  "Online metrics from millions of users."),

 ("20", "Guo survey 2022",
  "Surveys knowledge-graph recommenders and sorts them into families.",
  "A survey. Nothing built.",
  "It tells me which family I am in, so I can name it in the chapter.",
  "Nothing."),

 ("21", "E-Prod 2023",
  "Machine learning plus semantic matching, tested on 250+ real users against collaborative "
  "filtering.",
  "General e-commerce. No regulation, no chemistry.",
  "My matching is over ingredients, with a legal backing.",
  "250 real users. That is a proper evaluation and I do not have one."),

 ("22", "Lahoud 2022",
  "Ontology plus case-based reasoning, evaluated on Lebanese students.",
  "Not skincare.",
  "Proof that this kind of work gets done and published in Lebanon.",
  "A comparative evaluation with real local users."),

 ("D", "Evaluation, and the alternative I have to answer",
  "What counts as good, and the deep learning answer to the same problem."),

 ("23", "Rahayu review 2022",
  "Reviews 28 ontology-based recommender studies.",
  "A review.",
  "Its finding is my justification. Not one of the 28 described how it was evaluated. So I "
  "describe mine.",
  "Nothing."),

 ("24", "Tarus 2017",
  "Ontology plus sequential pattern mining for e-learning.",
  "E-learning.",
  "The idea that order matters. My routine_step column is the same instinct.",
  "Experiments against baselines."),

 ("25", "COPPER 2025",
  "Evaluated on three layers: the process against OBO principles, logical consistency, then "
  "competency questions.",
  "Not skincare.",
  "This is the evaluation design I copy. It is the most complete one in my review.",
  "They ran it. I have only planned it."),

 ("26", "FEVR 2022",
  "A framework for how ontology recommenders should be evaluated.",
  "A framework.",
  "It tells me to match the evaluation to the goal, instead of reporting precision by reflex.",
  "Nothing."),

 ("27", "Lee 2024 (lululab)",
  "A deep neural network plus AI skin analysis. No ontology.",
  "It cannot explain a single recommendation. No ingredients, no rules, no regulation.",
  "Everything I do can be inspected. That is the argument.",
  "It works today, at commercial scale, with real customers."),

 ("28", "Ali 2026",
  "An ontology-grounded graph feeding an LLM. Three conditions, the same 60 questions.",
  "Very new. Not skincare.",
  "It shows the ontology stops the model inventing things. This is my future work chapter.",
  "A clean experimental design I should copy."),
]

GAP_SUMMARY = (
 "Everyone recommends from ratings, reviews or photos. Nobody recommends from what is in the "
 "product, tied to the regulator, with a record of where each fact came from, for products you "
 "can really buy.\n\n"
 "Abesova's third limitation says this in their own words: \"class restrictions based on "
 "ingredients could be developed. This would ensure a more symbolic and chemical approach, "
 "compared to the statistical one that is currently employed.\""
)


# ------------------------------------------------------- reasoning and SHACL
REASONING_INTRO = (
 "Reasoning means the machine works something out that I never typed in. There are five ways "
 "to do it and they are not interchangeable. For each one: what it does, an example from my "
 "own data, who in my review uses it, and whether it fits me."
)

REASONING_COLS = [
    ("The technique", 26),
    ("What it does", 44),
    ("Example from my data", 52),
    ("Who in my review uses it", 28),
    ("Fits me", 9),
    ("Why", 44),
]

REASONING = [
 ("H", "1. The five ways to reason"),

 ("RDFS entailment",
  "The cheapest one. If Cleanser is a subclass of Product, then every cleanser is a product.",
  "I say CeraVe Cleanser is a skc:Cleanser. The machine works out it is also a Product. I "
  "never typed that.",
  "Abesova gets this free in GraphDB",
  "yes",
  "Free and always on. But it only does the hierarchy. Nothing clever."),

 ("OWL defined classes",
  "I write the definition of a class, and the reasoner decides who belongs. I never tag "
  "anything by hand.",
  "SensitiveSafeProduct = a Product with no restricted ingredient and no fragrance allergen. "
  "The reasoner finds all the members itself.",
  "Abesova, OntoCosmetic, COPPER",
  "yes",
  "This is my main mechanism. If I add a product tomorrow it lands in the right classes with "
  "no extra work. A database cannot do this."),

 ("SWRL rules",
  "If-then rules bolted onto OWL, for things OWL alone cannot say.",
  "If a product has retinol and an AHA, flag a conflict. OWL alone struggles with rules that "
  "need two variables.",
  "OntoCosmetic, for its thresholds",
  "maybe",
  "Powerful, but it slows the reasoner and only Pellet or Openllet runs it properly. Two "
  "rules at most."),

 ("SPARQL CONSTRUCT",
  "A query that writes new triples instead of returning a table.",
  "Construct a triple saying a product suits winter, by combining occlusive with no drying "
  "alcohol.",
  "Abesova, to build the OilyScore triples",
  "yes",
  "Simple and fast, and I already know SPARQL. But the rules sit in loose .rq files and "
  "nothing checks them."),

 ("SHACL rules (SHACL-AF)",
  "Rules written in the graph, in Turtle, that add new triples. Also the only standard way "
  "to validate.",
  "See section 3 below. This is the one nobody in my review uses.",
  "Nobody. 0 of 28 papers.",
  "yes",
  "Two jobs in one language: catch bad data, and infer new facts. And it is a gap I can claim."),

 ("H", "2. Why OWL and SHACL are not the same thing"),

 ("OWL is open world",
  "If something is not written down, OWL assumes it might still be true. It never complains "
  "about missing data.",
  "I say a product must have one price. A product has two. OWL does not error. It decides "
  "the two prices are the same thing.",
  "Everyone using OWL",
  "yes",
  "Right for inferring. Wrong for checking my data is clean."),

 ("SHACL is closed world",
  "What is not in the graph is treated as false. It reports an error and points at the exact "
  "triple.",
  "Same case. SHACL says 'product X has 2 values for hasPrice, maximum is 1', and names X.",
  "Nobody in my review",
  "yes",
  "This is what I want when validating 12,629 rows. OWL cannot do it."),

 ("The mistake to avoid",
  "People write owl:maxCardinality thinking it is a constraint. It is not. It is an "
  "instruction to infer.",
  "The most common beginner mistake in OWL. Worth one sentence in my chapter.",
  "",
  "",
  "Source: Knublauch, 'SHACL and OWL Compared', spinrdf.org/shacl-and-owl.html"),

 ("H", "3. What SHACL would do in my thesis"),

 ("Job 1. Guard the dataset",
  "Check every product before it enters the graph.",
  "Every product must have at least one ingredient, one price, a country from a fixed list, "
  "and a rating between 0 and 5. Run once, get a report naming every bad row.",
  "", "yes",
  "I have 12,629 rows from eight sources. Something is wrong in there. The report goes in "
  "the appendix as evidence."),

 ("Job 2. Enforce my evidence rule",
  "The rule I keep saying matters. No claim without a source.",
  "Every ingredient with a CosIng annex status must carry prov:wasAttributedTo and a date. "
  "SHACL refuses it otherwise.",
  "", "yes",
  "This turns my provenance design from a promise into something a machine enforces. The "
  "strongest single use for me."),

 ("Job 3. Infer, with sh:TripleRule",
  "Add a triple when a condition holds. The same job as a defined class, but easier to read.",
  "If a product has three or more barrier lipids, add rdf:type BarrierRepairProduct.",
  "", "yes",
  "Compare with OWL. OWL can only ever infer types and sameAs. SHACL can infer any triple."),

 ("Job 4. Count, with sh:SPARQLRule",
  "A rule that does arithmetic and writes the answer back.",
  "Count how many EU-restricted ingredients a product has, and store it as a number I can "
  "sort on.",
  "", "yes",
  "OWL cannot count. This is the honest limit of OWL and the cleanest reason to add SHACL."),

 ("H", "4. How to run it"),

 ("pySHACL",
  "Python. pip install pyshacl, then one line.",
  "pyshacl -s shapes.ttl -f human data.ttl",
  "", "yes",
  "My pipeline is Python and it pairs with RDFLib. The slowest of the three, but my graph is "
  "1.8 million triples, which is small."),

 ("Apache Jena SHACL",
  "Java. The fastest of the three in published benchmarks.",
  "Command line or library. It also reads SHACL-C, a compact syntax that is easier to read "
  "than Turtle.",
  "", "maybe",
  "Benchmarked around four times faster than pySHACL. Only worth it if pySHACL gets slow."),

 ("TopBraid SHACL API",
  "Java, from the people who wrote the spec. The reference implementation.",
  "It defines correct behaviour when the other engines disagree.",
  "", "maybe",
  "Useful to check against if a result looks wrong."),

 ("GraphDB",
  "My triple store has SHACL validation built in.",
  "Turn it on when creating the repository, and bad data is rejected at load time.",
  "", "yes",
  "No extra tooling. This is where I would start."),
]

SHACL_CODE = [
 ("Job 1. Catch bad data. Plain SHACL Core, no extras.", """\
sk:ProductShape
    a sh:NodeShape ;
    sh:targetClass sk:Product ;

    sh:property [                      # must have at least one ingredient
        sh:path sk:hasIngredient ;
        sh:minCount 1 ;
        sh:message "Product has no ingredients at all" ] ;

    sh:property [                      # one price, and not negative
        sh:path sk:priceUSD ;
        sh:maxCount 1 ;
        sh:datatype xsd:decimal ;
        sh:minInclusive 0 ;
        sh:message "Price missing, doubled, or negative" ] ;

    sh:property [                      # rating must be 0 to 5
        sh:path sk:rating ;
        sh:minInclusive 0 ;
        sh:maxInclusive 5 ] ."""),

 ("Job 2. No claim without a source. My provenance rule, enforced.", """\
sk:AnnexClaimShape
    a sh:NodeShape ;
    sh:targetClass sk:AnnexStatusClaim ;

    sh:property [
        sh:path prov:wasAttributedTo ;
        sh:minCount 1 ;
        sh:class sk:Authority ;
        sh:message "A regulatory claim with no authority behind it" ] ;

    sh:property [
        sh:path prov:generatedAtTime ;
        sh:minCount 1 ;
        sh:datatype xsd:date ;
        sh:message "A claim with no date cannot be checked" ] ."""),

 ("Job 3. Infer a new type. sh:TripleRule, from SHACL Advanced Features.", """\
sk:BarrierRepairRule
    a sh:NodeShape ;
    sh:targetClass sk:Product ;
    sh:rule [
        a sh:TripleRule ;
        sh:condition [                       # the if part
            sh:path sk:hasBarrierLipid ;
            sh:minCount 3 ] ;
        sh:subject   sh:this ;               # the then part
        sh:predicate rdf:type ;
        sh:object    sk:BarrierRepairProduct ] ."""),

 ("Job 4. Count something. OWL cannot do this. sh:SPARQLRule.", """\
sk:RestrictedCountRule
    a sh:NodeShape ;
    sh:targetClass sk:Product ;
    sh:rule [
        a sh:SPARQLRule ;
        sh:construct \"\"\"
            CONSTRUCT { $this sk:restrictedCount ?n }
            WHERE {
              { SELECT $this (COUNT(?i) AS ?n) WHERE {
                  $this sk:hasIngredient ?i .
                  ?i    sk:annexStatus  ?s .
                } GROUP BY $this }
            }\"\"\" ;
        sh:prefixes sk: ] ."""),
]

SHACL_SENTENCE = (
 "\"None of the 28 reviewed systems reports any use of SHACL. Validation of the underlying "
 "data, and the enforcement of provenance constraints, are therefore unaddressed in the "
 "existing skincare ontology literature.\"\n\n"
 "That is a small, true, defensible gap claim, and it costs one afternoon of work to earn it."
)


# ------------------------------------------------------------- Abesova paper
ABESOVA_FACTS = [
 ("Full title", "Skincare Ontology, Final Project"),
 ("Who", "Sara Abesova, Karolina Hajkova, Yozlem Ramadan, Malgorzata Zdych"),
 ("Where", "Vrije Universiteit Amsterdam, course 'Knowledge and Data', Group 31"),
 ("What kind of thing",
  "A student course project. Not peer reviewed, not in a journal. I have to say this or a "
  "supervisor will catch it."),
 ("Why I still care",
  "The main idea in it is the mechanism my thesis is built on, and their third limitation is "
  "my contribution written in their own words."),
 ("Size", "36 classes, 6 object properties, 6 data properties"),
 ("Method", "Middle-out. Start from a base ontology and let the data pull it wider."),
 ("Tools", "OntoRefine, GraphDB, SPARQL, DBpedia, Jupyter, pandas, folium. No Protege."),
 ("Data",
  "1. A Sephora review CSV found on GitHub (agorina91/final_project). "
  "2. A hand-made CSV of countries with Sephora links. "
  "3. DBpedia, live, for capital city coordinates."),
 ("Output",
  "9 products (3 cleansers, 3 moisturisers, 3 treatments), plus the local Sephora link, plus "
  "whether there is a physical shop"),
]

ABESOVA_PIPELINE = [
 "Sephora review CSV  ->  OntoRefine  ->  9 Turtle files  ->  GraphDB  ->  reasoner  ->  SPARQL  ->  9 products",
 "",
 "side input 1   a CSV they typed themselves: country -> Sephora link",
 "side input 2   DBpedia, live: country -> capital city -> geo:lat and geo:long, for the map",
]

ABESOVA_STEPS = [
 ("1", "Start from a base ontology",
  "One teammate had already built a small skincare ontology earlier in the course.",
  "-",
  "This is why it is middle-out and not top-down. They did not start from nothing."),
 ("2", "Find outside data",
  "They searched the web and found a CSV of Sephora product reviews on GitHub.",
  "GitHub",
  "They say this was the hardest part of the project. Finding data usually is."),
 ("3", "Clean it",
  "Deleted columns that did not matter, such as Eye Color and Hair Color. Checked nothing "
  "important was removed by accident.",
  "by hand",
  "The same thing I did. Boring and necessary."),
 ("4", "Turn the CSV into RDF",
  "Loaded the CSV into OntoRefine and drew the mapping: which column becomes a subject, "
  "which becomes a predicate.",
  "OntoRefine, inside GraphDB",
  "This is the step Morph-KGC does for me. Theirs is point-and-click, mine is a file I can "
  "put in the appendix."),
 ("5", "Build the graphs and export",
  "SPARQL CONSTRUCT, one graph at a time, downloaded as nine separate Turtle files, then all "
  "imported into one default graph.",
  "SPARQL CONSTRUCT",
  "Nine files by hand is fragile. To rerun it they have to redo all nine."),
 ("6", "Glue the two vocabularies together",
  "The CSV had its own class names and the base ontology had different ones, so they declared "
  "rdf:Cleanser owl:equivalentClass skc:Cleanser.",
  "GraphDB class restrictions",
  "This is real ontology work, and it is the honest answer to 'how do you merge two sources'."),
 ("7", "Add the main idea",
  "Compute an average rating per skin type, store it as hasOilyScore, then define the class "
  "OilySkinProducts as 'hasOilyScore value 5'. The reasoner fills the class.",
  "OWL hasValue, GraphDB reasoner",
  "This is the part I use. See section 4."),
 ("8", "Reach out to DBpedia",
  "SPARQL against the live DBpedia endpoint. Country to capital city to geo:lat and geo:long, "
  "then draw a map.",
  "DBpedia, geo: and dbo:",
  "They typed no coordinates at all. This is what reuse looks like in practice."),
 ("9", "Recommend",
  "Query reviews from people with the same skin type and skin tone, rank by rating, take the "
  "top 3 per category. If there is not enough data, fall back to the defined class.",
  "SPARQL, Jupyter",
  "The fallback is smart. Their thin-data problem is my cold-start problem."),
 ("10", "Show it",
  "Two pie charts, counts per skin type and per skin tone, and a world map of Sephora countries.",
  "pandas, folium",
  "The pie charts exist so the user can judge how much data the answer rests on. I like that."),
]

ABESOVA_MAIN_IDEA = """\
They never tag a product as good for oily skin. Not once. Instead:

   Step 1   Query all reviews written by people with oily skin, average the stars,
            and store the result on the product:      Product  hasOilyScore  5.0

   Step 2   Define the class, once:
            OilySkinProducts  owl:equivalentClass  ( hasOilyScore value 5 )

   Step 3   Press the reasoner. It finds every product with a 5 and puts it in the
            class by itself. Nobody typed a single membership.

Why this matters to me

If a new product arrives tomorrow with hasOilyScore 5.0, it lands in the class with
no extra work. No script to rerun, no list to update. A normal database cannot do this.
It is the best argument for using an ontology at all, and it is the method my four
defined classes use.

What I change

Their score comes from star ratings. Mine comes from ingredients. Same machinery,
different evidence. Theirs says people liked it. Mine says it contains ceramides,
no fragrance allergen, and nothing on Annex II."""

ABESOVA_CLASSES = [
 ("Country", "class", "Where the user lives"),
 ("Brand", "class", ""),
 ("Category", "class", "Cleanser, Moisturizer, Treatment"),
 ("  Treatment", "subclass", "and under it: Exfoliant (Chemical, Physical), Serum, Toner"),
 ("Product", "class", ""),
 ("  Oily Skin Products", "defined", "= hasOilyScore value 5      the reasoner fills this"),
 ("  Dry Skin Products", "defined", "= hasDryScore value 5"),
 ("  Normal Skin Products", "defined", "= hasNormalScore value 5"),
 ("  Combination Skin Products", "defined", "= hasCombinationScore value 5"),
 ("Review Id", "class", "One review by one person"),
 ("Rating Stars", "class", ""),
 ("Skin Tone", "class", "9 values: Porcelain, Fair, Light, Medium, Olive, Tan, Deep, Dark, Ebony"),
 ("Skin Type", "class", "4 values: Oily, Dry, Normal, Combination"),
]

ABESOVA_PROPS = [
 ("object", "Product hasBrand Brand", ""),
 ("object", "Review Id hasSkinType Skin Type", ""),
 ("object", "Review Id hasSkinTone Skin Tone", ""),
 ("object", "Review Id aboutProduct Product", ""),
 ("object", "Product hasCategory Category",
  "They admit this one was never implemented. They used rdf:type instead and found out too late."),
 ("object", "Product hasReviewId Review Id", ""),
 ("data", "Product hasRating", ""),
 ("data", "Product hasOilyScore", "and hasDryScore, hasNormalScore, hasCombinationScore"),
 ("data", "Country hasSephoraWebPage", ""),
]

ABESOVA_HONEST = [
 ("They say it themselves",
  "'The team found out about the mistake too late to modify it in the OntoRefine.' "
  "Product hasCategory Category was never implemented."),
 ("They say it themselves",
  "'The team was under time-pressure hence the output shows a whole URI instead of only a "
  "product.' The interface prints raw IRIs."),
 ("No evaluation",
  "One worked example for one made-up user. No precision, no recall, no user study, no "
  "competency questions."),
 ("Nothing published",
  "No OWL file, no permanent address, no DOI. I cannot download it and neither can anyone else."),
 ("The deeper problem",
  "The recommendation comes from star ratings only. The system never looks at what is inside "
  "the product. Two products with a 5 are identical to it, even if one is full of fragrance "
  "allergens and the other is not."),
]

ABESOVA_LIMITATION = """\
In their own words:

   "Lastly, class restrictions based on ingredients could be developed.
    This would ensure a more symbolic and chemical approach, compared to
    the statistical one that is currently employed."

That sentence is my thesis. They describe my contribution as their future work.
I can quote it directly in the gap paragraph of my related work chapter."""
