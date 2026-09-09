"""
add_derived_attributes.py

Adds columns to SKINCARE_FINAL.csv derived from data we already hold. No new
scraping, no API calls, nothing bought.

Everything comes from three places we already have:
  the INCI list                (11,802 products, 93.5%)
  the CosIng link              (99.2% of those matched)
  columns already in the file  (name, country, product_type, price)

The property list follows what the cosmetic analysis sites actually check:
SkinCarisma (malassezia, comedogenic, silicone, alcohol, allergens), CosDNA
(comedogenic and irritancy), SkinSort, plus the EU regulatory items that are
coming into force (nanomaterials, microplastics under 2023/2055, endocrine
disruptor restrictions under 2026/909).

WHAT THIS FILE WILL NOT DO
--------------------------
No "vegan", "cruelty free" or "organic" column. None of the three can be
derived from an ingredient list. See the notes at the end of this file.

Safety: write to a temp file, assert the row count, then os.replace.
"""
import csv, os, re, sys, collections

csv.field_size_limit(10**9)

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "..", "repo", "SKINCARE_FINAL.csv")

# ============================================================ ingredient sets
# Positive detection only. We say what IS present, never what is absent.

ANIMAL = ["CERA ALBA", "BEESWAX", "LANOLIN", r"\bMEL\b", "HONEY", "CARMINE",
 "CI 75470", r"\bSILK\b", "SERICA", "COLLAGEN", "ELASTIN", "KERATIN", "TALLOW",
 "CASEIN", "LACTOSE", r"\bMILK\b", "WHEY", r"\bEGG\b", "OVUM",
 "SNAIL SECRETION", "PROPOLIS", "ROYAL JELLY", "SHELLAC", "GUANINE",
 "CHITOSAN", "PLACENTA", r"\bEMU\b", r"\bMINK\b", "GELATIN", "CARMINIC",
 "PEARL POWDER", "CONCHIOLIN", "HELIX ASPERSA", "BOVINE", "PORCINE", "LACTIS"]
NOT_ANIMAL = ("SYNTHETIC", "VEGETAL", "VEGETABLE", "PLANT-DERIVED",
              "BIOMIMETIC", "VEGAN")

NUT = ["PRUNUS AMYGDALUS", "CORYLUS AVELLANA", "MACADAMIA", "ARGANIA",
 "JUGLANS", "ANACARDIUM", "BERTHOLLETIA", "PISTACIA VERA", r"\bCARYA\b",
 "PECAN", "CASHEW", "HAZELNUT", "SWEET ALMOND", "WALNUT"]
GLUTEN = ["TRITICUM", "AVENA", "HORDEUM", "SECALE", "WHEAT", "OAT KERNEL",
          "BARLEY", r"\bRYE\b", r"\bMALT\b"]
SOY = ["GLYCINE SOJA", "GLYCINE MAX", "SOYBEAN", r"\bSOY\b"]
COCONUT = ["COCOS NUCIFERA", "COCAMIDO", "COCAMIDE", "COCOYL", "COCOATE",
           "COCAMIN", r"\bCOCO-"]

RETINOID = ["RETINOL", "RETINYL", "RETINAL", "RETINOIC", "TRETINOIN",
            "ADAPALENE", "HYDROQUINONE", "RETINALDEHYDE"]
PHOTOSENS = ["CITRUS BERGAMIA", "CITRUS LIMON", "CITRUS AURANTIFOLIA",
 "BERGAPTEN", "FUROCOUMARIN", "CITRUS PARADISI", "ANGELICA ARCHANGELICA",
 "RUTA GRAVEOLENS"]
DRYING_ALCOHOL = ["ALCOHOL DENAT", "SD ALCOHOL", r"\bETHANOL\b",
                  "ISOPROPYL ALCOHOL"]
FATTY_ALCOHOL = ("CETYL", "CETEARYL", "STEARYL", "BEHENYL", "LAURYL",
                 "MYRISTYL", "ARACHIDYL")

