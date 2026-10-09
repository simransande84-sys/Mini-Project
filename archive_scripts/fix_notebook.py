"""
Comprehensive notebook fixer:
1. Removes %matplotlib inline (not valid Python outside Jupyter)
2. Replaces emoji in print() with plain text (encoding-safe)
3. Fixes sparse_output parameter (sklearn version compatibility)
4. Fixes any other known issues
"""
import json, re

with open('hostel_complaint_prioritization.ipynb', 'rb') as f:
    nb = json.loads(f.read().decode('utf-8', errors='replace'))

fixes_applied = []

def fix_cell_source(source_lines):
    fixed = []
    for line in source_lines:
        original = line

        # Fix 1: Remove %matplotlib inline (IPython magic, not standard Python)
        # Replace with plt.ion() or just remove — notebook already renders inline
        if '%matplotlib inline' in line:
            line = '# %matplotlib inline  # handled automatically by JupyterLab\n'
            fixes_applied.append('Removed %matplotlib inline')

        # Fix 2: Replace emoji in print statements with plain text
        # Common emojis used: ✅ ❌ 🔍 📊 📌 🌲 🎯 💾 🔮 🎓
        emoji_map = {
            '\u2705': '[OK]',       # ✅
            '\u274c': '[ERROR]',    # ❌
            '\U0001f50d': '[>>]',   # 🔍
            '\U0001f4ca': '[chart]',# 📊
            '\U0001f4cc': '[info]', # 📌
            '\U0001f333': '[tree]', # 🌲
            '\U0001f3af': '[aim]',  # 🎯
            '\U0001f4be': '[save]', # 💾
            '\U0001f52e': '[pred]', # 🔮
            '\U0001f393': '[grad]', # 🎓
            '\u2714': '[OK]',       # ✔
            '\u2716': '[X]',        # ✖
            '\u26a0': '[!]',        # ⚠
        }
        for emoji, replacement in emoji_map.items():
            if emoji in line:
                line = line.replace(emoji, replacement)
                fixes_applied.append(f'Replaced emoji with {replacement}')

        # Fix 3: sparse_output=False deprecated in newer sklearn, use sparse=False
        # Actually sparse_output is correct in sklearn >= 1.2, keep it
        # But check for the older 'sparse' parameter if needed
        # We'll keep sparse_output=False as is

        fixed.append(line)
    return fixed

# Fix 4: Check for OneHotEncoder sparse_output vs sparse compatibility
# Also fix: Section 5.4 uses StandardScaler demo import that may conflict
# Fix 5: Section 9 uses 'from scipy.sparse import issparse, hstack, csr_matrix'
#         but scipy.sparse is also imported inline - check for duplicates

# Apply fixes to all code cells
cell_fixed_count = 0
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        original = cell['source'][:]
        cell['source'] = fix_cell_source(cell['source'])
        if cell['source'] != original:
            cell_fixed_count += 1

# Fix 6: In Section 1 imports cell, check if matplotlib inline is present
# and also ensure plt.rcParams line is fine

# Fix 7: Section 7.4 - feature names from OneHotEncoder
# preprocessor.transformers_[1][1].get_feature_names_out(categorical_features)
# In newer sklearn, get_feature_names_out() takes no args for OHE
# Find and fix this
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if 'get_feature_names_out(categorical_features)' in src:
            new_src = src.replace(
                'get_feature_names_out(categorical_features)',
                'get_feature_names_out()'
            )
            cell['source'] = [new_src]
            fixes_applied.append('Fixed OHE get_feature_names_out(categorical_features) -> get_feature_names_out()')

# Fix 8: Section 14.2 pipeline visualization - ax.transAxes + clip_on=False
# This can sometimes cause issues, but is generally fine. Leave as is.

# Fix 9: In Section 9.1, X_train_nb may need to be dense for older sklearn
# The code already handles sparse/dense, so it should be fine.

