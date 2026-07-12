import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Force Python to read local directory paths dynamically
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if "ai_engine" in sys.modules:
    del sys.modules["ai_engine"]

from ai_engine import get_hybrid_question, evaluate_answer
from database import create_table, save_result, get_results
from speech_to_text import voice_to_text

# Initialize Database System
create_table()

# High-End Visual Configuration
st.set_page_config(
    page_title="InterviewCoach.Pro",
    layout="wide",
    page_icon="🧠",
    initial_sidebar_state="expanded"
)

# Premium Custom CSS & JavaScript Security Injection Block
st.markdown("""
    <style>
    .stApp {
        background-color: #0f172a;
        color: #f8fafc;
    }
    [data-testid="stSidebar"] {
        background-color: #1e293b !important;
        border-right: 1px solid #334155;
    }
    .question-box {
        background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(99, 102, 241, 0.05));
        border-left: 5px solid #3b82f6;
        padding: 1.5rem;
        border-radius: 0px 12px 12px 0px;
        margin: 1.5rem 0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        user-select: none; /* Prevents text highlighting/selection natively */
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
    }
    .metric-container {
        background-color: #1e293b;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.25rem;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
    }
    .status-active {
        color: #ef4444;
        font-weight: bold;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }
    </style>

    <script>
    // Access the central workspace window
    const parentDoc = window.parent.document;
    
    // 1. INTERCEPT AND BLOCK PASTE ACTIONS
    parentDoc.addEventListener('paste', (e) => {
        e.preventDefault();
        alert("🚨 SECURITY BREACH: External text pasting is strictly deactivated to maintain interview integrity! Session terminated.");
        window.parent.location.reload(); // Wipes memory state instantly
    });

    // 2. INTERCEPT AND BLOCK COPY ACTIONS
    parentDoc.addEventListener('copy', (e) => {
        e.preventDefault();
        alert("🚨 SECURITY VIOLATION: Copying evaluation content is prohibited. Session terminated.");
        window.parent.location.reload();
    });

    // 3. DETECT SWITCHING TABS OR MINIMIZING WINDOWS
    parentDoc.addEventListener('visibilitychange', () => {
        if (parentDoc.visibilityState === 'hidden') {
            alert("🚨 LEAVING INTERVIEW ZONE DETECTED: You have navigated away from the active tab! This session has been forced closed.");
            window.parent.location.reload();
        }
    });
    </script>
""", unsafe_allow_html=True)

# Session State Initialization
if "current_question" not in st.session_state:
    st.session_state["current_question"] = ""
if "voice_transcript" not in st.session_state:
    st.session_state["voice_transcript"] = ""
if "evaluation_results" not in st.session_state:
    st.session_state["evaluation_results"] = None
if "current_menu" not in st.session_state:
    st.session_state["current_menu"] = "Live Evaluation Arena"

# =======================================================================
# NAVIGATION PROCTOR & STATE EVALUATION LOCK
# =======================================================================
menu_options = ["Live Evaluation Arena", "Performance Ledger", "Telemetry Dashboard"]

# Check if an exam loop is actively running without a recorded evaluation submission
is_exam_active = st.session_state["current_question"] != ""
has_submitted = st.session_state["evaluation_results"] is not None
should_lock_navigation = is_exam_active and not has_submitted

# Enforce layout indexing properties dynamically based on security lock rules
if should_lock_navigation:
    default_index = 0
else:
    try:
        default_index = menu_options.index(st.session_state["current_menu"])
    except ValueError:
        default_index = 0

# Sidebar Navigation Control Center
with st.sidebar:
    st.markdown("<h2 style='color:#3b82f6; margin-bottom:0;'>🧠 InterviewCoach</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#94a3b8; font-size:0.85rem; margin-bottom:2rem;'>Enterprise AI Proctor Pipeline</p>", unsafe_allow_html=True)
    
    menu = st.radio(
        "Navigation Gateway",
        menu_options,
        index=default_index,
        key="navigation_gateway_radio"
    )
    st.markdown("---")
    st.markdown("### 🌐 System Infrastructure")
    st.caption("Core Node: `gemini-1.5-flash-latest`")
    st.caption("Capture Pipeline: PyAudio / WebRTC")
    st.caption("Database Engine: SQLite Relational v3")

