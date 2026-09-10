# -*- coding: utf-8 -*-
"""
Text for the new tabs. Kept separate from the drawing code so I can fix a
sentence without touching the layout.

Written in my own voice, first person, plain words.
"""

# ============================================================ TAB: The gap
# Paper, group, what they did, what is missing in it, what I do instead,
# what they still have that I do not
GAP_COLS = [
    ("#", 5),
    ("Paper", 22),
    ("What they actually did", 46),
    ("What is MISSING in it", 46),
    ("What I do instead", 46),
    ("What they have that I do NOT", 34),
]

GAP = [
 # ---------------------------------------------------------------- GROUP A
 ("A", "SKINCARE AND COSMETICS ONTOLOGIES",
  "These are my direct competitors. My gap has to be stated against these seven."),

 ("1", "Moe & Aung 2014",
  "Two ontologies, cosmetics and skin problems. Six questions narrow you down, then a "
  "max-flow algorithm scores what is left.",
  "No reasoner at all. No SPARQL. No outside data. No real products. They never say how "
  "many. Nothing is downloadable.",
  "12,629 real products with real prices. A reasoner that actually runs. Every ingredient "
  "tied to the EU database.",
  "Their question-and-eliminate interaction is nicer than anything I have. I only have queries."),

 ("2", "OntoCosmetic 2021/23",
  "Helps a chemist FORMULATE a cream. SWRL rules with high and low thresholds for each "
  "ingredient function. Published and downloadable.",
  "It is for the person MAKING the product, not the person buying it. No shopper, no price, "
  "no availability, no skin type.",
  "Same chemistry idea but pointed at the buyer. Their rule shape is what I copy for my "
  "defined classes.",
  "They publish their OWL file at a permanent address and I have not yet. They also ran real "
  "user testing across iterations."),

 ("3", "Hansanie & Silva 2024",
  "Photo of your face goes into a small CNN, the grade comes out, the ontology picks products. "
  "Pellet checks consistency.",
  "The ontology is tiny and never released. No SPARQL. No outside data. The CNN does the work "
  "and the ontology is decoration.",
  "No photos at all. My reasoning is the contribution, not a bolt-on. My ingredient layer is "
  "the part theirs does not have.",
  "They have a working end-to-end app with a real interface and 24 people tested it. I have "
  "no interface yet."),

 ("4", "Abesova 2023 (VU)",
  "Student project. Sephora review CSV to RDF with OntoRefine, GraphDB, defined classes like "
  "'OilyScore = 5', SPARQL picks 9 products.",
  "Not peer reviewed. Recommends from REVIEW SCORES only, never looks at what is in the "
  "product. They admit one property was implemented wrong.",
  "Same defined-class trick, but driven by INGREDIENTS instead of star ratings. That is "
  "literally their Limitation 3.",
  "They link to DBpedia for a live map and they have a working country-to-shop link. My "
  "Lebanon layer does the same job but only for one country."),

 ("5", "bit-Tech 2025",
  "METHONTOLOGY, Apache Jena Fuseki, SPARQL with reasoning, about 3,800 products. My closest "
  "competitor on paper.",
  "I only have the abstract. No ingredients, no regulation link, no provenance mentioned "
  "anywhere.",
  "Ingredients tied to EU law, four levels of evidence, and real shop availability. None of "
  "which they claim.",
  "3,800 products in a proper published venue with a named method, already finished. I need "
  "the full PDF before I can say more."),

 ("6", "Utari 2023",
  "METHONTOLOGY on 62 products. Evaluated with SPARQL queries.",
  "62 products is a demonstration, not a system. No tools stated. Nothing downloadable.",
  "12,629 products, which is 200 times more, and every one has a source and a date.",
  "Nothing I can see."),

 ("7", "Mahadewi 2024",
  "Slope One collaborative filtering. Measured with SUS and MAE.",
  "Not an ontology at all. Needs a ratings matrix. Cannot explain why it recommended "
  "anything.",
  "Symbolic reasoning that can always show its working. Cold start is not a problem for me.",
  "They have two named evaluation instruments and real numbers. My evaluation plan is still "
  "on paper."),

 # ---------------------------------------------------------------- GROUP B
 ("B", "INGREDIENTS, REGULATION AND SKIN CONDITIONS",
  "Not recommenders. These give my ingredient and concern layers a standing nobody in Group A has."),

 ("8", "TOXIN KG 2025",
  "Toxicology graph. R2RML from spreadsheets, TXPO ontology, named graphs so every fact keeps "
  "its source. Links out by IRI.",
  "Toxicology, not cosmetics. No consumer anywhere near it.",
  "I steal the named-graph idea wholesale. One graph per source: Skinsort, Amazon, the six "
  "Lebanese shops.",
  "Their provenance is more mature than mine and they score study reliability automatically "
  "with ToxRTool."),

 ("9", "HaCKG 2025",
  "Neural graph network that predicts halal status from a knowledge graph.",
  "The reasoning is inside a neural net, so it cannot explain itself. No rules.",
  "Rules I can print. A supervisor can check any single decision by hand.",
  "It beats rule systems on raw accuracy and it handles cases no rule covers."),

 ("10", "CosIng-KG",
  "CosIng already turned into RDF and published on GitHub.",
  "Not a paper and I have not verified it works yet.",
  "If it is usable I reuse it and save weeks. If not, I build the ingredient layer myself.",
  "It may already contain a cleaner version of my whole ingredient layer."),

 ("11", "CCIBP 2023",
  "A chemical and biological database of cosmetic ingredients.",
  "A resource, not a system. No recommendation, no consumer.",
  "I use it as a cross-check on my ingredient names.",
  "Proper chemoinformatics depth that I do not have."),

 ("12", "DermO 2016",
  "3,000 skin disease terms written by dermatologists, on BioPortal.",
  "It is a terminology. It does not recommend anything.",
  "I align my six concern values to it. Six lines of code and my medical claims stop being "
  "my own invention.",
  "Actual clinical authority. Mine is borrowed from them."),

 ("13", "Halal flavouring 2024",
  "Ingredient to STATUS to AUTHORITY, with the certifying body as a real entity in the graph.",
  "Food, not cosmetics.",
  "I copy the three-part shape exactly for CosIng annex status and for evidence levels.",
  "They consulted the actual certifying body. I have consulted nobody yet."),

 ("14", "Klaschka 2015",
  "Counts how many cosmetic ingredients carry hazard classifications under REACH and CLP.",
  "An analysis, not a tool.",
  "Gives me the sentence that justifies why a regulation link matters at all.",
  "Nothing structural."),

 ("15", "MVFM 2026",
  "A framework tested on three products by hand.",
  "Three products. No tools, no ontology file.",
  "Scale, and everything automated.",
  "Nothing."),

 # ---------------------------------------------------------------- GROUP C
 ("C", "ONTOLOGY RECOMMENDERS IN OTHER FIELDS",
  "Nobody solved my problems in skincare. People solved them in food and shopping."),

 ("16", "Middleton 2004",
  "The paper that proves an ontology in a recommender is a legitimate choice. ACM TOIS, "
  "thousands of citations.",
  "Academic papers, not products. Predates SPARQL entirely.",
  "I cite it first in the chapter. Its cold-start argument is my cold-start argument.",
  "Real deployments with real users over years. Mine is a dataset."),

 ("17", "FoodKG 2019/21",
  "Recipes, ingredients, nutrition from an authority, allergies as HARD constraints. SPARQL "
  "service on top. Published.",
  "Food. And they do not have a regulator the way I have CosIng.",
  "Almost the same shape as mine: recipes are products, nutrition data is CosIng, allergies "
  "are the EU allergen list.",
  "Everything, honestly. They publish, they state a maintenance plan, and they built several "
  "applications on one graph. This is my model."),

 ("18", "Di Noia / Ostuni",
  "Similarity computed from LINKS in the graph, not from words. No ratings needed.",
  "Movies. And they say themselves entity matching is the hard part.",
  "I can compute product similarity with zero user history, which is exactly my situation.",
  "Proper offline benchmarks against baselines."),

 ("19", "AliCoCo 2020",
  "Alibaba's own concept net, deployed at real scale.",
  "Internal, closed, and enormous. Nothing reusable.",
  "I work at a size one person can actually verify.",
  "Online metrics from millions of real users."),

 ("20", "Guo survey 2022",
  "Surveys knowledge-graph recommenders and sorts them into families.",
  "A survey. Nothing built.",
  "Tells me which family I am in so I can name it in the chapter.",
  "Nothing."),

 ("21", "E-Prod 2023",
  "Machine learning plus semantic matching, tested on 250+ real users against collaborative "
  "filtering.",
  "General e-commerce. No regulation, no chemistry.",
  "My matching is over ingredients with a legal backing.",
  "250 real users. That is a proper evaluation and I do not have one."),

 ("22", "Lahoud 2022",
  "Ontology plus case-based reasoning, evaluated on Lebanese students.",
  "Not skincare.",
  "Proof that this kind of work gets done and published in Lebanon.",
  "A comparative evaluation with real local users."),

 # ---------------------------------------------------------------- GROUP D
 ("D", "EVALUATION, AND THE ALTERNATIVE I MUST ANSWER",
  "What counts as good, and the deep-learning answer to the same problem."),

 ("23", "Rahayu review 2022",
  "Reviews 28 ontology-based recommender studies.",
  "A review.",
  "Its finding IS my justification: not one of the 28 described how it was evaluated. So I "
  "describe mine.",
  "Nothing."),

 ("24", "Tarus 2017",
  "Ontology plus sequential pattern mining for e-learning.",
  "E-learning.",
  "The idea that order matters. My routine_step column is the same instinct.",
  "Experiments against baselines."),

 ("25", "COPPER 2025",
  "Evaluated on THREE layers: process against OBO principles, logical consistency, then "
  "competency questions.",
  "Not skincare.",
  "This is the evaluation design I copy, because it is the most complete one in my review.",
  "They actually ran it. I have only planned it."),

 ("26", "FEVR 2022",
  "A framework for how ontology recommenders should be evaluated.",
  "A framework.",
  "Tells me to match the evaluation to the goal instead of reporting precision by reflex.",
  "Nothing."),

 ("27", "Lee 2024 (lululab)",
  "Deep neural network plus AI skin analysis. No ontology anywhere.",
  "Cannot explain a single recommendation. No ingredients, no rules, no regulation.",
  "Everything I do is inspectable. That is the whole argument.",
  "It works today, at commercial scale, with real customers."),

 ("28", "Ali 2026",
  "Ontology-grounded graph feeding an LLM. Three conditions, same 60 questions.",
  "Very new. Not skincare.",
  "Shows the ontology stops the model inventing things. This is my future work chapter.",
  "A clean experimental design I should imitate."),
]


