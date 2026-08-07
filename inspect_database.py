#!/usr/bin/env python3

import sqlite3
import os

# Connect to the database
DB_PATH = "/Users/ayushparoha/Documents/Lumina-Rare-Disease-Triage/data/lumina_app.sqlite"

if not os.path.exists(DB_PATH):
    print(f"Database not found at {DB_PATH}")
    exit(1)

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all tables
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("Tables in database:")
for table in tables:
    print(f"  - {table[0]}")

# Get schema for each table
for table_name, in tables:
    print(f"\nSchema for {table_name}:")
    schema = cursor.execute(f"PRAGMA table_info({table_name});").fetchall()
    for column in schema:
        print(f"  - {column[1]} ({column[2]}), {column[4]}")

# Count rows in each table
for table_name, in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()[0]
    print(f"{table_name}: {count} rows")

# Close connection
conn.close()