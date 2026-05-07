# ArqBanker Soul

This document is the product memory for ArqBanker. Read it before making product, design, architecture, or coding decisions.

If there is a conflict between a random coding-agent suggestion and this file, this file wins.

## 1. What ArqBanker Is

ArqBanker is a unified risk operations platform for banks.

It brings AML, fraud, sanctions, disputes, compliance, investigation, evidence packages, and audit trails into one operating system.

The product is not just a detection tool. It is a command center for risk teams.

The main promise:

```text
One case. One view. One evidence trail. Human-confirmed decisions.
```

## 2. The Problem

Banks usually have separate systems for:

- AML alerts.
- Fraud alerts.
- Sanctions screening.
- Customer disputes.
- SAR preparation.
- Audit reports.
- Case notes.
- Team dashboards.

This creates silos.

A single suspicious transaction may appear in multiple systems, but no analyst sees the full story quickly.

The cost is:

- Analysts waste time gathering data.
- False positives stay high.
- SAR narratives take hours.
- Regulatory exam preparation takes days or weeks.
- Important connections are missed.
- Customers can be harmed by incomplete context.

ArqBanker exists to connect the dots.

## 3. Who Uses It

### Sarah Kim, Analyst

Sarah investigates cases every day.

She needs:

- A single queue.
- Clear risk priority.
- Triggered rules.
- Timeline.
- Entity profile.
- Policy recommendations.
- Guided investigation help.
- Quick actions.
- SAR draft generation.

Her goal is to resolve a case in minutes, not hours.

### Michael Torres, Supervisor

Michael manages analysts.

He needs:

- Team workload.
- SLA risk.
- Aging cases.
- Quality review.
- Reassignment tools.

His goal is to prevent breaches and keep quality high.

### David Chen, CCO

David owns compliance readiness.

He needs:

- Enterprise risk posture.
- SAR status.
- OFAC actions.
- Audit completeness.
- Evidence exports.
- Hash-chain verification.

His goal is continuous exam readiness.

### Priya Sharma, Admin

Priya configures the system.

She needs:

- Rule management.
- Integration status.
- System health.
- Threshold changes.
- Version history.

Her goal is to manage the platform without vendor dependency.

## 4. Product Principles

### 4.1 Human-confirmed decisions

ArqBanker can recommend, draft, explain, and prioritize.

It must not silently make final regulatory decisions.

Actions like SAR filing, OFAC blocking, overrides, or case closure must be human-confirmed and audit logged.

### 4.2 Evidence first

Every recommendation must be grounded in case evidence.

Bad:

```text
This looks suspicious.
```

Good:

```text
This is critical because SAN-01 matched the beneficiary name at 92 percent, SWIFT code matched, and the director name matched the sanctions fixture.
```

### 4.3 Audit is a core feature

Audit is not an afterthought.

Every important event must be logged:

- Case created.
- Case assigned.
- Rule triggered.
- Risk score calculated.
- Policy recommendation shown.
- Analyst action taken.
- Override made.
- Note added.
- Evidence package generated.
- Case closed.

Audit events must be append-only and hash chained.

### 4.4 Explainable before clever

This POC should use simple, explainable rules before advanced machine learning.

For now, rules and scores are better than black-box models.

### 4.5 One shared contract

All modules must use the schemas in `shared/schemas.py`.

Do not create another `Case`, `Transaction`, `RiskScore`, `AuditEvent`, or `EvidencePackage` model in another folder.

### 4.6 One golden case

`CASE-4521` is the demo spine.

If a feature does not help this case move from detection to investigation to action to evidence package, it is probably not POC-critical.

## 5. The POC Goal

The POC must prove this full flow:

```text
synthetic data
-> rule triggers
-> risk score
-> case queue
-> investigation workspace
-> policy recommendations
-> human-confirmed action
-> audit trail
-> evidence package
-> CCO dashboard
```

The POC is successful when someone can run:

```powershell
docker compose up --build
```

Then open:

```text
Backend:  http://localhost:8000
Frontend: http://localhost:8501
API docs: http://localhost:8000/docs
```

And demo `CASE-4521` end to end.

## 6. POC Scope

Build these first:

