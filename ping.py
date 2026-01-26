import os, json, datetime
from telegram import Bot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

BOT_TOKEN = os.getenv("BOT_TOKEN")
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

employees_sheet = client.open("Aries Daily Updates").worksheet("Employees")

# Run only on weekdays
if datetime.datetime.today().weekday() < 5:
    for emp in employees_sheet.get_all_records():
        if str(emp["Active"]).strip().upper() != "YES":
            continue

        try:
            bot.send_message(
                chat_id=int(emp["TelegramID"]),
                text=f"""Hey {emp['FirstName']} 👋
Hope you had a productive day.

Quick check-in — what did you work on today at NoCapCode?
Just reply to this message (1–2 lines is perfect)."""
            )
        except Exception as e:
            print("Skip:", emp["FirstName"], e)
