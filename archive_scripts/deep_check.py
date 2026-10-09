"""
Deep check: scan notebook code for known runtime pitfalls
"""
import json, re

with open('hostel_complaint_prioritization.ipynb', 'rb') as f:
    nb = json.loads(f.read().decode('utf-8', errors='replace'))

issues = []
warnings_list = []

code_cells = [(i, cell) for i, cell in enumerate(nb['cells']) if cell['cell_type'] == 'code']
full_src = '\n'.join(''.join(c['source']) for _, c in code_cells)

checks = [
    # (pattern, severity, message)
    (r'%matplotlib',        'ERROR',   'IPython magic command found'),
    (r'multi_class=',       'ERROR',   'Deprecated multi_class= in LogisticRegression (removed in sklearn 1.6)'),
    (r'get_feature_names_out\(categorical_features\)', 'ERROR', 'OHE.get_feature_names_out() takes no args in new sklearn'),
    (r'sparse=False',       'WARNING', 'sparse= is old param; new sklearn uses sparse_output='),
    (r'sparse_output=False','OK',      'sparse_output= is correct for sklearn >= 1.2'),
    (r'X_train\b(?!_)',     'OK',      'X_train used (transformed matrix)'),
    (r'X_train_raw\b',      'OK',      'X_train_raw used (raw DataFrame)'),
    (r'final_model\b',      'OK',      'final_model referenced'),
    (r'best_tuned_name\b',  'OK',      'best_tuned_name referenced'),
    (r'loaded_model\b',     'OK',      'loaded_model referenced (from joblib.load)'),
]

print('RUNTIME PATTERN CHECK')
print('=' * 60)
found_errors = []
for pattern, severity, msg in checks:
    count = len(re.findall(pattern, full_src))
    if severity == 'ERROR' and count > 0:
        found_errors.append(f'  [ERROR] {msg}  (found {count} occurrence(s))')
    elif severity == 'WARNING' and count > 0:
        print(f'  [WARN ] {msg}  (found {count} occurrence(s))')
    elif severity == 'OK' and count > 0:
        print(f'  [ OK  ] {msg}')

if found_errors:
    print('\nERRORS FOUND:')
    for e in found_errors:
        print(e)
else:
    print('\n[ALL CLEAR] No critical runtime issues detected.')

# Check for undefined variables that are used cross-section
cross_section_vars = [
    ('results',          'Section 10 - comparison dict'),
    ('label_encoder',    'Section 5  - target encoder'),
    ('preprocessor',     'Section 6  - ColumnTransformer'),
    ('X_train_raw',      'Section 6  - raw train split'),
    ('X_test_raw',       'Section 6  - raw test split'),
    ('y_train',          'Section 6  - train labels'),
    ('y_test',           'Section 6  - test labels'),
    ('lr_model',         'Section 6  - LogisticRegression model'),
    ('rf_model',         'Section 7  - RandomForest model'),
    ('svm_model',        'Section 8  - LinearSVC model'),
    ('nb_model',         'Section 9  - Naive Bayes model'),
    ('final_model',      'Section 11/12 - tuned best model'),
    ('loaded_model',     'Section 12 - joblib loaded model'),
]

print('\nCross-Section Variable Definitions:')
print('-' * 55)
for var, section in cross_section_vars:
    defined = f'{var} =' in full_src or f'{var},' in full_src
    status = 'DEFINED' if defined else 'NOT FOUND'
    print(f'  {var:<20} -> {status:<10} ({section})')

print('\nCheck complete.')
