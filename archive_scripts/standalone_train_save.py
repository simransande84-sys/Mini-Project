"""
standalone_train_save.py
========================
Trains the full hostel complaint prioritization pipeline from scratch
and saves all deployment artifacts to the saved_model/ directory.

Run with:   python -X utf8 standalone_train_save.py
"""

# ── Imports ──────────────────────────────────────────────────────────────
import os, json, re, warnings
import pandas as pd
import numpy as np
import joblib
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

from sklearn.compose import ColumnTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report
from sklearn.pipeline import Pipeline
from scipy.sparse import issparse, csr_matrix

warnings.filterwarnings('ignore')

# ── NLTK data ─────────────────────────────────────────────────────────────
print("Downloading NLTK data...")
nltk.download('stopwords', quiet=True)
nltk.download('wordnet',   quiet=True)
nltk.download('omw-1.4',   quiet=True)

# ── 1. LOAD DATA ─────────────────────────────────────────────────────────
CSV_FILE = 'hostel_complaints_800_final (1).csv'
print(f"\n[1] Loading dataset: {CSV_FILE}")
df = pd.read_csv(CSV_FILE)
print(f"    Shape: {df.shape}")
print(f"    Columns: {df.columns.tolist()}")

# ── 2. NLP PREPROCESSING ──────────────────────────────────────────────────
print("\n[2] Preprocessing text...")

domain_stopwords = {
    'please', 'kindly', 'sir', 'madam', 'hello', 'thanks', 'thank',
    'look', 'now', 'today', 'day', 'days', 'week', 'weeks', 'asap',
    'dear', 'hi', 'regards', 'hostel', 'room', 'complaint', 'issue',
    'problem', 'request', 'warden', 'office', 'management', 'student',
    'students', 'block', 'floor', 'need', 'want', 'get', 'us', 'our',
    'we', 'my', 'am', 'also'
}

