"""
The three columns that come out of the ingredient list

COSTS NOTHING.  No searching, no fetching. These fields are CALCULATED from the
formula that is already in the file, which is why so much effort went into
getting the ingredient lists right first: a wrong list would produce three
wrong columns here, silently.

Usage:
    py derive_from_ingredients.py
"""
import re
import sys
import pandas as pd

FILES = ['LEBANESE_RETAIL.csv', 'LEBANESE_ORIGIN.csv', 'COMBINED_DATASET.csv',
         'SKINCARE_DATASET.csv']
OVERWRITE = '--overwrite' in sys.argv

# ---------------------------------------------------------- key ingredients
# name -> what a reader would call it
ACTIVES = {
    r'niacinamide': 'Niacinamide',
    r'sodium hyaluronate|hyaluronic acid': 'Hyaluronic Acid',
    r'\bceramide': 'Ceramides',
    r'retinol|retinal|retinyl|adapalene': 'Retinoid',
    r'ascorbic acid|ascorbyl|ethyl ascorbic': 'Vitamin C',
    r'tocopherol|tocopheryl': 'Vitamin E',
    r'salicylic acid|\bbha\b': 'Salicylic Acid',
    r'glycolic acid': 'Glycolic Acid',
    r'lactic acid': 'Lactic Acid',
    r'mandelic acid': 'Mandelic Acid',
    r'azelaic acid': 'Azelaic Acid',
    r'tranexamic acid': 'Tranexamic Acid',
    r'kojic acid': 'Kojic Acid',
    r'arbutin': 'Arbutin',
    r'panthenol|provitamin b5': 'Panthenol',
    r'allantoin': 'Allantoin',
    r'centella|madecassoside|asiaticoside|cica\b': 'Centella',
    r'aloe barbadensis|aloe vera': 'Aloe Vera',
    r'butyrospermum|shea butter': 'Shea Butter',
    r'squalane|squalene': 'Squalane',
    r'peptide|palmitoyl|matrixyl|argireline': 'Peptides',
    r'caffeine': 'Caffeine',
    r'green tea|camellia sinensis': 'Green Tea',
    r'chamomilla|chamomile|bisabolol': 'Chamomile',
    r'rosa damascena|rose water|rosa centifolia': 'Rose',
    r'lavandula|lavender': 'Lavender',
    r'olea europaea|olive oil': 'Olive Oil',
    r'laurus nobilis|laurel': 'Laurel Oil',
    r'argania|argan': 'Argan Oil',
    r'simmondsia|jojoba': 'Jojoba Oil',
    r'cocos nucifera|coconut oil': 'Coconut Oil',
    r'rosa canina|rosehip': 'Rosehip Oil',
    r'zinc oxide': 'Zinc Oxide',
    r'titanium dioxide': 'Titanium Dioxide',
    r'avobenzone|octocrylene|homosalate|ethylhexyl methoxycinnamate': 'UV Filters',
    r'urea\b': 'Urea',
    r'collagen': 'Collagen',
    r'colloidal oatmeal|avena sativa': 'Oat',
    r'honey|\bmel\b': 'Honey',
    r'propolis': 'Propolis',
    r'snail secretion|snail mucin': 'Snail Mucin',
    r'charcoal|carbo activatus': 'Charcoal',
    r'kaolin|bentonite|clay': 'Clay',
    r'glycyrrhiza|licorice': 'Licorice',
    r'vitis vinifera|grape seed': 'Grape Seed',
    r'hippophae|sea buckthorn': 'Sea Buckthorn',
    r'melaleuca|tea tree': 'Tea Tree',
    r'sulfur|sulphur': 'Sulfur',
    r'benzoyl peroxide': 'Benzoyl Peroxide',
    r'hydroquinone': 'Hydroquinone',
    r'\bpdrn\b|polydeoxyribonucleotide': 'PDRN',
    r'beta[- ]glucan': 'Beta Glucan',
    r'ectoin': 'Ectoin',
    r'bakuchiol': 'Bakuchiol',
}
ACTIVES = {re.compile(k, re.I): v for k, v in ACTIVES.items()}

# ------------------------------------------------------------- free from
AVOID = {
    'Fragrance': re.compile(r'\b(parfum|fragrance|aroma)\b', re.I),
    'Parabens': re.compile(r'\w*paraben\b', re.I),
    'Alcohol': re.compile(r'\b(alcohol denat|ethanol|sd alcohol|isopropyl alcohol)\b', re.I),
    'Essential Oils': re.compile(
        r'\b(lavandula|citrus|mentha|eucalyptus|rosmarinus|melaleuca|'
        r'cymbopogon|pelargonium)\b[^,]{0,30}\b(oil|essential)\b|'
        r'\b(limonene|linalool|citronellol|geraniol|eugenol|citral)\b', re.I),
    'Silicones': re.compile(r'\w*(methicone|siloxane)\b', re.I),
    'Sulfates': re.compile(r'\b(sodium lauryl sulfate|sodium laureth sulfate|'
                           r'ammonium lauryl sulfate|\w*sulfate)\b', re.I),
    'Mineral Oil': re.compile(r'\b(paraffinum liquidum|mineral oil|petrolatum)\b', re.I),
    'Drying Alcohols': re.compile(r'\balcohol denat\b', re.I),
    'Oils': re.compile(r'\b\w+\s+(seed|nut|fruit|kernel)?\s*oil\b', re.I),
}
TRUNCATED = re.compile(r'(and \d+ (more|other)|\.\.\.|…|and more)\s*$', re.I)


