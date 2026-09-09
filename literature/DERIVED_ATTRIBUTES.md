# What else we can get from the data we already have

My supervisor asked whether we can add things like organic, cruelty free and
animal friendly. I went and looked at what the cosmetic analysis sites actually
check, then tested every property against our real 12,629 products.

**Result: 54 new columns.** No new scraping, no API calls, nothing bought. Three
of the specific things she named cannot be derived at all, and I say why rather
than faking them.

---

## Where I looked, and why the obvious route failed

The first idea is to mine our text for marketing claims. I searched all 12,629
products across `product_summary`, `name` and `benefits` for seventeen claim
patterns.

| Claim | Found | % |
|---|---|---|
| natural | 756 | 6.0% |
| organic | 342 | 2.7% |
| vegan | 109 | 0.9% |
| **cruelty free** | **16** | **0.1%** |

**Not usable.** `product_summary` is not marketing copy. It is boilerplate we
generated ourselves during collection: *"A moisturizer with 26 ingredients,
including PHA, spf, and vitamin E."* There is nothing in it to mine. A column
that is 0.1% full looks like an answer and is not one.

**The signal is the ingredient list.** We have it on 11,802 products with 96.6%
of individual ingredients matched to the EU register.

---

## What the analysis sites actually check

Before deciding what to build I checked what already exists, so we match the
vocabulary people expect.

| Site | What it flags |
|---|---|
| **SkinCarisma** | Parabens, sulfates, alcohol, silicones, EU allergens, **comedogenic**, and **fungal acne (Malassezia)** triggers. Fungal-acne-safe filtering is its best known feature |
| **CosDNA** | A 1 to 9 **comedogenic** rating and a 1 to 9 **irritancy** rating per ingredient, plus a 1 to 10 safety level drawn from CIR, RTECS and FDA reports |
| **SkinSort** | Fungal acne safe, non-comedogenic, silicone free, reef safe |
| **EWG Skin Deep** | A hazard score per ingredient |

One caveat worth knowing and quoting: **the comedogenic ratings everyone uses
come from a study done on the inside of rabbit ears**, not on human skin. That
is why our column is called `contains_comedogenic` and not `will_cause_acne`.

I also checked the EU regulations coming into force, since those are the ones a
Lebanese importer will meet next: **nanomaterial labelling**, **microplastics
under 2023/2055** with rinse-off reformulation due October 2027, and
**Regulation 2026/909** which bans triphenyl phosphate and tightens benzyl
salicylate as endocrine disruptors.

---

## What we can add now, with real counts

All dry-run figures from `FINAL_PIPELINE/add_derived_attributes.py` over the
whole dataset. **28 flags, 14 evidence columns, 12 descriptive columns.**

### Acne and skin reactivity, the thing people search for most

| Column | Products | % | Note |
|---|---|---|---|
| `feeds_malassezia` | **7,093** | 60.1% | Fungal acne triggers. SkinCarisma's flagship filter |
| `contains_comedogenic` | **1,991** | 16.9% | From the standard comedogenic list |

### Allergy and diet

| Column | Products | % |
|---|---|---|
| `contains_coconut` | **2,778** | 23.5% |
| `contains_animal_derived` | **1,641** | 13.9% |
| `contains_tree_nut` | **1,243** | 10.5% |
| `contains_gluten_grain` | 861 | 7.3% |
| `contains_soy` | 815 | 6.9% |

### Safety and caution

| Column | Products | % | Why it matters |
|---|---|---|---|
| `contains_drying_alcohol` | 826 | 7.0% | Real ethanol only. Cetyl and cetearyl alcohol correctly excluded |
| `contains_reef_harmful_uv` | 747 | 6.3% | Oxybenzone, octinoxate, octocrylene |
| `contains_photosensitiser` | 704 | 6.0% | Citrus oils that make skin burn in sun. **Matters more in Lebanon than in Europe** |
| `contains_retinoid` | 681 | 5.8% | The standard pregnancy caution |

### EU regulatory watch, and this is the part nobody else has

