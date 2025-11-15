# data_clean3.py
import pandas as pd
import re

# --- Keyword patterns for initial inference ---
QUESTION_KEYWORDS = {
    r"date|time": "Datetime",
    r"satisfaction|rate|agree|importance": "Categorical",
    r"age": "Numeric/Scale",
    r"gender|sex": "Categorical",
    r"feedback|comment|describe|thought|explain|open|why|tell": "Free Text",
    r"location|city|state|country": "Categorical",
    r"zip": "ID/Unique",
    r"email|phone|id|name|record|user|uuid|timestamp|login": "ID/Unique",
}

# --- Function for Categorization ---
def infer_question_type(series, col, unique_threshold=20):
    """Infers the likely survey question type for a pandas Series."""
    n_unique = series.nunique(dropna=True)
    n_rows = len(series)
    # 1️⃣ Keyword-based detection
    for pattern, qtype in QUESTION_KEYWORDS.items():
        if re.search(pattern, col):
            return qtype
    if n_unique / n_rows > 0.95 and n_unique > unique_threshold:
        return "ID/Unique"
    if n_unique == 2:
        return "Binary"
    if n_unique <= unique_threshold:
        return "Categorical"
    if series.dtype == 'object' and n_unique > unique_threshold:
        return "Free Text"
    if pd.api.types.is_numeric_dtype(series):
        return "Numeric/Scale"
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

def _convert_datetime(df, datetime_cols):
    for col in datetime_cols:
        if col in df.columns: # Check if col exists
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

# --- THIS IS THE FUNCTION YOUR DASHBOARD IS LOOKING FOR ---
def process_and_analyze_data(df):
    """
    Cleans a survey dataframe and returns the cleaned df
    and an analysis of its column types.
    """
    
    # 1. Standardize column names
    #df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    # 2. Categorize columns for cleaning
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime"]).columns.tolist()
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()

    # 3. Apply cleaning functions
    df = _remove_empty_rows_columns(df)
    df = _strip_strings(df, text_cols)
    df = _convert_numeric(df, numeric_cols)
    df = _convert_datetime(df, datetime_cols)
    
    # 4. Perform analysis *after* cleaning
    column_categories = {}
    
    # Re-check datetime_cols after conversion, as some might be text initially
    final_datetime_cols = df.select_dtypes(include=["datetime"]).columns.tolist()

    for col in df.columns:
        if col in final_datetime_cols:
            column_categories[col] = "Date/Time"
        else:
            column_categories[col] = infer_question_type(df[col], col)
            
    # 5. Create the analysis dataframe
    category_df = pd.DataFrame(
        list(column_categories.items()), 
        columns=["Column Name", "Inferred Type"]
    )

    # 6. Return both results
    return df, category_df