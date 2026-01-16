import gspread
from google.oauth2.service_account import Credentials

# GOOGLE SHEETS SETUP
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDS = Credentials.from_service_account_file('tests/credentials.json', scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)

def search_by_id(id, wb):
    for section in workbook.worksheets():
        records = section.get_all_records()

        for row, student in enumerate(records):
            if student.get('Student Number') == id:
                return student['Complete Name']
            
def log_attendance(id, wb):
    # Pass search function to reference student
    # Log status and timestamp

    # if current_time > subject_time + grace_period:
    #   return LATE
    # elif current_time > cut_off_time:
    #   return ABSENT
    # else:
    #   return PRESENT
    ...

if __name__ == '__main__':
    # Linking Google Sheets
    sheet_url = 'https://docs.google.com/spreadsheets/d/16y8xpRNcwNdvnQTWgYn48q7QIhvUdwegv1az1JTAA3k/edit?usp=sharing'
    workbook = CLIENT.open_by_url(sheet_url)

    student_id = 'A123F0024'
    my_id = search_by_id(student_id, workbook)