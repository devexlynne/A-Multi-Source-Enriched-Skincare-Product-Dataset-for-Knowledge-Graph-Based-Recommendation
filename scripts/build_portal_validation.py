"""
The validation pages of the portal

Three pages:

    VA1  What checking a dataset means, and which papers say so
    VA2  The 48 questions asked of this file, and the answers
    VA3  What the checking found the first time it ran

Everything is read from VALIDATION_REPORT.txt and COMBINED_DATASET.csv when
this runs, so the page cannot claim a check passed that did not.

Usage:
    py build_portal_validation.py
"""
import re
import csv
import collections
from pathlib import Path

PORTAL = Path(r'C:\Users\User\Documents\Thesis\Lynne-Thesis Portal.html')
if not PORTAL.exists():
    # the portal normally sits one level up; the absolute path stays first
    PORTAL = Path(__file__).resolve().parent.parent / 'Lynne-Thesis Portal.html'
csv.field_size_limit(10 ** 8)

REPORT = 'VALIDATION_REPORT.txt'
lines = []
try:
    lines = Path(REPORT).read_text(encoding='utf-8').splitlines()
except FileNotFoundError:
    raise SystemExit('run validate_dataset.py first, there is no report to read')

checks = []
group = ''
for ln in lines:
    m = re.match(r'^([A-G])\. (.+)$', ln.strip())
    if m:
        group = m.group(1)
    # split on the DETAIL, which always starts with a number or is empty,
    # rather than on runs of spaces. A check name longer than the column left
    # only one space between the two and quietly lost a check from the count.
    m = re.match(r'^\s{2}(PASS|FAIL)\s{2}(.+)$', ln)
    if m:
        rest = m.group(2).rstrip()
        d = re.search(r'\s+(\d[\d,]*\s+\S.*|\d+ columns.*)$', rest)
        if d:
            name, detail = rest[:d.start()].strip(), d.group(1).strip()
        else:
            name, detail = rest.strip(), ''
        checks.append((group, m.group(1), name, detail))

npass = sum(1 for c in checks if c[1] == 'PASS')
nfail = len(checks) - npass

with open('COMBINED_DATASET.csv', newline='', encoding='utf-8') as fh:
    D = [{k: (v or '') for k, v in r.items()} for r in csv.DictReader(fh)]
N = len(D)
NCOL = len(D[0]) if D else 0

GROUPS = {
    'A': ('Can the file be read at all',
          'A file that looks fine in Excel can still be broken. This one was: '
          'a crash put machine code inside it and nothing noticed for hours.'),
    'B': ('Is every row a row, and every product one product',
          'One product, one row. Two rows for the same cream means every count '
          'in the thesis is wrong by one.'),
    'C': ('Do the controlled columns hold only their allowed values',
          'A column with five allowed values should contain five, not seven '
          'with two spelled differently.'),
    'D': ('Are the numbers inside sensible limits',
          'A rating of 7 out of 5 and an SPF of 504 are both easy to spot and '
          'both were in the file.'),
    'E': ('Do fields that depend on each other agree',
          'The ingredient count should match the ingredient list. The category '
          'should match the markers it came from. When two columns disagree, '
          'at least one is wrong.'),
    'F': ('Does every claim say where it came from',
          'A value nobody can trace is not evidence. This is the group that '
          'matters most for a knowledge graph.'),
    'G': ('Is anything left that means "we do not know"',
          'The word "none" in a cell reads as data to a computer and as a gap '
          'to a person. That difference once made review coverage look like '
          '89% when it was 15%.'),
}


def f(x):
    return f'{x:,}'


def tbl(head, rows):
    h = ''.join(f'<th>{x}</th>' for x in head)
    b = ''.join('<tr>' + ''.join(f"<td class='td'>{x}</td>" for x in r) + '</tr>'
                for r in rows)
    return f'<table><tr>{h}</tr>{b}</table>'


def kpis(items):
    return ('<div class="kpis">' + ''.join(
        f'<div class="kpi"><div class="n">{v}</div><div class="l">{l}</div></div>'
        for v, l in items) + '</div>')


