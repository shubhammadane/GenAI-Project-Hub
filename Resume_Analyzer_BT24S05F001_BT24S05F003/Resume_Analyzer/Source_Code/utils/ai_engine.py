import json
import re
import os
from typing import Dict, Any, Optional

SYSTEM_PROMPT = """You are an elite Silicon Valley Technical Recruiter, Hiring Manager, and ATS (Applicant Tracking System) Expert.
Your job is to thoroughly analyze the provided candidate resume, compare it against the Target Job Role / Job Description (if provided), provide actionable, constructive suggestions to maximize their interview chances, and generate 10+ tailored, high-caliber interview questions with model answers.

Respond ONLY with a valid JSON object matching the following exact JSON structure, without any markdown formatting around it (do not wrap in ```json ... ```, just pure valid JSON text):

{
  "ats_score": 85,
  "ats_rating": "Competitive Match",
  "executive_summary": "A concise 2-3 sentence summary evaluating the candidate's core strengths, experience level, and market readiness.",
  "category_scores": {
    "technical_skills": 88,
    "experience_projects": 82,
    "quantifiable_impact": 75,
    "formatting_structure": 90,
    "role_alignment": 80
  },
  "key_strengths": [
    "Strength 1 with specific details",
    "Strength 2",
    "Strength 3",
    "Strength 4"
  ],
  "critical_improvements": [
    {
      "priority": "High",
      "area": "Quantifiable Metrics",
      "issue": "Specific weakness observed in resume",
      "suggestion": "Actionable, precise advice on how to fix it"
    },
    {
      "priority": "High",
      "area": "Keyword Optimization",
      "issue": "Missing relevant tools or concepts",
      "suggestion": "Add specific keywords such as..."
    },
    {
      "priority": "Medium",
      "area": "Impact Statements",
      "issue": "Bullet points list duties rather than achievements",
      "suggestion": "Use Google's X-Y-Z formula (Accomplished [X] as measured by [Y], by doing [Z])"
    }
  ],
  "matched_keywords": [
    "Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"
  ],
  "missing_keywords": [
    "Missing Keyword 1", "Missing Keyword 2", "Missing Keyword 3"
  ],
  "bullet_point_rewrites": [
    {
      "original": "A weak or average bullet point extracted from the resume",
      "improved": "A high-impact rewritten version using strong action verbs and metrics",
      "reason": "Why this rewritten version is significantly more compelling to recruiters and ATS"
    },
    {
      "original": "Another extracted bullet point from projects or experience",
      "improved": "High-impact rewrite with quantifiable outcome",
      "reason": "Enhanced clarity and technical ownership"
    }
  ],
  "interview_questions": [
    {
      "category": "Technical Deep Dive",
      "question": "In-depth technical question based directly on their listed skills or projects",
      "interviewer_intent": "What the interviewer is evaluating (e.g., depth of knowledge, edge case handling)",
      "model_answer": "Recommended response structure and key concepts the candidate should mention"
    },
    {
      "category": "Technical Deep Dive",
      "question": "Second technical question probing their tech stack or system architecture",
      "interviewer_intent": "Testing practical implementation experience",
      "model_answer": "Key points, trade-offs, and best practices to highlight"
    },
    {
      "category": "Project Architecture & Design",
      "question": "Specific question about a project listed on their resume (e.g. data flow, scalability, trade-offs)",
      "interviewer_intent": "Verifying project authenticity, decision making, and architectural trade-offs",
      "model_answer": "Step-by-step structure showing technical ownership and challenges overcome"
    },
    {
      "category": "Project Architecture & Design",
      "question": "Question about error handling, caching, or performance optimization in their projects",
      "interviewer_intent": "Assessing production-readiness knowledge",
      "model_answer": "Strategies for monitoring, caching, and fallback handling"
    },
    {
      "category": "Behavioral (STAR Method)",
      "question": "Tell me about a challenging technical hurdle you faced in your project and how you solved it.",
      "interviewer_intent": "Assessing problem-solving under pressure and perseverance",
      "model_answer": "STAR framework: Situation (context), Task (goal), Action (technical actions taken), Result (measurable positive outcome)"
    },
    {
      "category": "Behavioral (STAR Method)",
      "question": "Describe a time you had to quickly learn an unfamiliar technology or framework to deliver a feature.",
      "interviewer_intent": "Assessing learning agility and curiosity",
      "model_answer": "Structure highlighting documentation review, prototyping, and fast delivery"
    },
    {
      "category": "Role & Domain Specific",
      "question": "Question tailored specifically for the target role",
      "interviewer_intent": "Assessing role readiness and industry awareness",
      "model_answer": "High-level industry perspective and best practices"
    },
    {
      "category": "Role & Domain Specific",
      "question": "How do you ensure code quality, testability, and maintainability in your development workflow?",
      "interviewer_intent": "Evaluating engineering discipline and standard operating procedures",
      "model_answer": "Mention unit tests, CI/CD, linting, code reviews, and documentation"
    }
  ]
}
"""

