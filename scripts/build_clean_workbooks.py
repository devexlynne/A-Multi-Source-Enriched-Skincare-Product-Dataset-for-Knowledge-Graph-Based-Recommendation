"""
Build the two datasets as clean Excel files. One sheet each, essential columns only.

  DATASET_A_mixed_sources.xlsx   skin type from the best available source per product
  DATASET_B_skincarisma.xlsx     skin type from SkinCarisma for every product

Same 7,569 products and same columns in both. The ONLY difference is where
skin_type / sensitivity / skin_type_source come from, so the two files can be
compared directly.
"""
import pandas as pd
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

# the columns that belong in the deliverable, in reading order
KEEP = [
    'product_id', 'brand', 'name', 'product_type', 'country',
    'skin_type', 'sensitivity', 'skin_type_source',
    'ingredients', 'ingredient_count', 'key_ingredients', 'free_from', 'spf',
    'benefits', 'concerns',
    'rating', 'review_count', 'review_source', 'review_texts_json',
    'product_summary', 'skinsort_url',
]
WIDTH = {'product_id': 11, 'brand': 20, 'name': 42, 'product_type': 20, 'country': 16,
         'skin_type': 14, 'sensitivity': 13, 'skin_type_source': 26,
         'ingredients': 60, 'ingredient_count': 9, 'key_ingredients': 34,
         'free_from': 26, 'spf': 7, 'benefits': 44, 'concerns': 34,
         'rating': 8, 'review_count': 10, 'review_source': 14,
         'review_texts_json': 46, 'product_summary': 46, 'skinsort_url': 40}


def build(src, out, title):
    df = pd.read_csv(src, low_memory=False, dtype=str)
    df = df[[c for c in KEEP if c in df.columns]].fillna('')
    # keep the review text readable rather than a wall of JSON
    if 'review_texts_json' in df.columns:
        df['review_texts_json'] = df['review_texts_json'].str.slice(0, 2000)

    with pd.ExcelWriter(out, engine='openpyxl') as w:
        df.to_excel(w, sheet_name='Dataset', index=False)
        ws = w.sheets['Dataset']
        for c in ws[1]:
            c.fill = PatternFill('solid', fgColor='584A7A')
            c.font = Font(bold=True, color='FFFFFF', size=10)
            c.alignment = Alignment(vertical='center', horizontal='left')
        ws.row_dimensions[1].height = 22
        ws.freeze_panes = 'D2'
        ws.auto_filter.ref = ws.dimensions
        for i, col in enumerate(df.columns, 1):
            ws.column_dimensions[get_column_letter(i)].width = WIDTH.get(col, 16)

    n = len(df)
    seb = df['skin_type'].ne('').sum()
    sen = df['sensitivity'].ne('').sum()
    print(f'{out}')
    print(f'   {n:,} rows x {df.shape[1]} columns   |   {title}')
    print(f'   skin_type filled   {seb:,} ({100*seb/n:.1f}%)')
    print(f'   sensitivity filled {sen:,} ({100*sen/n:.1f}%)\n')


build('OPTION_A_mixed_sources.csv', 'DATASET_A_mixed_sources.xlsx',
      'skin type from the best available source per product')
build('OPTION_B_single_source.csv', 'DATASET_B_skincarisma.xlsx',
      'skin type from SkinCarisma only')
