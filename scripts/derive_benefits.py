"""
Benefits, read from what the product already says about itself

COSTS NOTHING. No searching, no keys. 5,823 products have no benefits, and
5,153 of those already carry the shop's own description of the product. The
words are sitting in the file.

Three jobs, in this order
  1. TIDY WHAT IS THERE. The column holds two vocabularies. Twelve values
     appear thousands of times each, and a tail of near-duplicates appears
     once or twice: "Hydration" beside "Hydrating", "Acne" beside "Acne
     Fighting", "Pores" beside "Reduces Large Pores". The tail is folded into
     the main list.

Usage:
    py derive_benefits.py --dry     say what would change
    py derive_benefits.py           do it
"""
import os
import re
import csv
import sys
import collections

csv.field_size_limit(10 ** 8)
DATA = 'COMBINED_DATASET.csv'
DRY = '--dry' in sys.argv

# ------------------------------------------------------- the allowed values
# The twelve that already appear thousands of times, plus two the data uses
# meaningfully. Nothing outside this list is ever written.
BENEFITS = ['Hydrating', 'Anti-Aging', 'Brightening', 'Acne Fighting',
            'Barrier Repair', 'Reduces Irritation', 'Redness Reducing',
            'Scar Healing', 'Reduces Large Pores', 'Skin Texture',
            'Dark Spots', 'Good For Oily Skin', 'Eczema', 'Sun Protection']

# the tail of near-duplicates, folded into the main list
FOLD = {
    'hydration': 'Hydrating', 'moisturizing': 'Hydrating',
    'moisturising': 'Hydrating',
    'acne': 'Acne Fighting', 'pores': 'Reduces Large Pores',
    'sensitivity': 'Reduces Irritation', 'soothing': 'Reduces Irritation',
    'soothe': 'Reduces Irritation', 'calming': 'Reduces Irritation',
    'exfoliation': 'Skin Texture', 'smoothing': 'Skin Texture',
    'hyperpigmentation': 'Dark Spots', 'firming': 'Anti-Aging',
    'purifying': 'Good For Oily Skin', 'oil control': 'Good For Oily Skin',
    'anti aging': 'Anti-Aging', 'antiaging': 'Anti-Aging',
    'anti-ageing': 'Anti-Aging', 'brightening': 'Brightening',
    'sun protection': 'Sun Protection', 'spf': 'Sun Protection',
}
# things that are not benefits and should be empty
NOT_A_BENEFIT = {'none reported', 'none', 'general skincare', 'cleansing',
                 'n/a', 'not available', 'unknown', '-'}

# ---------------------------------------------- reading a claim from a blurb
CLAIMS = [
    (r'hydrat|moistur|water[- ]?retention|humect|quench|dewy|dryness', 'Hydrating'),
    (r'anti[- ]?ag|fine lines?|wrinkl|elastic|collagen|firm|lift|sagg|plump',
     'Anti-Aging'),
    # "complexion" on its own is not a brightening claim. "For a clear
    # complexion" is about acne. It only counts next to a word about light.
    (r'brighten|radian|glow|dull|luminos|luminous|even(?:s|ing)? (?:out )?(?:the )?'
     r'(?:skin )?tone|(?:brighten|illuminat|lighten|even|radian|luminous)\w* '
     r'(?:the |your )?complexion', 'Brightening'),
    (r'acne|blemish|breakout|spot[- ]?prone|pimple|blackhead|whitehead|comedon',
     'Acne Fighting'),
    (r'barrier|ceramid|protect(?:s|ive)? (?:the )?skin|strengthen(?:s|ing)? '
     r'(?:the )?skin|resilien', 'Barrier Repair'),
    (r'sooth|calm|irritat|comfort|sensitiv|relie', 'Reduces Irritation'),
    (r'redness|rosacea|flush', 'Redness Reducing'),
    # heal, not health. The loose version matched "healthy", "healthier"
    # and "skin health" 257 times, none of which is a claim to heal anything.
    # "renew" and "recover" are dropped for the same reason: "cell renewal"
    # is a texture claim and "recovery" is usually about the routine.
    (r'\bscars?\b|\bheals?\b|\bhealing\b|\brepairs?\b|\brepairing\b|regenerat',
     'Scar Healing'),
    (r'pore|refin(?:e|es|ing) (?:the )?skin', 'Reduces Large Pores'),
    (r'textur|exfoliat|smooth|rough|resurfac|polish|soft(?:en|ens|ening)',
     'Skin Texture'),
    (r'dark spot|pigment|melanin|discolo|blemish mark|sun spot|age spot',
     'Dark Spots'),
    # "shine" is the trap here. A lip gloss promising a glossy shine is not
    # claiming to control oil, and neither is a highlighter. Only shine that
    # is being REDUCED counts, which is what the words around it show.
    (r'oil(?:y|iness)? (?:control|skin)|excess oil|sebum|mattif|matte finish|'
     r'(?:reduces?|controls?|minimi[sz]es?|less|excess|unwanted|free of|'
     r'combats?|fights?) \w{0,12}shine|shine[- ]?(?:control|free)|'
     r'degreas|removes? (?:dirt|oil)', 'Good For Oily Skin'),
    (r'eczema|dermatitis|psoriasis', 'Eczema'),
    (r'\bspf\s*\d|sunscreen|sun protection|uva|uvb|broad spectrum',
     'Sun Protection'),
]
CLAIMS = [(re.compile(p, re.I), b) for p, b in CLAIMS]

