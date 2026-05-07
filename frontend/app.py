from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

import requests
import streamlit as st

API_URL = os.getenv("ARQBANKER_API_URL", "http://localhost:8000")


def api_get(path: str):
    response = requests.get(f"{API_URL}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload=None, params=None):
    response = requests.post(f"{API_URL}{path}", json=payload, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


st.set_page_config(page_title="ArqBanker POC", layout="wide")
st.title("ArqBanker POC")

tabs = st.tabs(["Analyst Queue", "Case Workspace", "CCO Dashboard", "Audit"])

with tabs[0]:
    st.subheader("Unified Case Queue")
    cases = api_get("/cases")
    for case in cases:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            c1.markdown(f"**{case['case_id']}** - {case['customer']['entity_name']}")
            c2.metric("Risk", case["risk_score"]["overall_score"])
            c3.write(case["risk_score"]["band"].upper())
            c4.write(case["status"])
            st.write(" + ".join(rule["rule_id"] for rule in case["triggered_rules"]))

with tabs[1]:
    case = api_get("/cases/CASE-4521")
    st.subheader(f"{case['case_id']} - {case['customer']['entity_name']}")
    top = st.columns([1, 1, 1, 1])
    top[0].metric("Overall Risk", case["risk_score"]["overall_score"])
    top[1].metric("Primary Domain", case["risk_score"]["primary_domain"].upper())
    top[2].metric("Status", case["status"])
    top[3].metric("Assigned", case["assigned_to"])

    left, center, right = st.columns([1.2, 1.4, 1])

    with left:
        st.markdown("### Timeline")
        for event in case["timeline"]:
            st.write(event)

        st.markdown("### Triggered Rules")
        for rule in case["triggered_rules"]:
            st.warning(f"{rule['rule_id']}: {rule['rule_name']} ({rule['confidence']:.0%})")

    with center:
        st.markdown("### Guided Investigation")
        st.info(
            "Critical finding: Ocean Holdings Ltd has a 92 percent sanctions match "
            "with corroborating identifiers. The wire amount also sits just below "
            "the USD 10,000 threshold."
        )
        st.write("Recommended next step: human-confirm the block, then generate the SAR evidence package.")

        if st.button("Block Transaction And Restrict Account", type="primary"):
            action = {
                "action_id": f"ACT-{uuid4().hex[:8]}",
                "action_type": "block_transaction",
                "actor_user_id": "sarah.kim",
                "actor_role": "analyst_l2",
                "created_at": datetime.now(UTC).isoformat(),
                "summary": "Human-confirmed block of transaction and account restriction",
                "details": {
                    "transaction_id": "TXN-9001",
                    "amount_usd": 9500,
                    "customer_notification": False
                },
                "human_confirmed": True
            }
            api_post("/cases/CASE-4521/actions", action)
            st.success("Action recorded and audit logged.")

        if st.button("Generate SAR Evidence Package"):
            package = api_post("/cases/CASE-4521/evidence-package", params={"generated_by": "sarah.kim"})
            st.json(package)

    with right:
        st.markdown("### Policy Recommendations")
        for policy in case["policy_recommendations"]:
            if policy["severity"] == "critical":
                st.error(policy["title"])
            else:
                st.warning(policy["title"])
            st.caption(policy["recommendation"])

        st.markdown("### Confidence")
        st.write("Strengthening")
        for item in case["risk_score"]["strengthening_factors"]:
            st.write(f"- {item}")
        st.write("Weakening")
        for item in case["risk_score"]["weakening_factors"]:
            st.write(f"- {item}")

with tabs[2]:
    st.subheader("CCO Dashboard")
    dashboard = api_get("/dashboard/cco")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Cases", dashboard["active_cases"])
    c2.metric("Critical Cases", dashboard["critical_cases"])
    c3.metric("SARs Due", dashboard["sars_due"])
    c4.metric("OFAC Actions", dashboard["ofac_action_required"])
    st.write(f"Audit hash chain verified: {dashboard['audit_hash_chain_verified']}")

with tabs[3]:
    st.subheader("Audit Trail")
    verify = api_get("/audit/verify")
    st.metric("Events", verify["event_count"])
    st.write(f"Hash chain verified: {verify['verified']}")
    st.dataframe(api_get("/audit"), use_container_width=True)
