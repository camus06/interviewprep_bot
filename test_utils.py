from backend.utils import (
    load_faqs, find_answer, parse_resume,
    analyze_gap_fuzzy, generate_questions, evaluate_answer, all_skills
)
from groq import Groq
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
FAQS = load_faqs(BASE_DIR / "data" / "faqs.json")

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

#Test FAQ matching
print("\n=== FAQ Test ===")
question = "What is Mission UpSkill India Hackathon by HCL GUVI ABES Edition 2025?"
answer = find_answer(question, FAQS)
print("Q:", question)
print("A:", answer)

#Test Resume Parsing
print("\n=== Resume Parsing Test ===")
resume_path = BASE_DIR / "samples" / "resume.pdf"  # create a test resume
resume_text = parse_resume(str(resume_path))
print("Extracted Resume Text (first 300 chars):", resume_text[:300])

#Test Gap Analysis
print("\n=== Gap Analysis Test ===")
jd_text = "We are looking for Python, SQL, and AWS developers"
score, matched = analyze_gap_fuzzy(resume_text, jd_text, all_skills)
print("Match Score:", score, "%")
print("Matched Skills:", matched)

#Test Interview Question Generation
print("\n=== AI Interview Question Generation Test ===")
role_desc = "Backend Developer skilled in Python and SQL"
questions = generate_questions(role_desc, client)
print("Generated Questions:\n", questions)

#Test Answer Evaluation
print("\n=== AI Answer Evaluation Test ===")
sample_question = "What is Python?"
sample_answer = "Python is a programming language."
feedback = evaluate_answer(sample_question, sample_answer, client)
print("Feedback:\n", feedback)
