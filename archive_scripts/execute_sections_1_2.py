"""
execute_sections_1_2.py
Executes ALL code cells in Section 1 and Section 2 of the notebook
using DATSETminiproject.csv and embeds outputs.
"""
import json, sys, io, traceback, base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings('ignore')

NB_PATH = r'hostel_complaint_prioritization.ipynb'

with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

# Find Section 3 start (cells before it = Sections 1+2)
sec3_start = None
for i, cell in enumerate(cells):
    src = ''.join(cell['source'])
    if 'SECTION 3' in src and cell['cell_type'] == 'markdown':
        sec3_start = i
        break

print(f"Executing cells 0 to {sec3_start - 1} (Sections 1 & 2)")
print(f"Dataset: DATSETminiproject.csv")
print("=" * 60)

namespace = {}
exec_order = 1

for i in range(sec3_start):
    cell = cells[i]
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source']).strip()
    if not src:
        continue

    print(f"\n>>> Cell {i} (exec #{exec_order})")

    old_stdout = sys.stdout
    sys.stdout = io.StringIO()
    outputs = []
    figs_before = set(plt.get_fignums())

    try:
        exec(compile(src, f'<cell_{i}>', 'exec'), namespace)
        stdout_val = sys.stdout.getvalue()
        figs_after = set(plt.get_fignums())
        new_figs = figs_after - figs_before

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
            img_b64 = base64.b64encode(buf.read()).decode()
            outputs.append({
                "output_type": "display_data",
                "data": {"image/png": img_b64, "text/plain": ["<Figure>"]},
                "metadata": {}
            })
            plt.close(fig_num)
            print(f"  -> Figure captured", file=old_stdout)

        # Capture DataFrame display (df.head(), df.tail())
        lines = src.strip().split('\n')
        last_line = lines[-1].strip()
        if last_line and not last_line.startswith('#') and not last_line.startswith('print'):
            try:
                result = eval(last_line, namespace)
                if hasattr(result, '_repr_html_'):
                    html = result._repr_html_()
                    outputs.append({
                        "output_type": "execute_result",
                        "execution_count": exec_order,
                        "data": {
                            "text/html": html.splitlines(keepends=True),
                            "text/plain": [repr(result)]
                        },
                        "metadata": {}
                    })
                    print(f"  -> DataFrame displayed", file=old_stdout)
            except:
                pass

    except Exception as e:
        err = traceback.format_exc()
        print(f"  ERROR in cell {i}: {e}", file=old_stdout)
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

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\n{'='*60}")
print(f"✅ Sections 1 & 2 complete. {exec_order-1} code cells executed.")
print(f"   Dataset used: DATSETminiproject.csv")
print(f"   Notebook saved: {NB_PATH}")
