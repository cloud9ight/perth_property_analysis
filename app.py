# app.py - Final version with both /add and /explore routes

# --- 1. Imports and Setup ---
from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy import create_engine, text
import pandas as pd
import logging
import os
from dotenv import load_dotenv
import hashlib 
import random

#load_dotenv()

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
            property_types = pd.read_sql("SELECT DISTINCT property_type FROM FACT_Properties WHERE property_type IS NOT NULL ORDER BY property_type", connection)['property_type'].tolist()
            agencies = pd.read_sql("SELECT agency_id, agency_name FROM DIM_Agencies ORDER BY agency_name", connection).to_dict('records')
            primary_schools = pd.read_sql("SELECT primary_school_id, primary_school_name FROM DIM_Primary_Schools ORDER BY primary_school_name", connection).to_dict('records')
            secondary_schools = pd.read_sql("SELECT secondary_school_id, secondary_school_name FROM DIM_Secondary_Schools ORDER BY secondary_school_name", connection).to_dict('records')
            years = pd.read_sql("SELECT DISTINCT YEAR(date_sold) as year FROM FACT_Properties ORDER BY year DESC", connection)['year'].tolist()
            postcodes = pd.read_sql("SELECT DISTINCT postcode FROM DIM_Suburbs ORDER BY postcode", connection)['postcode'].tolist()
        return {
            'suburbs': suburbs, 'layouts': layouts, 'agencies': agencies,
            'primary_schools': primary_schools, 'secondary_schools': secondary_schools,
            'available_years': years,
            'postcodes': postcodes,
            'property_types': property_types
        }
    except Exception as e:
        logging.error(f"Failed to fetch dimension data: {e}")
        return {key: [] for key in ['suburbs', 'layouts', 'agencies', 'primary_schools', 'secondary_schools', 'available_years', 'postcodes', 'property_types']}
    
    
# COLOR_PALETTE = [
#     '#3498db', '#2ecc71', '#e74c3c', '#9b59b6', '#f1c40f', 
#     '#1abc9c', '#e67e22', '#34495e', '#16a085', '#c0392b'
# ]
# def get_color_for_string(text):
#     """
#     Generates a unique, visually pleasing HSL color based on the hash of a string.
#     By keeping Saturation and Lightness constant, we ensure all colors feel like
#     they belong to the same palette.
#     """
#     # 1. Hash the string to get a consistent, large number.
#     hash_value = int(hashlib.md5(text.encode('utf-8')).hexdigest(), 16)
    
#     # 2. Use modulo to map the hash to a degree on the 360-degree color wheel (Hue).
#     hue = hash_value % 360
    
#     # 3. Define a fixed, professional-looking Saturation and Lightness.
#     saturation = 65  # in percent
#     lightness = 45   # in percent
    
#     # 4. Return the HSL color string.
#     return f"hsl({hue}, {saturation}%, {lightness}%)"

color_cache = {}
# A random starting point for our hue, so the colors are different on each page load.
random.seed()
HUE_START = random.random()
GOLDEN_RATIO_CONJUGATE = 0.61803398875

