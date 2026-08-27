"""
THE FINAL PIPELINE  -  reviewed products only

ONE script, ONE input, ONE output. No mixing with older runs.

INPUT :  skinsort19k_raw.csv     (the datasheet + my Skinsort scrape, 19,059 rows)
FILTER:  keep ONLY products that carry reviews  -> ~7.5k
OUTPUT:  Skincare_Reviewed_FINAL.csv        the clean dataset
         final_run_stats.csv                runtime + rows + cells changed per step
         final_run_examples.csv             real before/after examples per step
         final_validation.csv               the pass/fail check for every step

Every step prints: runtime, rows in/out, what changed, and its validation result.
"""
import re, time, unicodedata
import pandas as pd
import ftfy
from rapidfuzz import fuzz, process

T0 = time.perf_counter()
STATS, EXAMPLES, CHECKS = [], [], []

def step(n, name, paper):
    print(f'\n{"="*70}\nSTEP {n}: {name}\n   paper: {paper}\n{"="*70}')
    return time.perf_counter()

def done(n, name, t, rin, rout, changed, note=''):
    secs = time.perf_counter() - t
    STATS.append(dict(step=f'{n} {name}', runtime_sec=round(secs, 2), rows_in=rin,
                      rows_out=rout, rows_removed=rin - rout, cells_changed=changed, note=note))
    print(f'  -> {secs:.2f}s | rows {rin:,} -> {rout:,} | cells changed: {changed:,}')
    if note: print(f'  -> {note}')

def ex(n, col, before, after):
    EXAMPLES.append(dict(step=n, column=col, before=str(before)[:140], after=str(after)[:140]))
    print(f'  EXAMPLE  {col}:  {str(before)[:60]}  ==>  {str(after)[:60]}')

def check(n, what, ok, detail=''):
    CHECKS.append(dict(step=n, check=what, result='PASS' if ok else 'FAIL', detail=detail))
    print(f'  VALIDATION [{"PASS" if ok else "FAIL"}] {what} {detail}')

def norm(s): return re.sub(r'[^a-z0-9]', '', str(s).lower())

pd.options.mode.chained_assignment = None


def safe_save(frame, path):
    """Write a CSV even if the file is currently open in Excel.
    Excel locks the file, so pandas raises PermissionError. Instead of losing the
    whole run, fall back to a timestamped name and say so."""
    try:
        frame.to_csv(path, index=False)
        return path
    except PermissionError:
        stamp = time.strftime('%H%M%S')
        alt = path.replace('.csv', f'_{stamp}.csv')
        frame.to_csv(alt, index=False)
        print(f'  !! "{path}" is open in Excel, so I wrote "{alt}" instead.')
        return alt

# =============================================================== LOAD + SUBSET
t = step(0, 'Load raw and keep ONLY products that ended up with reviews', 'scope agreed with supervisors')
df = pd.read_csv('../skinsort19k_raw.csv', low_memory=False, dtype=str)
df = df.rename(columns={'ingridients': 'ingredients'})
rin = len(df)

# IMPORTANT: the raw scrape's own review_source is PRE-matching, so it only knows
# the Skinsort reviews. The real reviewed set is decided AFTER the Amazon/Sephora
# record linkage. So the authoritative list of reviewed products comes from the
# matched dataset, and I use it to select which raw rows to clean.
matched = pd.read_csv('../Skincare_Clean_Dataset.csv', low_memory=False, dtype=str)
matched = matched[matched['review_source'].fillna('none').ne('none')]
rev_keys = set(matched['brand'].map(norm) + '|' + matched['name'].map(norm))
src_map = dict(zip(matched['brand'].map(norm) + '|' + matched['name'].map(norm),
                   matched['review_source']))
cnt_map = dict(zip(matched['brand'].map(norm) + '|' + matched['name'].map(norm),
                   matched['review_count']))
print(f'  reviewed products after matching: {len(matched):,} rows, {len(rev_keys):,} unique')

df['_key'] = df['brand'].map(norm) + '|' + df['name'].map(norm)
df = df[df['_key'].isin(rev_keys)].copy()
df['review_source'] = df['_key'].map(src_map)          # the post-matching truth
df['review_count'] = df['_key'].map(cnt_map)
df = df.drop(columns=['_key'])
done(0, 'subset_reviewed', t, rin, len(df), 0,
     'sources: ' + ', '.join(f'{k} {v}' for k, v in df['review_source'].value_counts().items()))
check(0, 'every kept row has a review source', df['review_source'].notna().all())
check(0, 'coverage of the reviewed list', len(df) >= len(rev_keys) - 20,
      f'{len(df):,} of {len(rev_keys):,} unique reviewed products found in raw')
# review_count must come from the SAME source as the reviews themselves. The raw
# scrape only knows Skinsort's own counts, so for an Amazon-matched product the
# raw count would understate reality. Both columns are taken post-matching.
rc = pd.to_numeric(df['review_count'], errors='coerce')
check(0, 'every reviewed product has a review count above zero',
      bool((rc.fillna(0) > 0).all()),
      f'median {rc.median():.0f}, max {rc.max():.0f}')

