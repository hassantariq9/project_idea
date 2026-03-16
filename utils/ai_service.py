import json
import streamlit as st
from anthropic import Anthropic

def get_client():
    return Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])

# ── Similarity check ──────────────────────────────────────────────────────────
def check_similarity(title, desc, existing_ideas):
    """Returns {isSimilar, similarTo, similarity_score, reason}"""
    if not existing_ideas:
        return {"isSimilar": False, "similarTo": None, "similarity_score": 0.0, "reason": ""}

    existing_list = "\n".join(
        f'[{i["id"]}] "{i["title"]}": {i["description"][:200]}'
        for i in existing_ideas
    )
    prompt = f"""You are evaluating if a new project idea is too similar to existing approved/pending ideas at a university.

NEW IDEA:
Title: "{title}"
Description: "{desc}"

EXISTING IDEAS:
{existing_list}

Evaluate conceptual similarity (core problem being solved, domain, approach).
Minor wording differences don't count — focus on whether they would compete for the same project slot.

Respond ONLY with valid JSON (no markdown, no explanation):
{{
  "isSimilar": true/false,
  "similarTo": "idea title or null",
  "similarity_score": 0.0-1.0,
  "reason": "one sentence explanation"
}}"""

    client = get_client()
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip().replace("```json","").replace("```","")
    return json.loads(text)

# ── Idea clustering ───────────────────────────────────────────────────────────
def cluster_ideas(ideas):
    """Assign cluster labels to a list of ideas. Returns list of {id, cluster, tags}"""
    if not ideas:
        return []

    idea_list = "\n".join(
        f'[{i["id"]}] "{i["title"]}": {i["description"][:150]}'
        for i in ideas
    )
    prompt = f"""You are a university project coordinator. Cluster these project ideas into meaningful topic groups.

IDEAS:
{idea_list}

Group them into 4-8 clusters based on domain/technology/problem area.
Assign each idea a cluster name and 2-4 relevant tags.

Respond ONLY with valid JSON array (no markdown):
[
  {{"id": "IDEA-xxx", "cluster": "Web Development", "tags": ["react", "fullstack", "e-commerce"]}},
  ...
]"""

    client = get_client()
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip().replace("```json","").replace("```","")
    return json.loads(text)

# ── Idea quality scoring ──────────────────────────────────────────────────────
def score_idea(title, desc):
    """Returns {score, strengths, weaknesses, suggestion}"""
    prompt = f"""You are evaluating a university student's project idea for feasibility, innovation, and clarity.

Title: "{title}"
Description: "{desc}"

Score this idea and provide brief feedback.

Respond ONLY with valid JSON (no markdown):
{{
  "score": 0-10,
  "strengths": ["strength 1", "strength 2"],
  "weaknesses": ["weakness 1", "weakness 2"],
  "suggestion": "One concrete improvement suggestion",
  "difficulty": "Easy/Medium/Hard",
  "estimated_weeks": 8
}}"""

    client = get_client()
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip().replace("```json","").replace("```","")
    return json.loads(text)

# ── AI idea suggestions ───────────────────────────────────────────────────────
def suggest_ideas(department, batch, existing_titles, num=5):
    """Generate fresh project idea suggestions for a student"""
    taken = "\n".join(f"- {t}" for t in existing_titles[:30]) if existing_titles else "None yet"
    prompt = f"""You are helping a {batch} year student in {department} find a fresh, interesting final-year project idea.

Already taken/approved ideas (avoid these):
{taken}

Generate {num} unique, practical, and interesting project ideas suitable for a university final-year project.
Each should be doable in one semester.

Respond ONLY with valid JSON array (no markdown):
[
  {{
    "title": "Smart Campus Navigation App",
    "description": "A mobile app using indoor positioning to help students navigate campus buildings, find free classrooms, and check facility availability in real-time.",
    "tags": ["mobile", "IoT", "maps"],
    "difficulty": "Medium",
    "why_good": "Solves a real campus problem with modern tech"
  }},
  ...
]"""

    client = get_client()
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}]
    )
    text = resp.content[0].text.strip().replace("```json","").replace("```","")
    return json.loads(text)

# ── Generate feedback ─────────────────────────────────────────────────────────
def generate_feedback(title, desc, decision):
    """Generate professional faculty feedback for a decision"""
    prompt = f"""Write a brief, professional feedback message from a faculty member to a student regarding their project idea.

Project: "{title}"
Description: "{desc}"
Decision: {decision}

Write 2-3 sentences of constructive feedback appropriate for the decision.
Be encouraging but honest. No greeting/signature needed.
Return plain text only."""

    client = get_client()
    resp = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text.strip()

# ── Email notification (simulated) ───────────────────────────────────────────
def send_email_notification(to_email, to_name, subject, body):
    """
    In production: integrate SendGrid / SMTP via st.secrets.
    For now, stores notification in DB and prints to console.
    """
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    try:
        smtp_host  = st.secrets.get("SMTP_HOST", "")
        smtp_port  = int(st.secrets.get("SMTP_PORT", 587))
        smtp_user  = st.secrets.get("SMTP_USER", "")
        smtp_pass  = st.secrets.get("SMTP_PASS", "")
        from_email = st.secrets.get("FROM_EMAIL", "noreply@university.edu")

        if not smtp_host or not smtp_user:
            # Email not configured — skip silently
            return False, "Email not configured"

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"IdeaVault Portal <{from_email}>"
        msg["To"]      = to_email

        html_body = f"""
        <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;padding:20px;">
          <div style="background:#1e1b4b;color:white;padding:20px;border-radius:8px 8px 0 0;">
            <h2 style="margin:0;">💡 IdeaVault Portal</h2>
          </div>
          <div style="background:#f9fafb;padding:24px;border-radius:0 0 8px 8px;border:1px solid #e5e7eb;">
            <p>Hi {to_name},</p>
            {body}
            <hr style="border:none;border-top:1px solid #e5e7eb;margin:20px 0;">
            <p style="font-size:12px;color:#6b7280;">IdeaVault — University Project Idea Portal</p>
          </div>
        </body></html>"""

        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, to_email, msg.as_string())
        return True, "Sent"
    except Exception as e:
        return False, str(e)
