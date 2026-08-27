"""
One dataset from three sources

Implements MERGE_SPECIFICATION.md exactly. Nothing is fetched or searched; this
only combines and cleans what is already on disk.

Usage:
    py merge_all_sources.py
"""
import os
import re
import sys
import json
import html as htmllib
import unicodedata
import pandas as pd
from rapidfuzz import fuzz
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

SOURCES = [
    ('SKINCARE_DATASET.csv', 'GLB', 'src_global', 'global (Skinsort)'),
    ('LEBANESE_RETAIL.csv', 'LBR', 'src_lb_retail', 'Lebanese retail'),
    ('LEBANESE_ORIGIN.csv', 'LBO', 'src_lb_origin', 'Lebanese origin'),
]
OUT_C = 'COMBINED_DATASET.csv'
OUT_X = 'COMBINED_DATASET.xlsx'
VOCAB = 'VOCABULARY.json'
REPORT = 'MERGE_REPORT.txt'

CORE = ['product_id', 'source_category', 'brand', 'name', 'product_type',
        'country', 'price_usd', 'price_usd_min', 'price_usd_max',
        'skin_type', 'sensitivity', 'skin_type_status', 'skin_type_tier',
        'skin_type_authority', 'skin_type_source', 'skin_type_rule',
        'skin_type_quote', 'skin_type_url', 'ingredients', 'ingredients_raw',
        'ingredient_count', 'ingredient_source', 'ingredient_url',
        'key_ingredients', 'free_from', 'certifications', 'spf',
        'benefits', 'concerns', 'rating', 'review_count', 'review_source',
        'review_texts_json', 'product_summary', 'skinsort_url']
RETAIL_COLS = ['retailers', 'n_retailers', 'retailer_urls',
               'retailer_skin_types', 'retailers_agree', 'product_url', 'domain']

# THE THREE CATEGORIES
#
# Every product belongs to exactly one of these, and the wording is the wording
# used in the thesis. A product can physically appear in two sources, so the
# category is decided by the strongest fact known about it, in this order:
#
#   1. Lebanese origin   made by a Lebanese company or person. This is a fact
#                        about who MAKES it, so it outranks the others. A
#                        Lebanese brand stocked by a Lebanese shop is still
#                        Lebanese origin.
#   2. Lebanese retail   sold in Lebanon, but the maker is not Lebanese. A fact
#                        about where it is SOLD.
#   3. Global            in Skinsort and nowhere else in this project.
#
# The three src_ markers are kept as they are, so nothing is hidden: a global
# product also carried in Lebanon still has src_global = 1 AND src_lb_retail =
# 1, and can be found either way.
CATEGORIES = ['Global (Skinsort)', 'Lebanese retail', 'Lebanese origin']

# Lebanese pounds per US dollar. This is the rate Banque du Liban settles card
# payments at, fixed at 89,500 since December 2023 and unchanged since. A few
# Lebanese shops list in lira, so their prices are divided by this to sit in
# the same column as everyone else's. Quote the rate and the date in the
# thesis, because a price in this dataset is only meaningful alongside it.
#   https://en.wikipedia.org/wiki/Lebanese_pound
LBP_PER_USD = 89500.0
PRICE_COLS = ['price_usd', 'price_usd_min', 'price_usd_max']
MARKERS = ['src_global', 'src_lb_retail', 'src_lb_origin', 'source_count',
           'first_source', 'match_method', 'match_score']
FINAL = CORE + RETAIL_COLS + MARKERS

# ----------------------------------------------------- controlled vocabularies
SKIN_TYPES = ['Dry', 'Oily', 'Combination', 'Normal', 'All']
SENSITIVITY = ['Sensitive', 'Resistant']
TIERS = ['1', '2', '3', '4']
REVIEW_SOURCES = ['skinsort', 'amazon', 'sephora', 'ounousa', 'lebanese_local',
                  'global_inherited']
SHOPS = ['sohaticare', 'feel22', 'mazenonline', 'zeinacare', 'nexuscare', 'daouk']
CERTS = ['Vegan', 'Cruelty-free', 'Reef-safe', 'Fungal-acne-safe',
         'EU-allergen-free']

# Every string that means "we do not know" and must become a genuine blank.
#
# "0" is deliberately NOT in this list. It is a real value in several columns:
# src_global is 0 or 1, n_retailers can be 0, spf can be 0. Treating it as a
# placeholder flagged 37,635 cells on the first run, almost all of them
# perfectly good zeros.
PLACEHOLDER = re.compile(
    r'^\s*(not available|not specified|not comparable|no information|unknown|'
    r'none|n/?a|nan|null|-{1,3}|\?)\s*$', re.I)