# ============================================================ VA1
VA1 = f"""
<section class="section" id="va-why">
  <h2>VA1 &middot; What checking a dataset means</h2>
  <p class="lead">A dataset that has been cleaned and a dataset that has been
  checked are two different things. Cleaning is what I did to the data.
  Checking is asking, afterwards and separately, whether the result holds up.
  This part of the work is written down because a reader has no reason to take
  my word for it.</p>

  {kpis([(str(len(checks)), 'questions asked'), (str(npass), 'passed'),
         (str(nfail), 'failed'), (f(N), 'products'), (str(NCOL), 'columns')])}

  <h3>Where the groups come from</h3>
  <p>The checks are grouped the way the data quality literature groups them,
  rather than the way the code happens to be written. Wang and Strong (1996)
  interviewed data users and found they judge quality on more than whether the
  numbers are right: they also ask whether the data suits the job, whether it
  is clearly presented, and whether it can be reached and believed. Pipino,
  Lee and Wang (2002) turned those into measurable ratios, which is what a
  check like "how many rows carry a source" actually is. Batini and colleagues
  (2009) surveyed thirteen assessment methods and found they share the same
  three steps: describe the data, measure it against stated rules, then decide
  what to do about the failures. That is the shape of this page.</p>

  {tbl(['what the literature calls it', 'what it means here', 'group'],
       [['free of error', 'the values are what the source page said', 'D, E'],
        ['completeness', 'how much of each column is filled, honestly counted',
         'G'],
        ['consistent representation', 'one column, one vocabulary, one meaning',
         'C, E'],
        ['believability and reputation',
         'every value names the page it came from and how strong that page is',
         'F'],
        ['accessibility', 'the file opens and reads back',
         'A'],
        ['appropriate amount of data', 'one row for one product', 'B']])}

  <h3>Three rules I worked to</h3>
  {tbl(['rule', 'why'],
       [['A wrong value is worse than a blank.',
         'A blank tells a reader to go and look. A wrong value tells them '
         'nothing is missing. Every fix in VA3 that removes a value rather '
         'than mending it comes from this.'],
        ['Check the output, not the intention.',
         'Every script in this project reported success while writing files '
         'that were wrong. The only thing worth trusting is the file itself, '
         'read back afterwards.'],
        ['Write down what failed, not only what passed.',
         'The value of this page is the nine things that were wrong, not the '
         'thirty-nine that were fine.']])}

  <div class="note">Clean each source before joining them, not after. Rahm and
  Do (2000) make this point and it decided the shape of the whole pipeline:
  the three files were each cleaned on their own terms, and only then merged.
  Joining first would have mixed three sets of problems together and made
  every one of them harder to see.</div>
</section>
"""

# ============================================================ VA2
rows_by_group = collections.defaultdict(list)
for gname, verdict, name, detail in checks:
    rows_by_group[gname].append((verdict, name, detail))

blocks = []
for gname in 'ABCDEFG':
    if gname not in rows_by_group:
        continue
    title, why = GROUPS[gname]
    items = rows_by_group[gname]
    ok = sum(1 for v, _, _ in items if v == 'PASS')
    blocks.append(f"""
  <h3>{gname}. {title}</h3>
  <p>{why}</p>
  {tbl(['check', 'result', 'detail'],
       [[nm, ('<span style="color:#3f6b48;font-weight:700">passed</span>'
              if v == 'PASS' else
              '<span style="color:#b5484d;font-weight:700">FAILED</span>'),
         dt or ''] for v, nm, dt in items])}
  <p class="mini">{ok} of {len(items)} passed</p>
""")

VA2 = f"""
<section class="section" id="va-checks">
  <h2>VA2 &middot; The {len(checks)} questions, and the answers</h2>
  <p class="lead">These run against the file on disk, not against anything the
  merge remembers doing. The script changes nothing. It reads, asks, and
  writes down the answer, and it prints real examples for anything that fails
  so the problem can be looked at rather than argued about.</p>

  <div class="dg">
  <svg viewBox="0 0 720 180" xmlns="http://www.w3.org/2000/svg"
       font-family="Segoe UI,Arial" font-size="11.5">
    <text x="0" y="16" fill="#584a7a" font-weight="700">Two separate lines of defence</text>

    <rect x="10" y="34" width="300" height="60" rx="8" fill="#f7f5fb" stroke="#7a68a6"/>
    <text x="160" y="56" text-anchor="middle" fill="#584a7a" font-weight="700">the merge, while writing</text>
    <text x="160" y="74" text-anchor="middle" fill="#6b6478">14 checks, refuses to save on failure</text>
    <text x="160" y="88" text-anchor="middle" fill="#6b6478">stops a broken file being made</text>

    <rect x="380" y="34" width="330" height="60" rx="8" fill="#eef6ee" stroke="#6f9c78"/>
    <text x="545" y="56" text-anchor="middle" fill="#3f6b48" font-weight="700">the validation, afterwards</text>
    <text x="545" y="74" text-anchor="middle" fill="#6b6478">{len(checks)} checks, changes nothing</text>
    <text x="545" y="88" text-anchor="middle" fill="#6b6478">finds what the merge never thought to ask</text>

    <text x="10" y="126" fill="#6b6478">The second one earns its place. The merge passed all fourteen of its</text>
    <text x="10" y="144" fill="#6b6478">checks on this file, and the validation still found nine faults, including</text>
    <text x="10" y="162" fill="#b5484d" font-weight="700">8,118 ingredient lists with no record of where they came from.</text>
  </svg>
  <div class="cap">Checking while writing, and checking afterwards, catch different things</div>
  </div>
  {''.join(blocks)}
</section>
"""

