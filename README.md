# Perth Property Market Analysis & Price Prediction

## 1. Project Overview

This project conducts an end-to-end analysis of the Perth real estate market using a dataset of property listings from Kaggle. The project's core objectives are:

1.  **Data Engineering:** To design and implement a robust ETL (Extract, Transform, Load) pipeline that cleans raw data and populates a structured, relational MySQL database.
2.  **Exploratory Data Analysis (EDA):** To uncover key trends, patterns, and insights from the cleaned data through SQL queries and Python-based visualizations.
3.  **Predictive Modeling:** To build and evaluate a machine learning model capable of predicting property prices based on their features.

This repository documents the entire workflow, from initial data inspection to the final analysis and modeling.

## 2. Tech Stack

- **Programming Language:** Python
- **Core Libraries:** Pandas, NumPy, Matplotlib, Seaborn, Scikit-learn
- **Database:** MySQL
- **Database Interface:** SQLAlchemy, PyMySQL
- **Development Environment:** Jupyter Notebook, Git, VS Code, MySQL Workbench

## 3. Database Schema Design

A relational **Star Schema** was designed to structure the data for optimal analytical querying and data integrity. This model separates descriptive attributes (Dimensions) from core transactional data (Facts).

**Final Schema Diagram:**

- **Fact Table:** `FACT_Properties` (Contains core metrics like price, land size, and foreign keys)
- **Dimension Tables:**
  - `DIM_Suburbs` (Unique suburbs and postcodes)
  - `DIM_Agencies` (Unique real estate agencies)
  - `DIM_Layouts` (Unique combinations of bedrooms and bathrooms)
  - `DIM_Primary_Schools` (Unique primary schools and their ICSEA scores)
  - `DIM_Secondary_Schools` (Unique secondary schools and their ICSEA scores)

This design ensures data consistency, reduces redundancy, and significantly improves query performance for analytical tasks.

_(The detailed `CREATE TABLE` script can be found in the `sql/create_tables.sql` file.)_

## 4. ETL (Extract, Transform, Load) Pipeline

A comprehensive ETL process was developed in a Jupyter Notebook to populate the MySQL database. This automated workflow is fully reproducible.

### 4.1. Extract

- Loaded the raw `perth_housing.csv` dataset into a pandas DataFrame.
- Loaded a custom `corrections.csv` file to manage rules for manual data fixes.

### 4.2. Transform

The transformation phase involved several critical steps to ensure data quality:

- **Manual Correction:** Programmatically applied fixes from `corrections.csv` to correct known data entry errors or delete invalid rows (e.g., properties with a price of $1).
- **Data Sanitization:** Standardized key categorical columns (`Agency_Name`, `Primary_School_Name`, `Secondary_School_Name`) by stripping hidden whitespace and converting to a consistent lowercase format. This was a crucial step to prevent `UNIQUE` constraint violations in the database.
- **Type Conversion:** Converted the `Date_Sold` column to a proper `datetime` object.
- **Feature Engineering:** Created a powerful `Layout` interaction feature by combining `Bedrooms` and `Bathrooms` (e.g., '3b2b') to capture the property's floor plan.

### 4.3. Load

- The ETL script first executes `sql/create_tables.sql` to drop and recreate all tables, ensuring an idempotent (safely re-runnable) process.
- Populated all `DIM_` tables with unique, sanitized data.
- Fetched the auto-generated primary keys from the `DIM_` tables.
- Merged these foreign keys back into the main dataset.
- Loaded the final, clean, and fully-related data into the central `FACT_Properties` table.

## 5. Exploratory Data Analysis (EDA)

_(This section will be filled with insights discovered from querying the database.)_

## 6. Predictive Modeling

_(This section will be updated after the modeling phase.)_
