# Perth Property Market - Full Stack Data Analysis & BI Web App

This repository documents an end-to-end data analysis project, evolving from a raw dataset to a fully interactive Business Intelligence (BI) web application for exploring the Perth real estate market.

**Live Application (Example URL):**
![alt text](image.png)

## 1. Project Overview & Objectives

This project was conceived as a comprehensive portfolio piece to demonstrate a wide range of data-centric skills, including:

- **Data Engineering:** Designing a robust relational database schema and building an automated ETL pipeline to clean, transform, and load raw data.
- **Backend Development:** Creating a powerful API and server-side logic using Python and Flask to handle complex, data-driven requests.
- **Frontend Development:** Building a user-friendly, responsive, and interactive user interface with HTML, CSS, and modern JavaScript to present data insights.
- **Data Analysis & BI:** Providing users with powerful tools to perform multi-dimensional analysis, compare market segments, and derive actionable insights from the data.

## 2. Tech Stack

| Category               | Technology / Library                                            |
| ---------------------- | --------------------------------------------------------------- |
| **Programming**        | Python 3.10+                                                    |
| **Backend**            | Flask                                                           |
| **Database**           | MySQL                                                           |
| **DB Interface (ORM)** | SQLAlchemy, PyMySQL                                             |
| **Data Manipulation**  | Pandas                                                          |
| **Frontend**           | HTML5, CSS3, JavaScript                                         |
| **JS Libraries**       | Choices.js (for searchable dropdowns), Google Maps API (Places) |
| **Development**        | Jupyter Notebook, VS Code, Git, MySQL Workbench                 |
| **Environment**        | `python-dotenv` for secret management                           |

## 3. Data Engineering: The ETL Pipeline & Database

The foundation of this application is a well-structured relational database populated by a reproducible ETL process.

### 3.1. Database Schema Design

A **Star Schema** was designed and implemented in MySQL. This model separates descriptive attributes (Dimensions) from core transactional data (Facts), ensuring data integrity and optimizing analytical query performance.

- **Fact Table:** `FACT_Properties` (Stores core metrics like price, land size, dates, and foreign keys)
- **Dimension Tables:**
  - `DIM_Suburbs` (Unique suburbs and postcodes)
  - `DIM_Agencies` (Unique real estate agencies)
  - `DIM_Layouts` (Unique combinations of bedrooms & bathrooms)
  - `DIM_Primary_Schools` & `DIM_Secondary_Schools` (Decoupled school dimensions with ICSEA scores)

_(The full DDL script is available in `sql/create_tables.sql`.)_

### 3.2. The ETL (Extract, Transform, Load) Process

A Python script, initially prototyped in a Jupyter Notebook, performs the following automated steps:

1.  **Extract:** Loads the raw `perth_housing.csv` and a custom `corrections.csv` for auditable manual fixes.
2.  **Transform:**
    - **Data Sanitization:** A critical step that standardizes key text fields (e.g., Suburb, Agency) by stripping whitespace and enforcing a consistent lowercase format to prevent data duplication.
    - **Type Conversion:** Converts date columns to `datetime` objects.
    - **Feature Engineering:** Creates powerful interaction features like `Layout` ('3b2b') from existing data.
3.  **Load:** Populates the five `DIM_` tables with unique, sanitized data, then uses the returned primary keys to populate the central `FACT_Properties` table, correctly establishing all relationships.

## 4. Full Stack Web Application

The core of this project is an interactive Flask web application that serves as a BI dashboard.

### 4.1. Feature: Data Entry (`/add`)

A user-friendly form for adding new property records, featuring:

- **Address Autocomplete:** Integrates the **Google Maps Places API** to provide real-time address suggestions and auto-fill Suburb and Postcode information, significantly improving user experience and data quality.
- **Searchable Dropdowns:** Implements **Choices.js** for long lists like Agency and Schools, allowing users to find options by typing.
- **Robust Validation:** Employs both client-side (HTML5) and server-side (Flask) validation to ensure data integrity (e.g., checking for unique Listing IDs).
- **Mock Mode:** A toggleable mode that allows testing the form's functionality by saving data to a temporary in-memory list instead of the live database.

