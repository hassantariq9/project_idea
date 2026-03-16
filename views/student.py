import streamlit as st
import time
from utils.auth import logout, get_current_user
from utils.db import (load_ideas, add_idea, fmt_date,
                      STATUS_COLORS, STATUS_LABELS,
                      get_user_notifications, mark_notifications_read,
                      add_notification, load_users)
from utils.ai_service import check_similarity, score_idea, suggest_ideas

def show_student_portal():
    user = get_current_user()
    uid  = user["id"]
    ideas = load_ideas()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"### 💡 IdeaVault")
        st.markdown(f"**{user['name']}**")
        st.caption(f"{user['dept']} · Student")
        st.divider()

        unread = len(get_user_notifications(uid, unread_only=True))
        notif_label = f"🔔 Notifications {'🔴' if unread else ''}"
        page = st.radio("Navigation", ["📝 Submit Idea", "📋 My Ideas", "🔮 AI Suggestions", notif_label], label_visibility="collapsed")
        st.divider()
        if st.button("Sign Out", use_container_width=True):
            logout()

    my_ideas = [i for i in ideas if i["studentId"] == uid]
    approved_count = sum(1 for i in ideas if i["status"] == "approved")

    # ── Pages ─────────────────────────────────────────────────────────────────
    if "Submit" in page:
        show_submit(user, ideas)
    elif "My Ideas" in page:
        show_my_ideas(my_ideas)
    elif "AI Suggestions" in page:
        show_suggestions(user, ideas)
    else:
        show_notifications(uid)

# ── Submit ────────────────────────────────────────────────────────────────────
def show_submit(user, ideas):
    st.markdown("## 📝 Submit a Project Idea")
    st.caption("Your idea will be checked for uniqueness by AI before reaching faculty review.")

    with st.form("submit_form", clear_on_submit=True):
        title = st.text_input("Idea Title *", placeholder="A clear, specific title", max_chars=120)
        desc  = st.text_area("Description *", placeholder="Describe what you want to build, the problem it solves, and your approach...", max_chars=600, height=130)
        st.caption(f"Be as specific as possible. Vague ideas may be asked for revisions.")
        submitted = st.form_submit_button("🚀 Submit Idea", type="primary")

    if submitted:
        if not title.strip() or not desc.strip():
            st.error("Please fill in both the title and description.")
            return

        col_spin, col_txt = st.columns([1, 8])
        status_placeholder = st.empty()

        # 1. Similarity check
        with status_placeholder.container():
            st.info("🤖 Step 1/2 — Checking for duplicate or similar ideas...")
        time.sleep(0.3)

        compare_against = [i for i in ideas if i["status"] in ("approved", "pending")]
        try:
            sim_result = check_similarity(title, desc, compare_against)
        except Exception as e:
            sim_result = {"isSimilar": False, "similarTo": None, "similarity_score": 0.0, "reason": ""}
            st.warning(f"Similarity check unavailable ({e}). Submitted for manual review.")

        # 2. AI scoring
        with status_placeholder.container():
            st.info("🤖 Step 2/2 — AI quality analysis...")
        time.sleep(0.3)

        try:
            score_result = score_idea(title, desc)
        except:
            score_result = None

        status_placeholder.empty()

        # Determine outcome
        if sim_result["isSimilar"] and sim_result.get("similarity_score", 0) > 0.75:
            final_status   = "auto_rejected"
            final_feedback = (f"Automatically rejected: This idea is {int(sim_result['similarity_score']*100)}% similar "
                              f"to \"{sim_result['similarTo']}\". {sim_result.get('reason','')}")
            st.error(f"⚠️ **Auto-rejected** — Your idea is too similar to an existing submission: **\"{sim_result['similarTo']}\"**")
            st.markdown(f'<div class="dup-warning">🔍 {sim_result.get("reason","")}</div>', unsafe_allow_html=True)
        else:
            final_status   = "pending"
            final_feedback = ""
            if sim_result.get("similarity_score", 0) > 0.4:
                st.warning(f"⚠️ Mild similarity ({int(sim_result['similarity_score']*100)}%) detected with \"{sim_result.get('similarTo','')}\" — but not a duplicate. Submitted for faculty review.")
            else:
                st.success("✅ No duplicates found! Your idea has been submitted for faculty review.")

        # Show AI score
        if score_result:
            sc = score_result.get("score", 0)
            color = "#10b981" if sc >= 7 else "#f59e0b" if sc >= 5 else "#ef4444"
            st.markdown(f"""
<div style="background:white;border:1px solid #e5e7eb;border-radius:12px;padding:16px 20px;margin:12px 0;">
  <div style="display:flex;align-items:center;justify-content:space-between;">
    <div>
      <div style="font-size:13px;font-weight:600;color:#374151;">AI Quality Score</div>
      <div style="font-size:12px;color:#6b7280;margin-top:4px;">Difficulty: {score_result.get('difficulty','?')} · ~{score_result.get('estimated_weeks','?')} weeks</div>
    </div>
    <div style="width:52px;height:52px;border-radius:50%;border:3px solid {color};display:flex;align-items:center;justify-content:center;font-size:18px;font-weight:700;color:{color};">{sc}/10</div>
  </div>
  <div style="margin-top:10px;font-size:12px;color:#4b5563;line-height:1.6;">
    <b>Strengths:</b> {' · '.join(score_result.get('strengths',[])) or 'N/A'}<br>
    <b>To improve:</b> {' · '.join(score_result.get('weaknesses',[])) or 'N/A'}<br>
    <b>Suggestion:</b> {score_result.get('suggestion','')}
  </div>
</div>""", unsafe_allow_html=True)

        # Save
        ai_tags = score_result.get("tags", []) if score_result else []
        idea = add_idea(
            student_id=user["id"],
            student_name=user["name"],
            title=title,
            description=desc,
            tags=ai_tags,
        )
        from utils.db import update_idea
        update_idea(idea["id"],
            status=final_status,
            feedback=final_feedback,
            similarity_score=sim_result.get("similarity_score", 0.0),
            similar_to=sim_result.get("similarTo"),
            ai_score=score_result.get("score") if score_result else None,
            ai_strengths=score_result.get("strengths", []) if score_result else [],
            ai_weaknesses=score_result.get("weaknesses", []) if score_result else [],
        )
        # Notify student
        add_notification(user["id"], "Idea Submitted",
            f'Your idea "{title}" was submitted. Status: {STATUS_LABELS.get(final_status, final_status)}',
            "success" if final_status == "pending" else "danger")

