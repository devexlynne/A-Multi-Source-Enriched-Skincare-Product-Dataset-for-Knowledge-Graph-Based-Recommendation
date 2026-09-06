"""
Builds PAPERS_TABLE.xlsx

Everything I read for the ontology chapter. 59 papers, 38 columns, 7 sheets.
The paper text lives in papers_data.py; this file is only the look of it.

Run:  py build_papers_table.py
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from papers_data import COLS, PAPERS as P

# ---------------------------------------------------------------- palette
# Warm and low contrast. Nothing shouts except the things that should.
INK    = "2E2A25"   # soft near-black, warm
PAPER   = "FFFFFF"
ALT     = "FBFAF7"   # barely-there stripe
LINE    = "E8E2D8"   # hairline
SUB     = "8A8175"   # muted text
MINE    = "FFF6E0"   # my own columns
MINE_HD = "E8A33D"   # and their header
FLAG    = "FCEEE6"   # things I must not forget
FLAGTXT = "A83A1E"

TRACK = {                       # dot colour, soft row wash
 "B": ("1F6F6B", "F0F6F5"),     # skincare ontologies, teal
 "C": ("8C4A62", "FAF2F5"),     # recommenders, rose
 "D": ("A6612F", "FBF4EC"),     # deep learning, amber
 "E": ("40518F", "F1F3FA"),     # hybrid, indigo
 "F": ("5F6B31", "F5F6EE"),     # tools, olive
}
GROUP = {                        # header wash per column group
 "Basics":           "EFEAE1",
 "The paper itself": "EAEFF2",
 "What it's about":  "EFEAE1",
 "Their data":       "EAEFF2",
 "Their ontology":   "EFEAE1",
 "Filling it up":    "EAEFF2",
 "How it works":     "EFEAE1",
 "Did it work?":     "EAEFF2",
 "For my thesis":    MINE,
}
FONT = "Calibri"

hair = Side(style="thin", color=LINE)
under = Border(bottom=hair)          # rows get a bottom rule only, no boxes
nolines = Border()


def banner(ws, span, title, sub, tag=None):
    """Title block. Colour band, then one line of me talking."""
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    c = ws.cell(row=1, column=1, value="  " + title)
    c.font = Font(name=FONT, size=18, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=INK)
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 40

    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=span)
    c = ws.cell(row=2, column=1, value="  " + sub)
    c.font = Font(name=FONT, size=11, color=SUB, italic=True)
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[2].height = 24

    if tag:
        ws.merge_cells(start_row=3, start_column=1, end_row=3, end_column=span)
        c = ws.cell(row=3, column=1, value="  " + tag)
        c.font = Font(name=FONT, size=10.5, bold=True, color=FLAGTXT)
        c.fill = PatternFill("solid", fgColor=FLAG)
        c.alignment = Alignment(vertical="center")
        ws.row_dimensions[3].height = 22
    ws.row_dimensions[4].height = 8      # breathing room


wb = Workbook()

# ============================================================ 1. START HERE
ws = wb.active
ws.title = "Start here"
banner(ws, 3, "Everything I read for the ontology",
       "Lynne · MSc thesis, Beirut Arab University · September 2026")
ws.column_dimensions['A'].width = 4
ws.column_dimensions['B'].width = 26
ws.column_dimensions['C'].width = 112

INTRO = [
 ("What this is",
  "Every paper I found while working out how to build the ontology. 59 of them. I put it all in one file "
  "so nobody has to read 59 PDFs to find out that most of them don't solve our problem."),
 ("How I found them",
  "Two rounds. First I searched the normal web. Then I searched a proper academic index (Semantic Scholar, "
  "PubMed, Scopus, arXiv) and it found nine papers I'd completely missed, plus two of my citations were "
  "wrong. That's why there's a column saying whether I read the full paper or just the abstract."),
 ("The five tracks",
  "B is ontologies for skincare and cosmetics. These are the ones we're actually competing with.   "
  "C is ontology recommenders in other areas like food and shopping, where I stole most of the ideas.   "
  "D is deep learning, which is the thing people will ask why we're not doing.   "
  "E is mixing graphs with neural networks, which is our future work.   "
  "F is methods and tools, meaning how to actually build the thing."),
 ("Which sheet to open",
  "'The papers' is the big one. 'Head to head' is only the skincare ontologies compared, and it's the one "
  "to put on a screen in a meeting. 'My ontology' is every class and property I plan to build. 'Tools' is "
  "what to install. 'Roadmap' is the six steps. 'The gap' is the whole argument on one page."),
 ("How to read the big sheet",
  "Columns are grouped, and each group has its own shade. The cream ones on the far right are the only "
  "ones about US. Everything left of those is about them. If you're in a hurry: read 'How much I care', "
  "the title, and the cream columns."),
 ("The one thing to know",
  "Somebody reviewed 28 ontology recommender papers and found they hardly ever name a proper method for "
  "building the ontology, and that NOT ONE of the 28 said how they evaluated it. Not one. So naming our "
  "method and actually testing our ontology isn't us being tidy. In this field it counts as a contribution."),
 ("Our gap, in one line",
  "Nobody has ingredients tied to actual EU law AND real products AND a record of where each claim came "
  "from. The one graph that links cosmetic ingredients to EU law has zero products in it. Everyone else "
  "has products and no law. That empty space is us."),
 ("What's still missing",
  "I don't have the full PDF of the Indonesian 2025 paper, which is our closest competitor. Five papers "
  "I only read the abstract of, and they're marked. Citation counts are from September 2026 so they'll "
  "drift."),
]
r = 6
for h, t in INTRO:
    c = ws.cell(row=r, column=2, value=h)
    c.font = Font(name=FONT, size=12, bold=True, color=TRACK["B"][0])
    c.alignment = Alignment(vertical="top", wrap_text=True)
    c = ws.cell(row=r, column=3, value=t)
    c.font = Font(name=FONT, size=11, color="333029")
    c.alignment = Alignment(vertical="top", wrap_text=True)
    ws.cell(row=r + 1, column=2).border = under
    ws.cell(row=r + 1, column=3).border = under
    ws.row_dimensions[r].height = 56
    ws.row_dimensions[r + 1].height = 8
    r += 2
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 100

# ============================================================ 2. THE PAPERS
ws = wb.create_sheet("The papers")
NC = len(COLS)
banner(ws, NC, "The papers",
       "59 of them. Grouped columns, one shade per group. The cream ones on the right are about us.",
       "Short of time? Read column D, column E, and the cream ones.")

GR, HR = 5, 6
ci, prev, start = 1, None, 1
for grp, hdr, w in list(COLS) + [("__end__", "", 0)]:
    if prev is not None and grp != prev:
        ws.merge_cells(start_row=GR, start_column=start, end_row=GR, end_column=ci - 1)
        c = ws.cell(row=GR, column=start, value=prev.upper())
        c.font = Font(name=FONT, size=10, bold=True,
                      color=INK if prev != "For my thesis" else "7A5200")
        c.fill = PatternFill("solid", fgColor=GROUP[prev])
        c.alignment = Alignment(horizontal="center", vertical="center")
        start = ci
    prev = grp
    ci += 1
ws.row_dimensions[GR].height = 22

for i, (grp, hdr, w) in enumerate(COLS, start=1):
    c = ws.cell(row=HR, column=i, value=hdr)
    mine = grp == "For my thesis"
    c.font = Font(name=FONT, size=10.5, bold=True, color="4A3200" if mine else PAPER)
    c.fill = PatternFill("solid", fgColor=MINE_HD if mine else INK)
    c.alignment = Alignment(horizontal="left", vertical="center", wrap_text=True, indent=1)
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[HR].height = 44

HOT = ("URGENT", "CITE IN INTRO", "CHECK FIRST", "TEMPLATE", "THE BRIDGE", "MY ", "RUN IT")

for ri, row in enumerate(P, start=HR + 1):
    trk = row[1]
    dot, wash = TRACK.get(trk, (INK, PAPER))
    stripe = (ri % 2 == 0)
    for i, val in enumerate(row, start=1):
        grp = COLS[i - 1][0]
        c = ws.cell(row=ri, column=i, value=val)
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        c.border = under
        if i == 2:                                    # the track dot
            c.value = "●"
            c.font = Font(name=FONT, size=16, color=dot)
            c.fill = PatternFill("solid", fgColor=wash)
            c.alignment = Alignment(horizontal="center", vertical="center")
        elif i == 3:                                  # short name
            c.font = Font(name=FONT, size=11.5, bold=True, color=dot)
            c.fill = PatternFill("solid", fgColor=wash)
            c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
        elif i == 4:                                  # how much I care
            hot = any(k in str(val).upper() for k in HOT)
            c.font = Font(name=FONT, size=10, bold=hot, color=FLAGTXT if hot else SUB)
            c.fill = PatternFill("solid", fgColor=FLAG if hot else (ALT if stripe else PAPER))
            c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
        elif i == 5:                                  # title
            c.font = Font(name=FONT, size=10.5, bold=True, color=INK)
            c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
        elif i == 12:                                 # link
            c.font = Font(name=FONT, size=9, color="2166A5", underline="single")
            c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
        elif i == 18:                                 # can I download it
            yes = str(val).upper().startswith("YES")
            c.font = Font(name=FONT, size=10, bold=yes, color=TRACK["B"][0] if yes else SUB)
            c.fill = PatternFill("solid", fgColor="EDF5F3" if yes else (ALT if stripe else PAPER))
        elif grp == "For my thesis":
            c.font = Font(name=FONT, size=10, color="3A3226")
            c.fill = PatternFill("solid", fgColor=MINE)
        else:
            c.font = Font(name=FONT, size=10, color="3A3630")
            c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
    ws.row_dimensions[ri].height = 112

ws.freeze_panes = "E7"
ws.auto_filter.ref = f"A{HR}:{get_column_letter(NC)}{HR + len(P)}"
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 80

# ========================================================= 3. HEAD TO HEAD
ws = wb.create_sheet("Head to head")
banner(ws, 10, "Us against the ones doing the same thing",
       "Only the skincare ontologies. Look at the last column, then try to find another one like it.",
       "The three highlighted rows are the whole thesis.")

H = ["What I'm comparing", "Moe\n2014", "OntoCosmetic\n2021/23", "Hansanie\n2024",
     "Abesova\n2023", "Indonesian\n2025", "Utari\n2023", "TOXIN\n2025",
     "HaCKG\n2025", "WHAT WE'RE DOING"]
ROWS = [
 ("Is it properly peer reviewed", "weak journal", "yes", "yes", "no, it's a student project",
  "yes", "yes", "yes", "yes", "will be", False),
 ("Can anyone actually download it", "no", "YES", "no", "no", "don't know", "no",
  "YES", "don't know", "yes, that's the plan", False),
 ("Did they follow a named method", "eight steps, unnamed", "no", "no", "middle out",
  "METHONTOLOGY", "METHONTOLOGY", "no", "no", "MOMo + LOT", False),
 ("How many products", "they never say", "279", "they never say", "some Sephora ones",
  "3,800", "62", "none at all", "some", "12,629", False),
 ("Ingredients tied to actual EU law", "no", "no", "no", "no", "no", "no", "YES",
  "no", "YES, all 28,573 CosIng entries", True),
 ("Do they say who claimed what", "no", "only for their rules", "no", "no", "no", "no",
  "yes, by source", "no", "YES, four evidence levels", True),
 ("Do they know if you can buy it", "a price band, that's all", "price as one criterion",
  "no", "a shop link", "no", "no", "no", "no", "YES, per shop, in two currencies", True),
 ("Which country's market", "none", "none", "none", "none", "Indonesia", "Indonesia",
  "none", "none", "LEBANON", False),
 ("Is there a neural bit", "no", "no", "CNN reads your face", "no", "no", "no", "no",
  "graph neural net", "no, that's future work", False),
 ("Did they properly test it", "no baseline", "no", "asked 24 people", "no", "unclear",
  "ran some queries", "use cases", "benchmarks", "yes, four different ways", False),
 ("What it's really for", "matching problems to products", "making a cream that doesn't split",
  "grading acne from a photo", "building a routine", "Indonesian shopping",
  "proving it can be done", "animal-free safety testing", "predicting halal",
  "buying skincare in Lebanon, with a reason", False),
]
for i, h in enumerate(H, start=1):
    c = ws.cell(row=6, column=i, value=h)
    last = i == 10
    c.font = Font(name=FONT, size=10.5, bold=True, color="4A3200" if last else PAPER)
    c.fill = PatternFill("solid", fgColor=MINE_HD if last else INK)
    c.alignment = Alignment(horizontal="left" if i == 1 else "center",
                            vertical="center", wrap_text=True, indent=1)
    ws.column_dimensions[get_column_letter(i)].width = 32 if i == 1 else (30 if last else 17)
ws.row_dimensions[6].height = 42

for ri, row in enumerate(ROWS, start=7):
    key = row[-1]
    for i, val in enumerate(row[:-1], start=1):
        c = ws.cell(row=ri, column=i, value=val)
        c.border = under
        c.alignment = Alignment(horizontal="left" if i in (1, 10) else "center",
                                vertical="center", wrap_text=True, indent=1)
        if i == 1:
            c.font = Font(name=FONT, size=10.5, bold=key, color=TRACK["B"][0] if key else INK)
            c.fill = PatternFill("solid", fgColor="EDF5F3" if key else "F4F1EB")
        elif i == 10:
            c.font = Font(name=FONT, size=10.5, bold=True, color="7A5200")
            c.fill = PatternFill("solid", fgColor=MINE)
        else:
            no = str(val) in ("no", "none", "they never say")
            c.font = Font(name=FONT, size=10, color=SUB if no else "3A3630")
            c.fill = PatternFill("solid", fgColor="EDF5F3" if key else
                                 (ALT if ri % 2 == 0 else PAPER))
    ws.row_dimensions[ri].height = 34

r = 7 + len(ROWS) + 1
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=10)
c = ws.cell(row=r, column=1, value=
  "  The three green rows are the point. TOXIN has the EU law but not a single product. Everyone else has "
  "products and no law. And nobody at all writes down who made a claim, or checks whether you can buy the "
  "thing where you live.")
c.font = Font(name=FONT, size=12, bold=True, color=INK)
c.fill = PatternFill("solid", fgColor=MINE)
c.alignment = Alignment(vertical="center", wrap_text=True)
ws.row_dimensions[r].height = 46
ws.freeze_panes = "B7"
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 90

# ========================================================== 4. MY ONTOLOGY
ws = wb.create_sheet("My ontology")
banner(ws, 6, "What I'm actually going to build",
       "Four modules. Every class and property, where I got it from, and which of my 42 columns it holds.")
oc = [("Module", 16), ("Kind of thing", 15), ("Name", 28),
      ("What it means, in normal words", 60), ("Where I got it from", 32),
      ("Which of my columns", 28)]
for i, (h, w) in enumerate(oc, start=1):
    c = ws.cell(row=6, column=i, value=h)
    c.font = Font(name=FONT, size=10.5, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=INK)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[6].height = 28

ONT = [
 ("core","Class","SkinType","Oily, dry, normal, combination","Hansanie & Silva, and Abesova","skin_type"),
 ("core","Class","Sensitivity","Sensitive or not","Ours","sensitivity"),
 ("core","Class","SkinConcern","Acne, dryness, redness, dark marks, wrinkles, dullness, pores, oiliness","Ours, but I want to line these up with DermO","concerns"),
 ("core","SKOS concept","Benefit","Hydrating, brightening, soothing. These are just words people use, not logical classes, so SKOS not OWL","SKOS","benefits"),
 ("core","Class","IngredientFunction","What an ingredient does: emollient, humectant, preservative, UV filter, surfactant, antioxidant, solvent, and so on","Names come straight from CosIng","ingredient_functions"),
 ("core","Class","RegulatoryStatus","Banned (Annex II), restricted (III), allowed colorant (IV), preservative (V), UV filter (VI), and the 26 allergens you must declare","EU Regulation 1223/2009","restricted_ingredients"),
 ("core","Individual","Annex","AnnexII through AnnexVI. These are specific entries, not kinds of thing, so they're individuals not classes","The Noy & McGuinness rule of thumb","restricted_ingredients"),
 ("core","Class","Authority","European Commission, SCCS, and later maybe the Lebanese Ministry of Health. Somebody always GRANTS a status","Borrowed from the halal flavouring ontology","new"),
 ("product","Class","Product","The thing on the shelf. Underneath: Cleanser, Moisturiser (with SunCare under it), Serum, Toner, Exfoliant, Mask, EyeCare, Treatment","schema:Product, and the breakdown from Abesova","product_type"),
 ("product","Class","Ingredient","One per CosIng entry, named by its register ID and not by its spelling","CosIng","ingredients"),
 ("product","Class","IngredientListing","An ingredient AT A POSITION in one product's list. We need this because INCI order tells you roughly how much is in there, and a plain triple has nowhere to put the position","The n-ary relation design pattern","ingredients"),
 ("product","Class","Brand","Who makes it","schema:Brand, linked out to Wikidata","brand"),
 ("product","Class","Offer","One price, one shop, one date. Kept SEPARATE from the product, which is how one lotion holds two Beirut prices at once","schema:Offer","price_usd, price_lbp, price_seen_date"),
 ("product","Class","Shop","Online or a real shop","schema.org plus ours","shops_in_lebanon"),
 ("product","Class","Country","Where a brand or a shop is","schema.org","country"),
 ("evidence","Class","Claim","A statement about a product carrying who said it, where, when, the exact sentence, and how much that source is worth. THIS IS THE CONTRIBUTION","PROV-O, specialised. O'Sullivan 2025 did the same thing","skin_type_source, price_source"),
 ("evidence","Class","EvidenceLevel","Manufacturer said it (1), a shop said it (2), something weaker said it (3), we worked it out from the formula (4)","Ours","skin_type_source"),
 ("evidence","Class","prov:Agent","Whoever made the claim: a manufacturer, a retailer, or our own inference","PROV-O","all the source columns"),
 ("lebanon","Class","LebaneseShop","A shop that actually sells here","Ours","shops_in_lebanon"),
 ("lebanon","Class","ConsumerNeed","A need as its own thing, not an attribute. A routine under $20 a month. One you can buy in a single pharmacy. One for humid summer","AliCoCo, SIGMOD 2020","new, this is our original bit"),
 ("--","--","--","--","--","--"),
 ("product","Object property","skc:hasListing","Product to one positioned ingredient entry","n-ary pattern","ingredients"),
 ("product","Object property","skc:listsIngredient","Which ingredient that entry points to","Ours","ingredients"),
 ("product","Object property","skc:hasIngredient","Shortcut straight to the ingredient, so easy questions stay easy","Ours, worked out by the reasoner","ingredients"),
 ("core","Object property","skc:hasFunction","What the ingredient does","CosIng","ingredient_functions"),
 ("core","Object property","skc:restrictedUnder","Which annex restricts it","EU Regulation 1223/2009","restricted_ingredients"),
 ("core","Object property","skc:accordingTo","WHO says so. Leaves the door open for Lebanese rules later","The halal ontology pattern","new"),
 ("product","Object property","skc:suitableFor","Product suits a skin type","Hansanie & Silva","skin_type"),
 ("product","Object property","skc:addressesConcern","Product helps with a concern","Ours","concerns"),
 ("product","Object property","schema:offers","Product to Offer","schema.org","price columns"),
 ("product","Object property","schema:seller","Offer to Shop. Note the price sits on the OFFER, not the product","schema.org","sold_by_shops"),
 ("evidence","Object property","skc:hasClaim","Product to Claim","Ours","source columns"),
 ("evidence","Object property","skc:hasEvidenceLevel","Claim to how much we trust it","Ours","skin_type_source"),
 ("evidence","Object property","prov:wasAttributedTo","Who said it","PROV-O","source columns"),
 ("evidence","Object property","prov:wasDerivedFrom","The page we read it on","PROV-O","evidence file URLs"),
 ("lebanon","Object property","skc:satisfiedBy","A need met by a product, or by a few together","AliCoCo","new"),
 ("--","--","--","--","--","--"),
 ("product","Data property","skc:atPosition","Where it sits in the INCI list, which is roughly concentration order","The MVFM paper uses this too","from ingredients"),
 ("product","Data property","skc:cosingCoverage","How much of the formula we found in the register","Ours","cosing_coverage"),
 ("product","Data property","skc:ingredientCount","How many ingredients","Ours","ingredient_count"),
 ("product","Data property","schema:price","Sits on the Offer","schema.org","price_usd"),
 ("product","Data property","skc:priceSeenDate","When that price was true","Ours","price_seen_date"),
 ("--","--","--","--","--","--"),
 ("lebanon","WORKED OUT BY THE REASONER","SensitiveSafeProduct","Any product where NONE of the ingredients is one of the 26 declarable allergens. We never list them, the software finds them. Should come out around 9,537","Abesova's trick","from ingredients"),
 ("lebanon","WORKED OUT BY THE REASONER","AvailableInLebanon","Any product with at least one offer from a Lebanese shop. Around 11,937","Ours","shops_in_lebanon"),
 ("lebanon","WORKED OUT BY THE REASONER","ManufacturerStatedProduct","Products where the manufacturer themselves made the claim. Around 4,460","Ours","skin_type_source"),
 ("lebanon","WORKED OUT BY THE REASONER","RegulatedProduct","Has at least one restricted ingredient. Around 9,613","Ours","restricted_ingredients"),
 ("lebanon","WORKED OUT BY THE REASONER","FullyIdentifiedProduct","Every single ingredient found in the register. Around 9,032","Ours","cosing_coverage"),
 ("lebanon","WORKED OUT BY THE REASONER","NaturalClaimProduct","Products sold as natural. Built so we can TEST them against the finding that 56% of natural INCI substances are classed as hazardous","Klaschka 2015","free_from, product_summary"),
]
for ri, row in enumerate(ONT, start=7):
    sep = row[0] == "--"
    defined = "REASONER" in str(row[1])
    for i, val in enumerate(row, start=1):
        c = ws.cell(row=ri, column=i, value="" if sep else val)
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        if sep:
            c.fill = PatternFill("solid", fgColor=INK)
        else:
            c.border = under
            if defined:
                c.font = Font(name=FONT, size=10, bold=(i == 3), color="7A5200")
                c.fill = PatternFill("solid", fgColor=MINE)
            elif row[0] == "evidence":
                c.font = Font(name=FONT, size=10, bold=(i == 3), color="6B3550")
                c.fill = PatternFill("solid", fgColor="FAF2F5")
            else:
                c.font = Font(name=FONT, size=10, bold=(i == 3), color="3A3630")
                c.fill = PatternFill("solid", fgColor=ALT if ri % 2 == 0 else PAPER)
    ws.row_dimensions[ri].height = 6 if sep else 40
ws.freeze_panes = "A7"
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 95

# =============================================================== 5. TOOLS
ws = wb.create_sheet("Tools")
banner(ws, 6, "What I need to install, and why that one",
       "Every choice has a reason, and usually a paper that already did it this way.")
tc = [("What it's for", 24), ("What I picked", 24), ("Why this one", 62),
      ("What I said no to", 48), ("Price", 11), ("Where to get it", 40)]
for i, (h, w) in enumerate(tc, start=1):
    c = ws.cell(row=6, column=i, value=h)
    c.font = Font(name=FONT, size=10.5, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=TRACK["F"][0])
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[6].height = 26
TOOLS = [
 ("Drawing the modules","CoModIDE","Made for the MOMo method I'm following. You draw the module and it gives you the OWL","Drawing it in PowerPoint, which produces nothing a machine can read","Free","comodide.com"),
 ("Editing the ontology","Protégé 5.6","The standard one, everyone knows it, reasoners built in. I use it to check the reasoner is happy and to grab the class hierarchy screenshot","WebProtégé is nicer for sharing but has fewer features","Free","protege.stanford.edu"),
 ("The real source of truth","Turtle files in git","Diffs cleanly so I can see what changed. It's also what other people download","Keeping the Protégé file as the master, which makes version control useless","Free","w3.org/TR/turtle"),
 ("Finding an existing term","Linked Open Vocabularies","Search before you invent. This one habit is what separates an ontology that looks amateur from one that doesn't","Inventing terms and hoping nobody notices","Free","lov.linkeddata.es"),
 ("Getting my CSV into the graph","Morph-KGC with a YARRRML mapping","THE most important decision here. The mapping is a file I can put in the appendix, a reviewer can read it, and rerunning it after I fix the data takes one command. TOXIN did exactly this in an Oxford journal","A Python script. Same triples, but nobody can audit it and I can't cite it. OntoRefine is good but traps the mapping inside GraphDB","Free","morph-kgc.readthedocs.io"),
 ("Documenting the mapping","RMLdoc","Turns the mapping into readable documentation with diagrams. Free appendix material","Writing that documentation by hand","Free","github.com/oeg-upm/rmldoc"),
 ("Storing and querying","GraphDB Free","Reasoning built in, and a visual explorer that draws the graph. Showing a supervisor a picture beats any paragraph I could write","Jena Fuseki is simpler but its reasoning is weak. Stardog is stronger but you have to pay","Free desktop","graphdb.ontotext.com"),
 ("Working out what follows","HermiT","Comes with Protégé, solid, fast enough","Pellet and ELK. But careful: if I write SWRL rules HermiT ignores them SILENTLY, so I'd have to switch","Free","hermit-reasoner.com"),
 ("Rules OWL can't express","Openllet, only if I need it","Handles SWRL, which HermiT doesn't. OntoCosmetic used SWRL for exactly this kind of rule","Writing everything as rules. It slows reasoning right down","Free","github.com/Galigator/openllet"),
 ("Checking my DATA is right","SHACL, through pySHACL","OWL can't say 'every product MUST have a brand', because it assumes anything unsaid might just be unknown. SHACL can. This is where validate_dataset.py moves to","Trusting the reasoner to catch bad data. Wrong tool, and it'll quietly accept rubbish","Free","github.com/RDFLib/pySHACL"),
 ("Checking my DESIGN is right","OOPS!","41 known design mistakes, graded. One afternoon for a real evaluation number that none of our competitors has","Not evaluating the design at all, which is what 28 out of 28 reviewed studies did","Free website","oops.linkeddata.es"),
 ("Checking it's FAIR","FOOPS!","24 checks on whether people can find and reuse it. Since I criticise everyone for not publishing, I'd better measure my own","Just claiming it's FAIR without measuring","Free website","w3id.org/foops"),
 ("Structural numbers","OntoMetrics","Depth, breadth, richness. Gives me comparable numbers for the evaluation table","Reporting just a class count and hoping","Free","ontometrics.uni-rostock.de"),
 ("Python access","Owlready2 and RDFLib","My whole pipeline is Python. Owlready2 also runs a reasoner from code, which is what Hansanie & Silva used","The Java OWL API. Powerful, wrong language for me","Free","owlready2.readthedocs.io"),
 ("Documentation for humans","WIDOCO","Generates an HTML page from the ontology itself, so the docs can't drift away from the code","Writing docs by hand and watching them go stale","Free","github.com/dgarijo/Widoco"),
 ("A permanent web address","w3id.org","A stable address that survives me leaving BAU. It's just a pull request on GitHub","A university URL that dies the day I graduate","Free","w3id.org"),
 ("Something citable","Zenodo","A DOI for each release, so people can cite the ontology like a paper. One of my five criticisms is that nobody publishes theirs","GitHub only. No DOI means no proper citation","Free","zenodo.org"),
]
for ri, row in enumerate(TOOLS, start=7):
    for i, val in enumerate(row, start=1):
        c = ws.cell(row=ri, column=i, value=val)
        c.border = under
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        if i == 2:
            c.font = Font(name=FONT, size=10.5, bold=True, color=TRACK["F"][0])
            c.fill = PatternFill("solid", fgColor=TRACK["F"][1])
        elif i == 6:
            c.font = Font(name=FONT, size=9.5, color="2166A5", underline="single")
            c.fill = PatternFill("solid", fgColor=ALT if ri % 2 == 0 else PAPER)
        else:
            c.font = Font(name=FONT, size=10, color="3A3630")
            c.fill = PatternFill("solid", fgColor=ALT if ri % 2 == 0 else PAPER)
    ws.row_dimensions[ri].height = 58
ws.freeze_panes = "B7"
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 95

# ============================================================= 6. ROADMAP
ws = wb.create_sheet("Roadmap")
banner(ws, 6, "Six steps from here to a published ontology",
       "Each one produces something I can show. Nothing is blocked on anything I don't already have.")
rc = [("Step", 13), ("What I do", 54), ("Why it comes here", 52),
      ("What exists at the end", 44), ("Who told me to do this", 32),
      ("What goes wrong if I skip it", 48)]
for i, (h, w) in enumerate(rc, start=1):
    c = ws.cell(row=6, column=i, value=h)
    c.font = Font(name=FONT, size=10.5, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=TRACK["E"][0])
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[6].height = 26
ROAD = [
 ("1\nAsk the questions first",
  "Write down what the ontology is for, who it's for, what it is NOT for, and 15 questions it has to be able to answer",
  "Everything after this gets checked against those questions. It's three pages of writing, no code, and it's the best hour I'll spend on the whole thing",
  "A requirements doc, and 15 questions that later become my evaluation chapter",
  "LOT, and Noy & McGuinness",
  "I build classes nobody needs, and at the end I can't prove the thing works"),
 ("2\nLook before building",
  "Go through all 42 columns and decide: reuse someone's term, or invent one. Then check three things that could each save weeks: the CosIng RDF on GitHub, DermO on BioPortal, and whether Wikidata knows our 1,463 brands",
  "If CosIng already exists as proper RDF, our whole ingredient layer arrives free and we cite them. Finding that out AFTER building it would hurt",
  "A 42-row table that goes straight into the thesis, and possibly a free ingredient layer",
  "Both LOT and MOMo say reuse before you build",
  "I reinvent 28,573 ingredient entries that already exist"),
 ("3\nBuild the four modules",
  "Draw each module as a diagram first, then write the Turtle. core, product, evidence, user, plus the Lebanon file that pulls them together",
  "The four change at completely different speeds. Product data moves weekly, medical knowledge barely moves. And I can hand a dermatologist ONE small file instead of 12,629 rows",
  "The ontology, plus the diagrams my chapter needs anyway",
  "MOMo. Hansanie & Silva did the same and explained why",
  "One giant file nobody can review, reuse, or update in pieces"),
 ("4\nFill it up",
  "Build the long helper file (one row per ingredient mention, about 295,991 rows), write the YARRRML mapping, run Morph-KGC, load into GraphDB with each source in its own named box",
  "This is what decides whether this is a METHOD or just a script. A mapping file can be audited and cited. Named boxes mean I can reload one source without disturbing the rest",
  "About 1.8 million triples, plus a mapping file for the appendix",
  "TOXIN used R2RML. Abesova used OntoRefine",
  "An unauditable script, and no way to trace where a statement came from"),
 ("5\nMake it think, then check it",
  "Switch on the reasoner-computed classes, run HermiT, write the SHACL shapes, run OOPS! and FOOPS!. But PREDICT the numbers first, then see what the reasoner actually gives",
  "Predicting and then checking is a real test. If SensitiveSafeProduct doesn't land near 9,537, something in the model is wrong and I want to know now, not later",
  "Evaluation numbers. Plus those 593 sensitive-skin products with allergens finally showing up as a proper contradiction instead of a note in a README",
  "Abesova for the defined classes. OOPS! and FOOPS! for the rest",
  "I publish an ontology whose computed classes were never checked against reality"),
 ("6\nPublish it and prove it",
  "w3id address, WIDOCO docs, Zenodo DOI. Then answer all 15 questions with SPARQL and put every query and its result in the thesis",
  "One of my five criticisms is that almost nobody publishes theirs. I can't say that and then not publish. And the 15 answers ARE the evaluation chapter",
  "Something citable with a DOI, and a finished evaluation chapter",
  "LOT. FoodKG and COPPER both did it. Braun 2025 is the template",
  "The thesis ends with a claim instead of a thing, and nobody can build on it"),
]
for ri, row in enumerate(ROAD, start=7):
    for i, val in enumerate(row, start=1):
        c = ws.cell(row=ri, column=i, value=val)
        c.border = under
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        if i == 1:
            c.font = Font(name=FONT, size=11, bold=True, color=PAPER)
            c.fill = PatternFill("solid", fgColor=TRACK["E"][0])
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        elif i == 6:
            c.font = Font(name=FONT, size=10, italic=True, color=FLAGTXT)
            c.fill = PatternFill("solid", fgColor=FLAG)
        else:
            c.font = Font(name=FONT, size=10, color="3A3630")
            c.fill = PatternFill("solid", fgColor=ALT if ri % 2 == 0 else PAPER)
    ws.row_dimensions[ri].height = 96
ws.freeze_panes = "B7"
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 90

# ============================================================== 7. THE GAP
ws = wb.create_sheet("The gap")
banner(ws, 5, "The whole argument on one page",
       "What's missing everywhere, what we do about it, and how safe each claim actually is.")
gc = [("What's missing everywhere", 42), ("How I know", 56),
      ("What we do about it", 56), ("How safe is that claim", 40),
      ("Where it goes", 24)]
for i, (h, w) in enumerate(gc, start=1):
    c = ws.cell(row=6, column=i, value=h)
    c.font = Font(name=FONT, size=10.5, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=TRACK["C"][0])
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[6].height = 26
GAP = [
 ("Ingredients that mean something legally",
  "Every skincare ontology stores ingredients as loose text or a small homemade list. The ONE graph that ties cosmetic ingredients to EU law (TOXIN, Oxford, 2025) has zero products in it",
  "Our ingredients are identified by their CosIng entry, so the regulatory status comes from the European Commission and not from us. 99.2% of products with a formula are linked",
  "SAFEST. Nobody has both halves. This is the thesis",
  "Contribution 1"),
 ("Anyone writing down who said what",
  "No skincare ontology records who made a claim or how much that source is worth. Everything is presented as equally true",
  "Every claim is its own thing carrying its source, the exact sentence, the date, and one of four levels of trust. Built on PROV-O, which is a W3C standard",
  "STRONG. The pattern exists elsewhere, which is GOOD, because it means we're reusing rather than inventing",
  "Contribution 2"),
 ("Whether you can actually buy it",
  "Every system recommends without asking whether you can get hold of the thing. In Lebanon that falls apart, and it falls apart differently for imported and local products",
  "Price in dollars and lira, per shop, with the date we saw it. 11,937 products with at least one Lebanese shop",
  "STRONG AND UNIQUE. No cosmetics system models whether you can buy it",
  "Contribution 3"),
 ("Anybody publishing their ontology",
  "One out of six skincare ontologies is actually downloadable. The field can't build on itself",
  "w3id address, WIDOCO docs, Zenodo DOI, a named method, and a FAIR score we actually measure",
  "EASY AND RARE. Costs a week, and one in six manage it",
  "Contribution 4"),
 ("Any evaluation at all",
  "Somebody reviewed 28 ontology recommenders and found NOT ONE described an evaluation method. In our own set: two asked under 30 people, one is a case study, one admits expert testing never happened",
  "Four layers: structural (OOPS!, FOOPS!), functional (15 questions as SPARQL), logical (predict the class sizes then check), and the comparison sheet",
  "STRONG, and cheap. None of it needs users we don't have",
  "Evaluation chapter"),
 ("Anyone modelling what people actually NEED",
  "Concerns are treated everywhere as an attribute of a product. AliCoCo (SIGMOD 2020) argues that misses the point, because shoppers think in needs, not categories",
  "Lebanese needs as their own entities. A routine under $20 a month. One that survives a power cut. One you can buy in a single pharmacy",
  "MOST ORIGINAL, LEAST CERTAIN. Do this AFTER the four safe ones are done",
  "Contribution 5, optional"),
]
for ri, row in enumerate(GAP, start=7):
    for i, val in enumerate(row, start=1):
        c = ws.cell(row=ri, column=i, value=val)
        c.border = under
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        if i == 1:
            c.font = Font(name=FONT, size=11, bold=True, color=TRACK["C"][0])
            c.fill = PatternFill("solid", fgColor=TRACK["C"][1])
        elif i == 4:
            c.font = Font(name=FONT, size=10, bold=True, color="7A5200")
            c.fill = PatternFill("solid", fgColor=MINE)
        else:
            c.font = Font(name=FONT, size=10, color="3A3630")
            c.fill = PatternFill("solid", fgColor=ALT if ri % 2 == 0 else PAPER)
    ws.row_dimensions[ri].height = 84

r = 7 + len(GAP) + 2
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=5)
c = ws.cell(row=r, column=1, value="  IF I ONLY GET TO SAY ONE SENTENCE")
c.font = Font(name=FONT, size=11, bold=True, color=PAPER)
c.fill = PatternFill("solid", fgColor=INK)
c.alignment = Alignment(vertical="center")
ws.row_dimensions[r].height = 26
ws.merge_cells(start_row=r + 1, start_column=1, end_row=r + 1, end_column=5)
c = ws.cell(row=r + 1, column=1, value=
  "  Nobody has ingredients tied to actual EU law, and real products you can buy, and a record of where "
  "every claim came from. The one graph that links cosmetic ingredients to European law has no products "
  "in it at all. Everyone else has products and no law. We're the bit in the middle, built for Lebanon, "
  "on 12,629 products.")
c.font = Font(name=FONT, size=12, color=INK)
c.fill = PatternFill("solid", fgColor=MINE)
c.alignment = Alignment(vertical="center", wrap_text=True)
ws.row_dimensions[r + 1].height = 66
ws.sheet_view.showGridLines = False
ws.sheet_view.zoomScale = 95

# ------------------------------------------------------------------ save
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PAPERS_TABLE.xlsx")
wb.save(out)
print("written:", out)
print(f"{len(P)} papers, {len(COLS)} columns, {len(wb.sheetnames)} sheets")
