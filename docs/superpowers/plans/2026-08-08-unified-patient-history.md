# Unified Cross-Doctor Patient History Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let a doctor reviewing a new patient's submission see a consent-gated, AI-summarized history of that patient's completed diagnoses from other doctors, so the patient never has to re-explain their history.

**Architecture:** Two new SQLModel tables (`PatientHistoryConsent`, `PatientHistorySummary`) in the existing Supabase-backed app DB. A new FastAPI router (`patient_history.py`) exposes consent list/approve/deny and a cached, Groq-generated history summary endpoint. `start_review` in `submissions.py` is extended to auto-create a pending consent row. Frontend adds a small consent-request card to the patient submissions page and a history panel to the doctor's case page.

**Tech Stack:** FastAPI, SQLModel, Supabase Postgres, Groq (llama-3.3-70b-versatile), Next.js 16 / React, next-intl.

## Global Constraints

- Follow the spec at `docs/superpowers/specs/2026-08-08-unified-patient-history-design.md` exactly — source cases are `doctor_completed` / `released_to_patient` only; no in-progress or rejected data ever appears in the summary.
- Match existing code style: FastAPI routers use `_actor(request)` header-based auth (`x-lumina-user-id`, `x-lumina-role`) exactly as in `submissions.py`.
- Match existing frontend conventions: `next-intl` translations (all 7 locale files under `apps/web/src/messages/`), Tailwind utility classes matching the existing patient/doctor pages (see `patient/submissions/page.tsx` for the established visual style), `useApiActor()` for the current actor.
- `ruff check .` and `ruff format --check .` must pass in `apps/api` (per `.github/workflows/ci.yml`).
- No test-suite run is possible without a working `DATABASE_URL` — flag this to the user rather than silently skipping verification.

---

### Task 1: Add `PatientHistoryConsent` and `PatientHistorySummary` tables

**Files:**
- Modify: `apps/api/api/app_models.py`

**Interfaces:**
- Produces: `PatientHistoryConsent` (fields: `id`, `patient_owner_id`, `doctor_id`, `status`, `triggered_by_submission_id`, `requested_at`, `decided_at`) and `PatientHistorySummary` (fields: `id`, `patient_owner_id` unique, `summary_markdown`, `source_case_ids_json`, `generated_at`) — both SQLModel tables, imported by `init_app_db()` automatically since it imports the whole `api.app_models` module.

- [ ] **Step 1: Add the two table classes**

Append to `apps/api/api/app_models.py`:

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
    source_case_ids_json: str
    generated_at: int
```

- [ ] **Step 2: Verify the module still imports cleanly**

Run: `cd apps/api && uv run python -c "from api import app_models; print('ok')"`
Expected: `ok`

- [ ] **Step 3: Lint**

Run: `cd apps/api && uv run ruff check api/app_models.py && uv run ruff format --check api/app_models.py`
Expected: no output, exit 0

- [ ] **Step 4: Commit**

```bash
git add apps/api/api/app_models.py
git commit -m "feat(api): add patient history consent and summary cache tables

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 2: Auto-create pending consent on `start-review`

**Files:**
- Modify: `apps/api/api/routes/submissions.py`

**Interfaces:**
- Consumes: `PatientSubmission`, `ClinicalCase` (existing), `PatientHistoryConsent` (from Task 1), `_now_ms()` (existing helper in this file).
- Produces: `_maybe_request_history_consent(session, patient_owner_id, doctor_id, submission_id)` — called from `start_review`. No return value used by callers.

- [ ] **Step 1: Import the new model**

In `apps/api/api/routes/submissions.py`, change:

```python
from api.app_models import ClinicalCase, DoctorRequestMessage, PatientSubmission
```

to:

```python
from api.app_models import (
    ClinicalCase,
    DoctorRequestMessage,
    PatientHistoryConsent,
    PatientSubmission,
)
```

- [ ] **Step 2: Add the helper function**

Add above `start_review`:

