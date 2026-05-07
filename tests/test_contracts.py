import json
from pathlib import Path

from shared.constants import GOLDEN_CASE_ID
from shared.schemas import Case


def test_golden_case_matches_shared_contract() -> None:
    raw = json.loads(Path("data/golden_case_4521.json").read_text(encoding="utf-8"))
    case = Case(**raw)

    assert case.case_id == GOLDEN_CASE_ID
    assert case.risk_score.band == "critical"
    assert {rule.rule_id for rule in case.triggered_rules} >= {"SAN-01", "AML-01", "FRAUD-03"}
    assert case.policy_recommendations
