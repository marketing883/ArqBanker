# Chaitanya Assignment: Frontend Analyst and CCO Experience

Hi Chaitanya. Your job is to build the demo surface of the ArqBanker POC.

You are responsible for the Streamlit user interface that shows the case queue, investigation workspace, guided flow, CCO dashboard, and audit view.

## 1. Your Mission

Build this part of the flow:

```text
backend API -> analyst UI -> action buttons -> evidence package -> CCO dashboard
```

Your work should answer:

```text
Can a user understand the case quickly?
Can an analyst take action?
Can a CCO see that the case is audit-ready?
```

## 2. Read These Files First

Before coding, read these files in this order:

```text
README.md
SOUL.md
docs/integration_contract.md
frontend/app.py
shared/schemas.py
data/golden_case_4521.json
```

## 3. Create Your Branch

Run:

```powershell
git checkout main
git pull
git checkout -b chaitanya-frontend-workspace
```

Do all your work on this branch.

## 4. Files You Own

You should mainly work in:

```text
frontend/
tests/
```

You may create:

```text
frontend/components.py
frontend/api_client.py
frontend/formatters.py
frontend/pages.py
```

You may edit:

```text
frontend/app.py
frontend/requirements.txt
```

Do not build backend business logic in the frontend.

Do not create your own fake case model.

## 5. Important Rule

The frontend must use the backend API.

Good:

```text
GET /cases
GET /cases/CASE-4521
POST /cases/CASE-4521/actions
POST /cases/CASE-4521/notes
POST /cases/CASE-4521/evidence-package
GET /dashboard/cco
GET /audit/verify
```

Bad:

```text
Hard-coding a complete fake case inside frontend/app.py
```

Temporary mock data is okay for a few hours while building a screen, but final work must use the API.

## 6. Main Screens To Build

### Screen 1: Analyst Queue

Show a list of cases.

For each case, show:

- Case ID.
- Entity name.
- Risk score.
- Risk band.
- Primary domain.
- Status.
- Triggered rule IDs.
- Assigned analyst.

Make `CASE-4521` easy to find.

### Screen 2: Case Workspace

This is the most important screen.

For `CASE-4521`, show:

- Header with case ID and entity.
- Risk score.
- Status.
- Timeline.
- Entity profile.
- Triggered rules.
- Confidence factors.
- Policy recommendations.
- Notes.
- Quick actions.
- Evidence package section.

The user should understand the case in less than one minute.

### Screen 3: Guided Investigation

Build a simple guided flow.

It can be scripted for the POC.

Example:

```text
Step 1: Show critical sanctions finding.
Step 2: Show corroborating evidence.
Step 3: Show regulatory implications.
Step 4: Ask analyst to confirm action.
Step 5: Show next steps after action.
```

Use buttons for choices.

Do not call a real LLM unless approved.

### Screen 4: CCO Dashboard

Use:

```text
GET /dashboard/cco
```

Show:

- Active cases.
- Critical cases.
- SARs due.
- OFAC action required.
- Audit hash-chain status.
- False-positive-rate target.

Keep it simple and executive-readable.

### Screen 5: Audit View

Use:

```text
GET /audit
GET /audit/verify
```

Show:

- Event count.
- Hash-chain verified true or false.
- Audit event table.

## 7. Quick Actions To Add

Add buttons for:

```text
Accept Case
Block Transaction
Restrict Account
Send Secure Message
Add Note
Generate Evidence Package
Verify Audit Chain
```

When a button is clicked, call the backend.

Do not only change the UI state.

## 8. Visual Style

This is a bank operations tool.

Use a clean, serious, practical style.

Good:

- Clear headings.
- Compact cards.
- Tables where useful.
- Risk colors used carefully.
- Buttons with direct labels.
- No big marketing hero.
- No decorative graphics.

Avoid:

- Landing page design.
- Random gradients.
- Decorative animations.
- Huge text.
- Fake chat magic.
- Screens that look like a pitch deck instead of a working tool.

## 9. Suggested Layout

Use tabs:

```text
Analyst Queue
Case Workspace
Guided Investigation
CCO Dashboard
Audit
```

Inside Case Workspace, use columns:

```text
left: timeline and entity profile
middle: triggered rules and guided analysis
right: policy recommendations and actions
```

## 10. API Client

Create:

```text
frontend/api_client.py
```

Put API calls there, for example:

```python
def get_cases():
    ...

def get_case(case_id: str):
    ...

def add_action(case_id: str, action: dict):
    ...

def add_note(case_id: str, text: str):
    ...

def generate_evidence_package(case_id: str):
    ...
```

This keeps `frontend/app.py` cleaner.

## 11. Tests Or Checks

At minimum, manually check:

```text
Frontend starts
Backend starts
Case queue loads
CASE-4521 opens
Block Transaction button calls backend
Add Note button calls backend
Generate Evidence Package button calls backend
Audit verify shows true
CCO dashboard loads
```

Run:

```powershell
docker compose up --build
```

Then open:

```text
http://localhost:8501
```

## 12. What Not To Do

Do not:

- Build backend rules.
- Build audit hash-chain logic in the frontend.
- Create a second copy of the case data.
- Change shared schemas without asking.
- Change backend endpoint names without asking Ashwanth.
- Add a real LLM.
- Add real customer data.

## 13. First Coding-Agent Prompt

You can paste this into your coding agent:

```text
I am working on the ArqBanker POC. My assignment is the Streamlit frontend.

Read README.md, SOUL.md, docs/integration_contract.md, frontend/app.py, shared/schemas.py, and data/golden_case_4521.json.

Create a clean Streamlit UI with tabs: Analyst Queue, Case Workspace, Guided Investigation, CCO Dashboard, and Audit.

Move API calls into frontend/api_client.py.

The UI must use backend API responses. Do not hard-code a full fake case in the frontend.

Add buttons for Accept Case, Block Transaction, Add Note, Generate Evidence Package, and Verify Audit Chain.

Do not edit backend business logic. Do not create new schema classes.
```

## 14. Your Definition Of Done

You are done when:

- The frontend starts.
- The case queue shows `CASE-4521`.
- The case workspace is useful and readable.
- The guided investigation flow is clear.
- Buttons call backend endpoints.
- Evidence package output can be viewed.
- CCO dashboard loads from API.
- Audit view shows hash-chain status.

## 15. Pull Request Message

Use this format:

```text
Title: Build Streamlit analyst workspace and CCO dashboard

Summary:
- Added analyst queue.
- Added CASE-4521 workspace.
- Added guided investigation flow.
- Added CCO dashboard and audit view.

Tests:
- docker compose up --build
- Manually opened http://localhost:8501

Notes:
- Frontend uses backend API.
```
