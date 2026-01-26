import os
import json
import datetime
from telegram.ext import Application, MessageHandler, filters
import gspread
from oauth2client.service_account import ServiceAccountCredentials

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")

# Google auth
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(GOOGLE_CREDS_JSON), scope
)
client = gspread.authorize(creds)

updates_sheet = client.open("Aries Daily Updates").worksheet("Updates")

async def handle_reply(update, context):
    user = update.message.from_user
    msg = update.message.text
    now = datetime.datetime.now()

    # Save to sheet
    updates_sheet.append_row([
        now.strftime("%Y-%m-%d"),
        user.first_name,
        user.username,
        msg,
        now.strftime("%H:%M")
    ])

    # Send to founders group
    await context.bot.send_message(
        chat_id=GROUP_ID,
        text=f"""🟢 Daily Update
👤 {user.first_name}
📝 {msg}
⏰ {now.strftime('%H:%M')}"""
    )

    # Acknowledge employee
    await update.message.reply_text(
        "Thanks! Your update is noted 👍"
    )

app = Application.builder().token(BOT_TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_reply))
app.run_polling()
