# -*- coding: utf-8 -*-
"""
Adds three new tabs to the workbook Lynne already edited, and appends new rows
to the Tools tab. Nothing existing is touched.

  The gap            every paper, what is missing in it, what I do instead,
                     and what they still have that I do not
  Reasoning + SHACL  the five ways to reason, OWL against SHACL, and the
                     actual SHACL code for four jobs in my thesis
  Abesova paper      the attached PDF pulled apart: tools, steps, classes,
                     the one clever idea, what they admit is broken, and a
                     drawn pipeline

Run:  py add_gap_tabs.py
"""
import os, shutil
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from gap_data import (GAP_COLS, GAP, REASONING_INTRO, REASONING_COLS, REASONING,
                      SHACL_CODE, ABESOVA_FACTS, ABESOVA_STEPS, ABESOVA_CLASSES,
                      ABESOVA_PROPS, ABESOVA_HONEST, ABESOVA_LIMITATION)
from tools_extra import EXTRA

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "PAPERS_TABLE.xlsx")

# ------------------------------------------------------------------ the look
# same palette as the tabs that are already there
INK   = "2E2A25"
PAPER = "FFFFFF"
ALT   = "FBFAF7"
LINE  = "E8E2D8"
SUB   = "8A8175"
MINE  = "FFF6E0"
MINEH = "E8A33D"
FLAG  = "FCEEE6"
FLAGT = "A83A1E"
GOOD  = "EDF5F3"
GOODT = "1F6F6B"
CODE  = "F4F2ED"
FONT  = "Calibri"
MONO  = "Consolas"

GCOL = {"A": ("1F6F6B", "EEF5F4"),
        "B": ("6B4E9B", "F2EEF8"),
        "C": ("8C4A62", "FAF2F5"),
        "D": ("A6612F", "FBF4EC")}

hair  = Side(style="thin", color=LINE)
under = Border(bottom=hair)


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
    c.alignment = Alignment(vertical="center", wrap_text=True)
    ws.row_dimensions[2].height = 30
    ws.row_dimensions[3].height = 6


def band(ws, row, span, text, dark):
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=span)
    c = ws.cell(row=row, column=1, value="  " + text)
    c.font = Font(name=FONT, size=11.5, bold=True, color=PAPER)
    c.fill = PatternFill("solid", fgColor=dark)
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[row].height = 26


def header(ws, row, cols, mine_from=None):
    for i, (h, w) in enumerate(cols, start=1):
        c = ws.cell(row=row, column=i, value=h)
        mine = mine_from is not None and i >= mine_from
        c.font = Font(name=FONT, size=10.5, bold=True,
                      color="4A3200" if mine else PAPER)
        c.fill = PatternFill("solid", fgColor=MINEH if mine else INK)
        c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 34


# ================================================================== 1. THE GAP
def build_gap(wb):
    if "The gap" in wb.sheetnames:
        del wb["The gap"]
    ws = wb.create_sheet("The gap", 1)
    NC = len(GAP_COLS)
    title(ws, NC, "The gap",
          "Read the middle column. That is what is missing in their work. The two orange "
          "columns are mine: what I do instead, and what I honestly still do not have.")
    header(ws, 4, GAP_COLS, mine_from=5)

    r, dark, wash = 5, GCOL["A"][0], GCOL["A"][1]
    for row in GAP:
        if len(row) == 3:                       # a group divider
            g, name, why = row
            dark, wash = GCOL[g]
            band(ws, r, NC, f"GROUP {g}   {name}     {why}", dark)
            r += 1
            continue
        stripe = (r % 2 == 0)
        for i, val in enumerate(row, start=1):
            c = ws.cell(row=r, column=i, value=val)
            c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
            c.border = under
            if i == 1:
                c.font = Font(name=FONT, size=11, bold=True, color=PAPER)
                c.fill = PatternFill("solid", fgColor=dark)
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif i == 2:
                c.font = Font(name=FONT, size=11, bold=True, color=dark)
                c.fill = PatternFill("solid", fgColor=wash)
                c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
            elif i == 4:                                     # what is missing
                c.font = Font(name=FONT, size=10, color=FLAGT)
                c.fill = PatternFill("solid", fgColor=FLAG)
            elif i == 5:                                     # what I do
                c.font = Font(name=FONT, size=10, bold=True, color="3A3226")
                c.fill = PatternFill("solid", fgColor=MINE)
            elif i == 6:                                     # what I lack
                c.font = Font(name=FONT, size=9.5, italic=True, color=SUB)
                c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
            else:
                c.font = Font(name=FONT, size=10, color="3A3630")
                c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
        ws.row_dimensions[r].height = 92
        r += 1

    # the one-line summary, at the bottom where it lands after reading
    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r + 2, end_column=NC)
    c = ws.cell(row=r, column=1, value=
      "  THE GAP IN ONE SENTENCE\n"
      "  Everyone recommends from ratings, reviews or photos. Nobody recommends from what is actually IN the product, "
      "tied to the regulator, with a record of where each fact came from, for products you can really buy.\n"
      "  Abesova's Limitation 3 says this in their own words: \"class restrictions based on ingredients could be developed... "
      "a more symbolic and chemical approach, compared to the statistical one that is currently employed.\"")
    c.font = Font(name=FONT, size=11.5, bold=True, color="4A3200")
    c.fill = PatternFill("solid", fgColor=MINE)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    for k in range(3):
        ws.row_dimensions[r + k].height = 26

    ws.freeze_panes = "C5"
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 85
    return ws


