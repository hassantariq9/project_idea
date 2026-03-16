import streamlit as st
import json
import io
import time
from collections import Counter
from datetime import datetime, timedelta
from utils.auth import logout, get_current_user
from utils.db import (load_ideas, save_ideas, update_idea, fmt_date,
                      STATUS_COLORS, STATUS_LABELS, load_users, save_users,
                      add_notification, bulk_add_students, add_user, hash_pw)
from utils.ai_service import cluster_ideas, send_email_notification

def show_admin_portal():
    user  = get_current_user()
    ideas = load_ideas()
    users = load_users()

    with st.sidebar:
        st.markdown("### 💡 IdeaVault")
        st.markdown(f"**{user['name']}**")
        st.caption("System Administrator")
        st.divider()
        page = st.radio("Navigation", [
            "📊 Dashboard",
            "🔍 Visual Duplicates",
            "🗂️ Clusters",
            "📋 All Ideas",
            "👥 User Management",
            "📤 Bulk Import",
            "⚙️ Settings",
        ], label_visibility="collapsed")
        st.divider()
        if st.button("Sign Out", use_container_width=True):
            logout()

    if   "Dashboard"   in page: show_dashboard(ideas, users)
    elif "Duplicate"   in page: show_duplicates(ideas)
    elif "Cluster"     in page: show_clusters(ideas)
    elif "All Ideas"   in page: show_all_ideas(ideas, users)
    elif "User"        in page: show_user_mgmt(users)
    elif "Bulk"        in page: show_bulk_import()
    else:                        show_settings(users)

# ── Dashboard ─────────────────────────────────────────────────────────────────
def show_dashboard(ideas, users):
    st.markdown("## 📊 Dashboard Analytics")

    total     = len(ideas)
    pending   = sum(1 for i in ideas if i["status"] == "pending")
    approved  = sum(1 for i in ideas if i["status"] == "approved")
    rejected  = sum(1 for i in ideas if i["status"] in ("rejected","auto_rejected"))
    changes   = sum(1 for i in ideas if i["status"] == "changes")
    taken     = sum(1 for i in ideas if i["status"] == "taken")
    students  = sum(1 for u in users.values() if u["role"] == "student")
    faculty   = sum(1 for u in users.values() if u["role"] == "faculty")

    # KPI row
    cols = st.columns(6)
    kpis = [
        ("Total Ideas",    total,    ""),
        ("🟡 Pending",     pending,  ""),
        ("🟢 Approved",    approved, ""),
        ("🔴 Rejected",    rejected, ""),
        ("🎓 Students",    students, ""),
        ("👨‍🏫 Faculty",    faculty,  ""),
    ]
    for col, (label, val, delta) in zip(cols, kpis):
        with col:
            st.metric(label, val)

    st.divider()

    # Charts row
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("#### Status Distribution")
        status_data = {"Pending": pending, "Approved": approved, "Rejected": rejected, "Changes": changes, "Taken": taken}
        status_data = {k:v for k,v in status_data.items() if v > 0}
        if status_data:
            import streamlit as st
            chart_data = {"Status": list(status_data.keys()), "Count": list(status_data.values())}
            st.bar_chart(chart_data, x="Status", y="Count", use_container_width=True)

    with col_right:
        st.markdown("#### Submissions Over Time (Last 30 days)")
        now = datetime.now()
        day_counts = Counter()
        for idea in ideas:
            try:
                d = datetime.fromisoformat(idea["submittedAt"])
                if (now - d).days <= 30:
                    day_counts[d.strftime("%b %d")] += 1
            except: pass
        if day_counts:
            import pandas as pd
            dates = sorted(day_counts.keys())
            df = pd.DataFrame({"Date": dates, "Submissions": [day_counts[d] for d in dates]})
            st.line_chart(df.set_index("Date"), use_container_width=True)
        else:
            st.info("No submission data yet.")

    st.divider()

    # Department breakdown
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Ideas by Department")
        all_users = load_users()
        dept_counts = Counter()
        for idea in ideas:
            dept = all_users.get(idea["studentId"], {}).get("department", "Unknown")
            dept_counts[dept] += 1
        if dept_counts:
            import pandas as pd
            df = pd.DataFrame({"Department": list(dept_counts.keys()), "Ideas": list(dept_counts.values())})
            st.bar_chart(df.set_index("Department"), use_container_width=True)

    with col2:
        st.markdown("#### Cluster Distribution")
        cluster_counts = Counter(i.get("cluster","Uncategorized") for i in ideas)
        if cluster_counts:
            import pandas as pd
            df = pd.DataFrame({"Cluster": list(cluster_counts.keys()), "Count": list(cluster_counts.values())})
            st.bar_chart(df.set_index("Cluster"), use_container_width=True)

    st.divider()

    # Recent activity
    st.markdown("#### Recent Activity")
    recent = sorted(ideas, key=lambda x: x["submittedAt"], reverse=True)[:10]
    for i in recent:
        s = i["status"]
        icon = STATUS_COLORS.get(s, ("⬜","",""))[0]
        st.markdown(f"""
<div style="display:flex;align-items:center;gap:12px;padding:8px 0;border-bottom:1px solid #f3f4f6;">
  <div style="font-size:18px;">{icon}</div>
  <div style="flex:1;">
    <div style="font-size:13px;font-weight:500;color:#111827;">{i['title']}</div>
    <div style="font-size:12px;color:#9ca3af;">{i['studentName']} · {fmt_date(i['submittedAt'])}</div>
  </div>
  <span class="badge badge-{s}">{STATUS_LABELS.get(s,s)}</span>
</div>""", unsafe_allow_html=True)

