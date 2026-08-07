#!/usr/bin/env python3

import sqlite3
import os
from datetime import datetime

# Connect to the database
DB_PATH = "/Users/ayushparoha/Documents/Lumina-Rare-Disease-Triage/data/lumina_app.sqlite"

if not os.path.exists(DB_PATH):
    print(f"Database not found at {DB_PATH}")
    exit(1)

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Function to generate a UUID-like ID
def generate_id():
    return str(datetime.now().timestamp()) + '-' + os.urandom(4).hex()

# Insert sample data into app_patient_submission
sample_data = [
    (
        generate_id(),  # id
        int(datetime.now().timestamp()),  # timestamp
        int(datetime.now().timestamp()),  # updated_at
        "owner_123",  # patient_owner_id
        "reviewer_456",  # doctor_reviewer_id
        "John Doe",  # patient_name
        "45",  # age
        "M",  # sex
        "Patient presents with rare symptoms",  # notes
        "photo1.jpg",  # photo_file_name
        "photos/submission1/",  # photo_path
        "image/jpeg",  # photo_content_type
        "lab1.pdf",  # lab_file_name
        "labs/submission1/",  # lab_path
        "application/pdf",  # lab_content_type
        '{"finding1": "value1"}',  # genetic_evidence_json
        "active",  # status
        "case_789",  # linked_case_id
        "Message from doctor",  # latest_doctor_message
        '{"summary": "Patient summary"}',  # patient_summary_json
        "# Release letter content",  # released_letter_markdown
        1678901234,  # release_timestamp
        "referral"  # visit_recommendation
    )
]

# Insert sample data
cursor.executemany("""
INSERT INTO app_patient_submission (
    id, timestamp, updated_at, patient_owner_id, doctor_reviewer_id,
    patient_name, age, sex, notes, photo_file_name, photo_path,
    photo_content_type, lab_file_name, lab_path, lab_content_type,
    genetic_evidence_json, status, linked_case_id,
    latest_doctor_message, patient_summary_json, released_letter_markdown,
    release_timestamp, visit_recommendation
) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
""", sample_data)

# Insert sample data into other tables
cursor.execute("""
INSERT INTO app_doctor_request_message (id, submission_id, doctor_id, message, timestamp)
VALUES (?,?,?,?,?),
(?,?,?,?,?)
""", [
    (generate_id(), "sub_123", "doctor_1", "Initial consultation requested", int(datetime.now().timestamp())),
    (generate_id(), "sub_123", "doctor_2", "Follow-up needed", int(datetime.now().timestamp()))
])

cursor.execute("""
INSERT INTO app_clinical_case (id, timestamp, updated_at, doctor_owner_id, submission_id, patient_owner_id, case_json)
VALUES (?,?,?,?,?,?,?)
""", (
    generate_id(),
    int(datetime.now().timestamp()),
    int(datetime.now().timestamp()),
    "owner_123",
    "sub_123",
    "owner_456",
    '{"diagnosis": "Rare Disease X", "notes": "Case details"}'
))

# Commit changes
conn.commit()

# Verify the data was inserted
print("Tables and row counts:")
tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
for table in tables:
    count = cursor.execute(f"SELECT COUNT(*) FROM {table[0]};").fetchone()[0]
    print(f"  - {table[0]}: {count} rows")

# Print some sample data
print("\nSample data from app_patient_submission:")
submissions = cursor.execute("SELECT id, patient_name, status, notes FROM app_patient_submission LIMIT 5;").fetchall()
for row in submissions:
    print(f"  - ID: {row[0]}, Name: {row[1]}, Status: {row[2]}, Notes: {row[3]}")

# Close connection
conn.close()