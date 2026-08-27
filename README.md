# A skincare dataset for Lebanon

13,184 products, 42 columns, and a record of where every claim came from.

I started this because the recommendation papers I could find assume a market
where you can buy anything. Lebanon is not that market. A product can suit your skin
perfectly and simply not be sold here, or cost three different amounts in
three Beirut shops, or be priced in dollars when you're paid in lira. So the
dataset tracks what a product is *and* whether you can actually get it.

## What's in it

Three sources, kept separate rather than blended together:

| | products |
|---|---|
| Global (Skinsort) | 6,350 |
| Lebanese retail, sold by shops here | 5,914 |
| Lebanese origin, made here | 920 |

Coverage runs from 100% on brand, name, product type, country, skin type and
sensitivity, through 99.5% on images and 96.6% on benefits, down to 83.8% on
ingredients and 50% on ratings. 87 automated checks pass on every build.

## The bit I'd actually point at

Every claim carries its source and how strong that source is. Skin type is
graded 1 to 4:

| tier | | products |
|---|---|---|
| 1 | the manufacturer said so | 4,522 |
| 2 | a retailer said so | 4,657 |
| 3 | something weaker said so | 2,068 |
| 4 | nobody said so, worked out from the formula | 1,937 |

So the column reads 100%, but only **85.3% of it is stated by a source**. The
rest is inferred and labelled as such. `WHERE skin_type_tier IN (1,2,3)` gets
you just the stated ones.

That split is the whole point. A full column you can't audit is worth less
than a patchy one you can. 10,620 products also store the exact sentence the
claim was read from, and 11,794 store the page it was read on.

## Ingredients are linked to the EU register

Every formula is matched against CosIng, the European Commission's inventory
under Regulation (EC) 1223/2009. 10,876 of the 11,050 products with an
ingredient list matched, 98.4%.

This is what lets a concern point at a regulator instead of at a rule I wrote.
The dataset doesn't just say a product may worsen dryness; it can name the
ingredient, give the function the Commission recognises for it, and link the
register entry.

## Things I didn't expect

The interesting split isn't Lebanese against global, it's **manufacturers
against retailers**. Brands publish ingredient lists and reviews. The shops
reselling those brands mostly do not. Roughly half of Lebanese retail listings
carry no ingredient declaration, even though Article 19 of the same regulation
makes it the manufacturer's job. The gap is in the listing, not the product.

I also assumed big brands would be the easy ones to collect from. The opposite.
Of 316 brand sites asked for a sitemap, Dior, Clinique, Estée Lauder, La Mer,
Kiehl's, Lancôme, LUSH, Benefit and Dove all returned nothing. Beesline gave
523 products, Khan El Kaser 1,100, Dermedic 638, Babaria 1,861. The companies
best resourced to publish structured product data are the ones withholding it.

And a null result worth stating: Beirut shops price identically. Only 375
products are sold by more than one Lebanese shop, and the median difference
between cheapest and dearest is 0.0%. No arbitrage story here, and I'd rather
say so than imply one.

## Files

`SKINCARE_FINAL.csv` is the dataset. `COMBINED_EVIDENCE.csv` holds everything
trimmed out of it, the quotes, source URLs and tier columns, joined on `product_id`.
Nothing was thrown away to make the main file readable, it was moved.
`VALIDATION_REPORT.txt` lists the 87 checks and what each one found.

## Running it

```bash
cd scripts
py build_final_dataset.py       # rebuild the tidy file
py validate_dataset.py          # 52 checks on the working file
py validate_dataset.py --final  # 35 on the tidy one
```

The scripts expect `COMBINED_DATASET.csv` beside them. That is the working
file, 30 MB of intermediate columns, and it is not in this repository:
`SKINCARE_FINAL.csv` and `COMBINED_EVIDENCE.csv` together hold everything it
contains.

Collection scripts need API keys from the environment: `set SERPER_KEYS=k1,k2`,
or a line `SERPER_KEYS=k1,k2` in a `.env` file, which git ignores.

## What it isn't

A snapshot, not a feed. Prices move and Lebanese prices move fast;
`price_seen_date` says when each was true.

Ratings sit at 50% and no amount of effort fixes that. 5,623 Lebanese shop
pages were read in full and carried no review data at all, because those shops
run Shopify without a review app. The brand sites do publish reviews and those
are in here.

And nobody has hand-checked a random sample yet. The 87 checks prove the file
is internally consistent, which isn't the same as proving it's right. That's
what I want to do next, and the provenance columns exist so it's possible.

## Licence

Code is MIT. The data is publicly published product information collected for
academic research. See LICENSE before redistributing it.

Part of an MSc thesis on ontology-based skincare recommendation for the
Lebanese market.
