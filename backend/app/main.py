from __future__ import annotations

from fastapi import FastAPI, HTTPException

from backend.app.audit import verify_hash_chain
from backend.app.evidence import generate_evidence_package as build_evidence_package
from backend.app.policy import ensure_policy_recommendations
from backend.app.store import audit_events, cases, initialize_store
from backend.app.workflow import add_case_action as apply_case_action
from backend.app.workflow import add_case_note as apply_case_note
from shared.constants import GOLDEN_CASE_ID
from shared.schemas import AuditEvent, Case, CaseAction, EvidencePackage

app = FastAPI(title="ArqBanker POC API", version="0.1.0")


@app.on_event("startup")
def startup() -> None:
    initialize_store()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "golden_case": GOLDEN_CASE_ID}


@app.get("/cases", response_model=list[Case])
def list_cases() -> list[Case]:
    initialize_store()
    return list(cases.values())


@app.get("/cases/{case_id}", response_model=Case)
def get_case(case_id: str) -> Case:
    initialize_store()
    if case_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")
    return ensure_policy_recommendations(cases[case_id])


@app.post("/cases/{case_id}/actions", response_model=Case)
def add_case_action(case_id: str, action: CaseAction) -> Case:
    initialize_store()
    if case_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")

    try:
        return apply_case_action(cases[case_id], action, audit_events)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/cases/{case_id}/notes", response_model=Case)
def add_case_note(case_id: str, note: dict[str, str]) -> Case:
    initialize_store()
    if case_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")

    try:
        return apply_case_note(cases[case_id], note, audit_events)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/cases/{case_id}/evidence-package", response_model=EvidencePackage)
def generate_evidence_package(case_id: str, generated_by: str = "sarah.kim") -> EvidencePackage:
    initialize_store()
    if case_id not in cases:
        raise HTTPException(status_code=404, detail="Case not found")

    case = ensure_policy_recommendations(cases[case_id])
    return build_evidence_package(case, audit_events, generated_by=generated_by)


@app.get("/audit", response_model=list[AuditEvent])
def get_audit_events() -> list[AuditEvent]:
    initialize_store()
    return audit_events


@app.get("/audit/verify")
def verify_audit() -> dict[str, bool | int]:
    initialize_store()
    return {"verified": verify_hash_chain(audit_events), "event_count": len(audit_events)}


@app.get("/dashboard/cco")
def cco_dashboard() -> dict[str, int | float | bool]:
    initialize_store()
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
