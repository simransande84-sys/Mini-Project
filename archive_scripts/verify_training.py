"""
verify_training.py
Read-only verification of:
1. Notebook cell outputs (embedded evidence of actual execution)
2. Saved model artifacts on disk
3. Load and predict with saved model
NO training, NO file modifications.
"""
import json, os, sys
from datetime import datetime

NB_PATH    = r'hostel_complaint_prioritization.ipynb'
SAVE_DIR   = r'saved_model'

print("=" * 65)
print("  HostelSense ML — Training Verification Report")
print("=" * 65)

# ─── 1. Read notebook cell outputs ────────────────────────────────
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

print(f"\n[1] NOTEBOOK STRUCTURE")
print(f"  Total cells  : {len(cells)}")
code_cells = [c for c in cells if c['cell_type'] == 'code']
exec_cells  = [c for c in code_cells if c.get('execution_count') is not None]
print(f"  Code cells   : {len(code_cells)}")
print(f"  Executed     : {len(exec_cells)}")
print(f"  Not executed : {len(code_cells) - len(exec_cells)}")

# ─── 2. Find the training results cell output ─────────────────────
print(f"\n[2] SECTION 5 — CLASSIFIER TRAINING OUTPUT")
print("  (Extracted from notebook cell outputs)")
print()

for i, cell in enumerate(cells):
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source'])
    # Find the model training cell
    if 'Training 5 classifiers' in src or 'Best model:' in src:
        outputs = cell.get('outputs', [])
        if outputs:
            for out in outputs:
                if out.get('output_type') == 'stream':
                    text = ''.join(out.get('text', []))
                    print(f"  [Cell {i}, exec #{cell.get('execution_count')}]")
                    print(text)
        else:
            print(f"  Cell {i}: CODE EXISTS but NO OUTPUT — cell was not executed!")
        break

# ─── 3. Feature matrix shape ──────────────────────────────────────
print(f"\n[3] FEATURE MATRIX & PREPROCESSING OUTPUT")
for i, cell in enumerate(cells):
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source'])
    if 'Feature Matrix Summary' in src or 'X_train :' in src:
        outputs = cell.get('outputs', [])
        if outputs:
            for out in outputs:
                if out.get('output_type') == 'stream':
                    text = ''.join(out.get('text', []))
                    print(f"  [Cell {i}, exec #{cell.get('execution_count')}]")
                    print(text)
        else:
            print(f"  Cell {i}: NO OUTPUT — not executed!")
        break

# ─── 4. CV output ─────────────────────────────────────────────────
print(f"\n[4] CROSS-VALIDATION OUTPUT")
for i, cell in enumerate(cells):
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source'])
    if 'cross_validate' in src and 'CV Accuracy' in src:
        outputs = cell.get('outputs', [])
        if outputs:
            for out in outputs:
                if out.get('output_type') == 'stream':
                    text = ''.join(out.get('text', []))
                    print(f"  [Cell {i}, exec #{cell.get('execution_count')}]")
                    print(text)
        else:
            print(f"  Cell {i}: NO OUTPUT — not executed!")
        break

# ─── 5. Save cell output ──────────────────────────────────────────
print(f"\n[5] MODEL SAVE OUTPUT")
for i, cell in enumerate(cells):
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source'])
    if 'joblib.dump' in src and 'SAVE_DIR' in src and 'Saved to' in src:
        outputs = cell.get('outputs', [])
        if outputs:
            for out in outputs:
                if out.get('output_type') == 'stream':
                    text = ''.join(out.get('text', []))
                    print(f"  [Cell {i}, exec #{cell.get('execution_count')}]")
                    print(text)
        else:
            print(f"  Cell {i}: NO OUTPUT — not executed!")
        break

# ─── 6. Verify files on disk ──────────────────────────────────────
print(f"\n[6] SAVED ARTIFACTS ON DISK")
required = ['model.pkl', 'preprocessor.pkl', 'label_encoder.pkl',
            'feature_config.json', 'model_metadata.json']
