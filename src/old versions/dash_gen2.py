# app.py
import streamlit as st
import pandas as pd
import io
from data_clean2 import auto_clean_data


st.set_page_config(page_title="🧹 Smart Survey Data Cleaner", layout="wide")

st.title("🧠 Smart Survey Data Cleaner (AI-Assisted)")

# --- Streamlit UI ---
uploaded = st.file_uploader("📁 Upload a survey file (CSV or Excel)", type=["csv", "xlsx"])

if uploaded:
    try:
        df = pd.read_csv(uploaded) if uploaded.name.endswith(".csv") else pd.read_excel(uploaded)
        st.success(f"Loaded {len(df)} rows × {len(df.columns)} columns.")
        st.write(df.head())
    except Exception as e:
        st.error(f"Error loading file: {e}")
        st.stop()

    # --- Step 2: Auto-infer question types ---
    st.subheader("🔍 Automatically Detected Question Types")
    _, type_summary = auto_clean_data(df)

    # --- Step 3: Let user override ---
    st.markdown("### ✏️ Review and adjust detected types (optional)")
    editable = st.data_editor(
        type_summary,
        hide_index=True,
        num_rows="fixed",
        use_container_width=True,
        column_config={"Detected Type": st.column_config.SelectboxColumn(options=[
            "Likert Scale", "Numeric/Continuous", "Categorical", "Free Text",
            "Binary (Yes/No)", "Binary (Other)", "Metadata/ID", "Datetime", "Other"
        ])}
    )

    # --- Step 4: Apply cleaning with user overrides ---
    if st.button("🚀 Clean and Finalize Data"):
        overrides = dict(zip(editable["Column"], editable["Detected Type"]))
        cleaned_df, final_summary = auto_clean_data(df, overrides)

        st.success("Data cleaned successfully!")
        st.write("### ✅ Final Schema")
        st.dataframe(final_summary, use_container_width=True)

        st.write("### 🧾 Cleaned Data Preview")
        st.dataframe(cleaned_df.head(10), use_container_width=True)

        # Optionally let user download cleaned data
        csv = cleaned_df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 Download Cleaned Data", csv, file_name="cleaned_survey.csv", mime="text/csv")