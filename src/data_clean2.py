import pandas as pd
import re
import streamlit as st

# --- Keyword patterns for initial inference ---
QUESTION_KEYWORDS = {
    r"satisfaction|rate|agree|importance": "Likert Scale",
    r"age": "Numeric/Continuous",
    r"gender|sex": "Categorical",
    r"feedback|comment|describe|thought|explain|open|why|tell": "Free Text",
    r"location|city|state|country": "Categorical",
    r"zip": "Numeric/ID",
    r"email|phone|id|name|record|user|uuid|timestamp|login": "Metadata/ID",
    r"date|time": "Datetime",
}


# --- Utility functions ---
def normalize_name(name: str):
    return re.sub(r'[^a-z0-9 ]+', ' ', name.lower())


def infer_type(name, series):
    name = normalize_name(name)
    s = series.dropna()
    n_unique, n_total = s.nunique(), len(s)

    # 1️⃣ Keyword-based detection
    for pattern, qtype in QUESTION_KEYWORDS.items():
        if re.search(pattern, name):
            return qtype

    # 2️⃣ Value-based inference
    if n_unique == 2:
        vals = [v.lower() for v in s.astype(str).unique()]
        if any(v in vals for v in ["yes","no","true","false","y","n","male","female"]):
            return "Binary (Yes/No)"
        return "Binary (Other)"

    if pd.api.types.is_numeric_dtype(series):
        if n_unique <= 7 and series.min() >= 1:
            return "Likert Scale"
        return "Numeric/Continuous"

    if pd.api.types.is_datetime64_any_dtype(series):
        return "Datetime"

    if s.astype(str).str.match(r"\d{4}-\d{2}-\d{2}").any():
        return "Datetime"

    # 3️⃣ Text-based inference
    avg_len = s.astype(str).str.len().mean()
    if avg_len > 40:
        return "Free Text"

    if n_unique / n_total < 0.3 and n_unique <= 20:
        return "Categorical"

    return "Free Text"


def auto_clean_data(df, type_overrides=None):
    """Clean data based on inferred or user-adjusted types."""
    df = df.dropna(how="all").dropna(axis=1, how="all").drop_duplicates()

    inferred = {col: infer_type(col, df[col]) for col in df.columns}
    if type_overrides:
        inferred.update(type_overrides)  # apply user changes

    for col, t in inferred.items():
        if "Text" in t or "Categorical" in t:
            df[col] = df[col].astype(str).str.strip()
        elif "Numeric" in t or "Likert" in t:
            df[col] = pd.to_numeric(df[col], errors="coerce")
        elif "Datetime" in t:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    summary = pd.DataFrame({
        "Column": inferred.keys(),
        "Detected Type": inferred.values()
    })

    return df, summary