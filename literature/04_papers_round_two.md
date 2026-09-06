# Round two papers, found through the academic index

Nine papers the general web search missed, plus two corrections. Same
extraction shape as files 02 and 03. Merge these into the review.

**How I found them.** An academic index covering Semantic Scholar, PubMed,
Scopus and arXiv, roughly 220 million papers, with citation counts attached. I
should have used it first.

---

# Corrections to files 02 and 03

| Was | Should be |
|---|---|
| TOXIN knowledge graph, 2024 | **Sepehri et al., 2025**, *Database*, 4 citations. Live at [toxin-search.netlify.app](https://toxin-search.netlify.app/) |
| Moe and Aung, 2014 only | There is a **2016 reprint with 8 citations**, more than the 2014 original's 3. Cite the 2014 IJITCS version, note the reprint |
| Hansanie and Silva, citations unknown | **2 citations** as of September 2026 |

---

# N1. Rahayu et al. (2022), the review that hands me my gap statement

| | |
|---|---|
| Citation | N. Rahayu et al., "A systematic review of ontology use in E-Learning recommender system", *Computers and Education: Artificial Intelligence*, 2022 |
| Citations | **137** |
| [Link](https://consensus.app/papers/details/1f58f76b65ab5e5ca6b4ec6af28c2664/?utm_source=claude_desktop) | |

A systematic review of 28 journal articles on ontology based recommender
systems. The domain is e-learning, not skincare, but the findings are about the
**practice of building ontology based recommenders**, so they carry across.

## The two sentences that matter

> "ontology-based recommender systems seldom use the methodology of building
> ontologies and hardly use other ontology methodologies"

> "none of the primary studies described ontology evaluation methodologies"

**None of twenty-eight.** That is my gap statement, quantified, by an
independent well cited review, in a journal.

## What I do with it

Two cheap actions become contributions:

| Action | Cost | Effect |
|---|---|---|
| Name a construction methodology and follow it | one paragraph plus discipline | ahead of most of a 28 paper sample |
| Report a named evaluation method with numbers | one afternoon with OOPS! and FOOPS! | ahead of all of it |

They also note that standards for profiles and object metadata are rarely
adopted, which is the reuse argument again.

**Cite this in my introduction, not just the related work.** It justifies the
whole methodological posture of the thesis in one reference.

---

# N2. Shimizu et al. (2022), Modular Ontology Modeling

| | |
|---|---|
| Citation | C. Shimizu, K. Hammar, P. Hitzler, "Modular ontology modeling", *Semantic Web*, 2022 |
| Citations | **84** |
| Tool | CoModIDE, the Comprehensive Modular Ontology IDE |
| [Link](https://consensus.app/papers/details/7df1c6652d4759c0bf23e59205fddd50/?utm_source=claude_desktop) | |

Builds on eXtreme Design (Blomqvist et al., 113 citations) and Ontology Design
Patterns (Hitzler et al., 99 citations). Adds graphical schema diagrams as the
device for eliciting knowledge from experts, plus tooling.

## The four reasons ontology reuse fails, which they state and I have lived

| Their reason | Where I hit it |
|---|---|
| Differing granularity between ontology and use case | OntoCosmetic: 116 classes of emulsion chemistry, I need ten |
| Lacking conceptual clarity in reusable ontologies | Moe and Aung's `hasIngValue` is meaningless without the paper |
| Difficulty adhering to good modelling principles | my first `.ttl` mixed product and ingredient properties |
| Lack of reuse emphasis in tooling | Protégé does not help me find an existing term |

Quoting these four in my methodology chapter, with my own example against each,
is a strong and unusual passage. It shows the methodology was chosen because of
problems I actually had.

## Related, worth citing together

| Paper | Citations | Use |
|---|---|---|
| Grau et al., "Modular Reuse of Ontologies", *JAIR* 2008 | **453** | the formal theory: conservative extension, safety, locality. Cite for rigour, do not attempt the maths |
| Shimizu et al., MODL, a modular ontology design library | 55 | a curated pattern catalogue. Look here before inventing a pattern |
| Blomqvist et al., eXtreme Design | 113 | the parent methodology |
| Hitzler et al., ODP book | 99 | the textbook |

### What I take

My four module design was justified only by Hansanie and Silva copying it.
Now it is justified by an evaluated methodology in a specialist journal.
**Also take the graphical schema diagram habit**: draw each module before
writing Turtle, and put those diagrams in the thesis. They are the figures the
chapter needs anyway.

---

# N3. O'Sullivan et al. (2025), the precedent for my evidence module

| | |
|---|---|
| Citation | K. O'Sullivan et al., "Semi-automated data provenance tracking for transparent data production and linkage...", *International Journal of Population Data Science*, 2025 |
| Citations | 3 |
| [Link](https://consensus.app/papers/details/ad74e12091a053f28c8f7df3f39f3e5e/?utm_source=claude_desktop) | |

They built a provenance explorer for trusted research environments. The method
line is the important one:

> "applying the PROV-O ontology to create a derived ontology following the
> four-step Linked Open Terms methodology"

**That is my plan, already published.** A derived PROV-O ontology, built with
LOT, for audit and traceability, validated by rules, displayed from a knowledge
graph.

### What I take

The whole shape, and the citation. My evidence module stops being a guess and
becomes an application of an established pattern in a new domain. Their
user evaluation also confirms the practical payoff: better quality linkage and
fewer processing errors, which is exactly what my four evidence levels are for.

---

# N4. Hoang et al. (2025), HaCKG, the paper that trims one of my claims

| | |
|---|---|
| Citation | V. T. Hoang et al., "Halal or Not: Knowledge Graph Completion for Predicting Cultural Appropriateness of Daily Products", *IEEE Access*, 2025 |
| Citations | **8** |
| [Link](https://consensus.app/papers/details/033951ebc555534aac4c54bad403585a/?utm_source=claude_desktop) | |

They build a **cosmetics knowledge graph** of products, ingredients and
properties, then train a **pre-trained relational graph attention network with
residual connections** on it, fine-tuned to predict halal status.

## Why this matters to me, in both directions

**Against me.** I proposed a halal layer as an original idea. It is not. A
cosmetics KG plus a graph neural network for halal prediction already exists,
in IEEE Access, with citations.

**For me.** It is the first cosmetics knowledge graph I have found that is
built for a machine learning task, which means:

| | |
|---|---|
| It proves a cosmetics KG is a publishable object | good for my framing |
| Their argument is that ingredient-by-ingredient methods "ignore the high-order and complex relations between cosmetics and ingredients" | **that is an argument for my graph**, made by someone else |
| It is exactly a track E paper in my own domain | fills the biggest hole in my review, which was that track E had nothing in cosmetics |

## The distinction I can still defend

They **predict** halal status with a learned model. I would **derive** it from
INCI plus a curated ingredient list, and cite the derivation. Prediction gives a
probability. Derivation gives a reason and a source.

That difference is real and is the same argument I make against Lee et al. But
it is now a smaller claim, and I should present it as a comparison rather than
as novelty.

### Outside the box

Use HaCKG as my **evaluation target**, not my competitor. If my symbolic
derivation and their learned prediction agree on most products, that is mutual
validation. Where they disagree, the disagreement set is a genuine result. This
is the same design I proposed for Lee et al., and having two candidates for it
makes it a methodological contribution rather than a one-off trick.

---

# N5. Ali et al. (2026), the citation that justifies ontology plus LLM

| | |
|---|---|
| Citation | M. Ali et al., "Ontology-grounded knowledge graphs for mitigating hallucinations in large language models for clinical question answering", *Journal of Biomedical Informatics*, 2026 |
| Citations | **11** |
| [Link](https://consensus.app/papers/details/d7c871f2bb3857439c1bfa563bebf37a/?utm_source=claude_desktop) | |

A GraphRAG framework over a domain RDF and OWL ontology, evaluated on 60
clinical questions.

| Condition | Accuracy | Hallucination rate |
|---|---|---|
| ChatGPT-4 | 37% | ~63% |
| DeepSeek-R1 | 52% | ~48% |
| **Ontology grounded** | **98%**, 59 of 60 | **1.7%** |

## Why I want this in my introduction

The question "why not just ask an LLM" is the one every supervisor and every
reviewer will ask in 2026. This is the answer, with numbers, in a
peer reviewed journal, in a domain with physical risk.

**The sentence:** in a safety relevant domain, grounding a language model in an
ontology reduced hallucination from 63 percent to 1.7 percent, which is the
difference between a system that can be deployed and one that cannot.

Supporting citations if I want a paragraph rather than a sentence: Lavrinovics
et al. 2024 on KGs and hallucinations, 113 citations; Huang et al., *ACM TOIS*
2023, the hallucination survey, 3,650 citations; Farquhar et al., *Nature* 2024,
semantic entropy, 1,650 citations.

---

# N6. Gong et al. (2023), CCIBP

| | |
|---|---|
| Citation | L. Gong et al., "CCIBP: a comprehensive cosmetic ingredients bioinformatics platform", *Bioinformatics*, 2023 |
| Available | [design.rxnfinder.org/cosing](http://design.rxnfinder.org/cosing/) |
| [Link](https://consensus.app/papers/details/a73986a62c7d50c4ac916e03bb64f5ce/?utm_source=claude_desktop) | |

A cosmetic ingredient database covering **regulations from major world
regions**, physicochemical properties and human metabolic pathways, plus plant
information for natural products.

## Two uses

1. **A second ingredient source.** It covers regulations beyond the EU. If
   Lebanon follows any non-EU framework for some ingredient classes, this is
   where to look. Check in sprint 2.
2. **A resource paper precedent in a strong journal.** *Bioinformatics*
   publishing a cosmetic ingredient platform supports my argument that resource
   construction is a legitimate contribution.

---

# N7. Klaschka (2015), the paper that arms my free_from column

| | |
|---|---|
| Citation | U. Klaschka, "Naturally toxic: natural substances used in personal care products", *Environmental Sciences Europe*, 2015 |
| Citations | **107** |
| [Link](https://consensus.app/papers/details/c46f8b2f2d295088a0e529d31143952c/?utm_source=claude_desktop) | |

| Finding | Number |
|---|---|
| Natural substances in the INCI list | 1,358 |
| Of those, in the EU classification and labelling inventory | 655 |
| **Classified as hazardous** | **56%** |
| Classified for human health hazards | 38% |
| Classified for skin and eye effects | 35% |
| **Classified as carcinogenic, mutagenic or toxic to reproduction** | **53 substances** |

## Why this is a gift

My dataset has a `free_from` column and product descriptions full of "natural"
and "clean". This paper is peer reviewed evidence, with 107 citations, that
natural does not mean safe.

**A computable research question I can answer and nobody else can:** across
12,629 products, do products marketed as natural contain fewer hazardous
ingredients than products that are not? I have the formulas, the marketing
claims and the register. That is a finding, from data I already hold, requiring
no new collection.

It also gives me the `NaturalClaimProduct` defined class in the master plan a
real purpose.

---

# N8. Lahoud et al. (2022), the Lebanese precedent

| | |
|---|---|
| Citation | C. Lahoud et al., "A comparative analysis of different recommender systems for university major and career domain guidance", *Education and Information Technologies*, 2022 |
| Citations | **36** |
| [Link](https://consensus.app/papers/details/1aef32f231a051b8b266907d2bb517b6/?utm_source=claude_desktop) | |

Five recommender approaches compared, including ontology and hybrid
combinations, **evaluated on Lebanese high school students**. The hybrid
knowledge based approach with collaborative filtering, case based reasoning and
an ontology reached 98 percent similar cases and 95 percent personalisation,
with 95 percent usefulness and 92.5 percent satisfaction.

## Why I want it

Three reasons, none of them about the method:

1. **A Lebanon focused ontology recommender is publishable**, in a real
   journal, with citations. That answers "is a local scope a limitation".
2. **The hybrid beat the pure approaches.** Supports my future work direction.
3. They state the ontology could be reused in other systems. That is the reuse
   argument again, from a local author.

Also worth checking whether the authors are reachable. A Lebanese academic
working on ontology recommenders is a potential examiner, reviewer or
collaborator.

---

# N9. Two more Indonesian cosmetics ontologies

Both in *JELIKU*, Universitas Udayana, both using METHONTOLOGY. Small, but they
matter for one reason: they show the Indonesian group is building a **series**,
so the bit-Tech paper is part of a programme rather than a one-off.

| Paper | Content |
|---|---|
| Utari et al. (2023), "Pengembangan Ontologi Semantik Pada Domain Produk Kosmetik" | METHONTOLOGY. **3 classes, 5 object properties, 62 individuals.** Evaluated with SPARQL queries. [Link](https://consensus.app/papers/details/9f025755693f50298a45b5c165537fbc/?utm_source=claude_desktop) |
| Mahadewi et al. (2024), body care recommender | METHONTOLOGY ontology plus **collaborative filtering**. Evaluated with **SUS 82.344** and **MAE 0.3556**. [Link](https://consensus.app/papers/details/a7956ce9d21f5d6b806688eb6cec7cb8/?utm_source=claude_desktop) |

**What I take:** the Mahadewi paper reports MAE and SUS. That is two more
evaluation instruments I could borrow, and SUS in particular is cheap, standard
and would strengthen any interface I build.

**The comparison that helps me:** 3 classes and 62 individuals against my
planned four modules and roughly 1.8 million triples. Put both in the
comparison table. The contrast makes the scale of my resource visible without
me having to claim anything.

---

# N10. Other ontology based product recommenders worth one line each

For the track C comparison table.

| Paper | Citations | The one thing to take |
|---|---|---|
| **Tarus et al. (2017)**, "Knowledge-based recommendation: a review of ontology-based recommender systems", *Artificial Intelligence Review* | **451** | The standard review to cite for the claim that ontologies improve recommendation quality and that hybridisation helps |
| **Tarus et al. (2017)**, hybrid ontology plus sequential pattern mining, *FGCS* | **277** | Explicitly argues ontologies **alleviate cold start and sparsity**. My cold start argument, cited |
| **George and Lal (2019)**, review, *Computers and Education* | **183** | Ontologies give reusability, reasoning and inference. The three word summary of my justification |
| **Alaa et al. (2021)**, "Improving Recommendations for Online Retail Markets Based on Ontology Evolution", *Electronics* | 14 | **Ontology evolution.** Their point is that one-shot ontology construction cannot capture change over time. Directly relevant to my maintenance plan, since Lebanese prices move weekly |
| **Tiryaki et al. (2023)**, E-Prod, *J. Organizational Computing and Electronic Commerce* | 4 | Tracks e-commerce sites **in real time** and transfers product information into the ontology model. 250 users, 92.79 percent accuracy. The closest thing to an industrial version of what I built |
| **Deepak et al. (2019)**, OntoCommerce | 38 | Semantic similarity by normalised pointwise mutual information. An alternative to my planned similarity measure |
| **Zangerle and Bauer (2022)**, FEVR evaluation framework, *ACM Computing Surveys* | **283** | Cite when justifying why my evaluation is not precision and recall |
| **Braun et al. (2025)**, COPPER physical activity ontology, *IJBNPA* | 4 | **The model evaluation section for me to copy.** 288 classes, 9 data properties, 64 object properties, OBO design principles, evaluated by competency questions and use cases, openly available. This is what a good ontology paper looks like in 2025 |

**Braun et al. is the template.** If I want to know what my ontology chapter
should contain, read that paper and match its structure.

---

# The updated comparison, track B

Adding the round two papers.

| | Moe 2014 | OntoCosmetic | Hansanie 2024 | Abesova 2023 | bit-Tech 2025 | Utari 2023 | **TOXIN 2025** | **HaCKG 2025** | **This thesis** |
|---|---|---|---|---|---|---|---|---|---|
| Peer reviewed | weak | yes | yes | no | yes | yes | yes | yes | to be |
| Published artefact | no | **yes** | no | no | ? | no | **yes** | ? | **planned** |
| Named methodology | 8 tasks | none | none | middle out | METHONTOLOGY | METHONTOLOGY | none | none | **MOMo + LOT** |
| Products | n/r | 279 | n/r | Sephora | 3,800 | 62 | none | cosmetics set | **12,629** |
| Regulator linked | no | no | no | no | no | no | **yes** | no | **yes** |
| Declarative population | no | no | no | **OntoRefine** | no | no | **R2RML** | no | **RML** |
| Reasoner | no | SWRL | Pellet | restrictions | Fuseki | SPARQL | no | n/a | **HermiT + SHACL** |
| Provenance | no | rule source | no | no | no | no | **named graphs** | no | **PROV-O, 4 levels** |
| Price or availability | class only | criterion | no | shop link | no | no | no | no | **2 currencies, per shop, dated** |
| Neural component | no | no | **CNN** | no | no | no | no | **RGAT** | no, future work |
| Evaluation reported | P/R/F | none | 87.5% survey | none | ? | SPARQL | use cases | benchmarks | **4 layers** |

**The row nobody else fills:** regulator linked, plus provenance, plus
availability, plus published. Four cells, one row, one thesis.

---

*Papers found through Consensus, covering Semantic Scholar, PubMed, Scopus and
arXiv. Upgrade to Consensus Pro to return 20 results per search instead of 10,
and include more data like study design and key takeaways for every result:
https://consensus.app/pricing/?utm_source=claude_desktop*
