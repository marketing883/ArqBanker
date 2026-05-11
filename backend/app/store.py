from __future__ import annotations

import json
from pathlib import Path

from backend.app.audit import create_audit_event
from backend.app.rules.engine import build_case_from_synthetic_input
from shared.constants import GOLDEN_CASE_ID
from shared.schemas import AuditEvent, Case

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
CASE_FIXTURE_FILES = ("golden_case_4521.json", "case_4532.json")
SYNTHETIC_INPUT_FILES = ("synthetic_case_1234.json",)

cases: dict[str, Case] = {}
audit_events: list[AuditEvent] = []


def load_golden_case() -> Case:
    raw = json.loads((DATA_DIR / "golden_case_4521.json").read_text(encoding="utf-8"))
    return Case(**raw)


def load_case_fixture(filename: str) -> Case:
    raw = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
    return Case(**raw)


def load_case_fixtures() -> list[Case]:
    return [load_case_fixture(filename) for filename in CASE_FIXTURE_FILES]


def load_synthetic_input_case(filename: str) -> Case:
    raw = json.loads((DATA_DIR / filename).read_text(encoding="utf-8"))
    return build_case_from_synthetic_input(raw)


def load_all_cases() -> list[Case]:
    fixture_cases = load_case_fixtures()
    generated_cases = [load_synthetic_input_case(filename) for filename in SYNTHETIC_INPUT_FILES]
    return [*fixture_cases, *generated_cases]


def initialize_store() -> None:
    if GOLDEN_CASE_ID in cases:
        return

    for case in load_all_cases():
        cases[case.case_id] = case
        audit_events.append(
            create_audit_event(
                events=audit_events,
                actor_user_id="system",
                actor_role="system",
                event_type="case_created",
                entity_type="case",
                entity_id=case.case_id,
                summary=f"Loaded demo case {case.case_id}",
                payload={"risk_score": case.risk_score.overall_score},
            )
        )


def reset_store() -> None:
    cases.clear()
    audit_events.clear()
    initialize_store()
