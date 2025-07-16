import os
import re
import json
from dotenv import load_dotenv
from datetime import datetime
from openai import OpenAI
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from apscheduler.schedulers.background import BackgroundScheduler
from gpt_planner import generate_meal_plan

# ─── Setup ────────────────────────────────────────────────────────────────────
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")
OPENAI_API_KEY  = os.getenv("OPENAI_API_KEY")
USER_ID         = os.getenv("USER_ID")

# scheduling params
DAY_OF_WEEK = os.getenv("SCHEDULE_DAY_OF_WEEK", "1")  # Monday default
HOUR        = os.getenv("SCHEDULE_HOUR", "8")
MINUTE      = os.getenv("SCHEDULE_MINUTE", "0")

# init clients
app    = App(token=SLACK_BOT_TOKEN)
client = OpenAI(api_key=OPENAI_API_KEY)

# identify bot
BOT_ID   = app.client.auth_test()["user_id"]
bot_info = app.client.users_info(user=BOT_ID)["user"]["profile"]
BOT_NAME = bot_info.get("real_name") or bot_info.get("display_name") or BOT_ID

# ─── Helpers ──────────────────────────────────────────────────────────────────
def log_message(prefix, message_text):
    ts = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z%z")
    log_path = os.path.join(os.path.dirname(__file__), "user_input_log.txt")
    with open(log_path, "a") as f:
        f.write(f"[{ts}] {prefix}: {message_text}\n")

def get_user_name(user_id):
    resp = app.client.users_info(user=user_id)
    profile = resp["user"]["profile"]
    return profile.get("real_name") or profile.get("display_name") or user_id

def extract_count(text: str, default: int = 5) -> int:
    # look for digits
    m = re.search(r"\b(\d+)\b", text)
    if m:
        return int(m.group(1))
    # optionally, look for spelled‑out numbers (one, two, three…)
    words_to_nums = {
        "one": 1, "two": 2, "three": 3, "four": 4,
        "five": 5, "six": 6, "seven": 7, "eight": 8,
        "nine": 9, "ten": 10
    }
    for word, num in words_to_nums.items():
        if re.search(rf"\b{word}\b", text, re.IGNORECASE):
            return num
    return default

# def generate_meal_plan(prefs: str) -> str:
#     prompt = (
#         f"You are a meal‑planning assistant.\n"
#         f"Preferences: {prefs}\n\n"
#         "Give me a 5‑day plan in this format:\n"
#         "Monday: [Name] - [desc] (Time: XX mins)\n…"
#     )
#     resp = client.chat.completions.create(
#         model="gpt-4",
#         messages=[
#             {"role": "system",  "content": "You help users plan meals."},
#             {"role": "user",    "content": prompt}
#         ],
#         temperature=0.7,
#         max_tokens=500
#     )
#     return resp.choices[0].message.content

# ─── 1) Scheduled Weekly DM ──────────────────────────────────────────────────
def send_weekly_prompt():
    # open or reuse a DM
    conv = app.client.conversations_open(users=USER_ID)
    channel = conv["channel"]["id"]
    text = "👋 Ready to plan your meals this week? Just reply here with your preferences!"
    app.client.chat_postMessage(channel=channel, text=text)
    log_message(BOT_NAME, f"Sent weekly kickoff to {USER_ID}")

scheduler = BackgroundScheduler()
scheduler.add_job(
    send_weekly_prompt,
    "cron",
    day_of_week=DAY_OF_WEEK,
    hour=int(HOUR),
    minute=int(MINUTE)
)
scheduler.start()

# ─── 2) DM Handler ───────────────────────────────────────────────────────────
@app.event("message")
def handle_dm(event, say):
    # only DMs (no channel) – ensures channel-level mentions don't hit this
    if event.get("channel_type") != "im":
        return

    user_id = event["user"]
    text    = event["text"].strip()
    user_nm = get_user_name(user_id)
    count   = extract_count(text, default=5)

    log_message(user_nm, text)
    plan = generate_meal_plan(text, count=count)
        # 1) Parse JSON
    try:
        meals = json.loads(plan)
    except json.JSONDecodeError as e:
        log_message(BOT_NAME, f"[JSON parse error] {e}")
        say(f"❗️ I couldn’t parse the plan properly—here’s the output:\n```{plan}```")
        return

    # 2) Format nicely
    formatted = "\n".join(
        f"- *{item['name']}* ({item['time_minutes']} min): {item['description']}"
        for item in meals
    )

    # 3) Send that instead of raw JSON
    say(f"🍽️ *Here’s your {count}-item meal plan:*\n{formatted}")
    log_message(BOT_NAME, formatted)

# ─── 3) Slash Command ────────────────────────────────────────────────────────
@app.command("/mealplan")
def handle_slash(ack, body, say):
    ack()
    user_id = body["user_id"]
    text    = body.get("text", "").strip() or "I want quick meals this week"
    user_nm = get_user_name(user_id)
    count   = extract_count(text, default=5)

    log_message(user_nm, text)
    plan = generate_meal_plan(text, count=count)
        # 1) Parse JSON
    try:
        meals = json.loads(plan)
    except json.JSONDecodeError as e:
        log_message(BOT_NAME, f"[JSON parse error] {e}")
        say(f"❗️ I couldn’t parse the plan properly—here’s the output:\n```{plan}```")
        return

    # 2) Format nicely
    formatted = "\n".join(
        f"- *{item['name']}* ({item['time_minutes']} min): {item['description']}"
        for item in meals
    )

    # 3) Send that instead of raw JSON
    say(f"🍽️ *Here’s your {count}-item meal plan:*\n{formatted}")
    log_message(BOT_NAME, formatted)

# ─── (Optional) In‑Channel App Mention ───────────────────────────────────────
@app.event("app_mention")
def handle_mention(event, say):
    raw = event["text"]
    prefs = " ".join(tok for tok in raw.split() if not tok.startswith("<@"))
    user_id = event["user"]
    user_nm = get_user_name(user_id)
    count   = extract_count(prefs, default=5)

    log_message(user_nm, prefs)
    plan = generate_meal_plan(prefs, count=count)
        # 1) Parse JSON
    try:
        meals = json.loads(plan)
    except json.JSONDecodeError as e:
        log_message(BOT_NAME, f"[JSON parse error] {e}")
        say(f"❗️ I couldn’t parse the plan properly—here’s the output:\n```{plan}```")
        return

    # 2) Format nicely
    formatted = "\n".join(
        f"- *{item['name']}* ({item['time_minutes']} min): {item['description']}"
        for item in meals
    )

    # 3) Send that instead of raw JSON
    say(f"🍽️ *Here’s your {count}-item meal plan:*\n{formatted}")
    log_message(BOT_NAME, formatted)

# ─── Entry Point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"⚡️ {BOT_NAME} is running!")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