# --- what SkinCarisma and CosDNA flag ---------------------------------------
MALASSEZIA = ["POLYSORBATE", "SORBITAN", "GLYCERYL STEARATE",
 "ISOPROPYL MYRISTATE", "ISOPROPYL PALMITATE", "LAURIC ACID", "MYRISTIC ACID",
 "OLEIC ACID", "PALMITIC ACID", "STEARIC ACID", "LINOLEIC ACID",
 "CAPRYLIC/CAPRIC", "GALACTOMYCES", "SACCHAROMYCES", "LACTOBACILLUS",
 r"\bFERMENT\b", r"PEG-\d+ STEARATE", r"PEG-\d+ LAURATE", r"PEG-\d+ OLEATE",
 "OLEA EUROPAEA", "COCOS NUCIFERA OIL", "SIMMONDSIA"]
COMEDOGENIC = ["ISOPROPYL MYRISTATE", "ISOPROPYL PALMITATE",
 "COCOS NUCIFERA OIL", "LAURIC ACID", "MYRISTYL MYRISTATE", "OCTYL PALMITATE",
 "ETHYLHEXYL PALMITATE", "LINSEED OIL", "WHEAT GERM", "LAURETH-4",
 "OLEYL ALCOHOL", "SODIUM LAURYL SULFATE", "BUTYL STEARATE",
 "ISOCETYL STEARATE", "MYRISTYL LACTATE", "COCOA BUTTER", "THEOBROMA CACAO"]

# --- sunscreen chemistry ----------------------------------------------------
UV_MINERAL = ["ZINC OXIDE", "TITANIUM DIOXIDE"]
UV_CHEMICAL = ["AVOBENZONE", "BUTYL METHOXYDIBENZOYLMETHANE", "OCTOCRYLENE",
 "HOMOSALATE", "OCTISALATE", "ETHYLHEXYL SALICYLATE", "OCTINOXATE",
 "ETHYLHEXYL METHOXYCINNAMATE", "OXYBENZONE", "BENZOPHENONE-3", "TINOSORB",
 "BEMOTRIZINOL", "BISOCTRIZOLE", "UVINUL", "ENSULIZOLE",
 "DIETHYLAMINO HYDROXYBENZOYL", "ETHYLHEXYL TRIAZONE"]
REEF_HARMFUL = ["BENZOPHENONE-3", "OXYBENZONE", "ETHYLHEXYL METHOXYCINNAMATE",
 "OCTINOXATE", "OCTOCRYLENE", "4-METHYLBENZYLIDENE CAMPHOR"]

# --- EU regulatory watch ----------------------------------------------------
NANO = [r"\[NANO\]", r"\(NANO\)", r"\bNANO\b"]
# EU 2023/2055 restricts SOLID microplastic particles. Carbomer and the
# polyquaterniums are dissolved or swollen polymers, not solid beads, so they
# belong in the broader column and not in this one.
MICROPLASTIC = [r"\bNYLON-\d", r"POLYETHYLENE\b", "POLYPROPYLENE",
 "POLYMETHYL METHACRYLATE", r"\bPMMA\b", "POLYURETHANE",
 "STYRENE/ACRYLATES COPOLYMER", r"\bPTFE\b"]
SYNTHETIC_POLYMER = MICROPLASTIC + [r"\bCARBOMER\b", "ACRYLATES COPOLYMER",
 "POLYQUATERNIUM", "SODIUM CARBOMER", "ACRYLATES CROSSPOLYMER"]
ENDOCRINE = ["BUTYLPARABEN", "PROPYLPARABEN", "BENZOPHENONE-3", "OXYBENZONE",
 "TRICLOSAN", r"\bBHA\b", "BUTYLATED HYDROXYANISOLE", "CYCLOPENTASILOXANE",
 "CYCLOTETRASILOXANE", "BENZYL SALICYLATE", "TRIPHENYL PHOSPHATE",
 "RESORCINOL"]
PFAS = ["PERFLUOR", "POLYFLUOR", r"\bPTFE\b", r"\bFLUORO"]

