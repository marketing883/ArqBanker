from __future__ import annotations

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.store import reset_store
from shared.constants import GOLDEN_CASE_ID
from shared.schemas import CaseAction


def test_evidence_package_contains_case_artifact_ids() -> None:
    reset_store()
    action = CaseAction(
        action_id="ACT-BLOCK-EVIDENCE",
        action_type="block_transaction",
        actor_user_id="sarah.kim",
        actor_role="analyst",
        created_at=datetime.now(UTC),
        summary="Blocked transaction after sanctions review.",
        details={"transaction_id": "TXN-9001"},
    )

    with TestClient(app) as client:
        client.post(f"/cases/{GOLDEN_CASE_ID}/actions", json=action.model_dump(mode="json"))
        response = client.post(
            f"/cases/{GOLDEN_CASE_ID}/evidence-package",
            params={"generated_by": "sarah.kim"},
        )
        audit_response = client.get("/audit")

    package = response.json()
    evidence_events = [
        event for event in audit_response.json() if event["event_type"] == "evidence_package_generated"
    ]

    assert response.status_code == 200
    assert set(package["triggered_rule_ids"]) >= {"SAN-01", "AML-01", "FRAUD-03"}
    assert set(package["policy_recommendation_ids"]) >= {"POL-OFAC-001", "POL-BSA-001"}
    assert action.action_id in package["action_ids"]
    assert evidence_events[-1]["event_id"] in package["audit_event_ids"]
    assert package["hash_chain_verified"] is True

