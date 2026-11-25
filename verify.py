import duckdb

duckdb.sql("""
    SELECT COUNT(*) AS rows,
           COUNT(DISTINCT session_id) AS unique_ids,
           SUM(CASE WHEN session_quality_score IS NULL THEN 1 ELSE 0 END) AS nulls
    FROM 'website_sessions_clean.parquet'
""").show()

duckdb.sql("SELECT * FROM 'website_sessions_clean.parquet' LIMIT 5").show()