# "0" only means "missing" in these, where a zero would be a claim
ZERO_IS_MISSING = {'rating', 'review_count', 'price_usd'}

BPRE = re.compile(r'^(the|eau thermale|laboratoires?|labo|by)\s+', re.I)
SIZE = re.compile(r'\b\d+(\.\d+)?\s*(ml|g|gr|oz|fl|l|kg|mg|pcs?)\b', re.I)
PROMO = re.compile(r'buy\s*\d*\s*get\s*\d*|bundle|free gift|with every purchase', re.I)
STOP = {'the', 'and', 'for', 'with', 'of', 'de', 'la', 'le', 'du', 'new', 'pack',
        'set', 'kit', 'skin', 'face', 'facial', 'ml', 'g', 'gr', 'oz', 'fl',
        'duo', 'in', 'to', 'plus', 'my', 'a', 'x'}
TRAIL = re.compile(r'\s*(natural\s+)?(cosmetics?|skincare|skin care|beauty|'
                   r'care products?|products?|online shop|shop|store|official)\s*$', re.I)


def asc(s):
    return unicodedata.normalize('NFKD', str(s)).encode('ascii', 'ignore').decode().lower()


def bkey(s):
    t = asc(s).strip()
    for _ in range(3):
        t = BPRE.sub('', t).strip()
    return re.sub(r'[^a-z0-9]', '', t)


def nkey(brand, name):
    """The significant words of a product name. SHORT WORDS ARE KEPT: dropping
    them merged 'Ruboril Expert M' with 'Ruboril Expert S'."""
    s = PROMO.sub(' ', asc(name))
    for w in re.split(r'[^a-z0-9]+', asc(brand)):
        if len(w) > 2:
            s = s.replace(w, ' ')
    s = SIZE.sub(' ', s)
    return ' '.join(sorted(w for w in re.sub(r'[^a-z0-9 ]', ' ', s).split()
                           if w not in STOP))


def key_of(brand, name):
    return bkey(brand) + '||' + nkey(brand, name)


def tidy_brand(b):
    t = htmllib.unescape(str(b))
    t = re.sub(r'[‘’ʼ]', "'", t)
    t = re.sub(r'[–—]', '-', t)
    t = re.sub(r'\s*[-|,]\s*(lebanon|lb|official).*$', '', t, flags=re.I)
    t = re.sub(r'\s+', ' ', t).strip(' -&')
    for _ in range(3):
        t = TRAIL.sub('', t).strip()
    return t or str(b)[:40]


def load_reviews(blob):
    """Return the reviews in a cell as a list, whatever shape they were saved in.

    Three shapes exist in the sources, because three different scrapers wrote
    them: a JSON list, a JSON object keyed by reviewer, and plain text with
    "||" between reviews. All three come back as a list here so they can be
    pooled without one shape quietly counting as a single review.
    """
    b = str(blob).strip()
    if not b:
        return []
    try:
        v = json.loads(b)
        if isinstance(v, list):
            return v
        if isinstance(v, dict):
            return list(v.values())
        return [v]
    except Exception:
        return [x.strip() for x in b.split('||') if x.strip()]


def blank_placeholders(df):
    n = 0
    for col in df.columns:
        if df[col].dtype != object:
            continue
        m = df[col].astype(str).str.match(PLACEHOLDER, na=False)
        if col in ZERO_IS_MISSING:
            m = m | df[col].astype(str).str.match(r'^\s*0(\.0+)?\s*$', na=False)
        n += int(m.sum())
        df.loc[m, col] = ''
    return n


# ---------------------------------------------------- skin type normalisation
# The original Lebanese workbook stored multi-values: "All, Dry",
# "Combination, Dry, Normal, Oily". A controlled column can hold ONE value, so
# these collapse using the same rule the rest of the project uses: dry AND oily
# together is Combination, and anything naming three or more types is All.
def one_skin_type(v):
    t = str(v).strip()
    if not t:
        return ''
    parts = {p.strip().title() for p in re.split(r'[,/&+]| and ', t) if p.strip()}
    parts.discard('Sensitive')          # that belongs on the other axis
    if not parts:
        return ''
    if len(parts) == 1:
        p = parts.pop()
        return p if p in SKIN_TYPES else ''
    if 'All' in parts or len(parts) >= 3:
        return 'All'
    if 'Combination' in parts or {'Dry', 'Oily'} <= parts:
        return 'Combination'
    for lab in ('Oily', 'Dry', 'Normal'):
        if lab in parts:
            return lab
    return 'All'


def has_sensitive(v):
    return bool(re.search(r'sensitiv', str(v), re.I))


log = []


def say(s=''):
    print(s)
    log.append(s)


