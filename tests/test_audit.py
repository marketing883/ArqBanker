from __future__ import annotations

from backend.app.audit import create_audit_event, verify_hash_chain


def test_audit_hash_chain_verifies_true() -> None:
    events = []
    events.append(
        create_audit_event(
            events=events,
            actor_user_id="system",
            actor_role="system",
            event_type="case_created",
            entity_type="case",
            entity_id="CASE-4521",
            summary="Case created",
        )
    )
    events.append(
        create_audit_event(
            events=events,
            actor_user_id="sarah.kim",
            actor_role="analyst",
            event_type="case_note_added",
            entity_type="case",
            entity_id="CASE-4521",
            summary="Note added",
            payload={"text": "Reviewed triggered rules"},
        )
    )

    assert verify_hash_chain(events) is True


def test_audit_hash_chain_detects_tampering() -> None:
    events = [
        create_audit_event(
            events=[],
            actor_user_id="system",
            actor_role="system",
            event_type="case_created",
            entity_type="case",
            entity_id="CASE-4521",
            summary="Case created",
        )
    ]
    tampered = events[0].model_copy(update={"summary": "Changed after the fact"})

    assert verify_hash_chain([tampered]) is False

