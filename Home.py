# =========================================================
# 01 - IMPORTS
# =========================================================

import sqlite3
from pathlib import Path

import streamlit as st

from database import (
    create_all_tables,
    add_user,
    login_user,
)


# =========================================================
# 02 - STREAMLIT PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="AI Response Evaluation Tool",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# =========================================================
# 03 - LOAD CSS FILE
# =========================================================

def load_css():

    css_path = Path(__file__).resolve().parent / "style.css"

    if css_path.exists():

        with open(css_path, "r", encoding="utf-8") as css_file:

            st.markdown(
                f"<style>{css_file.read()}</style>",
                unsafe_allow_html=True,
            )

    else:

        st.error("style.css file not found!")


load_css()


# =========================================================
# 04 - DATABASE SETUP
# =========================================================

create_all_tables()


# =========================================================
# 05 - SESSION STATE SETUP
# =========================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


if "auth_option" not in st.session_state:
    st.session_state.auth_option = "login"


# =========================================================
# 06 - CLEAR LOGIN INPUTS
# =========================================================

if st.session_state.pop("clear_login", False):

    st.session_state["login_username"] = ""
    st.session_state["login_password"] = ""


# =========================================================
# 07 - CLEAR REGISTER INPUTS
# =========================================================

if st.session_state.pop("clear_register", False):

    st.session_state["reg_username"] = ""
    st.session_state["reg_password"] = ""


# =========================================================
# 08 - HIDE SIDEBAR BEFORE LOGIN
# =========================================================

if not st.session_state.logged_in:

    st.markdown(
        """
        <style>

        [data-testid="stSidebar"] {
            display: none !important;
        }

        [data-testid="collapsedControl"] {
            display: none !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# 09 - MAIN LOGIN PAGE
# =========================================================

with st.container(key="main_page"):

    left_column, right_column = st.columns(
        [1, 1],
        gap=None,
    )


    with left_column:

        with st.container(key="left_side"):

            st.markdown(
                """
                <div class="main-title">
                    AI Response<br>
                    Evaluation<br>
                    Tool
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="tagline">
                    Compare. Rate. Decide.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="feature-box cyan-box">
                    A vs B responses
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="feature-box yellow-box">
                    5 criteria ratings
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown(
                """
                <div class="feature-box white-box">
                    Justify &amp; export CSV
                </div>
                """,
                unsafe_allow_html=True,
            )


    with right_column:

        with st.container(key="right_side"):

            with st.container(key="auth_box"):

                if not st.session_state.logged_in:

                    with st.container(key="auth_tabs"):

                        login_tab, register_tab = st.columns(
                            [1, 1],
                            gap="small",
                        )

                        with login_tab:

                            if st.button(
                                "Login",
                                key="login_option",
                                width="stretch",
                            ):

                                st.session_state.auth_option = "login"

                                st.rerun()


                        with register_tab:

                            if st.button(
                                "Register",
                                key="register_option",
                                width="stretch",
                            ):

                                st.session_state.auth_option = "register"

                                st.rerun()


                    if st.session_state.auth_option == "login":

                        st.markdown(
                            """
                            <div class="auth-title">
                                Welcome back
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        if st.session_state.pop(
                            "registration_success",
                            False,
                        ):

                            st.success(
                                "Account created successfully! Please login."
                            )

                        if st.session_state.pop(
                            "login_error",
                            False,
                        ):

                            st.error(
                                "Invalid username or password."
                            )

                        username = st.text_input(
                            "Username",
                            placeholder="Enter username",
                            key="login_username",
                        )

                        password = st.text_input(
                            "Password",
                            placeholder="Enter password",
                            type="password",
                            key="login_password",
                        )

                        if st.button(
                            "Login",
                            key="main_login_button",
                            type="primary",
                            width="stretch",
                        ):

                            if not username or not password:

                                st.warning(
                                    "Please enter username and password."
                                )

                            else:

                                user_id = login_user(
                                    username,
                                    password,
                                )

                                if user_id:

                                    st.session_state.logged_in = True

                                    st.session_state.user_id = user_id

                                    st.session_state.clear_login = True

                                    st.switch_page(
                                        "pages/1_Task_Management.py"
                                    )

                                else:

                                    st.session_state.clear_login = True

                                    st.session_state.login_error = True

                                    st.rerun()


                    elif st.session_state.auth_option == "register":

                        st.markdown(
                            """
                            <div class="auth-title">
                                Create Account
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                        reg_username = st.text_input(
                            "Username",
                            placeholder="Create a username",
                            key="reg_username",
                        )

                        reg_password = st.text_input(
                            "Password",
                            placeholder="Create a password",
                            type="password",
                            key="reg_password",
                        )

                        if st.button(
                            "Register",
                            key="main_register_button",
                            type="primary",
                            width="stretch",
                        ):

                            if not reg_username or not reg_password:

                                st.warning(
                                    "Please enter both a username and a password."
                                )

                            else:

                                try:

                                    add_user(
                                        reg_username,
                                        reg_password,
                                    )

                                    st.session_state.clear_register = True

                                    st.session_state.auth_option = "login"

                                    st.session_state.registration_success = True

                                    st.rerun()

                                except sqlite3.IntegrityError:

                                    st.error(
                                        "An account with this username already exists."
                                    )

                                except ValueError as error:

                                    st.warning(str(error))

                                except sqlite3.Error:

                                    st.error(
                                        "A database error occurred. Please try again."
                                    )


                else:

                    st.markdown(
                        """
                        <div class="auth-title">
                            Welcome
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    st.write(
                        "You are logged in."
                    )

                    if st.button(
                        "Go to Task Management",
                        key="task_management_button",
                        width="stretch",
                    ):

                        st.switch_page(
                            "pages/1_Task_Management.py"
                        )

                    if st.button(
                        "Logout",
                        key="logout_button",
                        width="stretch",
                    ):

                        st.session_state.logged_in = False

                        st.session_state.pop(
                            "user_id",
                            None,
                        )

                        st.session_state.auth_option = "login"

                        st.rerun()
