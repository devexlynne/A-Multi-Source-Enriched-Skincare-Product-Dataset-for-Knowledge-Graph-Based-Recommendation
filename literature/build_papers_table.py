"""
Builds PAPERS_TABLE.xlsx. Four tabs.

  The papers    28 papers in four groups, 28 columns, read left to right
                the way you would read a paper
  7ad ba3ed     the skincare ontologies side by side with us
  My ontology   drawn as a map, not a table
  Tools         every tool named anywhere in the workbook: what it is,
                what it does, link, do we use it, why

Text lives in papers_data.py. Run:  py build_papers_table.py
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from papers_data import COLS, PAPERS, GROUPS

# ---------------------------------------------------------------- look
INK   = "2E2A25"
PAPER = "FFFFFF"
ALT   = "FBFAF7"
LINE  = "E8E2D8"
SUB   = "8A8175"
MINE  = "FFF6E0"
MINEH = "E8A33D"
FLAG  = "FCEEE6"
FLAGT = "A83A1E"
FONT  = "Calibri"

GCOL = {  # dark, wash
 "A": ("1F6F6B", "EEF5F4"),
 "B": ("6B4E9B", "F2EEF8"),
 "C": ("8C4A62", "FAF2F5"),
 "D": ("A6612F", "FBF4EC"),
}
BAND = {
 "Paper":          "EFEAE1",
 "The problem":    "EAEFF2",
 "Their data":     "EFEAE1",
 "Their ontology": "EAEFF2",
 "Building it":    "EFEAE1",
 "Did it work":    "EAEFF2",
 "For us":         MINE,
}

hair  = Side(style="thin", color=LINE)
under = Border(bottom=hair)
thick = Side(style="medium", color=INK)


def title(ws, span, text, sub):
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    c = ws.cell(row=1, column=1, value="  " + text)
    c.font = Font(name=FONT, size=17, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=INK)
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 36
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=span)
    c = ws.cell(row=2, column=1, value="  " + sub)
    c.font = Font(name=FONT, size=10.5, italic=True, color=SUB)
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[2].height = 22
    ws.row_dimensions[3].height = 6


wb = Workbook()

# ================================================================ 1. PAPERS
ws = wb.active
ws.title = "The papers"
NC = len(COLS)
title(ws, NC, "The papers",
      "28 papers in four groups. Columns run left to right the way you read a paper: "
      "who, what problem, their data, their ontology, how they built it, did it work, and what it means for us.")

GR, HR = 4, 5
ci = prev = None
ci, prev, start = 1, None, 1
for grp, hdr, w in list(COLS) + [("__end__", "", 0)]:
    if prev is not None and grp != prev:
        ws.merge_cells(start_row=GR, start_column=start, end_row=GR, end_column=ci - 1)
        c = ws.cell(row=GR, column=start, value=prev.upper())
        c.font = Font(name=FONT, size=9.5, bold=True, color="7A5200" if prev == "For us" else INK)
        c.fill = PatternFill("solid", fgColor=BAND[prev])
        c.alignment = Alignment(horizontal="center", vertical="center")
        start = ci
    prev = grp
    ci += 1
ws.row_dimensions[GR].height = 20

for i, (grp, hdr, w) in enumerate(COLS, start=1):
    c = ws.cell(row=HR, column=i, value=hdr)
    mine = grp == "For us"
    c.font = Font(name=FONT, size=10.5, bold=True, color="4A3200" if mine else PAPER)
    c.fill = PatternFill("solid", fgColor=MINEH if mine else INK)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[HR].height = 40

r = HR + 1
current = None
for row in PAPERS:
    g = row[1]
    dark, wash = GCOL[g]
    if g != current:                                   # group divider row
        current = g
        name, why = GROUPS[g]
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=NC)
        c = ws.cell(row=r, column=1, value=f"  GROUP {g}   {name.upper()}     {why}")
        c.font = Font(name=FONT, size=11.5, bold=True, color=PAPER)
        c.fill = PatternFill("solid", fgColor=dark)
        c.alignment = Alignment(vertical="center")
        ws.row_dimensions[r].height = 26
        r += 1
    stripe = (r % 2 == 0)
    for i, val in enumerate(row, start=1):
        grp = COLS[i - 1][0]
        c = ws.cell(row=r, column=i, value=val)
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        c.border = under
        if i == 2:
            c.font = Font(name=FONT, size=12, bold=True, color=PAPER)
            c.fill = PatternFill("solid", fgColor=dark)
            c.alignment = Alignment(horizontal="center", vertical="center")
        elif i == 3:
            c.font = Font(name=FONT, size=11.5, bold=True, color=dark)
            c.fill = PatternFill("solid", fgColor=wash)
            c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
        elif i == 4:
            c.font = Font(name=FONT, size=10.5, bold=True, color=INK)
            c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
        elif i == 8:                                    # notes
            hot = any(k in str(val).upper() for k in ("STRONG", "BEST", "NEED", "CHECK", "TEMPLATE", "RIVAL", "ANSWER", "BIGGEST", "PRECEDENT", "USEFUL", "STUDENT"))
            c.font = Font(name=FONT, size=10, bold=hot, color=FLAGT if hot else SUB)
            c.fill = PatternFill("solid", fgColor=FLAG if hot else (ALT if stripe else PAPER))
        elif i == 11:
            c.font = Font(name=FONT, size=9, color="2166A5", underline="single")
            c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
        elif i == 22:                                   # can we download
            yes = str(val).upper().startswith("YES")
            c.font = Font(name=FONT, size=10, bold=yes, color=GCOL["A"][0] if yes else SUB)
            c.fill = PatternFill("solid", fgColor="EDF5F3" if yes else (ALT if stripe else PAPER))
        elif grp == "For us":
            c.font = Font(name=FONT, size=10, color="3A3226")
            c.fill = PatternFill("solid", fgColor=MINE)
        else:
            c.font = Font(name=FONT, size=10, color="3A3630")
            c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
    ws.row_dimensions[r].height = 150
    r += 1

ws.freeze_panes = "D6"
ws.auto_filter.ref = f"A{HR}:{get_column_letter(NC)}{r-1}"
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 80

# ============================================================ 2. 7AD BA3ED
ws = wb.create_sheet("7ad ba3ed")
title(ws, 10, "7ad ba3ed",
      "Only the skincare ontologies, side by side with us. The three green rows are the whole thesis.")
H = ["", "Moe & Aung\n2014", "OntoCosmetic\n2021/23", "Hansanie\n2024", "Abesova\n2023",
     "bit-Tech\n2025", "Utari\n2023", "TOXIN\n2025", "HaCKG\n2025", "US"]
ROWS = [
 ("Properly peer reviewed?", "weak journal", "yes", "yes", "no, students", "yes", "yes", "yes", "yes", "will be", 0),
 ("Can you download the ontology?", "no", "YES", "no", "no", "?", "no", "YES", "?", "yes, planned", 0),
 ("Followed a named method?", "8 steps, unnamed", "no", "no", "middle out", "METHONTOLOGY", "METHONTOLOGY", "no", "no", "MOMo + LOT", 0),
 ("How many products", "never say", "279", "never say", "some Sephora", "3,800", "62", "none", "some", "12,629", 0),
 ("Ingredients tied to EU law?", "no", "no", "no", "no", "no", "no", "YES", "no", "YES, all 28,573", 1),
 ("Records who claimed what?", "no", "rules only", "no", "no", "no", "no", "by source", "no", "YES, 4 levels", 1),
 ("Knows if you can buy it?", "price band", "as a criterion", "no", "shop link", "no", "no", "no", "no", "YES, per shop, 2 currencies", 1),
 ("Which market", "none", "none", "none", "none", "Indonesia", "Indonesia", "none", "none", "LEBANON", 0),
 ("How the data got in", "by hand?", "by hand", "?", "OntoRefine", "scraping", "?", "R2RML", "?", "RML mapping", 0),
 ("Reasoner used", "none", "SWRL", "Pellet", "class rules", "Fuseki", "none", "?", "neural", "HermiT + SHACL", 0),
 ("Neural bit?", "no", "no", "CNN on your face", "no", "no", "no", "no", "graph attention", "no, future", 0),
 ("Tested properly?", "no baseline", "no", "24 people", "no", "?", "queries only", "use cases", "benchmarks", "4 ways, planned", 0),
 ("What it's really for", "problem to product", "a cream that doesn't split", "grading acne", "a routine", "Indonesian shops", "proof of concept", "animal-free safety", "predicting halal", "buying skincare in Lebanon, with a reason", 0),
]
for i, h in enumerate(H, start=1):
    c = ws.cell(row=5, column=i, value=h)
    last = i == 10
    c.font = Font(name=FONT, size=10.5, bold=True, color="4A3200" if last else PAPER)
    c.fill = PatternFill("solid", fgColor=MINEH if last else INK)
    c.alignment = Alignment(horizontal="left" if i == 1 else "center", vertical="center", wrap_text=True, indent=1)
    ws.column_dimensions[get_column_letter(i)].width = 30 if i == 1 else (28 if last else 16)
ws.row_dimensions[5].height = 40
for ri, row in enumerate(ROWS, start=6):
    key = row[-1]
    for i, val in enumerate(row[:-1], start=1):
        c = ws.cell(row=ri, column=i, value=val)
        c.border = under
        c.alignment = Alignment(horizontal="left" if i in (1, 10) else "center", vertical="center", wrap_text=True, indent=1)
        if i == 1:
            c.font = Font(name=FONT, size=10.5, bold=bool(key), color=GCOL["A"][0] if key else INK)
            c.fill = PatternFill("solid", fgColor="EDF5F3" if key else "F4F1EB")
        elif i == 10:
            c.font = Font(name=FONT, size=10.5, bold=True, color="7A5200")
            c.fill = PatternFill("solid", fgColor=MINE)
        else:
            no = str(val) in ("no", "none", "never say", "?")
            c.font = Font(name=FONT, size=10, color=SUB if no else "3A3630")
            c.fill = PatternFill("solid", fgColor="EDF5F3" if key else (ALT if ri % 2 else PAPER))
    ws.row_dimensions[ri].height = 32
r = 6 + len(ROWS) + 1
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=10)
c = ws.cell(row=r, column=1, value="  TOXIN has the law but not one product. Everyone else has products and no law. Nobody writes down who made a claim. Nobody checks if you can buy it. We are the bit in the middle.")
c.font = Font(name=FONT, size=11.5, bold=True, color=INK)
c.fill = PatternFill("solid", fgColor=MINE)
c.alignment = Alignment(vertical="center", wrap_text=True)
ws.row_dimensions[r].height = 44
ws.freeze_panes = "B6"
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 90

# ========================================================== 3. MY ONTOLOGY
ws = wb.create_sheet("My ontology")
title(ws, 12, "My ontology, drawn out",
      "Read it top to bottom. First how a product travels through, then the four modules, then one real product, then the classes the reasoner works out by itself.")
for col, w in zip("ABCDEFGHIJKL", [3, 26, 4, 26, 4, 26, 4, 26, 4, 26, 4, 3]):
    ws.column_dimensions[col].width = w

def box(ws, r, col, text, fill, fg=INK, bold=False, h=None, size=10.5, span=1):
    if span > 1:
        ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + span - 1)
    c = ws.cell(row=r, column=col, value=text)
    c.font = Font(name=FONT, size=size, bold=bold, color=fg)
    c.fill = PatternFill("solid", fgColor=fill)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border = Border(left=thick, right=thick, top=thick, bottom=thick)
    if h: ws.row_dimensions[r].height = h

def arrow(ws, r, col):
    c = ws.cell(row=r, column=col, value="→")
    c.font = Font(name=FONT, size=18, bold=True, color=SUB)
    c.alignment = Alignment(horizontal="center", vertical="center")

def label(ws, r, text, col=2, span=10):
    ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + span - 1)
    c = ws.cell(row=r, column=col, value=text)
    c.font = Font(name=FONT, size=12.5, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=INK)
    c.alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[r].height = 26

def note(ws, r, text, col=2, span=10, h=34):
    ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + span - 1)
    c = ws.cell(row=r, column=col, value=text)
    c.font = Font(name=FONT, size=10.5, italic=True, color=SUB)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    ws.row_dimensions[r].height = h

# ---- 1. the flow
r = 5
label(ws, r, "1.  How one product gets from our CSV into an answer"); r += 1
box(ws, r, 2, "ONE CSV ROW\n12,629 of them, 42 columns", "EFEAE1", h=58)
arrow(ws, r, 3)
box(ws, r, 4, "A MAPPING FILE\nsays which column becomes which property. Morph-KGC reads it and writes the triples", "EAEFF2")
arrow(ws, r, 5)
box(ws, r, 6, "GRAPHDB\none box per source: skinsort, lb-retail, lb-origin, cosing, evidence", "EFEAE1")
arrow(ws, r, 7)
box(ws, r, 8, "THE REASONER (HermiT)\nworks out which products belong to each rule-defined class", "EAEFF2")
arrow(ws, r, 9)
box(ws, r, 10, "A SPARQL QUESTION\n'oily skin, no allergens, under $20, buyable in Beirut'", MINE, fg="7A5200", bold=True)
r += 1
note(ws, r, "About 1.8 million triples. The mapping file goes in the appendix, so a reviewer can read exactly how every cell became a fact. A Python script could do the same but nobody could audit it."); r += 2

# ---- 2. the modules
label(ws, r, "2.  Four modules, because the four parts change at different speeds"); r += 1
mods = [
 ("CORE\nchanges almost never", "1F6F6B", "EEF5F4",
  ["SkinType: oily, dry, normal, combination", "Sensitivity", "SkinConcern: acne, dryness, redness, dark marks… → aligned to DermO",
   "Benefit (SKOS words, not classes)", "IngredientFunction: emollient, humectant, preservative, UV filter… names from CosIng",
   "RegulatoryStatus: banned, restricted, allowed preservative… + the 26 declarable allergens",
   "Annex II to VI (individuals, not classes)", "Authority: European Commission, SCCS, later Lebanon"]),
 ("PRODUCT\nchanges with the market", "6B4E9B", "F2EEF8",
  ["Product → Cleanser, Moisturiser (SunCare under it), Serum, Toner, Exfoliant, Mask, EyeCare, Treatment",
   "Ingredient: one per CosIng entry, named by ID not spelling", "IngredientListing: an ingredient AT A POSITION in one product",
   "Brand → linked to Wikidata", "Offer: one price, one shop, one date. Separate from the product",
   "Shop: online or physical", "Country"]),
 ("EVIDENCE\nthe contribution", "8C4A62", "FAF2F5",
  ["Claim: a statement about a product, carrying who said it, the exact sentence, the date, and how much we trust it",
   "EvidenceLevel: 1 manufacturer, 2 shop, 3 weaker source, 4 worked out from the formula",
   "prov:Agent: Manufacturer, Retailer, our own inference", "Built on PROV-O, a W3C standard. O'Sullivan 2025 did the same with LOT"]),
 ("LEBANON\nthe market", "A6612F", "FBF4EC",
  ["LebaneseShop", "ConsumerNeed: a need as its own thing. 'A routine under $20 a month'. 'Buyable in one pharmacy'. From AliCoCo",
   "The six rule-defined classes (section 4)", "Imports the other three modules"]),
]
cols = [2, 4, 6, 8]
for (head, dark, wash, items), col in zip(mods, cols):
    ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + 1)
    box(ws, r, col, head, dark, fg=PAPER, bold=True, h=40, size=11)
maxlen = max(len(m[3]) for m in mods)
for k in range(maxlen):
    rr = r + 1 + k
    for (head, dark, wash, items), col in zip(mods, cols):
        ws.merge_cells(start_row=rr, start_column=col, end_row=rr, end_column=col + 1)
        c = ws.cell(row=rr, column=col, value=("• " + items[k]) if k < len(items) else "")
        c.font = Font(name=FONT, size=10, color=INK)
        c.fill = PatternFill("solid", fgColor=wash)
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        c.border = Border(left=Side(style="thin", color=dark), right=Side(style="thin", color=dark))
    ws.row_dimensions[rr].height = 44
r = r + 1 + maxlen
note(ws, r, "Hansanie & Silva split theirs into three for the same reason and said why. MOMo, the method we follow, is built around modules. Handing a dermatologist the CORE file alone is 40 lines, not 12,629 rows."); r += 2

# ---- 3. one real product drawn
label(ws, r, "3.  One real product, drawn out. Cetaphil Moisturizing Lotion, sold by two Beirut shops"); r += 1
box(ws, r, 2, "PRODUCT\nCetaphil Moisturizing Lotion\nbrand → Cetaphil → Galderma (Wikidata)", "F2EEF8", bold=True, h=70)
arrow(ws, r, 3)
box(ws, r, 4, "hasListing → INGREDIENT LISTING\nNiacinamide, position 3\n→ Ingredient (CosIng 28769)\n→ function: skin conditioning\n→ restricted under: none", "EEF5F4")
arrow(ws, r, 5)
box(ws, r, 6, "hasListing → INGREDIENT LISTING\nPhenoxyethanol, position 11\n→ Ingredient (CosIng 122-99-6)\n→ function: preservative\n→ restricted under Annex V/29, according to European Commission", "EEF5F4")
arrow(ws, r, 7)
box(ws, r, 8, "hasClaim → CLAIM\n'suitable for sensitive skin'\nsaid by: Cetaphil (manufacturer)\nlevel 1\nread on cetaphil.com, 2026-03-14", "FAF2F5")
arrow(ws, r, 9)
box(ws, r, 10, "offers → OFFER $8.66\nseller: Sohati, 2026-03-14\n\noffers → OFFER $32.36\nseller: Feel22, 2026-03-14", "FBF4EC")
r += 1
note(ws, r, "Three things a spreadsheet cannot do here. The ingredient carries its POSITION (INCI order is concentration order). The claim carries WHO said it and how much we trust them. And the price sits on the OFFER, not the product, so one lotion holds two Beirut prices at once."); r += 2

# ---- 4. defined classes
label(ws, r, "4.  Six classes we never fill in by hand. We write the rule once, the reasoner finds the members."); r += 1
DEF = [
 ("SensitiveSafeProduct", "no ingredient is one of the 26 declarable allergens", "about 9,537"),
 ("AvailableInLebanon", "at least one offer from a Lebanese shop", "about 11,937"),
 ("ManufacturerStatedProduct", "its suitability claim is level 1", "about 4,460"),
 ("RegulatedProduct", "at least one restricted ingredient", "about 9,613"),
 ("FullyIdentifiedProduct", "every ingredient found in the register", "about 9,032"),
 ("NaturalClaimProduct", "marketed as natural. Built to test Klaschka's finding that 56% of natural INCI substances are classed hazardous", "to measure"),
]
for i, h in enumerate(["The class", "The rule, in words", "How many we expect"]):
    col = [2, 4, 8][i]; span = [2, 4, 4][i]
    ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + span - 1)
    c = ws.cell(row=r, column=col, value=h)
    c.font = Font(name=FONT, size=10.5, bold=True, color="4A3200")
    c.fill = PatternFill("solid", fgColor=MINEH)
    c.alignment = Alignment(vertical="center", indent=1)
ws.row_dimensions[r].height = 24; r += 1
for name, rule, n in DEF:
    for i, v in enumerate([name, rule, n]):
        col = [2, 4, 8][i]; span = [2, 4, 4][i]
        ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + span - 1)
        c = ws.cell(row=r, column=col, value=v)
        c.font = Font(name=FONT, size=10.5, bold=(i == 0), color="7A5200" if i == 0 else INK)
        c.fill = PatternFill("solid", fgColor=MINE if i == 0 else PAPER)
        c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
        c.border = under
    ws.row_dimensions[r].height = 30; r += 1
note(ws, r, "This is Abesova's trick. We PREDICT each number first, then run the reasoner. If SensitiveSafeProduct does not land near 9,537, the model is wrong and we want to know now. Expect the 593 sensitive-skin products that contain an allergen to show up as a contradiction. That is a finding, not a bug.", h=44)
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 90

# ================================================================ 4. TOOLS
ws = wb.create_sheet("Tools")
title(ws, 7, "Every tool named in this workbook",
      "What it is, what it does, where to get it, whether we use it, and why. Grouped by the job it does.")
TH = [("Tool", 22), ("What it is, in one line", 44), ("What it does", 46), ("Link", 36), ("Do we use it?", 14), ("Why, or why not", 52)]
for i, (h, w) in enumerate(TH, start=2):
    c = ws.cell(row=5, column=i, value=h)
    c.font = Font(name=FONT, size=10.5, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=INK)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    ws.column_dimensions[get_column_letter(i)].width = w
ws.column_dimensions["A"].width = 3
ws.row_dimensions[5].height = 30

TOOLS = [
 ("THE LANGUAGES", None),
 ("RDF", "The rule that all data is made of three-part sentences: subject, predicate, object", "Lets you add any new fact without changing a schema. 'Cetaphil contains Phenoxyethanol' is one triple", "w3.org/TR/rdf11-primer", "YES", "It is what an ontology is written in. No choice here"),
 ("Turtle (.ttl)", "The readable way of writing RDF", "Our ontology file. Diffs cleanly in git", "w3.org/TR/turtle", "YES", "Readable by humans, which the other formats are not"),
 ("OWL", "RDF plus real logic", "Lets you say 'a sensitive-safe product is any product with no allergens' and have software work out who qualifies", "w3.org/TR/owl2-primer", "YES", "The defined classes need it. This is what makes it an ontology and not a spreadsheet"),
 ("SPARQL", "The query language for graphs. SQL for RDF. Say 'sparkle'", "Answers questions like 'oily skin, no allergens, under $20, in Beirut'. Abesova, bit-Tech, TOXIN and FoodKG all use it", "w3.org/TR/sparql11-query", "YES", "Our 15 competency questions are each one SPARQL query"),
 ("SWRL", "If-then rules for what OWL cannot say", "OntoCosmetic writes its formulation rules in it. 'If product has a declarable allergen then not for sensitive skin'", "w3.org/submissions/SWRL", "MAYBE", "Only for two rules. It slows reasoning, and HermiT ignores it silently, so we would switch to Openllet"),
 ("SHACL", "Checks the data obeys rules. OWL says what follows, SHACL says what MUST be true", "'Every product must have exactly one brand.' Our validate_dataset.py, moved onto the graph", "w3.org/TR/shacl", "YES", "OWL assumes anything unsaid might be true, so it cannot enforce. SHACL can"),
 ("R2RML / RML / YARRRML", "A file that says 'this column becomes this property'. R2RML is for databases, RML adds CSV, YARRRML is RML in readable YAML", "TOXIN used R2RML to turn Excel into a graph. This is how our CSV becomes triples", "rml.io", "YES", "A mapping file goes in the appendix and can be audited. A script cannot"),
 ("EDITORS AND LIBRARIES", None),
 ("Protégé", "The free desktop editor from Stanford. Everyone uses it", "Build classes by clicking, press the reasoner button, screenshot the hierarchy. Moe, OntoCosmetic, Hansanie and COPPER all used it", "protege.stanford.edu", "YES", "Standard, and reasoners are built in. But keep the Turtle file in git as the real master"),
 ("Owlready2", "A Python library for ontologies", "Load the ontology, add facts, run a reasoner from code. Hansanie & Silva used it", "owlready2.readthedocs.io", "YES", "Our whole pipeline is Python"),
 ("RDFLib", "A Python library for plain RDF and SPARQL", "Read and write triples, run queries, from Python", "rdflib.readthedocs.io", "YES", "Same reason. Pairs with Owlready2"),
 ("CoModIDE", "A drawing tool for ontology modules, made for the MOMo method", "Draw the module, get the OWL", "comodide.com", "MAYBE", "Nice for the diagrams the chapter needs. Not essential"),
 ("Tkinter", "Python's basic window toolkit", "Hansanie & Silva built their desktop app with it", "docs.python.org/3/library/tkinter.html", "NO", "We are not building a desktop app"),
 ("REASONERS", None),
 ("HermiT", "A reasoner. Reads the ontology and works out what follows, and finds contradictions", "Fills the defined classes. Flags the 593 sensitive-skin products that contain an allergen", "hermit-reasoner.com", "YES", "Ships with Protégé, solid default. Does NOT run SWRL rules"),
 ("Pellet / Openllet", "Another reasoner. Openllet is the maintained version", "Same job, but it also runs SWRL rules. Hansanie & Silva used Pellet", "github.com/Galigator/openllet", "MAYBE", "Only if we write SWRL rules"),
 ("ELK", "A very fast reasoner for a simple subset of OWL", "Used by the big biomedical ontologies", "github.com/liveontologies/elk-reasoner", "NO", "Too limited for our defined classes"),
 ("DATABASES", None),
 ("GraphDB", "A database for triples with SPARQL on the front and a picture of the graph", "Stores our 1.8 million triples in named boxes per source. Abesova used it", "graphdb.ontotext.com", "YES", "Free desktop edition, reasoning built in, and the visual explorer is worth more in a meeting than any paragraph"),
 ("Apache Jena Fuseki", "A free, simpler triple store", "Same job as GraphDB. bit-Tech used it", "jena.apache.org/documentation/fuseki2", "NO", "Simpler, but its reasoning is weak and it has no visual explorer. GraphDB does more for the same price"),
 ("Stardog / Virtuoso", "Commercial triple stores. Virtuoso runs DBpedia itself", "Same job, bigger scale", "stardog.com, virtuoso.openlinksw.com", "NO", "We do not need the scale and Stardog costs money"),
 ("OntoRefine", "A point-and-click tool inside GraphDB that turns a CSV into triples", "Abesova's team used it to map Sephora columns to classes", "graphdb.ontotext.com/documentation", "NO", "Good, but the mapping is trapped inside GraphDB. Morph-KGC's mapping is a file we can put in the appendix"),
 ("Morph-KGC", "The Python engine that reads an RML mapping and writes the triples", "One command turns our CSV into the graph. Rerun it whenever the data changes", "morph-kgc.readthedocs.io", "YES", "Python, fast on big CSVs, and the mapping is auditable. This is our population tool"),
 ("VOCABULARIES WE REUSE", None),
 ("schema.org", "The vocabulary Google uses for products and shops", "Gives us Product, Offer, price, brand, seller. Splits the product from the offer, which is how one lotion holds two prices", "schema.org", "YES", "Everyone understands it already. No point inventing our own word for 'price'"),
 ("PROV-O", "A W3C standard for saying where information came from", "wasAttributedTo, wasDerivedFrom, generatedAtTime. Our four evidence levels in a language other people speak", "w3.org/TR/prov-o", "YES", "Turns our most original design choice into a standard one. O'Sullivan 2025 did exactly this"),
 ("SKOS", "For lists of words that are labels, not objects", "Our benefits: 'Hydrating' and 'Hydration' become one concept with two labels", "w3.org/TR/skos-reference", "YES", "Benefits are terms people use, not logical classes"),
 ("Dublin Core", "The basic bookkeeping vocabulary: title, creator, licence, date", "Makes the dataset and ontology citable", "dublincore.org", "YES", "Cheap and expected"),
 ("OUTSIDE DATA WE LINK TO", None),
 ("CosIng", "The European Commission's official cosmetic ingredient register, 28,573 entries", "Our ingredients get a legal status from it. Already linked on 99.2% of products with a formula", "ec.europa.eu/growth/tools-databases/cosing", "YES", "It is the whole point"),
 ("CosIng-KG", "CosIng already converted to RDF, on GitHub", "Could be our entire ingredient layer for free", "github.com/biobricks-ai/cosing-kg", "CHECK FIRST", "If usable, we cite it and save weeks. If not, our own conversion is a contribution"),
 ("DermO", "3,000 skin disease terms written by dermatologists, on BioPortal", "Our concerns (eczema, rosacea, acne) point at real clinical terms aligned to ICD-10", "bioportal.bioontology.org/ontologies/DERMO", "YES", "Six lines of alignment fix the fact that no clinician has checked our vocabulary"),
 ("Wikidata", "Wikipedia's facts as a queryable graph", "Tells us who owns each brand. L'Oreal owns 570 of our products", "wikidata.org", "YES", "One line per brand, and we get ownership and country for free"),
 ("DBpedia", "Wikipedia turned into a graph, older cousin of Wikidata", "Abesova pulled countries and map coordinates from it", "dbpedia.org", "MAYBE", "Wikidata is better maintained now"),
 ("BioPortal / OBO Foundry", "Where biomedical ontologies live. OBO is the community with shared rules", "DermO is on BioPortal. TOXIN reused TXPO from OBO", "bioportal.bioontology.org", "YES", "We fetch DermO from here"),
 ("Linked Open Vocabularies (LOV)", "A search engine for existing vocabulary terms", "Search 'price' before inventing skc:price", "lov.linkeddata.es", "YES", "The one habit that separates an amateur ontology from a professional one"),
 ("CHECKING AND PUBLISHING", None),
 ("OOPS!", "A free website that checks your ontology against 41 known design mistakes", "Paste the file, get a graded list: critical, important, minor", "oops.linkeddata.es", "YES", "One afternoon for a real evaluation number nobody in group A has"),
 ("FOOPS!", "A free website that scores how FAIR your ontology is (findable, accessible, interoperable, reusable)", "24 checks, a score, and what is missing", "w3id.org/foops", "YES", "We criticise everyone for not publishing, so we measure our own"),
 ("OntoMetrics", "Structural numbers: depth, breadth, richness", "Comparable figures for the evaluation table", "ontometrics.uni-rostock.de", "YES", "Cheap and standard"),
 ("WIDOCO", "Makes a documentation web page from the ontology file", "So the docs cannot drift from the code", "github.com/dgarijo/Widoco", "YES", "Free, and it is what the w3id address will point at"),
 ("w3id.org", "A permanent web address for your ontology", "Survives you leaving BAU. It is a pull request on GitHub", "w3id.org", "YES", "A university URL dies when you graduate"),
 ("Zenodo", "Gives a DOI to each release", "The ontology becomes citable like a paper", "zenodo.org", "YES", "One in six competitors publishes. This is how we do it properly"),
 ("METHODS", None),
 ("METHONTOLOGY", "An older, document-heavy method: glossary, taxonomies, relation diagrams, concept dictionary", "The default in this field. bit-Tech, Utari and Mahadewi all use it. Moe & Aung follow it without naming it", "search: METHONTOLOGY Fernandez-Lopez 1997", "NO", "Thorough but old. We take its glossary step and use MOMo + LOT instead, with a stated reason"),
 ("MOMo", "Modular Ontology Modeling. Build in modules using design patterns, draw before you write", "Our four-module design follows it", "search: Shimizu Modular Ontology Modeling 2022", "YES", "Names four reasons reuse fails and we have hit three of them"),
 ("LOT", "Linked Open Terms. Four steps: requirements, build, publish, maintain", "Our project structure and publication discipline", "lot.linkeddata.es", "YES", "Built around reusing terms and publishing, which are the two things this field is worst at"),
 ("Ontology Development 101", "Noy & McGuinness 2001, the seven-step teaching guide", "Its class-vs-individual test told us Annex entries are individuals", "protege.stanford.edu/publications/ontology_development/ontology101.pdf", "CITE", "Everyone cites it. Too light to be our only method"),
 ("Competency questions", "Questions the ontology must be able to answer, written BEFORE building", "Our 15 questions become our 15 SPARQL queries become our evaluation chapter. COPPER did the same", "in 06_ontology_master_plan.md", "YES", "Turns 'is it good' into something measurable"),
 ("THINGS THE PAPERS USED THAT WE DON'T", None),
 ("CCBR", "Conversational case-based reasoning. Narrow a problem by asking questions, like a doctor", "Moe & Aung: six questions turn 'I have acne' into 'papules'", "in the Moe & Aung paper", "NO", "Needs a hand-built case base and a dermatologist"),
 ("Ford-Fulkerson", "A maximum-flow algorithm. Water through pipes", "Moe & Aung score products by how much flow reaches them", "search: Ford-Fulkerson algorithm", "NO", "A weighted filter does the same for us with less machinery"),
 ("CNN", "Convolutional neural network, a model that reads images", "Hansanie & Silva grade acne from a photo. Lee et al. read the face", "search: convolutional neural network", "NO", "No photos, no ethics approval. Could plug in later"),
 ("Graph attention network", "A neural net that passes messages between connected nodes", "HaCKG predicts halal status with one", "search: relational graph attention network", "NO", "Future work. Needs interaction data"),
 ("AHP", "Analytic Hierarchy Process. Weigh several criteria by comparing them in pairs", "Formultools ranks ingredients on performance, origin and price with it", "search: Saaty AHP 1987", "MAYBE", "Could rank products on price, availability and evidence. Not needed yet"),
 ("AttrakDiff / SUS", "Standard questionnaires for user experience and usability", "Formultools used AttrakDiff between iterations. Mahadewi reported SUS 82", "attrakdiff.de, search: System Usability Scale", "MAYBE", "If we ever build an interface. Cheap and standard"),
 ("Precision, recall, F-measure, MAE", "Standard accuracy measures", "Moe & Aung, Hansanie, E-Prod and Mahadewi all report some of these", "any ML textbook", "NO", "FEVR says match the evaluation to the goal. Ours is verifiable correctness, so competency questions and consistency instead"),
 ("Slope One", "A simple collaborative filtering algorithm", "Mahadewi predicts ratings with it", "search: Slope One", "NO", "Needs a ratings matrix we do not have"),
 ("SMILES", "A text way of writing a molecule's structure", "TOXIN adds it so every chemical has one identity", "search: SMILES chemistry", "NO", "We have CAS numbers from CosIng, same job"),
 ("TXPO", "The ToXic Process Ontology from OBO Foundry", "TOXIN's backbone ontology", "obofoundry.org", "NO", "Too deep into toxicology mechanisms for us"),
]
r = 6
for row in TOOLS:
    if row[1] is None:                                   # section
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
        c = ws.cell(row=r, column=2, value="  " + row[0])
        c.font = Font(name=FONT, size=11, bold=True, color=PAPER)
        c.fill = PatternFill("solid", fgColor=GCOL["C"][0])
        c.alignment = Alignment(vertical="center")
        ws.row_dimensions[r].height = 24
        r += 1
        continue
    for i, val in enumerate(row, start=2):
        c = ws.cell(row=r, column=i, value=val)
        c.border = under
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        if i == 2:
            c.font = Font(name=FONT, size=10.5, bold=True, color=INK)
            c.fill = PatternFill("solid", fgColor="F4F1EB")
        elif i == 5:
            c.font = Font(name=FONT, size=9, color="2166A5", underline="single")
            c.fill = PatternFill("solid", fgColor=PAPER)
        elif i == 6:
            v = str(val).upper()
            colr = {"YES": "1F6F6B", "NO": SUB, "MAYBE": "A6612F", "CHECK FIRST": FLAGT, "CITE": "6B4E9B"}.get(v, INK)
            fill = {"YES": "EDF5F3", "NO": PAPER, "MAYBE": "FBF4EC", "CHECK FIRST": FLAG, "CITE": "F2EEF8"}.get(v, PAPER)
            c.font = Font(name=FONT, size=10.5, bold=True, color=colr)
            c.fill = PatternFill("solid", fgColor=fill)
            c.alignment = Alignment(horizontal="center", vertical="top")
        else:
            c.font = Font(name=FONT, size=10, color="3A3630")
            c.fill = PatternFill("solid", fgColor=PAPER)
    ws.row_dimensions[r].height = 46
    r += 1
ws.freeze_panes = "C6"
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 90

# ---------------------------------------------------------------- save
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PAPERS_TABLE.xlsx")
wb.save(out)
print("written:", out)
print(f"{len(PAPERS)} papers, {len(COLS)} columns, {len(wb.sheetnames)} sheets:", wb.sheetnames)
print("tools listed:", sum(1 for t in TOOLS if t[1] is not None))
