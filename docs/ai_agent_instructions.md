# AI Agent Instructions

Use this when asking coding agents to work on the repo.

## Prime Directive

Do not create a separate architecture. This repo is the architecture.

## Before Coding

Read:

1. `README.md`
2. `docs/product_brief.md`
3. `docs/integration_contract.md`
4. `docs/developer_assignments.md`
5. `shared/schemas.py`

## Rules

- Use shared schemas from `shared/schemas.py`.
- Keep `CASE-4521` working.
- Prefer small, reviewable changes.
- Do not rewrite files owned by another developer unless the task requires it.
- Do not add external services unless the README and Docker Compose are updated.
- Do not add real customer data.
- Do not make regulatory actions automatic. The system recommends; humans confirm.

## Output Standard

Every task should end with:

- Files changed.
- How to run it.
- What was tested.
- Any assumptions.
