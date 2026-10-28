import os
import json
import streamlit as st
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from utils.resume_parser import extract_text, clean_extracted_text
from utils.ai_engine import (
    analyze_with_gemini,
    analyze_with_groq,
    analyze_offline_heuristics
)
from utils.sample_resumes import (
    SAMPLE_RESUME_SWE,
    SAMPLE_JD_SWE,
    SAMPLE_RESUME_JUNIOR,
    SAMPLE_JD_JUNIOR
)

# Page configuration
st.set_page_config(
    page_title="AI Resume Intelligence & Interview Prep",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Professional CSS
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Polish */
    .main .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1250px;
    }

    /* Header styling */
    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 50%, #06B6D4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
        letter-spacing: -0.02em;
    }
    
    .hero-subtitle {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
        font-weight: 400;
    }

    .badge-tag {
        display: inline-block;
        background: rgba(37, 99, 235, 0.1);
        color: #2563EB;
        font-size: 0.8rem;
        font-weight: 600;
        padding: 4px 12px;
        border-radius: 9999px;
        border: 1px solid rgba(37, 99, 235, 0.2);
        margin-bottom: 0.8rem;
    }

    /* Metric & Scorecard Cards */
    .metric-card {
        background: #FFFFFF;
        border-radius: 14px;
        padding: 20px;
        border: 1px solid #E2E8F0;
        box-shadow: 0 4px 20px -4px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px -4px rgba(0, 0, 0, 0.09);
    }

    .score-badge {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1;
        margin: 8px 0;
    }
    .score-green { color: #10B981; }
    .score-blue { color: #3B82F6; }
    .score-amber { color: #F59E0B; }
    .score-red { color: #EF4444; }

    /* Custom Strength & Improvement Cards */
    .strength-item {
        background: #F0FDF4;
        border-left: 4px solid #22C55E;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 0 8px 8px 0;
        color: #166534;
        font-size: 0.95rem;
        font-weight: 500;
    }

    .improvement-item {
        background: #FFFBEB;
        border-left: 4px solid #F59E0B;
        padding: 14px 16px;
        margin-bottom: 12px;
        border-radius: 0 8px 8px 0;
    }

    .improvement-high {
        background: #FEF2F2;
        border-left: 4px solid #EF4444;
    }

    .priority-badge {
        font-size: 0.72rem;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        margin-right: 8px;
    }
    .priority-high { background: #FEE2E2; color: #DC2626; }
    .priority-med { background: #FEF3C7; color: #D97706; }
    .priority-low { background: #E0E7FF; color: #4338CA; }

    /* Skill Chips */
    .skill-chip {
        display: inline-block;
        background: #EFF6FF;
        color: #1D4ED8;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px 4px 4px 0;
        border: 1px solid #BFDBFE;
    }

    .missing-chip {
        display: inline-block;
        background: #FEF2F2;
        color: #B91C1C;
        padding: 5px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 4px 4px 4px 0;
        border: 1px solid #FECACA;
    }

    /* Rewrite Box */
    .rewrite-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 16px;
    }

    .before-text {
        background: #FFF1F2;
        border-left: 3px solid #F43F5E;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        color: #9F1239;
        font-size: 0.92rem;
        margin-bottom: 10px;
    }

    .after-text {
        background: #ECFDF5;
        border-left: 3px solid #10B981;
        padding: 10px 14px;
        border-radius: 0 6px 6px 0;
        color: #065F46;
        font-size: 0.92rem;
        font-weight: 500;
        margin-bottom: 8px;
    }

    /* Interview Question Card */
    .interview-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }

    /* Streamlit Button Tweaks */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #2563EB 0%, #4F46E5 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }
    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #4338CA 100%);
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.35);
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR CONFIGURATION -----------------
with st.sidebar:
    st.markdown("### ⚙️ Engine Settings")
    
    api_provider = st.selectbox(
        "AI Provider / Mode",
        options=["Google Gemini (Recommended Free)", "Groq AI (Ultra Fast Free)", "Offline Heuristic Engine (No API Key)"],
        index=0,
        help="Google Gemini and Groq offer generous free API tiers. The Offline Heuristic mode works immediately without any key."
    )

    api_key = ""
    model_choice = ""

    if api_provider == "Google Gemini (Recommended Free)":
        env_gemini_key = os.getenv("GEMINI_API_KEY", "")
        api_key = st.text_input(
            "Gemini API Key",
            value=env_gemini_key,
            type="password",
            placeholder="AIzaSy...",
            help="Get your free API key at https://aistudio.google.com/app/apikey"
        )
        st.markdown(
            """<small>🔑 <a href="https://aistudio.google.com/app/apikey" target="_blank" style="color: #2563EB;">Get Free Gemini API Key (1-click)</a></small>""",
            unsafe_allow_html=True
        )
        model_choice = st.selectbox(
            "Gemini Model",
            options=["Auto-Detect (Recommended)", "gemini-1.5-flash", "gemini-2.0-flash", "gemini-1.5-pro", "gemini-pro"],
            index=0
        )
        if model_choice == "Auto-Detect (Recommended)":
            model_choice = "gemini-1.5-flash"

    elif api_provider == "Groq AI (Ultra Fast Free)":
        env_groq_key = os.getenv("GROQ_API_KEY", "")
        api_key = st.text_input(
            "Groq API Key",
            value=env_groq_key,
            type="password",
            placeholder="gsk_...",
            help="Get your free key at https://console.groq.com/keys"
        )
        st.markdown(
            """<small>🔑 <a href="https://console.groq.com/keys" target="_blank" style="color: #2563EB;">Get Free Groq API Key</a></small>""",
            unsafe_allow_html=True
        )
        model_choice = st.selectbox(
            "Groq Model",
            options=["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"],
            index=0
        )

    else:
        st.info("💡 Offline mode uses NLP rules, keyword mapping, and heuristic scoring. No internet or API key required!")

    st.markdown("---")
    st.markdown("### 🎯 Target Job Parameters")
    target_role = st.text_input(
        "Target Role / Position",
        value="Associate Software Engineer / Full-Stack Developer",
        placeholder="e.g. Data Scientist, Cloud Engineer, Product Manager"
    )

    experience_level = st.selectbox(
        "Target Seniority Level",
        options=["Entry-Level / Fresher (0-1 yrs)", "Junior Developer (1-3 yrs)", "Mid-Level (3-5 yrs)", "Senior (5+ yrs)"],
        index=0
    )

    st.markdown("---")
    st.markdown("### 🧪 Quick 1-Click Test Data")
    col_demo1, col_demo2 = st.columns(2)
    with col_demo1:
        if st.button("Sample: SWE", use_container_width=True):
            st.session_state["resume_text_content"] = SAMPLE_RESUME_SWE
            st.session_state["jd_text_content"] = SAMPLE_JD_SWE
            st.rerun()
    with col_demo2:
        if st.button("Sample: Fresher", use_container_width=True):
            st.session_state["resume_text_content"] = SAMPLE_RESUME_JUNIOR
            st.session_state["jd_text_content"] = SAMPLE_JD_JUNIOR
            st.rerun()

    st.markdown("---")
    st.caption("🎓 GECA CS | Generative AI Honours Project")

# Initialize session state keys if not present
if "resume_text_content" not in st.session_state:
    st.session_state["resume_text_content"] = ""
if "jd_text_content" not in st.session_state:
    st.session_state["jd_text_content"] = ""

# ----------------- MAIN CONTENT -----------------
st.markdown('<span class="badge-tag">✨ Generative AI Career Suite</span>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">AI Resume Analyzer & Interview Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Elevate your candidacy with real-time ATS scoring, gap diagnostics, bullet point rewrites, and 10+ tailored interview questions.</p>', unsafe_allow_html=True)

# Resume Input Section
col_left, col_right = st.columns([1.1, 0.9], gap="large")

with col_left:
    st.markdown("#### 📄 1. Upload or Paste Resume")
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF, DOCX, TXT)",
        type=["pdf", "docx", "doc", "txt"],
        help="Upload your existing resume file. Text will be cleanly extracted."
    )

    # If file uploaded, detect new upload and extract text
    if uploaded_file is not None:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state.get("last_uploaded_file_id") != file_id:
            extracted = extract_text(uploaded_file)
            if extracted.strip():
                st.session_state["resume_text_content"] = extracted
                st.session_state["last_uploaded_file_id"] = file_id
                st.success(f"✅ Successfully extracted {len(extracted.split())} words from `{uploaded_file.name}`")
                st.rerun()
            else:
                st.error(f"⚠️ Could not extract text from `{uploaded_file.name}`. If this PDF is a scanned image or photo, please paste the text directly into the box below.")
        else:
            word_count = len(st.session_state["resume_text_content"].split())
            st.success(f"📄 Loaded `{uploaded_file.name}` ({word_count} words extracted)")

    # Text Area for manual edit or preview (bound directly to resume_text_content)
    st.text_area(
        "Resume Text Content (Preview & Edit):",
        height=260,
        placeholder="Upload a document above or paste your complete resume text here...",
        key="resume_text_content"
    )

with col_right:
    st.markdown("#### 🎯 2. Target Job Description (Optional but Recommended)")
    st.text_area(
        "Paste Job Description / Requirements:",
        height=260,
        placeholder="Paste the target job description here to enable direct keyword gap analysis, ATS match percentage, and targeted interview question generation...",
        key="jd_text_content"
    )

# Action Button
st.markdown("<br>", unsafe_allow_html=True)
analyze_col, clear_col, _ = st.columns([2, 1, 3])

with analyze_col:
    analyze_clicked = st.button("🚀 Analyze Resume & Generate Insights", use_container_width=True)

with clear_col:
    if st.button("🔄 Reset All", use_container_width=True):
        st.session_state["resume_text_content"] = ""
        st.session_state["jd_text_content"] = ""
        st.session_state["last_uploaded_file_id"] = None
        if "analysis_results" in st.session_state:
            del st.session_state["analysis_results"]
        st.rerun()

# ----------------- ANALYSIS PROCESSING -----------------
if analyze_clicked:
    current_resume = st.session_state.get("resume_text_content", "").strip()

    # Fail-safe: if text box was somehow empty but file is present, extract directly
    if not current_resume and uploaded_file is not None:
        current_resume = extract_text(uploaded_file).strip()
        if current_resume:
            st.session_state["resume_text_content"] = current_resume

    current_jd = st.session_state.get("jd_text_content", "").strip()

    if not current_resume:
        if uploaded_file is not None:
            st.error(f"⚠️ We detected your uploaded file `{uploaded_file.name}`, but no selectable text could be extracted. If your resume is an image/scanned PDF, please copy-paste the text directly into the box above.")
        else:
            st.error("⚠️ Please upload a resume file (PDF, DOCX) or paste your resume text in the box above to begin analysis.")
    else:
        with st.spinner("Analyzing resume against industry ATS benchmarks and generating questions..."):
            try:
                results = None
                
                # Check chosen provider
                if api_provider == "Google Gemini (Recommended Free)":
                    if not api_key:
                        st.warning("⚠️ No Gemini API key provided. Automatically falling back to our high-accuracy **Offline Heuristic Engine**!")
                        results = analyze_offline_heuristics(current_resume, target_role, current_jd)
                    else:
                        try:
                            results = analyze_with_gemini(
                                resume_text=current_resume,
                                target_role=target_role,
                                job_description=current_jd,
                                api_key=api_key,
                                model_name=model_choice
                            )
                        except Exception as e:
                            st.warning(f"⚠️ Gemini API encountered an issue ({str(e)}). Seamlessly switched to **Offline Heuristic Engine** so your demo continues smoothly!")
                            results = analyze_offline_heuristics(current_resume, target_role, current_jd)

                elif api_provider == "Groq AI (Ultra Fast Free)":
                    if not api_key:
                        st.warning("⚠️ No Groq API key provided. Automatically using the **Offline Heuristic Engine**!")
                        results = analyze_offline_heuristics(current_resume, target_role, current_jd)
                    else:
                        try:
                            results = analyze_with_groq(
                                resume_text=current_resume,
                                target_role=target_role,
                                job_description=current_jd,
                                api_key=api_key,
                                model_name=model_choice
                            )
                        except Exception as e:
                            st.warning(f"⚠️ Groq API encountered an issue ({str(e)}). Switched to **Offline Heuristic Engine**!")
                            results = analyze_offline_heuristics(current_resume, target_role, current_jd)

                else:
                    results = analyze_offline_heuristics(current_resume, target_role, current_jd)

                if results:
                    st.session_state["analysis_results"] = results
                    st.success("🎉 Comprehensive Resume & Interview Analysis Complete!")

            except Exception as e:
                st.error(f"Error during analysis: {str(e)}")

# ----------------- RESULTS DASHBOARD -----------------
results = st.session_state.get("analysis_results")

if results:
    st.markdown("---")
    st.markdown("## 📊 Comprehensive AI Evaluation Dashboard")

    score = results.get("ats_score", 75)
    rating = results.get("ats_rating", "Competitive Match")
    cat_scores = results.get("category_scores", {})

    # Score color class
    if score >= 80:
        score_class = "score-green"
    elif score >= 65:
        score_class = "score-blue"
    elif score >= 50:
        score_class = "score-amber"
    else:
        score_class = "score-red"

    # Top Metric Banner
    top_col1, top_col2, top_col3, top_col4 = st.columns(4)
    with top_col1:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="color: #64748B; font-size: 0.88rem; font-weight: 600; text-transform: uppercase;">Overall ATS Score</div>
            <div class="score-badge {score_class}">{score}<span style="font-size: 1.5rem; color: #94A3B8;">/100</span></div>
            <div style="font-weight: 700; color: #1E293B;">{rating}</div>
        </div>
        """, unsafe_allow_html=True)

    with top_col2:
        tech_score = cat_scores.get("technical_skills", 80)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #64748B; font-size: 0.88rem; font-weight: 600; text-transform: uppercase;">Technical Skills</div>
            <div style="font-size: 2rem; font-weight: 800; color: #3B82F6; margin: 6px 0;">{tech_score}%</div>
            <div style="color: #64748B; font-size: 0.85rem;">Alignment with target stack</div>
        </div>
        """, unsafe_allow_html=True)

    with top_col3:
        impact_score = cat_scores.get("quantifiable_impact", 70)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #64748B; font-size: 0.88rem; font-weight: 600; text-transform: uppercase;">Quantifiable Impact</div>
            <div style="font-size: 2rem; font-weight: 800; color: #8B5CF6; margin: 6px 0;">{impact_score}%</div>
            <div style="color: #64748B; font-size: 0.85rem;">Metrics, numbers & scale</div>
        </div>
        """, unsafe_allow_html=True)

    with top_col4:
        format_score = cat_scores.get("formatting_structure", 85)
        st.markdown(f"""
        <div class="metric-card">
            <div style="color: #64748B; font-size: 0.88rem; font-weight: 600; text-transform: uppercase;">ATS Readability</div>
            <div style="font-size: 2rem; font-weight: 800; color: #10B981; margin: 6px 0;">{format_score}%</div>
            <div style="color: #64748B; font-size: 0.85rem;">Structure & section clarity</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Tabs for in-depth inspection
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Executive Summary & Recommendations",
        "🎯 ATS & Keyword Gap Analysis",
        "🎙️ Tailored Interview Questions & Model Answers",
        "✍️ Bullet Point Transformations (Rewrites)",
        "📥 Export Complete Report"
    ])

    # ---------------- TAB 1: SUMMARY & CRITICAL IMPROVEMENTS ----------------
    with tab1:
        st.markdown("### 📌 Executive Assessment")
        summary_text = results.get("executive_summary", "")
        st.info(f"💡 **Recruiter's Perspective:** {summary_text}")

        c_left, c_right = st.columns(2, gap="medium")

        with c_left:
            st.markdown("#### ✅ Key Profile Strengths")
            strengths = results.get("key_strengths", [])
            for s in strengths:
                st.markdown(f'<div class="strength-item">✓ {s}</div>', unsafe_allow_html=True)

        with c_right:
            st.markdown("#### ⚠️ High-Priority Actionable Improvements")
            improvements = results.get("critical_improvements", [])
            for imp in improvements:
                prio = imp.get("priority", "Medium")
                prio_class = "priority-high" if prio == "High" else ("priority-med" if prio == "Medium" else "priority-low")
                st.markdown(f"""
                <div class="improvement-item {'improvement-high' if prio == 'High' else ''}">
                    <div>
                        <span class="priority-badge {prio_class}">{prio} Priority</span>
                        <strong style="color: #0F172A;">{imp.get('area', 'General')}</strong>
                    </div>
                    <div style="font-size: 0.92rem; color: #475569; margin: 6px 0;"><strong>Issue:</strong> {imp.get('issue', '')}</div>
                    <div style="font-size: 0.92rem; color: #0F172A;"><strong>Fix:</strong> {imp.get('suggestion', '')}</div>
                </div>
                """, unsafe_allow_html=True)

    # ---------------- TAB 2: KEYWORD & ATS MATCH ----------------
    with tab2:
        st.markdown("### 🔍 Skill & ATS Keyword Diagnostics")
        st.markdown("Applicant Tracking Systems match your resume against job keywords. Here is your profile's keyword density breakdown:")

        k_col1, k_col2 = st.columns(2, gap="medium")

        with k_col1:
            st.markdown("#### 🟢 Matched Skills & Keywords Found")
            matched = results.get("matched_keywords", [])
            if matched:
                chips_html = "".join([f'<span class="skill-chip">{k}</span>' for k in matched])
                st.markdown(chips_html, unsafe_allow_html=True)
            else:
                st.write("No distinct keywords detected.")

        with k_col2:
            st.markdown("#### 🔴 Missing Keywords for Target Role")
            missing = results.get("missing_keywords", [])
            if missing:
                missing_html = "".join([f'<span class="missing-chip">+ {k}</span>' for k in missing])
                st.markdown(missing_html, unsafe_allow_html=True)
                st.caption("💡 Adding these technologies to your projects or coursework will notably increase ATS match percentage.")
            else:
                st.success("Great job! No prominent missing keywords detected.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 📐 Structural ATS Checklist")
        st.markdown("""
        - **Standard Fonts & Headings:** Ensure headings use standard titles (`Experience`, `Projects`, `Skills`, `Education`).
        - **Single-Column Format:** Avoid multi-column text tables that confuse automated parsers.
        - **File Format:** PDF is preferred, but ensure text is selectable (not flattened image scans).
        - **Date Format Consistency:** Use `MMM YYYY – MMM YYYY` (e.g. `Aug 2023 – Dec 2023`).
        """)

    # ---------------- TAB 3: INTERVIEW QUESTIONS ----------------
    with tab3:
        st.markdown("### 🎙️ AI-Generated Interview Preparation")
        st.markdown("Our Generative AI model analyzed your projects, claimed tools, and target role to generate **10+ realistic interview questions** along with winning model answers using the **STAR framework** (Situation, Task, Action, Result).")

        questions = results.get("interview_questions", [])

        # Filter by category
        categories = ["All Categories"] + list(set([q.get("category", "General") for q in questions]))
        selected_cat = st.selectbox("Filter Question Category:", options=categories, index=0)

        filtered_q = questions if selected_cat == "All Categories" else [q for q in questions if q.get("category") == selected_cat]

        for i, q in enumerate(filtered_q, 1):
            category = q.get("category", "General")
            question_text = q.get("question", "")
            intent = q.get("interviewer_intent", "Assessing competency")
            model_ans = q.get("model_answer", "Highlight key project metrics and engineering decisions.")

            with st.expander(f"**Q{i} [{category}]:** {question_text}", expanded=(i <= 2)):
                st.markdown(f"**🎯 Interviewer's Intent:** *{intent}*")
                st.markdown("---")
                st.markdown(f"**💡 Recommended Model Answer & Talking Points:**")
                st.info(model_ans)

    # ---------------- TAB 4: REWRITES ----------------
    with tab4:
        st.markdown("### ✍️ High-Impact Bullet Point Rewrites")
        st.markdown("Transform passive duty descriptions into high-converting, metric-backed accomplishment statements using Google's **X-Y-Z formula** (*Accomplished [X] as measured by [Y] by doing [Z]*):")

        rewrites = results.get("bullet_point_rewrites", [])
        for rw in rewrites:
            st.markdown(f"""
            <div class="rewrite-card">
                <div style="font-size: 0.8rem; font-weight: 700; color: #E11D48; text-transform: uppercase;">Original Bullet Point</div>
                <div class="before-text">❌ {rw.get('original', '')}</div>
                <div style="font-size: 0.8rem; font-weight: 700; color: #059669; text-transform: uppercase;">AI High-Impact Rewrite</div>
                <div class="after-text">⭐ {rw.get('improved', '')}</div>
                <div style="font-size: 0.88rem; color: #475569; margin-top: 6px;"><strong>Why this works:</strong> {rw.get('reason', '')}</div>
            </div>
            """, unsafe_allow_html=True)

    # ---------------- TAB 5: EXPORT REPORT ----------------
    with tab5:
        st.markdown("### 📥 Download Complete AI Analysis Report")
        st.markdown("Export a complete summary report containing your ATS scorecard, actionable recommendations, keyword gap diagnostics, and complete interview questions with model answers.")

        # Prepare export text
        report_text = f"""=======================================================
AI RESUME INTELLIGENCE & INTERVIEW PREPARATION REPORT
Target Role: {target_role}
=======================================================

OVERALL ATS SCORE: {score}/100 ({rating})
- Technical Skills Score: {cat_scores.get('technical_skills', 80)}%
- Quantifiable Impact Score: {cat_scores.get('quantifiable_impact', 70)}%
- ATS Readability Score: {cat_scores.get('formatting_structure', 85)}%
- Role Alignment: {cat_scores.get('role_alignment', 80)}%

EXECUTIVE SUMMARY:
{results.get('executive_summary', '')}

KEY STRENGTHS:
"""
        for s in results.get("key_strengths", []):
            report_text += f"- {s}\n"

        report_text += "\nCRITICAL IMPROVEMENTS:\n"
        for imp in results.get("critical_improvements", []):
            report_text += f"- [{imp.get('priority', 'Medium')} Priority] {imp.get('area')}: {imp.get('issue')}\n  Recommendation: {imp.get('suggestion')}\n"

        report_text += "\nMATCHED SKILLS:\n" + ", ".join(results.get("matched_keywords", [])) + "\n"
        report_text += "\nMISSING TARGET KEYWORDS:\n" + ", ".join(results.get("missing_keywords", [])) + "\n"

        report_text += "\n=======================================================\nINTERVIEW QUESTIONS & MODEL ANSWERS\n=======================================================\n"
        for i, q in enumerate(results.get("interview_questions", []), 1):
            report_text += f"\nQ{i} ({q.get('category')}): {q.get('question')}\n"
            report_text += f"Interviewer Intent: {q.get('interviewer_intent')}\n"
            report_text += f"Model Answer: {q.get('model_answer')}\n"

        st.download_button(
            label="📄 Download Full Analysis Report (.txt)",
            data=report_text,
            file_name="resume_analysis_report.txt",
            mime="text/plain",
            use_container_width=True
        )

# Footer
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; color: #94A3B8; font-size: 0.85rem; padding: 10px 0;">
    Built with Python & Generative AI | Department of Computer Science & Engineering | GECA Honours Project
</div>
""", unsafe_allow_html=True)