# ============================================================ TAB: Reasoning
REASONING_INTRO = (
 "Reasoning means the machine works something out that I never typed in. "
 "There are five ways to do it and they are NOT interchangeable. "
 "Below: what each one is, an example from MY data, who in my review uses it, and whether it fits me."
)

REASONING_COLS = [
    ("", 3),
    ("The technique", 26),
    ("What it does, in one line", 44),
    ("Example from MY data", 52),
    ("Who in my review uses it", 30),
    ("Fits me?", 12),
    ("Why", 44),
]

REASONING = [
 ("H", "  1. THE FIVE WAYS TO REASON", "", "", "", "", ""),

 ("", "RDFS entailment",
  "The cheapest one. If Cleanser is a subclass of Product, then every cleanser is a product.",
  "I say CeraVe Cleanser is a skc:Cleanser. The machine works out it is also a Product. "
  "I never typed that.",
  "Abesova gets this for free in GraphDB",
  "YES",
  "Free, always on, no cost. But it only does the hierarchy. It cannot do anything clever."),

 ("", "OWL defined classes",
  "I write the DEFINITION of a class, and the reasoner decides who belongs. I never tag "
  "anything by hand.",
  "SensitiveSafeProduct = a Product with no restricted ingredient AND no fragrance allergen. "
  "The reasoner finds all 12,629 members itself.",
  "Abesova (OilyScore value 5), OntoCosmetic, COPPER",
  "YES",
  "This is my core mechanism. If I add a product tomorrow it lands in the right classes with "
  "no extra work. This is the thing a database cannot do."),

 ("", "SWRL rules",
  "If-then rules bolted onto OWL, for things OWL alone cannot say.",
  "IF a product has retinol AND has an AHA THEN flag conflict. OWL alone struggles with "
  "two-variable rules like this.",
  "OntoCosmetic, for its formulation thresholds",
  "MAYBE",
  "Powerful but it slows the reasoner badly and only Pellet/Openllet runs it properly. "
  "I would use it for two rules at most."),

 ("", "SPARQL CONSTRUCT",
  "A query that writes new triples instead of returning a table.",
  "CONSTRUCT a triple saying a product is 'suitable for winter' by combining occlusive plus "
  "no drying alcohol.",
  "Abesova, to build the OilyScore triples",
  "YES",
  "Simple, fast, and I already know SPARQL. But the rules live in loose .rq files and nothing "
  "checks them."),

 ("", "SHACL rules  (SHACL-AF)",
  "Rules written IN the graph, in Turtle, that add new triples. Also the only standard way to "
  "VALIDATE.",
  "See the SHACL section below. This is the one nobody in my review uses.",
  "NOBODY.  0 of 28 papers.",
  "YES",
  "Two jobs in one language: catch bad data, and infer new facts. And it is a gap I can "
  "genuinely claim."),

 ("H", "  2. WHY OWL AND SHACL ARE NOT THE SAME THING", "", "", "", "", ""),

 ("", "OWL = open world",
  "If something is not written down, OWL assumes it MIGHT still be true. It never complains "
  "about missing data.",
  "I say a product must have exactly one price. A product has two prices. OWL does not error. "
  "It DECIDES the two prices are the same thing.",
  "Everyone who uses OWL",
  "YES",
  "Correct for inferring. Completely wrong for checking my data is clean."),

 ("", "SHACL = closed world",
  "What is not in the graph is treated as false. It reports an error, and points at the exact "
  "triple.",
  "Same case: SHACL says 'product X has 2 values for hasPrice, maximum is 1', and names X.",
  "Nobody in my review",
  "YES",
  "This is what I actually want when validating 12,629 rows. OWL literally cannot do it."),

 ("", "The trap to avoid",
  "People write owl:maxCardinality thinking it is a constraint. It is not. It is an "
  "instruction to infer.",
  "This is the single most common beginner mistake in OWL, and it is worth one sentence in "
  "my chapter.",
  "-",
  "-",
  "Source: Knublauch, 'SHACL and OWL Compared', spinrdf.org/shacl-and-owl.html"),

 ("H", "  3. WHAT SHACL WOULD ACTUALLY DO IN MY THESIS", "", "", "", "", ""),

 ("", "Job 1: guard the dataset",
  "Check every product before it enters the graph.",
  "Every Product must have >=1 ingredient, exactly one price_usd, a country from a fixed list, "
  "and a rating between 0 and 5. Run once, get a report naming every bad row.",
  "-", "YES",
  "I have 12,629 rows from 8 different sources. Something IS wrong in there. This finds it and "
  "the report goes in the appendix as evidence."),

 ("", "Job 2: enforce my evidence rule",
  "The rule I keep saying matters: no claim without a source.",
  "Every ingredient with a CosIng annex status MUST have prov:wasAttributedTo and a date. "
  "SHACL refuses the triple otherwise.",
  "-", "YES",
  "This turns my provenance design from a promise into something a machine enforces. Strongest "
  "single use for me."),

 ("", "Job 3: infer, with sh:TripleRule",
  "Add a new triple when a condition holds. Same job as a defined class, but readable.",
  "IF a product has >=3 barrier lipids THEN add rdf:type BarrierRepairProduct.",
  "-", "YES",
  "Compare to OWL: OWL can ONLY infer types and sameAs. SHACL can infer any triple at all."),

 ("", "Job 4: compute, with sh:SPARQLRule",
  "A rule that does arithmetic and writes the answer back.",
  "Count how many EU-restricted ingredients a product has and store it as a number I can sort "
  "on. OWL cannot count. At all.",
  "-", "YES",
  "This is the honest limit of OWL, and the cleanest reason to bring SHACL in."),

 ("H", "  4. HOW TO ACTUALLY RUN IT", "", "", "", "", ""),

 ("", "pySHACL",
  "Python. pip install pyshacl, one line to validate.",
  "pyshacl -s shapes.ttl -f human data.ttl",
  "-", "YES",
  "My whole pipeline is Python. Slowest of the three, but I have 1.8M triples, not a billion."),

 ("", "Apache Jena SHACL",
  "Java. The fastest of the three in published benchmarks.",
  "Command line, or from Java. Also reads SHACL-C, a compact syntax that is easier to read.",
  "-", "MAYBE",
  "Benchmarked about 4x faster than pySHACL. Only worth it if pySHACL gets slow."),

 ("", "TopBraid SHACL API",
  "Java, from the people who wrote the spec. The reference implementation.",
  "The one that defines correct behaviour when the others disagree.",
  "-", "MAYBE",
  "Useful to check against if a result looks wrong."),

 ("", "GraphDB",
  "My triple store has SHACL validation built in on a repository.",
  "Turn it on when creating the repository, and bad data is rejected at load time.",
  "-", "YES",
  "Zero extra tooling. This is probably where I start."),
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

    sh:property [                      # exactly one price, and not negative
        sh:path sk:priceUSD ;
        sh:maxCount 1 ;
        sh:datatype xsd:decimal ;
        sh:minInclusive 0 ;
        sh:message "Price missing, doubled, or negative" ] ;

    sh:property [                      # rating must be 0 to 5
        sh:path sk:rating ;
        sh:minInclusive 0 ;
        sh:maxInclusive 5 ] ."""),

 ("Job 2. No claim without a source. This is my whole provenance argument, enforced.", """\
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
        sh:message "A claim with no date is not checkable" ] ."""),

 ("Job 3. Infer a new type.  sh:TripleRule, from SHACL Advanced Features.", """\
