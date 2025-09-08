#!/usr/bin/env python3
"""
Startup script for the Interview Prep Bot application
"""
import subprocess
import sys
import os
import time
import threading
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server in a separate thread"""
    backend_dir = Path(__file__).parent / "backend"
    os.chdir(backend_dir)
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except Exception as e:
        print(f"Backend error: {e}")

def start_frontend():
    """Start the Streamlit frontend"""
    print("🎯 Starting Interview Prep Bot Frontend...")
    time.sleep(3)  # Wait for backend to start
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", 
            "run", "career.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], check=True)
    except Exception as e:
        print(f"Frontend error: {e}")

def main():
    """Start both backend and frontend"""
    print("🚀 Starting Interview Prep Bot...")
    print("📋 Make sure you have:")
    print("   1. Created a .env file with your GROQ_API_KEY")
    print("   2. Installed requirements: pip install -r requirements.txt")
    print("   3. Backend will run on: http://localhost:8000")
    print("   4. Frontend will run on: http://localhost:8501")
    print()
    
    # Start backend in a separate thread
    backend_thread = threading.Thread(target=start_backend, daemon=True)
    backend_thread.start()
    
    # Start frontend in main thread
    start_frontend()

if __name__ == "__main__":
    main()
