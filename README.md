# Skincare products in Lebanon

A dataset of 13,184 skincare products, built for my MSc thesis on
ontology-based skincare recommendation.

Most recommendation research assumes you can buy anything. In Lebanon you
often can't. A product might suit your skin and simply not be sold here, or
cost different amounts in different Beirut shops, or be priced in dollars when
you're paid in lira. So this dataset records what a product is *and* whether
you can actually get it.

## The numbers

| | |
|---|---|
| products | 13,184 |
| brands | 1,475 |
| product types | 22 |
| columns | 42 |
| automated checks, all passing | 87 |

Where the products come from:

| | |
|---|---|
| Global, from Skinsort | 6,350 |
| Lebanese retail, sold by shops here | 5,914 |
| Lebanese origin, made here | 920 |

How full each column is:

| | |
|---|---|
| brand, name, type, country | 100% |
| skin type, sensitivity | 100% |
| product link | 99.7% |
| product image | 99.5% |
| benefits | 96.6% |
| price, and price in lira | 92.4% |
| short description | 91.2% |
| concerns | 83.9% |
| ingredients | 83.8% |
| EU ingredient functions | 82.5% |
| rating | 50.0% |

A few things the data says. The median price is $22, ranging from $0.10 to
$540. 6,033 products are sold by at least one Lebanese shop, 375 by more than
one. 4,782 products are safe for sensitive skin by EU allergen rules, 8,402
are not.

## What matters most about it

Every claim records where it came from and how much that source is worth.
Skin type is graded:

| | | |
|---|---|---|
| tier 1 | the manufacturer said so | 4,522 |
| tier 2 | a retailer said so | 4,657 |
| tier 3 | a weaker source said so | 2,068 |
| tier 4 | nobody said so, worked out from the ingredients | 1,937 |

The column is 100% full, but only **85.3% of it comes from a source that
stated it**. The rest is inferred and marked as such, so it can be excluded
with `skin_type_tier IN (1,2,3)`.

A full column you can't check is worth less than a patchy one you can. 10,620
products also store the exact sentence the claim was read from, and 11,794
store the page it was read on.

Ingredients are matched against CosIng, the European Commission's official
inventory under Regulation (EC) 1223/2009. 10,876 of the 11,050 products with
an ingredient list matched, 98.4%. That means a concern like "may worsen
dryness" can name the ingredient and cite the EU register rather than a rule I
invented.

## Three things I didn't expect

**The divide is between manufacturers and retailers, not Lebanon and the rest
of the world.** Brands publish ingredient lists and reviews. The shops
reselling them often don't. About half of Lebanese retail listings carry no
ingredient declaration, even though EU law makes it the manufacturer's
responsibility.

**Big brands are the hard ones.** Of 316 brand websites asked for a sitemap,
Dior, Clinique, Estée Lauder, La Mer, Kiehl's, Lancôme, LUSH, Benefit and Dove
returned nothing. Beesline gave 523 products, Khan El Kaser 1,100, Dermedic
638, Babaria 1,861. The companies with the most resources to publish product
data are the ones blocking access to it.

**Beirut shops charge the same.** Of the 375 products sold in more than one
shop, the median difference between cheapest and dearest is 0.0%. No arbitrage
story, and I'd rather say that than imply one.

## What's in this repository

**SKINCARE_FINAL.csv** is the dataset. 13,184 rows, 42 columns. This is the one
to open.

**COMBINED_EVIDENCE.csv** holds the working columns that were trimmed out of the
main file to keep it readable: the quoted sentences, the source URLs, the tier
columns, and the merge bookkeeping. Joins to the dataset on `product_id`.
Nothing was deleted, only moved.

**VALIDATION_REPORT.txt** and **VALIDATION_REPORT_FINAL.txt** list the 87 checks
and what each one found. 52 on the working file, 35 on the final one.

**portal.html** is worth opening in a browser. Fifty pages walking through
where every part of the dataset came from, what went wrong along the way, and how
each problem was fixed. This is the fullest explanation of the work.

**ONTOLOGY_REUSE.md** is the plan for the ontology phase: which four
vocabularies to reuse, download links for each, what their classes and
properties mean in plain terms, how all 42 columns map onto them, and an
honest list of what to skip and why.

**THE_FOUR_COSING_COLUMNS.md** is the one to hand somebody who asks what the
EU register added. It explains the four new columns and walks a single real
product, a Revox B77 niacinamide serum sold in Beirut, through all four.

**WHAT_COSING_GIVES_US.md** explains, with worked examples from the data,
what linking to the EU ingredient register made possible, and what the RDF
version of it would add on top. It also records the finding that came out of
the link: 574 products marked safe for sensitive skin contain one of the 26
EU declarable allergens.

**WHY_REUSE_VOCABULARY.md** is the short answer to "says who?" It gives the
four sources behind the decision to reuse standard vocabulary rather than
invent new terms, and flags which part of that argument was opinion rather
than citation.

**RUNBOOK.md** gives the order to run things in if you want to rebuild or extend
the dataset.

**scripts/** has 111 Python files. The ones that matter:

| | |
|---|---|
| `build_final_dataset.py` | turns the working file into SKINCARE_FINAL.csv |
| `validate_dataset.py` | runs the 87 checks |
| `merge_all_sources.py` | combines the three sources into one |
| `link_cosing.py` | matches ingredients to the EU register |
| `fetch_product_images.py` | reads product images from shop pages |
| `fill_skin_type_from_formula.py` | the tier 4 inference |
| `resolve_skin_type_conflicts.py` | settles disagreements between shops |

Most scripts explain in their opening comment why they exist and what went
wrong before they worked. Several were rewritten two or three times.

## Running it

```
cd scripts
py build_final_dataset.py
py validate_dataset.py
py validate_dataset.py --final
```

Both validators should end with all checks passed.

The collection scripts need API keys, read from the environment rather than
written in the code:

```
set SERPER_KEYS=key1,key2
```

## What it isn't

A snapshot, not a live feed. Prices move, and Lebanese prices move quickly.
`price_seen_date` records when each one was true.

Ratings sit at 50% and more effort won't fix it. 5,623 Lebanese shop pages
were read in full and carried no review data at all, because those shops run
Shopify without a review app installed. The brand sites do publish reviews and
those are included.

Nobody has hand-checked a random sample yet. The 87 checks prove the file is
internally consistent, which is not the same as proving it's correct. That's
the next thing to do, and the provenance columns exist so that it can be.

## Licence

Code is MIT. The data is publicly published product information collected for
academic research. See LICENSE before redistributing it.