std_stopwords = set(stopwords.words('english'))
all_stopwords = std_stopwords.union(domain_stopwords)
lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if not isinstance(text, str):
        return ''
    text = text.lower()
    text = re.sub(r'\bleakage\b', 'leaking', text)
    text = re.sub(r'\bleak\b', 'leaking', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = [lemmatizer.lemmatize(w) for w in text.split() if w not in all_stopwords and len(w) > 2]
    return ' '.join(tokens)

df['Cleaned_Text'] = df['Complaint_Text'].apply(preprocess_text)
print(f"    Text preprocessing done. Sample: '{df['Cleaned_Text'].iloc[0][:60]}...'")

# ── 3. FEATURE DEFINITIONS ────────────────────────────────────────────────
print("\n[3] Defining features...")
categorical_features = ['Complaint_Type', 'Block', 'Floor', 'Category']
numerical_features   = ['Students_Affected', 'Support_Count']

# Check which columns actually exist in the dataset
all_needed = categorical_features + numerical_features + ['Cleaned_Text', 'Priority']
missing_cols = [c for c in all_needed if c not in df.columns]
if missing_cols:
    print(f"    [WARN] Missing columns: {missing_cols}")
    # Auto-detect alternatives
    categorical_features = [c for c in categorical_features if c in df.columns]
    numerical_features   = [c for c in numerical_features   if c in df.columns]
    print(f"    Using categorical: {categorical_features}")
    print(f"    Using numerical:   {numerical_features}")

# ── 4. ENCODE TARGET ──────────────────────────────────────────────────────
print("\n[4] Encoding target variable 'Priority'...")
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(df['Priority'])
print(f"    Classes: {label_encoder.classes_}")
for cls, enc in zip(label_encoder.classes_, range(len(label_encoder.classes_))):
    cnt = (y == enc).sum()
    print(f"      {cls:8s} -> {enc}  ({cnt} samples, {cnt/len(y)*100:.1f}%)")

# ── 5. PREPARE X ──────────────────────────────────────────────────────────
drop_cols = ['Complaint_ID', 'Room_No', 'Duration', 'Status', 'Complaint_Date', 'Complaint_Text', 'Priority']
drop_cols = [c for c in drop_cols if c in df.columns]
X = df.drop(columns=drop_cols)
print(f"\n[5] Feature matrix X: {X.shape}")
print(f"    Columns: {X.columns.tolist()}")

# ── 6. TRAIN-TEST SPLIT ───────────────────────────────────────────────────
print("\n[6] Train-test split (80/20, stratified)...")
X_train_raw, X_test_raw, y_train, y_test = train_test_split(
    X, y, test_size=0.20, random_state=42, stratify=y
)
print(f"    Train: {len(X_train_raw)} | Test: {len(X_test_raw)}")

# ── 7. COLUMN TRANSFORMER ─────────────────────────────────────────────────
print("\n[7] Building ColumnTransformer...")

def make_preprocessor():
    return ColumnTransformer(
        transformers=[
            ('tfidf', TfidfVectorizer(
                max_features=1000, ngram_range=(1, 2),
                min_df=2, max_df=0.95, sublinear_tf=True
            ), 'Cleaned_Text'),
            ('cat', OneHotEncoder(
                drop='first', sparse_output=False, handle_unknown='ignore'
            ), categorical_features),
            ('num', StandardScaler(), numerical_features)
        ],
        remainder='drop'
    )

# Fit preprocessor
preprocessor = make_preprocessor()
X_train = preprocessor.fit_transform(X_train_raw)
X_test  = preprocessor.transform(X_test_raw)
print(f"    X_train shape: {X_train.shape}")
print(f"    X_test  shape: {X_test.shape}")

# ── 8. TRAIN ALL MODELS ───────────────────────────────────────────────────
print("\n[8] Training all models...")
results = {}

# 8a. Logistic Regression
print("    Training Logistic Regression...")
lr_model = LogisticRegression(
    C=1.0, max_iter=1000, solver='lbfgs',
    class_weight='balanced', random_state=42
)
lr_model.fit(X_train, y_train)
y_pred_lr = lr_model.predict(X_test)
results['Logistic Regression'] = {
    'Accuracy':  round(accuracy_score(y_test, y_pred_lr), 4),
    'Precision': round(precision_score(y_test, y_pred_lr, average='weighted'), 4),
    'Recall':    round(recall_score(y_test, y_pred_lr, average='weighted'), 4),
    'F1-Score':  round(f1_score(y_test, y_pred_lr, average='weighted'), 4),
}
print(f"      LR  -> Acc={results['Logistic Regression']['Accuracy']:.4f}  F1={results['Logistic Regression']['F1-Score']:.4f}")

# 8b. Random Forest
print("    Training Random Forest...")
rf_model = RandomForestClassifier(
    n_estimators=200, min_samples_split=5, min_samples_leaf=2,
    class_weight='balanced', random_state=42, n_jobs=-1
)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)
results['Random Forest'] = {
    'Accuracy':  round(accuracy_score(y_test, y_pred_rf), 4),
    'Precision': round(precision_score(y_test, y_pred_rf, average='weighted'), 4),
    'Recall':    round(recall_score(y_test, y_pred_rf, average='weighted'), 4),
    'F1-Score':  round(f1_score(y_test, y_pred_rf, average='weighted'), 4),
}
print(f"      RF  -> Acc={results['Random Forest']['Accuracy']:.4f}  F1={results['Random Forest']['F1-Score']:.4f}")

# 8c. Linear SVM
print("    Training Linear SVM...")
svm_model = LinearSVC(
    C=1.0, max_iter=2000, class_weight='balanced', random_state=42
)
svm_model.fit(X_train, y_train)
y_pred_svm = svm_model.predict(X_test)
results['Linear SVM'] = {
    'Accuracy':  round(accuracy_score(y_test, y_pred_svm), 4),
    'Precision': round(precision_score(y_test, y_pred_svm, average='weighted'), 4),
    'Recall':    round(recall_score(y_test, y_pred_svm, average='weighted'), 4),
    'F1-Score':  round(f1_score(y_test, y_pred_svm, average='weighted'), 4),
}
print(f"      SVM -> Acc={results['Linear SVM']['Accuracy']:.4f}  F1={results['Linear SVM']['F1-Score']:.4f}")

# 8d. Naive Bayes (TF-IDF only)
print("    Training Naive Bayes (TF-IDF only)...")
n_tfidf = len(preprocessor.transformers_[0][1].get_feature_names_out())
if issparse(X_train):
    X_train_nb = X_train[:, :n_tfidf]
    X_test_nb  = X_test[:, :n_tfidf]
