"""
add_derived_attributes.py

Adds new columns to SKINCARE_FINAL.csv that are DERIVED from data we already
hold. No new scraping, no new API calls, nothing bought.

Everything here comes from three places we already have:
  the INCI list          (11,802 products, 93.5%)
  the CosIng link        (99.2% of those matched)
  columns already in the file (country, product_type, price, shops)

WHAT THIS FILE WILL NOT DO
--------------------------
It will not write a "vegan" or "cruelty free" column. Those cannot be derived
from an ingredient list and saying otherwise would be a lie. See the notes at
the bottom of this file and in ../repo/literature/DERIVED_ATTRIBUTES.md.

Safety rules, same as the rest of the pipeline:
  write to a temp file, assert the row count, then os.replace
"""
import csv, os, re, sys, collections

csv.field_size_limit(10**9)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "..", "repo", "SKINCARE_FINAL.csv")

# ===================================================================== markers
# Curated INCI name markers. Positive detection only: we say what IS there.

ANIMAL = [
 "CERA ALBA", "BEESWAX", "LANOLIN", r"\bMEL\b", "HONEY", "CARMINE", "CI 75470",
 r"\bSILK\b", "SERICA", "COLLAGEN", "ELASTIN", "KERATIN", "TALLOW", "CASEIN",
 "LACTOSE", r"\bMILK\b", "WHEY", r"\bEGG\b", "OVUM", "SNAIL SECRETION",
 "PROPOLIS", "ROYAL JELLY", "SHELLAC", "GUANINE", "CHITOSAN", "PLACENTA",
 r"\bEMU\b", r"\bMINK\b", "GELATIN", "CARMINIC", "PEARL POWDER", "CONCHIOLIN",
 "HELIX ASPERSA", "BOVINE", "PORCINE", "LACTIS", "HYDROLYZED SILK",
]
NUT = [
 "PRUNUS AMYGDALUS", "CORYLUS AVELLANA", "MACADAMIA", "ARGANIA", "JUGLANS",
 "ANACARDIUM", "BERTHOLLETIA", "PISTACIA VERA", r"\bCARYA\b", "PECAN",
 "CASHEW", "HAZELNUT", "SWEET ALMOND", "WALNUT",
]
GLUTEN = ["TRITICUM", "AVENA", "HORDEUM", "SECALE", "WHEAT", "OAT KERNEL",
          "BARLEY", r"\bRYE\b", r"\bMALT\b"]
SOY    = ["GLYCINE SOJA", "GLYCINE MAX", "SOYBEAN", r"\bSOY\b"]
COCONUT= ["COCOS NUCIFERA", "COCAMIDO", "COCAMIDE", "COCOYL", "COCOATE",
          "COCAMIN", r"\bCOCO-"]
RETINOID = ["RETINOL", "RETINYL", "RETINAL", "RETINOIC", "TRETINOIN",
            "ADAPALENE", "HYDROQUINONE", "RETINALDEHYDE"]
PHOTOSENS = ["CITRUS BERGAMIA", "CITRUS LIMON", "CITRUS AURANTIFOLIA",
             "BERGAPTEN", "FUROCOUMARIN", "CITRUS PARADISI",
             "ANGELICA ARCHANGELICA", "RUTA GRAVEOLENS"]
REEF = ["BENZOPHENONE-3", "OXYBENZONE", "ETHYLHEXYL METHOXYCINNAMATE",
        "OCTINOXATE", "OCTOCRYLENE", "4-METHYLBENZYLIDENE CAMPHOR"]
DRYING_ALCOHOL = ["ALCOHOL DENAT", "SD ALCOHOL", r"\bETHANOL\b",
                  "ISOPROPYL ALCOHOL"]
# fatty alcohols are emollients, not drying. Never flag these.
FATTY_ALCOHOL = ("CETYL", "CETEARYL", "STEARYL", "BEHENYL", "LAURYL",
                 "MYRISTYL", "ARACHIDYL")
# a lab-made copy of an animal substance is not animal-derived
NOT_ANIMAL = ("SYNTHETIC", "VEGETAL", "VEGETABLE", "PLANT-DERIVED",
              "BIOMIMETIC", "SOY COLLAGEN", "VEGAN")

PRESERVATIVES = [
 ("Phenoxyethanol",        ["PHENOXYETHANOL"]),
 ("Parabens",              ["PARABEN"]),
 ("Organic acid",          ["SODIUM BENZOATE", "POTASSIUM SORBATE",
                            "BENZOIC ACID", "SORBIC ACID"]),
 ("Formaldehyde releaser", ["DMDM HYDANTOIN", "IMIDAZOLIDINYL",
                            "DIAZOLIDINYL", "QUATERNIUM-15"]),
 ("Isothiazolinone",       ["METHYLISOTHIAZOLINONE",
                            "METHYLCHLOROISOTHIAZOLINONE"]),
 ("Alcohol or glycol",     ["ALCOHOL DENAT", "BENZYL ALCOHOL",
                            "ETHYLHEXYLGLYCERIN", "CAPRYLYL GLYCOL"]),
]