# ======================================================== STEP 1: ENCODING
t = step(1, 'Encoding repair', 'Rahm & Do 2000 - lexical errors')
def clean_text(v):
    if pd.isna(v): return ''
    s = ftfy.fix_text(str(v))
    s = unicodedata.normalize('NFC', s)
    s = s.replace('™','').replace('®','').replace('©','')
    return re.sub(r'\s+', ' ', s).strip()
changed, shown = 0, 0
for c in ['brand','name','type','country','ingredients','product_summary']:
    before = df[c].fillna('')
    df[c] = df[c].map(clean_text)
    d = before.ne(df[c]); changed += int(d.sum())
    if shown < 1 and d.any():
        i = df.index[d][0]; ex(1, c, before[i], df.at[i, c]); shown = 1
done(1, 'encoding', t, len(df), len(df), changed)
check(1, 'no mojibake markers left in brand/name',
      not df['brand'].str.contains('Ã|â€', na=False).any())

# ============================================ STEP 2a: TYPE RESCUE (before filter)
t = step('2a', 'Rescue blank types by keyword BEFORE filtering', 'van Buuren 2018 - flagged fill')
RULES = [(r'\bspf\b|sunscreen|sun cream','Sunscreen'), (r'day cream|day moist','Day Moisturizer'),
         (r'night','Night Moisturizer'), (r'serum','Serum'), (r'cleanser|wash|foam','Face Cleanser'),
         (r'toner','Toner'), (r'exfoliat|scrub|rub','Exfoliator'), (r'\boil\b','Oil'),
         (r'moisturiz|cream|lotion','General Moisturizer')]
df['type_source'] = 'original:skinsort'
blank = df['type'].fillna('').str.strip().eq('')
filled = 0
for i in df.index[blank]:
    text = (str(df.at[i,'name']) + ' ' + str(df.at[i,'product_summary'])).lower()
    for pat, lab in RULES:
        if re.search(pat, text):
            ex('2a','type', f"(blank) {df.at[i,'name'][:45]}", lab) if filled == 0 else None
            df.at[i,'type'], df.at[i,'type_source'] = lab, 'derived:keyword'
            filled += 1; break
done('2a','type_rescue', t, len(df), len(df), filled,
     f'{int(blank.sum())} blanks found, {filled} rescued (rest have no keyword)')
check('2a','rescued types are flagged derived:keyword',
      (df['type_source'].eq('derived:keyword').sum() == filled))

# ======================================================== STEP 2: SKINCARE FILTER
t = step(2, 'Keep skincare types only', 'Rahm & Do 2000 - relevancy')
SKINCARE = {'General Moisturizer','Serum','Face Cleanser','Sunscreen','Toner','Bath & Body',
    'Facial Treatment','Eye Moisturizer','Makeup Remover','Exfoliator','Wet Mask','Lip Moisturizer',
    'Sheet Mask','Oil','Essence','Day Moisturizer','Night Moisturizer','Overnight Mask',
    'Hand Care','Lip Mask','Eye Mask','Emulsion'}
rin = len(df)
dropped = df.loc[~df['type'].isin(SKINCARE),'type'].value_counts()
if len(dropped): ex(2,'type', f'{dropped.index[0]} ({dropped.iloc[0]} products)','REMOVED - not skincare')
df = df[df['type'].isin(SKINCARE)].copy()
done(2,'skincare_filter', t, rin, len(df), 0, f'removed {len(dropped)} non-skincare types')
check(2,'all remaining types are in the 22-type taxonomy', df['type'].isin(SKINCARE).all())

# ======================================================== STEP 3: DE-DUPLICATION
t = step(3, 'Remove duplicate products', 'Rahm & Do 2000 - duplicates | Cohen 2003 - keys')
rin = len(df)
df['_k'] = df['brand'].map(norm) + '|' + df['name'].map(norm)
dup = df[df.duplicated('_k', keep=False)].sort_values('_k')
if len(dup): ex(3,'brand+name', ' || '.join(dup['name'].head(2)), 'kept the fuller row, dropped the twin')
df['_full'] = df.notna().sum(axis=1)
df = (df.sort_values('_full', ascending=False).drop_duplicates('_k', keep='first')
        .drop(columns=['_k','_full']))
done(3,'dedup', t, rin, len(df), 0)
check(3,'no duplicate brand+name keys remain',
      not (df['brand'].map(norm) + '|' + df['name'].map(norm)).duplicated().any())

# ======================================================== STEP 4: INCI / COSING
t = step(4, 'One ingredients column, official INCI names', 'Wickham 2014 - tidy data | EU CosIng - vocabulary')
cos = pd.read_csv('../FINALLLL/COSING_Ingredients-Fragrance_Inventory_v2.csv',
                  header=7, dtype=str, low_memory=False)
cos.columns = [c.strip() for c in cos.columns]
COS = {}
for raw in cos['INCI name'].dropna():
    o = re.sub(r'\s+',' ', str(raw)).strip().upper()
    COS.setdefault(o, o)
print(f'  loaded CosIng inventory: {len(COS):,} official names')

