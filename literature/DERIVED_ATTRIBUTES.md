# What else we can get from the data we already have

My supervisor asked whether we can add things like organic, cruelty free and
animal friendly. I checked all of it against the real dataset rather than
guessing. This is what came back.

**Short version.** Fourteen new columns are available right now with no new
scraping, no API calls and nothing bought. But three of the specific things she
named cannot be derived at all, and I explain why rather than faking them.

---

## Where I looked first, and why it failed

The obvious idea is to mine our text columns for marketing claims. I tried it
across all 12,629 products, searching `product_summary`, `name` and `benefits`
for seventeen claim patterns.

| Claim | Products found | % |
|---|---|---|
| natural | 756 | 6.0% |
| organic | 342 | 2.7% |
| vegan | 109 | 0.9% |
| fragrance free | 94 | 0.7% |
| cruelty free | **16** | **0.1%** |
| reef safe | 2 | 0.0% |

**Not usable.** The reason is that `product_summary` is not real marketing copy.
It is boilerplate we generated ourselves during collection, and it reads like
this:

> "A moisturizer with 26 ingredients, including PHA, spf, and vitamin E."

So there is nothing in it to mine. A column that is 0.1% full is worse than no
column, because it looks like an answer and is not one.

**The real signal is the ingredient list.** We have it on 11,802 products, 93.5
percent, with 96.6 percent of the individual ingredients matched to the EU
register. That is where everything below comes from.

---

## Part 1. What we can add now, and the real numbers

I wrote `FINAL_PIPELINE/add_derived_attributes.py` and ran it in dry-run mode
over the whole dataset. These are actual counts, not estimates.

### Allergy and diet flags

| New column | Products | % of formulas | Why it matters |
|---|---|---|---|
| `contains_animal_derived` | **1,641** | 13.9% | The honest version of "vegan". See Part 2 |
| `contains_tree_nut` | **1,243** | 10.5% | Nut allergy is common and serious, and nobody labels for it |
| `contains_gluten_grain` | **861** | 7.3% | Wheat, oat, barley, rye |
| `contains_soy` | **815** | 6.9% | |
| `contains_coconut` | **2,778** | 23.5% | A very common contact allergen |

### Safety and caution flags

| New column | Products | % | Why it matters |
|---|---|---|---|
| `contains_retinoid` | **681** | 5.8% | Retinoids and hydroquinone. The standard pregnancy caution |
| `contains_photosensitiser` | **704** | 6.0% | Citrus oils that make skin burn in sun. **In Lebanon that matters more than in Europe** |
| `contains_reef_harmful_uv` | **747** | 6.3% | Oxybenzone, octinoxate, octocrylene. Banned in some countries |
| `contains_drying_alcohol` | **826** | 7.0% | Real alcohol only. Cetyl and cetearyl alcohol are emollients and are correctly excluded |

### Formulation description

| New column | What it holds |
|---|---|
| `preservative_system` | Which family preserves it. Phenoxyethanol 37.4%, organic acids 23.3%, parabens 4.1%, formaldehyde releasers 1.3%, isothiazolinones 1.1%, none detected 33.7% |
| `formula_base` | From the first ingredient. Water-based 66.8%, anhydrous 5.9%, humectant-led 1.4% |
| `actives_present` | Which of eight known actives are in it |
| `lead_active_position` | **Where the active sits in the list.** INCI is in concentration order, so position 3 means a lot more than position 30 |

`lead_active_position` is the interesting one. Real result:

| Active | In how many products | In the first 5 ingredients |
|---|---|---|
| Niacinamide | 2,043 | 877 (43%) |
| Glycolic acid | 562 | 269 (48%) |
| Vitamin C | 759 | 187 (25%) |
| Salicylic acid | 985 | 203 (21%) |
| **Retinol** | 295 | **32 (11%)** |

**Only 11 percent of retinol products have retinol anywhere near the front.**
That is a finding about the market, computed from data we already had.

### Everything else

| New column | What it holds |
|---|---|
| `routine_step` | Cleanse, tone, treat, moisturise, protect. **All 12,629 mapped, none unmatched** |
| `body_site` | Face, eye area, lips, hands, body. Feeds the DermO anatomy idea |
| `regional_style` | K-beauty 2,084, French pharmacy 1,948, Lebanese made 910, J-beauty 244 |
| `price_band_lebanon` | Under $10, $10 to $25, $25 to $50, over $50 |

Plus an `_evidence` column beside each flag, naming the exact ingredient that
triggered it. So a reader can check every single "yes".

---

## Part 2. The three things she asked for that we cannot do

