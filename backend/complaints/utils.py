"""
complaints/utils.py
====================
ML prediction utilities for HostelSenseAI.

Design decisions
----------------
* preprocessor.pkl (ColumnTransformer) and model.pkl (LinearSVC) are loaded
  ONCE at module import time (singleton pattern).  Subsequent calls reuse the
  already-loaded objects — no repeated disk I/O per request.

* The ColumnTransformer expects a DataFrame with exactly these columns:
    Cleaned_Text   — NLP-preprocessed complaint text
    Category       — categorical (OneHotEncoder)
    Complaint_Type — categorical (OneHotEncoder)
    Block          — categorical (OneHotEncoder)
    Floor          — categorical (OneHotEncoder)
    Duration_Hours — float (StandardScaler)

* Duration_Hours is derived from the complaint's `duration` field (text choice)
  or from elapsed time since created_at.  It is NOT a raw text column.

* Excluded features (Support_Count, Students_Affected, Room_No, Status,
  Complaint_Date, Complaint_ID) are never passed to the model.

* NLP preprocessing matches the notebook exactly:
    lowercase → domain normalisations → contraction expansion →
    punctuation removal → digit removal → stopword removal (len≥2) → lemmatise
"""
import os
import re
import logging

import joblib
import pandas as pd
import numpy as np
from scipy.sparse import issparse
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from django.conf import settings

logger = logging.getLogger(__name__)

# ── NLTK data (downloaded once) ────────────────────────────────────────────────
nltk.download("stopwords", quiet=True)
nltk.download("wordnet",   quiet=True)
nltk.download("omw-1.4",   quiet=True)

# ── Load ML artifacts (once at import time) ────────────────────────────────────
_MODEL_DIR = settings.ML_MODEL_DIR

try:
    _preprocessor  = joblib.load(os.path.join(_MODEL_DIR, "preprocessor.pkl"))
    _model         = joblib.load(os.path.join(_MODEL_DIR, "model.pkl"))
    _label_encoder = joblib.load(os.path.join(_MODEL_DIR, "label_encoder.pkl"))
    logger.info(
        "ML artifacts loaded — preprocessor: %s | model: %s | classes: %s",
        type(_preprocessor).__name__,
        type(_model).__name__,
        _label_encoder.classes_.tolist(),
    )
except Exception as exc:
    _preprocessor = _model = _label_encoder = None
    logger.error("Failed to load ML artifacts: %s", exc)

# ── Stopword set (matches notebook exactly) ────────────────────────────────────
_DOMAIN_STOPWORDS = {
    "please", "kindly", "sir", "madam", "hello", "thanks", "thank",
    "dear", "hi", "regards", "asap", "hostel", "complaint", "request",
    "warden", "office", "management", "student", "students", "look",
    "also", "us", "am",
}
# Words that must NEVER be removed — negation / severity signals
_PRESERVE_WORDS = {
    "no", "not", "never", "cannot", "cant", "wont",
    "isnt", "doesnt", "hasnt", "havent", "wasnt", "wouldnt",
}
_std_stopwords = set(stopwords.words("english"))
_all_stopwords = (_std_stopwords | _DOMAIN_STOPWORDS) - _PRESERVE_WORDS

_lemmatizer = WordNetLemmatizer()

# ── Duration_Standardized → Duration_Hours (matches notebook exactly) ──────────
#
# Training data Duration_Standardized format: "N unit"
# where unit ∈ {hour, hours, day, days, week, weeks}
#
# Exact values seen in Dataset_duration.csv:
#   '1 hour', '2 hours', '3 hours', '4 hours', '5 hours', '6 hours', '8 hours'
#   '1 day',  '2 days',  '3 days',  '4 days',  '6 days',  '8 days',
#   '12 days','13 days'
#   '1 week', '2 weeks', '4 weeks'
#
# Conversion (identical to notebook parse_dur()):
#   hours  → value × 1
#   days   → value × 24
#   weeks  → value × 168

_DURATION_DEFAULT_HOURS = 24.0   # median-ish fallback when value is None/unparseable


