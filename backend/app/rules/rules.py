from __future__ import annotations

from datetime import UTC, datetime
from difflib import SequenceMatcher

from shared.schemas import Customer, RuleTrigger, Transaction

HIGH_RISK_COUNTRIES = {"KY", "PA", "AE", "RU"}
NEW_DEVICE_MARKERS = ("new", "unknown", "unrecognized")
RISKY_IP_PREFIXES = ("185.", "187.", "45.", "103.")


def aml_01_structuring(transaction: Transaction, related_transactions: list[Transaction] | None = None) -> RuleTrigger | None:
    related_transactions = related_transactions or [transaction]
    near_threshold = [txn for txn in related_transactions if 9000 <= txn.amount_usd <= 9999]
    if not near_threshold:
        return None

    evidence = [f"Transaction amount is near USD 10,000 threshold: USD {transaction.amount_usd:,.0f}"]
    if len(near_threshold) > 1:
        evidence.append(f"{len(near_threshold)} near-threshold wires found in the case window")

    return RuleTrigger(
        rule_id="AML-01",
        domain="aml",
        rule_name="Structuring Detection",
        description="Transaction behavior sits just below reporting thresholds.",
        severity=8,
        weight=9,
        confidence=0.86 if len(near_threshold) > 1 else 0.81,
        evidence=evidence,
        regulatory_references=["31 CFR 1020.320"],
    )


def aml_02_high_risk_geography(transaction: Transaction) -> RuleTrigger | None:
    countries = {transaction.origin_country, transaction.destination_country}
    matched = sorted(countries & HIGH_RISK_COUNTRIES)
    if not matched:
        return None

    return RuleTrigger(
        rule_id="AML-02",
        domain="aml",
        rule_name="High-Risk Geography",
        description="Transaction touches a jurisdiction configured for enhanced review.",
        severity=7,
        weight=8,
        confidence=0.78,
        evidence=[f"Origin or destination country is in high-risk list: {', '.join(matched)}"],
        regulatory_references=["31 CFR 1020.210"],
    )


def aml_03_shell_company_indicators(customer: Customer, transaction: Transaction, context: dict | None = None) -> RuleTrigger | None:
    context = context or {}
    now = transaction.timestamp.astimezone(UTC)
    account_age_days = (now - customer.account_opened_at.astimezone(UTC)).days
    revenue = customer.stated_annual_revenue_usd or 0
    amount_to_revenue = revenue > 0 and transaction.amount_usd > revenue * 0.05

    signals: list[str] = []
    if customer.entity_type == "business":
        signals.append("Customer is a business entity")
    if account_age_days < 180:
        signals.append(f"Account age is {account_age_days} days, below 180-day review threshold")
    if revenue and revenue < 250000:
        signals.append(f"Stated annual revenue is below USD 250,000: USD {revenue:,.0f}")
    if amount_to_revenue:
        signals.append("Transaction amount is greater than 5 percent of stated annual revenue")

    business_profile = context.get("business_profile") or {}
    ubo = context.get("ubo") or {}
    if business_profile.get("registered_address_type") == "virtual_office":
        signals.append("Business uses a virtual-office style registered address")
    if ubo and not ubo.get("verified", True):
        signals.append("UBO verification is incomplete")

    if len(signals) < 2:
        return None

    return RuleTrigger(
        rule_id="AML-03",
        domain="aml",
        rule_name="Shell Company Indicators",
        description="Business account has multiple profile signals requiring enhanced review.",
        severity=7,
        weight=8,
        confidence=min(0.9, 0.58 + len(signals) * 0.06),
        evidence=signals,
        regulatory_references=["31 CFR 1010.610"],
    )


def san_01_ofac_sdn_fuzzy_match(transaction: Transaction, watchlist: list[dict]) -> RuleTrigger | None:
    if not transaction.beneficiary_name:
        return None

    best_match = None
    best_score = 0.0
    evidence: list[str] = []

    for candidate in watchlist:
        listed_name = candidate.get("listed_name") or candidate.get("name") or candidate.get("entity_name") or ""
        name_score = SequenceMatcher(None, transaction.beneficiary_name.lower(), listed_name.lower()).ratio()
        candidate_evidence = []
        if name_score >= 0.82:
            candidate_evidence.append(
                f"Beneficiary name fuzzy match {name_score:.0%}: {transaction.beneficiary_name} vs {listed_name}"
            )
        candidate_swift = candidate.get("beneficiary_swift") or candidate.get("swift")
        if transaction.beneficiary_swift and transaction.beneficiary_swift == candidate_swift:
            candidate_evidence.append(f"SWIFT {transaction.beneficiary_swift} matches watchlist fixture")

        director_name = candidate.get("director_name") or candidate.get("director")
        if director_name and candidate_evidence:
            candidate_evidence.append(f"Director {director_name} appears in watchlist fixture")

        registration_number = candidate.get("registration_number") or candidate.get("registration")
        if registration_number and candidate_evidence:
            candidate_evidence.append(
                f"Registration number {registration_number} appears in watchlist fixture"
            )

        score = name_score + (0.08 if len(candidate_evidence) > 1 else 0)
        if candidate_evidence and score > best_score:
            best_score = score
            best_match = candidate
            evidence = candidate_evidence

    if not best_match:
        return None

    confidence = min(0.96, max(0.82, best_score))
    return RuleTrigger(
        rule_id="SAN-01",
        domain="sanctions",
        rule_name="OFAC SDN Fuzzy Match",
        description="Beneficiary has a potential sanctions fixture match requiring human review.",
        severity=10,
        weight=10,
        confidence=confidence,
        evidence=evidence,
        regulatory_references=[best_match.get("regulatory_reference", "31 CFR 501.603")],
    )


def fraud_03_account_takeover(transaction: Transaction, login_events: list[dict] | None = None) -> RuleTrigger | None:
    login_events = login_events or []
    device = (transaction.device_id or "").lower()
    ip_address = transaction.ip_address or ""
    device_looks_new = any(marker in device for marker in NEW_DEVICE_MARKERS)
    ip_looks_risky = ip_address.startswith(RISKY_IP_PREFIXES)
    failed_mfa = False
    vpn_or_tor = False

    for event in login_events:
        if event.get("device_id") == transaction.device_id:
            device_looks_new = device_looks_new or event.get("device_seen_before") is False
            ip_looks_risky = ip_looks_risky or event.get("ip_risk") == "high"
            failed_mfa = failed_mfa or event.get("mfa_result") == "failed"
            vpn_or_tor = vpn_or_tor or bool(event.get("vpn_or_tor"))

    if not (device_looks_new and ip_looks_risky and transaction.amount_usd > 5000):
        return None

    evidence = [
        "Device looks new or unknown for the customer",
        "IP address looks risky or different from normal behavior",
        f"Transaction amount is greater than USD 5,000: USD {transaction.amount_usd:,.0f}",
    ]
    if failed_mfa:
        evidence.append("Failed MFA attempt appears before or near the transaction")
    if vpn_or_tor:
        evidence.append("VPN or Tor indicator is present in login fixture")

    return RuleTrigger(
        rule_id="FRAUD-03",
        domain="fraud",
        rule_name="Account Takeover Indicators",
        description="New device, risky IP behavior, and high-value transaction suggest possible account takeover.",
        severity=7,
        weight=8,
        confidence=0.82 if failed_mfa or vpn_or_tor else 0.74,
        evidence=evidence,
        regulatory_references=[],
    )
