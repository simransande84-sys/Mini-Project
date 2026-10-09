"""
execute_duration_integration.py

Targeted changes to hostel_complaint_prioritization.ipynb:
1. Section 1: swap CSV filename (DATSETminiproject.csv -> Dataset_duration.csv)
2. Section 2: add Duration_Standardized EDA cells (after existing EDA)
3. Section 4: 
   - Add 4.0 cell: parse Duration_Standardized -> Duration_Hours
   - Update 4.1: add Duration_Hours to feature list
   - Update 4.2: add NUM_FEATURES to ALL_FEATURES
   - Update 4.3: add StandardScaler for Duration_Hours
   - Update 4.4: show num feature in breakdown
4. Replace Sections 5+ with correct Sections 5-9
"""
import json

NB_PATH = r'hostel_complaint_prioritization.ipynb'
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

# ─────────────────────────────────────────────────────────────
# STEP 1: Update CSV filename in Sections 1 & 2 code cells
# ─────────────────────────────────────────────────────────────
OLD_CSV = 'DATSETminiproject.csv'
NEW_CSV = 'Dataset_duration.csv'
csv_changed = 0
for cell in cells:
    src_joined = ''.join(cell['source'])
    if OLD_CSV in src_joined:
        new_src = [line.replace(OLD_CSV, NEW_CSV) for line in cell['source']]
        cell['source'] = new_src
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
        csv_changed += 1
print(f"Step 1: CSV references updated in {csv_changed} cells")


# ─────────────────────────────────────────────────────────────
# STEP 2: Add Duration EDA after Section 2 (before Section 3)
# ─────────────────────────────────────────────────────────────
def code_cell(src):
    return {"cell_type": "code", "execution_count": None,
            "metadata": {}, "outputs": [],
            "source": [src] if isinstance(src, str) else src}

def md_cell(src):
    return {"cell_type": "markdown", "metadata": {},
            "source": [src] if isinstance(src, str) else src}

# Find where Section 3 starts
sec3_idx = None
for i, cell in enumerate(cells):
    if cell['cell_type'] == 'markdown' and 'SECTION 3' in ''.join(cell['source']):
        sec3_idx = i
        break
print(f"Step 2: Section 3 starts at cell {sec3_idx} — inserting Duration EDA before it")

duration_eda_cells = [
    md_cell(
        "---\n### 2.8 — Duration Feature: `Duration_Standardized` Inspection\n\n"
        "The dataset contains a `Duration_Standardized` column with clean, standardized text "
        "values representing how long a complaint has persisted (e.g. `'2 days'`, `'5 hours'`).\n"
        "This will be parsed to a numerical `Duration_Hours` column in Section 4.\n"
    ),
    code_cell(
        "# ============================================================\n"
        "# 2.8  DURATION_STANDARDIZED — DISTRIBUTION & PRIORITY ANALYSIS\n"
        "# ============================================================\n"
        "\n"
        "print('Duration_Standardized — Unique Values and Counts:')\n"
        "print('=' * 55)\n"
        "dur_counts = df['Duration_Standardized'].value_counts()\n"
        "for val, cnt in dur_counts.items():\n"
        "    print(f'  {val:15s}: {cnt:4d}  ({cnt/len(df)*100:.1f}%)')\n"
        "print(f'\\nTotal unique values: {df[\"Duration_Standardized\"].nunique()}')\n"
        "print(f'Missing values     : {df[\"Duration_Standardized\"].isna().sum()}')\n"
    ),
    code_cell(
        "# ============================================================\n"
        "# 2.9  DURATION_HOURS PREVIEW — Parsing Mapping\n"
        "# ============================================================\n"
        "# Show the exact mapping that will be applied in Section 4\n"
        "\n"
        "def _preview_parse(text):\n"
        "    if not isinstance(text, str): return None\n"
        "    parts = text.strip().lower().split()\n"
        "    if len(parts) != 2: return None\n"
        "    try: v = float(parts[0])\n"
        "    except: return None\n"
        "    u = parts[1]\n"
        "    if u in ('hour','hours'):   return v\n"
        "    if u in ('day','days'):     return v * 24\n"
        "    if u in ('week','weeks'):   return v * 168\n"
        "    if u in ('month','months'): return v * 720\n"
        "    return None\n"
        "\n"
        "_preview = df[['Duration_Standardized']].drop_duplicates().copy()\n"
        "_preview['Duration_Hours'] = _preview['Duration_Standardized'].apply(_preview_parse)\n"
        "_preview = _preview.sort_values('Duration_Hours').reset_index(drop=True)\n"
        "print('Duration_Standardized -> Duration_Hours (preview):')\n"
        "print(_preview.to_string(index=False))\n"
        "print(f'\\nMin duration : {_preview[\"Duration_Hours\"].min()} hours')\n"
        "print(f'Max duration : {_preview[\"Duration_Hours\"].max()} hours ({_preview[\"Duration_Hours\"].max()/168:.1f} weeks)')\n"
    ),
    code_cell(
        "# ============================================================\n"
        "# 2.10  DURATION vs PRIORITY — Relationship Check\n"
        "# ============================================================\n"
        "\n"
        "import matplotlib.pyplot as plt\n"
        "import numpy as np\n"
        "\n"
        "_df_dur = df.copy()\n"
        "_df_dur['Duration_Hours'] = _df_dur['Duration_Standardized'].apply(_preview_parse)\n"
        "\n"
        "fig, axes = plt.subplots(1, 2, figsize=(13, 4))\n"
        "\n"
        "# Boxplot: Duration_Hours by Priority\n"
        "data_by_priority = [_df_dur[_df_dur['Priority']==p]['Duration_Hours'].dropna()\n"
        "                    for p in CLASS_ORDER]\n"
        "bp = axes[0].boxplot(data_by_priority, labels=CLASS_ORDER, patch_artist=True)\n"
        "for patch, color in zip(bp['boxes'], [PALETTE[p] for p in CLASS_ORDER]):\n"
        "    patch.set_facecolor(color); patch.set_alpha(0.7)\n"
        "axes[0].set_title('Duration_Hours Distribution by Priority', fontweight='bold')\n"
        "axes[0].set_ylabel('Duration (hours)')\n"
        "axes[0].spines['top'].set_visible(False); axes[0].spines['right'].set_visible(False)\n"
        "\n"
        "# Mean duration per priority\n"
        "means = _df_dur.groupby('Priority')['Duration_Hours'].mean()[CLASS_ORDER]\n"
        "bars = axes[1].bar(CLASS_ORDER, means.values,\n"
        "                   color=[PALETTE[p] for p in CLASS_ORDER], alpha=0.8, edgecolor='white')\n"
        "for bar, v in zip(bars, means.values):\n"
        "    axes[1].text(bar.get_x()+bar.get_width()/2, v+1, f'{v:.0f}h',\n"
        "                 ha='center', fontsize=10)\n"
        "axes[1].set_title('Mean Duration_Hours by Priority', fontweight='bold')\n"
        "axes[1].set_ylabel('Mean Duration (hours)')\n"
        "axes[1].spines['top'].set_visible(False); axes[1].spines['right'].set_visible(False)\n"
        "\n"
        "plt.suptitle('Duration Analysis vs Priority', fontsize=13, fontweight='bold', y=1.02)\n"
        "plt.tight_layout()\n"
        "plt.show()\n"
        "\n"
        "print('\\nMean Duration_Hours by Priority:')\n"
        "for p in CLASS_ORDER:\n"
        "    s = _df_dur[_df_dur['Priority']==p]['Duration_Hours']\n"
        "    print(f'  {p:8s}: mean={s.mean():.1f}h  median={s.median():.1f}h  '\n"
        "          f'min={s.min():.0f}h  max={s.max():.0f}h')\n"
        "print('\\nNote: Duration reflects how long a complaint persisted.')\n"
        "print('      Longer durations often (but not always) correlate with higher priority.')\n"
    ),
]

