"""
Builds THESIS_LITERATURE_TABLE.xlsx

Seven sheets. The master sheet is 38 columns wide and holds every paper found
across both search rounds, written in plain language so it can be handed to a
supervisor without explanation.

Run:  py build_table.py
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.dimensions import ColumnDimension

# ----------------------------------------------------------------- palette
INK      = "1B2430"   # near black, headings
PAPER    = "FBF8F3"   # warm off white, body
RULE     = "C9BFB0"   # hairline
B_TEAL   = "0F4C4C"   # track B
C_PLUM   = "5A2A44"   # track C
D_RUST   = "7B3F1D"   # track D
E_INDIGO = "27356B"   # track E
F_OLIVE  = "4A5320"   # track F
GOLD     = "B8862B"   # highlight
TINT_B   = "E3EDEC"
TINT_C   = "F1E6EC"
TINT_D   = "F6E9DF"
TINT_E   = "E6EAF4"
TINT_F   = "ECEEE0"
MINE     = "FFF3D6"   # the "for me" column band

SERIF = "Georgia"
MONO  = "Consolas"

thin = Side(style="thin", color=RULE)
box  = Border(left=thin, right=thin, top=thin, bottom=thin)

TRACK_COLOUR = {"B": (B_TEAL, TINT_B), "C": (C_PLUM, TINT_C),
                "D": (D_RUST, TINT_D), "E": (E_INDIGO, TINT_E),
                "F": (F_OLIVE, TINT_F)}

# ------------------------------------------------------- column definition
# (group, header, width)
COLS = [
 ("Where it sits",  "No.",                              5),
 ("Where it sits",  "Track",                            7),
 ("Where it sits",  "Short name I use",                18),
 ("Where it sits",  "Priority for me",                 14),

 ("The paper",      "Full title",                      52),
 ("The paper",      "Authors",                         30),
 ("The paper",      "Year",                             6),
 ("The paper",      "Where it was published",          34),
 ("The paper",      "How good is that venue",          30),
 ("The paper",      "Times cited (Sept 2026)",         12),
 ("The paper",      "Country / institution",           28),
 ("The paper",      "Link",                            46),
 ("The paper",      "Did I read it, or only the abstract", 26),

 ("What it is about","The problem they set out to solve", 52),
 ("What it is about","Who it is for",                   26),

 ("Their data",     "What data they used",              44),
 ("Their data",     "How much data",                    30),
 ("Their data",     "Is their data or ontology public", 34),

 ("Their ontology", "Did they name a building method",  28),
 ("Their ontology", "How many classes",                 16),
 ("Their ontology", "How many properties",              20),
 ("Their ontology", "The classes worth knowing",        54),
 ("Their ontology", "The properties worth knowing",     50),
 ("Their ontology", "Rules or defined classes",         44),

 ("Filling it up",  "How the data got into the ontology", 44),
 ("Filling it up",  "Software they used",               38),

 ("How it works",   "How a recommendation is produced", 54),
 ("How it works",   "Reasoner used",                    22),
 ("How it works",   "SPARQL used",                      14),
 ("How it works",   "Outside vocabularies they linked to", 34),

 ("Did it work",    "How they tested it",               40),
 ("Did it work",    "The numbers they report",          38),
 ("Did it work",    "Do the numbers back the claim",    40),

 ("For my thesis",  "What I take from it",              54),
 ("For my thesis",  "What I leave, and why",            42),
 ("For my thesis",  "What they could not do that I can",46),
 ("For my thesis",  "The idea nobody would expect",     58),
 ("For my thesis",  "Where it goes in my chapter",      26),
]

GROUP_TINT = {
 "Where it sits":   "EDE7DD",
 "The paper":       "E8EDF2",
 "What it is about":"EDE7DD",
 "Their data":      "E8EDF2",
 "Their ontology":  "EDE7DD",
 "Filling it up":   "E8EDF2",
 "How it works":    "EDE7DD",
 "Did it work":     "E8EDF2",
 "For my thesis":   MINE,
}

NR = "Not reported"
NA = "Not applicable"

# =========================================================== THE PAPERS ===
# Order of fields matches COLS exactly.
P = []

P.append(["1","B","Moe & Aung","Read closely",
 "Building Ontologies for Cross-domain Recommendation on Facial Skin Problem and Related Cosmetics",
 "K. S. M. Moe, T. N. Aung","2014",
 "Int. Journal of Information Technology and Computer Science 6(6) 33-39",
 "Weak. A low barrier journal. Say so plainly if asked; I cite it for its method, not its standing",
 "3 (2014 version), 8 (2016 reprint)","Univ. of Technology Yatanarpon Cyber City + Univ. of Computer Studies Yangon, Myanmar",
 "https://www.mecs-press.org/ijitcs/ijitcs-v6-n6/v6n6-5.html",
 "Full PDF, in repo/papers/",
 "A user has a facial skin problem and needs a cosmetic. The problem and the products live in two different worlds, so how do you bridge them",
 "Consumers with a skin complaint",
 "None stated. This is the paper's biggest weakness","Not reported anywhere in the paper",
 "No. No link, no repository, no address. The ontology exists only as figures",
 "No name given, but it is METHONTOLOGY in all but name: an eight task procedure",
 NR,NR,
 "SkinProblem, Symptom, Cause, Cosmetics, and ContextualFeatures which holds PlaceZone, AgeLevel, CosmeticsBrand, Season, PriceRange",
 "hasIngredients, hasIngValue, isNextRelatedTo, hasSymptom, hasCause",
 "None. No defined classes, no rules",
 "Not reported. Almost certainly typed in by hand in Protege",
 "Protege",
 "Three stages. Conversational questioning narrows a vague query to a definite problem, then problem and products go into a weighted graph, then Ford-Fulkerson maximum flow scores each product. Highest flow wins",
 "None. An ontology paper that never actually reasons","No",
 "None",
 "Precision, recall and F-measure, plotted against a cut-off they call alpha",
 "Product flow weights from 0.38 to 0.70. No dataset size given",
 "No. They claim to beat related work but there is no comparison table, no baseline and no dataset size",
 "The eight task checklist, especially task 1, a glossary of every term with its synonyms. Also their ContextualFeatures class: price and place describe a product as sold somewhere, not the product itself",
 "Ford-Fulkerson. My products already carry availability, price and evidence level, so a weighted filter does the same job with less machinery",
 "Their ingredients are free text with a number attached and no register behind them. Nothing in their model can say an ingredient is regulated. Mine can, on 99.2% of products with a formula",
 "Their throwaway Season class. Beirut summer is humid and coastal, winter is dry, so a gel cleanser right in August is wrong in January. Nobody in my whole review models climate, and Lebanon has a genuinely seasonal skin problem",
 "Section 3.2, first competitor"])

P.append(["2","B","OntoCosmetic (Serna)","Read closely",
 "Towards an ontology-based decision support system for the design of emulsion-based cosmetic products",
 "J. Serna, V. Falk, P. Perre, M. Camargo, S. Morel","2021",
 "Computer Aided Chemical Engineering (ESCAPE)",
 "Respectable chemical engineering proceedings",NR,
 "Universite de Lorraine (ERPI-ENSGSI, LRGP), France + Universidad Nacional de Colombia",
 "https://purl.org/ontocosmetic",
 "Full PDF plus the OWL file itself",
 "Help a formulator design a stable emulsion by encoding what makes creams work",
 "Cosmetic formulators and R&D chemists",
 "Emulsion science principles, expert knowledge, ingredient databases typed by function, and heuristics",
 "279 individuals in the published file",
 "YES. The only cosmetics ontology in my whole review that is publicly downloadable. purl.org/ontocosmetic",
 "None stated, but the four building-block structure is deliberate",
 "116 (I counted them in the file)","26 object, 20 data (counted)",
 "HLB, DropletSize, Rheology, AqueousThickeners, OWCosmeticEmulsion, HeuristicForSurfactant, MeltingPoint, Emollient_Dosage. Ingredient types: Emollient, Surfactant, Thickener, Active, Preservative, UvFilter, Humectant, Antioxidant, Stabilizer, PHRegulator",
 "hasHeuristicHighThreshold, hasHeuristicLowThreshold, hasHeuristicSource, hasOrigin (natural or synthetic)",
 "SWRL rules written in Protege for the formulation heuristics",
 "By hand, by experts. 279 individuals typed in. Fine at 279, impossible at 12,629",
 "Protege with SWRL",
 "It does not recommend to a shopper. It checks whether a formulation you propose satisfies the heuristics",
 "Yes, via SWRL in Protege","No","None",
 "A case study: they design a moisturising cream with it",
 "No accuracy, no precision, no user study",
 "It is a demonstration, not an evaluation, and they present it as such",
 "The ingredient function names, the split between product properties and ingredient properties, hasOrigin, and above all hasHeuristicSource which records where each RULE came from. That is provenance applied to rules",
 "The whole emulsion science branch: HLB, droplet size, rheology, dosage. Manufacturers never publish it and I will never have it. Also importing the file, since I need 10 of 116 classes",
 "It models how to make a cream. It cannot say whether you can buy one in Beirut, what it costs, or whether the claim on the box came from the manufacturer",
 "Invert their direction. They answer 'given a goal, what goes in the cream'. My 295,991 ingredient mentions with functions attached could answer 'given what is in the cream, what was the formulator trying to do'. Infer formulation strategy from the market, then test it against their heuristics",
 "Section 3.3, part one"])

P.append(["3","B","Formultools (Gabriel)","Read closely",
 "An ontology-based mobile application to support cosmetic product design decisions (Formultools)",
 "A. Gabriel, M. Camargo, S. Morel, J. Serna","2023",
 "Computer Aided Chemical Engineering, ESCAPE-33",
 "Respectable chemical engineering proceedings",NR,
 "Universite de Lorraine, France","https://purl.org/ontocosmetic",
 "Full PDF, in repo/papers/",
 "Turn OntoCosmetic into software a formulator can actually use",
 "Cosmetics formulation experts",
 "The OntoCosmetic knowledge base","Same 279 individuals",
 "The underlying ontology is public; the app is described but I found no download",
 "Yes: the five planes user-centred design method (Garrett 2011), with co-design and iterative usability testing",
 "Inherits OntoCosmetic's 116","Inherits OntoCosmetic's 46",
 "Same as OntoCosmetic","Same as OntoCosmetic","Same SWRL heuristics",
 "Inherited from OntoCosmetic, no new population",
 "Cross-platform mobile app on top of the ontology",
 "Three decisions: screen ingredients by property, select ingredients against several criteria at once (performance, origin, price), and check a proposed formulation against the heuristics. They cite the Analytic Hierarchy Process for the multi-criteria part",
 NR,"No","None",
 "AttrakDiff questionnaire (Lallemand et al. 2015) between design iterations, with non-expert testers",
 "No accuracy figures. They stopped iterating when non-expert testers stopped finding problems",
 "No, and they say so themselves. Their conclusion states expert testing was still future work",
 "The design process: co-design with domain experts, iterate, measure each iteration with a standard instrument. Also AttrakDiff as a cheap named evaluation tool",
 "The mobile app itself. My deliverable is the ontology and the graph, not an application",
 "The most technically serious cosmetics ontology in the literature was never validated with experts. Mine will have a four-layer evaluation",
 "They measured user experience with a standard instrument and reported it. Almost nobody in my review reports any named evaluation instrument. Borrowing one costs an afternoon and puts me ahead of the field",
 "Section 3.3, part two"])

P.append(["4","B","Hansanie & Silva","Read closely",
 "Ontology based Machine Learning Approach for Facial Skincare Products Recommendation",
 "M. Hansanie, T. Silva","2024",
 "IEEE Int. Conference on Image Processing and Robotics (ICIPRoB) 2024",
 "IEEE conference. Decent standing, better than most in this row",
 "2","Sri Lanka",
 "https://consensus.app/papers/details/a76d6c9238dd52a3b3b12bdb93addb5b/",
 "Full PDF, in repo/papers/",
 "Recommend facial skincare by combining a photograph of the user's face with an ontology of products",
 "Consumers, especially with acne",
 "Dermatologist interviews, a survey of 21 people aged 21-30, and facial images for the CNN",
 "21 survey respondents for vocabulary, 24 for evaluation. Product count not reported",
 "No link given anywhere in the paper",
 "No name given. Built top down: general classes first, specific ones underneath",
 NR,NR,
 "Product, TreatmentProduct, AcneControlCleanser, SkinType, OilySkin, KeyIngredient, SalicylicAcid, Person, ProductRecommendation",
 "suitableFor, hasKeyIngredient, hasProductRecommendation, hasAge, hasGender, hasRating",
 "None reported, but Pellet is used for consistency checking",
 "Not clearly reported. The spreadsheet to ontology step is described as a design step, not an automated one",
 "Protege to build, Pellet to reason, Owlready2 to query from Python, Tkinter for the interface",
 "A CNN grades acne severity from a photo. That grade is written into the ontology as a fact about the user. Pellet classifies. Owlready2 pulls the answer out. The image model and the knowledge stay separate, so either can be swapped",
 "Pellet","Indirectly, through Owlready2","None",
 "CNN accuracy on a test set, plus a satisfaction survey of 24 people",
 "CNN accuracy 77.5%. Survey satisfaction 87.5% of 24 people",
 "Partly. The headline 87.5% is user satisfaction, NOT system accuracy. There is no baseline and no ground-truth set of correct recommendations. Quoting this correctly in my thesis is itself a small mark of quality",
 "Three separate ontologies merged, because the three parts change at completely different speeds. A reasoner from day one. Ratings held inside the ontology. Owlready2, since my pipeline is Python",
 "The CNN. I have no facial photographs, no ethical approval to collect any, and my contribution is the product side. Their layered design means vision could be added later without touching anything else",
 "They consulted dermatologists and I have not, so this is a gap in MY favour reversed. But they cannot say a product is stocked in Beirut, costs eleven dollars, and contains a restricted preservative",
 "Their architecture has an empty socket where the sensor plugs in. They put a CNN in it. I could put a BARCODE in it. A shopper in a Beirut pharmacy scans the box and asks 'does this suit me, and is it cheaper next door'. That uses my price and availability columns, needs no ethics approval and no image dataset",
 "Section 3.1, lead with this"])

P.append(["5","B","Abesova (VU Amsterdam)","Read closely",
 "Skincare Ontology for Personalised Recommendation",
 "S. Abesova, K. Hajkova, Y. Ramadan, M. Zdych","2023",
 "Vrije Universiteit Amsterdam, Knowledge and Data course, Group 31",
 "A STUDENT PROJECT. Not peer reviewed. I must say this when I cite it",
 "0","Vrije Universiteit Amsterdam, Netherlands",
 "In repo/papers/","Full PDF, in repo/papers/",
 "Recommend a full skincare routine from four user inputs: skin type, skin tone, country, and how complicated a routine they will tolerate",
 "Consumers",
 "Sephora product and review data scraped to CSV, a second CSV of countries with Sephora shops, and DBpedia",
 "36 classes, 6 object properties, 6 data properties",
 "Not stated as published",
 "Yes: middle out. Start with concepts you are sure of, work outward in both directions. Explicitly iterative",
 "36","6 object, 6 data",
 "Category (Cleanser, Moisturizer, Treatment; Treatment splits into Exfoliant with Chemical and Physical, Serum, Toner; SPF sits under Moisturizer), Product with four skin-type subclasses, Skin Type, Skin Tone with nine values, Brand, Country, Rating Stars, Review Id",
 "hasBrand, hasCategory, hasSkinType, hasSkinTone, aboutProduct, hasReviewId, hasRating, hasOilyScore, hasDryScore, hasNormalScore, hasCombinationScore, hasSephoraWebPage",
 "YES, and this is the single most important idea in my whole review. OilySkinProducts is DEFINED as 'hasOilyScore value 5'. They never tag a product; the reasoner works out membership",
 "OntoRefine turned the scraped CSV into RDF by mapping columns to classes. This is a real tool, not a script",
 "OntoRefine, GraphDB, DBpedia via an external SPARQL endpoint",
 "It is a set of SPARQL queries, not code. Class restrictions put products into skin-type classes automatically, then queries assemble a routine",
 "Yes, through GraphDB's class restrictions","YES, it IS the mechanism",
 "DBpedia. dbr:Czech_Republic gave them the country AND the latitude/longitude of its capital for a map, without typing any of it",
 "One worked example. No metrics",
 "9 recommended products for one user, three per category",
 "No. One example, no metrics, and they admit the interface was rushed and shows raw URIs instead of product names",
 "THE DEFINED CLASS. State the rule once instead of tagging 4,000 rows. Also OntoRefine as a population tool, and DBpedia linking to get data free",
 "Their reliance on review scores as the basis for class membership. Mine will rest on the formula",
 "Their limitation 3, in their own words: 'class restrictions based on ingredients could be developed. This would ensure a more symbolic and chemical approach, compared to the statistical one that is currently employed.' MY CONTRIBUTION IS WRITTEN AS FUTURE WORK IN THEIR PAPER",
 "They pulled PLACE out of DBpedia and got a map. I can pull CORPORATE OWNERSHIP out of Wikidata. My 1,463 brands belong to far fewer parent companies. That gives me market concentration in Lebanon, detection of two prices from one manufacturer, and the question a shopper in a currency crisis actually asks: is there a cheaper equivalent from the same maker",
 "Section 3.4, the mechanism section"])

P.append(["6","B","bit-Tech 2025","URGENT - get the PDF",
 "Personalized Skincare Recommendation System Based on Ontology and User Preferences",
 "Not yet confirmed - I only have the abstract","2025",
 "bit-Tech, Komunitas Dosen Indonesia",
 "Regional Indonesian journal. Modest standing but the work is directly comparable to mine",
 NR,"Indonesia",
 "https://jurnal.kdi.or.id/index.php/bt/article/view/2857",
 "ABSTRACT AND PUBLISHER PAGE ONLY. I have not read the full paper. This is my closest competitor so I must fix that",
 "Traditional content-based and collaborative filtering miss the semantic links between skin types, concerns and ingredients. They use an ontology to capture them",
 "Indonesian skincare consumers",
 "Web scraping of Sociolla, Beautyhaul and SKINSORT. Note: Skinsort is the same global source I used",
 "Over 3,800 products and over 28,000 ingredients",
 "Not stated in the abstract. CHECK when I get the PDF",
 "YES, METHONTOLOGY, named explicitly",
 "12","More than 25 object properties",
 "User, Product, Brand, Product Category, Allergen Type, Ingredient, Benefit, Formulation Trait, Key Ingredient, Skin Concern, Skin Type, What It Does",
 "Not detailed in the abstract",
 "Not stated in the abstract",
 "Web scraping into the ontology. Whether a mapping language was used is not stated. FIND OUT",
 "Apache Jena Fuseki",
 "SPARQL over the ontology with semantic reasoning, per the abstract",
 "Via Jena Fuseki inference","Yes","None mentioned",
 "Not clear from the abstract","Not clear from the abstract",
 "Cannot assess without the full paper",
 "Two class names I would not have thought of: Formulation Trait and What It Does. That split IS my evidence problem in class form. What It Does is the marketing claim; Formulation Trait is the physical property. One is asserted by a seller, the other is derivable from the formula",
 "Their market and their allergen handling",
 "Four things: they cover Indonesia, I cover Lebanon where availability itself is uncertain; their allergen class is locally defined, mine links to the statutory EU register of 28,573 entries; they model no price, availability or provenance; and they have 3,800 products against my 12,629",
 "Adopt their two class names but attach my evidence levels to What It Does and my CosIng derivation to Formulation Trait. The result is a model that states openly which half of a product description is advertising",
 "Section 3.5, the closest competitor"])

P.append(["7","B","Utari (JELIKU)","Skim only",
 "Pengembangan Ontologi Semantik Pada Domain Produk Kosmetik (Developing a Semantic Ontology in the Cosmetic Product Domain)",
 "N. N. R. D. Utari et al.","2023",
 "JELIKU, Jurnal Elektronik Ilmu Komputer Udayana",
 "Small regional journal","0","Universitas Udayana, Indonesia",
 "https://consensus.app/papers/details/9f025755693f50298a45b5c165537fbc/",
 "Abstract only",
 "Too many cosmetic products on the market, so buyers cannot choose. Use a semantic ontology to help",
 "Indonesian cosmetics buyers","Cosmetic product data, source not specified in the abstract",
 "3 classes, 5 object properties, 62 individuals","Not stated",
 "YES, METHONTOLOGY","3","5 object properties",
 "Not detailed in the abstract","Not detailed in the abstract","None stated",
 "Not stated","Not stated",
 "Not a recommender as such. Evaluated by running SPARQL queries",
 NR,"Yes","None",
 "SPARQL queries returning appropriate results","No metrics beyond 'queries gave appropriate results'",
 "It is a proof of concept and does not claim more",
 "Almost nothing technically. Its value is as a scale comparison",
 "Everything else","62 individuals against my roughly 1.8 million triples. Putting both in one table makes my scale visible without me having to claim anything",
 "This plus Mahadewi shows the Indonesian group is building a SERIES, so the bit-Tech paper is part of a programme, not a one-off. That is worth knowing about my closest competitor",
 "Comparison table only"])

P.append(["8","B","Mahadewi (JELIKU)","Skim only",
 "Penerapan Algoritma Slope One dalam Collaborative Filtering (Body care product recommendation using ontology and collaborative filtering)",
 "I. A. Mahadewi et al.","2024",
 "JELIKU, Jurnal Elektronik Ilmu Komputer Udayana",
 "Small regional journal","0","Universitas Udayana, Indonesia",
 "https://consensus.app/papers/details/a7956ce9d21f5d6b806688eb6cec7cb8/",
 "Abstract only",
 "Body care product information online is often irrelevant or inaccurate, so build a recommender on an ontology knowledge base",
 "Indonesian body care buyers","Body care product data mapped into an ontology",
 "Not stated","Not stated","YES, METHONTOLOGY. System built with Prototyping",
 NR,NR,"Not detailed","Not detailed","None stated",
 "Not stated","Not stated",
 "Collaborative filtering (Slope One algorithm) over an ontology knowledge base",
 NR,"Not stated","None",
 "Two instruments: System Usability Scale (SUS) and Mean Absolute Error (MAE)",
 "SUS 82.344 (good). MAE 0.3556 (closer to 0 is better)",
 "Reasonable for what it claims. Two named instruments is more than most papers in my review manage",
 "The two evaluation instruments. SUS in particular is standard, cheap and would strengthen any interface I build",
 "Slope One and collaborative filtering. I have no user ratings matrix",
 "They still model no regulator, no provenance and no availability",
 "They report MAE and SUS. In a field where a 137-citation review found that NONE of 28 studies described an evaluation methodology, simply naming your instruments is a differentiator",
 "Comparison table, evaluation column"])

P.append(["9","B","TOXIN KG","Read closely",
 "The TOXIN knowledge graph: supporting animal-free risk assessment of cosmetics",
 "S. Sepehri et al.","2025",
 "Database: The Journal of Biological Databases and Curation, Oxford University Press",
 "STRONG. Oxford Academic, peer reviewed, open access. Better than every skincare recommendation paper in my review",
 "4","Vrije Universiteit Brussel and partners, Belgium",
 "https://doi.org/10.1093/database/baae121  |  live at https://toxin-search.netlify.app/",
 "Full article text",
 "The EU banned animal testing for cosmetics but validated replacements are missing. Make existing safety data reusable so risk can be assessed without animals",
 "Toxicologists and risk assessors",
 "Safety data on annexed cosmetic ingredients from Scientific Committee on Consumer Safety opinions issued 2009-2019. Same committee that produces the CosIng annexes I already use",
 "88 cosmetic ingredients, of which 53 affect at least one liver toxicity parameter",
 "YES. Live and searchable at toxin-search.netlify.app",
 "Not named as a methodology, but the process is carefully documented",
 "Inherited from TXPO","Inherited from TXPO",
 "Reuses the ToXic Process Ontology (TXPO) from the OBO Foundry, which itself pulls in Gene Ontology, ChEBI, Disease Ontology, Cell Ontology, UniProt and others",
 "Not detailed, but they add SMILES notation to standardise chemical identity",
 "Reliability of each study is scored automatically with ToxRTool",
 "CURATED SPREADSHEETS CONVERTED TO RDF USING R2RML. This is the single most useful sentence in the paper for me. Toxicologists transcribe into Excel; computer scientists have read-only access and generate the RDF",
 "R2RML, TXPO, OECD QSAR Toolbox, Ontodia for visualisation",
 "It is not a recommender. It is a retrieval and assessment tool: filter for ingredients linked to liver toxicity, then follow the chain to the adverse outcome",
 "Not stated","Yes","OBO Foundry ontologies, KEGG, Reactome, UniProt, all linked BY IRI rather than copied",
 "Demonstration through use cases",
 "88 ingredients loaded; 53 identified as affecting a liver parameter in 90-day studies",
 "Yes. It claims to be a retrieval tool and it demonstrates retrieval. No overreach",
 "THREE THINGS. R2RML for population, which is now my chosen method. NAMED GRAPHS per source so the origin of any statement is traceable, which is my evidence-level idea at the storage layer. And linking out by IRI instead of copying data",
 "The toxicology depth: hepatotoxic mechanisms, KEGG pathways, gene products. I model consumer products, not mechanisms of harm",
 "IT HAS NO PRODUCTS. It has the regulation and the science with nothing on a shelf. Every skincare ontology has products and no regulation. Nobody has both. That intersection is my thesis",
 "They model the EVIDENCE BEHIND a restriction. I model only the restriction itself as a pointer like Annex V/29. Link the two and a product on a Beirut shelf carries a traceable path all the way to the SCCS opinion that limits phenoxyethanol to 1%. No consumer-facing system anywhere does that, and the link is one owl:sameAs per ingredient",
 "Section 3.6, the regulatory precedent"])

P.append(["10","B","HaCKG","Read closely",
 "Halal or Not: Knowledge Graph Completion for Predicting Cultural Appropriateness of Daily Products",
 "V. T. Hoang et al.","2025","IEEE Access",
 "IEEE Access. Open access, indexed, respectable","8","South Korea",
 "https://consensus.app/papers/details/033951ebc555534aac4c54bad403585a/",
 "Abstract only",
 "Existing halal prediction looks at ingredients one at a time and misses the relationships between cosmetics and their components",
 "Muslim consumers, and cosmetics retailers in Muslim-majority markets",
 "A cosmetics dataset of products, ingredients and their properties","Not stated in the abstract",
 "Not stated in the abstract",
 "None stated. This is a machine learning paper that happens to build a KG",
 NR,NR,
 "Cosmetics, Ingredients and their properties as entities in a knowledge graph",
 "Not detailed in the abstract","None. The learning is in the network, not in axioms",
 "Not stated","A pre-trained relational graph attention network with residual connections, fine-tuned on downstream cosmetic data",
 "The graph is embedded by a relational graph attention network which learns high-order relations between cosmetics and ingredients, then fine-tuned to predict halal status",
 "None. Neural, not symbolic","Not stated","None stated",
 "Benchmark comparison against state-of-the-art baselines on halal prediction",
 "Reported as outperforming baselines. Exact figures not in the abstract",
 "Appears sound for a machine learning paper, but this is a prediction task with no reasoning and no citation of an authority",
 "Their own argument, which helps me: ingredient-by-ingredient methods 'ignore the high-order and complex relations between cosmetics and ingredients'. That is an argument FOR my graph, made by someone else. Also, it proves a cosmetics KG is a publishable object",
 "The graph neural network. I have no interaction data and my contribution is the resource",
 "They PREDICT halal status with a learned model. I would DERIVE it from INCI plus a curated list and cite the derivation. Prediction gives a probability; derivation gives a reason and a source",
 "Use them as an EVALUATION TARGET rather than a competitor. Where my symbolic derivation and their learned prediction agree, that is mutual validation. Where they disagree, the disagreement set is a research result. Same design I proposed for Lee et al., and having two candidates turns a trick into a method",
 "Section 5, hybrid track. THIS WEAKENS MY HALAL CLAIM - be honest about it"])

P.append(["11","B","CCIBP","Check in sprint 2",
 "CCIBP: a comprehensive cosmetic ingredients bioinformatics platform",
 "L. Gong et al.","2023","Bioinformatics, Oxford University Press",
 "STRONG. Bioinformatics is a leading journal","2","China",
 "http://design.rxnfinder.org/cosing/",
 "Abstract only",
 "Understand the physicochemical properties, metabolic pathways, toxicology and safe concentrations of cosmetic molecules in one place",
 "Cosmetic researchers and formulators",
 "Regulations from major world regions, physicochemical properties, human metabolic pathways, plant information for natural products",
 "Not stated in the abstract","YES, publicly available at the URL",
 "None stated","Not an ontology as such, a platform","Not applicable",
 "Not applicable, it is a database not an ontology","Not applicable","None",
 "Curated from regulatory and chemical sources","Chemoinformatics and bioinformatics tooling",
 "Not a recommender. Supports formulation analysis and efficacy component analysis",
 "None","Not stated","Links plant information to natural products",
 "Presented as a resource, demonstrated through use",
 "Not stated in the abstract","It claims to be a platform and it is one",
 "Possibly a SECOND ingredient source. It covers regulations beyond the EU, which matters if Lebanon follows any non-EU framework for some ingredient classes. Also, a resource paper in a strong journal, which supports my argument that resource construction is a legitimate contribution",
 "The synthetic biology and biosynthesis material, which is irrelevant to retail",
 "It has ingredients and no products, same as TOXIN",
 "If Lebanon's regulation is not purely EU-aligned, this is where the non-EU annexes live. Worth 30 minutes in sprint 2 to check whether it adds anything my CosIng link does not already give me",
 "Toolkit, ingredient sources"])

P.append(["12","B","CosIng-KG","CHECK FIRST - could save weeks",
 "cosing-kg: the European Commission CosIng database converted to RDF",
 "biobricks-ai","n/a","GitHub repository, serving kg.toxindex.com",
 "Not a paper. An artefact",NR,"biobricks-ai",
 "https://github.com/biobricks-ai/cosing-kg",
 "Repository description only",
 "Make CosIng available as principled RDF",
 "Anyone building on cosmetic ingredient regulation",
 "CosIng itself, the same register I already use","28,573 CosIng entries",
 "YES, on GitHub","Not stated",NA,NA,
 "Whatever CosIng's structure maps to","Not inspected yet","None",
 "Converted from the CosIng release","Not inspected yet",NA,"None",NA,"CosIng identifiers",
 NA,NA,NA,
 "POSSIBLY MY ENTIRE INGREDIENT LAYER, free and citable. If its IRIs and licence work for me, I reuse it and my products link straight to its ingredient IRIs",
 "Nothing yet, I have not inspected it",
 "If it is NOT usable, that is equally valuable: my own conversion then becomes a stated contribution rather than an assumption",
 "This is the highest-value 30 minutes available to me right now. Two outcomes and both are good. Do it before writing any Turtle",
 "Sprint 2 action item, and a footnote in the methodology"])

P.append(["13","B","DermO","Check in sprint 2",
 "DermO: an ontology for the description of dermatologic disease",
 "Multiple authors, University of Birmingham","2016",
 "Journal of Biomedical Semantics",
 "Solid specialist journal, and the ontology is properly published",NR,
 "University of Birmingham, UK",
 "https://bioportal.bioontology.org/ontologies/DERMO",
 "Abstract and BioPortal record",
 "Give dermatologic disease a formal, shareable terminology",
 "Clinicians and biomedical informaticians",
 "Expert-authored terminology, built manually by domain experts",
 "More than 3,000 terms in 20 upper-level categories",
 "YES. GitHub plus BioPortal, in OBO flat file and OWL 2",
 "Follows biomedical ontology conventions; aligned to ICD-10",
 "3,000+ terms",NR,
 "Disease entities categorised by anatomical location, heritability, affected cell or tissue type, and cause",
 "Not inspected in detail","Not applicable",
 "Manually, by domain experts","OBO tooling, Protege",
 "Not a recommender. A terminology","Not stated","Via BioPortal",
 "Aligned to ICD-10 and integrated with other disease and phenotype ontologies",
 "Expert review and cross-ontology mapping",
 "3,000+ terms, 20 categories","Yes, for a terminology resource",
 "MY CONCERN VOCABULARY. Right now acne, dryness, redness and hyperpigmentation are free text I invented. If they link to DermO they become entities a dermatologist can check, aligned to ICD-10",
 "The clinical disease depth. I am not diagnosing anything",
 "It has no products. But this one repairs a weakness in MY work rather than theirs",
 "I identified that nobody clinical has reviewed my vocabulary, and I cannot get a dermatologist quickly. I can ALIGN TO ONE THAT DERMATOLOGISTS ALREADY BUILT. Beyond that: DermO categorises by anatomical location, so aligning products to body site lets me ask which products cover which site, and where a routine leaves a site uncovered. No retail taxonomy can do that",
 "Section 3.6, and sprint 2 action"])

P.append(["14","B","D3X","Skim only",
 "Dermoscopy Differential Diagnosis Explorer (D3X) Ontology to Aggregate and Link Dermoscopic Patterns to Differential Diagnoses",
 "Multiple authors","2024","JMIR Medical Informatics 12:e49613",
 "Good specialist journal, peer reviewed",NR,"Not recorded",
 "https://medinform.jmir.org/2024/1/e49613",
 "Abstract only",
 "Link dermoscopic patterns to the diagnoses they suggest",
 "Dermatologists",
 "Dermoscopic patterns and differential diagnoses","Not stated in the abstract",
 "Described as a development and usability study; check availability",
 "Not stated",NR,NR,"Dermoscopic patterns, differential diagnoses",
 "Not detailed in the abstract","Not stated","Not stated","Not stated",
 "Not a recommender","Not stated","Not stated","Dermatology terminologies",
 "A USABILITY STUDY. This is the point for me",
 "Not stated in the abstract","Appears appropriate for its claim",
 "The EVALUATION DESIGN. Ontologies in this space are evaluated by expert review and task completion, not by precision and recall. Knowing that saves me from promising an evaluation I cannot deliver",
 "The dermoscopy domain entirely",
 "No products, no market, no regulation",
 "It tells me what a credible 2024 dermatology ontology evaluation looks like. Competency questions plus a usability study, not accuracy figures. That is the shape my evaluation chapter should take",
 "Evaluation chapter, method justification"])

P.append(["15","B","Halal flavouring ontology","Read the pattern",
 "Development of Flavouring Ontology for Recommending the Halal Status of Flavours",
 "Multiple authors","2024",
 "Journal of Information Science Theory and Practice 12(2)",
 "Modest but peer reviewed",NR,"Malaysia",
 "https://accesson.kr/jistap/v.12/2/22/42865",
 "Abstract only",
 "Trace the halal status of flavour ingredients so a manufacturer can predict a product's status",
 "Food manufacturers and halal certifiers",
 "Flavour ingredients and halal certification references. Domain experts from JAKIM (Malaysian Dept of Islamic Development) were consulted",
 "Not stated","Not stated",
 "Not named","Not stated","Not stated",
 "Halal certification process, halal concept, reference sources, traceability",
 "Not detailed in the abstract","Not stated",
 "Not stated","Not stated",
 "Status is inherited: a product's halal status follows from its ingredients' statuses according to a named authority",
 "Not stated","Not stated","None",
 "Expert consultation with the certifying body","Not stated",
 "Appears appropriate for a conceptual framework",
 "THE THREE-PART PATTERN: ingredient, AUTHORITY, status, with the authority as a first-class entity rather than an attribute. Swap halal certification for EU Annex restriction and it is my problem exactly",
 "The halal food domain specifics",
 "Nothing directly. This is a pattern donor, not a competitor",
 "Because the authority is modelled separately, I can say 'Phenoxyethanol is restricted under Annex V/29 ACCORDING TO the European Commission' and leave room for a second authority later. For Lebanon that is realistic, since local regulation is not identical to EU regulation. This one design choice future-proofs the whole regulatory layer",
 "Section 3.6, pattern source"])

P.append(["16","B","Klaschka","Read closely - free finding",
 "Naturally toxic: natural substances used in personal care products",
 "U. Klaschka","2015","Environmental Sciences Europe",
 "Good peer-reviewed journal, and heavily cited","107","Ulm University, Germany",
 "https://consensus.app/papers/details/c46f8b2f2d295088a0e529d31143952c/",
 "Abstract only",
 "Which natural substances in personal care products are actually hazardous, and how does EU law handle them",
 "Regulators, and anyone who believes natural means safe",
 "The INCI list and the EU classification and labelling inventory",
 "1,358 natural substances in INCI. 655 of them in the EU C&L inventory",
 "The underlying registers are public",
 "Not an ontology paper",NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,
 "REACH and CLP regulatory instruments",
 "Regulatory analysis and classification counting",
 "56% of the 655 classified as hazardous. 38% for human health hazards. 35% for skin and eye effects. 53 substances classified as carcinogenic, mutagenic or toxic to reproduction",
 "Yes, and it also flags inconsistencies in the classifications themselves",
 "PEER-REVIEWED EVIDENCE, 107 citations, that natural does not mean safe. That arms my free_from column and every 'natural' and 'clean' claim in my product descriptions",
 "The environmental toxicology detail",
 "They have the hazard classifications and no products. I have 11,802 formulas AND the marketing claims AND the register",
 "A COMPUTABLE RESEARCH QUESTION NOBODY ELSE CAN ANSWER: across 12,629 products, do products marketed as natural contain FEWER hazardous ingredients than products that are not? I already hold all three pieces. No new data collection. That is a finding sitting in my existing dataset waiting to be run",
 "Section 3.6, and a results chapter of its own"])

P.append(["17","B","MVFM","Interesting, low priority",
 "Predictive Analysis of Cosmetic Formulations: A Multi-Vector INCI Mapping Methodology for Objective Product Assessment",
 "R. Plonsak","2026","Journal of Applied Cosmetology",
 "Small journal, very recent","0","Not recorded",
 "https://consensus.app/papers/details/ea07c5e70d905e3694e09206096364f2/",
 "Abstract only",
 "EU law requires claims not to mislead but does not require them to be grounded in composition. A product sold as barrier-restoring need not contain barrier lipids. There is no standard way to check from the label alone",
 "Practitioners and dermatologists",
 "INCI lists from commercial products","Three commercial products as a test case",
 "The method is described in the paper","Not an ontology",NA,NA,NA,NA,NA,
 "Manual scoring by one evaluator","None",
 "Finds the first regulated preservative or fragrance marker in the INCI list and uses its POSITION as a boundary. Ingredients above it are scored on three vectors: Hydration, Lipid, Structural, each 0 to 3",
 "None","No","None",
 "Applied to three products by one evaluator",
 "Segmentation worked on all three. One product marketed as anti-aging scored H=4 L=7 S=6, a lipid-dominant profile more like a texture cream. Two regulated fragrance allergens found in its functional zone",
 "No, and the author says so: three products, one evaluator, and larger validation and inter-rater reliability still to do",
 "THE USE OF INCI POSITION AS A SIGNAL. This is why my ontology must reify IngredientListing with a position number. Position is concentration order, the only concentration signal a consumer ever gets",
 "The manual three-vector scoring. It is subjective and unvalidated",
 "They tested three products by hand. I could run their method across 11,802 formulas automatically and report inter-product statistics, which is the validation they say is missing",
 "Their core finding is that a marketing claim can be unsupported by composition. That is EXACTLY my evidence-level argument, arrived at from the formulation side. Running their method at scale on my data would produce the first large-sample test of whether cosmetic claims are compositionally grounded. That is a paper",
 "Section 3.6, and possible future work"])

P.append(["18","B","Landau INCI guide","Background reading",
 "Hacking the International Nomenclature of Cosmetic Ingredients List: How to Read Ingredients in Cosmetic Products and What Is Important for a Dermatologist to Know",
 "M. Landau et al.","2023","Dermatologic Clinics, Elsevier",
 "Good clinical review journal","4","Israel",
 "https://consensus.app/papers/details/ae9df404874a59bb9266b3e1d1bf4821/",
 "Abstract only",
 "Dermatologists are asked to recommend cosmetics but are rarely taught to read an ingredient list",
 "Dermatologists",
 "Review of INCI structure and formulation principles",NA,NA,
 NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,
 "Narrative review",NA,"It is a review and does not overclaim",
 "A CITABLE SOURCE for how INCI lists are structured and read. Useful in my methods chapter when I explain why parsing them is hard",
 "Nothing to leave, it is background",
 "It confirms that even dermatologists find INCI hard to read, which is an argument for automating the interpretation",
 "If dermatologists are not taught to read INCI, then a tool that reads it FOR them has a professional user, not just a consumer one. That widens who my ontology is for, and pharmacists in Beirut are a realistic first audience",
 "Introduction, motivation"])

# --------------------------------------------------------------- TRACK C
P.append(["19","C","Middleton","Read closely - cite first",
 "Ontological User Profiling in Recommender Systems",
 "S. E. Middleton, N. R. Shadbolt, D. C. De Roure","2004",
 "ACM Transactions on Information Systems 22(1) 54-88",
 "THE BEST VENUE IN MY ENTIRE REVIEW. ACM TOIS, Q1",
 "In the thousands","University of Southampton, UK",
 "https://doi.org/10.1145/963770.963773","Abstract and secondary sources",
 "Recommend academic papers by describing what a user is interested in using an ontology rather than a bag of keywords",
 "Researchers",
 "Academic paper databases, plus unobtrusively monitored user behaviour and relevance feedback",
 "Two deployed systems, Quickstep and Foxtrot",
 "The systems are described in the paper",
 "Not named as a methodology",NR,NR,
 "A research paper topic ontology","Topic hierarchy relations","Ontological inference over the topic hierarchy",
 "Papers classified into ontological classes automatically","Their own systems",
 "User behaviour builds a profile expressed in ontology terms. Ontological inference extends it up the hierarchy. Collaborative recommendation then finds papers seen by similar people on the user's current topics",
 "Yes, ontological inference","Predates widespread SPARQL","Used an external publication database to bootstrap",
 "Deployed experiments with real users over time",
 "Three findings, all positive: inference improves profiling, external knowledge bootstraps the system, and profile visualisation improves accuracy",
 "Yes. Real deployments, real users, and the findings are stated as findings rather than as superiority claims",
 "ALL THREE FINDINGS ARE MY THREE ARGUMENTS. Inference up a hierarchy (my concerns have one). External knowledge bootstraps a cold start (a new Beirut user has no history but the ontology already knows what suits combination skin). Profile visualisation (a user can see and correct 'the system thinks your skin is oily')",
 "The collaborative filtering half. I have no user base",
 "They had no regulatory grounding and no product safety dimension, because papers are not dangerous",
 "Their unobtrusive monitoring, applied to Lebanon, is not browsing history. It is THE RECEIPT. Beirut pharmacies are small and repeat custom is the norm. A profile built from what someone actually re-bought is more honest than one built from clicks, and my shops_in_lebanon and price columns are the start of a purchase-side model no global system has",
 "Section 4.1, opens the chapter"])

P.append(["20","C","FoodKG","Read closely - closest analogue",
 "FoodKG: A Semantics-Driven Knowledge Graph for Food Recommendation",
 "S. Haussmann, O. Seneviratne, Y. Chen, Y. Ne'eman, J. Codella, C. Chen, D. L. McGuinness, M. J. Zaki",
 "2019","The Semantic Web, ISWC 2019, Springer LNCS",
 "ISWC is the top semantic web conference. Rank A","Several hundred",
 "Rensselaer Polytechnic Institute and IBM Research, USA",
 "https://doi.org/10.1007/978-3-030-30796-7_10  |  https://foodkg.github.io/",
 "Abstract, project site and secondary sources",
 "Recipes and food information are scattered across the web. Organise diet knowledge into one graph so people can eat more healthily",
 "Consumers wanting to eat well, and researchers",
 "Recipes, nutrition data, food taxonomies, and links into existing ontologies",
 "A large integrated graph. Millions of triples",
 "YES, published at foodkg.github.io",
 "Not named as a formal methodology, but construction is described as a contribution",
 "Not stated as a single number","Not stated as a single number",
 "Recipes, ingredients, nutrients, food taxonomy categories",
 "Links between recipes, their ingredients and nutrition facts","Constraint handling for allergies",
 "Integration of several existing datasets and ontologies into one graph, described step by step",
 "Semantic web stack, SPARQL services",
 "A SPARQL-based service finds recipes you can make from ingredients you have, while respecting HARD CONSTRAINTS such as allergies. Also powers a question-answering agent",
 "Not the focus","YES, it is the service layer",
 "Links into existing food and nutrition ontologies",
 "Demonstrated through several applications built on the graph",
 "Not framed as accuracy. The contribution is the resource and its uses",
 "Yes. It claims to be a resource and it is one, published and reusable",
 "FOUR PRACTICES. Construction described as a contribution in its own right. A stated MAINTENANCE PLAN, which no skincare ontology has. Multiple applications on one graph, so the graph is infrastructure not an app. And HARD CONSTRAINTS, not preferences: an allergy is a filter, not something to weigh",
 "The recipe domain specifics",
 "Nothing. This is the model to follow, not a competitor. Its existence proves a top venue accepts graph construction as the contribution",
 "It powers a QUESTION ANSWERING agent, not a ranked list. A Lebanese user does not want 12,629 products ranked. They want to ask 'something for dry skin, under fifteen dollars, that I can actually buy in Hamra'. That is a constrained question and all four constraints are real columns in my data. Framing my system as constrained QA rather than ranking is both more useful and more defensible, because constraint satisfaction is where symbolic methods genuinely beat neural ones",
 "Section 4.2, the structural analogue"])

P.append(["21","C","Constrained QA over FoodKG","Read closely",
 "Personalized Food Recommendation as Constrained Question Answering over a Large-scale Food Knowledge Graph",
 "Y. Chen, A. Subburathinam, C.-H. Chen, M. J. Zaki","2021","WSDM / arXiv 2101.01775",
 "Strong. WSDM is a leading conference","Over 100",
 "Rensselaer Polytechnic Institute and IBM, USA",
 "https://arxiv.org/abs/2101.01775","Abstract",
 "Turn food recommendation into answering a question with constraints rather than ranking a list",
 "Consumers with dietary constraints",
 "The FoodKG graph","Large-scale food knowledge graph",
 "Builds on published FoodKG","Not an ontology construction paper",NA,NA,NA,NA,NA,
 "Inherits FoodKG","Question answering over a KG",
 "The user's requirements become constraints in a question; the system answers over the graph subject to those constraints",
 "Not the focus","Yes, over the KG","FoodKG's existing links",
 "Benchmarks on constrained recommendation",
 "Reported as effective; exact figures not in the abstract",
 "Appears sound",
 "THE FRAMING. Recommendation as constrained question answering. My four hard constraints are skin suitability, allergen absence, price ceiling and Lebanese availability",
 "The food specifics",
 "They have no regulatory authority behind their constraints. My allergen constraint cites EU law",
 "This is the paper that tells me what my SYSTEM should be, if I build one. Not a recommender that ranks. A question answerer that filters. It also makes my evaluation easier, because a constraint is either satisfied or it is not, which is checkable without a user study",
 "Section 4.2, system framing"])

P.append(["22","C","Di Noia / Ostuni","Read closely",
 "Linked Open Data to Support Content-based Recommender Systems (and the RecSys 2013 and WIMS 2015 papers in the same line)",
 "T. Di Noia, R. Mirizzi, V. C. Ostuni, D. Romito, M. Zanker","2012-2015",
 "I-SEMANTICS 2012, RecSys 2013, WIMS 2015",
 "RecSys is the top recommender systems conference","Several hundred across the line",
 "Politecnico di Bari, Italy",
 "https://doi.org/10.1145/2797115.2797128","Abstracts and secondary sources",
 "Recommend items using the links they have in the linked open data cloud, when you do not have rich item descriptions",
 "Content-based recommender builders",
 "DBpedia, Freebase, LinkedMDB. Movies","Standard movie benchmark datasets",
 "Methods published; datasets are public",
 "Not an ontology construction paper",NA,NA,
 "Uses DBpedia's existing classes","DBpedia predicates as vector dimensions","None",
 "Uses existing linked data","SPARQL against DBpedia endpoints",
 "A semantic vector space model. Each item becomes a vector whose dimensions are its LINKS in the LOD cloud rather than its words. Two films are similar if they share a director, a genre, a period, a country",
 "No","YES, central to the method","DBpedia, Freebase, LinkedMDB",
 "Offline evaluation on movie benchmarks",
 "Reported as promising. Precision and recall on standard splits",
 "Reasonably. They describe results as promising rather than conclusive, and name their open problems",
 "PRODUCT SIMILARITY WITHOUT ANY RATINGS. Two products are similar if they share ingredient functions, a restriction profile, a concern, a price band, a country. My rating column is only 51% complete and I have no user history, so this is the only content-based similarity available that uses everything I collected",
 "The movie domain and the collaborative components",
 "They enrich thin items with external data. My items are unusually rich already",
 "INVERT IT. They used LOD to enrich the ITEMS. I should use it to enrich the SHOPS. Wikidata and OpenStreetMap know where Beirut pharmacies are. A graph that knows a product is available fifteen minutes' walk away is doing something no cosmetics recommender has done, and geography is the one dimension where a Lebanese thesis has data nobody else can get",
 "Section 4.3, similarity method"])

P.append(["23","C","AliCoCo","Read closely - biggest idea",
 "AliCoCo: Alibaba E-commerce Cognitive Concept Net",
 "X. Luo, L. Liu, Y. Yang, L. Bo, Y. Cao, J. Wu, Q. Li, K. Yang, K. Q. Zhu","2020",
 "ACM SIGMOD 2020",
 "SIGMOD. Rank A*, one of the very best database venues","Several hundred",
 "Alibaba Group and Shanghai Jiao Tong University, China",
 "https://doi.org/10.1145/3318464.3386132  |  https://github.com/alicogintel/AliCoCo",
 "Abstract, repository and secondary sources",
 "Existing product ontologies describe what a product IS. Shoppers think in terms of what they NEED. That gap stops shopping being intelligent",
 "E-commerce platforms and their shoppers",
 "Alibaba's own catalogue and user behaviour, at national scale",
 "Very large. Millions of concepts and items","Partially, via the GitHub repository",
 "Not named, but the design principle is explicit",
 "Large","Large",
 "The key move: E-COMMERCE CONCEPTS, meaning user needs, as FIRST-CLASS ENTITIES. Not 'moisturiser' but 'outdoor barbecue', 'keeping warm in winter', 'preparing for a beach holiday'",
 "Relations connecting needs to items, categories and attributes",
 "Not the focus. The contribution is the representation",
 "Semi-automatic extraction at scale from catalogue and behavioural data",
 "Alibaba's internal infrastructure",
 "Needs are matched to items through the concept net, so a shopper's stated situation retrieves products that serve it rather than products that match keywords",
 "Not stated","Not stated","Their own concept net",
 "Deployed at Alibaba scale, with online metrics",
 "Reported improvements in the deployed system",
 "Yes, and unusually it is validated by production deployment rather than an offline split",
 "THE ONE IDEA. My concerns column is already a user need sitting in a product schema pretending to be an attribute. Promote it. A need entity can be satisfied by a ROUTINE of several products, can carry a budget, can carry a season, and can be constrained by availability. A product attribute can do none of that",
 "The scale and the behavioural extraction. I have no behavioural data",
 "They model needs but have no regulatory grounding and no provenance. Nothing in AliCoCo says who claimed what",
 "LEBANESE NEEDS ARE NOT GLOBAL NEEDS. 'A routine under twenty dollars a month.' 'Products that do not need refrigeration.' 'Something for a bride.' 'A routine I can buy entirely in one pharmacy.' These are real needs shaped by a real economy and every one is expressible in my data because I have lira prices, shop-level availability and multi-shop comparison. IF I WANT ONE IDEA THAT MAKES THIS THESIS SPECIAL RATHER THAN COMPETENT, IT IS THIS",
 "Section 4.4, and the novelty claim"])

P.append(["24","C","Guo survey","Read for structure",
 "A Survey on Knowledge Graph-Based Recommender Systems",
 "Q. Guo, F. Zhuang, C. Qin, H. Zhu, X. Xie, H. Xiong, Q. He","2022",
 "IEEE Transactions on Knowledge and Data Engineering 34(8) 3549-3568",
 "IEEE TKDE. Q1, top journal","Over a thousand",
 "Chinese Academy of Sciences, Microsoft Research Asia, Rutgers",
 "https://arxiv.org/abs/2003.00911",
 "Abstract and the arXiv preprint",
 "Organise the field of knowledge-graph-based recommendation into a usable taxonomy",
 "Recommender systems researchers","A survey of the literature","Hundreds of papers surveyed",
 "The survey is public",NA,NA,NA,NA,NA,NA,NA,NA,
 "Their three families: EMBEDDING-BASED (turn entities into vectors), PATH-BASED (find meaningful paths between user and item, which is the explainable one), and UNIFIED (propagate over the graph, combining both)",
 NA,NA,NA,"Reviews others' evaluations",NA,
 "It is a survey and is appropriately cautious",
 "THE TAXONOMY, as the structure of my hybrid section. Also the strengths and weaknesses: embeddings scale but lose the reasoning, paths explain but are expensive",
 "The methods themselves, for now",
 "ALL THREE FAMILIES ASSUME A USER-ITEM INTERACTION MATRIX. I have none. So my work sits UPSTREAM of the whole taxonomy",
 "This turns my biggest apparent weakness into a scope statement. The sentence: 'the survey classifies methods for USING a knowledge graph in recommendation, and assumes such a graph exists for the domain. For skincare in a local market, it does not. This thesis constructs one.' Say that and 'you have no user data' stops being a criticism",
 "Section 4.5, positions the whole thesis"])

P.append(["25","C","Rahayu review","CITE IN INTRODUCTION",
 "A systematic review of ontology use in E-Learning recommender system",
 "N. Rahayu et al.","2022",
 "Computers and Education: Artificial Intelligence",
 "Well cited Elsevier journal","137","Indonesia",
 "https://consensus.app/papers/details/1f58f76b65ab5e5ca6b4ec6af28c2664/",
 "Abstract and quoted findings",
 "Ontology use in recommender systems has not been studied systematically. So study it",
 "Researchers building ontology-based recommenders",
 "28 journal articles on ontology-based recommender systems","28 primary studies",
 "The review is published",
 "Studies whether OTHERS named a methodology, and finds they mostly did not",
 NA,NA,NA,NA,NA,NA,NA,
 "Reviews how others produce recommendations","Reviews others","Reviews others",
 "Reviews others' use of standards, and finds standards for profiles and object metadata are rarely adopted",
 "Systematic review methodology",
 "TWO FINDINGS THAT ARE MY GAP STATEMENT: ontology-based recommender systems 'seldom use the methodology of building ontologies', and 'NONE of the primary studies described ontology evaluation methodologies'. None of 28",
 "Yes. It is a systematic review and reports what it found",
 "THE MOST USEFUL SINGLE CITATION IN MY WHOLE REVIEW. It means naming a construction methodology and reporting a named evaluation method are not housekeeping, they are CONTRIBUTIONS, because a 137-citation review found nobody does either",
 "The e-learning domain specifics",
 "Nothing. It is an ally, not a competitor",
 "Two cheap actions become contributions. Naming MOMo and LOT costs one paragraph plus discipline. Running OOPS! and FOOPS! costs one afternoon. Together they put me ahead of a 28-paper sample on the two dimensions that sample was weakest on. There is no cheaper way to strengthen a thesis",
 "INTRODUCTION, not just related work"])

P.append(["26","C","Tarus review","Cite for justification",
 "Knowledge-based recommendation: a review of ontology-based recommender systems for e-learning",
 "J. Tarus, Z. Niu, G. Mustafa","2017","Artificial Intelligence Review",
 "Springer, strong review journal","451","Beijing Institute of Technology, China",
 "https://consensus.app/papers/details/015574eca5b4569e908597b9530f1c34/",
 "Abstract",
 "Review ontology-based recommendation for e-learning, which no prior review covered properly",
 "Researchers","Journal papers 2005-2014",NR,"Published review",
 "Categorises others' knowledge representation and ontology languages",
 NA,NA,NA,NA,NA,NA,NA,
 "Categorises others' recommendation techniques",NA,NA,NA,
 "Systematic review",
 "Concludes that using ontology for knowledge representation IMPROVES recommendation quality, and that hybridising knowledge-based with other techniques improves effectiveness",
 "Yes for a review",
 "THE STANDARD CITATION for the claim that ontologies improve recommendation quality. 451 citations means nobody will argue with it",
 "The e-learning specifics",
 "Nothing, it is a justification source",
 "When a supervisor asks 'why an ontology at all', this is the reference with 451 citations that answers it in one line. Keep it to hand",
 "Section 4, opening justification"])

P.append(["27","C","Tarus hybrid","Cite for cold start",
 "A hybrid knowledge-based recommender system for e-learning based on ontology and sequential pattern mining",
 "J. Tarus, Z. Niu, A. Yousif","2017","Future Generation Computer Systems",
 "Elsevier, Q1","277","Beijing Institute of Technology, China",
 "https://consensus.app/papers/details/69c37012e3de5c3891ffa9bed00d6c52/",
 "Abstract",
 "Recommenders suffer cold start and rating sparsity, and ignore differences between learners",
 "E-learning platforms","Learner data and learning resources",NR,"Not stated",
 "Not named","Not stated","Not stated",
 "Learner and learning resource classes","Ontology domain knowledge for similarity","None stated",
 "Not stated","Ontology plus sequential pattern mining",
 "Four steps: build the ontology, compute rating similarity using ontology domain knowledge, generate top-N with collaborative filtering, then apply sequential pattern mining to reorder",
 "Not stated","Not stated","None",
 "Experiments comparing against baselines",
 "Reported improved performance","Reasonable",
 "THEIR EXPLICIT CLAIM that ontological domain knowledge ALLEVIATES COLD START AND SPARSITY. That is my cold start argument with a 277-citation citation attached",
 "Sequential pattern mining and collaborative filtering. No user sequences here",
 "They still model no authority, no provenance, no availability",
 "The structure of their argument is transferable wholesale: ontology handles what you know about the domain, the learned component handles what you know about users. That is exactly the division I should propose for future work, and it means my ontology is the half that must exist first",
 "Section 4, cold start; Section 5, future work"])

P.append(["28","C","George & Lal","Cite in passing",
 "Review of ontology-based recommender systems in e-learning",
 "G. George, A. M. Lal","2019","Computers and Education, Elsevier",
 "Q1 journal","183","India",
 "https://consensus.app/papers/details/1171abdae4bf54eebbc12c0da1d98e60/",
 "Abstract","Survey ontology use for personalisation in e-learning recommenders",
 "Researchers","Literature",NR,"Published review","Reviews others",
 NA,NA,NA,NA,NA,NA,NA,"Reviews others",NA,NA,NA,"Review",
 "Names the three benefits of ontologies: REUSABILITY, REASONING ABILITY, and support for INFERENCE",
 "Yes for a review",
 "The three-word summary of why an ontology: reusability, reasoning, inference. Useful phrasing for a supervisor conversation",
 "The domain","Nothing",
 "When I need to say in one breath what an ontology buys me over a spreadsheet, this is the phrasing, and it is citable",
 "Section 4, opening justification"])

P.append(["29","C","Alaa ontology evolution","Read for maintenance",
 "Improving Recommendations for Online Retail Markets Based on Ontology Evolution",
 "R. Alaa et al.","2021","Electronics, MDPI",
 "Indexed MDPI journal","14","Egypt",
 "https://consensus.app/papers/details/3d92e67dcc925ea89d0541ffbf6b99a3/",
 "Abstract",
 "Ontology-based recommenders build the ontology once from a snapshot, but user preferences change over time, so one-shot construction is too constrained",
 "E-retailers","Online retail purchase data",NR,"Not stated",
 "Proposes a SEMI-AUTOMATIC ontology building methodology, plus an ontology evolution subsystem",
 "Not stated","Not stated","Online retail ontology, classes not detailed in the abstract",
 "Not detailed","Recommendation by ontology REASONING",
 "Semi-automatic technique","Not stated",
 "Recommendation is produced by reasoning over the ontology, which evolves as purchase data accumulates",
 "Yes, reasoning is the mechanism","Not stated","None",
 "Not stated in the abstract","Not stated","Cannot assess from the abstract",
 "THE MAINTENANCE ARGUMENT. One-shot ontology construction cannot capture change. Every skincare ontology in my review is a snapshot with no plan. Lebanese prices move weekly, so this is not theoretical for me",
 "The retail evolution machinery itself",
 "They evolve preferences. I need to evolve PRICES and AVAILABILITY, which is a harder and more concrete version of the same problem",
 "This gives me the citation for the maintenance section that LOT requires and nobody in track B has. My named graphs design already supports it: reload graph:lb-retail weekly without touching anything else. The architecture answers the paper's criticism by construction, and I can say so",
 "Section 4, and my maintenance plan"])

P.append(["30","C","E-Prod","Read for architecture",
 "An ontology based product recommendation system for next generation e-retail",
 "A. M. Tiryaki et al.","2023",
 "Journal of Organizational Computing and Electronic Commerce",
 "Taylor and Francis, respectable","4","Turkey",
 "https://consensus.app/papers/details/d79755c5a1a65d048c1d926a7e172938/",
 "Abstract",
 "Product recommenders fail because they lack semantics",
 "E-commerce sellers and buyers",
 "Live e-commerce sites, tracked in real time. Clothing, shoes and bags",
 "Over 250 registered users","Not stated, it was a state-funded R&D project",
 "Not named","Not stated","Not stated",
 "Product model classes, not detailed in the abstract","Not detailed",
 "Semantic matching between products and user preferences",
 "IT TRACKS E-COMMERCE SITES IN REAL TIME AND TRANSFERS PRODUCT INFORMATION INTO THE ONTOLOGY MODEL. That is an automated, continuous population pipeline",
 "Not stated",
 "Combines machine learning with semantic matching. Learns preferences by watching user behaviour, then matches semantically between products and preferences",
 "Not stated","Not stated","None",
 "Compared against traditional collaborative recommendation with 250+ real users",
 "92.79% accuracy, 92.93% precision, 90.58% recall, beating the collaborative baseline",
 "Better than most in my review. Real users, a stated baseline, three metrics",
 "THE POPULATION ARCHITECTURE. Real-time tracking of retail sites into an ontology is the industrial version of what I built by hand. Also their evaluation design: a real baseline and 250 users",
 "The clothing domain and the behavioural learning",
 "No regulator, no provenance, no availability modelling, and no safety dimension. Clothes cannot hurt you",
 "They prove the pipeline can run continuously rather than as a one-off scrape. My six Lebanese retailers could be re-read on a schedule, which turns my dataset from a snapshot into a live resource. That is the single biggest upgrade available to my dataset paper and it needs no new modelling",
 "Section 4, and future work"])

P.append(["31","C","OntoCommerce","Cite in passing",
 "OntoCommerce: an ontology focused semantic framework for personalised product recommendation for user targeted e-commerce",
 "G. Deepak et al.","2019",
 "International Journal of Computer Aided Engineering and Technology",
 "Modest journal","38","India",
 "https://consensus.app/papers/details/020e8260f3395f61aae71e369bce366e/",
 "Abstract","Bring semantics into e-commerce product recommendation",
 "Online shoppers","E-commerce product data and user navigation logs",NR,"Not stated",
 "Not named","Not stated","Not stated","Not detailed","Not detailed",
 "Parametric fuzzification to widen the recommendable set",
 "Not stated","Not stated",
 "Semantic similarity computed with enriched normalised pointwise mutual information, combined with user query, recorded navigation and profile analysis",
 "Not stated","Not stated","None",
 "Accuracy and false discovery rate",
 "88.68% average accuracy, false discovery rate 0.13",
 "Plausible, though 'best-in-class' is a strong phrase for the evidence given",
 "AN ALTERNATIVE SIMILARITY MEASURE: normalised pointwise mutual information. Worth knowing when I choose how to compute product similarity",
 "The fuzzification and the navigation logs",
 "Same as the rest of track C: no regulator, no provenance, no availability",
 "Their false discovery rate metric is unusual and useful. In a domain with physical risk, reporting how often the system recommends something it should not is arguably MORE important than accuracy. I could adopt it and justify it on safety grounds, which no cosmetics paper has done",
 "Comparison table, similarity methods"])

P.append(["32","C","Lahoud (Lebanon)","Read - local precedent",
 "A comparative analysis of different recommender systems for university major and career domain guidance",
 "C. Lahoud et al.","2022","Education and Information Technologies, Springer",
 "Solid Springer journal","36","LEBANON",
 "https://consensus.app/papers/details/1aef32f231a051b8b266907d2bb517b6/",
 "Abstract",
 "Lebanese high school students are confused choosing a university major, with a volatile labour market and too much web data",
 "Lebanese high school students",
 "A case study on LEBANESE high school students, with a purpose-built ontology",
 "Not stated","The ontology is described as reusable in other systems",
 "Not named","Not stated","Not stated","A novel ontology covering the guidance domain","Not detailed",
 "Case-based reasoning combined with the ontology",
 "Not stated","Not stated",
 "Five approaches compared: user-based and item-based collaborative filtering, demographic, knowledge-based with case-based reasoning, ontology, and hybrids of them",
 "Not stated","Not stated","None",
 "Comparative evaluation on Lebanese students with feedback and satisfaction measures",
 "The hybrid (knowledge-based + collaborative + case-based reasoning + ontology) reached 98% similar cases, 95% personalised, 95% usefulness, 92.5% satisfaction",
 "Reasonably. Five approaches compared on the same case study is a proper comparison",
 "THE LOCAL PRECEDENT. A Lebanon-focused ontology recommender is publishable in a real journal with citations. That answers 'is a local scope a limitation' before it is asked. Also: the HYBRID beat every pure approach, which supports my future work direction",
 "The education domain",
 "Nothing. It is an ally",
 "Beyond the citation: these are LEBANESE ACADEMICS WORKING ON ONTOLOGY RECOMMENDERS. That makes them potential examiners, reviewers, collaborators or at minimum a friendly audience for a seminar. Worth finding out where they are",
 "Section 4, and scope justification"])

P.append(["33","C","COPPER ontology","THE TEMPLATE TO COPY",
 "Development and evaluation of the COntextualised and Personalised Physical activity and Exercise Recommendations (COPPER) Ontology",
 "M. Braun et al.","2025",
 "International Journal of Behavioral Nutrition and Physical Activity",
 "Strong Q1 health journal","4","Europe",
 "https://consensus.app/papers/details/49832525b1df5c31865f019b8635ffe5/",
 "Abstract, in detail",
 "Personalised physical activity plans need to combine expert knowledge, user input and data, and black-box approaches cannot do that transparently",
 "People being advised on physical activity, and the professionals advising them",
 "Literature research, use case scenarios, decision-tree workshops, existing theories and classification systems, end-users, domain experts and datasets",
 "288 classes, 9 data properties, 64 object properties",
 "YES, openly available, and being open is stated as one of its three novelty claims",
 "Follows OBO Foundry design principles, with specification, conceptualisation and formalisation phases",
 "288","9 data, 64 object",
 "An upper-level ontology plus lower-level ontologies for PERSONAL PROFILE, PLANNING, ACTIVITY, CONTEXT, BARRIER and COPING STRATEGY. Note the modular split",
 "Not detailed in the abstract","Logic rules created during formalisation",
 "Conceptualisation combined theory, classification systems, end-user input, expert input and datasets",
 "Protege, translated into OWL",
 "Recommendations for action and coping plans are produced from the ontology given a personal profile and context",
 "Yes, checked for logical consistency","Not stated","OBO Foundry principles",
 "THREE-PART EVALUATION: the PROCESS was evaluated against OBO Repository Principles, the ONTOLOGY was checked for logical consistency, and the RECOMMENDATIONS were evaluated using COMPETENCY QUESTIONS and USE CASES",
 "288 classes, 9 data properties, 64 object properties, logically and structurally consistent, recommendations deemed relevant",
 "Yes, and carefully. They claim consistency and relevance, and they demonstrate both. No accuracy claim is made because none is warranted",
 "THIS IS THE TEMPLATE FOR MY WHOLE ONTOLOGY CHAPTER. Modular lower-level ontologies including a CONTEXT module and a BARRIER module. Openly available as a stated contribution. Evaluation by competency questions and use cases rather than accuracy. Even the size, 288 classes, is a realistic target",
 "The physical activity domain",
 "Nothing. Read it and match its structure",
 "They have a BARRIER module: things that stop a person doing the activity. My equivalent is unavailability, price, and the currency crisis. Nobody in cosmetics models barriers, and 'barrier' is a much better frame than 'availability' because it covers price, stock, distance and season in one concept. Consider renaming my Lebanon module around it",
 "Methodology chapter, the model to follow"])

P.append(["34","C","FEVR","Cite for evaluation",
 "Evaluating Recommender Systems: Survey and Framework",
 "E. Zangerle, C. Bauer","2022","ACM Computing Surveys",
 "ACM CSUR. Q1, very high impact","283","Austria",
 "https://consensus.app/papers/details/793b2c09411459cda72df729aee73069/",
 "Abstract",
 "Evaluating a recommender properly means choosing goals, methods, data and metrics together, and that knowledge is scattered across the field",
 "Recommender systems researchers",
 "The literature on recommender evaluation",NR,"Published survey, widely used",
 NA,NA,NA,NA,NA,NA,
 NA,NA,
 "Not a recommender. It is a framework for deciding HOW to evaluate one",
 NA,NA,NA,
 "Consolidates the scattered knowledge on recommender evaluation into FEVR, the Framework for Evaluating Recommender systems",
 "Not applicable. It is a framework, not an experiment",
 "Yes. It is careful, widely adopted and does not overclaim",
 "THE JUSTIFICATION FOR MY EVALUATION DESIGN. FEVR's core argument is that the evaluation setting must follow the evaluation GOAL. My goal is correctness with a stated reason, not ranking accuracy, so precision and recall are the wrong instruments to reach for",
 "The metric catalogue for interaction-based systems, which does not apply to me",
 "Nothing. It is a framing source rather than a competitor",
 "This is the shield against 'why no precision and recall'. A 283-citation ACM Computing Surveys paper says the evaluation must match the goal. My goal is verifiable correctness. That is a complete answer and it takes one sentence",
 "Evaluation chapter, opening justification"])

# --------------------------------------------------------------- TRACK D
P.append(["35","D","Lee (lululab)","Read closely - direct rival",
 "Deep learning-based skin care product recommendation: A focus on cosmetic ingredient analysis and facial skin conditions",
 "J. Lee, H. Yoon, S. Kim, C. Lee, J. Lee, S. Yoo","2024",
 "Journal of Cosmetic Dermatology, Wiley",
 "Wiley clinical dermatology journal. Better standing than most of my track B",NR,
 "AI R&D Center, lululab Inc., Seoul, South Korea",
 "https://doi.org/10.1111/jocd.16218","Abstract and publisher page",
 "Cosmetic recommendation ignores what the ingredients actually do. Estimate efficacy from ingredients and combine it with AI skin analysis",
 "Consumers, through a commercial product",
 "Cosmetic ingredient lists and facial skin images. Proprietary",
 "Not stated","No. Corporate R&D",
 "Not applicable, no ontology",NA,NA,NA,NA,NA,
 "Not applicable","Deep neural network plus AI skin analysis",
 "A deep neural network estimates the efficacy of a cosmetic FROM ITS INGREDIENTS. AI skin analysis assesses the user's face. The two combine into a personalised recommendation",
 "None","No","None",
 "Reported as effective for various skin issues",
 "Exact figures not in the abstract","Cannot fully assess; it is a corporate paper in a clinical journal",
 "Nothing technical. Its value is that IT DOES MY PROBLEM WITHOUT AN ONTOLOGY, so I must answer it directly and honestly",
 "The whole approach. I have no labelled efficacy data and no facial images",
 "MY COMPARISON TABLE: they learn ingredient-to-efficacy from data, I derive it from the EU register plus stated rules. They give a weight, I give an ingredient, its function and the annex entry. They need proprietary training data, I need none. They cannot handle an unseen ingredient, I either have it in the register or report that I do not. They cite nothing, I cite Regulation (EC) 1223/2009. They model no availability, I model it as core",
 "USE THEIR MODEL AS A HYPOTHESIS GENERATOR AND MY ONTOLOGY AS THE CHECK. Train something small on my 11,802 formulas to predict claimed benefits, take its confident predictions and test them against CosIng functions. Where model and register agree, the claim is well supported. Where they disagree, I have found either a mislabelled product or a genuinely novel formulation. THAT DISAGREEMENT SET IS A RESEARCH RESULT, and only computable because I have both halves",
 "Section 5, and the honesty paragraph"])

P.append(["36","D","NCF","Cite as baseline",
 "Neural Collaborative Filtering",
 "X. He, L. Liao, H. Zhang, L. Nie, X. Hu, T.-S. Chua","2017","WWW 2017",
 "The Web Conference. Rank A*","Many thousands",
 "National University of Singapore",
 "https://arxiv.org/abs/1708.05031","Abstract and general knowledge",
 "Matrix factorisation uses a simple inner product. Replace it with a neural network that can learn arbitrary interaction functions",
 "Recommender systems researchers","Standard benchmark interaction datasets",
 "Millions of interactions","Yes, code is public",NA,NA,NA,NA,NA,NA,NA,
 "Neural networks, standard deep learning stack",
 "Learns user and item embeddings from an interaction matrix and predicts a score with a neural network",
 "None","No","None","Offline benchmarks with standard splits",
 "Improvements over matrix factorisation baselines","Yes, it is a careful methods paper",
 "The citation, as the standard neural baseline",
 "The method entirely. IT NEEDS A USER-ITEM MATRIX AND I HAVE NONE",
 "It cannot recommend to a user with no history, cannot say why, and cannot cite a regulator",
 "Its very requirement is my scope statement. Every method in this family learns from USER BEHAVIOUR. My dataset contains none, by design, because it is a product resource and not an interaction log. That is a boundary, not a defect, and it defines which half of the literature I belong to",
 "Section 5, background"])

P.append(["37","D","Zhang DL survey","Cite for taxonomy",
 "Deep Learning based Recommender System: A Survey and New Perspectives",
 "S. Zhang, L. Yao, A. Sun, Y. Tay","2019","ACM Computing Surveys 52(1)",
 "ACM CSUR. Q1, very high impact","Several thousand",
 "UNSW Australia and NTU Singapore",
 "https://arxiv.org/abs/1707.07435","Abstract and general knowledge",
 "Organise the fast-growing field of neural recommendation",
 "Researchers","Literature",NR,"Published survey",
 NA,NA,NA,NA,NA,NA,NA,NA,
 "Surveys the neural architectures used for recommendation",NA,NA,NA,
 "Review",NA,"Yes for a survey",
 "The reference taxonomy for the deep learning track, so I can characterise the whole family in one citation instead of ten",
 "Everything else","Not applicable",
 "Using one survey to cover a whole track keeps my chapter proportionate. Track D is the alternative I position against, not the field I am joining, so it should be short and well cited rather than long",
 "Section 5, background"])

# --------------------------------------------------------------- TRACK E
P.append(["38","E","CKE","Cite in passing",
 "Collaborative Knowledge Base Embedding for Recommender Systems",
 "F. Zhang, N. J. Yuan, D. Lian, X. Xie, W.-Y. Ma","2016","ACM SIGKDD 2016",
 "SIGKDD. Rank A*","Thousands","Microsoft Research Asia",
 "https://dl.acm.org/doi/10.1145/2939672.2939673","Abstract and general knowledge",
 "Ratings alone are sparse. Use a knowledge base to enrich item representations",
 "Recommender researchers","Knowledge base plus ratings","Benchmark scale",
 "Widely reimplemented",NA,NA,NA,NA,NA,NA,NA,"Deep learning stack",
 "Learns item representations jointly from a knowledge base and from ratings, then recommends",
 "None","No","Knowledge base entities",
 "Offline benchmarks","Improvements over collaborative baselines","Yes",
 "The citation. It is the first of the four canonical hybrid models",
 "The method. Needs ratings","No provenance, no authority, no availability",
 "It is the earliest of the four, so it marks the start of the line. Useful for showing the hybrid track has a decade of history and my future work joins something established rather than speculative",
 "Section 6, hybrid background"])

P.append(["39","E","RippleNet","Cite in passing",
 "RippleNet: Propagating User Preferences on the Knowledge Graph for Recommender Systems",
 "H. Wang, F. Zhang, J. Wang, M. Zhao, W. Li, X. Xie, M. Guo","2018","ACM CIKM 2018",
 "CIKM. Rank A","Thousands","Shanghai Jiao Tong University and Microsoft Research Asia",
 "https://arxiv.org/abs/1803.03467","Abstract and general knowledge",
 "Spread a user's known preferences outward through a knowledge graph like ripples on water",
 "Recommender researchers","Interaction history plus a knowledge graph","Benchmark scale",
 "Code public",NA,NA,NA,NA,NA,NA,NA,"Deep learning stack",
 "Starting from items the user liked, propagate outward along graph edges to discover related items, weighting by distance",
 "None","No","Knowledge graph entities","Offline benchmarks",
 "Improvements over baselines","Yes",
 "The citation, and the intuition that graph distance encodes relatedness",
 "The method. Needs interaction history",
 "Same as the rest: no regulator, no provenance, no availability",
 "Its intuition, propagation along edges, is the neural cousin of what a reasoner does symbolically. Noting that parallel in my thesis shows I understand both halves rather than treating them as rival tribes",
 "Section 6, hybrid background"])

P.append(["40","E","KGAT","Cite in passing",
 "KGAT: Knowledge Graph Attention Network for Recommendation",
 "X. Wang, X. He, Y. Cao, M. Liu, T.-S. Chua","2019","ACM SIGKDD 2019",
 "SIGKDD. Rank A*","Thousands",
 "National University of Singapore and University of Science and Technology of China",
 "https://arxiv.org/pdf/1905.07854  |  code: https://github.com/xiangwang1223/knowledge_graph_attention_network",
 "Abstract, code repository and general knowledge",
 "Model high-order relations in a collaborative knowledge graph, so item side information genuinely helps",
 "Recommender researchers","Interaction history plus item side information as a graph",
 "Benchmark scale","YES, code on GitHub",NA,NA,NA,NA,NA,NA,NA,
 "Graph neural network with attention",
 "Attention over a collaborative knowledge graph learns which neighbours matter, capturing relations several hops away",
 "None","No","Knowledge graph entities",
 "Offline benchmarks against CKE, CFKG, RippleNet, MCRec and factorisation baselines",
 "Better accuracy, and comparable computational cost to the lighter models while being much cheaper than path-based ones",
 "Yes. Proper baselines, proper ablations. A well-run empirical paper",
 "The citation, and its comparison table which tells me the cost profile of the whole family",
 "The method. Needs interaction history",
 "It treats the knowledge graph as SIDE INFORMATION to fix sparsity. My position is the mirror image: the graph is the contribution and the interactions do not exist yet",
 "That mirror-image framing is the cleanest way to place my thesis relative to the strongest work in the field. I am not competing with KGAT. I am building the thing KGAT assumes it already has, for a domain and a market where it does not exist",
 "Section 6, and future work"])

P.append(["41","E","KPRN","Read - explainability",
 "Explainable Reasoning over Knowledge Graphs for Recommendation (KPRN)",
 "X. Wang, D. Wang, C. Xu, X. He, Y. Cao, T.-S. Chua","2019",
 "AAAI Conference on Artificial Intelligence 33, 5329-5336",
 "AAAI. Rank A*","Over a thousand","National University of Singapore",
 "https://ojs.aaai.org/index.php/AAAI/article/view/4470","Abstract and general knowledge",
 "Make the reason for a recommendation visible by reasoning over paths in the knowledge graph",
 "Recommender researchers who care about explainability",
 "Interaction history plus a knowledge graph","Benchmark scale","Code public",
 NA,NA,NA,NA,NA,NA,NA,"Recurrent neural network over graph paths",
 "Builds a representation of each PATH between user and item by composing the meanings of the entities and relations along it, then pools paths with weights so stronger paths count more. THE PATH IS THE EXPLANATION",
 "None symbolic, but the path serves the same role","No","Knowledge graph entities",
 "Offline benchmarks plus explanation quality discussion",
 "Improvements over non-explainable baselines","Yes",
 "THE MOST RELEVANT PAPER IN TRACK E. Its insight is that a path through the graph IS a reason. That is the same intuition as a reasoner producing a justification, arrived at from the neural side",
 "The recurrent network and the interaction requirement",
 "Their paths explain a correlation. My paths would explain a REGULATION: this product contains phenoxyethanol, which is a preservative, restricted under Annex V entry 29, according to the European Commission. That is a stronger kind of explanation",
 "Related work on EXPLANATION PATH QUALITY (Balloccu et al.) optimises paths for recency, popularity and diversity. For a safety domain the quality criterion should be VERIFIABILITY: can each hop in the path be traced to a source. My evidence levels make that computable, and nobody has proposed verifiability as a path quality metric",
 "Section 6, and the explainability argument"])

P.append(["42","E","RDF2Vec","Cite for embeddings",
 "RDF2Vec: RDF Graph Embeddings for Data Mining",
 "P. Ristoski, H. Paulheim","2016","ISWC 2016, Springer LNCS",
 "ISWC. Rank A","Over a thousand","University of Mannheim, Germany",
 "https://doi.org/10.1007/978-3-319-46523-4_30","Abstract and general knowledge",
 "Make RDF graphs usable by machine learning, which needs numbers not triples",
 "Data mining researchers","RDF graphs including DBpedia","Large-scale knowledge graphs",
 "Yes, widely available",NA,NA,NA,NA,NA,NA,NA,
 "Random walks over the graph plus word2vec",
 "Walks around the graph, treats each walk as a sentence and each entity as a word, then applies word2vec to get a vector per entity",
 "No","Operates on RDF","DBpedia and similar",
 "Machine learning benchmarks on entities from DBpedia",
 "Effective embeddings for large-scale knowledge graphs","Yes",
 "The concept, and the citation. Turning a graph into vectors is how the two halves of my review connect",
 "For me it is superseded by OWL2Vec*, because RDF2Vec ignores OWL logic and my ontology will have real logical constructors",
 "It embeds structure but discards axioms",
 "The distinction between RDF2Vec and OWL2Vec* is a neat way to show in one paragraph that my ontology carries more information than a plain graph. If my defined classes and restrictions were pointless, RDF2Vec would be sufficient. That OWL2Vec* exists is evidence that they are not",
 "Section 6, embeddings"])

P.append(["43","E","OWL2Vec*","THE BRIDGE I CAN USE NOW",
 "OWL2Vec*: Embedding of OWL Ontologies",
 "J. Chen, P. Hu, E. Jimenez-Ruiz, O. M. Holter, D. Antonyrajah, I. Horrocks","2021",
 "Machine Learning journal 110, 1813-1845, Springer",
 "Strong journal, and the Oxford group is authoritative","Several hundred",
 "University of Oxford, City University of London",
 "https://doi.org/10.1007/s10994-021-05997-6  |  code: https://github.com/KRR-Oxford/OWL2Vec-Star",
 "Abstract and repository",
 "RDF2Vec cannot capture the logical axioms of an OWL ontology, so build an embedding that can",
 "Anyone with an OWL ontology and a prediction task",
 "OWL ontologies, evaluated on biomedical ones","Large ontologies",
 "YES, code on GitHub",NA,NA,NA,NA,NA,NA,NA,
 "Random walks plus word embeddings, but FIRST materialising the ontology with a REASONER",
 "Encodes graph structure, lexical information AND logical constructors into a vector per entity",
 "YES, used to materialise the ontology before walking","No","Works on any OWL ontology",
 "Class membership prediction and class subsumption prediction",
 "Benefits demonstrated from all three information sources: structure, lexical content, logic",
 "Yes. Careful ablations showing each component contributes",
 "THE RIGHT HYBRID ENTRY POINT FOR ME, and the only one in track E I could use immediately, because IT NEEDS AN ONTOLOGY, NOT A USER LOG. Two concrete uses: product similarity with no ratings, and predicting missing values",
 "Nothing yet. This is the one to try",
 "Everything else in track E requires interactions I do not have. This does not",
 "It was EVALUATED ON CLASS MEMBERSHIP PREDICTION. My size_value is 27% complete and rating is 51% complete. Predicting missing values with an embedding, then checking the predictions against the CosIng-derived facts I already hold, is a self-validating experiment. I can measure how well it works without collecting anything new",
 "Section 6, and my future work chapter"])

P.append(["44","E","Ontology-grounded GraphRAG","CITE IN INTRODUCTION",
 "Ontology-grounded knowledge graphs for mitigating hallucinations in large language models for clinical question answering",
 "M. Ali et al.","2026","Journal of Biomedical Informatics, Elsevier",
 "Strong specialist journal","11","Egyptian institutions",
 "https://consensus.app/papers/details/d7c871f2bb3857439c1bfa563bebf37a/",
 "Abstract, in detail",
 "Large language models hallucinate, which makes them unusable clinically. Ground them in an ontology and see if that fixes it",
 "Clinicians and biomedical informaticians",
 "Clinical and hospital data from multiple Egyptian institutions",
 "60 clinical questions, with reference answers from five peer-reviewed hospital studies",
 "Not stated","Domain-specific RDF/OWL ontology, construction not detailed in the abstract",
 "Not stated","Not stated","Clinical concepts","Not detailed",
 "The ontology enforces structured semantic grounding during question answering",
 "From clinical and hospital data","GraphRAG framework, RDF/OWL, LLMs",
 "Retrieval augmented generation where the retrieval is over an ontology-grounded knowledge graph, so the model's answers are constrained by the graph",
 "Semantic grounding rather than a classical reasoner","Implied","None stated",
 "Three conditions compared on the same 60 questions against clinically reported reference answers",
 "ChatGPT-4: 37% accurate, ~63% hallucination. DeepSeek-R1: 52%, ~48%. ONTOLOGY-GROUNDED: 98% (59 of 60), 1.7% hallucination",
 "Yes, and it is a proper controlled comparison on a fixed question set with external reference answers",
 "THE ANSWER TO 'WHY NOT JUST ASK AN LLM', which is the question every supervisor and reviewer will ask in 2026. With numbers, peer reviewed, in a domain with physical risk",
 "The clinical QA application itself",
 "Not a competitor. It is my strongest supporting citation",
 "The sentence for my introduction: in a safety-relevant domain, grounding a language model in an ontology reduced hallucination from 63 percent to 1.7 percent, which is the difference between a system that can be deployed and one that cannot. Skincare is a safety-relevant domain too, and my ontology is the grounding",
 "INTRODUCTION, and Section 6"])

P.append(["45","E","LLMs4OL","Read for future work",
 "LLMs4OL 2024 Overview: The 1st Large Language Models for Ontology Learning Challenge (and the 2025 second edition)",
 "H. Babaei Giglou, J. D'Souza, S. Auer","2024-2025",
 "ISWC challenge proceedings",
 "ISWC-affiliated shared task. Community standard","Growing","TIB Hannover, Germany",
 "https://arxiv.org/abs/2409.10146","Abstract",
 "Can large language models do ontology learning, and how well",
 "Ontology and NLP researchers",
 "Ontologies across several domains, used as evaluation targets","Multiple ontologies",
 "YES, the challenge data is public",
 "A shared task rather than a methodology",NA,NA,NA,NA,NA,
 "The whole point is automated construction","BERT through GPT-3.5 to LLaMA-3-70B, with fine-tuning, retrieval-augmented prompting and prompt engineering",
 "Not a recommender",NA,NA,NA,
 "THREE TASKS: term typing (what category does this term belong to), taxonomy discovery (what is the hierarchy), and non-taxonomic relation extraction",
 "Strong precision, recall and macro-F1 on several ontologies, but some domains only partially resolved",
 "Yes, and honestly. They state where it did not work and what add-ons are needed",
 "THE TASK DEFINITIONS. My benefits and concerns columns are free text in several languages written by retailers. That is term typing and taxonomy discovery, exactly",
 "Nothing yet. This is a future work direction, not a method for the core thesis",
 "They evaluate on existing ontologies. I would evaluate against an AUTHORITY, which is stronger",
 "THE DESIGN THAT MAKES THIS DEFENSIBLE: let an LLM PROPOSE a concern taxonomy from my own data, then VALIDATE every proposal against CosIng and DermO, and report the survival rate. The LLM proposes, the authority disposes. That is defensible where 'I asked ChatGPT' is not, and the survival rate is a number nobody has published for cosmetics. Strong second paper",
 "Section 6, future work"])

P.append(["46","E","Shimizu LLM+ontology","Read for future work",
 "Accelerating Knowledge Graph and Ontology Engineering with Large Language Models",
 "C. Shimizu, P. Hitzler","2024","arXiv, position paper",
 "Position paper by authoritative authors","46","Kansas State University, USA",
 "https://consensus.app/papers/details/82d868ee8f7953108246241e28d5e339/",
 "Abstract",
 "Lay out LLM-based knowledge graph and ontology engineering as a research area",
 "Ontology engineers","Position paper, no data",NA,"Public preprint",
 "Argues that MODULAR approaches to ontologies will be of central importance",
 NA,NA,NA,NA,NA,
 "Discusses LLMs for ontology modelling, extension, modification, POPULATION, alignment and entity disambiguation",
 "Large language models",NA,NA,NA,NA,"Position paper, no evaluation",NA,
 "It is explicitly a position paper and does not claim results",
 "THE ARGUMENT THAT MODULARITY MATTERS MORE, NOT LESS, IN THE LLM ERA. That is direct support for my four-module design, from the authors of the modular methodology I am adopting",
 "The speculative parts",
 "Not a competitor",
 "It lists entity disambiguation as an LLM opportunity. Entity matching is precisely where I measured a 19 to 33 percent error rate with fuzzy string matching. An LLM-assisted matching pass, validated against my hand-checked sample, would be a small, well-scoped and genuinely useful experiment with a ready-made ground truth",
 "Section 6, and methodology justification"])

# --------------------------------------------------------------- TRACK F
P.append(["47","F","Noy & McGuinness 101","Cite, do not rely on",
 "Ontology Development 101: A Guide to Creating Your First Ontology",
 "N. F. Noy, D. L. McGuinness","2001","Stanford Knowledge Systems Laboratory technical report",
 "Not peer reviewed, but universally cited","Many thousands","Stanford University, USA",
 "https://protege.stanford.edu/publications/ontology_development/ontology101.pdf",
 "Read in full",
 "Teach a beginner to build their first ontology",
 "Beginners","None, it is a guide",NA,"Freely available",
 "Yes, a seven-step process",NA,NA,NA,NA,NA,NA,"Protege",NA,NA,NA,NA,NA,NA,
 "It is a teaching guide and claims nothing more",
 "The class-versus-property test, and the individual-versus-class test, which I used to decide that Annex entries are individuals. Also the practice of writing competency questions",
 "It is too light to be my only methodology, and it is 25 years old",
 "It predates linked data, so it has nothing to say about reuse or publication, which is where MOMo and LOT come in",
 "Everyone cites it and almost nobody follows anything else. Rahayu et al. found 28 studies that mostly named no methodology at all. Citing 101 AND naming a modern methodology is a cheap way to look serious",
 "Methodology chapter"])

P.append(["48","F","LOT","MY PUBLICATION METHOD",
 "LOT: An industrial oriented ontology engineering framework",
 "M. Poveda-Villalon, A. Fernandez-Izquierdo, M. Fernandez-Lopez, R. Garcia-Castro","2022",
 "Engineering Applications of Artificial Intelligence 111, Elsevier",
 "Q1 Elsevier journal","Growing fast",
 "Universidad Politecnica de Madrid, Spain",
 "https://lot.linkeddata.es/  |  https://doi.org/10.1016/j.engappai.2022.104755",
 "Abstract and the methodology website",
 "Existing ontology methodologies are heavy and academic. Industry needs something lightweight, iterative and oriented to actually publishing the result",
 "Ontology engineers in industry and research",
 "The methodology itself",NA,"Freely documented",
 "IT IS the methodology. Four activities: requirements, implementation, publication, maintenance",
 NA,NA,NA,NA,NA,
 "Not about population, but its requirements activity produces the ORSD that drives everything",
 "Compatible with agile sprints and standard software practice",NA,NA,NA,
 "Emphasises REUSING TERMS from published vocabularies and PUBLISHING the result",
 "Presented as a framework with case studies",NA,"Appropriate for a methodology paper",
 "THE PROJECT STRUCTURE AND THE PUBLICATION DISCIPLINE. Four activities, each producing a thesis deliverable: requirements to the methodology chapter, implementation to the design chapter, publication to the results chapter, maintenance to the discussion",
 "Nothing. I am adopting it",
 "Not a competitor",
 "Its two emphases are exactly my two criticisms of track B. It stresses REUSING published terms, and track B invents everything. It stresses PUBLISHING, and one of six track B ontologies is published. Adopting LOT is therefore not just a method choice, it is a direct response to my own gap analysis, and I can say so in one sentence",
 "Methodology chapter, the framework"])

P.append(["49","F","MOMo","MY DESIGN METHOD",
 "Modular ontology modeling",
 "C. Shimizu, K. Hammar, P. Hitzler","2022","Semantic Web journal, IOS Press",
 "The specialist journal of the field","84",
 "Kansas State University, USA and Jonkoping University, Sweden",
 "https://consensus.app/papers/details/7df1c6652d4759c0bf23e59205fddd50/  |  tool: https://comodide.com/",
 "Abstract, in detail",
 "Reusing ontologies is hard for four specific reasons, so provide a methodology and tooling that address them",
 "Ontology engineers",
 "The methodology, plus a rigorous usability evaluation of its tool",
 "Evaluation of CoModIDE with real users","Freely documented, tool available",
 "IT IS the methodology. Builds on eXtreme Design, adds GRAPHICAL SCHEMA DIAGRAMS as the knowledge elicitation device",
 NA,NA,"Uses Ontology Design Patterns as the unit of reuse",NA,NA,
 "Not about population","CoModIDE, the Comprehensive Modular Ontology IDE",NA,NA,NA,
 "Ontology Design Patterns and the MODL pattern library",
 "Rigorous usability evaluation of CoModIDE",
 "CoModIDE significantly improves the approachability of graphical modular modelling, and shows high usability",
 "Yes, and unusually for a methodology paper it evaluates its own tooling properly",
 "THE DESIGN METHOD, AND THE FOUR REASONS REUSE FAILS, WHICH I HAVE PERSONALLY HIT THREE OF: differing granularity (OntoCosmetic has 116 classes and I need 10), lacking conceptual clarity (Moe and Aung's hasIngValue means nothing without the paper), difficulty adhering to good principles (my first ttl mixed product and ingredient properties), and no reuse support in tooling (Protege will not help me find an existing term)",
 "Nothing. I am adopting it",
 "Not a competitor",
 "Quoting their four failure reasons and giving MY OWN EXAMPLE AGAINST EACH ONE is a strong and unusual passage for a methodology chapter. It shows the methodology was chosen because of problems I actually had, not picked off a list. Also take the habit of drawing each module before writing Turtle, since those diagrams are the figures my chapter needs anyway",
 "Methodology chapter, the design method"])

P.append(["50","F","eXtreme Design","Cite as parent method",
 "Engineering Ontologies with Patterns: The eXtreme Design Methodology",
 "E. Blomqvist, K. Hammar, V. Presutti","2016","Ontology Engineering with ODPs, IOS Press",
 "Book chapter in the standard reference","113","Linkoping and Jonkoping, Sweden",
 "https://consensus.app/papers/details/ed01a11435b75058a2e98e48ccdc4d8d/",
 "Abstract","Build ontologies agilely using design patterns as the unit of work",
 "Ontology engineers","The methodology",NA,"Published",
 "IT IS the methodology. Agile, pattern-based",NA,NA,
 "Ontology Design Patterns as reusable modelling units",NA,NA,NA,"Pattern catalogues",NA,NA,NA,NA,NA,NA,
 "Appropriate for a methodology chapter",
 "The parent of MOMo. Cite both to show the lineage of the method I chose",
 "I use MOMo rather than XD directly, because MOMo adds the graphical modelling and the tooling",
 "Not a competitor",
 "Citing the lineage (ODP book, then eXtreme Design, then MOMo) in two sentences shows the methodology has a twenty-year research history behind it. That is much harder to challenge than 'I followed a blog post'",
 "Methodology chapter, lineage"])

P.append(["51","F","ODP book","Background",
 "Ontology Engineering with Ontology Design Patterns: Foundations and Applications",
 "P. Hitzler, A. Gangemi, K. Janowicz, A. Krisnadhi, V. Presutti (eds)","2016","IOS Press",
 "The standard textbook of the area","99","International",
 "https://consensus.app/papers/details/b0ac301002d95b13844ad0c55cc322a4/",
 "Abstract","Bring together everything known about ontology design patterns",
 "Ontology engineers","Edited volume",NA,"Published book",
 "Modular ontology modelling based on design patterns",NA,NA,
 "Design patterns including the N-ARY RELATION pattern, which is what my IngredientListing and Claim reifications are",
 NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,"Appropriate",
 "THE NAME FOR WHAT I AM DOING. My two reifications are the n-ary relation pattern. Calling them that, and citing this, turns an improvisation into an application of an established pattern",
 "The chapters on domains far from mine",
 "Not a competitor",
 "The difference between writing 'I made Claim into its own class because a triple only has three slots' and 'the Claim construct applies the n-ary relation ontology design pattern' is the difference between a student and a researcher. Same design, different standing",
 "Design chapter, pattern justification"])

P.append(["52","F","Grau modular reuse","Cite for rigour",
 "Modular Reuse of Ontologies: Theory and Practice",
 "B. Cuenca Grau, I. Horrocks, Y. Kazakov, U. Sattler","2008",
 "Journal of Artificial Intelligence Research",
 "JAIR. Q1, highly respected","453","University of Oxford and University of Manchester, UK",
 "https://consensus.app/papers/details/3bc32d5e379851aeaef1106fdfd67cef/",
 "Abstract",
 "Formalise what it actually means to safely reuse part of an ontology",
 "Description logic researchers","Theory","Not applicable","Published",
 "Formal theory rather than a methodology",NA,NA,
 "Introduces conservative extension, safety, and locality",NA,NA,NA,NA,NA,NA,NA,NA,
 "Formal proofs plus modularisation algorithms",
 "Shows the general problems are undecidable for OWL DL, then identifies LOCALITY as a practical sufficient condition for safe reuse",
 "Yes. It is a formal paper and proves what it claims",
 "ONE SENTENCE OF RIGOUR. When I import part of another ontology, there is a formal notion of doing so SAFELY, meaning without changing the meaning of the imported terms. I do not need the mathematics, but citing it shows I know the guarantee exists",
 "The proofs. I am not attempting them",
 "Not a competitor",
 "This is the paper that justifies my decision NOT to import all 116 classes of OntoCosmetic. Importing an ontology wholesale can change the meaning of your own terms. Referencing safety and locality turns 'I only took ten classes' from laziness into a principled decision",
 "Design chapter, reuse justification"])

P.append(["53","F","MODL","Use as a catalogue",
 "MODL: A Modular Ontology Design Library",
 "C. Shimizu, Q. Hirt, P. Hitzler","2019","WOP / arXiv",
 "Workshop paper, but widely used","55","Kansas State University, USA",
 "https://consensus.app/papers/details/4af016e1676c59d79b0de41f7ea96d68/",
 "Abstract",
 "Reusing a design pattern requires knowing it exists, which is a real barrier",
 "Ontology engineers",
 "A curated collection of well-documented patterns from many disciplines",
 "A library of patterns","YES, publicly available",
 "Supports pattern-based modular development",NA,NA,
 "A catalogue of reusable patterns",NA,NA,NA,NA,NA,NA,NA,NA,NA,NA,
 "It is a resource and presents itself as one",
 "A PLACE TO LOOK BEFORE INVENTING A PATTERN. They state the barrier plainly: you cannot reuse a pattern you do not know exists",
 "Nothing","Not a competitor",
 "Pattern-based modular ontologies are explicitly linked to FAIR data practice, particularly Interoperability and Reusability. Since I am already going to run FOOPS! for a FAIR score, designing with patterns and then measuring FAIRness is a coherent story that connects my design choices to my evaluation numbers",
 "Design chapter, sprint 2"])

P.append(["54","F","OOPS!","RUN IT - one afternoon",
 "OOPS! (OntOlogy Pitfall Scanner!): An On-line Tool for Ontology Evaluation",
 "M. Poveda-Villalon, A. Gomez-Perez, M. C. Suarez-Figueroa","2014",
 "International Journal on Semantic Web and Information Systems 10(2) 7-34",
 "The specialist journal for this area","Several hundred",
 "Universidad Politecnica de Madrid, Spain",
 "https://oops.linkeddata.es/","Abstract and the tool itself",
 "Ontology developers make the same design mistakes over and over. Detect them automatically instead of hoping a reviewer spots them",
 "Ontology developers, at any level",
 "A catalogue of common pitfalls collected from real ontologies","41 pitfalls catalogued",
 "YES, free web tool, no login",
 "Not a methodology. It is an evaluation tool",NA,NA,NA,NA,NA,
 NA,NA,
 "Not a recommender. You paste an ontology URL or file and it returns a report",
 NA,"No",NA,
 "Automated detection against the 41-pitfall catalogue",
 "41 pitfalls, graded CRITICAL, IMPORTANT and MINOR",
 "Yes. It detects what it says it detects",
 "A CONCRETE EVALUATION NUMBER FOR ONE AFTERNOON OF WORK. Upload the ontology, get a graded pitfall report, fix what is cheap, and report the rest honestly",
 "Nothing. I am simply going to run it",
 "Not a competitor. It is a free instrument",
 "Rahayu et al. found that NONE of 28 ontology-based recommender papers described any evaluation methodology. Running a free web tool and putting the graded result in a table therefore puts me ahead of an entire 28-paper sample on that dimension. There is no cheaper contribution available anywhere in this thesis",
 "Evaluation chapter, structural layer"])

P.append(["55","F","FOOPS!","RUN IT - one afternoon",
 "FOOPS!: An Ontology Pitfall Scanner for the FAIR Principles",
 "D. Garijo, O. Corcho, M. Poveda-Villalon","2021",
 "ISWC Posters and Demos, CEUR-WS vol 2980",
 "A demo paper, but the tool has become standard practice","Growing",
 "Universidad Politecnica de Madrid, Spain",
 "https://w3id.org/foops/","Abstract and the tool itself",
 "How FAIR is your ontology, measured rather than asserted. FAIR means Findable, Accessible, Interoperable and Reusable",
 "Anyone publishing an ontology or a vocabulary",
 "FAIR best practices for semantic artefacts, turned into automated checks",
 "24 checks across the four FAIR dimensions",
 "YES, free, and it works for both OWL and SKOS",
 "Not a methodology. It is an evaluation tool",NA,NA,NA,NA,NA,
 NA,NA,
 "Not a recommender. Point it at your ontology and it returns a FAIR score with a breakdown",
 NA,"No",NA,
 "24 automated checks, four dimensions",
 "A FAIR score with a per-dimension breakdown showing exactly what is missing",
 "Yes. Every check maps to a stated FAIR best practice",
 "A SECOND FREE EVALUATION NUMBER. And since one of my five gap findings is that track B does not publish its artefacts, measuring my own FAIRness closes that criticism with evidence rather than with a promise",
 "Nothing. I am simply going to run it",
 "Not a competitor. It is a free instrument",
 "Reporting a FAIR score is rare in this literature and increasingly expected by journals and funders. It also gives me a before-and-after: run it early, fix what it flags, run it again, report both numbers. An improvement story reads far better than a single score",
 "Evaluation chapter, structural layer"])

P.append(["56","F","Morph-KGC","MY POPULATION TOOL",
 "Morph-KGC: Scalable knowledge graph materialization with mapping partitions (and Boosting Knowledge Graph Generation from Tabular Data with RML Views)",
 "J. Arenas-Guerrero, D. Chaves-Fraga, J. Toledo, M. S. Perez, O. Corcho","2023-2024",
 "Semantic Web journal, plus workshop papers",
 "The specialist journal, and the group is the reference group for this",
 "26 for the ETL overview, 6 for the RML views paper",
 "Universidad Politecnica de Madrid, Spain",
 "https://morph-kgc.readthedocs.io/  |  https://github.com/morph-kgc/morph-kgc",
 "Documentation and abstracts",
 "Generate RDF knowledge graphs from heterogeneous sources declaratively, and do it fast enough for real data",
 "Anyone turning tabular data into a knowledge graph",
 "Compliant with the W3C R2RML recommendation and with RML. Built on pandas",
 "Designed for large sources through mapping partitions","YES, open source",
 "Not a methodology, a tool for the population step",NA,NA,NA,NA,NA,
 "THIS IS THE POPULATION METHOD. A declarative mapping file describes column-to-property, and the engine generates the triples",
 "Python, pandas, RML, YARRRML, and RML views so transformations can be written in SQL",
 NA,NA,NA,"Whatever vocabularies the mapping references",
 "Benchmarked against other RML and RML+FnO systems",
 "Significantly more scalable than the alternatives tested",
 "Yes, with benchmarks",
 "THE TOOL, AND THE ARGUMENT FOR IT. A Python script would produce the same triples but would not be auditable, citable or rerunnable by a reviewer. A mapping file is all three, goes in my appendix, and rebuilds the graph with one command when the dataset changes",
 "The advanced features I do not need yet, such as RDF-star",
 "Not a competitor",
 "Their RML views paper exists BECAUSE plain RML forces people back into scripting for complex cases. That is directly relevant to my hardest population problem, splitting one ingredients string into 295,991 positioned listings. Knowing the limitation is documented in the literature means my preprocessing step is a recognised practice rather than a workaround I have to apologise for",
 "Methodology chapter, population"])

P.append(["57","F","PE-TRE","MY EVIDENCE MODULE PRECEDENT",
 "Semi-automated data provenance tracking for transparent data production and linkage to enhance auditing and quality assurance in Trusted Research Environments",
 "K. O'Sullivan et al.","2025","International Journal of Population Data Science",
 "Peer reviewed specialist journal","3","United Kingdom",
 "https://consensus.app/papers/details/ad74e12091a053f28c8f7df3f39f3e5e/",
 "Abstract, in detail",
 "Data linkage in secure research environments is opaque, so analysts and governance teams cannot audit how a dataset was produced",
 "Data analysts, researchers and information governance teams",
 "Data processing workflows inside a trusted research environment",
 "Not stated","Not stated, but the method is fully described",
 "YES, AND IT IS EXACTLY MINE: they applied PROV-O to CREATE A DERIVED ONTOLOGY FOLLOWING THE FOUR-STEP LINKED OPEN TERMS METHODOLOGY",
 "Not stated","Not stated",
 "A derived ontology they call SHP, specialising PROV-O for their domain",
 "PROV-O properties, specialised","Rule-based validation checks over the graph",
 "Automated scripts collect provenance information from the data processing workflow",
 "PROV-O, LOT methodology, a knowledge graph, and an interactive explorer tool",
 "Not a recommender. It displays data linkage information extracted from the knowledge graph, alongside validation results",
 "Not stated","Implied","PROV-O",
 "Participatory design, contextual inquiry, user requirements interviews, co-design workshops and prototype evaluations with real users",
 "User evaluations confirmed the tool would improve data linkage quality and reduce processing errors",
 "Yes. A design-and-evaluate study that claims usefulness and demonstrates it with users",
 "THE ENTIRE SHAPE OF MY EVIDENCE MODULE, ALREADY PUBLISHED. A derived PROV-O ontology, built with LOT, for audit and traceability, with rule-based validation. My design stops being a guess and becomes an application of an established pattern in a new domain",
 "The trusted research environment specifics",
 "They audit a data pipeline. I audit CLAIMS ABOUT PRODUCTS, which is a consumer-facing use nobody has applied this to",
 "Their user evaluation found the payoff was better quality linkage and fewer processing errors. That is precisely what my four evidence levels are for, and it means I can argue the benefit of provenance modelling from someone else's user study rather than from first principles. It also validates the method combination I chose independently, which is reassuring",
 "Design chapter, the evidence module"])

P.append(["58","F","SWRL","Cite if I use rules",
 "OWL rules: A proposal and prototype implementation (SWRL)",
 "I. Horrocks, P. F. Patel-Schneider, S. Bechhofer, D. Tsarkov","2005",
 "Journal of Web Semantics",
 "The specialist journal, and the authors are the field's founders","366",
 "University of Manchester UK, Bell Labs USA",
 "https://www.w3.org/submissions/SWRL/","Abstract",
 "OWL cannot express everything, particularly about properties. Add Horn clause rules",
 "Ontology engineers","Formal proposal",NA,"W3C member submission, widely implemented",
 "Not a methodology",NA,NA,NA,NA,
 "SWRL IS the rule mechanism. Rules extend OWL syntactically and semantically",
 NA,"Protege, Pellet, Jess, Drools",NA,
 "Pellet and Openllet support SWRL. HermiT does NOT",
 NA,"None","Formal analysis",
 "Shows SWRL is expressive, and that ontology consistency becomes UNDECIDABLE with it",
 "Yes, and honestly. They state the undecidability result plainly",
 "THE MECHANISM FOR THE TWO RULES I ACTUALLY NEED, plus the warning that comes with it. OntoCosmetic uses SWRL for its heuristics, so there is domain precedent",
 "Heavy rule use. Undecidability is a real cost and rules slow reasoning",
 "Not a competitor",
 "The practical consequence to remember: if I write SWRL rules I must switch reasoner from HermiT to Openllet, because HermiT ignores them. That is exactly the kind of detail that goes wrong silently and produces plausible output rather than an error, which is the fault class that has cost me the most time on this project already",
 "Design chapter, rules"])

P.append(["59","F","PROV-O","MY PROVENANCE VOCABULARY",
 "PROV-O: The PROV Ontology",
 "T. Lebo, S. Sahoo, D. McGuinness (eds)","2013","W3C Recommendation",
 "A W3C Recommendation. The highest standing a vocabulary can have","784",
 "W3C Provenance Working Group",
 "https://www.w3.org/TR/prov-o/","Read in full",
 "Provide a standard way to say where information came from, who produced it and how",
 "Anyone recording data provenance",
 "The vocabulary itself",
 "A set of classes, properties and restrictions","YES, a W3C standard",
 "Not a methodology","Core classes: Entity, Activity, Agent",
 "wasAttributedTo, wasDerivedFrom, wasGeneratedBy, generatedAtTime, actedOnBehalfOf",
 "Entity, Activity, Agent, and their specialisations",
 "wasAttributedTo, wasDerivedFrom, generatedAtTime, used, wasInformedBy",
 "Designed to be SPECIALISED, meaning you create your own classes and properties underneath it, which is exactly what I will do",
 "Not applicable","Any RDF stack",NA,"Works with any reasoner","Yes, standard RDF",
 "It IS an external vocabulary, and the standard one",
 "W3C standardisation process with implementation reports",
 "784 citations and adoption across many domains","Yes",
 "MY FOUR EVIDENCE LEVELS, EXPRESSED IN A LANGUAGE OTHER PEOPLE ALREADY SPEAK. A claim is not a fact floating in space: someone said it, somewhere, on a date. wasAttributedTo, wasDerivedFrom and generatedAtTime say exactly that",
 "The workflow and activity machinery, which I do not need for static claims",
 "Not a competitor. It is the standard that makes my contribution reusable rather than bespoke",
 "The single most persuasive thing about using PROV-O is that it converts my most novel design decision into a STANDARD one. Inventing four evidence levels is a choice a reviewer can question. Specialising a W3C Recommendation to a new domain is a contribution a reviewer can only assess on whether the specialisation is sound. Same idea, much stronger position",
 "Design chapter, the evidence module"])

# ---- integrity check: every row must have exactly one value per column ----
_bad = [(r[0], r[2], len(r)) for r in P if len(r) != len(COLS)]
if _bad:
    for n, nm, ln in _bad:
        print(f"  ROW {n} ({nm}) has {ln} fields, expected {len(COLS)}")
    raise SystemExit("Aborting: column counts do not match, data would be misaligned.")
print(f"integrity check passed: {len(P)} rows x {len(COLS)} columns")

# ============================================================ BUILD BOOK ==
wb = Workbook()

def style_title_block(ws, title, subtitle, span, note=None):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    c = ws.cell(row=1, column=1, value=title)
    c.font = Font(name=SERIF, size=17, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=INK)
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[1].height = 34

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=span)
    c = ws.cell(row=2, column=1, value=subtitle)
    c.font = Font(name=SERIF, size=10, italic=True, color="4A4A4A")
    c.fill = PatternFill("solid", fgColor=PAPER)
    c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[2].height = 20

    if note:
        ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=span)
        c = ws.cell(row=3, column=1, value=note)
        c.font = Font(name=SERIF, size=9, color=GOLD, bold=True)
        c.fill = PatternFill("solid", fgColor=PAPER)
        c.alignment = Alignment(horizontal="left", vertical="center", indent=1)
        ws.row_dimensions[3].height = 18

# ------------------------------------------------------- SHEET 1: read me
ws = wb.active
ws.title = "Start here"
style_title_block(ws, "Literature behind the skincare ontology",
                  "Lynne  ·  MSc thesis, Beirut Arab University  ·  compiled September 2026", 3)
ws.column_dimensions['A'].width = 4
ws.column_dimensions['B'].width = 30
ws.column_dimensions['C'].width = 118

rows = [
 ("What this workbook is",
  "Every paper I found while researching the ontology chapter, with everything that matters about each one "
  "written out in plain language. 59 papers. It exists so that a supervisor can open one file and see the "
  "whole field without reading 59 PDFs."),
 ("How it was built",
  "Two search rounds. The first used general web search. The second used an academic index covering Semantic "
  "Scholar, PubMed, Scopus and arXiv, which found nine papers the first round missed and corrected two "
  "citations. The 'Did I read it' column says honestly, for each paper, whether I read the full text or only "
  "the abstract."),
 ("The five tracks",
  "B = ontologies for skincare, cosmetics and cosmetic regulation. These are the direct competitors.  "
  "C = ontology and knowledge-graph recommenders in other domains, where the mechanisms come from.  "
  "D = deep learning, the alternative I position against.  "
  "E = hybrid work combining graphs with neural methods, which is future work.  "
  "F = methodology and tools, meaning how to actually build the thing."),
 ("The sheets",
  "'The papers' is the main table, 39 columns wide. 'Head to head' compares only the skincare ontologies on "
  "the features that matter. 'My ontology' is the class and property design. 'Tools' is what to install. "
  "'Roadmap' is the six sprints. 'The gap' is the argument in one page."),
 ("Reading the main table",
  "Columns are grouped by colour band. The last five columns, on the cream background, are the only ones "
  "about MY thesis rather than about the paper. If you are short of time, read column D (priority), column E "
  "(title), and the last five columns."),
 ("The one finding to know",
  "A systematic review of 28 ontology-based recommender systems (Rahayu et al. 2022, 137 citations) found "
  "that they 'seldom use the methodology of building ontologies' and that NONE of the 28 described an "
  "ontology evaluation methodology. Naming a methodology and reporting an evaluation are therefore not "
  "housekeeping in this field. They are contributions."),
 ("The gap in one sentence",
  "No existing system combines an ingredient layer with legal standing, a record of where each claim came "
  "from, and whether the product can actually be bought in the user's market. The one knowledge graph that "
  "links cosmetic ingredients to EU regulation has no products in it at all."),
 ("What is still missing",
  "The full text of the bit-Tech 2025 paper, which is my closest competitor. Five papers are read from "
  "abstracts only and are marked as such. Citation counts are as of September 2026 and will drift."),
]
r = 5
for h, t in rows:
    c = ws.cell(row=r, column=2, value=h)
    c.font = Font(name=SERIF, size=11, bold=True, color=B_TEAL)
    c.alignment = Alignment(vertical="top", wrap_text=True)
    c = ws.cell(row=r, column=3, value=t)
    c.font = Font(name=SERIF, size=10.5, color="222222")
    c.alignment = Alignment(vertical="top", wrap_text=True)
    ws.row_dimensions[r].height = 58
    r += 2
ws.sheet_view.showGridLines = False

# --------------------------------------------------- SHEET 2: the papers
ws = wb.create_sheet("The papers")
NC = len(COLS)
style_title_block(ws, "Every paper, every detail",
    "59 papers across five tracks. Grey-blue and sand bands describe the paper. "
    "The cream band on the right is about my thesis.",
    NC, "Read the cream columns first if you are short of time.")

# group header row (row 5), column header row (row 6)
GR, HR = 5, 6
ci = 1
prev = None
start = 1
for (grp, hdr, w) in COLS + [("__end__", "", 0)]:
    if prev is not None and grp != prev:
        ws.merge_cells(start_row=GR, start_column=start, end_row=GR, end_column=ci-1)
        c = ws.cell(row=GR, column=start, value=prev.upper())
        c.font = Font(name=SERIF, size=9.5, bold=True, color=INK)
        c.fill = PatternFill("solid", fgColor=GROUP_TINT[prev])
        c.alignment = Alignment(horizontal="center", vertical="center")
        c.border = box
        start = ci
    prev = grp
    ci += 1
ws.row_dimensions[GR].height = 20

for i, (grp, hdr, w) in enumerate(COLS, start=1):
    c = ws.cell(row=HR, column=i, value=hdr)
    c.font = Font(name=SERIF, size=9.5, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=INK if grp != "For my thesis" else GOLD)
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    c.border = box
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[HR].height = 46

for ri, row in enumerate(P, start=HR+1):
    trk = row[1]
    dark, tint = TRACK_COLOUR.get(trk, (INK, "FFFFFF"))
    for i, val in enumerate(row, start=1):
        grp = COLS[i-1][0]
        c = ws.cell(row=ri, column=i, value=val)
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        c.border = box
        if i == 2:            # track letter
            c.font = Font(name=SERIF, size=11, bold=True, color=PAPER)
            c.fill = PatternFill("solid", fgColor=dark)
            c.alignment = Alignment(horizontal="center", vertical="center")
        elif i == 3:          # short name
            c.font = Font(name=SERIF, size=10, bold=True, color=dark)
            c.fill = PatternFill("solid", fgColor=tint)
        elif i == 4:          # priority
            hot = any(k in str(val).upper() for k in
                      ("URGENT","CITE IN INTRO","CHECK FIRST","TEMPLATE","THE BRIDGE","MY "))
            c.font = Font(name=SERIF, size=9.5, bold=hot,
                          color="8A1C1C" if hot else "555555")
            c.fill = PatternFill("solid", fgColor="FBEEDC" if hot else PAPER)
        elif i == 12:         # link
            c.font = Font(name=MONO, size=8, color="1F5C99", underline="single")
            c.fill = PatternFill("solid", fgColor=PAPER)
        elif grp == "For my thesis":
            c.font = Font(name=SERIF, size=9.5, color="1E1E1E")
            c.fill = PatternFill("solid", fgColor=MINE)
        else:
            c.font = Font(name=SERIF, size=9.5, color="222222")
            c.fill = PatternFill("solid", fgColor=PAPER if ri % 2 else "F5F1EA")
    ws.row_dimensions[ri].height = 116

ws.freeze_panes = "E7"
ws.auto_filter.ref = f"A{HR}:{get_column_letter(NC)}{HR+len(P)}"
ws.sheet_view.showGridLines = False

# ----------------------------------------------- SHEET 3: head to head
ws = wb.create_sheet("Head to head")
style_title_block(ws, "The skincare ontologies, side by side",
  "Only the direct competitors. The last column is this thesis. Read down the last column and across the rows.",
  10, "The four rows in bold are the ones nobody else fills together.")

H2H_COLS = ["What I am comparing","Moe & Aung 2014","OntoCosmetic 2021/23","Hansanie 2024",
            "Abesova 2023","bit-Tech 2025","Utari 2023","TOXIN 2025","HaCKG 2025","THIS THESIS"]
H2H = [
 ("Peer reviewed","Weak venue","Yes","Yes","No, student project","Yes","Yes","Yes","Yes","To be",False),
 ("Ontology publicly downloadable","No","YES, purl.org","No","No","Unknown","No","YES","Unknown","Planned, w3id + Zenodo",True),
 ("Named building methodology","Eight tasks, unnamed","None","None","Middle out","METHONTOLOGY","METHONTOLOGY","None","None","MOMo + LOT",False),
 ("How many products","Not reported","279 individuals","Not reported","Sephora subset","3,800","62","None","Cosmetics set","12,629",False),
 ("Ingredients linked to a legal register","No","No","No","No","Own allergen class","No","YES, SCCS","No","YES, CosIng 28,573 entries",True),
 ("How the data got in","Not reported","By hand","Not reported","OntoRefine","Scraping","Not reported","R2RML","Not reported","RML / Morph-KGC",False),
 ("Reasoner","None","SWRL in Protege","Pellet","Class restrictions","Jena Fuseki","SPARQL only","Not stated","None","HermiT + SHACL",False),
 ("SPARQL","No","No","Via Owlready2","YES, it is the mechanism","Yes","Yes","Yes","No","Yes",False),
 ("Links to outside data","No","No","No","DBpedia","No","No","OBO, KEGG, UniProt","No","Wikidata, CosIng, DermO",False),
 ("Records where each claim came from","No","Rule sources only","No","No","No","No","Named graphs","No","YES, 4 evidence levels + PROV-O",True),
 ("Price or availability modelled","A PriceRange class","Price as a criterion","No","Shop page link","No","No","No","No","YES, two currencies, per shop, dated",True),
 ("Local market","No","No","No","No","Indonesia","Indonesia","No","No","LEBANON",False),
 ("Neural component","No","No","CNN for acne","No","No","No","No","Graph attention network","No, positioned as future work",False),
 ("Evaluated against ground truth","No","No","Partly, 24-person survey","No","Unclear","SPARQL only","Use cases","Benchmarks","Planned, four layers",False),
 ("What it is actually for","Cross-domain matching","Making a stable cream","Grading acne from a photo","Building a routine","Indonesian retail","Proof of concept","Animal-free risk assessment","Halal prediction","Buying skincare in Lebanon, with a reason",False),
]
for i, h in enumerate(H2H_COLS, start=1):
    c = ws.cell(row=6, column=i, value=h)
    c.font = Font(name=SERIF, size=10, bold=True,
                  color=PAPER if i < 10 else INK)
    c.fill = PatternFill("solid", fgColor=INK if i < 10 else GOLD)
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    c.border = box
    ws.column_dimensions[get_column_letter(i)].width = 34 if i == 1 else (30 if i == 10 else 22)
ws.row_dimensions[6].height = 40
for ri, row in enumerate(H2H, start=7):
    key = row[-1]
    for i, val in enumerate(row[:-1], start=1):
        c = ws.cell(row=ri, column=i, value=val)
        c.border = box
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        if i == 1:
            c.font = Font(name=SERIF, size=10, bold=key, color=B_TEAL if key else INK)
            c.fill = PatternFill("solid", fgColor="E3EDEC" if key else "EDE7DD")
        elif i == 10:
            c.font = Font(name=SERIF, size=10, bold=True, color="6B4A00")
            c.fill = PatternFill("solid", fgColor=MINE)
        else:
            c.font = Font(name=SERIF, size=9.5, color="333333")
            c.fill = PatternFill("solid", fgColor=PAPER if ri % 2 else "F5F1EA")
    ws.row_dimensions[ri].height = 34
ws.freeze_panes = "B7"
ws.sheet_view.showGridLines = False

# ------------------------------------------------ SHEET 4: my ontology
ws = wb.create_sheet("My ontology")
style_title_block(ws, "The ontology I am going to build",
  "Four modules. Every class and property, with where it came from and which of my 42 dataset columns it holds.",
  6)
oc = ["Module","Kind","Name","What it means in plain language","Where it comes from","Which of my columns"]
for i,h in enumerate(oc, start=1):
    c = ws.cell(row=6, column=i, value=h)
    c.font = Font(name=SERIF, size=10, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=INK)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    c.border = box
    ws.column_dimensions[get_column_letter(i)].width = [18,16,30,62,34,30][i-1]
ws.row_dimensions[6].height = 30

ONT = [
 ("core","Class","SkinType","Oily, Dry, Normal, Combination","Hansanie & Silva; Abesova","skin_type"),
 ("core","Class","Sensitivity","Sensitive or not","My dataset","sensitivity"),
 ("core","Class","SkinConcern","Acne, dryness, redness, hyperpigmentation, wrinkles, dullness, pores, oiliness","Mine, to be ALIGNED TO DermO","concerns"),
 ("core","SKOS concept","Benefit","Hydrating, brightening, soothing. These are labels people use, not logical classes, so SKOS not OWL","SKOS","benefits"),
 ("core","Class","IngredientFunction","Emollient, humectant, preservative, UV filter, surfactant, antioxidant, solvent, viscosity controller, skin conditioning, fragrance, chelating agent","Names taken from CosIng; aligned to OntoCosmetic","ingredient_functions"),
 ("core","Class","RegulatoryStatus","Prohibited (Annex II), Restricted (III), Permitted colorant (IV), preservative (V), UV filter (VI), Declarable allergen (the EU 26)","Regulation (EC) 1223/2009","restricted_ingredients"),
 ("core","Individual","Annex","AnnexII to AnnexVI. These are specific entries, not kinds of thing, so individuals not classes","Noy & McGuinness test","restricted_ingredients"),
 ("core","Class","Authority","European Commission, SCCS, and later the Lebanese Ministry of Health. A status is always granted BY somebody","Halal flavouring ontology pattern","n/a, new"),
 ("product","Class","Product","The thing on the shelf. Subclasses: Cleanser, Moisturiser (with SunCare under it), Serum, Toner, Exfoliant (chemical and physical), Mask, EyeCare, Treatment","schema:Product; taxonomy from Abesova","product_type"),
 ("product","Class","Ingredient","One individual per CosIng entry, identified by its register ID not by its name","CosIng","ingredients"),
 ("product","Class","IngredientListing","REIFIED. An ingredient AT A POSITION in one product's list. Needed because INCI order is concentration order, and a plain triple has no room for the position","N-ary relation design pattern","ingredients, ingredient_count"),
 ("product","Class","Brand","The maker","schema:Brand, linked to Wikidata","brand"),
 ("product","Class","Offer","A price, from one shop, on one date. SEPARATE from the product, which is why one lotion can carry two Beirut prices","schema:Offer","price_usd, price_lbp, price_seen_date"),
 ("product","Class","Shop","Online or physical","schema.org + mine","shops_in_lebanon, sold_by_shops"),
 ("product","Class","Country","Where a brand or shop is","schema.org","country"),
 ("evidence","Class","Claim","REIFIED. A statement about a product, carrying who said it, where, when, the exact sentence, and how much that source is worth. THIS IS THE CONTRIBUTION","PROV-O specialisation; precedent in O'Sullivan 2025","skin_type_source, price_source, rating_source"),
 ("evidence","Class","EvidenceLevel","ManufacturerStated (1), RetailerStated (2), WeakSourceStated (3), FormulaInferred (4)","Mine","skin_type_source"),
 ("evidence","Class","prov:Agent","Manufacturer, Retailer, InferenceProcedure. Whoever made the claim","PROV-O","all source columns"),
 ("lebanon","Class","LebaneseShop","A shop that actually sells here","Mine","shops_in_lebanon"),
 ("lebanon","Class","ConsumerNeed","A need as an entity in its own right, not an attribute. Budget-constrained routine, single-shop routine, humid-season routine, occasion routine","AliCoCo (SIGMOD 2020)","new, the original claim"),
 ("--","--","--","--","--","--"),
 ("product","Object property","skc:hasListing","Links a product to one positioned ingredient entry","N-ary pattern","ingredients"),
 ("product","Object property","skc:listsIngredient","Which ingredient that entry refers to","Mine","ingredients"),
 ("product","Object property","skc:hasIngredient","Shortcut from product straight to ingredient, so simple queries stay simple","Mine, inferred","ingredients"),
 ("core","Object property","skc:hasFunction","What an ingredient does","CosIng","ingredient_functions"),
 ("core","Object property","skc:restrictedUnder","Which annex restricts this ingredient","Regulation 1223/2009","restricted_ingredients"),
 ("core","Object property","skc:accordingTo","WHICH AUTHORITY says so. Leaves room for Lebanese regulation later","Halal ontology pattern","new"),
 ("product","Object property","skc:suitableFor","Product suits a skin type","Hansanie & Silva","skin_type"),
 ("product","Object property","skc:addressesConcern","Product addresses a concern","Mine","concerns"),
 ("product","Object property","skc:notRecommendedFor","Product should be avoided for a skin type","Mine, inferred by rule","derived"),
 ("product","Object property","schema:offers","Product to Offer","schema.org","price columns"),
 ("product","Object property","schema:seller","Offer to Shop. NOTE the price lives on the Offer, not the Product","schema.org","sold_by_shops"),
 ("evidence","Object property","skc:hasClaim","Product to Claim","Mine","source columns"),
 ("evidence","Object property","skc:hasEvidenceLevel","Claim to its level","Mine","skin_type_source"),
 ("evidence","Object property","prov:wasAttributedTo","Who said it","PROV-O","source columns"),
 ("evidence","Object property","prov:wasDerivedFrom","The page it was read from","PROV-O","evidence file URLs"),
 ("lebanon","Object property","skc:satisfiedBy","A need is satisfied by a product or a set of them","AliCoCo","new"),
 ("--","--","--","--","--","--"),
 ("product","Data property","skc:atPosition","Where in the INCI list. Concentration order","MVFM paper uses this too","derived from ingredients"),
 ("product","Data property","skc:cosingCoverage","What share of the formula was found in the register","Mine","cosing_coverage"),
 ("product","Data property","skc:ingredientCount","How many ingredients","Mine","ingredient_count"),
 ("product","Data property","schema:price","On the Offer","schema.org","price_usd"),
 ("product","Data property","skc:priceSeenDate","When that price was true","Mine","price_seen_date"),
 ("--","--","--","--","--","--"),
 ("lebanon","DEFINED CLASS","SensitiveSafeProduct","Any product NONE of whose ingredients is a declarable allergen. I never list them; the reasoner works it out. Expect about 9,537","Abesova's mechanism","derived from ingredients"),
 ("lebanon","DEFINED CLASS","AvailableInLebanon","Any product with at least one Offer from a Lebanese shop. Expect about 11,937","Mine","shops_in_lebanon"),
 ("lebanon","DEFINED CLASS","ManufacturerStatedProduct","Any product whose suitability claim is level 1. Expect about 4,460","Mine","skin_type_source"),
 ("lebanon","DEFINED CLASS","RegulatedProduct","Contains at least one restricted ingredient. Expect about 9,613","Mine","restricted_ingredients"),
 ("lebanon","DEFINED CLASS","FullyIdentifiedProduct","Every ingredient found in the register. Expect about 9,032","Mine","cosing_coverage"),
 ("lebanon","DEFINED CLASS","NaturalClaimProduct","Marketed as natural. Built to TEST against Klaschka's finding that 56% of natural INCI substances are classified hazardous","Klaschka 2015","free_from, product_summary"),
]
for ri, row in enumerate(ONT, start=7):
    sep = row[0] == "--"
    for i, val in enumerate(row, start=1):
        c = ws.cell(row=ri, column=i, value="" if sep else val)
        c.border = box
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        if sep:
            c.fill = PatternFill("solid", fgColor=INK)
        elif "DEFINED" in str(row[1]):
            c.font = Font(name=SERIF, size=9.5, bold=(i==3), color="6B4A00")
            c.fill = PatternFill("solid", fgColor=MINE)
        elif row[0] == "evidence":
            c.font = Font(name=SERIF, size=9.5, bold=(i==3), color=INK)
            c.fill = PatternFill("solid", fgColor=TINT_C)
        else:
            c.font = Font(name=SERIF, size=9.5, bold=(i==3), color="222222")
            c.fill = PatternFill("solid", fgColor=PAPER if ri%2 else "F5F1EA")
    ws.row_dimensions[ri].height = 8 if sep else 42
ws.freeze_panes = "A7"
ws.sheet_view.showGridLines = False

# ------------------------------------------------------ SHEET 5: tools
ws = wb.create_sheet("Tools")
style_title_block(ws, "What to install, and why that one",
  "Every choice has a reason and, where possible, a paper that already did it this way.", 6)
tc = ["Job","The tool I chose","Why this one","What I rejected, and why","Cost","Link"]
for i,h in enumerate(tc, start=1):
    c = ws.cell(row=6, column=i, value=h)
    c.font = Font(name=SERIF, size=10, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=F_OLIVE)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    c.border = box
    ws.column_dimensions[get_column_letter(i)].width = [26,26,66,52,12,44][i-1]
ws.row_dimensions[6].height = 28
TOOLS = [
 ("Drawing the modules","CoModIDE","The tool built for the MOMo methodology I am following. Draw the module, get the OWL","Drawing in PowerPoint. It does not produce anything machine readable","Free","https://comodide.com/"),
 ("Editing the ontology","Protege 5.6","Standard, everyone knows it, reasoners built in. I use it to check the reasoner is happy and to produce the class hierarchy screenshot","WebProtege is nicer for sharing but has fewer features","Free","https://protege.stanford.edu/"),
 ("The source of truth","Hand-edited Turtle in git","Diffs cleanly, reviewable, and it is what other people will download. Protege files do not diff well","Keeping the Protege file as the master. It makes version control useless","Free","https://www.w3.org/TR/turtle/"),
 ("Finding an existing term","Linked Open Vocabularies","Search before inventing. This single habit is what separates an amateur ontology from a professional one","Inventing terms and hoping. LOT and MOMo both say reuse first","Free","https://lov.linkeddata.es/dataset/lov/"),
 ("Getting my CSV into the graph","Morph-KGC with a YARRRML mapping","THE most important tool decision. A declarative mapping file goes in my appendix, is auditable, and rebuilds the graph with one command. TOXIN used R2RML for cosmetic data in a peer-reviewed Oxford journal","A Python script with RDFLib. It produces the same triples but nobody can audit it and it is not citable. OntoRefine is good but traps the mapping inside GraphDB","Free","https://morph-kgc.readthedocs.io/"),
 ("Documenting the mapping","RMLdoc","Turns the mapping file into readable documentation with diagrams. Free thesis appendix material","Writing the documentation by hand","Free","https://github.com/oeg-upm/rmldoc"),
 ("Storing and querying","GraphDB Free","Reasoning built in, OntoRefine included, and a visual graph explorer. Showing a supervisor a picture of the graph is worth more than any paragraph","Apache Jena Fuseki is simpler and free but its reasoning is weak. Stardog is stronger but commercial","Free desktop","https://graphdb.ontotext.com/"),
 ("Working out what follows","HermiT","Ships with Protege, solid default, fast enough","Pellet and ELK. But NOTE: if I write SWRL rules I must switch to Openllet, because HermiT ignores rules silently","Free","http://www.hermit-reasoner.com/"),
 ("Rules OWL cannot express","Openllet, only if needed","Handles SWRL, which HermiT does not. OntoCosmetic used SWRL for the same kind of rules","Writing everything as SWRL. Rules make reasoning slower and consistency undecidable","Free","https://github.com/Galigator/openllet"),
 ("Checking my data is right","SHACL via pySHACL","OWL cannot say 'every product MUST have a brand', because it assumes anything unstated might be true. SHACL can. This is where validate_dataset.py moves to","Relying on the reasoner for validation. It is the wrong tool and will silently accept bad data","Free","https://github.com/RDFLib/pySHACL"),
 ("Checking my DESIGN is right","OOPS!","41 known design pitfalls graded critical, important, minor. One afternoon for a concrete evaluation number that no paper in my competitor set has","Not evaluating the design at all, which is what 28 of 28 reviewed studies did","Free web tool","https://oops.linkeddata.es/"),
 ("Checking it is FAIR","FOOPS!","24 checks across Findable, Accessible, Interoperable, Reusable. Since I criticise track B for not publishing, I must measure my own","Asserting the ontology is FAIR without measuring","Free web tool","https://w3id.org/foops/"),
 ("Structural numbers","OntoMetrics","Depth, breadth, richness. Comparable numbers for the evaluation table","Reporting only a class count","Free","https://ontometrics.informatik.uni-rostock.de/"),
 ("Python access","Owlready2 and RDFLib","My whole pipeline is Python. Owlready2 also runs a reasoner from code, which Hansanie and Silva used","The Java OWL API. Powerful but wrong language for me","Free","https://owlready2.readthedocs.io/"),
 ("Documentation for humans","WIDOCO","Generates a readable HTML page from the ontology itself, so the documentation cannot drift from the code","Writing documentation by hand and letting it go stale","Free","https://github.com/dgarijo/Widoco"),
 ("A permanent address","w3id.org","A stable IRI that survives me changing hosting. A pull request on GitHub","A university URL that dies when I graduate, or a purl","Free","https://w3id.org/"),
 ("A citable version","Zenodo","A DOI per release, so the ontology can be cited like a paper. One of my five gap findings is that track B does not publish","Putting it on GitHub only. No DOI means no proper citation","Free","https://zenodo.org/"),
]
for ri,row in enumerate(TOOLS, start=7):
    for i,val in enumerate(row, start=1):
        c = ws.cell(row=ri, column=i, value=val)
        c.border = box
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        if i==2:
            c.font = Font(name=SERIF, size=10, bold=True, color=F_OLIVE)
            c.fill = PatternFill("solid", fgColor=TINT_F)
        elif i==6:
            c.font = Font(name=MONO, size=8, color="1F5C99", underline="single")
            c.fill = PatternFill("solid", fgColor=PAPER)
        else:
            c.font = Font(name=SERIF, size=9.5, color="222222")
            c.fill = PatternFill("solid", fgColor=PAPER if ri%2 else "F5F1EA")
    ws.row_dimensions[ri].height = 60
ws.freeze_panes = "B7"
ws.sheet_view.showGridLines = False

# ---------------------------------------------------- SHEET 6: roadmap
ws = wb.create_sheet("Roadmap")
style_title_block(ws, "Six sprints, from here to a published ontology",
  "Each sprint produces something I can show. Nothing is blocked on anything I do not already have.", 6)
rc = ["Sprint","What I do","Why it comes here","What exists at the end","Which paper told me to do this","Risk if I skip it"]
for i,h in enumerate(rc, start=1):
    c = ws.cell(row=6, column=i, value=h)
    c.font = Font(name=SERIF, size=10, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=E_INDIGO)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    c.border = box
    ws.column_dimensions[get_column_letter(i)].width = [12,56,54,46,34,50][i-1]
ws.row_dimensions[6].height = 28
ROAD = [
 ("1. Ask the questions first",
  "Write the requirements document: purpose, scope, who it is for, what it is NOT for, and 15 competency questions the ontology must be able to answer",
  "Everything downstream gets checked against these. It is three pages of writing, not code, and it is the highest-value hour available",
  "requirements.md, and 15 questions that also become my evaluation chapter",
  "LOT (Poveda-Villalon 2022); Noy & McGuinness 101",
  "I build classes nobody needs and cannot prove the ontology works at the end"),
 ("2. Look before building",
  "Go through all 42 columns and decide: reuse an existing term or invent one. Check three things that could each save weeks: the CosIng RDF on GitHub, DermO on BioPortal, and Wikidata coverage of my 1,463 brands",
  "If CosIng already exists as usable RDF, my entire ingredient layer arrives free and cited. Finding that out AFTER building it would be painful",
  "A 42-row table that goes straight into the thesis, and possibly a free ingredient layer",
  "LOT and MOMo both put reuse before building; Grau et al. on safe reuse",
  "I reinvent 28,573 ingredient entries that already exist in RDF"),
 ("3. Build the four modules",
  "Draw each module as a diagram first, then write the Turtle. core, product, evidence, user, plus the Lebanon file that imports them",
  "Modules change at completely different speeds. Product data changes weekly, clinical knowledge barely changes. I can hand a dermatologist ONE small file instead of 12,629 rows",
  "The ontology itself, and the diagrams my thesis chapter needs anyway",
  "MOMo (Shimizu 2022); Hansanie & Silva did the same and said why",
  "One monolithic file that nobody can review, reuse or update in parts"),
 ("4. Fill it up",
  "Build the long-format helper file (one row per ingredient mention, about 295,991 rows), write the YARRRML mapping, run Morph-KGC, load into GraphDB as named graphs split by source",
  "This is the step that decides whether this is a METHOD or a script. A mapping file is auditable, citable and rerunnable. Named graphs mean I can reload one source without touching the others",
  "Roughly 1.8 million triples, and a mapping file for the appendix",
  "TOXIN used R2RML; Abesova used OntoRefine; Morph-KGC papers",
  "An unauditable script, and no way to trace which source a statement came from"),
 ("5. Make it think, then check it",
  "Turn on the defined classes, run HermiT, write the SHACL shapes, run OOPS! and FOOPS!. PREDICT each defined class size first, then compare against what the reasoner actually produces",
  "Predicting then checking is a real validation step. If SensitiveSafeProduct does not come out near 9,537, my model is wrong and I want to know now",
  "Evaluation numbers, and the 593 sensitive-marked products containing EU allergens surfacing as a FORMAL inconsistency rather than a note in a README",
  "Abesova for defined classes; OOPS! and FOOPS! papers; Rahayu on the evaluation gap",
  "I publish an ontology whose defined classes were never checked against reality"),
 ("6. Publish and prove",
  "w3id address, WIDOCO documentation, Zenodo DOI. Then answer every one of the 15 competency questions with a SPARQL query and put the query and its result in the thesis",
  "One of my five criticisms of the existing literature is that almost nothing is published. I cannot make that criticism and then not publish. And the CQ answers ARE the evaluation chapter",
  "A citable artefact with a DOI, and a complete evaluation chapter",
  "LOT publication activity; FoodKG and COPPER both publish; Braun 2025 is the template",
  "The thesis ends with a claim instead of an artefact, and the field cannot build on it"),
]
for ri,row in enumerate(ROAD, start=7):
    for i,val in enumerate(row, start=1):
        c = ws.cell(row=ri, column=i, value=val)
        c.border = box
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        if i==1:
            c.font = Font(name=SERIF, size=11, bold=True, color=PAPER)
            c.fill = PatternFill("solid", fgColor=E_INDIGO)
        elif i==6:
            c.font = Font(name=SERIF, size=9.5, italic=True, color="8A1C1C")
            c.fill = PatternFill("solid", fgColor="FBEEDC")
        else:
            c.font = Font(name=SERIF, size=9.5, color="222222")
            c.fill = PatternFill("solid", fgColor=PAPER if ri%2 else "F5F1EA")
    ws.row_dimensions[ri].height = 96
ws.freeze_panes = "B7"
ws.sheet_view.showGridLines = False

# ---------------------------------------------------- SHEET 7: the gap
ws = wb.create_sheet("The gap")
style_title_block(ws, "The argument, in one page",
  "What is missing across the whole literature, what I do about it, and how strong each claim is.", 5)
gc = ["What is missing everywhere","How I know","What I do about it","How strong is that claim","Where it goes"]
for i,h in enumerate(gc, start=1):
    c = ws.cell(row=6, column=i, value=h)
    c.font = Font(name=SERIF, size=10, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=C_PLUM)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    c.border = box
    ws.column_dimensions[get_column_letter(i)].width = [46,58,58,44,26][i-1]
ws.row_dimensions[6].height = 28
GAP = [
 ("No ingredient layer with legal standing",
  "Every skincare ontology I found stores ingredients as free text or a small hand-made list. The ONE knowledge graph that links cosmetic ingredients to EU law (TOXIN, Oxford, 2025) contains no products at all",
  "Ingredients are individuals identified by their CosIng register entry, so regulatory status is INHERITED from the European Commission rather than asserted by me. 99.2% of products with a formula are linked",
  "STRONGEST. Nobody has both halves. This is the thesis",
  "Contribution 1"),
 ("Nobody records where a claim came from",
  "No reviewed skincare ontology says who asserted a claim or how much that source is worth. Every claim is presented as equally true",
  "Every suitability claim is a Claim entity carrying its source, the exact sentence it was read from, the date, and one of four evidence levels. Specialised from PROV-O, a W3C standard",
  "STRONG. The pattern exists elsewhere (O'Sullivan 2025), which is GOOD: I reuse rather than invent",
  "Contribution 2"),
 ("Everyone assumes you can buy the product",
  "Every reviewed system recommends without asking whether the item is obtainable. In Lebanon that assumption fails, and it fails differently for imported and locally made products",
  "Price in two currencies, per shop, with the date it was observed. Availability as a defined class. 11,937 products with at least one Lebanese shop",
  "STRONG AND UNIQUE. No cosmetics system models purchasability",
  "Contribution 3"),
 ("Almost nothing is published",
  "One of six reviewed skincare ontologies is publicly resolvable. The field cannot build on its own results",
  "w3id address, WIDOCO documentation, Zenodo DOI, named methodology, and a FOOPS! FAIR score I actually measure",
  "EASY AND RARE. Costs a week, and one in six competitors manages it",
  "Contribution 4"),
 ("Evaluation is weak or absent",
  "Rahayu et al. (2022), reviewing 28 ontology-based recommenders, found that NONE described an evaluation methodology. In my own set: two report satisfaction on under 30 people, one is a case study, one admits expert testing never happened",
  "Four layers: structural (OOPS!, FOOPS!, OntoMetrics), functional (15 competency questions as SPARQL), logical (predicted vs inferred membership of six defined classes), comparative (the head-to-head sheet)",
  "STRONG, and cheap. None of it needs users I do not have",
  "Evaluation chapter"),
 ("Nobody models what the user actually NEEDS",
  "Concerns are modelled everywhere as an attribute of a product. AliCoCo (SIGMOD 2020) argues that leaves a semantic gap, because shoppers think in needs, not categories",
  "Lebanese consumer needs as first-class entities: a routine under twenty dollars a month, one that survives a power cut, one buyable in a single pharmacy",
  "MOST ORIGINAL, LEAST CERTAIN. Attempt it AFTER the four safe claims are delivered",
  "Contribution 5, optional"),
]
for ri,row in enumerate(GAP, start=7):
    for i,val in enumerate(row, start=1):
        c = ws.cell(row=ri, column=i, value=val)
        c.border = box
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        if i==1:
            c.font = Font(name=SERIF, size=10.5, bold=True, color=C_PLUM)
            c.fill = PatternFill("solid", fgColor=TINT_C)
        elif i==4:
            c.font = Font(name=SERIF, size=9.5, bold=True, color="6B4A00")
            c.fill = PatternFill("solid", fgColor=MINE)
        else:
            c.font = Font(name=SERIF, size=9.5, color="222222")
            c.fill = PatternFill("solid", fgColor=PAPER if ri%2 else "F5F1EA")
    ws.row_dimensions[ri].height = 88

r = 7 + len(GAP) + 2
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
c = ws.cell(row=r, column=1, value="THE WHOLE ARGUMENT IN ONE SENTENCE")
c.font = Font(name=SERIF, size=11, bold=True, color=PAPER)
c.fill = PatternFill("solid", fgColor=INK)
c.alignment = Alignment(vertical="center", indent=1)
ws.row_dimensions[r].height = 24
ws.merge_cells(start_row=r+1, start_column=1, end_row=r+1, end_column=5)
c = ws.cell(row=r+1, column=1, value=
  "No system anywhere combines an ingredient layer with legal standing, a record of where each claim came from, "
  "and whether the product can actually be bought in the user's market. The one knowledge graph that links "
  "cosmetic ingredients to European regulation has no products in it. Every skincare ontology has products and "
  "no regulation. This thesis is the intersection, built for Lebanon, on 12,629 products.")
c.font = Font(name=SERIF, size=11, color=INK)
c.fill = PatternFill("solid", fgColor=MINE)
c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
ws.row_dimensions[r+1].height = 62
ws.sheet_view.showGridLines = False

# ------------------------------------------------------------------ save
out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "THESIS_LITERATURE_TABLE.xlsx")
wb.save(out)
print("written:", out)
print("papers:", len(P), " columns:", len(COLS), " sheets:", len(wb.sheetnames))
print("sheets:", wb.sheetnames)