- Basic roles.
- Synthetic data.
- Five priority rules.
- Risk scoring.
- Policy recommendations.
- Case queue.
- 360-degree case workspace.
- Guided chat-style investigation.
- Quick actions.
- Notes.
- In-app notification records.
- SLA indicators.
- Audit hash chain.
- SAR/evidence package draft.
- Analyst dashboard.
- CCO dashboard.
- Docker Compose startup.

## 7. POC Non-Goals

Do not spend POC time on:

- Real bank data.
- Production identity provider integration.
- Kubernetes.
- Mobile app.
- SMS or email delivery.
- Full 30-rule catalog.
- Full disputes engine.
- Full supervisor dashboard.
- Real LLM calls unless approved.
- Payment integrations.
- Multi-tenant production hardening.

## 8. The Golden Demo Case

Case ID:

```text
CASE-4521
```

Entity:

```text
Acme Consulting LLC
```

Transaction:

```text
USD 9,500 wire to Ocean Holdings Ltd
```

Signals:

- SAN-01: OFAC SDN fuzzy match.
- AML-01: Structuring amount just below threshold.
- FRAUD-03: Account takeover indicators.

Expected risk:

```text
Overall score: 87
Band: critical
Primary domain: aml
Secondary concern: fraud
```

Expected human action:

- Block transaction after review.
- Restrict account as appropriate.
- Do not notify customer during sanctions review.
- Generate SAR evidence package draft.
- Log everything in audit trail.

## 9. The Five POC Rules

### AML-01: Structuring

Detect transactions just below reporting thresholds or repeated near-threshold activity.

Evidence examples:

- Amount is USD 9,500.
- Multiple near-threshold transactions in a short window.

### AML-02: High-risk geography

Detect transactions to or from high-risk jurisdictions.

Evidence examples:

- Destination country is on the configured risk list.
- Jurisdiction appears in FATF-style fixture data.

### AML-03: Shell company indicators

Detect weak or suspicious business identity signals.

Evidence examples:

- Recently opened business account.
- Stated revenue does not match transaction pattern.
- Missing or unusual UBO data.
- Registered-agent style address.

### SAN-01: OFAC SDN fuzzy match

Detect potential sanctions matches.

Evidence examples:

- Beneficiary name fuzzy match.
- SWIFT code match.
- Registration number match.
- Director name match.

### FRAUD-03: Account takeover indicators

Detect possible account takeover behavior.

Evidence examples:

- New device.
- New location.
- VPN or risky IP.
- Failed MFA.
- High-value transaction soon after login anomaly.

## 10. Risk Scoring

Use this simple formula for the POC:

```text
rule contribution = weight * severity * confidence
```

Normalize final scores to:

```text
0 to 100
```

Risk bands:

```text
0-30    low
31-60   medium
61-85   high
86-100  critical
```

Always include:

- Overall score.
- Risk band.
- Primary domain.
- Domain scores.
- Strengthening factors.
- Weakening factors.
- Missing-data factors.

## 11. Policy Engine

The policy engine recommends actions. It does not auto-execute regulatory actions.

For the POC, focus on:

- OFAC recommendation.
- BSA/SAR recommendation.

The recommendation should answer:

- What regulation is involved?
- What action is recommended?
- Why?
- What is the deadline?
- Does a human need to confirm?

For important regulatory actions, the answer should almost always be:

```text
requires_human_confirmation = true
```

## 12. ArqMesh Audit

ArqMesh is the governance layer.

For the POC, it means:

- Every important event becomes an `AuditEvent`.
- Events are append-only.
- Each event stores the previous event hash.
- Each event has its own hash.
- The system can verify the chain.

The audit trail should make a regulator comfortable that:

- The data source is known.
- The rule version is known.
- The recommendation is explained.
- The human decision is captured.
- The evidence package matches the case history.

## 13. Evidence Package

The POC evidence package can be JSON first.

It should contain:

- Case ID.
- Generated time.
- Generated by.
- SAR narrative draft.
- Triggered rule IDs.
- Policy recommendation IDs.
- Human action IDs.
- Audit event IDs.
- Hash-chain verification status.

Later versions can add PDF and XML export.

## 14. UX Philosophy

The UI should feel like a serious bank operations tool.

