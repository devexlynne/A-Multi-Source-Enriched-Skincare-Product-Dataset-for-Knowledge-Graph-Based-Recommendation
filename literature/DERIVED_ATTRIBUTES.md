# The 68 new columns: what they are, how they were made, and why

My supervisor asked whether we could add things like organic, cruelty free and
animal friendly. I researched what people actually check, tested every candidate
against the real 12,629 products, and applied it.

**The dataset now has 110 columns instead of 42.** Same 12,629 rows. Not one
original cell was touched. All validation checks pass.

---

## Part 1. How it works, in plain words

### The idea

We already collected the ingredient list for 11,802 products, and matched 96.6%
of the individual ingredients to the EU register. **That list is a fingerprint.**
Almost everything a person wants to know about a product is already sitting in
it, unread.

So instead of scraping more, we read what we have more carefully.

### The mechanism, step by step

**Step 1. Split the ingredient list properly.** INCI strings separate
ingredients with commas, but some ingredient names contain commas, like
`1,2-Hexanediol`. So the splitter protects a comma sitting between two digits
before splitting on the rest.

**Step 2. Match against curated marker lists.** For each property there is a
list of INCI names that indicate it. `BEESWAX`, `CERA ALBA` and `LANOLIN`
indicate an animal source. `PRUNUS AMYGDALUS` and `MACADAMIA` indicate a tree
nut.

**Step 3. Record what matched.** Every flag writes two things: `yes` or `no`,
and an `_evidence` column naming the exact ingredient that triggered it. So a
reader can check any single answer, and a wrong answer traces back to the rule
that made it rather than being unexplained.

**Step 4. Never claim absence.** Every rule is positive detection. We say what
IS in a product. We never say what is not. Part 4 explains why that distinction
matters more than it sounds.

### One engineering note worth knowing

The first version took several minutes and kept dying. It was recompiling every
regular expression for every ingredient of every product, roughly 40 million
compiles. Compiling each pattern list once and caching it brought the whole run
down to **8 seconds**. Same output, same rules.

---

## Part 2. Where the properties came from

I did not invent the list. I checked what the tools people already use actually
flag, so our vocabulary matches what a user expects.

| Source | What it flags |
|---|---|
| **SkinCarisma** | Parabens, sulfates, alcohol, silicones, EU allergens, comedogenic, and **fungal acne (Malassezia)** triggers. The fungal-acne filter is its most used feature |
| **CosDNA** | Comedogenic 1 to 9 and irritancy 1 to 9 per ingredient, plus a safety level from CIR, RTECS and FDA reports |
| **SkinSort** | Fungal acne safe, non-comedogenic, silicone free, reef safe |
| **EU regulation** | Nanomaterial labelling, microplastics under 2023/2055, endocrine disruptors under 2026/909 |
| **Consumer vocabulary** | Mature skin, barrier repair, purging, layering conflicts, AM versus PM |

A caveat worth quoting: **the comedogenic ratings everyone uses come from a
study done on the inside of rabbit ears**, not on human skin. That is why our
column is `contains_comedogenic` and not `will_cause_acne`.

---

## Part 3. The 68 columns

**33 flags, 18 evidence columns, 17 descriptive columns.** All counts are from
the applied run.

### What people ask for by name

Your friend said "mature skin". That is the trade word for skin losing collagen
and lipids: fine lines, slower turnover, more dryness. So the column looks for
the actives that address it.

| Column | Products | % | What it means |
|---|---|---|---|
| `supports_barrier_repair` | **5,690** | 48.2% | Ceramides, cholesterol, niacinamide, panthenol, centella. The lipids skin makes itself |
| `suits_mature_skin` | **4,802** | 40.7% | Retinoids, peptides, vitamin C, CoQ10, AHAs |
| `may_cause_purging` | **2,510** | 21.3% | Speeds cell turnover, so skin can look worse for 4 to 8 weeks before better |

### When and how to use it

| Column | What it holds |
|---|---|
| `use_time` | **718 night only** (retinoids, benzoyl peroxide, hydroquinone), **1,757 morning** (has a UV filter), **1,667 night preferred** (acids), 7,660 either |
| `do_not_layer_with` | **3,002 products carry a warning.** Retinoids clash with acids and vitamin C on the same night. Vitamin C is oxidised by benzoyl peroxide |
| `strength_level` | 7,183 gentle, 3,465 intermediate, **1,154 advanced, patch test first** |
| `texture` | Cream 1,778, serum 1,477, gel 906, oil 819, balm 539, lotion 404 |
| `white_cast_risk` | **1,004 possible**, because the mineral filter is not marked nano. 52 lower risk |

