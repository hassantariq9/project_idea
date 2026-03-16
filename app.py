
import streamlit as st
from dashboards.student import student_dashboard
from dashboards.faculty import faculty_dashboard
from dashboards.analytics import analytics_dashboard
from auth.auth import login, create_default_users

create_default_users()

st.sidebar.title("Idea Vault AI")

menu = st.sidebar.selectbox("Menu",["Login","Analytics"])

if menu=="Login":
    username = st.text_input("Username")
    password = st.text_input("Password",type="password")

    if st.button("Login"):
        role = login(username,password)
        if role:
            st.session_state["user"] = username
            st.session_state["role"] = role
        else:
            st.error("Invalid login")

if "role" in st.session_state:
    if st.session_state["role"]=="student":
        student_dashboard(st.session_state["user"])
    elif st.session_state["role"]=="faculty":
        faculty_dashboard()

if menu=="Analytics":
    analytics_dashboard()
