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
            result = response.json()
            return result.get('message') or response.text
        return None
    except Exception:
        return None


def call_ai(message):
    gemini_response = call_gemini(message)
    if gemini_response is not None:
        return gemini_response
    return call_copilot(message)


SAMPLE_QUESTION_TEMPLATES = {
    'Full Stack': [
        {
            'text': 'Explain the role of a REST API in a Full Stack web application.',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'A REST API allows the frontend and backend to exchange information over HTTP using standard methods.',
            'explanation': 'REST APIs provide a consistent interface for client-server communication.'
        },
        {
            'text': 'Which HTTP status code means the request was successful?',
            'question_type': 'mcq',
            'options': ['200', '201', '400', '500'],
            'correct_answer': '200',
            'explanation': '200 indicates a successful GET or POST response from the server.'
        },
        {
            'text': 'What is the difference between client-side and server-side rendering?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'Client-side rendering runs in the browser, while server-side rendering builds HTML on the server before sending it to the client.',
            'explanation': 'This explains how UI rendering differs between frontend and backend execution.'
        },
        {
            'text': 'Which database operation does CRUD stand for?',
            'question_type': 'mcq',
            'options': ['Create, Read, Update, Delete', 'Copy, Run, Undo, Delete', 'Connect, Request, Upload, Download', 'Compile, Run, Update, Deploy'],
            'correct_answer': 'Create, Read, Update, Delete',
            'explanation': 'CRUD are the four basic operations performed on persistent storage.'
        },
        {
            'text': 'Name one common security concern for Full Stack applications.',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'Cross-site scripting (XSS) or SQL injection or insecure authentication.',
            'explanation': 'Security issues must be considered on both frontend and backend.'
        },
    ],
    'Data Science': [
        {
            'text': 'Describe the difference between supervised and unsupervised learning.',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'Supervised learning uses labeled data, while unsupervised learning finds patterns without labels.',
            'explanation': 'This distinguishes the two primary machine learning training approaches.'
        },
        {
            'text': 'Which metric is best for evaluating classification accuracy?',
            'question_type': 'mcq',
            'options': ['Mean Squared Error', 'Accuracy', 'RMSE', 'Silhouette Score'],
            'correct_answer': 'Accuracy',
            'explanation': 'Accuracy measures the proportion of correctly classified examples.'
        },
        {
            'text': 'What is feature engineering in Data Science?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'Creating or transforming variables to improve model performance.',
            'explanation': 'Good features help models learn more effectively.'
        },
        {
            'text': 'Which chart is commonly used to show the relationship between two variables?',
            'question_type': 'mcq',
            'options': ['Bar chart', 'Scatter plot', 'Pie chart', 'Histogram'],
            'correct_answer': 'Scatter plot',
            'explanation': 'Scatter plots are ideal for visualizing variable relationships.'
        },
        {
            'text': 'Why is data cleaning important before modeling?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'It removes errors, handles missing values, and ensures data quality so the model can learn correctly.',
            'explanation': 'Clean data leads to more reliable models.'
        },
    ],
    'AI/ML': [
        {
            'text': 'What is the difference between classification and regression?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'Classification predicts categories, regression predicts continuous values.',
            'explanation': 'This is the basic distinction between two supervised learning tasks.'
        },
        {
            'text': 'Which algorithm is best for image recognition?',
            'question_type': 'mcq',
            'options': ['Linear Regression', 'Decision Tree', 'Convolutional Neural Network', 'K-means'],
            'correct_answer': 'Convolutional Neural Network',
            'explanation': 'CNNs are the standard for image-based tasks.'
        },
        {
            'text': 'What does overfitting mean in machine learning?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'The model learns noise from the training data and performs poorly on new data.',
            'explanation': 'Overfitting reduces generalization performance.'
        },
        {
            'text': 'Which metric is used to measure binary classification performance?',
            'question_type': 'mcq',
            'options': ['R-squared', 'Accuracy', 'MSE', 'Euclidean Distance'],
            'correct_answer': 'Accuracy',
            'explanation': 'Accuracy is a simple measure for binary classification.'
        },
        {
            'text': 'What is a neural network activation function?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'A function that introduces non-linearity into a neural network layer.',
            'explanation': 'Activation functions allow networks to learn complex patterns.'
        },
    ],
    'Cybersecurity': [
        {
            'text': 'What is SQL injection and how can it be prevented?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'SQL injection is when attackers insert SQL into input fields; it is prevented with parameterized queries and input validation.',
            'explanation': 'Parameterized queries prevent malicious SQL execution.'
        },
        {
            'text': 'What does HTTPS protect in a web application?',
            'question_type': 'mcq',
            'options': ['Code quality', 'Data in transit', 'Database schema', 'Browser performance'],
            'correct_answer': 'Data in transit',
            'explanation': 'HTTPS encrypts traffic between client and server.'
        },
        {
            'text': 'Why is multi-factor authentication important?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'It adds an extra layer of security beyond passwords.',
            'explanation': 'MFA reduces the risk of account takeover.'
        },
        {
            'text': 'Which control helps protect against brute-force attacks?',
            'question_type': 'mcq',
            'options': ['Strong password policy', 'Unlimited login attempts', 'Plaintext storage', 'No encryption'],
            'correct_answer': 'Strong password policy',
            'explanation': 'Strong passwords and account lockouts reduce brute-force risk.'
        },
        {
            'text': 'What is the purpose of a firewall?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'A firewall filters network traffic to block unauthorized access.',
            'explanation': 'Firewalls enforce network security policies.'
        },
    ],
    'Product Management': [
        {
            'text': 'What is a product roadmap?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'A product roadmap is a plan that outlines product goals and delivery timelines.',
            'explanation': 'Roadmaps guide feature development and stakeholder alignment.'
        },
        {
            'text': 'Which activity helps understand user needs?',
            'question_type': 'mcq',
            'options': ['Coding', 'User interviews', 'Market spec creation', 'Bug fixing'],
            'correct_answer': 'User interviews',
            'explanation': 'User interviews reveal real customer problems.'
        },
        {
            'text': 'What is MVP in product development?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'Minimum Viable Product: the smallest version of a product that delivers value.',
            'explanation': 'MVP enables fast validation with users.'
        },
        {
            'text': 'Which metric measures product engagement?',
            'question_type': 'mcq',
            'options': ['Bounce Rate', 'Conversion Rate', 'Daily Active Users', 'CPU Usage'],
            'correct_answer': 'Daily Active Users',
            'explanation': 'DAU is a common engagement metric for products.'
        },
        {
            'text': 'Why is prioritization important in product management?',
            'question_type': 'text',
            'options': None,
            'correct_answer': 'Prioritization ensures the team builds the highest-value features first.',
            'explanation': 'It keeps the roadmap focused on customer impact.'
        },
    ],
}