else:
    X_train_nb = csr_matrix(X_train[:, :n_tfidf])
    X_test_nb  = csr_matrix(X_test[:, :n_tfidf])
nb_model = MultinomialNB(alpha=1.0)
nb_model.fit(X_train_nb, y_train)
y_pred_nb = nb_model.predict(X_test_nb)
results['Naive Bayes'] = {
    'Accuracy':  round(accuracy_score(y_test, y_pred_nb), 4),
    'Precision': round(precision_score(y_test, y_pred_nb, average='weighted'), 4),
    'Recall':    round(recall_score(y_test, y_pred_nb, average='weighted'), 4),
    'F1-Score':  round(f1_score(y_test, y_pred_nb, average='weighted'), 4),
}
print(f"      NB  -> Acc={results['Naive Bayes']['Accuracy']:.4f}  F1={results['Naive Bayes']['F1-Score']:.4f}")

# ── 9. GRID SEARCH TUNING ─────────────────────────────────────────────────
print("\n[9] GridSearchCV tuning (LR and SVM)...")

def make_lr_pipe():
    return Pipeline([
        ('preprocessor', make_preprocessor()),
        ('model', LogisticRegression(
            max_iter=1000, solver='lbfgs',
            class_weight='balanced', random_state=42
        ))
    ])

def make_svm_pipe():
    return Pipeline([
        ('preprocessor', make_preprocessor()),
        ('model', LinearSVC(max_iter=2000, class_weight='balanced', random_state=42))
    ])

param_grid = {'model__C': [0.01, 0.1, 1.0, 5.0, 10.0]}

print("    Tuning Logistic Regression...")
lr_grid = GridSearchCV(make_lr_pipe(), param_grid, cv=5, scoring='f1_weighted', n_jobs=-1)
lr_grid.fit(X_train_raw, y_train)
lr_best_f1 = f1_score(y_test, lr_grid.best_estimator_.predict(X_test_raw), average='weighted')
print(f"      Best C={lr_grid.best_params_['model__C']}  CV_F1={lr_grid.best_score_:.4f}  Test_F1={lr_best_f1:.4f}")

print("    Tuning Linear SVM...")
svm_grid = GridSearchCV(make_svm_pipe(), param_grid, cv=5, scoring='f1_weighted', n_jobs=-1)
svm_grid.fit(X_train_raw, y_train)
svm_best_f1 = f1_score(y_test, svm_grid.best_estimator_.predict(X_test_raw), average='weighted')
print(f"      Best C={svm_grid.best_params_['model__C']}  CV_F1={svm_grid.best_score_:.4f}  Test_F1={svm_best_f1:.4f}")

# ── 10. SELECT BEST MODEL ─────────────────────────────────────────────────
print("\n[10] Selecting best model...")
candidates = {
    'LR (tuned)':  (lr_grid.best_estimator_,  lr_best_f1),
    'SVM (tuned)': (svm_grid.best_estimator_, svm_best_f1),
}
best_name, (final_model, best_f1) = max(candidates.items(), key=lambda x: x[1][1])
best_acc = accuracy_score(y_test, final_model.predict(X_test_raw))
print(f"    Selected: {best_name}")
print(f"    Test F1-Score : {best_f1:.4f}")
print(f"    Test Accuracy : {best_acc:.4f}")
print("\n    Full Classification Report:")
print(classification_report(y_test, final_model.predict(X_test_raw),
                             target_names=label_encoder.classes_))

# ── 11. SAVE ARTIFACTS ────────────────────────────────────────────────────
print("\n[11] Saving deployment artifacts...")
model_dir = 'saved_model'
os.makedirs(model_dir, exist_ok=True)

# 11a. Full pipeline (preprocessor + model)
model_path = os.path.join(model_dir, 'hostel_priority_model.pkl')
joblib.dump(final_model, model_path)
print(f"    Saved: {model_path}  ({os.path.getsize(model_path)/1024:.1f} KB)")

# 11b. Label encoder
encoder_path = os.path.join(model_dir, 'label_encoder.pkl')
joblib.dump(label_encoder, encoder_path)
print(f"    Saved: {encoder_path}  ({os.path.getsize(encoder_path)/1024:.1f} KB)")