# ── My Ideas ──────────────────────────────────────────────────────────────────
def show_my_ideas(my_ideas):
    st.markdown("## 📋 My Submitted Ideas")

    if not my_ideas:
        st.info("You haven't submitted any ideas yet. Head to **Submit Idea** to get started!")
        return

    my_ideas = sorted(my_ideas, key=lambda x: x["submittedAt"], reverse=True)

    # Summary row
    c1, c2, c3, c4 = st.columns(4)
    from collections import Counter
    counts = Counter(i["status"] for i in my_ideas)
    c1.metric("Total Submitted", len(my_ideas))
    c2.metric("🟢 Approved", counts.get("approved", 0))
    c3.metric("🟡 Pending", counts.get("pending", 0))
    c4.metric("🔴 Rejected", counts.get("rejected", 0) + counts.get("auto_rejected", 0))

    st.divider()

    for idea in my_ideas:
        s  = idea["status"]
        icon, color, bg = STATUS_COLORS.get(s, ("⬜","#6b7280","#f9fafb"))
        sc = idea.get("ai_score")
        score_html = ""
        if sc is not None:
            sc_color = "#10b981" if sc >= 7 else "#f59e0b" if sc >= 5 else "#ef4444"
            score_html = f'<div style="float:right;width:44px;height:44px;border-radius:50%;border:2.5px solid {sc_color};display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700;color:{sc_color};">{sc}/10</div>'

        tags_html = "".join(f'<span class="tag-pill">{t}</span>' for t in idea.get("tags", []))
        cluster_html = f'<span class="cluster-pill">{idea.get("cluster","Uncategorized")}</span>' if idea.get("cluster") else ""

        st.markdown(f"""
<div class="iv-card">
  {score_html}
  <div class="iv-card-title">{idea['title']}</div>
  <span class="badge badge-{s}">{icon} {STATUS_LABELS.get(s, s)}</span>
  {cluster_html} {tags_html}
  <div class="iv-card-desc">{idea['description']}</div>
  <div class="iv-card-meta">Submitted: {fmt_date(idea['submittedAt'])} · {idea['id']}</div>
  {"<div class='feedback-box'>💬 <b>Faculty feedback:</b> " + idea['feedback'] + "</div>" if idea.get('feedback') else ""}
  {f"<div style='font-size:12px;color:#9ca3af;margin-top:6px;'>Similar to: <i>{idea['similar_to']}</i> ({int(idea.get('similarity_score',0)*100)}% similarity)</div>" if idea.get('similar_to') else ""}
</div>""", unsafe_allow_html=True)