| Column | Products | % | Which rule |
|---|---|---|---|
| `contains_synthetic_polymer` | **3,125** | 26.5% | Broad polymer set |
| `contains_endocrine_concern` | **1,582** | 13.4% | Regulation 2026/909 and prior restrictions |
| `contains_solid_microplastic` | **~700** | 6% | Regulation 2023/2055, solid particles only |
| `contains_nanomaterial` | 101 | 0.9% | Products already carrying `[nano]` on the label |
| `contains_pfas` | 51 | 0.4% | PTFE, perfluorodecalin, perfluorohexane |

**This is a forward-looking column set.** A product with a solid microplastic
has to be reformulated before October 2027. Nothing in our review flags that.

### The usual "free from" filters

`contains_peg` 3,162 (26.8%), `contains_silicone` 2,879 (24.4%),
`contains_propylene_glycol` 1,609 (13.6%), `contains_sulfate` 390 (3.3%),
`contains_talc` 103 (0.9%).

### Active families

| Column | Products | % |
|---|---|---|
| `contains_soothing` | 5,522 | 46.8% |
| `contains_antioxidant` | 5,157 | 43.7% |
| `contains_aha` | 1,254 | 10.6% |
| `contains_ceramide` | 1,064 | 9.0% |
| `contains_bha` | 1,026 | 8.7% |
| `contains_peptide` | 839 | 7.1% |
| `contains_pha` | 409 | 3.5% |

### Descriptive columns

| Column | What it holds |
|---|---|
| `sunscreen_filter_type` | **827 chemical, 727 mineral, 329 hybrid.** 1,883 products carry a UV filter |
| `moisturiser_type` | Humectant 6,020, draws and seals 3,577, occlusive 601 |
| `preservative_system` | Phenoxyethanol 37.4%, organic acids 23.3%, parabens 4.1%, formaldehyde releasers 1.3%, isothiazolinones 1.1% |
| `formula_base` | Water-based 66.8%, anhydrous 5.9% |
| `actives_present` | Which of ten known actives are in it |
| `lead_active_position` | **Where the strongest active sits in the INCI list** |
| `stated_concentration` | **505 products state a percentage in their own name** |
| `halal_candidate` | 9,415 candidates. Candidate only, see below |
| `routine_step` | Cleanse, tone, treat, moisturise, protect. All 12,629 mapped |
| `body_site` | Face, eye area, lips, hands, body |
| `regional_style` | K-beauty 2,084, French pharmacy 1,948, Lebanese 910, J-beauty 244 |
| `price_band_lebanon` | Four bands |

Every flag has an `_evidence` column naming the exact ingredient that triggered
it, so a reader can check any single "yes".

---

## The two findings worth showing her

**One. Nine out of ten retinol products have almost no retinol.**

INCI is in concentration order, so position tells you strength.

| Active | Products containing it | In the first 5 ingredients |
|---|---|---|
| Glycolic acid | 562 | 269 (48%) |
| Niacinamide | 2,043 | 877 (43%) |
| Vitamin C | 759 | 187 (25%) |
| Salicylic acid | 985 | 203 (21%) |
| **Retinol** | 295 | **32 (11%)** |

**Two. 505 products state their own concentration in the name.** "2% BHA
Liquid Exfoliant", "10% Glycolic Acid Toner", "Arbutin 2%". That is a free,
self-declared strength label on 4% of the catalogue, and it lets us check the
claim against where the ingredient actually sits in the list.

---

## The three things she asked for that we cannot do

### Vegan: no

**Stearic acid, glycerin, squalane and lactic acid can each come from a plant or
an animal, and the INCI name is identical either way.** The manufacturer knows;
the label does not say.

| Can we say | |
|---|---|
| This product **contains** an animal-derived ingredient | **Yes.** 1,641 products |
| This product contains **no** animal ingredient | Only that we found none |
| This product **is vegan** | **No.** Absence of evidence is not evidence of absence |

That is why the column is `contains_animal_derived`. Same reasoning is why
`halal_candidate` says candidate.

### Cruelty free: no, but obtainable