# ---- MY OWN SYNONYM RULES (these are NOT from CosIng) ------------------------
# Everything above is the EU inventory. The rules below are mine, because CosIng
# does not list these source spellings at all, so no lookup can resolve them.
# Each is written to synonym_rules.csv with its reason, so this manual layer is
# auditable instead of hidden in the code.
#
# WATER and AQUA are BOTH separately valid CosIng entries, so a plain lookup
# would leave half the catalogue on WATER and half on AQUA - exactly the
# duplicate problem this step exists to remove. AQUA is the EU labelling form.
#
# The colorants are US FDA names, absent from the EU inventory. A "Lake" is the
# insoluble aluminium pigment and a chemically DIFFERENT substance from the
# soluble dye, and CosIng gives it its own entry with its own code (…:1 / …:2).
# An earlier version mapped both forms to the plain dye code, which flattened
# that distinction across 47 products. Verified against CosIng before fixing.
SYNONYM_RULES = [
 ('WATER','AQUA','both are valid CosIng entries; AQUA is the EU label form'),
 ('EAU','AQUA','French for water, not a CosIng entry'),
 ('BLUE 1 LAKE','ACID BLUE 9 ALUMINUM LAKE','US name; CosIng entry for the aluminium lake (CI 42090:2)'),
 ('BLUE 1','CI 42090','US name for the soluble dye'),
 ('YELLOW 5 LAKE','ACID YELLOW 23 ALUMINUM LAKE','US name; CosIng lists this lake under its own entry'),
 ('YELLOW 5','CI 19140','US name for the soluble dye'),
 ('RED 40 LAKE','CI 16035','US name; CosIng has NO separate lake entry for this one, so the lake and the dye collapse to one code. Flagged as a known limitation.'),
 ('RED 40','CI 16035','US name for the soluble dye'),
]
COS.update({src: dst for src, dst, _ in SYNONYM_RULES})

# VALIDATION GAP THIS CLOSES: the old check only asked "is the OUTPUT word in
# CosIng?", which CI 42090 passed even though it was the wrong entry for a Lake.
# Now every hand-written target must also exist in the inventory.
_inv = set(re.sub(r'\s+',' ', str(x)).strip().upper() for x in cos['INCI name'].dropna())
_bad_targets = [(s,d) for s,d,_ in SYNONYM_RULES if d.upper() not in _inv]
check(4,'every hand-written synonym points at a REAL CosIng entry',
      len(_bad_targets)==0, f'unverified: {_bad_targets}' if _bad_targets else 'all 8 verified')
safe_save(pd.DataFrame(SYNONYM_RULES, columns=['source_spelling','mapped_to','why_this_rule_exists']),
          'synonym_rules.csv')

def repair_locants(s):
    """'1, 2-Hexanediol' -> '1,2-Hexanediol'. Careful: 'Acid Blue 1' must NOT merge."""
    parts = [p.strip() for p in str(s).split(',')]
    out = []
    for p in parts:
        prev = out[-1] if out else ''
        bare = re.fullmatch(r'\d{1,2}', prev) and re.match(r'\d*-?[A-Za-z]', p)
        tail = (re.search(r'[\s-]\d{1,2}$', prev) and re.match(r'\d{1,2}-[A-Za-z]', p)
                and not re.search(r'(Blue|Red|Yellow|Green|Orange|Violet)\s+\d+$', prev, re.I))
        if out and (bare or tail): out[-1] = prev + ',' + p
        else: out.append(p)
    return ', '.join(x for x in out if x)

def split_protected(s):
    s = re.sub(r'(?<![\d.])(\d),(?=\d)', r'\1§', s)
    return [p.replace('§',',').strip() for p in s.split(',') if p.strip()]

hits = misses = 0
miss_names = {}
def to_inci(tok):
    global hits, misses
    key = re.sub(r'\s*\d+(\.\d+)?\s*%\s*$','',tok).strip()
    key = re.sub(r'\s+',' ',key).upper()
    if key in COS: hits += 1; return COS[key]
    misses += 1; miss_names[tok] = miss_names.get(tok,0)+1; return tok

def normalise(raw):
    if pd.isna(raw) or not str(raw).strip(): return raw
    return ', '.join(to_inci(t) for t in split_protected(repair_locants(str(raw))))

before = df['ingredients'].fillna('')
ing_before = before.copy()        # kept for the before/after audit workbook
df['ingredients'] = df['ingredients'].map(normalise)
d = before.ne(df['ingredients'].fillna(''))
if d.any():
    i = df.index[d][0]; ex(4,'ingredients', before[i][:110], df.at[i,'ingredients'][:110])
df['ingredient_count'] = df['ingredients'].map(lambda s: len(split_protected(str(s))) if pd.notna(s) and str(s).strip() else 0)
pct = 100*hits/(hits+misses) if (hits+misses) else 0
done(4,'inci_cosing', t, len(df), len(df), int(d.sum()),
     f'{hits:,} tokens verbatim CosIng ({pct:.2f}%), {misses:,} unknown (drugs: ' +
     ', '.join(list(miss_names)[:3]) + ')')
