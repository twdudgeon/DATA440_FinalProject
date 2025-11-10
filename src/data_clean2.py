# cleaning_functions.py
import pandas as pd

# --- Function for Categorization ---
def infer_question_type(series, unique_threshold=20):
    """Infers the likely survey question type for a pandas Series."""
    # Count of unique, non-NaN values
    n_unique = series.nunique(dropna=True)
    n_rows = len(series)

    # 1. ID/Unique Check (High unique count)
    if n_unique / n_rows > 0.95 and n_unique > unique_threshold:
        return "ID/Unique"

    # 2. Binary Check (2 unique values)
    if n_unique == 2:
        return "Binary"

    # 3. Categorical Check (Low to medium unique count)
    if n_unique <= unique_threshold:
        return "Categorical"

    # 4. Free Text Check (High unique count for string columns)
    if series.dtype == 'object' and n_unique > unique_threshold:
        return "Free Text"

    # 5. Numeric/Scale Check
    if pd.api.types.is_numeric_dtype(series):
        return "Numeric/Scale"

    # Default fallback
    return "Other"

# --- Cleaning Helper Functions ---
# (These were defined inside your original 'if' block)

def remove_empty_rows_columns(df):
    df.dropna(how="all", inplace=True)
    df.dropna(axis=1, how="all", inplace=True)
    df.drop_duplicates(inplace=True)
    return df

def strip_strings(df, text_cols):
    for col in text_cols:
        df[col] = df[col].astype(str).str.strip()
    return df

def convert_numeric(df, numeric_cols):
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def convert_datetime(df, datetime_cols):
    for col in datetime_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

# --- Main Cleaning Function ---
# (Slightly modified to accept the col lists as arguments)

def clean_data(df, text_cols, numeric_cols, datetime_cols):
    df = remove_empty_rows_columns(df)
    df = strip_strings(df, text_cols)
    df = convert_numeric(df, numeric_cols)
    df = convert_datetime(df, datetime_cols)
    return df