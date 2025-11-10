# app.py
import streamlit as st
import pandas as pd
import io

# --- IMPORT YOUR CLEANING FUNCTIONS ---
from data_clean2 import (
    infer_question_type, 
    clean_data, 
    remove_empty_rows_columns, 
    strip_strings, 
    convert_numeric, 
    convert_datetime
)
# Note: We import all functions here, even though clean_data is the main one,
# to match your original structure where they were all defined in the same place.

st.set_page_config(page_title="Survey Data Cleaner", layout="wide")
st.title("🧹 Smart Survey Data Cleaner")

# --- Step 1: Upload file ---
uploaded_file = st.file_uploader("Upload a survey file (CSV or Excel)", type=["csv", "xlsx"])

# --- (The infer_question_type function definition was here) ---
# (It has been removed and is now imported)

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

    #Categorize columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    datetime_cols = df.select_dtypes(include=["datetime"]).columns.tolist()
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()

    # --- (All cleaning function definitions were here) ---
    # (They have been removed and are now imported)

    # --- THIS IS THE ONLY LINE THAT REALLY CHANGES ---
    # We now pass the column lists to the imported function.
    cleaned_df = clean_data(df, text_cols, numeric_cols, datetime_cols)
    
    st.subheader("📊 Question Type Analysis")
    column_categories = {}
    
    # Iterate through cleaned columns and assign type
    for col in cleaned_df.columns:
        if col in datetime_cols: # This list is still defined locally
            column_categories[col] = "Date/Time"
        else:
            # This imported function is called just as before
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