"""
Step 1 of 3. re-label the sources. costs nothing, no searches.

Why this exists
  When I graded each source I used a short list of retailer names and a strict
  brand-name test. Both were too narrow, so a lot of perfectly good sources
  were filed under "analysis site" or "other source" when they were nothing of
  the kind:

Usage:
    py retier.py
"""
import re
import pandas as pd

DATASET = 'SKINCARE_DATASET.csv'

# ---------------------------------------------------------------- retailers
# every shop that actually sells skincare, not just the eight I first thought of
RETAILER = re.compile(
    r'(sephora|ulta|boots\.com|douglas|lookfantastic|cultbeauty|dermstore|'
    r'feelunique|notino|amazon|walmart|target\.com|superdrug|beautybay|'
    r'yesstyle|stylevana|oliveyoung|jolse|iherb|sokoglam|watsons|nykaa|'
    r'flipkart|shopee|lazada|macys|nordstrom|bluemercury|lovelyskin|spacenk|'
    r'peachandlily|asianbeautyessentials|skinstore|beautylish|revolve|'
    r'saksfifthavenue|harrods|selfridges|johnlewis|cvs\.com|walgreens|riteaid|'
    r'costco|kohls|dillards|neimanmarcus|bloomingdales|thebay|'
    r'shoppersdrugmart|chemistwarehouse|priceline|adorebeauty|meccabeauty|'
    r'mecca\.com|sasa\.com|hktvmall|beautyhabit|stylekorean|wishtrend|'
    r'skinsociety|sohaticare|feel22|nexuscare|zeinacare|mazenonline|'
    r'dm\.de|rossmann|beautyplussalon|glowrecipe|soko|kbeauty|'
    r'thedermshop|skincarehero|beautypie|escentual|allbeauty|justmylook)', re.I)

STOP = {'the', 'la', 'le', 'dr', 'st', 'and', 'by', 'of', 'co', 'lab', 'labs',
        'beauty', 'skin', 'skincare', 'paris', 'london', 'new', 'york'}


def host(u):
    u = str(u)
    h = u.split('/')[2] if '://' in u else u
    return h.lower().lstrip('.')


def squash(s):
    return re.sub(r'[^a-z0-9]', '', str(s).lower())


def is_manufacturer(brand, source):
    """Does this domain belong to the brand?

    Three tests, any one is enough:
      1. the whole brand name, punctuation removed, appears in the domain
         "DERMA E"  ->  "dermae"  ->  found in "dermae.com"
      2. the brand's longest meaningful word appears in the domain
         "Peter Thomas Roth"  ->  "thomas" is in "peterthomasroth.com"
      3. the domain's own name, minus country and shop prefixes, matches
         "us.no7beauty.com"  ->  "no7beauty"  vs brand "No7"
    """
    h = squash(host(source))
    if not h:
        return False
    k = squash(brand)
    if len(k) >= 4 and k in h:
        return True
    words = [w for w in re.split(r'[^a-z0-9]+', str(brand).lower())
             if len(w) >= 5 and w not in STOP]
    for w in words:
        if w in h:
            return True
    # brand written as an acronym or with digits, e.g. No7 / CeraVe / A-Derma
    k2 = squash(re.sub(r'\b(the|la|le)\b', '', str(brand).lower()))
    return len(k2) >= 4 and k2 in h


# ------------------------------------------------------------------- quotes
TAG = re.compile(r'<[^>]{0,400}>')
ENT = re.compile(r'&[a-z]{2,8};|&#\d{2,5};', re.I)
JUNK = re.compile(r'(class=|id=|href=|style=|div |span |</|/>|_\d{6,})', re.I)


def clean_quote(q):
    q = str(q)
    if not q.strip():
        return ''
    q = ENT.sub(' ', TAG.sub(' ', q))
    q = re.sub(r'\s+', ' ', q).strip(' .|•"\'>-')
    # if markup survived, or there are almost no real words left, drop it
    if JUNK.search(q):
        return ''
    letters = len(re.findall(r'[a-zA-Z]', q))
    if letters < 15 or letters < 0.55 * max(len(q), 1):
        return ''
    if 'skin' not in q.lower():
        return ''
    return q[:220]


# =========================================================================
df = pd.read_csv(DATASET, low_memory=False, dtype=str).fillna('')
n = len(df)
before = df['skin_type_tier'].value_counts().to_dict()
bad_quotes_before = int((df['skin_type_quote'] != '').sum())

target = df['skin_type_tier'].isin(['3', '4'])
moved1 = moved2 = 0
rows1, rows2 = [], []

for i in df.index[target]:
    brand, src = df.at[i, 'brand'], df.at[i, 'skin_type_source']
    if is_manufacturer(brand, src):
        df.at[i, 'skin_type_tier'] = '1'
        df.at[i, 'skin_type_authority'] = 'manufacturer'
        moved1 += 1
        if len(rows1) < 6:
            rows1.append((brand, host(src)))
    elif RETAILER.search(host(src)):
        df.at[i, 'skin_type_tier'] = '2'
        df.at[i, 'skin_type_authority'] = 'retailer'
        moved2 += 1
        if len(rows2) < 6:
            rows2.append((brand, host(src)))

df['skin_type_quote'] = df['skin_type_quote'].map(clean_quote)
df.to_csv(DATASET, index=False)

after = df['skin_type_tier'].value_counts().to_dict()
got = df[df['skin_type'] != '']
t12 = int(pd.to_numeric(got['skin_type_tier'], errors='coerce').le(2).sum())

print('=' * 68)
print('  SOURCES RE-LABELLED   (no searches were made, nothing was deleted)')
print('=' * 68)
print(f'  moved into tier 1, the manufacturer   {moved1:,}')
for b, h in rows1:
    print(f'       {b[:24]:24s} {h}')
print(f'  moved into tier 2, a real retailer    {moved2:,}')
for b, h in rows2:
    print(f'       {b[:24]:24s} {h}')
print()
LAB = {'1': 'manufacturer', '2': 'retailer', '3': 'analysis site', '4': 'other source'}
print('  tier          before    after')
for t in ('1', '2', '3', '4'):
    print(f'    {t} {LAB[t]:16s}{before.get(t, 0):7,}{after.get(t, 0):9,}')
print()
print(f'  values from a manufacturer or a shop   {t12:,}  '
      f'({100*t12/max(len(got),1):.1f}% of the filled rows)')
print()
q_now = int((df['skin_type_quote'] != '').sum())
print(f'  quotes cleaned: {bad_quotes_before:,} -> {q_now:,} readable '
      f'({bad_quotes_before - q_now:,} were raw page markup and were emptied)')
print()
left = int(df['skin_type_tier'].isin(['3', '4']).sum())
print(f'  still on an analysis site or an unknown site   {left:,}')
print('  those are the ones step 2 re-searches.')
print('\nnow run:  py serper_rescue.py')
