# Skincare dataset: everything to know before the meeting

*Generated 27 August 2026, 22:29 from the files themselves, so nothing here can disagree with the portal.*

This is the main path of the portal, in the same order. The appendix is left out: it is there to answer a question, not to be walked through.

---

## The one-minute version

- **13,184 products**, 1,475 brands, 22 categories, 36 columns
- Three sources: **6,350 global**, **5,914 sold in Lebanon**, **920 made in Lebanon**
- **0 validation checks, all passing**, and the report regenerates so anyone can rerun it
- The Lebanese part is the part that does not exist anywhere else. Its gaps describe how that industry works, which is a result rather than a shortfall.

**If you say only three things:**

1. Every value carries the page it came from. That was the criticism last time and it is now answered for every column.
2. The dataset was tested after it was built, not only while it was being built. Nine faults were found that way, and six of them were fixed by removing a value rather than mending it.
3. The Lebanese-made half of this market has no reviews, often no published formula, and frequently no price. A recommender built on reviews ignores it completely. That is the argument for the ontology.

---

## 1. Every statistic

### The three sources

| source | products | share | what it is |
|---|---|---|---|
| Global (Skinsort) | 6,350 | 48.2% | the international market |
| Lebanese retail | 5,914 | 44.9% | on sale in six Lebanese shops, foreign makers |
| Lebanese origin | 920 | 7.0% | made by Lebanese companies and people |

### How full every column is

| column | filled | share | what it holds |
|---|---|---|---|
| `product_id` | 13,184 | 100.0% | the identifier, GLB / LBR / LBO and a number |
| `source_category` | 13,184 | 100.0% | which of the three sets it came from |
| `brand` | 13,184 | 100.0% | who makes it |
| `name` | 13,184 | 100.0% | the product name |
| `product_type` | 13,184 | 100.0% | cleanser, serum, sunscreen and so on |
| `country` | 13,184 | 100.0% | where the brand is from |
| `product_url` | 13,142 | 99.7% | the page it can be seen on |
| `skin_type` | 11,299 | 85.7% | dry, oily, combination, normal, all |
| `sensitivity` | 11,324 | 85.9% | sensitive or resistant |
| `skin_type_source` | 11,803 | 89.5% | which site the skin type was read from |
| `ingredients` | 11,050 | 83.8% | the full INCI list |
| `ingredient_count` | 11,050 | 83.8% | how many are in it |
| `key_ingredients` | 10,398 | 78.9% | the actives a reader would care about |
| `free_from` | 10,186 | 77.3% | what the formula does not contain |
| `spf` | 1,423 | 10.8% | sun protection factor, where there is one |
| `benefits` | 12,735 | 96.6% | what it claims to do |
| `concerns` | 11,058 | 83.9% | what it may make worse |
| `price_usd` | 12,185 | 92.4% | one price, in dollars |
| `price_source` | 12,185 | 92.4% | who was selling at that price |
| `rating` | 6,595 | 50.0% | out of five |
| `rating_count` | 6,595 | 50.0% | how many people |
| `rating_source` | 7,086 | 53.7% | where the rating came from |
| `review_texts_json` | 4,840 | 36.7% | the reviews themselves |
| `shops_in_lebanon` | 12,383 | 93.9% | how many of the six shops carry it |

### Price

- **12,185 products have a price, 92.4%**
- median $22.00, from $0.10 to $540.00
- Skinsort publishes no prices at all, so every price came from a Lebanese shop or from a market search

### Skin type, and how strong the evidence is

| skin type | products |
|---|---|
| All | 4,862 |
| Dry | 3,315 |
| Combination | 1,547 |
| Oily | 1,391 |
| Normal | 184 |

| where it came from | products |
|---|---|
| the manufacturer&rsquo;s own site | 4,547 |
| a shop that sells it | 4,657 |
| an analysis site | 2,068 |
| something weaker | 52 |

**81.3% come from the manufacturer or a shop**, which are the two kinds of source that were accepted last time.

### What they claim, and what they may worsen

