"""
run_all_cells.py
Executes every code cell in the notebook top-to-bottom,
rebuilding the namespace incrementally so each cell sees
variables defined by all previous cells.
"""
import json, sys, io, traceback, base64, re, warnings, time, os
warnings.filterwarnings('ignore')

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd, numpy as np
from collections import Counter
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet',   quiet=True)
nltk.download('omw-1.4',  quiet=True)

NB_PATH = r'hostel_complaint_prioritization.ipynb'
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

print(f"Total cells: {len(cells)}")

namespace = {}
exec_order = 1
errors = []

for i, cell in enumerate(cells):
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source']).strip()
    if not src:
        continue

    section_hint = ''
    # Look back for nearest markdown header
    for j in range(i-1, max(-1, i-5), -1):
        if cells[j]['cell_type'] == 'markdown':
            txt = ''.join(cells[j]['source'])
            if '##' in txt:
                section_hint = txt.strip().split('\n')[0][:60]
            break

    print(f"\n>>> Cell {i:3d} (exec #{exec_order:3d})  {section_hint[:50]}")

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
            # Print first 30 lines to console
            lines = stdout_val.splitlines()
            for line in lines[:30]:
                print(line, file=old_stdout)
            if len(lines) > 30:
                print(f"  ... ({len(lines)-30} more lines)", file=old_stdout)
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
        print(f"  !! ERROR: {e}", file=old_stdout)
        errors.append({'cell': i, 'exec': exec_order, 'error': str(e)})
        outputs.append({
            "output_type": "stream", "name": "stderr",
            "text": [err]
        })
    finally:
        sys.stdout = old_stdout

    cell['outputs'] = outputs
    cell['execution_count'] = exec_order
    exec_order += 1

# Save notebook with all outputs
with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\n{'='*65}")
print(f"Execution complete.")
print(f"  Total code cells executed: {exec_order - 1}")
print(f"  Errors encountered       : {len(errors)}")
if errors:
    print("\n  Error summary:")
    for e in errors:
        print(f"    Cell {e['cell']} (exec #{e['exec']}): {e['error'][:100]}")
else:
    print("  All cells ran successfully!")
print(f"  Notebook saved: {NB_PATH}")
