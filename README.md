# Skincare products in Lebanon

A dataset of 12,629 skincare products, built for my MSc thesis on
ontology-based skincare recommendation.

Most recommendation research assumes you can buy anything. In Lebanon you
often can't. A product might suit your skin and simply not be sold here, or
cost different amounts in different Beirut shops, or be priced in dollars when
you're paid in lira. So this dataset records what a product is *and* whether
you can actually get it.

## The numbers

**12,629 products. 1,463 brands. 22 product types. 42 columns.**

Three sources, kept separate, plus the products that appear in two of them:

| | |
|---|---|
| Global, from Skinsort | 6,294 |
| Lebanese retail, sold by shops here | 5,014 |
| Lebanese origin, made here | 802 |
| Both, in the global catalogue *and* sold here | 519 |

That last row is the one worth knowing about. Those 519 products carry an
international listing and a Lebanese price on the same line, so they are the
only rows that can support any comparison between the two markets. Everything
else is either global with no local price, or local with no international
reference.

How full each column is:

| | |
|---|---|
| brand, name, type, country, skin type, sensitivity | 100% |
| product link, image | 99.8%, 99.5% |
| benefits | 96.8% |
| price, and price in lira | 92.6% |
| ingredients | 93.5% |
| EU ingredient functions | 92.7% |
| short description | 91.8% |
| concerns | 93.5% |
| size | 27.4% |
| rating | 51.4% |

What the data says:

| | |
|---|---|
| median price | $22, from $0.10 to $540 |
| sold by at least one Lebanese shop | 11,937 |
| sold by more than one | 356 |
| formulas matched to the EU ingredient register | 11,704 of 11,802, 99.2% |
| ingredient mentions found in the register | 285,917 of 295,991, 96.6% |
| every ingredient identified, no gaps | 9,032 |
| contain an ingredient the EU restricts | 9,613 |
| declare none of the 26 EU fragrance allergens | 9,537 |

## What matters most about it

Every claim records where it came from and how much that source is worth.
Skin type is graded:

| | | |
|---|---|---|
| level 1 | the manufacturer said so | 4,460 |
| level 2 | a retailer said so | 4,539 |
| level 3 | a weaker source said so | 1,954 |
| level 4 | nobody said so, worked out from the ingredients | 1,676 |

The column is 100% full, but only **86.7% of it comes from a source that
stated it**. The rest is inferred and marked as such, so it can be excluded
with `skin_type_tier IN (1,2,3)`.

A full column you can't check is worth less than a patchy one you can. 10,351
products also store the exact sentence the claim was read from, and 11,404
store the page it was read on.

Ingredients are matched against CosIng, the European Commission's official
inventory under Regulation (EC) 1223/2009. 11,704 of the 11,802 products with
an ingredient list matched, 99.2%, and across the whole dataset 96.6% of
295,991 individual ingredient mentions were found in the register. That means
a concern like "may worsen dryness" can name the ingredient and cite the EU
register rather than a rule I invented.

That link also turned up something I was not looking for: **593 products
marked suitable for sensitive skin contain one of the 26 fragrance allergens
the EU requires to be declared by name.** The dataset records both the claim
and the ingredient rather than overruling either.

## Getting the ingredient lists

This was the hard part, and it is worth describing because the per-route rates
are more useful than the final percentage.

Coverage started at 83.8% and finished at 93.5%. Eight routes did it, and they
are not interchangeable:

| route | recovered | of | rate |
|---|---|---|---|
| retailer product pages, initial scrape | 9,063 | 12,629 | 72% |
| web search of the open web | 464 | 1,992 | 23% |
| web search with cleaned queries and Arabic | 196 | 1,173 | 17% |
| shop pages re-read with a table-aware extractor | 44 | 260 | 17% |
| third-party ingredient database | 169 | 1,761 | 10% |
| manufacturer sitemaps | 63 | 1,432 | 4% |
| direct crawl of brand sites | 14 | 1,208 | 1% |
| read by hand from the manufacturer's page | 219 | 533 | 41% |

