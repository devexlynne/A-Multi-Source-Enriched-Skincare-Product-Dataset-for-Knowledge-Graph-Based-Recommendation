"""
The papers, one list per paper. 28 papers, 28 columns.
Design lives in build_papers_table.py. Edit here, rerun the builder.

Column order goes from the paper itself, to the problem, to their data, to
their ontology, to how they built it, to whether it worked, to what it means
for us. Same order you would read a paper in.
"""

# (group, heading, width)
COLS = [
 ("Paper",         "#",                                    5),
 ("Paper",         "Group",                                9),
 ("Paper",         "What I call it",                      20),
 ("Paper",         "Full title",                          46),
 ("Paper",         "Who wrote it",                        26),
 ("Paper",         "Year",                                 7),
 ("Paper",         "Where it came out",                   30),
 ("Paper",         "notes",                               28),
 ("Paper",         "How many people cite it",             13),
 ("Paper",         "Where they're from",                  24),
 ("Paper",         "Link",                                38),
 ("The problem",   "What problem were they solving",      44),
 ("The problem",   "Who they built it for",               22),
 ("Their data",    "What data they used",                 40),
 ("Their data",    "How much of it",                      26),
 ("Their ontology","Did they follow a proper method?",    26),
 ("Their ontology","How many classes",                    13),
 ("Their ontology","How many properties",                 16),
 ("Their ontology","The classes worth knowing about",     46),
 ("Their ontology","The properties",                      42),
 ("Their ontology","Any rules or clever definitions",     40),
 ("Their ontology","can we download ontology",            26),
 ("Building it",   "How the data got in",                 38),
 ("Building it",   "Tools they used, and for what",       46),
 ("Building it",   "How it actually recommends things",   48),
 ("Did it work",   "How they tested it",                  34),
 ("Did it work",   "What they got, and does it hold up",  44),
 ("For us",        "What this means for us",              66),
]

GROUPS = {
 "A": ("Skincare and cosmetics ontologies",
       "The ones doing what we are doing. These are the direct competitors."),
 "B": ("Ingredients, regulation and skin conditions",
       "Not recommenders. They give our ingredients and concerns a legal or medical standing nobody else has."),
 "C": ("Ontology recommenders in other fields",
       "Food, shopping, academic papers. Nobody solved our problems in skincare, but people solved them here."),
 "D": ("Reviews, evaluation, and the alternative",
       "What counts as good, and the deep learning paper we have to answer."),
}

NR  = "They never say"
NA  = "Doesn't apply"
ABS = "Abstract doesn't say"

P = []

# ============================================================== GROUP A ===
P.append(["1","A","Moe & Aung",
 "Building Ontologies for Cross-domain Recommendation on Facial Skin Problem and Related Cosmetics",
 "Hla Hla Moe, Win Thanda Aung","2014",
 "Int. Journal of Information Technology and Computer Science, 6(6), 33 to 39",
 "weak journal. I cite it for the method, not the standing",
 "3 (2014), 8 (2016 reprint)","Two universities in Myanmar",
 "doi.org/10.5815/ijitcs.2014.06.05",
 "Your skin problem lives in one world, the products live in another. How do you bridge them? No dataset links the two, so they built both worlds themselves.",
 "People with a skin complaint",
 "Nothing stated. No source, no size. Biggest weakness of the paper",
 NR,
 "Not named, but it is an eight step procedure: glossary, taxonomies, relation diagrams, concept dictionary, and so on. That is METHONTOLOGY in all but name",
 NR, NR,
 "Problem side: Questions, Answers (YesNo and Concept), QApairs, Problems, Solutions. Cosmetics side: FacialFoam, Toner, CleansingCream, MilkyLotion, plus ContextualFeatures holding PlaceZone, AgeLevel, Brand, Season, PriceRange",
 "isNextRelatedTo (which question to ask next), hasQuestion, hasAnswer, hasProblem, hasSolution, hasIngredients, hasIngValue, consistsOfPlaceZone",
 "None. No defined classes, no rules",
 "No. It only exists as figures in the paper",
 "Not reported. I think most certainly typed in by hand in Protege",
 "Protege to build both ontologies. No reasoner at all, no SPARQL, no outside data. An ontology paper that never actually reasons",
 "Three steps. (1) The system asks you questions until 'I have acne' becomes 'papules', six questions in their example. (2) Problem and products go into a graph. (3) Ford-Fulkerson, a water-through-pipes algorithm, scores each product. Most flow wins",
 "Precision, recall, F-measure, plotted against a cut-off they call alpha",
 "Ten products scored 0.32 to 0.70. But no dataset size, no baseline, and they claim to beat related work with no comparison table anywhere. Doesn't hold up",
 "Take: the eight task checklist, especially task 1, a glossary of every term with its synonyms (ya3ne our unified schema). Also their ContextualFeatures class: price and place describe a product as sold somewhere, not the product itself.\n"
 "Leave: Ford-Fulkerson. My products already carry availability, price and evidence level, so a weighted filter does the same job.\n"
 "They can't: say an ingredient is regulated. Theirs is just text with a number. Ours links to CosIng on 99.2% of products.\n"
 "My idea: their throwaway Season class. Beirut summer is humid, winter is dry. Nobody in the whole review models climate."])

P.append(["2","A","OntoCosmetic",
 "Towards an ontology-based decision support system for the design of emulsion-based cosmetic products (2021), and Decision making software for cosmetic product design based on an ontology, the Formultools app (2023)",
 "J. Serna, V. Falk, P. Perre, M. Camargo, S. Morel (2021); A. Gabriel, M. Camargo, S. Morel, J. Serna (2023)",
 "2021 and 2023",
 "European Congress of Chemical Engineering (2021); ESCAPE-33, pp 1987 to 1992 (2023)",
 "Respectable chemical engineering venues. Two papers, one ontology",
 NR,"Universite de Lorraine, France, with Universidad Nacional de Colombia",
 "purl.org/ontocosmetic  |  doi.org/10.1016/B978-0-443-15274-0.50316-4",
 "Help a chemist design a cream that stays stable. The second paper turns that into a phone app called Formultools.",
 "Cosmetic formulators, not shoppers",
 "Emulsion science, expert knowledge, ingredient databases typed by function, and heuristics (rules of thumb)",
 "279 individuals in the file",
 "No. But the 2023 app used a proper design method: five planes user-centred design, co-design with experts, iterated with usability tests",
 "116 (I counted)","26 object, 20 data (I counted)",
 "HLB, DropletSize, Rheology, AqueousThickeners, OWCosmeticEmulsion, HeuristicForSurfactant, MeltingPoint, Emollient_Dosage. Ingredient types: Emollient, Surfactant, Thickener, Active, Preservative, UvFilter, Humectant, Antioxidant, Stabilizer, PHRegulator",
 "hasHeuristicHighThreshold, hasHeuristicLowThreshold, hasHeuristicSource (where each rule came from), hasOrigin (natural or synthetic)",
 "Yes, SWRL rules in Protege for the formulation heuristics, each with a high and low threshold and a source",
 "YES. purl.org/ontocosmetic. The only one in the whole review you can actually download",
 "By hand, by experts. 279 individuals typed in. (impossible for us)",
 "Protege with SWRL rules. AttrakDiff questionnaire to measure the app each iteration. AHP (Analytic Hierarchy Process) to weigh several criteria: you pick the properties, say which to maximise, compare them in pairs, and it computes weights. No SPARQL, no outside data",
 "It doesn't recommend to a shopper. The app does three things for a formulator: screen ingredients by property, rank ingredients on several criteria at once using AHP, and check a proposed formula against the heuristics",
 "2021: one case study, a moisturising cream. 2023: AttrakDiff with non-expert testers between iterations",
 "No numbers. And they say in their own conclusion that expert testing was still future work. So the most serious cosmetics ontology out there was never validated with experts",
 "Take: the ingredient function names (emollient, humectant, preservative, UV filter). Keeping product properties separate from ingredient properties. hasOrigin. And hasHeuristicSource: every rule records where it came from, same instinct as our evidence levels. They measured user experience with a standard instrument and reported it. Almost nobody in my review reports any named evaluation instrument. We can take this maybe.\n"
 "Leave: the whole chemistry branch (HLB, droplet size, rheology). Manufacturers never publish it. And the mobile app itself.\n"
 "They can't: say whether you can buy it, what it costs, or who made the claim on the box.\n"
 "My idea: flip it. They go from goal to ingredients. We have 295,991 ingredient mentions with functions, so we could go from ingredients back to what the formulator was trying to do, and check it against their rules."])

