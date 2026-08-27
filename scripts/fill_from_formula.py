"""
The last fill: benefits from the formula itself

Benefits have been read from what a product SAYS about itself. This reads them
from what a product IS MADE OF, which reaches a different set of rows: the
ones with a full ingredient list and no marketing text at all.

Why this is allowed
  Saying that a product containing 3% niacinamide is brightening is not a
  guess about the marketing. It is what niacinamide does, and it is the same
  reasoning the key_ingredients column already uses. The rule only fires when
  the active is in the first two thirds of the list, because an INCI list is
  ordered by how much of each thing is in the formula and a trace at the very
  end does nothing.

  A product type is also evidence. A sunscreen protects from the sun. That is
  what the word means.

What it does not do
  It does not touch a row that already has benefits, and it does not invent
  concerns. Concerns say a formula may make something worse, and the only
  honest source for that is the presence of a specific ingredient, which the
  concerns rules already check.

Usage:
    py fill_from_formula.py --dry
    py fill_from_formula.py
"""
import os
import re
import csv
import sys
import collections

csv.field_size_limit(10 ** 8)
DATA = 'COMBINED_DATASET.csv'
DRY = '--dry' in sys.argv

BENEFITS = ['Hydrating', 'Anti-Aging', 'Brightening', 'Acne Fighting',
            'Barrier Repair', 'Reduces Irritation', 'Redness Reducing',
            'Scar Healing', 'Reduces Large Pores', 'Skin Texture',
            'Dark Spots', 'Good For Oily Skin', 'Eczema', 'Sun Protection']

# an ingredient, and what it is understood to do
FROM_INGREDIENT = [
    (r'\b(sodium hyaluronate|hyaluronic acid|glycerin|glycerol|betaine|'
     r'panthenol|sodium pca|urea|trehalose|propanediol|butylene glycol|'
     r'squalane|aloe barbadensis)\b', ['Hydrating']),
    (r'\b(niacinamide|ascorbic acid|ascorbyl|arbutin|kojic acid|tranexamic|'
     r'alpha[- ]arbutin|licorice|glycyrrhiza|glutathione)\b',
     ['Brightening', 'Dark Spots']),
    (r'\b(retinol|retinal|retinyl|adapalene|bakuchiol|peptide|palmitoyl|'
     r'matrixyl|argireline|coenzyme q10|ubiquinone|collagen)\b', ['Anti-Aging']),
    (r'\b(salicylic acid|benzoyl peroxide|azelaic acid|tea tree|melaleuca|'
     r'zinc pca|sulfur|sulphur|niacinamide)\b', ['Acne Fighting']),
    (r'\b(ceramide|cholesterol|phytosphingosine|squalane|shea butter|'
     r'butyrospermum|panthenol|allantoin)\b', ['Barrier Repair']),
    (r'\b(centella|madecassoside|asiaticoside|bisabolol|chamomilla|'
     r'allantoin|oat kernel|avena sativa|colloidal oatmeal|calendula)\b',
     ['Reduces Irritation', 'Redness Reducing']),
    (r'\b(glycolic acid|lactic acid|mandelic acid|salicylic acid|'
     r'gluconolactone|lactobionic|papain|bromelain)\b',
     ['Skin Texture', 'Reduces Large Pores']),
    (r'\b(zinc oxide|titanium dioxide|avobenzone|octocrylene|homosalate|'
     r'ethylhexyl methoxycinnamate|octinoxate|tinosorb|uvinul)\b',
     ['Sun Protection']),
    (r'\b(kaolin|bentonite|charcoal|carbo activatus|clay|witch hazel)\b',
     ['Good For Oily Skin']),
    (r'\b(centella|panthenol|allantoin|madecassoside|snail secretion)\b',
     ['Scar Healing']),
]
FROM_INGREDIENT = [(re.compile(p, re.I), b) for p, b in FROM_INGREDIENT]

# the category itself says something
FROM_TYPE = {
    'Sunscreen': ['Sun Protection'],
    'Exfoliator': ['Skin Texture'],
    'General Moisturizer': ['Hydrating'],
    'Day Moisturizer': ['Hydrating'],
    'Night Moisturizer': ['Hydrating'],
    'Eye Moisturizer': ['Hydrating'],
    'Lip Moisturizer': ['Hydrating'],
}


def split_ing(s):
    return [p.strip(' .;:') for p in re.split(r'[,;]', str(s)) if p.strip(' .;:')]


def from_formula(ing):
    """Only actives in the first two thirds count. An INCI list is ordered by
    how much is in it, so a name at the very end is a trace."""
    parts = split_ing(ing)
    if len(parts) < 3:
        return []
    cut = max(3, int(len(parts) * 0.67))
    head = ', '.join(parts[:cut])
    out = []
    for pat, labels in FROM_INGREDIENT:
        if pat.search(head):
            for l in labels:
                if l not in out:
                    out.append(l)
    return out[:5]


with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


N = len(D)
before = sum(1 for r in D if g(r, 'benefits'))
print('=' * 70)
print('  BENEFITS FROM THE FORMULA')
print('=' * 70)
print(f'  {N:,} products, {before:,} already have benefits '
      f'({100*before/N:.1f}%)')

n_ing = n_type = 0
added = collections.Counter()
for r in D:
    if g(r, 'benefits'):
        continue
    got = from_formula(g(r, 'ingredients'))
    how = 'read from the ingredient list'
    if not got:
        got = FROM_TYPE.get(g(r, 'product_type'), [])
        how = 'what this kind of product does'
    if got:
        r['benefits'] = ', '.join(got)
        r['benefit_source'] = how
        for b in got:
            added[b] += 1
        if how.startswith('read from'):
            n_ing += 1
        else:
            n_type += 1

after = sum(1 for r in D if g(r, 'benefits'))
print(f'  read from the ingredient list   {n_ing:,}')
print(f'  from the kind of product        {n_type:,}')
print(f'  benefits now                    {after:,}  ({100*after/N:.1f}%)')
print()
for k, v in added.most_common():
    print(f'     {k:24s}{v:6,}')

bad = set()
for r in D:
    for x in g(r, 'benefits').split(','):
        if x.strip() and x.strip() not in BENEFITS:
            bad.add(x.strip())
print(f'\n  vocabulary: ' + ('all allowed' if not bad else f'OUTSIDE: {bad}'))

print('\n  EXAMPLES')
shown = 0
for r in D:
    if g(r, 'benefit_source') == 'read from the ingredient list' and shown < 4:
        print(f"    {g(r, 'brand')[:16]:18s}{g(r, 'name')[:36]:38s}")
        print(f"       formula starts: {g(r, 'ingredients')[:70]}")
        print(f"       wrote         : {g(r, 'benefits')}")
        shown += 1

if DRY:
    print('\n  --dry, nothing written.')
    sys.exit(0)

tmp = DATA + '.tmp'
with open(tmp, 'w', newline='', encoding='utf-8') as fh:
    w = csv.DictWriter(fh, FIELDS, extrasaction='ignore')
    w.writeheader()
    w.writerows(D)
with open(tmp, 'rb') as fh:
    raw = fh.read()
try:
    raw.decode('utf-8')
except UnicodeDecodeError as e:
    os.remove(tmp)
    sys.exit(f'  came back damaged at byte {e.start:,}, nothing written')
os.replace(tmp, DATA)
print(f'\n  written. now run:  py build_final_dataset.py')
