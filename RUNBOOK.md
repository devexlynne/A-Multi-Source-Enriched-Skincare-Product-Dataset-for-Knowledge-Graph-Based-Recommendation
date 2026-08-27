# Runbook

Every command runs from `C:\Users\User\Documents\Thesis\FINAL_PIPELINE`.

```
cd C:\Users\User\Documents\Thesis\FINAL_PIPELINE
```

Everything below is free. No API keys, no credits.

---

## 1. Product images — three passes, in this order

Cheapest and most trustworthy source first. Each pass only handles what the
one before it could not, so nothing is paid for twice.

### Pass 1 — the product's own page (DONE, 6,849 images)

```
py fetch_product_images.py --gentle
py fetch_product_images.py --apply
```

Free. This finished the Lebanese retailers, which are the products a Lebanese
shop would actually display. **Skinsort refuses automated requests entirely**,
so its 5,793 products got nothing here and no pacing setting changes that.

`--apply` only writes. It never fetches.

### Pass 2 — the brand's own site

```
py fetch_images_brand_sites.py --dry
```

Read the ten sample matches. Check each pair is the SAME product, not just the
same brand. Then:

```
py fetch_images_brand_sites.py
py fetch_images_brand_sites.py --apply
```

Free. Covers 5,339 of the 6,335 missing, spread over 855 brand sites, so no
single site is asked for more than a handful. That is what avoids the block
that stopped pass 1.

Expect well under 5,339 to match, because a brand's site only lists what it
currently sells.

### Pass 3 — image search, only for the remainder

```
py fetch_images_serper.py --test 40
```

Costs one credit per product, so run it LAST, on whatever is genuinely left.
The test prints the accept rate and which hosts were accepted or refused.

```
py fetch_images_serper.py
py fetch_images_serper.py --apply
```

It accepts an image only from the brand's own domain or a retailer already
trusted elsewhere in this project, and refuses Pinterest, blogs, marketplaces
and Google's own thumbnails. It will refuse a lot. That is the design working:
a wrong image looks fine and quietly shows a customer the wrong product, while
a missing one is visibly missing.

Each image records how it was found in `image_source`, so search results can be
reported separately from images read off a product page, and dropped if a
supervisor objects.

---

## 2. Rebuild and check

Run this after **any** step that changes the data. It is the only thing that
tells you the dataset is still sound.

```
py build_final_dataset.py
py validate_dataset.py --final
py validate_dataset.py
```

You want `ALL 33 CHECKS PASSED` and `ALL 50 CHECKS PASSED`.

If either fails, stop and read the failure before running anything else.

---

## 3. Ingredients from brand sitemaps — optional

Fills formulas for international brands from the manufacturer's own site.
Worth roughly 2 to 4 points of ingredient coverage.

```
py fill_ingredients_sitemaps.py --dry
```

Read the ten sample matches it prints. If they are the same product:

```
py fill_ingredients_sitemaps.py
py fill_ingredients_sitemaps.py --apply
py derive_from_ingredients.py
py fill_from_formula.py
```

Then rebuild and check (section 2).

---

## 4. Ingredients from shop pages — optional, low yield

Measured at roughly 5 percent. Only worth running if you want the coverage
number moved and have the time to spare.

```
py fill_gaps_from_pages.py --worth-it
py fill_gaps_from_pages.py --apply
py derive_from_ingredients.py
py fill_from_formula.py
```

`--worth-it` skips shops already measured to publish nothing, which is most of
them. Then rebuild and check (section 2).

---

## 5. Documents

After the data is final and both validators pass:

```
py build_briefing.py
py make_workbook.py --final
```

`build_briefing.py` regenerates `MEETING_BRIEFING.md` with every figure read
from the live files, so it can never drift from the data.

---

## Already done, do not re-run

These have run and their results are in the dataset:

```
py add_commerce_fields.py          size_ml, price_lbp, price_per_ml, price_tier
py recover_ingredients_offline.py  258 formulas found in older files
py borrow_formula_within_dataset.py  tested, 4 matches, correctly not applied
```

---

## The one thing that is not free

Roughly 14 API keys are hardcoded in `serper_price.py`,
`fill_ingredients_brand_sites.py` and about eleven older scripts. They travel
with this folder if it is ever shared or handed in. Regenerate them on the
provider sites: Serper, Talordata, ScraperAPI, Rayobyte.
