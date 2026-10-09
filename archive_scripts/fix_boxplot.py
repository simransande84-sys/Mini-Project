"""
fix_boxplot.py — Fix cell 56 boxplot 'labels' -> 'label' API change
"""
import json

NB_PATH = r'hostel_complaint_prioritization.ipynb'
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

target = None
for i, cell in enumerate(cells):
    if cell['cell_type'] == 'code' and 'boxplot' in ''.join(cell['source']) and 'Duration' in ''.join(cell['source']):
        target = i
        break

if target is None:
    print("ERROR: Could not find boxplot cell")
    exit(1)

src = ''.join(cells[target]['source'])
new_src = src.replace(
    'bp = axes[0].boxplot(data_by_priority, labels=CLASS_ORDER, patch_artist=True)',
    'bp = axes[0].boxplot(data_by_priority, tick_labels=CLASS_ORDER, patch_artist=True)'
)
if new_src == src:
    # Try the older form too
    new_src = src.replace(
        ', labels=CLASS_ORDER,',
        ', tick_labels=CLASS_ORDER,'
    )

cells[target]['source'] = [new_src]
cells[target]['outputs'] = []
cells[target]['execution_count'] = None

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"✅ Fixed boxplot labels in cell {target}")

# Re-run just that cell
import sys, io, traceback, base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd, numpy as np, re, warnings
warnings.filterwarnings('ignore')
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

CLASS_ORDER = ['High', 'Medium', 'Low']
PALETTE = {'High': '#E74C3C', 'Medium': '#F39C12', 'Low': '#27AE60'}

df = pd.read_csv('Dataset_duration.csv')

DOMAIN_STOPWORDS = {'please','kindly','sir','madam','hello','thanks','thank','dear','hi','regards','asap','hostel','complaint','request','warden','office','management','student','students','look','also','us','am'}
STD_STOPWORDS  = set(stopwords.words('english'))
ALL_STOPWORDS  = STD_STOPWORDS.union(DOMAIN_STOPWORDS)
PRESERVE_WORDS = {'no','not','never','cannot','cant','wont','isnt','doesnt','hasnt','havent','wasnt','wouldnt'}
ALL_STOPWORDS -= PRESERVE_WORDS
_lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if not isinstance(text, str) or not text.strip(): return ''
    text = text.lower()
    text = re.sub(r'\bleakage\b', 'leaking', text)
    text = re.sub(r'\bleak\b', 'leaking', text)
    text = re.sub(r'\belectricity\b', 'electric', text)
    text = text.replace("can't","cannot").replace("won't","wont").replace("isn't","is not")
    text = text.replace("doesn't","does not").replace("hasn't","has not")
    text = text.replace("haven't","have not").replace("wasn't","was not").replace("wouldn't","would not")
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return ' '.join(_lemmatizer.lemmatize(w) for w in text.split() if w not in ALL_STOPWORDS and len(w) >= 2)

df['Cleaned_Text'] = df['Complaint_Text'].apply(preprocess_text)

def _preview_parse(text):
    if not isinstance(text, str): return None
    parts = text.strip().lower().split()
    if len(parts) != 2: return None
    try: v = float(parts[0])
    except: return None
    u = parts[1]
    if u in ('hour','hours'): return v
    if u in ('day','days'): return v * 24
    if u in ('week','weeks'): return v * 168
    if u in ('month','months'): return v * 720
    return None

namespace = {
    'df': df, 'CLASS_ORDER': CLASS_ORDER, 'PALETTE': PALETTE,
    '_preview_parse': _preview_parse, 'plt': plt, 'np': np, 're': re,
    'preprocess_text': preprocess_text,
}

src_to_run = ''.join(cells[target]['source'])
old_stdout = sys.stdout
sys.stdout = io.StringIO()
outputs = []
figs_before = set(plt.get_fignums())

try:
    exec(compile(src_to_run, f'<cell_{target}>', 'exec'), namespace)
    stdout_val = sys.stdout.getvalue()
    figs_after = set(plt.get_fignums())
    new_figs = figs_after - figs_before
    if stdout_val.strip():
        print(stdout_val, file=old_stdout)
        outputs.append({"output_type": "stream", "name": "stdout", "text": stdout_val.splitlines(keepends=True)})
    for fig_num in sorted(new_figs):
        fig = plt.figure(fig_num)
        buf = io.BytesIO()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        outputs.append({"output_type": "display_data", "data": {"image/png": base64.b64encode(buf.read()).decode(), "text/plain": ["<Figure>"]}, "metadata": {}})
        plt.close(fig_num)
        print("  -> Figure captured", file=old_stdout)
except Exception as e:
    print(f"ERROR: {e}", file=old_stdout)
    outputs.append({"output_type": "stream", "name": "stderr", "text": [traceback.format_exc()]})
finally:
    sys.stdout = old_stdout

prev_exec = max((c.get('execution_count') or 0) for c in cells[:target] if c['cell_type'] == 'code')
cells[target]['outputs'] = outputs
cells[target]['execution_count'] = prev_exec + 1

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("✅ Cell re-executed and output embedded.")