say('=' * 72)
say('  MERGING THREE SOURCES INTO ONE DATASET')
say('=' * 72)

# ============================================================= 1. load + clean
frames = {}
stats = {}
for path, prefix, marker, label in SOURCES:
    if not os.path.exists(path):
        say(f'  {path} not found, skipping')
        continue
    d = pd.read_csv(path, dtype=str, low_memory=False).fillna('')
    before = len(d)
    n_ph = blank_placeholders(d)
    d['brand'] = d['brand'].map(tidy_brand)
    for c in FINAL:
        if c not in d.columns:
            d[c] = ''
    d['_k'] = [key_of(b, n) for b, n in zip(d['brand'], d['name'])]
    d['_prefix'] = prefix
    d['_marker'] = marker
    d['_label'] = label
    frames[prefix] = d
    stats[prefix] = dict(label=label, rows=before, placeholders=n_ph)
    say(f'  {label:20s} {before:6,} rows   {n_ph:,} placeholders blanked')

say()

# ============================================== 2. match products across sources
# Every distinct product gets a group id. Start from the global source so its
# ids are the stable ones, then attach the Lebanese rows to it.
groups = {}          # key -> group id
rows_by_group = {}   # group id -> list of (prefix, row)
match_note = {}
n_exact = n_fuzzy = 0

order = ['GLB', 'LBR', 'LBO']
brand_index = {}     # brand key -> [(name key, group id)]

for prefix in order:
    if prefix not in frames:
        continue
    d = frames[prefix]
    for i, r in d.iterrows():
        k = r['_k']
        b = k.split('||')[0]
        nm = k.split('||')[1]

        gid = groups.get(k)
        method = 'exact' if gid is not None else ''
        score = '100' if gid is not None else ''
        if gid is not None:
            n_exact += 1
        else:
            # fuzzy: same brand, token_set_ratio >= 90 on the name
            best, bs = None, 0
            for onm, ogid in brand_index.get(b, []):
                s = fuzz.token_set_ratio(nm, onm)
                if s > bs:
                    best, bs = ogid, s
            if best is not None and bs >= 90:
                gid = best
                method, score = 'fuzzy', str(int(bs))
                n_fuzzy += 1

        if gid is None:
            gid = len(rows_by_group)
            rows_by_group[gid] = []
            # NOT the word "none". "none" is in the placeholder vocabulary,
            # so writing it here would mean 11,521 perfectly correct cells get
            # read back later as missing data. The value is a fact about the
            # product: it appeared in one source only.
            match_note[gid] = ('single source', '')
        if method:
            match_note[gid] = (method, score)
        groups.setdefault(k, gid)
        brand_index.setdefault(b, []).append((nm, gid))
        rows_by_group[gid].append((prefix, r))

say(f'  distinct products          {len(rows_by_group):,}')
say(f'    matched exactly          {n_exact:,}')
say(f'    matched fuzzily (>=90)   {n_fuzzy:,}')
say()


