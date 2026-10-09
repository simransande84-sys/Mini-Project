"""
patch_severity_test.py
Updates ONLY the severity word preservation test cell in Section 3.
No other cells, scripts, or files are modified.
"""
import json

NB_PATH = r'hostel_complaint_prioritization.ipynb'

with open(NB_PATH, 'r', encoding='utf-8') as f:
    nb = json.load(f)

cells = nb['cells']

# Find the exact cell containing the severity word test
target_idx = None
for i, cell in enumerate(cells):
    if cell['cell_type'] == 'code':
        src = ''.join(cell['source'])
        if 'VERIFY SEVERITY' in src or 'severity_words' in src:
            target_idx = i
            break

if target_idx is None:
    print("ERROR: Could not find severity test cell.")
    exit(1)

print(f"Found severity test cell at index {target_idx}")
print("Current source (first 200 chars):")
print(''.join(cells[target_idx]['source'])[:200])

# New improved cell source
new_source = """\
# ============================================================
# 3.6  VERIFY SEVERITY / SIGNAL WORDS ARE PRESERVED BY PREPROCESSING
#
# PURPOSE: This test ONLY checks that important words survive the
# NLP preprocessing pipeline. It does NOT claim that finding a
# severity word guarantees any particular ML model prediction.
# ============================================================

# Words that carry severity/negation signal and must NOT be lost.
# Duplicates removed; list is deduplicated.
SEVERITY_WORDS = [
    'urgent', 'emergency', 'dangerous', 'unsafe', 'severe',
    'broken', 'leaking', 'fire', 'shock',
    'no', 'not', 'cannot',
]

# Test sentences: each targets one or more specific signal words
test_cases = [
    # Negation words
    ("there is no water in the cooler",
     ['no']),
    ("the fan is not working since yesterday",
     ['not']),
    ("we cannot sleep because of the noise",
     ['cannot']),
    # Contractions (expand before punctuation removal)
    ("the AC won't turn on",
     ['wont']),
    ("the tap doesn't stop dripping",
     ['not']),          # doesn't -> does not -> 'not' survives
    # Severity / urgency words
    ("this is urgent, the pipe is severely leaking",
     ['urgent', 'severe', 'leaking']),
    ("there was an electrical shock from the broken socket",
     ['shock', 'broken']),
    ("the situation is dangerous and unsafe for students",
     ['dangerous', 'unsafe']),
    ("there is a fire risk near the generator room",
     ['fire']),
    ("severe flooding in the corridor, emergency action needed",
     ['severe', 'emergency', 'leaking']),   # 'flooding' may lemmatize; test severe+emergency
]

print("Severity and Negation Word Preservation Test")
print("=" * 65)
print("PURPOSE: Verify words survive NLP preprocessing only.")
print("         This does NOT predict ML model output.")
print("=" * 65)

all_pass = True
for sentence, expected_words in test_cases:
    cleaned = preprocess_text(sentence)
    cleaned_tokens = cleaned.split()

    # Find which expected words actually survived
    found   = [w for w in expected_words if w in cleaned_tokens]
    missing = [w for w in expected_words if w not in cleaned_tokens]

    passed = len(missing) == 0
    if not passed:
        all_pass = False
    status = "PASS ✅" if passed else "FAIL ❌"

    print(f"\\n  [{status}]")
    print(f"  Original : {sentence}")
    print(f"  Cleaned  : {cleaned}")
    print(f"  Expected words  : {expected_words}")
    print(f"  Words found     : {found}")
    if missing:
        print(f"  Words MISSING   : {missing}  ← needs attention")

print("\\n" + "=" * 65)
if all_pass:
    print("  ✅ All signal words survived preprocessing.")
else:
    print("  ⚠  Some signal words were lost. Review preprocessing.")
print("=" * 65)

# Explicit check for the key negation word 'no'
no_test  = preprocess_text("there is no water and no electricity")
not_test = preprocess_text("fan isn't working")   # isn't -> is not -> 'not'

print(f"\\nExplicit negation checks:")
print(f"  'no'  in \\"there is no water...\\":  {{'no' in no_test.split()}}  -> cleaned: \\"{no_test}\\"")
print(f"  'not' in \\"fan isn't working\\":     {{'not' in not_test.split()}} -> cleaned: \\"{not_test}\\"")
"""

cells[target_idx]['source'] = [new_source]
cells[target_idx]['outputs'] = []
cells[target_idx]['execution_count'] = None

with open(NB_PATH, 'w', encoding='utf-8') as f:
    json.dump(nb, f, ensure_ascii=False, indent=1)

print(f"\n✅ Severity test cell {target_idx} updated.")
print("   No other cells modified.")