```python
def _maybe_request_history_consent(
    session: Session, patient_owner_id: str, doctor_id: str, submission_id: str
) -> None:
    has_other_doctor_case = session.exec(
        select(ClinicalCase.id)
        .join(
            PatientSubmission,
            PatientSubmission.id == ClinicalCase.submission_id,
        )
        .where(ClinicalCase.patient_owner_id == patient_owner_id)
        .where(ClinicalCase.doctor_owner_id != doctor_id)
        .where(
            PatientSubmission.status.in_(["doctor_completed", "released_to_patient"])
        )
    ).first()
    if has_other_doctor_case is None:
        return
    existing = session.exec(
        select(PatientHistoryConsent)
        .where(PatientHistoryConsent.patient_owner_id == patient_owner_id)
        .where(PatientHistoryConsent.doctor_id == doctor_id)
    ).first()
    if existing is not None:
        return
    session.add(
        PatientHistoryConsent(
            id=str(uuid4()),
            patient_owner_id=patient_owner_id,
            doctor_id=doctor_id,
            status="pending",
            triggered_by_submission_id=submission_id,
            requested_at=_now_ms(),
        )
    )
```

- [ ] **Step 3: Call it from `start_review`**

In `start_review`, after `row.doctor_reviewer_id = user_id` and before `session.commit()`, add:

```python
        _maybe_request_history_consent(session, row.patient_owner_id, user_id, submission_id)
```

The full updated function body:

```python
@router.post("/submissions/{submission_id}/start-review")
async def start_review(submission_id: str, request: Request):
    user_id, role = _actor(request)
    if role != "doctor":
        raise HTTPException(status_code=403, detail="Only doctors can review")
    with Session(request.app.state.app_db_engine) as session:
        row = session.get(PatientSubmission, submission_id)
        if row is None:
            raise HTTPException(status_code=404, detail="Submission not found")
        row.status = "in_review"
        row.doctor_reviewer_id = user_id
        row.updated_at = _now_ms()
        session.add(row)
        _maybe_request_history_consent(session, row.patient_owner_id, user_id, submission_id)
        session.commit()
        session.refresh(row)
        return _submission_payload(row)
```

- [ ] **Step 4: Write the test**

Create `tests/test_patient_history.py`:

