from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

# Initialize app
app = App(token=SLACK_BOT_TOKEN)

# Get bot identity (AFTER app is created)
BOT_ID = app.client.auth_test()["user_id"]
BOT_NAME = app.client.users_info(user=BOT_ID)["user"]["real_name"]


def log_message(prefix, message_text):
    log_path = os.path.join(os.path.dirname(__file__), "user_input_log.txt")
    with open(log_path, "a") as log_file:
        log_file.write(f"{prefix}: {message_text}\n")

def get_user_name(user_id):
    try:
        response = app.client.users_info(user=user_id)
        if response["ok"]:
            return response["user"]["real_name"]
        else:
            print(f"[ERROR] Failed to get user info for {user_id}: {response['error']}")
            return user_id
    except Exception as e:
        print(f"[EXCEPTION] Failed to fetch user name for {user_id}: {str(e)}")
        return user_id

@app.event("app_mention")
def handle_mention(event, say):
    user_id = event["user"]
    text = event["text"]
    user_name = get_user_name(user_id)

    cleaned_text = text
    for token in cleaned_text.split():
        if token.startswith("<@") and token.endswith(">"):
            cleaned_text = cleaned_text.replace(token, "").strip()

    log_message(user_name, cleaned_text)

    reply = f"Hi {user_name}! Ready to plan your meals for the week? Just reply with your preferences!"
    say(reply)
    log_message(BOT_NAME, reply)

@app.message("")
def handle_message(message, say):
    user_id = message["user"]
    text = message["text"]
    user_name = get_user_name(user_id)

    log_message(user_name, text)

    reply = "Got it! I’ve noted that. I’ll take this into account for your meal plan."
    say(reply)
    log_message(BOT_NAME, reply)

if __name__ == "__main__":
    print("⚡️ Slack Meal Planner Bot is running!")
    SocketModeHandler(app, SLACK_APP_TOKEN).start()
