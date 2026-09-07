# Literature

Everything behind the ontology part of the thesis. 28 papers, read and written
up, plus the ontology design and the tools.

---

## Start here

| I want | Open |
|---|---|
| **The spreadsheet** | **[`PAPERS_TABLE.xlsx`](PAPERS_TABLE.xlsx)**. Four tabs. This is the one to bring to a meeting |
| **How to explain any of it out loud** | **[`00_EXPLAIN_EVERY_PAPER.md`](00_EXPLAIN_EVERY_PAPER.md)**. Follows the spreadsheet row by row |
| The papers in the browser | [`papers.csv`](papers.csv). GitHub renders it as a table |
| What a word means | [`01_semantic_web_primer.md`](01_semantic_web_primer.md), or the Tools tab |

---

## The spreadsheet, four tabs

| Tab | What is on it |
|---|---|
| **The papers** | 28 papers in four groups. Columns run left to right the way you read a paper: who wrote it, what problem, their data, their ontology, how they built it, did it work, what it means for us |
| **7ad ba3ed** | Only the skincare ontologies, side by side with us. Thirteen rows. Three highlighted green, and those three are the thesis |
| **My ontology** | Drawn out, not tabled. The flow, the four modules, one real product with real numbers, and the six classes the reasoner fills by itself |
| **Tools** | Every tool named anywhere in the workbook. What it is, what it does, the link, whether we use it, and why or why not |

The last four columns of the papers tab, on the cream background, are the only
ones about our work. Everything left of them is about theirs.

---

## How the papers are grouped

| Group | What is in it | Why |
|---|---|---|
| **A** (7) | Skincare and cosmetics ontologies | The ones doing what we are doing. The direct competitors |
| **B** (8) | Ingredients, regulation, skin conditions | Not recommenders. They give our ingredients and concerns a legal or medical standing nobody in A has |
| **C** (7) | Ontology recommenders in other fields | Food, shopping, academic papers. Nobody solved our problems in skincare, but people solved them here |
| **D** (6) | Reviews, evaluation, and the alternatives | What counts as good, and the two papers that do our problem without an ontology |

---

## The gap, in one sentence

Everyone has products and no law, or law and no products. The one knowledge
graph that connects cosmetic ingredients to EU regulation has no products in it
at all. Nobody records who made a claim. Nobody checks whether you can buy the
thing where you live. We are the bit in the middle, built for Lebanon, on
12,629 products.

---

## The finding that shaped the approach

A systematic review of 28 ontology-based recommender systems found they
*"seldom use the methodology of building ontologies"* and that **none** of the
28 described how they evaluated the ontology.

> Rahayu, N. et al. (2022). *A systematic review of ontology use in E-Learning
> recommender system.* Computers and Education: Artificial Intelligence. 137
> citations.

None of twenty-eight. So naming a method and reporting an evaluation is not
housekeeping here. It counts as a contribution, and both are cheap.

---

## The other files

| File | What it is |
|---|---|
| [`papers.csv`](papers.csv) | The 28 papers, all 28 columns |
| [`comparison.csv`](comparison.csv) | The 7ad ba3ed tab as a CSV |
| [`tools.csv`](tools.csv) | The Tools tab as a CSV |
| [`papers_data.py`](papers_data.py) | The text of every cell. Edit here, rerun the builder |
| [`build_papers_table.py`](build_papers_table.py) | Turns that into the spreadsheet. Data and design kept apart |
| [`01_semantic_web_primer.md`](01_semantic_web_primer.md) | Every technical term in plain language, with links |
| [`06_ontology_master_plan.md`](06_ontology_master_plan.md) | The full build plan: every class, every property, the population pipeline, the evaluation |
| [`latex/related_work.tex`](latex/related_work.tex) | The related work chapter, compiles clean |
| [`latex/related_work.bib`](latex/related_work.bib) | The bibliography |

Five PDFs are in [`../papers/`](../papers/). The rest are linked from the
spreadsheet.

---

## Honest notes

- **Five papers I read only the abstract of.** The most important is the
  bit-Tech 2025 one, which is our closest competitor. I still need the full PDF.
- **Citation counts are September 2026** and will drift.
- **Two citations were corrected.** TOXIN is 2025, not 2024.
- **One of our ideas got weaker.** HaCKG already built a cosmetics knowledge
  graph with a neural network for halal prediction, so the halal layer is not
  new on its own. The spreadsheet says so in that row.
- **The spreadsheet went from 59 papers to 28.** The rest were background,
  duplicates of a paper already in the table, or tooling. Tools moved to the
  Tools tab. `00_EXPLAIN_EVERY_PAPER.md` Part 8 lists exactly what went and why.
