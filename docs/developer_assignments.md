# Developer Assignments

Each developer can use coding agents in their own local branch, but all work must converge through this repo.

## Developer 1: Data, Rules, Risk Scoring

Owns the risk brain.

Build:

- Synthetic customer and transaction generator.
- Golden data fixtures, including `CASE-4521`.
- Rule execution service.
- Five POC rules:
  - `AML-01`
  - `AML-02`
  - `AML-03`
  - `SAN-01`
  - `FRAUD-03`
- Risk scoring formula.
- Confidence breakdown with strengthening, weakening, and missing-data factors.

Must output:

- `RuleTrigger`
- `RiskScore`
- `Case`

Do not build UI screens. Do not invent new schemas.

## Developer 2: Backend Workflow, Governance, Evidence

Owns the operating system.

Build:

- FastAPI case endpoints.
- Case status transitions.
- Case action handling.
- Notes.
- Policy recommendations for OFAC and BSA.
- Append-only audit event storage.
- Hash-chain verification.
- Evidence package generation.
- SAR draft payload.
- SLA timer and notification records.

Must consume:

- `Case`
- `CaseAction`
- `AuditEvent`
- `EvidencePackage`

Do not build the rule engine. Do not build the UI except minimal API docs.

## Developer 3: Frontend Experience

Owns the demo surface.

Build:

- Streamlit analyst case queue.
- 360-degree case workspace.
- Triggered rules panel.
- Timeline.
- Entity profile.
- Confidence breakdown.
- Policy recommendations.
- Guided chat-style investigation flow.
- Quick actions.
- Notes panel.
- CCO dashboard.
- Evidence package export button.
- Hash-chain verification indicator.

Must consume the backend API. Temporary mock data is allowed for very short work, but final PRs must use API responses.

Do not duplicate backend business logic in the UI.

## Daily Integration Rule

Every day:

1. Pull latest `main`.
2. Merge `main` into your branch.
3. Run tests.
4. Open or update a pull request.
5. Mention which shared contracts you touched.

## Pull Request Checklist

- Uses `shared/schemas.py`.
- Supports `CASE-4521`.
- Has focused tests where useful.
- Does not silently change another developer's contract.
- Updates docs if endpoints or schemas changed.
- Can still start with Docker Compose.
