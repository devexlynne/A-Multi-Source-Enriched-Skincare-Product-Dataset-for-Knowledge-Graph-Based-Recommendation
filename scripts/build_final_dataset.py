"""
The tidy dataset: 56 columns down to 26

The working file grew a column every time something was learned. That was
right while the work was going on and wrong now, because a reader opening 56
columns cannot tell which ones matter.

This makes the version to show people. Nothing is thrown away: everything
removed from here is written to COMBINED_EVIDENCE.csv, joined by product_id,
so any claim can still be traced.

Usage:
    py build_final_dataset.py --dry     say what would happen
    py build_final_dataset.py           write SKINCARE_FINAL.csv and the evidence
"""
import os
import re
import csv
import sys
import collections

csv.field_size_limit(10 ** 8)
SRC = 'COMBINED_DATASET.csv'
OUT = 'SKINCARE_FINAL.csv'
EVID = 'COMBINED_EVIDENCE.csv'
DRY = '--dry' in sys.argv

with open(SRC, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    OLD = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]
N = len(D)


def g(r, c):
    return str(r.get(c, '')).strip()


print('=' * 74)
print('  MAKING THE TIDY VERSION')
print('=' * 74)
print(f'  {N:,} products, {len(OLD)} columns to start')

# ---------------------------------------------------------------- 1. urls
# WHICH LINK IS THE USEFUL ONE DEPENDS ON THE SOURCE.
#
# A Lebanese retail product should link to the Beirut shop selling it, not to
# a Skinsort catalogue page, because the point of that row is that it is on
# sale in Lebanon. A global product has no Lebanese shop, so Skinsort is the
# right link. A Lebanese brand links to its own site.
ORDER_BY_SOURCE = {
    'Lebanese origin': ['product_url', 'retailer_urls', 'skinsort_url',
                        'skin_type_url', 'ingredient_url'],
    'Lebanese retail': ['retailer_urls', 'product_url', 'skinsort_url',
                        'skin_type_url', 'ingredient_url'],
    'Global (Skinsort)': ['skinsort_url', 'product_url', 'skin_type_url',
                          'ingredient_url', 'retailer_urls'],
}
url_from = collections.Counter()
for r in D:
    best = ''
    for c in ORDER_BY_SOURCE.get(g(r, 'source_category'),
                                 ['product_url', 'skinsort_url',
                                  'skin_type_url', 'ingredient_url']):
        v = g(r, c)
        # the shops store several addresses in one cell, take the first
        if c == 'retailer_urls':
            v = v.split(',')[0].split('|')[0].strip()
        if v.startswith('http'):
            best = v
            url_from[c] += 1
            break
    r['_url'] = best
have_url = sum(1 for r in D if r['_url'])
print(f'\n  1. ONE PRODUCT LINK')
print(f'     product_url was {sum(1 for r in D if g(r, "product_url")):,} '
      f'({100*sum(1 for r in D if g(r, "product_url"))/N:.1f}%)')
print(f'     now              {have_url:,} ({100*have_url/N:.1f}%)')
for c, n in url_from.most_common():
    print(f'        {n:6,} from {c}')

# ---------------------------------------------------------------- 2. price
price_kind = collections.Counter()
for r in D:
    shop, market = g(r, 'price_usd'), g(r, 'price_usd_market')
    if shop:
        r['_price'] = shop
        r['_price_src'] = (g(r, 'retailers').split(',')[0].strip()
                           or g(r, 'domain') or 'a Lebanese shop')
        price_kind['a shop in Lebanon'] += 1
    elif market:
        r['_price'] = market
        r['_price_src'] = g(r, 'price_market_source')
        price_kind['the open market'] += 1
    else:
        r['_price'] = r['_price_src'] = ''
have_price = sum(1 for r in D if r['_price'])
print(f'\n  2. ONE PRICE')
print(f'     seven columns became three')
print(f'     price_usd read {sum(1 for r in D if g(r, "price_usd")):,} '
      f'({100*sum(1 for r in D if g(r, "price_usd"))/N:.1f}%), now '
      f'{have_price:,} ({100*have_price/N:.1f}%)')
for k, n in price_kind.most_common():
    print(f'        {n:6,} from {k}')

