import streamlit as st
import json
import os
import time
from datetime import datetime
from anthropic import Anthropic

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Project Idea Portal",
    page_icon="💡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ─── Anthropic client ──────────────────────────────────────────────────────────
client = Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# ─── Storage helpers (JSON file on disk) ───────────────────────────────────────
DATA_FILE = "ideas.json"
USERS_FILE = "users.json"

def load_ideas():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_ideas(ideas):
    with open(DATA_FILE, "w") as f:
        json.dump(ideas, f, indent=2)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    # Default demo users
    default = {
        "S001": {"password": "pass123", "name": "Alice Rahman", "role": "student"},
        "S002": {"password": "pass123", "name": "Omar Farooq", "role": "student"},
        "admin": {"password": "admin123", "name": "Administrator", "role": "admin"},
    }
    save_users(default)
    return default

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

# ─── Status helpers ────────────────────────────────────────────────────────────
STATUS_COLORS = {
    "pending":  "🟡",
    "approved": "🟢",
    "rejected": "🔴",
    "changes":  "🔵",
    "taken":    "⚫",
}
STATUS_LABELS = {
    "pending":  "Pending Review",
    "approved": "Approved",
    "rejected": "Rejected",
    "changes":  "Needs Changes",
    "taken":    "Already Taken",
}

def fmt_date(iso):
    try:
        d = datetime.fromisoformat(iso)
        return d.strftime("%d %b %Y, %H:%M")
    except:
        return iso

# ─── AI similarity check ───────────────────────────────────────────────────────
def check_similarity(title, desc, approved_ideas):
    if not approved_ideas:
        return {"isSimilar": False, "similarTo": None}
    existing = "\n".join(f'- "{i["title"]}": {i["description"]}' for i in approved_ideas)
    prompt = f"""You are checking if a new project idea is too similar to existing approved ideas.

New idea:
Title: "{title}"
Description: "{desc}"

Existing approved ideas:
{existing}

Is the new idea conceptually similar or a duplicate of any existing idea? Consider the core concept, not just wording.

Respond ONLY with valid JSON — no explanation, no markdown:
{{"isSimilar": true, "similarTo": "title of similar idea"}}
or
{{"isSimilar": false, "similarTo": null}}"""

    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip()
    return json.loads(text)

# ─── Session state defaults ────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_id" not in st.session_state:
    st.session_state.user_id = None