P.append(["3","A","Hansanie & Silva",
 "Ontology based Machine Learning Approach for Facial Skincare Products Recommendation",
 "Maduri Hansanie, Thushari Silva","2024",
 "IEEE Int. Conference on Image Processing and Robotics (ICIPRoB)",
 "IEEE conference.",
 "2","University of Moratuwa, Sri Lanka",
 "doi.org/10.1109/ICIPRoB62548.2024.10543444",
 "Choosing skincare is hard and the wrong product makes skin worse. Read the user's face with a neural network, then let an ontology pick the products.",
 "Consumers, especially with acne",
 "For the vocabulary: interviews with dermatologists, plus a survey of 11 men and 10 women aged 21 to 30. For the image model: the ACNE04 dataset (Xiaoping Wu) topped up with DermNet photos",
 "21 people surveyed for vocabulary, 24 tested the system. Product count never given",
 "Not named. Built top down: general classes first, specific ones underneath. Split into THREE ontologies then merged",
 NR, NR,
 "Person, TreatmentProduct (e.g. AcneControlCleanser), SkinType (e.g. OilySkin), KeyIngredient (e.g. SalicylicAcid), ProductRecommendation. Three files: skincare concepts, product info, user profile",
 "suitableFor (product to skin type), hasKeyIngredient, hasProductRecommendation, hasRating, hasAge, hasGender",
 "None reported. Pellet checks consistency",
 "No link given anywhere",
 "Not clearly reported. The spreadsheet-to-ontology step is described as design, not automation",
 "Protege to build. Pellet reasoner to check consistency and infer. Owlready2 to query from Python. Tkinter for the desktop window. A small CNN (three Conv2D layers, 16/32/16 filters, softmax over 3 classes) for the photo. No SPARQL, no outside data",
 "Photo goes in. CNN grades acne as mild, moderate or severe (they merged severe and very severe because the data was unbalanced). That grade is written into the ontology as a fact about the user. Pellet reasons. Owlready2 pulls the products out. Image model and knowledge stay separate",
 "Standard ML metrics for the CNN. Then a five-point survey of 24 people who tried the system",
 "CNN: accuracy 77.5%, precision 78.2%, recall 75.1%, F1 76.6%. Survey: 87.5% said products suited them, 91.7% said the interface was easy. The headline 87.5 is satisfaction, NOT accuracy. No baseline, no ground truth. Quote it correctly and we look careful",
 "Take: three separate ontologies merged, because the three parts change at completely different speeds (products weekly, medical knowledge almost never). A reasoner from day one. Ratings inside the ontology. Owlready2 since our pipeline is Python.\n"
 "Leave: the CNN. No face photos, no ethics approval, and our contribution is the product side. Their layered design means it could be added later.\n"
 "They can't: say a product is stocked in Beirut, costs 11 dollars, and has a restricted preservative. They did consult dermatologists though, and we have not. Say that before they ask.\n"
 "My idea: their architecture has an empty socket where the camera plugs in. We could plug in a BARCODE. Scan the box in the pharmacy, ask if it suits you and if it is cheaper next door."])

P.append(["4","A","Abesova (VU Amsterdam)",
 "Skincare Ontology for Personalised Recommendation",
 "S. Abesova, K. Hajkova, Y. Ramadan, M. Zdych","2023",
 "Vrije Universiteit Amsterdam, Knowledge and Data course, Group 31",
 "A STUDENT PROJECT",
 "0","Vrije Universiteit Amsterdam, Netherlands",
 "In repo/papers/",
 "Give someone a full routine from four inputs: skin type, skin tone, country, and how much effort they will put in.",
 "Consumers",
 "A Sephora review CSV they found on GitHub, a second CSV of countries with Sephora shops, and DBpedia for country data",
 "36 classes, 6 object properties, 6 data properties",
 "Yes: middle out. Start with what you are sure of, work outward both ways. Explicitly iterative, scope widened twice as new CSVs arrived",
 "36","6 object, 6 data",
 "Category (Cleanser, Moisturizer, Treatment; Treatment splits into Exfoliant, Serum, Toner; SPF under Moisturizer). Product with four skin-type subclasses. Skin Type. Skin Tone with nine values. Brand, Country, Rating Stars, Review Id",
 "hasBrand, hasCategory, hasSkinType, hasSkinTone, aboutProduct, hasReviewId, hasRating, hasOilyScore, hasDryScore, hasNormalScore, hasCombinationScore, hasSephoraWebPage",
 "YES, the most important idea in the whole review. OilySkinProducts is DEFINED as 'hasOilyScore value 5'. They never tag a product. The reasoner works out who belongs. Same for Dry, Normal, Combination. Also skc:Cleanser is declared equivalent to rdf:Cleanser to merge two vocabularies",
 "No",
 "CSV into OntoRefine, mapped columns to classes, built the graphs with SPARQL CONSTRUCT, downloaded nine Turtle files, imported them into GraphDB with the base ontology. A real tool, not a script",
 "OntoRefine to map CSV to RDF. GraphDB to store and reason with class restrictions. SPARQL for everything. DBpedia through an outside endpoint: dbr:Czech_Republic gave the country, then its capital dbr:Prague, then geo:lat and geo:long for a map, without typing any of it",
 "It is a set of SPARQL queries, not code. Class restrictions put products into skin-type classes automatically, then queries pick three per category and add the Sephora page for your country",
 "One worked example. No metrics",
 "9 products for one user, three per category. They admit the interface was rushed and shows raw URIs. Doesn't hold up as evaluation, but that is not why I cite it",
 "Take: THE DEFINED CLASS. Write the rule once instead of tagging 4,000 rows. OntoRefine as a way to load data. DBpedia linking to get facts free.\n"
 "Leave: their classes rest on review scores. Ours will rest on the formula.\n"
 "They can't: their own limitation 3, in their words: 'class restrictions based on ingredients could be developed. This would ensure a more symbolic and chemical approach.' MY CONTRIBUTION IS WRITTEN AS FUTURE WORK IN THEIR PAPER.\n"
 "My idea: they pulled PLACE out of DBpedia. I can pull OWNERSHIP out of Wikidata. L'Oreal owns 570 of our products across 9 brands. 118 of them have niacinamide and sell in Lebanon, from $0.51 (Vichy) to $185.58 (SkinCeuticals). Same company, same active, 364x the price."])