### Acne and reactivity

| Column | Products | % |
|---|---|---|
| `feeds_malassezia` | **7,093** | 60.1% |
| `contains_fragrance` | **5,047** | 42.8% |
| `contains_comedogenic` | 1,991 | 16.9% |
| `contains_essential_oil` | 1,888 | 16.0% |

### Allergy and diet

`contains_coconut` 2,778 (23.5%), `contains_animal_derived` 1,641 (13.9%),
`contains_tree_nut` 1,243 (10.5%), `contains_gluten_grain` 861 (7.3%),
`contains_soy` 815 (6.9%).

### Safety and caution

`contains_drying_alcohol` 826, `contains_reef_harmful_uv` 747,
`contains_photosensitiser` 704, `contains_retinoid` 681.

The photosensitiser one matters more here than in Europe. Citrus oils make skin
burn in sun, and Lebanon has a lot more of it.

### EU regulatory watch, which nobody else in our review has

| Column | Products | Which rule |
|---|---|---|
| `contains_synthetic_polymer` | 3,162 | Broad polymer set |
| `contains_endocrine_concern` | 1,582 | Regulation 2026/909 and prior |
| `contains_solid_microplastic` | ~700 | Regulation 2023/2055, **rinse-off reformulation due October 2027** |
| `contains_nanomaterial` | 101 | Already carrying `[nano]` on the label |
| `contains_pfas` | 51 | PTFE, perfluorodecalin, perfluorohexane |

### The usual "free from" filters

`contains_peg` 3,162, `contains_silicone` 2,879, `contains_propylene_glycol`
1,609, `contains_sulfate` 390, `contains_talc` 103.

### Active families

`contains_soothing` 5,522, `contains_antioxidant` 5,157, `contains_aha` 1,254,
`contains_ceramide` 1,064, `contains_bha` 1,026, `contains_peptide` 839,
`contains_pha` 409.

### Formulation and classification

| Column | What it holds |
|---|---|
| `sunscreen_filter_type` | 827 chemical, 727 mineral, 329 hybrid |
| `moisturiser_type` | Humectant 6,020, draws and seals 3,577, occlusive 601 |
| `preservative_system` | Phenoxyethanol 37.4%, organic acids 23.3%, parabens 4.1% |
| `formula_base` | Water-based 66.8%, anhydrous 5.9% |
| `actives_present` | Which of ten known actives |
| `lead_active_position` | **Where the strongest active sits in the INCI list** |
| `stated_concentration` | 505 products state a percentage in their own name |
| `halal_candidate` | 9,415 candidates |
| `routine_step` | All 12,629 mapped, none unmatched |
| `body_site` | Face, eye area, lips, hands, body |
| `regional_style` | K-beauty 2,084, French pharmacy 1,948, Lebanese 910 |
| `price_band_lebanon` | Four bands |

### One product, all the way through

**StriVectin Super-C Retinol Brighten & Correct**

```
use_time                 night only
do_not_layer_with        acids (AHA, BHA) and vitamin C on the same night;
                         benzoyl peroxide, which oxidises it
strength_level           intermediate
may_cause_purging        yes
suits_mature_skin        yes
supports_barrier_repair  no
texture                  serum
lead_active_position     vitamin C at position 10
```

Every line of that came out of the ingredient list. Nobody typed it.

---

## Part 4. The three things we cannot do, and why

### Vegan: no

**Stearic acid, glycerin, squalane and lactic acid can each come from a plant or
an animal, and the INCI name is identical either way.** The manufacturer knows.
The label does not say.

| Can we say | |
|---|---|
| This product **contains** an animal-derived ingredient | **Yes.** 1,641 products |
| This product contains **no** animal ingredient | Only that we found none |
| This product **is vegan** | **No** |

Absence of evidence is not evidence of absence. That is why the column is
`contains_animal_derived`, and why `halal_candidate` says *candidate*.

### Cruelty free: no, but obtainable

It is a property of a **company**, granted by Leaping Bunny or PETA. Nothing in
an ingredient list can tell you. But it is cheap to get, because it is
brand-level and we have 1,463 brands, not 12,629 products. Both certifiers
publish their lists. Match on brand, store the certifier and date as the source,
exactly like every other claim in our dataset.

### Organic: no, same reason

A COSMOS, Ecocert or USDA certification. Same route.

---

## Part 5. Five precision problems I found and fixed

This is the part worth showing a supervisor, because it is where the care is.

