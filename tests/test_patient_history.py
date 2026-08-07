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
