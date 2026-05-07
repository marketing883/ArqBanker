from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException

from backend.app.audit import create_audit_event, verify_hash_chain
from shared.constants import GOLDEN_CASE_ID
from shared.schemas import AuditEvent, Case, CaseAction, EvidencePackage

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"

app = FastAPI(title="ArqBanker POC API", version="0.1.0")

cases: dict[str, Case] = {}
audit_events: list[AuditEvent] = []


def load_golden_case() -> Case:
    raw = json.loads((DATA_DIR / "golden_case_4521.json").read_text(encoding="utf-8"))
    return Case(**raw)


@app.on_event("startup")
def startup() -> None:
    if GOLDEN_CASE_ID not in cases:
        case = load_golden_case()
        cases[case.case_id] = case
        audit_events.append(
            create_audit_event(
                events=audit_events,
                actor_user_id="system",
                actor_role="system",
                event_type="case_created",
                entity_type="case",
                entity_id=case.case_id,
                summary=f"Loaded golden demo case {case.case_id}",
                payload={"risk_score": case.risk_score.overall_score},
            )
        )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "golden_case": GOLDEN_CASE_ID}


@app.get("/cases", response_model=list[Case])
def list_cases() -> list[Case]:
    return list(cases.values())


@app.get("/cases/{case_id}", response_model=Case)
def get_case(case_id: str) -> Case:
    if case_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")
    return cases[case_id]


@app.post("/cases/{case_id}/actions", response_model=Case)
def add_case_action(case_id: str, action: CaseAction) -> Case:
    if case_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")

    case = cases[case_id]
    case.actions.append(action)
    case.status = "pending_filing" if action.action_type == "block_transaction" else "investigating"
    case.updated_at = datetime.now(UTC)

    audit_events.append(
        create_audit_event(
            events=audit_events,
            actor_user_id=action.actor_user_id,
            actor_role=action.actor_role,
            event_type=f"case_action.{action.action_type}",
            entity_type="case",
            entity_id=case_id,
            summary=action.summary,
            payload={"action_id": action.action_id, **action.details},
        )
    )
    return case


@app.post("/cases/{case_id}/notes", response_model=Case)
def add_case_note(case_id: str, note: dict[str, str]) -> Case:
    if case_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")

    text = note.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="Note text is required")

    case = cases[case_id]
    case.notes.append(text)
    case.updated_at = datetime.now(UTC)

    audit_events.append(
        create_audit_event(
            events=audit_events,
            actor_user_id=note.get("actor_user_id", "unknown"),
            actor_role=note.get("actor_role", "analyst"),
            event_type="case_note_added",
            entity_type="case",
            entity_id=case_id,
            summary="Investigation note added",
            payload={"text": text[:250]},
        )
    )
    return case


@app.post("/cases/{case_id}/evidence-package", response_model=EvidencePackage)
def generate_evidence_package(case_id: str, generated_by: str = "sarah.kim") -> EvidencePackage:
    if case_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")

    case = cases[case_id]
    package = EvidencePackage(
        package_id=f"EVP-{uuid4().hex[:10]}",
        case_id=case.case_id,
        generated_at=datetime.now(UTC),
        generated_by=generated_by,
        sar_narrative=(
            f"{case.customer.entity_name} initiated a USD "
            f"{case.transactions[0].amount_usd:,.0f} wire to "
            f"{case.transactions[0].beneficiary_name}. The case triggered "
            f"{', '.join(rule.rule_id for rule in case.triggered_rules)}. "
            "Human review is required before filing or external reporting."
        ),
        triggered_rule_ids=[rule.rule_id for rule in case.triggered_rules],
        policy_recommendation_ids=[policy.policy_id for policy in case.policy_recommendations],
        action_ids=[action.action_id for action in case.actions],
        audit_event_ids=[event.event_id for event in audit_events if event.entity_id == case_id],
        hash_chain_verified=verify_hash_chain(audit_events),
    )

    audit_events.append(
        create_audit_event(
            events=audit_events,
            actor_user_id=generated_by,
            actor_role="analyst_l2",
            event_type="evidence_package_generated",
            entity_type="case",
            entity_id=case_id,
            summary=f"Evidence package {package.package_id} generated",
            payload={"package_id": package.package_id},
        )
    )
    return package


@app.get("/audit", response_model=list[AuditEvent])
def get_audit_events() -> list[AuditEvent]:
    return audit_events


@app.get("/audit/verify")
def verify_audit() -> dict[str, bool | int]:
    return {"verified": verify_hash_chain(audit_events), "event_count": len(audit_events)}


@app.get("/dashboard/cco")
def cco_dashboard() -> dict[str, int | float | bool]:
    active_cases = [case for case in cases.values() if case.status not in {"closed", "resolved"}]
    critical_cases = [case for case in active_cases if case.risk_score.band == "critical"]
    return {
        "active_cases": len(active_cases),
        "critical_cases": len(critical_cases),
        "sars_due": len(critical_cases),
        "ofac_action_required": sum(
            1
            for case in active_cases
            for policy in case.policy_recommendations
            if policy.regulation == "OFAC"
        ),
        "audit_hash_chain_verified": verify_hash_chain(audit_events),
        "false_positive_rate_target": 15,
    }