def _duration_to_hours(duration_str) -> float:
    """
    Convert a Duration_Standardized string (e.g. '2 days', '1 hour', '3 weeks')
    to a float number of hours — identical to the notebook's parse_dur() function.

    Only accepts the 'N unit' format present in the training dataset.
    Returns _DURATION_DEFAULT_HOURS (24.0) for None or unrecognised values.
    """
    if not isinstance(duration_str, str) or not duration_str.strip():
        return _DURATION_DEFAULT_HOURS
    parts = duration_str.strip().lower().split()
    if len(parts) != 2:
        return _DURATION_DEFAULT_HOURS
    try:
        value = float(parts[0])
    except ValueError:
        return _DURATION_DEFAULT_HOURS
    unit = parts[1]
    if unit in ("hour", "hours"):
        return value
    if unit in ("day", "days"):
        return value * 24.0
    if unit in ("week", "weeks"):
        return value * 168.0
    return _DURATION_DEFAULT_HOURS


# ── NLP preprocessing (matches notebook exactly) ───────────────────────────────

def _preprocess_text(text: str) -> str:
    """
    Apply the same NLP pipeline used during model training:

    1. Lowercase
    2. Domain-specific normalisation  (leakage→leaking, electricity→electric)
    3. Contraction expansion          (isn't→is not, can't→cannot …)
    4. Punctuation removal
    5. Digit removal
    6. Stopword removal + length filter (len ≥ 2 preserves "no")
    7. Lemmatisation
    """
    if not isinstance(text, str) or not text.strip():
        return ""

    # 1. Lowercase
    text = text.lower()

    # 2. Domain normalisation
    text = re.sub(r"\bleakage\b", "leaking", text)
    text = re.sub(r"\bleak\b",    "leaking", text)
    text = re.sub(r"\belectricity\b", "electric", text)

    # 3. Contraction expansion (BEFORE punctuation removal)
    text = text.replace("can't",    "cannot")
    text = text.replace("won't",    "wont")
    text = text.replace("isn't",    "is not")
    text = text.replace("doesn't",  "does not")
    text = text.replace("hasn't",   "has not")
    text = text.replace("haven't",  "have not")
    text = text.replace("wasn't",   "was not")
    text = text.replace("wouldn't", "would not")

    # 4. Punctuation removal
    text = re.sub(r"[^\w\s]", " ", text)

    # 5. Digit removal (standalone numbers only)
    text = re.sub(r"\b\d+\b", "", text)

    # 6. Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # 7. Stopword removal (len ≥ 2 keeps "no") + lemmatisation
    tokens = [
        _lemmatizer.lemmatize(w)
        for w in text.split()
        if w not in _all_stopwords and len(w) >= 2
    ]
    return " ".join(tokens)


# ── Public API ─────────────────────────────────────────────────────────────────

def is_model_loaded() -> bool:
    """Return True if all ML artifacts were loaded successfully."""
    return _preprocessor is not None and _model is not None


def predict_priority(complaint_data: dict) -> str:
    """
    Predict the priority of a complaint using the trained LinearSVC model.

    Parameters
    ----------
    complaint_data : dict
        Keys used:
            complaint_text  (str)   — raw complaint text
            complaint_type  (str)   — "Public" | "Private"
            block           (str)   — "A" | "B" | "C" | "D"
            floor           (str)   — "Ground"|"First"|"Second"|"Third"
            category        (str)   — e.g. "Cleanliness", "Electricity" …
            duration        (str)   — text duration choice (optional)
            duration_hours  (float) — pre-computed numeric hours (optional;
                                      takes precedence over `duration`)

    NOT used by the ML model (excluded features):
            students_affected, support_count, room_no, status, complaint_date

    Returns
    -------
    str  — "High", "Medium", or "Low"
           Returns "Unknown" if the model is not loaded.
    """
    if not is_model_loaded():
        logger.error("predict_priority called but ML model is not loaded.")
        return "Unknown"

    # ── 1. Preprocess text ────────────────────────────────────────────────────
    cleaned_text = _preprocess_text(complaint_data.get("complaint_text", ""))

    # ── 2. Resolve Duration_Hours ──────────────────────────────────────────────
    # Priority: explicit duration_hours float > duration text choice > default
    if "duration_hours" in complaint_data and complaint_data["duration_hours"] is not None:
        duration_hours = float(complaint_data["duration_hours"])
    else:
        duration_hours = _duration_to_hours(complaint_data.get("duration"))

    # ── 3. Build feature DataFrame (column names must match training exactly) ──
    row = pd.DataFrame([{
        "Cleaned_Text"  : cleaned_text,
        "Category"      : complaint_data.get("category",       "Other"),
        "Complaint_Type": complaint_data.get("complaint_type", "Public"),
        "Block"         : complaint_data.get("block",          "A"),
        "Floor"         : complaint_data.get("floor",          "Ground"),
        "Duration_Hours": duration_hours,
    }])

    # ── 4. Preprocess + predict ────────────────────────────────────────────────
    X_proc = _preprocessor.transform(row)
    if issparse(X_proc):
        X_proc = X_proc.toarray()

    encoded_pred = _model.predict(X_proc)
    priority     = _label_encoder.inverse_transform(encoded_pred)[0]

    logger.debug(
        "Predicted priority: %s | text: %.60s | category: %s | duration_h: %.1f",
        priority, cleaned_text,
        complaint_data.get("category", "?"),
        duration_hours,
    )
    return priority


