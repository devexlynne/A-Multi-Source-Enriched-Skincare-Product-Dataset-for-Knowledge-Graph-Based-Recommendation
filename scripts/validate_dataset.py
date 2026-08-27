"""
Checking the dataset, one question at a time

The merge runs fourteen checks and refuses to save if any of them fail. This
goes further. It asks everything a reader could reasonably ask, whether or not
the merge would have caught it, and writes down the answer either way.

It changes nothing. It only reports.

What it checks, and why those things
  The groups below follow the data quality dimensions in Wang and Strong
  (1996), which is the paper most quality frameworks still build on. They
  split quality into how correct the data is in itself, how well it fits the
  job, how clearly it is presented, and whether it can be reached and trusted.

     A. can the file be read at all
     B. is every row a row, and every product one product
     C. do the controlled columns hold only their allowed values
     D. are the numbers inside sensible limits
     E. do fields that depend on each other agree
     F. does every claim say where it came from
     G. is anything left that means "we do not know" while pretending not to

  Each check prints PASS or FAIL with a count, and every failure lists a few
  real examples so it can be looked at rather than argued about.

Usage:
    py validate_dataset.py                 check and print
    py validate_dataset.py --examples 10   show more examples per failure
"""
import os
import re
import csv
import sys
import json
import math
import statistics
import collections
import datetime

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
if '--final' in sys.argv:
    # the tidy 26-column version. Same questions, fewer columns to ask them of.
    DATA = 'SKINCARE_FINAL.csv'
REPORT = ('VALIDATION_REPORT_FINAL.txt' if '--final' in sys.argv
          else 'VALIDATION_REPORT.txt')
NEX = 3
if '--examples' in sys.argv:
    i = sys.argv.index('--examples')
    NEX = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 10

LINES = []


def say(s=''):
    print(s)
    LINES.append(s)


results = []


def check(group, name, ok, detail='', examples=()):
    results.append((group, name, bool(ok), detail, list(examples)[:NEX]))
    mark = 'PASS' if ok else 'FAIL'
    say(f'  {mark}  {name:58s}{detail}')
    if not ok:
        for e in list(examples)[:NEX]:
            say(f'          {str(e)[:110]}')


say('=' * 78)
say('  VALIDATING ' + DATA)
say('  ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M'))
say('=' * 78)

# ============================================================ A. readable
say()
say('A. CAN THE FILE BE READ AT ALL')
raw = open(DATA, 'rb').read()
enc_ok, enc_where = True, ''
try:
    raw.decode('utf-8')
except UnicodeDecodeError as e:
    enc_ok, enc_where = False, f'byte {e.start:,}'
check('A', 'the whole file is valid UTF-8', enc_ok, enc_where)

# Machine code once ended up inside this file after a crash. Control
# characters are the fingerprint of that, so they are looked for by name.
ctrl = len(re.findall(rb'[\x00-\x08\x0b\x0c\x0e-\x1f]', raw))
check('A', 'no control characters anywhere', ctrl == 0, f'{ctrl:,} found')

with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]
N = len(D)
check('A', 'every row has the same number of columns',
      all(None not in r and len(r) == len(FIELDS) for r in D),
      f'{len(FIELDS)} columns, {N:,} rows')
check('A', 'no column name is repeated',
      len(FIELDS) == len(set(FIELDS)))
say(f'        {N:,} products, {len(FIELDS)} columns, {len(raw):,} bytes')


def g(r, c):
    return str(r.get(c, '')).strip()


def filled(c):
    return sum(1 for r in D if g(r, c))


def num(r, c):
    v = g(r, c)
    if not v:
        return None
    try:
        return float(v)
    except ValueError:
        return math.nan


# ============================================================ B. rows
say()
say('B. IS EVERY ROW A ROW, AND EVERY PRODUCT ONE PRODUCT')
ids = [g(r, 'product_id') for r in D]
dup_ids = [k for k, v in collections.Counter(ids).items() if v > 1]
check('B', 'product ids are unique', not dup_ids, f'{len(dup_ids)} repeated',
      dup_ids)
bad_id = [i for i in ids if not re.fullmatch(r'(GLB|LBR|LBO)-\d{5}', i)]
check('B', 'product ids are correctly formed', not bad_id,
      f'{len(bad_id)} malformed', bad_id)

blank_key = [g(r, 'product_id') for r in D
             if not g(r, 'brand') or not g(r, 'name')]
check('B', 'every product has a brand and a name', not blank_key,
      f'{len(blank_key)} missing', blank_key)


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


pair = collections.Counter(norm(g(r, 'brand')) + '|' + norm(g(r, 'name'))
                           for r in D)
