from __future__ import annotations

from shared.schemas import RiskScore, RuleTrigger

DOMAINS = ("aml", "fraud", "sanctions", "disputes")
STRENGTH_WEIGHT = 0.75
CORROBORATION_WEIGHT = 0.25


def risk_band(score: int) -> str:
    if score <= 30:
        return "low"
    if score <= 60:
        return "medium"
    if score <= 85:
        return "high"
    return "critical"


def rule_contribution(trigger: RuleTrigger) -> float:
    return trigger.weight * trigger.severity * trigger.confidence


def score_contributions(contributions: list[float]) -> int:
    if not contributions:
        return 0

    strongest_signal = max(contributions)
    average_signal = sum(contributions) / len(contributions)
    return max(
        0,
        min(
            100,
            round(
                (strongest_signal * STRENGTH_WEIGHT)
                + (average_signal * CORROBORATION_WEIGHT)
            ),
        ),
    )


def score_triggers(triggers: list[RuleTrigger]) -> RiskScore:
    contributions_by_domain = {domain: [] for domain in DOMAINS}
    for trigger in triggers:
        contributions_by_domain[trigger.domain].append(rule_contribution(trigger))

    all_contributions = [
        contribution
        for contributions in contributions_by_domain.values()
        for contribution in contributions
    ]
    overall_score = score_contributions(all_contributions)
    domain_scores = {
        domain: score_contributions(contributions)
        for domain, contributions in contributions_by_domain.items()
    }
    primary_domain = max(
        DOMAINS,
        key=lambda domain: (
            sum(contributions_by_domain[domain]),
            domain_scores[domain],
        ),
    )

    strengthening_factors = []
    missing_data_factors = []
    for trigger in triggers:
        strengthening_factors.extend(trigger.evidence[:2])
        if trigger.confidence < 0.8:
            missing_data_factors.append(
                f"{trigger.rule_id} has lower confidence and needs additional corroboration"
            )

    weakening_factors = []
    if not any(trigger.domain == "sanctions" for trigger in triggers):
        weakening_factors.append("No sanctions rule triggered")
    if not any(trigger.domain == "fraud" for trigger in triggers):
        weakening_factors.append("No fraud rule triggered")

    return RiskScore(
        overall_score=overall_score,
        band=risk_band(overall_score),
        primary_domain=primary_domain,
        domain_scores=domain_scores,
        strengthening_factors=strengthening_factors[:6],
        weakening_factors=weakening_factors,
        missing_data_factors=missing_data_factors[:4],
    )