P.append(["5","A","bit-Tech 2025",
 "Personalized Skincare Recommendation System Based on Ontology and User Preferences",
 "Not yet confirmed. I only have the abstract","2025",
 "bit-Tech, Komunitas Dosen Indonesia",
 "Regional Indonesian journal. Modest standing but the work is directly comparable to ours. NEED THE FULL PDF",
 NR,"Indonesia",
 "jurnal.kdi.or.id/index.php/bt/article/view/2857",
 "Content-based and collaborative filtering miss the links between skin types, concerns and ingredients. An ontology captures them.",
 "Indonesian skincare consumers",
 "Web scraping of Sociolla, Beautyhaul and SKINSORT. Note: Skinsort is the same global source we used",
 "Over 3,800 products and over 28,000 ingredients",
 "YES, METHONTOLOGY, named explicitly",
 "12","More than 25 object properties",
 "User, Product, Brand, Product Category, Allergen Type, Ingredient, Benefit, Formulation Trait, Key Ingredient, Skin Concern, Skin Type, What It Does",
 ABS, ABS,
 "Not stated in the abstract. CHECK when I get the PDF",
 "Web scraping into the ontology. Whether a mapping language was used is not stated. Find out",
 "Apache Jena Fuseki to store and query. SPARQL with reasoning. No outside data mentioned",
 "SPARQL over the ontology with semantic reasoning, per the abstract",
 "Not clear from the abstract",
 "Can't tell without the full paper",
 "Take: two class names I would not have thought of: Formulation Trait and What It Does. That split IS our evidence problem in class form. What It Does is the marketing claim, Formulation Trait is the physical fact.\n"
 "Leave: their market and their homemade allergen list.\n"
 "They can't: Indonesia vs our Lebanon where availability itself is uncertain. 3,800 vs our 12,629. Their allergen class vs our link to the EU register of 28,573 entries. No price, no availability, no provenance.\n"
 "My idea: adopt their two class names, attach our evidence levels to What It Does and our CosIng derivation to Formulation Trait. Then the model says openly which half of a product description is advertising."])

P.append(["6","A","Utari (JELIKU)",
 "Pengembangan Ontologi Semantik Pada Domain Produk Kosmetik",
 "N. N. R. D. Utari et al.","2023",
 "JELIKU, Universitas Udayana, Indonesia",
 "Small regional journal",
 "0","Universitas Udayana, Indonesia",
 "consensus.app/papers/details/9f025755693f50298a45b5c165537fbc",
 "Too many cosmetic products to choose from. Use a semantic ontology to help.",
 "Indonesian buyers",
 "Cosmetic product data, source not given",
 "3 classes, 5 object properties, 62 individuals",
 "YES, METHONTOLOGY","3","5 object",
 ABS, ABS, "None stated",
 "No",
 NR,
 "Not stated. SPARQL for evaluation",
 "Not really a recommender. They ran SPARQL queries and checked the results looked right",
 "SPARQL queries", "No numbers. It is a proof of concept and doesn't pretend otherwise",
 "Take: honestly not much. I keep it for one reason: 62 products next to our 12,629 shows the scale without me claiming anything. It also shows METHONTOLOGY is the default here, which is why choosing something else needs a stated reason.\n"
 "Leave: everything else.\n"
 "They can't: same as all of group A.\n"
 "My idea: none."])

P.append(["7","A","Mahadewi (JELIKU)",
 "Penerapan Algoritma Slope One dalam Collaborative Filtering (a body care recommender)",
 "I. A. Mahadewi et al.","2024",
 "JELIKU, Universitas Udayana, Indonesia",
 "Small regional journal",
 "0","Universitas Udayana, Indonesia",
 "consensus.app/papers/details/a7956ce9d21f5d6b806688eb6cec7cb8",
 "Body care info online is often wrong or irrelevant. Put the knowledge in an ontology and recommend on top of it.",
 "Indonesian body care buyers",
 "Body care product data mapped into an ontology", NR,
 "YES, METHONTOLOGY for the ontology, Prototyping for the system",
 NR, NR, ABS, ABS, "None stated",
 "No", NR,
 "Slope One, a collaborative filtering algorithm that predicts your rating from the average difference between items. SUS and MAE for evaluation",
 "Collaborative filtering over the ontology knowledge base",
 "Two named instruments: SUS (System Usability Scale, a standard 10-question survey out of 100) and MAE (Mean Absolute Error, how far predicted ratings are from real ones)",
 "SUS 82.344, which counts as good. MAE 0.3556, closer to zero is better. Reasonable for what it claims, and two named instruments is more than most papers here manage",
 "Take: SUS. Standard, free, ten questions. If we ever build an interface this is how we measure it. And the habit of naming your instruments, since the Rahayu review found nobody does.\n"
 "Leave: Slope One and collaborative filtering. We have no user ratings.\n"
 "They can't: no regulator, no provenance, no availability. And an MAE on ratings says nothing about whether the advice was medically sensible.\n"
 "My idea: none."])

# ============================================================== GROUP B ===
P.append(["8","B","TOXIN KG",
 "The TOXIN knowledge graph: supporting animal-free risk assessment of cosmetics",
 "S. Sepehri et al.","2025",
 "Database: The Journal of Biological Databases and Curation, Oxford University Press",
 "STRONG. Oxford, peer reviewed, open access. Better than every skincare paper in group A",
 "4","Vrije Universiteit Brussel, Belgium",
 "doi.org/10.1093/database/baae121  |  live at toxin-search.netlify.app",
 "The EU banned animal testing for cosmetics but there is no validated replacement. Make the old safety data reusable so risk can be judged without animals.",
 "Toxicologists and risk assessors",
 "Safety data on annexed cosmetic ingredients from SCCS scientific opinions 2009 to 2019. Same committee that writes the CosIng annexes we use",
 "88 ingredients, 53 of them with liver effects",
 "Not named as a method, but the process is carefully documented",
 "Inherited from TXPO","Inherited from TXPO",
 "Reuses TXPO, the ToXic Process Ontology, from the OBO Foundry. TXPO itself pulls in Gene Ontology, ChEBI, Disease Ontology and others",
 "Not detailed. SMILES notation added so every chemical has one standard identity",
 "ToxRTool scores how reliable each study is automatically",
 "YES. Live and searchable at toxin-search.netlify.app",
 "CURATED EXCEL TO RDF USING R2RML. Toxicologists type into spreadsheets, computer scientists have read-only access and generate the graph. The most useful sentence in the paper for us",
 "R2RML to turn spreadsheets into triples. TXPO as the ontology. NAMED GRAPHS, one box per data source, so you always know where a fact came from. Links out to KEGG, Reactome, UniProt by IRI instead of copying. Ontodia to draw it",
 "Not a recommender. You filter for ingredients linked to liver toxicity and follow the chain to the harm",
 "Use cases showing retrieval works",
 "88 ingredients loaded, 53 flagged. Claims to be a retrieval tool and demonstrates retrieval. No overreach",
 "Take: THREE THINGS that change our plan. R2RML/RML for loading data, a mapping file not a script. Named graphs per source, which is our evidence-level idea at the storage layer. Linking out by IRI rather than copying.\n"
 "Leave: the toxicology depth, liver mechanisms, gene pathways.\n"
 "They can't: IT HAS NO PRODUCTS. All the law, nothing on a shelf. Every skincare ontology has products and no law. Nobody has both. That is exactly where we sit.\n"
 "My idea: they model the evidence BEHIND a restriction. We only model the restriction as a pointer like Annex V/29. One owl:sameAs per ingredient and a product on a Beirut shelf traces all the way to the SCCS opinion that limits phenoxyethanol to 1%."])

