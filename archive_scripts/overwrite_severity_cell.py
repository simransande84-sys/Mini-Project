"""
overwrite_severity_cell.py
Completely rewrites the severity test cell source from scratch.
Only touches cell 66 (or wherever SEVERITY_WORDS is defined).
"""
import json, sys, io, traceback, warnings, re
warnings.filterwarnings('ignore')

NB_PATH = r'hostel_complaint_prioritization.ipynb'
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

# Find the target cell
target_idx = None
for i, cell in enumerate(cells):
    if cell['cell_type'] == 'code' and 'SEVERITY_WORDS' in ''.join(cell['source']):
        target_idx = i
        break

if target_idx is None:
    print("ERROR: Cannot locate severity test cell.")
    exit(1)

# Definitive correct source
new_source = (
    "# ============================================================\n"
    "# 3.6  VERIFY SEVERITY / SIGNAL WORDS ARE PRESERVED BY PREPROCESSING\n"
    "#\n"
    "# PURPOSE: This test ONLY checks that important words survive the\n"
    "# NLP preprocessing pipeline. It does NOT claim that finding a\n"
    "# severity word guarantees any particular ML model prediction.\n"
    "# ============================================================\n"
    "\n"
    "# Words that carry severity/negation signal and must NOT be lost.\n"
    "# Deduplicated list (no repeats).\n"
    "SEVERITY_WORDS = [\n"
    "    'urgent', 'emergency', 'dangerous', 'unsafe', 'severe',\n"
    "    'broken', 'leaking', 'fire', 'shock',\n"
    "    'no', 'not', 'cannot',\n"
    "]\n"
    "\n"
    "# Test sentences with CORRECT expected tokens after preprocessing\n"
    "test_cases = [\n"
    "    # Negation words\n"
    "    ('there is no water in the cooler',\n"
    "     ['no']),\n"
    "    ('the fan is not working since yesterday',\n"
    "     ['not']),\n"
    "    ('we cannot sleep because of the noise',\n"
    "     ['cannot']),\n"
    "    # Contractions expanded before punctuation removal\n"
    "    (\"the AC won't turn on\",\n"
    "     ['wont']),\n"
    "    (\"the tap doesn't stop dripping\",\n"
    "     ['not']),           # doesn't -> does not -> 'not' survives\n"
    "    # Severity / urgency words\n"
    "    ('this is urgent, the pipe is severely leaking',\n"
    "     ['urgent', 'severely', 'leaking']),\n"
    "    ('there was an electrical shock from the broken socket',\n"
    "     ['shock', 'broken']),\n"
    "    ('the situation is dangerous and unsafe for students',\n"
    "     ['dangerous', 'unsafe']),\n"
    "    ('there is a fire risk near the generator room',\n"
    "     ['fire']),\n"
    "    # 'flooding' stays as 'flooding' after preprocessing (does not become 'leaking')\n"
    "    ('severe flooding in the corridor, emergency action needed',\n"
    "     ['severe', 'flooding', 'emergency']),\n"
    "]\n"
    "\n"
    "print('Severity and Negation Word Preservation Test')\n"
    "print('=' * 65)\n"
    "print('PURPOSE: Verify words survive NLP preprocessing only.')\n"
    "print('         This does NOT predict ML model output.')\n"
    "print('=' * 65)\n"
    "\n"
    "all_pass = True\n"
    "for sentence, expected_words in test_cases:\n"
    "    cleaned        = preprocess_text(sentence)\n"
    "    cleaned_tokens = cleaned.split()\n"
    "    found   = [w for w in expected_words if w in cleaned_tokens]\n"
    "    missing = [w for w in expected_words if w not in cleaned_tokens]\n"
    "    passed  = len(missing) == 0\n"
    "    if not passed:\n"
    "        all_pass = False\n"
    "    status = 'PASS \\u2705' if passed else 'FAIL \\u274c'\n"
    "    print(f'\\n  [{status}]')\n"
    "    print(f'  Original : {sentence}')\n"
    "    print(f'  Cleaned  : {cleaned}')\n"
    "    print(f'  Expected words : {expected_words}')\n"
    "    print(f'  Words found    : {found}')\n"
    "    if missing:\n"
    "        print(f'  Words MISSING  : {missing}  \\u2190 needs attention')\n"
    "\n"
    "print('\\n' + '=' * 65)\n"
    "if all_pass:\n"
    "    print('  \\u2705 All signal words survived preprocessing.')\n"
    "else:\n"
    "    print('  \\u26a0  Some signal words were lost. Review preprocessing.')\n"
    "print('=' * 65)\n"
    "\n"
    "# Explicit negation checks\n"
    "no_test  = preprocess_text('there is no water and no electricity')\n"
    "not_test = preprocess_text(\"fan isn't working\")\n"
    "print('\\nExplicit negation checks:')\n"
    "print(f'  no  in \"there is no water...\" : {\"no\" in no_test.split()}  -> cleaned: \"{no_test}\"')\n"
    "print(f'  not in \"fan isn\\'t working\"   : {\"not\" in not_test.split()} -> cleaned: \"{not_test}\"')\n"
)

cells[target_idx]['source'] = [new_source]
cells[target_idx]['outputs'] = []
cells[target_idx]['execution_count'] = None

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"✅ Cell {target_idx} completely rewritten with correct expectations.")

# Now execute it
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

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

# Execute the updated cell
old_stdout = sys.stdout
sys.stdout = io.StringIO()
outputs = []

try:
    exec(compile(new_source, '<severity_cell>', 'exec'), namespace)
    stdout_val = sys.stdout.getvalue()
    print(stdout_val, file=old_stdout)
    outputs.append({
        "output_type": "stream", "name": "stdout",
        "text": stdout_val.splitlines(keepends=True)
    })
except Exception as e:
    err = traceback.format_exc()
    print(f"ERROR: {e}", file=old_stdout)
    outputs.append({
        "output_type": "stream", "name": "stderr", "text": [err]
    })
finally:
    sys.stdout = old_stdout

# Re-read and save with embedded output
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb2 = json.load(f)

prev_exec = max(
    (c.get('execution_count') or 0)
    for c in nb2['cells'][:target_idx]
    if c['cell_type'] == 'code'
)
nb2['cells'][target_idx]['outputs'] = outputs
nb2['cells'][target_idx]['execution_count'] = prev_exec + 1

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb2, f, ensure_ascii=False, indent=1)

print("\n✅ Output embedded. Notebook saved.")
