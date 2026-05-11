from __future__ import annotations

from datetime import UTC, datetime

from backend.app.audit import create_audit_event
from shared.schemas import AuditEvent, Case, CaseAction, CaseStatus

SUPPORTED_ACTION_TYPES = {
    "accept_case",
    "block_transaction",
    "restrict_account",
    "send_secure_message",
    "generate_sar_draft",
    "escalate",
    "close_case",
}


def status_for_action(current_status: CaseStatus, action_type: str) -> CaseStatus:
    if action_type == "accept_case":
        return "investigating"
    if action_type in {"block_transaction", "generate_sar_draft"}:
        return "pending_filing"
    if action_type == "close_case":
        return "closed"
    if action_type == "escalate":
        return "escalated"
    return current_status


def add_case_action(case: Case, action: CaseAction, audit_events: list[AuditEvent]) -> Case:
    if action.action_type not in SUPPORTED_ACTION_TYPES:
        raise ValueError(f"Unsupported action type: {action.action_type}")
    if not action.actor_user_id.strip():
        raise ValueError("Action actor is required")
    if not action.actor_role.strip():
        raise ValueError("Action actor role is required")
    if not action.summary.strip():
        raise ValueError("Action summary is required")

    case.actions.append(action)
    case.status = status_for_action(case.status, action.action_type)
    case.updated_at = datetime.now(UTC)

    audit_events.append(
        create_audit_event(
            events=audit_events,
            actor_user_id=action.actor_user_id,
            actor_role=action.actor_role,
            event_type=f"case_action.{action.action_type}",
            entity_type="case",
            entity_id=case.case_id,
            summary=action.summary,
            payload={"action_id": action.action_id, **action.details},
        )
    )
    return case


def add_case_note(case: Case, note: dict[str, str], audit_events: list[AuditEvent]) -> Case:
    text = note.get("text", "").strip()
    if not text:
        raise ValueError("Note text is required")

    actor_user_id = note.get("actor_user_id", "unknown").strip() or "unknown"
    actor_role = note.get("actor_role", "analyst").strip() or "analyst"

    case.notes.append(text)
    case.updated_at = datetime.now(UTC)

    audit_events.append(
        create_audit_event(
            events=audit_events,
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            event_type="case_note_added",
            entity_type="case",
            entity_id=case.case_id,
            summary="Investigation note added",
            payload={"text": text[:250]},
        )
    )
    return case

