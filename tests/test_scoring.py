from __future__ import annotations

import json
from pathlib import Path

from backend.app.rules.engine import evaluate_transaction
from backend.app.rules.scoring import risk_band, score_triggers
from shared.schemas import Case


def load_golden_case() -> Case:
    raw = json.loads(Path("data/golden_case_4521.json").read_text(encoding="utf-8"))
    return Case(**raw)


def test_risk_band_thresholds() -> None:
    assert risk_band(30) == "low"
    assert risk_band(31) == "medium"
    assert risk_band(61) == "high"
    assert risk_band(86) == "critical"


def test_case_4521_scoring_remains_critical() -> None:
    case = load_golden_case()
    triggers = evaluate_transaction(case.customer, case.transactions[0], related_transactions=case.transactions)
    score = score_triggers(triggers)

    assert score.overall_score >= 86
    assert score.band == "critical"
    assert score.primary_domain in {"aml", "sanctions"}
    assert score.domain_scores["aml"] > 0
    assert score.domain_scores["sanctions"] > 0
    assert score.domain_scores["fraud"] > 0

