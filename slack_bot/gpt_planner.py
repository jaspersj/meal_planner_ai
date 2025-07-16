# slack_bot/gpt_planner.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_meal_plan(user_preferences: str, count: int = 5) -> str:
    """
    Return a 5-day meal plan (or `count` items) in strict JSON format.
    """
    prompt = (
        f"You are a precise meal‑planning assistant.\n"
        f"Based on these preferences, produce exactly {count} meals:\n\n"
        f"Preferences: {user_preferences}\n\n"
        "Return as a JSON array of objects, each with:\n"
        "- name (string)\n"
        "- description (string)\n"
        "- time_minutes (integer)\n\n"
        "Example output:\n"
        "[\n"
        "  {\"name\":\"Sheet‑Pan Salmon\",\"description\":\"Roast salmon and veggies\",\"time_minutes\":25},\n"
        "  …\n"
        "]"
    )

    resp = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role":"system", "content":"You output valid JSON only."},
            {"role":"user",   "content":prompt}
        ],
        temperature=0.2,
        max_tokens=500
    )
    return resp.choices[0].message.content

