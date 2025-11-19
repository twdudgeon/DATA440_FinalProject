# data_clean3.py
import pandas as pd
import re
from datetime import datetime

# --- Keyword patterns for initial inference ---
QUESTION_KEYWORDS = {
    r"satisfaction|rate|agree|importance": "Likert Scale",
    r"age": "Numeric",
    r"gender|sex": "Categorical",
    r"feedback|comment|describe|thought|explain|open|why|tell": "Free Text",
    r"location|city|state|country": "Categorical",
    r"zip": "ID/Unique",
    r"email|phone|id|name|record|user|uuid|login": "ID/Unique",
}


# --- Helper Functions for Specific Type Detection ---
LIKERT_OPTIONS = [
    ["strongly disagree", "disagree", "neutral", "agree", "strongly agree"],
    ["very unsatisfied", "unsatisfied", "neutral", "satisfied", "very satisfied"]
]

def is_likert(series):
    s = series.dropna()

    # ---------- 1. Detect numeric Likert scales ----------
    if pd.api.types.is_numeric_dtype(series):
        unique_vals = sorted(s.unique())

        if len(unique_vals) <= 7:  # Likert scales rarely exceed 7 levels
            span = max(unique_vals) - min(unique_vals)

            # Typical Likert spans are 3–6 points
            if 2 <= span <= 6:
                return True

    # ---------- 2. Detect text-based Likert options ----------
    text_vals = s.astype(str).str.lower().unique().tolist()

    # Partial matching allowed (only 2+ matching labels needed)
    LIKERT_KEYWORDS = [
        "strongly agree", "agree", "disagree", "strongly disagree",
        "satisfied", "unsatisfied", "neutral",
        "very", "somewhat"
    ]

    matches = sum(
        any(keyword in v for keyword in LIKERT_KEYWORDS)
        for v in text_vals
    )

    # If at least 2 Likert keywords appear → Likert
    if matches >= 2:
        return True

    return False

DATE_PATTERNS = [
    r"\d{4}-\d{1,2}-\d{1,2}",   # YYYY-MM-DD
    r"\d{1,2}/\d{1,2}/\d{4}",   # MM/DD/YYYY
    r"\d{1,2}-\d{1,2}-\d{4}",   # MM-DD-YYYY
    r"\d{4}/\d{1,2}/\d{1,2}",   # YYYY/MM/DD
]
DATETIME_PATTERNS = [
    r".*\d{4}-\d{1,2}-\d{1,2} \d{1,2}:\d{2}.*",
    r".*\d{1,2}/\d{1,2}/\d{4} \d{1,2}:\d{2}.*",
]

def is_datetime(series):
    return pd.api.types.is_datetime64_any_dtype(series)

def is_categorical(series, unique_threshold=20):
    n_unique = series.nunique(dropna=True)
    return n_unique <= unique_threshold

def is_numeric(series):
    return pd.api.types.is_numeric_dtype(series)

def is_binary(series):
    n_unique = series.nunique(dropna=True)
    return n_unique == 2

def is_freetext(series, unique_threshold=20, min_mean_length=20):
    if not pd.api.types.is_object_dtype(series):
        return False

    n_unique = series.nunique(dropna=True)
    if n_unique <= unique_threshold:
        return False

    # Check average length to differentiate from short IDs
    mean_len = series.dropna().astype(str).map(len).mean()
    return mean_len > min_mean_length

def is_id_field(series, uniqueness_threshold=0.95, max_mean_length=20):

    n_unique = series.nunique(dropna=True)
    n_total = len(series)
    uniqueness_ratio = n_unique / n_total

    # Only consider strings or numbers
    if not (pd.api.types.is_object_dtype(series) or pd.api.types.is_integer_dtype(series)):
        return False

    # If almost all values are unique AND values are short, likely an ID
    if uniqueness_ratio > uniqueness_threshold:
        # Optional: check average length for strings
        if pd.api.types.is_object_dtype(series):
            mean_len = series.dropna().astype(str).map(len).mean()
            if mean_len <= max_mean_length:
                return True
            else:
                return False
        return True
    return False

def keyword_match(col):
    col_lower = col.lower()
    for pattern, q_type in QUESTION_KEYWORDS.items():
        if re.search(pattern, col_lower):
            return q_type
    return None

def infer_question_type(series, col_name):
    # 1. Check keyword matches first
    keyword_type = keyword_match(col_name)
    if keyword_type:
        return keyword_type

    # 2. Use specific detection functions
    if keyword_type:
        return keyword_type
    if is_datetime(series):
        return "Datetime"
    if is_id_field(series):
        return "ID/Unique"
    if is_binary(series):
        return "Binary"
    if is_freetext(series):
        return "Free Text"
    if is_likert(series):
        return "Likert Scale"
    if is_categorical(series):
        return "Categorical"
    if is_numeric(series):
        return "Numeric"
    return "Other"

# --- Internal Helper Cleaning Functions ---
# (These are now "private" helpers, indicated by the _)

def _remove_empty_rows_columns(df):
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def _strip_strings(df, text_cols):
    for col in text_cols:
        if col in df.columns: # Check if col exists
            df[col] = df[col].astype(str).str.strip()
    return df

def _convert_numeric(df, numeric_cols):
    for col in numeric_cols:
        if col in df.columns: # Check if col exists
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

# --- THIS IS THE FUNCTION YOUR DASHBOARD IS LOOKING FOR ---
def process_and_analyze_data(df):
    """
    Cleans a survey dataframe and returns the cleaned df
    and an analysis of its column types.
    """
    # 1. Infer question types for each column
    column_categories = {}
    for col in df.columns:
        column_categories[col] = infer_question_type(df[col], col)

    # 2. Categorize columns for cleaning
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()

    # 3. Apply cleaning functions
    df = _remove_empty_rows_columns(df)
    df = _strip_strings(df, text_cols)
    df = _convert_numeric(df, numeric_cols)

            
    # 5. Create the analysis dataframe
    category_df = pd.DataFrame(
        list(column_categories.items()), 
        columns=["Column Name", "Inferred Type"]
    )

    # 6. Return both results
    return df, category_df