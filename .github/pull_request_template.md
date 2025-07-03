# 🚀 Pull Request: Slack Bot Setup

## ✅ Summary

This PR adds a working Slack bot to the project. It handles:

- Listening for `@mentions` and direct messages
- Resolving and logging user real names
- Responding with confirmation
- Logging bot replies for future reference

---

## 📦 What's Changed

- Created `slack_bot/bot.py`
- Added `log_message()` with user name resolution
- Introduced `user_input_log.txt` for conversational logging
- Added `.env` setup support for Slack tokens

---

## 🧪 Testing Steps

1. Run the bot locally with `python bot.py`
2. Mention the bot in Slack or send a DM
3. Confirm:
   - You get a response in Slack
   - `user_input_log.txt` is updated with real names
   - No exceptions in terminal

---

## 🔒 Notes

- Ensure `.env` includes `SLACK_BOT_TOKEN` and `SLACK_APP_TOKEN`
- `.env` and `venv/` are excluded from Git
- You must invite the bot to a Slack channel or DM it manually before testing

---

## 🔮 Next Up

- Feature: GPT meal planning
- Feature: Pantry tracking (barcode + manual entry)
