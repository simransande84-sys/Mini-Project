"""
swap_dataset.py
Updates every CSV_PATH / read_csv reference in the notebook and all
Python scripts from DATASET.CSV -> DATSETminiproject.csv
"""
import json, re, os

NEW_CSV = 'DATSETminiproject.csv'
OLD_CSV = 'DATASET.CSV'

# ── 1. Update the notebook ────────────────────────────────────────
NB_PATH = r'hostel_complaint_prioritization.ipynb'
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

changed_cells = []
for i, cell in enumerate(nb['cells']):
    new_source = []
    modified = False
    for line in cell['source']:
        if OLD_CSV in line:
            line = line.replace(OLD_CSV, NEW_CSV)
            modified = True
        new_source.append(line)
    if modified:
        cell['source'] = new_source
        # clear stale outputs so re-run is clean
        if cell['cell_type'] == 'code':
            cell['outputs'] = []
            cell['execution_count'] = None
        changed_cells.append(i)

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"Notebook: updated {len(changed_cells)} cells — {changed_cells}")

# ── 2. Update Python scripts in the project root ──────────────────
scripts = [
    'standalone_train_save.py',
    'section2_validation_eda.py',
    'run_section1_cells.py',
    'run_section2_cells.py',
    'inject_section2.py',
    'fix_section1_full.py',
]

for script in scripts:
    if not os.path.exists(script):
        continue
    with open(script, 'r', encoding='utf-8') as f:
        content = f.read()
    if OLD_CSV in content:
        content = content.replace(OLD_CSV, NEW_CSV)
        with open(script, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated: {script}")

print(f"\nAll references changed from '{OLD_CSV}' -> '{NEW_CSV}'")
