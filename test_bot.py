from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.app import app

client=TestClient(app)

def test_root():
    response=client.get("/")
    assert response.status_code==200
    assert response.json()=={"message":"Interview Bot is running!"}

def test_faq_question():
    question = "What is Python?"
    response = client.post("/ask", json={"question": question})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] == "Python is a high-level programming language known for simplicity."
 
@patch("backend.app.client.chat.completions.create")
def test_non_faq_question(mock_groq):
    mock_groq.return_value.choices = [type("Obj", (), {"message": type("Msg", (), {"content": "Mocked AI answer"})()})()]

    question = "Explain Generative AI."
    response = client.post("/ask", json={"question": question})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert data["answer"] == "Mocked AI answer"

print("All tests passed successfully!")
