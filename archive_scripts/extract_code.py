"""
Extract all code from the notebook into a single Python script for error checking.
"""
import json

with open('hostel_complaint_prioritization.ipynb', 'rb') as f:
    nb = json.loads(f.read().decode('utf-8', errors='replace'))

code_cells = [cell for cell in nb['cells'] if cell['cell_type'] == 'code']

full_code = []
full_code.append("# AUTO-EXTRACTED FROM NOTEBOOK FOR ERROR CHECKING\n")
full_code.append("import warnings; warnings.filterwarnings('ignore')\n\n")

for idx, cell in enumerate(code_cells):
    src = ''.join(cell['source'])
    full_code.append(f"\n# ====== CELL {idx+1} ======\n")
    full_code.append(src)
    full_code.append("\n")

with open('notebook_all_code.py', 'w', encoding='utf-8') as f:
    f.write(''.join(full_code))

print(f'Extracted {len(code_cells)} code cells into notebook_all_code.py')
print(f'Total lines: {len("".join(full_code).splitlines())}')
