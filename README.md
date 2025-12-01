## 🌟 Highlights

- Generate visualizations with jsut a .CSV file
- Automatically organize visualizations based on category
- Reorganize manually if needed
- 


## ℹ️ Overview

This fileset is meant to generate a dashboard on a tab using streamlit, which will then allow for a user to input a .CSV file. The code will then automatically clean the data such that it can then be processed to automatically create visualizations on a dashboard. This is intended specifically for .csv data from surveys, with a primary first column being questions and the rest being responses (review .CSV we used to see if this correct)

### ✍️ Authors

Mention who you are and link to your GitHub or organization's website.

### 💭 Purpose

We created these files to help organizations automate the visualizations of large survey response data sets. This is meant to aid them in gaining a better understanding of their feedback without needing to comb through large sets of responses,hire a contractor to set up a visualization for them, or take time out of their work force to learn how to do so on their own.

## Dashboard Description

This part will describe the various categories, visualizations, and human side interactions of the dashboard

## ⬇️ Environment Set Up

This project is managed using [UV](https://docs.astral.sh/uv/guides/install-python/). If you do not yet have UV installed or need help troubleshooting issues with UV, refer to [their documentation](https://docs.astral.sh/uv/guides/install-python/).

Once you have UV installed, simply download the repository, navigate to the directory and run: `uv sync` to install dependencies.

To run the program:
1. First, from your terminal run `uv add streamlit`
2. To generate the dashboard run `uv run streamlit run .\src\dash_gen.py`
3. Once the webpage loads, upload your survey data.
4. Next, check that each survey question has been categorized correctly and mannually override inferred question types as needed. 
5. When you are finished in the dashboard, go to terminal and click Ctrl + C to end the streamlit session. 
