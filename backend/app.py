from fastapi import FastAPI
from dotenv import load_dotenv
from pydantic import BaseModel
from pathlib import Path
import os 
from groq import Groq
 
load_dotenv()

from backend.utils import load_faqs,find_answer

app=FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(dotenv_path=BASE_DIR / ".env")


client=Groq(api_key=os.getenv("GROQ_API_KEY"))

FAQS=load_faqs(BASE_DIR/"data"/"faqs.json")

class QuestionRequest(BaseModel):
    question: str
    
@app.get("/")
def root():
    return {"message":"Interview Bot is running!"}

@app.post("/ask")
def ask_question(request: QuestionRequest):
    faq_answer=find_answer(request.question,FAQS)
    if faq_answer:
        return{"answer":faq_answer,"source":"faqs.json"}
    
    response=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"user","content": request.question}],
    )
    return{"answer": response.choices[0].message.content}
    