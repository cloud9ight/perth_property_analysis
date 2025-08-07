-- Query 1: Basic Validation - Row Counts
SELECT 'DIM_Suburbs' AS table_name, COUNT(*) AS number_of_rows FROM DIM_Suburbs
UNION ALL
SELECT 'DIM_Agencies', COUNT(*) FROM DIM_Agencies
UNION ALL
SELECT 'DIM_Layouts', COUNT(*) FROM DIM_Layouts
UNION ALL
SELECT 'DIM_Primary_Schools', COUNT(*) FROM DIM_Primary_Schools
UNION ALL
SELECT 'DIM_Secondary_Schools', COUNT(*) FROM DIM_Secondary_Schools
UNION ALL
SELECT 'FACT_Properties', COUNT(*) FROM FACT_Properties;

-- Query 2: Top 10 Most Expensive Properties with Full Details
SELECT
    p.price AS property_price,
    p.address,
    s.suburb_name,
    l.layout_name,
    a.agency_name
FROM
    FACT_Properties p
JOIN
    DIM_Suburbs s ON p.suburb_id = s.suburb_id
JOIN
    DIM_Layouts l ON p.layout_id = l.layout_id
JOIN
    DIM_Agencies a ON p.agency_id = a.agency_id
ORDER BY
    property_price DESC
LIMIT 10;

-- Query 3: 
WITH
-- CTE 1: Calculate average price for each suburb specifically for the year 2020
stats_2020 AS (
    SELECT
        s.suburb_id,
        s.suburb_name,
        AVG(p.price) AS avg_price_2020,
        COUNT(p.listing_id) AS sales_2020
    FROM
        FACT_Properties p
    JOIN
        DIM_Suburbs s ON p.suburb_id = s.suburb_id
    WHERE
        YEAR(p.date_sold) = 2020
    GROUP BY
        s.suburb_id, s.suburb_name
),

-- CTE 2: Calculate average price for each suburb specifically for the year 2024
stats_2024 AS (
    SELECT
        s.suburb_id,
        AVG(p.price) AS avg_price_2024,
        COUNT(p.listing_id) AS sales_2024
    FROM
        FACT_Properties p
    JOIN
        DIM_Suburbs s ON p.suburb_id = s.suburb_id
    WHERE
        YEAR(p.date_sold) = 2024
    GROUP BY
        s.suburb_id
)

-- Final Query: Join the 2020 and 2024 stats to calculate growth
SELECT
    s20.suburb_name,
    CAST(s20.avg_price_2020 AS UNSIGNED) AS price_in_2020,
    CAST(s24.avg_price_2024 AS UNSIGNED) AS price_in_2024,
    CAST(s24.avg_price_2024 - s20.avg_price_2020 AS SIGNED) AS absolute_growth_aud,
    -- The key metric: percentage growth, formatted to 2 decimal places
    CAST(((s24.avg_price_2024 / s20.avg_price_2020) - 1) * 100 AS DECIMAL(10, 2)) AS percentage_growth
FROM
    stats_2020 s20
JOIN
    stats_2024 s24 ON s20.suburb_id = s24.suburb_id
-- Data Quality Filter: Only include suburbs with at least 5 sales in both years for reliability
WHERE
    s20.sales_2020 >= 5 AND s24.sales_2024 >= 5
-- ORDER BY absolute_growth_aud DESC -- To find the highest dollar increase
ORDER BY
    percentage_growth DESC -- To find the highest growth rate 
LIMIT 15;