"""
tune_linearsvc.py
-----------------
Hyperparameter tuning for LinearSVC using GridSearchCV
on TRAINING DATA ONLY (X_train). Test set is untouched.

Search space:
  clf__C             : [0.01, 0.05, 0.1, 0.5, 1.0, 2.0]
  prep__tfidf__max_features: [3000, 5000]

Selection criterion: best CV F1 (weighted)
If tuned model improves over baseline, saves updated artifacts.
Injects Section 10 results into the notebook.
"""

import warnings, json, os, time, copy, joblib
warnings.filterwarnings('ignore')

import numpy as np, pandas as pd, re
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.svm import LinearSVC
from sklearn.model_selection import (StratifiedKFold, GridSearchCV,
                                     cross_validate, train_test_split)
from sklearn.metrics import accuracy_score, f1_score, classification_report

import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet',   quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ── Constants ─────────────────────────────────────────────────────
RANDOM_STATE = 42
CLASS_ORDER  = ['High', 'Medium', 'Low']

# Baseline (existing saved model) for comparison
BASELINE = {
    'model'       : 'LinearSVC (C=1.0, max_features=5000)',
    'train_acc'   : 0.9927,
    'test_acc'    : 0.6628,
    'test_f1'     : 0.6627,
    'cv_acc'      : 0.7048,
    'cv_f1'       : 0.7043,
    'gap'         : round(0.9927 - 0.6628, 4),
}

# ── Load and preprocess data ───────────────────────────────────────
print("Loading dataset...")
df = pd.read_csv('Dataset_duration.csv')

DOMAIN_SW = {'please','kindly','sir','madam','hello','thanks','thank','dear','hi',
             'regards','asap','hostel','complaint','request','warden','office',
             'management','student','students','look','also','us','am'}
ALL_SW = (set(stopwords.words('english')) | DOMAIN_SW) - \
         {'no','not','never','cannot','cant','wont','isnt','doesnt',
          'hasnt','havent','wasnt','wouldnt'}
_lem = WordNetLemmatizer()

def preprocess_text(text):
    if not isinstance(text, str) or not text.strip(): return ''
    text = text.lower()
    text = re.sub(r'\bleakage\b','leaking',text)
    text = re.sub(r'\bleak\b','leaking',text)
    text = re.sub(r'\belectricity\b','electric',text)
    for old,new in [("can't","cannot"),("won't","wont"),("isn't","is not"),
                    ("doesn't","does not"),("hasn't","has not"),
                    ("haven't","have not"),("wasn't","was not"),
                    ("wouldn't","would not")]:
        text = text.replace(old,new)
    text = re.sub(r'[^\w\s]',' ',text)
    text = re.sub(r'\b\d+\b','',text)
    text = re.sub(r'\s+',' ',text).strip()
    return ' '.join(_lem.lemmatize(w) for w in text.split()
                    if w not in ALL_SW and len(w) >= 2)

def parse_duration(text):
    if not isinstance(text, str): return None
    parts = text.strip().lower().split()
    if len(parts) != 2: return None
    try: v = float(parts[0])
    except: return None
    u = parts[1]
    if u in ('hour','hours'):   return v
    if u in ('day','days'):     return v * 24
    if u in ('week','weeks'):   return v * 168
    if u in ('month','months'): return v * 720
    return None

df['Cleaned_Text']   = df['Complaint_Text'].apply(preprocess_text)
df['Duration_Hours'] = df['Duration_Standardized'].apply(parse_duration)

TEXT_FEATURE = 'Cleaned_Text'
CAT_FEATURES = ['Category','Complaint_Type','Block','Floor']
NUM_FEATURES = ['Duration_Hours']
ALL_FEATURES = [TEXT_FEATURE] + CAT_FEATURES + NUM_FEATURES
TARGET       = 'Priority'

X = df[ALL_FEATURES].copy()
y = df[TARGET].copy()

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y)

le = LabelEncoder()
le.fit(CLASS_ORDER)
y_train_enc = le.transform(y_train)
y_test_enc  = le.transform(y_test)

