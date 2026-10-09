"""
fix_severity_expectations.py
Corrects two wrong expected-word entries in the severity test cell.
  - 'severe' -> 'severely'  (the sentence uses the adverb form)
  - 'leaking' -> 'flooding'  (the sentence uses 'flooding', not 'leaking')
Only cell 66 is touched. No other files modified.
"""
import json

NB_PATH = r'hostel_complaint_prioritization.ipynb'
with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)
cells = nb['cells']

# Find severity test cell
target_idx = None
for i, cell in enumerate(cells):
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if 'SEVERITY_WORDS' in src and 'VERIFY SEVERITY' in src:
            target_idx = i
            break

if target_idx is None:
    print("ERROR: Cannot find severity test cell.")
    exit(1)

src = ''.join(cells[target_idx]['source'])

# Fix 1: sentence uses "severely" not "severe"
OLD1 = "     ['urgent', 'severe', 'leaking']),"
NEW1 = "     ['urgent', 'severely', 'leaking']),"

# Fix 2: sentence uses "flooding" not "leaking"
OLD2 = "    ('severe flooding in the corridor, emergency action needed',\n     ['severe', 'emergency', 'leaking']),   # 'flooding' may lemmatize; test severe+emergency"
NEW2 = "    ('severe flooding in the corridor, emergency action needed',\n     ['severe', 'flooding', 'emergency']),"

new_src = src.replace(OLD1, NEW1)
new_src = new_src.replace(OLD2, NEW2)

if new_src == src:
    print("WARNING: Could not find strings to replace. Showing nearby context:")
    idx = src.find('urgent')
    print(repr(src[idx:idx+200]))
    idx2 = src.find('flooding')
    print(repr(src[idx2-10:idx2+150]))
    exit(1)

cells[target_idx]['source'] = [new_src]
cells[target_idx]['outputs'] = []
cells[target_idx]['execution_count'] = None

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"✅ Fixed severity test expectations in cell {target_idx}.")
print("   'severe' -> 'severely' (sentence uses adverb form)")
print("   'leaking' -> 'flooding' (sentence uses 'flooding')")
print("   No other cells or files modified.")
