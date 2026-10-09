"""
rerun_section3.py
Re-executes all Section 3 code cells with the patched preprocess_text
and embeds fresh outputs into the notebook.
"""
import json, sys, io, traceback, base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings, re, time
warnings.filterwarnings('ignore')

import pandas as pd, numpy as np
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet',   quiet=True)
nltk.download('omw-1.4',  quiet=True)
from collections import Counter

CLASS_ORDER  = ['High', 'Medium', 'Low']
PALETTE      = {'High': '#E74C3C', 'Medium': '#F39C12', 'Low': '#27AE60'}
RANDOM_STATE = 42
df = pd.read_csv('DATSETminiproject.csv')

namespace = {
    'pd': pd, 'np': np, 'plt': plt, 're': re,
    'nltk': nltk, 'time': time, 'Counter': Counter,
    'CLASS_ORDER': CLASS_ORDER, 'PALETTE': PALETTE,
    'RANDOM_STATE': RANDOM_STATE, 'df': df,
}

NB_PATH = r'hostel_complaint_prioritization.ipynb'
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

sec3_start = sec4_start = None
for i, cell in enumerate(cells):
    src = ''.join(cell['source'])
    if sec3_start is None and 'SECTION 3' in src and cell['cell_type'] == 'markdown':
        sec3_start = i
    if sec3_start is not None and i > sec3_start:
        if 'SECTION 4' in src and cell['cell_type'] == 'markdown':
            sec4_start = i
            break

prev_exec = max(
    (c.get('execution_count') or 0)
    for c in cells[:sec3_start]
    if c['cell_type'] == 'code'
)
exec_order = prev_exec + 1

print(f"Re-running Section 3: cells {sec3_start} to {sec4_start-1}")

for i in range(sec3_start, sec4_start):
    cell = cells[i]
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source']).strip()
    if not src:
        continue

    print(f">>> Cell {i} (exec #{exec_order})")

    old_stdout = sys.stdout
    sys.stdout  = io.StringIO()
    outputs     = []
    figs_before = set(plt.get_fignums())

    try:
        exec(compile(src, f'<cell_{i}>', 'exec'), namespace)
        stdout_val = sys.stdout.getvalue()
        figs_after = set(plt.get_fignums())
        new_figs   = figs_after - figs_before

        if stdout_val.strip():
            print(stdout_val, file=old_stdout)
            outputs.append({
                "output_type": "stream", "name": "stdout",
                "text": stdout_val.splitlines(keepends=True)
            })
        for fig_num in sorted(new_figs):
            fig = plt.figure(fig_num)
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            img_b64 = base64.b64encode(buf.read()).decode()
            outputs.append({
                "output_type": "display_data",
                "data": {"image/png": img_b64, "text/plain": ["<Figure>"]},
                "metadata": {}
            })
            plt.close(fig_num)
            print(f"  -> Figure captured", file=old_stdout)

    except Exception as e:
        err = traceback.format_exc()
        print(f"  ERROR in cell {i}: {e}", file=old_stdout)
        outputs.append({
            "output_type": "stream", "name": "stderr",
            "text": [err]
        })
    finally:
        sys.stdout = old_stdout

    cell['outputs'] = outputs
    cell['execution_count'] = exec_order
    exec_order += 1

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\n✅ Section 3 re-executed with contraction handling.")
print(f"   Cleaned_Text present: {'Cleaned_Text' in namespace['df'].columns}")
print(f"\nKey test — fan isn't working:")
fn = namespace.get('preprocess_text')
if fn:
    r = fn("fan isn't working")
    print(f"  -> '{r}'  ('not' in result: {'not' in r.split()})")
