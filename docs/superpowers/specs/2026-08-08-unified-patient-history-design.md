# Unified Cross-Doctor Patient History — Design

Date: 2026-08-08
Status: Approved (pending spec review)

## Problem

Lumina's data model scopes `ClinicalCase` rows to the doctor who created them
(`doctor_owner_id`). If a patient submits evidence, is reviewed by Doctor A,
and later submits again and is claimed by Doctor B, Doctor B has no
visibility into Doctor A's prior workup — accepted phenotypes, diagnostic
impression, or referral outcome. The patient has to re-explain their entire
history from scratch to every new doctor.

There is currently no patient-level aggregation of history across doctors
anywhere in the codebase (confirmed: no such feature exists in
`apps/api/api/routes/*`, `apps/web/src/lib/*`, or `apps/web/src/app/**`).

## Goals

- Give a doctor reviewing a new submission a fast, doctor-in-the-loop-safe
  summary of the patient's prior doctor-completed diagnoses from *other*
  doctors, without requiring the patient to re-explain anything.
- Gate all cross-doctor visibility behind explicit per-doctor patient
  consent — no doctor sees another doctor's case for a shared patient
  without that patient's approval.
- Keep the summary limited to vetted, doctor-approved conclusions (never
  surface another doctor's in-progress or unreviewed workup).

## Non-goals

- Real ABHA/ABDM integration (separate track — see prior discussion in this
  session). This feature is purely internal to Lumina's own data.
- Patient-initiated sharing controls beyond approve/deny of an incoming
  request (no revocation UI in this pass; can be added later).

## Data model

Two new tables in `apps/api/api/app_models.py`:

```python
class PatientHistoryConsent(SQLModel, table=True):
    __tablename__ = "app_patient_history_consent"

    id: str = Field(primary_key=True)
    patient_owner_id: str = Field(index=True)
    doctor_id: str = Field(index=True)
    status: str = Field(index=True)  # "pending" | "approved" | "denied"
    triggered_by_submission_id: str | None = None
    requested_at: int
    decided_at: int | None = None


class PatientHistorySummary(SQLModel, table=True):
    __tablename__ = "app_patient_history_summary"

    id: str = Field(primary_key=True)
    patient_owner_id: str = Field(index=True, unique=True)
    summary_markdown: str
    source_case_ids_json: str  # sorted list of ClinicalCase ids that fed this summary
    generated_at: int
```

One `PatientHistoryConsent` row per `(patient_owner_id, doctor_id)` pair.
One `PatientHistorySummary` row per patient — a cache invalidated by
comparing `source_case_ids_json` against the current qualifying case set.

## Consent flow

1. `POST /submissions/{id}/start-review` (in
   `apps/api/api/routes/submissions.py`) is extended: when a doctor claims a
   submission, the handler checks whether the patient has any
   `doctor_completed` / `released_to_patient` case owned by a *different*
   doctor. If so, and no `PatientHistoryConsent` row exists yet for
   `(patient_owner_id, this doctor)`, create one with `status="pending"`.
2. New patient-facing endpoints (new file
   `apps/api/api/routes/patient_history.py`):
   - `GET /patients/me/consent-requests` — list the caller's pending
     requests (role must be `patient`).
   - `POST /consent-requests/{id}/approve`
   - `POST /consent-requests/{id}/deny`
   Both mutation endpoints verify `row.patient_owner_id == user_id` and
   `role == "patient"` before acting, and set `decided_at`.
3. New doctor-facing endpoint:
   - `GET /patients/{patient_id}/history` — 403 unless an `approved`
     `PatientHistoryConsent` row exists for `(patient_id, calling doctor)`.

No consent row is ever created for a doctor who has no qualifying prior
case to see — this avoids spurious approval requests for a patient's first
doctor, or for doctors who are already the sole reviewer.

## Summary generation

- **Source cases**: `ClinicalCase` rows whose linked `PatientSubmission` has
  `status in {"doctor_completed", "released_to_patient"}`, filtered by
  `patient_owner_id`, across all doctors (including the requesting doctor's
  own prior cases for that patient, if any — the history view is a full
  picture, not just "other doctors only").
- **On a `GET /patients/{patient_id}/history` call** with approved consent:
  1. Compute the current qualifying case id set for the patient.
  2. If a cached `PatientHistorySummary` exists with the same
     `source_case_ids_json`, return it as-is (no LLM call).
  3. Otherwise, call Groq (same client/pattern as
     `POST /agent/patient-summary` in `apps/api/api/routes/agent.py`) with
     each qualifying case's: reviewing doctor id, date, accepted HPO
     findings (`assertion == "present"`), and top diagnosis. Prompt for a
     short prose handoff paragraph (2-4 sentences, plain clinical language,
     no confidence scores) analogous in style to the existing patient
     summary prompt. Store the result, replacing any prior cached row for
     that patient.
  4. Alongside the prose summary, the endpoint also returns a **structured
     timeline** built directly from the rows (not LLM-generated): per case,
     `{date, doctor_id, top_diagnosis, visit_recommendation}` — this is the
     ground truth a doctor can double check against the prose.
- **Cache invalidation**: `complete_review` and `release_submission` in
  `submissions.py` do not need to explicitly bust the cache — staleness is
  detected structurally by comparing case-id sets on each read, so no extra
  invalidation code path is needed beyond keeping the comparison logic
  correct.

## API surface summary

| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | `/patients/me/consent-requests` | patient | List pending requests to approve/deny |
| POST | `/consent-requests/{id}/approve` | patient | Approve a doctor's history access |
| POST | `/consent-requests/{id}/deny` | patient | Deny a doctor's history access |
| GET | `/patients/{patient_id}/history` | doctor | Fetch cached/regenerated summary + timeline (403 if not approved) |

## Frontend

- **Patient side**: a new "History sharing requests" card added to
  `apps/web/src/app/[locale]/patient/submissions/page.tsx`, listing pending
  requests with Approve/Deny buttons, following the existing card/list
  patterns already used on that page.
- **Doctor side**: a new "Patient History" panel added to
  `apps/web/src/app/[locale]/case/[id]/page.tsx` (and/or
  `clinical-reviewer/page.tsx`), which:
  - Shows "Access pending patient approval" state if no approved consent
    exists yet (and a request was or will be auto-created via
    `start-review`).
  - Shows the AI prose summary plus the structured timeline once approved.

## Safety properties

- No cross-doctor visibility without explicit per-doctor patient consent.
- Summary source data is restricted to `doctor_completed` /
  `released_to_patient` cases only — never in-progress workups, never
  rejected/pending phenotype suggestions. This preserves the existing
  doctor-in-the-loop guarantee: only clinician-approved conclusions ever
  reach another clinician's view.
- Denied consent is terminal for that `(patient, doctor)` pair in this pass
  — no automatic re-request. A patient could theoretically be asked again
  if the *doctor* calls `start-review` again on a new submission and the
  existing row is checked first (row already exists → no duplicate created,
  regardless of status), so a denial is not re-prompted.

## Open items for the implementation plan

- Exact Groq prompt text for the handoff summary (mirror
  `agent.py`'s `_fallback_patient_summary` fallback pattern for when
  `GROQ_API_KEY` is unset).
- Whether `/patients/{patient_id}/history` needs pagination for very long
  case histories (out of scope for a 10-hour build; timeline can be
  unpaginated for now).
