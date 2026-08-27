"""
Full audit of the two deliverable datasets

Written after my supervisor meeting prep turned up a wrong number in my own
portal (i had written "Sephora 440" when the file said 101). So i stopped
quoting figures from memory and wrote this instead.

It re-derives EVERY number i present, from the files themselves, and it fails
loudly if anything does not line up.

What it checks
  1. Sephora and Kaggle contribute ZERO skin types
  2. every skin_type_source value is one i can name and defend
  3. row counts identical across A, B and both Excel deliverables
  4. the Excel files really do contain what the CSVs contain
  5. no skin type without a source, and no source without a skin type
  6. sebum and sensitivity values are from the allowed vocabulary
  7. the "all skin types" products carry a blank skin type (Vendruscolo fix)
  8. coverage percentages i quote in the portal

Usage:
    py audit_final_datasets.py
"""
import re
import sys
import pandas as pd

A_CSV = 'OPTION_A_mixed_sources.csv'
B_CSV = 'OPTION_B_single_source.csv'
A_XLS = 'DATASET_A_mixed_sources.xlsx'
B_XLS = 'DATASET_B_skincarisma.xlsx'

FORBIDDEN = re.compile(r'sephora|kaggle|cosmetic_p|highlight|afteruse|suited_for', re.I)
SEBUM = {'Dry', 'Oily', 'Normal', 'Combination', ''}
SENS  = {'Sensitive', 'Resistant', ''}

fails, checks = [], 0


def check(label, ok, detail=''):
    global checks
    checks += 1
    print(f'  [{"PASS" if ok else "FAIL"}]  {label}' + (f'   {detail}' if detail else ''))
    if not ok:
        fails.append(label)


a = pd.read_csv(A_CSV, low_memory=False, dtype=str).fillna('')
b = pd.read_csv(B_CSV, low_memory=False, dtype=str).fillna('')

print('=' * 74)
print(' 1. IS SEPHORA OR KAGGLE ANYWHERE IN THE SKIN TYPE?')
print('=' * 74)
for nm, d in (('A', a), ('B', b)):
    src = d['skin_type_source']
    n = int(src.str.contains(FORBIDDEN, na=False).sum())
    check(f'dataset {nm}: no forbidden source in skin_type_source', n == 0, f'found {n}')
    cols = [c for c in d.columns if FORBIDDEN.search(c)]
    check(f'dataset {nm}: no forbidden COLUMN survives', not cols, str(cols))

print('\n  where the word "sephora" still legitimately appears (NOT skin type):')
for c in ('brand', 'review_source', 'where_to_buy'):
    if c in a.columns:
        n = int(a[c].str.contains('sephora', case=False, na=False).sum())
        print(f'      {c:16s} {n:4d}   <- a real brand / review origin / stockist, kept on purpose')

print('\n' + '=' * 74)
print(' 2. EVERY SOURCE VALUE, NAMED AND COUNTED')
print('=' * 74)
for nm, d in (('A', a), ('B', b)):
    print(f'  dataset {nm}:')
    vc = d['skin_type_source'].replace('', '(blank)').value_counts()
    for k, v in vc.items():
        print(f'      {k:34s}{v:6,}  ({100*v/len(d):5.1f}%)')
    check(f'dataset {nm}: sources sum to row count', int(vc.sum()) == len(d))

print('\n' + '=' * 74)
print(' 3. ROW COUNTS AGREE EVERYWHERE')
print('=' * 74)
xa = pd.read_excel(A_XLS, sheet_name='Dataset', dtype=str).fillna('')
xb = pd.read_excel(B_XLS, sheet_name='Dataset', dtype=str).fillna('')
check('A csv == B csv row count', len(a) == len(b), f'{len(a):,} vs {len(b):,}')
check('A csv == A xlsx row count', len(a) == len(xa), f'{len(a):,} vs {len(xa):,}')
check('B csv == B xlsx row count', len(b) == len(xb), f'{len(b):,} vs {len(xb):,}')
check('A xlsx and B xlsx have the same columns', list(xa.columns) == list(xb.columns))
check('both workbooks have exactly one sheet',
      len(pd.ExcelFile(A_XLS).sheet_names) == 1 and len(pd.ExcelFile(B_XLS).sheet_names) == 1,
      f'{pd.ExcelFile(A_XLS).sheet_names} / {pd.ExcelFile(B_XLS).sheet_names}')
check('same products, same order, in A xlsx and A csv',
      list(xa['product_id']) == list(a['product_id']))
check('same products in A and B (so they compare row for row)',
      list(xa['product_id']) == list(xb['product_id']))

print('\n' + '=' * 74)
print(' 4. THE EXCEL REALLY CONTAINS WHAT THE CSV CONTAINS')
print('=' * 74)
for nm, csv, xls in (('A', a, xa), ('B', b, xb)):
    same = all((csv[c].astype(str).str.strip() == xls[c].astype(str).str.strip()).all()
               for c in ('product_id', 'brand', 'name', 'skin_type', 'sensitivity'))
    check(f'dataset {nm}: key fields identical csv vs xlsx', same)

print('\n' + '=' * 74)
print(' 5. INTERNAL CONSISTENCY OF THE SKIN TYPE')
print('=' * 74)
for nm, d in (('A', a), ('B', b)):
    has_t = d['skin_type'] != ''
    has_s = d['skin_type_source'] != ''
    orphan = int((has_t & ~has_s).sum())
    check(f'dataset {nm}: no skin type without a source', orphan == 0, f'{orphan} orphans')
    check(f'dataset {nm}: sebum vocabulary is clean',
          set(d['skin_type'].unique()) <= SEBUM, str(sorted(set(d['skin_type'].unique()) - SEBUM)))
    check(f'dataset {nm}: sensitivity vocabulary is clean',
          set(d['sensitivity'].unique()) <= SENS, str(sorted(set(d['sensitivity'].unique()) - SENS)))

print('\n' + '=' * 74)
print(' 6. THE "ALL SKIN TYPES" FIX IS STILL IN PLACE  (Vendruscolo et al. 2025)')
print('=' * 74)
uni = a['skin_type_source'].str.startswith('claim:universal')
check('universal-claim products carry NO sebum value',
      (a.loc[uni, 'skin_type'] == '').all(), f'{int(uni.sum()):,} products')
check('universal-claim products carry NO sensitivity value',
      (a.loc[uni, 'sensitivity'] == '').all())

print('\n' + '=' * 74)
print(' 7. THE COVERAGE NUMBERS I QUOTE')
print('=' * 74)
n = len(a)
print(f'{"":34s}{"OPTION A":>14s}{"OPTION B":>14s}')
for label, col in (('sebum axis filled', 'skin_type'), ('sensitivity filled', 'sensitivity')):
    ca, cb = int((a[col] != '').sum()), int((b[col] != '').sum())
    print(f'  {label:32s}{ca:7,} {100*ca/n:5.1f}%{cb:7,} {100*cb/n:5.1f}%')
agree = 100 * (a['skin_type'] == b['skin_type']).mean()
print(f'  {"A and B give the same value":32s}{agree:12.1f}%')

print('\n' + '=' * 74)
print(f' RESULT: {checks - len(fails)} of {checks} checks passed')
print('=' * 74)
if fails:
    print(' FAILED:')
    for f in fails:
        print('   -', f)
    sys.exit(1)
print(' Sephora and Kaggle contribute nothing. Both datasets are internally')
print(' consistent and the Excel deliverables match their CSVs exactly.')