# ── AI Suggestions ────────────────────────────────────────────────────────────
def show_suggestions(user, ideas):
    st.markdown("## 🔮 AI Project Idea Suggestions")
    st.caption("Get personalized project idea suggestions based on your department and existing submissions.")

    existing_titles = [i["title"] for i in ideas if i["status"] in ("approved","pending")]

    col1, col2 = st.columns([3, 1])
    with col1:
        num = st.slider("Number of suggestions", 3, 8, 5)
    with col2:
        st.markdown("")
        generate = st.button("✨ Generate Ideas", type="primary", use_container_width=True)

    if generate:
        with st.spinner("AI is generating fresh ideas for you..."):
            try:
                suggestions = suggest_ideas(
                    department=user["dept"] or "Computer Science",
                    batch=st.session_state.get("user_batch", "final year"),
                    existing_titles=existing_titles,
                    num=num
                )
            except Exception as e:
                st.error(f"Could not generate suggestions: {e}")
                return

        st.success(f"Here are {len(suggestions)} fresh ideas for you:")
        for s in suggestions:
            diff_colors = {"Easy": "#10b981", "Medium": "#f59e0b", "Hard": "#ef4444"}
            dc = diff_colors.get(s.get("difficulty","Medium"), "#6b7280")
            tags_html = "".join(f'<span class="tag-pill">{t}</span>' for t in s.get("tags", []))
            st.markdown(f"""
<div class="iv-card" style="border-left: 4px solid {dc};">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:6px;">
    <div class="iv-card-title">{s['title']}</div>
    <span style="font-size:11px;font-weight:600;color:{dc};background:{dc}22;padding:3px 10px;border-radius:20px;">{s.get('difficulty','Medium')}</span>
  </div>
  <div class="iv-card-desc">{s['description']}</div>
  <div style="margin-top:8px;">{tags_html}</div>
  <div style="font-size:12px;color:#6366f1;margin-top:8px;">💡 {s.get('why_good','')}</div>
</div>""", unsafe_allow_html=True)
        st.caption("Like an idea? Copy the title and description into the **Submit Idea** form.")

# ── Notifications ─────────────────────────────────────────────────────────────
def show_notifications(uid):
    st.markdown("## 🔔 Notifications")
    notifs = get_user_notifications(uid)
    if not notifs:
        st.info("No notifications yet.")
        return

    unread = [n for n in notifs if not n["read"]]
    if unread:
        if st.button(f"Mark all {len(unread)} as read"):
            mark_notifications_read(uid)
            st.rerun()

    type_icons = {"success":"✅","danger":"🔴","warning":"⚠️","info":"ℹ️"}
    type_bgs   = {"success":"#d1fae5","danger":"#fee2e2","warning":"#fef3c7","info":"#dbeafe"}

    for n in notifs:
        t    = n.get("type","info")
        icon = type_icons.get(t,"ℹ️")
        bg   = type_bgs.get(t,"#f9fafb")
        unread_dot = "🔵 " if not n["read"] else ""
        st.markdown(f"""
<div style="background:{bg};border-radius:10px;padding:12px 16px;margin-bottom:10px;">
  <div style="font-size:13px;font-weight:600;color:#111827;">{unread_dot}{icon} {n['title']}</div>
  <div style="font-size:13px;color:#374151;margin-top:4px;">{n['message']}</div>
  <div style="font-size:11px;color:#9ca3af;margin-top:6px;">{fmt_date(n['createdAt'])}</div>
</div>""", unsafe_allow_html=True)
