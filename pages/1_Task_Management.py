# 01 - Imports

import streamlit as st
import requests
import time

from pathlib import Path
from groq import Groq
from database import add_task


# =========================================================
# LOAD PAGE CSS
# =========================================================

css_path = Path(__file__).resolve().parent.parent / "style.css"

with open(css_path, "r", encoding="utf-8") as css_file:
    st.markdown(
        f"<style>{css_file.read()}</style>",
        unsafe_allow_html=True
    )


# -------------------------------------------------
# 02 - Page Setup
# -------------------------------------------------

st.set_page_config(
    page_title="Task Management",
    page_icon="🗒️",
    layout="wide"
)


# -------------------------------------------------
# 03 - Login Check
# -------------------------------------------------

if not st.session_state.get("logged_in", False):
    st.switch_page("Home.py")


# -------------------------------------------------
# 04 - API Setup
# -------------------------------------------------

# Groq API
groq_key = st.secrets["GROQ_API_KEY"]

groq_client = Groq(
    api_key=groq_key
)


# Cloudflare Workers AI API
cloudflare_token = st.secrets["CLOUDFLARE_API_TOKEN"]

cloudflare_account_id = st.secrets[
    "CLOUDFLARE_ACCOUNT_ID"
]


# -------------------------------------------------
# 05 - Custom UI
# -------------------------------------------------

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #FFE34F;
    }


    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFE34F;
    }


    /* Main content width */
    .block-container {
        max-width: 1000px;
        padding-top: 60px;
    }


    /* Task Management heading */
    .task-title {
        font-family: Georgia, serif;
        font-size: 30px;
        font-weight: 700;
        text-align: center;
        color: #111111;
        white-space: nowrap;
        margin-bottom: 25px;
    }


    /* Prompt label */
    .prompt-label {
        font-size: 25px;
        font-weight: 700;
        color: #111111;
        margin-bottom: 5px;
    }


    /* Text area */
    div[data-testid="stTextArea"] textarea {
        background-color: #FFFFFF;
        color: #111111;

        border: 4px solid #222222;
        border-radius: 18px;

        min-height: 260px;

        font-size: 18px;
        padding: 20px;
    }


    /* Text area placeholder */
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #6b6b6b;
        opacity: 1;
    }


    /* Button */
    div.stButton > button {
        background-color: #49DA7E;
        color: #111111;

        border: 4px solid #222222;
        border-radius: 0px;

        font-size: 22px;
        font-weight: 700;

        min-width: 230px;

        box-shadow:
            10px 10px 0px #222222;

        transition: all 0.15s ease;
    }


    /* Button hover */
    div.stButton > button:hover {
        background-color: #38C96D;
        color: #111111;
        border: 4px solid #222222;

        transform: translate(3px, 3px);
        box-shadow:
            7px 7px 0px #222222;
    }


    /* Disabled button (while generating) */
    div.stButton > button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
        transform: none;
    }


    /* Response text areas */
    div[data-testid="stTextArea"] textarea:disabled {
        background-color: #FFFFFF;
        color: #111111;
        opacity: 1;
    }


    /* Normal text */
    p {
        color: #111111;
    }


    /* Subheaders */
    h2, h3 {
        color: #111111;
    }


    /* Task Status (Completed) box */
    .status-completed {
        background-color: #15803D;
        color: #FFE34F;

        font-size: 17px;
        font-weight: 700;

        padding: 14px 18px;

        border: 4px solid #222222;
        border-radius: 12px;

        box-shadow:
            6px 6px 0px #222222;

        margin-bottom: 30px;
    }


    </style>
    """,
    unsafe_allow_html=True
)


# =================================================
# 06 - Task Management
# =================================================


# -------------------------------------------------
# Initialize Session State
# -------------------------------------------------

# Initialize Response A
if "response_a" not in st.session_state:
    st.session_state.response_a = ""


# Initialize Response B
if "response_b" not in st.session_state:
    st.session_state.response_b = ""


# Initialize Saved Prompt
if "saved_prompt" not in st.session_state:
    st.session_state.saved_prompt = ""


# Initialize the generating flag (disables the button)
if "generating" not in st.session_state:
    st.session_state.generating = False


# -------------------------------------------------
# Clear Task Data After Saving
# -------------------------------------------------

if st.session_state.get("clear_task", False):

    st.session_state.response_a = ""
    st.session_state.response_b = ""
    st.session_state.saved_prompt = ""

    st.session_state.clear_task = False


# -------------------------------------------------
# Task Management UI
# -------------------------------------------------

left, middle, right = st.columns([1, 2, 1])


with middle:

    st.markdown(
        """
        <div class="task-title">
            Task Management
        </div>
        """,
        unsafe_allow_html=True
    )


    # -------------------------------------------------
    # Show Prompt Before Generation
    # -------------------------------------------------

    if (
        not st.session_state.response_a
        and not st.session_state.response_b
    ):

        prompt = st.text_area(
            "Prompt",
            placeholder="Enter the prompt here...",
            key="task_prompt"
        )


        # -------------------------------------------------
        # Generate Responses Button
        # (disabled while generating)
        # -------------------------------------------------

        if st.button(
            "Generate Responses",
            width="stretch",
            disabled=st.session_state.generating,
            key="generate_responses_button"
        ):

            if prompt:

                # Save the prompt before hiding the input
                st.session_state.saved_prompt = prompt

                # Mark generation as running
                st.session_state.generating = True

                # Refresh the page so the button shows as disabled
                st.rerun()


            else:

                st.warning(
                    "Please enter a prompt."
                )


        # -------------------------------------------------
        # Generation Logic
        # (runs on the rerun after the button click)
        # -------------------------------------------------

        if st.session_state.generating:

            # Loading animation
            loader = st.empty()

            loader.markdown(
                """
                <style>
                .loader-wrap {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    gap: 14px;
                    padding: 24px;
                }
                .loader-dots {
                    display: flex;
                    gap: 12px;
                }
                .loader-dots div {
                    width: 18px;
                    height: 18px;
                    border-radius: 50%;
                    border: 3px solid #222222;
                    animation: bounce 0.6s infinite alternate;
                }
                .loader-dots div:nth-child(1) { background: #FF666A; }
                .loader-dots div:nth-child(2) { background: #FFE34F; animation-delay: 0.2s; }
                .loader-dots div:nth-child(3) { background: #50C9C3; animation-delay: 0.4s; }
                @keyframes bounce {
                    to { transform: translateY(-14px); }
                }
                .loader-text {
                    font-weight: 700;
                    color: #111111;
                    font-size: 16px;
                }
                </style>
                <div class="loader-wrap">
                    <div class="loader-dots"><div></div><div></div><div></div></div>
                    <div class="loader-text">Generating responses...</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


            try:

                # =================================
                # Response A - Groq
                # =================================

                groq_response = (
                    groq_client.chat.completions.create(
                        model="openai/gpt-oss-120b",
                        messages=[
                            {
                                "role": "user",
                                "content": st.session_state.saved_prompt
                            }
                        ]
                    )
                )


                st.session_state.response_a = (
                    groq_response
                    .choices[0]
                    .message
                    .content
                )


                # =================================
                # Response B - Cloudflare
                # =================================

                cloudflare_url = (
                    "https://api.cloudflare.com/"
                    "client/v4/accounts/"
                    f"{cloudflare_account_id}/"
                    "ai/run/"
                    "@cf/meta/llama-3.1-8b-instruct"
                )


                cloudflare_response = requests.post(
                    cloudflare_url,
                    headers={
                        "Authorization":
                            f"Bearer {cloudflare_token}",

                        "Content-Type":
                            "application/json"
                    },

                    json={
                        "messages": [
                            {
                                "role": "user",
                                "content": st.session_state.saved_prompt
                            }
                        ]
                    },

                    timeout=60
                )


                # Raise an error if the API request fails
                cloudflare_response.raise_for_status()


                cloudflare_data = (
                    cloudflare_response.json()
                )


                st.session_state.response_b = (
                    cloudflare_data["result"][
                        "response"
                    ]
                )


            except Exception as e:

                # Stop loading and re-enable the button
                loader.empty()
                st.session_state.generating = False

                st.error(
                    f"Response generation failed: {e}"
                )

                st.stop()


            # Stop loading and re-enable the button
            loader.empty()
            st.session_state.generating = False

            # Refresh the page
            st.rerun()


# -------------------------------------------------
# Get Generated Responses
# -------------------------------------------------

response_a = st.session_state.response_a

response_b = st.session_state.response_b


# -------------------------------------------------
# Show Only After Both Responses Are Generated
# -------------------------------------------------

if response_a and response_b:

    left_space, response_area, right_space = (
        st.columns([1, 5, 1])
    )


    with response_area:

        response_a_col, response_b_col = (
            st.columns(
                2,
                gap="large"
            )
        )


        # -------------------------------------------------
        # Response A
        # -------------------------------------------------

        with response_a_col:

            st.text_area(
                "Response A",
                value=response_a,
                height=275,
                disabled=True
            )


        # -------------------------------------------------
        # Response B
        # -------------------------------------------------

        with response_b_col:

            st.text_area(
                "Response B",
                value=response_b,
                height=275,
                disabled=True
            )


        # -------------------------------------------------
        # Task Status
        # -------------------------------------------------

        st.write("Task Status")

        st.markdown(
            '<div class="status-completed">Completed</div>',
            unsafe_allow_html=True
        )


        # -------------------------------------------------
        # Save Task
        # -------------------------------------------------

        if st.button(
            "Save Task",
            type="primary",
            key="save_task_button"
        ):

            try:

                # Save the task to the database
                task_id = add_task(
                    st.session_state.saved_prompt,
                    response_a,
                    response_b
                )


                # Show the success message
                success_msg = st.markdown(
                    f'<div class="status-completed">'
                    f"Task saved successfully! Task ID: {task_id}"
                    f"</div>",
                    unsafe_allow_html=True
                )


                # Keep the message visible for 1 second
                time.sleep(1)


                # Hide the success message
                success_msg.empty()


                # Clear the task data
                st.session_state.clear_task = True


                # Refresh the page
                st.rerun()


            except Exception as e:

                st.error(
                    f"Task could not be saved: {e}"
                )