# --------------------------------------------------------------- 3. rating
rate_kind = collections.Counter()
for r in D:
    own, mkt = g(r, 'rating'), g(r, 'rating_market')
    if own:
        r['_rating'] = own
        r['_rating_n'] = g(r, 'review_count')
        r['_rating_src'] = g(r, 'review_source')
        rate_kind['a review site'] += 1
    elif mkt:
        r['_rating'] = mkt
        r['_rating_n'] = g(r, 'rating_market_count')
        r['_rating_src'] = g(r, 'price_market_source') or 'the open market'
        rate_kind['the open market'] += 1
    else:
        r['_rating'] = r['_rating_n'] = r['_rating_src'] = ''
    # 511 products carry review TEXT with no star rating. The source still has
    # to be recorded, or the text sits in the file with nothing saying where it
    # was written. Found by the validation, which asks exactly this.
    if not r['_rating_src'] and g(r, 'review_texts_json'):
        r['_rating_src'] = g(r, 'review_source') or 'a review site'
have_rate = sum(1 for r in D if r['_rating'])
print(f'\n  3. ONE RATING')
print(f'     five columns became three, review text kept separately')
print(f'     rating read {sum(1 for r in D if g(r, "rating")):,} '
      f'({100*sum(1 for r in D if g(r, "rating"))/N:.1f}%), now '
      f'{have_rate:,} ({100*have_rate/N:.1f}%)')
for k, n in rate_kind.most_common():
    print(f'        {n:6,} from {k}')

# ------------------------------------------------- 3b. shops in Lebanon
# sold_by held a list of shop names, and in 5,952 of 5,964 rows its first
# entry was the same string as price_source. A column that repeats another
# column is noise. What it actually knew that price_source did not is HOW MANY
# Lebanese shops carry the product, so that is what is kept: one small number
# instead of a long piece of text.
# the count is in n_retailers. The retailers column holds one name, so
# counting commas in it returns 1 for every row, which is not a fact about
# anything.
for r in D:
    n_shops = g(r, 'n_retailers')
    if n_shops.isdigit():
        r['_shops'] = n_shops
    elif g(r, 'retailers'):
        r['_shops'] = '1'
    elif g(r, 'source_category') == 'Global (Skinsort)':
        r['_shops'] = '0'
    else:
        r['_shops'] = ''
print('\n  3b. SOLD_BY BECOMES A COUNT')
print(f'     sold_by repeated price_source in 5,952 of 5,964 rows')
print(f'     replaced by shops_in_lebanon, 0 to 6')
sc = collections.Counter(r['_shops'] for r in D if r['_shops'])
for k in sorted(sc, key=lambda x: -int(x or 0))[:7]:
    print(f'        {k} shops  {sc[k]:6,}')

# -------------------------------------------------------------- 4. concerns
# The real vocabulary is a warning: this formula may make something worse.
# The rest leaked in from a scrape that read the benefits panel.
CONCERNS = ['May Trigger Acne', 'May Worsen Rosacea', 'May Worsen Eczema',
            'May Worsen Irritation', 'May Worsen Oily Skin',
            'May Worsen Dryness']
NOT_A_CONCERN = {'none reported', 'none', 'general skincare', 'n/a', '-',
                 'hydration', 'anti-aging', 'pores', 'cleansing', 'acne',
                 'sensitivity', 'soothing', 'exfoliation', 'brightening',
                 'sun protection', 'dark spots', 'firming'}

