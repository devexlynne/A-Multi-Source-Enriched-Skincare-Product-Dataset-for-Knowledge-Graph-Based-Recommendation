# Why reuse existing vocabulary rather than invent your own

Lynne asked where the rule came from that says *do not write `hasProductName`
when `schema:name` already exists*. Fair question, and worth answering with
citations rather than assertion, because it is the principle the whole
ontology plan rests on.

There are four sources. Three are standards or peer-reviewed methodology. One
sentence in the original wording was mine and is marked as such.

---

## 1. W3C, Data on the Web Best Practices

The clearest and most directly quotable source. It is a W3C Recommendation,
not a blog post or a convention.

> **Best Practice 15: Reuse vocabularies, preferably standardized ones.**
> Use terms from shared vocabularies, preferably standardized ones, to encode
> data and metadata.

Its stated reason is the one that matters here: reusing vocabularies already
in use *captures and facilitates consensus in communities*, and the document
gives a concrete example of the same shape as ours, that reusing Dublin Core's
`dct:title` rather than minting a new property lets any Dublin-Core-aware
application read your metadata without being taught how.

Worth knowing for the write-up: this was originally two separate best
practices, "use standardized terms" and "reuse vocabularies", which the
working group merged into one. So citing BP15 covers both halves of the
argument.

<https://www.w3.org/TR/dwbp/>

---

## 2. FAIR principles, Wilkinson et al. 2016

The FAIR guiding principles include, under Interoperability:

> **I2. (Meta)data use vocabularies that follow FAIR principles.**

The accompanying guidance is directly relevant to the position taken in this
project, because it also says what to do when the existing vocabulary is not
enough. Two options are given: publish an extension of an existing, closely
related vocabulary, or create and explicitly publish a new vocabulary resource
that itself follows FAIR.

That is exactly the split in `ONTOLOGY_REUSE.md`. Roughly two thirds of the 42
columns reuse published terms. The remaining skin-matching properties are new,
and they are declared openly rather than smuggled in.

Wilkinson, M. D. et al. (2016). *The FAIR Guiding Principles for scientific
data management and stewardship.* Scientific Data 3, 160018.

---

## 3. The NeOn Methodology

The standard methodology for building ontology networks, and it is built
around reuse rather than treating it as an optional extra. It defines nine
scenarios, several of which are specifically about reusing ontological and
non-ontological resources, re-engineering them, and merging them.

Its stated rationale: reuse supports semantic interoperability and reduces
engineering cost.

This matters for a thesis because it means "I reused four vocabularies and
invented a small layer on top" is a recognised methodology with a name, not an
improvised shortcut.

Suárez-Figueroa, M. C., Gómez-Pérez, A., Fernández-López, M. (2012). *The NeOn
Methodology for Ontology Engineering.*

---

## 4. OOPS!, the ontology pitfall catalogue

Poveda-Villalón and colleagues built a catalogue of common modelling errors
from an empirical analysis of **693 ontologies**, and a free scanner that
checks for them.

One pitfall is precisely the failure being avoided here:

> **P34. Missing equivalent properties.** When an ontology reuses terms from
> other ontologies, classes that have the same meaning should be defined as
> equivalent, in order to benefit interoperability.

So inventing `hasProductName` alongside `schema:name` without declaring them
equivalent is a named, catalogued, machine-detectable defect. Not a matter of
taste.

Running OOPS! over the finished ontology and screenshotting the result is
worth doing. It is free, it takes minutes, and it is external evidence of
quality that a supervisor can verify independently.

<https://oops.linkeddata.es/>

Poveda-Villalón, M., Gómez-Pérez, A., Suárez-Figueroa, M. C. (2014). *OOPS!
(OntOlogy Pitfall Scanner!): An On-line Tool for Ontology Evaluation.*
International Journal on Semantic Web and Information Systems, 10(2), 7-34.

---

## The part that was mine

The original sentence said *reviewers notice invented vocabulary*. That is my
opinion, not a finding from any of the papers above, and it should not be
cited as though it were. Nobody has measured what reviewers notice.

The defensible version of the same point is narrower and stronger:

> Invented vocabulary that duplicates an existing term makes the dataset
> harder to join to other people's work, is flagged as pitfall P34 by an
> automated checker, and runs against a W3C Recommendation and the FAIR
> interoperability principle.

That claim is checkable. The one about reviewers was not.

---

## What this means in practice for this project

Use `schema:name`, `schema:price`, `prov:wasDerivedFrom`, `skos:Concept` and
the rest where they exist. Invent only the skin-matching properties, which
genuinely have no standard equivalent. Where a new term is close to an
existing one, declare the relationship with `skos:closeMatch` rather than
leaving it implicit or overclaiming with `owl:sameAs`.

Then run OOPS! and keep the report.