sk:BarrierRepairRule
    a sh:NodeShape ;
    sh:targetClass sk:Product ;
    sh:rule [
        a sh:TripleRule ;
        sh:condition [                       # the IF part
            sh:path sk:hasBarrierLipid ;
            sh:minCount 3 ] ;
        sh:subject   sh:this ;               # the THEN part
        sh:predicate rdf:type ;
        sh:object    sk:BarrierRepairProduct ] ."""),

 ("Job 4. Count something. OWL cannot do this at all.  sh:SPARQLRule.", """\
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


# ============================================================ TAB: Abesova
ABESOVA_FACTS = [
 ("Full title", "Skincare Ontology, Final Project"),
 ("Who", "Sara Abesova, Karolina Hajkova, Yozlem Ramadan, Malgorzata Zdych"),
 ("Where", "Vrije Universiteit Amsterdam, course 'Knowledge and Data', Group 31"),
 ("What kind of thing is it",
  "A STUDENT COURSE PROJECT. Not peer reviewed, not in a journal. I must say this out loud "
  "or a supervisor will catch it."),
 ("Why I still care",
  "Because the ONE clever idea in it is the mechanism my whole thesis is built on, and their "
  "Limitation 3 is literally my contribution written in their own words."),
 ("Size", "36 classes, 6 object properties, 6 data properties"),
 ("Method", "Middle-out. Start from a base ontology, let the data pull it wider."),
 ("Tools", "OntoRefine, GraphDB, SPARQL, DBpedia, Jupyter, pandas, folium.  NO PROTEGE."),
 ("Data",
  "1) A Sephora review CSV found on GitHub (agorina91/final_project). "
  "2) A hand-made CSV of countries with Sephora links. "
  "3) DBpedia, live, for capital city coordinates."),
 ("Output", "9 products (3 cleanser, 3 moisturiser, 3 treatment) + local Sephora link + is there a physical shop"),
]

