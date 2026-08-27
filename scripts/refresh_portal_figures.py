"""
Make every number in the portal agree with the files

Why this is needed
  The portal was written in pieces over several weeks and each page was
  correct when it was written. The dataset kept moving, and pages that are not
  rebuilt keep the numbers they were born with.

  Four places were still telling a visitor something that is no longer true:

Usage:
    py refresh_portal_figures.py --dry     list what would change
    py refresh_portal_figures.py           change it
"""
import re
import csv
import sys
import collections
from pathlib import Path

csv.field_size_limit(10 ** 8)
PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
DRY = '--dry' in sys.argv


def load(p):
    try:
        with open(p, newline='', encoding='utf-8') as fh:
            return [{k: (v or '') for k, v in r.items()}
                    for r in csv.DictReader(fh)]
    except FileNotFoundError:
        return []


D = load('COMBINED_DATASET.csv')
N = len(D)


def g(r, c):
    return str(r.get(c, '')).strip()


def cnt(c):
    return sum(1 for r in D if g(r, c))


st = cnt('skin_type')
sn = cnt('sensitivity')
tier = collections.Counter(g(r, 'skin_type_tier') for r in D)
stated = sum(v for k, v in tier.items() if k in ('1', '2', '3'))
brands = len({g(r, 'brand').lower() for r in D if g(r, 'brand')})

html = PORTAL.read_text(encoding='utf-8')
before = html

print('=' * 74)
print('  MAKING EVERY NUMBER AGREE WITH THE FILES')
print('=' * 74)
print(f'  live figures: {N:,} products, skin type {100*st/N:.1f}%, '
      f'sensitivity {100*sn/N:.1f}%, {stated:,} of the skin types stated')
print()

# ---------------------------------------------------- 1. the wrong totals
changes = []
n_13384 = html.count('13,384')
if n_13384:
    html = html.replace('13,384', f'{N:,}')
    changes.append(f'{n_13384} occurrences of 13,384 became {N:,}')

# ------------------------------------------- 2. the claims about skin type
FIXES = [
    (r'0% skin type, being rebuilt',
     f'{100*st/N:.0f}% skin type, {100*stated/N:.0f}% of it stated by a source'),
    (r'the column is empty on purpose\s*\.?',
     'the column is now complete. '),
    (r'the previous version reached 74\.4%[^<]*',
     f'the previous version reached 74.4%. It now reads {100*st/N:.0f}%, '
     f'of which {100*stated/N:.0f}% is stated by a source and the rest is '
     f'inferred from the formula and marked tier 4. '),
    # The home page headline. These sit inside separate <div> tags, so the
    # sentence a reader sees never appears as one string in the source. That
    # is why the first attempt at this matched nothing: the pattern was
    # written against what the page reads like, not what it is made of.
    (r'<div class="n">0%</div><div class="l">skin type, being rebuilt</div>',
     f'<div class="n">{100*st/N:.0f}%</div><div class="l">skin type, '
     f'{100*stated/N:.0f}% of it stated</div>'),
    (r'the column is <b>empty on purpose</b>\.',
     'the column is <b>complete</b>.'),
    (r'skin type\s+11,3\d\d\s+8[0-9]\.\d%',
     f'skin type {st:,} {100*st/N:.1f}%'),
    (r'sensitivity\s+11,4\d\d\s+8[0-9]\.\d%',
     f'sensitivity {sn:,} {100*sn/N:.1f}%'),
]
for pat, rep in FIXES:
    n = len(re.findall(pat, html))
    if n:
        html = re.sub(pat, rep, html)
        changes.append(f'{n} x  {pat[:52]}')

# ------------------------------------- 3. the orphan that keeps coming back
if 'id="cd-now"' in html:
    html = re.sub(r'<section class="section[^"]*" id="cd-now">.*?</section>',
                  '', html, flags=re.S)
    changes.append('removed cd-now, a section with no navigation entry')

# ------------------------------------------------ 4. duplicated nav entries
nav_m = re.search(r'(<nav class="nav">)(.*?)(</nav>)', html, re.S)
if nav_m:
    seen, kept = set(), []
    for line in nav_m.group(2).splitlines():
        m = re.search(r'data-s="([a-z0-9-]+)"', line)
        if m:
            if m.group(1) in seen:
                continue
            seen.add(m.group(1))
        kept.append(line)
    newnav = nav_m.group(1) + '\n'.join(kept) + nav_m.group(3)
    if newnav != nav_m.group(0):
        html = html[:nav_m.start()] + newnav + html[nav_m.end():]
        changes.append('removed duplicated navigation entries')

# --------------------------------------------------- 5. drop dead nav links
ids = set(re.findall(r'<section class="section[^"]*" id="([a-z0-9-]+)"', html))
dead = [n for n in re.findall(r'data-s="([a-z0-9-]+)"', html) if n not in ids]
for d in set(dead):
    html = re.sub(r'\n\s*<a data-s="' + d + r'">[^<]*</a>', '', html)
if dead:
    changes.append(f'removed {len(set(dead))} navigation links pointing at '
                   f'nothing: {", ".join(sorted(set(dead)))}')

for c in changes:
    print(f'    {c}')
if not changes:
    print('    nothing needed changing')

ids = re.findall(r'<section class="section[^"]*" id="([a-z0-9-]+)"', html)
nav = re.findall(r'data-s="([a-z0-9-]+)"', html)
print(f'\n  {len(ids)} sections, {len(nav)} navigation links')
print(f'  sections with no link : '
      f'{[i for i in ids if i not in nav] or "none"}')
print(f'  links pointing nowhere: '
      f'{[n for n in nav if n not in ids] or "none"}')
print(f'  repeated section ids  : '
      f'{[k for k, v in collections.Counter(ids).items() if v > 1] or "none"}')

leftover = []
for probe, why in [('13,384', 'the old product count'),
                   ('0% skin type', 'the old skin type claim'),
                   ('being rebuilt', 'the old skin type claim'),
                   ('empty on purpose', 'the old skin type claim')]:
    if probe in html:
        leftover.append(f'{probe}  ({why})')
print(f'  stale text still present: {leftover or "none"}')

if DRY:
    print('\n  --dry, nothing written.')
    sys.exit(0)
if html != before:
    PORTAL.write_text(html, encoding='utf-8')
    print(f'\n  written. {len(before):,} -> {len(html):,} bytes')
else:
    print('\n  no change needed.')
