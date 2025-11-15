# app.py
import streamlit as st
import pandas as pd
import io

# --- IMPORT YOUR CLEANING FUNCTIONS ---
import data_clean3 as data_cleaner
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

# --- 3. Plot function for Categorical (Bar Chart) [CHANGE 1] ---
def plot_categorical(series, color): # Added 'color' parameter
    """Displays a Plotly bar chart for categorical data."""
    # 
    # Get value counts
    counts = series.value_counts().reset_index()
    counts.columns = ['Category', 'Count']
    
    # Optional: Sort values for a cleaner chart (e.g., highest to lowest)
    counts = counts.sort_values(by="Count", ascending=False)
    
    # Create Plotly bar chart instead of st.bar_chart
    fig = px.bar(counts, 
                 x='Category',      # Categories on the x-axis
                 y='Count',         # Count on the y-axis
                 title='Response Distribution',
                 color_discrete_sequence=[color] # Use the passed-in color
                )
    
    st.plotly_chart(fig, use_container_width=True)

# --- 4. Plot function for Numeric/Scale (Histogram) ---
def plot_numeric(series, color):
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
                       title='Response Distribution',
                       color_discrete_sequence=[color] # Set the bar color
                      )
    fig.update_layout(bargap=0.1) # Add a small gap between bars
    st.plotly_chart(fig, use_container_width=True)

# --- 5. Plot function for Free Text (Word Cloud) ---
def plot_text(series):
    """Displays a word cloud for free text data."""
    # 
    st.info("Word Cloud generated from the most frequent words. Common 'stop words' are removed.")
    
    # 1. Get the series, drop actual np.nan values, and convert all to string
    cleaned_series = series.dropna().astype(str)
    
    # 2. Define a set of null-like strings to exclude
    #    We check against a lower-case version
    cleaned_series_lower = cleaned_series.str.lower()
    null_strings = {'nan', 'none', 'null', ''} # Add others if needed
    
    # 3. Create a mask for values that are NOT in null_strings
    mask = ~cleaned_series_lower.isin(null_strings)
    
    # 4. Apply the mask to the original (non-lowercased) series
    filtered_series = cleaned_series[mask]

    # 5. Check if the filtered series is empty
    if filtered_series.empty:
        st.info("This column contains no text data to visualize (after filtering nulls).")
        return
        
    # 6. Combine all text
    text = ' '.join(filtered_series)
    
    if not text: # Fallback check
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

        # --- NEW: DETAILED VISUALIZATIONS (Tabs with Column Grids) ---
        st.subheader("📈 Detailed Visualizations by Column Type")

        # 1. Filter your category_df to get lists of columns for each type
        id_cols = category_df[category_df["Inferred Type"] == "ID/Unique"]
        binary_cols = category_df[category_df["Inferred Type"] == "Binary"]
        cat_cols = category_df[category_df["Inferred Type"] == "Categorical"]
        num_cols = category_df[category_df["Inferred Type"] == "Numeric/Scale"]
        text_cols = category_df[category_df["Inferred Type"] == "Free Text"]

        # Define a color palette to cycle through
        color_palette = px.colors.qualitative.Plotly 

        # 2. Create the main tabs
        #    We can combine Binary and Categorical since they are similar
        tab_cat, tab_num, tab_text, tab_id = st.tabs([
            f"📊 Categorical ({len(binary_cols) + len(cat_cols)})", 
            f"🔢 Numeric ({len(num_cols)})", 
            f"✍️ Free Text ({len(text_cols)})",
            f"🆔 ID Fields ({len(id_cols)})"
        ])


        # --- Populate the "Categorical & Binary" Tab [CHANGE 2] ---
        with tab_cat:
            st.header("Categorical & Binary Data")
            
            # Combine the two lists
            all_cat_cols = pd.concat([binary_cols, cat_cols])
            
            if all_cat_cols.empty:
                st.info("No categorical or binary columns found.")
            else:
                # 3. Create a grid (e.g., 3 columns)
                grid_cols = st.columns(3)
                col_index = 0
                
                # 4. Loop through the *filtered* list and plot
                for index, row in all_cat_cols.iterrows():
                    col_name = row["Column Name"]
                    col_type = row["Inferred Type"]
                    
                    # Get the color for this specific chart
                    color_to_use = color_palette[col_index % len(color_palette)]
                    
                    # Place the plot in the next column, wrapping around
                    with grid_cols[col_index % 3]:
                        # Using a container with a border makes it look like a "card"
                        with st.container(border=True):
                            st.subheader(f"{col_name}")
                            if col_type == "Binary":
                                # Binary pie charts don't need a single color
                                plot_binary(cleaned_df[col_name])
                            else:
                                # Categorical bar charts get the single color
                                plot_categorical(cleaned_df[col_name], color_to_use)
                    
                    col_index += 1

        # --- Populate the "Numeric" Tab ---
        with tab_num:
            st.header("Numeric (Scale) Data")
            
            if num_cols.empty:
                st.info("No numeric/scale columns found.")
            else:
                # Histograms are wider, so 2 columns might be better
                grid_cols = st.columns(2) 
                col_index = 0
                
                for index, row in num_cols.iterrows():
                    col_name = row["Column Name"]
                    
                    # Get the color for this specific chart
                    color_to_use = color_palette[col_index % len(color_palette)]
                    
                    with grid_cols[col_index % 2]:
                        with st.container(border=True):
                            st.subheader(f"{col_name}")
                            # Pass the selected color to the plot function
                            plot_numeric(cleaned_df[col_name], color_to_use)
                    col_index += 1

        # --- Populate the "Free Text" Tab ---
        with tab_text:
            st.header("Free Text Data (Word Clouds)")
            
            if text_cols.empty:
                st.info("No free text columns found.")
            else:
                # Word clouds are also wide
                grid_cols = st.columns(2)
                col_index = 0
                
                for index, row in text_cols.iterrows():
                    col_name = row["Column Name"]
                    with grid_cols[col_index % 2]:
                        with st.container(border=True):
                            st.subheader(f"{col_name}")
                            plot_text(cleaned_df[col_name])
                    col_index += 1

        # --- Populate the "ID" Tab ---
        with tab_id:
            st.header("ID / Unique Identifier Fields")
            
            if id_cols.empty:
                st.info("No ID/Unique columns found.")
            else:
                # Metric cards are small and can fit in more columns
                grid_cols = st.columns(4)
                col_index = 0
                
                for index, row in id_cols.iterrows():
                    col_name = row["Column Name"]
                    with grid_cols[col_index % 4]:
                        # Note: plot_id() already uses st.metric, which looks 
                        # great on its own, but the border adds consistency.
                        with st.container(border=True): 
                            st.subheader(f"{col_name}")
                            plot_id(cleaned_df[col_name])
                    col_index += 1

    except Exception as e:
        st.error(f"Error during processing or visualization: {e}")
        st.exception(e) # Shows the full error for debugging