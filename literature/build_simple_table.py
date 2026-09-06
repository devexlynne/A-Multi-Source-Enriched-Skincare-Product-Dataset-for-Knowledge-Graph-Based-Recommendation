"""
Builds ONTOLOGY_PAPERS.xlsx  -  the simple one.

Ten papers. Nine columns. Two sheets. Written the way you would explain it
to someone over coffee, not the way a journal would.

Run:  py build_simple_table.py
"""
import os
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

INK   = "22303C"
LINE  = "D6D0C6"
CREAM = "FFF6E4"
SOFT  = "F7F5F1"
TEAL  = "0F5A57"
RED   = "9B2226"
F     = "Calibri"

thin = Side(style="thin", color=LINE)
box  = Border(left=thin, right=thin, top=thin, bottom=thin)

wb = Workbook()

# ======================================================= SHEET 1: papers
ws = wb.active
ws.title = "The papers"

ws.merge_cells("A1:I1")
c = ws["A1"]
c.value = "Ontologies for skincare and cosmetics: everything that already exists"
c.font = Font(name=F, size=15, bold=True, color="FFFFFF")
c.fill = PatternFill("solid", fgColor=INK)
c.alignment = Alignment(vertical="center", indent=1)
ws.row_dimensions[1].height = 30

ws.merge_cells("A2:I2")
c = ws["A2"]
c.value = ("Ten of them. That is all there is. Read the last two columns if you only "
           "have five minutes: what we take, and what they got wrong.")
c.font = Font(name=F, size=10.5, italic=True, color="55504A")
c.fill = PatternFill("solid", fgColor="FFFFFF")
c.alignment = Alignment(vertical="center", indent=1)
ws.row_dimensions[2].height = 22

HEAD = [("What we call it", 20),
        ("Year", 7),
        ("Who did it, and where it came out", 30),
        ("What they actually did", 44),
        ("How big is their ontology", 26),
        ("Can we download it?", 20),
        ("What we take from it", 44),
        ("Their weak point", 40),
        ("Link", 40)]

for i, (h, w) in enumerate(HEAD, start=1):
    c = ws.cell(row=4, column=i, value=h)
    c.font = Font(name=F, size=11, bold=True, color="FFFFFF")
    c.fill = PatternFill("solid", fgColor=TEAL)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    c.border = box
    ws.column_dimensions[get_column_letter(i)].width = w
ws.row_dimensions[4].height = 34

