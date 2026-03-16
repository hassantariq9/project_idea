import streamlit as st
from utils.db import load_users, verify_pw

def init_session():
    defaults = {
        "logged_in": False,
        "user_id": None,
        "user_role": None,
        "user_name": None,
        "user_email": None,
        "user_dept": None,
        "login_mode": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_current_user():
    if not st.session_state.get("logged_in"):
        return None
    return {
        "id":    st.session_state.user_id,
        "role":  st.session_state.user_role,
        "name":  st.session_state.user_name,
        "email": st.session_state.user_email,
        "dept":  st.session_state.user_dept,
    }

def login(uid, password):
    users = load_users()
    user = users.get(uid.strip())
    if not user:
        return False, "User ID not found."
    if not verify_pw(password, user["password"]):
        return False, "Incorrect password."
    st.session_state.logged_in  = True
    st.session_state.user_id    = uid.strip()
    st.session_state.user_role  = user["role"]
    st.session_state.user_name  = user["name"]
    st.session_state.user_email = user.get("email", "")
    st.session_state.user_dept  = user.get("department", "")
    return True, user["role"]

def logout():
    for k in ["logged_in","user_id","user_role","user_name","user_email","user_dept","login_mode"]:
        st.session_state[k] = False if k == "logged_in" else None
    st.rerun()
