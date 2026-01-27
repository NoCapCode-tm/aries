import os, json, datetime, random
from telegram import Bot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")

bot = Bot(BOT_TOKEN)

# --------------------
# ACKNOWLEDGEMENT MESSAGES
# --------------------
ACK_MESSAGES = [
    "Thanks! Your update is noted 👍",
    "Got it — thanks for sharing 👍",
    "Noted! Appreciate the update 😊",
    "Thanks for the update, logged 👍",
    "All noted. Good work today 🙌",
    "Update received — thanks for sharing 👍",
    "Noted. Appreciate you taking the time 😊",
    "Got it! Thanks for the update 👍",
    "Thanks — your update is safely recorded 👍",
    "All set! Update received 🙌"
]

# --------------------
# Google auth
# --------------------
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

# --------------------
# Read last processed update_id
# --------------------
last_update_id = int(meta_sheet.cell(2, 2).value)

updates = bot.get_updates(offset=last_update_id, timeout=10)

for u in updates:
    # IMPORTANT: move offset forward FIRST (prevents duplicates)
    last_update_id = u.update_id + 1

    if not u.message or not u.message.text:
        continue

    # Ignore commands like /start
    if u.message.text.startswith("/"):
        continue

    user = u.message.from_user
    msg = u.message.text.strip()
    now = datetime.datetime.now()

    # --------------------
    # Save to Updates sheet
    # --------------------
    updates_sheet.append_row([
        now.strftime("%Y-%m-%d"),
        user.first_name,
        user.username,
        msg,
        now.strftime("%H:%M")
    ])

    # --------------------
    # Send to founders group
    # --------------------
    formatted = f"""📅 {now.strftime('%d %b %Y')} | {now.strftime('%H:%M')}
👤 {user.first_name}
📝 {msg}
"""
    bot.send_message(chat_id=GROUP_ID, text=formatted)

    # --------------------
    # Acknowledge employee (random message)
    # --------------------
    bot.send_message(
        chat_id=user.id,
        text=random.choice(ACK_MESSAGES)
    )

# --------------------
# Save updated offset
# --------------------
meta_sheet.update("B2", str(last_update_id))