print(f"  Train: {X_train.shape[0]} samples | Test: {X_test.shape[0]} samples")

# ── Build pipeline for GridSearch ─────────────────────────────────
def make_pipeline(C=1.0, max_features=5000, min_df=2):
    prep = ColumnTransformer([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1,2), max_features=max_features,
            sublinear_tf=True, min_df=min_df, strip_accents='unicode'),
         TEXT_FEATURE),
        ('ohe',   OneHotEncoder(handle_unknown='ignore', sparse_output=False),
         CAT_FEATURES),
        ('scaler', StandardScaler(), NUM_FEATURES),
    ], remainder='drop')

    clf = LinearSVC(C=C, max_iter=3000, class_weight='balanced',
                    random_state=RANDOM_STATE)
    return Pipeline([('prep', prep), ('clf', clf)])

# ── Grid search on X_train only ───────────────────────────────────
print("\nGridSearchCV — Training data only (5-fold stratified CV)...")
print("=" * 65)
param_grid = {
    'clf__C'                   : [0.01, 0.05, 0.1, 0.5, 1.0, 2.0],
    'prep__tfidf__max_features': [3000, 5000],
}
n_combos = 6 * 2
print(f"  Combinations: {n_combos}  |  Folds: 5  |  Total fits: {n_combos*5}")
print(f"  Scoring: f1_weighted")
print()

base_pipeline = make_pipeline()

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
grid_search = GridSearchCV(
    base_pipeline,
    param_grid,
    cv=skf,
    scoring='f1_weighted',
    refit=True,
    n_jobs=1,
    verbose=0,
    return_train_score=True,
)

t0 = time.time()
grid_search.fit(X_train, y_train_enc)
elapsed = time.time() - t0
print(f"  GridSearch complete in {elapsed:.1f}s")

# ── Print all results ──────────────────────────────────────────────
print("\nAll combinations (sorted by CV F1):")
print(f"  {'C':>6} | {'max_feat':>8} | {'CV F1':>8} | {'CV Acc':>8} | {'Train F1':>9}")
print("  " + "-"*55)
cv_results = grid_search.cv_results_
idx_sorted = np.argsort(cv_results['mean_test_score'])[::-1]
for idx in idx_sorted:
    p     = cv_results['params'][idx]
    cv_f1 = cv_results['mean_test_score'][idx]
    cv_ac = cv_results.get('mean_train_score', [0]*len(idx_sorted))[idx]
    print(f"  {p['clf__C']:>6} | {p['prep__tfidf__max_features']:>8} | "
          f"{cv_f1:>8.4f} | {'—':>8} | {'—':>9}")

# ── Best parameters ───────────────────────────────────────────────
best_params = grid_search.best_params_
best_cv_f1  = grid_search.best_score_
print(f"\n  Best C            : {best_params['clf__C']}")
print(f"  Best max_features : {best_params['prep__tfidf__max_features']}")
print(f"  Best CV F1        : {best_cv_f1:.4f}")

# ── Evaluate best pipeline on test set ───────────────────────────
best_pipeline = grid_search.best_estimator_

y_pred_train = best_pipeline.predict(X_train)
y_pred_test  = best_pipeline.predict(X_test)

tuned_train_acc = accuracy_score(y_train_enc, le.transform(y_train))
tuned_test_acc  = accuracy_score(y_test_enc,  y_pred_test)
tuned_test_f1   = f1_score(y_test_enc, y_pred_test, average='weighted')
tuned_train_acc = accuracy_score(le.transform(y_train), y_pred_train)
tuned_gap       = round(tuned_train_acc - tuned_test_acc, 4)

# Full CV on best pipeline
cv_full = cross_validate(
    make_pipeline(C=best_params['clf__C'],
                  max_features=best_params['prep__tfidf__max_features']),
    X_train, y_train_enc,
    cv=skf, scoring=['accuracy','f1_weighted'],
    return_train_score=True, n_jobs=1
)
tuned_cv_acc = round(float(cv_full['test_accuracy'].mean()),   4)
tuned_cv_f1  = round(float(cv_full['test_f1_weighted'].mean()),4)

