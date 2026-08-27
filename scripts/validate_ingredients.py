"""
Check every stored ingredient list, and keep only the real formula

WHY

  4,540 ingredient lists are now stored. Reading a sample shows about a third
  are not clean:

Usage:
    py validate_ingredients.py                 fix them
    py validate_ingredients.py --report-only   look first, change nothing
"""
import re
import sys
import pandas as pd

FILES = ['LEBANESE_RETAIL.csv', 'COMBINED_DATASET.csv']
REPORT_ONLY = '--report-only' in sys.argv

# a piece that is an ingredient name rather than a phrase
CHEM_END = re.compile(
    r'(ate|ite|ide|ine|one|ol|oic acid|ic acid|yl|ene|ose|an|um|ium|'
    r'extract|oil|butter|wax|water|acid|glycol|glycerin|alcohol|gum|'
    r'powder|seed|leaf|root|fruit|flower|juice|ferment|filtrate|protein|'
    r'peptide|ceramide|vitamin|silica|mica|dioxide|oxide)$', re.I)
KNOWN = re.compile(
    r'\b(aqua|water|eau|glycerin|glycerine|sodium|potassium|calcium|zinc|'
    r'titanium|magnesium|cetearyl|cetyl|stearyl|stearic|lauryl|laureth|'
    r'dimethicone|cyclopenta|siloxane|silicone|phenoxyethanol|tocopherol|'
    r'parfum|fragrance|limonene|linalool|citral|geraniol|coumarin|'
    r'xanthan|carbomer|panthenol|niacinamide|retinol|ascorbic|hyaluron|'
    r'salicylic|glycolic|lactic|citric|benzoic|sorbic|caprylic|capric|'
    r'triglyceride|polysorbate|peg-|ppg-|butylene|propylene|pentylene|'
    r'hexanediol|urea|allantoin|bisabolol|squalane|shea|olea|cocos|'
    r'butyrospermum|simmondsia|prunus|helianthus|aloe|centella|camellia|'
    r'chamomilla|lavandula|rosa|vitis|citrus|mineral oil|paraffinum|'
    r'petrolatum|lanolin|beeswax|cera alba|laurus|hippophae|niacin|'
    r'ethylhexyl|homosalate|avobenzone|octocrylene|oxybenzone|'
    r'phenylbenzimidazole|tromethamine|edta|parabens?|methylparaben|'
    r'propylparaben|phenethyl|benzyl|caffeine|adenosine|arbutin|kojic|'
    r'azelaic|tranexamic|ceramide|collagen|elastin|keratin|silk|'
    r'hydroxyethyl|hydroxypropyl|polyquaternium|acrylates|copolymer|'
    r'ethanol|alcohol denat|isopropyl|isododecane|dicaprylyl|coco-|'
    r'decyl|myristate|palmitate|oleate|linoleate|behenate|arachidyl)', re.I)
VERB = re.compile(
    r'\b(is|are|was|were|be|been|has|have|helps?|works?|leaves?|makes?|'
    r'gives?|provides?|delivers?|targets?|addresses?|boosts?|reduces?|'
    r'improves?|designed|formulated|created|apply|rinse|use|discover|'
    r'download|get it|show|click|read|shop|buy|add to|our|your|we |this |'
    r'that |which |thanks to|join forces|acts at)\b', re.I)
JUNK_PIECE = re.compile(r'(app store|google play|safety score|show full|'
                        r'read more|©|\bcart\b|\blogin\b|http)', re.I)
# whole pieces that are benefits or claims rather than ingredients
BENEFIT = re.compile(
    r'\s*(hydrating|moisturi[sz]ing|brightening|anti[- ]?aging|anti[- ]?ageing|'
    r'soothing|calming|firming|smoothing|nourishing|purifying|clarifying|'
    r'exfoliating|cleansing|mattifying|plumping|lifting|tightening|'
    r'barrier repair|redness reducing|reduces irritation|acne fighting|'
    r'oil control|pore minimi[sz]ing|scar healing|dark spots|skin texture|'
    r'sun protection|uv protection|good for [a-z ]+ skin|reduces [a-z ]+|'
    r'improves [a-z ]+|even skin tone|radiance|glow)\s*', re.I)


