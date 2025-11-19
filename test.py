import data_clean as data_cleaner
import pandas as pd

def test_process_and_analyze_data():
    df = pd.read_excel("Copy of Post Trip Survey Results - MW.xlsx")
    cleaned_df, category_df = data_cleaner.process_and_analyze_data(df.copy())
    print(category_df)

if __name__ == "__main__":
    test_process_and_analyze_data()