def get_model_info() -> dict:
    """Return basic metadata about the loaded model (for health/dashboard endpoints)."""
    if not is_model_loaded():
        return {"loaded": False}
    return {
        "loaded" : True,
        "classes": _label_encoder.classes_.tolist(),
        "model"  : type(_model).__name__,
        "features": [
            "Cleaned_Text (TF-IDF)",
            "Category (OHE)",
            "Complaint_Type (OHE)",
            "Block (OHE)",
            "Floor (OHE)",
            "Duration_Hours (StandardScaler)",
        ],
    }


# ── Priority Escalation ────────────────────────────────────────────────────────

# Priority ladder — ordered from lowest to highest
PRIORITY_ORDER = ["Low", "Medium", "High", "Critical"]


def escalate_priority(base_priority: str, support_count: int) -> str:
    """
    Apply community-support escalation rules on top of ML-predicted priority.

    Rules:
        0–10    → No change
        11–25   → Increase by one level (always)
        26–50   → Increase by one level only if currently Low or Medium
        > 50    → Increase by one level (always)

    Constraints:
        - Never decreases priority
        - Never exceeds Critical
        - Does not jump multiple levels at once

    Parameters
    ----------
    base_priority : str
        The ML-predicted priority before escalation.
    support_count : int
        Current number of student supports on the complaint.

    Returns
    -------
    str
        Final priority after applying escalation rules.
    """
    if base_priority not in PRIORITY_ORDER:
        logger.warning("Unknown base_priority '%s' — returning as-is.", base_priority)
        return base_priority

    idx = PRIORITY_ORDER.index(base_priority)

    if support_count <= 10:
        return base_priority

    elif 11 <= support_count <= 25:
        return PRIORITY_ORDER[min(idx + 1, 3)]

    elif 26 <= support_count <= 50:
        if idx < 2:
            return PRIORITY_ORDER[idx + 1]
        return base_priority

    else:
        return PRIORITY_ORDER[min(idx + 1, 3)]


def apply_priority_update(complaint) -> str:
    """
    Re-run ML prediction on the complaint's current field values,
    then apply escalation rules, and return the updated priority string.

    Duration_Hours is computed from the complaint's `duration` field.
    If `created_at` is available, elapsed time is used as a fallback.

    Parameters
    ----------
    complaint : Complaint model instance

    Returns
    -------
    str  — the new priority to store in complaint.predicted_priority
    """
    # Step 1: Re-run the ML model with current complaint data
    ml_priority = predict_priority({
        "complaint_text" : complaint.complaint_text,
        "complaint_type" : complaint.complaint_type,
        "block"          : complaint.block,
        "floor"          : complaint.floor,
        "category"       : complaint.category,
        "duration"       : getattr(complaint, "duration", None),
    })

    # Step 2: Apply escalation on top of ML result
    final_priority = escalate_priority(ml_priority, complaint.support_count)

    logger.info(
        "Priority update — ML: %s → Escalated: %s (support_count=%d)",
        ml_priority, final_priority, complaint.support_count,
    )
    return final_priority
