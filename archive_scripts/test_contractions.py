import re, warnings, sys
warnings.filterwarnings('ignore')
import nltk
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

DOMAIN_STOPWORDS = {
    'please','kindly','sir','madam','hello','thanks','thank',
    'dear','hi','regards','asap','hostel','complaint','request',
    'warden','office','management','student','students','look','also','us','am',
}
STD_STOPWORDS  = set(stopwords.words('english'))
ALL_STOPWORDS  = STD_STOPWORDS.union(DOMAIN_STOPWORDS)
PRESERVE_WORDS = {'no','not','never','cannot','cant','wont','isnt',
                  'doesnt','hasnt','havent','wasnt','wouldnt'}
ALL_STOPWORDS -= PRESERVE_WORDS
_lemmatizer = WordNetLemmatizer()

def preprocess_text(text):
    if not isinstance(text, str) or not text.strip():
        return ''
    text = text.lower()
    # Domain normalization
    text = re.sub(r'\bleakage\b', 'leaking', text)
    text = re.sub(r'\bleak\b',    'leaking', text)
    text = re.sub(r'\belectricity\b', 'electric', text)
    # Step 2b: Contraction expansion BEFORE punctuation removal
    text = text.replace("can't",    "cannot")
    text = text.replace("won't",    "wont")
    text = text.replace("isn't",    "is not")
    text = text.replace("doesn't",  "does not")
    text = text.replace("hasn't",   "has not")
    text = text.replace("haven't",  "have not")
    text = text.replace("wasn't",   "was not")
    text = text.replace("wouldn't", "would not")
    # Step 3: Remove punctuation
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = [_lemmatizer.lemmatize(w) for w in text.split()
              if w not in ALL_STOPWORDS and len(w) >= 2]
    return ' '.join(tokens)

# Test all contractions
print("Contraction Expansion Test:")
print("-" * 65)
tests = [
    "fan isn't working",
    "water doesn't come properly",
    "it hasn't been fixed since last week",
    "we can't sleep due to noise",
    "the door won't close properly",
    "the toilet wasn't cleaned",
    "we wouldn't report if it wasn't urgent",
    "they haven't fixed it",
    "there is no water",
    "the light is not working",
]

all_ok = True
for txt in tests:
    result = preprocess_text(txt)
    neg_found = [w for w in ['no','not','cannot','cant','wont','isnt',
                              'doesnt','hasnt','havent','wasnt','wouldnt']
                 if w in result.split()]
    print(f"  Original : {txt}")
    print(f"  Cleaned  : {result}")
    print(f"  Negation : {neg_found if neg_found else 'none (expected for some)'}")
    print()

print("\nKey example from user request:")
example = "fan isn't working"
cleaned = preprocess_text(example)
print(f'  "{example}" -> "{cleaned}"')
ok = 'not' in cleaned.split()
print(f'  "not" preserved: {"YES ✅" if ok else "NO ❌"}')