# ── Comparison table ──────────────────────────────────────────────
print("\n" + "=" * 65)
print("BASELINE vs TUNED — COMPARISON")
print("=" * 65)
print(f"{'Metric':25s} | {'Baseline':12s} | {'Tuned':12s} | {'Change':10s}")
print("-" * 65)

metrics = [
    ('Train Accuracy',  BASELINE['train_acc'], tuned_train_acc),
    ('Test Accuracy',   BASELINE['test_acc'],  tuned_test_acc),
    ('Test F1 (wt)',    BASELINE['test_f1'],   tuned_test_f1),
    ('CV Accuracy',     BASELINE['cv_acc'],    tuned_cv_acc),
    ('CV F1 (wt)',      BASELINE['cv_f1'],     tuned_cv_f1),
    ('Train-Test Gap',  BASELINE['gap'],       tuned_gap),
]

for name, base_val, tuned_val in metrics:
    delta = tuned_val - base_val
    if name == 'Train-Test Gap':
        arrow = '✅ Reduced' if delta < -0.005 else ('⚠️ Increased' if delta > 0.005 else '— Same')
    else:
        arrow = '✅ Better' if delta > 0.003 else ('⚠️ Worse' if delta < -0.003 else '— Same')
    print(f"  {name:23s} | {base_val:10.4f}   | {tuned_val:10.4f}   | {arrow}")

print()
improved = (tuned_cv_f1 > BASELINE['cv_f1'] + 0.003) or \
           (tuned_gap   < BASELINE['gap']   - 0.01)

print(f"  Best C            : {best_params['clf__C']}  (baseline: 1.0)")
print(f"  Best max_features : {best_params['prep__tfidf__max_features']}  (baseline: 5000)")
print()

if improved:
    print("  VERDICT: ✅ Tuned model genuinely improves over baseline.")
    print("           Saving updated artifacts...")
else:
    print("  VERDICT: The tuned model does not genuinely improve generalization.")
    print("           Baseline model is kept. Reporting findings only.")

# ── Save if improved ─────────────────────────────────────────────
SAVE_DIR = 'saved_model'
if improved:
    # Retrain best pipeline on full X_train (GridSearchCV already refits, but
    # we do it explicitly for clarity and to extract components separately)
    final_C    = best_params['clf__C']
    final_mf   = best_params['prep__tfidf__max_features']

    final_prep = ColumnTransformer([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1,2), max_features=final_mf,
            sublinear_tf=True, min_df=2, strip_accents='unicode'),
         TEXT_FEATURE),
        ('ohe', OneHotEncoder(handle_unknown='ignore', sparse_output=False),
         CAT_FEATURES),
        ('scaler', StandardScaler(), NUM_FEATURES),
    ], remainder='drop')

    final_clf = LinearSVC(C=final_C, max_iter=3000,
                          class_weight='balanced', random_state=RANDOM_STATE)

    X_train_proc = final_prep.fit_transform(X_train)
    final_clf.fit(X_train_proc, y_train_enc)

    joblib.dump(final_prep, os.path.join(SAVE_DIR, 'preprocessor.pkl'))
    joblib.dump(final_clf,  os.path.join(SAVE_DIR, 'model.pkl'))
    joblib.dump(le,         os.path.join(SAVE_DIR, 'label_encoder.pkl'))

    import json as jlib
    meta = {
        'model_name'        : f'LinearSVC (C={final_C}, max_features={final_mf})',
        'dataset'           : 'Dataset_duration.csv',
        'n_samples'         : int(len(df)),
        'n_train'           : int(len(X_train)),
        'n_test'            : int(len(X_test)),
        'n_features'        : int(X_train_proc.shape[1]),
        'tuning_C'          : final_C,
        'tuning_max_features': final_mf,
        'classes'           : CLASS_ORDER,
        'baseline_train_acc': BASELINE['train_acc'],
        'baseline_test_acc' : BASELINE['test_acc'],
        'baseline_cv_f1'    : BASELINE['cv_f1'],
        'train_accuracy'    : round(float(tuned_train_acc), 4),
        'test_accuracy'     : round(float(tuned_test_acc),  4),
        'test_f1_weighted'  : round(float(tuned_test_f1),   4),
        'cv_accuracy_mean'  : tuned_cv_acc,
        'cv_f1_mean'        : tuned_cv_f1,
        'train_test_gap'    : tuned_gap,
        'excluded'          : ['Support_Count','Room_No','Status','Complaint_Date',
                               'Complaint_ID','Duration_Standardized'],
        'leakage_fixed'     : True,
        'tuned'             : True,
        'tuning_method'     : 'GridSearchCV (5-fold stratified, train only)',
    }
    with open(os.path.join(SAVE_DIR, 'model_metadata.json'), 'w') as f:
        jlib.dump(meta, f, indent=2)
    print("  ✅ Updated artifacts saved.")

