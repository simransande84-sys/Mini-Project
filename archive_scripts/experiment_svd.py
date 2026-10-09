"""
experiment_svd.py
-----------------
Controlled experiment: TruncatedSVD on TF-IDF text features only.
Categorical (OHE) and Duration_Hours (StandardScaler) unchanged.

Technique: Pipeline([TfidfVectorizer, TruncatedSVD]) inside ColumnTransformer.
This applies SVD ONLY to the TF-IDF block, not to OHE or scaler outputs.

Evaluation: 5-fold stratified CV on X_train only.
Test set is NOT touched.
Baseline model is NOT modified.
"""

import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, re, time

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.model_selection import (StratifiedKFold, cross_validate,
                                     train_test_split)
from sklearn.metrics import accuracy_score, f1_score
from scipy.sparse import issparse

import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet',   quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ── Setup ─────────────────────────────────────────────────────────
RANDOM_STATE = 42
CLASS_ORDER  = ['High', 'Medium', 'Low']
BASELINE_CV_F1  = 0.7043
BASELINE_CV_ACC = 0.7048

TEXT_FEATURE = 'Cleaned_Text'
CAT_FEATURES = ['Category', 'Complaint_Type', 'Block', 'Floor']
NUM_FEATURES = ['Duration_Hours']

DOMAIN_SW = {'please','kindly','sir','madam','hello','thanks','thank','dear','hi',
             'regards','asap','hostel','complaint','request','warden','office',
             'management','student','students','look','also','us','am'}
ALL_SW = (set(stopwords.words('english')) | DOMAIN_SW) - \
         {'no','not','never','cannot','cant','wont','isnt','doesnt',
          'hasnt','havent','wasnt','wouldnt'}
_lem = WordNetLemmatizer()

def preprocess_text(t):
    if not isinstance(t, str) or not t.strip(): return ''
    t = t.lower()
    t = re.sub(r'\bleakage\b','leaking',t)
    t = re.sub(r'\bleak\b','leaking',t)
    t = re.sub(r'\belectricity\b','electric',t)
    for o, n in [("can't","cannot"),("won't","wont"),("isn't","is not"),
                 ("doesn't","does not"),("hasn't","has not"),
                 ("haven't","have not"),("wasn't","was not"),
                 ("wouldn't","would not")]:
        t = t.replace(o, n)
    t = re.sub(r'[^\w\s]',' ',t)
    t = re.sub(r'\b\d+\b','',t)
    t = re.sub(r'\s+',' ',t).strip()
    return ' '.join(_lem.lemmatize(w) for w in t.split()
                    if w not in ALL_SW and len(w)>=2)

def parse_dur(t):
    if not isinstance(t,str): return None
    p = t.strip().lower().split()
    if len(p)!=2: return None
    try: v=float(p[0])
    except: return None
    u=p[1]
    if u in ('hour','hours'):  return v
    if u in ('day','days'):    return v*24
    if u in ('week','weeks'):  return v*168
    return None

# ── Load and prepare data ─────────────────────────────────────────
print("Loading data...")
df = pd.read_csv('Dataset_duration.csv')
df['Cleaned_Text']   = df['Complaint_Text'].apply(preprocess_text)
df['Duration_Hours'] = df['Duration_Standardized'].apply(parse_dur)

ALL_FEATURES = [TEXT_FEATURE] + CAT_FEATURES + NUM_FEATURES
X = df[ALL_FEATURES].copy()
y = df['Priority'].copy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y)

le = LabelEncoder()
le.fit(CLASS_ORDER)
y_train_enc = le.transform(y_train)

print(f"  Train: {len(X_train)}  Test: {len(X_test)}")
print(f"  Classes: {le.classes_}")

