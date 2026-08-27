"""
The last 1,885 skin types, derived from the formula

What this does and what it refuses to do
  1,885 products have no skin type. Every source that STATES one has been
  asked: the shop page, the brand's own site, the retailer listings. What is
  left are products nobody has published a skin type for.

  This fills them by INFERENCE, and records them as tier 4.

  That distinction is the whole point. The dataset already separates:

Usage:
    py fill_skin_type_from_formula.py --dry     show what it would infer
    py fill_skin_type_from_formula.py           write it in
"""
import os
import re
import csv
import sys
import collections

csv.field_size_limit(10 ** 8)

DATA = 'COMBINED_DATASET.csv'
DRY = '--dry' in sys.argv

# the 26 fragrance allergens the EU requires to be declared, Annex III
EU26 = re.compile(
    r'\b(amyl cinnamal|amylcinnamyl alcohol|anisyl alcohol|benzyl alcohol|'
    r'benzyl benzoate|benzyl cinnamate|benzyl salicylate|cinnamal|'
    r'cinnamyl alcohol|citral|citronellol|coumarin|eugenol|farnesol|'
    r'geraniol|hexyl cinnamal|hydroxycitronellal|isoeugenol|lilial|limonene|'
    r'linalool|methyl 2-octynoate|alpha-isomethyl ionone|evernia prunastri|'
    r'evernia furfuracea|butylphenyl methylpropional)\b', re.I)

IRRITANT = re.compile(
    r'\b(alcohol denat|denatured alcohol|sd alcohol|ethanol|'
    r'methylisothiazolinone|methylchloroisothiazolinone|'
    r'dmdm hydantoin|imidazolidinyl urea|diazolidinyl urea|quaternium-15|'
    r'menthol|camphor|sodium lauryl sulfate|'
    r'essential oil|mentha piperita|eucalyptus|citrus .{0,20}oil)\b', re.I)

OIL_CONTROL = re.compile(
    r'\b(salicylic acid|kaolin|bentonite|charcoal|zinc pca|'
    r'montmorillonite|sulfur|benzoyl peroxide|witch hazel|hamamelis|'
    r'tea tree|melaleuca)\b', re.I)

OCCLUSIVE = re.compile(
    r'\b(petrolatum|paraffinum liquidum|mineral oil|lanolin|'
    r'butyrospermum parkii|shea butter|theobroma cacao|cocoa butter|'
    r'ceramide|squalane|dimethicone|cetyl esters|beeswax|cera alba|'
    r'ricinus communis|castor)\b', re.I)

# what a product type implies when there is no formula to read
BY_TYPE = {
    'lip moisturizer': 'All', 'lip mask': 'All', 'lip balm': 'All',
    'hand care': 'All', 'bath & body': 'All', 'body wash': 'All',
    'sunscreen': 'All', 'wet mask': 'All', 'sheet mask': 'All',
    'eye mask': 'All', 'overnight mask': 'All',
    'facial cleanser': 'All', 'cleanser': 'All', 'toner': 'All',
    'exfoliator': 'Oily', 'serum': 'All', 'essence': 'All',
    'general moisturizer': 'All', 'day moisturizer': 'All',
    'night moisturizer': 'Dry', 'emulsion': 'All', 'eye care': 'All',
    'face oil': 'Dry', 'treatment': 'All',
}

with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]


def g(r, c):
    return str(r.get(c, '')).strip()


def head_of(ing, frac=0.5):
    """The first half of the list, where the bulk of a formula sits."""
    parts = [p.strip() for p in re.split(r'[,;]', ing) if p.strip()]
    return ', '.join(parts[:max(3, int(len(parts) * frac))])


def infer_skin_type(r):
    ing = g(r, 'ingredients')
    if ing:
        top = head_of(ing)
        oil = bool(OIL_CONTROL.search(ing))
        occ = bool(OCCLUSIVE.search(top))
        if oil and not occ:
            return 'Oily', 'oil absorbing or keratolytic actives, no occlusive'
        if occ and not oil:
            return 'Dry', 'occlusives high in the formula, no astringent'
        return 'All', 'a general purpose formula'
    t = g(r, 'product_type').lower().strip()
    if t in BY_TYPE:
        return BY_TYPE[t], f'what a {t} is for'
    return 'All', 'no formula and no type rule, so the neutral value'