# ================================================================ 3. survivorship
def merge_group(members):
    """members is [(prefix, row), ...]. Produce one row."""
    out = {c: '' for c in FINAL}
    by_prefix = {p: r for p, r in members}

    # --- skin type: LOWEST tier wins
    best_tier, best_row = 99, None
    for p, r in members:
        if not str(r['skin_type']):
            continue
        try:
            t = int(str(r['skin_type_tier']) or 9)
        except ValueError:
            t = 9
        if t < best_tier:
            best_tier, best_row = t, r
    if best_row is not None:
        for c in ('skin_type', 'sensitivity', 'skin_type_status', 'skin_type_tier',
                  'skin_type_authority', 'skin_type_source', 'skin_type_rule',
                  'skin_type_quote', 'skin_type_url'):
            out[c] = str(best_row[c])

    # --- ingredients: LONGEST list wins
    ing_row = max(members, key=lambda pr: len(str(pr[1]['ingredients'])))[1]
    for c in ('ingredients', 'ingredients_raw', 'ingredient_source', 'ingredient_url'):
        out[c] = str(ing_row[c])

    # --- reviews: MERGED, never chosen between
    #
    # An earlier version kept the LONGEST review set and threw the others away.
    # That quietly cost about 550 products their reviews: a CeraVe cleanser
    # listed on Skinsort and again in a Lebanese shop would keep whichever set
    # had more characters, so the Ounousa comments vanished behind the Skinsort
    # ones. Reviews are the one thing in this dataset that genuinely ADD UP.
    # Two shops' reviews of the same product are two pieces of evidence, not
    # two competing answers, so both are kept.
    for c in ('rating', 'review_source'):
        for p, r in members:
            if str(r[c]):
                out[c] = str(r[c])
                break
    seen, pooled, srcs = set(), [], []
    for p, r in members:
        for one in load_reviews(r['review_texts_json']):
            k = re.sub(r'\W+', '', str(one).lower())[:120]
            if k and k not in seen:
                seen.add(k)
                pooled.append(one)
        s = str(r['review_source'])
        if s and s not in srcs:
            srcs.append(s)
    if pooled:
        out['review_texts_json'] = json.dumps(pooled, ensure_ascii=False)
        out['review_source'] = ', '.join(srcs)
    # review_count is a count, so it is the SUM across sources, not a pick
    tot = 0
    for p, r in members:
        try:
            tot += int(float(str(r['review_count']) or 0))
        except ValueError:
            pass
    out['review_count'] = str(tot) if tot else ''

    # --- price: the SPREAD, not one shop's number
    #
    # The same cream can be 18 dollars in one Beirut shop and 26 in another,
    # and picking the first row silently turns a real price range into a single
    # figure nobody can check. All three are kept: the lowest, the highest, and
    # a middle value in price_usd for anyone who just wants one number.
    prices = []
    for p, r in members:
        try:
            v = float(str(r['price_usd']))
        except ValueError:
            continue
        if v >= 10000:
            # This is Lebanese pounds in a column labelled USD. Five products
            # from Lebanese-origin shops price in lira: AloeLab's vitamin C
            # serum was stored as 1,540,000, which is 17.21 dollars, not one
            # and a half million. Nothing in skincare costs 10,000 dollars, so
            # the threshold is safe.
            v = v / LBP_PER_USD
        if 0 < v < 10000:          # a 0 is not a price
            prices.append(v)
    if prices:
        prices.sort()
        mid = prices[len(prices) // 2]
        out['price_usd'] = f'{mid:.2f}'
        out['price_usd_min'] = f'{prices[0]:.2f}'
        out['price_usd_max'] = f'{prices[-1]:.2f}'

    # --- retail facts come from the Lebanese rows
    for c in RETAIL_COLS:
        for p in ('LBR', 'LBO', 'GLB'):
            if p in by_prefix and str(by_prefix[p][c]):
                out[c] = str(by_prefix[p][c])
                break

    # --- brand and name: the fullest form
    out['brand'] = max((str(r['brand']) for p, r in members), key=len)
    out['name'] = max((str(r['name']) for p, r in members), key=len)

    # --- everything else: first non-empty, global first
    for c in FINAL:
        if out[c]:
            continue
        # Price is NEVER filled here. The block above already decided it, and
        # it checked the currency while doing so. Letting the generic rule top
        # it up put "1540000" back into a dollar column, because as far as this
        # loop is concerned any non-empty string will do.
        if c in PRICE_COLS:
            continue
        for p in ('GLB', 'LBR', 'LBO'):
            if p in by_prefix and str(by_prefix[p][c]):
                out[c] = str(by_prefix[p][c])
                break

    # --- markers
    out['src_global'] = '1' if 'GLB' in by_prefix else '0'
    out['src_lb_retail'] = '1' if 'LBR' in by_prefix else '0'
    out['src_lb_origin'] = '1' if 'LBO' in by_prefix else '0'
    out['source_count'] = str(sum(int(out[m]) for m in
                                  ('src_global', 'src_lb_retail', 'src_lb_origin')))
    out['first_source'] = members[0][0]

    # --- the one category the product belongs to, strongest fact first
    if out['src_lb_origin'] == '1':
        out['source_category'] = 'Lebanese origin'
    elif out['src_lb_retail'] == '1':
        out['source_category'] = 'Lebanese retail'
    else:
        out['source_category'] = 'Global (Skinsort)'
    return out


merged = []
for gid in sorted(rows_by_group):
    row = merge_group(rows_by_group[gid])
    row['match_method'], row['match_score'] = match_note[gid]
    merged.append(row)

c = pd.DataFrame(merged)[FINAL]
say(f'  merged into                {len(c):,} rows')

overlap = int((pd.to_numeric(c['source_count']) > 1).sum())
say(f'    in more than one source  {overlap:,}')
say()

# ================================================================ 4. identifiers
counters = {'GLB': 0, 'LBR': 0, 'LBO': 0}
ids = []
for fs in c['first_source']:
    counters[fs] += 1
    ids.append(f'{fs}-{counters[fs]:05d}')
c['product_id'] = ids
say('  identifiers assigned')
for p, n in counters.items():
    say(f'    {p}  {n:,}')
say()

# ======================================================= 5. certifications split
CERT_RE = re.compile(r'\b(vegan|cruelty[- ]free|reef[- ]safe|fungal[- ]acne[- ]safe|'
                     r'eu[- ]allergen[- ]free)\b', re.I)


def pull_certs(v):
    found = []
    for m in CERT_RE.finditer(str(v)):
        t = m.group(1).lower().replace(' ', '-')
        t = {'vegan': 'Vegan', 'cruelty-free': 'Cruelty-free',
             'reef-safe': 'Reef-safe', 'fungal-acne-safe': 'Fungal-acne-safe',
             'eu-allergen-free': 'EU-allergen-free'}.get(t, '')
        if t and t not in found:
            found.append(t)
    return found


n_cert = 0
for i in c.index:
    got = pull_certs(c.at[i, 'free_from'])
    if got:
        c.at[i, 'certifications'] = ', '.join(got)
        n_cert += 1
    # free_from keeps only chemical claims
    kept = [x.strip() for x in str(c.at[i, 'free_from']).split(',')
            if x.strip() and not CERT_RE.search(x)]
    # drop the old "-free" vocabulary, it is replaced by the computed one
    kept = [x for x in kept if not re.search(r'-free$|-safe$', x, re.I)]
    c.at[i, 'free_from'] = ', '.join(kept)
say(f'  certifications moved to their own column   {n_cert:,} rows')

# =============================================== 6. recompute the derived fields
def split_ing(s):
    return [p.strip(' .;:•|*-') for p in re.split(r'[,;]', str(s))
            if p.strip(' .;:•|*-')]


n_cnt = 0
for i in c.index:
    ing = c.at[i, 'ingredients']
    if ing:
        c.at[i, 'ingredient_count'] = str(len(split_ing(ing)))
        n_cnt += 1
    else:
        c.at[i, 'ingredient_count'] = ''
say(f'  ingredient_count recomputed                {n_cnt:,} rows')

# --- skin type reduced to ONE controlled value
n_multi = 0
for i in c.index:
    v = c.at[i, 'skin_type']
    if not v:
        continue
    if has_sensitive(v) and not c.at[i, 'sensitivity']:
        c.at[i, 'sensitivity'] = 'Sensitive'
    nv = one_skin_type(v)
    if nv != v:
        n_multi += 1
    c.at[i, 'skin_type'] = nv
say(f'  skin_type reduced to one value             {n_multi:,} rows')

# sensitivity must exist wherever a skin type does
m = (c['skin_type'] != '') & (c['sensitivity'] == '')
c.loc[m, 'sensitivity'] = 'Resistant'
say(f'  sensitivity completed                      {int(m.sum()):,} rows')

# --- a skin type with no source cannot be defended, so it is removed.
# 56 rows came from the original Lebanese workbook, which listed a skin type
# but recorded nowhere it came from. Every other value in this project carries
# its source, and an exception would be the one a supervisor finds.
m = (c['skin_type'] != '') & (c['skin_type_source'] == '')
n_nosrc = int(m.sum())
c.loc[m, ['skin_type', 'sensitivity', 'skin_type_tier', 'skin_type_authority',
          'skin_type_rule', 'skin_type_quote', 'skin_type_url']] = ''
c.loc[m, 'skin_type_status'] = 'stated without a source, removed'
say(f'  skin types with no source removed          {n_nosrc:,} rows')

# --- free_from is a claim about an ABSENCE, so it needs a complete list
m = (c['free_from'] != '') & (
    pd.to_numeric(c['ingredient_count'], errors='coerce').fillna(0) < 8)
n_short = int(m.sum())
c.loc[m, 'free_from'] = ''
say(f'  free_from blanked, list too short          {n_short:,} rows')

# review_count from the stored texts, never 0 to mean unknown
def count_reviews(blob):
    b = str(blob).strip()
    if not b:
        return ''
    try:
        v = json.loads(b)
        if isinstance(v, (list, dict)):
            return str(len(v))
    except Exception:
        pass
    return str(max(b.count('"},{') + 1 if '"},{' in b else
                   len([x for x in b.split('||') if x.strip()]), 1))


m = (c['review_count'] == '') & (c['review_texts_json'] != '')
c.loc[m, 'review_count'] = c.loc[m, 'review_texts_json'].map(count_reviews)
say(f'  review_count from stored texts             {int(m.sum()):,} rows')
say()

# ============================================================ 7. vocabulary audit
say('  VOCABULARY AUDIT')
problems = []


def audit(col, allowed, split=False):
    vals = set()
    for v in c.loc[c[col] != '', col]:
        if split:
            vals.update(x.strip() for x in str(v).split(',') if x.strip())
        else:
            vals.add(str(v).strip())
    bad = sorted(vals - set(allowed))
    say(f'    {col:18s}{len(vals):4d} distinct'
        + (f'   OUTSIDE THE LIST: {bad[:6]}' if bad else '   all allowed'))
    if bad:
        problems.append((col, bad))
    return sorted(vals)


vocab = {}
vocab['skin_type'] = audit('skin_type', SKIN_TYPES)
vocab['sensitivity'] = audit('sensitivity', SENSITIVITY)
vocab['skin_type_tier'] = audit('skin_type_tier', TIERS)
# split=True because a product carried by two shops now names both, e.g.
# "skinsort, lebanese_local". Each piece still has to be an allowed value.
vocab['review_source'] = audit('review_source', REVIEW_SOURCES, split=True)
vocab['certifications'] = audit('certifications', CERTS, split=True)
vocab['product_type'] = sorted({v for v in c['product_type'] if v})
vocab['country'] = sorted({v for v in c['country'] if v})
vocab['key_ingredients'] = sorted({x.strip() for v in c['key_ingredients']
                                   for x in str(v).split(',') if x.strip()})
vocab['free_from'] = sorted({x.strip() for v in c['free_from']
                             for x in str(v).split(',') if x.strip()})
say(f'    product_type      {len(vocab["product_type"]):4d} distinct')
say(f'    key_ingredients   {len(vocab["key_ingredients"]):4d} distinct')
say(f'    free_from         {len(vocab["free_from"]):4d} distinct')
say()

# ==================================================================== 8. checks
say('  THE FOURTEEN CHECKS')
fails = []


def check(n, desc, ok, detail=''):
    say(f'    {n:2d}. {desc:52s} {"PASS" if ok else "FAIL"}'
        + (f'  {detail}' if not ok and detail else ''))
    if not ok:
        fails.append((n, desc, detail))


ids_ok = c['product_id'].str.match(r'^(GLB|LBR|LBO)-\d{5}$').all()
check(1, 'ids unique and correctly formed',
      ids_ok and c['product_id'].is_unique)

c['_k2'] = [key_of(b, n) for b, n in zip(c['brand'], c['name'])]
dupes = int(c['_k2'].duplicated().sum())
check(2, 'no duplicate brand+name survives', dupes == 0, f'{dupes} duplicates')

check(3, 'controlled columns hold only allowed values', not problems,
      f'{len(problems)} columns')

ph = 0
for col in c.columns:
    ph += int(c[col].astype(str).str.match(PLACEHOLDER, na=False).sum())
check(4, 'no placeholder string survives', ph == 0, f'{ph} cells')

miss_sens = int(((c['skin_type'] != '') & (c['sensitivity'] == '')).sum())
check(5, 'sensitivity filled wherever skin_type is', miss_sens == 0,
      f'{miss_sens} rows')

no_src = int(((c['skin_type'] != '') & (c['skin_type_source'] == '')).sum())
check(6, 'every skin type has a source', no_src == 0, f'{no_src} rows')

bad_cnt = 0
for i in c.index[c['ingredients'] != '']:
    if str(c.at[i, 'ingredient_count']) != str(len(split_ing(c.at[i, 'ingredients']))):
        bad_cnt += 1
check(7, 'ingredient_count matches the list', bad_cnt == 0, f'{bad_cnt} rows')

short = c[(c['free_from'] != '') &
          (pd.to_numeric(c['ingredient_count'], errors='coerce').fillna(0) < 8)]
check(8, 'free_from blank where the list is short', len(short) == 0,
      f'{len(short)} rows')

rt = pd.to_numeric(c['rating'], errors='coerce')
bad_rt = int(((rt < 0) | (rt > 5)).sum())
check(9, 'rating between 0 and 5', bad_rt == 0, f'{bad_rt} rows')

# the category must be one of the three, and must agree with the markers it
# was derived from, or the plain-language column and the numbers disagree
cat_ok = set(c['source_category']) <= set(CATEGORIES)
derived = c.apply(lambda r: 'Lebanese origin' if r['src_lb_origin'] == '1'
                  else 'Lebanese retail' if r['src_lb_retail'] == '1'
                  else 'Global (Skinsort)', axis=1)
check(13, 'category is one of three and matches the markers',
      cat_ok and bool((derived == c['source_category']).all()))

# a price has to be a positive number, and min <= middle <= max
pmin = pd.to_numeric(c['price_usd_min'], errors='coerce')
pmid = pd.to_numeric(c['price_usd'], errors='coerce')
pmax = pd.to_numeric(c['price_usd_max'], errors='coerce')
has_p = pmid.notna()
bad_p = int((has_p & ~((pmin <= pmid) & (pmid <= pmax) & (pmin > 0))).sum())
check(14, 'prices positive and min <= price <= max', bad_p == 0, f'{bad_p} rows')

sc = (pd.to_numeric(c['src_global']) + pd.to_numeric(c['src_lb_retail']) +
      pd.to_numeric(c['src_lb_origin']))
check(10, 'markers add up to source_count',
      bool((sc == pd.to_numeric(c['source_count'])).all()))

expected = sum(s['rows'] for s in stats.values())
collapsed = expected - len(c)
# The first version of this check compared len(c) + (expected - len(c)) to
# expected, which is true no matter what the run did. It is rewritten to test
# something that can actually fail: every input row must appear in exactly one
# output group, so the group memberships have to add back up to the input.
placed = sum(len(v) for v in rows_by_group.values())
check(11, 'every input row landed in exactly one output row',
      placed == expected and len(rows_by_group) == len(c),
      f'{placed} placed of {expected}, {len(rows_by_group)} groups vs {len(c)} rows')

# check 12: no product lost a review it had in any source
lost = 0
for gid, members in rows_by_group.items():
    had = any(str(r['review_source']) or str(r['rating']) or
              str(r['review_texts_json']) for p, r in members)
    if not had:
        continue
lostcheck = 0
for idx, gid in enumerate(sorted(rows_by_group)):
    members = rows_by_group[gid]
    had = any(str(r['review_source']) or str(r['rating']) or
              str(r['review_texts_json']) for p, r in members)
    now = bool(str(c.iloc[idx]['review_source']) or str(c.iloc[idx]['rating']) or
               str(c.iloc[idx]['review_texts_json']))
    if had and not now:
        lostcheck += 1
check(12, 'no product lost a review it had', lostcheck == 0, f'{lostcheck} lost')

c = c.drop(columns=['_k2'])
say()

if fails:
    say('  ' + '!' * 60)
    say(f'  {len(fails)} CHECK(S) FAILED. The file has NOT been saved.')
    for n, desc, detail in fails:
        say(f'     {n}. {desc}  {detail}')
    say('  ' + '!' * 60)
    open(REPORT, 'w', encoding='utf-8').write('\n'.join(log))
    sys.exit(1)

# ==================================================================== 9. write
# WRITTEN TO A TEMPORARY FILE, THEN RENAMED, THEN READ BACK.
#
# COMBINED_DATASET.csv was found with machine code inside it: a run of x86
# instructions sitting in the middle of an ingredient list at byte 16,322,568.
# Something crashed while writing and put a piece of memory in the file. It
# was 27MB and looked normal, and only failed when a later script tried to
# read it.
#
# Writing to a temporary name and renaming means a crash leaves the previous
# good file untouched, because renaming is atomic. Reading it back afterwards
# means the damage is caught here rather than three scripts later.
_tmp = OUT_C + '.tmp'
c.to_csv(_tmp, index=False)
with open(_tmp, 'rb') as _fh:
    _raw = _fh.read()
try:
    _raw.decode('utf-8')
except UnicodeDecodeError as _e:
    os.remove(_tmp)
    sys.exit(f'\n  THE FILE CAME BACK DAMAGED at byte {_e.start:,}. '
             f'{OUT_C} has NOT been replaced.\n'
             f'  Run this again. If it happens twice, the disk is the suspect.')
os.replace(_tmp, OUT_C)
json.dump(vocab, open(VOCAB, 'w'), indent=1, ensure_ascii=False)

W = {'product_id': 11, 'brand': 22, 'name': 44, 'product_type': 18, 'country': 15,
     'skin_type': 12, 'sensitivity': 12, 'ingredients': 50, 'key_ingredients': 30,
     'free_from': 28, 'certifications': 22, 'benefits': 30, 'concerns': 26,
     'source_category': 18, 'price_usd': 11, 'price_usd_min': 13,
     'price_usd_max': 13, 'review_texts_json': 34, 'skin_type_quote': 40, 'skin_type_url': 34,
     'retailers': 26, 'retailer_urls': 30, 'product_url': 34}
GREEN = set(RETAIL_COLS) | set(MARKERS)
PINK = {x for x in CORE if x.startswith('skin_type')} | {'sensitivity'}

# Excel refuses control characters. A handful of ingredient lists came off web
# pages carrying vertical tabs and form feeds, invisible on screen but enough
# to abort the whole workbook write on row 4,000-something. They are stripped
# here, in the copy that goes to Excel only. The CSV keeps the text as scraped.
CTRL = re.compile(r'[\x00-\x08\x0b\x0c\x0e-\x1f]')


def excel_safe(df):
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).str.replace(CTRL, ' ', regex=True)
    return df


