"""
execute_section4.py
Executes all Section 4 code cells and embeds outputs.
Rebuilds full namespace from scratch.
"""
import json, sys, io, traceback, base64, re, warnings, time
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd, numpy as np
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet',   quiet=True)
nltk.download('omw-1.4',  quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from collections import Counter

CLASS_ORDER  = ['High', 'Medium', 'Low']
PALETTE      = {'High': '#E74C3C', 'Medium': '#F39C12', 'Low': '#27AE60'}
RANDOM_STATE = 42

df = pd.read_csv('DATSETminiproject.csv')

# Rebuild preprocess_text
DOMAIN_STOPWORDS = {
    'please','kindly','sir','madam','hello','thanks','thank',
    'dear','hi','regards','asap','hostel','complaint','request',
    'warden','office','management','student','students','look','also','us','am',
}
STD_STOPWORDS  = set(stopwords.words('english'))
ALL_STOPWORDS  = STD_STOPWORDS.union(DOMAIN_STOPWORDS)
PRESERVE_WORDS = {'no','not','never','cannot','cant','wont','isnt',
                  'doesnt','hasnt','havent','wasnt','wouldnt'}
ALL_STOPWORDS -= PRESERVE_WORDS
_lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if not isinstance(text, str) or not text.strip():
        return ''
    text = text.lower()
    text = re.sub(r'\bleakage\b', 'leaking', text)
    text = re.sub(r'\bleak\b',    'leaking', text)
    text = re.sub(r'\belectricity\b', 'electric', text)
    text = text.replace("can't",    "cannot")
    text = text.replace("won't",    "wont")
    text = text.replace("isn't",    "is not")
    text = text.replace("doesn't",  "does not")
    text = text.replace("hasn't",   "has not")
    text = text.replace("haven't",  "have not")
    text = text.replace("wasn't",   "was not")
    text = text.replace("wouldn't", "would not")
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = [_lemmatizer.lemmatize(w) for w in text.split()
              if w not in ALL_STOPWORDS and len(w) >= 2]
    return ' '.join(tokens)

df['Cleaned_Text'] = df['Complaint_Text'].apply(preprocess_text)

namespace = {
    'pd': pd, 'np': np, 'plt': plt, 're': re, 'nltk': nltk,
    'time': time, 'Counter': Counter,
    'CLASS_ORDER': CLASS_ORDER, 'PALETTE': PALETTE,
    'RANDOM_STATE': RANDOM_STATE, 'df': df,
    'preprocess_text': preprocess_text,
}

NB_PATH = r'hostel_complaint_prioritization.ipynb'
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

sec4_start = sec5_start = None
for i, cell in enumerate(cells):
    src = ''.join(cell['source'])
    if sec4_start is None and 'SECTION 4' in src and cell['cell_type'] == 'markdown':
        sec4_start = i
    if sec4_start is not None and i > sec4_start:
        if 'SECTION 5' in src and cell['cell_type'] == 'markdown':
            sec5_start = i
            break

prev_exec = max(
    (c.get('execution_count') or 0)
    for c in cells[:sec4_start]
    if c['cell_type'] == 'code'
)
exec_order = prev_exec + 1
print(f"Executing Section 4: cells {sec4_start} to {sec5_start-1}  (starting exec #{exec_order})")

for i in range(sec4_start, sec5_start):
    cell = cells[i]
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source']).strip()
    if not src:
        continue

    print(f"\n>>> Cell {i} (exec #{exec_order})")
    old_stdout = sys.stdout
    sys.stdout  = io.StringIO()
    outputs     = []

    try:
        exec(compile(src, f'<cell_{i}>', 'exec'), namespace)
        stdout_val = sys.stdout.getvalue()
        if stdout_val.strip():
            print(stdout_val, file=old_stdout)
            outputs.append({
                "output_type": "stream", "name": "stdout",
                "text": stdout_val.splitlines(keepends=True)
            })
    except Exception as e:
        err = traceback.format_exc()
        print(f"  ERROR: {e}", file=old_stdout)
        print(err, file=old_stdout)
        outputs.append({
            "output_type": "stream", "name": "stderr", "text": [err]
        })
    finally:
        sys.stdout = old_stdout

    cell['outputs'] = outputs
    cell['execution_count'] = exec_order
    exec_order += 1

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\n{'='*60}")
print("✅ Section 4 complete.")
print(f"   X_train shape: {namespace.get('X_train_proc', np.array([])).shape}")
print(f"   X_test  shape: {namespace.get('X_test_proc',  np.array([])).shape}")
print(f"   Label classes : {namespace.get('le').classes_ if 'le' in namespace else 'N/A'}")