dups = [k for k, v in pair.items() if v > 1]
ex = [f"{g(r,'brand')} / {g(r,'name')}" for r in D
      if norm(g(r, 'brand')) + '|' + norm(g(r, 'name')) in set(dups)]
check('B', 'no two rows are the same brand and product name', not dups,
      f'{len(dups)} repeated pairs', ex)

trim = [g(r, 'product_id') for r in D
        if g(r, 'brand') != r.get('brand', '')
        or g(r, 'name') != r.get('name', '')]
check('B', 'no stray spaces at the ends of brand or name', not trim,
      f'{len(trim)} rows', trim)

# ============================================================ C. vocabularies
say()
say('C. DO THE CONTROLLED COLUMNS HOLD ONLY THEIR ALLOWED VALUES')
ALLOWED = {
    'source_category': {'Global (Skinsort)', 'Lebanese retail', 'Lebanese origin'},
    'skin_type': {'Dry', 'Oily', 'Combination', 'Normal', 'All'},
    'sensitivity': {'Sensitive', 'Resistant'},
    'skin_type_tier': {'1', '2', '3', '4'},
    'src_global': {'0', '1'}, 'src_lb_retail': {'0', '1'},
    'src_lb_origin': {'0', '1'}, 'source_count': {'1', '2', '3'},
    'match_method': {'exact', 'fuzzy', 'single source'},
}
SPLIT = {'concerns': {'May Trigger Acne', 'May Worsen Rosacea',
                      'May Worsen Eczema', 'May Worsen Irritation',
                      'May Worsen Oily Skin', 'May Worsen Dryness',
                      # a formula that was read and tripped no rule. This is
                      # a result, not an empty cell, so it has to be a legal
                      # value of the column rather than an exception to it.
                      'None identified in the formula'},
         'benefits': {'Hydrating', 'Anti-Aging', 'Brightening',
                      'Acne Fighting', 'Barrier Repair', 'Reduces Irritation',
                      'Redness Reducing', 'Scar Healing',
                      'Reduces Large Pores', 'Skin Texture', 'Dark Spots',
                      'Good For Oily Skin', 'Eczema', 'Sun Protection'},
         'review_source': {'skinsort', 'amazon', 'sephora', 'ounousa',
                           'lebanese_local', 'global_inherited'},
         'certifications': {'Vegan', 'Cruelty-free', 'Reef-safe',
                            'Fungal-acne-safe', 'EU-allergen-free'}}
for col, allow in ALLOWED.items():
    if col not in FIELDS:
        continue
    bad = sorted({g(r, col) for r in D if g(r, col)} - allow)
    check('C', f'{col}', not bad, f'{len(bad)} unexpected', bad)
for col, allow in SPLIT.items():
    if col not in FIELDS:
        continue
    seen = set()
    for r in D:
        seen.update(x.strip() for x in g(r, col).split(',') if x.strip())
    bad = sorted(seen - allow)
    check('C', f'{col} (each piece)', not bad, f'{len(bad)} unexpected', bad)

# ============================================================ D. numbers
say()
say('D. ARE THE NUMBERS INSIDE SENSIBLE LIMITS')
RANGE = [('rating', 0, 5), ('rating_count', 0, 10 ** 8),
         ('price_usd', 0.01, 5000),
         ('price_usd_min', 0.01, 5000), ('price_usd_max', 0.01, 5000),
         ('price_usd_market', 0.01, 5000), ('rating_market', 0, 5),
         ('review_count', 0, 10 ** 7), ('rating_market_count', 0, 10 ** 8),
         ('ingredient_count', 1, 300), ('spf', 0, 110)]
for col, lo, hi in RANGE:
    if col not in FIELDS:
        continue
    bad = []
    for r in D:
        v = num(r, col)
        if v is None:
            continue
        if v != v or not (lo <= v <= hi):
            bad.append(f"{g(r,'product_id')} {col}={g(r,col)}")
    check('D', f'{col} between {lo} and {hi}', not bad, f'{len(bad)} outside',
          bad)

# ============================================================ E. agreement
say()
say('E. DO FIELDS THAT DEPEND ON EACH OTHER AGREE')
bad = [g(r, 'product_id') for r in D
       if g(r, 'skin_type') and not g(r, 'sensitivity')]
check('E', 'sensitivity is filled wherever skin type is', not bad,
      f'{len(bad)} rows', bad)

# CHECKS ONLY RUN IF THE COLUMN IS THERE.
#
# The tidy file has 26 columns instead of 56, so a check written for
# price_usd_min has nothing to look at. Reporting that as a failure would say
# the data is wrong when the column was removed on purpose.
if 'price_usd_min' in FIELDS:
    bad = []
    for r in D:
        lo, mid, hi = (num(r, 'price_usd_min'), num(r, 'price_usd'),
                       num(r, 'price_usd_max'))
        if mid is None:
            continue
        if lo is None or hi is None or not (lo <= mid <= hi):
            bad.append(f"{g(r,'product_id')} {lo} / {mid} / {hi}")
    check('E', 'lowest price <= price <= highest price', not bad,
          f'{len(bad)} rows', bad)