def get_color_for_string(text, index):
    """
    Generates a unique, visually pleasing, and well-distributed HSL color
    for each string using the golden ratio.
    """
    global HUE_START
    # Use the golden ratio to advance the hue, ensuring good distribution.
    hue = (HUE_START + index * GOLDEN_RATIO_CONJUGATE) % 1.0
    
    # Convert hue from 0-1 range to 0-360 range for HSL.
    hue_degrees = hue * 360
    
    saturation = 65
    lightness = 45
    
    return f"hsl({hue_degrees:.0f}, {saturation}%, {lightness}%)"

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
            listing_id_str = request.form.get('listing_id', '').strip()
            if not listing_id_str.isdigit() or len(listing_id_str) < 9:
                # If validation fails, flash an error message
                flash('Validation Error: Listing ID must be at least 9 digits long.', 'danger')
                # It's important to redirect back to the form
                return redirect(url_for('add_new_record'))

            
            listing_id = int(listing_id_str)
            # with engine.connect() as connection:
            #     result = connection.execute(text("SELECT 1 FROM FACT_Properties WHERE listing_id = :id"), {'id': listing_id}).first()
            #     if result:
            #         flash(f'Validation Error: Listing ID {listing_id} already exists in the database.', 'danger')
            #         return redirect(url_for('add_new_record'))

            # mock mode, only check fake_db
            if any(record['listing_id'] == listing_id for record in fake_database_records):
                 flash(f'Validation Error: Listing ID {listing_id} has already been added in this session.', 'danger')
                 return redirect(url_for('add_new_record'))     
                    
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
    """Handles displaying filters and showing query results from real db."""
    dim_data = get_dimension_data() # Get data for dropdowns
    results_list = []
    stats_summary = None
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
            logging.info(f"User submitted filters: {selected_filters}")
            
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

            where_clause = ""
            if conditions:
                where_clause += " WHERE " + " AND ".join(conditions)
          
            # Build the query dynamically
            query_list = f"""
                SELECT 
                    p.price AS "Price",
                    DATE_FORMAT(p.date_sold, '%Y-%m-%d') AS "Date Sold",
                    s.suburb_name AS "Suburb",
                    l.layout_name AS "Layout",
                    p.land_size AS "Land Size (sqm)",
                    p.address AS "Address"
                FROM FACT_Properties p
                JOIN DIM_Suburbs s ON p.suburb_id = s.suburb_id
                JOIN DIM_Layouts l ON p.layout_id = l.layout_id
                {where_clause}
                ORDER BY p.price DESC LIMIT 100;
           
            """
            # --- 4. Execute Query 2: Get the statistical summary ---
            # This query finds the min, max, avg, and median prices.
            # We also find the specific properties that correspond to the min and max prices.
            query_stats = f"""
                WITH FilteredProperties AS (
                    SELECT p.price, p.address, p.date_sold, p.land_size
                    FROM FACT_Properties p
                    {where_clause}
                ),
                RankedProperties AS (
                    SELECT 
                        price,
                        ROW_NUMBER() OVER (ORDER BY price ASC) as row_num,
                        (SELECT COUNT(*) FROM FilteredProperties) as total_count
                    FROM FilteredProperties
                )
                SELECT

                    (SELECT price FROM FilteredProperties ORDER BY price ASC LIMIT 1) as min_price,
                    (SELECT address FROM FilteredProperties ORDER BY price ASC LIMIT 1) as min_price_address,
                    (SELECT date_sold FROM FilteredProperties ORDER BY price ASC LIMIT 1) as min_price_date,
                    (SELECT land_size FROM FilteredProperties ORDER BY price ASC LIMIT 1) as min_price_land_size,
                    
                    (SELECT price FROM FilteredProperties ORDER BY price DESC LIMIT 1) as max_price,
                    (SELECT address FROM FilteredProperties ORDER BY price DESC LIMIT 1) as max_price_address,
                    (SELECT date_sold FROM FilteredProperties ORDER BY price DESC LIMIT 1) as max_price_date,
                    (SELECT land_size FROM FilteredProperties ORDER BY price DESC LIMIT 1) as max_price_land_size,

                    AVG(price) as avg_price,
                    COUNT(*) as total_sales,

                    -- Median Calculation using Window Functions
                    (SELECT AVG(price) FROM RankedProperties 
                     WHERE row_num IN (FLOOR((total_count + 1) / 2), CEIL((total_count + 1) / 2))) as median_price
                
                FROM FilteredProperties;
            """
            
            

            with engine.connect() as connection:
                # Execute list query
                results_df = pd.read_sql(text(query_list), connection, params=params)
                if not results_df.empty:
                    results_list = results_df.to_dict('records')
                    
                # Execute stats query
                stats_df = pd.read_sql(text(query_stats), connection, params=params)
                # If we get a result, convert the single row DataFrame to a dictionary
                if not stats_df.empty and stats_df.iloc[0]['total_sales'] > 0:
                    stats_summary = stats_df.iloc[0].to_dict()
                else:
                    # If no properties match, we can't show stats.
                    results_list = [] # Also clear the list if no stats are found.

        except Exception as e:
            flash(f"Error running query: {e}", 'danger')
            logging.error(f"Failed during explore POST request: {e}")

    return render_template('explore.html', 
                           available_years=dim_data['available_years'], 
                           available_suburbs=dim_data['suburbs'],
                           available_layouts=dim_data['layouts'],
                           results_list=results_list,
                           stats_summary=stats_summary,
                           selected_filters=selected_filters)
    