ROUTINE_STEP = {
 "Face Cleanser": "1 Cleanse", "Makeup Remover": "1 Cleanse",
 "Toner": "2 Tone", "Essence": "3 Essence",
 "Serum": "4 Treat", "Facial Treatment": "4 Treat", "Exfoliator": "4 Treat",
 "Eye Moisturizer": "5 Eye",
 "General Moisturizer": "6 Moisturise", "Day Moisturizer": "6 Moisturise",
 "Night Moisturizer": "6 Moisturise", "Emulsion": "6 Moisturise",
 "Oil": "7 Oil", "Sunscreen": "8 Protect",
 "Wet Mask": "9 Mask", "Sheet Mask": "9 Mask", "Overnight Mask": "9 Mask",
 "Eye Mask": "9 Mask", "Lip Mask": "9 Mask",
 "Lip Moisturizer": "10 Lips",
 "Bath & Body": "11 Body", "Hand Care": "11 Body",
}
REGION = {"South Korea": "K-beauty", "Japan": "J-beauty",
          "France": "French pharmacy", "Lebanon": "Lebanese made"}

ACTIVES = [("NIACINAMIDE", "niacinamide"), ("ASCORBIC ACID", "vitamin C"),
           ("SALICYLIC ACID", "salicylic acid"), ("RETINOL", "retinol"),
           ("GLYCOLIC ACID", "glycolic acid"), ("LACTIC ACID", "lactic acid"),
           ("AZELAIC ACID", "azelaic acid"), ("ADENOSINE", "adenosine")]

BODY_SITE = {
 "Eye Moisturizer": "eye area", "Eye Mask": "eye area",
 "Lip Moisturizer": "lips", "Lip Mask": "lips",
 "Hand Care": "hands", "Bath & Body": "body",
}

# ================================================================== helpers
def split_inci(text):
    """Split an INCI string, protecting commas inside numbers like 1,2-Hexanediol."""
    s = (text or "").upper()
    if not s.strip():
        return []
    s = re.sub(r"(?<=\d),(?=\d)", "\x00", s)
    return [x.replace("\x00", ",").strip(" .*") for x in s.split(",") if x.strip()]


def matches(patterns, items, exclude=()):
    """Return the ingredients that match, so every flag can show its evidence."""
    found = []
    for ing in items:
        if any(e in ing for e in exclude):
            continue
        for p in patterns:
            rx = p if p.startswith("\\b") or "-" in p or "\\" in p else r"\b" + re.escape(p)
            if re.search(rx, ing):
                found.append(ing)
                break
    return found


def first_of(patterns, items):
    m = matches(patterns, items)
    return m[0] if m else ""


# =================================================================== columns
NEW_COLS = [
 "contains_animal_derived", "animal_derived_evidence",
 "contains_tree_nut",       "tree_nut_evidence",
 "contains_gluten_grain",   "gluten_evidence",
 "contains_soy",
 "contains_coconut",
 "contains_retinoid",       "retinoid_evidence",
 "contains_photosensitiser","photosensitiser_evidence",
 "contains_reef_harmful_uv","reef_harmful_evidence",
 "contains_drying_alcohol", "drying_alcohol_evidence",
 "preservative_system",
 "formula_base",
 "actives_present",
 "lead_active_position",
 "routine_step",
 "body_site",
 "regional_style",
 "price_band_lebanon",
]


