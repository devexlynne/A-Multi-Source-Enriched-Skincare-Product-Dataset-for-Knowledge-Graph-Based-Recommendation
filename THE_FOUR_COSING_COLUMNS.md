# The four CosIng columns, explained with one product

Four columns were added when the ingredients were matched against CosIng, the
European Commission's register of cosmetic ingredients. This page explains
what each one holds and then walks a single real product through all four.

---

## What the four columns hold

| column | what it is | example value |
|---|---|---|
| `cosing_matched` | how many of this product's ingredients were found in the EU register | `8` |
| `cosing_coverage` | that as a percentage of the whole formula | `100` |
| `ingredient_functions` | what the Commission says those ingredients **do** | `Skin Conditioning, Humectant, Fragrance, ...` |
| `restricted_ingredients` | which of them the regulation places a **limit** on | `Phenoxyethanol, Zinc Citrate` |

The first two are about **trust**. The last two are about **meaning**.

`cosing_matched` and `cosing_coverage` answer "how much of this formula do we
actually understand?" A product matched at 100% is fully accounted for. One
matched at 40% has more than half its formula unidentified, and any conclusion
drawn from it is weaker. Without these two, every product would look equally
reliable.

`ingredient_functions` and `restricted_ingredients` answer "what is in it, and
what does the law say?" They turn a line of free text into something a
computer can filter on and a person can be shown a reason from.

---

## One product, all the way through

**Revox B77, JUST 10% Niacinamide Daily Moisturiser**
Product `LBR-00114`, sold by zeinacare in Beirut for $8.83 (790,285 LBP).

Its ingredient list, exactly as printed:

```
ROSA DAMASCENA FLOWER WATER, NIACINAMIDE, PROPYLENE GLYCOL, ZINC CITRATE,
PHENOXYETHANOL, XANTHAN GUM, PPG-1-PEG-9 LAURYL GLYCOL ETHER, DISODIUM EDTA
```

Eight ingredients. Before today, that was a single string. A person could read
it. A computer could not do anything with it.

### Step 1: each ingredient is looked up in the register

| ingredient | EU ref | CAS | what the Commission says it does | limited? |
|---|---|---|---|---|
| ROSA DAMASCENA FLOWER WATER | 59340 | 90106-38-0 | **Fragrance**, skin conditioning, skin protecting | no |
| NIACINAMIDE | 35499 | 98-92-0 | Smoothing | no |
| PROPYLENE GLYCOL | 37269 | 57-55-6 | Humectant, skin conditioning, solvent | no |
| ZINC CITRATE | 80748 | 546-46-3 | Antiplaque, oral care | **yes, Annex III/24** |
| PHENOXYETHANOL | 36522 | 122-99-6 | Antimicrobial, preservative | **yes, Annex V/29** |
| XANTHAN GUM | 80699 | 11138-66-2 | Binding, emulsion stabilising, gel forming | no |
| PPG-1-PEG-9 LAURYL GLYCOL ETHER | 79934 | none listed | Surfactant, cleansing and emulsifying | no |
| DISODIUM EDTA | 33604 | 139-33-3 | Chelating, viscosity controlling | no |

### Step 2: that becomes the four columns

```
cosing_matched          8
cosing_coverage         100
ingredient_functions    Skin Conditioning, Viscosity Controlling,
                        Surfactant - Cleansing, Surfactant - Emulsifying,
                        Fragrance, Skin Protecting, Smoothing, Humectant
restricted_ingredients  Phenoxyethanol, Zinc Citrate
```

**8 of 8 found, so 100% coverage.** Nothing in this formula is unidentified.
Every claim made about this product rests on ingredients the Commission
recognises.

---

## What that buys, in four sentences

**1. A recommender can filter on it.** A customer avoiding fragrance can now
exclude this product, because the register says rose water carries a fragrance
function, whatever the marketing says.

**2. A recommendation can explain itself.** Instead of "we suggest this," the
system can say: it contains niacinamide, which the Commission records as
*smoothing*, and it is preserved with phenoxyethanol rather than a paraben.

**3. The confidence is visible.** `cosing_coverage = 100` means every
ingredient is accounted for. A product at 45% would be flagged as a weaker
basis for any claim.

**4. Regulatory questions become answerable.** "Which products contain an
ingredient with a concentration limit?" was unanswerable yesterday. It is now
a single filter, and the answer across the dataset is **9,321 products**.

---

## The part worth showing a supervisor

This product's `free_from` column says:

```
free_from    Fragrance, Parabens, Alcohol, Essential Oils, Silicones, Sulfates
```

That is the shop's own claim. **Free from fragrance.**

But `ingredient_functions` says **Fragrance**, because ROSA DAMASCENA FLOWER
WATER, rose water, carries FRAGRANCE as one of its three recognised functions
in the EU register, entry 59340.

**Both statements are defensible.** The product contains no added perfume,
which is what the shop means. It also contains a botanical water that the
Commission classifies as having a fragrance function, which is what the
register means. They are answering different questions.

This matters for three reasons.

**It is a cross-check that did not exist before.** A marketing claim can now
be tested against a regulator's classification, automatically, across 13,184
products.

**It is a real safety consideration.** Somebody who reacts to rose does not
care that the label says fragrance-free. A recommender that reads only the
shop's claim would hand them this product.

**It generalises.** The same check across the whole dataset found **574
products marked safe for sensitive skin that contain one of the 26 fragrance
allergens the EU requires to be declared** by name. 224 of those "sensitive"
claims came from the manufacturer, not a shop.

The response is not to overrule the manufacturer. It is to record both, and
let the recommender warn instead of silently choosing.

---

## The one-sentence version

> Two of the columns say how much of a formula we actually understand, and two
> say what the European Commission recognises those ingredients as doing. The
> result is that a recommendation can explain itself, and a marketing claim can
> be checked against a regulator rather than taken on trust.