# "without drying", "free from irritation", "does not clog"
NEG = re.compile(r'\b(without|free from|free of|no |non[- ]|does not|doesn.t|'
                 r'never|avoid|prevents?|reduces? the risk of|anti)\b', re.I)


def claims_in(text):
    """The benefits a piece of text actually claims, negations refused."""
    t = re.sub(r'\s+', ' ', str(text))
    if len(t) < 15:
        return []
    out = []
    for pat, label in CLAIMS:
        m = pat.search(t)
        if not m:
            continue
        # look at the four words before the match. "without drying" is not a
        # claim to dry, and "prevents breakouts" is a claim to fight acne, so
        # only the plainly reversing words count.
        before = t[max(0, m.start() - 40):m.start()]
        words = before.split()[-4:]
        if any(re.fullmatch(r'without|free|no|non|not|never|avoid',
                            w.strip('.,;:').lower()) for w in words):
            continue
        if label not in out:
            out.append(label)
    return out[:6]


def tidy(value):
    """Fold the tail vocabulary into the main list and drop non-benefits."""
    out = []
    for piece in str(value).split(','):
        p = piece.strip()
        if not p:
            continue
        low = p.lower().strip(' .;')
        if low in NOT_A_BENEFIT:
            continue
        if p in BENEFITS:
            if p not in out:
                out.append(p)
            continue
        folded = FOLD.get(low)
        if folded and folded not in out:
            out.append(folded)
    return ', '.join(out)


# ===================================================================== data
with open(DATA, newline='', encoding='utf-8') as fh:
    rd = csv.DictReader(fh)
    FIELDS = list(rd.fieldnames or [])
    D = [{k: (v if v is not None else '') for k, v in r.items()} for r in rd]
if 'benefit_source' not in FIELDS:
    FIELDS.insert(FIELDS.index('benefits') + 1, 'benefit_source')
    for r in D:
        r['benefit_source'] = ''


def g(r, c):
    return str(r.get(c, '')).strip()


N = len(D)
before = sum(1 for r in D if g(r, 'benefits'))

print('=' * 72)
print('  BENEFITS, FROM WHAT THE PRODUCTS ALREADY SAY')
print('=' * 72)
print(f'  products                    {N:,}')
print(f'  had a benefit               {before:,}  ({100*before/N:.1f}%)')

# ------------------------------------------------------------- 1 and 2 tidy
n_folded = n_dropped = 0
for r in D:
    old = g(r, 'benefits')
    if not old:
        continue
    new = tidy(old)
    if new != old:
        if new:
            n_folded += 1
        else:
            n_dropped += 1
        r['benefits'] = new
    if new and not g(r, 'benefit_source'):
        r['benefit_source'] = 'the source listing'
print(f'  tidied to the main list     {n_folded:,}')
print(f'  emptied, not a benefit      {n_dropped:,}   ("None reported" and the like)')

# ------------------------------------------------------------- 3 derive
n_new = 0
found_from = collections.Counter()
added = collections.Counter()
for r in D:
    if g(r, 'benefits'):
        continue
    for field in ('product_summary', 'concerns'):
        got = claims_in(g(r, field))
        if got:
            r['benefits'] = ', '.join(got)
            r['benefit_source'] = f'read from the {field.replace("_", " ")}'
            found_from[field] += 1
            for b in got:
                added[b] += 1
            n_new += 1
            break
after = sum(1 for r in D if g(r, 'benefits'))
print(f'  read from the description   {found_from["product_summary"]:,}')
print(f'  read from the concerns      {found_from["concerns"]:,}')
print(f'  now                         {after:,}  ({100*after/N:.1f}%)')

print()
print('  WHAT WAS ADDED')
for k, v in added.most_common():
    print(f'    {k:24s}{v:6,}')

vocab = collections.Counter()
for r in D:
    for x in g(r, 'benefits').split(','):
        if x.strip():
            vocab[x.strip()] += 1
outside = sorted(set(vocab) - set(BENEFITS))
print()
print(f'  vocabulary now {len(vocab)} values'
      + (f'   OUTSIDE THE LIST: {outside}' if outside else '   all allowed'))

print()
print('  EXAMPLES')
shown = 0
for r in D:
    if g(r, 'benefit_source').startswith('read from') and g(r, 'product_summary'):
        print(f"    {g(r,'brand')[:18]:20s}{g(r,'name')[:34]:36s}")
        print(f"       said : {g(r,'product_summary')[:96]}")
        print(f"       wrote: {g(r,'benefits')}")
        shown += 1
        if shown >= 3:
            break

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
    sys.exit(f'  the file came back damaged at byte {e.start:,}, nothing replaced')
os.replace(tmp, DATA)
print(f'\n  written. now run:  py validate_dataset.py  then  py make_workbook.py')