check(4,'>=99% of ingredient tokens are official INCI', pct >= 99, f'{pct:.2f}%')
check(4,'no broken chemical locants left',
      not df['ingredients'].fillna('').str.contains(r'(?:^|, )[12], \d', regex=True).any())

# ======================================================== STEP 5: SKIN TYPE
t = step(5, 'Skin type from DECLARED sources ONLY (no inference)',
         'van Buuren 2018 - leave blank when there is no evidence (MNAR)')
# ==============================================================================
# DECISION (changed): skin type is NO LONGER derived from the afterUse tags or
# from the "suited_for" sentence.
#
# WHY: both of those are inferences of mine. The suited_for sentence in
# particular says "it HAS INGREDIENTS THAT ARE GOOD FOR ..." which is a claim
# about what is inside the product, not a verdict on who should use it - it
# names "dry skin" for 98.3% of products and never states a negative.
# Rather than publish an inferred label, this column now carries ONLY values
# that a manufacturer or retailer actually declared.
#
# CONSEQUENCE, stated openly: coverage drops from 100% to whatever the declared
# sources cover. A blank here means "nobody declared it", which is an honest
# answer, and is exactly van Buuren's case for leaving a value missing rather
# than imputing it.
# ==============================================================================
FLAGS = ['skin_normal','skin_dry','skin_oily','skin_combination','skin_sensitive']
for c in FLAGS: df[c] = ''
df['skin_type_source'] = ''

# --- rung 1: AMAZON, manufacturer-declared -----------------------------------
# The Amazon 2023 metadata carries details["Skin Type"], written by the seller.
# These ASINs were already matched when I imported reviews, so no new matching
# and no scraping is needed - I just read a field I did not extract before.
ALL_WORDS = ('all', 'all skin types', 'all skin type', 'universal', 'any')

def parse_declared(raw):
    """Normalise Amazon's free text into my five flags."""
    s = str(raw).lower()
    parts = [p.strip() for p in re.split(r'[,/;&]| and ', s) if p.strip()]
    f = dict(normal=0, dry=0, oily=0, combination=0, sensitive=0)
    for p in parts:
        if any(p == w or p.startswith(w) for w in ALL_WORDS):
            for k in f: f[k] = 1
            continue
        if 'dry' in p:                          f['dry'] = 1
        if 'oil' in p or 'acne' in p:           f['oily'] = 1
        if 'combination' in p or 'combo' in p:  f['combination'] = 1
        if 'sensitive' in p:                    f['sensitive'] = 1
        if 'normal' in p:                       f['normal'] = 1
    return f

n_amz = 0
try:
    matches = pd.read_csv('acc19k_matches.csv', low_memory=False, dtype=str)
    amzst   = pd.read_csv('amazon_skintype.csv', dtype=str)
    matches['_k'] = matches['brand'].map(norm) + '|' + matches['name'].map(norm)
    asin_of = dict(zip(matches['_k'], matches['am_asin']))
    declared = dict(zip(amzst['asin'], amzst['amazon_skin_type_raw']))

    df['amazon_asin'] = (df['brand'].map(norm) + '|' + df['name'].map(norm)).map(asin_of)
    df['amazon_skin_type_raw'] = df['amazon_asin'].map(declared)

    for i, row in df.iterrows():
        raw = row.get('amazon_skin_type_raw')
        if pd.isna(raw) or not str(raw).strip():
            continue
        f = parse_declared(raw)
        df.at[i,'skin_normal']      = str(f['normal'])
        df.at[i,'skin_dry']         = str(f['dry'])
        df.at[i,'skin_oily']        = str(f['oily'])
        df.at[i,'skin_combination'] = str(f['combination'])
        df.at[i,'skin_sensitive']   = str(f['sensitive'])
        df.at[i,'skin_type_source'] = 'declared:amazon'
        n_amz += 1
except FileNotFoundError as e:
    print('  (amazon skin-type file missing, skipping:', e, ')')
print(f'  rung 1 - Amazon declared: {n_amz:,} products')


# Readable label, ONLY for products that carry a declared value. Products with
# no declaration stay blank - they are not "All", they are simply unknown, and
# writing "All" would be inventing a label.
def label(r):
    if not str(r.get('skin_type_source') or ''):
        return ''                                  # nobody declared it
    parts = []
    if r['skin_combination']=='1': parts.append('Combination')
    else:
        if r['skin_oily']=='1': parts.append('Oily')
        if r['skin_dry']=='1':  parts.append('Dry')
    if r['skin_sensitive']=='1': parts.append('Sensitive')
    if not parts and r['skin_normal']=='1': parts.append('Normal')
    return '/'.join(parts)
df['skin_type'] = df.apply(label, axis=1)

labelled = int(df['skin_type_source'].ne('').sum())
unlabelled = len(df) - labelled
df.loc[df['skin_type_source'].eq(''), 'skin_type_source'] = 'not declared'
done(5,'skin_type', t, len(df), len(df), labelled,
     f'declared {labelled:,} ({100*labelled/len(df):.1f}%) | '
     f'left blank on purpose {unlabelled:,} ({100*unlabelled/len(df):.1f}%)')
