# 01 - Imports

import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from database import get_dashboard_stats, get_all_evaluations




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

st.set_page_config(page_title="Dashboard", page_icon="📈", layout="wide")


# -------------------------------------------------
# 03 - Login Check
# -------------------------------------------------

if not st.session_state.get("logged_in", False):
    st.switch_page("Home.py")


# -------------------------------------------------
# 04 - Dashboard
# -------------------------------------------------

st.title("Evaluation Dashboard")
stats = get_dashboard_stats()


# -------------------------------------------------
# 05 - Dashboard Cards (built with HTML and CSS)
# -------------------------------------------------

st.markdown(
    """
    <style>

    .metric-card {
        padding: 22px 28px;
        border-radius: 16px;
        height: 145px;
        color: white;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.20);
    }

    .metric-number {
        font-size: 38px;
        font-weight: 700;
        margin: 0;
    }

    .metric-title {
        font-size: 17px;
        font-weight: 500;
        margin: 0;
    }

    .card-purple {
        background: linear-gradient(135deg, #7B2CFF, #A000FF);
    }

    .card-blue {
        background: linear-gradient(135deg, #00AEEF, #20C5E9);
    }

    .card-red {
        background: linear-gradient(135deg, #FF3D3D, #FF5A36);
    }

    .card-green {
        background: linear-gradient(135deg, #159A8C, #20A99A);
    }

    .card-orange {
        background: linear-gradient(135deg, #F59E0B, #FF9F1C);
    }

    </style>
    """,
    unsafe_allow_html=True,
)


col1, col2, col3, col4, col5 = st.columns(5)


with col1:
    st.markdown(
        f"""
        <div class="metric-card card-purple">
            <p class="metric-number">{stats["total_tasks"]}</p>
            <p class="metric-title">Total Tasks</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:
    st.markdown(
        f"""
        <div class="metric-card card-blue">
            <p class="metric-number">{stats["total_evaluations"]}</p>
            <p class="metric-title">Evaluations</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:
    st.markdown(
        f"""
        <div class="metric-card card-red">
            <p class="metric-number">{stats["response_a_wins"]}</p>
            <p class="metric-title">A Wins</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col4:
    st.markdown(
        f"""
        <div class="metric-card card-green">
            <p class="metric-number">{stats["response_b_wins"]}</p>
            <p class="metric-title">B Wins</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


with col5:
    st.markdown(
        f"""
        <div class="metric-card card-orange">
            <p class="metric-number">{stats["equal_count"]}</p>
            <p class="metric-title">Equal</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------------------------
# 06 - Dashboard Charts (Donut + Bar chart)
# -------------------------------------------------

st.write("")

evaluations = get_all_evaluations()

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

    df = pd.DataFrame(
        evaluations,
        columns=columns
    )

    chart_col1, chart_col2 = st.columns(2)

    # -------------------------------------------------
    # Winner Split Donut
    # -------------------------------------------------

    with chart_col1:

        preference_counts = (
            df["Preference"]
            .value_counts()
            .reset_index()
        )

        preference_counts.columns = [
            "Preference",
            "Count"
        ]

        donut_fig = px.pie(
            preference_counts,
            names="Preference",
            values="Count",
            hole=0.55,
            title="Winner Split"
        )

        donut_fig.update_layout(
            height=420,
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )

        st.plotly_chart(
            donut_fig,
            use_container_width=True
        )


    # -------------------------------------------------
    # Average Rating Per Criterion
    # -------------------------------------------------

    with chart_col2:

        criteria = [
            "Correctness",
            "Relevance",
            "Clarity",
            "Completeness",
            "Instruction"
        ]

        averages = [
            (
                df["A Correctness"].mean()
                + df["B Correctness"].mean()
            ) / 2,

            (
                df["A Relevance"].mean()
                + df["B Relevance"].mean()
            ) / 2,

            (
                df["A Clarity"].mean()
                + df["B Clarity"].mean()
            ) / 2,

            (
                df["A Completeness"].mean()
                + df["B Completeness"].mean()
            ) / 2,

            (
                df["A Instruction"].mean()
                + df["B Instruction"].mean()
            ) / 2
        ]


        rating_df = pd.DataFrame(
            {
                "Criteria": criteria,
                "Average Rating": averages
            }
        )


        bar_fig = px.bar(
            rating_df,
            x="Criteria",
            y="Average Rating",
            color="Criteria",
            title="Average Rating Per Criterion"
        )


        bar_fig.update_layout(
            height=420,
            showlegend=False,
            yaxis_range=[0, 5],
            margin=dict(
                l=20,
                r=20,
                t=60,
                b=20
            )
        )


        st.plotly_chart(
            bar_fig,
            use_container_width=True
        )


else:

    st.info("No evaluation data available for charts.")
