-- =================================================================================
-- SQL Script for Creating the Perth Property Database Schema 
--
-- Design:      Star Schema with decoupled dimensions for Layouts and Schools.
-- Convention:  Use DIM_ for dimension tables and FACT_ for the central fact table.
-- Idempotent:  This script can be re-run safely. It drops old tables before creating new ones.
-- =================================================================================


-- Drop tables in reverse order of dependency to avoid foreign key constraint errors.
-- FACT_Properties depends on all DIM tables, so it must be dropped first.
DROP TABLE IF EXISTS FACT_Properties;
DROP TABLE IF EXISTS DIM_Layouts;
DROP TABLE IF EXISTS DIM_Suburbs;
DROP TABLE IF EXISTS DIM_Agencies;
DROP TABLE IF EXISTS DIM_Primary_Schools;
DROP TABLE IF EXISTS DIM_Secondary_Schools;


-- Dimension Table for property layouts (Bedrooms & Bathrooms combination)
CREATE TABLE DIM_Layouts (
    layout_id INTEGER PRIMARY KEY AUTO_INCREMENT, -- Use SERIAL for PostgreSQL
    bedrooms INTEGER NOT NULL,
    bathrooms INTEGER NOT NULL,
    layout_name VARCHAR(10) NOT NULL,
    UNIQUE(bedrooms, bathrooms) -- This constraint ensures each layout combo is stored only once.
);

-- Dimension Table for Suburbs
CREATE TABLE DIM_Suburbs (
    suburb_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    suburb_name VARCHAR(255) UNIQUE NOT NULL,
    postcode INTEGER
);

-- Dimension Table for Real Estate Agencies
CREATE TABLE DIM_Agencies (
    agency_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    agency_name VARCHAR(255) UNIQUE NOT NULL
);

-- Dimension Table for Primary Schools
CREATE TABLE DIM_Primary_Schools (
    primary_school_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    primary_school_name VARCHAR(255) UNIQUE NOT NULL,
    primary_school_icsea INTEGER
);

-- Dimension Table for Secondary Schools
CREATE TABLE DIM_Secondary_Schools (
    secondary_school_id INTEGER PRIMARY KEY AUTO_INCREMENT,
    secondary_school_name VARCHAR(255) UNIQUE NOT NULL,
    secondary_school_icsea INTEGER
);

-- The main Fact Table for all property listings and their core metrics.
CREATE TABLE FACT_Properties (
    listing_id BIGINT PRIMARY KEY,
    price DECIMAL(12, 2) NOT NULL,
    address VARCHAR(255),
    longitude DECIMAL(11, 8),
    latitude DECIMAL(10, 8),
    property_type VARCHAR(50),
    parking_spaces INTEGER,
    date_sold DATE,
    land_size INTEGER,
    distance_to_cbd INTEGER,
    
    -- Relationship attributes (distances) correctly remain in the fact table.
    primary_school_distance INTEGER,
    secondary_school_distance INTEGER,
    
    -- Foreign Keys that link to all dimension tables.
    suburb_id INTEGER,
    agency_id INTEGER,
    layout_id INTEGER,
    primary_school_id INTEGER,
    secondary_school_id INTEGER,
    
    -- Defining the relationships
    FOREIGN KEY (suburb_id) REFERENCES DIM_Suburbs(suburb_id),
    FOREIGN KEY (agency_id) REFERENCES DIM_Agencies(agency_id),
    FOREIGN KEY (layout_id) REFERENCES DIM_Layouts(layout_id),
    FOREIGN KEY (primary_school_id) REFERENCES DIM_Primary_Schools(primary_school_id),
    FOREIGN KEY (secondary_school_id) REFERENCES DIM_Secondary_Schools(secondary_school_id)
);