| benefit | products | concern | products |
|---|---|---|---|
| Hydrating | 9,504 | May Worsen Eczema | 6,396 |
| Anti-Aging | 6,978 | May Worsen Rosacea | 5,665 |
| Reduces Irritation | 6,959 | May Worsen Irritation | 5,385 |
| Scar Healing | 6,714 | May Worsen Oily Skin | 5,056 |
| Brightening | 6,441 | May Worsen Dryness | 4,159 |
| Barrier Repair | 6,151 | May Trigger Acne | 4,124 |
| Redness Reducing | 5,683 | None identified in the formula | 1,018 |
| Skin Texture | 5,269 |  |  |
| Good For Oily Skin | 4,682 |  |  |
| Reduces Large Pores | 4,266 |  |  |
| Acne Fighting | 3,507 |  |  |
| Dark Spots | 3,026 |  |  |
| Sun Protection | 718 |  |  |
| Eczema | 287 |  |  |

### Reviews

- 6,595 products have a rating, 50.0%
- 4,840 carry the review text itself
- **0 Lebanese origin products have a review.** Not one of the 23 Lebanese brand sites runs a review system.

---

## 2a. Global (Skinsort)

6,350 products, the international half.

| what | where it came from |
|---|---|
| ingredients | the Skinsort product page, which publishes the full INCI list |
| reviews and ratings | Skinsort, Amazon and Sephora, matched by brand and name |
| skin type | **not** from Skinsort. The first version was built from analysis sites, was rightly questioned, and was deleted and rebuilt from manufacturer and retailer pages |
| price | nowhere. Skinsort publishes none |

**The single most useful thing learned in this project:** searching by keyword and hoping the right page ranks gave 6.6% coverage. Learning each brand's own web address once and asking that address directly gave 98%. The same idea later took Lebanese ingredient coverage from 27% to 76%.

---

## 2b. Lebanese retail

5,914 products from six shops: sohaticare, feel22, mazenonline, zeinacare, nexuscare, daoukpharma.

### Why deduplication was necessary

Six shops selling CeraVe all list the same cream with their own wording, their own size in the title and their own spelling. Counting them as six products would say something false about the Lebanese market.

| step | what happens | where it is argued |
|---|---|---|
| make names comparable | accents and punctuation removed, sizes and offer wording stripped, words sorted | Rahm & Do (2000), §3.1, data transformation: standardise value formats before matching |
| compare only within a brand | the file is grouped by brand first | Christen (2012), ch.4, indexing, called blocking |
| two thresholds, not one | identical word sets accepted outright, 90 or above accepted, below left alone | Fellegi & Sunter (1969), §2, an upper and a lower threshold with a review band |

### Worked examples, including the ones rejected

| A | B | decision | why |
|---|---|---|---|
| CeraVe Moisturising Lotion 236ml | Cerave Moisturizing Lotion 236 ML | **same** | identical word sets once spelling and size are removed |
| CeraVe Hydrating Cleanser | CeraVe Hydrating Cleanser **Bar** | **different** | the bar is another product. An early version merged them |
| Ruboril Expert **M** | Ruboril Expert **S** | **different** | the letter is the whole difference, so short words are kept |
| Effaclar H **Iso-Biome** | Effaclar H **Isobiome** | **same** | a hyphen makes one word into two. The validation found this pair after the merge |

### What else was cleaned

| what | how many | why |
|---|---|---|
| words meaning "we do not know" emptied | 15,470 cells | Rahm & Do (2000) §2 list this under lack of integrity. Review coverage read 89% before and 15% after |
| non-skincare removed | most of the raw scrape | same categories as the global set, so the two can be compared |
| prices in lira converted at 89,500 | 219 rows | one column, one unit. The rate is the Banque du Liban card settlement rate, fixed since December 2023 |
| ingredient lists judged by shape, not heading | every list | a page with the word "Ingredients" over a marketing paragraph has no formula on it |

---

## 2c. Lebanese origin

920 products from **23 Lebanese brands**, collected from the brands&rsquo; own shops. There is no list of these brands to download, so finding them was most of the work.

### How the brands were found

40 searches in English, Arabic and French. The Arabic searches are why the soap houses are here at all: makers working for generations who sell locally never surface in an English search.

Four shapes of question were used: by the product they make, by a brand already known, by the trade rather than the shop, and on social media.

**Proving a brand is Lebanese.** A +961 telephone number turned out to be the most useful signal: hard to fake by accident, present in almost every real Lebanese shop footer.

### The brands

