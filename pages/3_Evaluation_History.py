# 01 - Imports

import streamlit as st
import pandas as pd
from pathlib import Path

from database import get_all_evaluations


# =========================================================
# LOAD EVALUATION CSS
# =========================================================

css_path = Path(__file__).resolve().parent.parent / "evaluation.css"

with open(css_path, "r", encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )


# -------------------------------------------------
# 02 - Page Setup
# -------------------------------------------------

st.set_page_config(
    page_title="History",
    page_icon="📋",
    layout="wide"
)


# -------------------------------------------------
# 03 - Login Check
# -------------------------------------------------

if not st.session_state.get("logged_in", False):
    st.switch_page("Home.py")


# -------------------------------------------------
# 04 - Page UI
# -------------------------------------------------

st.title("Evaluation History")

st.write(
    "View all saved response evaluations."
)


# -------------------------------------------------
# 05 - Get Evaluations
# -------------------------------------------------

evaluations = get_all_evaluations()


# -------------------------------------------------
# 06 - Show Evaluation History
# -------------------------------------------------

if evaluations:

    columns = [
        "Evaluation ID",
        "Task ID",
        "Evaluator ID",

        "A Correctness",
        "A Relevance",
        "A Clarity",
        "A Completeness",
        "A Instruction",

        "B Correctness",
        "B Relevance",
        "B Clarity",
        "B Completeness",
        "B Instruction",

        "Preference",
        "Flags",
        "Feedback",
        "Created At"
    ]


    # Convert database rows into a DataFrame
    df = pd.DataFrame(
        evaluations,
        columns=columns
    )


    # -------------------------------------------------
    # Calculate Total Scores
    # -------------------------------------------------

    df["Response A Score"] = (
        df["A Correctness"]
        + df["A Relevance"]
        + df["A Clarity"]
        + df["A Completeness"]
        + df["A Instruction"]
    )


    df["Response B Score"] = (
        df["B Correctness"]
        + df["B Relevance"]
        + df["B Clarity"]
        + df["B Completeness"]
        + df["B Instruction"]
    )


    # -------------------------------------------------
    # 07 - History Filters
    # -------------------------------------------------

    filter_col1, filter_col2 = st.columns(2)


    # Task ID filter
    with filter_col1:

        task_options = ["ALL"] + sorted(
            df["Task ID"].unique().tolist()
        )

        selected_task = st.selectbox(
            "Filter by Task ID",
            task_options
        )


    # Preference filter
    with filter_col2:

        preference_options = ["ALL"] + sorted(
            df["Preference"].dropna().unique().tolist()
        )

        selected_preference = st.selectbox(
            "Filter by Preference",
            preference_options
        )


    # Apply Task ID filter
    filtered_df = df.copy()

    if selected_task != "ALL":

        filtered_df = filtered_df[
            filtered_df["Task ID"] == selected_task
        ]


    # Apply Preference filter
    if selected_preference != "ALL":

        filtered_df = filtered_df[
            filtered_df["Preference"] == selected_preference
        ]


    # -------------------------------------------------
    # History Table
    # -------------------------------------------------

    history_df = filtered_df[
        [
            "Evaluation ID",
            "Task ID",
            "Evaluator ID",
            "Response A Score",
            "Response B Score",
            "Preference",
            "Flags",
            "Feedback",
            "Created At"
        ]
    ]


    st.table(history_df)


    # -------------------------------------------------
    # 08 - Export CSV
    # -------------------------------------------------

    csv = history_df.to_csv(
        index=False
    ).encode("utf-8")


    st.download_button(
        label="Download CSV",
        data=csv,
        file_name="evaluation_history.csv",
        mime="text/csv"
    )


    # -------------------------------------------------
    # 09 - Evaluation Details
    # -------------------------------------------------

    st.subheader("Evaluation Details")

    evaluation_ids = filtered_df[
        "Evaluation ID"
    ].tolist()


    if evaluation_ids:

        selected_evaluation_id = st.selectbox(
            "Select Evaluation ID",
            evaluation_ids
        )


        # Get the selected evaluation
        selected_evaluation = filtered_df[
            filtered_df["Evaluation ID"]
            == selected_evaluation_id
        ].iloc[0]


        # -------------------------------------------------
        # Evaluation Score Table
        # -------------------------------------------------

        details_df = pd.DataFrame(
            {
                "Criteria": [
                    "Correctness",
                    "Relevance",
                    "Clarity",
                    "Completeness",
                    "Instruction Following",
                    "Total Score"
                ],

                "Response A": [
                    selected_evaluation["A Correctness"],
                    selected_evaluation["A Relevance"],
                    selected_evaluation["A Clarity"],
                    selected_evaluation["A Completeness"],
                    selected_evaluation["A Instruction"],
                    selected_evaluation["Response A Score"]
                ],

                "Response B": [
                    selected_evaluation["B Correctness"],
                    selected_evaluation["B Relevance"],
                    selected_evaluation["B Clarity"],
                    selected_evaluation["B Completeness"],
                    selected_evaluation["B Instruction"],
                    selected_evaluation["Response B Score"]
                ]
            }
        )

        st.table(details_df)


        # -------------------------------------------------
        # Final Evaluation Table
        # -------------------------------------------------

        final_details_df = pd.DataFrame(
            {
                "Details": [
                    "Evaluation ID",
                    "Task ID",
                    "Preference",
                    "Quality Flags",
                    "Feedback",
                    "Created At"
                ],

                "Value": [
                    selected_evaluation["Evaluation ID"],
                    selected_evaluation["Task ID"],
                    selected_evaluation["Preference"],
                    selected_evaluation["Flags"] or "None",
                    selected_evaluation["Feedback"] or "No feedback",
                    selected_evaluation["Created At"]
                ]
            }
        )


        st.write("#### Final Evaluation")


        st.table(final_details_df)

    else:

        st.info(
            "No evaluations match the selected filters."
        )


else:

    st.info(
        "No evaluations available."
    )
