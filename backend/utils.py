import json
import os
from typing import List,Dict,Optional
from rapidfuzz import fuzz
import string
from PyPDF2 import PdfReader
from docx import Document
from itertools import islice

def load_faqs(filepath:str) ->List[Dict[str,str]]:
    """returns a list of directories"""

    if not os.path.exists(filepath):
        return[]
    
    with open(filepath,"r", encoding="utf-8") as f:
        return json.load(f)

# Load skills JSON once
def load_skills(json_path="skills.json"):
    if not os.path.exists(json_path):
        return {}
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SKILLS_PATH = BASE_DIR / "data" / "skills.json"

skills_json = load_skills(SKILLS_PATH)

# Flatten all skills for easier matching
all_skills = [skill.lower() for category in skills_json.values() for skill in category]

if all_skills:
    max_words_in_skill = max(len(skill.split()) for skill in all_skills)
else:
    max_words_in_skill = 1  # fallback
    print("Warning: No skills found in skills.json. Gap analysis may not work properly.")

def normalize(text: str) -> str:
    return text.lower().translate(str.maketrans("", "", string.punctuation)).strip()

def generate_ngrams(words_list, n):
    return [" ".join(words_list[i:i+n]) for i in range(len(words_list)-n+1)]


def find_answer(user_question: str, faqs: List[Dict[str, str]]) -> Optional[str]:
    user_norm = normalize(user_question)
    for faq in faqs:
        # Compare lowercase versions
        faq_norm = normalize(faq["question"])
        score = fuzz.ratio(user_norm, faq_norm)
        if score >= 85:
            return faq["answer"]
    return None

def parse_resume(file_path: str) -> str:
    text=""
    try:
        if file_path.endswith(".pdf"):
         reader=PdfReader(file_path)
         text=" ".join([page.extract_text() for page in reader.pages])
        elif file_path.endswith(".docx"):
         doc=Document(file_path)
         text=" ".join([para.text for para in doc.paragraphs]) 
    except Exception as e:
        print(f"Error parsing {file_path}:{e}")
    return text

def analyze_gap_fuzzy(resume_text: str, jd_text: str, all_skills: set, threshold=85):
    resume_text = resume_text.lower()
    jd_text = jd_text.lower()
    if not resume_text or not jd_text:
       return 0, set()

    matched = set()
    jd_skills_in_text = {skill for skill in all_skills if skill in jd_text}
    
    resume_words = resume_text.split()

    # Check n-grams from 1 to max_words_in_skill
    ngrams = []
    for n in range(1, max_words_in_skill+1):
        ngrams.extend(generate_ngrams(resume_words, n))
    
    # Fuzzy match each JD skill against n-grams
    for skill in jd_skills_in_text:
        for gram in ngrams:
            if fuzz.ratio(skill, gram) >= threshold:
                matched.add(skill)
                break  # no need to match the same skill multiple times
    
    score = (len(matched) / len(jd_skills_in_text) * 100) if jd_skills_in_text else 0
    return score, matched




def generate_questions(role_descriptions: str,client) -> str:
    response=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"user","content":f"Generate interview questions for: {role_descriptions}"}],
    )
    return response.choices[0].message.content

def evaluate_answer(question: str, answer: str,client) -> str:
    response=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": f"Evaluate this answer:\nQ: {question}\nA: {answer}"}],
    )
    return response.choices[0].message.content