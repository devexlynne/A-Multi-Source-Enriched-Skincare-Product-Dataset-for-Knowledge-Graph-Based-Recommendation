"""
Putting the portal in order

The portal grew one section at a time, so it ended up with 41 pages in 12
groups, the merge explained twice and statistics in three places. Nothing was
wrong with the pages. The order was wrong.

This rearranges them into the order somebody would be walked through, and
moves the deep detail into an appendix at the bottom rather than the middle of
the path.

  THE MAIN PATH
    1 start            what this is
    2 the dataset      every statistic, in one place
    3 where it came    the three sources, one page each
    4 how it was clean the rules, the merge, the faults
    5 validation       what was checked and what it found
    6 ontology         the next phase
    7 reference        papers, files, code

  THE APPENDIX
    the eight skin type pages, Amazon matching, distance metrics and the
    eleven cleaning steps. Still there, still linked, out of the way.

It only moves and renames. No section text is edited, so nothing that was
checked against the data can drift.

Usage:
    py portal_restructure.py
"""
import re
import shutil
import datetime
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')

# ---------------------------------------------------------------- the order
# (group, section id, the title as it appears in the sidebar)
# A group of '' means it carries on under the group above.
PLAN = [
    ('start', 'home', 'Start here'),

    ('the dataset', 'fs-all', '1. Every statistic'),

    ('where it came from', 'src-global', '2a. Global (Skinsort)'),
    ('', 'lb-retail', '2b. Lebanese retail'),
    ('', 'lb-origin', '2c. Lebanese origin'),

    ('how it was cleaned', 'cd-rules', '3a. When a value is kept'),
    ('', 'mg-merge', '3b. Three files into one'),
    ('', 'cd-fixed', '3c. What went wrong'),
    ('', 'cd-left', '3d. What is still empty'),

    ('validation', 'va-why', '4a. What checking means'),
    ('', 'va-checks', '4b. The 48 checks'),
    ('', 'va-found', '4c. What it found'),

    ('ontology', 'ont-what', '5a. What an ontology is'),
    ('', 'ont-reuse', '5b. Ontologies to reuse'),
    ('', 'ont-model', '5c. The model I propose'),
    ('', 'ont-populate', '5d. Filling it with our data'),
    ('', 'ont-validate', '5e. Checking the ontology'),
    ('', 'ont-useback', '5f. Using it on the dataset'),

    ('reference', 'papers', 'Papers'),
    ('', 'databases', 'Ingredient databases'),
    ('', 'files', 'Files and code'),

    ('appendix, skin type', 'st-why', 'A1. Starting again'),
    ('', 'st-tries', 'A2. Everything I tried'),
    ('', 'st-serper', 'A3. How Serper works'),
    ('', 'st-trace', 'A4. Serper, traced'),
    ('', 'st-passes', 'A5. The seven passes'),
    ('', 'st-tiers', 'A6. The four tiers'),
    ('', 'st-rules', 'A7. Sentence to value'),
    ('', 'st-fixes', 'A8. Mistakes I fixed'),
    ('', 'st-results', 'A9. The final numbers'),

    ('appendix, the rest', 'steps', 'B1. The eleven cleaning steps'),
    ('', 'amazon', 'B2. Amazon matching'),
    ('', 'metrics', 'B3. Distance metrics'),
    ('', 'inci', 'B4. INCI and CosIng'),
    ('', 'mg-rules', 'B5. Keeping the best copy'),
    ('', 'mg-checks', 'B6. The fourteen checks'),
    ('', 'mg-price', 'B7. Price and rating'),
    ('', 'lb-shops', 'B8. The six shops, long version'),
    ('', 'lb-dedup', 'B9. Lebanese cleaning, long version'),
    ('', 'lb-match', 'B10. Matching and reviews'),
    ('', 'lo-find', 'B11. Finding the brands, long version'),
    ('', 'lo-domains', 'B12. Sites kept and dropped'),
    ('', 'lo-gaps', 'B13. Lebanese origin gaps'),
    ('', 'cd-paid', 'B14. What was paid for'),
]

# Pages folded into the new ones, so they are dropped from the portal. Their
# content now lives in the section named beside them.
FOLDED = {
    'dataset': 'fs-all',
    'cb-one': 'fs-all',
    'cb-stats': 'fs-all',
    'cd-now': 'fs-all',
    'lo-what': 'lb-origin',
    'on-ready': 'ont-what',
    'on-model': 'ont-model',
    'on-check': 'ont-validate',
}

html = PORTAL.read_text(encoding='utf-8')
backup = PORTAL.with_name(
    f'Lynne-Thesis Portal BACKUP {datetime.datetime.now():%H%M}.html')
shutil.copy(PORTAL, backup)

# ------------------------------------------------------------ pull them out
sections = {}
for m in re.finditer(r'<section class="section[^"]*" id="([^"]+)">.*?</section>',
                     html, re.S):
    sections[m.group(1)] = m.group(0)

head, tail = html.split('<main class="main">', 1)
_, tail = tail.split('</main>', 1) if '</main>' in tail else ('', tail)

wanted = [p[1] for p in PLAN]
missing = [i for i in wanted if i not in sections]
extra = [i for i in sections if i not in wanted and i not in FOLDED]

print('=' * 70)
print('  PUTTING THE PORTAL IN ORDER')
print('=' * 70)
print(f'  sections found        {len(sections)}')
print(f'  places in the plan    {len(wanted)}')
if missing:
    print(f'\n  NOT WRITTEN YET, the plan leaves a place for them:')
    for i in missing:
        print(f'     {i}')
if extra:
    print(f'\n  in the portal but not in the plan, left where they are:')
    for i in extra:
        print(f'     {i}')

# --------------------------------------------------------------- rebuild
body = []
for grp, sid, title in PLAN:
    if sid in sections:
        body.append(sections[sid])
for sid in extra:
    body.append(sections[sid])

# the first section on the path is the one that shows when the page opens
out = []
first = True
for chunk in body:
    chunk = chunk.replace('<section class="section on"', '<section class="section"')
    if first:
        chunk = chunk.replace('<section class="section"',
                              '<section class="section on"', 1)
        first = False
    out.append(chunk)

nav_items = []
for grp, sid, title in PLAN:
    if sid not in sections:
        continue
    if grp:
        nav_items.append(f'    <div class="grp">{grp}</div>')
    nav_items.append(f'    <a data-s="{sid}">{title}</a>')
if extra:
    nav_items.append('    <div class="grp">not yet filed</div>')
    for sid in extra:
        nav_items.append(f'    <a data-s="{sid}">{sid}</a>')
nav = '<nav class="nav">\n' + '\n'.join(nav_items) + '\n  </nav>'

html2 = re.sub(r'<nav class="nav">.*?</nav>', nav, head, flags=re.S)
html2 += '<main class="main">\n\n' + '\n\n'.join(out) + '\n\n</main>' + tail

PORTAL.write_text(html2, encoding='utf-8')

kept = sum(1 for _, s, _ in PLAN if s in sections)
print()
print(f'  pages on the main path   '
      f'{sum(1 for g, s, t in PLAN if s in sections and not t.startswith(("A", "B")))}')
print(f'  pages in the appendix    '
      f'{sum(1 for g, s, t in PLAN if s in sections and t.startswith(("A", "B")))}')
print(f'  pages folded away        {len([k for k in FOLDED if k in sections])}')
print(f'  portal {len(html):,} -> {len(html2):,} characters')
print(f'  a copy of the old one is at {backup.name}')