This is the part I want to be careful about, because getting it wrong would be
worse than not doing it.

### Vegan: no, and here is why

You cannot prove a product is vegan from an ingredient list.

**Stearic acid, glycerin, squalane and lactic acid can each come from a plant or
from an animal, and the INCI name is identical either way.** There is no way to
tell them apart on the label. The manufacturer knows; the label does not say.

So the logic only works in one direction:

| Can we say | Yes or no |
|---|---|
| This product **contains** an animal-derived ingredient | **Yes.** 1,641 products |
| This product contains **no** animal-derived ingredient | Only that we found none |
| This product **is vegan** | **No.** Absence of evidence is not evidence of absence |

That is why the column is called `contains_animal_derived` and not `vegan`.
The distinction is small in words and large in honesty, and it is exactly the
kind of thing our evidence-level design exists for.

### Cruelty free: no, but obtainable

**Cruelty free is a property of a company, not of a formula.** It is granted by
a certifier such as Leaping Bunny or PETA. Nothing in an ingredient list can
tell you, no matter how good the parsing is.

But it is obtainable, and cheaply, because it is a **brand-level** fact and we
only have 1,463 brands rather than 12,629 products. Both certifiers publish
their approved company lists publicly. Match on brand, record the certifier and
the date as the source, exactly like every other claim in our dataset.

Wikidata would help here too, since it already links brands to parent companies
and some parent companies are certified as a group.

### Organic: no, same reason

Organic is a certification, COSMOS or Ecocert or USDA, held by a product or a
company. Not visible in an INCI list. Same route as cruelty free: an external
certified list, matched on brand or product, stored with its source.

---

## Part 3. Why this is worth doing

Three arguments, in the order I would give them.

**It costs nothing.** No scraping, no API keys, no money. One script over data
we already collected. The whole thing runs in under a minute.

**It fills the gap our own review identified.** The bit-Tech paper has an
`Allergen Type` class that they curated by hand. Ours would be derived from the
formula with the evidence recorded, on three times as many products.

**It gives the ontology real work to do.** Right now our defined classes are
about allergens and availability. With these columns we can write rules like:

```
NutFreeCandidate      = Product with no ingredient marked contains_tree_nut
PregnancyCaution      = Product containing a retinoid
ReefSafeCandidate     = SunCare with no reef-harmful UV filter
HighStrengthActive    = Product whose lead active sits in the first 5 ingredients
```

Note the word **Candidate** in two of those. That is deliberate, for the same
reason as the vegan column.

---

## Part 4. Two research questions this opens up

Both computable from the dataset once these columns exist. Neither needs new
data.

**One. Does "natural" mean safer?** Klaschka (2015, 107 citations) found that
of the 655 natural substances in the EU classification inventory, 56 percent are
classified as hazardous and 53 are carcinogenic, mutagenic or toxic to
reproduction. We have 756 products whose text says natural, we have their
formulas, and we have the register. Nobody has run that comparison at this
scale.

**Two. Are cosmetic claims supported by the composition?** The MVFM paper (2026)
tested three products by hand and found one sold as anti-aging was really a
texture cream. We could run the same check across 11,802 formulas using
`lead_active_position`. That would be the first large-sample test of whether
cosmetic claims are compositionally grounded, and their own paper says that
validation is what is missing.

---

## How to run it

```
cd FINAL_PIPELINE
py add_derived_attributes.py            # dry run, prints the counts
py add_derived_attributes.py --apply    # writes the columns
```

Dry run by default. On apply it writes to a temp file, asserts the row count is
still 12,629, then replaces. Same safety rules as the rest of the pipeline.

**I have not applied it yet.** Say the word and I will, then rerun
`validate_dataset.py` and update the README numbers.

---

## What I checked before trusting it

I sampled real matches from each flag and read them. Every one was a genuine
hit: collagen serums, beeswax balms, argan and macadamia oils in sunscreens,
alcohol denat in La Roche-Posay and ISDIN serums, octocrylene in Nivea and Glow
Recipe sunscreens.

**One false positive found and fixed.** Synthetic beeswax was being counted as
animal-derived on 43 products. It is a lab-made copy and is not animal-derived.
The script now excludes anything marked synthetic, vegetal or biomimetic, which
is why the animal count is 1,641 and not 1,684.

The most common animal-derived ingredients in the dataset, for interest:

| Ingredient | Products |
|---|---|
| Beeswax | 236 |
| Hydrolyzed collagen | 186 |
| Cera alba (beeswax, Latin name) | 109 |
| Honey | 83 |
| Propolis extract | 73 |
| Snail secretion filtrate | 64 |