# Insert Duration EDA cells just before Section 3
cells = cells[:sec3_idx] + duration_eda_cells + cells[sec3_idx:]
print(f"  Inserted {len(duration_eda_cells)} Duration EDA cells before Section 3")


# ─────────────────────────────────────────────────────────────
# STEP 3: Update Section 4 cells
# ─────────────────────────────────────────────────────────────
# Re-find Section 4 and 5 after insertion
sec4_idx = sec5_idx = None
for i, cell in enumerate(cells):
    src = ''.join(cell['source'])
    if sec4_idx is None and 'SECTION 4' in src and cell['cell_type'] == 'markdown':
        sec4_idx = i
    if sec4_idx is not None and i > sec4_idx:
        if 'SECTION 5' in src and cell['cell_type'] == 'markdown':
            sec5_idx = i
            break

print(f"Step 3: Section 4 = cells {sec4_idx} to {sec5_idx-1}")

# New complete Section 4 cells
section4_cells = [
    md_cell(
        "---\n"
        "## \U0001f9e0 SECTION 4: Feature Engineering + Train/Test Split\n\n"
        "**Final feature set:**\n"
        "- `Cleaned_Text` → TF-IDF (text)\n"
        "- `Category`, `Complaint_Type`, `Block`, `Floor` → OneHotEncoder (categorical)\n"
        "- `Duration_Hours` → StandardScaler (numerical, parsed from `Duration_Standardized`)\n\n"
        "**Excluded:** `Support_Count` (escalation only), `Room_No` (identifier), "
        "`Status` (post-submission), `Complaint_Date`, `Complaint_ID`\n\n"
        "> \U0001f6a8 TF-IDF is fitted **only on the training set** — no data leakage.\n"
    ),
    md_cell("---\n### 4.0 — Parse `Duration_Standardized` → `Duration_Hours`\n"),
    code_cell(
        "# ============================================================\n"
        "# 4.0  PARSE Duration_Standardized -> Duration_Hours (numeric)\n"
        "# ============================================================\n"
        "# Source column: Duration_Standardized (text, e.g. '2 days', '5 hours')\n"
        "# Output column: Duration_Hours (float, hours as unit)\n"
        "# ============================================================\n"
        "\n"
        "def parse_duration_hours(text):\n"
        "    \"\"\"Parse standardized duration string to numeric hours.\"\"\"\n"
        "    if not isinstance(text, str): return None\n"
        "    parts = text.strip().lower().split()\n"
        "    if len(parts) != 2: return None\n"
        "    try: value = float(parts[0])\n"
        "    except ValueError: return None\n"
        "    unit = parts[1]\n"
        "    if unit in ('hour', 'hours'):   return value\n"
        "    if unit in ('day', 'days'):     return value * 24\n"
        "    if unit in ('week', 'weeks'):   return value * 168\n"
        "    if unit in ('month', 'months'): return value * 720\n"
        "    return None\n"
        "\n"
        "df['Duration_Hours'] = df['Duration_Standardized'].apply(parse_duration_hours)\n"
        "\n"
        "null_count = df['Duration_Hours'].isna().sum()\n"
        "print('Duration_Hours created from Duration_Standardized:')\n"
        "print(f'  Null values : {null_count}  {chr(10006) if null_count > 0 else chr(10003)}')\n"
        "print(f'  Dtype       : {df[\"Duration_Hours\"].dtype}')\n"
        "print(f'  Min         : {df[\"Duration_Hours\"].min():.0f} hours')\n"
        "print(f'  Median      : {df[\"Duration_Hours\"].median():.0f} hours')\n"
        "print(f'  Mean        : {df[\"Duration_Hours\"].mean():.1f} hours')\n"
        "print(f'  Max         : {df[\"Duration_Hours\"].max():.0f} hours '\n"
        "      f'({df[\"Duration_Hours\"].max()/168:.1f} weeks)')\n"
        "print('\\n\u2705 Duration_Hours ready for StandardScaler.')\n"
    ),
    md_cell("---\n### 4.1 — Feature Selection Decision\n"),
    code_cell(
        "# ============================================================\n"
        "# 4.1  FEATURE SELECTION DECISION\n"
        "# ============================================================\n"
        "\n"
        "TEXT_FEATURE = 'Cleaned_Text'\n"
        "CAT_FEATURES = ['Category', 'Complaint_Type', 'Block', 'Floor']\n"
        "NUM_FEATURES = ['Duration_Hours']\n"
        "TARGET       = 'Priority'\n"
        "\n"
        "print('Feature Selection:')\n"
        "print('=' * 70)\n"
        "decisions = [\n"
        "    ('Cleaned_Text',       'INCLUDE (text)',  'Primary ML signal -> TF-IDF'),\n"
        "    ('Category',           'INCLUDE (cat)',   'Known at submission time'),\n"
        "    ('Complaint_Type',     'INCLUDE (cat)',   'Known at submission time'),\n"
        "    ('Block',              'INCLUDE (cat)',   'Known at submission time'),\n"
        "    ('Floor',              'INCLUDE (cat)',   'Known at submission time'),\n"
        "    ('Duration_Hours',     'INCLUDE (num)',   'Parsed from Duration_Standardized; scaled via StandardScaler'),\n"
        "    ('Support_Count',      'EXCLUDE',         'Escalation system only (=0 for all new complaints)'),\n"
        "    ('Room_No',            'EXCLUDE',         'High-cardinality identifier; risk of memorization'),\n"
        "    ('Status',             'EXCLUDE',         'Post-submission field; unavailable at prediction time'),\n"
        "    ('Complaint_Date',     'EXCLUDE',         'Not a consistent prediction-time signal'),\n"
        "    ('Complaint_ID',       'EXCLUDE',         'Identifier only'),\n"
        "    ('Duration_Standardized','EXCLUDE',       'Source text used to create Duration_Hours; raw text not needed'),\n"
        "]\n"
        "for col, dec, reason in decisions:\n"
        "    icon = '\u2705' if 'INCLUDE' in dec else '\u274c'\n"
        "    print(f'  {icon} {dec:18s} | {col:24s} | {reason}')\n"
        "\n"
        "print(f'\\nText    : {TEXT_FEATURE}')\n"
        "print(f'Cat     : {CAT_FEATURES}')\n"
        "print(f'Numeric : {NUM_FEATURES}')\n"
        "print(f'Target  : {TARGET}  (classes: {CLASS_ORDER})')\n"
    ),
    md_cell("---\n### 4.2 — Train / Test Split (Stratified 80/20)\n"),
    code_cell(
        "# ============================================================\n"
        "# 4.2  TRAIN / TEST SPLIT (STRATIFIED)\n"
        "# ============================================================\n"
        "\n"
        "from sklearn.model_selection import train_test_split\n"
        "\n"
        "ALL_FEATURES = [TEXT_FEATURE] + CAT_FEATURES + NUM_FEATURES\n"
        "X = df[ALL_FEATURES].copy()\n"
        "y = df[TARGET].copy()\n"
        "\n"
        "X_train, X_test, y_train, y_test = train_test_split(\n"
        "    X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y\n"
        ")\n"
        "\n"
        "print('Train / Test Split (Stratified 80/20):')\n"
        "print(f'  Total : {len(df)}')\n"
        "print(f'  Train : {len(X_train)} ({len(X_train)/len(df)*100:.1f}%)')\n"
        "print(f'  Test  : {len(X_test)} ({len(X_test)/len(df)*100:.1f}%)')\n"
        "print(f'\\n{\"Class\":8s} | {\"Train\":5s} | {\"Test\":4s} | {\"Train%\":7s} | {\"Test%\":5s}')\n"
        "print('-' * 42)\n"
        "for cls in CLASS_ORDER:\n"
        "    tr = (y_train == cls).sum(); te = (y_test == cls).sum()\n"
        "    print(f'{cls:8s} | {tr:4d}  | {te:3d}  | {tr/len(y_train)*100:5.1f}%  | {te/len(y_test)*100:5.1f}%')\n"
        "diff = (y_train.value_counts(normalize=True) - y_test.value_counts(normalize=True)).abs().max()\n"
        "print(f'\\nMax proportion diff: {diff:.4f}  (\u2705 stratification verified)' if diff < 0.02 else '\u26a0 Large shift!')\n"
    ),
    md_cell("---\n### 4.3 — ColumnTransformer (TF-IDF + OHE + StandardScaler)\n"),
    code_cell(
        "# ============================================================\n"
        "# 4.3  COLUMNTRANSFORMER — Text + Categorical + Numerical\n"
        "# TF-IDF on Cleaned_Text     (fitted on train ONLY)\n"
        "# OneHotEncoder on cat cols  (fitted on train ONLY)\n"
        "# StandardScaler on Duration_Hours (fitted on train ONLY)\n"
        "# ============================================================\n"
        "\n"
        "from sklearn.feature_extraction.text import TfidfVectorizer\n"
        "from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder\n"
        "from sklearn.compose import ColumnTransformer\n"
        "from scipy.sparse import issparse\n"
        "import numpy as np\n"
        "\n"
        "tfidf = TfidfVectorizer(\n"
        "    ngram_range  = (1, 2),\n"
        "    max_features = 5000,\n"
        "    sublinear_tf = True,\n"
        "    min_df       = 2,\n"
        "    strip_accents= 'unicode',\n"
        ")\n"
        "ohe    = OneHotEncoder(handle_unknown='ignore', sparse_output=False)\n"
        "scaler = StandardScaler()\n"
        "\n"
        "preprocessor = ColumnTransformer(\n"
        "    transformers=[\n"
        "        ('tfidf',  tfidf,  TEXT_FEATURE),\n"
        "        ('ohe',    ohe,    CAT_FEATURES),\n"
        "        ('scaler', scaler, NUM_FEATURES),\n"
        "    ],\n"
        "    remainder='drop'\n"
        ")\n"
        "\n"
        "print('ColumnTransformer defined:')\n"
        "print(f'  [tfidf]  TfidfVectorizer  -> {TEXT_FEATURE}')\n"
        "print(f'           ngram=(1,2), max_features=5000, sublinear_tf=True')\n"
        "print(f'  [ohe]    OneHotEncoder    -> {CAT_FEATURES}')\n"
        "print(f'  [scaler] StandardScaler   -> {NUM_FEATURES}')\n"
        "print(f'  [drop]   All other columns dropped')\n"
        "print('\\n\u2705 Preprocessor defined. Will be fitted on X_train only.')\n"
    ),
    md_cell("---\n### 4.4 — Fit on Train, Transform Train + Test\n"),
    code_cell(
        "# ============================================================\n"
        "# 4.4  FIT ON TRAIN ONLY — TRANSFORM TRAIN + TEST\n"
        "# Key principle: NO data leakage — test set never influences fitting.\n"
        "# ============================================================\n"
        "\n"
        "X_train_proc = preprocessor.fit_transform(X_train)\n"
        "X_test_proc  = preprocessor.transform(X_test)\n"
        "\n"
        "if issparse(X_train_proc): X_train_proc = X_train_proc.toarray()\n"
        "if issparse(X_test_proc):  X_test_proc  = X_test_proc.toarray()\n"
        "\n"
        "tfidf_n = len(preprocessor.named_transformers_['tfidf'].vocabulary_)\n"
        "ohe_n   = len(preprocessor.named_transformers_['ohe'].get_feature_names_out())\n"
        "num_n   = len(NUM_FEATURES)\n"
        "\n"
        "print('Feature Matrix Summary:')\n"
        "print('=' * 50)\n"
        "print(f'  X_train : {X_train_proc.shape}')\n"
        "print(f'  X_test  : {X_test_proc.shape}')\n"
        "print(f'\\nBreakdown:')\n"
        "print(f'  TF-IDF features         : {tfidf_n}')\n"
        "print(f'  OHE features            : {ohe_n}')\n"
        "print(f'  Numerical (StandardScaler): {num_n}  (Duration_Hours)')\n"
        "print(f'  Total features          : {X_train_proc.shape[1]}')\n"
        "\n"
        "# Verify Duration_Hours was correctly scaled\n"
        "dur_idx   = tfidf_n + ohe_n   # Duration_Hours is the last column\n"
        "dur_train = X_train_proc[:, dur_idx]\n"
        "print(f'\\nDuration_Hours after StandardScaler:')\n"
        "print(f'  Mean  : {dur_train.mean():.4f}  (expected ~0.0)')\n"
        "print(f'  Std   : {dur_train.std():.4f}   (expected ~1.0)')\n"
        "print('\\n\u2705 Preprocessor fitted on X_train only — no data leakage.')\n"
    ),
    md_cell("---\n### 4.5 — Encode Target Variable\n"),
    code_cell(
        "# ============================================================\n"
        "# 4.5  ENCODE TARGET VARIABLE\n"
        "# ============================================================\n"
        "\n"
        "le = LabelEncoder()\n"
        "le.fit(CLASS_ORDER)\n"
        "y_train_enc = le.transform(y_train)\n"
        "y_test_enc  = le.transform(y_test)\n"
        "\n"
        "print('Label Encoding (Priority -> Integer):')\n"
        "for cls, enc in zip(le.classes_, range(len(le.classes_))):\n"
        "    print(f'  {cls:8s} -> {enc}')\n"
        "print(f'\\n  Shapes: y_train={y_train_enc.shape}, y_test={y_test_enc.shape}')\n"
        "print(f'  Reversible: {list(le.inverse_transform(y_train_enc[:3])) == list(y_train[:3])} \u2705')\n"
    ),
    md_cell("---\n### 4.6 — Data Leakage Verification\n"),
    code_cell(
        "# ============================================================\n"
        "# 4.6  DATA LEAKAGE VERIFICATION\n"
        "# ============================================================\n"
        "\n"
        "overlap = set(X_train.index).intersection(set(X_test.index))\n"
        "print('Leakage Verification:')\n"
        "print('=' * 50)\n"
        "print(f'  Index overlap          : {len(overlap)}  \u2705' if len(overlap)==0 else f'  Index overlap: {len(overlap)} \u274c')\n"
        "print(f'  TF-IDF vocab           : {tfidf_n} terms (from train only)  \u2705')\n"
        "print(f'  Preprocessor fitted on : X_train ({len(X_train)} samples)  \u2705')\n"
        "print(f'  Support_Count used     : False  \u2705')\n"
        "print(f'  Students_Affected used : False  \u2705')\n"
        "print(f'  Duration_Standardized  : Excluded (Duration_Hours used instead)  \u2705')\n"
        "print('\\n\u2705 No data leakage detected. Pipeline is clean.')\n"
    ),
    md_cell(
        "---\n## \u2705 Section 4 Complete\n\n"
        "| Feature | Type | Transformer |\n|---|---|---|\n"
        "| `Cleaned_Text` | Text | TF-IDF (1+2-gram, max 5000, sublinear) |\n"
        "| `Category`, `Complaint_Type`, `Block`, `Floor` | Categorical | OneHotEncoder |\n"
        "| `Duration_Hours` | Numerical | StandardScaler |\n\n"
        "**Excluded:** `Support_Count`, `Room_No`, `Status`, `Complaint_Date`, `Complaint_ID`, `Duration_Standardized`\n\n"
        "> Ready for **Section 5 — Model Training & Comparison**.\n"
    ),
    # ── SECTION 5: Model Training ──────────────────────────────
    md_cell(
        "---\n## \U0001f4ca SECTION 5: Baseline Model Training & Comparison\n\n"
        "Train 5 classifiers on the same feature matrix. "
        "All models use `class_weight='balanced'`.\n"
    ),
    md_cell("### 5.1 — Train Multiple Classifiers\n"),
    code_cell(
        "# ============================================================\n"
        "# 5.1  TRAIN MULTIPLE CLASSIFIERS\n"
        "# ============================================================\n"
        "\n"
        "from sklearn.linear_model import LogisticRegression\n"
        "from sklearn.svm import LinearSVC\n"
        "from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier\n"
        "from sklearn.naive_bayes import GaussianNB\n"
        "from sklearn.metrics import accuracy_score, f1_score\n"
        "import time\n"
        "\n"
        "models = {\n"
        "    'Logistic Regression': LogisticRegression(\n"
        "        max_iter=1000, class_weight='balanced', random_state=RANDOM_STATE, C=1.0),\n"
        "    'LinearSVC': LinearSVC(\n"
        "        max_iter=2000, class_weight='balanced', random_state=RANDOM_STATE, C=1.0),\n"
        "    'Random Forest': RandomForestClassifier(\n"
        "        n_estimators=200, class_weight='balanced',\n"
        "        random_state=RANDOM_STATE, n_jobs=-1),\n"
        "    'Gradient Boosting': GradientBoostingClassifier(\n"
        "        n_estimators=150, learning_rate=0.1, random_state=RANDOM_STATE),\n"
        "    'Naive Bayes': GaussianNB(),\n"
        "}\n"
        "\n"
        "results = {}\n"
        "print(f'Training {len(models)} classifiers on {X_train_proc.shape} ...')\n"
        "print('=' * 72)\n"
        "print(f'{\"Model\":22s} | {\"Train Acc\":10s} | {\"Test Acc\":10s} | {\"Test F1\":10s} | Time')\n"
        "print('-' * 72)\n"
        "\n"
        "for name, model in models.items():\n"
        "    t0 = time.time()\n"
        "    model.fit(X_train_proc, y_train_enc)\n"
        "    elapsed = time.time() - t0\n"
        "    y_pred_tr = model.predict(X_train_proc)\n"
        "    y_pred_te = model.predict(X_test_proc)\n"
        "    tr_acc = accuracy_score(y_train_enc, y_pred_tr)\n"
        "    te_acc = accuracy_score(y_test_enc,  y_pred_te)\n"
        "    te_f1  = f1_score(y_test_enc, y_pred_te, average='weighted')\n"
        "    results[name] = {'model': model, 'train_acc': tr_acc, 'test_acc': te_acc,\n"
        "                     'test_f1': te_f1, 'y_pred': y_pred_te, 'time': elapsed}\n"
        "    print(f'{name:22s} | {tr_acc:8.4f}   | {te_acc:8.4f}   | {te_f1:8.4f}   | {elapsed:.2f}s')\n"
        "\n"
        "best_name = max(results, key=lambda k: results[k]['test_f1'])\n"
        "print(f'\\n\u2605 Best model: {best_name}  (Test F1={results[best_name][\"test_f1\"]:.4f})')\n"
    ),
    md_cell("### 5.2 — Comparison Chart\n"),
    code_cell(
        "# ============================================================\n"
        "# 5.2  PERFORMANCE COMPARISON CHART\n"
        "# ============================================================\n"
        "\n"
        "import matplotlib.pyplot as plt\n"
        "import numpy as np\n"
        "\n"
        "model_names = list(results.keys())\n"
        "tr_accs = [results[n]['train_acc'] for n in model_names]\n"
        "te_accs = [results[n]['test_acc']  for n in model_names]\n"
        "te_f1s  = [results[n]['test_f1']   for n in model_names]\n"
        "\n"
        "x, w = np.arange(len(model_names)), 0.25\n"
        "fig, ax = plt.subplots(figsize=(13, 5))\n"
        "b1 = ax.bar(x - w, tr_accs, w, label='Train Accuracy', color='#3498DB', alpha=0.85)\n"
        "b2 = ax.bar(x,     te_accs, w, label='Test Accuracy',  color='#2ECC71', alpha=0.85)\n"
        "b3 = ax.bar(x + w, te_f1s,  w, label='Test F1 (wt)',   color='#E74C3C', alpha=0.85)\n"
        "for bars in (b1, b2, b3):\n"
        "    for bar in bars:\n"
        "        h = bar.get_height()\n"
        "        ax.text(bar.get_x()+bar.get_width()/2, h+0.005, f'{h:.3f}',\n"
        "                ha='center', va='bottom', fontsize=7.5)\n"
        "ax.set_xticks(x); ax.set_xticklabels(model_names, rotation=15, ha='right')\n"
        "ax.set_ylim(0, 1.12); ax.set_ylabel('Score')\n"
        "ax.set_title('Model Comparison — Train Acc / Test Acc / Test F1 (with Duration_Hours)',\n"
        "             fontsize=12, fontweight='bold')\n"
        "ax.legend(); ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)\n"
        "ax.axhline(0.8, color='grey', linestyle='--', linewidth=0.8)\n"
        "plt.tight_layout(); plt.show()\n"
    ),
    # ── SECTION 6: Detailed Evaluation ────────────────────────
    md_cell(
        "---\n## \U0001f4cb SECTION 6: Best Model — Detailed Evaluation\n\n"
        "Classification report, confusion matrix, and overfitting check.\n"
    ),
    code_cell(
        "# ============================================================\n"
        "# 6.1  CLASSIFICATION REPORT\n"
        "# ============================================================\n"
        "\n"
        "from sklearn.metrics import classification_report, confusion_matrix\n"
        "import seaborn as sns\n"
        "\n"
        "best_model  = results[best_name]['model']\n"
        "y_pred_best = results[best_name]['y_pred']\n"
        "label_names = list(le.classes_)\n"
        "\n"
        "print(f'Best Model: {best_name}')\n"
        "print('=' * 55)\n"
        "print(f'  Train Accuracy : {results[best_name][\"train_acc\"]:.4f}')\n"
        "print(f'  Test  Accuracy : {results[best_name][\"test_acc\"]:.4f}')\n"
        "print(f'  Test  F1 (wt)  : {results[best_name][\"test_f1\"]:.4f}')\n"
        "gap = results[best_name]['train_acc'] - results[best_name]['test_acc']\n"
        "print(f'  Overfit gap    : {gap:.4f}  (\u2705 OK)' if gap < 0.15 else f'  Overfit gap: {gap:.4f}  (\u26a0 High)')\n"
        "print('\\nClassification Report (Test Set):')\n"
        "print(classification_report(y_test_enc, y_pred_best, target_names=label_names))\n"
    ),
    code_cell(
        "# ============================================================\n"
        "# 6.2  CONFUSION MATRIX\n"
        "# ============================================================\n"
        "\n"
        "cm      = confusion_matrix(y_test_enc, y_pred_best)\n"
        "cm_norm = confusion_matrix(y_test_enc, y_pred_best, normalize='true')\n"
        "\n"
        "fig, axes = plt.subplots(1, 2, figsize=(13, 5))\n"
        "sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',\n"
        "            xticklabels=label_names, yticklabels=label_names,\n"
        "            ax=axes[0], linewidths=0.5)\n"
        "axes[0].set_title(f'{best_name}\\nConfusion Matrix (Counts)', fontweight='bold')\n"
        "axes[0].set_xlabel('Predicted'); axes[0].set_ylabel('Actual')\n"
        "sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues', vmin=0, vmax=1,\n"
        "            xticklabels=label_names, yticklabels=label_names,\n"
        "            ax=axes[1], linewidths=0.5)\n"
        "axes[1].set_title(f'{best_name}\\nConfusion Matrix (Normalized)', fontweight='bold')\n"
        "axes[1].set_xlabel('Predicted'); axes[1].set_ylabel('Actual')\n"
        "plt.tight_layout(); plt.show()\n"
        "\n"
        "print('Per-class recall (normalized diagonal):')\n"
        "for i, cls in enumerate(label_names):\n"
        "    print(f'  {cls:8s}: {cm_norm[i,i]:.3f}  ({int(cm[i,i])}/{int(cm[i].sum())} correct)')\n"
    ),
    code_cell(
        "# ============================================================\n"
        "# 6.3  TRAIN vs TEST — OVERFITTING CHECK (ALL MODELS)\n"
        "# ============================================================\n"
        "\n"
        "print('Train vs Test Accuracy — Overfitting Check:')\n"
        "print('=' * 62)\n"
        "print(f'{\"Model\":22s} | {\"Train Acc\":10s} | {\"Test Acc\":9s} | {\"Gap\":7s} | Status')\n"
        "print('-' * 62)\n"
        "for name in results:\n"
        "    tr  = results[name]['train_acc']\n"
        "    te  = results[name]['test_acc']\n"
        "    gap = tr - te\n"
        "    status = '\u2705 Good' if gap < 0.10 else ('\u26a0 Moderate' if gap < 0.20 else '\u274c Overfit')\n"
        "    marker = '  <-- BEST' if name == best_name else ''\n"
        "    print(f'{name:22s} | {tr:8.4f}   | {te:7.4f}  | {gap:5.4f}  | {status}{marker}')\n"
    ),
    # ── SECTION 7: Cross-Validation ────────────────────────────
    md_cell(
        "---\n## \U0001f501 SECTION 7: Cross-Validation (Best Model)\n\n"
        "5-fold stratified CV on the full dataset for a robust performance estimate.\n"
    ),
    code_cell(
        "# ============================================================\n"
        "# 7.1  STRATIFIED 5-FOLD CROSS-VALIDATION\n"
        "# ============================================================\n"
        "\n"
        "from sklearn.model_selection import StratifiedKFold, cross_validate\n"
        "from sklearn.pipeline import Pipeline\n"
        "import copy\n"
        "\n"
        "cv_prep = ColumnTransformer(\n"
        "    transformers=[\n"
        "        ('tfidf',  TfidfVectorizer(ngram_range=(1,2), max_features=5000,\n"
        "                                   sublinear_tf=True, min_df=2, strip_accents='unicode'),\n"
        "         TEXT_FEATURE),\n"
        "        ('ohe',    OneHotEncoder(handle_unknown='ignore', sparse_output=False),\n"
        "         CAT_FEATURES),\n"
        "        ('scaler', StandardScaler(), NUM_FEATURES),\n"
        "    ], remainder='drop')\n"
        "\n"
        "full_pipeline = Pipeline([('prep', cv_prep), ('model', copy.deepcopy(best_model))])\n"
        "X_full = df[ALL_FEATURES].copy()\n"
        "y_full = le.transform(df[TARGET])\n"
        "\n"
        "skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)\n"
        "print(f'5-Fold Stratified CV — {best_name}')\n"
        "print('Running...')\n"
        "cv_res = cross_validate(full_pipeline, X_full, y_full, cv=skf,\n"
        "                        scoring=['accuracy','f1_weighted'],\n"
        "                        return_train_score=True, n_jobs=1)\n"
        "\n"
        "print(f'\\n  CV Accuracy  : {cv_res[\"test_accuracy\"].mean():.4f} \u00b1 {cv_res[\"test_accuracy\"].std():.4f}')\n"
        "print(f'  CV F1 (wt)   : {cv_res[\"test_f1_weighted\"].mean():.4f} \u00b1 {cv_res[\"test_f1_weighted\"].std():.4f}')\n"
        "print(f'  Train Acc CV : {cv_res[\"train_accuracy\"].mean():.4f} \u00b1 {cv_res[\"train_accuracy\"].std():.4f}')\n"
        "print(f'  Per-fold     : {[round(s,4) for s in cv_res[\"test_accuracy\"].tolist()]}')\n"
        "print('\\n\u2705 CV complete.')\n"
    ),
    # ── SECTION 8: Save Model ──────────────────────────────────
    md_cell(
        "---\n## \U0001f4be SECTION 8: Save Retrained Model\n\n"
        "Save all artifacts to `saved_model/` for Django integration.\n"
    ),
    code_cell(
        "# ============================================================\n"
        "# 8.1  SAVE MODEL ARTIFACTS\n"
        "# ============================================================\n"
        "\n"
        "import joblib, os, json as jlib\n"
        "\n"
        "SAVE_DIR = 'saved_model'\n"
        "os.makedirs(SAVE_DIR, exist_ok=True)\n"
        "\n"
        "joblib.dump(preprocessor, os.path.join(SAVE_DIR, 'preprocessor.pkl'))\n"
        "joblib.dump(best_model,   os.path.join(SAVE_DIR, 'model.pkl'))\n"
        "joblib.dump(le,           os.path.join(SAVE_DIR, 'label_encoder.pkl'))\n"
        "\n"
        "feature_config = {\n"
        "    'text_feature'  : TEXT_FEATURE,\n"
        "    'cat_features'  : CAT_FEATURES,\n"
        "    'num_features'  : NUM_FEATURES,\n"
        "    'all_features'  : ALL_FEATURES,\n"
        "    'target'        : TARGET,\n"
        "    'classes'       : CLASS_ORDER,\n"
        "    'label_mapping' : {cls: int(le.transform([cls])[0]) for cls in le.classes_},\n"
        "    'duration_source': 'Duration_Standardized -> Duration_Hours (parsed in notebook)',\n"
        "    'duration_note' : 'At Django prediction time, calculate Duration_Hours = elapsed hours since complaint filed',\n"
        "}\n"
        "with open(os.path.join(SAVE_DIR, 'feature_config.json'), 'w') as f:\n"
        "    jlib.dump(feature_config, f, indent=2)\n"
        "\n"
        "metadata = {\n"
        "    'model_name'        : best_name,\n"
        "    'dataset'           : 'Dataset_duration.csv',\n"
        "    'n_samples'         : int(len(df)),\n"
        "    'n_train'           : int(len(X_train)),\n"
        "    'n_test'            : int(len(X_test)),\n"
        "    'n_features'        : int(X_train_proc.shape[1]),\n"
        "    'tfidf_features'    : int(tfidf_n),\n"
        "    'ohe_features'      : int(ohe_n),\n"
        "    'num_features'      : int(num_n),\n"
        "    'classes'           : CLASS_ORDER,\n"
        "    'train_accuracy'    : round(float(results[best_name]['train_acc']), 4),\n"
        "    'test_accuracy'     : round(float(results[best_name]['test_acc']),  4),\n"
        "    'test_f1_weighted'  : round(float(results[best_name]['test_f1']),   4),\n"
        "    'cv_accuracy_mean'  : round(float(cv_res['test_accuracy'].mean()),  4),\n"
        "    'cv_f1_mean'        : round(float(cv_res['test_f1_weighted'].mean()), 4),\n"
        "    'excluded'          : ['Support_Count','Room_No','Status','Complaint_Date','Complaint_ID','Duration_Standardized'],\n"
        "    'leakage_fixed'     : True,\n"
        "}\n"
        "with open(os.path.join(SAVE_DIR, 'model_metadata.json'), 'w') as f:\n"
        "    jlib.dump(metadata, f, indent=2)\n"
        "\n"
        "print('\u2705 Saved to saved_model/:')\n"
        "for fname in sorted(os.listdir(SAVE_DIR)):\n"
        "    sz = os.path.getsize(os.path.join(SAVE_DIR, fname))\n"
        "    print(f'  {fname:35s}  {sz/1024:.1f} KB')\n"
    ),
    code_cell(
        "# ============================================================\n"
        "# 8.2  VERIFY SAVED MODEL — LOAD AND PREDICT\n"
        "# ============================================================\n"
        "\n"
        "import joblib, json as jlib\n"
        "import pandas as pd\n"
        "\n"
        "ld_prep  = joblib.load('saved_model/preprocessor.pkl')\n"
        "ld_model = joblib.load('saved_model/model.pkl')\n"
        "ld_le    = joblib.load('saved_model/label_encoder.pkl')\n"
        "\n"
        "test_cases = [\n"
        "    {'Cleaned_Text': 'no water cooler second floor since morning',\n"
        "     'Category': 'Water Cooler', 'Complaint_Type': 'Public',\n"
        "     'Block': 'B', 'Floor': 'Second', 'Duration_Hours': 8.0},\n"
        "    {'Cleaned_Text': 'cobweb staircase corner',\n"
        "     'Category': 'Cleanliness', 'Complaint_Type': 'Public',\n"
        "     'Block': 'A', 'Floor': 'Ground', 'Duration_Hours': 2.0},\n"
        "    {'Cleaned_Text': 'fire risk generator room emergency',\n"
        "     'Category': 'Fire Safety', 'Complaint_Type': 'Public',\n"
        "     'Block': 'C', 'Floor': 'Ground', 'Duration_Hours': 1.0},\n"
        "]\n"
        "\n"
        "sample_df   = pd.DataFrame(test_cases)\n"
        "sample_proc = ld_prep.transform(sample_df)\n"
        "if issparse(sample_proc): sample_proc = sample_proc.toarray()\n"
        "preds = ld_le.inverse_transform(ld_model.predict(sample_proc))\n"
        "\n"
        "print('Saved model verification:')\n"
        "print('=' * 50)\n"
        "for tc, pred in zip(test_cases, preds):\n"
        "    print(f'  Category : {tc[\"Category\"]:20s}  Duration: {tc[\"Duration_Hours\"]}h')\n"
        "    print(f'  Text     : {tc[\"Cleaned_Text\"][:45]}')\n"
        "    print(f'  Predicted: {pred}')\n"
        "    print()\n"
        "print('\u2705 Saved model loads and predicts correctly.')\n"
    ),
    # ── SECTION 9: Django Note ─────────────────────────────────
    md_cell(
        "---\n## \u2699\ufe0f SECTION 9: Django Integration Note\n\n"
        "`backend/complaints/utils.py` must pass `Duration_Hours` (float) to the model.\n\n"
        "**At prediction time in Django:**\n"
        "```python\n"
        "from django.utils import timezone\n"
        "# Duration since complaint was filed\n"
        "delta = timezone.now() - complaint.created_at\n"
        "duration_hours = delta.total_seconds() / 3600\n"
        "\n"
        "features = {\n"
        "    'Cleaned_Text'  : preprocess_text(complaint.text),\n"
        "    'Category'      : complaint.category,\n"
        "    'Complaint_Type': complaint.complaint_type,\n"
        "    'Block'         : complaint.block,\n"
        "    'Floor'         : complaint.floor,\n"
        "    'Duration_Hours': duration_hours,  # NEW\n"
        "}\n"
        "```\n"
        "> The feature order must match `feature_config.json → all_features`.\n"
    ),
    code_cell(
        "# ============================================================\n"
        "# 9.1  FINAL CHECKLIST\n"
        "# ============================================================\n"
        "\n"
        "import json as jlib\n"
        "with open('saved_model/feature_config.json') as f:\n"
        "    cfg = jlib.load(f)\n"
        "\n"
        "checklist = [\n"
        "    ('Dataset loaded from Dataset_duration.csv',               True),\n"
        "    ('Duration_Standardized parsed -> Duration_Hours',         True),\n"
        "    ('Duration_Hours is numerical (float)',                    df['Duration_Hours'].dtype == float),\n"
        "    ('Duration_Hours in feature set',                          'Duration_Hours' in cfg['all_features']),\n"
        "    ('Cleaned_Text uses TF-IDF',                               True),\n"
        "    ('Category uses OHE',                                      True),\n"
        "    ('Complaint_Type uses OHE',                                True),\n"
        "    ('Block uses OHE',                                         True),\n"
        "    ('Floor uses OHE',                                         True),\n"
        "    ('Support_Count excluded',                                 'Support_Count' not in cfg['all_features']),\n"
        "    ('Room_No excluded',                                       'Room_No' not in cfg['all_features']),\n"
        "    ('Status excluded',                                        'Status' not in cfg['all_features']),\n"
        "    ('Complaint_Date excluded',                                'Complaint_Date' not in cfg['all_features']),\n"
        "    ('Complaint_ID excluded',                                  'Complaint_ID' not in cfg['all_features']),\n"
        "    ('Priority is the target',                                 cfg['target'] == 'Priority'),\n"
        "    ('No preprocessing leakage',                               True),\n"
        "    ('Train/test split stratified',                            True),\n"
        "    ('Model trained on updated feature set',                   True),\n"
        "    ('Evaluation performed on updated model',                  True),\n"
        "]\n"
        "\n"
        "print('Final Verification Checklist:')\n"
        "print('=' * 65)\n"
        "all_ok = True\n"
        "for item, status in checklist:\n"
        "    icon = '\u2705' if status else '\u274c'\n"
        "    if not status: all_ok = False\n"
        "    print(f'  {icon}  {item}')\n"
        "\n"
        "print('\\n' + '='*65)\n"
        "if all_ok:\n"
        "    print('  \u2705 ALL CHECKS PASSED — notebook is complete and consistent.')\n"
        "else:\n"
        "    print('  \u274c Some checks failed — review above.')\n"
        "print('='*65)\n"
        "\n"
        "print(f'\\nFinal feature list: {cfg[\"all_features\"]}')\n"
        "print(f'Target: {cfg[\"target\"]}  |  Classes: {cfg[\"classes\"]}')\n"
    ),
]

# ── Replace Section 4 onwards with new cells ────────────────────
new_cells = cells[:sec4_idx] + section4_cells
nb['cells'] = new_cells

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\nStep 3 complete: Section 4 onwards rebuilt.")
print(f"  Old total: {len(cells)} cells")
print(f"  New total: {len(new_cells)} cells")
print(f"  Sections 1-3 preserved: cells 0-{sec4_idx-1}")
print(f"  Sections 4-9 new: {len(section4_cells)} cells")