# Intercept and neutralize navigation violations instantly before execution downstream
if should_lock_navigation and menu != "Live Evaluation Arena":
    st.sidebar.error("🚨 ACCESS DENIED: You cannot switch tabs or view matrices during an active examination cycle!")
    st.session_state["current_menu"] = "Live Evaluation Arena"
    st.rerun()
else:
    # Commit the user choice to memory if validation clearance is green
    st.session_state["current_menu"] = menu


# ===================== 1. LIVE INTERVIEW ARENA WORKSPACE =====================
if st.session_state["current_menu"] == "Live Evaluation Arena":
    st.markdown("## 💻 Live Simulation & Assessment Arena")
    
    with st.expander("⚙️ Track Calibration & Target Domain Selection", expanded=True):
        col1, col2, col3 = st.columns(3)
        with col1:
            role = st.selectbox(
                "Target Core Role Track", 
                [
                    "Software Engineer", 
                    "Full Stack Developer", 
                    "DevOps Cloud Architect", 
                    "Data Scientist", 
                    "Data Analyst",
                    "AI Developer",
                    "ML Developer",
                    "Cybersecurity Analyst",
                    ""
                ],
                index=0
            )
        with col2:
            company = st.text_input("Target Enterprise Blueprint", value="FAANG Ecosystem")
        with col3:
            difficulty = st.select_slider("Assessment Difficulty Grading", options=["Easy", "Medium", "Hard"], value="Medium")
            
        use_resume = st.checkbox("Inject Target Resume Context File (ATS Engine Activation)")
        resume_content = None
        if use_resume:
            uploaded_file = st.file_uploader("Upload Profile Data (.txt / .md)", type=["txt", "md"])
            if uploaded_file:
                resume_content = uploaded_file.read().decode("utf-8")
                st.toast("Profile data cached downstream!", icon="✅")

        if st.button("Initialize Live Session & Stream Question", type="primary", use_container_width=True):
            if role == "":
                st.error("❌ Action Blocked: Cannot initialize session context. Please select a valid Target Core Role Track configuration.")
            else:
                with st.spinner("Streaming conceptual questions matrix..."):
                    st.session_state["current_question"] = get_hybrid_question(role, company, difficulty, resume_content)
                    st.session_state["voice_transcript"] = ""
                    st.session_state["evaluation_results"] = None
                    st.rerun()

    if st.session_state["current_question"]:
        st.markdown(f"""
            <div class='question-box'>
                <h4 style='color:#3b82f6; margin:0 0 0.5rem 0;'>⚡ Current Interview Challenge (Secure Area):</h4>
                <p style='font-size:1.15rem; margin:0; color:#f8fafc;'>{st.session_state['current_question']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        workspace_col, camera_col = st.columns([1.6, 1])
        
        with workspace_col:
            st.markdown("### 📝 Technical Response Workspace")
            use_voice = st.toggle("Enable Voice Capture Pipeline Stream", value=True)
            
            user_response = ""
            if use_voice:
                v_col1, v_col2 = st.columns([1, 2])
                with v_col1:
                    if st.button("🔴 Start Live Voice Stream", use_container_width=True):
                        with st.spinner("Ingesting vocal frequencies..."):
                            st.session_state["voice_transcript"] = voice_to_text()
                with v_col2:
                    if st.session_state["voice_transcript"]:
                        st.markdown("<p style='margin-top:10px;'>Status: <span style='color:#10b981;'>Data Captured</span></p>", unsafe_allow_html=True)
                    else:
                        st.markdown("<p style='margin-top:10px;'>Status: <span class='status-active'>Awaiting Feed...</span></p>", unsafe_allow_html=True)
                        
                user_response = st.text_area("Live Spoken Transcript Output Confirmation", value=st.session_state["voice_transcript"], height=180)
            else:
                user_response = st.text_area("Developer Text Workspace Input", placeholder="Type or answer structurally here...", height=180)
                
            if st.button("🚀 Submit Complete Ingestion Matrix for AI Assessment", type="primary", use_container_width=True):
                if not user_response.strip():
                    st.error("Submission buffer is empty. Provide a transcript response matrix.")
                else:
                    with st.spinner("Running syntax parsing and structural assessment loops..."):
                        eval_data = evaluate_answer(st.session_state["current_question"], user_response)
                        st.session_state["evaluation_results"] = eval_data
                        save_result(st.session_state["current_question"], user_response, eval_data["raw_text"], eval_data["score"])
                        st.toast("Evaluation metrics persisted to relational storage!", icon="💾")
                        st.rerun()
        
        with camera_col:
            st.markdown("### 📷 Proctor Monitoring Video Feed")
            camera_image = st.camera_input("Maintain visual focus inside the camera viewport boundary during technical delivery.")
            if camera_image:
                st.caption("✅ Frame capture synchronized with session metadata.")

        if st.session_state["evaluation_results"]:
            st.markdown("---")
            st.markdown("### 📊 Live Session Performance Feedback Matrix")
            metric_col, gauge_col = st.columns([1.5, 1])
            
            with metric_col:
                st.markdown("#### Comprehensive Technical Assessment Summary")
                st.info(st.session_state["evaluation_results"]["raw_text"])
                
            with gauge_col:
                st.markdown("#### Score Verification Visual Vector")
                current_score = st.session_state["evaluation_results"]["score"]
                
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=current_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Calculated Score Target", 'font': {'color': "#f8fafc", 'size': 16}},
                    gauge={
                        'axis': {'range': [None, 10], 'tickwidth': 1, 'tickcolor': "#94a3b8"},
                        'bar': {'color': "#3b82f6"},
                        'bgcolor': "#1e293b",
                        'borderwidth': 2,
                        'bordercolor': "#334155",
                        'steps': [
                            {'range': [0, 5], 'color': '#ef4444'},
                            {'range': [5, 8], 'color': '#f59e0b'},
                            {'range': [8, 10], 'color': '#10b981'}
                        ],
                    }
                ))
                fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': "#f8fafc"}, height=280, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig_gauge, use_container_width=True)

# ===================== 2. HISTORICAL LOGS MATRIX =====================
elif st.session_state["current_menu"] == "Performance Ledger":
    st.markdown("## 🗄️ System Performance History Storage Matrix")
    data = get_results()
    
    if not data:
        st.info("No past operational history metrics compiled into workspace ledger.")
    else:
        for row in data:
            with st.expander(f"📦 Session Entry ID: {row[0]} | Performance Metric Score Evaluated: {row[4]} / 10"):
                st.markdown(f"**Question Challenged:** `{row[1]}`")
                st.markdown(f"**Submitted Narrative:**\n*{row[2]}*")
                st.markdown(f"**Evaluator Metric Output:**\n{row[3]}")

# ===================== 3. TELEMETRY GRAPHICS DASHBOARD =====================
elif st.session_state["current_menu"] == "Telemetry Dashboard":
    st.markdown("## 📈 Performance Analytics Reporting Matrix")
    data = get_results()
    
    if data:
        df = pd.DataFrame(data, columns=["ID", "Question", "Answer", "Feedback", "Score"])
        df = df.iloc[::-1].reset_index(drop=True)
        df['Historical Run Index'] = df.index + 1

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown("<div class='metric-container'><h4>Total Prompts Cleared</h4><h1 style='color:#3b82f6;'>{}</h1></div>".format(len(df)), unsafe_allow_html=True)
        with m2:
            st.markdown("<div class='metric-container'><h4>Mean Evaluation Track Score</h4><h1 style='color:#10b981;'>{} / 10</h1></div>".format(round(df['Score'].mean(), 2)), unsafe_allow_html=True)
        with m3:
            st.markdown("<div class='metric-container'><h4>Peak Vector Achieved</h4><h1 style='color:#f59e0b;'>{} / 10</h1></div>".format(df['Score'].max()), unsafe_allow_html=True)
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        fig = px.line(df, x="Historical Run Index", y="Score", title="Incremental Performance Trajectory Trace Analysis", markers=True)
        fig.update_traces(line_color='#6366f1', line_width=3, marker=dict(size=8, color='#10b981'))
        fig.update_layout(paper_bgcolor='#1e293b', plot_bgcolor='#1e293b', font_color='#f8fafc', yaxis=dict(range=[0, 10.5], gridcolor='#334155'), xaxis=dict(gridcolor='#334155'))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("System lacks adequate telemetry profiles. Complete live evaluation pipelines to chart data vectors.")