c = excel_safe(c)

try:
    open(OUT_X, 'a').close()
except PermissionError:
    import datetime
    OUT_X = OUT_X.replace('.xlsx', datetime.datetime.now().strftime('_%H%M%S.xlsx'))
    say(f'  workbook open in Excel, writing {OUT_X}')

with pd.ExcelWriter(OUT_X, engine='openpyxl') as w:
    summary = pd.DataFrame(
        [['products in the merged dataset', f'{len(c):,}']] +
        [[f'   from {s["label"]}', f'{s["rows"]:,}'] for s in stats.values()] +
        [['distinct products after matching', f'{len(c):,}'],
         ['in more than one source', f'{overlap:,}'],
         ['matched exactly', f'{n_exact:,}'],
         ['matched fuzzily', f'{n_fuzzy:,}'],
         ['brands', f'{c["brand"].nunique():,}'],
         ['product categories', f'{c["product_type"].nunique():,}'],
         ['all fourteen checks', 'PASSED']],
        columns=['figure', 'value'])
    summary.to_excel(w, sheet_name='0 SUMMARY', index=False)
    c.to_excel(w, sheet_name='1 COMBINED', index=False)
    for prefix, _, _, label in [(p, None, None, l) for _, p, _, l in SOURCES]:
        if prefix in frames:
            excel_safe(
                frames[prefix].drop(columns=['_k', '_prefix', '_marker', '_label'])
            ).to_excel(w, sheet_name=f'{prefix} {label[:22]}', index=False)
    for sh in w.sheets.values():
        for cell in sh[1]:
            v = str(cell.value)
            col = ('6f9c78' if v in GREEN else 'b06a97' if v in PINK else '584A7A')
            cell.fill = PatternFill('solid', fgColor=col)
            cell.font = Font(bold=True, color='FFFFFF', size=10)
            cell.alignment = Alignment(vertical='center', horizontal='left')
            sh.column_dimensions[get_column_letter(cell.column)].width = W.get(v, 16)
        sh.row_dimensions[1].height = 22
        sh.freeze_panes = 'D2'
        sh.auto_filter.ref = sh.dimensions

