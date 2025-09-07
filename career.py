import streamlit as st
import base64
from io import BytesIO
from PIL import Image
import time

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
        border-left: 4px solid #a777e3;
        padding-left: 0.75rem;
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
        border: #6e8efb;
        border-radius: 10px;
        padding: 1.5rem;
        background-color: #f8f9ff;
    }
    
    /* Chat messages */
    .user-message {
        background-color: #252529;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid #6e8efb;
    }
    
    .bot-message {
        background-color: #252529;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        border-left: 4px solid #a777e3;
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

# Section 1: Upload Resume and Job Description
st.markdown('<h2 class="section-header"> Upload Your Materials</h2>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    resume_file = st.file_uploader(" Upload your resume", type=['pdf', 'docx', 'txt'], 
                                  help="Supported formats: PDF, DOCX, TXT")

with col2:
    job_description = st.text_area(" Paste the job description", height=150,
                                  placeholder="Paste the full job description here...")

if resume_file:
    st.session_state.resume_uploaded = True
    st.success(" Resume uploaded successfully!")

if job_description:
    st.session_state.jd_provided = True

# Section 2: Interview Configuration
if st.session_state.resume_uploaded and st.session_state.jd_provided:
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
    
    # Mock interview questions based on type
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
    
    # Start interview button
    if st.button("Start Mock Interview", use_container_width=True):
        st.session_state.interview_started = True
        st.session_state.interview_mode = interview_type
        st.session_state.questions = questions[:question_count]
        st.session_state.current_question = 0
        st.session_state.user_answers = []
        st.rerun()

# Section 3: Interview Simulation
if st.session_state.interview_started:
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
                st.session_state.user_answers.append({
                    "question": current_q, 
                    "answer": user_answer, 
                    "skipped": False
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
        overall_score = 78  # This would be calculated based on answers
        st.markdown(f'<div class="card"><h3>Overall Score: {overall_score}/100</h3></div>', unsafe_allow_html=True)
        
        # Strengths
        st.markdown("#### Strengths")
        strengths = [
            "Clear communication style",
            "Good technical knowledge",
            "Effective use of examples",
            "Structured problem-solving approach"
        ]
        for strength in strengths:
            st.markdown(f"- {strength}")
        
        # Areas for improvement
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