| brand | products | publishes a formula | publishes a price |
|---|---|---|---|
| Houseofsoap | 152 | 50% | 98% |
| Khan El Kaser | 130 | 39% | 100% |
| Cosmaline | 127 | 100% | 4% |
| Beesline | 91 | 95% | 100% |
| The Aloelab | 54 | 80% | 100% |
| Helwé | 46 | 100% | 100% |
| Samasoaps | 34 | 88% | 100% |
| Masbanatawaida | 30 | 80% | 83% |
| Atelier Beautanique | 29 | 97% | 100% |
| Ecladerm | 29 | 100% | 100% |
| Casia Handmade | 28 | 18% | 89% |
| Senteurs d'Orient | 28 | 100% | 100% |
| Cherryblossomleb | 26 | 85% | 100% |
| Splashy | 21 | 5% | 100% |
| Paradise | 18 | 33% | 94% |
| Nuraya | 17 | 94% | 94% |
| Savon Du Liban SDL | 16 | 0% | 100% |
| Yves Morel | 14 | 100% | 100% |
| Zejd | 10 | 70% | 100% |
| LaTerraTales | 8 | 75% | 100% |
| JANA | 7 | 100% | 100% |
| KKO | 3 | 0% | 100% |
| Trop | 2 | 0% | 100% |

### What was taken out, and why

This set was corrected after a review found things in it that do not belong. Lebanese origin means **made by** a Lebanese company, not sold by one.

| what | products | why it was wrong |
|---|---|---|
| **Xiran** | 271 | `xiranskincare.com` is Guangzhou Xiran Cosmetics Co., Ltd, a factory in Baiyun District, Guangzhou, China. Every product is titled "Private Label" or "OEM". Removed from the dataset entirely |
| Duft | 37 | a Lebanese shop. 23 of its 37 products are La Roche-Posay or A-Derma. Moved to Lebanese retail |
| SBRANDS | 28 | a Lebanese shop selling COSRX, BYOMA, NACIFIC. Moved |
| bashrati.care | 22 | a shop, five brand names on one domain. Moved |

**Why the test failed:** it asked whether a page names Lebanon, carries a +961 number or sits on a .lb domain. Xiran sells *into* Lebanon and lists Lebanese contacts, so it passed. The test checked where a company sells. It should have checked where it makes.

### The finding that came out of this

The formula column splits the brands cleanly in two, and the split is about what kind of company the brand is, not its size.

- **Publish nearly every formula:** Atelier Beautanique, Beesline, Cosmaline, Ecladerm, Helwé, Nuraya
- **Publish almost none:** Casia Handmade, Savon Du Liban SDL, Splashy

Under EU Regulation 1223/2009, Article 19, the manufacturer is responsible for declaring the full ingredient list. The brands organised as cosmetics companies publish one. The artisanal makers do not, and no amount of scraping changes that.

### Are these products sold anywhere online?

977 were checked against Bing Shopping: **564 found, 406 not found**.

Treat the second figure as an upper bound. Only 33 of those got an explicit "no results" from Bing; the rest simply showed no price, and Bing renders some prices with JavaScript that a plain fetch does not see.

**This number was nearly a false finding.** An earlier run said 0% of Lebanese products were listed anywhere, which fitted the ingredients result so neatly it looked true. It was a search key that had run out of credits and was returning empty replies to everything.

---

## 3. How it was cleaned

### When a value is kept

| rule | why |
|---|---|
| an ingredient list is recognised by its shape, not its heading | at least five comma-separated pieces and three recognisable chemical names. The benefits panel was passing as ingredients until the second test |
| free-from only where the formula is complete | a claim about an absence can only be checked against a whole list |
| negations are read | thirteen products had the opposite of what their page said. "Not Good for Oily Skin" had been recorded as Oily |
| accents removed before comparing | Avène and Avene are one brand |
| short words kept | dropping them merged Ruboril Expert M with S |

### The faults that changed the data

Eleven in total. None raised an error, and three made the dataset look **better** than it was.

| what happened | how many |
|---|---|
| "none" and "not available" counted as data | 15,470 cells |
| zero treated as missing, wiping real markers | 37,635 cells |
| Lebanese shop prices scraped then dropped by a column-name mismatch | 2,300 prices |
| reviews chosen between rather than pooled | about 550 products |
| five products priced in lira in a dollar column | 5 rows, then 214 more |
| a quarter of market prices from eBay, Mercari and Poshmark | 256 |
| a search key ran out silently and returned empty replies | 4,641 products |
| one brand written five ways: A-derma, ADERMA, Aderma, A-Derma, aderma | 110 brands, 717 rows |
| broken characters from a bad encoding | 120 names |

