import streamlit as st
from utils.auth import logout, get_current_user
from utils.db import (load_ideas, update_idea, save_ideas, fmt_date,
                      STATUS_COLORS, STATUS_LABELS, load_users,
                      add_notification, get_user_notifications, mark_notifications_read)
from utils.ai_service import generate_feedback, send_email_notification

def show_faculty_portal():
    user  = get_current_user()
    uid   = user["id"]
    ideas = load_ideas()
    users = load_users()

    with st.sidebar:
        st.markdown("### 💡 IdeaVault")
        st.markdown(f"**{user['name']}**")
        st.caption(f"{user['dept']} · Faculty")
        st.divider()
        unread = len(get_user_notifications(uid, unread_only=True))
        page = st.radio("Navigation", [
            "🟡 Pending Review",
            "✅ Approved",
            "📂 All Ideas",
            f"🔔 Notifications {'🔴' if unread else ''}",
        ], label_visibility="collapsed")
        st.divider()
        if st.button("Sign Out", use_container_width=True):
            logout()

    # Filter to faculty's department (or show all if dept not set)
    dept = user.get("dept","")
    my_ideas = [i for i in ideas if not dept or _student_dept(i["studentId"], users) == dept or not _student_dept(i["studentId"], users)]

    if "Pending" in page:
        show_faculty_review(my_ideas, users, ideas)
    elif "Approved" in page:
        show_filtered(my_ideas, "approved")
    elif "All Ideas" in page:
        show_filtered(my_ideas, None)
    else:
        show_notifs(uid)

def _student_dept(student_id, users):
    return users.get(student_id, {}).get("department","")

def show_faculty_review(my_ideas, users, all_ideas):
    st.markdown("## 🟡 Ideas Pending Review")
    pending = [i for i in my_ideas if i["status"] == "pending"]
    pending.sort(key=lambda x: x["submittedAt"])  # FCFS

    if not pending:
        st.success("✅ All caught up! No pending ideas in your department.")
        return

    st.caption(f"{len(pending)} idea(s) awaiting review · Sorted by submission time (first-come, first-served)")

    for idea in pending:
        render_review_card(idea, all_ideas, users)

def render_review_card(idea, all_ideas, users):
    sc = idea.get("ai_score")
    score_color = "#10b981" if sc and sc >= 7 else "#f59e0b" if sc and sc >= 5 else "#ef4444"
    tags_html = "".join(f'<span class="tag-pill">{t}</span>' for t in idea.get("tags",[]))
    cluster_html = f'<span class="cluster-pill">{idea.get("cluster","Uncategorized")}</span>'

    with st.container(border=True):
        col_main, col_score = st.columns([5, 1])
        with col_main:
            st.markdown(f"**{idea['title']}**")
            st.caption(f"👤 {idea['studentName']} ({idea['studentId']}) · 🕐 {fmt_date(idea['submittedAt'])} · {idea['id']}")
        with col_score:
            if sc:
                st.markdown(f"<div style='text-align:center;font-size:20px;font-weight:700;color:{score_color};'>AI: {sc}/10</div>", unsafe_allow_html=True)

        st.markdown(f"<div style='font-size:13px;color:#374151;line-height:1.65;margin:8px 0;'>{idea['description']}</div>", unsafe_allow_html=True)
        st.markdown(f"{cluster_html} {tags_html}", unsafe_allow_html=True)

        if idea.get("ai_strengths"):
            with st.expander("🤖 AI Analysis"):
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown("**Strengths**")
                    for s in idea["ai_strengths"]: st.markdown(f"- {s}")
                with c2:
                    st.markdown("**Weaknesses**")
                    for w in idea["ai_weaknesses"]: st.markdown(f"- {w}")

        if idea.get("similar_to"):
            st.warning(f"⚠️ AI flagged {int(idea.get('similarity_score',0)*100)}% similarity with: \"{idea['similar_to']}\"")

        # Feedback
        fb_key = f"fb_{idea['id']}"
        if fb_key not in st.session_state:
            st.session_state[fb_key] = idea.get("feedback","")

        col_fb, col_ai = st.columns([4,1])
        with col_fb:
            fb = st.text_area("Feedback to student", value=st.session_state[fb_key], key=f"fbi_{idea['id']}", height=80, placeholder="Explain your decision...")
        with col_ai:
            st.markdown("")
            st.markdown("")
            if st.button("✨ AI Draft", key=f"aidr_{idea['id']}", help="Generate AI feedback"):
                with st.spinner("Drafting..."):
                    try:
                        drafted = generate_feedback(idea["title"], idea["description"], "needs_review")
                        st.session_state[fb_key] = drafted
                        st.rerun()
                    except:
                        st.error("AI draft failed.")

        c1, c2, c3, c4 = st.columns(4)
        def do_action(new_status):
            update_idea(idea["id"], status=new_status, feedback=fb)
            student = users.get(idea["studentId"], {})
            label   = STATUS_LABELS.get(new_status, new_status)
            add_notification(idea["studentId"], f"Idea {label}",
                f'Your idea "{idea["title"]}" has been {label.lower()}. {fb[:100] if fb else ""}',
                "success" if new_status == "approved" else "warning" if new_status == "changes" else "danger")
            send_email_notification(
                student.get("email",""),
                student.get("name","Student"),
                f"Project Idea Update — {label}",
                f"<p>Your idea <b>\"{idea['title']}\"</b> has been <b>{label}</b>.</p>"
                + (f"<p>Feedback: {fb}</p>" if fb else "")
            )
            st.rerun()

        with c1:
            if st.button("✅ Approve",        key=f"ap_{idea['id']}", use_container_width=True): do_action("approved")
        with c2:
            if st.button("❌ Reject",          key=f"rj_{idea['id']}", use_container_width=True): do_action("rejected")
        with c3:
            if st.button("🔄 Needs Changes",   key=f"ch_{idea['id']}", use_container_width=True): do_action("changes")
        with c4:
            if st.button("⊘ Already Taken",    key=f"tk_{idea['id']}", use_container_width=True): do_action("taken")

