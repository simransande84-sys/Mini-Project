"""
experiment_xgboost.py
---------------------
Controlled XGBoost experiment vs LinearSVC baseline.
- Same train/test split, same features, same ColumnTransformer
- 5-fold stratified CV on X_train only
- Test set used ONLY for final reporting, NOT for selection
- Production LinearSVC model NOT modified
"""

import warnings; warnings.filterwarnings('ignore')
import numpy as np, pandas as pd, re, time, json

# Check XGBoost is available
try:
    import xgboost as xgb
    print(f"XGBoost version: {xgb.__version__}")
except ImportError:
    print("XGBoost not installed. Installing...")
    import subprocess, sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'xgboost', '-q'])
    import xgboost as xgb
    print(f"XGBoost installed: {xgb.__version__}")

from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.model_selection import (StratifiedKFold, GridSearchCV,
                                     cross_validate, train_test_split)
from sklearn.metrics import accuracy_score, f1_score, classification_report
from scipy.sparse import issparse
from xgboost import XGBClassifier

import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet',   quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ── Constants ──────────────────────────────────────────────────────
RANDOM_STATE = 42
CLASS_ORDER  = ['High', 'Medium', 'Low']
BASELINE = {
    'name'      : 'LinearSVC (C=1.0)',
    'test_acc'  : 0.6628,
    'test_f1'   : 0.6627,
    'cv_acc'    : 0.7048,
    'cv_f1'     : 0.7043,
    'cv_f1_std' : 0.012,
    'train_acc' : 0.9927,
}

TEXT_FEATURE = 'Cleaned_Text'
CAT_FEATURES = ['Category','Complaint_Type','Block','Floor']
NUM_FEATURES = ['Duration_Hours']
ALL_FEATURES = [TEXT_FEATURE] + CAT_FEATURES + NUM_FEATURES

# ── Preprocessing ──────────────────────────────────────────────────
DOMAIN_SW = {'please','kindly','sir','madam','hello','thanks','thank','dear','hi',
             'regards','asap','hostel','complaint','request','warden','office',
             'management','student','students','look','also','us','am'}
ALL_SW = (set(stopwords.words('english')) | DOMAIN_SW) - \
         {'no','not','never','cannot','cant','wont','isnt','doesnt',
          'hasnt','havent','wasnt','wouldnt'}
_lem = WordNetLemmatizer()

def preprocess_text(t):
    if not isinstance(t,str) or not t.strip(): return ''
    t = t.lower()
    t = re.sub(r'\bleakage\b','leaking',t); t = re.sub(r'\bleak\b','leaking',t)
    t = re.sub(r'\belectricity\b','electric',t)
    for o,n in [("can't","cannot"),("won't","wont"),("isn't","is not"),
                ("doesn't","does not"),("hasn't","has not"),
                ("haven't","have not"),("wasn't","was not"),("wouldn't","would not")]:
        t = t.replace(o,n)
    t = re.sub(r'[^\w\s]',' ',t); t = re.sub(r'\b\d+\b','',t)
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

# ── Load and prepare data ──────────────────────────────────────────
print("\nLoading data...")
df = pd.read_csv('Dataset_duration.csv')
df['Cleaned_Text']   = df['Complaint_Text'].apply(preprocess_text)
df['Duration_Hours'] = df['Duration_Standardized'].apply(parse_dur)

X = df[ALL_FEATURES].copy()
y = df['Priority'].copy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y)

le = LabelEncoder()
le.fit(CLASS_ORDER)
y_train_enc = le.transform(y_train)
y_test_enc  = le.transform(y_test)
print(f"  Train: {len(X_train)} | Test: {len(X_test)}")

# ── Fit the same ColumnTransformer (identical to baseline) ─────────
print("  Fitting ColumnTransformer on X_train only (same as baseline)...")
preprocessor = ColumnTransformer([
    ('tfidf', TfidfVectorizer(
        ngram_range=(1,2), max_features=5000,
        sublinear_tf=True, min_df=2, strip_accents='unicode'),
     TEXT_FEATURE),
    ('ohe',   OneHotEncoder(handle_unknown='ignore', sparse_output=False),
     CAT_FEATURES),
    ('num',   StandardScaler(), NUM_FEATURES),
], remainder='drop')

X_train_proc = preprocessor.fit_transform(X_train)
X_test_proc  = preprocessor.transform(X_test)
if issparse(X_train_proc): X_train_proc = X_train_proc.toarray()
if issparse(X_test_proc):  X_test_proc  = X_test_proc.toarray()

print(f"  Feature matrix: X_train={X_train_proc.shape}, X_test={X_test_proc.shape}")

# ── XGBoost — Parameter Grid (training data only) ──────────────────
# Sensible small grid:
#   n_estimators: 100, 200, 300
#   max_depth   : 3, 5
#   learning_rate: 0.05, 0.1, 0.2
#   subsample   : 0.8
#   colsample_bytree: 0.7
# Total: 3 × 2 × 3 = 18 combinations × 5 folds = 90 fits

