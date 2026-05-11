from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

# Streamlit runs this file as a script, so the repo root is not always on
# sys.path. Add it explicitly so `frontend.api_client` works in local runs.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from frontend.api_client import (
    add_action,
    add_note,
    generate_evidence_package,
    get_audit_events,
    get_case,
    get_cases,
    get_cco_dashboard,
    get_health,
    verify_audit_chain,
)

GOLDEN_CASE_ID = "CASE-4521"
CURRENT_USER = "sarah.kim"
CURRENT_ROLE = "analyst_l2"


def money(value: float | int | None) -> str:
    if value is None:
        return "-"
    return f"USD {value:,.0f}"


def badge(value: str) -> str:
    return value.replace("_", " ").title()


def risk_color(band: str) -> str:
    return {
        "critical": "#b42318",
        "high": "#b54708",
        "medium": "#175cd3",
        "low": "#067647",
    }.get(band, "#344054")


def render_rule_explanation(rule: dict) -> None:
    rule_id = rule["rule_id"]
    if rule_id == "SAN-01":
        st.info(
            "This is the sanctions signal. The backend case says the beneficiary has a high-confidence "
            "potential OFAC SDN match, supported by name, SWIFT, registration, and director evidence."
        )
    elif rule_id == "AML-01":
        st.info(
            "This is the AML structuring signal. The transaction amount is USD 9,500, which sits just below "
            "the USD 10,000 threshold and needs analyst review with the rest of the case context."
        )
    elif rule_id == "FRAUD-03":
        st.info(
            "This is the fraud signal. The backend case includes account-takeover indicators: new device, "
            "unusual location/VPN route, failed MFA, and a high-value wire soon after."
        )


def render_demo_path() -> None:
    st.markdown("#### Demo Path")
    st.write("1. Start in Analyst Queue and confirm CASE-4521 is critical.")
    st.write("2. Open Case Workspace and review customer, transaction, rules, and policies.")
    st.write("3. Use Guided Investigation to understand SAN-01, AML-01, and FRAUD-03 together.")
    st.write("4. Click a human-confirmed action such as Accept Case or Block Transaction.")
    st.write("5. Add an investigation note so the reasoning is audit logged.")
    st.write("6. Generate the evidence package and verify the audit chain.")


def run_action(
    label: str,
    case_id: str,
    action_type: str,
    summary: str,
    details: dict | None = None,
    key: str | None = None,
):
    button_key = key or f"{case_id}-{action_type}-{label}"
    if st.button(label, use_container_width=True, key=button_key):
        try:
            case = add_action(
                case_id,
                action_type,
                summary,
                actor_user_id=CURRENT_USER,
                actor_role=CURRENT_ROLE,
                details=details,
            )
            st.success(f"Recorded {badge(action_type)}. Case status: {badge(case['status'])}.")
            st.rerun()
        except Exception as exc:
            st.error(f"Action failed: {exc}")


def load_case(case_id: str):
    try:
        return get_case(case_id)
    except Exception as exc:
        st.error(f"Could not load case {case_id}: {exc}")
        return None


def render_status_strip(case: dict) -> None:
    risk = case["risk_score"]
    cols = st.columns([1, 1, 1, 1, 1])
    cols[0].metric("Risk Score", risk["overall_score"])
    cols[1].metric("Risk Band", badge(risk["band"]))
    cols[2].metric("Primary Domain", risk["primary_domain"].upper())
    cols[3].metric("Status", badge(case["status"]))
    cols[4].metric("Assigned", case.get("assigned_to") or "Unassigned")