ABESOVA_STEPS = [
 ("1", "Start from a base ontology",
  "One teammate had already built a small skincare ontology in an earlier week of the course.",
  "-",
  "This is why it is middle-out and not top-down. They did not start from nothing."),
 ("2", "Find outside data",
  "They searched the web and found a CSV of Sephora product REVIEWS on GitHub.",
  "GitHub",
  "They say this was the hardest part of the whole project. Finding data is always the hard part."),
 ("3", "Clean it",
  "Deleted columns that did not matter, like Eye Color and Hair Color. Checked nothing "
  "important got deleted by accident.",
  "by hand",
  "Same thing I did. Boring and necessary."),
 ("4", "Turn the CSV into RDF",
  "Loaded the CSV into OntoRefine and drew the RDF mapping: which column becomes a subject, "
  "which becomes a predicate.",
  "OntoRefine (inside GraphDB)",
  "This is the step Morph-KGC does for me. Theirs is point-and-click, mine is a file I can "
  "put in the appendix."),
 ("5", "Build the graphs and export",
  "SPARQL CONSTRUCT, one graph at a time, downloaded as NINE separate Turtle files, then all "
  "imported into one default graph.",
  "SPARQL CONSTRUCT",
  "Nine files by hand is fragile. If they rerun it they must redo all nine."),
 ("6", "Glue the two vocabularies together",
  "The CSV had its own class names. The base ontology had different ones. So they declared "
  "rdf:Cleanser owl:equivalentClass skc:Cleanser.",
  "GraphDB class restrictions",
  "This is real ontology work and it is the honest answer to 'how do you merge two sources'."),
 ("7", "Add the clever part",
  "Compute an average rating per skin type, store it as hasOilyScore, then DEFINE the class "
  "OilySkinProducts as 'hasOilyScore value 5'. The reasoner fills the class.",
  "OWL hasValue + GraphDB reasoner",
  "THIS IS THE WHOLE REASON I READ THIS PAPER. See the box below."),
 ("8", "Reach out to DBpedia",
  "SPARQL against the live DBpedia endpoint: country to capital city to geo:lat and geo:long, "
  "then draw a map.",
  "DBpedia + geo: and dbo: vocabularies",
  "They typed zero coordinates. This is what reuse actually looks like."),
 ("9", "Recommend",
  "Query reviews from people with the same skin type AND skin tone, rank by rating, take top "
  "3 per category. If there is not enough data, fall back to the defined class.",
  "SPARQL + Jupyter",
  "The fallback is genuinely smart. Their thin-data problem is my cold-start problem."),
 ("10", "Show it",
  "Two pie charts (counts per skin type, per skin tone) and a world map of Sephora countries.",
  "pandas, folium",
  "The pie charts exist so the user can judge how much data the answer rests on. I like that."),
]

