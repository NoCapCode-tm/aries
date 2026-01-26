import os, json, datetime
from telegram import Bot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")

bot = Bot(BOT_TOKEN)

scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(json.loads(GOOGLE_CREDS_JSON), scope)
client = gspread.authorize(creds)

employees = client.open("Aries Daily Updates").worksheet("Employees")

if datetime.datetime.today().weekday() < 5:
    for e in employees.get_all_records():
        if e["Active"] == "YES":
            try:
                bot.send_message(
                    chat_id=int(e["TelegramID"]),
                    text=f"Hey {e['FirstName']} 👋\nWhat did you work on today at NoCapCode?"
                )
            except: pass
