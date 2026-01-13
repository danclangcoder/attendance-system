import re
import cv2
import time
from pyzbar.pyzbar import decode
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==============================
# GOOGLE SHEETS SETUP
# ==============================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json", scope
)

client = gspread.authorize(creds)

# PALITAN KUNG IBA ANG SHEET NAME MO
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


# ==============================
# CAMERA SETUP
# ==============================
cam = cv2.VideoCapture(0)

cam.set(3, 640)  # Width
cam.set(4, 480)  # Height

camera_open = True

# Prevent duplicate scan habang bukas ang app
scanned_codes = []

print("QR Scanner Started (Press Q to quit)")

#
def parse_qr_data(qr_text):
    student_id = "UNKNOWN"
    name = "UNKNOWN"
    course = "UNKNOWN"
    section = "UNKNOWN"

    # Student ID (number with 6+ digits)
    id_match = re.search(r"\b\d{6,}\b", qr_text)
    if id_match:
        student_id = id_match.group()

    # Name (letters + spaces, may capital)
    name_match = re.search(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)+)", qr_text)
    if name_match:
        name = name_match.group()

    # Course (common courses)
    course_match = re.search(r"\b(BSIT|BSCS|BSBA|BSHM|BSED|BEED)\b", qr_text)
    if course_match:
        course = course_match.group()

    # Section (e.g. 1A, 2B, 3-C)
    section_match = re.search(r"\b\d[A-Z]\b", qr_text)
    if section_match:
        section = section_match.group()

    return student_id, name, course, section


# ==============================
# MAIN LOOP
# ==============================
while camera_open:
    success, frame = cam.read()

    if not success:
        print("Camera device not selected.")
        break

    # ...existing code...

for output in decode(frame):
    str_txt = output.data.decode("utf-8")

    if str_txt in scanned_codes:
        print("Already scanned")
        time.sleep(2)
    else:
        student_id, name, course, section = parse_qr_data(str_txt)

        log_attendance(student_id, name, course, section)

        print(f"Logged: {name}")
        scanned_codes.append(str_txt)
        time.sleep(2)

# ...existing code...

    cv2.imshow("QR Scanner", frame)

    if cv2.waitKey(1) == ord("q"):
        break

    if cv2.getWindowProperty("QR Scanner", cv2.WND_PROP_VISIBLE) < 1:
        break


# ==============================
# CLEANUP
# ==============================
cam.release()
cv2.destroyAllWindows()
print("Scanner Closed")