@app.route('/compare', methods=['GET', 'POST'])
def compare():
    """
    Handles multi-dimensional comparison. 
    Fetches stats for each selected suburb for each selected year in a single query.
    """
    dim_data = get_dimension_data()

    stats_results = []
    selected_filters = {'years': [], 'suburb_ids': [], 'layout_ids': []}
    selected_filter_labels = {}
    # NEW: A dictionary to map suburb names to their colors
    suburb_color_map = {} 

    if request.method == 'POST':
        try:
            years = request.form.getlist('year_select', type=int)
            suburb_ids = request.form.getlist('suburb_select', type=int)
            layout_ids = request.form.getlist('layout_select', type=int)
            
            selected_filters = {'years': years, 'suburb_ids': suburb_ids, 'layout_ids': layout_ids}
            
            # --- Convert selected IDs to labels for display (no changes here) ---
            if years: selected_filter_labels['Years'] = sorted(years)
            if suburb_ids:
                suburb_map = {item['suburb_id']: item['suburb_name'] for item in dim_data['suburbs']}
                selected_suburbs = sorted([suburb_map.get(sid) for sid in suburb_ids if sid in suburb_map])
                selected_filter_labels['Suburbs'] = selected_suburbs
                suburb_color_map = {}
                for i, name in enumerate(selected_suburbs):
                    suburb_color_map[name] = get_color_for_string(name, i)
                    
            if layout_ids:
                layout_map = {item['layout_id']: item['layout_name'] for item in dim_data['layouts']}
                selected_filter_labels['Layouts'] = sorted([layout_map.get(lid) for lid in layout_ids if lid in layout_map])

            # --- Validation ---
            if not suburb_ids and not years and not layout_ids:
                flash("Please select at least one filter.", 'danger')
            else:
                # --- Dynamically build SELECT, WHERE, and GROUP BY clauses ---
                select_columns = ["s.suburb_name", "COUNT(*) AS total_sales", "AVG(p.price) AS avg_price"]
                group_by_columns = ["s.suburb_name"]
                conditions = []
                params = {}
                # Add filters and update SELECT/GROUP BY clauses dynamically
                if suburb_ids:
                    conditions.append("p.suburb_id IN :suburb_ids")
                    params['suburb_ids'] = tuple(suburb_ids)
                
                if years:
                    conditions.append("YEAR(p.date_sold) IN :years")
                    params['years'] = tuple(years)
                    select_columns.insert(1, "YEAR(p.date_sold) AS sale_year") # Add to SELECT
                    group_by_columns.append("sale_year") # Add to GROUP BY
                
                if layout_ids:
                    conditions.append("p.layout_id IN :layout_ids")
                    params['layout_ids'] = tuple(layout_ids)
                    select_columns.insert(1, "l.layout_name") # Add to SELECT
                    group_by_columns.append("l.layout_name") # Add to GROUP BY
                
                where_clause = "WHERE " + " AND ".join(conditions)
                select_clause = ", ".join(select_columns)
                group_by_clause = "GROUP BY " + ", ".join(group_by_columns)
                order_by_clause = "ORDER BY " + ", ".join(group_by_columns)
                
                # The final, powerful query with GROUP BY on both suburb and year
                query_final = f"""
                    SELECT {select_clause}
                    FROM FACT_Properties p
                    JOIN DIM_Suburbs s ON p.suburb_id = s.suburb_id
                    JOIN DIM_Layouts l ON p.layout_id = l.layout_id
                    {where_clause}
                    {group_by_clause}
                    {order_by_clause};
                """
                logging.info(f"Executing Dynamic Query: {query_final} with Params: {params}")
                with engine.connect() as connection:
                    results_df = pd.read_sql(text(query_final), connection, params=params)
                    if not results_df.empty:
                        stats_results = results_df.to_dict('records')
                        # NEW: Add the color to each result dictionary
                        for result in stats_results:
                            result['color'] = suburb_color_map.get(result['suburb_name'], '#bdc3c7') # Default grey

        except Exception as e:
            flash(f"Error running comparison query: {e}", 'danger')
            logging.error(f"Failed during compare POST request: {e}")

    return render_template('compare.html', 
                           available_years=dim_data['available_years'],
                           available_suburbs=dim_data['suburbs'],
                           available_layouts=dim_data['layouts'],
                           stats_results=stats_results, # Pass the new, more granular results
                           selected_filters=selected_filters,
                           selected_filter_labels=selected_filter_labels,
                           suburb_color_map=suburb_color_map)

