import os
import tempfile
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from agents.deadline_agent import analyze_deadlines
from utils.date_parser import categorize_deadline, format_date_friendly, get_days_remaining

# Page config
st.set_page_config(
    page_title="Student Deadline Tracker",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- CSS (THEME-AWARE: adapts to Streamlit's Light/Dark setting) ---------------- #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif;
}

/* ===== THEME-AWARE (uses Streamlit's own light/dark variables) ===== */
/* These variables flip automatically when the user switches Settings -> Theme */

.main-title {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
}

.sub-title {
    font-size: 1.2rem;
    color: var(--text-color);
    opacity: 0.65;
    text-align: center;
    margin-bottom: 2rem;
}

/* ----- Category pill headers (these stay colorful in both themes) ----- */
.category-header {
    font-size: 1.05rem;
    font-weight: 700;
    padding: 12px 18px;
    border-radius: 10px;
    margin-bottom: 16px;
    color: white;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

.bg-urgent   { background: linear-gradient(135deg,#fc8181,#f56565); }
.bg-upcoming { background: linear-gradient(135deg,#f6ad55,#ed8936); }
.bg-future   { background: linear-gradient(135deg,#63b3ed,#4299e1); }
.bg-overdue  { background: linear-gradient(135deg,#cbd5e0,#a0aec0); color:#2d3748; }

/* ----- Deadline cards: use Streamlit's secondary background so they adapt ----- */
.deadline-card {
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 16px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.12);
    background: var(--secondary-background-color);
    border: 1px solid rgba(128,128,128,0.25);
    transition: transform 0.15s ease;
}

.deadline-card:hover {
    transform: translateY(-3px);
}

.card-top-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.type-badge {
    display: inline-block;
    padding: 4px 12px;
    font-size: 0.7rem;
    font-weight: 700;
    border-radius: 20px;
    text-transform: uppercase;
    background: rgba(128,128,128,0.18);
    color: var(--text-color);
    letter-spacing: 0.5px;
}

.days-left {
    font-size: 0.8rem;
    font-weight: 600;
    white-space: nowrap;
}

.days-left.urgent   { color: #e53e3e; }
.days-left.upcoming { color: #dd6b20; }
.days-left.future   { color: #3182ce; }
.days-left.overdue  { color: #718096; }

.event-title {
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--text-color);
    margin: 6px 0 10px 0;
}

.meta-row {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    font-size: 0.85rem;
    color: var(--text-color);
    opacity: 0.85;
}

.meta-row .raw-text {
    opacity: 0.6;
    font-style: italic;
}

/* ----- Empty state box: tinted blue, adapts to theme ----- */
.empty-state {
    background: rgba(66,153,225,0.12);
    border: 1px solid rgba(66,153,225,0.35);
    border-radius: 12px;
    padding: 20px;
    color: #3182ce;
    font-size: 0.9rem;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# ---------------- UI HEADER ---------------- #
st.markdown("<div class='main-title'>Student Deadline Tracker</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Your AI-powered academic assistant</div>", unsafe_allow_html=True)

# ---------------- SESSION STATE ---------------- #
if "extracted_deadlines" not in st.session_state:
    st.session_state["extracted_deadlines"] = []

# ---------------- INPUT ---------------- #
sample_text = """Assignment submission on July 5.
Physics exam on July 10.
Scholarship application deadline July 15.
Fee payment tomorrow."""

col_input, col_action = st.columns([3, 1])

with col_input:
    input_method = st.radio("Choose Input Method:", ["Pasted Text", "Uploaded Text File (.txt)"])

    text_input = ""
    uploaded_file = None

    if input_method == "Pasted Text":
        text_input = st.text_area("Paste text here:", height=200)

        if st.button("📝 Load Sample"):
            text_input = sample_text
            st.rerun()

    else:
        uploaded_file = st.file_uploader("Upload .txt file", type=["txt"])

# ---------------- BUTTON ---------------- #
analyze_button = st.button("🚀 Analyze Deadlines", type="primary")

# ---------------- API CHECK (.env ONLY) ---------------- #
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("❌ GOOGLE_API_KEY missing in .env file")
    st.stop()

# ---------------- PROCESSING ---------------- #
if analyze_button:
    deadlines = []

    with st.spinner("Analyzing..."):
        if input_method == "Pasted Text" and text_input.strip():
            deadlines = analyze_deadlines(text_input)

        elif input_method == "Uploaded Text File (.txt)" and uploaded_file:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as tmp:
                tmp.write(uploaded_file.getvalue())
                path = tmp.name

            try:
                deadlines = analyze_deadlines(path, is_file_path=True)
            finally:
                os.remove(path)

        else:
            st.warning("Please provide input")

    if deadlines:
        st.session_state["extracted_deadlines"] = deadlines
        st.success(f"Successfully extracted {len(deadlines)} deadlines!")
    else:
        st.warning("No deadlines found")

# ---------------- DASHBOARD ---------------- #
if st.session_state["extracted_deadlines"]:

    st.markdown("---")
    st.markdown("### 📊 Results Dashboard")

    urgent, upcoming, future, overdue = [], [], [], []

    for d in st.session_state["extracted_deadlines"]:
        cat = categorize_deadline(d["deadline_date"])
        days = get_days_remaining(d["deadline_date"])

        item = {
            "name": d.get("event_name"),
            "type": d.get("event_type"),
            "date": d["deadline_date"],
            "days": days,
            "friendly": format_date_friendly(d["deadline_date"]),
            "raw_text": d.get("raw_date_text", "")
        }

        if cat == "URGENT":
            urgent.append(item)
        elif cat == "UPCOMING":
            upcoming.append(item)
        elif cat == "FUTURE":
            future.append(item)
        else:
            overdue.append(item)

    # ---- Top metric labels (mirrors target image's small headers) ---- #
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown("🚨 **Urgent (1 Day)**")
        st.markdown(f"<div style='font-size:2rem;font-weight:700;color:var(--text-color);'>{len(urgent)}</div>", unsafe_allow_html=True)
    with m2:
        st.markdown("📅 **Upcoming (7 Days)**")
        st.markdown(f"<div style='font-size:2rem;font-weight:700;color:var(--text-color);'>{len(upcoming)}</div>", unsafe_allow_html=True)
    with m3:
        st.markdown("⭐ **Future (>7 Days)**")
        st.markdown(f"<div style='font-size:2rem;font-weight:700;color:var(--text-color);'>{len(future)}</div>", unsafe_allow_html=True)
    with m4:
        st.markdown("⚠️ **Overdue**")
        st.markdown(f"<div style='font-size:2rem;font-weight:700;color:var(--text-color);'>{len(overdue)}</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    def days_label_and_class(days, fallback_class):
        if days is None:
            return "—", fallback_class
        if days < 0:
            return f"{abs(days)} day{'s' if abs(days) != 1 else ''} overdue", "overdue"
        if days == 0:
            return "Due today", fallback_class
        return f"{days} day{'s' if days != 1 else ''} left", fallback_class

    def render_column(col, header_html, bg_class, data, icon, empty_msg, days_class):
        with col:
            st.markdown(
                f"<div class='category-header {bg_class}'>{icon} {header_html}</div>",
                unsafe_allow_html=True
            )
            if not data:
                st.markdown(f"<div class='empty-state'>{empty_msg}</div>", unsafe_allow_html=True)
            else:
                for i in data:
                    label, cls = days_label_and_class(i["days"], days_class)
                    st.markdown(f"""
                    <div class="deadline-card">
                        <div class="card-top-row">
                            <span class="type-badge">{i['type']}</span>
                            <span class="days-left {cls}">⏳ {label}</span>
                        </div>
                        <div class="event-title">{i['name']}</div>
                        <div class="meta-row">
                            <span>📅 <b>Date:</b> {i['friendly'] if i['friendly'] in ("Today", "Tomorrow", "Yesterday") else i['date']}</span>
                            <span class="raw-text">Raw text: "{i['raw_text']}"</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    render_column(c1, "URGENT", "bg-urgent", urgent, "🚨", "No urgent deadlines. You're on top of it! 🎉", "urgent")
    render_column(c2, "UPCOMING", "bg-upcoming", upcoming, "📅", "No upcoming deadlines for the week.", "upcoming")
    render_column(c3, "FUTURE", "bg-future", future, "✨", "No future deadlines logged yet.", "future")
    render_column(c4, "OVERDUE", "bg-overdue", overdue, "⚠️", "No overdue deadlines. High five! 🙌", "overdue")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🧹 Clear"):
        st.session_state["extracted_deadlines"] = []
        st.rerun()