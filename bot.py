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

sheet = client.open("Aries Daily Updates").sheet1

# ========================
# TELEGRAM BOT
# ========================
bot = Bot(token=BOT_TOKEN)

def is_weekday():
    return datetime.datetime.today().weekday() < 5

# ========================
# HANDLE REPLY
# ========================
async def handle_reply(update: Update, context):
    user = update.message.from_user
    msg = update.message.text
    now = datetime.datetime.now()

    # Save to Google Sheet
    sheet.append_row([
        now.strftime("%Y-%m-%d"),
        user.first_name,
        user.username,
        msg,
        now.strftime("%H:%M")
    ])

    # Forward to founders group
    formatted = f"""
🟢 Daily Update
👤 {user.first_name}
📝 {msg}
⏰ {now.strftime('%H:%M')}
"""
    await bot.send_message(chat_id=GROUP_ID, text=formatted)

# ========================
# RUN BOT
# ========================
app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply))
app.run_polling()