def extract_json_from_llm_response(text: str) -> Optional[Dict[str, Any]]:
    """Clean markdown backticks or extra text and parse JSON safely."""
    text = text.strip()
    
    # Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try removing ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except Exception:
            pass

    # Try extracting outermost curly braces
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = text[start : end + 1]
        try:
            return json.loads(snippet)
        except Exception:
            pass

    return None

def analyze_with_gemini(resume_text: str, target_role: str, job_description: str, api_key: str, model_name: str = "gemini-1.5-flash") -> Dict[str, Any]:
    """Analyze resume using Google Gemini Free API with dynamic model discovery and multiple fallbacks."""
    import google.generativeai as genai
    import requests

    api_key = api_key.strip()
    genai.configure(api_key=api_key)

    user_content = f"""
TARGET JOB ROLE:
{target_role if target_role else 'General Software Engineer / Tech Professional'}

JOB DESCRIPTION (JD):
{job_description if job_description else 'Standard industry requirements for ' + (target_role or 'Software Engineer')}

CANDIDATE RESUME:
{resume_text}

Analyze the resume thoroughly and provide the output in the required JSON format.
"""
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_content}"

    # Step 1: Discover available models for this specific API key
    candidates_to_try = [model_name]
    
    try:
        discovered = []
        for m in genai.list_models():
            if "generateContent" in getattr(m, "supported_generation_methods", []):
                clean_name = m.name.replace("models/", "")
                discovered.append(clean_name)
        
        if discovered:
            # Prioritize fast, free flash models, then pro
            preference_order = [
                model_name,
                "gemini-1.5-flash",
                "gemini-1.5-flash-latest",
                "gemini-2.0-flash",
                "gemini-2.0-flash-exp",
                "gemini-1.5-flash-8b",
                "gemini-1.5-pro",
                "gemini-pro"
            ]
            ordered = [m for m in preference_order if m in discovered]
            # Add any other discovered models not in preference
            for d in discovered:
                if d not in ordered:
                    ordered.append(d)
            if ordered:
                candidates_to_try = ordered
    except Exception as e:
        print(f"Notice: list_models failed ({e}), using default model fallback chain.")
        # Fallback list of common models
        candidates_to_try = [
            model_name,
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-2.0-flash",
            "gemini-1.5-pro",
            "gemini-pro"
        ]

    # Remove duplicates preserving order
    seen = set()
    deduped_candidates = []
    for c in candidates_to_try:
        if c and c not in seen:
            seen.add(c)
            deduped_candidates.append(c)

    last_error = None

    # Step 2: Try SDK with each candidate model
    for candidate in deduped_candidates:
        try:
            # Try with JSON mime type
            try:
                model = genai.GenerativeModel(
                    model_name=candidate,
                    system_instruction=SYSTEM_PROMPT,
                    generation_config={"temperature": 0.2, "response_mime_type": "application/json"}
                )
                response = model.generate_content(user_content)
                parsed = extract_json_from_llm_response(response.text)
                if parsed:
                    return parsed
            except Exception:
                # Some older models don't support system_instruction or response_mime_type
                model = genai.GenerativeModel(model_name=candidate)
                response = model.generate_content(full_prompt)
                parsed = extract_json_from_llm_response(response.text)
                if parsed:
                    return parsed
        except Exception as err:
            last_error = err
            continue

    # Step 3: Direct HTTP REST API fallback (v1beta and v1)
    for api_version in ["v1beta", "v1"]:
        for candidate in deduped_candidates[:3]:
            try:
                url = f"https://generativelanguage.googleapis.com/{api_version}/models/{candidate}:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {"temperature": 0.2}
                }
                res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=45)
                if res.status_code == 200:
                    data = res.json()
                    candidates_resp = data.get("candidates", [])
                    if candidates_resp:
                        text_resp = candidates_resp[0]["content"]["parts"][0]["text"]
                        parsed = extract_json_from_llm_response(text_resp)
                        if parsed:
                            return parsed
            except Exception as rest_err:
                last_error = rest_err
                continue

    if last_error:
        raise ValueError(f"All Gemini models failed. Last error: {str(last_error)}")
    raise ValueError("Failed to obtain valid analysis response from Gemini.")

