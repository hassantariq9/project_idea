import streamlit as st

def inject_css():
    st.markdown("""
<style>
  #MainMenu, footer, .stAppDeployButton { display: none !important; }
  .stAppHeader { display: none !important; }
  .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

  /* Sidebar */
  [data-testid="stSidebar"] { background: #0f0e23 !important; }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  [data-testid="stSidebar"] .stButton button {
    background: rgba(255,255,255,0.08) !important;
    color: #e2e8f0 !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 8px !important;
    width: 100% !important;
    text-align: left !important;
  }
  [data-testid="stSidebar"] .stButton button:hover {
    background: rgba(255,255,255,0.15) !important;
  }

  /* Cards */
  .iv-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 14px;
    transition: box-shadow 0.15s;
  }
  .iv-card:hover { box-shadow: 0 4px 20px rgba(0,0,0,0.07); }
  .iv-card-title { font-size: 15px; font-weight: 600; color: #111827; margin-bottom: 4px; }
  .iv-card-desc  { font-size: 13px; color: #4b5563; line-height: 1.65; margin: 6px 0; }
  .iv-card-meta  { font-size: 12px; color: #9ca3af; margin-top: 8px; }

  /* Status badges */
  .badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 20px;
    letter-spacing: 0.02em;
  }
  .badge-pending       { background:#FEF3C7; color:#92400E; }
  .badge-approved      { background:#D1FAE5; color:#065F46; }
  .badge-rejected      { background:#FEE2E2; color:#991B1B; }
  .badge-changes       { background:#DBEAFE; color:#1E40AF; }
  .badge-taken         { background:#F3F4F6; color:#374151; }
  .badge-auto_rejected { background:#EDE9FE; color:#5B21B6; }

  /* Similarity bar */
  .sim-bar-wrap { background:#f3f4f6; border-radius:4px; height:6px; margin:4px 0; }
  .sim-bar { height:6px; border-radius:4px; transition: width 0.3s; }

  /* Notification dot */
  .notif-dot {
    display:inline-block; width:8px; height:8px;
    background:#ef4444; border-radius:50%; margin-left:6px;
  }

  /* Metric cards */
  .metric-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 16px 20px;
    text-align: center;
  }
  .metric-num  { font-size: 30px; font-weight: 700; }
  .metric-lbl  { font-size: 12px; color: #6b7280; margin-top: 2px; }

  /* Cluster pill */
  .cluster-pill {
    display: inline-block;
    font-size: 11px;
    padding: 2px 10px;
    border-radius: 20px;
    background: #ede9fe;
    color: #5b21b6;
    font-weight: 500;
    margin-right: 4px;
    margin-bottom: 4px;
  }
  .tag-pill {
    display: inline-block;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 20px;
    background: #f0f9ff;
    color: #0369a1;
    margin-right: 3px;
    margin-bottom: 3px;
  }

  /* AI score ring */
  .score-ring {
    width: 56px; height: 56px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; font-weight: 700;
    border: 3px solid;
    float: right;
    margin-left: 12px;
  }

  /* Landing hero */
  .hero {
    background: linear-gradient(135deg, #0f0e23 0%, #1e1b4b 50%, #312e81 100%);
    border-radius: 16px;
    padding: 48px 40px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
  }
  .hero h1 { font-size: 36px; font-weight: 800; margin: 0 0 10px; }
  .hero p  { font-size: 16px; opacity: 0.8; margin: 0; }

  /* Portal cards */
  .portal-card {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 16px;
    padding: 28px 20px;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
  }
  .portal-card:hover { border-color: #6366f1; box-shadow: 0 8px 30px rgba(99,102,241,0.15); }
  .portal-card-icon { font-size: 36px; margin-bottom: 12px; }
  .portal-card-title { font-size: 17px; font-weight: 700; color: #111827; }
  .portal-card-desc  { font-size: 13px; color: #6b7280; margin-top: 6px; }

  /* Feedback box */
  .feedback-box {
    background: #f8fafc;
    border-left: 3px solid #6366f1;
    border-radius: 6px;
    padding: 10px 14px;
    font-size: 13px;
    color: #374151;
    margin-top: 12px;
    line-height: 1.6;
  }

  /* Duplicate warning */
  .dup-warning {
    background: #fff7ed;
    border: 1px solid #fed7aa;
    border-radius: 10px;
    padding: 14px 16px;
    margin: 10px 0;
  }
</style>
""", unsafe_allow_html=True)
