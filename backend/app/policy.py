from __future__ import annotations

from datetime import UTC, datetime, timedelta

from shared.schemas import Case, PolicyRecommendation


def recommendations_for_case(case: Case) -> list[PolicyRecommendation]:
    if case.policy_recommendations:
        return case.policy_recommendations

    triggered_rule_ids = {rule.rule_id for rule in case.triggered_rules}
    generated: list[PolicyRecommendation] = []
    now = datetime.now(UTC)

    if "SAN-01" in triggered_rule_ids:
        generated.append(
            PolicyRecommendation(
                policy_id="POL-OFAC-001",
                regulation="OFAC",
                title="Potential SDN match requires immediate review",
                recommendation=(
                    "Block transaction and freeze assets if human reviewer confirms match. "
                    "Do not notify customer while sanctions review is active."
                ),
                severity="critical",
                requires_human_confirmation=True,
                due_at=now + timedelta(days=1),
            )
        )

    if {"AML-01", "AML-02", "AML-03"} & triggered_rule_ids:
        generated.append(
            PolicyRecommendation(
                policy_id="POL-BSA-001",
                regulation="BSA",
                title="SAR filing may be required",
                recommendation=(
                    "Prepare SAR draft within 30 calendar days with supporting evidence "
                    "and analyst decision history."
                ),
                severity="warning",
                requires_human_confirmation=True,
                due_at=now + timedelta(days=30),
            )
        )

    return generated


def ensure_policy_recommendations(case: Case) -> Case:
    case.policy_recommendations = recommendations_for_case(case)
    return case

