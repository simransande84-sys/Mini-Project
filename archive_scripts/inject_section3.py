"""
inject_section3.py
Replaces the existing Section 3 (NLP Preprocessing) cells in the notebook
with corrected, improved cells.

Key fixes vs old implementation:
1. len(w) > 2  →  len(w) >= 2   (preserves "no", "ac" — critical for negation)
2. Digit removal → kept only for pure number tokens, not embedded in severity context
3. Domain stopwords reviewed — severity words NOT removed
4. Negation preserved ("no water" stays "no water")
"""
import json

NB_PATH = r'hostel_complaint_prioritization.ipynb'

with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

def code_cell(src):
    return {"cell_type": "code", "execution_count": None,
            "metadata": {}, "outputs": [],
            "source": src if isinstance(src, list) else [src]}

def md_cell(src):
    return {"cell_type": "markdown", "metadata": {},
            "source": src if isinstance(src, list) else [src]}

# ─────────────────────────────────────────────────────────────────
# NEW SECTION 3 CELLS
# ─────────────────────────────────────────────────────────────────
section3_cells = [

    md_cell([
        "---\n",
        "## \U0001f9f9 SECTION 3: NLP Preprocessing\n\n",
        "Machine learning models cannot directly understand raw text. ",
        "We must **clean and standardize** the complaint text before feeding it to TF-IDF.\n\n",
        "**Key principle:** Clean enough to remove noise, but **do NOT over-clean** — ",
        "preserve severity words, negation, and domain-specific terms that carry priority signals.\n"
    ]),

    md_cell([
        "---\n",
        "### 3.1 — Inspect Old Preprocessing (Baseline Reference)\n\n",
        "The old model used this preprocessing pipeline (from `standalone_train_save.py`):\n\n",
        "```python\n",
        "text = text.lower()\n",
        "text = re.sub(r'\\bleakage\\b', 'leaking', text)\n",
        "text = re.sub(r'[^\\w\\s]', '', text)      # remove punctuation\n",
        "text = re.sub(r'\\d+', '', text)           # remove ALL digits\n",
        "tokens = [lemmatize(w) for w in text.split()\n",
        "          if w not in stopwords and len(w) > 2]  # drops 2-char words!\n",
        "```\n\n",
        "**Problems identified in the old preprocessing:**\n\n",
        "| Problem | Impact |\n",
        "|---|---|\n",
        "| `len(w) > 2` drops 2-char words | **`no`** becomes missing → `no water` → `water` (negation destroyed!) |\n",
        "| All digits removed | `3 days`, `2 weeks` lose duration context |\n",
        "| `'days'` and `'weeks'` are domain stopwords | Duration completely erased |\n",
        "| `'no'` has only 2 chars | Critical negation word silently dropped |\n\n",
        "> These will be fixed in the new preprocessing below.\n"
    ]),

    md_cell(["---\n### 3.2 — Sample Raw Complaints (Before Preprocessing)\n"]),

    code_cell([
        "# ============================================================\n",
        "# 3.1  DISPLAY SAMPLE RAW COMPLAINTS\n",
        "# ============================================================\n",
        "\n",
        "print('Sample Raw Complaint Texts (Before Any Preprocessing):')\n",
        "print('=' * 70)\n",
        "for priority in CLASS_ORDER:\n",
        "    samples = df[df['Priority'] == priority]['Complaint_Text'].head(3)\n",
        "    print(f'\\n--- {priority} Priority ---')\n",
        "    for i, txt in enumerate(samples, 1):\n",
        "        print(f'  [{i}] {txt}')\n"
    ]),

    md_cell([
        "---\n### 3.3 — Build the Improved NLP Preprocessing Function\n\n",
        "The preprocessing function applies these steps in order:\n\n",
        "| Step | What it does | Why |\n",
        "|---|---|---|\n",
        "| Lowercase | `Broken` → `broken` | Prevents same word treated as different |\n",
        "| Domain normalization | `leakage/leak` → `leaking` | Unifies variant spellings |\n",
        "| Punctuation removal | Remove `,./!?` etc | Reduces noise |\n",
        "| Digit cleanup | Remove **standalone** numbers only | Keeps severity context |\n",
        "| Extra whitespace | Collapse multiple spaces | Clean token splitting |\n",
        "| Stopword removal | Remove filler words | Keeps signal words |\n",
        "| **`len(w) >= 2`** | Keeps 2-char words like **`no`**, `ac` | **Preserves negation!** |\n",
        "| Lemmatization | `broken→break`, `leaking→leak` | Reduces vocabulary |\n\n",
        "> ✅ **Key fix:** Changed `len(w) > 2` to `len(w) >= 2` — this preserves `no`, `ac`, `ok` which are important words\n"
    ]),

    code_cell([
        "# ============================================================\n",
        "# 3.2  IMPROVED NLP PREPROCESSING FUNCTION\n",
        "# ============================================================\n",
        "\n",
        "import re\n",
        "import nltk\n",
        "from nltk.corpus import stopwords\n",
        "from nltk.stem import WordNetLemmatizer\n",
        "\n",
        "nltk.download('stopwords', quiet=True)\n",
        "nltk.download('wordnet',   quiet=True)\n",
        "nltk.download('omw-1.4',  quiet=True)\n",
        "\n",
        "# ── Domain-specific stopwords ──────────────────────────────────\n",
        "# These are hostel-specific FILLER words that add no priority signal.\n",
        "# IMPORTANT: Do NOT add severity words here.\n",
        "# Words like: urgent, emergency, broken, leaking, dangerous are KEPT.\n",
        "DOMAIN_STOPWORDS = {\n",
        "    # Polite openers (zero signal)\n",
        "    'please', 'kindly', 'sir', 'madam', 'hello', 'thanks', 'thank',\n",
        "    'dear', 'hi', 'regards', 'asap',\n",
        "    # Generic filler\n",
        "    'hostel', 'complaint', 'request', 'warden', 'office', 'management',\n",
        "    'student', 'students',\n",
        "    # Common structural filler (still kept some time words for context)\n",
        "    'look', 'also', 'us', 'am',\n",
        "    # NOTE: 'room', 'block', 'floor' are structural identifiers\n",
        "    # We keep them since they appear in Category/Block/Floor features anyway\n",
        "    # NOTE: 'no' is NOT added here — it is critical for negation!\n",
        "    # NOTE: 'days', 'week', 'weeks' are NOT added — they show duration/urgency\n",
        "}\n",
        "\n",
        "STD_STOPWORDS  = set(stopwords.words('english'))\n",
        "ALL_STOPWORDS  = STD_STOPWORDS.union(DOMAIN_STOPWORDS)\n",
        "\n",
        "# Re-add critical words that NLTK removes but we need:\n",
        "PRESERVE_WORDS = {'no', 'not', 'never', 'cannot', 'cant', 'wont', 'isnt',\n",
        "                  'doesnt', 'hasnt', 'havent', 'wasnt', 'wouldnt'}\n",
        "ALL_STOPWORDS -= PRESERVE_WORDS  # force-keep these negation words\n",
        "\n",
        "_lemmatizer = WordNetLemmatizer()\n",
        "\n",
        "def preprocess_text(text: str) -> str:\n",
        "    \"\"\"\n",
        "    Improved NLP preprocessing pipeline for hostel complaint text.\n",
        "    \n",
        "    Changes from old pipeline:\n",
        "    - len(w) >= 2  (was > 2) -> preserves 'no', 'ac'\n",
        "    - Negation words force-kept even if in NLTK stopwords\n",
        "    - Standalone digits removed, but NOT digits embedded in words\n",
        "    - Domain stopwords reduced (removed 'days','week','weeks' to keep duration)\n",
        "    \"\"\"\n",
        "    if not isinstance(text, str) or not text.strip():\n",
        "        return ''\n",
        "\n",
        "    # Step 1: Lowercase\n",
        "    text = text.lower()\n",
        "\n",
        "    # Step 2: Domain normalization\n",
        "    text = re.sub(r'\\bleakage\\b', 'leaking', text)\n",
        "    text = re.sub(r'\\bleak\\b',    'leaking', text)\n",
        "    text = re.sub(r'\\belectricity\\b', 'electric', text)\n",
        "\n",
        "    # Step 3: Remove punctuation (keep apostrophes for contractions briefly)\n",
        "    text = re.sub(r\"[^\\w\\s]\", ' ', text)\n",
        "\n",
        "    # Step 4: Remove standalone digits (pure number tokens)\n",
        "    # e.g. '3' or '14' standalone, but keep 'b2' 'room3' etc\n",
        "    text = re.sub(r'\\b\\d+\\b', '', text)\n",
        "\n",
        "    # Step 5: Collapse whitespace\n",
        "    text = re.sub(r'\\s+', ' ', text).strip()\n",
        "\n",
        "    # Step 6: Tokenize, filter stopwords, lemmatize\n",
        "    # KEY FIX: len(w) >= 2  (old was > 2, which dropped 'no', 'ac')\n",
        "    tokens = [\n",
        "        _lemmatizer.lemmatize(w)\n",
        "        for w in text.split()\n",
        "        if w not in ALL_STOPWORDS and len(w) >= 2\n",
        "    ]\n",
        "\n",
        "    return ' '.join(tokens)\n",
        "\n",
        "\n",
        "print('✅ NLP preprocessing function defined.')\n",
        "print(f'   Standard stopwords : {len(STD_STOPWORDS)}')\n",
        "print(f'   Domain stopwords   : {len(DOMAIN_STOPWORDS)}')\n",
        "print(f'   Force-kept words   : {sorted(PRESERVE_WORDS)}')\n",
        "print(f'   Total stopwords    : {len(ALL_STOPWORDS)}')\n",
        "print(f'   Min word length    : >= 2  (was > 2 in old model)')\n"
    ]),

    md_cell(["---\n### 3.4 — Step-by-Step Demonstration on One Complaint\n"]),

    code_cell([
        "# ============================================================\n",
        "# 3.3  STEP-BY-STEP DEMONSTRATION\n",
        "# ============================================================\n",
        "\n",
        "sample_text = df[df['Priority'] == 'High']['Complaint_Text'].iloc[0]\n",
        "print(f'Original: {sample_text}')\n",
        "print()\n",
        "\n",
        "# Trace each step\n",
        "t = sample_text\n",
        "print(f'Step 1 [lowercase]    : {t.lower()[:80]}')\n",
        "t = t.lower()\n",
        "\n",
        "t2 = re.sub(r'\\bleakage\\b', 'leaking', t)\n",
        "t2 = re.sub(r'\\bleak\\b', 'leaking', t2)\n",
        "print(f'Step 2 [normalize]    : {t2[:80]}')\n",
        "t = t2\n",
        "\n",
        "t3 = re.sub(r'[^\\w\\s]', ' ', t)\n",
        "print(f'Step 3 [no punct]     : {t3[:80]}')\n",
        "t = t3\n",
        "\n",
        "t4 = re.sub(r'\\b\\d+\\b', '', t)\n",
        "print(f'Step 4 [no digits]    : {t4[:80]}')\n",
        "t = t4\n",
        "\n",
        "t5 = re.sub(r'\\s+', ' ', t).strip()\n",
        "print(f'Step 5 [clean spaces] : {t5[:80]}')\n",
        "t = t5\n",
        "\n",
        "tokens_raw = t.split()\n",
        "tokens_filt = [w for w in tokens_raw if w not in ALL_STOPWORDS and len(w) >= 2]\n",
        "tokens_lem  = [_lemmatizer.lemmatize(w) for w in tokens_filt]\n",
        "print(f'Step 6 [filter]       : {tokens_filt}')\n",
        "print(f'Step 7 [lemmatize]    : {tokens_lem}')\n",
        "print(f'\\nFinal cleaned text    : {\" \".join(tokens_lem)}')\n",
        "print(f'\\nWord count: {len(sample_text.split())} → {len(tokens_lem)}')\n",
        "\n",
        "# Show negation preservation\n",
        "print('\\n--- Negation Preservation Test ---')\n",
        "neg_tests = [\n",
        "    'there is no water in the cooler',\n",
        "    'the fan is not working',\n",
        "    'we cannot sleep due to noise',\n",
        "]\n",
        "for txt in neg_tests:\n",
        "    cleaned = preprocess_text(txt)\n",
        "    has_no = any(w in cleaned.split() for w in ['no','not','cannot','cant'])\n",
        "    print(f'  Original : {txt}')\n",
        "    print(f'  Cleaned  : {cleaned}')\n",
        "    print(f'  Negation preserved: {\"✅\" if has_no else \"❌\"}')\n",
        "    print()\n"
    ]),

    md_cell(["---\n### 3.5 — Apply Preprocessing to All 857 Complaints\n"]),

    code_cell([
        "# ============================================================\n",
        "# 3.4  APPLY PREPROCESSING TO ENTIRE DATASET\n",
        "# ============================================================\n",
        "\n",
        "import time\n",
        "start = time.time()\n",
        "\n",
        "# Apply to the Complaint_Text column\n",
        "# Creates Cleaned_Text — does NOT modify original Complaint_Text\n",
        "df['Cleaned_Text'] = df['Complaint_Text'].apply(preprocess_text)\n",
        "\n",
        "elapsed = time.time() - start\n",
        "print(f'✅ Preprocessing complete in {elapsed:.2f}s')\n",
        "print(f'   Rows processed: {len(df)}')\n",
        "\n",
        "# Verify no empty results\n",
        "empty_after = (df['Cleaned_Text'].str.strip() == '').sum()\n",
        "null_after  = df['Cleaned_Text'].isna().sum()\n",
        "print(f'   Empty Cleaned_Text rows: {empty_after}')\n",
        "print(f'   Null  Cleaned_Text rows: {null_after}')\n",
        "\n",
        "# Word count reduction\n",
        "df['_orig_wc']    = df['Complaint_Text'].str.split().str.len()\n",
        "df['_cleaned_wc'] = df['Cleaned_Text'].str.split().str.len()\n",
        "avg_reduction = ((df['_orig_wc'] - df['_cleaned_wc']) / df['_orig_wc'] * 100).mean()\n",
        "print(f'   Avg word count: {df[\"_orig_wc\"].mean():.1f} → {df[\"_cleaned_wc\"].mean():.1f}',\n",
        "      f'(reduction: {avg_reduction:.1f}%)')\n",
        "df.drop(columns=['_orig_wc','_cleaned_wc'], inplace=True)\n"
    ]),

    md_cell(["---\n### 3.6 — Before vs After Comparison (High / Medium / Low samples)\n"]),

    code_cell([
        "# ============================================================\n",
        "# 3.5  BEFORE vs AFTER COMPARISON — 5 examples per class\n",
        "# ============================================================\n",
        "\n",
        "print('BEFORE vs AFTER PREPROCESSING')\n",
        "print('=' * 70)\n",
        "\n",
        "for priority in CLASS_ORDER:\n",
        "    samples = df[df['Priority'] == priority].head(6)\n",
        "    print(f'\\n{'─'*70}')\n",
        "    print(f'  {priority.upper()} PRIORITY')\n",
        "    print(f'{'─'*70}')\n",
        "    for _, row in samples.iterrows():\n",
        "        orig    = row['Complaint_Text']\n",
        "        cleaned = row['Cleaned_Text']\n",
        "        print(f'  Original : {orig[:80]}')\n",
        "        print(f'  Cleaned  : {cleaned}')\n",
        "        print()\n"
    ]),

    md_cell(["---\n### 3.7 — Verify Severity Words Are Preserved\n"]),

    code_cell([
        "# ============================================================\n",
        "# 3.6  VERIFY SEVERITY / SIGNAL WORDS ARE NOT LOST\n",
        "# ============================================================\n",
        "\n",
        "# These words should survive preprocessing\n",
        "severity_words = [\n",
        "    'urgent', 'emergency', 'dangerous', 'unsafe', 'severe',\n",
        "    'broken', 'leaking', 'flooded', 'fire', 'shock',\n",
        "    'damaged', 'no', 'not', 'cannot', 'dark', 'smell',\n",
        "    'smell', 'dirty', 'crack', 'collapse', 'hurt', 'pain'\n",
        "]\n",
        "\n",
        "test_sentences = [\n",
        "    ('High', 'There is no electricity in the room, it is dangerous and unsafe'),\n",
        "    ('High', 'Electrical shock from the broken socket, emergency situation'),\n",
        "    ('High', 'Severe leakage flooding the corridor, urgent attention needed'),\n",
        "    ('Medium', 'The fan in my room is not working since yesterday'),\n",
        "    ('Low', 'There are cobwebs in the staircase corner'),\n",
        "]\n",
        "\n",
        "print('Severity Word Preservation Test:')\n",
        "print('-' * 60)\n",
        "for expected_class, sentence in test_sentences:\n",
        "    cleaned = preprocess_text(sentence)\n",
        "    found = [w for w in severity_words if w in cleaned.split()]\n",
        "    print(f'Expected: {expected_class}')\n",
        "    print(f'Original: {sentence}')\n",
        "    print(f'Cleaned : {cleaned}')\n",
        "    print(f'Signal words preserved: {found}')\n",
        "    print()\n",
        "\n",
        "# Also verify 'no' is preserved\n",
        "no_test = preprocess_text('there is no water and no electricity')\n",
        "print(f'\"no\" preservation test: \"{no_test}\"')\n",
        "print(f'\"no\" in cleaned: {\"no\" in no_test.split()}  (✅ correct)' if 'no' in no_test.split() else '\"no\" MISSING ❌')\n"
    ]),

    md_cell(["---\n### 3.8 — Top Words After Preprocessing (by Priority)\n"]),

    code_cell([
        "# ============================================================\n",
        "# 3.7  TOP WORDS BY PRIORITY AFTER PREPROCESSING\n",
        "# ============================================================\n",
        "\n",
        "import matplotlib.pyplot as plt\n",
        "from collections import Counter\n",
        "\n",
        "fig, axes = plt.subplots(1, 3, figsize=(17, 5))\n",
        "\n",
        "for ax, priority in zip(axes, CLASS_ORDER):\n",
        "    texts  = ' '.join(df[df['Priority'] == priority]['Cleaned_Text'])\n",
        "    words  = texts.split()\n",
        "    top15  = Counter(words).most_common(15)\n",
        "    words_, counts_ = zip(*top15)\n",
        "\n",
        "    color  = PALETTE[priority]\n",
        "    bars   = ax.barh(range(len(words_)), counts_,\n",
        "                     color=color, alpha=0.8, edgecolor='white')\n",
        "    ax.set_yticks(range(len(words_)))\n",
        "    ax.set_yticklabels(words_, fontsize=10)\n",
        "    ax.invert_yaxis()\n",
        "    ax.set_title(f'{priority} Priority\\nTop 15 Words', fontsize=12, fontweight='bold')\n",
        "    ax.set_xlabel('Frequency', fontsize=10)\n",
        "    ax.spines['top'].set_visible(False)\n",
        "    ax.spines['right'].set_visible(False)\n",
        "\n",
        "plt.suptitle('Top Words After NLP Preprocessing (by Priority)',\n",
        "             fontsize=14, fontweight='bold', y=1.02)\n",
        "plt.tight_layout()\n",
        "plt.show()\n",
        "\n",
        "# Print side by side\n",
        "print('\\nTop 10 words by priority:')\n",
        "print(f'{\"HIGH\":25s} {\"MEDIUM\":25s} {\"LOW\":25s}')\n",
        "print('-' * 75)\n",
        "results = {}\n",
        "for p in CLASS_ORDER:\n",
        "    texts = ' '.join(df[df['Priority'] == p]['Cleaned_Text'])\n",
        "    results[p] = Counter(texts.split()).most_common(10)\n",
        "for i in range(10):\n",
        "    row = ''\n",
        "    for p in CLASS_ORDER:\n",
        "        w, c = results[p][i]\n",
        "        row += f'{w}({c}){\" \"*(25-len(w)-len(str(c))-2)}'\n",
        "    print(row)\n"
    ]),

    md_cell([
        "---\n",
        "## ✅ Section 3 Complete — NLP Preprocessing Summary\n\n",
        "### What the preprocessing does:\n",
        "| Step | Detail |\n",
        "|---|---|\n",
        "| Lowercase | All text → lowercase for uniformity |\n",
        "| Domain normalization | `leakage/leak` → `leaking` |\n",
        "| Punctuation removal | Remove `,./!?` etc |\n",
        "| Standalone digit removal | Remove bare numbers, keep letter-digit words |\n",
        "| Whitespace collapse | Clean multiple spaces |\n",
        "| Stopword removal | NLTK + domain stopwords |\n",
        "| `len(w) >= 2` | ✅ Fixed — keeps `no`, `ac` (was `> 2`) |\n",
        "| Negation force-kept | `no, not, cannot` are never removed |\n",
        "| Lemmatization | `broken→break`, `leaking→leak` |\n\n",
        "### Corrections vs Old Model:\n",
        "| Old Problem | Fix Applied |\n",
        "|---|---|\n",
        "| `len(w) > 2` dropped `no` | Changed to `len(w) >= 2` |\n",
        "| `'days','weeks'` were stopwords | Removed from domain list (keeps duration) |\n",
        "| `no` (negation) was silently lost | Added to `PRESERVE_WORDS` set |\n",
        "| All digits blindly removed | Only standalone digit tokens removed |\n\n",
        "> ✅ `Cleaned_Text` column created and ready for TF-IDF in Section 4.\n"
    ]),
]

# ─────────────────────────────────────────────────────────────────
# Find Section 3 and Section 4 boundaries
# ─────────────────────────────────────────────────────────────────
sec3_start = None
sec4_start = None

for i, cell in enumerate(cells):
    src = ''.join(cell['source'])
    if sec3_start is None and 'SECTION 3' in src and cell['cell_type'] == 'markdown':
        sec3_start = i
    if sec3_start is not None and i > sec3_start:
        if 'SECTION 4' in src and cell['cell_type'] == 'markdown':
            sec4_start = i
            break

print(f"Section 3: cells {sec3_start} to {sec4_start - 1}")
print(f"Replacing {sec4_start - sec3_start} old cells with {len(section3_cells)} new cells")

new_cells = cells[:sec3_start] + section3_cells + cells[sec4_start:]
nb['cells'] = new_cells

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"✅ Section 3 injected. Total cells: {len(new_cells)}")