# ========================================================= 2. REASONING + SHACL
def build_reasoning(wb):
    if "Reasoning + SHACL" in wb.sheetnames:
        del wb["Reasoning + SHACL"]
    ws = wb.create_sheet("Reasoning + SHACL", 2)
    NC = len(REASONING_COLS)
    title(ws, NC, "Reasoning, and why SHACL", REASONING_INTRO)
    header(ws, 4, REASONING_COLS)

    r = 5
    for row in REASONING:
        if row[0] == "H":
            band(ws, r, NC, row[1].strip(), INK)
            r += 1
            continue
        stripe = (r % 2 == 0)
        for i, val in enumerate(row, start=1):
            c = ws.cell(row=r, column=i, value=val)
            c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
            c.border = under
            if i == 2:
                c.font = Font(name=FONT, size=11, bold=True, color=GOODT)
                c.fill = PatternFill("solid", fgColor="EEF5F4")
                c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
            elif i == 4:
                c.font = Font(name=FONT, size=10, color="3A3226")
                c.fill = PatternFill("solid", fgColor=MINE)
            elif i == 5:
                hot = "NOBODY" in str(val)
                c.font = Font(name=FONT, size=9.5, bold=hot, color=FLAGT if hot else SUB)
                c.fill = PatternFill("solid", fgColor=FLAG if hot else (ALT if stripe else PAPER))
            elif i == 6:
                v = str(val)
                c.font = Font(name=FONT, size=10.5, bold=(v == "YES"),
                              color=GOODT if v == "YES" else SUB)
                c.fill = PatternFill("solid", fgColor=GOOD if v == "YES" else (ALT if stripe else PAPER))
                c.alignment = Alignment(horizontal="center", vertical="center")
            else:
                c.font = Font(name=FONT, size=10, color="3A3630")
                c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
        ws.row_dimensions[r] = ws.row_dimensions[r]
        ws.row_dimensions[r].height = 66
        r += 1

    # ---- the code blocks
    r += 1
    band(ws, r, NC, "  5. THE ACTUAL CODE.  Copy these four into a shapes.ttl file.", INK)
    r += 2
    for caption, code in SHACL_CODE:
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=NC)
        c = ws.cell(row=r, column=2, value=caption)
        c.font = Font(name=FONT, size=11, bold=True, color="4A3200")
        c.fill = PatternFill("solid", fgColor=MINE)
        c.alignment = Alignment(vertical="center", indent=1)
        ws.row_dimensions[r].height = 22
        r += 1
        lines = code.split("\n")
        ws.merge_cells(start_row=r, start_column=2, end_row=r + len(lines) - 1, end_column=NC)
        c = ws.cell(row=r, column=2, value=code)
        c.font = Font(name=MONO, size=9.5, color="2E2A25")
        c.fill = PatternFill("solid", fgColor=CODE)
        c.alignment = Alignment(vertical="top", wrap_text=False, indent=1)
        for k in range(len(lines)):
            ws.row_dimensions[r + k].height = 13
        r += len(lines) + 1

    # ---- the sentence for the chapter
    ws.merge_cells(start_row=r, start_column=2, end_row=r + 2, end_column=NC)
    c = ws.cell(row=r, column=2, value=
      "  THE SENTENCE FOR MY CHAPTER\n"
      "  \"None of the 28 reviewed systems reports any use of SHACL. Validation of the underlying data, and the "
      "enforcement of provenance constraints, are therefore unaddressed in the existing skincare ontology literature.\"\n"
      "  That is a small, true, defensible gap claim, and it costs me one afternoon of work to earn it.")
    c.font = Font(name=FONT, size=11.5, bold=True, color="4A3200")
    c.fill = PatternFill("solid", fgColor=MINE)
    c.alignment = Alignment(vertical="center", wrap_text=True, indent=1)
    for k in range(3):
        ws.row_dimensions[r + k].height = 26

    ws.freeze_panes = "C5"
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 85
    return ws


