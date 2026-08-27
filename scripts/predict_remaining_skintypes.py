"""
Fill the last 10% by learning from the labelled 90%

The situation
  766 products have no skin type from any source. 764 of them (99.7%) DO have
  a full INCI ingredient list. And 6,796 products already carry a skin type
  from Amazon or SkinCarisma - and they have ingredients too.

  So I have a labelled training set and an unlabelled set with the same
  features. This is a supervised learning problem, not a scraping problem.

Usage:
    py predict_remaining_skintypes.py     -> Skincare_Reviewed_FINAL_v11.csv
"""
import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

SRC   = 'Skincare_Reviewed_FINAL_v10.csv'
OUT   = 'Skincare_Reviewed_FINAL_v11.csv'
FLAGS = ['skin_dry', 'skin_oily', 'skin_sensitive', 'skin_combination', 'skin_normal']

df = pd.read_csv(SRC, low_memory=False, dtype=str)
print(f'read {len(df):,} products')


def usable(s):
    s = str(s).strip()
    return s and s.lower() != 'nan' and s != 'Not available'


has_ing   = df['ingredients'].map(usable)
labelled  = df['skin_type_source'].ne('not declared') & has_ing
unlabelled = df['skin_type_source'].eq('not declared') & has_ing
print(f'training set (labelled + ingredients): {labelled.sum():,}')
print(f'to predict   (unlabelled + ingredients): {unlabelled.sum():,}')

# ---- features: the ingredient list treated as a bag of ingredient names -----
# Each INCI name is one token. Ingredient ORDER matters in INCI (it reflects
# concentration), so I also weight the first 10 ingredients more heavily by
# repeating them - a simple stand-in for the sequence model Lee et al. use.
def featurise(s):
    toks = [re.sub(r'[^a-z0-9]+', '_', t.strip().lower())
            for t in str(s).split(',') if t.strip()]
    return ' '.join(toks + toks[:10])          # first 10 counted twice

X_text = df.loc[has_ing, 'ingredients'].map(featurise)
vec = TfidfVectorizer(min_df=3, max_features=20000, token_pattern=r'\S+')
vec.fit(X_text)

Xtr_all = vec.transform(df.loc[labelled, 'ingredients'].map(featurise))
Xun     = vec.transform(df.loc[unlabelled, 'ingredients'].map(featurise))
print(f'features (distinct ingredients): {len(vec.vocabulary_):,}')

# ---- train one classifier per skin type, and evaluate it honestly ----------
print('\n' + '=' * 72)
print('HELD-OUT EVALUATION  (20% the model never sees while training)')
print('=' * 72)
print(f"{'skin type':14s}{'accuracy':>10s}{'precision':>11s}{'recall':>9s}{'F1':>8s}{'n pos':>8s}")

models, report = {}, []
for f in FLAGS:
    y = (df.loc[labelled, f].astype(str) == '1').astype(int).values
    if y.sum() < 30 or y.sum() == len(y):
        print(f'{f:14s}  skipped (not enough variation)')
        continue
    Xa, Xb, ya, yb = train_test_split(Xtr_all, y, test_size=0.2,
                                      random_state=42, stratify=y)
    m = LogisticRegression(max_iter=2000, class_weight='balanced', C=1.0)
    m.fit(Xa, ya)
    p = m.predict(Xb)
    acc, pre = accuracy_score(yb, p), precision_score(yb, p, zero_division=0)
    rec, f1  = recall_score(yb, p, zero_division=0), f1_score(yb, p, zero_division=0)
    print(f'{f:14s}{acc:9.1%}{pre:11.1%}{rec:9.1%}{f1:8.1%}{int(y.sum()):8,}')
    report.append(dict(skin_type=f, accuracy=round(acc, 3), precision=round(pre, 3),
                       recall=round(rec, 3), f1=round(f1, 3), positives=int(y.sum())))
    # refit on ALL the labelled data for the real predictions
    m_full = LogisticRegression(max_iter=2000, class_weight='balanced', C=1.0)
    m_full.fit(Xtr_all, y)
    models[f] = m_full

pd.DataFrame(report).to_csv('model_evaluation.csv', index=False)

# ---- the ingredients driving each call, so the model is inspectable --------
print('\ntop ingredients the model uses for each skin type:')
inv = {v: k for k, v in vec.vocabulary_.items()}
for f, m in models.items():
    w = m.coef_[0]
    top = [inv[i].replace('_', ' ') for i in np.argsort(w)[-6:][::-1]]
    print(f'  {f:16s} {", ".join(top)}')

# ---- predict the unlabelled ------------------------------------------------
idx = df.index[unlabelled]
for f, m in models.items():
    df.loc[idx, f] = pd.Series(m.predict(Xun), index=idx).astype(str)

def sebum(r):
    d, o = str(r['skin_dry']) == '1', str(r['skin_oily']) == '1'
    return 'Combination' if (d and o) else 'Oily' if o else 'Dry' if d else (
        'Normal' if str(r['skin_normal']) == '1' else '')

df.loc[idx, 'skin_type']        = df.loc[idx].apply(sebum, axis=1)
df.loc[idx, 'sensitivity']      = np.where(df.loc[idx, 'skin_sensitive'] == '1',
                                           'Sensitive', 'Resistant')
df.loc[idx, 'skin_type_source'] = 'predicted:model'

df.to_csv(OUT, index=False)

n = len(df)
print('\n' + '=' * 72)
print('FINAL COVERAGE')
print('=' * 72)
for s, c in df['skin_type_source'].value_counts().items():
    print(f'  {s:22s} {c:6,}  ({100*c/n:5.1f}%)')
have = int(df['skin_type_source'].ne('not declared').sum())
print(f'\n  TOTAL {have:,} of {n:,} = {100*have/n:.1f}%')
print(f'\nwrote {OUT}')
print('wrote model_evaluation.csv  (the accuracy table for your thesis)')