def is_ingredient(piece):
    p = piece.strip(' .;:•|*-•▪()[]')
    if not p:
        return False
    if len(p) > 70 or JUNK_PIECE.search(p) or VERB.search(p):
        return False
    words = p.split()
    if len(words) > 7:
        return False
    if p.count('.') > 1:
        return False
    if KNOWN.search(p):
        return True
    # A chemical-looking ending on the last word. The minimum length is 3, not
    # 4: botanical entries very often end in "Oil", and requiring 4 characters
    # rejected "Ricinus Communis (Castor) Seed Oil", which then broke the run
    # and lost the formula around it.
    last = re.sub(r'[^A-Za-z]', '', words[-1]) if words else ''
    if len(last) >= 3 and CHEM_END.search(last):
        return True
    # things like "CI 77491" or "1,2-Hexanediol"
    if re.match(r'^(ci\s*\d{4,6}|[a-z]{2,}-\d+)$', p, re.I):
        return True
    # Botanical names. An INCI list is full of Latin binomials such as
    # "Arctostaphylos Uva-Ursi", "Morus Alba", "Butyrospermum Parkii", and no
    # word list will ever cover them all. They have a recognisable shape
    # instead: a few plain words, no verbs, no punctuation beyond hyphens,
    # brackets and slashes. Without this the run breaks at the first plant and
    # a real formula gets thrown away.
    # Accented letters have to be allowed. "Av&egrave;ne Thermal Spring Water"
    # is an ingredient, and a plain A-Z test rejected it, which broke the run
    # and threw away the whole formula around it. Same for Korean and French
    # brand names that appear inside INCI lists.
    if len(words) <= 5 and re.fullmatch(r"[^\W\d_][\w \-/()'.&%+]*", p, re.UNICODE):
        return True
    return False


GAP = 2      # how many odd pieces may sit inside a formula before it is broken


def longest_run(text):
    """Find the stretch of the text that is the formula.

    An earlier version took the longest run of UNBROKEN ingredient-looking
    pieces, and it cut real formulas in half. A single unusual name, a long
    botanical, or a stray bracket would break the run, and whichever half was
    longer survived while the other was thrown away:

        was: Aqua, propylene glycol, glycolic acid, acetyl hexapeptide-8, ...
        now: glycerin, copper peptide, polyquaternium-10, ...
             the first four ingredients were lost

    So a gap of up to GAP consecutive odd pieces is now tolerated inside a run.
    The span reaches from the first good piece to the last, and everything in
    between is kept, odd names included, because an odd name in the middle of a
    formula is almost always an ingredient I do not recognise rather than
    marketing copy.
    """
    t = str(text)
    # Some brands publish the list with a lead-in label, and some separate the
    # ingredients with FULL STOPS rather than commas:
    #
    #   "INCI formula: WATER (AQUA). CAPRYLIC/CAPRIC TRIGLYCERIDE. GLYCERIN."
    #
    # Splitting on commas alone left that as a single piece, so a perfectly
    # good formula was rejected. The lead-in is removed and the separator is
    # chosen by whichever character actually divides the text.
    # A lead-in label can appear at the start OR in the middle, as in a US
    # drug-facts panel: "Zinc Oxide 25% Inactive Ingredients: Water, ...".
    # Both are turned into separators so the list after them can be read.
    t = re.sub(r'\b(full\s+)?(inci\s*(formula|list)?|active ingredients?|'
               r'inactive ingredients?|other ingredients?|ingredients?|'
               r'composition)\s*[:\-–]\s*', ', ', t, flags=re.I)

    # Split on commas AND on full stops, always. Deciding between them by
    # counting characters failed: a list written with full stops but carrying a
    # few commas elsewhere in the text was split the wrong way, and the whole
    # formula stayed glued together as one unreadable piece.
    # A full stop followed by a space separates ingredients; one inside a name
    # such as "Alcohol Denat." is harmless, since the piece is still an
    # ingredient either way.
    # Spaced dashes are a separator too. Several brands write the list as
    #   "Aloe Vera extract - Vitamin C (L-Ascorbic acid) - Alpha-tocopherol"
    # Only SPACED dashes count, so hyphens inside a name are left alone:
    # "C12-15 Alkyl Benzoate" and "Coco-Caprylate" stay in one piece.
    pieces = [p for p in re.split(r'[,;]|\.\s+|\.$|\s[-–—]\s|\s•\s', t)
              if p is not None]
    flags = [is_ingredient(p) for p in pieces]

    spans, start, gap = [], -1, 0
    for i, ok in enumerate(flags + [False] * (GAP + 1)):
        if ok:
            if start < 0:
                start = i
            gap = 0
            last = i
        elif start >= 0:
            gap += 1
            if gap > GAP:
                spans.append((start, last, sum(flags[start:last + 1])))
                start, gap = -1, 0

    if not spans:
        return '', 0
    a, b, good = max(spans, key=lambda s: s[2])
    if good < 5:
        return '', good
    kept = ', '.join(p.strip(' .;:•|*-') for p in pieces[a:b + 1]
                     if p.strip(' .;:•|*-'))

    # A formula has to contain real chemical names, not merely comma separated
    # phrases of the right shape. Without this the benefits column passes:
    #
    #   "Hydrating, Barrier Repair, Reduces Irritation, Anti-Aging, Brightening"
    #
    # every piece is short and title case, so the shape test accepts them all,
    # and the whole thing would be stored as an ingredient list. Requiring three
    # recognised chemical names rejects it, because it contains none.
    # Count pieces that carry CHEMICAL evidence: either a recognised name, or a
    # chemical word ending such as -ate, -ol, Extract, Oil, Butter.
    #
    # Counting only recognised names was too strict for botanical formulas:
    #   "Glycerin, Niacinamide, Soybean Seed Extract, Barley Extract,
    #    Rice Extract, Sesame Extract"
    # scored 2 and was thrown away, although all six are ingredients.
    #
    # The benefits column still scores 0, because "Hydrating", "Barrier Repair"
    # and "Anti-Aging" are neither recognised names nor chemical endings.
    chem = 0
    for p in pieces[a:b + 1]:
        q = p.strip(' .;:•|*-')
        if not q:
            continue
        if KNOWN.search(q):
            chem += 1
            continue
        lastw = re.sub(r'[^A-Za-z]', '', q.split()[-1]) if q.split() else ''
        if len(lastw) >= 3 and CHEM_END.search(lastw):
            chem += 1
    if chem < 3:
        return '', good

    # benefit vocabulary appearing as whole pieces is another giveaway
    benefity = sum(1 for p in pieces[a:b + 1]
                   if BENEFIT.fullmatch(p.strip(' .;:•|*-')))
    if benefity >= 3:
        return '', good

    return kept[:4000], good


