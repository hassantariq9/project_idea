import streamlit as st

def show_landing():
    st.markdown("""
<div class="hero">
  <div style="font-size:48px;margin-bottom:16px;">💡</div>
  <h1>IdeaVault</h1>
  <p>University Project Idea Portal — Submit, track, and discover unique final-year project ideas</p>
</div>
""", unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
<div class="portal-card">
  <div class="portal-card-icon">🎓</div>
  <div class="portal-card-title">Student</div>
  <div class="portal-card-desc">Submit ideas, get AI feedback, track approval status</div>
</div>""", unsafe_allow_html=True)
        if st.button("Enter as Student", use_container_width=True, key="land_student"):
            st.session_state.login_mode = "student"
            st.rerun()

    with col2:
        st.markdown("""
<div class="portal-card">
  <div class="portal-card-icon">👨‍🏫</div>
  <div class="portal-card-title">Faculty</div>
  <div class="portal-card-desc">Review assigned ideas, approve or request changes</div>
</div>""", unsafe_allow_html=True)
        if st.button("Enter as Faculty", use_container_width=True, key="land_faculty"):
            st.session_state.login_mode = "faculty"
            st.rerun()

    with col3:
        st.markdown("""
<div class="portal-card">
  <div class="portal-card-icon">🛡️</div>
  <div class="portal-card-title">Admin</div>
  <div class="portal-card-desc">Full dashboard, analytics, manage users & clusters</div>
</div>""", unsafe_allow_html=True)
        if st.button("Enter as Admin", use_container_width=True, key="land_admin"):
            st.session_state.login_mode = "admin"
            st.rerun()

    st.divider()

    # Feature highlights
    f1, f2, f3, f4 = st.columns(4)
    for col, icon, title, desc in [
        (f1, "🤖", "AI Duplicate Detection", "Automatically rejects similar ideas using semantic analysis"),
        (f2, "📊", "Live Analytics", "Track submissions, approvals, and cluster distributions"),
        (f3, "🔮", "Idea Clustering", "Ideas auto-grouped into topic clusters for better overview"),
        (f4, "✉️", "Email Notifications", "Students notified instantly on status changes"),
    ]:
        with col:
            st.markdown(f"""
<div style="text-align:center;padding:16px 8px;">
  <div style="font-size:24px;margin-bottom:8px;">{icon}</div>
  <div style="font-size:13px;font-weight:600;color:#111827;margin-bottom:4px;">{title}</div>
  <div style="font-size:12px;color:#6b7280;line-height:1.5;">{desc}</div>
</div>""", unsafe_allow_html=True)

    st.divider()
    with st.expander("🔑 Demo Credentials"):
        st.markdown("""
| Role | ID / Username | Password | Department |
|------|--------------|----------|------------|
| 🎓 Student | S001 | Student@123 | Computer Science |
| 🎓 Student | S002 | Student@123 | Software Engineering |
| 🎓 Student | S003 | Student@123 | Computer Science |
| 👨‍🏫 Faculty | dr_smith | Faculty@123 | Computer Science |
| 👨‍🏫 Faculty | dr_khan | Faculty@123 | Software Engineering |
| 🛡️ Admin | admin | Admin@2024 | — |
""")
