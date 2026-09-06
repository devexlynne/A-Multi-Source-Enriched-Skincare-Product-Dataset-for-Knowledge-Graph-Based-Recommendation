# Semantic web, from zero

Everything in the literature review uses these words. This file defines all of
them before you meet them, in the order that they build on each other. Read it
once, then keep it open while reading the review.

Every term has a link so you can go deeper when a supervisor pushes.

---

## Part 1: the four ideas everything else rests on

### 1.1 The triple

A triple is a sentence with exactly three parts: **subject, predicate,
object**.

```
Cetaphil Lotion     contains        Phenoxyethanol
     subject         predicate          object
```

That is the whole data model. A million triples make a graph. There are no
tables, no columns, no rows. If you want to say a new kind of thing, you add a
triple. You never alter a schema.

Compare with your CSV. Your CSV has 42 fixed columns, and a product that needs
a 43rd fact has nowhere to put it. A graph has no columns, so it never has that
problem.

Read: [RDF 1.1 Primer, W3C](https://www.w3.org/TR/rdf11-primer/)

### 1.2 The IRI

An IRI is a name that is globally unique because it looks like a web address.
Instead of calling something `phenoxyethanol`, you call it
`http://myontology.org/ingredient/Phenoxyethanol`.

Why bother: two people can now say things about the same ingredient without
having agreed in advance, because they both used the same name. That is the
entire mechanism by which separate datasets join up.

You will also see **URI** and **URL**. For your purposes they are the same
idea. IRI is the modern version that allows non-Latin characters, which matters
to you because you have Arabic product names.

Read: [What is an IRI, W3C RDF concepts](https://www.w3.org/TR/rdf11-concepts/#section-IRIs)

### 1.3 RDF and its file formats

**RDF**, Resource Description Framework, is the standard that says data is made
of triples. It is a data model, not a file format.

RDF can be written in several formats. You will meet these:

| Format | Extension | What it looks like | Use it for |
|---|---|---|---|
| **Turtle** | `.ttl` | readable, indented, short | writing by hand, and your thesis |
| RDF/XML | `.rdf`, `.owl` | XML, verbose, painful | old tools, some downloads |
| JSON-LD | `.jsonld` | JSON with a context block | web APIs, Google reads this |
| N-Triples | `.nt` | one triple per line, no shortcuts | bulk loading, diffing |

Turtle is what your `skincare-profile.ttl` is written in. It is the one to
learn.

Read: [Turtle, W3C](https://www.w3.org/TR/turtle/) and
[JSON-LD](https://json-ld.org/)

### 1.4 Ontology versus knowledge graph

This distinction confuses everyone, including published authors, so learn it
properly and you will sound informed.

| | Ontology | Knowledge graph |
|---|---|---|
| Holds | the **rules and vocabulary**: what kinds of thing exist, what can relate to what | the **facts**: actual products, actual ingredients |
| Analogy | the empty form | the filled-in forms |
| Your case | `skincare-profile.ttl` says a Product can have Ingredients | the 12,629 rows once converted to triples |
| Size | small, tens or hundreds of classes | large, millions of triples |

A knowledge graph usually has an ontology inside it. The ontology is the part
that makes the graph mean something rather than just being a pile of edges.

**The sentence for your defence:** an ontology is the schema, a knowledge graph
is the schema plus the instances.

Read: [Knowledge Graphs, Hogan et al., ACM Computing Surveys 2021](https://arxiv.org/abs/2003.02320)

---

## Part 2: the languages

### 2.1 RDFS

**RDF Schema** adds the first bit of meaning on top of raw triples. It gives
you four things:

| Term | Means |
|---|---|
| `rdfs:Class` | this is a kind of thing |
| `rdfs:subClassOf` | every Serum is a Product |
| `rdfs:domain` | whatever has `hasIngredient` must be a Product |
| `rdfs:range` | whatever `hasIngredient` points to must be an Ingredient |

That is nearly all of RDFS. It is small and it is enough for simple work.

Read: [RDF Schema, W3C](https://www.w3.org/TR/rdf-schema/)

### 2.2 OWL

**OWL**, the Web Ontology Language, is RDFS plus real logic. This is where
ontologies become able to conclude things.

The parts you will use:

| Construct | Says | Your example |
|---|---|---|
| `owl:Class` | a kind of thing | `Product`, `Ingredient` |
| `owl:ObjectProperty` | a link between two things | `hasIngredient` |
| `owl:DatatypeProperty` | a link from a thing to a value | `priceUSD` |
| `owl:Restriction` | a condition on a property | must have at least one Offer |
| `owl:equivalentClass` | two descriptions mean the same set | the defined class trick |
| `owl:disjointWith` | nothing can be both | a Product is not an Ingredient |
| `owl:inverseOf` | the reverse link | `soldBy` and `sells` |
| `owl:TransitiveProperty` | if a to b and b to c then a to c | `partOf` |
| `owl:FunctionalProperty` | at most one value | a product has one manufacturer |
| `owl:sameAs` | these two IRIs are the same thing | linking your product to a Wikidata entry |

OWL comes in profiles, which are subsets with different speed and power
tradeoffs. **OWL 2 EL** is fast and used by big biomedical ontologies. **OWL 2
DL** is the expressive one most projects use. You will use DL.

Read: [OWL 2 Primer, W3C](https://www.w3.org/TR/owl2-primer/)

### 2.3 The defined class, which is the single most important idea for you

Normally you put things in a class by hand. A **defined class** describes a
condition, and the software works out the membership for you.

```turtle
skc:SensitiveSafeProduct
    owl:equivalentClass [
        a owl:Class ;
        owl:intersectionOf (
            skc:Product
            [ a owl:Restriction ;
              owl:onProperty skc:hasIngredient ;
              owl:allValuesFrom [ owl:complementOf skc:DeclarableAllergen ] ] ) ] .
```

In words: a SensitiveSafeProduct is any Product all of whose ingredients are
not declarable allergens.

You never list which products those are. You state the rule once, and when a
formula is corrected the membership corrects itself. **This is the answer to
"why not just use the spreadsheet".** A spreadsheet can filter. It cannot hold
a definition.

### 2.4 SPARQL

**SPARQL** is the query language for RDF. It is SQL for graphs. You write a
pattern with question marks for the unknowns, and it returns everything that
matches.

```sparql
SELECT ?product ?price WHERE {
  ?product a skc:Product ;
           skc:hasIngredient skc:Niacinamide ;
           schema:offers [ schema:price ?price ;
                           schema:seller ?shop ] .
  ?shop skc:inCountry skc:Lebanon .
  FILTER (?price < 20)
}
ORDER BY ?price
```

That reads: find every product containing niacinamide, offered by a shop in
Lebanon, under twenty dollars, cheapest first.

Note what happened. You did not write a join. The pattern is the join.

Read: [SPARQL 1.1 Query, W3C](https://www.w3.org/TR/sparql11-query/) and the
gentle [Learning SPARQL book site](https://www.learningsparql.com/)

### 2.5 SHACL

**SHACL**, Shapes Constraint Language, validates a graph. OWL says what can be
inferred. SHACL says what must be true or the data is wrong.

You need this because RDF has no schema enforcement by default. Anyone can
assert anything. SHACL is how you write "every Product must have exactly one
brand and at least one offer, or flag it".

This is the RDF version of your `validate_dataset.py`, and saying that in your
defence shows you understand both.

Read: [SHACL, W3C Recommendation 2017](https://www.w3.org/TR/shacl/) and
[a plain introduction](https://graphwise.ai/fundamentals/what-is-shacl/)

### 2.6 SWRL

**SWRL**, Semantic Web Rule Language, writes if-then rules that OWL cannot
express. OntoCosmetic uses it for formulation heuristics.

```
Product(?p) ^ hasIngredient(?p, ?i) ^ DeclarableAllergen(?i)
    -> notRecommendedFor(?p, SensitiveSkin)
```

Use SWRL only when OWL genuinely cannot say the thing, because rules make
reasoning slower and some reasoners ignore them.

Read: [SWRL submission, W3C](https://www.w3.org/submissions/SWRL/)

---

## Part 3: the machinery

### 3.1 The reasoner

A **reasoner** is a program that reads your ontology and works out what follows
from it. Two jobs:

| Job | What it does | Why you care |
|---|---|---|
| **Classification** | works out which class everything belongs to, including defined classes | this is what makes defined classes actually do something |
| **Consistency checking** | finds contradictions | tells you when your data says something impossible |

The second one matters to you specifically. Your whole dataset story has been
about faults that produced plausible output instead of errors. A reasoner
complains loudly. That is the tool you have been missing.

| Reasoner | Notes | Link |
|---|---|---|
| **HermiT** | ships with Protégé, good default | [hermit-reasoner.com](http://www.hermit-reasoner.com/) |
| **Pellet / Openllet** | supports SWRL rules, used by Hansanie and Silva | [Openllet on GitHub](https://github.com/Galigator/openllet) |
| **ELK** | very fast, but only the EL profile | [ELK](https://github.com/liveontologies/elk-reasoner) |
| **FaCT++** | older, still around | [FaCT++](https://github.com/ethz-asl/factplusplus) |

### 3.2 The triple store

A **triple store** is a database for triples, with a SPARQL endpoint on the
front. An **endpoint** is just a URL you send SPARQL queries to.

| Store | Good for | Note |
|---|---|---|
| **Apache Jena Fuseki** | free, simple, runs on your laptop | [jena.apache.org/documentation/fuseki2](https://jena.apache.org/documentation/fuseki2/) |
| **GraphDB (Ontotext)** | free desktop edition, built in reasoning, includes OntoRefine | [graphdb.ontotext.com](https://graphdb.ontotext.com/) |
| **Stardog** | strong reasoning, commercial | [stardog.com](https://www.stardog.com/) |
| **Virtuoso** | runs DBpedia itself | [virtuoso.openlinksw.com](https://virtuoso.openlinksw.com/) |
| **Neo4j with neosemantics** | if you already know Neo4j | [neo4j.com/labs/neosemantics](https://neo4j.com/labs/neosemantics/) |

For a thesis: **GraphDB Free** or **Fuseki**. GraphDB if you want OntoRefine in
the same tool, which you probably do.

### 3.3 The editor and the libraries

| Tool | What it is | Link |
|---|---|---|
| **Protégé** | the desktop ontology editor, Stanford, free | [protege.stanford.edu](https://protege.stanford.edu/) |
| **WebProtégé** | the browser version, good for showing supervisors | [webprotege.stanford.edu](https://webprotege.stanford.edu/) |
| **Owlready2** | Python library, load an ontology, add individuals, run a reasoner | [owlready2 docs](https://owlready2.readthedocs.io/) |
| **RDFLib** | Python library for plain RDF and SPARQL | [rdflib.readthedocs.io](https://rdflib.readthedocs.io/) |
| **OWL API** | the Java library everything else is built on | [owlcs.github.io/owlapi](https://owlcs.github.io/owlapi/) |

Your pipeline is Python, so **Owlready2 plus RDFLib** is your combination.

### 3.4 Named graphs

A **named graph** is a labelled box inside a triple store holding a set of
triples. Instead of one giant pile, you have `graph:skinsort`,
`graph:lebanese-retail`, `graph:cosing`, `graph:inferred`.

Why this matters enormously to you: you can then say *which graph a fact came
from*, drop and reload one source without touching the others, and run a query
against only the sources you trust. The TOXIN knowledge graph uses exactly this
for traceability.

This is your evidence-level idea, implemented at the storage layer.

Read: [RDF Datasets and named graphs](https://www.w3.org/TR/rdf11-concepts/#section-dataset)

---

## Part 4: reusing other people's vocabulary

### 4.1 Why reuse at all

If you invent `skc:productName`, only your software understands it. If you use
`schema:name`, every tool already does. The rule is: **reuse for anything
general, invent only where your contribution is.**

### 4.2 The four you are reusing

| Vocabulary | Gives you | Address |
|---|---|---|
| **schema.org** | `Product`, `Offer`, `price`, `brand`, `seller`, `image` | [schema.org](https://schema.org/) |
| **PROV-O** | `wasAttributedTo`, `wasDerivedFrom`, `generatedAtTime` | [W3C PROV-O](https://www.w3.org/TR/prov-o/) |
| **SKOS** | `prefLabel`, `altLabel`, `broader`, `narrower`, `Concept` | [W3C SKOS](https://www.w3.org/TR/skos-reference/) |
| **Dublin Core** | `title`, `creator`, `license`, `modified` | [DCMI Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/) |

The one-line justification for each:

- **schema.org** splits the product from the offer, which is why one Cetaphil
  lotion can carry two Beirut prices at once.
- **PROV-O** is your evidence levels, in a language other people already speak.
- **SKOS** handles your controlled vocabularies, where "Hydrating" and
  "Hydration" are one concept with two labels.
- **Dublin Core** is the bookkeeping that makes the dataset citable.

Others worth knowing: **GoodRelations** for richer commerce (now largely folded
into schema.org), **FOAF** for people, **OWL-Time** for temporal facts, and the
**OBO Foundry** for biomedical ontologies.

### 4.3 Linking out

**DBpedia** is Wikipedia turned into a knowledge graph. **Wikidata** is the
same idea, hand-curated, and generally better maintained now.

You link to them with `owl:sameAs` or `rdfs:seeAlso`. The payoff is real: the
VU Amsterdam group pulled country data and capital city coordinates out of
DBpedia and got a map for free, without typing any of it.

For you: linking brands to Wikidata gives you parent company, founding year and
country without collecting any of it. L'Oréal owns more of your brand list than
you would guess, and Wikidata already knows which.

Read: [DBpedia](https://www.dbpedia.org/) and [Wikidata](https://www.wikidata.org/)

---

## Part 5: getting your CSV into the graph

This is the step nobody explains and everybody needs. It is called
**population** or **materialisation** or **lifting**.

Four ways, worst to best for a thesis:

| Way | What it means | Verdict |
|---|---|---|
| By hand in Protégé | typing individuals | fine for ten, impossible for 12,629 |
| A Python script | loop the CSV, write triples with RDFLib or Owlready2 | works, but the mapping is buried in code |
| **A mapping file** | a declarative file saying column to property | **this is the right answer** |
| An LLM | ask a model to produce triples | promising, not yet defensible alone |

### The mapping languages

| Language | What it is | Link |
|---|---|---|
| **R2RML** | W3C standard, relational database to RDF | [W3C R2RML](https://www.w3.org/TR/r2rml/) |
| **RML** | R2RML extended to CSV, JSON, XML | [rml.io](https://rml.io/specs/rml/) |
| **YARRRML** | RML written in YAML so a human can read it | [rml.io/yarrrml](https://rml.io/yarrrml/) |

### The engines that run them

| Tool | Notes | Link |
|---|---|---|
| **Morph-KGC** | Python, built on pandas, handles large CSVs, supports RML and YARRRML | [morph-kgc.readthedocs.io](https://morph-kgc.readthedocs.io/) |
| **RMLMapper** | the Java reference implementation | [RMLMapper](https://github.com/RMLio/rmlmapper-java) |
| **OntoRefine** | inside GraphDB, point and click, based on OpenRefine | [OntoRefine docs](https://graphdb.ontotext.com/documentation/) |
| **Karma** | interactive, learns the mapping from examples | [usc-isi-i2.github.io/karma](https://usc-isi-i2.github.io/karma/) |
| **Tarql** | SPARQL over a CSV, quick and dirty | [tarql.github.io](https://tarql.github.io/) |

**My recommendation for you: Morph-KGC with a YARRRML mapping.** It is Python,
which matches your pipeline. The mapping is a file you can put in the thesis
appendix and in the repository. When the dataset changes you rerun one command
and the graph is rebuilt. That is a repeatable, citable method rather than a
script nobody can audit.

A directory of everything in this space:
[awesome-kgc-tools](https://kg-construct.github.io/awesome-kgc-tools/)

---

## Part 6: checking your ontology is any good

| Tool | Checks | Link |
|---|---|---|
| **OOPS!** | 41 known ontology design pitfalls, graded critical, important, minor | [oops.linkeddata.es](https://oops.linkeddata.es/) |
| **FOOPS!** | 24 checks for whether your ontology is FAIR | [w3id.org/foops](https://w3id.org/foops/) |
| **OntoMetrics** | structural metrics, depth, breadth, richness | [ontometrics.informatik.uni-rostock.de](https://ontometrics.informatik.uni-rostock.de/) |
| **SHACL** | your own data constraints | [W3C](https://www.w3.org/TR/shacl/) |
| **WIDOCO** | generates human readable documentation from your ontology | [WIDOCO](https://github.com/dgarijo/Widoco) |

Running OOPS! and FOOPS! and reporting the results is a cheap, concrete
evaluation section that almost none of the papers in your review have. Take it.

### Competency questions

A **competency question** is a question your ontology must be able to answer.
You write them before you build, and you test against them after. They are how
you turn "is my ontology good" into something measurable.

Yours would include:

1. Which products under twenty dollars, sold in Lebanon, suit oily skin and
   contain no declarable allergen?
2. Which products claiming sensitive skin suitability contain one of the EU 26?
3. For a given product, which shop is cheapest, and when was that price seen?
4. Which Lebanese origin products contain an ingredient restricted under
   Annex III?
5. Which claims about this product come from the manufacturer rather than a
   retailer?

Write these in the thesis. Then show the SPARQL that answers each. That is a
complete evaluation chapter in itself.

---

## Part 7: the words in the neural half of the literature

You need these to read tracks D and E without drowning.

| Term | Plain meaning |
|---|---|
| **Embedding** | turning a thing into a list of numbers so that similar things get similar numbers |
| **TransE and friends** | early methods that embed a triple so that subject plus predicate is close to object |
| **RDF2Vec** | walks around the graph, treats each walk as a sentence, applies word2vec. [Paper](https://link.springer.com/chapter/10.1007/978-3-319-46523-4_30) |
| **OWL2Vec\*** | RDF2Vec but keeps the OWL logic too. [Machine Learning journal 2021](https://link.springer.com/article/10.1007/s10994-021-05997-6) |
| **Collaborative filtering** | recommend what similar users liked. Needs user history, which you do not have |
| **Content-based filtering** | recommend things similar to what you liked. Needs item features, which you have a lot of |
| **Matrix factorisation** | the classic collaborative filtering maths |
| **NCF** | Neural Collaborative Filtering, the same idea with a neural network |
| **GNN, graph neural network** | a network that learns by passing messages between connected nodes |
| **Cold start** | you cannot recommend to a new user with no history. Ontologies help here, which is one of your arguments |
| **PyKEEN** | Python library for knowledge graph embeddings. [pykeen.readthedocs.io](https://pykeen.readthedocs.io/) |

---

## Part 8: the ten links worth bookmarking

1. [W3C RDF 1.1 Primer](https://www.w3.org/TR/rdf11-primer/)
2. [W3C OWL 2 Primer](https://www.w3.org/TR/owl2-primer/)
3. [W3C SPARQL 1.1](https://www.w3.org/TR/sparql11-query/)
4. [Protégé](https://protege.stanford.edu/)
5. [Ontology Development 101, Noy and McGuinness](https://protege.stanford.edu/publications/ontology_development/ontology101.pdf)
6. [LOT methodology](https://lot.linkeddata.es/)
7. [Morph-KGC](https://morph-kgc.readthedocs.io/)
8. [OOPS!](https://oops.linkeddata.es/)
9. [Linked Open Vocabularies, search for an existing term before inventing one](https://lov.linkeddata.es/dataset/lov/)
10. [awesome-kgc-tools](https://kg-construct.github.io/awesome-kgc-tools/)

Number 9 is the one to use constantly. Before you invent a property, search LOV
for it. If somebody already defined it, use theirs and cite them. That single
habit is what separates an ontology that looks amateur from one that looks
professional.
