from __future__ import annotations

import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from backend.app.rules.rules import (
    aml_01_structuring,
    aml_02_high_risk_geography,
    aml_03_shell_company_indicators,
    fraud_03_account_takeover,
    san_01_ofac_sdn_fuzzy_match,
)
from backend.app.rules.scoring import score_triggers
from shared.schemas import Case, Customer, PolicyRecommendation, RuleTrigger, Transaction

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "data"
WATCHLIST_PATH = DATA_DIR / "watchlist_fixture.json"


def load_watchlist() -> list[dict]:
    return json.loads(WATCHLIST_PATH.read_text(encoding="utf-8"))


def evaluate_transaction(
    customer: Customer,
    transaction: Transaction,
    *,
    related_transactions: list[Transaction] | None = None,
    watchlist: list[dict] | None = None,
    context: dict | None = None,
) -> list[RuleTrigger]:
    context = context or {}
    watchlist = watchlist if watchlist is not None else load_watchlist()
    checks = [
        aml_01_structuring(transaction, related_transactions),
        aml_02_high_risk_geography(transaction),
        aml_03_shell_company_indicators(customer, transaction, context),
        san_01_ofac_sdn_fuzzy_match(transaction, watchlist),
        fraud_03_account_takeover(transaction, context.get("login_events", [])),
    ]
    return [trigger for trigger in checks if trigger is not None]


def dedupe_triggers(triggers: list[RuleTrigger]) -> list[RuleTrigger]:
    by_rule: dict[str, RuleTrigger] = {}
    for trigger in triggers:
        existing = by_rule.get(trigger.rule_id)
        if existing is None or trigger.confidence > existing.confidence:
            by_rule[trigger.rule_id] = trigger
        elif existing:
            merged_evidence = list(dict.fromkeys([*existing.evidence, *trigger.evidence]))
            by_rule[trigger.rule_id] = existing.model_copy(update={"evidence": merged_evidence})
    return list(by_rule.values())


def policy_recommendations_for_triggers(triggers: list[RuleTrigger], base_time: datetime) -> list[PolicyRecommendation]:
    rule_ids = {trigger.rule_id for trigger in triggers}
    recommendations: list[PolicyRecommendation] = []
    if "SAN-01" in rule_ids:
        recommendations.append(
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
                due_at=base_time + timedelta(days=1),
            )
        )
    if {"AML-01", "AML-02", "AML-03"} & rule_ids:
        recommendations.append(
            PolicyRecommendation(
                policy_id="POL-BSA-001",
                regulation="BSA",
                title="SAR filing may be required",
                recommendation="Prepare SAR draft if analyst confirms suspicious activity after review.",
                severity="warning",
                requires_human_confirmation=True,
                due_at=base_time + timedelta(days=30),
            )
        )
    return recommendations


def build_case_from_synthetic_input(raw: dict) -> Case:
    customer = Customer(**raw["customer"])
    transactions = [Transaction(**transaction) for transaction in raw["transactions"]]
    context = {
        "login_events": raw.get("login_events", []),
        "business_profile": raw.get("customer", {}).get("business_profile", {}),
        "ubo": raw.get("customer", {}).get("ubo", {}),
    }
    triggers = dedupe_triggers(
        [
            trigger
            for transaction in transactions
            for trigger in evaluate_transaction(
                customer,
                transaction,
                related_transactions=transactions,
                context=context,
            )
        ]
    )
    risk_score = score_triggers(triggers)
    created_at = datetime.now(UTC)
    return Case(
        case_id=raw["case_id"],
        status="new",
        assigned_to="sarah.kim",
        customer=customer,
        transactions=transactions,
        triggered_rules=triggers,
        risk_score=risk_score,
        policy_recommendations=policy_recommendations_for_triggers(triggers, created_at),
        resolution_path="investigate_and_act",
        timeline=[
            f"{customer.account_opened_at:%Y-%m-%d %H:%M} Account opened",
            *[
                f"{transaction.timestamp:%Y-%m-%d %H:%M} USD {transaction.amount_usd:,.0f} "
                f"{transaction.transaction_type} to {transaction.beneficiary_name}"
                for transaction in transactions
            ],
        ],
        related_case_ids=[],
        notes=[],
        actions=[],
        created_at=created_at,
        updated_at=created_at,
    )

