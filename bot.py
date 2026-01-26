import os
import json
import datetime
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ========================
# ENV VARIABLES
# ========================
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")

# ========================
# GOOGLE SHEETS SETUP
# ========================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(GOOGLE_CREDS_JSON)
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

spreadsheet = client.open("Aries Daily Updates")
employees_sheet = spreadsheet.worksheet("Employees")
updates_sheet = spreadsheet.worksheet("Updates")

# ========================
# TELEGRAM BOT
# ========================
bot = Bot(token=BOT_TOKEN)

def is_weekday():
    return datetime.datetime.today().weekday() < 5

# ========================
# DAILY PING (CALLED BY SCHEDULE)
# ========================
async def send_daily_ping():
    if not is_weekday():
        return

    employees = employees_sheet.get_all_records()

    for emp in employees:
        if emp["Active"].strip().upper() != "YES":
            continue

        message = f"""Hey {emp['FirstName']} 👋
Hope you had a productive day.

Quick check-in — what did you work on today at NoCapCode?
Just reply to this message (1–2 lines is perfect)."""

        try:
            await bot.send_message(chat_id=emp["TelegramID"], text=message)
        except Exception as e:
            print(f"Failed to message {emp['FirstName']}: {e}")

# ========================
# HANDLE EMPLOYEE REPLY
# ========================
async def handle_reply(update: Update, context):
    user = update.message.from_user
    msg = update.message.text
    now = datetime.datetime.now()

    # Save update
    updates_sheet.append_row([
        now.strftime("%Y-%m-%d"),
        user.first_name,
        user.username,
        msg,
        now.strftime("%H:%M")
    ])

    # Forward to founders group
    formatted = f"""🟢 Daily Update
👤 {user.first_name}
📝 {msg}
⏰ {now.strftime('%H:%M')}"""

    await bot.send_message(chat_id=GROUP_ID, text=formatted)

    # Polite acknowledgement
    await update.message.reply_text("Thanks for the update! Noted 👍")

# ========================
# RUN BOT
# ========================
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply))

# ⚠️ IMPORTANT:
# When run by GitHub Action at 8 PM, this line will send pings
import asyncio
asyncio.run(send_daily_ping())

app.run_polling()
