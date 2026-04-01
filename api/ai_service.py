import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

RAPIDAPI_KEY = os.getenv('RAPIDAPI_KEY')
COPILOT_HOST = os.getenv('RAPIDAPI_HOST_COPILOT')
GEMNAI_API_KEY = os.getenv('GEMNAI_API_KEY')


def call_gemini(message):
    if not GEMNAI_API_KEY:
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta2/models/text-bison-001:generateText?key={GEMNAI_API_KEY}"
    payload = {
        'prompt': {
            'text': message,
        }
    }
    headers = {
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            candidates = data.get('candidates')
            if candidates and len(candidates) > 0:
                return candidates[0].get('output')
        return None
    except Exception:
        return None


def call_copilot(message):
    if not RAPIDAPI_KEY or not COPILOT_HOST:
        return None

    url = f"https://{COPILOT_HOST}/copilot"
    payload = {
        'message': message,
        'conversation_id': None,
        'mode': 'CHAT',
        'markdown': False,
    }
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': COPILOT_HOST,
        'Content-Type': 'application/json',
    }

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        if response.status_code == 200:
            return response.json().get('message', '')
        return None
    except Exception:
        return None


def call_ai(message):
    gemini_response = call_gemini(message)
    if gemini_response is not None:
        return gemini_response
    return call_copilot(message)


def generate_interview_questions(domain, difficulty, count=5):
    prompt = f"""
Generate {count} interview questions for a {domain} role at {difficulty}.
Return valid JSON only as a list of objects:
[
  {
    "text": "The question content",
    "question_type": "mcq" or "text" or "code",
    "options": ["A", "B", "C", "D"],
    "correct_answer": "The correct answer",
    "explanation": "Why this is correct"
  }
]
If the question_type is "mcq", include "options". Otherwise set "options" to null.
Do not include any other text outside the JSON.
"""
    response_text = call_copilot(prompt)
    try:
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        if start != -1 and end != -1:
            json_str = response_text[start:end]
            return json.loads(json_str)
        return []
    except Exception:
        return []


def evaluate_interview_answer(question_text, correct_answer, user_answer):
    prompt = f"""
Question: {question_text}
Correct Answer: {correct_answer}
User Answer: {user_answer}

Compare the user's answer to the correct answer and return valid JSON only:
{{
  "is_correct": true or false,
  "score": integer from 0 to 100,
  "ai_feedback": "Short feedback on whether the answer is correct and how to improve."
}}
Do not include any other text.
"""
    response_text = call_copilot(prompt)
    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = response_text[start:end]
            return json.loads(json_str)
        return {'is_correct': False, 'score': 0, 'ai_feedback': 'Could not evaluate.'}
    except Exception:
        return {'is_correct': False, 'score': 0, 'ai_feedback': 'Evaluation failed.'}
