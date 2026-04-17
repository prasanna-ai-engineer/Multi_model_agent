import streamlit as st
import sys
import os
import time
import threading
from io import StringIO
from datetime import datetime



import streamlit as st
gemini_api_key = st.secrets["GEMINI_API_KEY"]
tavily_api_key = st.secrets["TAVILY_API_KEY"]



# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResearchMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Fira+Code:wght@300;400;500&display=swap');

  /* ── Global reset ── */
  html, body, [class*="css"] {
    font-family: 'Fira Code', monospace;
    background-color: #050810;
    color: #c9d1e0;
  }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 2rem 2.5rem 4rem; max-width: 1300px; }

  /* ── Scanline overlay ── */
  body::before {
    content: "";
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,255,180,0.015) 2px,
      rgba(0,255,180,0.015) 4px
    );
    pointer-events: none;
    z-index: 9999;
  }

  /* ── Hero title ── */
  .hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.4rem;
    font-weight: 800;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #00ffb4 0%, #00c8ff 50%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.2rem;
  }

  .hero-sub {
    font-size: 0.82rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: #4a5568;
    margin-bottom: 2.5rem;
  }

  /* ── Pipeline step cards ── */
  .step-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
    border: 1px solid rgba(0,255,180,0.08);
    border-radius: 12px;
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.3s ease;
    position: relative;
    overflow: hidden;
  }

  .step-card::before {
    content: "";
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: #1a2035;
    border-radius: 3px 0 0 3px;
  }

  .step-card.active::before  { background: #00ffb4; }
  .step-card.done::before    { background: #a855f7; }
  .step-card.error::before   { background: #ff4d6d; }

  .step-card.active { border-color: rgba(0,255,180,0.25); }
  .step-card.done   { border-color: rgba(168,85,247,0.25); }
  .step-card.error  { border-color: rgba(255,77,109,0.2);  }

  .step-label {
    font-family: 'Syne', sans-serif;
    font-size: 0.7rem;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #4a5568;
    margin-bottom: 0.2rem;
  }

  .step-title {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: #e2e8f0;
  }

  .step-card.active .step-title { color: #00ffb4; }
  .step-card.done   .step-title { color: #a855f7; }

  /* ── Status badges ── */
  .badge {
    display: inline-block;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 0.2rem 0.55rem;
    border-radius: 999px;
    font-weight: 600;
  }

  .badge-waiting { background: rgba(74,85,104,0.3); color: #718096; }
  .badge-running { background: rgba(0,255,180,0.12); color: #00ffb4; animation: pulse 1.5s infinite; }
  .badge-done    { background: rgba(168,85,247,0.15); color: #c084fc; }
  .badge-error   { background: rgba(255,77,109,0.15); color: #ff4d6d; }

  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
  }

  /* ── Result panels ── */
  .result-panel {
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 1.5rem 1.8rem;
    margin-top: 0.6rem;
  }

  .result-panel h4 {
    font-family: 'Syne', sans-serif;
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #4a5568;
    margin-bottom: 0.9rem;
  }

  .result-content {
    font-size: 0.82rem;
    line-height: 1.75;
    color: #a0aec0;
    white-space: pre-wrap;
    word-break: break-word;
  }

  /* ── Score ring ── */
  .score-ring-wrap {
    display: flex;
    align-items: center;
    gap: 1.4rem;
    padding: 1.2rem 1.8rem;
    background: rgba(168,85,247,0.06);
    border: 1px solid rgba(168,85,247,0.15);
    border-radius: 14px;
    margin-top: 0.6rem;
  }

  .score-number {
    font-family: 'Syne', sans-serif;
    font-size: 3rem;
    font-weight: 800;
    color: #c084fc;
    line-height: 1;
    min-width: 90px;
    text-align: center;
  }

  .score-label {
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #6b7280;
  }

  .score-feedback {
    font-size: 0.82rem;
    line-height: 1.7;
    color: #a0aec0;
    white-space: pre-wrap;
  }

  /* ── Input area ── */
  .stTextInput > div > div > input {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(0,255,180,0.2) !important;
    border-radius: 10px !important;
    color: #000000 !important;
    font-family: 'Fira Code', monospace !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
  }

  .stTextInput > div > div > input:focus {
    border-color: rgba(0,255,180,0.5) !important;
    box-shadow: 0 0 0 3px rgba(0,255,180,0.08) !important;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: linear-gradient(135deg, #00ffb4, #00c8ff) !important;
    color: #050810 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.08em !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.65rem 1.8rem !important;
    cursor: pointer !important;
    transition: opacity 0.2s, transform 0.15s !important;
  }

  .stButton > button:hover {
    opacity: 0.88 !important;
    transform: translateY(-1px) !important;
  }

  .stButton > button:disabled {
    background: rgba(74,85,104,0.4) !important;
    color: #4a5568 !important;
    cursor: not-allowed !important;
    transform: none !important;
  }

  /* ── Sidebar ── */
  section[data-testid="stSidebar"] {
    background: rgba(5,8,16,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.05) !important;
  }

  .sidebar-section {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 1rem 1.1rem;
    margin-bottom: 1rem;
  }

  .sidebar-title {
    font-family: 'Syne', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: #4a5568;
    margin-bottom: 0.75rem;
  }

  .history-item {
    font-size: 0.78rem;
    color: #718096;
    padding: 0.45rem 0.6rem;
    border-radius: 7px;
    margin-bottom: 0.3rem;
    cursor: pointer;
    border: 1px solid transparent;
    transition: all 0.2s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .history-item:hover {
    background: rgba(0,255,180,0.05);
    border-color: rgba(0,255,180,0.15);
    color: #00ffb4;
  }

  /* ── Progress bar ── */
  .progress-bar-outer {
    background: rgba(255,255,255,0.05);
    border-radius: 999px;
    height: 4px;
    overflow: hidden;
    margin-top: 1rem;
    margin-bottom: 0.3rem;
  }

  .progress-bar-inner {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, #00ffb4, #00c8ff);
    transition: width 0.6s ease;
  }

  .progress-text {
    font-size: 0.7rem;
    color: #4a5568;
    letter-spacing: 0.1em;
    text-align: right;
  }

  /* ── Log box ── */
  .log-box {
    background: #020409;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-size: 0.75rem;
    line-height: 1.8;
    color: #4a5568;
    max-height: 200px;
    overflow-y: auto;
    font-family: 'Fira Code', monospace;
  }

  .log-line-info  { color: #4a5568; }
  .log-line-ok    { color: #00ffb4; }
  .log-line-warn  { color: #f59e0b; }
  .log-line-error { color: #ff4d6d; }

  /* ── Divider ── */
  hr { border-color: rgba(255,255,255,0.06) !important; }

  /* ── Expander ── */
  .streamlit-expanderHeader {
    font-family: 'Syne', sans-serif !important;
    font-size: 0.78rem !important;
    color: #718096 !important;
    letter-spacing: 0.1em !important;
  }

  /* ── Toast notification ── */
  .toast {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    background: rgba(0,255,180,0.1);
    border: 1px solid rgba(0,255,180,0.3);
    border-radius: 10px;
    padding: 0.85rem 1.3rem;
    font-size: 0.8rem;
    color: #00ffb4;
    z-index: 9998;
    backdrop-filter: blur(8px);
  }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar       { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 999px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(0,255,180,0.3); }
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────
def _init_state():
    defaults = {
        "pipeline_state": "idle",   # idle | running | done | error
        "current_step": 0,
        "results": {},
        "history": [],
        "logs": [],
        "topic": "",
        "error_msg": "",
        "score": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()

# ── Helpers ───────────────────────────────────────────────────────────────
STEPS = [
    ("01", "Search Agent",    "Scanning the web for reliable sources on your topic"),
    ("02", "Reader Agent",    "Scraping the most relevant URL for deep content"),
    ("03", "Report Writer",   "Synthesising findings into a structured report"),
    ("04", "Report Reviewer", "Evaluating report quality and scoring it /10"),
]

def _step_status(idx):
    cs = st.session_state.current_step
    ps = st.session_state.pipeline_state
    if ps == "idle":             return "waiting"
    if idx < cs:                 return "done"
    if idx == cs:
        return "error" if ps == "error" else ("running" if ps == "running" else "done")
    return "waiting"

def _card_class(idx):
    s = _step_status(idx)
    return {"waiting": "step-card", "running": "step-card active",
            "done": "step-card done", "error": "step-card error"}[s]

def _badge(idx):
    s = _step_status(idx)
    labels = {"waiting": ("waiting","badge-waiting"), "running": ("● running","badge-running"),
              "done": ("✓ done","badge-done"), "error": ("✗ error","badge-error")}
    txt, cls = labels[s]
    return f'<span class="badge {cls}">{txt}</span>'

def _log(msg, kind="info"):
    ts = datetime.now().strftime("%H:%M:%S")
    colour = {"info": "log-line-info", "ok": "log-line-ok",
              "warn": "log-line-warn", "error": "log-line-error"}.get(kind, "log-line-info")
    st.session_state.logs.append(f'<span class="{colour}">[{ts}] {msg}</span>')

def _extract_score(feedback_text):
    """Try to pull a numeric score (x/10 or x.x/10) from feedback."""
    import re
    patterns = [r'(\d+(?:\.\d+)?)\s*/\s*10', r'score[:\s]+(\d+(?:\.\d+)?)',
                r'rating[:\s]+(\d+(?:\.\d+)?)']
    for p in patterns:
        m = re.search(p, str(feedback_text), re.IGNORECASE)
        if m:
            return float(m.group(1))
    return None

def _run_pipeline(topic):
    """Execute the pipeline and update session state."""
    try:
        from pipeline import run_research_pipeline
    except ImportError as e:
        st.session_state.pipeline_state = "error"
        st.session_state.error_msg = (
            f"Could not import pipeline.py → {e}\n\n"
            "Make sure app.py is in the same folder as pipeline.py and all dependencies are installed."
        )
        _log(f"Import error: {e}", "error")
        return

    try:
        _log(f"Starting research on: {topic}", "ok")

        # Step 1
        st.session_state.current_step = 0
        _log("Search agent initialising…")
        from agent import build_search_agent
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic}")]
        })
        st.session_state.results["search_result"] = sr["messages"][-1].content
        _log("Search complete ✓", "ok")

        # Step 2
        st.session_state.current_step = 1
        _log("Reader agent initialising…")
        from agent import build_reader_agent
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [(
                "user",
                f"Based on the following search results about '{topic}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{st.session_state.results['search_result'][:800]}"
            )]
        })
        st.session_state.results["scraped_data"] = rr["messages"][-1].content
        _log("Scraping complete ✓", "ok")

        # Step 3
        st.session_state.current_step = 2
        _log("Report writer composing…")
        from agent import report_writing_chain
        research_combined = (
            f"searched result \n {st.session_state.results['search_result']} ",
            f"scraped data \n {st.session_state.results['scraped_data']}"
        )
        st.session_state.results["generated_report"] = report_writing_chain.invoke({
            "topic": topic,
            "research": research_combined
        })
        _log("Report generated ✓", "ok")

        # Step 4
        st.session_state.current_step = 3
        _log("Report reviewer evaluating…")
        from agent import report_reviewer_chain
        st.session_state.results["feedback"] = report_reviewer_chain.invoke({
            "report": st.session_state.results["generated_report"]
        })
        st.session_state.score = _extract_score(st.session_state.results["feedback"])
        _log("Review complete ✓", "ok")

        # Done
        st.session_state.current_step = 4
        st.session_state.pipeline_state = "done"
        st.session_state.history.insert(0, {"topic": topic, "ts": datetime.now().strftime("%b %d %H:%M"),
                                             "score": st.session_state.score})
        _log("Pipeline finished successfully 🎉", "ok")

    except Exception as e:
        st.session_state.pipeline_state = "error"
        st.session_state.error_msg = str(e)
        _log(f"Pipeline error: {e}", "error")

# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="hero-title" style="font-size:1.6rem">ResearchMind</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub" style="font-size:0.65rem;margin-bottom:1.5rem">Multi-Agent Pipeline</div>', unsafe_allow_html=True)

    # Pipeline steps overview
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Pipeline Steps</div>', unsafe_allow_html=True)
    for i, (num, name, desc) in enumerate(STEPS):
        status = _step_status(i)
        icon = {"waiting": "○", "running": "◉", "done": "●", "error": "✗"}[status]
        colour = {"waiting": "#2d3748", "running": "#00ffb4", "done": "#a855f7", "error": "#ff4d6d"}[status]
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:0.7rem;padding:0.35rem 0;border-bottom:1px solid rgba(255,255,255,0.04)">'
            f'<span style="color:{colour};font-size:0.85rem">{icon}</span>'
            f'<span style="font-size:0.78rem;color:{"#e2e8f0" if status in ("running","done") else "#4a5568"}">{name}</span>'
            f'</div>',
            unsafe_allow_html=True
        )
    st.markdown('</div>', unsafe_allow_html=True)

    # History
    if st.session_state.history:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">Recent Searches</div>', unsafe_allow_html=True)
        for h in st.session_state.history[:8]:
            score_txt = f" · {h['score']}/10" if h.get("score") else ""
            st.markdown(
                f'<div class="history-item" title="{h["topic"]}">'
                f'<span style="color:#4a5568;font-size:0.68rem">{h["ts"]}</span>'
                f'<br>{h["topic"][:30]}{"…" if len(h["topic"])>30 else ""}'
                f'<span style="color:#a855f7">{score_txt}</span>'
                f'</div>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # Live log
    if st.session_state.logs:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown('<div class="sidebar-title">Activity Log</div>', unsafe_allow_html=True)
        log_html = "<br>".join(st.session_state.logs[-20:])
        st.markdown(f'<div class="log-box">{log_html}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ── Main layout ────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">ResearchMind AI</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Autonomous Multi-Agent Research System</div>', unsafe_allow_html=True)

# ── Input row ──────────────────────────────────────────────────────────────
col_input, col_btn, col_reset = st.columns([6, 1.4, 1.2])

with col_input:
    topic_input = st.text_input(
        label="topic",
        label_visibility="collapsed",
        placeholder="Enter a research topic — e.g. 'Quantum computing breakthroughs 2025'",
        value=st.session_state.topic,
        key="topic_field",
        disabled=(st.session_state.pipeline_state == "running"),
    )

with col_btn:
    run_disabled = (st.session_state.pipeline_state == "running") or not topic_input.strip()
    run_clicked = st.button("▶ Research", disabled=run_disabled, use_container_width=True)

with col_reset:
    reset_clicked = st.button("↺ Reset", use_container_width=True,
                               disabled=(st.session_state.pipeline_state == "running"))

# ── Handle reset ───────────────────────────────────────────────────────────
if reset_clicked:
    for k in ["pipeline_state", "current_step", "results", "logs", "topic", "error_msg", "score"]:
        del st.session_state[k]
    _init_state()
    st.rerun()

# ── Handle run ─────────────────────────────────────────────────────────────
if run_clicked and topic_input.strip():
    st.session_state.topic = topic_input.strip()
    st.session_state.pipeline_state = "running"
    st.session_state.current_step = 0
    st.session_state.results = {}
    st.session_state.logs = []
    st.session_state.score = None
    st.session_state.error_msg = ""
    st.rerun()

# ── Run pipeline (synchronously in Streamlit's thread) ────────────────────
if st.session_state.pipeline_state == "running":
    _run_pipeline(st.session_state.topic)
    st.rerun()

# ── Progress bar ───────────────────────────────────────────────────────────
if st.session_state.pipeline_state != "idle":
    completed = min(st.session_state.current_step, 4)
    pct = int((completed / 4) * 100)
    bar_colour = "#ff4d6d" if st.session_state.pipeline_state == "error" else "linear-gradient(90deg,#00ffb4,#00c8ff)"
    st.markdown(
        f'<div class="progress-bar-outer">'
        f'<div class="progress-bar-inner" style="width:{pct}%;background:{bar_colour}"></div>'
        f'</div>'
        f'<div class="progress-text">{pct}% complete</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)

# ── Step cards + result panels ────────────────────────────────────────────
result_keys = ["search_result", "scraped_data", "generated_report", "feedback"]
result_labels = ["Search Results", "Scraped Content", "Generated Report", "Reviewer Feedback"]

for i, (num, name, desc) in enumerate(STEPS):
    card_cls = _card_class(i)
    badge_html = _badge(i)
    status = _step_status(i)

    st.markdown(
        f'<div class="{card_cls}">'
        f'<div class="step-label">Step {num}</div>'
        f'<div style="display:flex;align-items:center;justify-content:space-between">'
        f'<div class="step-title">{name}</div>'
        f'{badge_html}'
        f'</div>'
        f'<div style="font-size:0.75rem;color:#4a5568;margin-top:0.25rem">{desc}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

    # Show result if available
    rk = result_keys[i]
    if rk in st.session_state.results and st.session_state.results[rk]:
        data = st.session_state.results[rk]

        # Special rendering for feedback step (score ring)
        if rk == "feedback" and status == "done":
            score = st.session_state.score
            score_display = f"{score}/10" if score else "—"
            score_int = int(score) if score else 0

            st.markdown(
                f'<div class="score-ring-wrap">'
                f'<div>'
                f'  <div class="score-label">Quality Score</div>'
                f'  <div class="score-number">{score_display}</div>'
                f'</div>'
                f'<div style="flex:1">'
                f'  <div class="score-label" style="margin-bottom:0.5rem">Reviewer Notes</div>'
                f'  <div class="score-feedback">{str(data)[:600]}{"…" if len(str(data))>600 else ""}</div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            # Full feedback in expander
            if len(str(data)) > 600:
                with st.expander("Read full reviewer feedback"):
                    st.markdown(f'<div class="result-content">{data}</div>', unsafe_allow_html=True)

        # Special rendering for report (full width)
        elif rk == "generated_report" and status == "done":
            with st.expander("📄 View Full Report", expanded=True):
                st.markdown(
                    f'<div class="result-panel">'
                    f'<h4>{result_labels[i]}</h4>'
                    f'<div class="result-content">{data}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                # Download button
                st.download_button(
                    label="⬇ Download Report (.txt)",
                    data=str(data),
                    file_name=f"report_{st.session_state.topic[:30].replace(' ','_')}.txt",
                    mime="text/plain",
                )

        else:
            preview = str(data)[:500]
            with st.expander(f"View {result_labels[i]}"):
                st.markdown(
                    f'<div class="result-panel">'
                    f'<h4>{result_labels[i]}</h4>'
                    f'<div class="result-content">{preview}{"…" if len(str(data))>500 else ""}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

# ── Error banner ───────────────────────────────────────────────────────────
if st.session_state.pipeline_state == "error" and st.session_state.error_msg:
    st.markdown(
        f'<div style="margin-top:1.5rem;padding:1.1rem 1.4rem;background:rgba(255,77,109,0.08);'
        f'border:1px solid rgba(255,77,109,0.25);border-radius:12px">'
        f'<div style="font-family:Syne,sans-serif;font-size:0.72rem;letter-spacing:0.18em;'
        f'text-transform:uppercase;color:#ff4d6d;margin-bottom:0.4rem">Pipeline Error</div>'
        f'<div style="font-size:0.82rem;color:#fc8181;white-space:pre-wrap">{st.session_state.error_msg}</div>'
        f'</div>',
        unsafe_allow_html=True
    )

# ── Success summary ────────────────────────────────────────────────────────
if st.session_state.pipeline_state == "done":
    score = st.session_state.score
    score_txt = f" · Score {score}/10" if score else ""
    st.markdown(
        f'<div class="toast">✓ Research complete{score_txt}</div>',
        unsafe_allow_html=True
    )

# ── Idle state prompt ──────────────────────────────────────────────────────
if st.session_state.pipeline_state == "idle":
    st.markdown(
        '<div style="text-align:center;padding:4rem 2rem;color:#2d3748">'
        '<div style="font-size:3rem;margin-bottom:1rem">🔬</div>'
        '<div style="font-family:Syne,sans-serif;font-size:1.1rem;font-weight:700;color:#374151">'
        'Enter a topic above to begin</div>'
        '<div style="font-size:0.8rem;margin-top:0.5rem">The pipeline will search, scrape, write, and review — automatically.</div>'
        '</div>',
        unsafe_allow_html=True
    )