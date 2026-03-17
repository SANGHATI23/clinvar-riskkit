import streamlit as st
import pandas as pd

st.set_page_config(page_title="Variant Interpretation Workbench", layout="wide")

st.title("Variant Interpretation Workbench")
st.caption("Uncertainty-aware clinical variant reasoning demo")

import json

with open("data/challenges_v1.json") as f:
    cases = pd.DataFrame(json.load(f))

st.sidebar.header("Challenge Library")
selected_variant = st.sidebar.selectbox(
    "Choose a variant case",
    cases["variant"]
)

case = cases[cases["variant"] == selected_variant].iloc[0]

col1, col2 = st.columns([1.2, 1])

with col1:
    st.header("Case Details")
    st.write(f"**Variant:** {case['variant']}")
    st.write(f"**Gene:** {case['gene']}")
    st.write(f"**Condition:** {case['condition']}")

    st.subheader("Clinical Vignette")
    st.info(case["vignette"])

    st.subheader("Evidence Snapshot")
    st.write(f"**Review Status:** {case['review_status']}")
    st.write(f"**Number of Submitters:** {case['num_submitters']}")
    st.write(f"**Years Since Review:** {case['years_since_review']}")
    st.write(f"**Conflicting Interpretations:** {case['conflicts']}")
    st.write(f"**Risk Tier:** {case['risk_tier']}")

with col2:
    st.header("Your Submission")

    label = st.selectbox(
        "Your classification",
        ["Pathogenic", "Likely Pathogenic", "VUS", "Likely Benign", "Benign"]
    )

    confidence = st.selectbox(
        "Confidence level",
        ["Low", "Medium", "High"]
    )

    if st.button("Submit"):

        reference_label = case["reference_label"]

        if label == reference_label:
            label_score = 40
        elif label in ["Pathogenic", "Likely Pathogenic"] and reference_label in ["Pathogenic", "Likely Pathogenic"]:
            label_score = 25
        else:
            label_score = 10

        if case["risk_tier"] == "High" and confidence == "Low":
            calibration_score = 35
        elif case["risk_tier"] == "Low" and confidence == "High":
            calibration_score = 35
        elif case["risk_tier"] == "Medium" and confidence == "Medium":
            calibration_score = 30
        else:
            calibration_score = 15

        evidence_score = 20
        total_score = label_score + calibration_score + evidence_score

        st.success("Submission recorded")

        st.subheader("Score Breakdown")
        st.write(f"**Total Score:** {total_score} / 100")
        st.write(f"**Label Agreement:** {label_score} / 40")
        st.write(f"**Calibration:** {calibration_score} / 35")
        st.write(f"**Evidence Completeness:** {evidence_score} / 25")

        if total_score >= 80:
            st.info("Strong reasoning and good confidence calibration.")
        elif total_score >= 60:
            st.info("Reasonable interpretation, but calibration or evidence use could improve.")
        else:
            st.warning("This interpretation needs more caution and better alignment to the evidence.")

        st.subheader("Recommended Next Step")
        if case["risk_tier"] == "High":
            st.write("Recommend expert review, updated evidence check, and cautious confidence due to instability/conflict risk.")
        elif case["risk_tier"] == "Medium":
            st.write("Recommend targeted evidence review and moderate confidence until additional support is confirmed.")
        else:
            st.write("Evidence appears relatively stable; higher confidence may be appropriate with routine verification.")

st.markdown("---")
st.subheader("Available Challenges")
st.dataframe(
    cases[["variant", "gene", "condition", "risk_tier", "review_status"]],
    use_container_width=True
)