# -*- coding: utf-8 -*-
"""
Extra rows appended to the existing Tools tab.

Two new sections:
  1. Editors that are NOT Protege, because my supervisor asked which papers
     used something else and what the alternatives are
  2. Reasoning and rules, with the SHACL family spelled out

Same 6 columns as the tab already has:
  Tool | What it is, in one line | What it does | Link | Do we use it? | Why, or why not
"""

EXTRA = [

 ("H", "Editors instead of Protege. My supervisor asked. Five of my 28 papers used no Protege at all."),

 ("WebProtege",
  "Protege in a browser, multi-user",
  "Same model as Protege but two people can edit at once, with change history and comments. "
  "Handles thousands of classes.",
  "webprotege.stanford.edu",
  "MAYBE",
  "Useful if my supervisor wants to comment directly on the ontology instead of by email. "
  "Weaker than desktop Protege for reasoning."),

 ("OntoRefine",
  "Point-and-click CSV to RDF, inside GraphDB",
  "You see your spreadsheet, you draw which column becomes a subject and which becomes a "
  "predicate, it writes the RDF.",
  "graphdb.ontotext.com",
  "NO",
  "Abesova used this instead of Protege. It works, but the mapping is trapped inside GraphDB. "
  "I cannot put it in an appendix or re-run it from a script. Morph-KGC does the same job as "
  "a file I can publish."),

 ("TopBraid Composer / EDG",
  "The commercial editor, from the people who wrote SHACL",
  "Full OWL editing plus the best SHACL support anywhere. EDG adds governance and workflows.",
  "topquadrant.com",
  "NO",
  "The reference implementation for SHACL, so worth knowing it exists. But commercial, and I "
  "do not need governance workflows for a one-person thesis."),

 ("VocBench 3",
  "Web platform for vocabularies and thesauri",
  "Strong on SKOS, multilingual labels, and editorial workflow. Almost full OWL 2 coverage.",
  "vocbench.uniroma2.it",
  "NO",
  "Built for thesauri, not for defined classes. My benefits list is SKOS so it would suit that "
  "one part, but not the rest."),

 ("ROBOT",
  "A command-line tool for ontology jobs, from the OBO world",
  "Convert formats, run a reasoner, extract a module, run quality reports. All from a script, "
  "no clicking.",
  "github.com/ontodev/robot",
  "MAYBE",
  "This is how the serious biomedical ontologies are actually built. If I want my build to be "
  "repeatable rather than 'I clicked some things in Protege', this is the answer. Paper: "
  "Jackson et al., BMC Bioinformatics 2019."),

 ("LinkML",
  "Write the model in YAML, generate everything else",
  "One YAML schema generates OWL, SHACL, JSON Schema, Python classes and docs together.",
  "linkml.io",
  "MAYBE",
  "Tempting, because it would give me OWL and SHACL from one source with no chance of them "
  "drifting apart. But it is another thing to learn and my ontology is small."),

 ("Chowlk",
  "Turn a diagram into OWL",
  "You draw the ontology in diagrams.net using their notation, it outputs the OWL file.",
  "chowlk.linkeddata.es",
  "MAYBE",
  "My chapter needs diagrams anyway. Drawing once and getting both the picture and the file is "
  "attractive. Same idea as CoModIDE."),

 ("OWLGrEd",
  "Draws an existing ontology as a UML-style picture",
  "Point it at the OWL file, get a compact diagram of the whole thing.",
  "owlgred.lumii.lv",
  "MAYBE",
  "Only for producing the figure in the chapter. Not for building."),

 ("Fluent Editor",
  "Write the ontology in near-English sentences",
  "'Every SensitiveSafeProduct is a Product that has-no restricted-ingredient.' It compiles to OWL.",
  "cognitum.eu",
  "NO",
  "Nice for explaining to a non-technical supervisor. Windows only, and small community."),

 ("Apache Jena Fuseki",
  "Free triple store with a SPARQL endpoint",
  "Store the graph, query it over HTTP. No editor, just the server.",
  "jena.apache.org/documentation/fuseki2",
  "NO",
  "bit-Tech 2025 used this instead of Protege, with no editor at all. Its reasoning is weaker "
  "than GraphDB, but its SHACL engine is the fastest."),

 ("R2RML / RML mapping files",
  "The ontology is defined by the mapping, not by an editor",
  "You never open an editor. The mapping file decides the shape of the graph.",
  "rml.io",
  "YES",
  "TOXIN KG 2025 worked this way. It is also how my pipeline works, so I should say so plainly: "
  "my ontology is built by a script, not by clicking."),

 ("H", "Reasoning and rules. Five ways to reason. See the Reasoning + SHACL tab."),

 ("RDFS entailment",
  "The cheapest reasoning. Subclass and domain/range only",
  "If Cleanser is a subclass of Product, every cleanser becomes a product automatically.",
  "w3.org/TR/rdf-mt",
  "YES",
  "Free and always on in GraphDB. Does the hierarchy and nothing else."),

 ("OWL 2 profiles (RL, EL, QL, DL)",
  "Four cut-down versions of OWL that trade power for speed",
  "RL runs as rules and scales. EL is for huge simple hierarchies. DL is full power but slow.",
  "w3.org/TR/owl2-profiles",
  "YES",
  "I should say in the chapter which profile I am in. My defined classes need DL. Saying "
  "'OWL 2 DL' is a one-line answer to a very likely viva question."),

 ("SHACL Core",
  "Checks the data obeys rules, and names what broke",
  "'Every product must have exactly one price.' It reports the exact product that has two.",
  "w3.org/TR/shacl",
  "YES",
  "OWL cannot do this. OWL would decide the two prices are the same thing rather than "
  "complain. Not one of my 28 papers uses SHACL."),

 ("SHACL-AF  sh:TripleRule",
  "A rule in the graph that adds a new triple",
  "If a product has three or more barrier lipids, it is a BarrierRepairProduct.",
  "w3.org/TR/shacl-af",
  "YES",
  "Same result as a defined class but easier to read, and it can infer any triple. OWL can "
  "only ever infer types and sameAs."),

 ("SHACL-AF  sh:SPARQLRule",
  "A rule that runs a SPARQL CONSTRUCT and writes the answer back",
  "Count how many EU-restricted ingredients a product has, store the number.",
  "w3.org/TR/shacl-af",
  "YES",
  "OWL cannot count. This is the cleanest honest reason to bring SHACL in alongside it."),

 ("SHACL-SPARQL constraints",
  "When the built-in checks are not enough, drop into SPARQL",
  "'Every ingredient with an annex status must have an authority and a date.' My provenance "
  "rule, enforced by the machine.",
  "w3.org/TR/shacl",
  "YES",
  "This is what turns my evidence-level design from a promise into something checkable."),

 ("pySHACL",
  "SHACL validator in Python",
  "pip install pyshacl, then one command validates data against shapes.",
  "github.com/RDFLib/pySHACL",
  "YES",
  "My pipeline is Python and it pairs with RDFLib. Slowest of the three engines but my graph "
  "is 1.8 million triples, which is nothing."),

 ("Apache Jena SHACL",
  "SHACL validator in Java, the fast one",
  "Command line or library. Also reads SHACL-C, a compact syntax that is much easier to read "
  "than Turtle.",
  "jena.apache.org/documentation/shacl",
  "MAYBE",
  "Benchmarked around four times faster than pySHACL. Only matters if pySHACL gets slow."),

 ("TopBraid SHACL API",
  "The reference implementation",
  "Java, on top of Jena. Defines what correct behaviour is when engines disagree.",
  "github.com/TopQuadrant/shacl",
  "MAYBE",
  "Worth checking against if a validation result looks wrong."),

 ("SPIN",
  "The thing SHACL grew out of",
  "SPARQL rules attached to classes. A TopQuadrant submission from 2011.",
  "spinrdf.org",
  "NO",
  "Superseded by SHACL in 2017. Only useful to know because older papers mention it."),
]