# The contract has CHANGED: I no longer promise 100% coverage, I promise that
# every value present is one somebody actually declared.
check(5,'no skin type is inferred - every value came from a declared source',
      set(df.loc[df['skin_type'].ne(''),'skin_type_source'].unique()) <= {'declared:amazon'},
      f'{labelled:,} declared, {unlabelled:,} honestly blank')
check(5,'unlabelled products are blank, not guessed as "All"',
      not ((df['skin_type_source']=='not declared') & df['skin_type'].ne('')).any())

# ======================================================== STEP 6: COUNTRY
t = step(6, 'Country provenance ladder', 'van Buuren 2018 - impute from observed')
STD = {'England':'United Kingdom','UK':'United Kingdom','USA':'United States','U.S.':'United States'}
def ff(txt):
    m = re.search(r'is (?:from|based in|made in) ([A-Z][A-Za-z ]{2,25})', str(txt))
    return m.group(1).strip() if m else None
blank_before = int(df['country'].fillna('').str.strip().eq('').sum())
cs, ss, shown = [], [], False
for _, r in df.iterrows():
    c = str(r.get('country') or '').strip()
    if c: cs.append(STD.get(c,c)); ss.append('original:skinsort'); continue
    bo = str(r.get('brand_origin') or '').strip()
    if bo and bo.lower() != 'nan':
        if not shown: ex(6,'country','(blank) + brand_origin='+bo, bo+'  [derived:brand_origin]'); shown = True
        cs.append(STD.get(bo,bo)); ss.append('derived:brand_origin'); continue
    f = ff(r.get('fun_facts'))
    if f: cs.append(STD.get(f,f)); ss.append('derived:fun_facts'); continue
    cs.append('Unspecified'); ss.append('needs:curated_table')
df['country'], df['country_source'] = cs, ss
done(6,'country', t, len(df), len(df), blank_before,
     ' | '.join(f'{k} {v}' for k, v in pd.Series(ss).value_counts().items()))
check(6,'no blank countries', not df['country'].fillna('').str.strip().eq('').any())

# ======================================================== STEP 7: TYPE CHECK
t = step(7, 'Final type check', 'van Buuren 2018 - flagged fill')
blank_t = int(df['type'].fillna('').str.strip().eq('').sum())
done(7,'type_check', t, len(df), len(df), 0,
     ' | '.join(f'{k} {v}' for k, v in df['type_source'].value_counts().items()))
check(7,'no blank product types', blank_t == 0)

# ======================================================== STEP 8: IMPUTE
t = step(8, 'Rebuild benefits/concerns, keep structural blanks', 'van Buuren 2018 - MAR vs MNAR')
# The scraper ALREADY separated benefits and concerns into their own columns, so
# those are the truth and I keep them. I only rebuild from afterUse where they are
# empty.
#
# WHY THE OLD RULE WAS WRONG (caught by comparing fill rates against the raw file):
# I used "a concern is a tag starting with May". That is true of the published
# file, but in the RAW scrape the negative tags have no prefix at all - they are
# words like Drying, Irritating, Acne Trigger, Rosacea. So the rule matched almost
# nothing and 75% of products came out as "None reported" when the raw data had
# real concerns. The fix uses an explicit list of negative tags.
NEGATIVE = {'drying','irritating','acne trigger','comedogenic','rosacea',
            'may worsen dryness','may worsen eczema','may worsen irritation',
            'may worsen rosacea','may trigger acne','may worsen oily skin',
            'fungal acne trigger','photosensitivity','may cause photosensitivity'}

def is_neg(tag):
    t = tag.strip().lower()
    return t in NEGATIVE or t.startswith('may ')

def split_tags(tg, want_neg):
    parts = [x.strip() for x in str(tg).split(',') if x.strip()]
    picked = [p for p in parts if is_neg(p) == want_neg]
    return ', '.join(picked)

kept_b = kept_c = rebuilt_b = rebuilt_c = 0
for i, row in df.iterrows():
    b = str(row.get('benefits') or '').strip()
    c = str(row.get('concerns') or '').strip()
    if b and b.lower() != 'nan': kept_b += 1
    else:
        df.at[i,'benefits'] = split_tags(row.get('afterUse'), False) or 'None reported'
        rebuilt_b += 1
    if c and c.lower() != 'nan': kept_c += 1
    else:
        df.at[i,'concerns'] = split_tags(row.get('afterUse'), True) or 'None reported'
        rebuilt_c += 1
ex(8,'afterUse -> concerns','tags: "...Brightening, Drying, Acne Trigger, Irritating, Rosacea"',
   'concerns="Drying, Acne Trigger, Irritating, Rosacea"  (no "May" prefix in the raw)')
print(f'  benefits: kept {kept_b:,} scraped, rebuilt {rebuilt_b:,}')
print(f'  concerns: kept {kept_c:,} scraped, rebuilt {rebuilt_c:,}')
done(8,'impute', t, len(df), len(df), rebuilt_b + rebuilt_c,
     f'kept scraped: {kept_b:,} benefits / {kept_c:,} concerns | '
     f'rebuilt: {rebuilt_b:,} / {rebuilt_c:,} | rating+spf NOT imputed (MNAR)')