def render_queue() -> None:
    st.subheader("Analyst Queue")
    st.caption("Live case queue from the backend API.")
    try:
        cases = get_cases()
    except Exception as exc:
        st.error(f"Backend unavailable: {exc}")
        return

    if not cases:
        st.info("No cases in queue.")
        return

    rows = []
    for case in cases:
        rows.append(
            {
                "case_id": case["case_id"],
                "entity": case["customer"]["entity_name"],
                "risk_score": case["risk_score"]["overall_score"],
                "risk_band": case["risk_score"]["band"],
                "primary_domain": case["risk_score"]["primary_domain"],
                "status": case["status"],
                "rules": ", ".join(rule["rule_id"] for rule in case["triggered_rules"]),
                "assigned_to": case.get("assigned_to") or "",
            }
        )
    st.dataframe(rows, use_container_width=True, hide_index=True)

    case_ids = [case["case_id"] for case in cases]
    default_index = case_ids.index(GOLDEN_CASE_ID) if GOLDEN_CASE_ID in case_ids else 0
    selected = st.selectbox("Open case", case_ids, index=default_index)
    st.session_state["selected_case_id"] = selected

    with st.expander("What data is this queue using?", expanded=True):
        st.write(
            "This table is loaded from `GET /cases`. For the POC, the backend loads the golden case "
            "`CASE-4521` from `data/golden_case_4521.json`."
        )
        st.write(
            "The queue shows the backend's case status, assigned analyst, risk score, risk band, primary domain, "
            "and triggered rule IDs. The frontend is not calculating risk or inventing cases."
        )


def render_workspace() -> None:
    case_id = st.session_state.get("selected_case_id", GOLDEN_CASE_ID)
    case = load_case(case_id)
    if not case:
        return

    st.subheader(f"{case['case_id']} - {case['customer']['entity_name']}")
    st.caption("360-degree workspace using backend case, policy, action, note, and evidence APIs.")
    render_status_strip(case)

    transaction = case["transactions"][0] if case["transactions"] else {}
    with st.expander("What is happening in this case?", expanded=True):
        st.write(
            f"{case['customer']['entity_name']} initiated a {money(transaction.get('amount_usd'))} "
            f"{transaction.get('transaction_type', 'transaction')} to {transaction.get('beneficiary_name', 'the beneficiary')}. "
            "The backend case combines sanctions, AML, and fraud signals into one investigation workspace."
        )
        st.write(
            "The analyst should review the evidence, confirm any regulatory action manually, add notes, "
            "and generate the evidence package after action is taken."
        )

    left, middle, right = st.columns([1.15, 1.35, 1])

    with left:
        st.markdown("#### Entity Profile")
        customer = case["customer"]
        st.write(f"**Customer ID:** {customer['customer_id']}")
        st.write(f"**Account:** {customer['account_id']}")
        st.write(f"**KYC:** {badge(customer['kyc_status'])}")
        st.write(f"**Industry:** {customer.get('stated_industry') or '-'}")
        st.write(f"**Annual Revenue:** {money(customer.get('stated_annual_revenue_usd'))}")
        st.write(f"**Prior Alerts:** {customer['prior_alert_count']}")

        st.markdown("#### Transaction")
        st.write(f"**Type:** {badge(transaction.get('transaction_type', '-'))}")
        st.write(f"**Amount:** {money(transaction.get('amount_usd'))}")
        st.write(f"**Beneficiary:** {transaction.get('beneficiary_name') or '-'}")
        st.write(f"**Destination:** {transaction.get('destination_country') or '-'}")
        st.write(f"**SWIFT:** {transaction.get('beneficiary_swift') or '-'}")

        st.markdown("#### Timeline")
        for item in case["timeline"]:
            st.write(f"- {item}")

    with middle:
        st.markdown("#### Triggered Rules")
        for rule in case["triggered_rules"]:
            with st.container(border=True):
                st.markdown(f"**{rule['rule_id']} - {rule['rule_name']}**")
                st.caption(f"{rule['domain'].upper()} - confidence {rule['confidence']:.0%}")
                st.write(rule["description"])
                render_rule_explanation(rule)
                for evidence in rule["evidence"]:
                    st.write(f"- {evidence}")

        st.markdown("#### Confidence Factors")
        factor_cols = st.columns(3)
        for title, key, column in [
            ("Strengthening", "strengthening_factors", factor_cols[0]),
            ("Weakening", "weakening_factors", factor_cols[1]),
            ("Missing Data", "missing_data_factors", factor_cols[2]),
        ]:
            with column:
                st.caption(title)
                for factor in case["risk_score"][key]:
                    st.write(f"- {factor}")

        st.markdown("#### Notes")
        for note in case["notes"]:
            st.write(f"- {note}")
        note_text = st.text_area("Add investigation note", placeholder="Record what you reviewed and why.")
        if st.button("Add Note", type="primary", key=f"{case['case_id']}-workspace-add-note"):
            if not note_text.strip():
                st.warning("Enter a note before submitting.")
            else:
                try:
                    add_note(case["case_id"], note_text, actor_user_id=CURRENT_USER, actor_role=CURRENT_ROLE)
                    st.success("Note added and audit logged.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Could not add note: {exc}")

    with right:
        st.markdown("#### Policy Recommendations")
        for policy in case["policy_recommendations"]:
            severity = policy["severity"]
            with st.container(border=True):
                if severity == "critical":
                    st.error(policy["title"])
                else:
                    st.warning(policy["title"])
                st.write(policy["recommendation"])
                st.caption(
                    f"{policy['policy_id']} - {policy['regulation']} - "
                    f"Human confirmation: {policy['requires_human_confirmation']}"
                )

        st.markdown("#### Quick Actions")
        st.caption("Buttons call backend endpoints. They do not only change frontend state.")
        run_action(
            "Accept Case",
            case["case_id"],
            "accept_case",
            "Accepted case for investigation.",
            key=f"{case['case_id']}-workspace-accept",
        )
        run_action(
            "Block Transaction",
            case["case_id"],
            "block_transaction",
            "Blocked transaction after human review.",
            {"transaction_id": transaction.get("transaction_id"), "customer_notification": False},
            key=f"{case['case_id']}-workspace-block",
        )
        run_action(
            "Restrict Account",
            case["case_id"],
            "restrict_account",
            "Restricted account while sanctions review is active.",
            {"account_id": case["customer"]["account_id"]},
            key=f"{case['case_id']}-workspace-restrict",
        )
        run_action(
            "Send Secure Message",
            case["case_id"],
            "send_secure_message",
            "Prepared secure message record for controlled customer communication.",
            {"customer_notification": True},
            key=f"{case['case_id']}-workspace-message",
        )

        if st.button("Generate Evidence Package", use_container_width=True, key=f"{case['case_id']}-workspace-evidence"):
            try:
                st.session_state["evidence_package"] = generate_evidence_package(case["case_id"], CURRENT_USER)
                st.success("Evidence package generated and audit logged.")
                st.rerun()
            except Exception as exc:
                st.error(f"Could not generate evidence package: {exc}")

        if st.button("Verify Audit Chain", use_container_width=True, key=f"{case['case_id']}-workspace-verify"):
            try:
                st.session_state["audit_verify"] = verify_audit_chain()
            except Exception as exc:
                st.error(f"Could not verify audit chain: {exc}")

        if st.session_state.get("audit_verify"):
            verify = st.session_state["audit_verify"]
            st.info(f"Audit verified: {verify['verified']} - Events: {verify['event_count']}")

        if st.session_state.get("evidence_package"):
            st.markdown("#### Latest Evidence Package")
            st.json(st.session_state["evidence_package"])