# Read off the formula, the same way the source site does it. Each rule names
# ingredients that are widely reported to cause that problem.
# The lists below are longer than the first version, because the first one
# only reached products whose formula happened to contain one of a dozen
# names. Each group is the ingredients widely reported to cause that problem:
# the EU list of 26 declarable fragrance allergens for irritation, the usual
# comedogenic esters and oils for acne, drying alcohols for dryness.
RULES = [
    (r'\b(alcohol denat|sd alcohol|alcohol 40|isopropyl alcohol|ethanol|'
     r'benzyl alcohol|denatured alcohol)\b|\balcohol\b(?!\s*(cetyl|stearyl|'
     r'cetearyl|behenyl|lauryl|myristyl))', 'May Worsen Dryness'),
    (r'\b(parfum|fragrance|aroma)\b|\b(limonene|linalool|citronellol|'
     r'geraniol|eugenol|citral|coumarin|benzyl benzoate|benzyl salicylate|'
     r'benzyl cinnamate|cinnamal|cinnamyl alcohol|farnesol|hexyl cinnamal|'
     r'isoeugenol|amyl cinnamal|anise alcohol|butylphenyl methylpropional|'
     r'hydroxycitronellal|methyl 2-octynoate|alpha-isomethyl ionone|'
     r'evernia prunastri|evernia furfuracea)\b', 'May Worsen Irritation'),
    (r'\b(limonene|linalool|citral|eugenol|cinnamal|geraniol)\b|'
     r'\b(menthol|camphor|peppermint|mentha piperita|mentha arvensis|'
     r'eucalyptus|cinnamomum|witch hazel|hamamelis|sodium lauryl sulfate)\b|'
     r'\b(alcohol denat|sd alcohol)\b', 'May Worsen Rosacea'),
    (r'\b(sodium lauryl sulfate|ammonium lauryl sulfate|sodium laureth '
     r'sulfate)\b|\b(parfum|fragrance|aroma)\b|\b(methylisothiazolinone|'
     r'methylchloroisothiazolinone|formaldehyde|dmdm hydantoin|imidazolidinyl '
     r'urea|diazolidinyl urea|quaternium-15)\b|\b(limonene|linalool|'
     r'geraniol|citral)\b|\b(propylene glycol)\b', 'May Worsen Eczema'),
    (r'\b(coconut oil|cocos nucifera oil|isopropyl myristate|isopropyl '
     r'palmitate|isopropyl isostearate|myristyl myristate|lauric acid|'
     r'wheat germ|triticum vulgare|algae extract|laminaria|ethylhexyl '
     r'palmitate|octyl palmitate|cocoa butter|theobroma cacao|wheat germ oil|'
     r'sodium lauryl sulfate|red algae|carrageenan|oleth-3|laureth-4|'
     r'lauric|myristyl lactate|butyl stearate|decyl oleate|isocetyl '
     r'stearate|isostearyl neopentanoate|coconut butter|palm oil)\b',
     'May Trigger Acne'),
    (r'\b(coconut oil|cocos nucifera oil|petrolatum|paraffinum liquidum|'
     r'mineral oil|shea butter|butyrospermum parkii|isopropyl myristate|'
     r'isopropyl palmitate|cocoa butter|theobroma cacao|lanolin|'
     r'castor oil|ricinus communis|olive oil|olea europaea|dimethicone|'
     r'beeswax|cera alba|myristyl myristate)\b', 'May Worsen Oily Skin'),
]
RULES = [(re.compile(p, re.I), c) for p, c in RULES]

n_ph = n_fold = n_derived = n_clear = 0
for r in D:
    kept = []
    for piece in g(r, 'concerns').split(','):
        p = piece.strip()
        if not p:
            continue
        if p.lower() in NOT_A_CONCERN:
            if p.lower() in ('none reported', 'none'):
                n_ph += 1
            else:
                n_fold += 1
            continue
        if p in CONCERNS and p not in kept:
            kept.append(p)
    if not kept and g(r, 'ingredients'):
        ing = g(r, 'ingredients')
        for pat, lab in RULES:
            if pat.search(ing) and lab not in kept:
                kept.append(lab)
        if kept:
            n_derived += 1
    # A product whose full formula was read and which tripped none of the six
    # rules has NOT got a missing value. It has an answer, and the answer is
    # none. Leaving the cell blank would file that result alongside the
    # products we never managed to read at all, which are a different thing
    # entirely. Saying so in words keeps the two apart in the column itself.
    if not kept and g(r, 'ingredients'):
        r['_concerns'] = 'None identified in the formula'
        n_clear += 1
    else:
        r['_concerns'] = ', '.join(kept)
have_con = sum(1 for r in D if r['_concerns'])
print(f'\n  4. CONCERNS, CLEANED THEN FILLED')
print(f'     "None reported" removed from     {n_ph:,} rows')
print(f'     benefit words removed from       {n_fold:,} rows')
print(f'     read from the formula for        {n_derived:,} rows')
print(f'     formula read, nothing flagged    {n_clear:,} rows')
print(f'     honest coverage now              {have_con:,} '
      f'({100*have_con/N:.1f}%)')
cc = collections.Counter()
for r in D:
    for x in r['_concerns'].split(','):
        if x.strip():
            cc[x.strip()] += 1
for k, n in cc.most_common():
    print(f'        {k:24s}{n:7,}')

