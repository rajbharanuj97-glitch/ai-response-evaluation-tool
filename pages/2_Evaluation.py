# 01 - Imports

import streamlit as st
import time
from pathlib import Path

from database import get_all_tasks, add_evaluation


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

st.set_page_config(page_title="Evaluation", page_icon="⚖️", layout="wide")


# -------------------------------------------------
# 03 - Login Check
# -------------------------------------------------

if not st.session_state.get("logged_in", False):
    st.switch_page("Home.py")


# -------------------------------------------------
# 04 - Evaluation UI
# -------------------------------------------------

st.title("Response Evaluation")

st.write("Evaluate and compare Response A and Response B.")


# -------------------------------------------------
# 05 - Get Tasks from Database
# -------------------------------------------------

tasks = get_all_tasks()

# Check if tasks are available
if tasks:

    # -------------------------------------------------
    # Show Evaluation Save Success Message
    # -------------------------------------------------

    if st.session_state.get("evaluation_saved", False):

        st.success("Evaluation saved successfully!")

        # Clear the success flag
        st.session_state.evaluation_saved = False

    # -------------------------------------------------
    # Evaluation Default Values
    # -------------------------------------------------

    evaluation_defaults = {
        # Response A
        "a_correctness": 3,
        "a_relevance": 3,
        "a_clarity": 3,
        "a_completeness": 3,
        "a_instruction": 3,
        # Response B
        "b_correctness": 3,
        "b_relevance": 3,
        "b_clarity": 3,
        "b_completeness": 3,
        "b_instruction": 3,
        # Final evaluation
        "evaluation_preference": "Equal",
        "evaluation_flags": [],
        "evaluation_justification": "",
    }

    # -------------------------------------------------
    # Initialize Evaluation Values
    # -------------------------------------------------

    for key, value in evaluation_defaults.items():

        if key not in st.session_state:
            st.session_state[key] = value

    # -------------------------------------------------
    # Reset Evaluation After Save
    # -------------------------------------------------

    if st.session_state.get("reset_evaluation", False):

        for key, value in evaluation_defaults.items():
            st.session_state[key] = value

        # Reset complete
        st.session_state.reset_evaluation = False

    # -------------------------------------------------
    # Select Task
    # -------------------------------------------------

    selected_task = st.selectbox(
        "Select Task", tasks, format_func=lambda task: f"Task {task[0]} - {task[1]}"
    )

    # Get the selected task data
    task_id = selected_task[0]
    prompt = selected_task[1]
    response_a = selected_task[2]
    response_b = selected_task[3]

    # -------------------------------------------------
    # Show Prompt
    # -------------------------------------------------

    st.subheader("Prompt")

    st.info(prompt)

    # -------------------------------------------------
    # Response A & Response B
    # -------------------------------------------------

    response_a_col, response_b_col = st.columns(2, gap="large")

    # Response A
    with response_a_col:

        st.subheader("Response A")

        st.text_area(
            "Response A",
            value=response_a,
            height=300,
            disabled=True,
            label_visibility="collapsed",
        )

    # Response B
    with response_b_col:

        st.subheader("Response B")

        st.text_area(
            "Response B",
            value=response_b,
            height=300,
            disabled=True,
            label_visibility="collapsed",
        )

    # =================================================
    # 06 - Evaluation Ratings
    # =================================================

    st.divider()

    st.subheader("Evaluation Ratings")

    st.write("Rate both responses from 1 to 5.")

    rating_a_col, rating_b_col = st.columns(2, gap="large")

    # -------------------------------------------------
    # Response A Ratings
    # -------------------------------------------------

    with rating_a_col:

        st.markdown("### Response A")

        a_correctness = st.select_slider(
            "Correctness", options=[1, 2, 3, 4, 5], key="a_correctness"
        )

        a_relevance = st.select_slider(
            "Relevance", options=[1, 2, 3, 4, 5], key="a_relevance"
        )

        a_clarity = st.select_slider(
            "Clarity", options=[1, 2, 3, 4, 5], key="a_clarity"
        )

        a_completeness = st.select_slider(
            "Completeness", options=[1, 2, 3, 4, 5], key="a_completeness"
        )

        a_instruction = st.select_slider(
            "Instruction Following", options=[1, 2, 3, 4, 5], key="a_instruction"
        )

    # -------------------------------------------------
    # Response B Ratings
    # -------------------------------------------------

    with rating_b_col:

        st.markdown("### Response B")

        b_correctness = st.select_slider(
            "Correctness", options=[1, 2, 3, 4, 5], key="b_correctness"
        )

        b_relevance = st.select_slider(
            "Relevance", options=[1, 2, 3, 4, 5], key="b_relevance"
        )

        b_clarity = st.select_slider(
            "Clarity", options=[1, 2, 3, 4, 5], key="b_clarity"
        )

        b_completeness = st.select_slider(
            "Completeness", options=[1, 2, 3, 4, 5], key="b_completeness"
        )

        b_instruction = st.select_slider(
            "Instruction Following", options=[1, 2, 3, 4, 5], key="b_instruction"
        )

    # =================================================
    # 07 - Final Evaluation
    # =================================================

    st.divider()

    st.subheader("Final Evaluation")

    # -------------------------------------------------
    # Final Preference
    # -------------------------------------------------

    preference = st.radio(
        "Which response is better?",
        ["Response A", "Response B", "Equal", "Both Poor"],
        horizontal=True,
        key="evaluation_preference",
    )

    # -------------------------------------------------
    # Quality Flags
    # -------------------------------------------------

    st.write("Quality Flags")

    flags = st.multiselect(
        "Select any issues found in the responses",
        [
            "Factual Error",
            "Irrelevant",
            "Unclear",
            "Incomplete",
            "Instruction Not Followed",
        ],
        key="evaluation_flags",
    )

    # -------------------------------------------------
    # Feedback / Justification
    # -------------------------------------------------

    justification = st.text_area(
        "Feedback / Justification",
        placeholder="Explain why you selected this response...",
        key="evaluation_justification",
    )

# =================================================
# 08 - Save Evaluation
# =================================================

if st.button("Save Evaluation", type="primary", key="save_evaluation_button"):

    try:

        # Check the logged-in user ID
        if "user_id" not in st.session_state:

            st.error("User ID not found. Please log out and log in again.")

            st.stop()

        # Save the evaluation to the database
        evaluation_id = add_evaluation(
            task_id,
            st.session_state.user_id,
            # Response A ratings
            a_correctness,
            a_relevance,
            a_clarity,
            a_completeness,
            a_instruction,
            # Response B ratings
            b_correctness,
            b_relevance,
            b_clarity,
            b_completeness,
            b_instruction,
            # Final evaluation
            preference,
            flags,
            justification,
        )

        # Show the success message
        st.success(f"Evaluation saved successfully! Evaluation ID: {evaluation_id}")

        # Keep the message visible briefly
        time.sleep(1)

        # Reset the evaluation form
        st.session_state.reset_evaluation = True

        # Refresh the page
        st.rerun()

    except Exception as e:

        st.error(f"Evaluation could not be saved: {e}")
