from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.store import reset_store
from shared.constants import GOLDEN_CASE_ID
from shared.schemas import CaseAction


def test_case_4521_can_be_loaded() -> None:
    reset_store()

    with TestClient(app) as client:
        response = client.get(f"/cases/{GOLDEN_CASE_ID}")

    assert response.status_code == 200
    assert response.json()["case_id"] == GOLDEN_CASE_ID


def test_case_4532_is_available_in_case_queue() -> None:
    reset_store()

    with TestClient(app) as client:
        response = client.get("/cases")

    case_ids = {case["case_id"] for case in response.json()}
    assert response.status_code == 200
    assert case_ids >= {"CASE-4521", "CASE-4532"}


def test_adding_note_creates_audit_event() -> None:
    reset_store()

    with TestClient(app) as client:
        note_response = client.post(
            f"/cases/{GOLDEN_CASE_ID}/notes",
            json={
                "text": "Reviewed sanctions and AML evidence.",
                "actor_user_id": "sarah.kim",
                "actor_role": "analyst",
            },
        )
        audit_response = client.get("/audit")

    assert note_response.status_code == 200
    assert any(event["event_type"] == "case_note_added" for event in audit_response.json())


def test_block_transaction_action_changes_status_and_audits() -> None:
    reset_store()
    action = CaseAction(
        action_id="ACT-BLOCK-1",
        action_type="block_transaction",
        actor_user_id="sarah.kim",
        actor_role="analyst",
        created_at=datetime.now(UTC),
        summary="Blocked transaction after human review.",
        details={"transaction_id": "TXN-9001"},
    )

    with TestClient(app) as client:
        action_response = client.post(
            f"/cases/{GOLDEN_CASE_ID}/actions",
            json=action.model_dump(mode="json"),
        )
        audit_response = client.get("/audit")

    assert action_response.status_code == 200
    assert action_response.json()["status"] == "pending_filing"
    assert any(
        event["event_type"] == "case_action.block_transaction"
        and event["payload"]["action_id"] == action.action_id
        for event in audit_response.json()
    )


def test_cco_dashboard_reports_verified_hash_chain() -> None:
    reset_store()

    with TestClient(app) as client:
        response = client.get("/dashboard/cco")

    assert response.status_code == 200
    assert response.json()["audit_hash_chain_verified"] is True
