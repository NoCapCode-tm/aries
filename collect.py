import os, json, datetime
from telegram import Bot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")

bot = Bot(BOT_TOKEN)

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(GOOGLE_CREDS_JSON), scope)
client = gspread.authorize(creds)

updates_sheet = client.open("Aries Daily Updates").worksheet("Updates")

offset_file = "offset.txt"
offset = int(open(offset_file).read()) if os.path.exists(offset_file) else 0

updates = bot.get_updates(offset=offset, timeout=10)

for u in updates:
    if not u.message or not u.message.text:
        continue

    user = u.message.from_user
    msg = u.message.text
    now = datetime.datetime.now()

    updates_sheet.append_row([
        now.strftime("%Y-%m-%d"),
        user.first_name,
        user.username,
        msg,
        now.strftime("%H:%M")
    ])

    bot.send_message(
        chat_id=GROUP_ID,
        text=f"🟢 Daily Update\n👤 {user.first_name}\n📝 {msg}"
    )

    bot.send_message(
        chat_id=user.id,
        text="Thanks! Your update is noted 👍"
    )

    offset = u.update_id + 1

open(offset_file,"w").write(str(offset))
