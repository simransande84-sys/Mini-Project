"""
update_label_encoding_cell.py
Updates ONLY the Section 4.5 label encoding cell to add:
 - Clear documentation of the LabelEncoder mapping
 - Note that integer values are CLASS LABELS, not numerical measurements
 - Natural order context (Low < Medium < High) for human understanding
 - Explicit reversibility check
No other cells or files are modified.
"""
import json, sys, io, traceback
import warnings; warnings.filterwarnings('ignore')

NB_PATH = r'hostel_complaint_prioritization.ipynb'
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

# Find the Section 4.5 label encoding cell
target_idx = None
for i, cell in enumerate(cells):
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if 'ENCODE TARGET VARIABLE' in src and 'LabelEncoder' in src:
            target_idx = i
            break

if target_idx is None:
    print("ERROR: Cannot find label encoding cell")
    exit(1)
print(f"Found label encoding cell at index {target_idx}")

new_source = (
    "# ============================================================\n"
    "# 4.5  ENCODE TARGET VARIABLE (Priority)\n"
    "# ============================================================\n"
    "# Approach: LabelEncoder — integers are CLASS LABELS only.\n"
    "#\n"
    "# Priority has a natural human order:  Low < Medium < High\n"
    "# However, this is a MULTICLASS CLASSIFICATION problem.\n"
    "# The integer codes assigned by LabelEncoder are identifiers,\n"
    "# NOT numerical measurements or ordinal scores.\n"
    "# The model treats them as distinct categories, not a scale.\n"
    "#\n"
    "# Do NOT interpret e.g. High=0 as 'less than' Low=1.\n"
    "# The mapping is just an internal label — fully reversible.\n"
    "# ============================================================\n"
    "\n"
    "from sklearn.preprocessing import LabelEncoder\n"
    "\n"
    "le = LabelEncoder()\n"
    "le.fit(CLASS_ORDER)          # CLASS_ORDER = ['High', 'Medium', 'Low']\n"
    "\n"
    "y_train_enc = le.transform(y_train)\n"
    "y_test_enc  = le.transform(y_test)\n"
    "\n"
    "# ── Document the mapping ──────────────────────────────────────\n"
    "print('Priority Target Encoding')\n"
    "print('=' * 55)\n"
    "print('  Encoding approach : sklearn LabelEncoder')\n"
    "print('  Problem type      : Multiclass Classification (3 classes)')\n"
    "print('  Integer meaning   : CLASS LABEL only — not a numerical score')\n"
    "print()\n"
    "print('  Natural order (human context):  Low  <  Medium  <  High')\n"
    "print('  LabelEncoder mapping (alphabetical assignment):')\n"
    "print()\n"
    "print(f'  {\"Priority Class\":16s}  {\"Encoded Integer\":16s}  {\"Role\":20s}')\n"
    "print(f'  {\"-\"*16}  {\"-\"*16}  {\"-\"*20}')\n"
    "for cls in le.classes_:\n"
    "    enc = int(le.transform([cls])[0])\n"
    "    print(f'  {cls:16s}  {enc:<16}  Class label identifier')\n"
    "\n"
    "print()\n"
    "print('  Note: LabelEncoder assigns integers alphabetically.')\n"
    "print('        High=0, Low=1, Medium=2 — these integers carry NO')\n"
    "print('        ordinal meaning inside the classifier.')\n"
    "\n"
    "# ── Verify shapes ─────────────────────────────────────────────\n"
    "print(f'\\n  y_train_enc : shape={y_train_enc.shape}, unique={sorted(set(y_train_enc.tolist()))}')\n"
    "print(f'  y_test_enc  : shape={y_test_enc.shape},  unique={sorted(set(y_test_enc.tolist()))}')\n"
    "\n"
    "# ── Verify reversibility ──────────────────────────────────────\n"
    "print('\\nReversibility Check:')\n"
    "print('  (confirm le.inverse_transform recovers original string labels)')\n"
    "sample_orig    = list(y_train[:5])\n"
    "sample_encoded = list(y_train_enc[:5])\n"
    "sample_decoded = list(le.inverse_transform(y_train_enc[:5]))\n"
    "print(f'  Original : {sample_orig}')\n"
    "print(f'  Encoded  : {sample_encoded}')\n"
    "print(f'  Decoded  : {sample_decoded}')\n"
    "match = sample_orig == sample_decoded\n"
    "print(f'  Match    : {match}  {chr(10003) if match else chr(10006)}')\n"
    "\n"
    "# ── Show full encode/decode reference table ───────────────────\n"
    "print('\\nFull Encode / Decode Reference:')\n"
    "print(f'  {\"String Label\":14s} -> {\"Integer\":<8} -> {\"Decoded Back\":14s} -> {\"Reversible\"}')\n"
    "print(f'  {\"-\"*14}    {\"-\"*8}    {\"-\"*14}    {\"-\"*10}')\n"
    "for cls in sorted(le.classes_):   # alphabetical\n"
    "    enc     = int(le.transform([cls])[0])\n"
    "    decoded = le.inverse_transform([enc])[0]\n"
    "    ok      = decoded == cls\n"
    "    print(f'  {cls:14s} ->  {enc:<8} -> {decoded:14s} -> {chr(10003) if ok else chr(10006)}')\n"
    "\n"
    "print('\\n\u2705 LabelEncoder mapping documented and reversibility verified.')\n"
)