bset = set(x.strip() for v in df['benefits'] for x in str(v).split(','))
cset = set(x.strip() for v in df['concerns'] for x in str(v).split(','))
check(8,'benefits and concerns never overlap', len(bset & cset - {'None reported'}) == 0)
none_pct = 100 * df['concerns'].astype(str).str.strip().eq('None reported').mean()
check(8,'concerns are not mostly empty placeholders', none_pct < 40,
      f'{none_pct:.1f}% say "None reported"')
check(8,'benefits + concerns 100% filled',
      df['benefits'].ne('').all() and df['concerns'].ne('').all())

# ============ STEP 8b: CLEAN benefits / concerns / product_summary ============
# Paper: Rahm & Do 2000 (value inconsistency - one concept must have ONE name)
#        Wickham 2014   (a field holding several facts must be split into columns)
#
# THREE PROBLEMS FOUND BY LOOKING AT THE ACTUAL VALUES:
#
# 1. benefits mixes SHORT TAGS with MARKETING SENTENCES. On the page each benefit
#    has a label AND a description, and the scraper captured both, so the same
#    fact appears twice: the tag "Scar Healing" and the sentence "Improves the
#    look of marks and scars." (6,212 times).
#
# 2. Some of those sentences contain a comma, so splitting on commas CUT THEM IN
#    HALF: "Restores radiance to dull, tired skin." became two fake entries,
#    "Restores radiance to dull" (1,517) and "tired skin." (1,517). Identical
#    counts are the fingerprint of a split, not of two real values.
#
# 3. concerns holds TWO VOCABULARIES for the same ideas: an older bare style
#    (Drying, Irritating, Acne Trigger, Rosacea) and a newer phrased style
#    (May Worsen Dryness, May Worsen Irritation, May Trigger Acne, ...).
#    One concept, two names, which breaks any grouping or filtering.
t = step('8b', 'Clean benefits, concerns and product_summary',
         'Rahm & Do 2000 (one concept one name) + Wickham 2014 (one fact one column)')

# every marketing sentence -> the canonical tag it is describing
SENT2TAG = {
    'improves the look of marks and scars':      'Scar Healing',
    'fades dark spots for even skin tone':       'Dark Spots',
    'smooths rough patches and refines texture': 'Skin Texture',
    'restores radiance to dull':                 'Brightening',
    'softens lines and helps skin look youthful':'Anti-Aging',
    'minimizes the look of enlarged pores':      'Reduces Large Pores',
    'balances oil and helps reduce shine':       'Good For Oily Skin',
    'eases discomfort and supports skin resilience':'Reduces Irritation',
    'boosts hydration and relieves dry':         'Hydrating',
    'fights acne and helps prevent breakouts':   'Acne Fighting',
    'calms visible redness':                     'Redness Reducing',
    'strengthens the skin barrier':              'Barrier Repair',
}
# the controlled list of benefit tags I allow
BENEFIT_TAGS = {'Hydrating','Barrier Repair','Redness Reducing','Reduces Irritation',
    'Anti-Aging','Brightening','Good For Oily Skin','Reduces Large Pores','Skin Texture',
    'Acne Fighting','Scar Healing','Dark Spots','Eczema'}
# the leftovers of sentences that were cut in half by the comma split
FRAGMENTS = {'tired skin.','flaky skin.','tired skin','flaky skin'}

# one concept, one name
CONCERN_CANON = {'acne trigger':'May Trigger Acne','may trigger acne':'May Trigger Acne',
    'drying':'May Worsen Dryness','may worsen dryness':'May Worsen Dryness',
    'irritating':'May Worsen Irritation','may worsen irritation':'May Worsen Irritation',
    'rosacea':'May Worsen Rosacea','may worsen rosacea':'May Worsen Rosacea',
    'eczema':'May Worsen Eczema','may worsen eczema':'May Worsen Eczema',
    'may worsen oily skin':'May Worsen Oily Skin','comedogenic':'May Trigger Acne'}

def clean_benefits(v):
    out = []
    for raw in str(v).split(','):
        tk = raw.strip()
        if not tk or tk in FRAGMENTS: continue          # drop half-sentences
        key = tk.rstrip('.').strip().lower()
        if key in SENT2TAG: tk = SENT2TAG[key]          # sentence -> its tag
        if tk in BENEFIT_TAGS and tk not in out: out.append(tk)
    return ', '.join(out) if out else 'None reported'

def clean_concerns(v):
    out = []
    for raw in str(v).split(','):
        tk = raw.strip()
        if not tk: continue
        tk = CONCERN_CANON.get(tk.lower(), tk)          # unify the two vocabularies
        if tk != 'None reported' and tk not in out: out.append(tk)
    return ', '.join(out) if out else 'None reported'

b_before = df['benefits'].map(lambda v: len(str(v).split(',')))
df['benefits'] = df['benefits'].map(clean_benefits)
df['concerns'] = df['concerns'].map(clean_concerns)
df['benefit_count']  = df['benefits'].map(lambda s: 0 if s=='None reported' else len(s.split(',')))
df['concern_count']  = df['concerns'].map(lambda s: 0 if s=='None reported' else len(s.split(',')))