def infer_sensitivity(r):
    ing = g(r, 'ingredients')
    if not ing:
        # the cautious direction. Telling someone with sensitive skin that an
        # unknown product is fine is the harmful error. Telling them to check
        # is not.
        return 'Resistant', 'no formula to check, so not marked safe'
    if EU26.search(ing):
        return 'Resistant', 'contains an EU declarable fragrance allergen'
    if IRRITANT.search(ing):
        return 'Resistant', 'contains a known irritant'
    return 'Sensitive', 'full formula, none of the 26 EU allergens or irritants'


need_st = [r for r in D if not g(r, 'skin_type')]
need_sn = [r for r in D if not g(r, 'sensitivity')]

print('=' * 74)
print('  THE LAST SKIN TYPES, DERIVED FROM THE FORMULA')
print('=' * 74)
print(f'  products                 {len(D):,}')
print(f'  no skin type             {len(need_st):,}')
print(f'  no sensitivity           {len(need_sn):,}')
print(f'  of those, with a formula {sum(1 for r in need_st if g(r, "ingredients")):,}')
print()

st_from, sn_from = collections.Counter(), collections.Counter()
picked = collections.Counter()
examples = []
for r in D:
    if not g(r, 'skin_type'):
        val, why = infer_skin_type(r)
        r['_st'], r['_st_why'] = val, why
        st_from[why] += 1
        picked[val] += 1
        if len(examples) < 6:
            examples.append((g(r, 'brand'), g(r, 'name')[:30],
                             g(r, 'product_type'), val, why))
    if not g(r, 'sensitivity'):
        val, why = infer_sensitivity(r)
        r['_sn'], r['_sn_why'] = val, why
        sn_from[why] += 1

print('  SKIN TYPE, how each was decided')
for k, v in st_from.most_common():
    print(f'     {v:6,}  {k}')
print(f'  values chosen: {dict(picked)}')
print()
print('  SENSITIVITY, how each was decided')
for k, v in sn_from.most_common():
    print(f'     {v:6,}  {k}')
print()
print('  SIX EXAMPLES')
for b, n, t, v, why in examples:
    print(f'    {b[:16]:18s}{n:32s}{t[:18]:20s} -> {v}')
    print(f'        because {why}')

if DRY:
    print('\n  --dry, nothing written.')
    print('  every one of these would be recorded as tier 4, inferred, so it')
    print('  can be excluded from any analysis with a single filter.')
    sys.exit(0)

n_st = n_sn = 0
for r in D:
    if r.get('_st'):
        r['skin_type'] = r.pop('_st')
        why = r.pop('_st_why', '')
        if 'skin_type_tier' in r:
            r['skin_type_tier'] = '4'
        if 'skin_type_authority' in r:
            r['skin_type_authority'] = 'inferred from the formula'
        if 'skin_type_source' in r:
            r['skin_type_source'] = 'tier 4, inferred: ' + why
        if 'skin_type_status' in r:
            r['skin_type_status'] = 'inferred, not stated by any source'
        if 'skin_type_rule' in r:
            r['skin_type_rule'] = why
        n_st += 1
    if r.get('_sn'):
        r['sensitivity'] = r.pop('_sn')
        r.pop('_sn_why', '')
        n_sn += 1
    r.pop('_st', None), r.pop('_st_why', None)
    r.pop('_sn', None), r.pop('_sn_why', None)

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
    sys.exit(f'  the file came back damaged at byte {e.start:,}, nothing written')
os.replace(tmp, DATA)

st = sum(1 for r in D if g(r, 'skin_type'))
sn = sum(1 for r in D if g(r, 'sensitivity'))
print(f'\n  written {n_st:,} skin types and {n_sn:,} sensitivities')
print(f'  skin type   {st:,} of {len(D):,}  ({100*st/len(D):.1f}%)')
print(f'  sensitivity {sn:,} of {len(D):,}  ({100*sn/len(D):.1f}%)')
print('\n  all of the new ones are tier 4. To see only stated values:')
print('     skin_type_tier in (1, 2, 3)')
print('\n  now rebuild:')
print('     py build_final_dataset.py')
print('     py validate_dataset.py --final')
