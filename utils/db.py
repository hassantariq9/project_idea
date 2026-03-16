import json, os, time, hashlib
from datetime import datetime

IDEAS_FILE = "data/ideas.json"
USERS_FILE = "data/users.json"
NOTIF_FILE = "data/notifications.json"

os.makedirs("data", exist_ok=True)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def verify_pw(pw: str, hashed: str) -> bool:
    return hash_pw(pw) == hashed

DEFAULT_USERS = None  # populated after hash_pw is defined

def _make_defaults():
    return {
        "admin": {"password": hash_pw("Admin@2024"), "name": "System Administrator", "email": "admin@university.edu", "role": "admin", "department": "IT", "created_at": datetime.now().isoformat()},
        "dr_smith": {"password": hash_pw("Faculty@123"), "name": "Dr. Sarah Smith", "email": "s.smith@university.edu", "role": "faculty", "department": "Computer Science", "created_at": datetime.now().isoformat()},
        "dr_khan": {"password": hash_pw("Faculty@123"), "name": "Dr. Arif Khan", "email": "a.khan@university.edu", "role": "faculty", "department": "Software Engineering", "created_at": datetime.now().isoformat()},
        "S001": {"password": hash_pw("Student@123"), "name": "Alice Rahman", "email": "alice@student.university.edu", "role": "student", "department": "Computer Science", "batch": "2024", "created_at": datetime.now().isoformat()},
        "S002": {"password": hash_pw("Student@123"), "name": "Omar Farooq", "email": "omar@student.university.edu", "role": "student", "department": "Software Engineering", "batch": "2024", "created_at": datetime.now().isoformat()},
        "S003": {"password": hash_pw("Student@123"), "name": "Zara Ahmed", "email": "zara@student.university.edu", "role": "student", "department": "Computer Science", "batch": "2023", "created_at": datetime.now().isoformat()},
    }

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE) as f:
            return json.load(f)
    defaults = _make_defaults()
    save_users(defaults)
    return defaults

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=2)

def add_user(uid, name, email, role, password, department="", batch=""):
    users = load_users()
    if uid in users:
        return False, "User ID already exists."
    users[uid] = {"password": hash_pw(password), "name": name, "email": email, "role": role, "department": department, "batch": batch, "created_at": datetime.now().isoformat()}
    save_users(users)
    return True, "User created."

def bulk_add_students(rows):
    users = load_users()
    added, skipped = 0, 0
    for r in rows:
        uid = str(r.get("uid", "")).strip()
        if not uid or uid in users:
            skipped += 1
            continue
        users[uid] = {"password": hash_pw(str(r.get("password","Student@123"))), "name": r.get("name",""), "email": r.get("email",""), "role": "student", "department": r.get("department",""), "batch": str(r.get("batch","")), "created_at": datetime.now().isoformat()}
        added += 1
    save_users(users)
    return added, skipped

def load_ideas():
    if os.path.exists(IDEAS_FILE):
        with open(IDEAS_FILE) as f:
            return json.load(f)
    return []

def save_ideas(ideas):
    with open(IDEAS_FILE, "w") as f:
        json.dump(ideas, f, indent=2)

def add_idea(student_id, student_name, title, description, tags=None, cluster=None):
    ideas = load_ideas()
    idea = {"id": f"IDEA-{int(time.time()*1000)}", "studentId": student_id, "studentName": student_name, "title": title, "description": description, "tags": tags or [], "cluster": cluster or "Uncategorized", "status": "pending", "feedback": "", "similarity_score": 0.0, "similar_to": None, "assigned_faculty": None, "submittedAt": datetime.now().isoformat(), "reviewedAt": None, "ai_score": None, "ai_strengths": [], "ai_weaknesses": []}
    ideas.append(idea)
    save_ideas(ideas)
    return idea

def update_idea(idea_id, **kwargs):
    ideas = load_ideas()
    for i in ideas:
        if i["id"] == idea_id:
            i.update(kwargs)
            if "status" in kwargs:
                i["reviewedAt"] = datetime.now().isoformat()
    save_ideas(ideas)

def load_notifications():
    if os.path.exists(NOTIF_FILE):
        with open(NOTIF_FILE) as f:
            return json.load(f)
    return []

def save_notifications(notifs):
    with open(NOTIF_FILE, "w") as f:
        json.dump(notifs, f, indent=2)

def add_notification(user_id, title, message, notif_type="info"):
    if not user_id:
        return
    notifs = load_notifications()
    notifs.append({"id": f"N-{int(time.time()*1000)}", "userId": user_id, "title": title, "message": message, "type": notif_type, "read": False, "createdAt": datetime.now().isoformat()})
    save_notifications(notifs)

def get_user_notifications(user_id, unread_only=False):
    notifs = load_notifications()
    result = [n for n in notifs if n["userId"] == user_id]
    if unread_only:
        result = [n for n in result if not n["read"]]
    return sorted(result, key=lambda x: x["createdAt"], reverse=True)

def mark_notifications_read(user_id):
    notifs = load_notifications()
    for n in notifs:
        if n["userId"] == user_id:
            n["read"] = True
    save_notifications(notifs)

def fmt_date(iso):
    try:
        return datetime.fromisoformat(iso).strftime("%d %b %Y, %H:%M")
    except:
        return str(iso)

STATUS_COLORS = {
    "pending": ("🟡","#F59E0B","#FEF3C7"),
    "approved": ("🟢","#10B981","#D1FAE5"),
    "rejected": ("🔴","#EF4444","#FEE2E2"),
    "changes": ("🔵","#3B82F6","#DBEAFE"),
    "taken": ("⚫","#6B7280","#F3F4F6"),
    "auto_rejected": ("🤖","#7C3AED","#EDE9FE"),
}
STATUS_LABELS = {
    "pending": "Pending Review",
    "approved": "Approved ✓",
    "rejected": "Rejected",
    "changes": "Needs Changes",
    "taken": "Already Taken",
    "auto_rejected": "Auto-Rejected (AI)",
}