ABESOVA_CLASSES = [
 ("Country", "class", "Where the user lives"),
 ("Brand", "class", "-"),
 ("Category", "class", "Cleanser / Moisturizer / Treatment"),
 ("  Treatment", "subclass", "and under it: Exfoliant (Chemical, Physical), Serum, Toner"),
 ("Product", "class", "-"),
 ("  Oily Skin Products", "DEFINED", "= hasOilyScore value 5     <-- the reasoner fills this"),
 ("  Dry Skin Products", "DEFINED", "= hasDryScore value 5"),
 ("  Normal Skin Products", "DEFINED", "= hasNormalScore value 5"),
 ("  Combination Skin Products", "DEFINED", "= hasCombinationScore value 5"),
 ("Review Id", "class", "One review by one person"),
 ("Rating Stars", "class", "-"),
 ("Skin Tone", "class", "9 values: Porcelain, Fair, Light, Medium, Olive, Tan, Deep, Dark, Ebony"),
 ("Skin Type", "class", "4 values: Oily, Dry, Normal, Combination"),
]

ABESOVA_PROPS = [
 ("object", "Product hasBrand Brand", ""),
 ("object", "Review Id hasSkinType Skin Type", ""),
 ("object", "Review Id hasSkinTone Skin Tone", ""),
 ("object", "Review Id aboutProduct Product", ""),
 ("object", "Product hasCategory Category", "THEY ADMIT THIS ONE WAS NEVER IMPLEMENTED. They used rdf:type instead and found out too late."),
 ("object", "Product hasReviewId Review Id", ""),
 ("data", "Product hasRating (literal)", ""),
 ("data", "Product hasOilyScore (decimal)", "and hasDryScore, hasNormalScore, hasCombinationScore"),
 ("data", "Country hasSephoraWebPage (literal)", ""),
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
 ("Nothing is published",
  "No OWL file, no permanent address, no DOI. I cannot download it and neither can anyone else."),
 ("The deep problem",
  "The recommendation comes from STAR RATINGS ONLY. The system never looks at what is inside "
  "the product. A product with a 5 and a product with a 5 are identical to it, even if one is "
  "full of fragrance allergens and the other is not."),
]

ABESOVA_LIMITATION = (
 "Limitation 3, in their own words:\n\n"
 "   \"Lastly, class restrictions based on ingredients could be developed.\n"
 "    This would ensure a more symbolic and chemical approach, compared to\n"
 "    the statistical one that is currently employed.\"\n\n"
 "That sentence is my thesis. They describe my contribution as their future work.\n"
 "I can quote it directly in the gap paragraph of my related work chapter, and it is the\n"
 "single most useful sentence in the whole review."
)
