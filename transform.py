import duckdb
import os

if not os.path.exists("website_sessions_bronze.parquet"):
    raise FileNotFoundError("Bronze file 'website_sessions_bronze.parquet' not found.")

website_sessions = duckdb.read_parquet("website_sessions_bronze.parquet")
# Preview una
preview = duckdb.sql("""
    SELECT DISTINCT
        TRIM(session_id) AS session_id,
        UPPER(TRIM(device_type)) AS device_type,
        CAST(session_date AS DATE) AS session_date
    FROM website_sessions
    WHERE session_id IS NOT NULL
        AND TRIM(session_id) != ''
    LIMIT 10
""")

print("\nPREVIEW:")
print(preview)

# Save sa silver
duckdb.sql("""
    COPY (
        SELECT DISTINCT
            TRIM(session_id) AS session_id,

            CAST(session_date AS DATE) AS session_date,

            -- Merge sa year ug month para sayon i-group
            CONCAT(
                CAST(YEAR(CAST(session_date AS DATE)) AS VARCHAR),
                '-',
                LPAD(CAST(MONTH(CAST(session_date AS DATE)) AS VARCHAR), 2, '0')
            ) AS year_month,

            COALESCE(NULLIF(UPPER(TRIM(device_type)), ''), 'UNKNOWN') AS device_type,

            -- Himoang text label ang true/false
            CASE
                WHEN session_purchase_made THEN 'Purchased'
                ELSE 'No Purchase'
            END AS purchase_status,

            COALESCE(session_pages_visited, 0) AS pages_visited,

            -- Fill ug 0 ang missing, round sa 2 decimals
            ROUND(COALESCE(session_quality_score, 0), 2) AS quality_score,

            -- Bag-ong column: category base sa score
            CASE
                WHEN COALESCE(session_quality_score, 0) >= 0.5 THEN 'High'
                WHEN COALESCE(session_quality_score, 0) >= 0.25 THEN 'Medium'
                ELSE 'Low'
            END AS quality_tier

        FROM website_sessions

        WHERE session_id IS NOT NULL
            AND TRIM(session_id) != ''
            AND COALESCE(session_pages_visited, 0) >= 0
    )
    TO 'silver_sessions.parquet'
    (FORMAT PARQUET, COMPRESSION ZSTD)
""")

print("\nTransformation completed. Saved to 'silver_sessions.parquet'.")
duckdb.sql("SELECT * FROM 'silver_sessions.parquet' LIMIT 5").show()