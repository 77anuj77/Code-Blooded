-- Supabase Migration Script for Lumina Project
-- Migrating from current PostgreSQL deployment to Supabase

-- ========================================
-- 1. TABLES CREATION
-- ========================================

-- Create app_patient_submission table
CREATE TABLE IF NOT EXISTS app_patient_submission (
    id TEXT PRIMARY KEY,
    timestamp BIGINT,
    updated_at BIGINT,
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
    release_timestamp BIGINT,
    visit_recommendation TEXT
);

-- Create app_doctor_request_message table
CREATE TABLE IF NOT EXISTS app_doctor_request_message (
    id TEXT PRIMARY KEY,
    submission_id TEXT,
    doctor_id TEXT,
    message TEXT,
    timestamp BIGINT
);

-- Create app_clinical_case table
CREATE TABLE IF NOT EXISTS app_clinical_case (
    id TEXT PRIMARY KEY,
    timestamp BIGINT,
    updated_at BIGINT,
    doctor_owner_id TEXT,
    submission_id TEXT,
    patient_owner_id TEXT,
    case_json TEXT
);

-- ========================================
-- 2. INDICES
-- ========================================

-- Create indices
CREATE INDEX IF NOT EXISTS idx_app_patient_submission_status ON app_patient_submission(status);
CREATE INDEX IF NOT EXISTS idx_app_patient_submission_patient_owner_id ON app_patient_submission(patient_owner_id);
CREATE INDEX IF NOT EXISTS idx_app_patient_submission_doctor_reviewer_id ON app_patient_submission(doctor_reviewer_id);
CREATE INDEX IF NOT EXISTS idx_app_doctor_request_message_submission_id ON app_doctor_request_message(submission_id);
CREATE INDEX IF NOT EXISTS idx_app_clinical_case_submission_id ON app_clinical_case(submission_id);

-- ========================================
-- 3. SAMPLE DATA INSERTION
-- ========================================

-- Insert sample data into app_patient_submission
INSERT INTO app_patient_submission (
    id, timestamp, updated_at, patient_owner_id, doctor_reviewer_id,
    patient_name, age, sex, notes, photo_file_name, photo_path,
    photo_content_type, lab_file_name, lab_path, lab_content_type,
    genetic_evidence_json, status, linked_case_id,
    latest_doctor_message, patient_summary_json, released_letter_markdown,
    release_timestamp, visit_recommendation
) VALUES 
('sub-001', 1678901234, 1678901234, 'owner-123', 'reviewer-456',
 'John Doe', '45', 'M', 'Patient presents with rare symptoms', 'photo1.jpg',
 'photos/submission1/', 'image/jpeg', 'lab1.pdf', 'labs/submission1/',
 'application/pdf', '{"finding1": "value1"}', 'active', 'case-789',
 'Message from doctor', '{"summary": "Patient summary"}', '# Release letter content',
 1678901234, 'referral'), 
('sub-002', 1678901235, 1678901235, 'owner-456', 'reviewer-789',
 'Jane Smith', '38', 'F', 'Patient with mysterious symptoms', 'photo2.jpg',
 'photos/submission2/', 'image/jpeg', 'lab2.pdf', 'labs/submission2/',
 'application/pdf', '{"finding2": "value2"}', 'pending', 'case-890',
 'Second message from doctor', '{"summary": "Another patient summary"}', '# Second release letter', 
 1678901235, 'followup');

-- Insert sample data into app_doctor_request_message
INSERT INTO app_doctor_request_message (id, submission_id, doctor_id, message, timestamp)
VALUES 
('req-001', 'sub-001', 'doctor-1', 'Initial consultation requested', 1678901236),
('req-002', 'sub-001', 'doctor-2', 'Follow-up needed', 1678901236), 
('req-003', 'sub-002', 'doctor-3', 'Routine check-up', 1678901237);

-- Insert sample data into app_clinical_case
INSERT INTO app_clinical_case (id, timestamp, updated_at, doctor_owner_id, submission_id, patient_owner_id, case_json)
VALUES 
('case-001', 1678901238, 1678901238, 'doctor-1', 'sub-001', 'owner-123', '{"diagnosis": "Rare Disease X", "notes": "Case details"}'),
('case-002', 1678901239, 1678901239, 'doctor-2', 'sub-002', 'owner-456', '{"diagnosis": "Autoimmune Condition Y", "notes": "Additional case details"}');