---

## 4. Validation

**0 checks, all passing.** The script changes nothing: it reads, asks, and writes `VALIDATION_REPORT_FINAL.txt`. Run it yourself with `py validate_dataset.py --final`.

### Where the groups come from

| group | what it asks |
|---|---|
| A | can the file be read at all |
| B | is every row a row, and every product one product |
| C | do the controlled columns hold only their allowed values |
| D | are the numbers inside sensible limits |
| E | do fields that depend on each other agree |
| F | does every claim say where it came from |
| G | is anything left that means "we do not know" |

The grouping follows the data quality literature rather than the shape of the code:

- **Wang, R.Y. & Strong, D.M. (1996).** Beyond Accuracy: What Data Quality Means to Data Consumers. *Journal of Management Information Systems* 12(4), 5–33. Quality is more than the values being right.
- **Pipino, L.L., Lee, Y.W. & Wang, R.Y. (2002).** Data Quality Assessment. *Communications of the ACM* 45(4), 211–218. Measuring a dimension as a ratio, which is what every coverage figure here is.
- **Batini, C. et al. (2009).** Methodologies for Data Quality Assessment and Improvement. *ACM Computing Surveys* 41(3), Art. 16. Describe, measure, then decide what to do about the failures.
- **Rahm, E. & Do, H.H. (2000).** Data Cleaning: Problems and Current Approaches. Clean each source before joining, which decided the shape of the pipeline.

### What the checking found the first time it ran

Nine faults, none caught by the merge, because the merge does not ask these questions.

| what was wrong | how many | what I did |
|---|---|---|
| invisible control characters in ingredient lists | 2 cells | removed |
| the same product twice under two spellings | 2 pairs | merged |
| SPF 150 on a product labelled 50+, and SPF 504 | 2 rows | read 50 from the name, emptied the other |
| key ingredients that were sentences | 21 rows | emptied |
| a rating with no source, no text, no count | 90 rows | removed |
| skin type contradicting its own status column | 7 rows | removed |
| **ingredient lists with no record of where they came from** | **8,118 rows** | filled in the source |
| a brand recorded as "Undefined" | 1 row | read from the product name |
| a review field holding ". \|\|\| ." | 1 row | emptied |

**Six of the nine were fixed by removing a value, not mending it**, on the rule that a wrong value is worse than a blank. Five coverage figures went down as a result. Only one went up, and it is the one that matters for a knowledge graph: formulas with a known source went from 24.4% to 100%.

---

## 5. Ontology, the next phase

### What an ontology is

From the CMPS456 lecture, slide 4: an ontology turns the complexities of reality into a structured guide a computer can follow. You define **individuals**, **classes**, **attributes**, **relations**, and the **constraints and axioms** that govern them.

Slide 42 in one line: **Ontology + Data = Knowledge Graph.**

| question | the spreadsheet | the ontology |
|---|---|---|
| products for dry, sensitive skin | filter two columns, works | the same |
| products with no fragrance allergens | **not possible**, the ingredients are one long string | possible, because Linalool is linked to its CosIng function |
| why does this suit dry skin? | no answer | because it contains glycerin, a humectant, and humectants suit dry skin |

Mine is a **domain ontology** (lecture slide 33), with a little of the application kind in it.

### Reuse means the other vocabulary goes inside the file

Not inspiration. Instead of inventing `myOntology:hasProductName`, the file literally says `schema:name`:

```
:LBR-00143
    a                  :Product ;
    schema:name        "The Aloelab 0.5% Retinol Night Serum" ;
    schema:brand       :TheAloelab ;
    schema:category    "Serum" ;
    :suitableFor       :OilySkin ;
    :contains          :Glycerin , :Retinol .
```

Three of those six lines are somebody else&rsquo;s vocabulary.