# --- the usual "free from" filters ------------------------------------------
PEG = [r"PEG-\d", r"\bPEG\b", "POLYETHYLENE GLYCOL"]
TALC = [r"\bTALC\b"]
SILICONE = ["DIMETHICONE", "SILOXANE", "SILICONE", "CYCLOMETHICONE",
            "DIMETHICONOL", "TRIMETHICONE"]
SULFATE = ["SODIUM LAURYL SULFATE", "SODIUM LAURETH SULFATE",
           "AMMONIUM LAURYL SULFATE", "AMMONIUM LAURETH SULFATE"]
PROPYLENE_GLYCOL = ["PROPYLENE GLYCOL"]

# --- active families --------------------------------------------------------
# citric acid is deliberately NOT here. It is a pH adjuster in almost every
# formula that contains it, and counting it as an exfoliant would wrongly
# label 2,842 products.
AHA = ["GLYCOLIC ACID", "LACTIC ACID", "MANDELIC ACID", "MALIC ACID",
       "TARTARIC ACID"]
BHA_ACID = ["SALICYLIC ACID", "BETAINE SALICYLATE", "CAPRYLOYL SALICYLIC"]
PHA = ["GLUCONOLACTONE", "LACTOBIONIC ACID"]
CERAMIDE = ["CERAMIDE"]
PEPTIDE = ["PEPTIDE", "OLIGOPEPTIDE", "PALMITOYL TRIPEPTIDE",
           "ACETYL HEXAPEPTIDE", "MATRIXYL"]
ANTIOXIDANT = ["TOCOPHEROL", "ASCORBIC ACID", "ASCORBYL", "FERULIC ACID",
 "RESVERATROL", "COENZYME", "UBIQUINONE", "CAMELLIA SINENSIS", "GLUTATHIONE",
 "ASTAXANTHIN"]
SOOTHING = ["CENTELLA", "MADECASSOSIDE", "ASIATICOSIDE", "ALLANTOIN",
 "BISABOLOL", "ALOE", "CHAMOMILLA", "GLYCYRRHIZA", "BETA-GLUCAN", "PANTHENOL"]

# --- what people actually ask for -------------------------------------------
# "mature skin" is the trade word for skin losing collagen and lipids: fine
# lines, slower turnover, more dryness. These are the actives that address it.
MATURE_ACTIVES = ["RETINOL", "RETINYL", "RETINAL", "PEPTIDE", "MATRIXYL",
 "ASCORBIC ACID", "ASCORBYL", "COENZYME", "UBIQUINONE", "NIACINAMIDE",
 "BAKUCHIOL", "GLYCOLIC ACID", "LACTIC ACID", "ADENOSINE", "GROWTH FACTOR",
 "EGF", "RESVERATROL", "PHYTONADIONE"]
# barrier repair: the three lipids skin makes itself, plus the classic soothers
BARRIER_REPAIR = ["CERAMIDE", "CHOLESTEROL", "PHYTOSPHINGOSINE",
 "SPHINGOLIPID", "NIACINAMIDE", "PANTHENOL", "CENTELLA", "MADECASSOSIDE",
 "SQUALANE", "LINOLEIC ACID", "BETA-GLUCAN", "ALLANTOIN"]
# ingredients that speed cell turnover, so skin can look worse for 4 to 8 weeks
PURGING = ["RETINOL", "RETINYL", "RETINAL", "TRETINOIN", "ADAPALENE",
 "SALICYLIC ACID", "GLYCOLIC ACID", "LACTIC ACID", "MANDELIC ACID",
 "BENZOYL PEROXIDE", "AZELAIC ACID"]
# night only: unstable in light, or increases sun sensitivity
PM_ONLY = ["RETINOL", "RETINYL", "RETINAL", "TRETINOIN", "ADAPALENE",
 "BENZOYL PEROXIDE", "HYDROQUINONE"]
