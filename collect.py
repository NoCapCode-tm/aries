import os, json, datetime
from telegram import Bot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")

bot = Bot(BOT_TOKEN)

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(GOOGLE_CREDS_JSON), scope
)
client = gspread.authorize(creds)

spreadsheet = client.open("Aries Daily Updates")
updates_sheet = spreadsheet.worksheet("Updates")
meta_sheet = spreadsheet.worksheet("Meta")

# Read last update offset
last_update_id = int(meta_sheet.cell(2, 2).value)

updates = bot.get_updates(offset=last_update_id, timeout=10)

for u in updates:
    if not u.message or not u.message.text:
        continue

    user = u.message.from_user
    msg = u.message.text
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
    bot.send_message(
        chat_id=GROUP_ID,
        text=f"""🟢 Daily Update
👤 {user.first_name}
📝 {msg}
⏰ {now.strftime('%H:%M')}"""
    )

    # Acknowledge employee
    bot.send_message(
        chat_id=user.id,
        text="Thanks! Your update is noted 👍"
    )

    last_update_id = u.update_id + 1

# Save offset
meta_sheet.update("B2", str(last_update_id))
