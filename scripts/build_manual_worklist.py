"""
Build a manual worklist for the last 766 products

Why manual
  No remaining database covers these products, and a model gave only 42%
  precision on sensitivity, which is worse than an honest blank. So the last
  gap gets filled by hand, from named sources, and each entry records WHERE it
  came from - the same standard as every other value in the dataset.

What this produces
  Skin_Type_Worklist.xlsx, sorted so the work is as fast as possible:
    - grouped by BRAND, because once you have a brand's site open you can do
      all its products in one go (27 TONYMOLY, 27 La Roche-Posay, and so on)
    - ready-made search links per product for the manufacturer, Google,
      SkinCarisma, INCIDecoder and Amazon - one click each, no typing
    - empty columns to fill: skin_type, sensitivity, source, source_url
    - a reference sheet with the exact rules so labelling stays consistent

  Fill it in Excel, save, then run  merge_manual_worklist.py  to fold it back.

How long it really takes
  766 products, but only ~180 brands. Working brand by brand, most products
  take under 20 seconds once the brand's page is open. Budget 3-5 hours, and
  it is fully resumable - do 50 a day and merge whenever you like.

TIP: do the top 20 brands first. They cover roughly a third of the list.
"""
import urllib.parse as up
import pandas as pd

SRC = 'Skincare_Reviewed_FINAL_v10.csv'
OUT = 'Skin_Type_Worklist.xlsx'

df = pd.read_csv(SRC, low_memory=False, dtype=str)
todo = df[df['skin_type_source'] == 'not declared'].copy()
print(f'products needing a manual skin type: {len(todo):,}')
print(f'distinct brands: {todo["brand"].nunique():,}')


def q(*parts):
    return up.quote_plus(' '.join(str(p) for p in parts if p and str(p) != 'nan'))


rows = []
for _, p in todo.iterrows():
    brand, name = p['brand'], p['name']
    rows.append({
        'product_id': p['product_id'],
        'brand': brand,
        'product_name': name,
        'product_type': p.get('product_type', ''),
        # ---- YOU FILL THESE FOUR ----
        'skin_type': '',            # Dry | Normal | Oily | Combination
        'sensitivity': '',          # Sensitive | Resistant
        'source': '',               # e.g. manufacturer / sephora / ulta / incidecoder
        'source_url': '',           # paste the page you took it from
        # ---- one-click lookups ----
        'search_manufacturer': f'https://www.google.com/search?q={q(brand, name, "official site skin type")}',
        'search_google':       f'https://www.google.com/search?q={q(brand, name, "skin type suitable for")}',
        'search_skincarisma':  f'https://www.skincarisma.com/search?q={q(brand, name)}',
        'search_incidecoder':  f'https://incidecoder.com/search?query={q(brand, name)}',
        'search_amazon':       f'https://www.amazon.com/s?k={q(brand, name)}',
        'skinsort_page':       p.get('skinsort_url', ''),
    })

work = pd.DataFrame(rows)
# brand groups first (most products), so the biggest wins come first
order = work['brand'].map(work['brand'].value_counts())
work = work.assign(_n=order).sort_values(['_n', 'brand', 'product_name'],
                                         ascending=[False, True, True]).drop(columns='_n')

brands = (work['brand'].value_counts().rename_axis('brand')
          .reset_index(name='products_to_do'))
brands['cumulative'] = brands['products_to_do'].cumsum()
brands['share_done'] = (100 * brands['cumulative'] / len(work)).round(1)

rules = pd.DataFrame([
 ['skin_type', 'Dry | Normal | Oily | Combination',
  'The sebum axis. Combination = suits both dry and oily areas. Leave blank if the source says nothing about oiliness.'],
 ['sensitivity', 'Sensitive | Resistant',
  'A SEPARATE axis (Baumann). Sensitive = the source says suitable for/targeted at sensitive skin. Resistant = the source addresses skin type but does not mention sensitivity. Blank = unknown.'],
 ['source', 'manufacturer | sephora | ulta | incidecoder | skincarisma | other',
  'Where you actually read it. "manufacturer" is the strongest.'],
 ['source_url', 'paste the link', 'So any label can be checked later. This is what makes it auditable.'],
 ['', '', ''],
 ['IF THE SOURCE SAYS "all skin types"', 'skin_type = Normal, sensitivity = Resistant',
  'It is a real statement of universal suitability, not a blank.'],
 ['IF YOU CANNOT FIND ANYTHING', 'leave the row blank',
  'A blank is an honest result. Do not guess - an unfounded label is worse than a gap.'],
], columns=['field', 'allowed values', 'rule'])

with pd.ExcelWriter(OUT, engine='openpyxl') as w:
    work.to_excel(w, sheet_name='Worklist', index=False)
    brands.to_excel(w, sheet_name='Brands by size', index=False)
    rules.to_excel(w, sheet_name='How to fill it', index=False)
    from openpyxl.styles import Font, PatternFill, Alignment
    ws = w.sheets['Worklist']
    fills = {'A': '584A7A', 'B': '584A7A', 'C': '584A7A', 'D': '584A7A',
             'E': 'C0703E', 'F': 'C0703E', 'G': 'C0703E', 'H': 'C0703E'}
    for c in ws[1]:
        c.fill = PatternFill('solid', fgColor=fills.get(c.column_letter, '6F9C78'))
        c.font = Font(bold=True, color='FFFFFF')
        c.alignment = Alignment(vertical='center', wrap_text=True)
    widths = {'A': 11, 'B': 20, 'C': 46, 'D': 18, 'E': 14, 'F': 13, 'G': 15,
              'H': 30, 'I': 16, 'J': 16, 'K': 16, 'L': 16, 'M': 16, 'N': 16}
    for col, wd in widths.items():
        ws.column_dimensions[col].width = wd
    ws.freeze_panes = 'C2'
    for name in ('Brands by size', 'How to fill it'):
        s = w.sheets[name]
        for c in s[1]:
            c.fill = PatternFill('solid', fgColor='584A7A')
            c.font = Font(bold=True, color='FFFFFF')
        for col in s.columns:
            L = max((len(str(x.value)) for x in col[:40] if x.value), default=12)
            s.column_dimensions[col[0].column_letter].width = min(max(L + 2, 14), 70)

print(f'wrote {OUT}')
print('\nthe 15 brands worth doing first:')
print(brands.head(15).to_string(index=False))
print(f'\ndoing just those {int(brands.head(15)["products_to_do"].sum())} products '
      f'covers {brands.head(15)["share_done"].iloc[-1]}% of the list')