def split_ing(s):
    return [p.strip(' .;:•|*-') for p in re.split(r'[,;]', str(s)) if p.strip(' .;:•|*-')]


def key_ingredients(ing):
    parts = split_ing(ing)
    if not parts:
        return ''
    # INCI is ordered by concentration, so weight the earlier ones
    cutoff = max(4, int(len(parts) * 0.7))
    out = []
    for pat, label in ACTIVES.items():
        for pos, p in enumerate(parts):
            if pat.search(p):
                if label not in out and (pos < cutoff or len(out) < 3):
                    out.append(label)
                break
    return ', '.join(out[:8])


def looks_complete(ing):
    """free_from is a claim about an absence, so the list has to be whole."""
    parts = split_ing(ing)
    if len(parts) < 8:
        return False
    if TRUNCATED.search(str(ing)):
        return False
    last = parts[-1]
    if len(last) < 3 or not re.search(r'[a-zA-Z]', last):
        return False
    return True


def free_from(ing):
    if not looks_complete(ing):
        return ''
    out = [label for label, pat in AVOID.items() if not pat.search(str(ing))]
    # "Oils" and "Drying Alcohols" are noisy on their own, keep them last
    order = ['Fragrance', 'Parabens', 'Alcohol', 'Essential Oils', 'Silicones',
             'Sulfates', 'Mineral Oil']
    return ', '.join([x for x in order if x in out])


for path in FILES:
    try:
        df = pd.read_csv(path, dtype=str, low_memory=False).fillna('')
    except FileNotFoundError:
        continue
    if 'ingredients' not in df.columns:
        continue
    N = len(df)
    for c in ('key_ingredients', 'free_from', 'ingredient_count'):
        if c not in df.columns:
            df[c] = ''

    has = df['ingredients'] != ''
    b_key = int((df['key_ingredients'] != '').sum())
    b_free = int((df['free_from'] != '').sum())

    n_key = n_free = n_cnt = 0
    n_cleared_k = n_cleared_f = 0
    incomplete = 0
    for i in df.index[has]:
        ing = df.at[i, 'ingredients']
        if OVERWRITE or not df.at[i, 'ingredient_count']:
            df.at[i, 'ingredient_count'] = str(len(split_ing(ing)))
            n_cnt += 1
        # With --overwrite the cell is REPLACED, including with a blank.
        #
        # An earlier version only wrote when the new value was non-empty, so a
        # product whose ingredient list is truncated kept its old value. That
        # left rows like Bondi Sands still showing "Alcohol-free, EU-allergen-
        # free, Vegan" from the original scrape while every other row had been
        # recomputed. Mixing two vocabularies is the thing this run exists to
        # fix, so a blank is the correct outcome there.
        if OVERWRITE or not df.at[i, 'key_ingredients']:
            k = key_ingredients(ing)
            if k or OVERWRITE:
                df.at[i, 'key_ingredients'] = k
                n_key += 1 if k else 0
                n_cleared_k += 0 if k else 1
        if OVERWRITE or not df.at[i, 'free_from']:
            f = free_from(ing)
            if f or OVERWRITE:
                df.at[i, 'free_from'] = f
                n_free += 1 if f else 0
                n_cleared_f += 0 if f else 1
            if not looks_complete(ing):
                incomplete += 1

    df.to_csv(path, index=False)

    print('=' * 62)
    print(f'  {path}')
    print('=' * 62)
    print(f'  products with an ingredient list   {int(has.sum()):,}  '
          f'({100*has.mean():.1f}% of {N:,})')
    print()
    print(f'  key_ingredients   {b_key:,} -> {int((df["key_ingredients"] != "").sum()):,}'
          f'   (+{n_key:,})')
    print(f'  free_from         {b_free:,} -> {int((df["free_from"] != "").sum()):,}'
          f'   (+{n_free:,})')
    print(f'  ingredient_count  written for {n_cnt:,}')
    if OVERWRITE and (n_cleared_k or n_cleared_f):
        print(f'\n  cleared, because the formula did not support a value')
        print(f'    key_ingredients {n_cleared_k:,}')
        print(f'    free_from       {n_cleared_f:,}')
    if incomplete:
        print(f'\n  {incomplete:,} lists look truncated, so free_from is blank')
        print('  a "fragrance free" claim can only be made against a complete list')
    # show rows that were just RECOMPUTED, not whichever happen to be first
    ex = df[(df['key_ingredients'] != '') & (df['ingredients'].str.len() > 120)].head(3)
    if len(ex):
        print('\n  EXAMPLES')
        for _, r in ex.iterrows():
            print(f'    {str(r["brand"])[:18]:18s} {str(r["name"])[:34]:34s}')
            print(f'       key      : {r["key_ingredients"]}')
            print(f'       free from: {r["free_from"] or "(list not complete enough to say)"}')
    print()

print('nothing here was fetched or searched. these three columns are')
print('calculated from the ingredient lists already in the files.')
