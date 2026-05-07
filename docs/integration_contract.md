# Integration Contract

This file defines the shared contract between the three workstreams.

## Data Flow

```text
Synthetic data -> rules/scoring -> Case -> backend workflow -> frontend
                                 -> audit trail -> evidence package
```

## Shared Objects

All modules must import these objects from `shared/schemas.py`:

- `Customer`
- `Transaction`
- `RuleTrigger`
- `RiskScore`
- `Case`
- `CaseAction`
- `AuditEvent`
- `EvidencePackage`

## API Contract

Initial backend endpoints:

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

## Case Statuses

Use these exact status values:

```text
new
assigned
investigating
pending_filing
resolved
escalated
auto_resolved
closed
```

## Domains

Use these exact domain values:

```text
aml
fraud
sanctions
disputes
```

## Risk Bands

```text
0-30    low
31-60   medium
61-85   high
86-100  critical
```

## Golden Case Requirement

Every module must support `CASE-4521`. This case is the integration test for the POC.