@app.route('/trend', methods=['GET', 'POST'])
def trend():
    """
    Handles trend analysis, allowing users to filter by EITHER Suburb OR Postcode.
    """
    dim_data = get_dimension_data()
    chart_data = None
    chart_title = "Price Trend"
    # Initialize all possible filter keys
    selected_filters = {'filter_by': 'suburb'} # Default selection

    if request.method == 'POST':
        try:
            # --- 1. Get filter choices, including the new filter_by mode ---
            filter_by = request.form.get('filter_by') # This will be 'suburb' or 'postcode'
            suburb_id = request.form.get('suburb_id')
            postcode = request.form.get('postcode')
            property_type = request.form.get('property_type')
            layout_id = request.form.get('layout_id')
            start_date = request.form.get('start_date')
            end_date = request.form.get('end_date')
            
            selected_filters = {
                'filter_by': filter_by,
                'suburb_id': int(suburb_id) if suburb_id else None,
                'postcode': int(postcode) if postcode else None,
                'property_type': property_type,
                'layout_id': int(layout_id) if layout_id else None,
                'start_date': start_date,
                'end_date': end_date
            }
            
            # --- 2. Build the dynamic query based on the selected mode ---
            query = """
                SELECT DATE_FORMAT(p.date_sold, '%Y-%m') AS date_month, AVG(p.price) AS average_price
                FROM FACT_Properties p
                JOIN DIM_Suburbs s ON p.suburb_id = s.suburb_id
            """
            conditions = ["1=1"] # Start with a true condition
            params = {}
            title_parts = []

            # Determine the main geographic filter
            if filter_by == 'suburb' and suburb_id:
                conditions.append("p.suburb_id = :suburb_id")
                params['suburb_id'] = suburb_id
                suburb_map = {item['suburb_id']: item['suburb_name'] for item in dim_data['suburbs']}
                title_parts.append(suburb_map.get(int(suburb_id), "").title())
            elif filter_by == 'postcode' and postcode:
                conditions.append("s.postcode = :postcode")
                params['postcode'] = postcode
                title_parts.append(f"Postcode {postcode}")
                
            if property_type:
                conditions.append("p.property_type = :property_type")
                params['property_type'] = property_type
                title_parts.append(property_type.title())
            
            # Add other optional filters
            if layout_id:
                conditions.append("p.layout_id = :layout_id")
                params['layout_id'] = layout_id
                layout_map = {item['layout_id']: item['layout_name'] for item in dim_data['layouts']}
                title_parts.append(layout_map.get(int(layout_id), ""))
            if start_date:
                conditions.append("p.date_sold >= :start_date"); params['start_date'] = start_date
            if end_date:
                conditions.append("p.date_sold <= :end_date"); params['end_date'] = end_date
            
            query += " WHERE " + " AND ".join(conditions)
            query += " GROUP BY date_month ORDER BY date_month ASC;"

            # --- 3. Execute and prepare data (no changes here) ---
            with engine.connect() as connection:
                trend_df = pd.read_sql(text(query), connection, params=params)
                if not trend_df.empty:
                    chart_data = {
                        'labels': trend_df['date_month'].tolist(),
                        'values': trend_df['average_price'].tolist()
                    }
                    chart_title = "Price Trend for " + " & ".join(filter(None, title_parts)) if title_parts else "Overall Market Trend"
                else:
                    flash("No data found for the selected criteria.", "warning")

        except Exception as e:
            flash(f"Error running query: {e}", 'danger')

    return render_template('trend.html', 
                           suburbs=dim_data['suburbs'], 
                           layouts=dim_data['layouts'],
                           postcodes=dim_data['postcodes'], # Pass postcodes to the template
                           property_types=dim_data['property_types'],
                           chart_data=chart_data,
                           chart_title=chart_title,
                           selected_filters=selected_filters)

@app.route('/map')
def show_map():
    """
    Displays properties on an interactive map.
    It can receive a list of listing_ids to display, or show a default view.
    """
    # Get the list of listing IDs from the URL query parameter, if it exists
    listing_ids_str = request.args.get('ids', '')
    
    properties_for_map = []
    
    # Base query to fetch data needed for the map
    query = """
        SELECT listing_id, price, address, latitude, longitude, s.suburb_name
        FROM FACT_Properties p
        JOIN DIM_Suburbs s ON p.suburb_id = s.suburb_id
    """
    params = {}

    if listing_ids_str:
        # If IDs are provided, convert them to a list of integers
        try:
            listing_ids = [int(id_str) for id_str in listing_ids_str.split(',')]
            query += " WHERE p.listing_id IN :listing_ids"
            params['listing_ids'] = tuple(listing_ids)
        except ValueError:
            flash("Invalid listing IDs provided for the map.", "danger")
            # Fall back to the default view if IDs are invalid
    else:
        # Default view: Show a random sample of 500 properties if no IDs are given
        query += " ORDER BY RAND() LIMIT 500"

    try:
        with engine.connect() as connection:
            map_df = pd.read_sql(text(query), connection, params=params)
            if not map_df.empty:
                properties_for_map = map_df.to_dict('records')
    except Exception as e:
        flash(f"Error fetching map data: {e}", "danger")
        logging.error(f"Failed to fetch map data: {e}")

    # Pass the list of property data to the template
    return render_template('map.html', properties_for_map=properties_for_map)


# --- 5. Run the App ---
if __name__ == '__main__':
    app.run(debug=True, port=5001) 