def show_filtered(ideas, status_filter):
    label = "Approved Ideas" if status_filter == "approved" else "All Ideas"
    st.markdown(f"## 📂 {label}")

    filtered = [i for i in ideas if (not status_filter or i["status"] == status_filter)]
    filtered.sort(key=lambda x: x["submittedAt"], reverse=True)

    if not filtered:
        st.info("No ideas found.")
        return

    search = st.text_input("Search", placeholder="Search by title or student...")
    if search:
        q = search.lower()
        filtered = [i for i in filtered if q in i["title"].lower() or q in i["studentName"].lower()]

    for idea in filtered:
        s = idea["status"]
        icon, color, bg = STATUS_COLORS.get(s, ("⬜","#6b7280","#f9fafb"))
        tags_html = "".join(f'<span class="tag-pill">{t}</span>' for t in idea.get("tags",[]))
        st.markdown(f"""
<div class="iv-card">
  <div class="iv-card-title">{idea['title']} &nbsp; <span class="badge badge-{s}">{icon} {STATUS_LABELS.get(s,s)}</span></div>
  <div style="font-size:12px;color:#9ca3af;">👤 {idea['studentName']} · {fmt_date(idea['submittedAt'])}</div>
  <div class="iv-card-desc">{idea['description']}</div>
  {tags_html}
  {"<div class='feedback-box'>💬 " + idea['feedback'] + "</div>" if idea.get('feedback') else ""}
</div>""", unsafe_allow_html=True)

def show_notifs(uid):
    st.markdown("## 🔔 Notifications")
    notifs = get_user_notifications(uid)
    if not notifs:
        st.info("No notifications.")
        return
    unread = [n for n in notifs if not n["read"]]
    if unread:
        if st.button(f"Mark all {len(unread)} read"):
            mark_notifications_read(uid)
            st.rerun()
    for n in notifs:
        st.markdown(f"""
<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:12px 16px;margin-bottom:10px;">
  <div style="font-weight:600;font-size:13px;">{"🔵 " if not n["read"] else ""}{n['title']}</div>
  <div style="font-size:13px;color:#374151;margin-top:4px;">{n['message']}</div>
  <div style="font-size:11px;color:#9ca3af;margin-top:6px;">{fmt_date(n['createdAt'])}</div>
</div>""", unsafe_allow_html=True)