cells[target_idx]['source'] = [new_source]
cells[target_idx]['outputs'] = []
cells[target_idx]['execution_count'] = None

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)
print(f"Cell {target_idx} source updated. Now executing...")

# ── Execute the updated cell ───────────────────────────────────────
import pandas as pd, numpy as np, re
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import nltk; nltk.download('stopwords', quiet=True); nltk.download('wordnet', quiet=True)

CLASS_ORDER  = ['High', 'Medium', 'Low']
RANDOM_STATE = 42

df = pd.read_csv('Dataset_duration.csv')

DOMAIN_SW = {'please','kindly','sir','madam','hello','thanks','thank','dear','hi','regards','asap','hostel','complaint','request','warden','office','management','student','students','look','also','us','am'}
STD_SW = set(stopwords.words('english'))
ALL_SW = (STD_SW | DOMAIN_SW) - {'no','not','never','cannot','cant','wont','isnt','doesnt','hasnt','havent','wasnt','wouldnt'}
_lem = WordNetLemmatizer()
def preprocess_text(text):
    if not isinstance(text, str) or not text.strip(): return ''
    text = text.lower()
    text = re.sub(r'\bleakage\b','leaking', text); text = re.sub(r'\bleak\b','leaking', text)
    text = re.sub(r'\belectricity\b','electric', text)
    for old, new in [("can't","cannot"),("won't","wont"),("isn't","is not"),("doesn't","does not"),("hasn't","has not"),("haven't","have not"),("wasn't","was not"),("wouldn't","would not")]:
        text = text.replace(old, new)
    text = re.sub(r'[^\w\s]',' ',text); text = re.sub(r'\b\d+\b','',text); text = re.sub(r'\s+',' ',text).strip()
    return ' '.join(_lem.lemmatize(w) for w in text.split() if w not in ALL_SW and len(w)>=2)

def parse_duration_hours(text):
    if not isinstance(text, str): return None
    parts = text.strip().lower().split()
    if len(parts) != 2: return None
    try: v = float(parts[0])
    except: return None
    u = parts[1]
    if u in ('hour','hours'): return v
    if u in ('day','days'): return v*24
    if u in ('week','weeks'): return v*168
    if u in ('month','months'): return v*720
    return None

df['Cleaned_Text']   = df['Complaint_Text'].apply(preprocess_text)
df['Duration_Hours'] = df['Duration_Standardized'].apply(parse_duration_hours)

TEXT_FEATURE = 'Cleaned_Text'
CAT_FEATURES = ['Category','Complaint_Type','Block','Floor']
NUM_FEATURES = ['Duration_Hours']
ALL_FEATURES = [TEXT_FEATURE] + CAT_FEATURES + NUM_FEATURES
TARGET       = 'Priority'

X = df[ALL_FEATURES].copy()
y = df[TARGET].copy()
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=RANDOM_STATE, stratify=y)

namespace = {
    'CLASS_ORDER': CLASS_ORDER, 'RANDOM_STATE': RANDOM_STATE,
    'y_train': y_train, 'y_test': y_test,
    'LabelEncoder': LabelEncoder, 'chr': chr,
}

old_stdout = sys.stdout
sys.stdout = io.StringIO()
outputs = []
try:
    exec(compile(new_source, f'<cell_{target_idx}>', 'exec'), namespace)
    stdout_val = sys.stdout.getvalue()
    print(stdout_val, file=old_stdout)
    outputs.append({"output_type":"stream","name":"stdout","text":stdout_val.splitlines(keepends=True)})
except Exception as e:
    err = traceback.format_exc()
    print(f"ERROR: {e}", file=old_stdout)
    outputs.append({"output_type":"stream","name":"stderr","text":[err]})
finally:
    sys.stdout = old_stdout

prev_exec = max((c.get('execution_count') or 0) for c in cells[:target_idx] if c['cell_type']=='code')
cells[target_idx]['outputs']         = outputs
cells[target_idx]['execution_count'] = prev_exec + 1

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\n\u2705 Cell {target_idx} executed and saved.")
