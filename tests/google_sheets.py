import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# GOOGLE SHEETS SETUP
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "tests/credentials.json", scope
)

client = gspread.authorize(creds)
sheet = client.open("AttendanceLogs").sheet1


def log_attendance(student_id, name, course, section):
    now = datetime.now()
    time_in = now.strftime("%H:%M:%S")
    date_today = now.strftime("%Y-%m-%d")

    sheet.append_row([
        student_id,
        name,
        course,
        section,
        time_in,
        date_today
    ])