"""
Negated claims: find them, and stop trusting them

The bug
  Every wording rule in the pipeline matched a positive phrase and never
  checked whether it was negated. So

      "Not suitable for dry skin"

  contains the substring "suitable for dry skin", the rule fired, and the
  product was recorded as Dry. The stored quote even shows the word "Not",
  which is how this was eventually caught: the evidence was right there in the
  file, contradicting the value next to it.

Usage:
    py fix_negations.py                 apply the corrections
    py fix_negations.py --report-only   list them, change nothing
"""
import re
import sys
import pandas as pd

DATA = 'COMBINED_DATASET.csv'
ALSO = ['SKINCARE_DATASET.csv', 'LEBANESE_RETAIL.csv']
OUT = 'NEGATED_CLAIMS.csv'
REPORT_ONLY = '--report-only' in sys.argv

# A negation attached to the suitability verb ITSELF.
#
# The gap between the negation and the verb is deliberately tiny, and no comma
# or conjunction is allowed inside it. A looser version produced two false
# positives that are worth recording, because both look convincing:
#
#   "leaves skin clean but NOT tight or dry, FORMULATED FOR sensitive skin"
#        the "not" belongs to "tight or dry". the product IS for sensitive skin.
#
#   "AVOID chemical UV filters FOR sensitive skin"
#        advice about an ingredient class, not about this product, which is a
#        mineral sunscreen and therefore is for sensitive skin.
#
# Allowing at most a couple of short words, and no clause boundary, excludes
# both while still catching "not suitable for", "not recommended for" and
# "may not be ideal for".
GAP = r'(?:\s+\w+){0,2}\s*'
NEG = re.compile(
    r'\b(?:not|never|n.t)\b' + GAP +
    r'\b(?:suitable|suited|recommended|recommend|ideal|advisable|advised)\b'
    r'\s*(?:for|on|with)\s*(?:\w+\s+){0,2}?'
    r'(dry|oily|combination|normal|sensitive|acne[- ]prone|all)\s+skin'
    r'|\bnot\b\s+a?\s*good\s+(?:option|choice|idea|fit)?\s*(?:for|on)\s*(?:\w+\s+){0,2}?'
    r'(dry|oily|combination|normal|sensitive|acne[- ]prone|all)\s+skin'
    r'|\bnot\s+good\s+for\s+(?:\w+\s+){0,2}?'
    r'(dry|oily|combination|normal|sensitive|acne[- ]prone|all)\s+skin'
    r'|\b(?:unsuitable|not\s+for)\s+(?:\w+\s+){0,2}?'
    r'(dry|oily|combination|normal|sensitive|all)\s+skin', re.I)

# phrases that contain a negation word but do not negate the claim
FALSE_ALARM = re.compile(
    r'\bnot only\b|\bnot just\b|\bnot merely\b'
    r'|\bnot\s+(?:tight|greasy|sticky|heavy|oily|drying|irritating)\b'
    r'|\bavoid\b', re.I)


def negated_phrase(quote):
    if FALSE_ALARM.search(quote):
        return None
    m = NEG.search(quote)
    if not m:
        return None
    return next((x for x in m.groups() if x), None), m.group(0)


def apply(path, label):
    df = pd.read_csv(path, dtype=str, low_memory=False).fillna('')
    if 'skin_type_quote' not in df.columns:
        return df, []
    rows = []
    for i in df.index:
        q = str(df.at[i, 'skin_type_quote'])
        if not q or not df.at[i, 'skin_type']:
            continue
        got = negated_phrase(q)
        if not got:
            continue
        phrase, frag = got
        p = phrase.lower()
        before_t, before_s = df.at[i, 'skin_type'], df.at[i, 'sensitivity']
        action = ''
        if p.startswith('sensitiv'):
            # a real statement: this product is NOT for sensitive skin
            df.at[i, 'sensitivity'] = 'Resistant'
            action = 'sensitivity set to Resistant'
            if before_t in ('All', ''):
                df.at[i, 'skin_type'] = 'All'
        else:
            # "not for dry skin" does not say which type it IS for
            df.at[i, 'skin_type'] = ''
            df.at[i, 'sensitivity'] = ''
            df.at[i, 'skin_type_status'] = 'searched, not stated'
            action = 'value cleared, the negation does not name a type'
        df.at[i, 'skin_type_rule'] = (str(df.at[i, 'skin_type_rule'])
                                      + ' [NEGATION CORRECTED]').strip()
        rows.append(dict(file=label, product_id=df.at[i, 'product_id'],
                         brand=df.at[i, 'brand'], name=df.at[i, 'name'],
                         negated_phrase=phrase, fragment=frag.strip()[:120],
                         was_skin_type=before_t, was_sensitivity=before_s,
                         now_skin_type=df.at[i, 'skin_type'],
                         now_sensitivity=df.at[i, 'sensitivity'],
                         action=action, source=df.at[i, 'skin_type_source'],
                         url=df.at[i, 'skin_type_url'], quote=q[:220]))
    return df, rows


allrows = []
for path, label in [(DATA, 'COMBINED')] + [(p, p) for p in ALSO]:
    try:
        df, rows = apply(path, label)
    except FileNotFoundError:
        continue
    allrows += rows
    if rows and not REPORT_ONLY:
        df.to_csv(path, index=False)
    print(f'{label:24s} {len(rows):3d} negated claims'
          f'{"  (not written, report only)" if REPORT_ONLY else "  corrected"}')

if not allrows:
    print('\nno negated claims found')
    raise SystemExit

rep = pd.DataFrame(allrows)
rep.to_csv(OUT, index=False)

comb = rep[rep['file'] == 'COMBINED']
print('\n' + '=' * 70)
print('  NEGATED CLAIMS IN THE COMBINED DATASET')
print('=' * 70)
print(f'  found                    {len(comb)}')
print(f'  sensitivity corrected    {int((comb["action"].str.startswith("sensitivity")).sum())}')
print(f'  value cleared            {int((comb["action"].str.startswith("value")).sum())}')
print()
for _, r in comb.iterrows():
    print(f'  {r["product_id"]}  {r["brand"][:20]:20s} {r["name"][:34]:34s}')
    print(f'      "{r["fragment"][:70]}"')
    print(f'      {r["was_skin_type"]}/{r["was_sensitivity"]} '
          f'-> {r["now_skin_type"] or "(cleared)"}/{r["now_sensitivity"] or "(cleared)"}'
          f'   {r["action"]}')
print(f'\n  written to {OUT}, so every correction is checkable')

print('\n  NOTE FOR THE PIPELINE')
print('  the extraction rules still do not test for negation. this script is a')
print('  correction applied afterwards, not a fix to the matching itself. any')
print('  future search pass should be followed by running this again.')
