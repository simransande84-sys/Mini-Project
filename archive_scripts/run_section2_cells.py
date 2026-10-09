"""
run_section2_cells.py
Executes only the Section 2 code cells and embeds their output into the notebook.
This is a fallback if nbconvert full-notebook execution fails.
"""
import json, sys, io, traceback
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

NB_PATH = r'hostel_complaint_prioritization.ipynb'

with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

# Find section 2 code cells (between SECTION 2 and SECTION 3 headings)
sec2_start = None
sec2_end   = None
for i, cell in enumerate(cells):
    src = ''.join(cell['source'])
    if sec2_start is None and 'SECTION 2' in src and cell['cell_type'] == 'markdown':
        sec2_start = i
    if sec2_start is not None and i > sec2_start:
        if 'SECTION 3' in src and cell['cell_type'] == 'markdown':
            sec2_end = i
            break

print(f"Section 2 cells: {sec2_start} to {sec2_end - 1}")

# Shared execution namespace
namespace = {}
exec_order = 1

for i in range(sec2_start, sec2_end):
    cell = cells[i]
    if cell['cell_type'] != 'code':
        continue
    
    src = ''.join(cell['source'])
    if not src.strip():
        continue

    print(f"\n{'='*60}")
    print(f"  Running cell {i} (exec #{exec_order})...")
    print(f"{'='*60}")
    
    # Capture stdout
    old_stdout = sys.stdout
    sys.stdout  = io.StringIO()
    
    outputs = []
    figures_before = set(plt.get_fignums())
    
    try:
        exec(compile(src, f'<cell_{i}>', 'exec'), namespace)
        stdout_val = sys.stdout.getvalue()
        
        # New figures created
        figures_after = set(plt.get_fignums())
        new_figs = figures_after - figures_before
        
        if stdout_val.strip():
            print(stdout_val, file=old_stdout)
            outputs.append({
                "output_type": "stream",
                "name": "stdout",
                "text": stdout_val.splitlines(keepends=True)
            })
        
        for fig_num in sorted(new_figs):
            fig = plt.figure(fig_num)
            buf = io.BytesIO()
            fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
            buf.seek(0)
            import base64
            img_b64 = base64.b64encode(buf.read()).decode()
            outputs.append({
                "output_type": "display_data",
                "data": {"image/png": img_b64, "text/plain": ["<Figure>"]},
                "metadata": {"image/png": {"width": 800}}
            })
            plt.close(fig_num)
            print(f"  -> Plot captured for cell {i}", file=old_stdout)
            
    except Exception as e:
        err = traceback.format_exc()
        print(f"  ERROR in cell {i}: {e}", file=old_stdout)
        print(err, file=old_stdout)
        outputs.append({
            "output_type": "stream",
            "name": "stderr",
            "text": [err]
        })
    finally:
        sys.stdout = old_stdout
    
    cell['outputs'] = outputs
    cell['execution_count'] = exec_order
    exec_order += 1

# Save
with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\n✅ Section 2 cells executed and outputs embedded.")
print(f"   Notebook saved: {NB_PATH}")