def derive(row):
    ing = split_inci(row.get("ingredients"))
    out = {c: "" for c in NEW_COLS}

    # things we can only judge when there is a formula
    if ing:
        def flag(key, ev_key, pats, exclude=()):
            m = matches(pats, ing, exclude)
            out[key] = "yes" if m else "no"
            if ev_key:
                out[ev_key] = m[0] if m else ""

        flag("contains_animal_derived",  "animal_derived_evidence",  ANIMAL,
             exclude=NOT_ANIMAL)
        flag("contains_tree_nut",        "tree_nut_evidence",        NUT)
        flag("contains_gluten_grain",    "gluten_evidence",          GLUTEN)
        flag("contains_soy",             None,                       SOY)
        flag("contains_coconut",         None,                       COCONUT)
        flag("contains_retinoid",        "retinoid_evidence",        RETINOID)
        flag("contains_photosensitiser", "photosensitiser_evidence", PHOTOSENS)
        flag("contains_reef_harmful_uv", "reef_harmful_evidence",    REEF)
        flag("contains_drying_alcohol",  "drying_alcohol_evidence",
             DRYING_ALCOHOL, exclude=FATTY_ALCOHOL)

        systems = [name for name, pats in PRESERVATIVES if matches(pats, ing)]
        out["preservative_system"] = ", ".join(systems) if systems else \
            "none detected"

        first = ing[0]
        if re.search(r"\bAQUA\b|\bWATER\b|\bEAU\b", first):
            out["formula_base"] = "water-based"
        elif re.search(r"GLYCERIN|BUTYLENE GLYCOL|PROPANEDIOL", first):
            out["formula_base"] = "humectant-led"
        elif re.search(r"OIL\b|BUTTER|SQUALANE|CAPRYLIC", first):
            out["formula_base"] = "anhydrous"
        else:
            out["formula_base"] = "other"

        present, lead = [], ""
        for marker, label in ACTIVES:
            for i, x in enumerate(ing, 1):
                if marker in x:
                    present.append(label)
                    if not lead or i < int(lead.split(":")[1]):
                        lead = f"{label}:{i}"
                    break
        out["actives_present"] = ", ".join(present)
        out["lead_active_position"] = lead

    # things that need no formula
    ptype = (row.get("product_type") or "").strip()
    out["routine_step"]   = ROUTINE_STEP.get(ptype, "")
    out["body_site"]      = BODY_SITE.get(ptype, "face" if ptype else "")
    out["regional_style"] = REGION.get((row.get("country") or "").strip(), "")

    try:
        p = float(row.get("price_usd") or "")
        out["price_band_lebanon"] = ("under $10" if p < 10 else
                                     "$10 to $25" if p < 25 else
                                     "$25 to $50" if p < 50 else "over $50")
    except ValueError:
        pass
    return out


# ====================================================================== main
def main(apply=False):
    with open(SRC, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys())
    n_before = len(rows)
    print(f"read {n_before:,} rows, {len(fields)} columns")

    already = [c for c in NEW_COLS if c in fields]
    if already:
        print(f"WARNING: these columns already exist and will be overwritten: {already}")

    tally = collections.Counter()
    for r in rows:
        d = derive(r)
        r.update(d)
        for k, v in d.items():
            if v == "yes":
                tally[k] += 1

    with_formula = sum(1 for r in rows if split_inci(r.get("ingredients")))
    print(f"\nproducts with a formula: {with_formula:,}\n")
    print(f"{'new column':30s} {'yes':>8s} {'% of formulas':>15s}")
    print("-" * 56)
    for c in NEW_COLS:
        if c.startswith("contains_"):
            n = tally[c]
            print(f"{c:30s} {n:>8,} {n / with_formula * 100:>14.1f}%")

    if not apply:
        print("\nDRY RUN. Nothing written. Add --apply to write the file.")
        return

    out_fields = fields + [c for c in NEW_COLS if c not in fields]
    tmp = SRC + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=out_fields)
        w.writeheader()
        w.writerows(rows)

    with open(tmp, encoding="utf-8", newline="") as f:
        check = sum(1 for _ in csv.DictReader(f))
    assert check == n_before, f"row count changed: {n_before} -> {check}"

    os.replace(tmp, SRC)
    print(f"\nwritten. {n_before:,} rows, {len(out_fields)} columns "
          f"({len(out_fields) - len(fields)} new)")


if __name__ == "__main__":
    main(apply="--apply" in sys.argv)

# ============================================================== honest notes
#
# WHY THERE IS NO "vegan" COLUMN
#   Absence of a known animal marker does not prove a product is vegan. Stearic
#   acid, glycerin, squalane and lactic acid can each come from a plant or an
#   animal, and the INCI name is identical either way. So we can say a product
#   CONTAINS an animal-derived ingredient. We cannot say it does not.
#   The honest column is contains_animal_derived, and that is what we write.
#
# WHY THERE IS NO "cruelty free" COLUMN
#   Cruelty free is a property of a COMPANY, not a formula, and it is granted by
#   a certifier such as Leaping Bunny or PETA. Nothing in an ingredient list can
#   tell you. It would have to come from those public certification lists, keyed
#   on our 1,463 brands, and recorded with its source and date like any other
#   claim.
#
# WHY THERE IS NO "organic" COLUMN
#   Same reason. Organic is a certification (COSMOS, Ecocert, USDA) held by a
#   product or a company. It is not visible in an INCI list.
#
# WHAT THE _evidence COLUMNS ARE FOR
#   Every flag names the ingredient that triggered it. So a reader can check us,
#   and a wrong flag can be traced to the rule that produced it rather than
#   being an unexplained "yes".
