import os
import datetime
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("GOOGLE_CREDS_JSON", scope)
client = gspread.authorize(creds)
sheet = client.open("Aries Daily Updates").sheet1

bot = Bot(token=BOT_TOKEN)

def is_weekday():
    return datetime.datetime.today().weekday() < 5

async def send_daily_ping():
    if not is_weekday():
        return

    users = sheet.col_values(3)[1:]  # usernames
    for u in users:
        try:
            await bot.send_message(chat_id=u, text="Hey 👋\nWhat did you work on today at NoCapCode?")
        except:
            pass

async def handle_reply(update: Update, context):
    user = update.message.from_user
    msg = update.message.text
    now = datetime.datetime.now()

    sheet.append_row([
        now.strftime("%Y-%m-%d"),
        user.first_name,
        user.username,
        msg,
        now.strftime("%H:%M")
    ])

    formatted = f"""
🟢 Daily Update
👤 {user.first_name}
📝 {msg}
⏰ {now.strftime('%H:%M')}
"""

    await bot.send_message(chat_id=GROUP_ID, text=formatted)

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply))
app.run_polling()