def render_guided_investigation() -> None:
    case_id = st.session_state.get("selected_case_id", GOLDEN_CASE_ID)
    case = load_case(case_id)
    if not case:
        return

    st.subheader("Guided Investigation")
    st.caption("Scripted POC flow. The frontend explains; the backend records actions.")
    render_demo_path()

    steps = [
        ("1. SAN-01 sanctions finding", "The beneficiary is Ocean Holdings Ltd. The backend evidence says the name, SWIFT code, registration number, and director match sanctions fixture data."),
        ("2. AML-01 structuring concern", "The transaction is USD 9,500, close to the USD 10,000 reporting threshold. Alone that is not a decision, but it increases review priority."),
        ("3. FRAUD-03 account takeover concern", "The transaction followed a new device, unusual location or VPN route, failed MFA, and a high-value online wire."),
        ("4. Policy recommendations", "The backend recommends OFAC review and SAR preparation. Both require human confirmation and are not auto-executed."),
        ("5. Evidence and audit", "Actions, notes, and evidence package generation create audit events. The audit tab verifies the hash chain."),
    ]

    for title, body in steps:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.write(body)

    cols = st.columns(3)
    with cols[0]:
        run_action(
            "Accept Case",
            case["case_id"],
            "accept_case",
            "Accepted case from guided investigation.",
            key=f"{case['case_id']}-guided-accept",
        )
    with cols[1]:
        run_action(
            "Block Transaction",
            case["case_id"],
            "block_transaction",
            "Blocked transaction from guided investigation after human review.",
            {"transaction_id": case["transactions"][0]["transaction_id"] if case["transactions"] else None},
            key=f"{case['case_id']}-guided-block",
        )
    with cols[2]:
        if st.button("Generate Evidence Package", use_container_width=True, key=f"{case['case_id']}-guided-evidence"):
            st.session_state["evidence_package"] = generate_evidence_package(case["case_id"], CURRENT_USER)
            st.success("Evidence package generated.")
            st.rerun()


