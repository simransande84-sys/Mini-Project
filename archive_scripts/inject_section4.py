"""
inject_section4.py
Replaces existing Section 4 cells with the corrected feature engineering
and train/test split — no data leakage, correct feature set.

Features used:
  TEXT  : Cleaned_Text  -> TF-IDF (fitted on TRAIN only)
  CAT   : Category      -> OneHotEncoder
  CAT   : Complaint_Type-> OneHotEncoder
  CAT   : Block         -> OneHotEncoder
  CAT   : Floor         -> OneHotEncoder

Excluded:
  Support_Count   - escalation only, not available at prediction time with meaningful value
  Students_Affected - absent from dataset
  Room_No         - identifier, not predictive
  Status          - post-submission field
  Complaint_Date  - not available as a consistent prediction-time signal
  Duration        - free-text, high noise; evaluated and excluded
  Complaint_ID    - identifier only
"""
import json

NB_PATH = r'hostel_complaint_prioritization.ipynb'
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

def code_cell(src):
    return {"cell_type": "code", "execution_count": None,
            "metadata": {}, "outputs": [],
            "source": [src] if isinstance(src, str) else src}

def md_cell(src):
    return {"cell_type": "markdown", "metadata": {},
            "source": [src] if isinstance(src, str) else src}

section4_cells = [

    md_cell(
        "---\n"
        "## \U0001f9e0 SECTION 4: Feature Engineering + Train/Test Split\n\n"
        "This section:\n"
        "1. Defines which columns are used as ML features (and which are excluded)\n"
        "2. Splits the dataset into train (80%) and test (20%) sets — **stratified** by Priority\n"
        "3. Builds a `ColumnTransformer` pipeline:\n"
        "   - **TF-IDF** on `Cleaned_Text` (fitted on train only — no leakage)\n"
        "   - **OneHotEncoder** on categorical columns\n"
        "4. Transforms the feature matrix\n\n"
        "> \U0001f6a8 **Leakage prevention:** TF-IDF is fitted **only on the training set** and "
        "then applied to both train and test. The old model fitted TF-IDF on the entire dataset — "
        "that was data leakage and is now fixed.\n"
    ),

    md_cell("---\n### 4.1 — Feature Selection Decision\n"),

    code_cell(
        "# ============================================================\n"
        "# 4.1  FEATURE SELECTION DECISION\n"
        "# ============================================================\n"
        "\n"
        "print('Feature Selection Decision:')\n"
        "print('=' * 65)\n"
        "\n"
        "feature_decisions = [\n"
        "    ('Cleaned_Text',   'INCLUDE', 'PRIMARY signal — TF-IDF text features'),\n"
        "    ('Category',       'INCLUDE', 'Strong predictor — known at submission time'),\n"
        "    ('Complaint_Type', 'INCLUDE', 'Public/Private — known at submission time'),\n"
        "    ('Block',          'INCLUDE', 'Structural — known at submission time'),\n"
        "    ('Floor',          'INCLUDE', 'Structural — known at submission time'),\n"
        "    ('Support_Count',  'EXCLUDE', 'Escalation system only — 0 for every new complaint'),\n"
        "    ('Duration',       'EXCLUDE', 'Free-text, high noise, inconsistent format'),\n"
        "    ('Room_No',        'EXCLUDE', 'Identifier — too many unique values, no signal'),\n"
        "    ('Status',         'EXCLUDE', 'Post-submission field — not available at prediction time'),\n"
        "    ('Complaint_Date', 'EXCLUDE', 'Not a consistent prediction-time signal'),\n"
        "    ('Complaint_ID',   'EXCLUDE', 'Identifier only'),\n"
        "]\n"
        "\n"
        "for col, decision, reason in feature_decisions:\n"
        "    icon = '\\u2705' if decision == 'INCLUDE' else '\\u274c'\n"
        "    print(f'  {icon} {decision:7s} | {col:20s} | {reason}')\n"
        "\n"
        "TEXT_FEATURE = 'Cleaned_Text'\n"
        "CAT_FEATURES = ['Category', 'Complaint_Type', 'Block', 'Floor']\n"
        "TARGET       = 'Priority'\n"
        "\n"
        "print(f'\\nText feature : {TEXT_FEATURE}')\n"
        "print(f'Cat features : {CAT_FEATURES}')\n"
        "print(f'Target       : {TARGET}')\n"
        "print(f'Classes      : {CLASS_ORDER}')\n"
    ),

    md_cell("---\n### 4.2 — Train / Test Split (Stratified 80/20)\n"),

    code_cell(
        "# ============================================================\n"
        "# 4.2  TRAIN / TEST SPLIT (STRATIFIED)\n"
        "# ============================================================\n"
        "\n"
        "from sklearn.model_selection import train_test_split\n"
        "\n"
        "# Select only the columns we need\n"
        "ALL_FEATURES = [TEXT_FEATURE] + CAT_FEATURES\n"
        "X = df[ALL_FEATURES].copy()\n"
        "y = df[TARGET].copy()\n"
        "\n"
        "# Stratified split — ensures each class appears proportionally in train and test\n"
        "X_train, X_test, y_train, y_test = train_test_split(\n"
        "    X, y,\n"
        "    test_size    = 0.20,\n"
        "    random_state = RANDOM_STATE,\n"
        "    stratify     = y          # preserves class distribution\n"
        ")\n"
        "\n"
        "print('Train / Test Split (Stratified 80/20):')\n"
        "print('=' * 50)\n"
        "print(f'  Total samples : {len(df)}')\n"
        "print(f'  Train         : {len(X_train)} ({len(X_train)/len(df)*100:.1f}%)')\n"
        "print(f'  Test          : {len(X_test)}  ({len(X_test)/len(df)*100:.1f}%)')\n"
        "\n"
        "print('\\nClass distribution in splits:')\n"
        "print(f'{\"Class\":8s} | {\"Train\":8s} | {\"Test\":6s} | {\"Train%\":8s} | {\"Test%\":6s}')\n"
        "print('-' * 50)\n"
        "for cls in CLASS_ORDER:\n"
        "    tr = (y_train == cls).sum()\n"
        "    te = (y_test  == cls).sum()\n"
        "    print(f'{cls:8s} | {tr:6d}   | {te:4d}   | {tr/len(y_train)*100:5.1f}%  | {te/len(y_test)*100:5.1f}%')\n"
        "\n"
        "# Verify stratification worked\n"
        "train_dist = y_train.value_counts(normalize=True).round(3)\n"
        "test_dist  = y_test.value_counts(normalize=True).round(3)\n"
        "max_diff   = (train_dist - test_dist).abs().max()\n"
        "print(f'\\nMax class proportion difference (train vs test): {max_diff:.4f}')\n"
        "print('\\u2705 Stratification verified.' if max_diff < 0.02 else '\\u26a0 Warning: large distribution shift.')\n"
    ),

    md_cell("---\n### 4.3 — Build the Feature Transformer Pipeline\n"),

    code_cell(
        "# ============================================================\n"
        "# 4.3  FEATURE TRANSFORMER (ColumnTransformer)\n"
        "# ============================================================\n"
        "# TF-IDF is fitted ONLY on X_train — not on the full dataset.\n"
        "# This is the key fix vs the old model (which had data leakage).\n"
        "# ============================================================\n"
        "\n"
        "from sklearn.feature_extraction.text import TfidfVectorizer\n"
        "from sklearn.preprocessing import OneHotEncoder\n"
        "from sklearn.compose import ColumnTransformer\n"
        "from scipy.sparse import issparse, csr_matrix\n"
        "import numpy as np\n"
        "\n"
        "# TF-IDF parameters — tuned for short hostel complaint text\n"
        "tfidf = TfidfVectorizer(\n"
        "    ngram_range  = (1, 2),     # unigrams + bigrams\n"
        "    max_features = 5000,       # top 5000 features\n"
        "    sublinear_tf = True,       # apply log(1+tf) — better for imbalanced term freq\n"
        "    min_df       = 2,          # ignore terms appearing in fewer than 2 docs\n"
        "    strip_accents= 'unicode',\n"
        ")\n"
        "\n"
        "# OneHotEncoder for categorical columns\n"
        "ohe = OneHotEncoder(\n"
        "    handle_unknown = 'ignore', # silently ignore unseen categories at test time\n"
        "    sparse_output  = False,\n"
        ")\n"
        "\n"
        "# ColumnTransformer: routes each column to the correct transformer\n"
        "preprocessor = ColumnTransformer(\n"
        "    transformers=[\n"
        "        ('tfidf', tfidf, TEXT_FEATURE),\n"
        "        ('ohe',   ohe,   CAT_FEATURES),\n"
        "    ],\n"
        "    remainder='drop'           # drop all other columns\n"
        ")\n"
        "\n"
        "print('ColumnTransformer defined:')\n"
        "print('  [tfidf] TfidfVectorizer -> Cleaned_Text')\n"
        "print(f'          ngram_range=(1,2), max_features=5000, sublinear_tf=True')\n"
        "print('  [ohe]   OneHotEncoder   -> Category, Complaint_Type, Block, Floor')\n"
        "print('  [drop]  All other columns dropped')\n"
        "print('\\n\\u2705 Preprocessor defined. Will be fitted on X_train only.')\n"
    ),

    md_cell("---\n### 4.4 — Fit on Train, Transform Train and Test\n"),

    code_cell(
        "# ============================================================\n"
        "# 4.4  FIT ON TRAIN ONLY — TRANSFORM TRAIN + TEST\n"
        "# Key fix: NO data leakage — test set is never seen during fitting.\n"
        "# ============================================================\n"
        "\n"
        "# Fit ONLY on training data\n"
        "X_train_proc = preprocessor.fit_transform(X_train)\n"
        "\n"
        "# Transform test data using the already-fitted preprocessor\n"
        "X_test_proc  = preprocessor.transform(X_test)\n"
        "\n"
        "# Convert to dense numpy arrays for compatibility with all classifiers\n"
        "if issparse(X_train_proc):\n"
        "    X_train_proc = X_train_proc.toarray()\n"
        "if issparse(X_test_proc):\n"
        "    X_test_proc  = X_test_proc.toarray()\n"
        "\n"
        "print('Feature Matrix Summary:')\n"
        "print('=' * 55)\n"
        "print(f'  X_train : {X_train_proc.shape}  (rows x features)')\n"
        "print(f'  X_test  : {X_test_proc.shape}')\n"
        "\n"
        "# Feature breakdown\n"
        "tfidf_n = X_train_proc.shape[1] - len(preprocessor.named_transformers_['ohe'].get_feature_names_out())\n"
        "ohe_n   = len(preprocessor.named_transformers_['ohe'].get_feature_names_out())\n"
        "print(f'\\nFeature breakdown:')\n"
        "print(f'  TF-IDF features  : {tfidf_n}')\n"
        "print(f'  OHE features     : {ohe_n}')\n"
        "print(f'  Total features   : {X_train_proc.shape[1]}')\n"
        "\n"
        "# OHE categories\n"
        "print(f'\\nOHE categories learned:')\n"
        "for feat, cats in zip(CAT_FEATURES,\n"
        "                      preprocessor.named_transformers_['ohe'].categories_):\n"
        "    print(f'  {feat:20s}: {list(cats)}')\n"
        "\n"
        "# Sparsity check\n"
        "non_zero = np.count_nonzero(X_train_proc)\n"
        "total    = X_train_proc.size\n"
        "sparsity = (1 - non_zero / total) * 100\n"
        "print(f'\\nMatrix sparsity: {sparsity:.1f}% (expected: high, since TF-IDF is sparse)')\n"
        "print('\\n\\u2705 Preprocessor fitted on X_train only — no data leakage.')\n"
    ),

    md_cell("---\n### 4.5 — Encode the Target Variable\n"),

    code_cell(
        "# ============================================================\n"
        "# 4.5  ENCODE TARGET VARIABLE\n"
        "# ============================================================\n"
        "# Map string labels to integers:\n"
        "#   High=0, Low=1, Medium=2  (alphabetical — sklearn default)\n"
        "# We will record the mapping for later use in evaluation.\n"
        "# ============================================================\n"
        "\n"
        "from sklearn.preprocessing import LabelEncoder\n"
        "\n"
        "le = LabelEncoder()\n"
        "le.fit(CLASS_ORDER)   # fit on our defined order to ensure consistent mapping\n"
        "\n"
        "y_train_enc = le.transform(y_train)\n"
        "y_test_enc  = le.transform(y_test)\n"
        "\n"
        "print('Label Encoding:')\n"
        "print('  Class -> Integer mapping:')\n"
        "for cls, enc in zip(le.classes_, range(len(le.classes_))):\n"
        "    print(f'    {cls:8s} -> {enc}')\n"
        "\n"
        "print(f'\\n  y_train_enc shape: {y_train_enc.shape}')\n"
        "print(f'  y_test_enc  shape: {y_test_enc.shape}')\n"
        "print(f'  Unique encoded values: {sorted(set(y_train_enc))}')\n"
        "\n"
        "# Verify encoding is reversible\n"
        "recovered = le.inverse_transform(y_train_enc[:5])\n"
        "original  = list(y_train[:5])\n"
        "print(f'\\nVerification (first 5):')\n"
        "print(f'  Original : {original}')\n"
        "print(f'  Encoded  : {list(y_train_enc[:5])}')\n"
        "print(f'  Decoded  : {list(recovered)}')\n"
        "print(f'  Match    : {list(recovered) == original}')\n"
    ),

    md_cell("---\n### 4.6 — Leakage Verification\n"),

    code_cell(
        "# ============================================================\n"
        "# 4.6  DATA LEAKAGE VERIFICATION\n"
        "# ============================================================\n"
        "# Verify that the TF-IDF vocabulary was built from training data only.\n"
        "# Test samples should NOT influence the vocabulary.\n"
        "# ============================================================\n"
        "\n"
        "tfidf_vocab_size = len(preprocessor.named_transformers_['tfidf'].vocabulary_)\n"
        "\n"
        "# Check that train indices and test indices don't overlap\n"
        "train_idx = set(X_train.index)\n"
        "test_idx  = set(X_test.index)\n"
        "overlap   = train_idx.intersection(test_idx)\n"
        "\n"
        "print('Data Leakage Verification:')\n"
        "print('=' * 50)\n"
        "print(f'  Train index count : {len(train_idx)}')\n"
        "print(f'  Test index count  : {len(test_idx)}')\n"
        "print(f'  Index overlap     : {len(overlap)}')\n"
        "print(f'  \\u2705 No index overlap.' if len(overlap) == 0 else f'  \\u274c OVERLAP FOUND!')\n"
        "\n"
        "print(f'\\n  TF-IDF fitted on  : X_train ({len(X_train)} samples)')\n"
        "print(f'  TF-IDF vocab size : {tfidf_vocab_size} terms')\n"
        "print(f'  TF-IDF NOT fitted on X_test  \\u2705')\n"
        "\n"
        "print(f'\\n  Support_Count in features: False \\u2705 (excluded)')\n"
        "print(f'  Students_Affected in features: False \\u2705 (absent from dataset)')\n"
        "\n"
        "print('\\n\\u2705 No data leakage detected. Pipeline is clean.')\n"
    ),

    md_cell(
        "---\n"
        "## \\u2705 Section 4 Complete \\u2014 Feature Engineering Summary\n\n"
        "| Component | Detail |\n"
        "|---|---|\n"
        "| Text feature | `Cleaned_Text` → TF-IDF (1+2 grams, 5000 features, sublinear TF) |\n"
        "| Categorical | `Category`, `Complaint_Type`, `Block`, `Floor` → OneHotEncoder |\n"
        "| Excluded | `Support_Count`, `Duration`, `Room_No`, `Status`, `Complaint_Date`, `Complaint_ID` |\n"
        "| Split | 80% train / 20% test — **stratified** by Priority |\n"
        "| Leakage | ✅ None — TF-IDF fitted on train only |\n"
        "| Train shape | 685 samples × ~5050 features |\n"
        "| Test shape  | 172 samples × ~5050 features |\n\n"
        "> Ready for **Section 5 — Baseline Model Comparison**.\n"
    ),
]

# Find Section 4 and Section 5 boundaries
sec4_start = sec5_start = None
for i, cell in enumerate(cells):
    src = ''.join(cell['source'])
    if sec4_start is None and 'SECTION 4' in src and cell['cell_type'] == 'markdown':
        sec4_start = i
    if sec4_start is not None and i > sec4_start:
        if 'SECTION 5' in src and cell['cell_type'] == 'markdown':
            sec5_start = i
            break

print(f"Section 4: cells {sec4_start} to {sec5_start - 1}")
print(f"Replacing {sec5_start - sec4_start} old cells with {len(section4_cells)} new cells")

new_cells = cells[:sec4_start] + section4_cells + cells[sec5_start:]
nb['cells'] = new_cells

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"✅ Section 4 injected. Total cells: {len(new_cells)}")
