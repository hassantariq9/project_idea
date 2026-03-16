import streamlit as st

st.set_page_config(
    page_title="IdeaVault — Project Idea Portal",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from utils.auth import init_session, get_current_user
from utils.styles import inject_css
from views.landing import show_landing
from views.login import show_login
from views.student import show_student_portal
from views.faculty import show_faculty_portal
from views.admin import show_admin_portal

inject_css()
init_session()

user = get_current_user()

if not user:
    if st.session_state.get("login_mode"):
        show_login()
    else:
        show_landing()
elif user["role"] == "admin":
    show_admin_portal()
elif user["role"] == "faculty":
    show_faculty_portal()
else:
    show_student_portal()
