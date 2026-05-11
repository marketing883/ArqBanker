from __future__ import annotations

import json
from pathlib import Path

from backend.app.rules.engine import build_case_from_synthetic_input, evaluate_transaction, load_watchlist
from backend.app.rules.rules import (
    aml_01_structuring,
    aml_02_high_risk_geography,
    aml_03_shell_company_indicators,
    fraud_03_account_takeover,
    san_01_ofac_sdn_fuzzy_match,
)
from shared.schemas import Case, Customer, Transaction


def load_golden_case() -> Case:
    raw = json.loads(Path("data/golden_case_4521.json").read_text(encoding="utf-8"))
    return Case(**raw)


def test_aml_01_triggers_for_9500_wire() -> None:
    case = load_golden_case()
    trigger = aml_01_structuring(case.transactions[0])

    assert trigger is not None
    assert trigger.rule_id == "AML-01"
    assert "USD 10,000" in trigger.evidence[0]


def test_aml_02_triggers_for_destination_ky() -> None:
    case = load_golden_case()
    trigger = aml_02_high_risk_geography(case.transactions[0])

    assert trigger is not None
    assert trigger.rule_id == "AML-02"
    assert "KY" in trigger.evidence[0]


def test_aml_03_triggers_for_young_low_revenue_business() -> None:
    case = load_golden_case()
    trigger = aml_03_shell_company_indicators(case.customer, case.transactions[0])

    assert trigger is not None
    assert trigger.rule_id == "AML-03"
    assert len(trigger.evidence) >= 2


def test_san_01_triggers_for_ocean_holdings() -> None:
    case = load_golden_case()
    trigger = san_01_ofac_sdn_fuzzy_match(case.transactions[0], load_watchlist())

    assert trigger is not None
    assert trigger.rule_id == "SAN-01"
    assert any("Ocean Holdings" in evidence for evidence in trigger.evidence)


def test_fraud_03_triggers_for_new_device_high_value_wire() -> None:
    case = load_golden_case()
    trigger = fraud_03_account_takeover(case.transactions[0])

    assert trigger is not None
    assert trigger.rule_id == "FRAUD-03"


def test_evaluate_transaction_returns_expected_golden_rules() -> None:
    case = load_golden_case()
    triggers = evaluate_transaction(case.customer, case.transactions[0], related_transactions=case.transactions)
    rule_ids = {trigger.rule_id for trigger in triggers}

    assert rule_ids >= {"AML-01", "AML-02", "AML-03", "SAN-01", "FRAUD-03"}


def test_build_case_from_synthetic_input_generates_rules_for_case_1234() -> None:
    raw = json.loads(Path("data/synthetic_case_1234.json").read_text(encoding="utf-8"))
    case = build_case_from_synthetic_input(raw)
    rule_ids = {trigger.rule_id for trigger in case.triggered_rules}

    assert case.case_id == "CASE-1234"
    assert rule_ids >= {"AML-01", "AML-02", "AML-03", "SAN-01", "FRAUD-03"}
    assert case.risk_score.overall_score > 0

