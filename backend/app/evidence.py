from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from backend.app.audit import create_audit_event, verify_hash_chain
from shared.schemas import AuditEvent, Case, EvidencePackage


def build_sar_narrative(case: Case) -> str:
    transaction = case.transactions[0] if case.transactions else None
    amount = f"USD {transaction.amount_usd:,.0f}" if transaction else "the reviewed amount"
    beneficiary = transaction.beneficiary_name if transaction and transaction.beneficiary_name else "the beneficiary"
    rule_ids = ", ".join(rule.rule_id for rule in case.triggered_rules)
    return (
        f"{case.customer.entity_name} initiated a {amount} wire to {beneficiary}. "
        f"The case triggered {rule_ids}. Human review is required before filing or external reporting."
    )


def generate_evidence_package(
    case: Case,
    audit_events: list[AuditEvent],
    *,
    generated_by: str,
    actor_role: str = "analyst_l2",
) -> EvidencePackage:
    package_id = f"EVP-{uuid4().hex[:10]}"

    audit_events.append(
        create_audit_event(
            events=audit_events,
            actor_user_id=generated_by,
            actor_role=actor_role,
            event_type="evidence_package_generated",
            entity_type="case",
            entity_id=case.case_id,
            summary=f"Evidence package {package_id} generated",
            payload={"package_id": package_id},
        )
    )

    case.status = "pending_filing"
    case.updated_at = datetime.now(UTC)

    case_audit_event_ids = [
        event.event_id
        for event in audit_events
        if event.entity_type == "case" and event.entity_id == case.case_id
    ]
    return EvidencePackage(
        package_id=package_id,
        case_id=case.case_id,
        generated_at=datetime.now(UTC),
        generated_by=generated_by,
        sar_narrative=build_sar_narrative(case),
        triggered_rule_ids=[rule.rule_id for rule in case.triggered_rules],
        policy_recommendation_ids=[policy.policy_id for policy in case.policy_recommendations],
        action_ids=[action.action_id for action in case.actions],
        audit_event_ids=case_audit_event_ids,
        hash_chain_verified=verify_hash_chain(audit_events),
    )

