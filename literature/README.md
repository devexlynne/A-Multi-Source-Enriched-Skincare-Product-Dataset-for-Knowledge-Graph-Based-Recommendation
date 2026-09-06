# Literature

Everything behind the ontology phase of this thesis. 59 papers, read and
recorded, plus the design and the build plan that came out of them.

This folder exists so that one person can open one place and see the whole
field, rather than reading 59 PDFs to find out that most of them do not solve
the problem.

---

## Start here

| If you want | Open |
|---|---|
| The papers as a browsable table | [`papers.csv`](papers.csv) — GitHub renders this as a sortable table |
| The same thing with every column | [`papers_full.csv`](papers_full.csv), 38 columns |
| The formatted version for reading offline | [`PAPERS_TABLE.xlsx`](PAPERS_TABLE.xlsx), seven sheets |
| To know what any of the words mean | [`01_semantic_web_primer.md`](01_semantic_web_primer.md) |
| The argument in one page | [The gap](#the-gap), below |
| What I am actually going to build | [`06_ontology_master_plan.md`](06_ontology_master_plan.md) |

---

## What is in this folder

### The documents

| File | What it is | Length |
|---|---|---|
| [`01_semantic_web_primer.md`](01_semantic_web_primer.md) | Every technical term defined in plain language before it is used. Triples, IRIs, OWL, reasoners, SPARQL, SHACL, embeddings. Written for somebody who has never studied the semantic web | 2,900 words |
| [`02_skincare_ontologies.md`](02_skincare_ontologies.md) | The direct competitors. Ten entries, each with methodology, technique, results, and what I take from it | 6,100 words |
| [`03_recommenders_and_deep_learning.md`](03_recommenders_and_deep_learning.md) | Ontology and knowledge graph recommenders in other domains, deep learning, and hybrid work | 3,900 words |
| [`04_papers_round_two.md`](04_papers_round_two.md) | Nine papers a second, academic-index search round found, plus two corrections to the first round | 2,900 words |
| [`05_tools_and_methods.md`](05_tools_and_methods.md) | Methodologies compared, tools chosen, and why each one | 2,100 words |
| [`06_ontology_master_plan.md`](06_ontology_master_plan.md) | The full build plan. Every class, every property, the population pipeline, the evaluation design, six sprints | 4,900 words |
| [`07_research_prompt.md`](07_research_prompt.md) | The extraction template used for every paper. Reusable when the review grows | 1,500 words |

### The data

| File | What it is |
|---|---|
| [`papers.csv`](papers.csv) | 59 papers, 14 columns. The readable version |
| [`papers_full.csv`](papers_full.csv) | 59 papers, 38 columns. Everything |
| [`comparison_skincare_ontologies.csv`](comparison_skincare_ontologies.csv) | The direct competitors compared on 15 features, side by side |
| [`ontology_design.csv`](ontology_design.csv) | Every class and property planned, with its source and which dataset column it holds |
| [`tools.csv`](tools.csv) | 17 tools, why each was chosen, what was rejected |
| [`roadmap.csv`](roadmap.csv) | Six sprints, with the risk of skipping each |
| [`gap_analysis.csv`](gap_analysis.csv) | Six gaps, what I do about each, and how defensible the claim is |
| [`PAPERS_TABLE.xlsx`](PAPERS_TABLE.xlsx) | All of the above, formatted, seven sheets |
| [`build_papers_table.py`](build_papers_table.py) | Rebuilds the spreadsheet. The data lives in this script, so the spreadsheet is reproducible rather than hand-edited |

### For the thesis

| File | What it is |
|---|---|
| [`latex/related_work.tex`](latex/related_work.tex) | The related work chapter, ready to `\input`. Compiles clean, 17 pages, zero undefined citations |
| [`latex/related_work.bib`](latex/related_work.bib) | The matching bibliography |

### The PDFs

Five papers are stored in [`../papers/`](../papers/). The rest are linked from
`papers.csv`. Licences differ, so check before redistributing any of them.

---

## How the review is organised

Five tracks. The chapter narrows through them, and each one ends by naming what
is missing, which is what the next one addresses.

| Track | Count | What it covers | Why it is here |
|---|---|---|---|
| **B** | 18 | Ontologies for skincare, cosmetics, cosmetic regulation and dermatology | The direct competitors. The gap lives here |
| **C** | 16 | Ontology and knowledge graph recommenders in other domains | Where the mechanisms come from. Food, e-commerce, academic papers, movies |
| **D** | 3 | Deep learning recommenders and skin analysis | The alternative to position against, honestly |
| **E** | 9 | Hybrid work combining graphs with neural methods | Where the field is going. Future work, not this thesis |
| **F** | 13 | Methodology and tooling | How to actually build the thing |

---

## The gap

Six things are missing across the whole literature. Each one is something this
dataset already contains.

| Missing | How I know | What this thesis does | Strength |
|---|---|---|---|
| **An ingredient layer with legal standing** | Every skincare ontology stores ingredients as free text or a small hand-made list. The one knowledge graph that links cosmetic ingredients to EU law (TOXIN, *Database*, Oxford, 2025) contains no products at all | Ingredients are individuals identified by their CosIng register entry, so regulatory status is inherited from the European Commission rather than asserted by me. 99.2% of products with a formula are linked | **Strongest** |
| **A record of where each claim came from** | No reviewed skincare ontology says who asserted a claim or how much that source is worth. Every claim is presented as equally true | Every suitability claim is a `Claim` entity carrying its source, the sentence it was read from, the date, and one of four evidence levels. Specialised from PROV-O, a W3C standard | **Strong** |
| **Whether the product can be bought** | Every reviewed system recommends without asking whether the item is obtainable. In Lebanon that assumption fails, and it fails differently for imported and locally made products | Price in two currencies, per shop, with the date observed. Availability as a defined class. 11,937 products with at least one Lebanese shop | **Strong and unique** |
| **A published artefact** | One of six reviewed skincare ontologies is publicly resolvable. The field cannot build on its own results | w3id address, WIDOCO documentation, Zenodo DOI, named methodology, and a measured FAIR score | **Easy and rare** |
| **Any evaluation at all** | Rahayu et al. (2022), reviewing 28 ontology-based recommenders, found that **none** described an evaluation methodology. In this set: two report satisfaction on under 30 people, one is a case study, one admits expert testing never happened | Four layers: structural (OOPS!, FOOPS!, OntoMetrics), functional (15 competency questions as SPARQL), logical (predicted versus inferred membership of six defined classes), comparative | **Strong, and cheap** |
| **What the user actually needs** | Concerns are modelled everywhere as an attribute of a product. AliCoCo (SIGMOD 2020) argues that leaves a semantic gap, because shoppers think in needs, not categories | Lebanese consumer needs as first-class entities: a routine under twenty dollars a month, one that survives a power cut, one buyable in a single pharmacy | **Most original, least certain** |

### In one sentence

No system anywhere combines an ingredient layer with legal standing, a record
of where each claim came from, and whether the product can actually be bought
in the user's market. The one knowledge graph that links cosmetic ingredients
to European regulation has no products in it. Every skincare ontology has
products and no regulation. This thesis is the intersection, built for Lebanon,
on 12,629 products.

---

## The finding that shaped the whole approach

A systematic review of 28 ontology-based recommender systems, with 137
citations, found that they *"seldom use the methodology of building
ontologies"* and that *"none of the primary studies described ontology
evaluation methodologies"*.

> Rahayu, N. et al. (2022). *A systematic review of ontology use in E-Learning
> recommender system.* Computers and Education: Artificial Intelligence.

None of twenty-eight. So naming a construction methodology and reporting a
named evaluation method are not housekeeping in this field. They are
contributions, and both are cheap. That is why this thesis follows Modular
Ontology Modeling for design and Linked Open Terms for publication, and why the
evaluation runs OOPS! and FOOPS! and reports the numbers.

---

## Honesty notes

Things that are true about this review and that I would rather state than have
somebody discover.

- **Five papers are read from the abstract only**, not the full text. The
  `Did I read it, or only the abstract` column in `papers_full.csv` says which.
  The most important of them is the bit-Tech 2025 paper, which is the closest
  competitor to this work and still needs to be obtained in full.
- **Citation counts are as of September 2026** and will drift.
- **Two citations were corrected** between search rounds. TOXIN is Sepehri et
  al. 2025, not 2024. Moe and Aung has a 2016 reprint with more citations than
  the 2014 original.
- **One competitor claim was weakened** by the second search round. A cosmetics
  knowledge graph with a graph neural network for halal prediction already
  exists (HaCKG, IEEE Access 2025), so the halal layer proposed here is a
  smaller claim than it first appeared. `04_papers_round_two.md` says so
  directly.
- **The `Do the numbers back the claim` column is deliberately blunt.** Several
  papers do not support their own headline figures, and the column says so. The
  same standard is applied to this thesis in the gap table above.

---

## Related documents elsewhere in this repository

| File | What it covers |
|---|---|
| [`../ONTOLOGY_REUSE.md`](../ONTOLOGY_REUSE.md) | The earlier, narrower version of this review, kept because it goes deeper on the five papers stored as PDFs |
| [`../SUPPORTING_VOCABULARIES.md`](../SUPPORTING_VOCABULARIES.md) | What schema.org, PROV-O, SKOS and Dublin Core each give this project |
| [`../WHY_REUSE_VOCABULARY.md`](../WHY_REUSE_VOCABULARY.md) | The sources behind the decision to reuse standard vocabulary rather than invent terms |
| [`../vocabularies/skincare-profile.ttl`](../vocabularies/skincare-profile.ttl) | The first draft ontology, with three defined classes |
| [`../WHAT_COSING_GIVES_US.md`](../WHAT_COSING_GIVES_US.md) | What linking to the EU ingredient register made possible |
| [`../GLOSSARY.md`](../GLOSSARY.md) | INCI, CAS, annex, restricted, and the rest of the vocabulary |