# ============================================================== 3. ABESOVA TAB
def cell(ws, row, col, val, *, span=1, bold=False, size=10, colour="3A3630",
         fill=None, mono=False, wrap=True, center=False, italic=False):
    if span > 1:
        ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + span - 1)
    c = ws.cell(row=row, column=col, value=val)
    c.font = Font(name=MONO if mono else FONT, size=size, bold=bold,
                  italic=italic, color=colour)
    if fill:
        c.fill = PatternFill("solid", fgColor=fill)
    c.alignment = Alignment(vertical="center" if center else "top",
                            horizontal="center" if center else "general",
                            wrap_text=wrap, indent=1)
    return c


def build_abesova(wb):
    name = "Abesova paper"
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name, 3)
    NC = 13                       # wide enough for the six diagram boxes
    widths = [3, 26, 4, 30, 4, 30, 4, 26, 4, 26, 4, 26, 26]
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    title(ws, NC, "Abesova 2023, pulled apart",
          "The paper my supervisor attached. A student project, so I must say that out loud. "
          "But it contains the one mechanism my whole thesis rests on, and its Limitation 3 is my contribution.")

    r = 4
    # ---------------------------------------------------------- the facts
    band(ws, r, NC, "1.  WHAT IT IS", INK); r += 2
    for k, v in ABESOVA_FACTS:
        cell(ws, r, 2, k, bold=True, size=10, colour=GCOL["A"][0], fill="EEF5F4")
        cell(ws, r, 3, v, span=NC - 2, size=10)
        ws.row_dimensions[r].height = 15 + 13 * (len(v) // 105)
        r += 1
    r += 1

    # ---------------------------------------------------------- the diagram
    band(ws, r, NC, "2.  WHAT THEY DID, DRAWN", INK); r += 2
    boxes = [
      ("SEPHORA REVIEWS\nCSV from GitHub\nthousands of reviews", "EEF5F4", GCOL["A"][0]),
      ("ONTOREFINE\ndraw which column\nbecomes what", "F2EEF8", GCOL["B"][0]),
      ("9 TURTLE FILES\nbuilt one at a time\nwith CONSTRUCT", "FAF2F5", GCOL["C"][0]),
      ("GRAPHDB\none default graph\n+ the base ontology", "FBF4EC", GCOL["D"][0]),
      ("THE REASONER\nfills OilySkinProducts\nfrom the definition", MINE, "8A5A00"),
      ("SPARQL\ntop 3 per category\nfor your skin type", "EEF5F4", GCOL["A"][0]),
    ]
    col = 2
    for i, (txt, bg, fg) in enumerate(boxes):
        c = cell(ws, r, col, txt, size=9.5, bold=True, colour=fg, fill=bg, center=True)
        c.border = Border(left=Side(style="thin", color=fg), right=Side(style="thin", color=fg),
                          top=Side(style="thin", color=fg), bottom=Side(style="thin", color=fg))
        if i < len(boxes) - 1:
            cell(ws, r, col + 1, "->", size=12, bold=True, colour=SUB, center=True)
        col += 2
        if col > NC:
            break
    ws.row_dimensions[r].height = 52
    r += 1
    # second row of the diagram: the side inputs
    cell(ws, r, 2, "", size=9)
    ws.row_dimensions[r].height = 8
    r += 1
    cell(ws, r, 2, "SIDE INPUT 1\nA CSV they typed themselves:  country -> Sephora link",
         span=5, size=9.5, colour=SUB, fill=ALT, center=True)
    cell(ws, r, 8, "SIDE INPUT 2\nDBpedia, live: country -> capital city -> geo:lat, geo:long.\n"
                   "They typed zero coordinates. This is what reuse actually looks like.",
         span=6, size=9.5, colour=SUB, fill=ALT, center=True)
    ws.row_dimensions[r].height = 44
    r += 2

    cell(ws, r, 2, "OUT:   9 products  =  3 cleansers + 3 moisturisers + 3 treatments,   "
                   "plus your local Sephora link,   plus whether there is a physical shop",
         span=NC - 1, size=11, bold=True, colour="4A3200", fill=MINE, center=True)
    ws.row_dimensions[r].height = 26
    r += 2

    # ---------------------------------------------------------- the steps
    band(ws, r, NC, "3.  THE SAME THING AS TEN STEPS", INK); r += 1
    # headers must sit on the same columns as the data below: 1, 2, 3-4, 5, 6-9
    for col, span_, h in ((1, 1, "#"), (2, 1, "Step"), (3, 3, "What they did"),
                          (6, 1, "Tool"), (7, 7, "My note")):
        if span_ > 1:
            ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + span_ - 1)
        c = ws.cell(row=r, column=col, value=h)
        c.font = Font(name=FONT, size=10.5, bold=True, color=PAPER)
        c.fill = PatternFill("solid", fgColor=INK)
        c.alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[r].height = 20
    r += 1
    for n, step, what, tool, note in ABESOVA_STEPS:
        stripe = (r % 2 == 0)
        hot = "WHOLE REASON" in note
        cell(ws, r, 1, n, size=10, bold=True, colour=SUB, center=True)
        cell(ws, r, 2, step, size=10, bold=True, colour=GCOL["A"][0], fill="EEF5F4")
        cell(ws, r, 3, what, span=3, size=10, fill=ALT if stripe else PAPER)
        cell(ws, r, 6, tool, size=9.5, italic=True, colour=SUB, fill=ALT if stripe else PAPER)
        cell(ws, r, 7, note, span=7, size=10, bold=hot,
             colour=FLAGT if hot else "3A3630", fill=FLAG if hot else MINE)
        ws.row_dimensions[r].height = 44
        r += 1
    r += 1

    # ---------------------------------------------------------- the clever bit
    band(ws, r, NC, "4.  THE ONE CLEVER IDEA, AND IT IS THE WHOLE REASON I READ THIS", MINEH); r += 2
    explain = (
      "They never tag a product as 'good for oily skin'. Not once. Instead they do this:\n\n"
      "   STEP 1   Query all reviews written by people with oily skin, average the stars, and\n"
      "            store it on the product:      Product  hasOilyScore  5.0\n\n"
      "   STEP 2   Then they DEFINE the class, once:\n"
      "            OilySkinProducts  owl:equivalentClass  ( hasOilyScore value 5 )\n\n"
      "   STEP 3   They press the reasoner. It goes and finds every product with a 5 and puts\n"
      "            it in the class by itself. Nobody typed a single membership.\n\n"
      "WHY THIS MATTERS TO ME\n"
      "If a new product arrives tomorrow with hasOilyScore 5.0, it lands in the class with zero\n"
      "extra work. No script to rerun, no list to update. A normal database cannot do this.\n"
      "This is the single best argument for using an ontology at all, and it is the mechanism\n"
      "my four defined classes use.\n\n"
      "WHAT I CHANGE\n"
      "Their score comes from STAR RATINGS. Mine comes from INGREDIENTS. Same machinery,\n"
      "completely different evidence. Theirs says 'people liked it'. Mine says 'it contains\n"
      "ceramides, no fragrance allergen, and nothing on Annex II'."
    )
    lines = explain.split("\n")
    ws.merge_cells(start_row=r, start_column=2, end_row=r + len(lines) - 1, end_column=NC)
    c = ws.cell(row=r, column=2, value=explain)
    c.font = Font(name=MONO, size=10, color="3A3226")
    c.fill = PatternFill("solid", fgColor=MINE)
    c.alignment = Alignment(vertical="top", indent=1)
    for k in range(len(lines)):
        ws.row_dimensions[r + k].height = 14
    r += len(lines) + 2

    # ---------------------------------------------------------- classes
    band(ws, r, NC, "5.  THEIR 36 CLASSES AND 12 PROPERTIES", INK); r += 1
    for col, span_, h in ((2, 1, "Class"), (3, 3, "Kind"), (6, 8, "Note")):
        if span_ > 1:
            ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + span_ - 1)
        c = ws.cell(row=r, column=col, value=h)
        c.font = Font(name=FONT, size=10.5, bold=True, color=PAPER)
        c.fill = PatternFill("solid", fgColor=INK)
        c.alignment = Alignment(vertical="center", indent=1)
    ws.row_dimensions[r].height = 20
    r += 1
    for name_, kind, note in ABESOVA_CLASSES:
        defined = kind == "DEFINED"
        cell(ws, r, 2, name_, size=10, bold=defined, mono=True,
             colour=MINEH if defined else "3A3630", fill=MINE if defined else PAPER)
        cell(ws, r, 3, kind, span=3, size=9.5, bold=defined,
             colour=MINEH if defined else SUB, fill=MINE if defined else PAPER)
        cell(ws, r, 6, note, span=8, size=9.5, mono=defined,
             colour="3A3226" if defined else SUB, fill=MINE if defined else PAPER)
        ws.row_dimensions[r].height = 15
        r += 1
    r += 1
    for kind, txt, note in ABESOVA_PROPS:
        bad = note.startswith("THEY ADMIT")
        cell(ws, r, 2, kind, size=9.5, colour=SUB)
        cell(ws, r, 3, txt, span=3, size=10, mono=True,
             colour=FLAGT if bad else "3A3630", fill=FLAG if bad else PAPER)
        cell(ws, r, 6, note, span=8, size=9.5, bold=bad,
             colour=FLAGT if bad else SUB, fill=FLAG if bad else PAPER)
        ws.row_dimensions[r].height = 15 if not bad else 28
        r += 1
    r += 1

    # ---------------------------------------------------------- what is broken
    band(ws, r, NC, "6.  WHAT IS WRONG WITH IT.  Say these before a supervisor finds them.", FLAGT); r += 1
    for k, v in ABESOVA_HONEST:
        cell(ws, r, 2, k, bold=True, size=10, colour=FLAGT, fill=FLAG)
        cell(ws, r, 3, v, span=NC - 2, size=10, colour="3A3630")
        ws.row_dimensions[r].height = 15 + 13 * (len(v) // 100)
        r += 1
    r += 1

    # ---------------------------------------------------------- limitation 3
    band(ws, r, NC, "7.  AND THE BEST SENTENCE IN MY WHOLE LITERATURE REVIEW", MINEH); r += 1
    lines = ABESOVA_LIMITATION.split("\n")
    ws.merge_cells(start_row=r, start_column=2, end_row=r + len(lines) - 1, end_column=NC)
    c = ws.cell(row=r, column=2, value=ABESOVA_LIMITATION)
    c.font = Font(name=MONO, size=10.5, bold=True, color="4A3200")
    c.fill = PatternFill("solid", fgColor=MINE)
    c.alignment = Alignment(vertical="top", indent=1)
    for k in range(len(lines)):
        ws.row_dimensions[r + k].height = 15
    r += len(lines)

    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 85
    return ws


# ============================================================ 4. APPEND TOOLS
def append_tools(wb):
    ws = wb["Tools"]
    r = ws.max_row + 2
    for row in EXTRA:
        if row[0] == "H":
            ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
            c = ws.cell(row=r, column=2, value=row[1])
            c.font = Font(name=FONT, size=11.5, bold=True, color=PAPER)
            c.fill = PatternFill("solid", fgColor=INK)
            c.alignment = Alignment(vertical="center")
            ws.row_dimensions[r].height = 26
            r += 1
            continue
        tool, one, does, link, use, why = row
        stripe = (r % 2 == 0)
        vals = [tool, one, does, link, use, why]
        for i, val in enumerate(vals, start=2):
            c = ws.cell(row=r, column=i, value=val)
            c.alignment = Alignment(vertical="top", wrap_text=True, indent=1)
            c.border = under
            if i == 2:
                c.font = Font(name=FONT, size=10.5, bold=True, color=INK)
                c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
            elif i == 5:
                c.font = Font(name=FONT, size=9, color="2166A5", underline="single")
                c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
            elif i == 6:
                yes = val == "YES"
                c.font = Font(name=FONT, size=10, bold=yes, color=GOODT if yes else SUB)
                c.fill = PatternFill("solid", fgColor=GOOD if yes else (ALT if stripe else PAPER))
                c.alignment = Alignment(horizontal="center", vertical="center")
            elif i == 7:
                hot = any(k in str(val) for k in ("ABESOVA", "BIT-TECH", "TOXIN", "NOT ONE"))
                c.font = Font(name=FONT, size=10, bold=hot, color=FLAGT if hot else SUB)
                c.fill = PatternFill("solid", fgColor=FLAG if hot else (ALT if stripe else PAPER))
            else:
                c.font = Font(name=FONT, size=10, color="3A3630")
                c.fill = PatternFill("solid", fgColor=ALT if stripe else PAPER)
        ws.row_dimensions[r].height = 58
        r += 1
    return ws


def main():
    wb = load_workbook(SRC)
    before = wb.sheetnames[:]
    build_gap(wb)
    build_reasoning(wb)
    build_abesova(wb)
    append_tools(wb)
    # keep her original order first, new tabs after
    order = [s for s in before] + [s for s in wb.sheetnames if s not in before]
    wb._sheets = [wb[s] for s in order]
    wb.save(SRC)
    print("saved:", SRC)
    print("tabs :", wb.sheetnames)


if __name__ == "__main__":
    main()