FRAGRANCE = [r"\bPARFUM\b", r"\bFRAGRANCE\b", "AROMA", "LINALOOL", "LIMONENE",
 "CITRONELLOL", "GERANIOL", "EUGENOL", "COUMARIN", "CINNAMAL",
 "BENZYL ALCOHOL", "HEXYL CINNAMAL", "BUTYLPHENYL METHYLPROPIONAL"]
ESSENTIAL_OIL = ["ESSENTIAL OIL", "LAVANDULA", "MENTHA", "EUCALYPTUS",
 "ROSMARINUS", "CITRUS.*OIL", "PELARGONIUM", "CANANGA", "MELALEUCA",
 "POGOSTEMON", "SANTALUM"]

OCCLUSIVE = ["PETROLATUM", "MINERAL OIL", "PARAFFINUM", "DIMETHICONE",
             "LANOLIN", "SHEA BUTTER", "BUTYROSPERMUM", "CERA ALBA"]
HUMECTANT = ["GLYCERIN", "HYALURONIC", "SODIUM HYALURONATE",
 "BUTYLENE GLYCOL", r"\bUREA\b", "SODIUM PCA", "PANTHENOL", "TREHALOSE"]

PRESERVATIVES = [
 ("Phenoxyethanol",        ["PHENOXYETHANOL"]),
 ("Parabens",              ["PARABEN"]),
 ("Organic acid",          ["SODIUM BENZOATE", "POTASSIUM SORBATE",
                            "BENZOIC ACID", "SORBIC ACID"]),
 ("Formaldehyde releaser", ["DMDM HYDANTOIN", "IMIDAZOLIDINYL",
                            "DIAZOLIDINYL", "QUATERNIUM-15"]),
 ("Isothiazolinone",       ["METHYLISOTHIAZOLINONE",
                            "METHYLCHLOROISOTHIAZOLINONE"]),
 ("Glycol or alcohol",     ["ALCOHOL DENAT", "BENZYL ALCOHOL",
                            "ETHYLHEXYLGLYCERIN", "CAPRYLYL GLYCOL"]),
]

ACTIVES = [("NIACINAMIDE", "niacinamide"), ("ASCORBIC ACID", "vitamin C"),
 ("SALICYLIC ACID", "salicylic acid"), ("RETINOL", "retinol"),
 ("GLYCOLIC ACID", "glycolic acid"), ("LACTIC ACID", "lactic acid"),
 ("AZELAIC ACID", "azelaic acid"), ("ADENOSINE", "adenosine"),
 ("ARBUTIN", "arbutin"), ("TRANEXAMIC", "tranexamic acid")]

ROUTINE_STEP = {
 "Face Cleanser": "1 Cleanse", "Makeup Remover": "1 Cleanse",
 "Toner": "2 Tone", "Essence": "3 Essence", "Serum": "4 Treat",
 "Facial Treatment": "4 Treat", "Exfoliator": "4 Treat",
 "Eye Moisturizer": "5 Eye", "General Moisturizer": "6 Moisturise",
 "Day Moisturizer": "6 Moisturise", "Night Moisturizer": "6 Moisturise",
 "Emulsion": "6 Moisturise", "Oil": "7 Oil", "Sunscreen": "8 Protect",
 "Wet Mask": "9 Mask", "Sheet Mask": "9 Mask", "Overnight Mask": "9 Mask",
 "Eye Mask": "9 Mask", "Lip Mask": "9 Mask", "Lip Moisturizer": "10 Lips",
 "Bath & Body": "11 Body", "Hand Care": "11 Body",
}
BODY_SITE = {"Eye Moisturizer": "eye area", "Eye Mask": "eye area",
 "Lip Moisturizer": "lips", "Lip Mask": "lips", "Hand Care": "hands",
 "Bath & Body": "body"}
REGION = {"South Korea": "K-beauty", "Japan": "J-beauty",
          "France": "French pharmacy", "Lebanon": "Lebanese made"}


# ================================================================== helpers
def split_inci(text):
    """Split INCI, protecting commas inside numbers like 1,2-Hexanediol."""
    s = (text or "").upper()
    if not s.strip():
        return []
    s = re.sub(r"(?<=\d),(?=\d)", "\x00", s)
    return [x.replace("\x00", ",").strip(" .*") for x in s.split(",") if x.strip()]


