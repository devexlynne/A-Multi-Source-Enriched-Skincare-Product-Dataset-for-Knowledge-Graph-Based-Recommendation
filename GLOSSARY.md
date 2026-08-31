# Glossary

Plain definitions for the terms that appear across this repository. Written
for somebody opening the dataset for the first time.

---

## EU

The European Union. Twenty seven European countries that share one set of laws
for goods sold in any of them.

The relevant law here is **Regulation (EC) 1223/2009**, the Cosmetic Products
Regulation. It governs what may go into a cosmetic, what has to appear on the
label, and who is legally responsible for it.

**Why a Lebanese thesis uses a European law.** Lebanon has no equivalent
public register of cosmetic ingredients. And the catalogue itself is largely
European or European-compliant: 2,101 products in this dataset come from
France, 733 from the United Kingdom, 292 from Spain, alongside Germany and
Italy. Those were made to EU rules and carry EU-compliant ingredient labels
already. The register is the reference standard the products were built
against, not something imposed on them from outside.

---

## INCI

International Nomenclature of Cosmetic Ingredients. The standard naming system
for ingredients on a cosmetic label, used across the EU, the United States and
most other markets.

It is why every ingredient list in this dataset reads in capitals and in Latin
for botanicals. Water is `AQUA`. Rose water is
`ROSA DAMASCENA FLOWER WATER`. Vitamin B3 is `NIACINAMIDE`.

INCI is what makes the ingredient lists in this dataset comparable at all. If
shops printed ingredients in ordinary language, matching them to a register
would not be possible.

---

## CosIng

The European Commission's public database of cosmetic ingredients, short for
**Cosmetic Ingredients**. It is the official inventory maintained under
Regulation 1223/2009.

The version used here holds **28,710 entries**. For each ingredient it gives
the INCI name, a reference number, a CAS number, the functions the Commission
recognises for it, and any regulatory restriction.

In this project, 10,876 of the 11,050 products that have an ingredient list
were matched against it, which is 98.4%.

<https://ec.europa.eu/growth/tools-databases/cosing/>

---

## CAS number

Chemical Abstracts Service registry number. A unique identifier for a chemical
substance. Think of it as a passport number for a molecule.

Phenoxyethanol is **122-99-6**. That number means that exact substance
anywhere in the world, in any language, in any database.

**Why it matters here.** Chemical names are unreliable. Rose water appears as
"Rosa Damascena Flower Water", "rose water", "eau de rose" and
"ماء الورد" depending on who wrote the label. A CAS number covers all of them.
It is what would let this dataset be joined to a chemical or toxicology
database later without matching on text again.

Not every entry has one. Botanical extracts and polymers often do not, because
they are mixtures rather than single substances.

---

## CosIng reference number

The Commission's own entry number in the register, separate from the CAS
number. Phenoxyethanol is entry **36522**. Rose water is **59340**.

Where a CAS number identifies a chemical, a CosIng reference identifies a row
in the EU register, so it exists even for the botanical mixtures that have no
CAS number.

---

## Function

What the Commission records an ingredient as doing in a cosmetic. This is an
official classification, not marketing copy.

Examples from the register:

| ingredient | recognised function |
|---|---|
| NIACINAMIDE | smoothing |
| PHENOXYETHANOL | antimicrobial, preservative |
| ALCOHOL DENAT. | astringent, solvent |
| ROSA DAMASCENA FLOWER WATER | fragrance, skin conditioning, skin protecting |

An ingredient usually has several. Rose water has three, which is the source of
the fragrance example in `THE_FOUR_COSING_COLUMNS.md`.

---

## Restricted, and what it does not mean

An ingredient is **restricted** when the regulation attaches a condition to
using it, most often a maximum concentration or a limit on which products it
may go into.

**Restricted does not mean dangerous, and it does not mean banned.**
Phenoxyethanol is an ordinary preservative found in 3,529 products here. Citric
acid, which adjusts pH, is in 3,143. These are unremarkable ingredients used
within their limits.