# ── Visual Duplicates ─────────────────────────────────────────────────────────
def show_duplicates(ideas):
    st.markdown("## 🔍 Visual Duplicate Detection")
    st.caption("Ideas with similarity scores above threshold are flagged here.")

    threshold = st.slider("Similarity threshold", 0.3, 1.0, 0.5, 0.05)
    flagged = [i for i in ideas if i.get("similarity_score", 0) >= threshold and i.get("similar_to")]
    flagged.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)

    if not flagged:
        st.success(f"✅ No ideas exceed {int(threshold*100)}% similarity threshold.")
    else:
        st.warning(f"⚠️ {len(flagged)} idea(s) flagged above {int(threshold*100)}% similarity")

    for idea in flagged:
        score    = idea.get("similarity_score", 0)
        pct      = int(score * 100)
        bar_color = "#ef4444" if pct > 75 else "#f59e0b" if pct > 50 else "#6366f1"
        s = idea["status"]

        with st.container(border=True):
            col1, col2 = st.columns([3,1])
            with col1:
                st.markdown(f"**{idea['title']}** &nbsp; <span class='badge badge-{s}'>{STATUS_LABELS.get(s,s)}</span>", unsafe_allow_html=True)
                st.caption(f"👤 {idea['studentName']} · {fmt_date(idea['submittedAt'])}")
                st.markdown(f"<div style='font-size:13px;color:#4b5563;margin:6px 0;'>{idea['description'][:200]}...</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div style='text-align:center;'><div style='font-size:28px;font-weight:700;color:{bar_color};'>{pct}%</div><div style='font-size:12px;color:#6b7280;'>Similarity</div></div>", unsafe_allow_html=True)

            st.markdown(f"""
<div class="sim-bar-wrap">
  <div class="sim-bar" style="width:{pct}%;background:{bar_color};"></div>
</div>
<div style="font-size:12px;color:#6b7280;margin-top:4px;">Similar to: <i>"{idea.get('similar_to','')}"</i></div>
""", unsafe_allow_html=True)

            if idea["status"] == "pending":
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Override — Approve anyway", key=f"ov_ap_{idea['id']}"):
                        update_idea(idea["id"], status="approved")
                        add_notification(idea["studentId"], "Idea Approved",
                            f'Your idea "{idea["title"]}" was approved despite similarity flag.', "success")
                        st.rerun()
                with c2:
                    if st.button("❌ Confirm Rejection", key=f"ov_rj_{idea['id']}"):
                        update_idea(idea["id"], status="rejected",
                            feedback=f"Rejected: Too similar to existing idea \"{idea.get('similar_to','')}\".")
                        add_notification(idea["studentId"], "Idea Rejected",
                            f'Your idea "{idea["title"]}" was rejected due to similarity.', "danger")
                        st.rerun()

