#!/usr/bin/env python3

import os
from pathlib import Path
from sqlmodel import SQLModel, Field, create_engine

# Define the database path (matching what app_db.py uses)
DB_PATH = Path("/Users/ayushparoha/Documents/Lumina-Rare-Disease-Triage/data/lumina_app.sqlite")

# Create the data directory if it doesn't exist
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

# Define the PatientSubmission model based on what we found in app_models.py
class PatientSubmission(SQLModel, table=True):
    __tablename__ = "app_patient_submission"

    id: str = Field(primary_key=True)
    timestamp: int
    updated_at: int
    patient_owner_id: str = Field(index=True)
    doctor_reviewer_id: str | None = Field(default=None, index=True)
    patient_name: str | None = None
    age: str | None = None
    sex: str | None = None
    notes: str | None = None
    photo_file_name: str | None = None
    photo_path: str | None = None
    photo_content_type: str | None = None
    lab_file_name: str | None = None
    lab_path: str | None = None
    lab_content_type: str | None = None
    genetic_evidence_json: str | None = None
    status: str = Field(index=True)
    linked_case_id: str | None = Field(default=None, index=True)
    latest_doctor_message: str | None = None
    patient_summary_json: str | None = None
    released_letter_markdown: str | None = None
    released_case_id: str | None = Field(default=None, index=True)
    release_timestamp: int | None = None
    visit_recommendation: str | None = None

# Define other related models we found
class DoctorRequestMessage(SQLModel, table=True):
    __tablename__ = "app_doctor_request_message"

    id: str = Field(primary_key=True)
    submission_id: str = Field(index=True)
    doctor_id: str
    message: str
    timestamp: int

class ClinicalCase(SQLModel, table=True):
    __tablename__ = "app_clinical_case"

    id: str = Field(primary_key=True)
    timestamp: int
    updated_at: int
    doctor_owner_id: str = Field(index=True)
    submission_id: str | None = Field(default=None, index=True)
    patient_owner_id: str | None = Field(default=None, index=True)
    case_json: str

# Any other models we might have missed
class Submission(SQLModel, table=True):
    __tablename__ = "app_submission"

    id: str = Field(primary_key=True)
    # Add common fields that might exist
    created_at: int
    updated_at: int
    # ... other fields that might be in submissions

def create_database():
    """Create the SQLite database with all required tables"""
    # Create the engine
    engine = create_engine(f"sqlite:///{DB_PATH}")

    # Create all tables
    SQLModel.metadata.create_all(engine)

    print(f"Database created at {DB_PATH}")
    print("Tables created:")

    # List all tables in the database
    with engine.connect() as conn:
        result = conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for row in result:
            print(f"  - {row[0]}")

if __name__ == "__main__":
    create_database()