# ---------------------------------------------------------------- write
FINAL = [
    ('product_id', 'product_id'), ('source_category', 'source_category'),
    ('brand', 'brand'), ('name', 'name'), ('product_type', 'product_type'),
    ('country', 'country'), ('product_url', '_url'),
    ('skin_type', 'skin_type'), ('sensitivity', 'sensitivity'),
    ('skin_type_source', 'skin_type_source'),
    ('ingredients', 'ingredients'), ('ingredient_count', 'ingredient_count'),
    ('key_ingredients', 'key_ingredients'), ('free_from', 'free_from'),
    ('spf', 'spf'),
    ('benefits', 'benefits'), ('concerns', '_concerns'),
    ('price_usd', '_price'), ('price_source', '_price_src'),
    # what a shop needs on top of what a thesis needs. size_ml lets products
    # of different sizes be compared, price_lbp is the currency the customer
    # actually pays in, and price_per_ml is the value signal a recommender
    # needs so it does not steer people toward small expensive packages.
    ('size_value', 'size_value'), ('size_unit', 'size_unit'),
    ('size_ml', 'size_ml'),
    ('price_lbp', 'price_lbp'), ('price_lbp_rate', 'price_lbp_rate'),
    ('price_per_ml', 'price_per_ml'), ('price_tier', 'price_tier'),
    ('rating', '_rating'), ('rating_count', '_rating_n'),
    ('rating_source', '_rating_src'), ('review_texts_json', 'review_texts_json'),
    ('shops_in_lebanon', '_shops'),
    # A recommender a shop puts in front of a customer needs a picture. This
    # column has to be in the tidy file, not only the working one, because the
    # tidy file is what gets handed over.
    ('image_url', 'image_url'), ('image_source', 'image_source'),
    # A one line summary of the product, 91% filled. It was pulled out of the
    # tidy file when it was raw shop prose full of markup. It is not that any
    # more: no HTML, no line breaks, a median of 83 characters. It is
    # GENERATED from the formula rather than written by the brand, which is
    # why it is called a summary and not a description.
    ('product_summary', 'product_summary'),
    # A price nobody can date is a price nobody can judge, and Lebanese prices
    # move. These two say when the price was seen and who was selling at it.
    ('price_seen_date', 'price_market_date'),
    ('sold_by_shops', 'retailers'),
    # The cheapest and dearest a Lebanese shop was asking, and how many shops
    # that spread came from. Only 375 products are sold by more than one shop,
    # so this is thin, but a spread of one is honestly a spread of one and the
    # count says so.
    ('price_usd_lowest', 'price_usd_min'),
    ('price_usd_highest', 'price_usd_max'),
    # The EU register, joined on the INCI name. These say what the ingredients
    # DO according to the European Commission, rather than according to a rule
    # written here, which is what lets a concern cite a regulator.
    ('ingredient_functions', 'ingredient_functions'),
    ('cosing_matched', 'cosing_matched'),
    ('cosing_coverage', 'cosing_coverage'),
    ('restricted_ingredients', 'restricted_ingredients'),
]
EV = ['product_id', 'product_summary', 'price_market_date', 'skin_type_status', 'skin_type_tier',
      'skin_type_authority', 'skin_type_rule', 'skin_type_quote',
      'skin_type_url', 'ingredient_source', 'ingredient_url',
      'ingredients_raw', 'benefit_source', 'certifications',
      'price_usd_min', 'price_usd_max', 'price_usd_market',
      'price_market_source', 'price_market_n', 'rating_market',
      'rating_market_count', 'review_count', 'review_source', 'skinsort_url',
      'retailers', 'n_retailers', 'retailer_urls', 'retailer_skin_types',
      'retailers_agree', 'domain', 'src_global', 'src_lb_retail',
      'src_lb_origin', 'source_count', 'first_source', 'match_method',
      'match_score']
EV = [c for c in EV if c in OLD or c == 'product_id']

print(f'\n  THE TIDY FILE')
print(f'     {len(OLD)} columns  ->  {len(FINAL)}')
print(f'     {len(EV)-1} columns moved to {EVID}, joined on product_id')
print()
print(f'  {"column":22s}{"filled":>8s}{"%":>7s}')
for name, key in FINAL:
    n = sum(1 for r in D if str(r.get(key, '')).strip())
    print(f'    {name:22s}{n:8,}{100*n/N:6.1f}%')

if DRY:
    print('\n  --dry, nothing written.')
    sys.exit(0)


def save(path, cols, rows, keymap=None):
    tmp = path + '.tmp'
    with open(tmp, 'w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh)
        w.writerow(cols)
        for r in rows:
            if keymap:
                w.writerow([str(r.get(k, '')).strip() for _, k in keymap])
            else:
                w.writerow([str(r.get(c, '')).strip() for c in cols])
    with open(tmp, 'rb') as fh:
        raw = fh.read()
    try:
        raw.decode('utf-8')
    except UnicodeDecodeError as e:
        os.remove(tmp)
        sys.exit(f'  came back damaged at byte {e.start:,}, nothing written')
    os.replace(tmp, path)


save(OUT, [n for n, _ in FINAL], D, FINAL)
save(EVID, EV, D)
print(f'\n  written  {OUT}   {N:,} rows, {len(FINAL)} columns')
print(f'           {EVID}   {N:,} rows, {len(EV)} columns')
print(f'\n  next:  py validate_final.py     then     py make_workbook.py --final')