param_grid = {
    'n_estimators'    : [100, 200, 300],
    'max_depth'       : [3, 5],
    'learning_rate'   : [0.05, 0.1, 0.2],
    'subsample'       : [0.8],
    'colsample_bytree': [0.7],
}
n_combos = 3 * 2 * 3
print(f"\n{'='*68}")
print(f"  XGBoost GridSearchCV — Training Data Only (5-Fold Stratified CV)")
print(f"  Combinations: {n_combos}  |  Folds: 5  |  Total fits: {n_combos*5}")
print(f"  Scoring: f1_weighted")
print(f"{'='*68}\n")

xgb_base = XGBClassifier(
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=RANDOM_STATE,
    n_jobs=1,
    tree_method='hist',      # Fast histogram-based method
    verbosity=0,
)

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)

gs = GridSearchCV(
    xgb_base, param_grid,
    cv=skf, scoring='f1_weighted',
    refit=True, n_jobs=1, verbose=0,
    return_train_score=True,
)

t0 = time.time()
gs.fit(X_train_proc, y_train_enc)
elapsed = time.time() - t0
print(f"  GridSearch complete in {elapsed:.1f}s")

# ── Show all results ───────────────────────────────────────────────
cv_res = gs.cv_results_
idx_sorted = np.argsort(cv_res['mean_test_score'])[::-1]

print(f"\n  Top 10 XGBoost configurations (by CV F1):")
print(f"  {'n_est':>5} | {'depth':>5} | {'lr':>5} | {'sub':>4} | {'CV F1':>7} | {'±':>6}")
print("  " + "-"*50)
for rank, idx in enumerate(idx_sorted[:10]):
    p      = cv_res['params'][idx]
    cv_f1  = cv_res['mean_test_score'][idx]
    cv_std = cv_res['std_test_score'][idx]
    mark   = " ← BEST" if rank==0 else ""
    print(f"  {p['n_estimators']:>5} | {p['max_depth']:>5} | "
          f"{p['learning_rate']:>5} | {p['subsample']:>4} | "
          f"{cv_f1:>7.4f} | {cv_std:>6.4f}{mark}")

# ── Best XGBoost config ────────────────────────────────────────────
best_params  = gs.best_params_
best_cv_f1   = gs.best_score_

# Full CV on best config to get accuracy + std
best_xgb = XGBClassifier(
    **best_params,
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=RANDOM_STATE,
    n_jobs=1, tree_method='hist', verbosity=0,
)
cv_full = cross_validate(best_xgb, X_train_proc, y_train_enc,
                         cv=skf, scoring=['accuracy','f1_weighted'],
                         return_train_score=True, n_jobs=1)

xgb_cv_acc     = round(float(cv_full['test_accuracy'].mean()),     4)
xgb_cv_acc_std = round(float(cv_full['test_accuracy'].std()),      4)
xgb_cv_f1      = round(float(cv_full['test_f1_weighted'].mean()),  4)
xgb_cv_f1_std  = round(float(cv_full['test_f1_weighted'].std()),   4)
xgb_tr_acc     = round(float(cv_full['train_accuracy'].mean()),    4)
folds_f1       = [round(f,4) for f in cv_full['test_f1_weighted'].tolist()]

# ── Evaluate best XGBoost on test set ─────────────────────────────
best_xgb_final = XGBClassifier(
    **best_params,
    use_label_encoder=False,
    eval_metric='mlogloss',
    random_state=RANDOM_STATE,
    n_jobs=1, tree_method='hist', verbosity=0,
)
t0 = time.time()
best_xgb_final.fit(X_train_proc, y_train_enc)
train_time = time.time() - t0

y_pred_test  = best_xgb_final.predict(X_test_proc)
y_pred_train = best_xgb_final.predict(X_train_proc)
xgb_test_acc = round(accuracy_score(y_test_enc,  y_pred_test), 4)
xgb_test_f1  = round(f1_score(y_test_enc,  y_pred_test,  average='weighted'), 4)
xgb_tr_acc_final = round(accuracy_score(y_train_enc, y_pred_train), 4)
xgb_gap      = round(xgb_tr_acc_final - xgb_test_acc, 4)

# ── Classification report ──────────────────────────────────────────
label_names = list(le.classes_)
y_pred_str  = le.inverse_transform(y_pred_test)
y_true_str  = list(y_test)

print(f"\n{'='*68}")
print(f"  BEST XGBOOST — FULL EVALUATION RESULTS")
print(f"{'='*68}")
print(f"\n  Best parameters:")
for k,v in best_params.items():
    print(f"    {k:20s}: {v}")
