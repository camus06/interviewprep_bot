import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import time
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import json
import os
from pathlib import Path
import tempfile
from backend.utils import parse_resume, analyze_gap_fuzzy, load_skills

# Configuration
BACKEND_URL = "http://localhost:8000"  # FastAPI backend URL
BASE_DIR = Path(__file__).resolve().parent
SKILLS_PATH = BASE_DIR / "data" / "skills.json"

# Load skills for gap analysis
skills_json = load_skills(SKILLS_PATH)
all_skills = [skill.lower() for category in skills_json.values() for skill in category]

# Page configuration
st.set_page_config(
    page_title="Smart Career Copilot",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
def inject_custom_css():
    st.markdown("""
    <style>
    /* Main styling */
    .main {
        padding: 2rem;
        max-width: 800px;
        margin: 0 auto;
    }
    
    /* Typography */
    body, .main, p, li {
        line-height: 1.75;
    }
    
    /* Headers */
    .main-header {
        font-family: 'Monsterrat', sans-serif;
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .section-header {
        font-family: 'Monsterrat', sans-serif;
                
        font-size: 1.5rem;
        font-weight: 700;
        color: #6e8efb;
        margin: 1.5rem 0 1rem 0;
        padding-left: 0;
    }
    
    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(110, 142, 251, 0.3);
    }
    
    /* File uploader */
    .stFileUploader {
        padding: 0;
        background: transparent;
    }
    /* Dropzone container */
    div[data-testid="stFileUploadDropzone"] {
        background-color: #2c2c32;
        border: 1px solid #3a3a3f;
        border-radius: 12px;
        padding: 1rem 1.25rem;
    }
    /* Dropzone text */
    div[data-testid="stFileUploadDropzone"] p {
        margin: 0.25rem 0;
        color: #d8dbe6;
    }
    /* Browse button inside dropzone */
    div[data-testid="stFileUploadDropzone"] button {
        background: transparent;
        color: #d8dbe6;
        border: 1px solid #4a4a50;
        border-radius: 10px;
        padding: 0.4rem 0.9rem;
    }
    
    /* Chat messages */
    .user-message {
        background-color: #252529;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid #6e8efb;
        border: 1px solid #e6e9ff;
    }
    
    .bot-message {
        background-color: #252529;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid #a777e3;
        border: 1px solid #e6e9ff;
    }
    
    /* Cards */
    .card {
        background-color: #252529;
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin: 1rem 0;
        border: 1px solid #e6e9ff;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
    }
    
    /* Hide default Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Ensure sidebar toggle is visible */
    .stApp > div:first-child > div:first-child > div:first-child {
        visibility: visible !important;
    }
    
    /* Show the sidebar toggle button */
    button[data-testid="baseButton-header"] {
        visibility: visible !important;
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# App header
st.markdown('<h1 class="main-header">Smart Career Copilot</h1>', unsafe_allow_html=True)
st.markdown("Your AI-powered interview preparation assistant. Upload your resume, get tailored questions, practice, and receive instant feedback.")

# Initialize session state
if 'resume_uploaded' not in st.session_state:
    st.session_state.resume_uploaded = False
if 'jd_provided' not in st.session_state:
    st.session_state.jd_provided = False
if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'interview_mode' not in st.session_state:
    st.session_state.interview_mode = None
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'sessions' not in st.session_state:
    # Each item: {id, title, timestamp, interview_mode, questions, user_answers}
    st.session_state.sessions = []
if 'performance_data' not in st.session_state:
    # Track performance metrics: {date, score, interview_type, questions_answered, completion_rate}
    st.session_state.performance_data = []

# Helpers for history management
def _make_session_title(mode: str, ts: float) -> str:
    try:
        return f"{mode or 'Session'} - {time.strftime('%Y-%m-%d %H:%M', time.localtime(ts))}"
    except Exception:
        return f"{mode or 'Session'}"

def archive_current_session():
    has_any_answer = bool(st.session_state.get('user_answers'))
    has_started = bool(st.session_state.get('interview_started'))
    if not (has_started or has_any_answer):
        return
    session_obj = {
        'id': f"sess_{int(time.time()*1000)}",
        'title': _make_session_title(st.session_state.get('interview_mode'), time.time()),
        'timestamp': time.time(),
        'interview_mode': st.session_state.get('interview_mode'),
        'questions': st.session_state.get('questions', []),
        'user_answers': st.session_state.get('user_answers', []),
        'current_question': st.session_state.get('current_question', 0),
    }
    # Avoid duplicating identical consecutive sessions
    if not st.session_state.sessions or st.session_state.sessions[-1].get('user_answers') != session_obj['user_answers']:
        st.session_state.sessions.append(session_obj)

def load_session(session_idx: int):
    try:
        sess = st.session_state.sessions[session_idx]
    except Exception:
        return
    st.session_state.interview_mode = sess.get('interview_mode')
    st.session_state.questions = sess.get('questions', [])
    st.session_state.user_answers = sess.get('user_answers', [])
    # Continue from next unanswered question
    st.session_state.current_question = min(len(st.session_state.user_answers), len(st.session_state.questions))
    st.session_state.interview_started = True
    st.rerun()

def reset_for_new_chat():
    archive_current_session()
    st.session_state.interview_started = False
    st.session_state.current_question = 0
    st.session_state.user_answers = []
    st.session_state.interview_mode = None
    st.session_state.questions = []
    st.rerun()

def calculate_interview_score(answers):
    """Calculate a mock score based on answers"""
    if not answers:
        return 0
    
    total_questions = len(answers)
    answered_questions = len([a for a in answers if a.get('answer', '').strip() and not a.get('skipped', False)])
    
    # Base score from completion rate
    completion_rate = answered_questions / total_questions if total_questions > 0 else 0
    base_score = completion_rate * 60  # 60 points for completion
    
    # Bonus points for answer length (mock quality indicator)
    avg_answer_length = sum(len(a.get('answer', '')) for a in answers if a.get('answer', '').strip()) / max(answered_questions, 1)
    quality_bonus = min(avg_answer_length / 50, 40)  # Up to 40 points for quality
    
    return min(int(base_score + quality_bonus), 100)

def add_performance_data(interview_mode, answers, questions):
    """Add performance data to tracking"""
    score = calculate_interview_score(answers)
    completion_rate = len([a for a in answers if a.get('answer', '').strip() and not a.get('skipped', False)]) / len(questions) if questions else 0
    
    performance_entry = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'score': score,
        'interview_type': interview_mode,
        'questions_answered': len([a for a in answers if a.get('answer', '').strip() and not a.get('skipped', False)]),
        'total_questions': len(questions),
        'completion_rate': completion_rate
    }
    
    st.session_state.performance_data.append(performance_entry)

def create_performance_charts():
    """Create performance tracking charts"""
    if not st.session_state.performance_data:
        return None, None, None
    
    df = pd.DataFrame(st.session_state.performance_data)
    df['date'] = pd.to_datetime(df['date'])
    
    # Score trend chart
    score_chart = px.line(df, x='date', y='score', 
                         title='Score Trend Over Time',
                         color='interview_type',
                         markers=True)
    score_chart.update_layout(height=200, showlegend=True)
    
    # Completion rate chart
    completion_chart = px.bar(df, x='date', y='completion_rate',
                             title='Interview Completion Rate',
                             color='interview_type')
    completion_chart.update_layout(height=200, showlegend=True)
    
    # Interview type distribution
    type_counts = df['interview_type'].value_counts()
    type_chart = px.pie(values=type_counts.values, names=type_counts.index,
                       title='Interview Types Attempted')
    type_chart.update_layout(height=200)
    
    return score_chart, completion_chart, type_chart

# AI Integration Functions
def call_backend_api(endpoint, data=None):
    """Call the FastAPI backend"""
    try:
        if data:
            response = requests.post(f"{BACKEND_URL}{endpoint}", json=data)
        else:
            response = requests.get(f"{BACKEND_URL}{endpoint}")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error: {response.status_code}")
            return None
    except requests.exceptions.ConnectionError:
        st.warning("Backend not running. Please start the FastAPI server.")
        return None

def generate_ai_questions(resume_text, job_description, interview_type, question_count):
    """Generate AI-powered interview questions"""
    prompt = f"""
    Based on the following resume and job description, generate {question_count} {interview_type.lower()} interview questions.
    
    Resume: {resume_text[:1000]}...
    
    Job Description: {job_description[:1000]}...
    
    Please provide {question_count} specific, relevant questions that would be asked in a {interview_type} interview for this role.
    Format each question on a new line starting with a number.
    """
    
    response = call_backend_api("/ask", {"question": prompt})
    if response:
        questions_text = response.get("answer", "")
        # Parse questions from the response
        questions = []
        for line in questions_text.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('Q:')):
                # Remove numbering and clean up
                question = line.split('.', 1)[-1].strip()
                if question.startswith('Q:'):
                    question = question[2:].strip()
                if question:
                    questions.append(question)
        
        return questions[:question_count] if questions else get_fallback_questions(interview_type, question_count)
    
    return get_fallback_questions(interview_type, question_count)

def get_fallback_questions(interview_type, question_count):
    """Fallback questions if AI generation fails"""
    if interview_type == "Technical":
        questions = [
            "How would you optimize this algorithm for better time complexity?",
            "Explain the concept of database indexing and why it's important.",
            "Describe your approach to debugging a complex production issue.",
            "How would you design a scalable notification system?",
            "What's the difference between REST and GraphQL APIs?"
        ]
    elif interview_type == "Behavioral":
        questions = [
            "Tell me about a time you had to deal with a difficult teammate.",
            "Describe a project where you had to meet a tight deadline.",
            "How do you handle receiving critical feedback?",
            "Tell me about a time you took initiative on a project.",
            "Describe a situation where you had to persuade others to adopt your idea."
        ]
    else:  # Mixed
        questions = [
            "How would you approach optimizing a slow database query?",
            "Tell me about a time you had to learn a new technology quickly.",
            "Explain the concept of dependency injection.",
            "Describe a situation where you had to make a trade-off between quality and speed.",
            "How would you design a URL shortening service?"
        ]
    
    return questions[:question_count]

def evaluate_answer_with_ai(question, answer):
    """Evaluate user's answer using AI"""
    prompt = f"""
    Evaluate this interview answer and provide constructive feedback:
    
    Question: {question}
    Answer: {answer}
    
    Please provide:
    1. A score out of 100
    2. Strengths of the answer
    3. Areas for improvement
    4. Specific suggestions for a better answer
    """
    
    response = call_backend_api("/ask", {"question": prompt})
    if response:
        return response.get("answer", "Evaluation not available.")
    
    return "AI evaluation not available. Please ensure the backend is running."

def analyze_resume_gap(resume_file, job_description):
    """Analyze resume and job description for skill gaps"""
    if not resume_file or not job_description:
        return None, None
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(resume_file.getvalue())
            tmp_file_path = tmp_file.name
        
        # Parse resume
        resume_text = parse_resume(tmp_file_path)
        
        # Clean up temp file
        os.unlink(tmp_file_path)
        
        if resume_text:
            # Analyze skill gap
            gap_score, matched_skills = analyze_gap_fuzzy(resume_text, job_description, set(all_skills))
            
            # Find missing skills
            jd_skills = {skill for skill in all_skills if skill in job_description.lower()}
            missing_skills = jd_skills - matched_skills
            
            return gap_score, missing_skills
        
    except Exception as e:
        st.error(f"Error analyzing resume: {str(e)}")
    
    return None, None

# Sidebar: New Chat + History + Progress
with st.sidebar:
    st.markdown("### Smart Career Copilot")
    if st.button("New Chat", use_container_width=True):
        reset_for_new_chat()

    st.markdown("### History")
    if not st.session_state.sessions:
        st.caption("No history yet")
    else:
        # Show most recent first
        for idx, sess in enumerate(reversed(st.session_state.sessions)):
            label = sess.get('title') or _make_session_title(sess.get('interview_mode'), sess.get('timestamp', time.time()))
            if st.button(label, key=f"hist_{idx}", use_container_width=True):
                # Convert reversed index back to original
                original_idx = len(st.session_state.sessions) - 1 - idx
                load_session(original_idx)

    st.markdown("### Track Your Progress")
    
    # Performance summary
    if st.session_state.performance_data:
        total_interviews = len(st.session_state.performance_data)
        avg_score = sum(p['score'] for p in st.session_state.performance_data) / total_interviews
        latest_score = st.session_state.performance_data[-1]['score']
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Interviews", total_interviews)
            st.metric("Latest Score", f"{latest_score}/100")
        with col2:
            st.metric("Average Score", f"{avg_score:.1f}/100")
            completion_rate = sum(p['completion_rate'] for p in st.session_state.performance_data) / total_interviews
            st.metric("Avg Completion", f"{completion_rate:.1%}")
        
        # Performance charts
        score_chart, completion_chart, type_chart = create_performance_charts()
        
        if score_chart:
            st.plotly_chart(score_chart, use_container_width=True)
        if completion_chart:
            st.plotly_chart(completion_chart, use_container_width=True)
        if type_chart:
            st.plotly_chart(type_chart, use_container_width=True)
    else:
        st.caption("Complete interviews to see your progress!")

# Section 1: Upload Resume and Job Description
st.markdown('<h2 class="section-header"> Upload Your Resume</h2>', unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("**Drop your files**")
    resume_file = st.file_uploader(" ", type=['pdf', 'docx'], help="Limit 200MB per file • PDF, DOCX")
    
    st.markdown("**Job description**")
    job_description = st.text_area(" ", height=150,
                                   placeholder="Paste the full job description here...")

if resume_file:
    st.session_state.resume_uploaded = True
    st.success(" Resume uploaded successfully!")
    
    # Analyze resume gap if job description is also provided
    if job_description:
        with st.spinner("Analyzing resume and job description..."):
            gap_score, missing_skills = analyze_resume_gap(resume_file, job_description)
            if gap_score is not None:
                st.info(f"**Skill Match Score: {gap_score:.1f}%**")
                if missing_skills:
                    st.warning(f"**Missing Skills:** {', '.join(list(missing_skills)[:5])}")

if job_description:
    st.session_state.jd_provided = True

# Section 2: Interview Configuration
if st.session_state.resume_uploaded and st.session_state.jd_provided:
    with st.container(border=True):
        st.markdown('<h2 class="section-header">  Configure Your Interview</h2>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            interview_type = st.radio(
                "Interview Type",
                ["Technical", "Behavioral", "Mixed"],
                help="Technical: Coding, system design. Behavioral: STAR format, teamwork scenarios."
            )
        
        with col2:
            question_count = st.slider("Number of questions", 3, 10, 5)
            difficulty = st.select_slider("Difficulty level", options=["Easy", "Medium", "Hard"])
        
    # Start interview button
    if st.button("Start AI-Powered Interview", use_container_width=True):
        with st.spinner("Generating personalized interview questions..."):
            # Get resume text for AI question generation
            resume_text = ""
            if resume_file:
                try:
                    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{resume_file.name.split('.')[-1]}") as tmp_file:
                        tmp_file.write(resume_file.getvalue())
                        tmp_file_path = tmp_file.name
                    resume_text = parse_resume(tmp_file_path)
                    os.unlink(tmp_file_path)
                except:
                    resume_text = "Resume parsing failed"
            
            # Generate AI-powered questions
            questions = generate_ai_questions(resume_text, job_description, interview_type, question_count)
        
        st.session_state.interview_started = True
        st.session_state.interview_mode = interview_type
        st.session_state.questions = questions
        st.session_state.current_question = 0
        st.session_state.user_answers = []
        st.rerun()

# Section 3: Interview Simulation
if st.session_state.interview_started:
    with st.container(border=True):
        st.markdown(f'<h2 class="section-header"> {st.session_state.interview_mode} Interview</h2>', unsafe_allow_html=True)
        
        # Progress bar
        progress = (st.session_state.current_question) / len(st.session_state.questions)
        st.progress(progress)
        st.caption(f"Question {st.session_state.current_question + 1} of {len(st.session_state.questions)}")
        
        # Display current question
        if st.session_state.current_question < len(st.session_state.questions):
            current_q = st.session_state.questions[st.session_state.current_question]
            
            st.markdown(f'<div class="bot-message"><b>Interviewer:</b> {current_q}</div>', unsafe_allow_html=True)
            
            # User answer input
            user_answer = st.text_area("Your answer:", height=150, key=f"answer_{st.session_state.current_question}",
                                      placeholder="Type your answer here...")
            
            col1, col2, col3 = st.columns([1, 1, 2])
            
            with col1:
                if st.button("⏭ Skip", use_container_width=True):
                    st.session_state.user_answers.append({"question": current_q, "answer": "", "skipped": True})
                    st.session_state.current_question += 1
                    st.rerun()
            
            with col2:
                if st.button("Retry", use_container_width=True):
                    st.rerun()
            
            with col3:
                if user_answer and st.button("Submit Answer", use_container_width=True):
                    # Get AI evaluation
                    with st.spinner("Evaluating your answer..."):
                        ai_feedback = evaluate_answer_with_ai(current_q, user_answer)
                    
                    st.session_state.user_answers.append({
                        "question": current_q, 
                        "answer": user_answer, 
                        "skipped": False,
                        "ai_feedback": ai_feedback
                    })
                    st.session_state.current_question += 1
                    st.rerun()
        
        # Interview completion
        else:
            st.balloons()
            st.success("Interview completed! Generating your feedback report...")
        
        # Simulate report generation
        with st.spinner("Analyzing your responses..."):
            time.sleep(2)
        
        # Feedback report
        st.markdown('<h2 class="section-header">Your Feedback Report</h2>', unsafe_allow_html=True)
        
        # Overall score
        overall_score = calculate_interview_score(st.session_state.user_answers)
        st.markdown(f'<div class="card"><h3>Overall Score: {overall_score}/100</h3></div>', unsafe_allow_html=True)
        
        # Add performance data to tracking
        add_performance_data(st.session_state.interview_mode, st.session_state.user_answers, st.session_state.questions)
        
        # AI-Generated Feedback
        st.markdown("#### AI-Generated Feedback")
        for i, answer_data in enumerate(st.session_state.user_answers):
            if not answer_data.get('skipped', False) and answer_data.get('ai_feedback'):
                st.markdown(f"**Question {i+1}:** {answer_data['question']}")
                st.markdown(f"**Your Answer:** {answer_data['answer']}")
                st.markdown(f"**AI Feedback:** {answer_data['ai_feedback']}")
                st.markdown("---")
        
        # General Strengths and Improvements
        st.markdown("#### Overall Assessment")
        strengths = [
            "Clear communication style",
            "Good technical knowledge", 
            "Effective use of examples",
            "Structured problem-solving approach"
        ]
        for strength in strengths:
            st.markdown(f"- {strength}")
        
        st.markdown("#### Areas for Improvement")
        improvements = [
            "Provide more specific metrics in your examples",
            "Work on conciseness in technical explanations",
            "Practice more behavioral questions using the STAR method",
            "Include more details about your personal contribution in team projects"
        ]
        for improvement in improvements:
            st.markdown(f"- {improvement}")
        
        # Resources
        st.markdown("#### Recommended Resources")
        resources = [
            "[Tech Interview Handbook](https://www.techinterviewhandbook.org/)",
            "[Behavioral Questions Cheat Sheet](https://www.themuse.com/advice/star-interview-method)",
            "[System Design Primer](https://github.com/donnemartin/system-design-primer)",
            "[LeetCode](https://leetcode.com/) for coding practice"
        ]
        for resource in resources:
            st.markdown(f"- {resource}")
        
        # Download report button
        st.download_button(
            label="Download Full Report (PDF)",
            data="This would be a generated PDF in a real application",
            file_name="interview_feedback_report.pdf",
            mime="application/pdf",
            use_container_width=True
        )
        
        # Restart interview button
        if st.button("Start New Interview", use_container_width=True):
            for key in list(st.session_state.keys()):
                if key != 'resume_uploaded':
                    del st.session_state[key]
            st.session_state.jd_provided = False
            st.rerun()