# 11c. Domain stopwords
stopwords_path = os.path.join(model_dir, 'domain_stopwords.pkl')
joblib.dump(domain_stopwords, stopwords_path)
print(f"    Saved: {stopwords_path}  ({os.path.getsize(stopwords_path)/1024:.1f} KB)")

# 11d. Metadata JSON
metadata = {
    'model_name':          best_name,
    'test_f1_score':       round(best_f1, 4),
    'test_accuracy':       round(best_acc, 4),
    'classes':             label_encoder.classes_.tolist(),
    'class_encoding':      {cls: int(enc) for cls, enc in
                            zip(label_encoder.classes_, range(len(label_encoder.classes_)))},
    'features_used':       ['Cleaned_Text (TF-IDF)', *categorical_features, *numerical_features],
    'categorical_features': categorical_features,
    'numerical_features':  numerical_features,
    'training_samples':    int(len(X_train_raw)),
    'test_samples':        int(len(X_test_raw)),
    'tfidf_params': {
        'max_features': 1000,
        'ngram_range':  '(1,2)',
        'min_df':       2,
        'max_df':       0.95,
        'sublinear_tf': True
    },
    'all_model_results':   {k: {m: v for m, v in res.items() if m != 'y_pred'}
                            for k, res in results.items()},
    'preprocessing_steps': [
        'lowercase', 'remove_punctuation', 'remove_numbers',
        'remove_stopwords (standard + domain)', 'lemmatization'
    ]
}
metadata_path = os.path.join(model_dir, 'model_metadata.json')
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=2)
print(f"    Saved: {metadata_path}  ({os.path.getsize(metadata_path)/1024:.1f} KB)")

# ── 12. VERIFICATION ──────────────────────────────────────────────────────
print("\n[12] Verifying saved artifacts...")

# List all files
print(f"\n    Contents of '{model_dir}/':")
print(f"    {'Filename':<40} {'Size':>10}")
print(f"    {'-'*52}")
all_files = os.listdir(model_dir)
for fname in sorted(all_files):
    fpath = os.path.join(model_dir, fname)
    size  = os.path.getsize(fpath)
    print(f"    {fname:<40} {size/1024:>8.1f} KB")

# Load and test
print("\n    Testing load + predict cycle...")
loaded_model   = joblib.load(model_path)
loaded_encoder = joblib.load(encoder_path)
loaded_sw      = joblib.load(stopwords_path)

test_preds = loaded_model.predict(X_test_raw)
test_f1    = f1_score(y_test, test_preds, average='weighted')
match      = np.array_equal(test_preds, final_model.predict(X_test_raw))

print(f"    Loaded model type   : {type(loaded_model).__name__}")
print(f"    Loaded encoder classes: {loaded_encoder.classes_}")
print(f"    Predictions match   : {match}")
print(f"    Loaded model F1     : {test_f1:.4f}")

# Test on a single new complaint
lem2 = WordNetLemmatizer()
sw2  = set(stopwords.words('english')).union(loaded_sw)
sample_text = "water cooler in block b not working since three days students cannot drink water"
cleaned = ' '.join([lem2.lemmatize(w) for w in sample_text.split() if w not in sw2 and len(w) > 2])

sample_df = pd.DataFrame([{
    'Cleaned_Text':      cleaned,
    'Complaint_Type':    'Public',
    'Block':             'B',
    'Floor':             'Ground',
    'Category':          'Water Cooler',
    'Students_Affected': 40,
    'Support_Count':     15
}])

pred_enc   = loaded_model.predict(sample_df)
pred_label = loaded_encoder.inverse_transform(pred_enc)[0]
print(f"\n    Sample prediction:")
print(f"      Text     : '{sample_text}'")
print(f"      Priority : {pred_label}")

# ── DONE ─────────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("  TRAINING AND SAVING COMPLETE")
print("="*65)
print(f"  Best Model   : {best_name}")
print(f"  F1-Score     : {best_f1:.4f}")
print(f"  Accuracy     : {best_acc:.4f}")
print(f"  Artifacts    : {len(all_files)} files in '{model_dir}/'")
print(f"  READY FOR DEPLOYMENT IN DJANGO APPLICATION")
print("="*65)