# ── Clusters ──────────────────────────────────────────────────────────────────
def show_clusters(ideas):
    st.markdown("## 🗂️ Idea Clusters")

    col1, col2 = st.columns([3,1])
    with col1:
        st.caption("Ideas are automatically grouped by topic. Run AI clustering to update groups.")
    with col2:
        if st.button("🤖 Re-cluster All", type="primary", use_container_width=True):
            with st.spinner("AI is clustering all ideas..."):
                try:
                    results = cluster_ideas(ideas)
                    id_map  = {r["id"]: r for r in results}
                    for idea in ideas:
                        if idea["id"] in id_map:
                            idea["cluster"] = id_map[idea["id"]]["cluster"]
                            idea["tags"]    = id_map[idea["id"]].get("tags", idea.get("tags",[]))
                    save_ideas(ideas)
                    st.success("✅ Clustering complete!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Clustering failed: {e}")

    from collections import defaultdict
    clusters = defaultdict(list)
    for idea in ideas:
        clusters[idea.get("cluster","Uncategorized")].append(idea)

    for cluster_name, cluster_ideas_list in sorted(clusters.items(), key=lambda x: -len(x[1])):
        with st.expander(f"📁 {cluster_name} ({len(cluster_ideas_list)} ideas)", expanded=False):
            for idea in sorted(cluster_ideas_list, key=lambda x: x["submittedAt"]):
                s = idea["status"]
                icon = STATUS_COLORS.get(s, ("⬜","",""))[0]
                tags_html = "".join(f'<span class="tag-pill">{t}</span>' for t in idea.get("tags",[]))
                st.markdown(f"""
<div style="padding:10px 0;border-bottom:1px solid #f3f4f6;">
  <div style="display:flex;align-items:center;gap:8px;">
    <span>{icon}</span>
    <span style="font-size:13px;font-weight:500;">{idea['title']}</span>
    <span class="badge badge-{s}" style="font-size:10px;">{STATUS_LABELS.get(s,s)}</span>
  </div>
  <div style="font-size:12px;color:#6b7280;margin-top:4px;">{idea['studentName']} · {fmt_date(idea['submittedAt'])}</div>
  <div style="margin-top:4px;">{tags_html}</div>
</div>""", unsafe_allow_html=True)

# ── All Ideas ─────────────────────────────────────────────────────────────────
def show_all_ideas(ideas, users):
    st.markdown("## 📋 All Ideas")

    col1, col2, col3 = st.columns([3,1,1])
    with col1:
        search = st.text_input("Search", placeholder="Search title, student, ID...")
    with col2:
        sf = st.selectbox("Status", ["All"] + list(STATUS_LABELS.values()))
    with col3:
        sort = st.selectbox("Sort", ["Newest first","Oldest first","AI Score"])

    filtered = list(ideas)
    if search:
        q = search.lower()
        filtered = [i for i in filtered if q in i["title"].lower() or q in i["studentName"].lower() or q in i["id"].lower() or q in i["studentId"].lower()]
    if sf != "All":
        inv = {v:k for k,v in STATUS_LABELS.items()}
        filtered = [i for i in filtered if i["status"] == inv.get(sf, sf)]
    if sort == "Oldest first":
        filtered.sort(key=lambda x: x["submittedAt"])
    elif sort == "AI Score":
        filtered.sort(key=lambda x: x.get("ai_score") or 0, reverse=True)
    else:
        filtered.sort(key=lambda x: x["submittedAt"], reverse=True)

    st.caption(f"{len(filtered)} idea(s) found")

    # Export
    if filtered and st.button("⬇️ Export CSV"):
        import pandas as pd
        df = pd.DataFrame([{
            "ID": i["id"], "Title": i["title"], "Student": i["studentName"],
            "Student ID": i["studentId"], "Status": i["status"],
            "Cluster": i.get("cluster",""), "AI Score": i.get("ai_score",""),
            "Submitted": fmt_date(i["submittedAt"]), "Feedback": i.get("feedback","")
        } for i in filtered])
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "ideas_export.csv", "text/csv")

    for idea in filtered:
        s = idea["status"]
        icon = STATUS_COLORS.get(s, ("⬜","",""))[0]
        sc   = idea.get("ai_score")
        sc_html = f"<b style='color:#6366f1;'>AI: {sc}/10</b>" if sc else ""
        tags_html = "".join(f'<span class="tag-pill">{t}</span>' for t in idea.get("tags",[]))
        st.markdown(f"""
<div class="iv-card">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;">
    <div style="flex:1;">
      <div class="iv-card-title">{idea['title']}</div>
      <div style="font-size:12px;color:#9ca3af;margin-top:2px;">
        {idea['studentName']} ({idea['studentId']}) · {fmt_date(idea['submittedAt'])} · {idea['id']}
      </div>
    </div>
    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:4px;">
      <span class="badge badge-{s}">{icon} {STATUS_LABELS.get(s,s)}</span>
      <div style="font-size:12px;">{sc_html}</div>
    </div>
  </div>
  <div class="iv-card-desc">{idea['description']}</div>
  <div style="margin-top:6px;"><span class="cluster-pill">{idea.get('cluster','Uncategorized')}</span> {tags_html}</div>
  {"<div class='feedback-box'>💬 " + idea['feedback'] + "</div>" if idea.get("feedback") else ""}
</div>""", unsafe_allow_html=True)

