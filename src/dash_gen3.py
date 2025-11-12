# app.py
import streamlit as st
import pandas as pd
import io

# --- IMPORT YOUR CLEANING FUNCTIONS ---
import data_clean2 as data_cleaner
# --- NEW IMPORTS for visualizations ---
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# --- 1. Plot function for ID/Unique (Metric Card) ---
def plot_id(series):
    """Displays a large metric card for unique counts."""
    # 
    count = series.nunique()
    st.metric(f"Total Unique Values", count)
    st.info("This column is likely a unique identifier. The most relevant metric is the count of unique entries.")

# --- 2. Plot function for Binary (Pie Chart) ---
def plot_binary(series):
    """Displays a Plotly pie chart for binary data."""
    # 
    # Get value counts
    counts = series.value_counts().reset_index()
    counts.columns = ['Category', 'Count']
    
    # Create Plotly pie chart
    fig = px.pie(counts, 
                 values='Count', 
                 names='Category', 
                 title='Response Distribution')
    st.plotly_chart(fig, use_container_width=True)

# --- 3. Plot function for Categorical (Bar Chart) ---
def plot_categorical(series):
    """Displays a simple Streamlit bar chart for categorical data."""
    # 
    # Get value counts
    counts = series.value_counts().reset_index()
    counts.columns = ['Category', 'Count']
    
    # Use st.bar_chart, which expects the 'Category' to be the index
    counts_for_st = counts.set_index('Category')
    st.bar_chart(counts_for_st)

# --- 4. Plot function for Numeric/Scale (Histogram) ---
def plot_numeric(series):
    """Displays a Plotly histogram for numeric data."""
    # 
    # Drop NaNs for histogram calculation
    data_to_plot = series.dropna()
    
    if data_to_plot.empty:
        st.info("This column contains no numeric data to plot.")
        return
        
    # Use Plotly Express for histogram
    fig = px.histogram(data_to_plot, 
                       nbins=20,  # You can adjust the number of bins
                       title='Response Distribution')
    fig.update_layout(bargap=0.1) # Add a small gap between bars
    st.plotly_chart(fig, use_container_width=True)

# --- 5. Plot function for Free Text (Word Cloud) ---
def plot_text(series):
    """Displays a word cloud for free text data."""
    # 
    st.info("Word Cloud generated from the most frequent words. Common 'stop words' are removed.")
    
    # Check for empty series
    if series.dropna().empty:
        st.info("This column contains no text data to visualize.")
        return

    # Combine all text, dropping NaNs and converting to string
    text = ' '.join(series.dropna().astype(str))
    
    if not text:
        st.info("This column contains no text data to visualize.")
        return
        
    # Generate word cloud
    try:
        wordcloud = WordCloud(width=800, 
                              height=400, 
                              background_color='white',
                              stopwords=None, # You can add a set of custom stopwords
                              min_font_size=10
                             ).generate(text)
        
        # Display using matplotlib
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off') # Hide axes
        st.pyplot(fig)
    except ValueError as e:
        # Handle cases where text might be empty after processing
        st.warning(f"Could not generate word cloud. (Perhaps all words were filtered out?)")


# --- Original Dashboard Code (Starts Here) ---

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
        # Call the one main function from data_cleaner.py
        cleaned_df, category_df = data_cleaner.process_and_analyze_data(df.copy())
    
        # --- Display Analysis Table ---
        st.subheader("📊 Question Type Analysis")
        st.dataframe(category_df, use_container_width=True)

        # --- Display Cleaned Data Preview ---
        st.subheader("✨ Cleaned Data Preview")
        st.dataframe(cleaned_df.head(), use_container_width=True)

        # --- Download Button ---
        buffer = io.BytesIO()
        cleaned_df.to_csv(buffer, index=False)
        buffer.seek(0)
        st.download_button(
            label="📥 Download Cleaned Data (CSV)",
            data=buffer,
            file_name="cleaned_survey_data.csv",
            mime="text/csv"
        )

        # --- NEW: DETAILED VISUALIZATIONS SECTION ---
        st.subheader("📈 Detailed Visualizations by Column")
        
        # Loop through the category_df dataframe
        for index, row in category_df.iterrows():
            col_name = row["Column Name"]
            col_type = row["Inferred Type"]
            
            # Use an expander to keep things tidy
            with st.expander(f"Analysis for: {col_name} (Type: {col_type})"):
                
                # Select the right plot based on the type
                if col_type == "ID/Unique":
                    plot_id(cleaned_df[col_name])
                    
                elif col_type == "Binary":
                    plot_binary(cleaned_df[col_name])
                    
                elif col_type == "Categorical":
                    plot_categorical(cleaned_df[col_name])
                    
                elif col_type == "Numeric/Scale":
                    plot_numeric(cleaned_df[col_name])
                    
                elif col_type == "Free Text":
                    plot_text(cleaned_df[col_name])
                    
                else:
                    # Catch "Date/Time" or "Other"
                    st.info(f"No standard visualization for '{col_type}' type.")

    except Exception as e:
        st.error(f"Error during processing or visualization: {e}")
        st.exception(e) # Shows the full error for debugging