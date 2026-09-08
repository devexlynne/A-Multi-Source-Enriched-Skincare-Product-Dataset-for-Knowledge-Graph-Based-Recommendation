"""
Turns 00_EXPLAIN_EVERY_PAPER.md into a printable PDF.

Markdown files show as raw text with all the # and ** symbols when you send
them on WhatsApp. This makes a proper document instead.

Run:  py make_pdf.py
Needs pandoc and xelatex.
"""
import os, re, subprocess, sys, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "00_EXPLAIN_EVERY_PAPER.md")
OUT  = os.path.join(HERE, "Literature_review_Lynne.pdf")

# ------------------------------------------------------------------ preamble
PREAMBLE = r"""
\usepackage[a4paper,top=2.1cm,bottom=2.2cm,left=2.2cm,right=2.2cm]{geometry}
\usepackage{fontspec}
\usepackage{xcolor}
\usepackage{sectsty}
\usepackage{titlesec}
\usepackage{fancyhdr}
\usepackage{longtable,booktabs,array}
\usepackage{ragged2e}
\usepackage{enumitem}
\usepackage{tcolorbox}
\tcbuselibrary{skins,breakable}

% ---- colours, warm and quiet -------------------------------------------
\definecolor{ink}{HTML}{2E2A25}
\definecolor{teal}{HTML}{1F6F6B}
\definecolor{plum}{HTML}{6B4E9B}
\definecolor{rose}{HTML}{8C4A62}
\definecolor{amber}{HTML}{A6612F}
\definecolor{sand}{HTML}{FFF6E0}
\definecolor{sandline}{HTML}{E8A33D}
\definecolor{rule}{HTML}{D8D2C6}
\definecolor{soft}{HTML}{6E675E}

% ---- fonts --------------------------------------------------------------
\setmainfont{DejaVu Serif}[Scale=0.90]
\setsansfont{DejaVu Sans}[Scale=0.86]
\setmonofont{DejaVu Sans Mono}[Scale=0.78]

\color{ink}
\setlength{\parskip}{5pt}
\setlength{\parindent}{0pt}
\linespread{1.10}
\raggedright

% ---- headings -----------------------------------------------------------
\newcommand{\barsec}[1]{%
  \colorbox{ink}{\parbox{\dimexpr\textwidth-2\fboxsep\relax}{%
  \vspace{4pt}\sffamily\bfseries\Large\color{white}#1\vspace{4pt}}}}
\titleformat{\section}{}{}{0pt}{\barsec}
\titlespacing*{\section}{0pt}{22pt}{12pt}

\titleformat{\subsection}
  {\sffamily\bfseries\large\color{teal}}{}{0pt}{}
  [\vspace{-7pt}{\color{rule}\rule{\textwidth}{0.6pt}}]
\titlespacing*{\subsection}{0pt}{17pt}{5pt}

\titleformat{\subsubsection}
  {\sffamily\bfseries\normalsize\color{amber}}{}{0pt}{}
\titlespacing*{\subsubsection}{0pt}{12pt}{3pt}

% ---- page furniture -----------------------------------------------------
\pagestyle{fancy}\fancyhf{}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\headrule}{\hbox to\headwidth{\color{rule}\leaders\hrule height \headrulewidth\hfill}}
\fancyhead[L]{\sffamily\footnotesize\color{soft}Literature review, ontology phase}
\fancyhead[R]{\sffamily\footnotesize\color{soft}Lynne, MSc thesis, BAU}
\fancyfoot[C]{\sffamily\footnotesize\color{soft}\thepage}

% ---- tables -------------------------------------------------------------
\renewcommand{\arraystretch}{1.22}
\let\oldlongtable\longtable
\def\longtable{\footnotesize\oldlongtable}

% ---- block quotes become the "say this" boxes ---------------------------
\renewenvironment{quote}
 {\begin{tcolorbox}[breakable, enhanced, colback=sand, colframe=sandline,
    boxrule=0pt, leftrule=3pt, arc=1pt, left=9pt, right=9pt, top=7pt, bottom=7pt]}
 {\end{tcolorbox}}

% ---- code ---------------------------------------------------------------
\usepackage{fvextra}
\fvset{breaklines=true, breakanywhere=true, fontsize=\small}

\PassOptionsToPackage{hidelinks}{hyperref}
"""

def main():
    md = open(SRC, encoding="utf-8").read()

    # The cover page carries the title, and pandoc builds its own contents,
    # so drop the file's own title and its hand-written contents table first.
    md = re.sub(r'^# How to explain every paper.*?\n', '', md, count=1, flags=re.M)
    md = re.sub(r'^# CONTENTS\n.*?(?=^---$)', '', md, count=1, flags=re.M | re.S)

    # Then shift the rest down a level, so PART and GROUP become the coloured
    # bars and each paper sits underneath as a subsection.
    md = re.sub(r'^# ', '## ', md, flags=re.M)
    md = re.sub(r'^## PART', '# PART', md, flags=re.M)
    md = re.sub(r'^## GROUP', '# GROUP', md, flags=re.M)

    tmp = os.path.join(HERE, "_pdf_src.md")
    pre = os.path.join(HERE, "_pdf_preamble.tex")
    open(tmp, "w", encoding="utf-8").write(md)
    open(pre, "w", encoding="utf-8").write(PREAMBLE)

    today = datetime.date.today().strftime("%d %B %Y")
    cmd = [
        "pandoc", tmp, "-o", OUT,
        "--pdf-engine=xelatex",
        "-H", pre,
        "--toc", "--toc-depth=2",
        "-V", "documentclass=article",
        "-V", "fontsize=10pt",
        "-V", "title=Literature review: ontologies for skincare",
        "-V", "subtitle=28 papers, what each one did, and what we take from it",
        "-V", "author=Lynne \\\\ MSc thesis, Beirut Arab University",
        "-V", f"date={today}",
        "-V", "colorlinks=false",
        "--highlight-style=tango",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-3000:]); print(r.stderr[-3000:]); sys.exit(1)

    for f in (tmp, pre):
        os.remove(f)
    kb = os.path.getsize(OUT) // 1024
    print(f"written: {OUT}  ({kb} KB)")

if __name__ == "__main__":
    main()
