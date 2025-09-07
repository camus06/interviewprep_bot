# Smart Career Copilot - AI Interview Preparation Bot

An intelligent interview preparation system that combines AI-powered question generation, resume analysis, and real-time feedback to help you ace your interviews.

## Features

### 🤖 AI-Powered Interview Questions
- Generate personalized questions based on your resume and job description
- Support for Technical, Behavioral, and Mixed interview types
- Questions tailored to specific roles and requirements

### 📄 Resume Analysis
- Parse PDF and DOCX resumes
- Skill gap analysis comparing resume to job requirements
- Missing skills identification and recommendations

### 💬 Real-time AI Feedback
- Instant evaluation of your answers using AI
- Detailed feedback on strengths and areas for improvement
- Score tracking and performance analytics

### 📊 Progress Tracking
- Visual charts showing interview performance over time
- Completion rates and score trends
- Interview type distribution analytics

### 🗂️ Session Management
- Save and resume interview sessions
- History of all completed interviews
- New chat functionality for fresh starts

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory:
```env
GROQ_API_KEY=your_groq_api_key_here
BACKEND_URL=http://localhost:8000
```

Get your Groq API key from: https://console.groq.com/

### 3. Start the Application

#### Option A: Start Everything at Once
```bash
python start_app.py
```

#### Option B: Start Backend and Frontend Separately

**Terminal 1 - Backend:**
```bash
python start_backend.py
```

**Terminal 2 - Frontend:**
```bash
streamlit run career.py
```

### 4. Access the Application
- **Frontend**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## How to Use

1. **Upload Resume**: Upload your resume (PDF or DOCX format)
2. **Add Job Description**: Paste the job description you're applying for
3. **Configure Interview**: Choose interview type and number of questions
4. **Start Interview**: Click "Start AI-Powered Interview" to begin
5. **Answer Questions**: Respond to AI-generated questions
6. **Get Feedback**: Receive instant AI evaluation of your answers
7. **Track Progress**: View your performance analytics in the sidebar

## Architecture

### Frontend (Streamlit)
- `career.py`: Main application interface
- Interactive UI with sidebar navigation
- Real-time progress tracking and charts

### Backend (FastAPI)
- `backend/app.py`: API endpoints and server configuration
- `backend/utils.py`: Utility functions for resume parsing and AI integration
- RESTful API for AI question generation and evaluation

### Data
- `data/faqs.json`: FAQ database for common questions
- `data/skills.json`: Skills database for gap analysis

## API Endpoints

- `GET /`: Health check
- `POST /ask`: AI question generation and evaluation

## Technologies Used

- **Frontend**: Streamlit, Plotly
- **Backend**: FastAPI, Uvicorn
- **AI**: Groq API (Llama 3.1)
- **Data Processing**: Pandas, PyPDF2, python-docx
- **Analysis**: RapidFuzz for skill matching

## Troubleshooting

### Backend Not Running
- Ensure all dependencies are installed
- Check if port 8000 is available
- Verify your GROQ_API_KEY is set correctly

### Resume Parsing Issues
- Ensure resume is in PDF or DOCX format
- Check file size (should be under 200MB)
- Verify file is not corrupted

### AI Features Not Working
- Verify GROQ_API_KEY is valid and has credits
- Check internet connection
- Ensure backend is running and accessible

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.