summary = {}
examples = {'trimmed': [], 'emptied': []}

for path in FILES:
    try:
        df = pd.read_csv(path, dtype=str, low_memory=False).fillna('')
    except FileNotFoundError:
        continue
    if 'ingredients' not in df.columns:
        continue

    # Keep the text exactly as it was scraped, once, in its own column.
    #
    # Without this, every improvement to the rules meant restoring from a
    # progress file and re-reading thousands of shop pages, because validation
    # overwrites the thing it is judging. With it, validation always reads the
    # untouched text and rewrites the clean column, so the rules can be changed
    # and re-run as often as needed and nothing is ever lost.
    if 'ingredients_raw' not in df.columns:
        df['ingredients_raw'] = df['ingredients']
        print(f'  {path}: saved the original text into ingredients_raw '
              f'({int((df["ingredients_raw"] != "").sum()):,} lists)')
    else:
        # anything scraped since the last run has no raw copy yet
        fresh = (df['ingredients_raw'] == '') & (df['ingredients'] != '')
        if int(fresh.sum()):
            df.loc[fresh, 'ingredients_raw'] = df.loc[fresh, 'ingredients']
            print(f'  {path}: {int(fresh.sum()):,} newly scraped lists added to '
                  f'ingredients_raw')

    had = int((df['ingredients_raw'] != '').sum())
    kept = trimmed = emptied = 0
    for i in df.index:
        t = str(df.at[i, 'ingredients_raw'])     # always judge the original
        if not t:
            continue
        new, n_run = longest_run(t)
        if not new:
            emptied += 1
            if len(examples['emptied']) < 6:
                examples['emptied'].append((df.at[i, 'brand'][:16], t[:88]))
            if not REPORT_ONLY:
                df.at[i, 'ingredients'] = ''
                if 'ingredient_rule' in df.columns:
                    df.at[i, 'ingredient_rule'] = 'rejected, not a formula'
        elif len(new) < len(t) - 8:
            trimmed += 1
            if len(examples['trimmed']) < 6:
                examples['trimmed'].append((df.at[i, 'brand'][:16], t[:60], new[:60]))
            if not REPORT_ONLY:
                df.at[i, 'ingredients'] = new
        else:
            kept += 1
    if not REPORT_ONLY:
        df.to_csv(path, index=False)
    now = int((df['ingredients'] != '').sum())
    summary[path] = (had, kept, trimmed, emptied, now, len(df))

print('=' * 66)
print('  INGREDIENT LISTS CHECKED' + ('   (report only, nothing changed)'
                                      if REPORT_ONLY else ''))
print('=' * 66)
for path, (had, kept, trimmed, emptied, now, total) in summary.items():
    print(f'\n  {path}')
    print(f'    lists stored before     {had:6,}')
    print(f'      already clean         {kept:6,}')
    print(f'      trimmed to the formula{trimmed:6,}')
    print(f'      emptied, not a formula{emptied:6,}')
    print(f'    lists now               {now:6,}  ({100*now/total:.1f}% of {total:,})')

if examples['trimmed']:
    print('\n  TRIMMED, the junk was removed and the formula kept')
    for b, old, new in examples['trimmed']:
        print(f'    {b}')
        print(f'       was: {old}...')
        print(f'       now: {new}...')
if examples['emptied']:
    print('\n  EMPTIED, there was no formula in these at all')
    for b, old in examples['emptied']:
        print(f'    {b:16s} {old}...')

print('\n  a description stored as a formula would have produced three more')
print('  wrong columns, because key_ingredients, free_from and benefits are')
print('  all computed from this one. an empty cell produces nothing.')
if REPORT_ONLY:
    print('\n  run without --report-only to apply')
else:
    print('\nnow run:  py derive_from_ingredients.py')
