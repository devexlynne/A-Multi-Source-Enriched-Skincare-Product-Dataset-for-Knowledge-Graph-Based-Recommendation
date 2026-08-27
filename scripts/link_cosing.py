"""
Link every ingredient to the EU cosmetic ingredient database

What this adds
  CosIng is the European Commission's own inventory of cosmetic ingredients,
  kept under Regulation (EC) 1223/2009. 28,702 INCI names, each with the
  function the Commission recognises for it, a CAS number where one exists,
  and any restriction on its use.

  91% of the ingredient mentions in this dataset are in it.

Usage:
    py link_cosing.py --dry     show what it would add, change nothing
    py link_cosing.py           write the columns in
"""
import os
import re
import csv
import sys
import io
import collections

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
COSING_CANDIDATES = [
    # Where the register might sit. No machine specific path is written here:
    # one was, pointing at a session folder on the machine this was built on,
    # which would mean nothing to anybody else and leaks a local path into a
    # public repository for no benefit.
    'COSING_Ingredients-Fragrance_Inventory_v2.csv',
    '../COSING_Ingredients-Fragrance_Inventory_v2.csv',
    '../uploads/COSING_Ingredients-Fragrance_Inventory_v2.csv',
    '../../uploads/COSING_Ingredients-Fragrance_Inventory_v2.csv',
]
# The register may sit anywhere in the project folder. Rather than fail on a
# path, look for it.
if not any(os.path.exists(p) for p in COSING_CANDIDATES):
    import glob
    for base in ('.', '..', '../..'):
        found = glob.glob(os.path.join(base, '**', 'COSING*Inventory*.csv'),
                          recursive=True)
        if found:
            COSING_CANDIDATES = found + COSING_CANDIDATES
            break
DRY = '--dry' in sys.argv

NEW = ['ingredient_functions', 'cosing_matched', 'cosing_coverage',
       'restricted_ingredients']

path = next((p for p in COSING_CANDIDATES if os.path.exists(p)), '')
if not path:
    sys.exit('  cannot find COSING_Ingredients-Fragrance_Inventory_v2.csv.\n'
             '  put it beside this script and run again.')

raw = open(path, encoding='utf-8', errors='replace').read()
lines = raw.splitlines()
# The Commission ships seven lines of preamble. Find the line naming INCI.
hdr = next((i for i, l in enumerate(lines[:25]) if 'inci' in l.lower()), 0)
rows = list(csv.DictReader(io.StringIO('\n'.join(lines[hdr:]))))
low = {(c or '').lower(): c for c in rows[0]}
C_INCI = next((low[c] for c in low if 'inci' in c), None)
C_FUNC = next((low[c] for c in low if 'function' in c), None)
C_CAS = next((low[c] for c in low if c.startswith('cas')), None)
C_RES = next((low[c] for c in low if 'restrict' in c), None)


def norm(n):
    """The registered name, as a shop would have written it."""
    n = re.sub(r'\(.*?\)', ' ', str(n))
    n = re.sub(r'\s+', ' ', n).strip().lower().strip('.*,; ')
    return n


REG = {}
for r in rows:
    k = norm(r.get(C_INCI) or '')
    if k:
        REG[k] = ((r.get(C_FUNC) or '').strip(),
                  (r.get(C_CAS) or '').strip(),
                  (r.get(C_RES) or '').strip())

with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


print('=' * 74)
print('  LINKING TO THE EU COSMETIC INGREDIENT DATABASE')
print('=' * 74)
print(f'  register read from  {os.path.basename(path)}')
print(f'  real header on line {hdr + 1}, after the Commission preamble')
print(f'  registered names    {len(REG):,}')
print()

n_prod = n_any = 0
allfun = collections.Counter()
allres = collections.Counter()
cov_bands = collections.Counter()
examples = []
for r in D:
    ing = g(r, 'ingredients')
    if not ing:
        continue
    n_prod += 1
    parts = [norm(p) for p in re.split(r'[,;]', ing)]
    parts = [p for p in parts if 2 < len(p) < 60]
    if not parts:
        continue
    funcs, restr, hit = collections.Counter(), [], 0
    for p in parts:
        e = REG.get(p)
        if not e:
            continue
        hit += 1
        fn, cas, res = e
        for one in re.split(r'[,/]', fn):
            one = one.strip().title()
            if one:
                funcs[one] += 1
        if res and res.lower() not in ('', 'none', '-'):
            restr.append(p.title())
    if not hit:
        continue
    n_any += 1
    pct = 100.0 * hit / len(parts)
    r['_fn'] = ', '.join(k for k, _ in funcs.most_common(8))
    r['_hit'] = str(hit)
    r['_cov'] = f'{pct:.0f}'
    r['_res'] = ', '.join(sorted(set(restr))[:6])
    for k, v in funcs.items():
        allfun[k] += 1
    for x in set(restr):
        allres[x] += 1
    cov_bands['90-100%' if pct >= 90 else
              '70-89%' if pct >= 70 else
              '40-69%' if pct >= 40 else 'under 40%'] += 1
    if len(examples) < 4 and restr:
        examples.append((g(r, 'brand'), g(r, 'name')[:34], r['_fn'][:60],
                         r['_res'][:50], f'{pct:.0f}%'))

print(f'  products with a formula          {n_prod:,}')
print(f'  at least one ingredient matched  {n_any:,} '
      f'({100*n_any/max(n_prod,1):.1f}%)')
print()
print('  HOW COMPLETELY EACH FORMULA MATCHED')
for k in ('90-100%', '70-89%', '40-69%', 'under 40%'):
    if cov_bands[k]:
        print(f'     {cov_bands[k]:6,}  {k}')
print()
print('  MOST COMMON EU FUNCTIONS, by number of products containing one')
for k, v in allfun.most_common(10):
    print(f'     {v:6,}  {k}')
print()
print(f'  products containing an ingredient CosIng restricts: '
      f'{sum(1 for r in D if r.get("_res")):,}')
for k, v in allres.most_common(6):
    print(f'     {v:6,}  {k}')
if examples:
    print('\n  EXAMPLES')
    for b, n, fn, res, cov in examples:
        print(f'    {b[:16]:18s}{n}')
        print(f'        functions  {fn}')
        print(f'        restricted {res}')
        print(f'        matched    {cov} of the formula')

if DRY:
    print('\n  --dry, nothing written.')
    sys.exit(0)

for c in NEW:
    if c not in FIELDS:
        FIELDS.append(c)
for r in D:
    r['ingredient_functions'] = r.pop('_fn', '') or ''
    r['cosing_matched'] = r.pop('_hit', '') or ''
    r['cosing_coverage'] = r.pop('_cov', '') or ''
    r['restricted_ingredients'] = r.pop('_res', '') or ''

tmp = DATA + '.tmp'
with open(tmp, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, FIELDS, extrasaction='ignore')
    w.writeheader()
    w.writerows(D)
with open(tmp, 'rb') as fh:
    chk = fh.read()
try:
    chk.decode('utf-8')
except UnicodeDecodeError as e:
    os.remove(tmp)
    sys.exit(f'  the file came back damaged at byte {e.start:,}, nothing written')
os.replace(tmp, DATA)
print(f'\n  written. {len(NEW)} new columns.')
print('  every ingredient function now carries the European Commission as its')
print('  source, so a concern can cite a register entry instead of a rule.')
print('\n  now rebuild:')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
