from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from uuid import uuid4

from shared.schemas import AuditEvent

GENESIS_HASH = "0" * 64


def canonicalize(value):
    if isinstance(value, datetime):
        return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
    if isinstance(value, str) and value.endswith("+00:00"):
        return f"{value[:-6]}Z"
    if isinstance(value, dict):
        return {key: canonicalize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [canonicalize(item) for item in value]
    return value


def compute_event_hash(event_body: dict) -> str:
    encoded = json.dumps(canonicalize(event_body), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def create_audit_event(
    *,
    events: list[AuditEvent],
    actor_user_id: str,
    actor_role: str,
    event_type: str,
    entity_type: str,
    entity_id: str,
    summary: str,
    payload: dict[str, str | int | float | bool | None] | None = None,
) -> AuditEvent:
    sequence = len(events) + 1
    previous_hash = events[-1].event_hash if events else GENESIS_HASH
    body = {
        "event_id": f"AUD-{uuid4().hex[:12]}",
        "sequence": sequence,
        "created_at": datetime.now(UTC),
        "actor_user_id": actor_user_id,
        "actor_role": actor_role,
        "event_type": event_type,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "summary": summary,
        "payload": payload or {},
        "previous_hash": previous_hash,
    }
    body["event_hash"] = compute_event_hash(body)
    return AuditEvent(**body)


def verify_hash_chain(events: list[AuditEvent]) -> bool:
    previous_hash = GENESIS_HASH
    for event in events:
        if event.previous_hash != previous_hash:
            return False
        body = event.model_dump(mode="json")
        event_hash = body.pop("event_hash")
        if compute_event_hash(body) != event_hash:
            return False
        previous_hash = event_hash
    return True
