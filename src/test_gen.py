# app.py
import streamlit as st
import pandas as pd
import io
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import data_clean3 as data_cleaner

# --- Visualization functions (unchanged) ---
def plot_id(series):
    count = series.nunique()
    st.metric(f"Total Unique Values", count)
    st.info("This column is likely a unique identifier. The most relevant metric is the count of unique entries.")

def plot_binary(series):
    counts = series.value_counts().reset_index()
    counts.columns = ['Category', 'Count']
    fig = px.pie(counts, values='Count', names='Category', title='Response Distribution')
    st.plotly_chart(fig, use_container_width=True)

def plot_categorical(series):
    counts = series.value_counts().reset_index()
    counts.columns = ['Category', 'Count']
    st.bar_chart(counts.set_index('Category'))

def plot_numeric(series):
    data_to_plot = series.dropna()
    if data_to_plot.empty:
        st.info("This column contains no numeric data to plot.")
        return
    fig = px.histogram(data_to_plot, nbins=20, title='Response Distribution')
    fig.update_layout(bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)

def plot_text(series):
    st.info("Word Cloud generated from the most frequent words.")
    if series.dropna().empty:
        st.info("This column contains no text data to visualize.")
        return
    text = ' '.join(series.dropna().astype(str))
    if not text:
        st.info("This column contains no text data to visualize.")
        return
    try:
        stopwords = ["nan"]
        wordcloud = WordCloud(width=800, height=400, background_color='white', min_font_size=10, stopwords=stopwords).generate(text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    except ValueError:
        st.warning("Could not generate word cloud. (Perhaps all words were filtered out?)")

# --- Streamlit App ---
st.set_page_config(page_title="Survey Data Cleaner", layout="wide")
st.title("🧹 Smart Survey Data Cleaner")

uploaded_file = st.file_uploader("Upload a survey file (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
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

    st.subheader("⚙️ Cleaning in Progress...")
    try:
        cleaned_df, category_df = data_cleaner.process_and_analyze_data(df.copy())
        #st.subheader("📊 Auto-Detected Question Types")
        #st.dataframe(category_df, use_container_width=True)

        # ---------------- MANUAL OVERRIDE SECTION ----------------
        st.subheader("🧭 Manual Override of Question Categories")

        st.info("You can adjust any inferred type below. Changes will update the visualizations automatically.")

        type_options = ["ID/Unique", "Binary", "Categorical", "Numeric/Scale", "Free Text"]

        # Create a copy to store user overrides
        override_df = category_df.copy()

        # Let users pick overrides with selectboxes
        for i, row in override_df.iterrows():
            col1, col2 = st.columns([3, 2])
            with col1:
                st.write(f"**{row['Column Name']}**")
            with col2:
                new_type = st.selectbox(
                    f"Type for {row['Column Name']}",
                    options=type_options,
                    index=type_options.index(row["Inferred Type"]) if row["Inferred Type"] in type_options else 0,
                    key=f"override_{i}"
                )
                override_df.at[i, "Inferred Type"] = new_type

        # Apply button
        if st.button("✅ Apply Overrides and Refresh Visualizations"):
            category_df = override_df.copy()
            st.success("Overrides applied successfully!")

        # ---------------- CLEANED DATA AND DOWNLOAD ----------------
        st.subheader("✨ Cleaned Data Preview")
        st.dataframe(cleaned_df.head(), use_container_width=True)

        buffer = io.BytesIO()
        cleaned_df.to_csv(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="📥 Download Cleaned Data (CSV)",
            data=buffer,
            file_name="cleaned_survey_data.csv",
            mime="text/csv"
        )

        # ---------------- VISUALIZATIONS ----------------
        st.subheader("📈 Detailed Visualizations by Column Type")

        id_cols = category_df[category_df["Inferred Type"] == "ID/Unique"]
        binary_cols = category_df[category_df["Inferred Type"] == "Binary"]
        cat_cols = category_df[category_df["Inferred Type"] == "Categorical"]
        num_cols = category_df[category_df["Inferred Type"] == "Numeric/Scale"]
        text_cols = category_df[category_df["Inferred Type"] == "Free Text"]

        tab_cat, tab_num, tab_text, tab_id = st.tabs([
            f"📊 Categorical ({len(binary_cols) + len(cat_cols)})",
            f"🔢 Numeric ({len(num_cols)})",
            f"✍️ Free Text ({len(text_cols)})",
            f"🆔 ID Fields ({len(id_cols)})"
        ])

        # --- Categorical & Binary ---
        with tab_cat:
            st.header("Categorical & Binary Data")
            all_cat_cols = pd.concat([binary_cols, cat_cols])
            if all_cat_cols.empty:
                st.info("No categorical or binary columns found.")
            else:
                grid_cols = st.columns(3)
                for idx, row in all_cat_cols.iterrows():
                    col_name = row["Column Name"]
                    with grid_cols[idx % 3]:
                        with st.container(border=True):
                            st.subheader(col_name)
                            if row["Inferred Type"] == "Binary":
                                plot_binary(cleaned_df[col_name])
                            else:
                                plot_categorical(cleaned_df[col_name])

        # --- Numeric ---
        with tab_num:
            st.header("Numeric (Scale) Data")
            if num_cols.empty:
                st.info("No numeric/scale columns found.")
            else:
                grid_cols = st.columns(2)
                for idx, row in num_cols.iterrows():
                    col_name = row["Column Name"]
                    with grid_cols[idx % 2]:
                        with st.container(border=True):
                            st.subheader(col_name)
                            plot_numeric(cleaned_df[col_name])

        # --- Free Text ---
        with tab_text:
            st.header("Free Text Data (Word Clouds)")
            if text_cols.empty:
                st.info("No free text columns found.")
            else:
                grid_cols = st.columns(2)
                for idx, row in text_cols.iterrows():
                    col_name = row["Column Name"]
                    with grid_cols[idx % 2]:
                        with st.container(border=True):
                            st.subheader(col_name)
                            plot_text(cleaned_df[col_name])

        # --- ID ---
        with tab_id:
            st.header("ID / Unique Identifier Fields")
            if id_cols.empty:
                st.info("No ID/Unique columns found.")
            else:
                grid_cols = st.columns(4)
                for idx, row in id_cols.iterrows():
                    col_name = row["Column Name"]
                    with grid_cols[idx % 4]:
                        with st.container(border=True):
                            st.subheader(col_name)
                            plot_id(cleaned_df[col_name])

    except Exception as e:
        st.error(f"Error during processing or visualization: {e}")
        st.exception(e)
