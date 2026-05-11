from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

import requests

API_URL = os.getenv("ARQBANKER_API_URL", "http://localhost:8000").rstrip("/")


def api_get(path: str):
    response = requests.get(f"{API_URL}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: dict | None = None, params: dict | None = None):
    response = requests.post(f"{API_URL}{path}", json=payload, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def get_health():
    return api_get("/health")


def get_cases():
    return api_get("/cases")


def get_case(case_id: str):
    return api_get(f"/cases/{case_id}")


def add_action(
    case_id: str,
    action_type: str,
    summary: str,
    actor_user_id: str = "sarah.kim",
    actor_role: str = "analyst_l2",
    details: dict | None = None,
):
    payload = {
        "action_id": f"ACT-{uuid4().hex[:8]}",
        "action_type": action_type,
        "actor_user_id": actor_user_id,
        "actor_role": actor_role,
        "created_at": datetime.now(UTC).isoformat(),
        "summary": summary,
        "details": details or {},
        "human_confirmed": True,
    }
    return api_post(f"/cases/{case_id}/actions", payload)


def add_note(case_id: str, text: str, actor_user_id: str = "sarah.kim", actor_role: str = "analyst_l2"):
    return api_post(
        f"/cases/{case_id}/notes",
        {"text": text, "actor_user_id": actor_user_id, "actor_role": actor_role},
    )


def generate_evidence_package(case_id: str, generated_by: str = "sarah.kim"):
    return api_post(f"/cases/{case_id}/evidence-package", params={"generated_by": generated_by})


def get_audit_events():
    return api_get("/audit")


def verify_audit_chain():
    return api_get("/audit/verify")


def get_cco_dashboard():
    return api_get("/dashboard/cco")