```python
"""Patient history consent + summary endpoint tests."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from main import app
    with TestClient(app) as c:
        yield c


def _patient_headers(user_id: str) -> dict:
    return {"x-lumina-user-id": user_id, "x-lumina-role": "patient"}


def _doctor_headers(user_id: str) -> dict:
    return {"x-lumina-user-id": user_id, "x-lumina-role": "doctor"}


def _create_and_complete_case(client, patient_id: str, doctor_id: str) -> str:
    sub = client.post(
        "/submissions",
        headers=_patient_headers(patient_id),
        data={"notes": "history test notes"},
    ).json()
    client.post(f"/submissions/{sub['id']}/start-review", headers=_doctor_headers(doctor_id))
    case = client.post(
        "/cases",
        headers=_doctor_headers(doctor_id),
        json={
            "case_data": {
                "rankings": [{"orpha_code": 1, "name": "Test disease", "confidence": 90, "contributing_terms": []}],
                "hpoTerms": [],
                "modalities": ["notes"],
            },
            "submission_id": sub["id"],
        },
    ).json()
    client.post(
        f"/submissions/{sub['id']}/complete-review",
        headers=_doctor_headers(doctor_id),
        json={"case_id": case["id"]},
    )
    return sub["id"]


def test_no_consent_request_for_first_doctor(client):
    patient_id = "hist-patient-1"
    doctor_id = "hist-doctor-1"
    _create_and_complete_case(client, patient_id, doctor_id)
    resp = client.get("/patients/me/consent-requests", headers=_patient_headers(patient_id))
    assert resp.status_code == 200
    assert resp.json() == []


def test_consent_request_created_for_second_doctor(client):
    patient_id = "hist-patient-2"
    doctor_a = "hist-doctor-a"
    doctor_b = "hist-doctor-b"
    _create_and_complete_case(client, patient_id, doctor_a)

    sub2 = client.post(
        "/submissions",
        headers=_patient_headers(patient_id),
        data={"notes": "second visit"},
    ).json()
    client.post(f"/submissions/{sub2['id']}/start-review", headers=_doctor_headers(doctor_b))

    resp = client.get("/patients/me/consent-requests", headers=_patient_headers(patient_id))
    assert resp.status_code == 200
    requests = resp.json()
    assert len(requests) == 1
    assert requests[0]["doctorId"] == doctor_b
    assert requests[0]["status"] == "pending"


def test_history_denied_without_approval(client):
    patient_id = "hist-patient-3"
    doctor_a = "hist-doctor-c"
    doctor_b = "hist-doctor-d"
    _create_and_complete_case(client, patient_id, doctor_a)
    sub2 = client.post(
        "/submissions",
        headers=_patient_headers(patient_id),
        data={"notes": "second visit"},
    ).json()
    client.post(f"/submissions/{sub2['id']}/start-review", headers=_doctor_headers(doctor_b))

    resp = client.get(f"/patients/{patient_id}/history", headers=_doctor_headers(doctor_b))
    assert resp.status_code == 403


def test_approve_then_fetch_history(client):
    patient_id = "hist-patient-4"
    doctor_a = "hist-doctor-e"
    doctor_b = "hist-doctor-f"
    _create_and_complete_case(client, patient_id, doctor_a)
    sub2 = client.post(
        "/submissions",
        headers=_patient_headers(patient_id),
        data={"notes": "second visit"},
    ).json()
    client.post(f"/submissions/{sub2['id']}/start-review", headers=_doctor_headers(doctor_b))

    requests = client.get(
        "/patients/me/consent-requests", headers=_patient_headers(patient_id)
    ).json()
    consent_id = requests[0]["id"]
    approve = client.post(
        f"/consent-requests/{consent_id}/approve", headers=_patient_headers(patient_id)
    )
    assert approve.status_code == 200
    assert approve.json()["status"] == "approved"

    resp = client.get(f"/patients/{patient_id}/history", headers=_doctor_headers(doctor_b))
    assert resp.status_code == 200
    data = resp.json()
    assert "summary" in data
    assert len(data["timeline"]) == 1
    assert data["timeline"][0]["doctorId"] == doctor_a
```

