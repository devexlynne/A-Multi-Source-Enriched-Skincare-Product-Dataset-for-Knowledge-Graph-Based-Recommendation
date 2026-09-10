# -*- coding: utf-8 -*-
"""
Adds three tabs to the workbook and some rows to the Tools tab.
Nothing already in the file is changed.

  The gap            every paper, what is missing in it, what I do instead
  Reasoning + SHACL  the five ways to reason, and the SHACL code
  Abesova paper      the attached PDF explained

Plain black on white. One grey header row. No colours.

Run:  py add_gap_tabs.py
"""
import os
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from gap_data import (GAP_COLS, GAP, REASONING_INTRO, REASONING_COLS, REASONING,
                      SHACL_CODE, ABESOVA_FACTS, ABESOVA_STEPS, ABESOVA_CLASSES,
                      ABESOVA_PROPS, ABESOVA_HONEST, ABESOVA_LIMITATION,
                      ABESOVA_PIPELINE, ABESOVA_MAIN_IDEA, GAP_SUMMARY, SHACL_SENTENCE)
from tools_extra import EXTRA

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "PAPERS_TABLE.xlsx")          # her edited file, read only
OUT  = os.path.join(HERE, "PAPERS_TABLE_v2.xlsx")       # what this writes

BLACK = "000000"
GREY  = "666666"
HEAD  = "EDEDED"
FONT  = "Calibri"
MONO  = "Consolas"

thin   = Side(style="thin", color="D9D9D9")
under  = Border(bottom=thin)
above  = Border(top=Side(style="thin", color="9E9E9E"))


def head_block(ws, span, text, sub):
    """Plain title. No filled bar."""
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=span)
    c = ws.cell(row=1, column=1, value=text)
    c.font = Font(name=FONT, size=13, bold=True, color=BLACK)
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[1].height = 22
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=span)
    c = ws.cell(row=2, column=1, value=sub)
    c.font = Font(name=FONT, size=10, color=GREY)
    c.alignment = Alignment(vertical="top", wrap_text=True)
    ws.row_dimensions[2].height = 28
    ws.row_dimensions[3].height = 8


def section(ws, row, span, text):
    """Plain bold line with a rule above it."""
    ws.merge_cells(start_row=row, start_column=1, end_row=row, end_column=span)
    c = ws.cell(row=row, column=1, value=text)
    c.font = Font(name=FONT, size=11, bold=True, color=BLACK)
    c.border = above
    c.alignment = Alignment(vertical="center")
    ws.row_dimensions[row].height = 24