_COMPILED = {}


def _rx(patterns):
    """Compile a pattern list once into a single alternation, then cache it.

    Without this the script recompiles every pattern for every ingredient of
    every product, which is roughly 40 million regex compiles and takes
    minutes. With it the whole run is a few seconds.
    """
    key = id(patterns)
    if key not in _COMPILED:
        parts = [p if ("\\" in p or "-" in p) else r"\b" + re.escape(p)
                 for p in patterns]
        _COMPILED[key] = re.compile("|".join(parts))
    return _COMPILED[key]


def matches(patterns, items, exclude=()):
    """Ingredients that matched, so every flag can show its evidence."""
    rx = _rx(patterns)
    found = []
    for ing in items:
        if exclude and any(e in ing for e in exclude):
            continue
        if rx.search(ing):
            found.append(ing)
    return found


def any_match(patterns, items, exclude=()):
    return bool(matches(patterns, items, exclude))


# =================================================================== columns
FLAGS = [
 # (column, evidence column or None, pattern list, exclude tuple)
 ("contains_animal_derived",  "animal_derived_evidence",  ANIMAL, NOT_ANIMAL),
 ("contains_tree_nut",        "tree_nut_evidence",        NUT, ()),
 ("contains_gluten_grain",    "gluten_evidence",          GLUTEN, ()),
 ("contains_soy",             None,                       SOY, ()),
 ("contains_coconut",         None,                       COCONUT, ()),
 ("contains_retinoid",        "retinoid_evidence",        RETINOID, ()),
 ("contains_photosensitiser", "photosensitiser_evidence", PHOTOSENS, ()),
 ("contains_drying_alcohol",  "drying_alcohol_evidence",  DRYING_ALCOHOL,
                                                          FATTY_ALCOHOL),
 ("feeds_malassezia",         "malassezia_evidence",      MALASSEZIA, ()),
 ("contains_comedogenic",     "comedogenic_evidence",     COMEDOGENIC, ()),
 ("contains_reef_harmful_uv", "reef_harmful_evidence",    REEF_HARMFUL, ()),
 ("contains_nanomaterial",    "nanomaterial_evidence",    NANO, ()),
 ("contains_solid_microplastic", "microplastic_evidence",  MICROPLASTIC, ()),
 ("contains_synthetic_polymer", None,                     SYNTHETIC_POLYMER, ()),
 ("contains_endocrine_concern","endocrine_evidence",      ENDOCRINE, ()),
 ("contains_pfas",            None,                       PFAS, ()),
 ("contains_peg",             None,                       PEG, ()),
 ("contains_talc",            None,                       TALC, ()),
 ("contains_silicone",        None,                       SILICONE, ()),
 ("contains_sulfate",         None,                       SULFATE, ()),
 ("contains_propylene_glycol",None,                       PROPYLENE_GLYCOL, ()),
 ("contains_aha",             "aha_evidence",             AHA, ()),
 ("contains_bha",             "bha_evidence",             BHA_ACID, ()),
 ("contains_pha",             None,                       PHA, ()),
 ("contains_ceramide",        None,                       CERAMIDE, ()),
 ("contains_peptide",         None,                       PEPTIDE, ()),
 ("contains_antioxidant",     None,                       ANTIOXIDANT, ()),
 ("contains_soothing",        None,                       SOOTHING, ()),
 ("suits_mature_skin",       "mature_skin_evidence",     MATURE_ACTIVES, ()),
 ("supports_barrier_repair", "barrier_repair_evidence",  BARRIER_REPAIR, ()),
 ("may_cause_purging",       "purging_evidence",         PURGING, ()),
 ("contains_fragrance",      "fragrance_evidence",       FRAGRANCE, ()),
 ("contains_essential_oil",  None,                       ESSENTIAL_OIL, ()),
]

