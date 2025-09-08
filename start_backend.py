#!/usr/bin/env python3
"""
Startup script for the Interview Prep Bot backend
"""
import subprocess
import sys
import os
from pathlib import Path

def start_backend():
    """Start the FastAPI backend server"""
    backend_dir = Path(__file__).parent / "backend"
    
    print("🚀 Starting Interview Prep Bot Backend...")
    print("📍 Backend directory:", backend_dir)
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Start FastAPI server
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting backend: {e}")
        print("Make sure you have installed all requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    start_backend()
