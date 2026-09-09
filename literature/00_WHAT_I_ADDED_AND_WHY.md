# What I added to the dataset, in plain words

Lynne, MSc thesis, Beirut Arab University

My dataset started with 42 columns. It now has **111**. This document explains
every group of new columns: what the word means, one real example from my own
data, and **where the rule came from**, with a link.

I also grade every rule honestly, because my supervisor will ask "are you sure
about this?" and the truthful answer is different for different columns.

---

# CONTENTS

1. First, the one rule that makes all of this possible
2. How to read the grade next to every column
3. The 12 groups of columns, one by one
4. Two full worked examples
5. Three things I could not do, and why
6. Five mistakes I found and fixed
7. Short dictionary of every term
8. All sources in one list

---

# 1. First, the one rule that makes all of this possible

Every one of these columns is read out of the **ingredient list** printed on
the back of the box. In the industry that list is called the **INCI list**.

Two facts about that list do the heavy lifting.

**Fact one: the order is not random.** EU law says ingredients must be listed
from most to least. Below 1% the order stops mattering, so anything after the
1% mark can be in any order.

> "The list of ingredients shall be established in descending order of weight
> of the ingredients at the time they are added to the cosmetic product.
> Ingredients in concentrations of less than 1 % may be listed in any order."

That is [Regulation (EC) No 1223/2009, Article 19(1)(g)](https://www.legislation.gov.uk/eur/2009/1223/article/19). This is **law**, not
an opinion.

**Why I care:** if I see RETINOL at position 4 out of 8, it is a real dose. If
I see it at position 34 out of 40, it is nearly nothing. That is where my
`lead_active_position` column comes from.

**Fact two: nano ingredients must be labelled.** The same article says
nanomaterials must be followed by the word "(nano)" in brackets. So I can
detect them by looking for that exact bracket.

**What this means for the thesis:** I am not guessing. I am reading a
legally-mandated, legally-ordered document. My supervisor can verify any single
cell by picking up the physical product.

**I did no new scraping for any of this.** No API calls, nothing bought. It is
all squeezed out of data I already had.

---

# 2. How to read the grade next to every column

This is the honest part. Not all 69 columns rest on the same quality of
evidence. So every group below carries one of four grades.

| Grade | What it means | Can my supervisor challenge it? |
|---|---|---|
| **A — Law** | An EU regulation with an article number | No. It is legislation |
| **B — Published science** | A named paper in a named journal | Only on interpretation |
| **C — Industry practice** | What the cosmetic analysis sites do. No single paper behind it | Yes, and fairly |
| **D — My own rule** | I invented it for convenience | Yes. It is a label, not a finding |

**If you only remember one thing:** grades A and B are defensible in a viva.
Grade C is common practice that I should describe as common practice. Grade D
I should call a convenience label and not defend as science.

Rough split: **A covers 9 columns, B covers 21, C covers 26, D covers 13.**

---

# 3. The groups, one by one

## Group 1. Allergy and dietary avoidance
### Grade A for the allergen link, Grade C for the rest

**Columns:** `contains_animal_derived`, `contains_tree_nut`,
`contains_gluten_grain`, `contains_soy`, `contains_coconut`, plus an
`_evidence` column for each.

**What it means:** the product contains something from an animal, or something
a person with a nut, gluten or soy issue may want to avoid.

**Real example.** A product with CERA ALBA in the list gets
`contains_animal_derived = yes` and the evidence cell says `CERA ALBA`. Cera
alba is the Latin INCI name for beeswax.

**Where it comes from.** The names themselves are legally controlled. The EU
publishes **CosIng**, the official ingredient database, and my dataset is
already matched to it for 99.2% of products with an ingredient list. Latin
plant and animal names in INCI are not free text.

**Numbers:** animal 1,641 (13.0%), tree nut 1,243 (9.8%), gluten grain 861
(6.8%), soy 815 (6.5%), coconut 2,778 (22.0%).

**Related and stronger: the fragrance allergen list.** This is Grade A and it
is a real opportunity for my thesis. EU law used to require 26 named fragrance
allergens to be declared. That changed. [Commission Regulation (EU) 2023/1545](https://eur-lex.europa.eu/eli/reg/2023/1545/oj/eng)
expanded the list from 26 to **over 80 substances**, adding 56 new ones. The
deadlines are **31 July 2026** and **31 July 2028**.

**Say this to my supervisor:** the allergen rules are changing right now, in
the same year I am submitting. No skincare ontology in my literature review
has the new list. That is a live gap, not a historical one.

---

## Group 2. Malassezia, also called fungal acne
### Grade B, but with an honest warning

**Columns:** `feeds_malassezia`, `malassezia_evidence`.

**What the word means.** Malassezia is a **yeast that lives on everybody's
skin**. It is normal. In some people it overgrows and causes small itchy bumps
that look like acne but are not acne. Online people call it "fungal acne". The
medical names are pityrosporum folliculitis and seborrhoeic dermatitis.

**Why an ingredient can make it worse.** This is the good part, and it is real
biology. Malassezia **cannot make its own fatty acids**. It is missing the
genes for it. So it has to eat fatty acids from its surroundings, and it
secretes lipases to break down oils and get them.

Which fatty acids? Ones roughly **11 to 24 carbon atoms long**, with the best
documented feeding around C16 to C18.

**Source:** ["Lipid-dependent growth of Malassezia spp. in defined medium with single fatty acids", FEMS Yeast Research, 2025](https://academic.oup.com/femsyr/article/doi/10.1093/femsyr/foaf043/8239275). Open access copy on [PubMed Central](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12416284/).

**Real example.** The Ordinary Retinol 0.2% in Squalane gets
`feeds_malassezia = yes`, evidence `CAPRYLIC/CAPRIC TRIGLYCERIDE`. That
ingredient is a C8 to C10 oil, so honestly this one is borderline and sits at
the edge of the range.

**My honest warning.** 7,093 products, **56.2%**, come out as yes. That is
more than half the catalogue, which tells you the flag is broad. The
underlying biology is solid, but the exact list of which cosmetic ingredients
matter in a real formula, at real concentrations, is **not settled science**.
SkinCarisma, the site most people use for this, says so itself.

**What I will say in the viva:** the mechanism is published and I cite it. The
ingredient list is a screening heuristic. It should be shown to a user as
"contains ingredients some people avoid", not as "this will break you out".

---

## Group 3. Comedogenic, meaning pore-clogging
### Grade B for the concept, Grade C for the list, and the science is contested

**Columns:** `contains_comedogenic`, `comedogenic_evidence`.

**What the word means.** Comedogenic means an ingredient tends to block a pore
and form a comedone, which is the blackhead or whitehead that starts acne.

**Where this whole idea came from, and this is a good story for the viva.**

In **1972** two dermatologists, **Albert Kligman and Otto Mills**, published a
paper called *Acne Cosmetica*. They noticed adult women getting closed
comedones and blamed their cosmetics. To test ingredients, researchers then
developed the **rabbit ear assay**: paint the substance inside the ear of an
albino rabbit for two to four weeks, then look at the skin under a microscope
and count the comedones. The big published ingredient tables everyone still
quotes come from this. See [Kligman's 1984 ratings of therapeutic products, cosmetics and ingredients in the rabbit ear, JAAD](https://www.jaad.org/article/S0190-9622(84)80050-X/abstract).

**Here is the problem, and I should say it out loud.** In 1982 Kligman himself
tested the same chemicals **on humans** and found that some strong comedogens
in rabbits produced little or no comedones in people. The rabbit model is
**oversensitive**. There is a full re-evaluation of the concept in [JAAD, 2005](https://www.jaad.org/article/S0190-9622(05)04600-1/abstract), and a
[2025 clinical review in JAAD Reviews](https://www.jaadreviews.org/article/S2950-1989(25)00088-1/fulltext)
specifically about the regulatory gaps.

**Number:** 1,991 products, 15.8%.

**Say this to my supervisor:** "the comedogenic ratings everybody uses come
from rabbit ears in the 1970s and 80s, the man who invented the method showed
himself in 1982 that it overpredicts in humans, and I am labelling my column
accordingly." That sentence alone shows I read past the surface.

---

## Group 4. Barrier repair
### Grade B, and this is my strongest scientific column

**Columns:** `supports_barrier_repair`, `barrier_repair_evidence`,
`contains_ceramide`.

**What "barrier" means.** The outermost layer of skin, the stratum corneum, is
often described as a brick wall. The dead skin cells are the bricks, and a
mortar of fats holds them together. That mortar keeps water in and irritants
out. When it is damaged, skin stings, flakes and reacts to everything.

**What the mortar is made of.** Three lipids: **ceramides, cholesterol and
free fatty acids**.

**The published finding.** Work by **Peter Elias and colleagues at UCSF**
showed that if you apply only one or two of these lipids to damaged skin, you
**delay** recovery. Only a complete mixture allows normal repair. And repair
gets faster when one of the three is increased up to threefold, which is where
the famous **3:1:1 ratio** comes from.

**Source:** [Man, Feingold, Thornfeldt and Elias, "Optimization of Physiological Lipid Mixtures for Barrier Repair", Journal of Investigative Dermatology](https://www.sciencedirect.com/science/article/pii/S0022202X15425643), and the follow-up on aged skin in [JAAD](https://www.sciencedirect.com/science/article/abs/pii/S0190962297701403).

**Real example.** CeraVe Moisturising Face Lotion SPF30 gets
`supports_barrier_repair = yes`, evidence `NIACINAMIDE`.

**Numbers:** barrier repair 5,690 (45.1%), ceramide specifically 1,064 (8.4%).

**Where I should be careful.** My marker list is wider than the three lipids.
I also count niacinamide, panthenol, centella and squalane, which are
supported but are soothing agents rather than barrier lipids. **A stricter
version of this column that only counts the three Elias lipids would be more
precise**, and it is an easy improvement if a supervisor pushes.

---

## Group 5. Retinoids, night use and layering conflicts
### Grade B

**Columns:** `contains_retinoid`, `retinoid_evidence`, `use_time`,
`do_not_layer_with`, `may_cause_purging`, `purging_evidence`.

**What a retinoid is.** A vitamin A derivative. It speeds up how fast skin
cells turn over. It is the single best-evidenced anti-ageing ingredient there
is, and also the most irritating.

**Why night only.** Retinoids break down in light. When retinoid compounds are
hit by UV they isomerise and oxidise, which destroys the molecule and its
function. One study found isotretinoin drops significantly after roughly one
hour's worth of sunlight exposure.

**Source:** [Photostability of Topical Agents Applied to the Skin: A Review, Pharmaceutics 12(1):10, MDPI, 2020](https://www.mdpi.com/1999-4923/12/1/10).

**What "purging" means.** When you start a retinoid or an acid, skin can look
**worse for four to eight weeks** before it gets better, because everything
already forming under the surface is being pushed up faster. It is not an
allergic reaction and it is not the product failing. Users quit at week three
because nobody told them. That is exactly the sort of thing a recommender
should say.

**Real example.** The Ordinary Retinol 0.2% in Squalane:
`use_time = night only`, `may_cause_purging = yes` with evidence `RETINOL`,
and `do_not_layer_with = acids (AHA, BHA) and vitamin C, on the same night`.

**Numbers:** retinoid 681 (5.4%), purging 2,510 (19.9%), layering warning
3,002 (23.8%).

---

## Group 6. Exfoliating acids
### Grade C, with one important correction

**Columns:** `contains_aha`, `aha_evidence`, `contains_bha`, `bha_evidence`,
`contains_pha`.

**The terms.**

| Term | Full name | In one line |
|---|---|---|
| **AHA** | alpha hydroxy acid | Water-loving. Works on the surface. Glycolic, lactic |
| **BHA** | beta hydroxy acid | Oil-loving, so it gets down inside a pore. Salicylic |
| **PHA** | poly hydroxy acid | Bigger molecule, goes in slower, gentler. Gluconolactone |

**The correction, and this one matters.** My first version counted **citric
acid** as an AHA. Technically it is one. But in practice it is in almost every
formula as a **pH adjuster**, at a level that does nothing to exfoliate.
Counting it would have wrongly labelled **2,842 products** as exfoliants. I
took it out. The AHA count dropped from 4,096 to **1,254**.

**Numbers:** AHA 1,254 (9.9%), BHA 1,026 (8.1%), PHA 409 (3.2%).

---

## Group 7. Mature skin
### Grade C, and I think this column is too generous

**Columns:** `suits_mature_skin`, `mature_skin_evidence`.

**What "mature skin" actually means**, because a friend asked me this and I
did not have a clean answer.

It is a **trade term, not a medical diagnosis**. There is no age at which it
switches on. It describes skin that has lost collagen and lipids over time, so:

- fine lines and loss of firmness, because collagen production slows
- **drier**, because oil production drops after menopause
- slower cell turnover, so it looks duller and heals slower
- more uneven pigment from accumulated sun exposure
- thinner and more fragile

**The practical difference:** a product for oily acne-prone skin and a product
for mature skin can target the same concern and need completely opposite
bases. Mature skin usually needs the richer base.

**Real example.** CeraVe Moisturising Face Lotion gets `suits_mature_skin =
yes` on evidence `NIACINAMIDE`.

**My honest problem with this column.** 4,802 products, **38.0%**, say yes.
That is too many to be useful as a filter, and the reason is that I included
**niacinamide**, which is in a huge number of products. A stricter version
counting only retinoids, peptides and vitamin C would give a smaller and much
more meaningful number. **I would flag this myself before a supervisor finds
it.**

---

## Group 8. EU regulatory watch
### Grade A. This is the strongest group in the whole dataset

**Columns:** `contains_nanomaterial`, `contains_solid_microplastic`,
`contains_synthetic_polymer`, `contains_endocrine_concern`, `contains_pfas`,
plus evidence columns.

**Why this group is special.** These are not opinions or industry habits.
These are **named EU regulations**, several of which land in 2026 and 2027,
which is exactly when I submit. **Not one paper in my literature review has
this.**

| Column | The law | What it does |
|---|---|---|
| `contains_nanomaterial` | [1223/2009 Art. 19(1)(g)](https://www.legislation.gov.uk/eur/2009/1223/article/19) | Nano ingredients must be labelled "(nano)". I detect the bracket |
| `contains_solid_microplastic` | Regulation (EU) 2023/2055 | Restricts **solid** synthetic polymer microparticles |
| `contains_endocrine_concern` | Ongoing SCCS review and restriction | Substances under active EU review as endocrine disruptors |
| `contains_pfas` | Proposed EU-wide restriction | The "forever chemicals" |

**The correction I had to make.** My first version counted **carbomer** as a
microplastic and got 3,125 hits, of which 1,930 were carbomer. That is wrong.
Carbomer is a **swollen gel, not a solid bead**, and 2023/2055 restricts solid
particles. So I split the column in two:

- `contains_solid_microplastic` = **589** (4.7%). Actually in scope of the law
- `contains_synthetic_polymer` = **3,166** (25.1%). Broader, informational only

**Numbers:** nano 101 (0.8%), solid microplastic 589 (4.7%), synthetic polymer
3,166 (25.1%), endocrine concern 1,582 (12.5%), PFAS 51 (0.4%).

---

## Group 9. Sunscreen chemistry
### Grade C for the classification, Grade B for the reef flag

**Columns:** `sunscreen_filter_type`, `contains_reef_harmful_uv`,
`reef_harmful_evidence`, `white_cast_risk`.

**The terms.** A **mineral** filter, zinc oxide or titanium dioxide, sits on
top and reflects. A **chemical** filter, like avobenzone, absorbs UV and turns
it into heat. **Hybrid** means both.

**White cast** is the grey film mineral sunscreens can leave. It shows more on
deeper skin tones. It is the single biggest reason people stop wearing
sunscreen, so it belongs in a recommender.

**Reef harmful** flags oxybenzone and octinoxate, which are banned in Hawaii,
Palau and Key West.

**Numbers:** filter type on 1,883 products (14.9%), reef harmful 747 (5.9%),
white cast risk 1,056 (8.4%).

---

## Group 10. Formula shape
### Grade C

**Columns:** `formula_base`, `moisturiser_type`, `preservative_system`,
`texture`, `contains_fragrance`, `contains_essential_oil`,
`contains_drying_alcohol`.

**The terms that matter.**

**Water-based versus anhydrous.** Anhydrous means no water. This is not
trivia: **anything with water needs a preservative**, and anything without
water usually does not. It is also why an anhydrous oil and a water serum
behave differently when layered.

**Moisturiser type.** A **humectant** draws water in, like glycerin or
hyaluronic acid. An **occlusive** seals water in, like petrolatum. "Draws and
seals" means the formula does both, which is what a good moisturiser should
do. In dry winter air a humectant with nothing sealing it can actually pull
water **out** of the skin.

**Drying alcohol, and a correction.** My first version counted **cetearyl
alcohol** as a drying alcohol. That is wrong. Cetearyl, cetyl and stearyl are
**fatty alcohols**, which are waxy and conditioning, the opposite of drying.
Only alcohol denat, SD alcohol and ethanol count. The number fell from 1,503
to **826**.

**Real example.** CeraVe: `formula_base = water-based`, `moisturiser_type =
draws and seals`, `preservative_system = Organic acid, Glycol or alcohol`,
`texture = lotion`. The Ordinary retinol: `formula_base = anhydrous`,
`preservative_system = none detected`, which is correct and expected for an
oil.

**Numbers:** fragrance 5,047 (40.0%), essential oil 1,888 (14.9%), drying
alcohol 826 (6.5%), texture 7,432 (58.8%).

---

## Group 11. Routine placement
### Grade D. My own rules

**Columns:** `routine_step`, `body_site`, `use_time`, `strength_level`,
`regional_style`, `price_band_lebanon`.

**What they do.** `routine_step` puts each product in order, so "1 Cleanse"
through "7 Protect". `strength_level` says beginner, intermediate or advanced.
`regional_style` marks Korean, French pharmacy, Lebanese local and so on.

**I am being straight here: I invented these.** There is no standard behind
them. They are convenience labels that make the recommender usable. They are
**not findings** and I will not defend them as science. If asked, the correct
answer is "these are presentation rules I defined, and they are documented in
the script".

`routine_step` and `body_site` are on 100% of products.
`price_band_lebanon` is on 92.6%, and that one is grounded in my own real
price data, so it is stronger than the rest of this group.

---

## Group 12. Brand ownership
### Grade B. Verifiable public fact

**Column:** `brand_parent_company`.

Kenvue owns Neutrogena. L'Oreal owns CeraVe. Unilever owns Paula's Choice.
These are checkable against company annual reports.

**Why it is useful:** it shows how concentrated my catalogue really is, and it
lets any brand-level question be answered later without touching the dataset.

**Coverage is only 3,109 products, 24.6%.** This is the weakest coverage of
any column I kept. Wikidata has a `parent organization` property that would
raise it a lot in one pass. That is already on my Sprint 2 list.

*(Note: I built and then removed a boycott-listing feature. The published BDS
priority list matched only 2 of my 12,629 products, so it was not worth a
column. The parent company data survived because it is useful on its own.)*

---

# 4. Two full worked examples

## Example A. CeraVe Moisturising Face Lotion SPF30 AM, 52ml

40 ingredients. Here is what the system now knows without anyone typing
anything:

| Column | Value | Read it as |
|---|---|---|
| `formula_base` | water-based | Has water, so needs preservative |
| `preservative_system` | Organic acid, Glycol or alcohol | And it has one |
| `moisturiser_type` | draws and seals | Humectant plus occlusive. A proper moisturiser |
| `contains_ceramide` | yes | The brand's whole selling point, confirmed from the actual list |
| `supports_barrier_repair` | yes, via NIACINAMIDE | Good for damaged, stinging skin |
| `suits_mature_skin` | yes, via NIACINAMIDE | But see my warning in Group 7 |
| `feeds_malassezia` | yes, via ISOPROPYL PALMITATE | Fungal acne sufferers should skip it |
| `contains_comedogenic` | yes, via ISOPROPYL PALMITATE | Same ingredient, two different flags |
| `contains_fragrance` | no | Safe for the fragrance-sensitive |
| `routine_step` | 6 Moisturise | Where it goes |
| `use_time` | morning | It has SPF |
| `strength_level` | intermediate | |
| `actives_present` | niacinamide | |
| `lead_active_position` | niacinamide at position 6 | Position 6 of 40, so a real dose, not a sprinkle |

**Notice the useful tension.** This is a barrier-repair product that is also
flagged for fungal acne, and both flags point at the same single ingredient,
isopropyl palmitate. A keyword search would never surface that. A rule over a
structured ingredient list does.

## Example B. The Ordinary Retinol 0.2% in Squalane

Only 8 ingredients.

| Column | Value | Read it as |
|---|---|---|
| `formula_base` | anhydrous | No water |
| `preservative_system` | none detected | Correct. No water means no preservative needed |
| `contains_retinoid` | yes, RETINOL | |
| `use_time` | **night only** | Retinol degrades in UV. Source in Group 5 |
| `may_cause_purging` | yes, RETINOL | Warn the user it may get worse for 4 to 8 weeks |
| `do_not_layer_with` | acids (AHA, BHA) and vitamin C, same night | The conflict warning |
| `strength_level` | advanced, patch test first | |
| `suits_mature_skin` | yes, RETINOL | This time on strong evidence, unlike Example A |
| `lead_active_position` | retinol at position 4 | Position 4 of 8. Genuinely concentrated |
| `supports_barrier_repair` | yes, SQUALANE | The squalane in the name |

**Why this example is worth showing.** Four of these columns are safety
information a shopper actually needs and will not find on the box: do not use
in daylight, do not combine with acids tonight, expect it to look worse first,
patch test. That is what an ontology is for.

---

# 5. Three things I could not do, and why

My supervisor suggested pulling organic, cruelty free and vegan from what I
already had. I tried, and I want to be clear about why it failed, because the
failure is itself worth writing up.

**First I tried mining the text.** My `product_summary` column looked
promising. It is not. It turns out to be **self-generated boilerplate**, the
same phrases repeated. Searching it for "cruelty free" returned **16 products
out of 12,629**. That is noise, not a signal.

**Then I understood why it can never work from ingredients.**

| Claim | Why the INCI list cannot tell you |
|---|---|
| **Cruelty free** | It is about whether the finished product or its ingredients were **tested on animals**. That is a fact about a company's process, not about a molecule. Two identical formulas can differ |
| **Organic** | It is about **how the plant was farmed**. Organic and conventional lavender oil have the exact same INCI name |
| **Vegan** | Closer, since I can detect animal-derived ingredients. But absence of evidence is not evidence of absence. I can prove a product **is not** vegan. I cannot prove it **is** |

**The rule I followed everywhere: positive detection only.** I say what IS
present. I never claim something is absent, because an ingredient list I
failed to parse looks identical to a clean formula.

**This is the right answer, not a cop-out.** All three of these are
**certifications by an external body**, which is a completely different kind
of information from an ingredient. The correct way to model them is as a claim
by a named certifier with a date, not as a property of the product.

---

# 6. Five mistakes I found and fixed

I want these in the document because "I tested it and found my own errors" is
a stronger thing to say than "it worked first time".

| # | The mistake | How I found it | The fix |
|---|---|---|---|
| 1 | **Synthetic beeswax** counted as animal-derived, 43 products | Read random matches by eye | Added an exclusion list: synthetic, vegetal, biomimetic, vegan |
| 2 | **Cetearyl alcohol** counted as drying alcohol | Same | Excluded fatty alcohols. 1,503 down to 826 |
| 3 | **Citric acid** counted as exfoliating AHA | Count looked far too high | Removed it. Would have mislabelled **2,842 products**. 4,096 down to 1,254 |
| 4 | **Carbomer** counted as a solid microplastic, 1,930 of 3,125 hits | Read the regulation properly | Split into two columns. 589 in scope, 3,166 informational |
| 5 | **The script silently died.** It recompiled the same patterns for every ingredient of every product, roughly 40 million times | It just never finished | Cached the compiled patterns. Minutes down to 8 seconds |

**The method that caught all five:** after every rule, pull random matching
products and read them. Four of the five would have survived any amount of
code review, because the code was correct. The **rule** was wrong.

---

# 7. Short dictionary

| Term | Plain meaning |
|---|---|
| **INCI** | International Nomenclature of Cosmetic Ingredients. The standard naming system. Why every box says "Aqua" not "water" |
| **CosIng** | The European Commission's official cosmetic ingredient database |
| **Anhydrous** | Contains no water |
| **Humectant** | Draws water into skin. Glycerin, hyaluronic acid |
| **Occlusive** | Seals water in. Petrolatum, dimethicone |
| **Comedone** | A blocked pore. A blackhead or whitehead |
| **Comedogenic** | Tends to block pores |
| **Malassezia** | A yeast that lives on normal skin. Can overgrow into itchy bumps |
| **Stratum corneum** | The outermost layer of skin. The "barrier" |
| **Ceramide** | One of the three fats that hold the barrier together |
| **Retinoid** | A vitamin A derivative. Speeds cell turnover |
| **Purging** | Skin temporarily worsening when starting a retinoid or acid. 4 to 8 weeks |
| **AHA / BHA / PHA** | Three families of exfoliating acid. Water-loving, oil-loving, gentle |
| **Mature skin** | Trade term for skin that has lost collagen and lipids. Not an age |
| **Fatty alcohol** | Waxy and conditioning. The opposite of drying alcohol despite the name |
| **Nanomaterial** | Particles small enough that EU law requires "(nano)" on the label |
| **Fragrance allergen** | One of the substances EU law requires to be named separately. Was 26, now over 80 |
| **SCCS** | Scientific Committee on Consumer Safety. The EU's expert advisory body |

---

# 8. All sources in one list

**Law, Grade A**

1. [Regulation (EC) No 1223/2009, Article 19](https://www.legislation.gov.uk/eur/2009/1223/article/19). Ingredient order, the 1% rule, nano labelling
2. [Commission Regulation (EU) 2023/1545](https://eur-lex.europa.eu/eli/reg/2023/1545/oj/eng). Fragrance allergens from 26 to over 80. Deadlines 31 July 2026 and 31 July 2028
3. Regulation (EU) 2023/2055. Solid synthetic polymer microparticles
4. CosIng, the European Commission ingredient database. Already linked for 99.2% of my products with an ingredient list

**Published science, Grade B**

5. [Lipid-dependent growth of Malassezia spp. in defined medium with single fatty acids, FEMS Yeast Research, 2025](https://academic.oup.com/femsyr/article/doi/10.1093/femsyr/foaf043/8239275) ([PMC copy](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12416284/))
6. Kligman and Mills, *Acne Cosmetica*, 1972. The origin of the whole comedogenic idea
7. [Comedogenicity of current therapeutic products, cosmetics, and ingredients in the rabbit ear, JAAD, 1984](https://www.jaad.org/article/S0190-9622(84)80050-X/abstract)
8. [A re-evaluation of the comedogenicity concept, JAAD, 2005](https://www.jaad.org/article/S0190-9622(05)04600-1/abstract)
9. [Comedogenicity in cosmeceuticals: clinical relevance, regulatory gaps and future directions, JAAD Reviews, 2025](https://www.jaadreviews.org/article/S2950-1989(25)00088-1/fulltext)
10. [Man, Feingold, Thornfeldt and Elias, Optimization of Physiological Lipid Mixtures for Barrier Repair, Journal of Investigative Dermatology](https://www.sciencedirect.com/science/article/pii/S0022202X15425643)
11. [Optimal ratios of topical stratum corneum lipids improve barrier recovery in chronologically aged skin, JAAD](https://www.sciencedirect.com/science/article/abs/pii/S0190962297701403)
12. [Photostability of Topical Agents Applied to the Skin: A Review, Pharmaceutics 12(1):10, 2020](https://www.mdpi.com/1999-4923/12/1/10)

**Industry practice, Grade C.** Named honestly as practice, not as science.

13. SkinCarisma. Malassezia, comedogenic, silicone, alcohol and allergen flags
14. CosDNA. Comedogenic and irritancy ratings
15. SkinSort and EWG. The "free from" vocabulary consumers expect

**Grade D.** My own rules: `routine_step`, `body_site`, `strength_level`,
`regional_style`, `texture` and the presentation labels. Documented in
`FINAL_PIPELINE/add_derived_attributes.py`. Convenience labels, not findings.

---

# The one paragraph version

I did not invent a vocabulary. I took the properties that the cosmetic
analysis sites already flag, added the EU regulations that land in 2026 and
2027, and derived all of them from the legally ordered ingredient list I
already had. Where a real published paper backs a rule, I cite it. Where only
industry practice backs it, I say so. Where I made the rule up, I say that
too. Every flag carries an evidence cell naming the exact ingredient that
triggered it, so any single value can be checked by hand in a few seconds.

**42 columns to 111. 12,629 rows unchanged. Zero original cells altered.**