if os.path.isdir(SAVE_DIR):
    files = os.listdir(SAVE_DIR)
    for fname in required:
        fpath = os.path.join(SAVE_DIR, fname)
        if os.path.exists(fpath):
            size = os.path.getsize(fpath)
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            print(f"  ✅ {fname:35s}  {size/1024:7.1f} KB   modified: {mtime.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"  ❌ {fname} — MISSING!")
else:
    print(f"  ❌ Directory {SAVE_DIR} does not exist!")

# ─── 7. Load model and predict ────────────────────────────────────
print(f"\n[7] LOAD SAVED MODEL AND MAKE REAL PREDICTION")
try:
    import joblib, warnings
    import pandas as pd, numpy as np, re
    warnings.filterwarnings('ignore')

    loaded_prep  = joblib.load(os.path.join(SAVE_DIR, 'preprocessor.pkl'))
    loaded_model = joblib.load(os.path.join(SAVE_DIR, 'model.pkl'))
    loaded_le    = joblib.load(os.path.join(SAVE_DIR, 'label_encoder.pkl'))
    print(f"  ✅ Loaded preprocessor  : {type(loaded_prep).__name__}")
    print(f"  ✅ Loaded model         : {type(loaded_model).__name__}")
    print(f"  ✅ Loaded label encoder : {type(loaded_le).__name__}")
    print(f"     Model classes        : {loaded_le.classes_}")

    # Check model is actually fitted (has learned parameters)
    if hasattr(loaded_model, 'coef_'):
        print(f"  ✅ Model is FITTED — coef_ shape: {loaded_model.coef_.shape}")
    elif hasattr(loaded_model, 'estimators_'):
        print(f"  ✅ Model is FITTED — n_estimators: {len(loaded_model.estimators_)}")
    else:
        print(f"  ⚠️  Cannot confirm fitting from attributes")

    # TF-IDF vocabulary check
    tfidf_vocab = loaded_prep.named_transformers_['tfidf'].vocabulary_
    print(f"\n  ✅ TF-IDF vocabulary size: {len(tfidf_vocab)} terms")
    print(f"     Sample terms: {list(tfidf_vocab.keys())[:8]}")

    # OHE categories
    ohe_cats = loaded_prep.named_transformers_['ohe'].categories_
    print(f"  ✅ OHE fitted on {len(ohe_cats)} categorical features")
    for feat_cats in ohe_cats[:1]:
        print(f"     Sample cats: {list(feat_cats[:5])}")

    # Scaler params
    sc = loaded_prep.named_transformers_['scaler']
    print(f"  ✅ Scaler mean_={sc.mean_[0]:.2f}  std_={sc.scale_[0]:.2f}")

    # Make real predictions
    print(f"\n  Making 3 real predictions...")
    from scipy.sparse import issparse

    import nltk
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer

    DOMAIN_SW = {'please','kindly','sir','madam','hello','thanks','thank','dear','hi',
                 'regards','asap','hostel','complaint','request','warden','office',
                 'management','student','students','look','also','us','am'}
    ALL_SW = (set(stopwords.words('english')) | DOMAIN_SW) - \
             {'no','not','never','cannot','cant','wont','isnt','doesnt','hasnt','havent','wasnt','wouldnt'}
    _lem = WordNetLemmatizer()

    def preprocess_text(text):
        if not isinstance(text, str) or not text.strip(): return ''
        text = text.lower()
        text = re.sub(r'\bleakage\b','leaking',text); text = re.sub(r'\bleak\b','leaking',text)
        for old,new in [("can't","cannot"),("won't","wont"),("isn't","is not"),
                        ("doesn't","does not"),("hasn't","has not"),("haven't","have not"),
                        ("wasn't","was not"),("wouldn't","would not")]:
            text = text.replace(old,new)
        text = re.sub(r'[^\w\s]',' ',text); text = re.sub(r'\b\d+\b','',text)
        text = re.sub(r'\s+',' ',text).strip()
        return ' '.join(_lem.lemmatize(w) for w in text.split()
                        if w not in ALL_SW and len(w)>=2)

    test_complaints = [
        {'raw': "There is no electricity in the room, it is dangerous and unsafe",
         'Category': 'Electricity', 'Complaint_Type': 'Public',
         'Block': 'B', 'Floor': 'Second', 'Duration_Hours': 24.0},
        {'raw': "There are cobwebs all over the staircase",
         'Category': 'Cleanliness', 'Complaint_Type': 'Public',
         'Block': 'A', 'Floor': 'Ground', 'Duration_Hours': 48.0},
        {'raw': "The fan in my room is not working since yesterday",
         'Category': 'Fan', 'Complaint_Type': 'Private',
         'Block': 'C', 'Floor': 'First', 'Duration_Hours': 24.0},
    ]

    rows = []
    for tc in test_complaints:
        row = {k: v for k, v in tc.items() if k != 'raw'}
        row['Cleaned_Text'] = preprocess_text(tc['raw'])
        rows.append(row)

    sample_df   = pd.DataFrame(rows)
    sample_proc = loaded_prep.transform(sample_df)
    if issparse(sample_proc): sample_proc = sample_proc.toarray()
    preds_enc   = loaded_model.predict(sample_proc)
    preds       = loaded_le.inverse_transform(preds_enc)

    print()
    for tc, cleaned, pred in zip(test_complaints, [r['Cleaned_Text'] for r in rows], preds):
        print(f"  Original : {tc['raw'][:60]}")
        print(f"  Cleaned  : {cleaned}")
        print(f"  Category : {tc['Category']}   Duration: {tc['Duration_Hours']}h")
        print(f"  ► Predicted Priority: {pred}")
        print()

    print("  ✅ Saved model loaded and predicts successfully.")

except Exception as e:
    import traceback
    print(f"  ❌ ERROR: {e}")
    print(traceback.format_exc())

# ─── 8. model_metadata.json ───────────────────────────────────────
print(f"\n[8] MODEL METADATA (from model_metadata.json)")
meta_path = os.path.join(SAVE_DIR, 'model_metadata.json')
if os.path.exists(meta_path):
    with open(meta_path) as f:
        meta = json.load(f)
    for k, v in meta.items():
        print(f"  {k:25s}: {v}")
else:
    print("  ❌ model_metadata.json not found")

print("\n" + "=" * 65)
print("  Verification complete.")
print("=" * 65)