print(f"\n  CV Results (on X_train, 5-fold):")
print(f"    CV Accuracy : {xgb_cv_acc:.4f} ± {xgb_cv_acc_std:.4f}")
print(f"    CV F1 (wt)  : {xgb_cv_f1:.4f} ± {xgb_cv_f1_std:.4f}")
print(f"    Train Acc   : {xgb_tr_acc:.4f}")
print(f"    Per-fold F1 : {folds_f1}")

print(f"\n  Test Set Results (first time seeing test data):")
print(f"    Test Accuracy : {xgb_test_acc:.4f}")
print(f"    Test F1 (wt)  : {xgb_test_f1:.4f}")
print(f"    Train Acc     : {xgb_tr_acc_final:.4f}")
print(f"    Train-Test Gap: {xgb_gap:.4f}")
print(f"    Training time : {train_time:.2f}s")

print(f"\n  Classification Report (Test Set):")
print(classification_report(y_true_str, y_pred_str,
                             labels=CLASS_ORDER, target_names=CLASS_ORDER))

# ── Final comparison ───────────────────────────────────────────────
print(f"\n{'='*68}")
print(f"  XGBOOST vs LINEARSVC — FINAL COMPARISON")
print(f"{'='*68}")
print(f"\n  {'Metric':22s} | {'LinearSVC':12s} | {'XGBoost':12s} | {'Change':10s}")
print(f"  {'-'*64}")

comparison = [
    ('Test Accuracy',   BASELINE['test_acc'],  xgb_test_acc),
    ('Test F1 (wt)',    BASELINE['test_f1'],   xgb_test_f1),
    ('CV Accuracy',     BASELINE['cv_acc'],    xgb_cv_acc),
    ('CV F1 (wt)',      BASELINE['cv_f1'],     xgb_cv_f1),
    ('Train Accuracy',  BASELINE['train_acc'], xgb_tr_acc_final),
    ('Train-Test Gap',  BASELINE['cv_f1']-BASELINE['test_f1'],  xgb_gap),
]
for name, base_v, xgb_v in comparison:
    delta = xgb_v - base_v
    if name == 'Train-Test Gap':
        arrow = '✅ Better' if delta < -0.01 else ('⚠️ Worse' if delta > 0.01 else '— Same')
    else:
        arrow = '✅ Better' if delta > 0.003 else ('⚠️ Worse' if delta < -0.003 else '— Same')
    print(f"  {name:22s} | {base_v:12.4f} | {xgb_v:12.4f} | {arrow}")

# ── Verdict ────────────────────────────────────────────────────────
improved_cv  = xgb_cv_f1  > BASELINE['cv_f1']  + 0.003
improved_test= xgb_test_f1> BASELINE['test_f1'] + 0.003

print(f"\n{'='*68}")
print(f"  VERDICT")
print(f"{'='*68}")
print(f"\n  Baseline CV F1   : {BASELINE['cv_f1']:.4f}")
print(f"  XGBoost CV F1    : {xgb_cv_f1:.4f}")
print(f"  Baseline Test F1 : {BASELINE['test_f1']:.4f}")
print(f"  XGBoost Test F1  : {xgb_test_f1:.4f}")
print()
if improved_cv and improved_test:
    print("  RESULT: ✅ XGBoost OUTPERFORMS LinearSVC on BOTH CV and Test.")
    print("          Awaiting instructions to replace production model.")
elif improved_cv and not improved_test:
    print("  RESULT: ⚠️  XGBoost has better CV but not better Test F1.")
    print("          The CV gain may not be reliable. LinearSVC retained.")
elif not improved_cv and improved_test:
    print("  RESULT: ⚠️  XGBoost has better Test but not better CV F1.")
    print("          Test improvement may be coincidental. LinearSVC retained.")
else:
    print("  RESULT: ❌ XGBoost does NOT outperform LinearSVC.")
    print("          LinearSVC baseline is confirmed superior.")
    print("          Production model unchanged.")

print(f"\n  Note: The saved LinearSVC production model has NOT been modified.")
print(f"        All XGBoost results are experimental only.")
print(f"{'='*68}")

# Save results
results = {
    'experiment'     : 'XGBoost vs LinearSVC',
    'baseline'       : BASELINE,
    'xgboost_params' : best_params,
    'xgboost_cv_acc' : xgb_cv_acc, 'xgboost_cv_f1': xgb_cv_f1,
    'xgboost_cv_f1_std': xgb_cv_f1_std,
    'xgboost_test_acc': xgb_test_acc, 'xgboost_test_f1': xgb_test_f1,
    'xgboost_train_acc': xgb_tr_acc_final,
    'xgboost_gap'    : xgb_gap,
    'improved_cv'    : improved_cv,
    'improved_test'  : improved_test,
    'verdict'        : 'IMPROVED' if (improved_cv and improved_test) else 'BASELINE_RETAINED',
}
with open('xgboost_experiment_results.json','w') as f:
    json.dump(results, f, indent=2)
print("\n  Results saved to xgboost_experiment_results.json")
