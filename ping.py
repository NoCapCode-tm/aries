import os, json, datetime, random
from telegram import Bot
import gspread
from oauth2client.service_account import ServiceAccountCredentials

BOT_TOKEN = os.getenv("BOT_TOKEN")
GOOGLE_CREDS_JSON = os.getenv("GOOGLE_CREDS_JSON")

bot = Bot(BOT_TOKEN)

# ========================
# CHECK-IN MESSAGES
# ========================
CHECKIN_MESSAGES = [
    "Hi {name} 👋\nThis is Aries checking in.\nWhat did you work on today at NoCapCode?",
    "Hey {name} 🙂\nHope your day went well.\nQuick check-in — what did you get done today?",
    "Hi {name} 👋\nJust a friendly end-of-day check.\nWhat progress did you make today at NoCapCode?",
    "Hey {name} 🌱\nWrapping things up?\nTell me what you worked on today.",
    "Hi {name},\nAries here with a quick check-in.\nWhat did you spend your time building today?",
    "Hey {name} 👋\nHope things moved forward today.\nWhat did you work on at NoCapCode?",
    "Hi {name} 🙂\nOne small update before we close the day — what did you work on today?",
    "Hey {name},\nJust checking in.\nWhat progress did you make today?",
    "Hi {name} 👋\nEnd-of-day check-in from Aries.\nWhat did you get done today?",
    "Hey {name} 🌙\nBefore you log off — what did you work on today?",
    "Hi {name},\nQuick daily check from Aries.\nWhat did you work on today at NoCapCode?",
    "Hey {name} 👋\nHope your day had some wins.\nWhat did you work on today?",
    "Hi {name} 🙂\nJust a gentle check-in.\nWhat progress did you make today?",
    "Hey {name},\nDaily wrap-up time.\nWhat did you get done today at NoCapCode?",
    "Hi {name} 👋\nChecking in before the day ends.\nWhat did you work on today?",
    "Hey {name} 🌤️\nHope the day treated you well.\nWhat did you spend your time on today?",
    "Hi {name},\nSmall update check.\nWhat did you move forward today?",
    "Hey {name} 👋\nJust a quick nudge from Aries.\nWhat did you work on today?",
    "Hi {name} 🙂\nEnd-of-day sync.\nWhat did you work on today at NoCapCode?",
    "Hey {name} 🌙\nOne last thing before you log off — what did you work on today?"
]

# ========================
# GOOGLE SHEETS SETUP
# ========================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(
    json.loads(GOOGLE_CREDS_JSON), scope
)
client = gspread.authorize(creds)
employees_sheet = client.open("Aries Daily Updates").worksheet("Employees")

# ========================
# SEND DAILY PING
# ========================
if datetime.datetime.today().weekday() < 5:
    for emp in employees_sheet.get_all_records():

        if str(emp["Active"]).strip().upper() != "YES":
            continue

        try:
            message = random.choice(CHECKIN_MESSAGES).format(
                name=emp["FirstName"]
            )

            bot.send_message(
                chat_id=int(emp["TelegramID"]),
                text=message
            )

        except Exception as e:
            print(f"Skip {emp['FirstName']}: {e}")
