import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Survey Data Cleaner", layout="wide")
st.title("🧹 Smart Survey Data Cleaner")

# --- Step 1: Upload file ---
uploaded_file = st.file_uploader("Upload a survey file (CSV or Excel)", type=["csv", "xlsx"])

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