def analyze_with_groq(resume_text: str, target_role: str, job_description: str, api_key: str, model_name: str = "llama-3.3-70b-versatile") -> Dict[str, Any]:
    """Analyze resume using Groq Free API (OpenAI-compatible)."""
    import requests

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    user_content = f"""
TARGET JOB ROLE:
{target_role if target_role else 'General Software Engineer / Tech Professional'}

JOB DESCRIPTION (JD):
{job_description if job_description else 'Standard industry requirements for ' + (target_role or 'Software Engineer')}

CANDIDATE RESUME:
{resume_text}

Analyze the resume thoroughly and output ONLY valid JSON according to instructions.
"""
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=60)
    response.raise_for_status()
    result = response.json()
    content = result["choices"][0]["message"]["content"]
    parsed = extract_json_from_llm_response(content)
    if not parsed:
        raise ValueError("Failed to parse JSON response from Groq.")
    return parsed

def analyze_offline_heuristics(resume_text: str, target_role: str = "", job_description: str = "") -> Dict[str, Any]:
    """
    Intelligent Local Fallback / Offline Engine.
    Ensures the project is 100% testable and never fails even without an API key or when offline.
    Uses regex, NLP heuristics, and skill dictionaries to generate full structured feedback.
    """
    text_lower = resume_text.lower()
    
    # Common tech skill bank
    KNOWN_SKILLS = [
        "python", "java", "c++", "c#", "javascript", "typescript", "html", "css", "react", "angular",
        "vue", "node.js", "express", "fastapi", "django", "flask", "spring", "sql", "mysql", "postgresql",
        "mongodb", "redis", "docker", "kubernetes", "aws", "gcp", "azure", "git", "github", "linux",
        "ci/cd", "rest api", "graphql", "machine learning", "deep learning", "nlp", "generative ai",
        "langchain", "pytorch", "tensorflow", "pandas", "numpy", "scikit-learn", "data structures",
        "algorithms", "system design", "microservices", "unit testing", "agile", "scrum"
    ]
    
    found_skills = [s.title() for s in KNOWN_SKILLS if s in text_lower]
    
    # Action verbs check
    ACTION_VERBS = ["architected", "developed", "designed", "implemented", "optimized", "spearheaded", "engineered", "built", "launched", "reduced", "increased", "improved"]
    found_verbs = [v for v in ACTION_VERBS if v in text_lower]
    
    # Metrics check (e.g. 20%, 3x, $50k, 100+)
    metrics = re.findall(r"\b(?:\d+%(?: reduction| increase)?|\d+x|\d+\+? (?:users|projects|stars|req|ms))\b", text_lower)
    
    # Check section presence
    has_summary = any(k in text_lower for k in ["summary", "objective", "about me", "profile"])
    has_skills = any(k in text_lower for k in ["skills", "technical skills", "tech stack", "competencies"])
    has_projects = any(k in text_lower for k in ["projects", "personal projects", "academic projects"])
    has_experience = any(k in text_lower for k in ["experience", "work experience", "employment", "internship"])
    has_education = any(k in text_lower for k in ["education", "academic", "bachelor", "degree", "university", "college"])
    
    # Score calculation
    tech_score = min(95, max(45, len(found_skills) * 6))
    proj_score = 88 if has_projects else 55
    metric_score = min(92, max(40, len(metrics) * 15 + (15 if len(found_verbs) > 3 else 0)))
    format_score = 60 + (10 if has_summary else 0) + (10 if has_skills else 0) + (10 if has_education else 0) + (10 if has_experience else 0)
    
    # Overall score
    total_score = int(tech_score * 0.3 + proj_score * 0.25 + metric_score * 0.2 + format_score * 0.25)
    total_score = max(45, min(96, total_score))
    
    rating = "Strong Fit" if total_score >= 82 else ("Competitive Match" if total_score >= 70 else "Needs Work")
    
    # Strengths
    strengths = []
    if len(found_skills) >= 5:
        strengths.append(f"Strong technical skill breadth: Detected key proficiencies including {', '.join(found_skills[:4])}.")
    if has_projects:
        strengths.append("Concrete project experience demonstrating hands-on execution and problem-solving.")
    if found_verbs:
        strengths.append("Effective use of active verbs depicting engineering initiative (e.g., " + ", ".join([v.capitalize() for v in found_verbs[:3]]) + ").")
    if metrics:
        strengths.append("Inclusion of measurable outcomes and quantitative metrics that demonstrate real impact.")
    else:
        strengths.append("Clean educational and academic credentials outlined with solid foundations.")

    # Critical Improvements
    improvements = []
    if not metrics or len(metrics) < 2:
        improvements.append({
            "priority": "High",
            "area": "Quantifiable Achievements",
            "issue": "Bullet points primarily focus on responsibilities rather than measurable business/technical outcomes.",
            "suggestion": "Adopt Google's X-Y-Z formula: 'Accomplished [X] as measured by [Y] by doing [Z]'. Example: 'Reduced query latency by 35% through Redis caching'."
        })
    if not has_summary:
        improvements.append({
            "priority": "Medium",
            "area": "Professional Summary",
            "issue": "Missing a crisp 2-3 line executive summary at the top of the resume.",
            "suggestion": "Add a dedicated summary highlighting your core tech stack, years of experience/education, and unique value proposition."
        })
    if len(found_skills) < 8:
        improvements.append({
            "priority": "High",
            "area": "Technical Breadth & Keywords",
            "issue": "Low density of modern cloud/DevOps and testing frameworks.",
            "suggestion": "Integrate industry-standard tooling like Docker, CI/CD, Git, and automated testing frameworks relevant to target roles."
        })
    improvements.append({
        "priority": "Low",
        "area": "ATS Formatting Consistency",
        "issue": "Standardize dates, font hierarchy, and avoid multi-column layouts.",
        "suggestion": "Ensure consistent bullet point styling and explicit dates (e.g., 'June 2023 – Present') for seamless ATS parsing."
    })

    # Missing keywords comparison
    target_role_display = target_role if target_role else "Software Engineer"
    common_target_keywords = ["Docker", "PostgreSQL", "CI/CD", "Unit Testing", "System Design", "Cloud (AWS/GCP)", "Agile/Scrum", "Git"]
    missing = [kw for kw in common_target_keywords if kw.lower() not in text_lower][:5]

    # Sample rewrite
    rewrites = [
        {
            "original": "Worked on a web application project and handled backend database queries.",
            "improved": "Architected resilient backend REST APIs using FastAPI and PostgreSQL, optimizing database indexes to reduce query latency by 40%.",
            "reason": "Replaces passive language with active verbs, explicitly mentions technical tools, and adds a quantifiable metric."
        },
        {
            "original": "Responsible for fixing bugs and improving the user interface.",
            "improved": "Resolved 25+ critical UI/UX and state management bugs in React, boosting user workflow efficiency and cross-browser responsiveness.",
            "reason": "Demonstrates proactive problem ownership, volume of contribution, and user-centric focus."
        }
    ]

    # Interview questions
    questions = [
        {
            "category": "Technical Deep Dive",
            "question": f"Can you explain the core architectural trade-offs you encountered when building your backend services or APIs?",
            "interviewer_intent": "Testing system design intuition, framework understanding, and scalability foresight.",
            "model_answer": "Start with requirements, explain database selection (relational vs NoSQL), discuss state management, caching (e.g., Redis), and handling concurrency."
        },
        {
            "category": "Technical Deep Dive",
            "question": f"How do you approach database query optimization and indexing when experiencing high latency?",
            "interviewer_intent": "Evaluating practical debugging, SQL profiling (EXPLAIN ANALYZE), and database indexing knowledge.",
            "model_answer": "Explain execution plans, identifying sequential scans, adding composite indexes, connection pooling, and introducing a caching layer."
        },
        {
            "category": "Project Architecture & Design",
            "question": "Walk me through the most complex project listed on your resume. What was your specific technical contribution?",
            "interviewer_intent": "Verifying resume authenticity, code ownership, and ability to clearly articulate technical complexity.",
            "model_answer": "Use a 3-part structure: 1) Problem context & system architecture, 2) The most challenging technical component you personally built, 3) The verified outcome and lessons learned."
        },
        {
            "category": "Project Architecture & Design",
            "question": "How did you handle error boundaries, edge cases, and graceful degradation in your distributed or web application?",
            "interviewer_intent": "Assessing production-grade resilience vs naive academic code.",
            "model_answer": "Discuss structured logging, try/except boundaries, retry mechanisms with exponential backoff, health check endpoints, and user-friendly error states."
        },
        {
            "category": "Behavioral (STAR Method)",
            "question": "Describe a scenario where a project deadline was approaching and you ran into an unexpected bug or blocking dependency. How did you resolve it?",
            "interviewer_intent": "Assessing composure under pressure, prioritization, and communication.",
            "model_answer": "Situation: Looming release deadline. Task: Fix critical data serialization bug. Action: Isolated reproduction steps with unit tests, paired with teammate, implemented targeted patch. Result: Delivered on time with zero regressions."
        },
        {
            "category": "Behavioral (STAR Method)",
            "question": "Tell me about a time you received constructive criticism during a code review. How did you handle it?",
            "interviewer_intent": "Evaluating humility, team collaboration, and dedication to high software engineering standards.",
            "model_answer": "Acknowledge the feedback graciously, explain the architectural insight gained, verify the fix, and document the pattern so the whole team benefits."
        },
        {
            "category": "Role & Domain Specific",
            "question": f"As an aspiring {target_role_display}, what steps do you take to stay updated with modern Generative AI and software development trends?",
            "interviewer_intent": "Assessing long-term curiosity, self-driven learning, and technology passion.",
            "model_answer": "Mention following engineering blogs (e.g. Google AI, Uber Eng), experimenting with hands-on hobby projects, contributing to open-source or building prototypes."
        },
        {
            "category": "Role & Domain Specific",
            "question": "What is your approach to writing automated unit and integration tests for software you develop?",
            "interviewer_intent": "Testing adherence to test-driven principles and code maintainability.",
            "model_answer": "Mention pytest/mocking, testing critical path logic, mocking external API dependencies, and enforcing minimum test coverage through CI/CD gates."
        }
    ]

    return {
        "ats_score": total_score,
        "ats_rating": rating,
        "executive_summary": f"Candidate demonstrates solid fundamentals with {len(found_skills)} identified core competencies and hands-on project implementations. The profile aligns moderately to strongly with {target_role_display} opportunities.",
        "category_scores": {
            "technical_skills": tech_score,
            "experience_projects": proj_score,
            "quantifiable_impact": metric_score,
            "formatting_structure": format_score,
            "role_alignment": min(95, total_score + 2)
        },
        "key_strengths": strengths,
        "critical_improvements": improvements,
        "matched_keywords": found_skills[:10] if found_skills else ["Python", "Git", "Problem Solving"],
        "missing_keywords": missing,
        "bullet_point_rewrites": rewrites,
        "interview_questions": questions
    }