Seven different page layouts had to be handled: a specification table, a meta
description, a block of capitals under a "Composition INCI" heading, running
text after a heading, a line under a *second* heading (House of Soap prints
"INGREDIENTS" over a marketing block and "ALL INGREDIENTS" over the real one),
a bulleted list with no commas at all (Khan El Kaser), and a formula with no
heading anywhere near it (Rogé Cavaillès).

Four bugs in my own acceptance rules were rejecting real formulas, and each
one looked exactly like a brand that doesn't publish:

- the shape test assumed every formula opens with water, so every anhydrous
  product, meaning sticks, balms, oils and soaps, was thrown away
- ingredient headings were matched in English only, so `Ingrédients`,
  `Composition` and `Ingredienti` were invisible
- `inci` matched inside ordinary words like *principal*
- bullet separators were never normalised, so a formula written with `●`
  scored zero commas and failed at the first line of the test

**What I tried and didn't use**, because a route that fails for a stated
reason is as informative as one that works:

| | |
|---|---|
| borrowing a formula from a similar product | 7 candidates checked by hand, none was the same product |
| a second ingredient database (SkinCarisma) | returns HTTP 403; working around a refusal isn't a method |
| two large brand sites (L'Oréal, IDC Institute) | HTTP 403 to any script, so 31 were read by hand instead |
| a general web retailer as a source (Notino) | matched a Garnier serum to a Bentley fragrance and extracted it cleanly. Wrong, and silent |
| `token_set_ratio` for choosing between one brand's products | scores a short category page 100 against a full product name; replaced by token coverage |

The Notino case is the one I'd point at. A wrong formula that passes every
check is worse than a missing one, because nothing downstream can detect it.
Every third-party match is therefore level 3, and I read all 27 recoveries from
the database pass by hand: **5 were the wrong product and 4 more were
doubtful, an error rate between 19% and 33%.** That is what a name-based match
against someone else's catalogue costs, and it is why the level column exists.

## What was removed, and why

555 rows were taken out because they are not single skincare products. Each
group is written to its own file so the exclusion is reproducible:

| file | rows | what they are |
|---|---|---|
| `EXCLUDED_MAKEUP.csv` | 196 | lip gloss, liners, mascara, foundation, nail products |
| `EXCLUDED_BUNDLE_LISTINGS.csv` | 195 | "BUY 1 GET 1", "30% OFF X + Y". Offers, not products |
| `EXCLUDED_NON_SKINCARE.csv` | 80 | shampoo, hair colour, deodorant, aftershave |
| `EXCLUDED_NON_PRODUCTS.csv` | 59 | face cloths, exfoliating gloves, jade rollers |
| `EXCLUDED_MULTI_PRODUCT_SETS.csv` | 25 | gift boxes, travel kits, "4 BOTTLES SET" |

Two rules had to be abandoned along the way, and both are worth recording.
Matching "Duo" and "Trio" would have deleted twelve La Roche-Posay Effaclar
Duo products. Matching "&" as a sign of two products flagged 571 rows,
including `Vitamin C & Ferulic Acid Serum`. Lip balms, sheet masks and Korean
"sleeping packs" are all skincare and all stayed.

## Three things I didn't expect

**The divide is between manufacturers and retailers, not Lebanon and the rest
of the world.** Brands publish ingredient lists and reviews. The shops
reselling them often don't, even though EU law makes it the manufacturer's
responsibility.

**Big brands are the hard ones.** L'Oréal, Garnier, IDC Institute, Dior and
Estée Lauder return HTTP 403 to any script or publish catalogues built in
JavaScript. Khan El Kaser, a Lebanese soap maker, publishes 1,267 product
pages in a plain sitemap. The companies with the most resources to publish
product data are the ones blocking access to it.

**Beirut shops charge the same.** Of the 356 products sold in more than one
shop, the median difference between cheapest and dearest is 0.0%. No arbitrage
story, and I'd rather say that than imply one.

## What's in this repository

**SKINCARE_FINAL.csv** is the dataset. 12,629 rows, 42 columns. This is the one
to open.

**COMBINED_EVIDENCE.csv** holds the working columns that were trimmed out of the
main file to keep it readable: the quoted sentences, the source URLs, the level
columns, and the merge bookkeeping including how each cross-source match was
made and at what score. Joins to the dataset on `product_id`. Nothing was
deleted, only moved.

**EXCLUDED_*.csv** ,  the five exclusion files described above.

**scripts/validate_dataset.py** runs the checks: that the two files describe
the same products, that `ingredient_count` agrees with the formula, that no
markup survived extraction, that no field derived from a formula is set on a
row that has none, that prices and ratings are inside their possible ranges,
and that what was excluded stayed excluded.

**portal.html** is worth opening in a browser. Fifty pages walking through
where every part of the dataset came from, what went wrong along the way, and how
each problem was fixed. This is the fullest explanation of the work.

**ONTOLOGY_REUSE.md** is the plan for the ontology phase: which four
vocabularies to reuse, download links for each, what their classes and
properties mean in plain terms, how all 42 columns map onto them, and an
honest list of what to skip and why.

**GLOSSARY.md** defines the terms that come up everywhere else: EU, INCI,
CosIng, CAS number, restricted, annex, level, ontology. Start here if any of
those are unfamiliar.

**THE_FOUR_COSING_COLUMNS.md** is the one to hand somebody who asks what the
EU register added. It explains the four new columns and walks a single real
product, a Revox B77 niacinamide serum sold in Beirut, through all four.

**WHAT_COSING_GIVES_US.md** explains, with worked examples from the data,
what linking to the EU ingredient register made possible, and what the RDF
version of it would add on top.

**SUPPORTING_VOCABULARIES.md** answers the question I kept getting stuck on:
what do SKOS, PROV-O and the rest actually give me that I cannot do by hand? It
goes through each one with examples from my own data, including the Cetaphil
lotion that two Beirut shops price at $8.66 and $32.36, and it says plainly
which two I am skipping and why.

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
| `validate_dataset.py` | runs the checks |
| `merge_all_sources.py` | combines the three sources into one |
| `link_cosing.py` | matches ingredients to the EU register |
| `fetch_product_images.py` | reads product images from shop pages |
| `fill_skin_type_from_formula.py` | the level 4 inference |
| `resolve_skin_type_conflicts.py` | settles disagreements between shops |

Most scripts explain in their opening comment why they exist and what went
wrong before they worked. Several were rewritten two or three times, and the
comments say so.

## Running it

```
cd scripts
py build_final_dataset.py
py validate_dataset.py
```

The collection scripts need API keys, read from the environment rather than
written in the code:

```
set SERPER_KEYS=key1,key2
```

## What it isn't

A snapshot, not a live feed. Prices move, and Lebanese prices move quickly.
`price_seen_date` records when each one was true.

**Not complete on ingredients, and the gap is not random.** 984 products have
no formula. They are concentrated in brands whose sites refuse automated
access (L'Oréal, IDC Institute), brands with no reachable website at all
(Madica Swiss, Resultime, Cherry Blossom), and very simple artisanal products
whose entire composition is two or three ingredients written as prose. A
`MANUAL_INGREDIENTS.csv` worklist covers the 533 reachable ones.

**Size sits at 27% and can't be fixed from these sources.** Of 9,505 products
with no size, only 256 state one anywhere in any field. The rest never
published it.

Ratings sit at 51% and more effort won't fix it either. Thousands of Lebanese
shop pages were read in full and carried no review data, because those shops
run Shopify without a review app installed. The brand sites do publish reviews
and those are included.

**Blanks mean three different things** and the distinction matters when
computing coverage. An empty `restricted_ingredients` means no restricted
ingredient was found, which is a result. An empty `free_from` on a product
that has a formula means the rule refused to claim an absence from a list that
may be truncated. An empty `size_value` means the source never published one.

## Licence

Code is MIT. The data is publicly published product information collected for
academic research. See LICENSE before redistributing it.
