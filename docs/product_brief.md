# Product Brief

ArqBanker is a unified risk operations command center for banks. It connects AML, fraud, sanctions, disputes, and regulatory workflows that normally live in separate systems.

The POC should focus on proving the operating model, not building every future feature. The strongest demo is one high-risk case moving from detection to investigation to human-confirmed action to evidence package generation with a verifiable audit trail.

## Core POC Modules

- Basic auth and role concepts.
- Synthetic data ingestion.
- Five priority rules:
  - AML-01: Structuring.
  - AML-02: High-risk geography.
  - AML-03: Shell company indicators.
  - SAN-01: OFAC SDN fuzzy match.
  - FRAUD-03: Account takeover indicators.
- Risk scoring on a 0-100 scale.
- Policy recommendations for OFAC and BSA/SAR obligations.
- Analyst case queue.
- 360-degree investigation workspace.
- Guided chat-style investigation flow.
- Resolution paths for auto-resolve, investigate-and-act, and SLA/no-response escalation.
- In-app notification records and SLA timers.
- ArqMesh-style append-only audit trail with hash chaining.
- SAR/evidence package draft generation.
- Analyst and CCO dashboards.

## POC Non-Goals

- Real bank data integration.
- Full 30-rule production library.
- Production-grade identity provider integration.
- Full Reg E/Z disputes module.
- Kubernetes deployment.
- Mobile approvals.
- SMS/email/Teams delivery.
- Full LLM integration unless explicitly approved.

## Golden Demo Case

`CASE-4521` is the common case every module must support:

- Entity: Acme Consulting LLC.
- Transaction: USD 9,500 wire to Ocean Holdings Ltd.
- Signals: OFAC fuzzy match, structuring amount, account takeover indicators.
- Risk score: 87 critical.
- Analyst: Sarah Kim.
- Intended resolution: block wire, restrict account, prepare SAR draft and OFAC report, record all actions in audit trail.
