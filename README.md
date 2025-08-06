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

- **Manual Data Correction:** Programmatically corrected specific, known data entry errors using an external `corrections.csv` file. This process fixed or removed listings with demonstrably incorrect values (e.g., a price of $1), ensuring full reproducibility.
- **Data Integrity Decision:** After manual corrections, the remaining extreme values in `Price` and `Land_Size` were validated as legitimate market data points. A deliberate decision was made to **retain these outliers** to ensure the analysis reflects the full spectrum of the Perth real estate market, including high-value properties.
- **Technical Data Conversion:** Converted the `Date_Sold` column from a text-based format to a proper `datetime` object, a necessary step for any time-series or date-based analysis.
- **Feature Engineering:** Created new features (`Sale_Year`, `Sale_Month`, `Sale_DayOfWeek`) from the `Date_Sold` column to enable analysis of market trends over time.
