# The master research prompt

This is the prompt you asked me to write. It is the instruction set that
produces everything else in this folder. Keep it. When you want the review
extended, rerun it with a new track or a new paper and you will get output in
the same shape as what is already here.

Read it also as a checklist of what a good related work section must contain,
because that is what it encodes.

---

## How to use it

Paste everything between the two rules into a fresh conversation, then add the
papers or the track you want. Nothing in it is specific to one paper, so it
keeps working as the review grows.

---

## THE PROMPT

You are helping me write the related work chapter of an MSc thesis at Beirut
Arab University. The thesis has two contributions. The first is finished: a
dataset of 12,629 skincare products covering a global catalogue, Lebanese
retail and Lebanese origin products, with ingredient lists linked to CosIng,
the European Commission cosmetic ingredient register. The second is starting: a
foundation ontology for skincare, because no existing ontology fits the
problem.

**My starting position, so you do not explain things I already have.** The
dataset has 42 columns: product identity, brand, type, country, skin type and
its evidence level, ingredients, ingredient count, key ingredients, free from,
SPF, benefits, concerns, price in dollars and lira, price per millilitre, size,
rating, review texts, shops in Lebanon, image, summary, and four columns
derived from CosIng, which are ingredient functions, matched count, coverage
percentage and restricted ingredients. Ingredient coverage is 93.5 percent.
CosIng linkage is 99.2 percent of products that have a formula. Every claim
about skin type carries an evidence level from one to four, where one is the
manufacturer and four is inferred from the formula.

**Treat me as someone who has never studied the semantic web.** Define every
term the first time it appears, in one sentence, in plain language, before
using it. Never assume I know what a triple, an IRI, a reasoner, a triple
store, a shape, an axiom or an embedding is. Give me a link for every tool and
every standard so I can read further.

### What I want

Four things, in this order.

1. A literature review organised into tracks.
2. A teaching document that explains every technical term used in the review.
3. A roadmap of methodologies and tools I can actually use to build my
   ontology, with the decision points marked.
4. A LaTeX related work chapter, with a bib file, ready to compile.

### The tracks

| Track | Covers | Why I need it |
|---|---|---|
| A | Dataset and resource construction papers in cosmetics and adjacent domains | Justifies contribution one and shows where my dataset sits |
| B | Ontologies and knowledge graphs in skincare, cosmetics, dermatology and cosmetic regulation | The direct competitors. The gap I am filling lives here |
| C | Ontology and knowledge graph based recommender systems in any domain | Where the mechanisms come from. Food, tourism, e-commerce, academic papers, movies |
| D | Deep learning recommender systems, including skin and face analysis | The alternative approach I must position against |
| E | Hybrid work that combines knowledge graphs with neural methods | Where the field is going and where my strongest claim probably sits |

Track B is the core. Track C is where I steal mechanisms. Track E is where I
argue for the future of the work.

### The extraction template

For every single paper, fill in all of the following. If a field is not stated
in the paper, write **"not reported"** rather than guessing. Never invent a
number, a DOI or an availability claim.

**Identity**

1. Full citation with authors, title, venue, year, volume and pages
2. DOI or stable URL
3. Venue type and standing: journal or conference, and its quartile or rank if
   you can verify it
4. Approximate citation count, with the date you checked and the source
5. Country and institution of the authors

**Purpose**

6. The problem the paper says it is solving, in one sentence
7. Their stated contribution, in their own words where possible
8. Who the intended user is

**Data**

9. What data they used, and where it came from
10. Size of the data: products, ingredients, users, reviews, triples, classes
11. Whether the data is published, and under what licence
12. How they cleaned it, if they say

**The ontology or knowledge graph**

13. Is it published anywhere: BioPortal, GitHub, Zenodo, a PURL, a w3id
    address, a SPARQL endpoint. Give the link. If it is not published, say so
    plainly, because that is itself a finding
14. The methodology they followed by name: METHONTOLOGY, NeOn, LOT, SAMOD,
    eXtreme Design, Ontology Development 101, or none stated
15. The full class list, or the top two levels if it is large
16. The object properties, with domain and range
17. The data properties
18. Any defined classes, restrictions, or SWRL rules, quoted exactly
19. Which external vocabularies or ontologies they reused, and how
20. Counts: classes, object properties, data properties, individuals, axioms,
    triples
21. Whether the paper contains a figure of the ontology, and what that figure
    shows

**Population**

22. How instances got into the ontology. This is the field I care about most.
    Was it manual, a script, a mapping language such as R2RML or RML, a tool
    such as OntoRefine or Karma, an LLM, or not stated
23. If they scraped, what they scraped and how they handled the mess
24. Whether population was repeatable, and whether they say what happens when
    the source data changes

**The recommendation mechanism**

25. Exactly how a recommendation is produced, step by step
26. Whether a reasoner is used, which one, and what it infers
27. Whether SPARQL is used, and if the paper shows a query, reproduce it
28. Any algorithm outside the ontology: similarity, graph flow, matrix
    factorisation, a neural network, reinforcement learning
29. Whether explanations are produced, and how

**Semantic web components**

30. Whether they link to DBpedia, Wikidata, schema.org, PROV-O, SKOS, Dublin
    Core, OBO Foundry ontologies, or any external identifier system
31. Triple store, editor, reasoner, API and language used, named

**Evaluation**

32. What they measured, with the numbers
33. Sample size and whether there was a baseline
34. Whether the evaluation supports the claim they make from it. Say plainly
    when it does not

**For me**

35. **What I take.** The specific, concrete thing I can lift, named as a class,
    a property, a tool or a step
36. **What I leave, and why**
37. **The gap.** What they could not do, that my dataset lets me do
38. **Outside the box.** One idea per paper that is not the obvious lesson.
    Something that would make my ontology unusual rather than competent. Tie it
    to a real column in my dataset or a real fact about the Lebanese market

### Rules

- No dashes as punctuation. Use commas, full stops, or restructure the
  sentence.
- No filler adjectives. Not "comprehensive", "robust", "seamless", "crucial",
  "pivotal", "leverage", "delve", "furthermore", "moreover", "underscore".
- Write in the first person, as if I read the paper myself and am telling my
  supervisor what is in it. Plain, direct, no performance.
- Prefer a table or a diagram to a paragraph whenever the content is
  comparative or structural. Use mermaid for diagrams.
- Every claim about a paper must be traceable to that paper. If you searched
  for it rather than reading it, say which you did.
- Where a paper's own numbers do not support its headline claim, say so. That
  is the most useful thing a related work section can do.
- Mark anything you could not verify as unverified. Do not smooth over it.

### The related work hierarchy

Organise the chapter so that it narrows. Each section should end by naming
what is missing, and the missing thing should be what the next section
addresses. The final gap should be the thesis.

Give me a comparison table at the end of every track, with the papers as rows,
and columns chosen so that my work would occupy the only fully populated row.

### The LaTeX

Produce a `related_work.tex` that compiles on its own and a matching
`related_work.bib`. Use `\section`, `\subsection`, `\subsubsection`. Include
the comparison tables as real LaTeX tables using `booktabs`. Include a
`tikzpicture` or a described figure for the taxonomy of approaches. Add
`% TODO` comments where I have to insert something only I can write.

---

## What the prompt deliberately does not ask for

Three things, and each was left out for a reason.

| Left out | Why |
|---|---|
| A count of how many papers to include | Coverage of a track matters more than a target number. A track with four honest entries beats one padded to fifteen |
| A requirement to praise the papers | A related work section that likes everything cannot identify a gap |
| Any instruction to compare on accuracy | Most of this literature does not report comparable accuracy. Forcing a column would invent one |
