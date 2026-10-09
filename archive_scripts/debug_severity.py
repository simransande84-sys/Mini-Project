"""
fix_severity_expectations.py
Fixes two incorrect expected-word entries in the severity test cell.
- "severely" -> the surviving token is "severely" or "severe" via lemmatizer.
  Check which form actually survives, then fix the expectation.
- "flooding" does NOT become "leaking" — fix expected word to "flooding" or correct form.
No other cells or files are modified.
"""
import re, warnings
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
    text = re.sub(r'\bleakage\b', 'leaking', text)
    text = re.sub(r'\bleak\b',    'leaking', text)
    text = re.sub(r'\belectricity\b', 'electric', text)
    text = text.replace("can't",    "cannot")
    text = text.replace("won't",    "wont")
    text = text.replace("isn't",    "is not")
    text = text.replace("doesn't",  "does not")
    text = text.replace("hasn't",   "has not")
    text = text.replace("haven't",  "have not")
    text = text.replace("wasn't",   "was not")
    text = text.replace("wouldn't", "would not")
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\b\d+\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    tokens = [_lemmatizer.lemmatize(w) for w in text.split()
              if w not in ALL_STOPWORDS and len(w) >= 2]
    return ' '.join(tokens)

# Debug the two failing sentences
s1 = "this is urgent, the pipe is severely leaking"
s2 = "severe flooding in the corridor, emergency action needed"
print("Debugging failing sentences:")
print(f"S1: '{s1}'")
print(f"  -> '{preprocess_text(s1)}'")
print(f"  tokens: {preprocess_text(s1).split()}")
print()
print(f"S2: '{s2}'")
print(f"  -> '{preprocess_text(s2)}'")
print(f"  tokens: {preprocess_text(s2).split()}")