- [ ] **Step 5: Run test to verify it fails** (endpoints don't exist yet)

Run: `cd apps/api && DATABASE_URL=<your test db url> uv run pytest ../../tests/test_patient_history.py -v`
Expected: FAIL — `404 Not Found` on `/patients/me/consent-requests` (router not registered yet).

- [ ] **Step 6: Lint**

Run: `cd apps/api && uv run ruff check api/routes/submissions.py && uv run ruff format --check api/routes/submissions.py`
Expected: no output, exit 0

- [ ] **Step 7: Commit**

```bash
git add apps/api/api/routes/submissions.py tests/test_patient_history.py
git commit -m "feat(api): auto-request patient history consent on start-review

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 3: Consent list/approve/deny + history summary endpoints

**Files:**
- Create: `apps/api/api/routes/patient_history.py`
- Modify: `apps/api/main.py`

**Interfaces:**
- Consumes: `PatientHistoryConsent`, `PatientHistorySummary`, `ClinicalCase`, `PatientSubmission` (existing/Task 1 models), `_actor` pattern (re-implemented locally, matching `submissions.py`'s `_actor(request)` signature: returns `(user_id, role)` and raises `HTTPException(401, ...)`).
- Produces: `router` (FastAPI `APIRouter`, prefix `/patients`... — see routes below), registered in `main.py` as `patient_history_router`.

Routes on this router:
- `GET /patients/me/consent-requests` (patient) → `list[dict]` with keys `id`, `doctorId`, `status`, `requestedAt`, `submissionId`.
- `POST /consent-requests/{consent_id}/approve` (patient) → same shape as above for the updated row.
- `POST /consent-requests/{consent_id}/deny` (patient) → same shape.
- `GET /patients/{patient_id}/history` (doctor) → `{"summary": str, "timeline": list[{"caseId": str, "doctorId": str, "date": int, "topDiagnosis": str, "visitRecommendation": str | None}]}`.

- [ ] **Step 1: Write the router file**

Create `apps/api/api/routes/patient_history.py`:

```python
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


def _decide_consent(session: Session, consent_id: str, user_id: str, status: str) -> PatientHistoryConsent:
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
    lines = [
        f"- {entry['topDiagnosis']} (reviewed by a prior clinician)" for entry in timeline
    ]
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
```

- [ ] **Step 2: Register the router in `main.py`**

In `apps/api/main.py`, change:

```python
from api.routes.intake import router as intake_router  # noqa: E402
```

Add right after it:

```python
from api.routes.patient_history import router as patient_history_router  # noqa: E402
```

And after `app.include_router(intake_router)`, add:

```python
app.include_router(patient_history_router)
```

- [ ] **Step 3: Run the tests from Task 2**

Run: `cd apps/api && DATABASE_URL=<your test db url> uv run pytest ../../tests/test_patient_history.py -v`
Expected: `4 passed`

- [ ] **Step 4: Run the full existing suite to check nothing broke**

Run: `cd apps/api && DATABASE_URL=<your test db url> uv run pytest ../../tests/ -v`
Expected: all tests pass (existing `test_api.py`, `test_ingest.py`, `test_scoring.py` unaffected).

- [ ] **Step 5: Lint**

Run: `cd apps/api && uv run ruff check . && uv run ruff format --check .`
Expected: no output, exit 0

- [ ] **Step 6: Commit**

```bash
git add apps/api/api/routes/patient_history.py apps/api/main.py
git commit -m "feat(api): add patient history consent and summary endpoints

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 4: Frontend API client functions

**Files:**
- Modify: `apps/web/src/lib/api.ts`
- Modify: `apps/web/src/types/lumina.ts`

**Interfaces:**
- Produces: `ConsentRequest` type, `PatientHistoryResponse` type, `getConsentRequestsRemote(actor)`, `approveConsentRequestRemote(id, actor)`, `denyConsentRequestRemote(id, actor)`, `getPatientHistoryRemote(patientId, actor)`.

- [ ] **Step 1: Add types**

In `apps/web/src/types/lumina.ts`, append:

```typescript
export interface ConsentRequest {
  id: string;
  doctorId: string;
  status: "pending" | "approved" | "denied";
  requestedAt: number;
  decidedAt?: number | null;
  submissionId?: string | null;
}

export interface PatientHistoryTimelineEntry {
  caseId: string;
  doctorId: string;
  date: number;
  topDiagnosis: string;
  visitRecommendation?: string | null;
}

export interface PatientHistoryResponse {
  summary: string;
  timeline: PatientHistoryTimelineEntry[];
}
```

- [ ] **Step 2: Add API client functions**

In `apps/web/src/lib/api.ts`, add the import for the new types at the top (extend the existing `import type {...} from "@/types/lumina"` line) and append these functions near the other submission functions:

```typescript
export async function getConsentRequestsRemote(actor: ApiActor): Promise<ConsentRequest[]> {
  const res = await fetch(`${API}/patients/me/consent-requests`, { headers: actorHeaders(actor), cache: "no-store" });
  return jsonOrThrow<ConsentRequest[]>(res, "Could not load consent requests");
}

export async function approveConsentRequestRemote(id: string, actor: ApiActor): Promise<ConsentRequest> {
  const res = await fetch(`${API}/consent-requests/${id}/approve`, { method: "POST", headers: actorHeaders(actor) });
  return jsonOrThrow<ConsentRequest>(res, "Could not approve request");
}

export async function denyConsentRequestRemote(id: string, actor: ApiActor): Promise<ConsentRequest> {
  const res = await fetch(`${API}/consent-requests/${id}/deny`, { method: "POST", headers: actorHeaders(actor) });
  return jsonOrThrow<ConsentRequest>(res, "Could not deny request");
}

export async function getPatientHistoryRemote(patientId: string, actor: ApiActor): Promise<PatientHistoryResponse> {
  const res = await fetch(`${API}/patients/${patientId}/history`, { headers: actorHeaders(actor), cache: "no-store" });
  return jsonOrThrow<PatientHistoryResponse>(res, "Could not load patient history");
}
```

Update the top-of-file type import line to include the three new types:

```typescript
import type { CaseData, CaseOutcome, CaseSummary, ConsentRequest, GeneticEvidence, HPOTerm, PatientContext, PatientHistoryResponse, PatientSubmission, PatientSummary, RankResult, VisitRecommendation } from "@/types/lumina";
```

- [ ] **Step 3: Typecheck**

Run: `cd apps/web && pnpm typecheck`
Expected: no errors

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/lib/api.ts apps/web/src/types/lumina.ts
git commit -m "feat(web): add patient history consent API client

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 5: Patient-side consent request card

**Files:**
- Modify: `apps/web/src/app/[locale]/patient/submissions/page.tsx`
- Modify: `apps/web/src/messages/en.json` (and `de.json`, `es.json`, `fr.json`, `hi.json`, `ja.json`, `zh.json`)

**Interfaces:**
- Consumes: `getConsentRequestsRemote`, `approveConsentRequestRemote`, `denyConsentRequestRemote` (Task 4), `useApiActor()` (existing).

- [ ] **Step 1: Add translation keys**

In `apps/web/src/messages/en.json`, inside the existing `"patientSubmissions"` object, add:

```json
    "historyRequestsTitle": "History sharing requests",
    "historyRequestsDesc": "A doctor is requesting access to your prior diagnosis history so you don't have to re-explain it.",
    "historyRequestApprove": "Approve",
    "historyRequestDeny": "Deny",
    "historyRequestApproved": "Access approved",
    "historyRequestDenied": "Access denied"
```

Add the same six keys (English text is an acceptable placeholder for non-English locales in this pass) to the `"patientSubmissions"` object in `de.json`, `es.json`, `fr.json`, `hi.json`, `ja.json`, and `zh.json`.

- [ ] **Step 2: Add the card component to the page**

In `apps/web/src/app/[locale]/patient/submissions/page.tsx`, add imports:

```typescript
import { approveConsentRequestRemote, denyConsentRequestRemote, getConsentRequestsRemote } from "@/lib/api";
import type { ConsentRequest } from "@/types/lumina";
```

(merge with the existing `@/lib/api` import line rather than duplicating it)

Add state and loading effect, right after the existing `submissions` state/effect block:

```typescript
  const [consentRequests, setConsentRequests] = useState<ConsentRequest[]>([]);
  useEffect(() => {
    if (!actor) return;
    getConsentRequestsRemote(actor).then(setConsentRequests).catch(() => {});
  }, [actor]);

  async function handleConsentDecision(id: string, approve: boolean) {
    if (!actor) return;
    try {
      const updated = approve
        ? await approveConsentRequestRemote(id, actor)
        : await denyConsentRequestRemote(id, actor);
      setConsentRequests((current) => current.filter((item) => item.id !== updated.id));
      toast.success(approve ? t("historyRequestApproved") : t("historyRequestDenied"));
    } catch {
      toast.error(t("loadFailed"));
    }
  }
```

Add the card markup right before the existing `<div className="mb-8 flex items-end justify-between gap-4">` header block:

```tsx
          {consentRequests.length > 0 && (
            <div className="mb-6 rounded border border-[#DDE3ED] bg-white p-5">
              <p className="text-[14px] font-normal text-[#0D1B2A]">{t("historyRequestsTitle")}</p>
              <p className="mt-1 text-[13px] text-[#4A5568]">{t("historyRequestsDesc")}</p>
              <div className="mt-3 space-y-2">
                {consentRequests.map((req) => (
                  <div key={req.id} className="flex items-center justify-between rounded border border-[#F0F2F5] bg-[#F7F8FA] px-4 py-2.5">
                    <span className="text-[13px] text-[#0D1B2A]">Dr. {req.doctorId.slice(0, 8)}</span>
                    <div className="flex gap-3">
                      <button
                        type="button"
                        onClick={() => handleConsentDecision(req.id, true)}
                        className="text-[13px] font-normal text-[#0AAFCE] hover:underline"
                      >
                        {t("historyRequestApprove")}
                      </button>
                      <button
                        type="button"
                        onClick={() => handleConsentDecision(req.id, false)}
                        className="text-[13px] font-normal text-[#B42318] hover:underline"
                      >
                        {t("historyRequestDeny")}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
```

- [ ] **Step 3: Typecheck and lint**

Run: `cd apps/web && pnpm typecheck && pnpm lint`
Expected: no errors

- [ ] **Step 4: Commit**

```bash
git add apps/web/src/app/\[locale\]/patient/submissions/page.tsx apps/web/src/messages/*.json
git commit -m "feat(web): add patient-facing history consent request card

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 6: Doctor-side patient history panel

**Files:**
- Create: `apps/web/src/components/lumina/patient-history-panel.tsx`
- Modify: `apps/web/src/app/[locale]/case/[id]/page.tsx`
- Modify: `apps/web/src/messages/en.json` (and the other 6 locale files)

**Interfaces:**
- Consumes: `getPatientHistoryRemote` (Task 4), `useApiActor()` (existing), `PatientHistoryResponse` (Task 4).
- Produces: `PatientHistoryPanel` component, props `{ patientId: string }`.

- [ ] **Step 1: Add translation keys**

Add a new top-level `"patientHistory"` namespace to `apps/web/src/messages/en.json`:

```json
  "patientHistory": {
    "title": "Patient history",
    "pending": "Waiting on patient approval to view prior history.",
    "empty": "No prior doctor-completed history for this patient.",
    "timelineTitle": "Prior cases",
    "loadFailed": "Could not load patient history."
  },
```

Add the same structure (English text as placeholder) to the other 6 locale files.

- [ ] **Step 2: Write the component**

Create `apps/web/src/components/lumina/patient-history-panel.tsx`:

```tsx
"use client";

import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";
import { getPatientHistoryRemote } from "@/lib/api";
import { useApiActor } from "@/lib/use-api-actor";
import type { PatientHistoryResponse } from "@/types/lumina";

export function PatientHistoryPanel({ patientId }: { patientId: string }) {
  const t = useTranslations("patientHistory");
  const actor = useApiActor();
  const [history, setHistory] = useState<PatientHistoryResponse | null>(null);
  const [status, setStatus] = useState<"loading" | "pending" | "ready" | "error">("loading");

  useEffect(() => {
    if (!actor || actor.role !== "doctor" || !patientId) return;
    setStatus("loading");
    getPatientHistoryRemote(patientId, actor)
      .then((data) => {
        setHistory(data);
        setStatus("ready");
      })
      .catch((err: Error) => {
        setStatus(err.message.includes("403") || err.message.toLowerCase().includes("not approved") ? "pending" : "error");
      });
  }, [actor, patientId]);

  if (!actor || actor.role !== "doctor" || !patientId) return null;

  return (
    <div className="rounded border border-[#DDE3ED] bg-white p-5">
      <p className="text-[14px] font-normal text-[#0D1B2A]">{t("title")}</p>
      {status === "loading" && <p className="mt-2 text-[13px] text-[#8A94A6]">…</p>}
      {status === "pending" && <p className="mt-2 text-[13px] text-[#D4860A]">{t("pending")}</p>}
      {status === "error" && <p className="mt-2 text-[13px] text-[#B42318]">{t("loadFailed")}</p>}
      {status === "ready" && history && (
        <div className="mt-3">
          <p className="text-[13.5px] text-[#0D1B2A]">{history.summary}</p>
          {history.timeline.length > 0 && (
            <div className="mt-4">
              <p className="text-[11px] font-normal uppercase tracking-[0.08em] text-[#8A94A6]">{t("timelineTitle")}</p>
              <div className="mt-2 space-y-1.5">
                {history.timeline.map((entry) => (
                  <div key={entry.caseId} className="flex items-center justify-between text-[12.5px] text-[#4A5568]">
                    <span>{entry.topDiagnosis}</span>
                    <span className="text-[#8A94A6]">{new Date(entry.date).toLocaleDateString()}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
          {history.timeline.length === 0 && <p className="mt-2 text-[13px] text-[#8A94A6]">{t("empty")}</p>}
        </div>
      )}
    </div>
  );
}
```

- [ ] **Step 3: Find where `patientOwnerId` / `sourceSubmissionId` is available in the case page**

Run: `grep -n "patientOwnerId\|sourceSubmissionId\|caseData\." apps/web/src/app/\[locale\]/case/\[id\]/page.tsx | head -30`

Identify the variable holding the loaded `CaseData` (it will be a `caseData` state variable per existing conventions in this repo) and confirm whether `patientOwnerId` is present on the object returned from `getCaseRemote` (it is not currently serialized into `CaseData` on the frontend — the backend's `_case_payload` doesn't include it either, since `ClinicalCase.patient_owner_id` isn't in `case_json`). Because of this, plumb `patientOwnerId` through explicitly:

- [ ] **Step 4: Expose `patient_owner_id` on the case payload**

In `apps/api/api/routes/submissions.py`, in `_case_payload`, add the patient id:

```python
def _case_payload(row: ClinicalCase) -> dict:
    payload = json.loads(row.case_json)
    payload["id"] = row.id
    if row.submission_id:
        payload["sourceSubmissionId"] = row.submission_id
    if row.patient_owner_id:
        payload["patientOwnerId"] = row.patient_owner_id
    return payload
```

In `apps/web/src/types/lumina.ts`, add `patientOwnerId?: string;` to the `CaseData` interface.

- [ ] **Step 5: Render the panel in the case page**

In `apps/web/src/app/[locale]/case/[id]/page.tsx`, import the component:

```typescript
import { PatientHistoryPanel } from "@/components/lumina/patient-history-panel";
```

Render it conditionally near the top of the case detail layout, wherever the page already renders patient-context info (locate via `grep -n "patientContext" apps/web/src/app/\[locale\]/case/\[id\]/page.tsx` to find the right insertion point), e.g.:

```tsx
{caseData.patientOwnerId && <PatientHistoryPanel patientId={caseData.patientOwnerId} />}
```

- [ ] **Step 6: Typecheck and lint**

Run: `cd apps/web && pnpm typecheck && pnpm lint`
Expected: no errors

- [ ] **Step 7: Commit**

```bash
git add apps/web/src/components/lumina/patient-history-panel.tsx apps/web/src/app/\[locale\]/case/\[id\]/page.tsx apps/web/src/types/lumina.ts apps/web/src/messages/*.json apps/api/api/routes/submissions.py
git commit -m "feat(web): add doctor-facing patient history panel

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
```

---

### Task 7: End-to-end verification

**Files:** none (verification only)

- [ ] **Step 1: Run full API test suite**

Run: `cd apps/api && DATABASE_URL=<db url> GROQ_API_KEY=<key> uv run pytest ../../tests/ -v`
Expected: all tests pass, including the 4 new `test_patient_history.py` tests.

- [ ] **Step 2: Run API lint**

Run: `cd apps/api && uv run ruff check . && uv run ruff format --check .`
Expected: no output, exit 0

- [ ] **Step 3: Run web typecheck, lint, and build**

Run: `cd apps/web && pnpm typecheck && pnpm lint && pnpm build`
Expected: build succeeds with no type or lint errors.

- [ ] **Step 4: Manual smoke test (if a DB is available)**

Start both servers per `README.md`, then:
1. As patient A, create a submission and have doctor A claim + complete it.
2. As patient A, create a second submission.
3. As doctor B, claim the second submission — confirm patient A now sees a pending consent request on `/patient/submissions`.
4. Approve it as patient A.
5. As doctor B, open the case page for the linked case — confirm the Patient History panel shows the AI summary and a one-entry timeline referencing doctor A's completed case.