bad = []
for r in D:
    ing = g(r, 'ingredients')
    cnt = num(r, 'ingredient_count')
    if not ing:
        continue
    real = len([x for x in re.split(r'[,;]', ing) if x.strip(' .;:-')])
    if cnt is None or int(cnt) != real:
        bad.append(f"{g(r,'product_id')} says {g(r,'ingredient_count')} has {real}")
check('E', 'ingredient count matches the list', not bad, f'{len(bad)} rows',
      bad)

bad = [g(r, 'product_id') for r in D
       if g(r, 'free_from') and (num(r, 'ingredient_count') or 0) < 8]
check('E', 'free from only where the formula is complete', not bad,
      f'{len(bad)} rows', bad)

bad = [g(r, 'product_id') for r in D
       if g(r, 'key_ingredients') and not g(r, 'ingredients')]
check('E', 'key ingredients only where there is a formula', not bad,
      f'{len(bad)} rows', bad)

if 'src_global' in FIELDS:
    bad = []
    for r in D:
        marks = sum(1 for c in ('src_global', 'src_lb_retail', 'src_lb_origin')
                    if g(r, c) == '1')
        if str(marks) != g(r, 'source_count'):
            bad.append(f"{g(r,'product_id')} {marks} vs {g(r,'source_count')}")
    check('E', 'source markers add up to the source count', not bad,
          f'{len(bad)} rows', bad)

    bad = []
    for r in D:
        want = ('Lebanese origin' if g(r, 'src_lb_origin') == '1'
                else 'Lebanese retail' if g(r, 'src_lb_retail') == '1'
                else 'Global (Skinsort)')
        if g(r, 'source_category') != want:
            bad.append(f"{g(r,'product_id')} says {g(r,'source_category')}")
    check('E', 'category agrees with the markers it came from', not bad,
          f'{len(bad)} rows', bad)

_rsrc = 'review_source' if 'review_source' in FIELDS else 'rating_source'
bad = [g(r, 'product_id') for r in D
       if g(r, 'review_texts_json') and not g(r, _rsrc)]
check('E', 'review text always names its source', not bad, f'{len(bad)} rows',
      bad)

bad = [g(r, 'product_id') for r in D
       if g(r, 'rating') and not g(r, _rsrc)]
check('E', 'a rating names where it came from', not bad, f'{len(bad)} rows',
      bad)

# ============================================================ F. provenance
say()
say('F. DOES EVERY CLAIM SAY WHERE IT CAME FROM')
bad = [g(r, 'product_id') for r in D
       if g(r, 'skin_type') and not g(r, 'skin_type_source')]
check('F', 'every skin type names a source', not bad, f'{len(bad)} rows', bad)
if 'skin_type_tier' in FIELDS:
    bad = [g(r, 'product_id') for r in D
           if g(r, 'skin_type') and not g(r, 'skin_type_tier')]
    check('F', 'every skin type says how strong that source is', not bad,
          f'{len(bad)} rows', bad)
if 'ingredient_source' in FIELDS:
    bad = [g(r, 'product_id') for r in D
           if g(r, 'ingredients') and not g(r, 'ingredient_source')]
    check('F', 'every formula names a source', not bad, f'{len(bad)} rows', bad)
if 'price_usd_market' in FIELDS:
    bad = [g(r, 'product_id') for r in D
           if g(r, 'price_usd_market') and not g(r, 'price_market_date')]
    check('F', 'every market price carries the day it was collected', not bad,
          f'{len(bad)} rows', bad)
    bad = [g(r, 'product_id') for r in D
           if g(r, 'price_usd_market') and not g(r, 'price_market_source')]
    check('F', 'every market price names the seller', not bad,
          f'{len(bad)} rows', bad)
else:
    bad = [g(r, 'product_id') for r in D
           if g(r, 'price_usd') and not g(r, 'price_source')]
    check('F', 'every price names who was selling at it', not bad,
          f'{len(bad)} rows', bad)
    bad = [g(r, 'product_id') for r in D
           if g(r, 'rating') and not g(r, 'rating_source')]
    check('F', 'every rating names where it came from', not bad,
          f'{len(bad)} rows', bad)
    bad = [g(r, 'product_id') for r in D
           if not g(r, 'product_url').startswith('http') and g(r, 'product_url')]
    check('F', 'every product link is a real address', not bad,
          f'{len(bad)} rows', bad)

