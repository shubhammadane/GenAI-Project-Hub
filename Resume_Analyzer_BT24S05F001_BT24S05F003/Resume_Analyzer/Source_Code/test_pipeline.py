import sys
from utils.resume_parser import clean_extracted_text
from utils.sample_resumes import SAMPLE_RESUME_SWE, SAMPLE_JD_SWE
from utils.ai_engine import analyze_offline_heuristics

def test_pipeline():
    print("Testing Resume Text Processing...")
    cleaned = clean_extracted_text(SAMPLE_RESUME_SWE)
    assert len(cleaned) > 100, "Cleaned text too short!"
    print(f"Resume text length: {len(cleaned)} characters")

    print("\nTesting Heuristic & Analysis Engine...")
    result = analyze_offline_heuristics(
        resume_text=cleaned,
        target_role="Full-Stack Developer",
        job_description=SAMPLE_JD_SWE
    )

    print(f"ATS Score: {result.get('ats_score')}/100 ({result.get('ats_rating')})")
    print(f"Summary: {result.get('executive_summary')}")
    print(f"Strengths count: {len(result.get('key_strengths', []))}")
    print(f"Critical Improvements count: {len(result.get('critical_improvements', []))}")
    print(f"Interview Questions count: {len(result.get('interview_questions', []))}")
    print(f"Matched Keywords: {result.get('matched_keywords', [])}")

    assert result.get("ats_score") > 0, "ATS score must be positive"
    assert len(result.get("interview_questions", [])) >= 5, "Must generate interview questions"
    print("\n[SUCCESS] Pipeline test passed completely!")

if __name__ == "__main__":
    test_pipeline()
