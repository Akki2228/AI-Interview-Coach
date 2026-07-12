import os
import random
import re
from dotenv import load_dotenv
from google import genai
from questions import QUESTIONS

# Load environment variables from the .env file
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise Exception("GEMINI_API_KEY not found. Please check your .env file.")

# Initialize the modern GenAI Client
client = genai.Client(api_key=API_KEY)


def get_ai_question(role, company="Standard Company", difficulty="Medium", resume_text=None):
    prompt = f"""
You are a senior interviewer at {company}.

Generate ONE {difficulty} level interview question for a {role}.

Return only the question.
"""

    if resume_text:
        prompt += "\nCandidate Resume:\n"
        prompt += resume_text

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"


def get_hybrid_question(role, company="Standard Company", difficulty="Medium", resume_text=None):
    role_lower = role.lower()

    if resume_text:
        return get_ai_question(role, company, difficulty, resume_text)

    for key in QUESTIONS:
        if key in role_lower:
            return random.choice(QUESTIONS[key])

    return get_ai_question(role, company, difficulty)


def evaluate_answer(question, answer):
    prompt = f"""
You are evaluating an interview.

Question:
{question}

Candidate Answer:
{answer}

Return exactly this format.

SCORE:
(number from 0-10)

FEEDBACK:
(text)

IMPROVEMENT:
(text)
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text

        score_match = re.search(r"SCORE:\s*(\d+(\.\d+)?)", text)
        score = float(score_match.group(1)) if score_match else 7.0

        return {
            "raw_text": text,
            "score": score
        }
    except Exception as e:
        return {
            "raw_text": str(e),
            "score": 0.0
        }