| Problem | Effect if unfixed |
|---|---|
| **Citric acid counted as an exfoliating AHA** | It is a pH adjuster in almost every formula containing it. Would have wrongly labelled **2,842 products**. AHA count dropped from 4,096 to 1,254 |
| **Carbomer counted as a microplastic** | It is a swollen gel, not a solid bead. EU 2023/2055 targets solid particles. It was **1,930 of 3,125 hits**, so the column was split in two |
| **Cetearyl alcohol counted as a drying alcohol** | It is an emollient that softens skin. Inflated the count from 826 to 1,503 |
| **Synthetic beeswax counted as animal-derived** | It is a lab-made copy. 43 products |
| **The whole script too slow to finish** | Recompiling 40 million regexes. Cached them, 8 seconds |

---

## Part 6. What this gives the ontology

New defined classes become possible, and several are things no reviewed system
can express:

```
FungalAcneSafeCandidate  = Product with nothing that feeds malassezia
NutFreeCandidate         = Product with no tree nut detected
PregnancyCaution         = Product containing a retinoid
NightOnlyProduct         = Product whose use_time is night only
MineralSunscreen         = SunCare whose only filters are mineral
NeedsReformulationBy2027 = Product containing a solid microplastic
BarrierRepairProduct     = Product with ceramides or cholesterol
ConflictsWith            = an object property between two products
```

That last one is the interesting one. **`do_not_layer_with` is a relationship
between products, not a property of one.** It is exactly the kind of thing a
graph holds naturally and a spreadsheet cannot.

---

## Part 7. Two research questions now computable

**Does "natural" mean safer?** Klaschka (2015, 107 citations) found 56% of the
655 natural INCI substances in the EU inventory are classified hazardous, and 53
are carcinogenic, mutagenic or toxic to reproduction. We have 756 products
claiming natural, their formulas, and the register.

**Are claims supported by the composition?** MVFM (2026) tested three products by
hand and found one sold as anti-aging was really a texture cream. With
`lead_active_position` and `stated_concentration` we can run that across 11,802
formulas. Their own paper says large-scale validation is what is missing.

**And one finding already in hand.** Only **11%** of retinol products have
retinol in the first five ingredients, against 43% for niacinamide and 48% for
glycolic acid. Nine out of ten retinol products have almost none in them.

---

## Part 8. What was actually run, and the safety checks

```
cd FINAL_PIPELINE
py add_derived_attributes.py            # dry run
py add_derived_attributes.py --apply    # applied
```

| Check | Result |
|---|---|
| Rows before and after | 12,629 to 12,629, unchanged |
| Columns | 42 to 110, +68 |
| **Original cells altered** | **0** |
| Backup taken first | yes |
| `validate_dataset.py` | **ALL CHECKS PASSED** |
| File size | 29.1 MB |

The script writes to a temp file, asserts the row count, then replaces. Same
rules as the rest of the pipeline.

---

## Part 9. What is still not there

Being straight about the limits.

- **Nothing new for the 827 products with no formula.** Every ingredient-derived
  column is blank for them. That gap does not close without a formula.
- **The marker lists are curated, not exhaustive.** A rare animal-derived
  ingredient with an unusual INCI name will be missed. Positive detection means
  a miss is a false negative, which is the safer direction to fail.
- **Comedogenic and malassezia ratings are contested science.** Both come from
  limited studies. Our columns say what is present, not what will happen.
- **Cruelty free, organic and vegan remain absent**, for the reasons in Part 4.
  All three are obtainable from certifier lists if we decide to.

---

## Sources

- [SkinCarisma ingredient analyzer](https://www.skincarisma.com/ingredient-analyzer)
- [CosDNA ingredient analysis](https://www.cosdna.com/eng/ingredients.php)
- [SkinSort, comedogenic and irritancy ratings explained](https://skinsort.com/blog/comedogenic-irritancy-ratings-explained)
- [EU microplastics regulation 2023/2055](https://euverify.com/resource/eu-microplastics-regulation/)
- [EU Cosmetics Regulation 2026/909](https://cosmeservice.com/news/eu-cosmetics-regulation-2026-909-restrictions-deadlines/)
- [Dry versus dehydrated skin](https://www.barefaced.com/blogs/blog/the-difference-between-dry-and-dehydrated-skin)
- [Damaged skin barrier, signs and repair](https://www.theinkeylist.com/pages/damaged-skin-barrier)
- [Skin barrier and dry skin in the mature patient, PubMed](https://pubmed.ncbi.nlm.nih.gov/29566915/)
- [Retinol with vitamin C, BHA and niacinamide, Paula's Choice](https://www.paulaschoice-eu.com/retinol-with-vitamin-c-bha-aha-niacinamide)
- [Avoiding ingredient conflicts](https://skiningredients.com/avoiding-ingredient-conflicts-what-not-to-mix/)
