"""
final_fix_severity.py
Direct string replacement to fix the remaining 'leaking' expectation
in the last test case of the severity test cell.
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

src = ''.join(cells[target_idx]['source'])

# Print what we actually have around 'flooding'
idx = src.find('flooding')
print("Current context around 'flooding':")
print(repr(src[idx-20:idx+120]))
print()

# The fix: replace whatever 'leaking' expectation remains in the flooding test case
# Use a broader pattern
import re
# Find and replace the flooding test case expected list
old_pattern = r"(\('severe flooding in the corridor, emergency action needed',\s*\n\s*\[)([^\]]+)(\])"
match = re.search(old_pattern, src)
if match:
    print(f"Found: {match.group(0)}")
    new_src = re.sub(old_pattern,
                     r"\1'severe', 'flooding', 'emergency'\3",
                     src)
    cells[target_idx]['source'] = [new_src]
    cells[target_idx]['outputs'] = []
    cells[target_idx]['execution_count'] = None
    with open(NB_PATH, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=1)
    print("✅ Fixed. Saved notebook.")
else:
    print("Pattern not found. Showing full cell source for inspection:")
    print(src)
