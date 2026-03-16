# 💡 IdeaVault — University Project Idea Portal v2

A powerful Streamlit application for managing student project idea submissions.

## ✨ Features

| Feature | Details |
|---------|---------|
| 🎓 Student Portal | Submit ideas, get instant AI feedback & quality score, track status, get AI suggestions |
| 👨‍🏫 Faculty Panel | Review assigned ideas, one-click decisions, AI-drafted feedback, department filtering |
| 🛡️ Admin Dashboard | Full analytics, charts, user management, bulk import, data export |
| 🤖 AI Similarity | Semantic duplicate detection — auto-rejects ideas above similarity threshold |
| 🗂️ Auto Clustering | AI groups ideas into topic clusters (Web Dev, ML, IoT, etc.) |
| 🔍 Visual Duplicates | Admin sees similarity scores with visual bars, can override AI decisions |
| 🔔 Notifications | In-app notification bell with unread badge; email via SMTP |
| 📧 Email | SMTP integration (Gmail/SendGrid) for status change emails |
| 📊 Analytics | Submission trends, department breakdown, cluster distribution charts |
| 📤 Bulk Import | CSV/JSON upload to add hundreds of students at once |
| ⬇️ CSV Export | Download all ideas as CSV for offline analysis |

## 🔑 Default Credentials

| Role | Username | Password |
|------|----------|----------|
| Admin | admin | Admin@2024 |
| Faculty | dr_smith | Faculty@123 |
| Faculty | dr_khan | Faculty@123 |
| Student | S001 | Student@123 |
| Student | S002 | Student@123 |
| Student | S003 | Student@123 |

**⚠️ Change the admin password immediately after first login (Settings page).**

## 🚀 Deploy on Streamlit Community Cloud (Free)

### Step 1 — GitHub
1. Create a GitHub account at github.com
2. Create a new **public** repository named `ideavault`
3. Upload ALL these files maintaining the folder structure:
   ```
   app.py
   requirements.txt
   utils/__init__.py
   utils/auth.py
   utils/db.py
   utils/ai_service.py
   utils/styles.py
   views/__init__.py
   views/landing.py
   views/login.py
   views/student.py
   views/faculty.py
   views/admin.py
   ```

### Step 2 — Anthropic API Key
1. Go to console.anthropic.com → sign up free
2. Go to API Keys → Create key → copy it

### Step 3 — Streamlit Cloud
1. Go to share.streamlit.io → sign in with GitHub
2. Click **New app**
3. Select your repo, branch: `main`, main file: `app.py`
4. Click **Advanced settings** → Secrets → paste:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
5. Click **Deploy** → get your free URL!

### Step 4 (Optional) — Email notifications
Add Gmail SMTP secrets:
```toml
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = "587"
SMTP_USER = "your@gmail.com"
SMTP_PASS = "xxxx-xxxx-xxxx-xxxx"   # 16-char App Password from Google
FROM_EMAIL = "noreply@university.edu"
```

## 🏃 Run Locally
```bash
pip install -r requirements.txt
# create .streamlit/secrets.toml with your API key
streamlit run app.py
```

## ⚠️ Data Persistence Note
On Streamlit Community Cloud, `data/` files reset on each redeploy.
For permanent storage, integrate **Supabase** (free PostgreSQL) — ask Claude to add Supabase support.

## 📁 File Structure
```
ideavault/
├── app.py                  # Entry point & router
├── requirements.txt
├── .streamlit/
│   └── secrets.toml        # API keys (never commit this!)
├── utils/
│   ├── auth.py             # Login/session management
│   ├── db.py               # JSON file storage (ideas, users, notifications)
│   ├── ai_service.py       # Anthropic API calls
│   └── styles.py           # Custom CSS
├── views/
│   ├── landing.py          # Home page
│   ├── login.py            # Login form
│   ├── student.py          # Student portal
│   ├── faculty.py          # Faculty review panel
│   └── admin.py            # Admin dashboard
└── data/                   # Auto-created at runtime
    ├── ideas.json
    ├── users.json
    └── notifications.json
```