def sample_interview_questions(domain, difficulty, count=5):
    template_list = SAMPLE_QUESTION_TEMPLATES.get(domain, SAMPLE_QUESTION_TEMPLATES['Full Stack'])
    questions = []
    for idx in range(count):
        template = template_list[idx % len(template_list)]
        questions.append({
            'text': template['text'],
            'question_type': template['question_type'],
            'options': template['options'],
            'correct_answer': template['correct_answer'],
            'explanation': template['explanation'],
        })
    return questions


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
    response_text = call_ai(prompt)
    if not response_text:
        return sample_interview_questions(domain, difficulty, count)

    try:
        start = response_text.find('[')
        end = response_text.rfind(']') + 1
        if start != -1 and end != -1:
            json_str = response_text[start:end]
            parsed = json.loads(json_str)
            if isinstance(parsed, list) and parsed:
                return parsed
    except Exception:
        pass

    return sample_interview_questions(domain, difficulty, count)


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
    response_text = call_ai(prompt)
    if not response_text:
        is_correct = correct_answer.strip().lower() in user_answer.strip().lower()
        score = 100 if is_correct else min(50, max(0, len(user_answer.strip()) * 2))
        return {
            'is_correct': is_correct,
            'score': score,
            'ai_feedback': 'Unable to evaluate with AI service. Your answer has been recorded.'
        }

    try:
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = response_text[start:end]
            return json.loads(json_str)
        return {'is_correct': False, 'score': 0, 'ai_feedback': 'Could not evaluate.'}
    except Exception:
        return {'is_correct': False, 'score': 0, 'ai_feedback': 'Evaluation failed.'}