ROWS = [
[
 "Moe and Aung",
 "2014",
 "Two universities in Myanmar. A small journal, IJITCS. Nobody really cites it",
 "Built two separate ontologies, one for skin problems and one for cosmetics, then joined them with a "
 "graph algorithm to score which product fits which problem.",
 "They never say. No class count, no product count, nothing",
 "No. It only exists as pictures in the paper",
 "Their eight step checklist for building an ontology. Step one is writing a glossary of every term with "
 "its synonyms, which is exactly what our benefits column needs since we have Hydrating and Hydration "
 "sitting there as two different things.",
 "Ingredients are just text with a number next to them. Nothing in their model can say an ingredient is "
 "regulated. Also they claim they beat everyone else and there is no comparison table anywhere.",
 "doi.org/10.5815/ijitcs.2014.06.05"
],
[
 "OntoCosmetic",
 "2021 and 2023",
 "Universite de Lorraine in France with a Colombian university. Two papers, chemical engineering "
 "conferences",
 "An ontology for people who FORMULATE creams. It helps a chemist decide what to put in an emulsion so it "
 "stays stable. The second paper turned it into a phone app.",
 "116 classes, 26 object properties, 20 data properties, 279 products. We counted these ourselves from "
 "their file",
 "YES. purl.org/ontocosmetic. It is the only one of the ten you can actually download and open",
 "Their ingredient type names (emollient, humectant, preservative, UV filter) and the idea of keeping "
 "product properties separate from ingredient properties. Also they record where each RULE came from, "
 "which is the same instinct as our evidence levels.",
 "It is chemistry, not shopping. Droplet size, rheology, HLB. Manufacturers never publish any of that so "
 "we will never have it. And they admit at the end that no expert ever tested the tool.",
 "purl.org/ontocosmetic"
],
[
 "Hansanie and Silva",
 "2024",
 "University of Moratuwa, Sri Lanka. IEEE conference, so a proper venue",
 "You upload a photo of your face, a neural network grades how bad your acne is, that grade goes into an "
 "ontology, and the ontology picks products for you.",
 "Not reported. They describe the classes but never count them",
 "No link given anywhere",
 "The best structural idea we found: they built THREE separate ontologies (skincare knowledge, product "
 "info, user profile) and merged them, because the three change at completely different speeds. We are "
 "copying that. Also they used a reasoner from day one.",
 "The famous 87.5 percent is not accuracy. It is how many of 24 survey people said they liked the "
 "products. The actual model scored 77.5. We should quote that correctly, it makes us look careful.",
 "doi.org/10.1109/ICIPRoB62548.2024.10543444"
],
[
 "Abesova and team",
 "2023",
 "Four master's students at Vrije Universiteit Amsterdam. A COURSE PROJECT, not a real paper. We must say "
 "this when we cite it",
 "Scraped Sephora reviews, built a small ontology, and had it recommend a full routine from four inputs: "
 "skin type, skin tone, country, and how lazy you are about routines.",
 "36 classes, 6 object properties, 6 data properties. Small, and it still works",
 "Not published anywhere",
 "The single most important idea in the whole review, and it comes from students. They never tag a product "
 "as suitable for oily skin. They WRITE THE RULE ONCE and the software works out which products qualify. "
 "We write one line instead of tagging 4,000 rows, and if we fix a formula the answer fixes itself.",
 "Everything they classify is based on review scores, not on what is actually in the product. And they "
 "wrote in their own limitations that ingredient based rules would be better and they did not do it. That "
 "sentence is literally our contribution, sitting unfinished in their paper.",
 "In our repo, papers/ folder"
],
[
 "The Indonesian one",
 "2025",
 "Published in bit-Tech, an Indonesian journal. WE STILL NEED THE FULL PDF",
 "Closest thing to what we are doing. They scraped Skinsort (yes, the same site we used) plus two "
 "Indonesian shops and built a skincare ontology on top.",
 "12 classes, more than 25 object properties, 3,800 products, 28,000 ingredients",
 "The abstract does not say. Need to check",
 "Two class names we would not have thought of: Formulation Trait and What It Does. That split is our "
 "whole evidence problem in one line. What It Does is the marketing claim. Formulation Trait is the "
 "physical fact. One comes from a seller, the other from the formula.",
 "No prices, no availability, no provenance, and their allergen list is homemade instead of coming from "
 "the EU register. Also 3,800 products against our 12,629.",
 "jurnal.kdi.or.id/index.php/bt/article/view/2857"
],
[
 "The small Indonesian one",
 "2023",
 "Universitas Udayana, Indonesia. A small local journal",
 "A basic cosmetics ontology, mostly to prove the idea works. Tested by running some SPARQL queries.",
 "3 classes, 5 object properties, 62 products",
 "No",
 "Honestly, not much. We keep it in the table for one reason: it shows the scale difference. 62 products "
 "against our 12,629. We do not have to say we are bigger, the table says it.",
 "It is a proof of concept and does not pretend otherwise.",
 "Search: Pengembangan Ontologi Semantik Produk Kosmetik"
],
[
 "TOXIN",
 "2025",
 "Vrije Universiteit Brussel. Published in Database, an Oxford journal. This is a SERIOUS venue, better "
 "than everything above",
 "A knowledge graph of cosmetic ingredient safety, built from the official EU safety opinions. The same "
 "committee that writes the CosIng annexes we already use.",
 "88 ingredients, 53 of them with liver effects. Reuses an existing biomedical ontology instead of "
 "inventing one",
 "YES, live at toxin-search.netlify.app",
 "Three things, and they change our plan. One, they turned spreadsheets into a graph using R2RML, a proper "
 "mapping file instead of a script, so we will do the same. Two, they keep each data source in its own "
 "named box so you can always trace where a fact came from. Three, they link to other people's IDs "
 "instead of copying data.",
 "No products. None. It has all the regulation and all the science and nothing you can buy. That is "
 "exactly the space we sit in.",
 "doi.org/10.1093/database/baae121"
],
[
 "HaCKG",
 "2025",
 "South Korea. IEEE Access. 8 citations already",
 "Built a cosmetics knowledge graph of products and ingredients, then trained a neural network on it to "
 "predict whether a product is halal.",
 "Not stated in the abstract",
 "Not stated",
 "Their own argument helps us: they say looking at ingredients one at a time misses the relationships "
 "between products and ingredients. That is an argument FOR building a graph, made by someone else. Also "
 "it proves a cosmetics knowledge graph is a publishable thing.",
 "They PREDICT halal status with a model, which gives you a probability and no reason. We would DERIVE it "
 "from the ingredient list and be able to say why. But we should be honest: this weakens our halal idea, "
 "it is not new anymore.",
 "IEEE Access 2025, search HaCKG halal knowledge graph"
],
[
 "DermO",
 "2016",
 "University of Birmingham. Journal of Biomedical Semantics",
 "A proper medical ontology of skin diseases, built by hand by real dermatologists.",
 "Over 3,000 terms in 20 categories, lined up with ICD-10",
 "YES, on BioPortal, free",
 "This fixes a real hole in our work. Right now our concerns column (acne, dryness, redness, "
 "hyperpigmentation) is text WE made up. Nobody medical has checked it. We cannot get a dermatologist "
 "quickly, but we can line our words up with an ontology dermatologists already built.",
 "It has nothing to do with products. It is a disease vocabulary. But this one is not a competitor, it is "
 "a gift.",
 "bioportal.bioontology.org/ontologies/DERMO"
],
[
 "CosIng as RDF",
 "n/a",
 "A GitHub project, not a paper",
 "Somebody already converted the EU CosIng register into the exact graph format we need.",
 "All 28,573 CosIng entries, if it is complete",
 "YES, on GitHub. We have not checked it properly yet",
 "Possibly our ENTIRE ingredient layer, free, and we cite them instead of doing the work. This is the "
 "first thing to check, before we write a single line of the ontology.",
 "We do not know yet whether the licence and the IDs suit us. If they do not, that is also fine, because "
 "then our own conversion becomes something we can claim as ours.",
 "github.com/biobricks-ai/cosing-kg"
],
]

