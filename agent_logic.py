import os
import openai
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_reply(user_input: str) -> str:
    system_prompt = (
        "You are Miss Riverwood, a warm, friendly AI voice agent for Riverwood Projects LLP. "
        "Greet users casually in Hindi-English mix, ask about chai, and respond with empathy. "
        "Keep it short, natural, and locally relatable."
    )

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.7
    )

    return response.choices[0].message["content"]

