"""
Diagnostic: extract all code cells from the notebook and run them
together to find errors.
"""
import json, sys

with open('hostel_complaint_prioritization.ipynb', 'rb') as f:
    nb = json.loads(f.read().decode('utf-8', errors='replace'))

code_cells = [(i, cell) for i, cell in enumerate(nb['cells']) if cell['cell_type'] == 'code']
print(f'Total code cells: {len(code_cells)}')
print()
for idx, (i, cell) in enumerate(code_cells):
    src = ''.join(cell['source'])
    first_line = src.strip().split('\n')[0][:90]
    print(f'[{idx+1:3d}] nb_cell={i:3d} | {first_line}')
