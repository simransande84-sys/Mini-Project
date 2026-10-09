"""
Final targeted fix: ensure %matplotlib is fully gone (comment or removed).
Also do one final validation pass.
"""
import json, re

with open('hostel_complaint_prioritization.ipynb', 'rb') as f:
    nb = json.loads(f.read().decode('utf-8', errors='replace'))

fixes = 0
for cell in nb['cells']:
    if cell['cell_type'] != 'code':
        continue
    src = ''.join(cell['source'])
    if '%matplotlib' in src:
        # Remove the line entirely (it's either commented or raw)
        new_lines = []
        for line in src.split('\n'):
            if '%matplotlib' in line:
                # skip it completely
                fixes += 1
                continue
            new_lines.append(line)
        cell['source'] = ['\n'.join(new_lines)]

with open('hostel_complaint_prioritization.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f'Removed {fixes} line(s) containing %matplotlib')
print('Notebook saved.')

# Final syntax check on extracted code
import subprocess, sys
# Re-extract
exec(open('extract_code.py').read())

result = subprocess.run(
    [sys.executable, '-m', 'py_compile', 'notebook_all_code.py'],
    capture_output=True, text=True
)
if result.returncode == 0:
    print('\nFINAL SYNTAX CHECK: PASSED - No errors!')
else:
    print(f'\nFINAL SYNTAX CHECK: FAILED\n{result.stderr}')