P.append(["9","B","HaCKG",
 "Halal or Not: Knowledge Graph Completion for Predicting Cultural Appropriateness of Daily Products",
 "Van Thuy Hoang et al.","2025",
 "IEEE Access",
 "Indexed, respectable. This one trims one of my ideas, so I raise it myself",
 "8","South Korea",
 "consensus.app/papers/details/033951ebc555534aac4c54bad403585a",
 "Halal prediction looks at ingredients one at a time and misses the relationships between products and ingredients.",
 "Muslim consumers, retailers in Muslim-majority markets",
 "A cosmetics dataset of products, ingredients and properties", ABS,
 "No. It is a machine learning paper that happens to build a graph",
 ABS, ABS,
 "Cosmetics, ingredients and their properties as graph entities", ABS,
 "None. The learning is in the network, not in rules",
 "Not stated", ABS,
 "A relational graph attention network with residual connections: a neural net that learns by passing messages between connected nodes and paying attention to what kind of link each edge is. Pre-trained on the graph, fine-tuned to predict halal",
 "The network embeds the graph and predicts halal status. A probability, no reason",
 "Benchmarks against state-of-the-art baselines",
 "Reported as beating the baselines, figures not in the abstract. Sound for an ML paper, but it is prediction with no reasoning and no cited authority",
 "Take: their own argument helps us. They say one-ingredient-at-a-time misses the relationships between products and ingredients. That is an argument FOR a graph, made by somebody else. Also proves a cosmetics KG is publishable.\n"
 "Leave: the neural network. No interaction data, and our contribution is the resource.\n"
 "They can't: give a reason. They PREDICT with a model. We would DERIVE from the INCI list and cite it. But be honest: this weakens our halal idea, it is not new anymore.\n"
 "My idea: use them as an evaluation target. Where our derivation and their prediction agree, mutual validation. Where they disagree, that set is a result."])

P.append(["10","B","CosIng-KG",
 "cosing-kg: the EU CosIng database converted to RDF",
 "biobricks-ai (a GitHub project, not a paper)","n/a",
 "GitHub, serving kg.toxindex.com",
 "Not a paper. An artefact. CHECK FIRST, could save weeks",
 NA,"biobricks-ai",
 "github.com/biobricks-ai/cosing-kg",
 "Make the EU CosIng register available as a proper graph.",
 "Anyone building on cosmetic ingredient regulation",
 "CosIng itself, the same register we already use","All 28,573 CosIng entries, if complete",
 NA, NA, NA, "Whatever CosIng's structure maps to","Haven't looked properly yet","None",
 "YES, on GitHub. Haven't checked licence or identifiers yet",
 "Converted from the CosIng release", "Haven't looked yet", NA, NA, NA,
 "Take: POSSIBLY OUR ENTIRE INGREDIENT LAYER, free and citable. If usable, our products link straight to their ingredient IRIs.\n"
 "Leave: nothing yet.\n"
 "They can't: if it is NOT usable that is also fine, our own conversion becomes a stated contribution instead of an assumption.\n"
 "My idea: this is the highest-value half hour available right now. Do it before writing any Turtle."])

P.append(["11","B","CCIBP",
 "CCIBP: a comprehensive cosmetic ingredients bioinformatics platform",
 "Linlin Gong et al.","2023",
 "Bioinformatics, Oxford University Press",
 "STRONG journal. A resource paper precedent",
 "2","China",
 "design.rxnfinder.org/cosing",
 "One place for the physical properties, metabolic pathways, toxicology and safe concentrations of cosmetic molecules.",
 "Cosmetic researchers and formulators",
 "Regulations from major world regions (not only EU), physicochemical properties, human metabolic pathways, plant data for natural ingredients", ABS,
 "None stated. It is a database, not an ontology", NA, NA, NA, NA, "None",
 "YES, publicly available at the URL",
 "Curated from regulatory and chemical sources","Chemoinformatics and bioinformatics tooling",
 "Not a recommender. Supports formulation and efficacy analysis",
 "Presented as a resource, shown through use", "No numbers in the abstract. It claims to be a platform and it is one",
 "Take: possibly a SECOND ingredient source, since it covers non-EU regulation. Thirty minutes in step 2 to see if it adds anything CosIng doesn't. Also a resource paper in a strong journal, which backs our argument that building a resource counts.\n"
 "Leave: the synthetic biology material.\n"
 "They can't: ingredients and no products, same shape as TOXIN.\n"
 "My idea: if Lebanon follows anything non-European for some ingredient classes, this is where it lives."])

P.append(["12","B","DermO",
 "DermO: an ontology for the description of dermatologic disease",
 "University of Birmingham group","2016",
 "Journal of Biomedical Semantics",
 "Solid specialist journal. The ontology is properly published",
 NR,"University of Birmingham, UK",
 "bioportal.bioontology.org/ontologies/DERMO",
 "Skin diseases had no formal, shareable vocabulary. Build one by hand with dermatologists.",
 "Clinicians and medical informatics people",
 "Expert-written terms. No scraping, no learning",
 "Over 3,000 terms in 20 top-level categories",
 "Biomedical ontology conventions, aligned to ICD-10 (the WHO disease list every hospital uses)",
 "3,000+ terms", NR,
 "Diseases filed by: where on the body, whether inherited, what tissue is affected, what causes it",
 "Not inspected in detail", NA,
 "YES. GitHub plus BioPortal, in OBO and OWL 2 formats, free",
 "By hand, by domain experts","OBO tooling, Protege",
 "Not a recommender. A vocabulary",
 "Expert review and cross-ontology mapping","3,000+ terms, 20 categories. Yes for a vocabulary",
 "Take: OUR CONCERNS COLUMN. It has six values and every one names a real disease: eczema on 6,901 products, rosacea 5,871, acne 4,261. We are already making medical statements and no clinician has checked them. Six lines of alignment to DermO gives our vocabulary clinical standing.\n"
 "Leave: the disease depth. We are not diagnosing.\n"
 "They can't: no products. But this one is a gift, not a competitor. It fixes the weakness in Hansanie & Silva's row: they had dermatologists, we did not. We cannot get one quickly, but we can align to one they built.\n"
 "My idea: DermO knows WHERE on the body a disease sits. Our types imply a body site: 637 eye products, 550 lip, 676 body, 62 hand. Link them and we can say 'you have nothing for your eye area'. Nobody in cosmetics connects product to body site through a clinical ontology."])