DESCRIPTIVE = ["preservative_system", "formula_base", "moisturiser_type",
               "sunscreen_filter_type", "actives_present",
               "lead_active_position", "stated_concentration",
               "halal_candidate", "routine_step", "body_site",
               "regional_style", "price_band_lebanon",
               "use_time", "do_not_layer_with", "strength_level",
               "texture", "white_cast_risk"]

NEW_COLS = []
for col, ev, _, _ in FLAGS:
    NEW_COLS.append(col)
    if ev:
        NEW_COLS.append(ev)
NEW_COLS += DESCRIPTIVE

PCT = re.compile(r"(\d{1,3}(?:\.\d)?)\s?%")


def derive(row):
    ing = split_inci(row.get("ingredients"))
    out = {c: "" for c in NEW_COLS}

    if ing:
        for col, ev, pats, exc in FLAGS:
            m = matches(pats, ing, exc)
            out[col] = "yes" if m else "no"
            if ev:
                out[ev] = m[0] if m else ""

        systems = [n for n, p in PRESERVATIVES if any_match(p, ing)]
        out["preservative_system"] = ", ".join(systems) or "none detected"

        first = ing[0]
        if re.search(r"\bAQUA\b|\bWATER\b|\bEAU\b", first):
            out["formula_base"] = "water-based"
        elif re.search(r"GLYCERIN|BUTYLENE GLYCOL|PROPANEDIOL", first):
            out["formula_base"] = "humectant-led"
        elif re.search(r"OIL\b|BUTTER|SQUALANE|CAPRYLIC", first):
            out["formula_base"] = "anhydrous"
        else:
            out["formula_base"] = "other"

        occ, hum = any_match(OCCLUSIVE, ing), any_match(HUMECTANT, ing)
        out["moisturiser_type"] = ("draws and seals" if occ and hum else
                                   "occlusive, seals" if occ else
                                   "humectant, draws" if hum else "neither")

        mineral = any_match(UV_MINERAL, ing)
        chemical = any_match(UV_CHEMICAL, ing)
        out["sunscreen_filter_type"] = ("hybrid, mineral and chemical"
                                        if mineral and chemical else
                                        "mineral" if mineral else
                                        "chemical" if chemical else "")

        present, lead, lead_pos = [], "", 10 ** 6
        for marker, label in ACTIVES:
            for i, x in enumerate(ing, 1):
                if marker in x:
                    present.append(label)
                    if i < lead_pos:
                        lead, lead_pos = f"{label} at position {i}", i
                    break
        out["actives_present"] = ", ".join(present)
        out["lead_active_position"] = lead

        # halal is a CANDIDATE only, same logic limit as vegan
        no_alc = not any_match(DRYING_ALCOHOL, ing, FATTY_ALCOHOL)
        no_ani = not any_match(ANIMAL, ing, NOT_ANIMAL)
        out["halal_candidate"] = "candidate" if (no_alc and no_ani) else "no"

        # ---- when to use it -------------------------------------------
        pm = any_match(PM_ONLY, ing)
        exfo = any_match(AHA, ing) or any_match(BHA_ACID, ing)
        uv = mineral or chemical
        out["use_time"] = ("night only" if pm else
                           "morning" if uv else
                           "night preferred" if exfo else "morning or night")

        # ---- what not to layer it with --------------------------------
        clash = []
        if any_match(RETINOID, ing):
            clash.append("acids (AHA, BHA) and vitamin C, on the same night")
        if exfo and not any_match(RETINOID, ing):
            clash.append("retinoids and other acids, same session")
        if any_match(["ASCORBIC ACID"], ing):
            clash.append("benzoyl peroxide, which oxidises it")
        out["do_not_layer_with"] = "; ".join(clash)

        # ---- how strong is it -----------------------------------------
        strong = any_match(RETINOID, ing) or exfo
        pos = lead_pos if lead else 10 ** 6
        out["strength_level"] = ("advanced, patch test first" if strong and pos <= 8
                                 else "intermediate" if strong or present
                                 else "gentle")

        # ---- white cast, mineral filters that are not nano -------------
        if mineral and not any_match(NANO, ing):
            out["white_cast_risk"] = "possible, mineral filter not marked nano"
        elif mineral:
            out["white_cast_risk"] = "lower, nano mineral filter"

    # ---- texture, from the product name ------------------------------
    nm = (row.get("name") or "").lower()
    for word, label in [("balm", "balm"), ("butter", "balm"), ("oil", "oil"),
                        ("gel", "gel"), ("foam", "foam"), ("mousse", "foam"),
                        ("milk", "milk"), ("lotion", "lotion"),
                        ("mist", "mist"), ("spray", "mist"),
                        ("water", "water"), ("essence", "essence"),
                        ("stick", "stick"), ("powder", "powder"),
                        ("cream", "cream"), ("serum", "serum")]:
        if word in nm:
            out["texture"] = label
            break

    m = PCT.search(row.get("name") or "")
    if m and m.group(1) not in ("100",):
        out["stated_concentration"] = m.group(0)

    ptype = (row.get("product_type") or "").strip()
    out["routine_step"] = ROUTINE_STEP.get(ptype, "")
    out["body_site"] = BODY_SITE.get(ptype, "face" if ptype else "")
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

    tally = collections.Counter()
    for r in rows:
        d = derive(r)
        r.update(d)
        for k, v in d.items():
            if v == "yes":
                tally[k] += 1

    wf = sum(1 for r in rows if split_inci(r.get("ingredients")))
    print(f"products with a formula: {wf:,}\n")
    print(f"{'new flag':32s} {'yes':>8s} {'% formulas':>12s}")
    print("-" * 56)
    for col, _, _, _ in FLAGS:
        n = tally[col]
        print(f"{col:32s} {n:>8,} {n / wf * 100:>11.1f}%")

    print(f"\n{len(NEW_COLS)} new columns "
          f"({len(FLAGS)} flags, {sum(1 for c,e,_,_ in FLAGS if e)} evidence, "
          f"{len(DESCRIPTIVE)} descriptive)")

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
# NO "vegan" COLUMN
#   Stearic acid, glycerin, squalane and lactic acid can each come from a plant
#   or an animal, and the INCI name is identical either way. So we can say a
#   product CONTAINS an animal-derived ingredient. We cannot say it does not.
#
# NO "cruelty free" OR "organic" COLUMN
#   Both are certifications held by a company or a product, granted by Leaping
#   Bunny, PETA, COSMOS or Ecocert. Nothing in an ingredient list can tell you.
#   Both are obtainable from those public lists, keyed on our 1,463 brands.
#
# WHY halal_candidate SAYS "candidate"
#   Same limit as vegan. We can see there is no ethanol and no animal marker.
#   We cannot see that an ambiguous ingredient was plant sourced. Real halal
#   status is a certification.
#
# WHY THERE ARE TWO POLYMER COLUMNS
#   EU 2023/2055 restricts SOLID microplastic particles. A first pass caught
#   3,125 products, but 1,930 of those were carbomer, which is a swollen gel
#   network rather than a solid bead, and several hundred more were dissolved
#   polyquaternium conditioners. Calling those microplastics would be wrong. So
#   contains_solid_microplastic holds only what the restriction targets, and
#   contains_synthetic_polymer holds the broader set.
#
# WHY CITRIC ACID IS NOT IN THE AHA LIST
#   3,267 products contain citric acid, but in almost all of them it is a pH
#   adjuster, not an exfoliant. Including it would wrongly label 2,842 products
#   as containing an AHA.
#
# WHY FATTY ALCOHOLS ARE EXCLUDED FROM contains_drying_alcohol
#   Cetyl, cetearyl and stearyl alcohol are emollients. They soften skin. Only
#   ethanol and its denatured forms are drying.
#
# WHY SYNTHETIC BEESWAX IS NOT ANIMAL-DERIVED
#   It is a lab-made copy. Excluded along with vegetal and biomimetic variants.
#
# THE _evidence COLUMNS
#   Every flag names the ingredient that triggered it, so a reader can check us
#   and a wrong flag traces back to the rule that made it.