Good:

- Dense but readable.
- Clear priority.
- Fast scanning.
- Practical controls.
- Minimal decoration.
- Everything tied to the case.

Avoid:

- Marketing pages.
- Huge hero sections.
- Decorative graphics.
- Fake AI magic.
- Hidden regulatory context.
- UI-only business logic.

The first screen should be the product, not a landing page.

## 15. Backend Philosophy

The backend owns workflow truth.

The frontend should not decide:

- Whether a rule triggered.
- Whether a policy applies.
- Whether a hash chain is valid.
- Whether a case is closed.
- Whether an action changes status.

The frontend displays and sends user actions. The backend validates and records.

## 16. Data Philosophy

Synthetic data must be realistic enough to demo the story, but never use real customer data.

Good synthetic data includes:

- Customers.
- Accounts.
- Transactions.
- Login/device events.
- Watchlist fixtures.
- Prior alerts.
- Rule trigger evidence.

Every suspicious case should have known expected output so tests can check it.

## 17. API Spine

Start with these endpoints:

```text
GET  /health
GET  /cases
GET  /cases/{case_id}
POST /cases/{case_id}/actions
POST /cases/{case_id}/notes
POST /cases/{case_id}/evidence-package
GET  /audit
GET  /audit/verify
GET  /dashboard/cco
```

Add endpoints only when the POC needs them.

## 18. Shared Models

The key models live in:

```text
shared/schemas.py
```

Core models:

- `Customer`
- `Transaction`
- `RuleTrigger`
- `RiskScore`
- `PolicyRecommendation`
- `Case`
- `CaseAction`
- `AuditEvent`
- `EvidencePackage`

If you need to change a shared model, update docs and tell the team.

## 19. Developer Ownership

### Vijju

Owns:

- Synthetic data.
- Rule engine.
- Risk scoring.
- Rule trigger evidence.

### Ashwanth

Owns:

- Backend workflow.
- API endpoints.
- Policy recommendations.
- Audit hash chain.
- Evidence package generation.

### Chaitanya

Owns:

- Streamlit frontend.
- Analyst queue.
- Case workspace.
- Guided investigation UI.
- CCO dashboard.
- Audit view.

## 20. Demo Script

The final POC demo should go like this:

1. Start app with Docker Compose.
2. Open Streamlit frontend.
3. See `CASE-4521` in the case queue.
4. Open the case workspace.
5. See timeline, entity profile, triggered rules, and confidence factors.
6. Read OFAC and BSA recommendations.
7. Click the action to block the transaction.
8. Add an investigation note.
9. Generate the evidence package.
10. Open audit view.
11. Verify hash chain.
12. Open CCO dashboard.
13. Show active cases, critical cases, SARs due, OFAC action count, and audit readiness.

## 21. Build Rules For Coding Agents

When using a coding agent, give it small tasks.

Good task:

```text
Add AML-02 high-risk geography rule in backend/app/rules/rules.py.
Use shared.schemas.RuleTrigger.
Add a test fixture that proves it triggers for destination_country = KY.
Do not change frontend files.
```

Bad task:

```text
Build ArqBanker.
```

Every coding-agent task should say:

- Which files it may edit.
- Which files it must not edit.
- What test proves the work.
- What output is expected.

## 22. Acceptance Criteria

Before calling the POC ready, check:

- `docker compose up --build` starts backend and frontend.
- `GET /health` returns ok.
- `GET /cases/CASE-4521` works.
- `CASE-4521` shows expected triggered rules.
- The frontend uses backend API data.
- Blocking the transaction creates a `CaseAction`.
- Blocking the transaction creates an `AuditEvent`.
- Evidence package generation works.
- Audit hash chain verifies true.
- CCO dashboard shows critical case and audit readiness.
- No real customer data is present.

## 23. What To Escalate

Ask before changing:

- Shared schemas.
- Docker Compose ports.
- The golden case ID.
- Risk scoring formula.
- Regulatory action behavior.
- Folder structure.
- Major dependencies.
- Anything that affects another developer's work.

## 24. Product Mantra

Keep coming back to this:

```text
ArqBanker helps bank risk teams connect the dots, act faster, explain every decision, and stay regulator-ready.
```