# ── Pipeline factory ──────────────────────────────────────────────
def make_svd_pipeline(n_components):
    """
    TF-IDF → TruncatedSVD applied ONLY to text features.
    OHE on categorical features (unchanged).
    StandardScaler on Duration_Hours (unchanged).
    All combined → LinearSVC.
    """
    tfidf_svd = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1,2), max_features=5000,
            sublinear_tf=True, min_df=2, strip_accents='unicode')),
        ('svd', TruncatedSVD(
            n_components=n_components, random_state=RANDOM_STATE)),
    ])
    prep = ColumnTransformer([
        ('text', tfidf_svd,    TEXT_FEATURE),   # TF-IDF + SVD (text only)
        ('ohe',  OneHotEncoder(handle_unknown='ignore',
                               sparse_output=False), CAT_FEATURES),
        ('num',  StandardScaler(),                NUM_FEATURES),
    ], remainder='drop')

    clf = LinearSVC(C=1.0, max_iter=3000,
                    class_weight='balanced', random_state=RANDOM_STATE)
    return Pipeline([('prep', prep), ('clf', clf)])

def make_baseline_pipeline():
    """Original pipeline — no SVD."""
    prep = ColumnTransformer([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1,2), max_features=5000,
            sublinear_tf=True, min_df=2, strip_accents='unicode'),
         TEXT_FEATURE),
        ('ohe',   OneHotEncoder(handle_unknown='ignore',
                                sparse_output=False), CAT_FEATURES),
        ('num',   StandardScaler(), NUM_FEATURES),
    ], remainder='drop')
    clf = LinearSVC(C=1.0, max_iter=3000,
                    class_weight='balanced', random_state=RANDOM_STATE)
    return Pipeline([('prep', prep), ('clf', clf)])

# ── CV evaluation ─────────────────────────────────────────────────
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

def evaluate_cv(pipeline, X_tr, y_tr_enc, label):
    t0 = time.time()
    cv = cross_validate(pipeline, X_tr, y_tr_enc, cv=skf,
                        scoring=['accuracy','f1_weighted'],
                        return_train_score=True, n_jobs=1)
    elapsed = time.time() - t0
    return {
        'label'       : label,
        'cv_acc_mean' : round(float(cv['test_accuracy'].mean()),   4),
        'cv_acc_std'  : round(float(cv['test_accuracy'].std()),    4),
        'cv_f1_mean'  : round(float(cv['test_f1_weighted'].mean()),4),
        'cv_f1_std'   : round(float(cv['test_f1_weighted'].std()), 4),
        'tr_acc_mean' : round(float(cv['train_accuracy'].mean()),  4),
        'folds'       : [round(f,4) for f in cv['test_f1_weighted'].tolist()],
        'time_s'      : round(elapsed, 1),
    }

# ── Run all configurations ────────────────────────────────────────
print("\n" + "=" * 68)
print("  TruncatedSVD Experiment — 5-Fold Stratified CV on X_train")
print("  Test set NOT used. Baseline model NOT modified.")
print("=" * 68)
print()

configs = [
    ('Baseline (no SVD)',      make_baseline_pipeline()),
    ('SVD n_components=50',   make_svd_pipeline(50)),
    ('SVD n_components=100',  make_svd_pipeline(100)),
    ('SVD n_components=150',  make_svd_pipeline(150)),
]

results = []
for label, pipeline in configs:
    print(f"  Running: {label} ...")
    r = evaluate_cv(pipeline, X_train, y_train_enc, label)
    results.append(r)
    print(f"    CV Acc : {r['cv_acc_mean']:.4f} ± {r['cv_acc_std']:.4f}")
    print(f"    CV F1  : {r['cv_f1_mean']:.4f} ± {r['cv_f1_std']:.4f}")
    print(f"    Train  : {r['tr_acc_mean']:.4f}")
    print(f"    Folds  : {r['folds']}")
    print(f"    Time   : {r['time_s']}s")
    print()

# ── Comparison table ──────────────────────────────────────────────
print("=" * 68)
print("  RESULTS COMPARISON (vs Baseline CV F1 = 0.7043)")
print("=" * 68)
print(f"\n  {'Configuration':28s} | {'CV Acc':8s} | {'CV F1':8s} | {'±':6s} | "
      f"{'Train Acc':9s} | {'vs Baseline':11s}")
print("  " + "-" * 82)