STAR = {2, 4, 7, 9, 10}  # rows we lean on most

for ri, row in enumerate(ROWS, start=5):
    n = ri - 4
    for i, val in enumerate(row, start=1):
        c = ws.cell(row=ri, column=i, value=val)
        c.border = box
        c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
        if i == 1:
            c.font = Font(name=F, size=11.5, bold=True,
                          color=TEAL if n in STAR else INK)
            c.fill = PatternFill("solid", fgColor=CREAM if n in STAR else SOFT)
            c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
        elif i == 6:
            yes = str(val).startswith("YES")
            c.font = Font(name=F, size=10, bold=yes, color=TEAL if yes else "7A7A7A")
            c.fill = PatternFill("solid", fgColor="EAF3F0" if yes else "FFFFFF")
        elif i == 7:
            c.font = Font(name=F, size=10, color="2A2A2A")
            c.fill = PatternFill("solid", fgColor=CREAM)
        elif i == 8:
            c.font = Font(name=F, size=10, color=RED)
            c.fill = PatternFill("solid", fgColor="FFFFFF")
        elif i == 9:
            c.font = Font(name=F, size=9, color="2166A5", underline="single")
            c.fill = PatternFill("solid", fgColor="FFFFFF")
        else:
            c.font = Font(name=F, size=10, color="2A2A2A")
            c.fill = PatternFill("solid", fgColor="FFFFFF")
    ws.row_dimensions[ri].height = 118

r = 5 + len(ROWS) + 1
ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
c = ws.cell(row=r, column=1)
c.value = ("So: ten ontologies exist. Only two you can download. Not one of them links ingredients to the "
           "EU register AND has products AND records where each claim came from. That empty space is us.")
c.font = Font(name=F, size=12, bold=True, color=INK)
c.fill = PatternFill("solid", fgColor=CREAM)
c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
c.border = box
ws.row_dimensions[r].height = 40

ws.freeze_panes = "B5"
ws.sheet_view.showGridLines = False

# ======================================================= SHEET 2: us vs them
ws2 = wb.create_sheet("Us vs them")

ws2.merge_cells("A1:I1")
c = ws2["A1"]
c.value = "The same ten, but only on the things that matter to us"
c.font = Font(name=F, size=15, bold=True, color="FFFFFF")
c.fill = PatternFill("solid", fgColor=INK)
c.alignment = Alignment(vertical="center", indent=1)
ws2.row_dimensions[1].height = 30

ws2.merge_cells("A2:I2")
c = ws2["A2"]
c.value = "Look at the last column. Then look for another column that has the same ticks. There is not one."
c.font = Font(name=F, size=10.5, italic=True, color="55504A")
c.fill = PatternFill("solid", fgColor="FFFFFF")
c.alignment = Alignment(vertical="center", indent=1)
ws2.row_dimensions[2].height = 22

COLS2 = ["", "Moe\n2014", "OntoCosmetic", "Hansanie\n2024", "Abesova\n2023",
         "Indonesian\n2025", "TOXIN\n2025", "HaCKG\n2025", "OUR WORK"]