# ── User Management ───────────────────────────────────────────────────────────
def show_user_mgmt(users):
    st.markdown("## 👥 User Management")

    tab1, tab2 = st.tabs(["All Users", "Add New User"])

    with tab1:
        role_filter = st.selectbox("Filter by role", ["All","student","faculty","admin"])
        search = st.text_input("Search by name or ID", placeholder="Search...")

        filtered = {uid: u for uid, u in users.items()
                    if (role_filter == "All" or u["role"] == role_filter)
                    and (not search or search.lower() in uid.lower() or search.lower() in u["name"].lower())}

        st.caption(f"{len(filtered)} user(s)")
        role_icons = {"student":"🎓","faculty":"👨‍🏫","admin":"🛡️"}

        for uid, u in sorted(filtered.items(), key=lambda x: x[1]["role"]):
            with st.container(border=True):
                c1, c2, c3 = st.columns([3,2,1])
                with c1:
                    st.markdown(f"**{role_icons.get(u['role'],'👤')} {u['name']}** `{uid}`")
                    st.caption(f"✉️ {u.get('email','—')} · {u.get('department','—')}")
                with c2:
                    st.caption(f"Role: **{u['role'].title()}** · Batch: {u.get('batch','—')}")
                with c3:
                    if u["role"] != "admin":
                        if st.button("🗑️ Remove", key=f"del_{uid}"):
                            del users[uid]
                            save_users(users)
                            st.success(f"Removed {uid}")
                            st.rerun()

    with tab2:
        st.markdown("#### Add a Single User")
        with st.form("add_user_form"):
            c1, c2 = st.columns(2)
            with c1:
                new_uid  = st.text_input("User ID *", placeholder="e.g. S100")
                new_name = st.text_input("Full Name *")
                new_role = st.selectbox("Role", ["student","faculty","admin"])
            with c2:
                new_email = st.text_input("Email")
                new_dept  = st.text_input("Department", placeholder="Computer Science")
                new_batch = st.text_input("Batch / Year", placeholder="2024")
            new_pass = st.text_input("Password", type="password", value="Student@123")
            if st.form_submit_button("➕ Add User", type="primary"):
                if not new_uid or not new_name:
                    st.error("ID and Name are required.")
                else:
                    ok, msg = add_user(new_uid, new_name, new_email, new_role, new_pass, new_dept, new_batch)
                    if ok: st.success(msg)
                    else:  st.error(msg)