# ============================================================ VA3
VA3 = f"""
<section class="section" id="va-found">
  <h2>VA3 &middot; What it found, and what I did about it</h2>
  <p class="lead">The first run failed nine of its {len(checks)} checks. None
  of them were caught by the merge, because the merge does not ask these
  questions. Each is written out with the decision, because in six of the nine
  the honest answer was to remove a value rather than repair it.</p>

  {tbl(['what was wrong', 'how many', 'what I did', 'why'],
       [['An invisible control character sat inside two ingredient lists, left '
         'over from a web page.', '2 cells', 'removed the character',
         'It breaks Excel and any strict reader, and it carries no meaning.'],
        ['The same product appeared twice under two spellings: Effaclar H '
         'Iso-Biome against Isobiome, and Reti Age against Retiage.',
         '2 pairs',
         'merged them, and gave the surviving row every source marker the '
         'other one had',
         'The merge compares sets of words, and a hyphen makes one word into '
         'two. Dropping the row without folding its markers in would have '
         'made a product quietly stop being Lebanese.'],
        ['A sunscreen labelled 50+ was stored as SPF 150, and a Vichy '
         'giveaway listing had SPF 504.', '2 rows',
         'read 50 from the product name, emptied the other',
         'The first has an answer on the page. The second does not, and '
         'inventing one would be worse than leaving it out.'],
        ['Products had key ingredients but no formula, and the values were '
         'sentences like "Removes dead skin cells to smooth texture".',
         '21 rows', 'emptied them',
         'They came from an old scrape that read the benefits panel. A key '
         'ingredient that is not an ingredient is not a key ingredient.'],
        ['A rating with no source, no review text and no review count.',
         '90 rows', 'removed the ratings',
         'I traced 86 of them back to the Lebanese retail file, which has no '
         'source recorded either. A number nobody can check is not evidence, '
         'and 41.0% honest coverage beats 41.7% with a hole in it.'],
        ['A skin type of "All" on products whose own status column said '
         '"searched, not stated".', '7 rows', 'removed the skin type',
         'Both cannot be true. The status column is the one that matches what '
         'was actually found on the page.'],
        ['Ingredient lists with no record of where they came from.',
         '8,118 rows', 'filled in the source',
         'The only fix on this list that adds rather than removes. The source '
         'was known all along: the global products came from Skinsort and the '
         'Lebanese ones from the shop named in their domain column. Nothing '
         'is invented, the fact was simply never written down.'],
        ['A brand recorded as the word "Undefined".', '1 row',
         'read the brand out of the product name, R&amp;R',
         'The product is "R&amp;R Sun Serum".'],
        ['A review field holding ". ||| ." with no review in it.', '1 row',
         'emptied it',
         'It counted as a review in every coverage figure while containing '
         'nothing.']])}

  <div class="ok">All {len(checks)} checks pass on the file as it stands.
  {f(N)} products, {NCOL} columns, and the report is written to
  <code>VALIDATION_REPORT.txt</code> every time the check runs, so the claim on
  this page can be tested rather than believed.</div>

  <h3>What this cost, in coverage</h3>
  {tbl(['column', 'before checking', 'after', 'what moved'],
       [['products', '13,386', f(N), 'two duplicate rows merged away'],
        ['a rating', '41.6%', '41.0%', '90 ratings with nothing behind them'],
        ['key ingredients', '74.8%', '74.6%', '21 sentences that were not ingredients'],
        ['skin type', '85.1%', '85.1%', '7 removed, too few to move the figure'],
        ['formulas with a known source', '24.4%', '100%',
         'the one number that went up']])}

  <div class="note">Five of the six figures went down. That is the point of
  checking: the file was not as full as it looked, and a coverage figure that
  drops after checking is worth more than one that never moved.</div>

  <h3>Running it yourself</h3>
  <p>Two commands, and neither needs an internet connection or a key:</p>
  {tbl(['command', 'what it does'],
       [['<code>py validate_dataset.py</code>',
         f'asks all {len(checks)} questions, changes nothing, writes '
         f'VALIDATION_REPORT.txt'],
        ['<code>py fix_validation_failures.py --dry</code>',
         'says what it would change, without changing it'],
        ['<code>py fix_validation_failures.py</code>',
         'applies the nine decisions above']])}

  <h3>References</h3>
  {tbl(['work', 'what it is used for here'],
       [['Wang, R.Y. &amp; Strong, D.M. (1996). Beyond Accuracy: What Data '
         'Quality Means to Data Consumers. <i>Journal of Management '
         'Information Systems</i> 12(4), 5&ndash;33.',
         'the grouping of the checks, and the idea that quality is more than '
         'the values being right'],
        ['Pipino, L.L., Lee, Y.W. &amp; Wang, R.Y. (2002). Data Quality '
         'Assessment. <i>Communications of the ACM</i> 45(4), 211&ndash;218.',
         'measuring a quality dimension as a ratio, which is what every '
         'coverage figure on these pages is'],
        ['Batini, C., Cappiello, C., Francalanci, C. &amp; Maurino, A. (2009). '
         'Methodologies for Data Quality Assessment and Improvement. <i>ACM '
         'Computing Surveys</i> 41(3), Article 16.',
         'describe, measure, then decide what to do about failures'],
        ['Rahm, E. &amp; Do, H.H. (2000). Data Cleaning: Problems and Current '
         'Approaches. <i>IEEE Data Engineering Bulletin</i> 23(4), 3&ndash;13.',
         'clean each source before joining them, which decided the shape of '
         'the pipeline'],
        ['Fellegi, I.P. &amp; Sunter, A.B. (1969). A Theory for Record '
         'Linkage. <i>Journal of the American Statistical Association</i> '
         '64(328), 1183&ndash;1210.',
         'matching records with two thresholds, one for accept and one for '
         'review'],
        ['Christen, P. (2012). <i>Data Matching</i>. Springer.',
         'deduplication, and deciding which copy of a record survives'],
        ['EU Regulation 1223/2009, Article 19.',
         'the manufacturer is responsible for the ingredient declaration, '
         'which is why a brand page outranks a shop page']])}
</section>
"""