P.append(["13","B","Halal flavouring ontology",
 "Development of Flavouring Ontology for Recommending the Halal Status of Flavours",
 "Malaysian group with JAKIM experts","2024",
 "Journal of Information Science Theory and Practice, 12(2)",
 "Modest but peer reviewed. A pattern donor, not a competitor",
 NR,"Malaysia",
 "accesson.kr/jistap/v.12/2/22/42865",
 "Trace whether a flavour ingredient is halal so a manufacturer can predict the product's status.",
 "Food makers and halal certifiers",
 "Flavour ingredients and certification references, with experts from JAKIM (Malaysia's Department of Islamic Development)", NR,
 "Not named", NR, NR,
 "Halal certification process, halal concept, reference sources, traceability", ABS, "Not stated",
 "Not stated", "Not stated", "Not stated",
 "Status is inherited: a product's halal status follows from its ingredients' statuses, according to a named authority",
 "Expert consultation with the certifying body", "No numbers. Fine for a conceptual framework",
 "Take: THE THREE-PART PATTERN: ingredient, AUTHORITY, status, with the authority as its own thing rather than an attribute. Swap halal for EU annex restriction and it is our problem exactly.\n"
 "Leave: the food specifics.\n"
 "They can't: nothing to attack, it is a pattern.\n"
 "My idea: because the authority is separate, we can say Phenoxyethanol is restricted under Annex V/29 ACCORDING TO the European Commission, and leave room for a Lebanese authority later. That one choice future-proofs the whole regulatory layer."])

P.append(["14","B","Klaschka",
 "Naturally toxic: natural substances used in personal care products",
 "Ursula Klaschka","2015",
 "Environmental Sciences Europe",
 "Good journal, heavily cited. Not an ontology, but gives us a free finding",
 "107","Ulm University, Germany",
 "consensus.app/papers/details/c46f8b2f2d295088a0e529d31143952c",
 "Which natural substances in personal care products are actually hazardous, and how does EU law treat them?",
 "Regulators, and anyone who thinks natural means safe",
 "The INCI list and the EU classification and labelling inventory",
 "1,358 natural substances in INCI, 655 of them in the EU inventory",
 NA, NA, NA, NA, NA, NA, "The registers are public",
 NA, "REACH and CLP regulatory instruments",
 NA,
 "Regulatory analysis, counting classifications",
 "Of the 655: 56% classified hazardous, 38% for human health, 35% for skin and eyes, and 53 substances classified carcinogenic, mutagenic or toxic to reproduction. Holds up, and flags inconsistencies in the classifications too",
 "Take: peer reviewed proof, 107 citations, that NATURAL DOES NOT MEAN SAFE. That arms our free_from column and every 'clean' claim in our descriptions.\n"
 "Leave: the environmental detail.\n"
 "They can't: substances only, no products. We have 11,802 formulas AND the marketing claims AND the register.\n"
 "My idea: a question nobody else can answer: across 12,629 products, do the ones sold as natural actually contain fewer hazardous ingredients? We hold all three pieces already. No new data. That is why the plan has a NaturalClaimProduct class."])

P.append(["15","B","MVFM",
 "Predictive Analysis of Cosmetic Formulations: A Multi-Vector INCI Mapping Methodology",
 "Rusana Plonsak","2026",
 "Journal of Applied Cosmetology",
 "Small journal, brand new. One idea I need",
 "0",NR,
 "consensus.app/papers/details/ea07c5e70d905e3694e09206096364f2",
 "EU law says claims must not mislead, but does not require them to be backed by the composition. A barrier-repair cream need not contain barrier lipids. How do you check from the label alone?",
 "Practitioners and dermatologists",
 "INCI lists of commercial products","Three products, one evaluator",
 NA, NA, NA, NA, NA, NA, "The method is in the paper",
 "Manual scoring", "None",
 "Find the first regulated preservative or fragrance in the INCI list. That is roughly the 1% line, since INCI is in concentration order. Score everything above it on Hydration, Lipid, Structural, 0 to 3 each. Compare to the claim",
 "Three products by hand",
 "Worked on all three. One product sold as anti-aging scored H=4 L=7 S=6, a lipid-heavy texture cream with two regulated allergens in its active zone. Author says larger validation and inter-rater reliability are still to do",
 "Take: INCI POSITION AS A SIGNAL. This is why our ontology must record where each ingredient sits in the list, not just that it is there. Position is the only concentration information a consumer ever gets.\n"
 "Leave: the manual three-vector scoring, it is subjective.\n"
 "They can't: three products by hand. We could run it across 11,802 automatically, which is the validation they say is missing.\n"
 "My idea: their finding is that a claim can be unsupported by the composition. That is our evidence-level argument from the chemistry side. Running it at scale would be the first large test of whether cosmetic claims are compositionally grounded."])

# ============================================================== GROUP C ===
P.append(["16","C","Middleton",
 "Ontological User Profiling in Recommender Systems",
 "Stuart Middleton, Nigel Shadbolt, David De Roure","2004",
 "ACM Transactions on Information Systems, 22(1), 54 to 88",
 "THE BEST VENUE IN THE WHOLE REVIEW. Q1. Cite it first",
 "Thousands","University of Southampton, UK",
 "doi.org/10.1145/963770.963773",
 "Describe what a user is interested in using an ontology rather than a bag of keywords, and see if recommendations get better.",
 "Researchers looking for papers",
 "Academic paper databases plus watching what users read and asking them",
 "Two deployed systems, Quickstep and Foxtrot",
 "Not named", NR, NR,
 "A research topic ontology", "Topic hierarchy links", "Inference up the hierarchy",
 "Described in the paper",
 "Papers classified into ontology classes automatically","Their own systems. Inference over the topic tree. Bootstrapped from an outside publication database. Predates SPARQL",
 "Watching you builds a profile in ontology terms. Inference extends it up the tree. Then collaborative recommendation finds papers similar people liked on your topics",
 "Real deployments with real users over time",
 "Three findings, all positive: inference improves profiling, outside knowledge bootstraps a cold start, showing users their profile improves accuracy. Holds up, real deployments",
 "Take: ALL THREE FINDINGS ARE OUR THREE ARGUMENTS. (1) Inference up a hierarchy: our concerns have one. (2) Outside knowledge bootstraps a cold start: a new Beirut user has no history, but the ontology already knows what suits combination skin. THIS IS OUR COLD START ANSWER. (3) Users correcting their own profile.\n"
 "Leave: the collaborative half, we have no user base.\n"
 "They can't: no safety dimension, papers cannot hurt you.\n"
 "My idea: their 'watching the user' in Lebanon is not browsing history. It is THE RECEIPT. Beirut pharmacies are small and repeat custom is normal. What somebody actually re-bought is more honest than what they clicked."])