# ── Bulk Import ───────────────────────────────────────────────────────────────
def show_bulk_import():
    st.markdown("## 📤 Bulk Student Import")
    st.caption("Upload a CSV or JSON file to add multiple students at once.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### CSV Format")
        st.code("uid,name,email,department,batch,password\nS100,John Doe,john@uni.edu,CS,2024,Student@123", language="csv")
    with col2:
        st.markdown("#### JSON Format")
        st.code('[{"uid":"S100","name":"John","email":"j@uni.edu","department":"CS","batch":"2024","password":"pass"}]', language="json")

    uploaded = st.file_uploader("Upload CSV or JSON", type=["csv","json"])
    if uploaded:
        try:
            if uploaded.name.endswith(".csv"):
                import pandas as pd
                df = pd.read_csv(uploaded)
                rows = df.to_dict("records")
            else:
                rows = json.load(uploaded)

            st.info(f"Preview: {len(rows)} users found")
            import pandas as pd
            st.dataframe(pd.DataFrame(rows).head(10), use_container_width=True)

            if st.button("✅ Import All", type="primary"):
                added, skipped = bulk_add_students(rows)
                st.success(f"✅ Added {added} students. Skipped {skipped} duplicates.")
        except Exception as e:
            st.error(f"Error reading file: {e}")

    st.divider()
    st.markdown("#### Send Bulk Email")
    st.caption("Notify all students or a filtered group.")

    recipients = st.multiselect("Send to", ["All Students","All Faculty"])
    subject    = st.text_input("Email Subject")
    body_text  = st.text_area("Email Body (plain text)", height=120)

    if st.button("📧 Send Email") and recipients and subject:
        all_users = load_users()
        targets = []
        if "All Students" in recipients:
            targets += [u for u in all_users.values() if u["role"] == "student"]
        if "All Faculty" in recipients:
            targets += [u for u in all_users.values() if u["role"] == "faculty"]

        sent = 0
        with st.spinner(f"Sending to {len(targets)} recipients..."):
            for u in targets:
                ok, _ = send_email_notification(u.get("email",""), u.get("name",""), subject, f"<p>{body_text}</p>")
                if ok: sent += 1
                add_notification(
                    next((k for k,v in all_users.items() if v==u), ""),
                    subject, body_text, "info"
                )
        st.success(f"✅ Sent to {sent}/{len(targets)} users (in-app notifications sent to all).")

# ── Settings ──────────────────────────────────────────────────────────────────
def show_settings(users):
    st.markdown("## ⚙️ Settings")

    st.markdown("#### Change Admin Password")
    with st.form("change_pass"):
        old_pass = st.text_input("Current password", type="password")
        new_pass = st.text_input("New password", type="password")
        new_pass2 = st.text_input("Confirm new password", type="password")
        if st.form_submit_button("Update Password"):
            from utils.db import verify_pw
            admin = users.get("admin",{})
            if not verify_pw(old_pass, admin.get("password","")):
                st.error("Current password incorrect.")
            elif new_pass != new_pass2:
                st.error("Passwords don't match.")
            elif len(new_pass) < 8:
                st.error("Password must be at least 8 characters.")
            else:
                users["admin"]["password"] = hash_pw(new_pass)
                save_users(users)
                st.success("✅ Password updated.")

    st.divider()
    st.markdown("#### Email Configuration")
    st.caption("Set SMTP credentials in Streamlit Secrets to enable real email delivery.")
    st.code("""# .streamlit/secrets.toml
ANTHROPIC_API_KEY = "sk-ant-..."
SMTP_HOST  = "smtp.gmail.com"
SMTP_PORT  = "587"
SMTP_USER  = "your@gmail.com"
SMTP_PASS  = "your-app-password"
FROM_EMAIL = "noreply@university.edu"
""", language="toml")

    st.divider()
    st.markdown("#### Data Management")
    col1, col2 = st.columns(2)
    with col1:
        ideas = load_ideas()
        if ideas:
            import json
            st.download_button("⬇️ Export All Ideas (JSON)", json.dumps(ideas, indent=2),
                               "ideas_backup.json", "application/json")
    with col2:
        if st.button("🗑️ Clear All Ideas", type="secondary"):
            st.session_state["confirm_clear"] = True
        if st.session_state.get("confirm_clear"):
            st.warning("Are you sure? This cannot be undone.")
            if st.button("Yes, delete all ideas", type="primary"):
                save_ideas([])
                st.session_state["confirm_clear"] = False
                st.success("All ideas cleared.")
                st.rerun()
