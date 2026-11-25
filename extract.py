import duckdb
import os

SOURCE_FILE = "website_sessions.csv"
OUTPUT_FILE = "website_sessions_bronze.parquet"

duckdb.sql(f"""
    COPY (
        SELECT *
        FROM read_csv_auto('{SOURCE_FILE}')
    )
    TO '{OUTPUT_FILE}' (FORMAT PARQUET);
""")

print(f"Done: {OUTPUT_FILE} ({os.path.getsize(OUTPUT_FILE)} bytes)")