P.append(["17","C","FoodKG",
 "FoodKG: A Semantics-Driven Knowledge Graph for Food Recommendation (2019), and the follow-up: Personalized Food Recommendation as Constrained Question Answering over a Large-scale Food Knowledge Graph (2021)",
 "Haussmann, Seneviratne, Chen, Ne'eman, Codella, Chen, McGuinness, Zaki (2019); Chen, Subburathinam, Chen, Zaki (2021)",
 "2019 and 2021",
 "ISWC 2019 (top semantic web conference) and WSDM 2021",
 "Rank A. The closest thing to us in any field. If you read one paper outside skincare, this one",
 "Several hundred, plus over 100 for the follow-up","Rensselaer Polytechnic Institute and IBM Research, USA",
 "doi.org/10.1007/978-3-030-30796-7_10  |  foodkg.github.io  |  arxiv.org/abs/2101.01775",
 "Recipes and food facts are scattered everywhere. Put them in one graph so people can eat better. Then (2021): stop ranking, and answer a question with constraints instead.",
 "People who want to eat well",
 "Recipes, nutrition data, food taxonomies, links into existing ontologies","Millions of triples",
 "Not named, but the construction process is presented as the contribution itself", NR, NR,
 "Recipes, ingredients, nutrients, food categories","Recipe to ingredient to nutrition links","Allergies as HARD constraints, not preferences",
 "YES, foodkg.github.io",
 "Integration of several existing datasets and ontologies, described step by step",
 "Semantic web stack. A SPARQL service on top. Links to existing food and nutrition ontologies",
 "A SPARQL service finds a recipe from the ingredients you have while respecting hard constraints like allergies. The 2021 paper turns the user's requirements into constraints and answers over the graph: the output is the set of things that satisfy every requirement, not a ranked list",
 "Several applications built on the graph; benchmarks in the 2021 paper",
 "Claims to be a resource and is one, published and reused. Holds up",
 "Take: FOUR PRACTICES. Present construction itself as the contribution (a top venue accepted that). State a maintenance plan (no skincare ontology has one). Several apps on one graph, so the graph is infrastructure. HARD CONSTRAINTS: an allergy is a filter, not a score. That is exactly where an ontology beats a neural net.\n"
 "Leave: the food specifics.\n"
 "They can't: their constraints cite no legal authority. Our allergen constraint cites EU law.\n"
 "My idea: the analogy is exact. Recipes = products. Nutrition from an authority = CosIng. Allergies = the EU 26. 'What can I cook with what is in my kitchen' = 'what can I buy in my pharmacy'. And the 2021 framing tells us what to build: not a ranker, a question answerer. 'Dry skin, under $15, buyable in Hamra' is four real columns."])

P.append(["18","C","Di Noia / Ostuni",
 "Linked Open Data to Support Content-based Recommender Systems (2012); Top-N Recommendations from Implicit Feedback Leveraging Linked Open Data (RecSys 2013); Using Linked Open Data in Recommender Systems (2015)",
 "Tommaso Di Noia, Vito Claudio Ostuni and colleagues","2012 to 2015",
 "I-SEMANTICS, RecSys, WIMS",
 "RecSys is the top recommender conference",
 "Several hundred across the line","Politecnico di Bari, Italy",
 "doi.org/10.1145/2797115.2797128",
 "Recommend items using only the links they have in public data, when you have no ratings and thin descriptions.",
 "Content-based recommender builders",
 "DBpedia, Freebase, LinkedMDB. Movies","Standard movie benchmarks",
 NA, NA, NA, "DBpedia's classes", "DBpedia predicates as the dimensions", "None",
 "Public data",
 "Uses existing linked data","SPARQL against DBpedia endpoints. DBpedia, Freebase, LinkedMDB as outside data",
 "A semantic vector space model. Each item becomes a list of numbers, but the dimensions are its LINKS in public data, not words. Two films are similar if they share a director, genre, period",
 "Offline movie benchmarks",
 "Described as promising. They name their open problem honestly: matching your item to the right outside entity is the hard part",
 "Take: PRODUCT SIMILARITY WITHOUT RATINGS. Two products are similar if they share ingredient functions, a restriction profile, a concern, a price band. Our rating column is half empty and we have no history, so this is the only similarity that uses everything we collected.\n"
 "Leave: the movie domain and the collaborative parts.\n"
 "They can't: their open problem is entity matching. We MEASURED that on our own data: fuzzy matching scored a category page 100 against a full product name, and the database pass had a 19 to 33% error rate. Strong paragraph.\n"
 "My idea: they enriched thin ITEMS with public data. Ours are rich already. So enrich the SHOPS instead. Wikidata and OpenStreetMap know where Beirut pharmacies are. 'Available fifteen minutes' walk away' is something no cosmetics system has done."])

P.append(["19","C","AliCoCo",
 "AliCoCo: Alibaba E-commerce Cognitive Concept Net",
 "Xusheng Luo et al.","2020",
 "ACM SIGMOD 2020",
 "Rank A star, one of the very best database venues. THE BIGGEST IDEA IN THE REVIEW",
 "Several hundred","Alibaba and Shanghai Jiao Tong University, China",
 "doi.org/10.1145/3318464.3386132  |  github.com/alicogintel/AliCoCo",
 "Every product ontology describes what a product IS. Shoppers think about what they NEED. That gap is why shopping feels stupid.",
 "E-commerce platforms and shoppers",
 "Alibaba's catalogue and user behaviour, at national scale","Millions of concepts and items",
 "Not named, but the design principle is explicit","Large","Large",
 "USER NEEDS AS FIRST-CLASS ENTITIES. Not 'moisturiser' but 'outdoor barbecue', 'keeping warm in winter', 'getting ready for a beach holiday'",
 "Needs linked to items, categories and attributes","The representation is the contribution",
 "Partly, via GitHub",
 "Semi-automatic extraction at scale from catalogue and behaviour","Alibaba's internal stack. Their own concept net",
 "Your stated situation retrieves the products that serve it, not the ones matching your keywords",
 "Deployed at Alibaba scale with online metrics",
 "Reported improvements in production. Holds up, validated by real deployment rather than an offline split",
 "Take: THE ONE IDEA. Our concerns column is a user need sitting in a product schema pretending to be an attribute. Promote it. A need entity can be met by a COMBINATION of products, can carry a budget, a season, a constraint. An attribute can do none of that.\n"
 "Leave: the scale and the behavioural extraction.\n"
 "They can't: no regulator, no provenance. Nothing in AliCoCo says who claimed what.\n"
 "My idea: LEBANESE NEEDS ARE NOT GLOBAL NEEDS. 'A routine under $20 a month.' 'Products that don't need a fridge.' 'Something for a bride.' 'A routine I can buy in one pharmacy.' Every one is expressible in our data. Nobody can copy it without our dataset. Most original claim, least certain, do it last."])

P.append(["20","C","Guo survey",
 "A Survey on Knowledge Graph-Based Recommender Systems",
 "Qingyu Guo et al.","2022",
 "IEEE Transactions on Knowledge and Data Engineering, 34(8), 3549 to 3568",
 "Q1. Cite the 2022 journal version, not the 2020 preprint. I nearly got that wrong",
 "Over a thousand","Chinese Academy of Sciences, Microsoft Research Asia, Rutgers",
 "arxiv.org/abs/2003.00911",
 "Sort the whole field of knowledge-graph recommenders into a usable map.",
 "Recommender researchers",
 "Hundreds of papers", NA, NA, NA, NA, NA, NA, NA, "Published survey",
 NA, NA,
 "Three families. EMBEDDING: turn entities into vectors, scales but the reasoning is gone. PATH: find paths between user and item, explainable but expensive. UNIFIED: propagate across the graph, best accuracy but needs lots of interaction data",
 "Reviews others", "A survey, appropriately careful",
 "Take: the three-family structure for our hybrid section.\n"
 "Leave: the methods themselves, for now.\n"
 "They can't: ALL THREE FAMILIES ASSUME A USER-ITEM MATRIX AND A GRAPH THAT ALREADY EXISTS. We have neither. So we sit UPSTREAM of the whole survey.\n"
 "My idea: this turns our biggest apparent weakness into a scope statement. Say: 'the survey classifies methods for USING a knowledge graph and assumes one exists for the domain. For skincare in a local market it does not. This thesis builds it.' Then 'you have no users' is answered."])