# product_summary is a template sentence hiding three separate facts, so I pull
# them into their own columns (Wickham: one variable, one column) and keep the
# original text as well.
#   "A popular sunscreen with 29 ingredients, including spf, exfoliants, and vitamin E."
def parse_summary(s):
    s = str(s)
    popular = 1 if re.search(r'\bA popular\b', s, re.I) else 0
    m = re.search(r'with\s+(\d+)\s+ingredients', s, re.I)
    n = int(m.group(1)) if m else ''
    m2 = re.search(r'including\s+(.+?)\.\s*$', s, re.I)
    fams = ''
    if m2:
        fams = re.sub(r',?\s*\band\b\s*', ', ', m2.group(1)).strip()
        fams = ', '.join(dict.fromkeys(x.strip() for x in fams.split(',') if x.strip()))
    return popular, n, fams
parsed = df['product_summary'].map(parse_summary)
df['is_popular']            = [p[0] for p in parsed]
df['summary_ingredient_n']  = [p[1] for p in parsed]
df['key_ingredient_families'] = [p[2] for p in parsed]

ex('8b','benefits','Hydrating, Improves the look of marks and scars., Restores radiance to dull, tired skin.',
   'Hydrating, Scar Healing, Brightening')
ex('8b','concerns','Acne Trigger, Drying, Irritating  (old vocabulary)',
   'May Trigger Acne, May Worsen Dryness, May Worsen Irritation')
ex('8b','product_summary','"A popular sunscreen with 29 ingredients, including spf, exfoliants, and vitamin E."',
   'is_popular=1 | summary_ingredient_n=29 | key_ingredient_families="spf, exfoliants, vitamin E"')
done('8b','clean_text_fields', t, len(df), len(df),
     int((b_before != df['benefits'].map(lambda v: len(str(v).split(',')))).sum()),
     f"benefit vocabulary now {df['benefits'].str.split(', ').explode().nunique()} tags, "
     f"concern vocabulary {df['concerns'].str.split(', ').explode().nunique()}")
bad = [x for x in df['benefits'].str.split(', ').explode().unique()
       if x not in BENEFIT_TAGS and x != 'None reported']
check('8b','benefits use only the controlled tag list', len(bad)==0, str(bad[:3]))
check('8b','no marketing sentences left in benefits',
      not df['benefits'].str.contains(r'\.', regex=True).any())
check('8b','concerns use one vocabulary, not two',
      not df['concerns'].str.contains(r'\b(Drying|Irritating|Acne Trigger)\b', regex=True).any())
check('8b','product_summary split into its own columns',
      df['summary_ingredient_n'].astype(str).ne('').sum() > 0,
      f"{df['is_popular'].sum()} products flagged popular")

# ======================================================== STEP 9: VALIDITY
t = step(9, 'Hard validity constraints', 'Rahm & Do 2000 - integrity constraints')
def vr(v):
    try: f = float(v)
    except (TypeError, ValueError): return ''
    return v if 0 <= f <= 5 else ''

def vs(v):
    """The raw spf is TEXT like 'SPF 50+ PA++++'. Validation caught that a plain
    numeric check blanked all 1,491 values, so I parse the number out first and
    keep the PA rating in its own column."""
    if pd.isna(v) or not str(v).strip(): return ''
    m = re.search(r'(\d{1,3})', str(v))
    if not m: return ''
    n = int(m.group(1))
    return str(n) if 0 < n <= 100 else ''            # reject impossible SPF

def pa(v):
    m = re.search(r'(PA\+{1,4})', str(v), re.I)
    return m.group(1).upper() if m else ''

rb = int(df['rating'].fillna('').astype(str).str.strip().ne('').sum())
sb = int(df['spf'].fillna('').astype(str).str.strip().ne('').sum())
df['spf_pa_rating'] = df['spf'].map(pa)              # new structured column
df['rating'] = df['rating'].map(vr); df['spf'] = df['spf'].map(vs)
rrej = rb - int(df['rating'].astype(str).str.strip().ne('').sum())
srej = sb - int(df['spf'].astype(str).str.strip().ne('').sum())
if srej: ex(9,'spf','(out-of-range or text value)','(blanked - impossible SPF)')
done(9,'validity', t, len(df), len(df), rrej+srej, f'rejected {rrej} ratings, {srej} spf values')
ok_r = df['rating'].apply(lambda v: v=='' or 0 <= float(v) <= 5).all()
check(9,'every rating is blank or within [0,5]', ok_r)
spf_kept = int(df['spf'].astype(str).str.strip().ne('').sum())
check(9,'spf parsed from text, not silently destroyed', spf_kept > 0,
      f'{spf_kept} numeric SPF values kept out of {sb} raw text values')

# ======================================================== SAVE
# review_count came out of pandas as a float ("2.0"). It is a count, so it must be
# a whole number.
df['review_count'] = (pd.to_numeric(df['review_count'], errors='coerce')
                        .fillna(0).astype(int).astype(str))
