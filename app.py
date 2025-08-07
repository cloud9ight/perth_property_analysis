# app.py - Final version with both /add and /explore routes

# --- 1. Imports and Setup ---
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, text
import pandas as pd
import logging
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = 'a_very_secret_key_for_flashing_messages'
logging.basicConfig(level=logging.INFO)

# This list will act as our in-memory "fake" database for new records.
# It will be reset every time the Flask server restarts.
fake_database_records = []

# --- 2. Database Connection ---
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = 'password' 
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'perth_property_db'
# Check if the database password was loaded
if not DB_PASS:
    raise ValueError("DB_PASS environment variable not set. Please create a .env file.")

try:
    db_connection_str = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(db_connection_str)
    logging.info("Successfully created database engine.")
except Exception as e:
    logging.error(f"Failed to create database engine: {e}")
    exit()

# --- 3. Helper function to get dimension data ---
# This avoids repeating code in both routes
def get_dimension_data():
    """Fetches all dimension data from the DB to populate dropdowns."""
    try:
        with engine.connect() as connection:
            suburbs = pd.read_sql("SELECT suburb_id, suburb_name FROM DIM_Suburbs ORDER BY suburb_name", connection).to_dict('records')
            layouts = pd.read_sql("SELECT layout_id, layout_name FROM DIM_Layouts ORDER BY layout_name", connection).to_dict('records')
            agencies = pd.read_sql("SELECT agency_id, agency_name FROM DIM_Agencies ORDER BY agency_name", connection).to_dict('records')
            primary_schools = pd.read_sql("SELECT primary_school_id, primary_school_name FROM DIM_Primary_Schools ORDER BY primary_school_name", connection).to_dict('records')
            secondary_schools = pd.read_sql("SELECT secondary_school_id, secondary_school_name FROM DIM_Secondary_Schools ORDER BY secondary_school_name", connection).to_dict('records')
            years = pd.read_sql("SELECT DISTINCT YEAR(date_sold) as year FROM FACT_Properties ORDER BY year DESC", connection)['year'].tolist()
        return {
            'suburbs': suburbs, 'layouts': layouts, 'agencies': agencies,
            'primary_schools': primary_schools, 'secondary_schools': secondary_schools,
            'available_years': years
        }
    except Exception as e:
        logging.error(f"Failed to fetch dimension data: {e}")
        return {key: [] for key in ['suburbs', 'layouts', 'agencies', 'primary_schools', 'secondary_schools', 'available_years']}

# --- 4. Application Routes ---

@app.route('/')
def index():
    """The main landing page, redirects to the explore page."""
    return redirect(url_for('explore'))

@app.route('/add', methods=['GET', 'POST'])
def add_new_record():
  
    # --- Handle POST Request (MODIFIED FOR MOCKING) ---
    if request.method == 'POST':
        try:
            # 1. Get all the data from the submitted form.
            new_record_data = {
                'listing_id': request.form.get('listing_id', type=int),
                'price': request.form.get('price', type=float),
                'address': request.form.get('address'),
                'property_type': request.form.get('property_type'),
                'date_sold': request.form.get('date_sold'),
                # We also get the text of the selected options for display purposes
                'suburb_name': request.form.get('suburb_name_text'),
                'layout_name': request.form.get('layout_name_text')
            }
            logging.info(f"Received new record data (mock mode): {new_record_data}")


            # Instead of creating and executing a SQL INSERT statement...
            #  append the new record dictionary to our global list.
            fake_database_records.append(new_record_data)
            
            
            flash('Success! New record has been simulated and added to the temporary list.', 'success')
            return redirect(url_for('add_new_record')) # Redirect to clear the form
        except Exception as e:
            flash(f'Error adding record: {e}', 'danger')
    
    # For GET request, fetch dimensions and render the add_record page
    dim_data = get_dimension_data()
    dim_data['google_maps_api_key'] = os.getenv("GOOGLE_MAPS_API_KEY")
    
    # pass the list of fake records to the template
    # display what has been "added" so far.
    dim_data['records'] = fake_database_records
    
    return render_template('add_record.html', **dim_data)


@app.route('/explore', methods=['GET', 'POST'])
def explore():
    """Handles displaying filters and showing query results."""
    dim_data = get_dimension_data() # Get data for dropdowns
    results = []
    selected_filters = {}

    if request.method == 'POST':
        try:
            # Get selected filters from the form
            year = request.form.get('year_select')
            suburb_id = request.form.get('suburb_select')
            layout_id = request.form.get('layout_select')
            
            # Store selected filters to re-populate the form
            selected_filters = {'year': int(year) if year else None, 
                                'suburb_id': int(suburb_id) if suburb_id else None,
                                'layout_id': int(layout_id) if layout_id else None}

            # Build the query dynamically
            base_query = """
                SELECT p.price, p.date_sold, s.suburb_name, l.layout_name, p.land_size
                FROM FACT_Properties p
                JOIN DIM_Suburbs s ON p.suburb_id = s.suburb_id
                JOIN DIM_Layouts l ON p.layout_id = l.layout_id
            """
            conditions = []
            params = {}

            if year:
                conditions.append("YEAR(p.date_sold) = :year")
                params['year'] = year
            if suburb_id:
                conditions.append("p.suburb_id = :suburb_id")
                params['suburb_id'] = suburb_id
            if layout_id:
                conditions.append("p.layout_id = :layout_id")
                params['layout_id'] = layout_id

            if conditions:
                base_query += " WHERE " + " AND ".join(conditions)
            
            base_query += " ORDER BY p.price DESC LIMIT 100;" # Limit results for performance

            with engine.connect() as connection:
                results_df = pd.read_sql(text(base_query), connection, params=params)
                results = results_df.to_dict('records')

        except Exception as e:
            flash(f"Error running query: {e}", 'danger')

    return render_template('explore.html', 
                           available_years=dim_data['available_years'], 
                           available_suburbs=dim_data['suburbs'],
                           available_layouts=dim_data['layouts'],
                           results=results,
                           selected_filters=selected_filters)

# --- 5. Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=5001) # Use a different port like 5001 to avoid conflicts