COMP = [
 ("Is it a real peer reviewed paper", "weak journal", "yes", "yes", "no, students",
  "yes", "yes", "yes", "will be"),
 ("Can anyone download the ontology", "no", "YES", "no", "no", "?", "YES", "?", "yes, planned"),
 ("Did they follow a named method", "no", "no", "no", "sort of", "yes", "no", "no", "yes, two of them"),
 ("How many products", "?", "279", "?", "Sephora", "3,800", "none", "?", "12,629"),
 ("Ingredients tied to EU law", "no", "no", "no", "no", "no", "YES", "no", "YES"),
 ("Do they say where each claim came from", "no", "no", "no", "no", "no", "yes", "no", "YES, 4 levels"),
 ("Do they know if you can buy it", "no", "no", "no", "no", "no", "no", "no", "YES, per shop, with price"),
 ("Which country's market", "none", "none", "none", "none", "Indonesia", "none", "none", "LEBANON"),
 ("Did they properly test it", "no", "no", "24 people", "no", "?", "examples", "yes", "planned, 4 ways"),
]
KEY = {5, 6, 7}

for i, h in enumerate(COLS2, start=1):
    c = ws2.cell(row=4, column=i, value=h)
    c.font = Font(name=F, size=10.5, bold=True,
                  color=INK if i == 9 else "FFFFFF")
    c.fill = PatternFill("solid", fgColor=CREAM if i == 9 else TEAL)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    c.border = box
    ws2.column_dimensions[get_column_letter(i)].width = 38 if i == 1 else (26 if i == 9 else 15)
ws2.row_dimensions[4].height = 40

for ri, row in enumerate(COMP, start=5):
    key = (ri - 4) in KEY
    for i, val in enumerate(row, start=1):
        c = ws2.cell(row=ri, column=i, value=val)
        c.border = box
        if i == 1:
            c.font = Font(name=F, size=10.5, bold=key, color=TEAL if key else INK)
            c.fill = PatternFill("solid", fgColor="EAF3F0" if key else SOFT)
            c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
        elif i == 9:
            c.font = Font(name=F, size=10.5, bold=True, color="6B4A00")
            c.fill = PatternFill("solid", fgColor=CREAM)
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        else:
            c.font = Font(name=F, size=10,
                          color="9B2226" if str(val) == "no" else "2A2A2A")
            c.fill = PatternFill("solid", fgColor="FFFFFF")
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws2.row_dimensions[ri].height = 30

r = 5 + len(COMP) + 1
ws2.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
c = ws2.cell(row=r, column=1)
c.value = ("The three green rows are the whole thesis. TOXIN has the EU link but no products. Everyone else "
           "has products but no EU link. Nobody at all records where a claim came from, and nobody asks "
           "whether you can actually buy the thing.")
c.font = Font(name=F, size=11.5, bold=True, color=INK)
c.fill = PatternFill("solid", fgColor=CREAM)
c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
c.border = box
ws2.row_dimensions[r].height = 46

r += 2
ws2.merge_cells(start_row=r, start_column=1, end_row=r, end_column=9)
c = ws2.cell(row=r, column=1, value="Two things to do before we build anything")
c.font = Font(name=F, size=12, bold=True, color="FFFFFF")
c.fill = PatternFill("solid", fgColor=INK)
c.alignment = Alignment(vertical="center", indent=1)
ws2.row_dimensions[r].height = 26

TODO = [
 ("1. Check the CosIng GitHub project",
  "If it is usable, our whole ingredient layer is done for free and we cite them. Thirty minutes of work "
  "that could save us weeks. Do this first."),
 ("2. Get the full Indonesian paper",
  "It is the closest thing to ours and we only have the abstract. We cannot write the related work section "
  "properly without it."),
 ("3. Line our concerns up with DermO",
  "Our acne, dryness and redness are words we invented. DermO has 3,000 terms written by actual "
  "dermatologists. This fixes the one criticism nobody has made yet but somebody will."),
]
for i, (a, b) in enumerate(TODO):
    rr = r + 1 + i
    c = ws2.cell(row=rr, column=1, value=a)
    c.font = Font(name=F, size=10.5, bold=True, color=TEAL)
    c.fill = PatternFill("solid", fgColor=SOFT)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    c.border = box
    ws2.merge_cells(start_row=rr, start_column=2, end_row=rr, end_column=9)
    c = ws2.cell(row=rr, column=2, value=b)
    c.font = Font(name=F, size=10.5, color="2A2A2A")
    c.fill = PatternFill("solid", fgColor="FFFFFF")
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    c.border = box
    ws2.row_dimensions[rr].height = 34

ws2.freeze_panes = "B5"
ws2.sheet_view.showGridLines = False

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ONTOLOGY_PAPERS.xlsx")
wb.save(out)
print("written:", out)
print(f"{len(ROWS)} papers, {len(HEAD)} columns, {len(wb.sheetnames)} sheets")
