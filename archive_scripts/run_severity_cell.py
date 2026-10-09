"""
run_severity_cell.py
Runs ONLY the updated severity test cell (cell 66) and embeds output.
Rebuilds the necessary namespace context first.
"""
import json, sys, io, traceback, warnings, re
warnings.filterwarnings('ignore')

import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet',   quiet=True)
nltk.download('omw-1.4',  quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Reconstruct preprocess_text exactly as defined in cell 58
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

namespace = {'preprocess_text': preprocess_text, 're': re}

NB_PATH = r'hostel_complaint_prioritization.ipynb'
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

# Find the severity test cell (index 66 or wherever it is now)
target_idx = None
for i, cell in enumerate(cells):
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if 'SEVERITY_WORDS' in src and 'VERIFY SEVERITY' in src:
            target_idx = i
            break

if target_idx is None:
    print("ERROR: Cannot find updated severity test cell")
    exit(1)

print(f"Running cell {target_idx}...")
src = ''.join(cells[target_idx]['source'])

old_stdout = sys.stdout
sys.stdout  = io.StringIO()
outputs     = []

try:
    exec(compile(src, f'<cell_{target_idx}>', 'exec'), namespace)
    stdout_val = sys.stdout.getvalue()
    print(stdout_val, file=old_stdout)
    outputs.append({
        "output_type": "stream",
        "name": "stdout",
        "text": stdout_val.splitlines(keepends=True)
    })
except Exception as e:
    err = traceback.format_exc()
    print(f"ERROR: {e}", file=old_stdout)
    print(err, file=old_stdout)
    outputs.append({
        "output_type": "stream", "name": "stderr",
        "text": [err]
    })
finally:
    sys.stdout = old_stdout

# Preserve existing execution_count from surrounding cells
prev_exec = max(
    (c.get('execution_count') or 0)
    for c in cells[:target_idx]
    if c['cell_type'] == 'code'
)
cells[target_idx]['outputs'] = outputs
cells[target_idx]['execution_count'] = prev_exec + 1

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\n✅ Cell {target_idx} re-executed. Output embedded in notebook.")
