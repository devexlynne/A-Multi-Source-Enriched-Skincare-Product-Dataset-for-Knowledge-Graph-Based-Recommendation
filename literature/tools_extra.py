# -*- coding: utf-8 -*-
"""
The whole Tools tab, rebuilt.

Seven columns, and every cell is short on purpose:

  Tool | What it is | Used by | How they used it | Us? | Why | Link

"Used by" names the actual paper. "-" means nobody in my review used it.
"""

TOOLS_COLS = [
    ("Tool", 24),
    ("What it is", 34),
    ("Used by", 22),
    ("How they used it", 42),
    ("Us?", 7),
    ("Why", 40),
    ("Link", 30),
]

TOOLS = [

 ("H", "1. Languages"),

 ("RDF", "Data written as three-part facts", "everyone",
  "The base layer under every ontology here",
  "yes", "What an ontology is made of", "w3.org/TR/rdf11-primer"),

 ("Turtle (.ttl)", "The readable way to write RDF", "Abesova, TOXIN",
  "Abesova exported nine .ttl files and merged them",
  "yes", "Humans can read it, and it diffs in git", "w3.org/TR/turtle"),

 ("OWL", "RDF plus logic", "Moe & Aung, OntoCosmetic, Hansanie, Abesova, COPPER, DermO",
  "Abesova defined OilySkinProducts as hasOilyScore value 5",
  "yes", "My defined classes need it", "w3.org/TR/owl2-primer"),

 ("SPARQL", "The query language for graphs", "Abesova, bit-Tech, Utari, FoodKG, Di Noia",
  "Abesova ranks reviews and picks the top 3 per category",
  "yes", "My 15 competency questions become 15 queries", "w3.org/TR/sparql11-query"),

 ("SWRL", "If-then rules on top of OWL", "OntoCosmetic",
  "Formulation rules with a high and low threshold each",
  "maybe", "Slows the reasoner. Two rules at most", "w3.org/submissions/SWRL"),

 ("SHACL", "Checks data and can infer", "nobody. 0 of 28",
  "-",
  "yes", "OWL cannot report an error. SHACL can", "w3.org/TR/shacl"),

 ("R2RML / RML", "A file saying which column becomes what", "TOXIN KG",
  "Turned toxicology spreadsheets into triples",
  "yes", "The mapping file goes in my appendix", "rml.io"),

 ("H", "2. How you build it. Five of my 28 papers used no Protege at all."),

 ("Protege", "Free desktop ontology editor, Stanford", "Moe & Aung, OntoCosmetic, Hansanie, DermO, COPPER",
  "Built classes by clicking, ran the reasoner from the menu",
  "yes", "Standard, free, reasoners built in", "protege.stanford.edu"),

 ("OntoRefine", "Point-and-click CSV to RDF, in GraphDB", "Abesova",
  "Drew the mapping for the Sephora review CSV. No Protege at all",
  "no", "The mapping is stuck inside GraphDB. I cannot publish it", "graphdb.ontotext.com"),

 ("RML mapping file", "No editor. The mapping defines the graph", "TOXIN KG",
  "Wrote R2RML and never opened an editor",
  "yes", "This is how my pipeline works. Built by script, not clicking", "rml.io"),

 ("Apache Jena Fuseki", "Triple store with a SPARQL endpoint", "bit-Tech 2025",
  "Stored and queried the graph. No editor at all",
  "no", "Weaker reasoning than GraphDB", "jena.apache.org"),

 ("WebProtege", "Protege in a browser, two people at once", "-",
  "-",
  "maybe", "If my supervisor wants to comment in the file", "webprotege.stanford.edu"),

 ("TopBraid Composer", "Commercial editor, best SHACL support", "-",
  "-",
  "no", "Commercial. Written by the SHACL authors", "topquadrant.com"),

 ("VocBench 3", "Web editor for thesauri and SKOS", "-",
  "-",
  "no", "Built for word lists, not defined classes", "vocbench.uniroma2.it"),

 ("ROBOT", "Command-line ontology jobs", "-",
  "-",
  "maybe", "Makes the build repeatable instead of clicked", "github.com/ontodev/robot"),

 ("LinkML", "Write YAML, get OWL and SHACL out", "-",
  "-",
  "maybe", "One source, so OWL and SHACL cannot drift apart", "linkml.io"),

 ("Chowlk", "Draw a diagram, get OWL", "-",
  "-",
  "maybe", "I need diagrams anyway. Draw once", "chowlk.linkeddata.es"),

 ("OWLGrEd", "Draws an OWL file as a picture", "-",
  "-",
  "maybe", "Only to make the figure for the chapter", "owlgred.lumii.lv"),

 ("CoModIDE", "Drag-and-drop ontology modules", "-",
  "-",
  "maybe", "Same idea as Chowlk", "comodide.com"),

 ("Owlready2", "Python library for ontologies", "Hansanie & Silva",
  "Queried the ontology from their Python app",
  "yes", "My pipeline is Python", "owlready2.readthedocs.io"),

 ("RDFLib", "Python library for RDF", "-",
  "-",
  "yes", "Pairs with Owlready2 and pySHACL", "rdflib.readthedocs.io"),

 ("H", "3. Reasoners and rules"),

 ("RDFS entailment", "Subclass and domain/range only", "Abesova",
  "Free in GraphDB, always on",
  "yes", "Cheapest reasoning. Does the hierarchy only", "w3.org/TR/rdf-mt"),

 ("HermiT", "OWL reasoner, ships with Protege", "-",
  "-",
  "yes", "Fills my defined classes. Solid default", "hermit-reasoner.com"),

 ("Pellet / Openllet", "OWL reasoner that also runs SWRL", "Hansanie & Silva",
  "Checked the ontology was consistent",
  "maybe", "Only if I write SWRL rules", "github.com/Galigator/openllet"),

 ("ELK", "Very fast reasoner, limited logic", "-",
  "-",
  "no", "Too limited for my defined classes", "github.com/liveontologies/elk-reasoner"),

 ("OWL 2 profiles", "RL, EL, QL, DL. Power against speed", "-",
  "-",
  "yes", "I should name mine in the chapter. It is DL", "w3.org/TR/owl2-profiles"),

 ("SPARQL CONSTRUCT", "A query that writes new triples", "Abesova",
  "Built the OilyScore triples, then the reasoner used them",
  "yes", "Simple, but the rules sit in loose files", "w3.org/TR/sparql11-query"),

 ("SHACL Core", "Reports which product broke a rule", "-",
  "-",
  "yes", "Validates my 12,629 rows. OWL cannot", "w3.org/TR/shacl"),

 ("sh:TripleRule", "Adds a triple when a condition holds", "-",
  "-",
  "yes", "Can infer any triple. OWL only infers types", "w3.org/TR/shacl-af"),

 ("sh:SPARQLRule", "A rule that counts and writes back", "-",
  "-",
  "yes", "OWL cannot count. This is why I add SHACL", "w3.org/TR/shacl-af"),

 ("pySHACL", "SHACL validator in Python", "-",
  "-",
  "yes", "My pipeline is Python", "github.com/RDFLib/pySHACL"),

 ("Apache Jena SHACL", "SHACL validator in Java, the fastest", "-",
  "-",
  "maybe", "Four times faster. Only if pySHACL gets slow", "jena.apache.org/documentation/shacl"),

 ("H", "4. Where the graph lives"),

 ("GraphDB", "Triple store with reasoning built in", "Abesova",
  "Held the merged graph and ran the class restrictions",
  "yes", "Free desktop edition, SHACL built in", "graphdb.ontotext.com"),

 ("Morph-KGC", "Python engine that runs an RML file", "-",
  "-",
  "yes", "One command turns my CSV into triples", "morph-kgc.readthedocs.io"),

 ("Stardog / Virtuoso", "Commercial triple stores", "-",
  "-",
  "no", "I do not need the scale", "stardog.com"),

 ("H", "5. Vocabularies I reuse instead of inventing"),

 ("schema.org", "Google's vocabulary for products", "-",
  "-",
  "yes", "Product, Offer, price, brand. Already understood", "schema.org"),

 ("PROV-O", "W3C standard for where a fact came from", "TOXIN KG (named graphs)",
  "One graph per source, so provenance is never lost",
  "yes", "Turns my evidence levels into a standard", "w3.org/TR/prov-o"),

 ("SKOS", "For lists of words, not classes", "-",
  "-",
  "yes", "My benefits list is terms, not logic", "w3.org/TR/skos-reference"),

 ("Dublin Core", "Title, creator, date, licence", "-",
  "-",
  "yes", "Makes the ontology citable. Cheap", "dublincore.org"),

 ("geo: and dbo:", "Coordinates and DBpedia terms", "Abesova",
  "Country to capital city to lat and long, for a map",
  "no", "Wikidata is better maintained now", "dbpedia.org"),

 ("H", "6. Outside data I link to"),

 ("CosIng", "The EU official ingredient database", "-",
  "-",
  "yes", "My ingredients get a legal status. The whole point",
  "ec.europa.eu/growth/tools-databases/cosing"),

 ("CosIng-KG", "CosIng already turned into RDF", "-",
  "-",
  "check", "If it works I reuse it and save weeks", "github.com/biobricks-ai/cosing-kg"),

 ("DermO", "3,000 skin disease terms by dermatologists", "DermO 2016",
  "Built with OBO tooling and Protege, published on BioPortal",
  "yes", "Fixes my medical claims in six lines", "bioportal.bioontology.org"),

 ("TXPO", "Toxic process ontology, from OBO", "TOXIN KG",
  "Used as the backbone of their graph",
  "no", "Too deep into toxicology mechanisms", "obofoundry.org"),

 ("Wikidata", "Wikipedia facts, queryable", "-",
  "-",
  "yes", "Gives me brand ownership, one line per brand", "wikidata.org"),

 ("DBpedia", "Older Wikipedia graph", "Abesova, Di Noia",
  "Abesova pulled countries and map coordinates live",
  "maybe", "Wikidata is better maintained", "dbpedia.org"),

 ("LOV", "Search engine for existing vocabularies", "-",
  "-",
  "yes", "Search before inventing a term. Amateur test", "lov.linkeddata.es"),

 ("H", "7. Checking and publishing"),

 ("OOPS!", "Free website that finds ontology errors", "-",
  "-",
  "yes", "One afternoon buys a real evaluation section", "oops.linkeddata.es"),

 ("FOOPS!", "Scores how findable and reusable it is", "-",
  "-",
  "yes", "I criticise everyone for not publishing", "w3id.org/foops"),

 ("OntoMetrics", "Depth, breadth, structural numbers", "-",
  "-",
  "yes", "Comparable figures for the evaluation table", "ontometrics.uni-rostock.de"),

 ("WIDOCO", "Makes a docs page from the ontology", "-",
  "-",
  "yes", "The docs cannot drift from the file", "github.com/dgarijo/Widoco"),

 ("w3id.org", "A permanent web address", "OntoCosmetic",
  "purl.org address that still works today",
  "yes", "A university URL dies when I graduate", "w3id.org"),

 ("Zenodo", "Gives each release a DOI", "-",
  "-",
  "yes", "1 in 6 competitors publishes. I will", "zenodo.org"),

 ("H", "8. Methods"),

 ("METHONTOLOGY", "Older, document-heavy method", "bit-Tech, Utari",
  "Both named it as their method",
  "no", "Thorough but old. I take its glossary step", "search: Fernandez-Lopez 1997"),

 ("Middle-out", "Start in the middle, grow both ways", "Abesova",
  "Started from a base ontology, let the CSV widen it",
  "maybe", "Honest, but it is what you do by accident", "-"),

 ("MOMo", "Modular ontology modeling", "-",
  "-",
  "yes", "My four modules follow it", "search: Shimizu MOMo"),

 ("LOT", "Linked Open Terms. Four steps", "-",
  "-",
  "yes", "Built around reuse and publishing", "lot.linkeddata.es"),

 ("Noy & McGuinness 101", "The classic seven-step guide", "-",
  "-",
  "cite", "Everyone cites it. Too light to be my method",
  "protege.stanford.edu/publications"),

 ("Competency questions", "Questions the ontology must answer", "COPPER",
  "Used them as one of three evaluation layers",
  "yes", "Turns 'is it good' into something testable", "-"),

 ("OBO principles", "Rules for building shared ontologies", "COPPER, DermO",
  "COPPER checked its process against them",
  "maybe", "Good practice to cite even if I do not join", "obofoundry.org"),

 ("H", "9. Used by the papers, not by me"),

 ("CCBR", "Conversational case-based reasoning", "Moe & Aung",
  "Six questions turn a vague complaint into a query",
  "no", "Needs a hand-built case base", "-"),

 ("Ford-Fulkerson", "A max-flow algorithm", "Moe & Aung",
  "Scored products by how much need they satisfy",
  "no", "A weighted filter does the same for me", "-"),

 ("CNN", "Neural net that reads images", "Hansanie, Lee (lululab)",
  "Graded acne from a face photo",
  "no", "No photos, no ethics approval", "-"),

 ("Graph attention network", "Neural net over a graph", "HaCKG",
  "Predicted halal status from the graph",
  "no", "Future work. Needs interaction data", "-"),

 ("AHP", "Weigh criteria by comparing in pairs", "OntoCosmetic",
  "Ranked ingredients on several properties at once",
  "maybe", "Could rank on price and availability", "search: Saaty AHP"),

 ("AttrakDiff", "User experience questionnaire", "OntoCosmetic",
  "Ran it between design iterations",
  "maybe", "Only if I build an interface", "attrakdiff.de"),

 ("SUS and MAE", "Usability score, and rating error", "Mahadewi",
  "The two numbers they report",
  "no", "FEVR says match evaluation to the goal", "-"),

 ("Slope One", "Simple collaborative filtering", "Mahadewi",
  "Predicted ratings from item differences",
  "no", "Needs a ratings matrix I do not have", "-"),

 ("Precision / recall / F", "Standard accuracy measures", "Moe & Aung, Hansanie, E-Prod",
  "Reported as the whole evaluation",
  "no", "Wrong measure for a knowledge graph", "-"),

 ("Sequential pattern mining", "Finds common orderings", "Tarus",
  "Learned the order people consume things in",
  "no", "My routine_step does this by rule", "-"),

 ("SMILES", "Text form of a molecule's structure", "TOXIN KG",
  "Every chemical gets a structure string",
  "no", "I have CAS numbers from CosIng", "-"),

 ("GraphRAG", "Ontology-grounded graph feeding an LLM", "Ali 2026",
  "The graph stops the model inventing answers",
  "no", "My future work chapter", "-"),

 ("Tkinter", "Python desktop windows", "Hansanie & Silva",
  "Built their desktop app with it",
  "no", "I am not building a desktop app", "-"),
]
