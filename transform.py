import duckdb

SOURCE_FILE = "website_sessions_bronze.parquet"
OUTPUT_FILE = "website_sessions_clean.parquet"

duckdb.sql(f"""
    COPY (
        WITH dedup AS (
            SELECT DISTINCT * FROM '{SOURCE_FILE}'
        ),
        med AS (
            SELECT median(session_quality_score) AS m FROM dedup
        )
        SELECT
            TRIM(session_id)                AS session_id,
            session_date::DATE              AS session_date,
            customer_id,
            store_id,
            TRIM(device_type)               AS device_type,
            SPLIT_PART(browser_os, '|', 1)  AS browser,
            SPLIT_PART(browser_os, '|', 2)  AS os,
            session_purchase_made,
            session_duration_minutes,
            session_pages_visited,
            COALESCE(session_quality_score, (SELECT m FROM med)) AS session_quality_score,
            session_quality_score IS NULL   AS quality_score_imputed
        FROM dedup
        ORDER BY session_id
    )
    TO '{OUTPUT_FILE}' (FORMAT PARQUET);
""")

print(f"Done: {OUTPUT_FILE}")