### 4.2. Feature: Multi-Dimensional Comparison (`/compare`)

The main analytical engine of the application, allowing users to:

- **Filter by Multiple Dimensions:** Select one or more **Suburbs**, **Years**, and **Layouts** to create highly specific market segments for analysis.
- **Dynamic Granularity:** The application intelligently aggregates and groups data based on the user's selections. A query for (2 Suburbs x 3 Years) will generate 6 unique summary cards, providing precise, non-aggregated insights.
- **Dynamic Color-Coding:** A sophisticated algorithm based on the **Golden Ratio** assigns a unique and visually distinct color to each selected suburb. This color is used consistently in filter tags and result cards, dramatically improving data readability.
- **Clear & Responsive UI:** An "Active Filters" bar provides context for the results, which are displayed in a fully responsive CSS Grid layout that adapts from 4 columns on desktop to a single column on mobile.

## 5. Feature: interactive map

## 6. Predictive Modeling: House Price Prediction

The final and most advanced feature of this project is a machine learning model that predicts property prices. This section details the end-to-end data science workflow, from feature engineering to model deployment via the web application.

_(The full experimental process is documented in the `model_training.ipynb` notebook.)_

### 6.1. Advanced Feature Engineering: Isolating Location Value

A critical challenge in real estate prediction is accurately quantifying the value of "location" while controlling for a property's physical attributes. A sophisticated, two-stage modeling approach was implemented to solve this:

1.  **Stage 1: Location-Agnostic Base Model:** A baseline RandomForest model was trained using _only_ the physical features of properties (e.g., bedrooms, bathrooms, land size, property type). This model learned the "average" price for a property of a certain specification, irrespective of its location.

2.  **Stage 2: Residual Analysis:** This base model was used to predict the price of every property in the dataset. The **residual** (`actual_price - predicted_price`) was then calculated for each sale. This residual represents the **"pure location premium"**—the portion of the price attributable to location alone.

3.  **Final Feature Creation:** The average residual (or "location premium") was calculated for each suburb. These premiums were then used to segment all suburbs into four distinct **`suburb_value_tier`** categories ('Standard', 'Good', 'High', 'Premium'). This data-driven, low-dimensionality feature became the primary geographical input for the final model, effectively solving the "suburb vs. postcode" dilemma.

### 6.2. Model Training & Evaluation

- **Model Choice:** A `RandomForestRegressor` was chosen for the final predictive model due to its high performance on tabular data, robustness to outliers, and its ability to provide clear feature importance scores.

- **Data Preparation:** The final feature set included both numerical attributes (e.g., `land_size`, `distance_to_cbd`) and the one-hot encoded `suburb_value_tier`.

- **Training:** The model was trained on an 80% split of the dataset, with 20% held back as an unseen test set for final evaluation.

### 6.3. Model Performance & Insights

The trained model demonstrated strong predictive power and provided valuable insights into the Perth property market.

**Performance Metrics:**

- **Test Set R-squared (R²):** **0.7972**
  - _This indicates that the model can explain approximately **79.7%** of the variance in property prices, a strong result for a complex market._
- **Test Set Root Mean Squared Error (RMSE):** **~$260,464**
  - _This represents the typical error margin of the model's price predictions._

**Top 5 Most Important Features:**
The model revealed the key drivers of property value in Perth:

1.  **`primary_school_icsea` (30.7%)**: The quality of the local primary school is, by a significant margin, the single most important predictor of price.
2.  **`bathrooms` (22.2%)**: The number of bathrooms has a greater impact on price than the number of bedrooms.
3.  **`land_size` (18.9%)**: The size of the property block remains a fundamental value driver.
4.  **`distance_to_cbd` (9.8%)**: Proximity to the city center is a major factor.
5.  **`tier_Premium Value` (6.3%)**: Our engineered feature, identifying if a property is in a top-tier suburb, proved to be highly influential.

### 6.4. Deployment: The `/predict` Page

The trained model and its required column structure were serialized using `joblib` (`property_price_predictor.pkl` & `model_columns.pkl`). These assets are loaded by the Flask application at startup to power the `/predict` page, where users can input property features and receive an instant price estimation, completing the full "model-to-production" lifecycle.
