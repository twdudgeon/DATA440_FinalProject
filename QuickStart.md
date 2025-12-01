## ⬇️ Environment Set Up

This project is managed using [UV](https://docs.astral.sh/uv/guides/install-python/). If you do not yet have UV installed or need help troubleshooting issues with UV, refer to [their documentation](https://docs.astral.sh/uv/guides/install-python/).

Once you have UV installed, simply download the repository, navigate to the directory and run: `uv sync` to install dependencies.

To run the program:
1. First, from your terminal run `uv add streamlit`
2. To generate the dashboard run `uv run streamlit run app.py`
3. Once the webpage loads, upload your survey data.
4. Next, check that each survey question has been categorized correctly and mannually override inferred question types as needed. 
5. When you are finished in the dashboard, go to terminal and click Ctrl + C to end the streamlit session.