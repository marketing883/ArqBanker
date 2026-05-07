# Vijju Assignment: Data, Rules, and Risk Scoring

Hi Vijju. Your job is to build the risk brain of the ArqBanker POC.

You are responsible for turning synthetic customer and transaction data into triggered rules and risk-scored cases.

## 1. Your Mission

Build this part of the flow:

```text
synthetic data -> rule engine -> risk score -> case output
```

Your work should answer:

```text
Why was this case flagged?
How risky is it?
What evidence supports the score?
```

## 2. Read These Files First

Before coding, read these files in this order:

```text
README.md
SOUL.md
docs/integration_contract.md
shared/schemas.py
data/golden_case_4521.json
```

Do not skip this. These files tell you the shape of the product.

## 3. Create Your Branch

Run:

```powershell
git checkout main
git pull
git checkout -b vijju-rules-risk-scoring
```

Do all your work on this branch.

## 4. Files You Own

You should mainly work in:

```text
backend/app/rules/
data/
tests/
```

You may create these files:

```text
backend/app/rules/__init__.py
backend/app/rules/rules.py
backend/app/rules/scoring.py
backend/app/rules/engine.py
data/synthetic_customers.json
data/synthetic_transactions.json
data/watchlist_fixture.json
tests/test_rules.py
tests/test_scoring.py
```

Do not redesign the frontend.

Do not create new versions of the shared models.

## 5. Shared Models You Must Use

Import from:

```text
shared/schemas.py
```

Use these models:

```text
Customer
Transaction
RuleTrigger
RiskScore
Case
```

Do not create your own `Case` class.

Do not create your own `Transaction` class.

## 6. Build These Five Rules

### Rule 1: AML-01 Structuring

Purpose:

Detect transaction behavior just below reporting thresholds.

For the POC, trigger when:

```text
amount_usd is between 9000 and 9999
```

Evidence should include:

```text
Transaction amount is near USD 10,000 threshold
```

Output:

```text
RuleTrigger(rule_id="AML-01", domain="aml", ...)
```

### Rule 2: AML-02 High-Risk Geography

Purpose:

Detect transactions to or from high-risk jurisdictions.

For the POC, create a small list:

```python
HIGH_RISK_COUNTRIES = ["KY", "PA", "AE", "RU"]
```

Trigger when:

```text
origin_country or destination_country is in the high-risk list
```

Output:

```text
RuleTrigger(rule_id="AML-02", domain="aml", ...)
```

### Rule 3: AML-03 Shell Company Indicators

Purpose:

Detect suspicious business account signals.

For the POC, trigger when at least two of these are true:

```text
entity_type is business
account age is less than 180 days
stated annual revenue is below 250000
transaction amount is greater than 5 percent of stated annual revenue
```

Output:

```text
RuleTrigger(rule_id="AML-03", domain="aml", ...)
```

### Rule 4: SAN-01 OFAC SDN Fuzzy Match

Purpose:

Detect possible sanctions matches.

Use `data/watchlist_fixture.json`.

For the POC, match on:

```text
beneficiary_name
beneficiary_swift
director name if present in fixture
registration number if present in fixture
```

You can use Python standard library tools like:

```python
difflib.SequenceMatcher
```

Avoid adding a big external fuzzy-matching dependency unless you ask first.

Output:

```text
RuleTrigger(rule_id="SAN-01", domain="sanctions", ...)
```

### Rule 5: FRAUD-03 Account Takeover Indicators

Purpose:

Detect signs that the customer account may have been taken over.

For the POC, trigger when:

```text
device_id looks new
and ip_address looks risky or different
and transaction amount is greater than 5000
```

You can keep this simple. This is a POC.

Output:

```text
RuleTrigger(rule_id="FRAUD-03", domain="fraud", ...)
```

## 7. Build The Scoring Function

Create a function like:

```python
def score_triggers(triggers: list[RuleTrigger]) -> RiskScore:
    ...
```

Use this formula:

```text
rule contribution = weight * severity * confidence
```

Then normalize to:

```text
0 to 100
```

Use these risk bands:

```text
0-30    low
31-60   medium
61-85   high
86-100  critical
```

For `CASE-4521`, the result should stay near:

```text
overall_score = 87
band = critical
```

## 8. Build The Rule Engine

Create a function like:

```python
def evaluate_transaction(customer: Customer, transaction: Transaction) -> list[RuleTrigger]:
    ...
```

Then create:

```python
def build_case_from_triggers(...) -> Case:
    ...
```

The exact function names can change, but keep them simple and readable.

## 9. Tests To Add

Create tests that prove:

```text
AML-01 triggers for USD 9,500
AML-02 triggers for destination_country = KY
AML-03 triggers for a young low-revenue business
SAN-01 triggers for Ocean Holdings Ltd
FRAUD-03 triggers for new device plus high-value wire
CASE-4521 remains critical
```

Run tests with:

```powershell
python -m pytest tests -q
```

If pytest is not installed:

```powershell
python -m pip install -r requirements-dev.txt
```

## 10. What Not To Do

Do not:

- Build frontend screens.
- Change the API without telling Ashwanth.
- Change shared schemas without asking.
- Use real bank data.
- Add a real LLM.
- Add complex ML models.
- Rewrite files outside your area unless needed.

## 11. First Coding-Agent Prompt

You can paste this into your coding agent:

```text
I am working on the ArqBanker POC. My assignment is data, rules, and risk scoring.

Read README.md, SOUL.md, docs/integration_contract.md, shared/schemas.py, and data/golden_case_4521.json.

Create backend/app/rules/__init__.py, backend/app/rules/rules.py, backend/app/rules/scoring.py, and backend/app/rules/engine.py.

Implement the five POC rules: AML-01, AML-02, AML-03, SAN-01, and FRAUD-03.

Use only shared schemas from shared/schemas.py.

Add tests in tests/test_rules.py and tests/test_scoring.py.

Do not edit frontend files. Do not create new schema classes.
```

## 12. Your Definition Of Done

You are done when:

- The five rules exist.
- The scoring function exists.
- `CASE-4521` triggers expected rules.
- `CASE-4521` remains critical risk.
- Tests pass.
- Your pull request explains what you changed.

## 13. Pull Request Message

Use this format:

```text
Title: Add POC rule engine and risk scoring

Summary:
- Added five POC rules.
- Added risk scoring.
- Added tests for golden case CASE-4521.

Tests:
- python -m pytest tests -q

Notes:
- No shared schema changes.
```