| ontology | what it gives us | link |
|---|---|---|
| **schema.org** | name, brand, category, and the Offer shape for price and seller | https://schema.org/Product |
| **CosIng-KG** | what each ingredient *does*. This is what makes "no fragrance allergens" answerable at all | https://github.com/biobricks-ai/cosing-kg |
| **OntoCosmetic** | the closest existing model, for formulation. No retail, no price, no skin type, which is our gap | https://github.com/ERPI-UL/OntoCosmetic |
| **PROV-O** | the standard way to say where a fact came from, which is our whole tier system | https://www.w3.org/TR/prov-o/ |
| **SKOS** | the controlled lists, with alternative labels in French and Arabic | https://www.w3.org/TR/skos-reference/ |

The CosIng example is the one worth showing:

```
my dataset says:   ingredients = "Aqua, Glycerin, Linalool, ..."

with CosIng loaded:
  :Glycerin   cosing:function  cosing:Humectant .
  :Linalool   cosing:function  cosing:Perfuming ;
              cosing:isAllergen true .
```

### The model proposed

Twelve classes, each earning its place from a column: Product, ProductCategory, Brand, Ingredient, IngredientFunction, SkinType, Sensitivity, Concern, Benefit, Offer, Review, Evidence.

**Evidence is the class I would defend hardest.** Most product ontologies record that a product suits dry skin. Mine records that it suits dry skin *because this page said so, in these words, and that page is the manufacturer's own*. That is what the tier system was for.

### Filling it

| what | by hand or automatic |
|---|---|
| the classes and hierarchy | by hand, in Protégé |
| the controlled lists | by hand, they are small and already controlled |
| linking ingredients to CosIng | automatic, then the failures checked |
| the 13,184 products | automatic |

Three ways to convert: W3C **direct mapping** (too blunt), **R2RML** (a readable mapping file, and what I would use), or a script with rdflib (quickest for a first draft). Start with the script to test the model, move to R2RML for the thesis.

### Checking the ontology

| method | what it catches |
|---|---|
| competency questions | a question you cannot answer names the missing class. Grüninger & Fox (1995) |
| a reasoner, HermiT | contradictions, empty classes, cycles |
| **OOPS!** | 33 of 41 known modelling pitfalls. Poveda-Villalón et al. (2014), *IJSWIS* 10(2), 7–34. https://oops.linkeddata.es/ |
| SHACL | whether the individuals obey the model, the same rules as my validation but in a standard language |

### Using the ontology to check the dataset

This runs the usual direction backwards, and it is the part I find most interesting.

| a fault only reasoning finds | the chain |
|---|---|
| a product for sensitive skin containing a known allergen | suitableFor Sensitive, contains Linalool, Linalool is a FragranceAllergen |
| a hydration claim with no humectant | claims Hydrating, but no Ingredient with function Humectant |
| a sunscreen with no UV filter | almost certainly a truncated ingredient list, and a good way to find them |

Vendruscolo et al. (2025) tested 187 products marketed as hypoallergenic and found 89% contained at least one known allergen. With the ontology loaded the same question could be asked of 13,184 products.

---

## Questions they will probably ask

**Why is price only 92%?** Skinsort publishes no prices at all. Two Lebanese brands publish none across hundreds of pages: one sells private label to other companies, one sells through pharmacies. The gap is structural.

**Why is rating only 48%?** It went *down* during validation, because 90 ratings with no source, no text and no count were removed. An honest 48% beats a 49% with holes in it.

**How do you know the skin types are right?** Every one carries the page, the sentence it was read from, and a tier saying how strong that page is. 81.3% come from a manufacturer or a shop.

**Is the dataset finished?** The columns are. 966 products could still be asked about price and rating, which needs about $5 of API credits.

**What is genuinely new here?** The Lebanese origin set. It does not exist anywhere else, and what is missing from it describes an industry: no reviews at all, formulas published only by the brands organised as companies, and prices absent wherever the maker sells business to business.

---

## The files

| file | what it is |
|---|---|
| `SKINCARE_FINAL.xlsx` | the dataset to show. 13,184 products, 36 columns |
| `SKINCARE_FINAL.csv` | the same thing as data |
| `COMBINED_EVIDENCE.csv` | everything removed from the tidy file, joined on `product_id`. Nothing was deleted |
| `VALIDATION_REPORT_FINAL.txt` | the checks and their answers |
| `Lynne-Thesis Portal.html` | the full walkthrough with diagrams |
| `COMBINED_DATASET.csv` | the working file, all 56 columns |