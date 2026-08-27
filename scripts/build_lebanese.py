"""
The lebanese retail dataset

Steps, in order
  1. Load the raw scrape from the six Lebanese shops, untouched.
  2. Deduplicate. The same physical product is listed by several shops.
  3. Enrich from the cleaned Lebanese workbook: category, ingredients, price,
     and any reviews already matched.
  4. REMOVE everything that is not skincare, and everything outside the 22
     categories used in the global dataset.
  5. Match what is left against SKINCARE_DATASET and against Amazon.
  6. Write it with the SAME COLUMNS as SKINCARE_DATASET so the two can be
     stacked into one dataset.

-------------------------------------------------------------------------------
 WHY STEP 4 EXISTS
-------------------------------------------------------------------------------
  The scrape took each shop's ENTIRE catalogue, not just skincare. Lebanese
  online pharmacies sell everything, so the raw file contains

Usage:
    py build_lebanese.py
    py build_portal_lebanese.py
"""
import re
import json
import unicodedata
import pandas as pd
from rapidfuzz import fuzz
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

RAW = 'src_lebanese_retail.csv'
CLEAN = r'C:\Users\User\Documents\Thesis\Lebanese_Clean_Dataset_v2_filled.csv'
MAIN = 'SKINCARE_DATASET.csv'
AMZ = 'amazon_products19k.jsonl'
OUT_X = 'LEBANESE_RETAIL.xlsx'
OUT_C = 'LEBANESE_RETAIL.csv'
COMBINED = 'FULL_DATASET_WORKBOOK.xlsx'
STATS = 'lebanese_stats.json'

SCHEMA = ['product_id', 'brand', 'name', 'product_type', 'country',
          'skin_type', 'sensitivity', 'skin_type_status', 'skin_type_tier',
          'skin_type_authority', 'skin_type_source', 'skin_type_rule',
          'skin_type_quote', 'skin_type_url', 'ingredients', 'ingredient_count',
          'key_ingredients', 'free_from', 'spf', 'benefits', 'concerns',
          'rating', 'review_count', 'review_source', 'review_texts_json',
          'product_summary', 'skinsort_url']
EXTRA = ['retailers', 'n_retailers', 'price_usd', 'retailer_urls',
         'retailer_skin_types', 'retailers_agree', 'matched_to', 'match_score']

PROMO = re.compile(r'buy\s*\d*\s*get\s*\d*|bundle|free gift|with every purchase', re.I)
STOP = {'the', 'and', 'for', 'with', 'of', 'de', 'la', 'le', 'du', 'new', 'pack',
        'set', 'kit', 'skin', 'face', 'facial', 'ml', 'g', 'gr', 'oz', 'fl',
        'duo', 'in', 'to', 'plus', 'my', 'a', 'x'}
SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)
BPRE = re.compile(r'^(the|eau thermale|laboratoires?|labo|by)\s+', re.I)

# everything that is not facial or body skincare, however it is categorised
NOTSKIN = re.compile(
    r'shampoo|conditioner|\bhair\b|scalp|\bbaby\b|diaper|nappy|toothpaste|dental|'
    r'mouthwash|deodorant|anti-?perspirant|\bdeo\b|perfume|body mist|fragrance|'
    r'\bnail\b|polish|lipstick|mascara|eyeshadow|eye ?liner|foundation|concealer|'
    r'blush|highlighter|primer|make-?up(?! remover)|supplement|\btabs?\b|capsule|'
    r'tablet|syrup|formula|\bbottle\b|pacifier|soother|sterilizer|razor|shaving|'
    r'feminine|tampon|condom|thermometer|glove|sticker|shower gel|body wash|'
    r'wipes|cotton|filter|\bbrush\b|sponge|tweezer|scissors|warmer|candle|'
    r'gift card|voucher|\bteat\b|breast pump', re.I)
S = {}


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()


def bkey(s):
    t = asc(s).strip()
    for _ in range(3):
        t = BPRE.sub('', t).strip()
    return re.sub(r'[^a-z0-9]', '', t)