# =================================================================== 10. report
N = len(c)
say('=' * 72)
say('  RESULT')
say('=' * 72)
say(f'  products                   {N:,}')
say(f'  brands                     {c["brand"].nunique():,}')
say(f'  categories                 {c["product_type"].nunique():,}')
say()
say('  THE THREE CATEGORIES')
for k in CATEGORIES:
    v = int((c['source_category'] == k).sum())
    say(f'    {k:24s}{v:6,}  ({100*v/N:5.1f}%)')
say()
say('  products carried by more than one source')
both = int((pd.to_numeric(c['source_count']) > 1).sum())
say(f'    counted once, in the category above     {both:,}')
say(f'    global products also sold in Lebanon    '
    f'{int(((c["src_global"] == "1") & (c["src_lb_retail"] == "1")).sum()):,}')
say(f'    Lebanese brands in a Lebanese shop      '
    f'{int(((c["src_lb_origin"] == "1") & (c["src_lb_retail"] == "1")).sum()):,}')
say()
say('  PRICE')
pr = pd.to_numeric(c['price_usd'], errors='coerce').dropna()
say(f'    products with a price                  {len(pr):,}  ({100*len(pr)/N:5.1f}%)')
say(f'    cheapest                               ${pr.min():,.2f}')
say(f'    median                                 ${pr.median():,.2f}')
say(f'    dearest                                ${pr.max():,.2f}')
# notna() on both sides matters: a blank is NaN, and NaN != NaN is True, so
# without it every product with no price at all counted as a price difference
lo = pd.to_numeric(c['price_usd_min'], errors='coerce')
hi = pd.to_numeric(c['price_usd_max'], errors='coerce')
spread = int((lo.notna() & hi.notna() & (lo != hi)).sum())
say(f'    sold at different prices in two shops  {spread:,}')
say('    Skinsort does not publish prices, so a global-only product has none.')
say()
say('  COVERAGE')
for col in ['brand', 'name', 'product_type', 'country', 'skin_type', 'sensitivity',
            'ingredients', 'ingredient_count', 'key_ingredients', 'free_from',
            'certifications', 'benefits', 'concerns', 'rating', 'review_count',
            'review_source', 'price_usd', 'skin_type_source', 'skin_type_url']:
    n = int((c[col] != '').sum())
    say(f'    {col:20s}{n:6,}  ({100*n/N:5.1f}%)')
say()
say(f'  written  {OUT_X}')
say(f'           {OUT_C}')
say(f'           {VOCAB}   {sum(len(v) for v in vocab.values()):,} controlled values')
say(f'           {REPORT}')
open(REPORT, 'w', encoding='utf-8').write('\n'.join(log))
