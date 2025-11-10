import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Survey Data Cleaner", layout="wide")
st.title("🧹 Smart Survey Data Cleaner")

# --- Step 1: Upload file ---
uploaded_file = st.file_uploader("Upload a survey file (CSV or Excel)", type=["csv", "xlsx"])

# --- New Function for Categorization ---
def infer_question_type(series, unique_threshold=20):
    """Infers the likely survey question type for a pandas Series."""
    # Count of unique, non-NaN values
    n_unique = series.nunique(dropna=True)
    n_rows = len(series)

    # 1. ID/Unique Check (High unique count)
    # If the number of unique values is very high (e.g., > 95% of rows), it's likely an ID or unique identifier.
    if n_unique / n_rows > 0.95 and n_unique > unique_threshold:
        return "ID/Unique"

    # 2. Binary Check (2 unique values)
    # Exclude Booleans, which are handled by dtypes, and look for two distinct object values.
    if n_unique == 2:
        return "Binary"

    # 3. Categorical Check (Low to medium unique count)
    # If unique values are manageable (e.g., less than the threshold), it's likely a multiple-choice or categorical question.
    if n_unique <= unique_threshold:
        return "Categorical"

    # 4. Free Text Check (High unique count for string columns)
    # If it's a string/object type and has many unique values but less than the ID threshold, it's probably open-ended text.
    if series.dtype == 'object' and n_unique > unique_threshold:
        return "Free Text"

    # 5. Numeric/Scale Check
    # Columns not caught by the above, but are numeric types, are likely scale (e.g., 1-5 rating) or raw numeric.
    if pd.api.types.is_numeric_dtype(series):
        # Numeric columns with few unique values might be ordinal scales (e.g., Likert scale 1-5).
        # We'll treat all remaining numeric columns as general "Numeric/Scale"
        return "Numeric/Scale"

    # Default fallback
    return "Other"

if uploaded_file:
    # --- Step 2: Load data ---
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.subheader("✅ Raw Data Preview")
        st.dataframe(df.head(), use_container_width=True)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        st.stop()

    # --- Step 3: Automatic Cleaning ---
    st.subheader("⚙️ Cleaning in Progress...")

    #standardize column names
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    #Categorize columns (I think we could use llms here)
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime"]).columns.tolist()
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()

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

    def clean_data(df):
        df = remove_empty_rows_columns(df)
        df = strip_strings(df, text_cols)
        df = convert_numeric(df, numeric_cols)
        df = convert_datetime(df, datetime_cols)
        return df

    cleaned_df = clean_data(df)

    st.subheader("📊 Question Type Analysis")
    column_categories = {}
    
    # Iterate through cleaned columns and assign type
    for col in cleaned_df.columns:
        # Skip Date/Time columns for visualization categorization
        if col in datetime_cols:
            column_categories[col] = "Date/Time"
        else:
            column_categories[col] = infer_question_type(cleaned_df[col])

    # Display the categorization
    category_df = pd.DataFrame(
        list(column_categories.items()), 
        columns=["Column Name", "Inferred Type"]
    )
    st.dataframe(category_df, use_container_width=True)

    # --- Step 4: Display cleaned data ---
    st.subheader("✨ Cleaned Data Preview")
    st.dataframe(cleaned_df.head(), use_container_width=True)

    # --- Step 5: Download cleaned file ---
    buffer = io.BytesIO()
    cleaned_df.to_csv(buffer, index=False)
    buffer.seek(0)

    st.download_button(
        label="📥 Download Cleaned Data (CSV)",
        data=buffer,
        file_name="cleaned_survey_data.csv",
        mime="text/csv"
    )
