# What CosIng actually does for this dataset

Two different questions get confused here, so they are separated below.

1. What did **today's CosIng work** add? It is done, and it already changed
   what the dataset can answer.
2. What would **CosIng-KG**, the RDF version, add on top? Less than you might
   expect, and the honest reason is worth knowing.

Every number and product name below came out of the live file.

---

## Part 1: what today's work already gives you

Four columns were added: `ingredient_functions`, `cosing_matched`,
`cosing_coverage`, `restricted_ingredients`. Here is what each one buys.

### Example 1. A customer question you could not answer yesterday

> *"I want a sunscreen for sensitive skin, with no EU declarable allergen,
> under $30, that I can actually buy in Beirut."*

That is four filters, and one of them did not exist before today:

```
product_type contains "Sunscreen"
sensitivity  = "Sensitive"
restricted_ingredients is empty     <- new
price_usd    < 30
shops_in_lebanon >= 1
```

**51 products match.** Three of them:

| | |
|---|---|
| A-Derma Creme Tres Haute Protection Sans Parfum | $9.50 |
| A-Derma Protect Spray SPF50+ 200ml | $25.50 |
| Avene Anti-Aging Suncare SPF 50+ 50ml | $22.50 |

Without the CosIng columns, the allergen filter is not available at all. You
could filter on the free-from claims the shop chose to print, which is
marketing copy, not a regulatory check.

### Example 2. Answering "why?" with a citation instead of an opinion

Take `LBR-00011`, Eucerin Sensitive Protect Dry Touch Sun Gel-Cream SPF50+,
sold in Lebanon. The dataset flags it as **may worsen dryness**.

**Before today**, if a supervisor asked why, the answer was: because a rule in
this project flags alcohol denat.

**After today**, the answer is: the product contains ALCOHOL DENAT., which the
European Commission records as an **astringent** and a solvent, register entry
74174. Astringents dry the skin.

Same conclusion. The authority moved from me to the Commission. That is the
entire point.

The row also shows `cosing_coverage = 100%`, meaning every single ingredient
in that formula was found in the register, so nothing is being guessed at.

### Example 3. Questions about the whole catalogue

The function column turns 13,184 free-text ingredient lists into something
countable:

| EU recognised function | products |
|---|---|
| Skin conditioning | 10,474 |
| Viscosity controlling | 8,917 |
| Fragrance | 8,625 |
| Solvent | 7,643 |
| Hair conditioning | 6,592 |
| Skin conditioning, emollient | 6,072 |

That last one is a small surprise worth checking: 6,592 products in a
*skincare* dataset contain a hair-conditioning agent. Not an error, since many
polymers do both jobs, but it is the kind of question that was unaskable
before.

Another: **120 products contain a UV filter but are not sold as sunscreen.**
Day creams with SPF, mostly. For a recommender that matters, because somebody
searching for sun protection would never have found them by category alone.

### Example 4. Restricted ingredients, in context

**9,321 products** contain at least one ingredient CosIng records a
restriction against:

| | |
|---|---|
| Phenoxyethanol | 3,529 |
| Citric acid | 3,143 |
| Sodium hydroxide | 1,606 |
| Sodium benzoate | 1,440 |
| Potassium sorbate | 1,285 |
| Limonene | 945 |

This is not a warning list. Restricted means the regulation sets a maximum
concentration, not that the ingredient is dangerous. Phenoxyethanol is an
ordinary preservative and citric acid adjusts pH. The column exists so
somebody can ask the question, not to answer it for them.

---

## The finding this produced

This is the part worth taking to a supervisor.

The dataset marks a product safe for sensitive skin using the 26 fragrance
allergens the EU requires to be declared under Regulation 1223/2009 Annex III.
Cross-checking that against the CosIng-linked formulas found something:

> **574 products marked safe for sensitive skin contain one of the 26
> declarable allergens.** That is 12% of everything marked Sensitive.

Which allergen:

| | |
|---|---|
| linalool | 303 |
| limonene | 291 |
| benzyl alcohol | 196 |
| citronellol | 136 |
| geraniol | 108 |
| hexyl cinnamal | 75 |

These add up to more than 574 because a product can contain several.

And where the "sensitive" claim came from:

| | |
|---|---|
| tier 1, the manufacturer said so | 224 |
| tier 2, a retailer said so | 197 |
| tier 3, weaker source | 151 |

**This is not a bug in the dataset.** The dataset faithfully records what the
manufacturer claimed. What the CosIng link reveals is a real tension between
two things that are both true:

- the manufacturer markets the product for sensitive skin, and
- the formula contains an ingredient the EU requires to be declared because it
  can cause a reaction in sensitive people.

Both can hold at once. Benzyl alcohol is a preservative that happens to also
be on the allergen list. Limonene occurs naturally in citrus oils. A product
can be formulated carefully and still contain one.

The sharpest single case in the data: **bondi sands "Fragrance Free Sunscreen
Daily Face Lotion" contains benzyl alcohol.** Fragrance-free as a marketing
claim, and a declarable fragrance allergen in the formula, both correct at the
same time, because benzyl alcohol is there as a preservative.

That is a genuinely publishable observation about cosmetic labelling, and it
exists only because the ingredients were linked to the register.

**What to do with it:** not overwrite the manufacturer's claim. Add a flag,
something like `allergen_despite_sensitive_claim`, so the recommender can warn
rather than silently decide. Someone with an allergy to linalool should see
that, whatever the box says.

---

## Part 2: what CosIng-KG would add

CosIng-KG (<https://github.com/biobricks-ai/cosing-kg>) is the same register,
published as RDF instead of a spreadsheet.

Being direct: **it adds almost no new facts.** Today's work already extracted
the function, the CAS number and the restriction from the source data. The
knowledge graph does not know anything the CSV did not.

What it adds is **identifiers**, and that matters in exactly one situation.

Right now an ingredient in this dataset is a string, `"ALCOHOL DENAT."`,
matched to a register row. In CosIng-KG it would be a URI, something the whole
Semantic Web can point at. Concretely:

| what you have now | what a URI adds |
|---|---|
| a string matched to a row | a stable identifier |
| joinable to CosIng only | joinable to any graph that also uses CosIng URIs |
| your own copy of the register | the same identity as everyone else's copy |

So the value is **joinability, not content.** Worth doing when:

- the thesis publishes a knowledge graph others are meant to query or extend,
- the graph gets linked to ChEBI, a toxicology resource, or another dataset
  that already uses those identifiers,
- somebody needs to combine this with an EU-wide resource without matching on
  strings again.

Not worth doing if the ontology stays a local artifact that answers local
questions. In that case the CSV columns you already have do the same work with
less machinery.

**A middle option that costs almost nothing:** keep the columns you have and
add the CosIng reference number as a URI next to each ingredient. Entry 74174
becomes an identifier rather than a number in a text field. That gets most of
the joinability without importing another graph.

---

## Short version

**Today's work** made four things possible that were not: filtering on
regulatory allergen status, explaining a concern by citing a regulator,
counting the catalogue by ingredient function, and cross-checking a
manufacturer's claim against EU labelling law. That last one already produced
a finding.

**CosIng-KG** would add stable identifiers so this graph can be joined to
other people's. Do it if the ontology is meant to be reused by others. Skip it
if it stays local, and instead store the CosIng reference number as a URI,
which is an afternoon's work.
