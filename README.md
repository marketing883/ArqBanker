# ArqBanker POC

This is the single convergence repo for the ArqBanker proof of concept.

ArqBanker is a unified banking risk operations platform that brings AML, fraud, sanctions, disputes, case workflow, policy recommendations, evidence packages, and auditability into one workspace.

## POC Goal

The first demo must prove one end-to-end workflow:

1. Load synthetic customer and transaction data.
2. Trigger priority AML, sanctions, and fraud rules.
3. Create a risk-scored case.
4. Let an analyst investigate the case in one workspace.
5. Show policy recommendations, not automatic regulatory decisions.
6. Let the analyst confirm actions.
7. Generate a SAR/evidence package draft.
8. Record every step in an append-only audit trail.
9. Verify the audit hash chain.
10. Show CCO-level readiness from a dashboard.

The canonical demo case is `CASE-4521`.

## Repo Layout

```text
SOUL.md               Product north star and end-to-end knowledge base
backend/              FastAPI API, workflow, audit, evidence packages
frontend/             Streamlit POC UI
shared/               Shared schemas and constants used by every module
data/                 Synthetic fixtures and the golden demo case
tests/                Contract and integration tests
docs/                 Product brief, assignments, and integration rules
docker-compose.yml    One-command local POC runner
```

## Developer Ownership

Developer 1 owns data, rules, and risk scoring.

Developer 2 owns backend workflow, policy recommendations, audit, and evidence packages.

Developer 3 owns the Streamlit analyst and CCO experience.

All developers must use the models in `shared/schemas.py`. Do not create separate versions of Case, Transaction, RiskScore, AuditEvent, or EvidencePackage.

Named starter assignments:

```text
docs/assignments/vijju.md
docs/assignments/ashwanth.md
docs/assignments/chaitanya.md
```

## Quick Start

From this folder:

```powershell
docker compose up --build
```

Expected local services:

```text
Backend API: http://localhost:8000
Frontend UI: http://localhost:8501
API docs:    http://localhost:8000/docs
```

## Branch Workflow

Each developer creates their own branch:

```powershell
git checkout -b dev1-rules-engine
git checkout -b dev2-case-workflow
git checkout -b dev3-frontend
```

Daily, each developer should sync with `main`:

```powershell
git checkout main
git pull
git checkout your-branch-name
git merge main
```

Open pull requests back into `main`. The reviewer checks:

- Uses shared schemas.
- Supports `CASE-4521`.
- Does not break Docker startup.
- Does not create a parallel product architecture.
- Includes focused tests for changed behavior.

## Definition Of Done

The POC is done when a clean checkout can run:

```powershell
docker compose up --build
```

Then the user can demo:

```text
open analyst dashboard -> accept CASE-4521 -> inspect triggered rules
-> follow guided investigation -> block transaction -> generate SAR package
-> verify audit hash chain -> view CCO dashboard
```
