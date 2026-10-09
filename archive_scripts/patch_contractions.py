"""
patch_contractions.py
Adds contraction expansion to the preprocess_text function in the notebook.
Only modifies the one code cell containing preprocess_text — nothing else.
"""
import json

NB_PATH = r'hostel_complaint_prioritization.ipynb'

with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

# Find the code cell containing preprocess_text definition
target_cell_idx = None
for i, cell in enumerate(cells):
    if cell['cell_type'] == 'code' and 'def preprocess_text' in ''.join(cell['source']):
        target_cell_idx = i
        break

if target_cell_idx is None:
    print("ERROR: Could not find preprocess_text cell!")
    exit(1)

print(f"Found preprocess_text in cell {target_cell_idx}")

src = ''.join(cells[target_cell_idx]['source'])
print("\n--- CURRENT Step 2 (normalize) block ---")
# Show the area we're editing
start = src.find('# Step 2')
print(src[start:start+300])
print("---")

# The exact line to insert BEFORE the punctuation removal step
OLD_STEP3 = "    # Step 3: Remove punctuation (keep apostrophes for contractions briefly)\n    text = re.sub(r\"[^\\w\\s]\", ' ', text)\n"

NEW_STEP3 = (
    "    # Step 2b: Expand contractions BEFORE punctuation removal\n"
    "    # This ensures negation words survive the apostrophe-stripping step.\n"
    "    # e.g. \"fan isn't working\" -> \"fan is not working\" -> \"fan not working\"\n"
    "    text = text.replace(\"can't\",   \"cannot\")\n"
    "    text = text.replace(\"won't\",   \"wont\")\n"
    "    text = text.replace(\"isn't\",   \"is not\")\n"
    "    text = text.replace(\"doesn't\", \"does not\")\n"
    "    text = text.replace(\"hasn't\",  \"has not\")\n"
    "    text = text.replace(\"haven't\", \"have not\")\n"
    "    text = text.replace(\"wasn't\",  \"was not\")\n"
    "    text = text.replace(\"wouldn't\",\"would not\")\n"
    "\n"
    "    # Step 3: Remove punctuation\n"
    "    text = re.sub(r\"[^\\w\\s]\", ' ', text)\n"
)

if OLD_STEP3 not in src:
    print("ERROR: Could not find the exact Step 3 block to replace.")
    print("Looking for:")
    print(repr(OLD_STEP3))
    print("\nActual source around 'Step 3':")
    idx = src.find('Step 3')
    print(repr(src[max(0,idx-20):idx+200]))
    exit(1)

# Also update the len(w) >= 2 comment
OLD_COMMENT = "    # KEY FIX: len(w) >= 2  (old was > 2, which dropped 'no', 'ac')\n"
NEW_COMMENT = "    # KEY FIX: len(w) >= 2  — preserves important 2-character words such as 'no', 'ac'\n"

new_src = src.replace(OLD_STEP3, NEW_STEP3)
new_src = new_src.replace(OLD_COMMENT, NEW_COMMENT)

if new_src == src:
    print("WARNING: No changes were made — check the strings above.")
    exit(1)

# Write back as source lines
cells[target_cell_idx]['source'] = [new_src]
cells[target_cell_idx]['outputs'] = []          # clear stale output
cells[target_cell_idx]['execution_count'] = None

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print("\n✅ Patch applied successfully.")
print(f"   Cell {target_cell_idx} updated.")
print("\n--- NEW Step 2b + Step 3 block ---")
new_start = new_src.find('# Step 2b')
print(new_src[new_start:new_start+600])
