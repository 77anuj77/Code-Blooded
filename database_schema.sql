-- SQLite database schema for Lumina project
-- Based on SQLModel models found in the project

-- Create the main table: app_patient_submission
CREATE TABLE IF NOT EXISTS app_patient_submission (
    id TEXT PRIMARY KEY,
    timestamp INTEGER,
    updated_at INTEGER,
    patient_owner_id TEXT,
    doctor_reviewer_id TEXT,
    patient_name TEXT,
    age TEXT,
    sex TEXT,
    notes TEXT,
    photo_file_name TEXT,
    photo_path TEXT,
    photo_content_type TEXT,
    lab_file_name TEXT,
    lab_path TEXT,
    lab_content_type TEXT,
    genetic_evidence_json TEXT,
    status TEXT,
    linked_case_id TEXT,
    latest_doctor_message TEXT,
    patient_summary_json TEXT,
    released_letter_markdown TEXT,
    released_case_id TEXT,
    release_timestamp INTEGER,
    visit_recommendation TEXT
);

-- Create other related tables
CREATE TABLE IF NOT EXISTS app_doctor_request_message (
    id TEXT PRIMARY KEY,
    submission_id TEXT,
    doctor_id TEXT,
    message TEXT,
    timestamp INTEGER
);

CREATE TABLE IF NOT EXISTS app_clinical_case (
    id TEXT PRIMARY KEY,
    timestamp INTEGER,
    updated_at INTEGER,
    doctor_owner_id TEXT,
    submission_id TEXT,
    patient_owner_id TEXT,
    case_json TEXT
);

-- Indexes for frequently queried columns
CREATE INDEX IF NOT EXISTS idx_app_patient_submission_status ON app_patient_submission(status);
CREATE INDEX IF NOT EXISTS idx_app_patient_submission_patient_owner_id ON app_patient_submission(patient_owner_id);
CREATE INDEX IF NOT EXISTS idx_app_patient_submission_doctor_reviewer_id ON app_patient_submission(doctor_reviewer_id);
CREATE INDEX IF NOT EXISTS idx_app_doctor_request_message_submission_id ON app_doctor_request_message(submission_id);
CREATE INDEX IF NOT EXISTS idx_app_clinical_case_submission_id ON app_clinical_case(submission_id);