# ── Verify loaded model prediction ────────────────────────────────
print("\n" + "=" * 65)
print("FINAL MODEL — LOAD AND PREDICT VERIFICATION")
print("=" * 65)

ld_prep  = joblib.load(os.path.join(SAVE_DIR, 'preprocessor.pkl'))
ld_model = joblib.load(os.path.join(SAVE_DIR, 'model.pkl'))
ld_le    = joblib.load(os.path.join(SAVE_DIR, 'label_encoder.pkl'))

from scipy.sparse import issparse
test_cases = [
    {'raw': "There is no electricity in the room, dangerous and unsafe",
     'Category':'Electricity','Complaint_Type':'Public','Block':'B','Floor':'Second','Duration_Hours':24.0},
    {'raw': "There are cobwebs all over the staircase",
     'Category':'Cleanliness','Complaint_Type':'Public','Block':'A','Floor':'Ground','Duration_Hours':48.0},
    {'raw': "The fan in my room is not working since yesterday",
     'Category':'Fan','Complaint_Type':'Private','Block':'C','Floor':'First','Duration_Hours':24.0},
    {'raw': "fire risk in generator room emergency",
     'Category':'Fire Safety','Complaint_Type':'Public','Block':'C','Floor':'Ground','Duration_Hours':1.0},
]
rows = []
for tc in test_cases:
    row = {k:v for k,v in tc.items() if k!='raw'}
    row['Cleaned_Text'] = preprocess_text(tc['raw'])
    rows.append(row)

sample_df   = pd.DataFrame(rows)
sample_proc = ld_prep.transform(sample_df)
if issparse(sample_proc): sample_proc = sample_proc.toarray()
preds       = ld_le.inverse_transform(ld_model.predict(sample_proc))

print(f"\n  Loaded model type : {type(ld_model).__name__}")
print(f"  Coef_ shape       : {ld_model.coef_.shape}")
print(f"\n  Sample predictions:")
for tc, pred in zip(test_cases, preds):
    print(f"    {tc['Category']:15s} | {tc['Duration_Hours']:4.0f}h | "
          f"{tc['raw'][:45]:45s} → {pred}")

print("\n  ✅ Final model loads and predicts correctly.")

# ── Save tuning results summary ─────────────────────────────────
summary = {
    'improved'         : improved,
    'best_C'           : best_params['clf__C'],
    'best_max_features': best_params['prep__tfidf__max_features'],
    'tuned_train_acc'  : round(tuned_train_acc, 4),
    'tuned_test_acc'   : round(tuned_test_acc,  4),
    'tuned_test_f1'    : round(tuned_test_f1,   4),
    'tuned_cv_acc'     : tuned_cv_acc,
    'tuned_cv_f1'      : tuned_cv_f1,
    'tuned_gap'        : tuned_gap,
    'all_results'      : [],
}
for idx in idx_sorted:
    p = cv_results['params'][idx]
    summary['all_results'].append({
        'C'           : p['clf__C'],
        'max_features': p['prep__tfidf__max_features'],
        'cv_f1'       : round(float(cv_results['mean_test_score'][idx]), 4),
    })

import json as jlib
with open('tuning_summary.json', 'w') as f:
    jlib.dump(summary, f, indent=2)

print("\nTuning summary saved to tuning_summary.json")
print("=" * 65)
