import os
print("Python is currently looking in this folder:", os.getcwd())
import sqlite3
import pandas as pd

# Connect to SQLite database (It will create the file if it doesn't exist)
conn = sqlite3.connect("app_analytics.db")
cursor = conn.cursor()

print("Creating staging table...")
# Create the raw staging table
cursor.execute("""
CREATE TABLE IF NOT EXISTS staging_app_events (
    timestamp TEXT,
    user_id TEXT,
    session_id TEXT,
    event_name TEXT,
    device_os TEXT
);
""")

print("Ingesting messy CSV into SQLite database...")
# Read the CSV we generated earlier
df = pd.read_csv(r"C:\Users\Admin\Downloads\raw_app_events.csv")

# Append data into the SQLite table
df.to_sql("staging_app_events", conn, if_exists="append", index=False)

# Verify ingestion
cursor.execute("SELECT COUNT(*) FROM staging_app_events;")
row_count = cursor.fetchone()[0]

print(f"Success! Database 'app_analytics.db' created.")
print(f"Verified rows in staging_app_events table: {row_count}")

# Close connection
conn.close()