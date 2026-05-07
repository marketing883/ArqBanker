from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


RiskDomain = Literal["aml", "fraud", "sanctions", "disputes"]
RiskBand = Literal["low", "medium", "high", "critical"]
CaseStatus = Literal[
    "new",
    "assigned",
    "investigating",
    "pending_filing",
    "resolved",
    "escalated",
    "auto_resolved",
    "closed",
]
ResolutionPath = Literal["auto_resolve", "investigate_and_act", "sla_no_response"]


class Customer(BaseModel):
    customer_id: str
    entity_name: str
    entity_type: Literal["individual", "business"]
    account_id: str
    account_opened_at: datetime
    kyc_status: str
    stated_industry: str | None = None
    stated_annual_revenue_usd: float | None = None
    risk_rating: str | None = None
    prior_alert_count: int = 0
    prior_sar_count: int = 0


class Transaction(BaseModel):
    transaction_id: str
    customer_id: str
    account_id: str
    transaction_type: str
    amount_usd: float
    currency: str = "USD"
    timestamp: datetime
    origin_country: str
    destination_country: str
    beneficiary_name: str | None = None
    beneficiary_bank: str | None = None
    beneficiary_swift: str | None = None
    device_id: str | None = None
    ip_address: str | None = None
    channel: str | None = None


class RuleTrigger(BaseModel):
    rule_id: str
    domain: RiskDomain
    rule_name: str
    description: str
    severity: float = Field(ge=0, le=10)
    weight: float = Field(ge=0, le=10)
    confidence: float = Field(ge=0, le=1)
    evidence: list[str] = Field(default_factory=list)
    regulatory_references: list[str] = Field(default_factory=list)


class RiskScore(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    band: RiskBand
    primary_domain: RiskDomain
    domain_scores: dict[RiskDomain, int]
    strengthening_factors: list[str] = Field(default_factory=list)
    weakening_factors: list[str] = Field(default_factory=list)
    missing_data_factors: list[str] = Field(default_factory=list)


class PolicyRecommendation(BaseModel):
    policy_id: str
    regulation: str
    title: str
    recommendation: str
    severity: Literal["info", "warning", "critical"]
    requires_human_confirmation: bool = True
    due_at: datetime | None = None
    acknowledged: bool = False


class CaseAction(BaseModel):
    action_id: str
    action_type: str
    actor_user_id: str
    actor_role: str
    created_at: datetime
    summary: str
    details: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
    human_confirmed: bool = True


class Case(BaseModel):
    case_id: str
    status: CaseStatus
    assigned_to: str | None = None
    customer: Customer
    transactions: list[Transaction]
    triggered_rules: list[RuleTrigger]
    risk_score: RiskScore
    policy_recommendations: list[PolicyRecommendation]
    resolution_path: ResolutionPath
    timeline: list[str] = Field(default_factory=list)
    related_case_ids: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
    actions: list[CaseAction] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class AuditEvent(BaseModel):
    event_id: str
    sequence: int
    created_at: datetime
    actor_user_id: str
    actor_role: str
    event_type: str
    entity_type: str
    entity_id: str
    summary: str
    payload: dict[str, str | int | float | bool | None] = Field(default_factory=dict)
    previous_hash: str
    event_hash: str


class EvidencePackage(BaseModel):
    package_id: str
    case_id: str
    generated_at: datetime
    generated_by: str
    sar_narrative: str
    triggered_rule_ids: list[str]
    policy_recommendation_ids: list[str]
    action_ids: list[str]
    audit_event_ids: list[str]
    hash_chain_verified: bool
    export_formats: list[Literal["json", "pdf", "xml"]] = Field(default_factory=lambda: ["json"])
