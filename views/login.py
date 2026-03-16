import streamlit as st
from utils.auth import login

MODE_LABELS = {
    "student": ("🎓", "Student Login"),
    "faculty": ("👨‍🏫", "Faculty Login"),
    "admin":   ("🛡️",  "Admin Login"),
}

def show_login():
    mode = st.session_state.login_mode
    icon, title = MODE_LABELS.get(mode, ("🔐", "Login"))

    col_center = st.columns([1,2,1])[1]
    with col_center:
        st.markdown(f"## {icon} {title}")
        st.markdown("")

        uid  = st.text_input("Username / Student ID", placeholder="e.g. S001 or admin")
        pwd  = st.text_input("Password", type="password")

        c1, c2 = st.columns([1, 2])
        with c1:
            if st.button("← Back"):
                st.session_state.login_mode = None
                st.rerun()
        with c2:
            if st.button("Sign In →", type="primary", use_container_width=True):
                if not uid or not pwd:
                    st.error("Please enter both fields.")
                else:
                    ok, result = login(uid, pwd)
                    if not ok:
                        st.error(result)
                    elif mode != "all" and result != mode:
                        st.error(f"This account is not a {mode}. Please use the correct portal.")
                        from utils.auth import logout
                        logout()
                    else:
                        st.rerun()