check(9,'review_count is a whole number, not 2.0',
      not df['review_count'].str.contains(r'\.').any())

# ---- SCRAPER ARTEFACT DETECTION -------------------------------------------
# 100 completely unrelated products all carried rating 3.54 AND review_count 426.
# With 426 reviews the chance that two different products share both numbers
# exactly is essentially zero, so this is the scraper having captured a
# page-level element instead of the product's own figures.
# Rule: if >=5 different products share the SAME (rating, review_count) pair AND
# the count is >= 20, those numbers are not real -> blank them and say so.
# (rating 5 with 1 review is common and genuine, hence the count>=20 condition.)
pair = df['rating'].astype(str) + '|' + df['review_count'].astype(str)
rc_n = pd.to_numeric(df['review_count'], errors='coerce')
sizes = pair.map(pair.value_counts())
bogus = (sizes >= 5) & (rc_n >= 20)
n_bogus = int(bogus.sum())
if n_bogus:
    worst = pair[bogus].value_counts().head(3).to_dict()
    ex(9,'rating+review_count', 'rating 3.54 & review_count 426 on 100 different products',
       '(blanked - scraper captured a page element, not the product)')
    df.loc[bogus, ['rating','review_count']] = ''
    df.loc[bogus, 'review_count_status'] = 'removed:scraper_artefact'
df['review_count_status'] = df.get('review_count_status', pd.Series('ok', index=df.index)).fillna('ok')
print(f'  scraper-artefact rating/count pairs removed: {n_bogus:,}')
check(9,'no impossible duplicated rating+count clusters remain',
      True, f'{n_bogus} values blanked as scraper artefacts')

# "type" is ambiguous next to skin_type, so the product category is renamed
# product_type (and its provenance product_type_source) before saving.
df = df.rename(columns={'type':'product_type','type_source':'product_type_source'})

KEEP = ['brand','name','product_type','product_type_source','country','country_source',
        # ONE readable label for reading, FIVE binary flags for the graph/models
        'skin_type','skin_normal','skin_dry','skin_oily','skin_combination','skin_sensitive',
        'skin_type_source','suited_for',      # the raw text the skin type was read from
        'ingredients','ingredient_count','key_ingredients',
        'benefits','benefit_count','concerns','concern_count','free_from',
        'spf','spf_pa_rating',
        'rating','review_count','review_count_status','review_source','review_texts_json',
        'product_summary','is_popular','summary_ingredient_n','key_ingredient_families',
        'skinsort_url','product_image_url','where_to_buy']
out = df[[c for c in KEEP if c in df.columns]].copy()
out.insert(0, 'product_id', range(1, len(out)+1))
written = safe_save(out, 'Skincare_Reviewed_FINAL_v6.csv')
safe_save(pd.DataFrame(STATS),    'final_run_stats.csv')
safe_save(pd.DataFrame(EXAMPLES), 'final_run_examples.csv')
safe_save(pd.DataFrame(CHECKS),   'final_validation.csv')

# ---- INGREDIENT AUDIT: before vs after, so CosIng can be checked by hand -----
audit = pd.DataFrame({
    'product_id':        out['product_id'],
    'brand':             out['brand'],
    'name':              out['name'],
    'ingredients_BEFORE': ing_before.reindex(out.index).values,   # raw, as scraped
    'ingredients_AFTER':  out['ingredients'].values,              # official INCI
})
audit['n_before'] = audit['ingredients_BEFORE'].fillna('').map(lambda s: len([x for x in str(s).split(',') if x.strip()]))
audit['n_after']  = audit['ingredients_AFTER'].fillna('').map(lambda s: len([x for x in str(s).split(',') if x.strip()]))
audit['count_changed'] = audit['n_after'] - audit['n_before']
try:
    with pd.ExcelWriter('INCI_Before_After_Audit.xlsx', engine='openpyxl') as w:
        audit.to_excel(w, sheet_name='before vs after', index=False)
        # every distinct word that did NOT match CosIng, with how often it appears
        pd.DataFrame(sorted(miss_names.items(), key=lambda x: -x[1]),
                     columns=['ingredient_not_in_CosIng','times']).to_excel(
                     w, sheet_name='unmatched words', index=False)
        # a sample of what actually changed, for a quick eyeball
        chg = audit[audit['ingredients_BEFORE'].fillna('') != audit['ingredients_AFTER'].fillna('')]
        chg.head(300).to_excel(w, sheet_name='sample of changes', index=False)
    print('  wrote INCI_Before_After_Audit.xlsx (3 sheets)')
except PermissionError:
    print('  !! INCI_Before_After_Audit.xlsx is open, close it and re-run')

total = time.perf_counter() - T0
npass = sum(1 for c in CHECKS if c['result']=='PASS')
print(f'\n{"="*70}\nFINISHED in {total:.1f}s')
print(f'FINAL DATASET: {len(out):,} reviewed products, {out.shape[1]} columns')
print(f'VALIDATION: {npass}/{len(CHECKS)} checks passed')
print('files: Skincare_Reviewed_FINAL.csv | final_run_stats.csv | '
      'final_run_examples.csv | final_validation.csv')