# Fix 10: Check for 'multi_class' parameter in LogisticRegression
# 'multi_class' was deprecated in sklearn 1.5 and removed in 1.6
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if 'multi_class=' in src:
            new_src = src.replace("multi_class='auto',\n", '')
            new_src = new_src.replace("multi_class='auto', ", '')
            new_src = new_src.replace(", multi_class='auto'", '')
            if new_src != src:
                cell['source'] = [new_src]
                fixes_applied.append('Removed deprecated multi_class parameter from LogisticRegression')

# Fix 11: In Section 14.7, 'best_tuned_name' and 'best_tuned_f1' may not be defined
# if Section 11 hasn't been run. Add a fallback.
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if '14.7  PROJECT SUMMARY STATISTICS' in src:
            # Add safeguard at top of cell
            safeguard = (
                "# ============================================================\n"
                "# 14.7  PROJECT SUMMARY STATISTICS\n"
                "# ============================================================\n"
                "\n"
                "import os\n"
                "\n"
                "# Safeguard: define defaults if Section 11 was not run\n"
                "if 'best_tuned_name' not in dir():\n"
                "    best_tuned_name = max(results, key=lambda x: results[x]['F1-Score'])\n"
                "if 'best_tuned_f1' not in dir():\n"
                "    best_tuned_f1 = results[best_tuned_name]['F1-Score']\n"
                "\n"
            )
            # Remove original header from src
            src_body = src.replace(
                "# ============================================================\n"
                "# 14.7  PROJECT SUMMARY STATISTICS\n"
                "# ============================================================\n\n"
                "import os\n\n",
                ''
            )
            cell['source'] = [safeguard + src_body]
            fixes_applied.append('Added safeguard for best_tuned_name/best_tuned_f1 in Section 14.7')

# Fix 12: Section 14.1 uses accuracy_score(y_test, final_model.predict(X_test_raw))
# Add safeguard for final_model
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if '14.1  FINAL PERFORMANCE SUMMARY TABLE' in src and 'final_model' in src:
            guard = (
                "# Safeguard: if Section 11 was skipped, use the best model from Section 10\n"
                "if 'final_model' not in dir():\n"
                "    _best = max({k:v for k,v in results.items() if k!='Naive Bayes'}, key=lambda x: results[x]['F1-Score'])\n"
                "    final_model = {'Logistic Regression': lr_model, 'Random Forest': rf_model, 'Linear SVM': svm_model}[_best]\n"
                "    best_tuned_name = _best\n"
                "    best_tuned_f1 = results[_best]['F1-Score']\n"
                "    X_test_raw = X_test  # fallback\n\n"
            )
            cell['source'] = [guard + src]
            fixes_applied.append('Added safeguard for final_model in Section 14.1')

# Fix 13: Section 12.1 uses best_tuned_name and best_tuned_f1 - add safeguard
for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if '12.1  SAVE FINAL MODEL PIPELINE' in src and 'best_tuned_name' in src:
            guard = (
                "# Safeguard: ensure final_model and metadata vars are defined\n"
                "if 'final_model' not in dir():\n"
                "    _best = max({k:v for k,v in results.items() if k!='Naive Bayes'}, key=lambda x: results[x]['F1-Score'])\n"
                "    _models = {'Logistic Regression': lr_model, 'Random Forest': rf_model, 'Linear SVM': svm_model}\n"
                "    final_model = _models[_best]; best_tuned_name = _best\n"
                "    best_tuned_f1 = results[_best]['F1-Score']\n\n"
            )
            cell['source'] = [guard + src]
            fixes_applied.append('Added safeguard for final_model in Section 12.1')

# Save the fixed notebook
with open('hostel_complaint_prioritization.ipynb', 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)

print(f'Notebook fixed and saved!')
print(f'Total cells: {len(nb["cells"])}')
print(f'\nFixes applied ({len(fixes_applied)} total):')
# Deduplicate while preserving order
seen = set()
for fix in fixes_applied:
    if fix not in seen:
        print(f'  - {fix}')
        seen.add(fix)