def toks(name, brand=''):
    s = PROMO.sub(' ', asc(name))
    for w in re.split(r'[^a-z0-9]+', asc(brand)):
        if len(w) > 2:
            s = s.replace(w, ' ')
    s = SIZE.sub(' ', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    return frozenset(w for w in s.split() if w not in STOP)   # short words KEPT


def key_of(brand, name):
    return bkey(brand) + '||' + ' '.join(sorted(toks(name, brand)))


# ===================================================== 1. load the raw scrape
raw = pd.read_csv(RAW, dtype=str, low_memory=False).fillna('')
raw = raw[raw['brand_name'] != 'ORIGINAL/enriched'].reset_index(drop=True)
S['raw_listings'] = len(raw)
S['raw_shops'] = raw['source'].value_counts().to_dict()
S['raw_brands'] = int(raw['brand_name'].map(bkey).nunique())
S['raw_with_skintype'] = int((raw['skin_type'] != '').sum())
print(f'1. raw scrape            {len(raw):,} listings, 6 shops, '
      f'{S["raw_brands"]:,} brands')

# ================================================== 2. deduplicate, two stages
raw['b'] = raw['brand_name'].map(bkey)
raw['t'] = [toks(n, b) for n, b in zip(raw['product_name'], raw['brand_name'])]
raw['grp'] = raw['b'] + '||' + raw['t'].map(lambda s: ' '.join(sorted(s)))
stage1 = int(raw['grp'].nunique())

alias = {}
for b, g in raw.groupby('b'):
    reps = g.drop_duplicates('grp')[['grp', 't']].values.tolist()
    for i in range(len(reps)):
        for j in range(i + 1, len(reps)):
            gi, ti = reps[i]
            gj, tj = reps[j]
            d = ti ^ tj
            if len(d) != 1 or len(ti) < 2 or len(tj) < 2:
                continue
            w = next(iter(d))
            other = tj if w in ti else ti
            if max([fuzz.ratio(w, o) for o in other] + [0]) >= 80:
                a, c = sorted([gi, gj])
                alias[c] = a
for _ in range(3):
    raw['grp'] = raw['grp'].map(lambda k: alias.get(k, k))
UNIQ = int(raw['grp'].nunique())
S['stage1'] = stage1
S['stage2_extra'] = stage1 - UNIQ
S['unique_products'] = UNIQ
S['collapsed'] = len(raw) - UNIQ
sz = raw.groupby('grp').size()
S['shops_per_product'] = {str(k): int(v) for k, v in
                          sz.value_counts().sort_index().head(8).items()}
S['multi_shop'] = int((sz > 1).sum())
print(f'2. deduplicated          {len(raw):,} -> {UNIQ:,} unique '
      f'({S["collapsed"]:,} duplicate listings removed)')


def joinu(s):
    return ' | '.join(sorted({str(x).strip() for x in s if str(x).strip()}))


agg = raw.groupby('grp').agg(
    brand=('brand_name', 'first'),
    name=('product_name', lambda s: max(s, key=len)),
    retailers=('source', joinu),
    n_retailers=('source', lambda s: len(set(s))),
    retailer_urls=('product_url', joinu),
    retailer_skin_types=('skin_type', joinu),
).reset_index()
agg['retailers_agree'] = [
    'single shop' if n == 1 else ('yes' if '|' not in st else 'no')
    for n, st in zip(agg['n_retailers'], agg['retailer_skin_types'])]
mm = agg[agg['n_retailers'] > 1]
S['agree'] = int((mm['retailers_agree'] == 'yes').sum())
S['disagree'] = int((mm['retailers_agree'] == 'no').sum())
print(f'   stocked by 2+ shops   {S["multi_shop"]:,}   '
      f'({S["agree"]} agree on skin type, {S["disagree"]} disagree)')

# ======================================== 3. enrich from the cleaned workbook
cl = pd.read_csv(CLEAN, dtype=str, low_memory=False).fillna('')
cl['grp'] = [key_of(b, n) for b, n in zip(cl['brand'], cl['name'])]
cl['grp'] = cl['grp'].map(lambda k: alias.get(k, k))
keep = ['grp', 'type', 'country', 'ingredients', 'ingredient_count',
        'key_ingredients', 'benefits', 'concerns', 'spf', 'free_from',
        'rating', 'review_count', 'review_source', 'review_texts',
        'product_summary', 'price_usd']
cl = cl[[c for c in keep if c in cl.columns]].drop_duplicates('grp')
agg = agg.merge(cl, on='grp', how='left').fillna('')
print(f'3. enriched              {int((agg["type"] != "").sum()):,} products '
      f'gained a category and ingredients')

for c in SCHEMA + EXTRA:
    if c not in agg.columns:
        agg[c] = ''
agg['product_type'] = agg['type']
agg['review_texts_json'] = agg['review_texts']
agg['country'] = agg['country'].replace('', 'Lebanon (retail)')
# the cleaned workbook writes the word "none" where it matched nothing.
# counting that as "has reviews" overstated coverage by 10,774 products.
agg['review_source'] = agg['review_source'].replace({'none': '', 'nan': ''})

# ============================================ 4. REMOVE everything not skincare
main = pd.read_csv(MAIN, dtype=str, low_memory=False).fillna('')
CATS = set(main['product_type'].unique()) - {''}
S['categories'] = sorted(CATS)

before = len(agg)
blob = (agg['name'] + ' ' + agg['product_type'])
in_cat = agg['product_type'].isin(CATS)
not_skin = blob.str.contains(NOTSKIN, na=False)
no_cat = agg['product_type'] == ''
keep_mask = in_cat & ~not_skin

S['removed_no_category'] = int(no_cat.sum())
S['removed_wrong_category'] = int((~in_cat & ~no_cat).sum())
S['removed_not_skincare'] = int((in_cat & not_skin).sum())
S['removed_total'] = before - int(keep_mask.sum())

dropped = agg[~keep_mask]
S['dropped_examples'] = [f'{r["brand"][:18]} {r["name"][:44]}'
                         for _, r in dropped.head(8).iterrows()]
S['dropped_by_type'] = (dropped['product_type'].replace('', '(no category)')
                        .value_counts().head(8).to_dict())

agg = agg[keep_mask].reset_index(drop=True)
KEPT = len(agg)
S['kept'] = KEPT
print(f'4. REMOVED not skincare  {before:,} -> {KEPT:,}')
print(f'      no category         {S["removed_no_category"]:,}')
print(f'      category not in the global 22  {S["removed_wrong_category"]:,}')
print(f'      body, hair, makeup, baby, etc  {S["removed_not_skincare"]:,}')

# ============================ 5. match against the finished dataset and Amazon
main['grp'] = [key_of(b, n) for b, n in zip(main['brand'], main['name'])]
midx = main.drop_duplicates('grp').set_index('grp')
INHERIT = ['skin_type', 'sensitivity', 'skin_type_status', 'skin_type_tier',
           'skin_type_authority', 'skin_type_source', 'skin_type_rule',
           'skin_type_quote', 'skin_type_url', 'ingredients', 'ingredient_count',
           'key_ingredients', 'free_from', 'spf', 'benefits', 'concerns',
           'rating', 'review_count', 'review_source', 'review_texts_json',
           'product_summary', 'skinsort_url']

hit = agg['grp'].isin(midx.index)
S['matched_exact'] = int(hit.sum())
for i in agg.index[hit]:
    src = midx.loc[agg.at[i, 'grp']]
    for c in INHERIT:
        if c in src.index and str(src[c]) and not str(agg.at[i, c]):
            agg.at[i, c] = src[c]
    agg.at[i, 'matched_to'] = 'SKINCARE_DATASET (exact)'
    agg.at[i, 'match_score'] = '100'

# a fuzzy second round. the exact key is right for deduplicating inside one
# source but too strict across two sources that name products differently.
mb = {}
for k, r_ in midx.iterrows():
    mb.setdefault(bkey(r_['brand']), []).append(
        (k, ' '.join(sorted(toks(r_['name'], r_['brand'])))))
n_fuzzy = 0
for i in agg.index[~hit]:
    cand = mb.get(bkey(agg.at[i, 'brand']), [])
    if not cand:
        continue
    mine = ' '.join(sorted(toks(agg.at[i, 'name'], agg.at[i, 'brand'])))
    best, bs = None, 0
    for k, nm in cand:
        s0 = fuzz.token_set_ratio(mine, nm)
        if s0 > bs:
            best, bs = k, s0
    if best and bs >= 90:
        src = midx.loc[best]
        for c in INHERIT:
            if c in src.index and str(src[c]) and not str(agg.at[i, c]):
                agg.at[i, c] = src[c]
        agg.at[i, 'matched_to'] = 'SKINCARE_DATASET (fuzzy)'
        agg.at[i, 'match_score'] = str(int(bs))
        n_fuzzy += 1
S['matched_fuzzy'] = n_fuzzy
S['matched_skinsort'] = S['matched_exact'] + n_fuzzy
print(f'5. matched to the global dataset  {S["matched_exact"]:,} exact '
      f'+ {n_fuzzy:,} fuzzy = {S["matched_skinsort"]:,}')

try:
    rows = []
    with open(AMZ, encoding='utf-8') as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except Exception:
                    pass
    amz = pd.DataFrame(rows).astype(str).fillna('')
    amz['grp'] = [key_of(s, t) for s, t in zip(amz['store'], amz['title'])]
    amz = amz.drop_duplicates('grp').set_index('grp')
    need = agg['review_source'].eq('') & agg['grp'].isin(amz.index)
    for i in agg.index[need]:
        a = amz.loc[agg.at[i, 'grp']]
        agg.at[i, 'rating'] = str(a.get('avg', ''))
        agg.at[i, 'review_count'] = str(a.get('n', ''))
        agg.at[i, 'review_source'] = 'amazon'
        agg.at[i, 'matched_to'] = agg.at[i, 'matched_to'] or 'Amazon 19k'
        agg.at[i, 'match_score'] = agg.at[i, 'match_score'] or '100'
    S['matched_amazon'] = int(need.sum())
    print(f'   matched to Amazon              {S["matched_amazon"]:,} more')
except Exception as e:
    S['matched_amazon'] = 0
    print(f'   amazon not matched ({e})')

# ============ 5b. the shops' own skin type claims, tiered the same way
# The shops state a skin type in two very different ways and they must not be
# treated alike:
#
#   "Dry, Sensitive"                              a DECLARED claim  -> tier 2
#   "It has ingredients that are good for dry     an INFERENCE from the
#    skin and scar healing"                       formula           -> tier 3
#
# The second is exactly the SkinCarisma style of statement my supervisors
# objected to, so it is recorded at tier 3 and never counted in the headline.
INFER = re.compile(r'it has ingredients|good for|ingredients that', re.I)
WORDS = {'dry': 'Dry', 'oily': 'Oily', 'oil': 'Oily', 'combination': 'Combination',
         'combo': 'Combination', 'normal': 'Normal', 'acne': 'Oily'}
UNIV = re.compile(r'all skin types?|every skin type', re.I)


def read_claim(txt):
    t = asc(txt)
    sens = 'Sensitive' if re.search(r'sensitiv|irritat|reactive', t) else ''
    if UNIV.search(t):
        return 'All', sens
    found = {v for k, v in WORDS.items() if re.search(r'\b' + k, t)}
    if ('Dry' in found and 'Oily' in found) or 'Combination' in found:
        return 'Combination', sens
    for lab in ('Oily', 'Dry', 'Normal'):
        if lab in found:
            return lab, sens
    return ('All' if sens else ''), sens


n_shop2 = n_shop3 = 0
for i in agg.index:
    claim = str(agg.at[i, 'retailer_skin_types'])
    if not claim or str(agg.at[i, 'skin_type']):
        continue
    st, sn = read_claim(claim)
    if not st and not sn:
        continue
    inferred = bool(INFER.search(claim))
    agg.at[i, 'skin_type'] = st or 'All'
    agg.at[i, 'sensitivity'] = sn or 'Resistant'
    agg.at[i, 'skin_type_tier'] = '3' if inferred else '2'
    agg.at[i, 'skin_type_authority'] = ('shop, inferred from ingredients'
                                        if inferred else 'Lebanese retailer')
    agg.at[i, 'skin_type_source'] = str(agg.at[i, 'retailers']).split(' | ')[0]
    agg.at[i, 'skin_type_rule'] = ('shop describes the ingredients'
                                   if inferred else 'shop states the skin type')
    agg.at[i, 'skin_type_quote'] = claim[:220]
    agg.at[i, 'skin_type_url'] = str(agg.at[i, 'retailer_urls']).split(' | ')[0]
    agg.at[i, 'skin_type_status'] = 'found'
    if inferred:
        n_shop3 += 1
    else:
        n_shop2 += 1
S['shop_declared'] = n_shop2
S['shop_inferred'] = n_shop3
print(f'5b. shop skin type claims        {n_shop2:,} declared (tier 2), '
      f'{n_shop3:,} inferred from ingredients (tier 3)')

agg['product_id'] = ['LB' + str(i + 1).zfill(5) for i in range(len(agg))]
tt = pd.to_numeric(agg['skin_type_tier'], errors='coerce')
S['tier'] = {str(t): int((tt == t).sum()) for t in (1, 2, 3, 4)}
S['skintype_strong'] = int((tt <= 2).sum())
S['with_reviews'] = int((agg['review_source'] != '').sum())
S['with_rating'] = int((agg['rating'] != '').sum())
S['with_ingredients'] = int((agg['ingredients'] != '').sum())
S['with_skintype'] = int((agg['skin_type'] != '').sum())
S['no_reviews'] = KEPT - S['with_reviews']
S['types'] = agg['product_type'].value_counts().head(22).to_dict()
S['shops_final'] = {}
for sh in S['raw_shops']:
    S['shops_final'][sh] = int(agg['retailers'].str.contains(sh, na=False).sum())
S['brands_final'] = int(agg['brand'].map(bkey).nunique())

# ================================================================ 6. write out
out = agg[SCHEMA + EXTRA]
out.to_csv(OUT_C, index=False)

W = {'product_id': 11, 'brand': 22, 'name': 46, 'product_type': 18, 'country': 16,
     'skin_type': 13, 'sensitivity': 12, 'retailers': 30, 'n_retailers': 8,
     'price_usd': 10, 'retailer_urls': 40, 'retailer_skin_types': 36,
     'retailers_agree': 14, 'matched_to': 22, 'ingredients': 55,
     'review_texts_json': 40, 'skin_type_quote': 44, 'skin_type_url': 36}


def style(ws, hi=()):
    for c in ws[1]:
        v = str(c.value)
        c.fill = PatternFill('solid', fgColor='6f9c78' if v in hi else '584A7A')
        c.font = Font(bold=True, color='FFFFFF', size=10)
        c.alignment = Alignment(vertical='center', horizontal='left')
        ws.column_dimensions[get_column_letter(c.column)].width = W.get(v, 16)
    ws.row_dimensions[1].height = 22
    ws.freeze_panes = 'D2'
    ws.auto_filter.ref = ws.dimensions


summary = pd.DataFrame([
    ['raw listings scraped from 6 shops', f'{len(raw):,}'],
    ['after removing duplicate listings', f'{UNIQ:,}'],
    ['after removing everything not skincare', f'{KEPT:,}'],
    ['', ''],
    ['duplicate listings removed', f'{S["collapsed"]:,}'],
    ['non-skincare products removed', f'{S["removed_total"]:,}'],
    ['', ''],
    ['products in the global Skinsort dataset', f'{len(main):,}'],
    ['Lebanese products present in both', f'{S["matched_skinsort"]:,}'],
    ['', ''],
    ['Lebanese products with reviews', f'{S["with_reviews"]:,}'],
    ['Lebanese products with NO reviews', f'{S["no_reviews"]:,}'],
    ['Lebanese products with ingredients', f'{S["with_ingredients"]:,}'],
    ['Lebanese products with a skin type', f'{S["with_skintype"]:,}'],
    ['brands', f'{S["brands_final"]:,}'],
], columns=['figure', 'value'])

with pd.ExcelWriter(OUT_X, engine='openpyxl') as w:
    out.to_excel(w, sheet_name='Lebanese skincare', index=False)
    style(w.sheets['Lebanese skincare'], set(EXTRA))
    raw.drop(columns=['b', 't', 'grp']).to_excel(w, sheet_name='RAW scrape', index=False)
    style(w.sheets['RAW scrape'])

with pd.ExcelWriter(COMBINED, engine='openpyxl') as w:
    summary.to_excel(w, sheet_name='0 SUMMARY', index=False)
    style(w.sheets['0 SUMMARY'])
    main.drop(columns=['grp']).to_excel(w, sheet_name='1 GLOBAL skinsort', index=False)
    style(w.sheets['1 GLOBAL skinsort'])
    out.to_excel(w, sheet_name='2 LEBANESE skincare', index=False)
    style(w.sheets['2 LEBANESE skincare'], set(EXTRA))
    dropped[['brand', 'name', 'product_type', 'retailers']].to_excel(
        w, sheet_name='3 REMOVED not skincare', index=False)
    style(w.sheets['3 REMOVED not skincare'])
    raw.drop(columns=['b', 't', 'grp']).to_excel(w, sheet_name='4 LEBANESE raw scrape', index=False)
    style(w.sheets['4 LEBANESE raw scrape'])

json.dump(S, open(STATS, 'w'), indent=1)

print(f'\n6. written  {OUT_X}   {COMBINED}   {OUT_C}')
print('=' * 64)
print(f'  raw listings             {len(raw):,}')
print(f'  minus duplicates         {UNIQ:,}')
print(f'  MINUS NON SKINCARE       {KEPT:,}   <- the real Lebanese dataset')
print(f'  brands                   {S["brands_final"]:,}')
print(f'  stocked by 2+ shops      {S["multi_shop"]:,}')
print(f'  also in the global set   {S["matched_skinsort"]:,}')
print(f'  with a skin type         {S["with_skintype"]:,}  ({100*S["with_skintype"]/KEPT:.1f}%)')
print(f'  with ingredients         {S["with_ingredients"]:,}  ({100*S["with_ingredients"]/KEPT:.1f}%)')
print(f'  with reviews             {S["with_reviews"]:,}  ({100*S["with_reviews"]/KEPT:.1f}%)')
print(f'  NO reviews               {S["no_reviews"]:,}  ({100*S["no_reviews"]/KEPT:.1f}%)')
print('=' * 64)
print('\nnow run:  py build_portal_lebanese.py')
