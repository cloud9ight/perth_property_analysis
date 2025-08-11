# scripts/geocode_schools.py (Using Google Places API)

import pandas as pd
from sqlalchemy import create_engine, text
import requests
import time
import os
from dotenv import load_dotenv

def geocode_and_update(engine, table_name, id_col, name_col, api_key):
    """
    Fetches schools without coordinates, uses the Google Places API "Find Place"
    endpoint for accurate entity searching, and updates the DB.
    """
    print(f"\n--- Processing table: {table_name} ---")
    
    try:
        query = f"SELECT {id_col}, {name_col} FROM {table_name} WHERE latitude IS NULL OR longitude IS NULL"
        df_schools = pd.read_sql(text(query), engine)

        if df_schools.empty:
            print("All schools in this table are already geocoded.")
            return

        print(f"Found {len(df_schools)} new school(s) to find places for.")
        
        with engine.connect() as connection:
            for index, row in df_schools.iterrows():
                school_id = row[id_col]
                school_name = row[name_col]
                
                endpoint = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
                params = {
                    'input': f"{school_name}, Western Australia",
                    'inputtype': 'textquery',
                    'fields': 'geometry',
                    'key': api_key
                }
                
                try:
                    response = requests.get(endpoint, params=params)
                    response.raise_for_status()
                    data = response.json()

                    if data.get('status') == 'OK' and data.get('candidates'):
                        location = data['candidates'][0]['geometry']['location']
                        lat, lng = location['lat'], location['lng']
                        
                        update_query = text(f"UPDATE {table_name} SET latitude = :lat, longitude = :lng WHERE {id_col} = :id")
                        with connection.begin():
                            connection.execute(update_query, {'lat': lat, 'lng': lng, 'id': school_id})
                        print(f"  - SUCCESS: Found place for '{school_name}' -> ({lat}, {lng})")
                    else:
                        print(f"  - WARNING: Could not find a place for: '{school_name}'. Status: {data.get('status')}")
                
                except requests.exceptions.RequestException as e:
                    print(f"  - ERROR: API request failed for {school_name}: {e}")
                
                time.sleep(0.05)

    except Exception as e:
        print(f"An error occurred while processing {table_name}: {e}")

def main():
    """
    Main function to configure, connect, and run the entire geocoding process.
    """
    # --- 1. Load Configuration from .env file ---
    load_dotenv()
    print("Loading configuration...")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASS = os.getenv("DB_PASS")
    API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    DB_HOST = 'localhost'
    DB_PORT = '3306'
    DB_NAME = 'perth_property_db'

    if not DB_PASS or not API_KEY:
        raise ValueError("Critical: DB_PASS or GOOGLE_MAPS_API_KEY not found in .env file.")

    # --- 2. Create Database Connection Engine ---
    try:
        db_connection_str = f'mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
        engine = create_engine(db_connection_str)
        print("Successfully connected to the database.")
    except Exception as e:
        print(f"FATAL: Database connection failed: {e}")
        return # Exit the function if we can't connect

    # --- 3. Run the Geocoding Process for both school tables ---
    geocode_and_update(engine, 'DIM_Primary_Schools', 'primary_school_id', 'primary_school_name', API_KEY)
    geocode_and_update(engine, 'DIM_Secondary_Schools', 'secondary_school_id', 'secondary_school_name', API_KEY)

    print("\nGeocoding process complete.")

# --- Standard Python entry point to run the main function ---
if __name__ == "__main__":
    main()