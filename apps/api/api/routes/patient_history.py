import json
import os
import time
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from sqlmodel import Session, select

from api.app_models import (
    ClinicalCase,
    PatientHistoryConsent,
    PatientHistorySummary,
    PatientSubmission,
)

router = APIRouter(tags=["patient-history"])


def _now_ms() -> int:
    return int(time.time() * 1000)


def _actor(request: Request) -> tuple[str, str]:
    user_id = request.headers.get("x-lumina-user-id", "").strip()
    role = request.headers.get("x-lumina-role", "").strip()
    if not user_id or role not in {"doctor", "patient"}:
        raise HTTPException(status_code=401, detail="Missing Lumina actor headers")
    return user_id, role


def _consent_payload(row: PatientHistoryConsent) -> dict:
    return {
        "id": row.id,
        "doctorId": row.doctor_id,
        "status": row.status,
        "requestedAt": row.requested_at,
        "decidedAt": row.decided_at,
        "submissionId": row.triggered_by_submission_id,
    }


@router.get("/patients/me/consent-requests")
async def list_consent_requests(request: Request):
    user_id, role = _actor(request)
    if role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can view consent requests")
    with Session(request.app.state.app_db_engine) as session:
        rows = session.exec(
            select(PatientHistoryConsent)
            .where(PatientHistoryConsent.patient_owner_id == user_id)
            .where(PatientHistoryConsent.status == "pending")
            .order_by(PatientHistoryConsent.requested_at.desc())
        ).all()
        return [_consent_payload(row) for row in rows]


def _decide_consent(
    session: Session, consent_id: str, user_id: str, status: str
) -> PatientHistoryConsent:
    row = session.get(PatientHistoryConsent, consent_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Consent request not found")
    if row.patient_owner_id != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    row.status = status
    row.decided_at = _now_ms()
    session.add(row)
    session.commit()
    session.refresh(row)
    return row


@router.post("/consent-requests/{consent_id}/approve")
async def approve_consent_request(consent_id: str, request: Request):
    user_id, role = _actor(request)
    if role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can approve requests")
    with Session(request.app.state.app_db_engine) as session:
        row = _decide_consent(session, consent_id, user_id, "approved")
        return _consent_payload(row)


@router.post("/consent-requests/{consent_id}/deny")
async def deny_consent_request(consent_id: str, request: Request):
    user_id, role = _actor(request)
    if role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can deny requests")
    with Session(request.app.state.app_db_engine) as session:
        row = _decide_consent(session, consent_id, user_id, "denied")
        return _consent_payload(row)


def _qualifying_cases(session: Session, patient_id: str) -> list[ClinicalCase]:
    rows = session.exec(
        select(ClinicalCase, PatientSubmission.status)
        .join(PatientSubmission, PatientSubmission.id == ClinicalCase.submission_id)
        .where(ClinicalCase.patient_owner_id == patient_id)
        .where(PatientSubmission.status.in_(["doctor_completed", "released_to_patient"]))
        .order_by(ClinicalCase.updated_at.asc())
    ).all()
    return [case for case, _status in rows]


def _timeline_entry(case: ClinicalCase) -> dict:
    payload = json.loads(case.case_json)
    rankings = payload.get("rankings") or []
    top_name = rankings[0].get("name") if rankings else "Unknown"
    return {
        "caseId": case.id,
        "doctorId": case.doctor_owner_id,
        "date": case.updated_at,
        "topDiagnosis": top_name,
        "visitRecommendation": payload.get("visitRecommendation"),
    }


def _fallback_summary(timeline: list[dict]) -> str:
    if not timeline:
        return "No prior doctor-completed history is available for this patient."
    lines = [f"- {entry['topDiagnosis']} (reviewed by a prior clinician)" for entry in timeline]
    return "Prior clinical history on file:\n" + "\n".join(lines)


async def _generate_summary(timeline: list[dict]) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return _fallback_summary(timeline)
    try:
        from groq import AsyncGroq

        client = AsyncGroq(api_key=api_key)
        user_msg = json.dumps(timeline, ensure_ascii=False)
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=300,
            temperature=0.2,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are writing a short clinical handoff note for a doctor who is "
                        "about to see a patient for the first time. You are given a JSON list "
                        "of the patient's prior doctor-completed cases (each with a reviewing "
                        "doctor id, date, top diagnosis, and visit recommendation). Write a "
                        "2-4 sentence plain-language prose summary a clinician can read in a "
                        "few seconds. Do not include confidence scores, HPO ids, or ORPHA "
                        "codes. Do not fabricate details not present in the data."
                    ),
                },
                {"role": "user", "content": user_msg},
            ],
        )
        text = response.choices[0].message.content.strip()
        return text or _fallback_summary(timeline)
    except Exception:
        return _fallback_summary(timeline)


@router.get("/patients/{patient_id}/history")
async def get_patient_history(patient_id: str, request: Request):
    user_id, role = _actor(request)
    if role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can view patient history")
    with Session(request.app.state.app_db_engine) as session:
        consent = session.exec(
            select(PatientHistoryConsent)
            .where(PatientHistoryConsent.patient_owner_id == patient_id)
            .where(PatientHistoryConsent.doctor_id == user_id)
            .where(PatientHistoryConsent.status == "approved")
        ).first()
        if consent is None:
            raise HTTPException(status_code=403, detail="Patient has not approved history access")

        cases = _qualifying_cases(session, patient_id)
        timeline = [_timeline_entry(case) for case in cases]
        source_ids_json = json.dumps(sorted(case.id for case in cases))

        cached = session.exec(
            select(PatientHistorySummary).where(
                PatientHistorySummary.patient_owner_id == patient_id
            )
        ).first()
        if cached is not None and cached.source_case_ids_json == source_ids_json:
            return {"summary": cached.summary_markdown, "timeline": timeline}

        summary_text = await _generate_summary(timeline)
        if cached is None:
            cached = PatientHistorySummary(
                id=str(uuid4()),
                patient_owner_id=patient_id,
                summary_markdown=summary_text,
                source_case_ids_json=source_ids_json,
                generated_at=_now_ms(),
            )
        else:
            cached.summary_markdown = summary_text
            cached.source_case_ids_json = source_ids_json
            cached.generated_at = _now_ms()
        session.add(cached)
        session.commit()
        return {"summary": summary_text, "timeline": timeline}