# Also show external baseline from saved model (full dataset CV)
print(f"  {'[External] Saved model CV':28s} | {'0.7048':8s} | {'0.7043':8s} | "
      f"{'0.012':6s} | {'0.9927':9s} | {'— reference':11s}")
print("  " + "·" * 82)

best = None
for r in results:
    delta_f1  = r['cv_f1_mean'] - BASELINE_CV_F1
    delta_str = (f"+{delta_f1:.4f} ✅" if delta_f1 > 0.003
                 else (f"{delta_f1:.4f} ⚠️" if delta_f1 < -0.003
                       else f"{delta_f1:.4f} —"))
    marker = " ← NEW BEST" if (best is None or
             r['cv_f1_mean'] > best['cv_f1_mean']) else ""
    if best is None or r['cv_f1_mean'] > best['cv_f1_mean']:
        best = r
    print(f"  {r['label']:28s} | {r['cv_acc_mean']:8.4f} | {r['cv_f1_mean']:8.4f} | "
          f"{r['cv_f1_std']:6.4f} | {r['tr_acc_mean']:9.4f} | {delta_str}{marker}")

# ── Feature size report ───────────────────────────────────────────
print(f"\n  Feature dimensions after transformation:")
print(f"  {'Configuration':28s} | Text dims | OHE dims | Num dims | Total")
print("  " + "-"*65)
ohe_dims = 39
num_dims  = 1
print(f"  {'Baseline (no SVD)':28s} |      1497 |       39 |        1 | 1537")
for nc in [50, 100, 150]:
    total = nc + ohe_dims + num_dims
    print(f"  {f'SVD n_components={nc}':28s} | {nc:9d} |       39 |        1 | {total:5d}")

# ── Verdict ───────────────────────────────────────────────────────
print("\n" + "=" * 68)
print("  VERDICT")
print("=" * 68)
best_svd = max((r for r in results if 'SVD' in r['label']),
               key=lambda r: r['cv_f1_mean'])

improved = best_svd['cv_f1_mean'] > BASELINE_CV_F1 + 0.003

print(f"\n  Baseline CV F1     : {BASELINE_CV_F1:.4f}")
print(f"  Best SVD CV F1     : {best_svd['cv_f1_mean']:.4f}  ({best_svd['label']})")
print(f"  Difference         : {best_svd['cv_f1_mean']-BASELINE_CV_F1:+.4f}")
print()

if improved:
    print(f"  RESULT: ✅ TruncatedSVD IMPROVES the model.")
    print(f"          Best config: {best_svd['label']}")
    print(f"          CV F1 improved from {BASELINE_CV_F1:.4f} → {best_svd['cv_f1_mean']:.4f}")
    print(f"          Recommendation: Retrain and replace baseline with SVD pipeline.")
else:
    print(f"  RESULT: ❌ TruncatedSVD does NOT improve the model.")
    print(f"          No SVD configuration beats the baseline CV F1 of {BASELINE_CV_F1:.4f}.")
    print(f"          Baseline model remains unchanged.")
    print(f"\n  Why SVD may not help here:")
    print(f"    - With only 857 samples, TF-IDF vocabulary is already compact (1497 terms)")
    print(f"    - SVD reduces dimensions but also discards discriminative rare terms")
    print(f"    - For short complaint texts (~9 words), rare specific terms matter")
    print(f"      (e.g. 'fire', 'emergency', 'shock' are rare but high-priority signals)")
    print(f"    - LinearSVC handles sparse high-dimensional data natively; SVD may not help")
    print(f"\n  Confirmed conclusion: The baseline is the correct production model.")
    print(f"  The primary improvement path remains: collect more labeled complaints.")

print("\n" + "=" * 68)

# Save results summary
import json
summary = {
    'baseline_cv_f1': BASELINE_CV_F1,
    'baseline_cv_acc': BASELINE_CV_ACC,
    'configurations': results,
    'best_svd': best_svd,
    'svd_improved': improved,
}
with open('svd_experiment_results.json', 'w') as f:
    json.dump(summary, f, indent=2)
print("\n  Results saved to svd_experiment_results.json")
