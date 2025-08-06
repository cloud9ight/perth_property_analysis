# Perth Property Market Analysis & Price Prediction

## 1. Project Overview

This project conducts a comprehensive analysis of the Perth real estate market using a dataset of property listings from Kaggle. The primary goals are to perform robust data cleaning and feature engineering, identify the key drivers of property prices through in-depth exploratory data analysis, and ultimately build a machine learning model to predict property valuations. This project also demonstrates data engineering skills by designing and planning the population of a relational SQL database schema for scalable data management.

## 2. Tech Stack

- **Programming Language:** Python
- **Core Libraries:** Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn
- **Database Schema:** SQL (designed for SQLite/PostgreSQL/MySQL)
- **Development Environment:** Jupyter Notebook, Git, VS Code

## 3. Data Source

The dataset used is the "Perth Property Prices" dataset sourced from Kaggle. The raw dataset contains approximately 43,000 listings with 21 features, including property attributes, location details, and sale prices.

[Link to Dataset](https://www.kaggle.com/datasets/heptix/perth-property-prices)

## 4. Methodology

### 4.1. Data Cleaning & Preprocessing

A multi-stage cleaning process was implemented to ensure data quality and integrity.

- **Manual Data Correction:** Initial exploration revealed specific, significant errors in the raw data (e.g., properties with a price of $1). To handle this transparently, a `corrections.csv` file was created to house rules for fixing or deleting these known erroneous rows. A Python script programmatically applies these rules at the start of the workflow, ensuring that all corrections are documented and the process is 100% reproducible.
- **Data Type Correction:** Converted the `Date_Sold` column from an object to a `datetime` type to enable time-based analysis.
- **Automated Outlier Handling:** After manual corrections, a broader filtering process was applied to remove statistical outliers in `Price` and `Land_Size` (e.g., removing the top 1%) to prevent skew in models.
- **Feature Engineering:** Extracted `Sale_Year` and `Sale_Month` from the `Date_Sold` column to create features that can capture market seasonality and long-term trends.