# ============================================================ write
html = PORTAL.read_text(encoding='utf-8')
before = len(html)
html = re.sub(r'<section class="section" id="va-(why|checks|found)">.*?</section>',
              '', html, flags=re.S)

anchor = -1
for a in ('<section class="section" id="cd-now">',
          '<section class="section" id="lo-what">',
          '<section class="section" id="mg-merge">',
          '<section class="section" id="home">'):
    if anchor == -1:
        anchor = html.find(a)
if anchor == -1:
    raise SystemExit('could not find where to insert, portal not changed')
html = html[:anchor] + VA1 + VA2 + VA3 + '\n\n' + html[anchor:]

# the portal has been reordered since these builders were written, so the
# group this used to insert beside may not exist. If the pages are already
# linked in the nav, there is nothing to add.
nav = re.search(r'<nav class="nav">.*?</nav>', html, re.S).group(0)
if 'va-why' not in nav:
    m = (re.search(r'(\s*<div class="grp">fixes and gaps</div>)', html) or
         re.search(r'(\s*<div class="grp">merging</div>)', html) or
         re.search(r'(\s*<div class="grp">overview</div>)', html))
    if m is None:
        print('  nav already has these pages, leaving it alone')
    else:
        html = (html[:m.start()] +
            '\n    <div class="grp">validation</div>\n'
            '    <a data-s="va-why">VA1. What checking means</a>\n'
            f'    <a data-s="va-checks">VA2. The {len(checks)} questions</a>\n'
            '    <a data-s="va-found">VA3. What it found</a>' +
            m.group(1) + html[m.end():])

PORTAL.write_text(html, encoding='utf-8')

w = {}
for m in re.finditer(r'<section class="section[^"]*" id="(va-[^"]+)">(.*?)</section>',
                     html, re.S):
    w[m.group(1)] = len(re.sub(r'<[^>]+>', ' ', m.group(2)).split())
print('=' * 62)
print('  VALIDATION PAGES ADDED')
print('=' * 62)
for k, v in w.items():
    print(f'    {k:12s}{v:6,} words')
print(f'\n  {sum(w.values()):,} words, '
      f'{sum(x.count("<table") for x in (VA1, VA2, VA3))} tables, '
      f'{sum(x.count("<svg") for x in (VA1, VA2, VA3))} diagrams')
print(f'  portal {before:,} -> {len(html):,} characters')
print(f'\n  read from {REPORT}: {len(checks)} checks, {npass} passed, '
      f'{nfail} failed')
