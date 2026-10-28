# 💼 AI Resume Intelligence & Interview Preparation Platform

A state-of-the-art **Generative AI Resume Analyzer and Career Preparation Engine** built in Python with a sleek, modern UI. Designed to analyze candidate resumes against job descriptions, calculate ATS match scores, highlight critical gap areas, rewrite weak bullet points, and generate 10+ tailored interview questions with winning model answers using the **STAR framework**.

Developed for **Final Year B.Tech / Sem VII Generative AI Honours** (GECA CS).

---

## ✨ Key Features

1. **📄 Universal Multi-Format Resume Parser**
   - Seamlessly extracts text from **PDF (`.pdf`)**, **Word (`.docx`, `.doc`)**, and plain text (`.txt`).
   - Built-in text normalization to remove formatting artifacts and corrupted symbols.

2. **🤖 Generative AI Analysis with Free External APIs**
   - **Google Gemini API** (`gemini-1.5-flash`, `gemini-2.0-flash`): High-accuracy reasoning with free Google AI Studio keys.
   - **Groq Cloud API** (`llama-3.3-70b-versatile`): Ultra-fast inference with free Groq keys.
   - **🛡️ Built-in Offline Heuristic Fallback Engine**: If you don't have an API key or run out of quota during a presentation, the application seamlessly switches to a rule-based NLP engine so the demo **never crashes or fails**.

3. **📊 Comprehensive ATS Scorecard**
   - Overall ATS Score (out of 100) with color-coded badge.
   - Category breakdowns:
     - Technical Skills Alignment (%)
     - Experience & Projects (%)
     - Quantifiable Metrics & Numbers (%)
     - ATS Readability & Structure (%)
     - Role Alignment (%)

4. **🔍 Keyword & Skill Gap Diagnostics**
   - Highlights detected technical competencies.
   - Flags missing high-demand keywords required by the target job description.

5. **🎙️ AI Interview Preparation Generator**
   - Generates 10+ role-tailored interview questions categorized into:
     - **Technical Deep-Dive Questions**
     - **Behavioral & Situational Questions (STAR Method)**
     - **Project Architecture & Scalability Questions**
     - **Role-Specific & Best-Practice Questions**
   - Expandable cards with **Interviewer's Intent** and **Recommended Model Answers**.

6. **✍️ Bullet Point Transformation (X-Y-Z Formula)**
   - Shows "Before vs After" rewrites using Google's formula: *Accomplished [X] as measured by [Y], by doing [Z]*.

7. **⚡ 1-Click Demo Testing**
   - Pre-loaded sample resumes (Full-Stack SWE & Fresher) for instant evaluation without searching for PDF files.

8. **📥 Export Complete Report**
   - Download the full analysis, scorecard, and interview preparation guide in a single `.txt` / `.md` file.

---

## 📁 Project Structure

```text
Resume_Analyzer/
├── app.py                   # Main Streamlit web application & modern dashboard
├── requirements.txt         # Project dependencies
├── .env.example             # Environment variables template
├── test_pipeline.py         # Automated test script for parsing & heuristic engine
├── utils/
│   ├── resume_parser.py     # PDF & DOCX universal extraction logic
│   ├── ai_engine.py         # Google Gemini, Groq, and offline heuristic analysis engines
│   └── sample_resumes.py    # Pre-configured test resumes and job descriptions
└── README.md                # Documentation and guide
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+ installed.

### 2. Installation
Open PowerShell or your terminal in this project folder and run:

```bash
pip install -r requirements.txt
```

### 3. (Optional) Configure Free API Key
You can obtain a **100% free Gemini API key** in 30 seconds:
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey) and click **"Create API Key"**.
2. Either:
   - Paste the key directly in the web app sidebar when running, OR
   - Create a `.env` file from `.env.example`:
     ```bash
     copy .env.example .env
     ```
     and set `GEMINI_API_KEY=your_key_here`.

> **Note:** If you do not provide an API key, the system automatically uses the built-in **Offline Heuristic Engine**, allowing full offline demonstrations!

### 4. Run the Application
Start the Streamlit application:

```bash
streamlit run app.py
```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 🧪 Testing the Project

1. Click **"Sample: SWE"** or **"Sample: Fresher"** in the sidebar.
2. Click the **"🚀 Analyze Resume & Generate Insights"** button.
3. Explore the 5 tabs:
   - **Executive Summary & Recommendations**
   - **ATS & Keyword Gap Analysis**
   - **Tailored Interview Questions & Model Answers**
   - **Bullet Point Transformations (Rewrites)**
   - **Export Complete Report**
