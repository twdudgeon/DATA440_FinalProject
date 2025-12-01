# Data 440 Final Project

![Python](https://img.shields.io/badge/Python-3.8%2B-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B)

## ℹ️ Overview

This project is a **Streamlit-based dashboard** designed to automate the cleaning and visualization of survey data. It allows users to upload a raw `.CSV` file and instantly generate an interactive dashboard of insights.

The tool is specifically engineered for survey data, handling the transition from raw responses to categorized visual trends without requiring manual data manipulation or external contractors.

## 💡 Quick Start Guide
[Quick Start Guide Here](QuickStart.md)

## 🌟 Highlights

- **Automated Data Cleaning:** The system automatically sanitizes and pre-processes raw datasets to ensure compatibility with visualization tools.
- **Instant Visualization:** Converts CSV column headers and response rows into meaningful charts and graphs immediately upon upload.
- **Smart Categorization:** Automatically organizes visualizations based on detected data categories.
- **Flexible Management:** Includes functionality for users to manually reorganize data categories to fit specific reporting needs.

## 📂 Data Structure Requirements

To ensure the dashboard functions correctly, the uploaded `.CSV` file should be structured as follows:

- **Row 1 (Header):** Survey Questions (Variables)
- **Rows 2+:** Survey Responses (Data Points)

> **Note:** The application is optimized for standard survey formats where the first column represents the primary identifier or first question, and subsequent columns represent associated responses.

## 💭 Purpose

We developed this tool to help organizations democratize their data analysis. Many organizations collect feedback but struggle to utilize it due to the technical barriers of data cleaning and visualization. 

By automating the "reading" of data into a helpful dashboard, we aim to remove the need for:
- Combing through massive spreadsheets manually.
- Hiring external contractors for basic data tasks.
- Extensive technical training for workforce members.

Ultimately, this project lowers the hurdle for analyzing trends, allowing organizations to react to feedback faster and more effectively.

## ✍️ Authors

**Meredith Weiner & Tate Dudgeon** *Students at the College of William & Mary, Class of 2025*

**Project Repository:** [View on GitHub](https://github.com/twdudgeon/DATA440_FinalProject)

## Dashboard Description

This part will describe the various categories, visualizations, and human side interactions of the dashboard
 