def render_cco_dashboard() -> None:
    st.subheader("CCO Dashboard")
    st.caption("Executive readiness metrics from the backend dashboard endpoint.")
    try:
        dashboard = get_cco_dashboard()
    except Exception as exc:
        st.error(f"Could not load dashboard: {exc}")
        return

    cols = st.columns(6)
    cols[0].metric("Active Cases", dashboard["active_cases"])
    cols[1].metric("Critical Cases", dashboard["critical_cases"])
    cols[2].metric("SARs Due", dashboard["sars_due"])
    cols[3].metric("OFAC Action Required", dashboard["ofac_action_required"])
    cols[4].metric("Audit Chain", "Verified" if dashboard["audit_hash_chain_verified"] else "Failed")
    cols[5].metric("FP Target", f"{dashboard['false_positive_rate_target']}%")

    if dashboard["audit_hash_chain_verified"]:
        st.success("Audit hash chain is verified.")
    else:
        st.error("Audit hash chain verification failed.")

    with st.expander("How to read this dashboard", expanded=True):
        st.write("Active cases and critical cases come from `GET /dashboard/cco`.")
        st.write("SARs due and OFAC action required summarize regulatory workload for the demo case.")
        st.write("Audit Chain shows whether backend hash-chain verification returned true.")


def render_audit() -> None:
    st.subheader("Audit")
    st.caption("Append-only backend audit events and hash-chain verification.")

    left, right = st.columns([1, 3])
    with left:
        if st.button("Verify Audit Chain", type="primary", use_container_width=True, key="audit-tab-verify"):
            st.session_state["audit_verify"] = verify_audit_chain()
        verify = st.session_state.get("audit_verify") or verify_audit_chain()
        st.metric("Event Count", verify["event_count"])
        st.metric("Hash Chain", "Verified" if verify["verified"] else "Failed")

    with right:
        try:
            events = get_audit_events()
        except Exception as exc:
            st.error(f"Could not load audit events: {exc}")
            return
        st.dataframe(events, use_container_width=True, hide_index=True)
        with st.expander("What these audit events prove"):
            st.write("Every case action and note creates an audit event in the backend.")
            st.write("Each event stores the previous event hash and its own event hash.")
            st.write("If an old event is changed, `GET /audit/verify` should fail.")


def main() -> None:
    st.set_page_config(page_title="ArqBanker POC", layout="wide")
    st.title("ArqBanker Risk Operations")

    try:
        health = get_health()
        st.caption(f"Backend: {health['status']} - Golden case: {health['golden_case']}")
    except Exception as exc:
        st.error(f"Backend is not reachable: {exc}")

    st.markdown(
        """
        <style>
        .stApp {
            background: #f7f9fc;
        }
        h1, h2, h3, h4 {
            color: #101828;
        }
        p, li, label {
            color: #344054;
        }
        [data-testid="stMetricValue"] { font-size: 1.45rem; }
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid #e4e7ec;
            border-radius: 8px;
            padding: 12px 14px;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 8px;
            border-color: #e4e7ec;
            background: #ffffff;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 6px;
            border-bottom: 1px solid #d0d5dd;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 12px;
            color: #344054;
        }
        .stButton > button {
            border-radius: 6px;
            border: 1px solid #98a2b3;
            font-weight: 600;
        }
        .stButton > button[kind="primary"] {
            background: #175cd3;
            border-color: #175cd3;
        }
        div[data-testid="stDataFrame"] {
            border: 1px solid #e4e7ec;
            border-radius: 8px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["Analyst Queue", "Case Workspace", "Guided Investigation", "CCO Dashboard", "Audit"])
    with tabs[0]:
        render_queue()
    with tabs[1]:
        render_workspace()
    with tabs[2]:
        render_guided_investigation()
    with tabs[3]:
        render_cco_dashboard()
    with tabs[4]:
        render_audit()


if __name__ == "__main__":
    main()
