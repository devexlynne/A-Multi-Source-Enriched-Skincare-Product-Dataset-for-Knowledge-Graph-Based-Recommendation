"""
Step 3 of 3. merge the rescue. a value can only get better, never worse.

The one rule
  A row is overwritten only when the rescue found a source with a LOWER tier
  number than the one already recorded. Lower means stronger:

      1  the manufacturer
      2  a shop that sells it
      3  an ingredient analysis site
      4  something else

  So a tier 1 answer replaces a tier 3 one. A tier 3 answer never replaces a
  tier 1 one. And if the rescue found nothing at all, the row is left exactly
  as it was.

  This is why the coverage figure cannot fall. No cell is ever emptied here.

What it prints
  The number that matters for your meeting is the last one: how many of the
  filled rows now come from the manufacturer or a shop. That is the figure to
  quote, because it is the one you can defend by clicking the link.

  It also prints what is LEFT on an analysis site, honestly, with the domains
  named. If skinsort or skincarisma still appear there, you will see it, and
  you can decide whether to keep those rows or blank them. That decision is
  yours, and this script does not make it for you.

Usage:
    py rescue_apply.py
    py mark_not_applicable.py
    py build_dataset.py
"""
import re
import sys
import pandas as pd

DATASET = 'SKINCARE_DATASET.csv'
# pass a different results file on the command line:
#     py rescue_apply.py serper_direct_results.csv
RESCUE = sys.argv[1] if len(sys.argv) > 1 else 'serper_rescue_results.csv'
print(f'merging {RESCUE}\n')

df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')
rs = pd.read_csv(RESCUE, dtype=str).fillna('')
rs = rs[rs['status'] == 'found']

# the rescue carries its own brand and name. drop them so the merge cannot
# overwrite the real ones. this bug cost a day the first time it happened.
rs = rs.drop(columns=[c for c in ('brand', 'name', 'status', 'pages_opened')
                      if c in rs.columns])
rs = rs.drop_duplicates('product_id', keep='first').set_index('product_id')

COLS = ['skin_type', 'sensitivity', 'skin_type_tier', 'skin_type_authority',
        'skin_type_source', 'skin_type_rule', 'skin_type_quote', 'skin_type_url']

before_tier = df['skin_type_tier'].value_counts().to_dict()
before_filled = int((df['skin_type'] != '').sum())

upgraded = 0
changed_value = 0
examples = []

for i in df.index:
    pid = df.at[i, 'product_id']
    if pid not in rs.index:
        continue
    new = rs.loc[pid]
    try:
        old_t = int(df.at[i, 'skin_type_tier'] or 9)
        new_t = int(new['skin_type_tier'] or 9)
    except ValueError:
        continue
    if new_t >= old_t:
        continue                      # never downgrade, never sideways

    old_type = df.at[i, 'skin_type']
    old_src = df.at[i, 'skin_type_source']

    for c in COLS:
        if c in new.index and str(new[c]):
            df.at[i, c] = new[c]
    # sensitivity is additive: a rescue that only names a sebum type must not
    # erase a sensitivity finding that was already there
    if not str(new.get('sensitivity', '')) and old_type:
        pass
    if str(new.get('universal_claim', '')) == '1' and not df.at[i, 'skin_type']:
        df.at[i, 'skin_type'] = 'All'

    upgraded += 1
    if df.at[i, 'skin_type'] != old_type:
        changed_value += 1
    if len(examples) < 8:
        examples.append((df.at[i, 'brand'][:20], df.at[i, 'name'][:34],
                         f'{old_type} ({old_src})', f'{df.at[i, "skin_type"]} '
                         f'({df.at[i, "skin_type_source"]})'))

df.to_csv(DATASET, index=False)

# ------------------------------------------------------------------- report
after_tier = df['skin_type_tier'].value_counts().to_dict()
filled = int((df['skin_type'] != '').sum())
got = df[df['skin_type'] != '']
t12 = int(pd.to_numeric(got['skin_type_tier'], errors='coerce').le(2).sum())

LAB = {'1': 'manufacturer', '2': 'retailer', '3': 'analysis site', '4': 'other source'}

print('=' * 70)
print('  RESCUE MERGED')
print('=' * 70)
print(f'  rows upgraded to a stronger source     {upgraded:,}')
print(f'    of those, the skin type itself changed  {changed_value:,}')
print(f'    (the rest kept the same answer, now backed by a better page)')
print()
if examples:
    print('  EXAMPLES,  before  ->  after')
    for b, n, o, w in examples:
        print(f'    {b:20s} {n:34s}')
        print(f'        {o}')
        print(f'     -> {w}')
    print()
print('  tier             before     after')
for t in ('1', '2', '3', '4'):
    print(f'    {t} {LAB[t]:16s}{before_tier.get(t, 0):8,}{after_tier.get(t, 0):10,}')
print()
print(f'  products with a skin type   {before_filled:,} -> {filled:,}   '
      f'(coverage did not fall)')
print(f'  FROM A MANUFACTURER OR A SHOP   {t12:,}   '
      f'({100*t12/max(filled,1):.1f}% of the filled rows)')
print()

weak = df[df['skin_type_tier'].isin(['3', '4']) & (df['skin_type'] != '')]
print(f'  still on an analysis site or an unknown site   {len(weak):,}')
if len(weak):
    print('    the domains, so nothing is hidden from you:')
    for d, c in weak['skin_type_source'].str.lower().str.replace(
            'www.', '', regex=False).value_counts().head(12).items():
        flag = '   <- the source your supervisors questioned' \
            if re.search(r'skinsort|skincarisma', d) else ''
        print(f'      {d:32s}{c:6,}{flag}')
    q = int((weak['skin_type_quote'] != '').sum())
    print(f'    of those, {q:,} still carry a readable quote you can show')

print('\nnow run:  py mark_not_applicable.py   then   py build_dataset.py')