P.append(["21","C","E-Prod",
 "An ontology based product recommendation system for next generation e-retail (plus Alaa et al. 2021 on ontology evolution)",
 "Ali Murat Tiryaki et al. (2023); Rana Alaa et al. (2021)","2023, 2021",
 "Journal of Organizational Computing and Electronic Commerce; Electronics (MDPI)",
 "Respectable. State-funded R&D. The industrial version of what we did by hand",
 "4, and 14 for Alaa","Turkey; Egypt",
 "consensus.app/papers/details/d79755c5a1a65d048c1d926a7e172938",
 "Product recommenders fail because they have no semantics. And (Alaa): everyone builds their ontology once from a snapshot, so it goes stale.",
 "E-commerce sellers and buyers. Clothing, shoes, bags",
 "Live e-commerce sites, tracked in real time","Over 250 registered users",
 "Not named. Alaa proposes a semi-automatic building method with an evolution subsystem", NR, NR,
 "Product model classes, not detailed", ABS, "Semantic matching between products and preferences",
 "Not stated",
 "TRACKS E-COMMERCE SITES IN REAL TIME AND PUSHES PRODUCT INFO STRAIGHT INTO THE ONTOLOGY. Continuous, not one-off",
 "Machine learning plus semantic matching. Not stated beyond that",
 "Learns preferences by watching behaviour, then matches semantically between products and preferences",
 "250+ real users against traditional collaborative filtering",
 "Accuracy 92.79%, precision 92.93%, recall 90.58%, beating the baseline. THE BEST EVALUATION IN THE REVIEW: real users, a stated baseline, three metrics",
 "Take: THE POPULATION ARCHITECTURE. They prove scraping can run continuously. Our six Lebanese retailers could be re-read on a schedule, turning the dataset from a snapshot into a live resource. Biggest upgrade available to the dataset paper, no new modelling. Also Alaa's point gives us the citation for the maintenance section LOT requires.\n"
 "Leave: the clothing domain and the behavioural learning.\n"
 "They can't: no regulator, no provenance, no safety. Clothes cannot hurt you.\n"
 "My idea: our named graph design already answers Alaa. Reload graph:lb-retail weekly without touching anything else. The architecture solves their criticism by construction, and we can say so."])

P.append(["22","C","Lahoud (Lebanon)",
 "A comparative analysis of different recommender systems for university major and career domain guidance",
 "Christine Lahoud et al.","2022",
 "Education and Information Technologies, Springer",
 "Solid Springer journal. THE LEBANESE PRECEDENT",
 "36","LEBANON",
 "consensus.app/papers/details/1aef32f231a051b8b266907d2bb517b6",
 "Lebanese high school students are lost choosing a major, with a volatile job market and too much data online.",
 "Lebanese high school students",
 "A case study on Lebanese students with a purpose-built ontology", NR,
 "Not named", NR, NR, "A guidance-domain ontology", ABS, "Case-based reasoning with the ontology",
 "Described as reusable in other systems",
 "Not stated", "Not stated",
 "Five approaches compared on the same case: user-based CF, item-based CF, demographic, knowledge-based with case-based reasoning, ontology, and hybrids",
 "Comparative evaluation on Lebanese students with feedback and satisfaction",
 "The hybrid (knowledge + CF + case-based reasoning + ontology) reached 98% similar cases, 95% personalised, 95% usefulness, 92.5% satisfaction. Five approaches on one case is a proper comparison",
 "Take: (1) a Lebanon-focused ontology recommender is publishable in a real journal with citations, so local scope is NOT a weakness. (2) The hybrid beat every pure approach, which backs our future work. (3) These are Lebanese academics working on ontology recommenders: possible examiners, reviewers, collaborators.\n"
 "Leave: the education domain.\n"
 "They can't: nothing, it is an ally.\n"
 "My idea: find out where they are."])

# ============================================================== GROUP D ===
P.append(["23","D","Rahayu review",
 "A systematic review of ontology use in E-Learning recommender system",
 "Nur Wahyu Rahayu et al.","2022",
 "Computers and Education: Artificial Intelligence",
 "Well cited Elsevier journal. THE MOST USEFUL SINGLE CITATION IN THE REVIEW. Put it in the introduction",
 "137","Indonesia",
 "consensus.app/papers/details/1f58f76b65ab5e5ca6b4ec6af28c2664",
 "Nobody had systematically looked at how ontology recommenders are actually built. So look.",
 "Researchers building ontology recommenders",
 "28 journal articles on ontology-based recommender systems","28 primary studies",
 "Studies whether OTHERS named a method, and finds they mostly didn't", NA, NA, NA, NA, NA, "Published review",
 NA, NA, NA,
 "Systematic review",
 "TWO FINDINGS: ontology recommenders 'seldom use the methodology of building ontologies', and 'NONE of the primary studies described ontology evaluation methodologies'. None of 28. Also: standards for profiles and metadata are rarely adopted",
 "Take: THIS IS OUR GAP STATEMENT, quantified by someone else. Naming a method (MOMo + LOT) and reporting an evaluation (OOPS!, FOOPS!, competency questions) are not housekeeping. In this field they are contributions, and cheap ones.\n"
 "Leave: the e-learning specifics.\n"
 "They can't: it is an ally.\n"
 "My idea: one paragraph naming our method plus one afternoon running two free web tools puts us ahead of an entire 28-paper sample on the two things it was worst at. No cheaper way to strengthen a thesis."])

P.append(["24","D","Tarus (two papers)",
 "Knowledge-based recommendation: a review of ontology-based recommender systems for e-learning (review, 2017); A hybrid knowledge-based recommender system based on ontology and sequential pattern mining (hybrid, 2017)",
 "John Tarus, Zhendong Niu, with Ghulam Mustafa / Abdallah Yousif","2017",
 "Artificial Intelligence Review (Springer); Future Generation Computer Systems (Elsevier, Q1)",
 "Both strong. The standard citations for 'why an ontology at all' and 'cold start'",
 "451 and 277","Beijing Institute of Technology, China",
 "consensus.app/papers/details/015574eca5b4569e908597b9530f1c34",
 "Review: nobody had reviewed ontology recommenders properly. Hybrid: recommenders suffer cold start and sparsity and ignore differences between users.",
 "Researchers; e-learning platforms",
 "Review: papers 2005 to 2014. Hybrid: learner data and learning resources", NR,
 "Not named", NR, NR, "Learner and resource classes", "Ontology knowledge used for similarity", "None stated",
 "Not stated",
 "Not stated","Ontology plus sequential pattern mining (finds common orderings in how people consume things)",
 "Hybrid: build the ontology, compute similarity using ontological knowledge, get a top-N list with collaborative filtering, reorder it with sequential pattern mining",
 "Review: systematic. Hybrid: experiments against baselines",
 "Review concludes ontologies improve recommendation quality and hybridising helps more. Hybrid reports improved performance. Both hold up for what they claim",
 "Take: the review is the 451-citation answer to 'why an ontology'. The hybrid states explicitly that ontological domain knowledge ALLEVIATES COLD START AND SPARSITY, our cold start argument with 277 citations attached. And the division of labour: ontology handles the domain, the learned part handles users. That means our ontology is the half that must exist first.\n"
 "Leave: sequential pattern mining and CF, no user sequences.\n"
 "They can't: no authority, no provenance, no availability.\n"
 "My idea: none, they are justification sources."])