def table_head(ws, row, cols):
    for i, (h, w) in enumerate(cols, start=1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = Font(name=FONT, size=10, bold=True, color=BLACK)
        c.fill = PatternFill("solid", fgColor=HEAD)
        c.border = under
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.row_dimensions[row].height = 28


def put(ws, row, col, val, *, span=1, bold=False, size=10, colour=BLACK,
        mono=False, wrap=True, top=False):
    if span > 1:
        ws.merge_cells(start_row=row, start_column=col, end_row=row, end_column=col + span - 1)
    c = ws.cell(row=row, column=col, value=val)
    c.font = Font(name=MONO if mono else FONT, size=size, bold=bold, color=colour)
    c.alignment = Alignment(vertical="top" if top else "center", wrap_text=wrap)
    return c


def est_height(text, width_chars, line=13, pad=6):
    lines = 1
    for para in str(text).split("\n"):
        lines += max(1, -(-len(para) // width_chars)) - 1
        lines += 1
    return max(16, pad + line * max(1, lines - 1))


# ------------------------------------------------------------------- the gap
def build_gap(wb):
    if "The gap" in wb.sheetnames:
        del wb["The gap"]
    ws = wb.create_sheet("The gap")
    NC = len(GAP_COLS)
    head_block(ws, NC, "The gap",
               "One row per paper. Column 3 is what their work does not have. "
               "Columns 4 and 5 are mine: what I do instead, and what I still do not have.")
    table_head(ws, 4, GAP_COLS)

    r = 5
    for row in GAP:
        if len(row) == 3:
            g, name, why = row
            section(ws, r, NC, f"Group {g}. {name}. {why}")
            r += 1
            continue
        for i, val in enumerate(row, start=1):
            c = ws.cell(row=r, column=i, value=val)
            c.font = Font(name=FONT, size=10, bold=(i == 2), color=BLACK)
            c.alignment = Alignment(vertical="top", wrap_text=True)
            c.border = under
        ws.row_dimensions[r].height = max(
            est_height(row[2], 44), est_height(row[3], 44),
            est_height(row[4], 44), est_height(row[5], 33))
        r += 1

    r += 1
    section(ws, r, NC, "The gap in one sentence")
    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=NC)
    c = ws.cell(row=r, column=1, value=GAP_SUMMARY)
    c.font = Font(name=FONT, size=10.5, color=BLACK)
    c.alignment = Alignment(vertical="top", wrap_text=True)
    ws.row_dimensions[r].height = 78

    ws.freeze_panes = "C5"
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 90
    return ws


# ------------------------------------------------------- reasoning and SHACL
def build_reasoning(wb):
    if "Reasoning + SHACL" in wb.sheetnames:
        del wb["Reasoning + SHACL"]
    ws = wb.create_sheet("Reasoning + SHACL")
    NC = len(REASONING_COLS)
    head_block(ws, NC, "Reasoning, and where SHACL fits", REASONING_INTRO)
    table_head(ws, 4, REASONING_COLS)

    r = 5
    for row in REASONING:
        if row[0] == "H":
            section(ws, r, NC, row[1].strip())
            r += 1
            continue
        for i, val in enumerate(row, start=1):
            c = ws.cell(row=r, column=i, value=val)
            c.font = Font(name=FONT, size=10, bold=(i == 1), color=BLACK)
            c.alignment = Alignment(
                horizontal="center" if i == 5 else "general",
                vertical="top", wrap_text=True)
            c.border = under
        ws.row_dimensions[r].height = max(
            est_height(row[1], 44), est_height(row[2], 52),
            est_height(row[5], 44))
        r += 1

    r += 1
    section(ws, r, NC, "The code. Put these four in a file called shapes.ttl")
    r += 2
    for caption, code in SHACL_CODE:
        put(ws, r, 1, caption, span=NC, bold=True, size=10.5)
        ws.row_dimensions[r].height = 18
        r += 1
        lines = code.split("\n")
        ws.merge_cells(start_row=r, start_column=1, end_row=r + len(lines) - 1, end_column=NC)
        c = ws.cell(row=r, column=1, value=code)
        c.font = Font(name=MONO, size=9.5, color=BLACK)
        c.alignment = Alignment(vertical="top", wrap_text=False)
        for k in range(len(lines)):
            ws.row_dimensions[r + k].height = 13
        r += len(lines) + 1

    section(ws, r, NC, "The sentence for my chapter")
    r += 1
    ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=NC)
    c = ws.cell(row=r, column=1, value=SHACL_SENTENCE)
    c.font = Font(name=FONT, size=10.5, color=BLACK)
    c.alignment = Alignment(vertical="top", wrap_text=True)
    ws.row_dimensions[r].height = 62

    ws.freeze_panes = "B5"
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 90
    return ws


# ------------------------------------------------------------- Abesova paper
def build_abesova(wb):
    name = "Abesova paper"
    if name in wb.sheetnames:
        del wb[name]
    ws = wb.create_sheet(name)
    NC = 5
    for i, w in enumerate([4, 26, 46, 26, 54], start=1):
        ws.column_dimensions[get_column_letter(i)].width = w

    head_block(ws, NC, "Abesova 2023, the paper my supervisor sent",
               "A student course project, so it is not peer reviewed and I have to say so. "
               "But the main idea in it is the one my thesis uses, and its third limitation is my contribution.")

    r = 4
    section(ws, r, NC, "1. What it is"); r += 1
    for k, v in ABESOVA_FACTS:
        put(ws, r, 2, k, bold=True, top=True)
        c = put(ws, r, 3, v, span=NC - 2, top=True)
        c.border = under
        ws.cell(row=r, column=2).border = under
        ws.row_dimensions[r].height = est_height(v, 118)
        r += 1
    r += 1

    section(ws, r, NC, "2. What they did, step by step"); r += 1
    table_head(ws, r, [("", 4), ("Step", 26), ("What they did", 46), ("Tool", 26), ("My note", 54)])
    r += 1
    for n, step, what, tool, note in ABESOVA_STEPS:
        for col, val, bold in ((1, n, False), (2, step, True), (3, what, False),
                               (4, tool, False), (5, note, False)):
            c = ws.cell(row=r, column=col, value=val)
            c.font = Font(name=FONT, size=10, bold=bold, color=BLACK)
            c.alignment = Alignment(vertical="top", wrap_text=True)
            c.border = under
        ws.row_dimensions[r].height = max(est_height(what, 44), est_height(note, 52))
        r += 1
    r += 1

    section(ws, r, NC, "3. The pipeline, in words"); r += 1
    for line in ABESOVA_PIPELINE:
        put(ws, r, 2, line, span=NC - 1, mono=True, size=10, top=True)
        ws.row_dimensions[r].height = 15
        r += 1
    r += 1

    section(ws, r, NC, "4. The main idea, and it is the one I use"); r += 1
    lines = ABESOVA_MAIN_IDEA.split("\n")
    ws.merge_cells(start_row=r, start_column=2, end_row=r + len(lines) - 1, end_column=NC)
    c = ws.cell(row=r, column=2, value=ABESOVA_MAIN_IDEA)
    c.font = Font(name=FONT, size=10.5, color=BLACK)
    c.alignment = Alignment(vertical="top", wrap_text=False)
    for k in range(len(lines)):
        ws.row_dimensions[r + k].height = 14
    r += len(lines) + 1

    section(ws, r, NC, "5. Their classes and properties"); r += 1
    table_head(ws, r, [("", 4), ("Class", 26), ("Kind", 46), ("", 26), ("Note", 54)])
    r += 1
    for name_, kind, note in ABESOVA_CLASSES:
        put(ws, r, 2, name_, mono=True, bold=(kind == "defined")).border = under
        put(ws, r, 3, kind, bold=(kind == "defined")).border = under
        put(ws, r, 4, note, span=2, top=True).border = under
        ws.row_dimensions[r].height = 15
        r += 1
    r += 1
    for kind, txt, note in ABESOVA_PROPS:
        put(ws, r, 2, kind, colour=GREY).border = under
        put(ws, r, 3, txt, mono=True).border = under
        put(ws, r, 4, note, span=2, top=True, size=9.5, colour=GREY).border = under
        ws.row_dimensions[r].height = est_height(note, 76) if note else 15
        r += 1
    r += 1

    section(ws, r, NC, "6. What is wrong with it. Say these first."); r += 1
    for k, v in ABESOVA_HONEST:
        put(ws, r, 2, k, bold=True, top=True).border = under
        put(ws, r, 3, v, span=NC - 2, top=True).border = under
        ws.row_dimensions[r].height = est_height(v, 118)
        r += 1
    r += 1

    section(ws, r, NC, "7. Their third limitation"); r += 1
    lines = ABESOVA_LIMITATION.split("\n")
    ws.merge_cells(start_row=r, start_column=2, end_row=r + len(lines) - 1, end_column=NC)
    c = ws.cell(row=r, column=2, value=ABESOVA_LIMITATION)
    c.font = Font(name=FONT, size=10.5, color=BLACK)
    c.alignment = Alignment(vertical="top", wrap_text=False)
    for k in range(len(lines)):
        ws.row_dimensions[r + k].height = 14

    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 90
    return ws


# ----------------------------------------------------------- append to Tools
def append_tools(wb):
    ws = wb["Tools"]
    r = ws.max_row + 2
    for row in EXTRA:
        if row[0] == "H":
            ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=7)
            c = ws.cell(row=r, column=2, value=row[1])
            c.font = Font(name=FONT, size=11, bold=True, color=BLACK)
            c.border = above
            c.alignment = Alignment(vertical="center")
            ws.row_dimensions[r].height = 24
            r += 1
            continue
        for i, val in enumerate(row, start=2):
            c = ws.cell(row=r, column=i, value=val)
            c.font = Font(name=FONT, size=10, bold=(i == 2), color=BLACK)
            c.alignment = Alignment(
                horizontal="center" if i == 6 else "general",
                vertical="top", wrap_text=True)
            c.border = under
        ws.row_dimensions[r].height = max(est_height(row[2], 44),
                                          est_height(row[5], 52))
        r += 1
    return ws


def main():
    wb = load_workbook(SRC)
    before = wb.sheetnames[:]
    build_gap(wb)
    build_reasoning(wb)
    build_abesova(wb)
    append_tools(wb)
    order = before + [s for s in wb.sheetnames if s not in before]
    wb._sheets = [wb[s] for s in order]
    wb.save(OUT)
    print("saved:", OUT)
    print("tabs :", wb.sheetnames)


if __name__ == "__main__":
    main()
