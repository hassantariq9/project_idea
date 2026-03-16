import streamlit as st

from dashboards.student import student_dashboard
from dashboards.faculty import faculty_dashboard
from dashboards.analytics import analytics_dashboard
from dashboards.admin import admin_dashboard

from auth.auth import login, create_default_users, register_student
from database.db import init_db


# -----------------------------
# Initialize Database
# -----------------------------

init_db()
create_default_users()


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("Idea Vault AI")

menu = st.sidebar.selectbox(
"Menu",
["Login","Sign Up","Analytics"]
)


# -----------------------------
# LOGIN PAGE
# -----------------------------

if menu == "Login":

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):

        role = login(username,password)

        if role:

            st.session_state["user"] = username
            st.session_state["role"] = role

            st.success("Login successful")

        else:
            st.error("Invalid login")


# -----------------------------
# SIGNUP PAGE
# -----------------------------

if menu == "Sign Up":

    st.title("Student Registration")

    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password",type="password")

    if st.button("Create Account"):

        success = register_student(username,password,email)

        if success:
            st.success("Account created. Please login.")
        else:
            st.error("Username already exists")


# -----------------------------
# DASHBOARDS AFTER LOGIN
# -----------------------------

if "role" in st.session_state:

    role = st.session_state["role"]

    if role == "student":
        student_dashboard(st.session_state["user"])

    elif role == "faculty":
        faculty_dashboard()

    elif role == "admin":
        admin_dashboard()


# -----------------------------
# ANALYTICS PAGE
# -----------------------------

if menu == "Analytics":
    analytics_dashboard()