P.append(["25","D","COPPER ontology",
 "Development and evaluation of the COntextualised and Personalised Physical activity and Exercise Recommendations (COPPER) Ontology",
 "M. Braun et al.","2025",
 "International Journal of Behavioral Nutrition and Physical Activity",
 "Q1 health journal. THE TEMPLATE FOR OUR ONTOLOGY CHAPTER. Read it and match its structure",
 "4","Europe",
 "consensus.app/papers/details/49832525b1df5c31865f019b8635ffe5",
 "Personalised exercise plans need expert knowledge, user input and data together, and black boxes cannot do that transparently.",
 "People getting activity advice, and their advisers",
 "Literature, use case scenarios, decision-tree workshops, existing theories, end users, domain experts, datasets",
 "288 classes, 64 object properties, 9 data properties",
 "Yes. Specification, conceptualisation, formalisation. Follows OBO Foundry design principles",
 "288","64 object, 9 data",
 "An upper ontology plus lower ones for PERSONAL PROFILE, PLANNING, ACTIVITY, CONTEXT, BARRIER and COPING STRATEGY. Note the modules", ABS,
 "Logic rules written during formalisation",
 "YES, openly available, and they list that as one of their three novelty claims",
 "Combined theory, classification systems, user input, expert input and datasets","Protege, translated into OWL",
 "Recommends action and coping plans from a profile plus context",
 "THREE LAYERS: the process against OBO principles, the ontology for logical consistency, the recommendations with competency questions and use cases",
 "Consistent, and recommendations judged relevant. They claim exactly what they show, no accuracy figure because none is warranted. Holds up",
 "Take: THE WHOLE STRUCTURE. Modular design, a stated process, three-layer evaluation, open publication as a contribution in itself. Even 288 classes is a realistic size for us.\n"
 "Leave: the physical activity domain.\n"
 "They can't: nothing. Read it and copy the shape.\n"
 "My idea: they have a BARRIER module: what stops a person doing the activity. Ours is unavailability, price, the currency crisis. 'Barrier' is a better name than 'availability' because it covers price, stock, distance and season in one idea. Consider renaming our Lebanon module around it."])

P.append(["26","D","FEVR",
 "Evaluating Recommender Systems: Survey and Framework",
 "Eva Zangerle, Christine Bauer","2022",
 "ACM Computing Surveys",
 "Q1, very high impact. The shield for our evaluation choice",
 "283","Austria",
 "consensus.app/papers/details/793b2c09411459cda72df729aee73069",
 "Evaluating a recommender means choosing goals, methods, data and metrics together, and that knowledge is scattered.",
 "Recommender researchers",
 "The literature on evaluation", NA, NA, NA, NA, NA, NA, NA, "Published survey",
 NA, NA, "Not a recommender, a framework for deciding HOW to evaluate one",
 "Consolidates the field into FEVR, a framework organising goals, methods, data and metrics",
 "A framework, not an experiment. Careful and widely adopted",
 "Take: the argument that THE EVALUATION MUST FOLLOW THE GOAL. Our goal is correctness with a stated reason, not ranking accuracy, so precision and recall are the wrong instruments.\n"
 "Leave: the metric catalogue for interaction-based systems.\n"
 "They can't: it is a framing source.\n"
 "My idea: this is the answer to 'why no precision and recall'. A 283-citation paper says match the evaluation to the goal. Ours is verifiable correctness. One sentence, fully defended."])

P.append(["27","D","Lee (lululab)",
 "Deep learning-based skin care product recommendation: A focus on cosmetic ingredient analysis and facial skin conditions",
 "Jinhee Lee, Huisu Yoon, Semin Kim, Chanhyeok Lee, Jongha Lee, Sangwook Yoo","2024",
 "Journal of Cosmetic Dermatology (Wiley)",
 "A real clinical journal, better standing than most of group A. THE DEEP LEARNING RIVAL we have to answer directly",
 NR,"lululab Inc., Seoul, South Korea. Corporate R&D",
 "doi.org/10.1111/jocd.16218",
 "Cosmetic recommendation ignores what ingredients actually do. Estimate efficacy from the ingredient list with a neural net, combine with AI skin analysis.",
 "Consumers, through a commercial product",
 "Cosmetic ingredient lists and facial skin images. Proprietary", ABS,
 NA, NA, NA, NA, NA, NA, "No. Corporate",
 NA, "A deep neural network plus AI skin analysis. No ontology, no reasoning, no outside data",
 "A neural net estimates a product's efficacy FROM ITS INGREDIENTS. Skin analysis reads your face. The two combine into a recommendation",
 "Reported as effective for various skin issues",
 "Figures not in the abstract. Can't fully assess a corporate paper",
 "Take: nothing technical. It DOES OUR PROBLEM WITHOUT AN ONTOLOGY, so we must answer it honestly.\n"
 "Leave: the whole approach. No labelled efficacy data, no face images.\n"
 "They can't: give a REASON. They learn ingredient-to-efficacy from data, we derive it from the EU register plus stated rules. They give a weight, we give the ingredient, its function and the annex entry. They need proprietary training data, we need none. They can't handle an unseen ingredient, we say it is in the register or it is not. They cite nothing, we cite Regulation 1223/2009. They ignore availability, we make it core. Be honest though: with enough labelled data a model probably beats rules on accuracy.\n"
 "My idea: use a model like theirs as a HYPOTHESIS GENERATOR and our ontology as the CHECK. Train something small on our 11,802 formulas, take its confident predictions, test them against CosIng. Where they disagree, that set is a result, and only we can compute it because we have both halves."])

P.append(["28","D","Ali (ontology vs LLM)",
 "Ontology-grounded knowledge graphs for mitigating hallucinations in large language models for clinical question answering",
 "Mohamed Ali et al.","2026",
 "Journal of Biomedical Informatics (Elsevier)",
 "Strong specialist journal. THE ANSWER TO 'WHY NOT JUST ASK AN LLM'. Put it in the introduction",
 "11","Egyptian hospitals and institutions",
 "consensus.app/papers/details/d7c871f2bb3857439c1bfa563bebf37a",
 "LLMs make things up, which makes them unusable in medicine. Ground them in an ontology and see if that fixes it.",
 "Clinicians",
 "Clinical and hospital data from several Egyptian institutions","60 clinical questions with reference answers from five peer-reviewed hospital studies",
 "Not stated", NR, NR, "Clinical concepts", ABS, "The ontology forces the model to stay inside the graph when it answers",
 "Not stated",
 "From clinical and hospital data","A GraphRAG setup: retrieval over an ontology-grounded graph feeding an LLM. RDF and OWL for the ontology",
 "The model can only answer from what the graph says, so it cannot invent",
 "Three conditions on the same 60 questions against external reference answers",
 "ChatGPT-4: 37% correct, ~63% hallucinated. DeepSeek-R1: 52%. ONTOLOGY-GROUNDED: 98% (59 of 60), 1.7% hallucination. A proper controlled comparison. Holds up",
 "Take: the citation that answers the question every supervisor asks in 2026. In a safety-relevant domain, grounding a model in an ontology cut hallucination from 63% to 1.7%. That is the difference between deployable and not.\n"
 "Leave: the clinical QA application.\n"
 "They can't: it is our strongest supporting citation, not a competitor.\n"
 "My idea: skincare is safety-relevant too, and our ontology is the grounding. That is the future work sentence."])

PAPERS = P
assert all(len(r) == len(COLS) for r in PAPERS), \
    [ (r[2], len(r)) for r in PAPERS if len(r) != len(COLS) ]