if 'image_url' in FIELDS:
    # An image column is only useful if the pictures actually load in a
    # browser. Two things stop that, and both are silent: an http address is
    # blocked as mixed content on an https page, and a logo or placeholder
    # loads perfectly while showing the wrong thing. Neither looks like an
    # error in the file, so both are checked here.
    bad = [g(r, 'product_id') for r in D
           if g(r, 'image_url') and not g(r, 'image_url').startswith('https://')]
    check('F', 'every image address is https, so it will not be blocked',
          not bad, f'{len(bad)} rows', bad)

    JUNK = re.compile(r'(logo|placeholder|no[-_]?image|sprite|favicon|'
                      r'spinner|1x1|pixel|blank)', re.I)
    bad = [f"{g(r,'product_id')} {g(r,'image_url')[:60]}" for r in D
           if JUNK.search(g(r, 'image_url'))]
    check('F', 'no image is a logo or a placeholder', not bad,
          f'{len(bad)} rows', bad)

RESALE = re.compile(r'\b(ebay|mercari|poshmark|whatnot|depop|vinted)\b', re.I)
_pcol = 'price_market_source' if 'price_market_source' in FIELDS else 'price_source'
bad = [f"{g(r,'product_id')} {g(r,_pcol)}" for r in D
       if RESALE.search(g(r, _pcol))]
check('F', 'no price came from a secondhand marketplace', not bad,
      f'{len(bad)} rows', bad)

bad_url = [f"{g(r,'product_id')} {g(r,'skin_type_url')[:60]}" for r in D
           if g(r, 'skin_type_url') and not g(r, 'skin_type_url').startswith('http')]
check('F', 'source addresses look like addresses', not bad_url,
      f'{len(bad_url)} rows', bad_url)

# ============================================================ G. placeholders
say()
say('G. IS ANYTHING LEFT THAT MEANS "WE DO NOT KNOW"')
PH = re.compile(r'^\s*(not available|not specified|not comparable|no information|'
                r'unknown|none|n/?a|nan|null|-{1,3}|\?|undefined|missing)\s*$', re.I)
tot = 0
worst = []
for c in FIELDS:
    hits = [g(r, 'product_id') for r in D if PH.match(g(r, c))]
    if hits:
        tot += len(hits)
        worst.append(f'{c}: {len(hits)}')
check('G', 'no cell says "we do not know" in words', tot == 0,
      f'{tot:,} cells', worst)

json_bad = []
for r in D:
    v = g(r, 'review_texts_json')
    if not v:
        continue
    try:
        json.loads(v)
    except Exception:
        json_bad.append(g(r, 'product_id'))
check('G', 'stored review text is readable back', not json_bad,
      f'{len(json_bad)} rows', json_bad)

# ============================================================ coverage
say()
say('COVERAGE, FOR THE RECORD')


def anyof(*cols):
    return sum(1 for r in D if any(g(r, c) for c in cols))


for lab, cols in [('brand', ['brand']), ('name', ['name']),
                  ('category', ['product_type']), ('concerns', ['concerns']),
                  ('sensitivity', ['sensitivity']), ('skin type', ['skin_type']),
                  ('description', ['product_summary']),
                  ('a price', ['price_usd', 'price_usd_market']),
                  ('ingredients', ['ingredients']),
                  ('key ingredients', ['key_ingredients']),
                  ('free from', ['free_from']), ('benefits', ['benefits']),
                  ('a rating', ['rating', 'rating_market']),
                  ('review text', ['review_texts_json'])]:
    n = anyof(*cols)
    say(f'    {lab:18s}{n:7,}  {100*n/N:5.1f}%')

# ============================================================ verdict
fails = [r for r in results if not r[2]]
say()
say('=' * 78)
by_group = collections.Counter(r[0] for r in results)
ok_group = collections.Counter(r[0] for r in results if r[2])
for gname, label in [('A', 'the file can be read'),
                     ('B', 'rows and products'),
                     ('C', 'controlled values'),
                     ('D', 'numbers in range'),
                     ('E', 'fields agree'),
                     ('F', 'claims carry sources'),
                     ('G', 'nothing pretending to be data')]:
    say(f'  {gname}  {label:34s}{ok_group[gname]:3d} of {by_group[gname]:3d} passed')
say()
if fails:
    say(f'  {len(fails)} of {len(results)} checks FAILED:')
    for gname, name, _, detail, _ in fails:
        say(f'    {gname}  {name}  {detail}')
else:
    say(f'  ALL {len(results)} CHECKS PASSED.')
say('=' * 78)

with open(REPORT, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(LINES) + '\n')
print(f'\n  written to {REPORT}')
sys.exit(1 if fails else 0)
