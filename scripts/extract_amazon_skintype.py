"""
Extract manufacturer-declared skin type from the amazon 2023 metadata

Why this exists
  My skin_type column is DERIVED from ingredients and effect tags. That is
  defensible (Lee et al. 2024 derive efficacy from composition) but it is my
  own rule, so I need independent evidence to test it against.

  Amazon's product metadata carries a manufacturer-DECLARED field:
        details["Skin Type"]  ->  "Dry", "Sensitive", "Oily, Combination", ...
  Measured on my own matched ASINs: 29.8% of them have it.

  Crucially this needs NO new matching and NO scraping. I already matched every
  product to an Amazon ASIN when I imported reviews - I simply never extracted
  this field, because at the time I only wanted the reviews.

        my product --match--> ASIN ---> reviews        (already done)
                                   \--> details["Skin Type"]   (this script)

What it produces
  amazon_skintype.csv          asin -> declared skin type, raw + parsed flags
  amazon_skintype_report.txt   coverage and agreement with my derived labels
"""
import json, re, time
import pandas as pd

META  = '../amazon_2023/meta_Beauty_and_Personal_Care.jsonl/meta_Beauty_and_Personal_Care.jsonl'
ASINS = 'amazon_products19k.jsonl'      # the ASINs I already matched
MINE  = 'Skincare_Reviewed_FINAL_v5.csv'

# ---------------------------------------------------------------- parse values
# Amazon's field is free text written by sellers, so it has to be normalised.
# Real values seen in the data: "All", "Dry", "Sensitive", "Oily, Combination,
# Dry, Normal", "Dry,Sensitive", "Acne Prone Skin", "Sensitive,All Skin Types".
ALL_WORDS = ('all', 'all skin types', 'all skin type', 'universal', 'any')

def parse_skin_type(raw):
    """Turn Amazon's free text into the same five flags I use everywhere."""
    s = str(raw).lower()
    parts = [p.strip() for p in re.split(r'[,/;&]| and ', s) if p.strip()]
    f = dict(normal=0, dry=0, oily=0, combination=0, sensitive=0)
    for p in parts:
        if any(p == w or p.startswith(w) for w in ALL_WORDS):
            for k in f: f[k] = 1                    # "All" means every type
            continue
        if 'dry' in p:                      f['dry'] = 1
        if 'oil' in p:                      f['oily'] = 1
        if 'combination' in p or 'combo' in p: f['combination'] = 1
        if 'sensitive' in p:                f['sensitive'] = 1
        if 'normal' in p:                   f['normal'] = 1
        # acne-prone is closest to oily in my scheme; recorded, not invented
        if 'acne' in p:                     f['oily'] = 1
    return f


def main():
    t0 = time.perf_counter()

    # ---- 1. the ASINs I already matched --------------------------------
    asins = set()
    with open(ASINS) as fh:
        for line in fh:
            asins.add(json.loads(line)['asin'])
    print(f'ASINs I already matched to my products : {len(asins):,}')

    # ---- 2. ONE pass over the 2.8 GB metadata --------------------------
    print('scanning the Amazon metadata (2.8 GB, one pass)...')
    rows, seen, n = [], 0, 0
    with open(META) as fh:
        for line in fh:
            n += 1
            if n % 500_000 == 0:
                print(f'   {n:,} products read, {seen:,} of mine found')
            # cheap pre-filter before the expensive json.loads
            if '"Skin Type"' not in line:
                continue
            d = json.loads(line)
            a = d.get('parent_asin') or d.get('asin')
            if a not in asins:
                continue
            st = (d.get('details') or {}).get('Skin Type')
            if not st:
                continue
            seen += 1
            f = parse_skin_type(st)
            rows.append(dict(asin=a, amazon_skin_type_raw=str(st)[:120],
                             amz_normal=f['normal'], amz_dry=f['dry'],
                             amz_oily=f['oily'], amz_combination=f['combination'],
                             amz_sensitive=f['sensitive']))
    out = pd.DataFrame(rows).drop_duplicates('asin')
    out.to_csv('amazon_skintype.csv', index=False)
    secs = time.perf_counter() - t0
    print(f'\nread {n:,} Amazon products in {secs/60:.1f} min')
    print(f'declared Skin Type found for {len(out):,} of my matched ASINs')

    # ---- 3. report -----------------------------------------------------
    lines = []
    def say(s=''):
        print(s); lines.append(str(s))
    say('=' * 62)
    say('AMAZON DECLARED SKIN TYPE - EXTRACTION REPORT')
    say('=' * 62)
    say(f'Amazon products scanned         : {n:,}')
    say(f'My matched ASINs                : {len(asins):,}')
    say(f'Of those, with a declared value : {len(out):,} ({100*len(out)/len(asins):.1f}%)')
    say(f'Runtime                         : {secs/60:.1f} minutes')
    say()
    say('Most common declared values:')
    for v, c in out['amazon_skin_type_raw'].value_counts().head(12).items():
        say(f'   {c:6,}  {v}')
    say()
    say('Parsed into my five flags:')
    for c in ['amz_normal','amz_dry','amz_oily','amz_combination','amz_sensitive']:
        say(f'   {c:18s} {out[c].sum():6,}  ({100*out[c].mean():.1f}% of the labelled)')

    with open('amazon_skintype_report.txt','w') as fh:
        fh.write('\n'.join(lines))
    print('\nwrote amazon_skintype.csv and amazon_skintype_report.txt')
    print('NEXT: join on asin to compare against my derived skin_type columns.')


if __name__ == '__main__':
    main()