The `restricted_ingredients` column exists so that somebody can ask the
question, not to answer it for them.

---

## Annex

The regulation's numbered lists, attached at the end of the legal text. The
register points at them rather than repeating their contents.

| annex | what it lists |
|---|---|
| II | substances prohibited in cosmetics |
| III | substances allowed only under stated restrictions |
| IV | permitted colourants |
| V | permitted preservatives |
| VI | permitted UV filters |

So `V/29` on phenoxyethanol reads as **Annex V, entry 29**: a permitted
preservative, subject to the conditions written at entry 29.

**A limitation worth stating up front.** The CosIng file gives the pointer to
the rule, not the rule itself. It says `V/29`; it does not say what the
maximum concentration is. Those numbers live in the annex text of the
regulation, which is a separate document. So this dataset can tell you *that*
an ingredient is restricted and *where* the rule is written, but not *what*
the limit is. Extracting the limits would mean parsing the annexes separately.

**A second caution, about Annex II.** Many Annex II entries are conditional
rather than absolute. `ACID RED 27 ALUMINUM LAKE` is listed as prohibited
"when used as a substance in hair dye products", which says nothing about its
use in a face cream. Citrus peel oils carry an Annex II reference under
conditions relating to their furocoumarin content, and they appear in plenty
of legally sold products. So an Annex II reference in this dataset must
**not** be read as evidence that a product is illegal or unsafe. The register
text alone does not carry enough information to reach that conclusion, and
this repository does not make that claim anywhere.

---

## The 26 declarable allergens

Regulation 1223/2009, Annex III lists 26 fragrance substances that must be
named individually on the label rather than hidden inside the word "parfum",
because they are known to cause reactions in some people. Limonene, linalool,
benzyl alcohol, geraniol and citral are among them.

This dataset uses that list to decide whether a product is safe for sensitive
skin. It is also what produced the finding described in
`WHAT_COSING_GIVES_US.md`: 574 products marked safe for sensitive skin contain
one of the 26.

Being on the list does not make an ingredient harmful. Limonene occurs
naturally in citrus. Benzyl alcohol is usually present as a preservative
rather than a perfume.

---

## level

This project's own term, not a regulatory one. It records how strong the source
of a claim is.

| level | meaning |
|---|---|
| 1 | the manufacturer stated it |
| 2 | a retailer stated it |
| 3 | a weaker source stated it |
| 4 | nobody stated it, and it was worked out from the ingredients |

It applies to skin type and to several other columns. `WHERE skin_type_tier IN
(1,2,3)` gives you only the claims somebody actually made.

---

## Ontology, knowledge graph, RDF, TTL

Terms from the next phase of the thesis rather than the dataset itself.

An **ontology** is a written definition of what kinds of thing exist in a
domain and how they relate. Here: products, brands, ingredients, skin types,
shops, offers, and the connections between them.

A **knowledge graph** is data expressed as a network of statements rather than
rows and columns. Each statement is a subject, a property and a value, such as
"product LBR-00114 has brand Revox B77".

**RDF** is the standard format for writing those statements. **TTL**, short for
Turtle, is the file extension for a readable RDF file. The links in
`ONTOLOGY_REUSE.md` mostly point at `.ttl` files.

**Vocabularies** referenced in that document:

| | |
|---|---|
| schema.org | standard terms for products, prices, offers and ratings |
| PROV-O | the W3C standard for recording where a fact came from |
| SKOS | the W3C standard for controlled lists of terms |
| ChEBI | a chemical ontology, listed as optional |

---

## Coverage

Used in two senses in this repository, so worth separating.

**Column coverage** is how full a column is across the dataset. Ingredients sit
at 83.8%, meaning 11,050 of 13,184 products have an ingredient list.

**CosIng coverage**, the `cosing_coverage` column, is per product: what
percentage of that product's own ingredients were found in the EU register.
5,424 products sit at 100%, meaning nothing in the formula is unidentified.