if "user_role" not in st.session_state:
    st.session_state.user_role = None
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "login_mode" not in st.session_state:
    st.session_state.login_mode = None  # "student" or "admin"

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .stAppDeployButton { display: none; }
  .block-container { padding-top: 2rem; max-width: 760px; }

  /* Idea cards */
  .idea-card {
    background: #fff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 14px;
  }
  .idea-title { font-size: 15px; font-weight: 600; margin-bottom: 4px; }
  .idea-meta  { font-size: 12px; color: #6b7280; margin-top: 6px; }
  .idea-desc  { font-size: 13px; color: #374151; line-height: 1.6; margin-top: 6px; }
  .feedback-box {
    background: #f9fafb;
    border-left: 3px solid #d1d5db;
    border-radius: 6px;
    padding: 8px 12px;
    font-size: 13px;
    color: #4b5563;
    margin-top: 10px;
  }
  .stat-num { font-size: 28px; font-weight: 700; }
  .stat-lbl { font-size: 13px; color: #6b7280; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# LANDING / LOGIN
# ══════════════════════════════════════════════════════════════════════════════
def show_landing():
    st.markdown("## 💡 Project Idea Portal")
    st.caption("Submit and track your project ideas — unique, first-come first-served.")
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎓 Student Portal")
        st.caption("Submit ideas & track their status")
        if st.button("Student Login", use_container_width=True, key="btn_student"):
            st.session_state.login_mode = "student"
            st.rerun()
    with col2:
        st.markdown("### 🛡️ Admin Portal")
        st.caption("Review, approve, or reject ideas")
        if st.button("Admin Login", use_container_width=True, key="btn_admin"):
            st.session_state.login_mode = "admin"
            st.rerun()

    st.divider()
    with st.expander("ℹ️ Demo credentials"):
        st.markdown("""
| Role | ID / Username | Password |
|------|--------------|----------|
| Student | S001 | pass123 |
| Student | S002 | pass123 |
| Admin | admin | admin123 |
        """)

def show_login():
    mode = st.session_state.login_mode
    st.markdown(f"## {'🎓 Student' if mode == 'student' else '🛡️ Admin'} Login")

    uid = st.text_input("Student ID" if mode == "student" else "Username", placeholder="e.g. S001")
    pwd = st.text_input("Password", type="password")

    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("← Back"):
            st.session_state.login_mode = None
            st.rerun()
    with col2:
        if st.button("Sign In", type="primary", use_container_width=True):
            users = load_users()
            user = users.get(uid.strip())
            if not user or user["password"] != pwd:
                st.error("Invalid credentials.")
            elif mode == "admin" and user["role"] != "admin":
                st.error("This account is not an admin.")
            elif mode == "student" and user["role"] != "student":
                st.error("Please use the Admin portal.")
            else:
                st.session_state.logged_in = True
                st.session_state.user_id = uid.strip()
                st.session_state.user_role = user["role"]
                st.session_state.user_name = user["name"]
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# STUDENT PORTAL
# ══════════════════════════════════════════════════════════════════════════════
def show_student_portal():
    ideas = load_ideas()
    st.markdown(f"### 💡 Project Idea Portal &nbsp; <span style='font-size:14px;font-weight:400;color:#6b7280;'>Logged in as {st.session_state.user_name}</span>", unsafe_allow_html=True)

    if st.button("Sign Out", key="student_logout"):
        for k in ["logged_in","user_id","user_role","user_name","login_mode"]:
            st.session_state[k] = None if k != "logged_in" else False
        st.rerun()

    st.divider()
    tab1, tab2 = st.tabs(["📝 Submit Idea", "📋 My Ideas"])

    # ── Submit tab ──
    with tab1:
        st.markdown("#### Submit a New Project Idea")
        title = st.text_input("Idea Title", placeholder="A clear, concise title for your project idea", max_chars=120)
        desc  = st.text_area("Description", placeholder="Describe your project idea in detail...", max_chars=500, height=120)
        st.caption(f"{len(desc)}/500 characters")

        if st.button("🚀 Submit Idea", type="primary", disabled=not (title and desc)):
            approved = [i for i in ideas if i["status"] == "approved"]
            with st.spinner("Checking for similar ideas with AI..."):
                try:
                    result = check_similarity(title, desc, approved)
                except Exception as e:
                    result = {"isSimilar": False, "similarTo": None}
                    st.warning(f"Similarity check unavailable — submitting for manual review.")

            status   = "pending"
            feedback = ""
            if result["isSimilar"]:
                status   = "rejected"
                feedback = f'Automatically rejected: Similar to an already-approved idea — "{result["similarTo"]}". Please choose a different topic.'
                st.error(f"⚠️ Your idea is too similar to an existing approved idea: **\"{result['similarTo']}\"**. It has been auto-rejected.")
            else:
                st.success("✅ No similar ideas found. Submitted for admin review!")

            new_idea = {
                "id":          f"IDEA-{int(time.time()*1000)}",
                "studentId":   st.session_state.user_id,
                "studentName": st.session_state.user_name,
                "title":       title,
                "description": desc,
                "status":      status,
                "feedback":    feedback,
                "submittedAt": datetime.now().isoformat(),
                "reviewedAt":  datetime.now().isoformat() if status == "rejected" else None,
            }
            ideas.append(new_idea)
            save_ideas(ideas)
            time.sleep(1)
            st.rerun()

    # ── My Ideas tab ──
    with tab2:
        my_ideas = [i for i in ideas if i["studentId"] == st.session_state.user_id]
        my_ideas.sort(key=lambda x: x["submittedAt"], reverse=True)

        if not my_ideas:
            st.info("You haven't submitted any ideas yet. Go to **Submit Idea** to get started!")
        else:
            st.caption(f"{len(my_ideas)} idea(s) submitted")
            for idea in my_ideas:
                s = idea["status"]
                st.markdown(f"""
<div class="idea-card">
  <div class="idea-title">{idea['title']} &nbsp; {STATUS_COLORS[s]} {STATUS_LABELS[s]}</div>
  <div class="idea-desc">{idea['description']}</div>
  <div class="idea-meta">Submitted: {fmt_date(idea['submittedAt'])} &nbsp;·&nbsp; {idea['id']}</div>
  {"<div class='feedback-box'>💬 " + idea['feedback'] + "</div>" if idea.get('feedback') else ""}
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# ADMIN PORTAL
# ══════════════════════════════════════════════════════════════════════════════
def show_admin_portal():
    ideas = load_ideas()

    st.markdown("### 🛡️ Admin Dashboard")
    if st.button("Sign Out", key="admin_logout"):
        for k in ["logged_in","user_id","user_role","user_name","login_mode"]:
            st.session_state[k] = None if k != "logged_in" else False
        st.rerun()

    # Stats
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    counts = {s: sum(1 for i in ideas if i["status"] == s) for s in STATUS_LABELS}
    c1.metric("Total Ideas",    len(ideas))
    c2.metric("🟡 Pending",     counts["pending"])
    c3.metric("🟢 Approved",    counts["approved"])
    c4.metric("🔴 Rejected",    counts["rejected"] + counts["taken"])
    st.divider()

    tab1, tab2 = st.tabs([f"🟡 Pending Review ({counts['pending']})", "📂 All Ideas"])

    # ── Pending tab ──
    with tab1:
        search = st.text_input("Search", placeholder="Search by title or student...", key="search_pending")
        pending = [i for i in ideas if i["status"] == "pending"]
        pending.sort(key=lambda x: x["submittedAt"])  # oldest first = FCFS
        if search:
            q = search.lower()
            pending = [i for i in pending if q in i["title"].lower() or q in i["studentName"].lower()]

        if not pending:
            st.info("✅ No pending ideas to review.")
        else:
            for idea in pending:
                render_admin_card(idea, ideas)

    # ── All Ideas tab ──
    with tab2:
        col_s, col_f = st.columns([3, 1])
        with col_s:
            search_all = st.text_input("Search", placeholder="Search ideas...", key="search_all")
        with col_f:
            status_filter = st.selectbox("Status", ["All"] + list(STATUS_LABELS.values()), key="status_filter")

        all_ideas = sorted(ideas, key=lambda x: x["submittedAt"], reverse=True)
        if search_all:
            q = search_all.lower()
            all_ideas = [i for i in all_ideas if q in i["title"].lower() or q in i["studentName"].lower() or q in i["studentId"].lower()]
        if status_filter != "All":
            inv = {v: k for k, v in STATUS_LABELS.items()}
            all_ideas = [i for i in all_ideas if i["status"] == inv[status_filter]]

        if not all_ideas:
            st.info("No ideas found.")
        else:
            for idea in all_ideas:
                render_admin_card(idea, ideas)

def render_admin_card(idea, all_ideas):
    s = idea["status"]
    with st.container(border=True):
        col_t, col_b = st.columns([5, 1])
        with col_t:
            st.markdown(f"**{idea['title']}**")
            st.caption(f"👤 {idea['studentName']} ({idea['studentId']}) &nbsp;·&nbsp; 🕐 {fmt_date(idea['submittedAt'])} &nbsp;·&nbsp; `{idea['id']}`")
        with col_b:
            st.markdown(f"{STATUS_COLORS[s]} {STATUS_LABELS[s]}")

        st.markdown(f"<div style='font-size:13px;color:#374151;line-height:1.6;margin:6px 0'>{idea['description']}</div>", unsafe_allow_html=True)

        if idea.get("feedback"):
            st.markdown(f"<div class='feedback-box'>💬 {idea['feedback']}</div>", unsafe_allow_html=True)

        feedback_key = f"fb_{idea['id']}"
        if feedback_key not in st.session_state:
            st.session_state[feedback_key] = idea.get("feedback", "")

        fb = st.text_input("Feedback for student (optional)", value=st.session_state[feedback_key], key=f"fbi_{idea['id']}", placeholder="e.g. Great idea! / Too vague, please elaborate...")

        c1, c2, c3, c4 = st.columns(4)
        def set_status(new_status):
            for i in all_ideas:
                if i["id"] == idea["id"]:
                    i["status"] = new_status
                    i["feedback"] = fb
                    i["reviewedAt"] = datetime.now().isoformat()
            save_ideas(all_ideas)
            st.rerun()

        with c1:
            if st.button("✅ Approve",       key=f"ap_{idea['id']}", use_container_width=True): set_status("approved")
        with c2:
            if st.button("❌ Reject",         key=f"rj_{idea['id']}", use_container_width=True): set_status("rejected")
        with c3:
            if st.button("🔄 Needs Changes",  key=f"ch_{idea['id']}", use_container_width=True): set_status("changes")
        with c4:
            if st.button("⊘ Already Taken",   key=f"tk_{idea['id']}", use_container_width=True): set_status("taken")

# ══════════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    if st.session_state.login_mode:
        show_login()
    else:
        show_landing()
elif st.session_state.user_role == "admin":
    show_admin_portal()
else:
    show_student_portal()