It is a property of a **company**, granted by Leaping Bunny or PETA. No
ingredient list can tell you. But it is cheap to get because it is brand-level
and we have 1,463 brands, not 12,629 products. Both certifiers publish their
lists. Match on brand, store the certifier and date as the source, exactly like
every other claim in our dataset.

### Organic: no, same reason

A COSMOS, Ecocert or USDA certification held by a product or company. Same route.

---

## Four precision problems I found and fixed

This is the part I would show a supervisor, because it is where the care is.

**Synthetic beeswax is not animal-derived.** It was being counted on 43
products. It is a lab-made copy. Now excluded along with vegetal and biomimetic
variants.

**Cetyl and cetearyl alcohol are not drying alcohols.** They are emollients that
soften skin. Including them inflated the drying-alcohol count from 826 to 1,503.
Only ethanol and its denatured forms count.

**Citric acid is not an exfoliating AHA.** 3,267 products contain it, but in
almost all of them it is a pH adjuster. Including it would have wrongly labelled
**2,842 products** as containing an AHA. Excluded, which is why the AHA count is
1,254 and not 4,096.

**Carbomer is not a microplastic.** A first pass caught 3,125 products, but
1,930 of those were carbomer, a swollen gel network rather than a solid bead,
plus several hundred dissolved polyquaternium conditioners. EU 2023/2055
restricts **solid particles**. So the column was split: `contains_solid_microplastic`
holds only what the restriction targets, `contains_synthetic_polymer` holds the
broader set.

---

## Why this is worth doing

**It costs nothing.** One script over data we already collected, runs in about a
minute.

**It answers our own gap analysis.** The bit-Tech paper has an `Allergen Type`
class curated by hand. Ours is derived from the formula with the evidence
recorded, on three times as many products.

**It gives the ontology real work.** New defined classes become possible:

```
FungalAcneSafeCandidate = Product with no ingredient that feeds malassezia
NutFreeCandidate        = Product with no tree nut detected
PregnancyCaution        = Product containing a retinoid
MineralSunscreen        = SunCare whose only filters are mineral
NeedsReformulationBy2027= Product containing a solid microplastic
HighStrengthActive      = Product whose lead active sits in the first 5
```

Note **Candidate** on two of them. Deliberate, for the same reason as vegan.

---

## Two research questions this opens

**Does "natural" mean safer?** Klaschka (2015, 107 citations) found 56% of the
655 natural INCI substances in the EU inventory are classified hazardous, and 53
are carcinogenic, mutagenic or toxic to reproduction. We have 756 products
claiming natural, their formulas, and the register. Nobody has run it at this
scale.

**Are claims supported by the composition?** MVFM (2026) tested three products
by hand and found one sold as anti-aging was really a texture cream. With
`lead_active_position` and `stated_concentration` we could run that across
11,802 formulas. Their own paper says large-scale validation is what is missing.

---

## How to run it

```
cd FINAL_PIPELINE
py add_derived_attributes.py            # dry run, prints all the counts
py add_derived_attributes.py --apply    # writes the 54 columns
```

Dry run by default. On apply it writes to a temp file, asserts the row count is
still 12,629, then replaces. Same safety rules as the rest of the pipeline.

**Not applied yet.** Say the word and I will, then rerun `validate_dataset.py`
and update the README.

---

## Sources

- [SkinCarisma ingredient analyzer](https://www.skincarisma.com/ingredient-analyzer)
- [CosDNA ingredient analysis](https://www.cosdna.com/eng/ingredients.php)
- [SkinSort comedogenic and irritancy ratings explained](https://skinsort.com/blog/comedogenic-irritancy-ratings-explained)
- [EU microplastics regulation 2023/2055](https://euverify.com/resource/eu-microplastics-regulation/)
- [EU Cosmetics Regulation 2026/909, new bans](https://cosmeservice.com/news/eu-cosmetics-regulation-2026-909-restrictions-deadlines/)
- [EU cosmetic ingredient regulations, nanomaterials](https://cosmetic.chemlinked.com/cosmepedia/eu-cosmetic-ingredient-regulations)
