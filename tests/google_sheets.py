import gspread
from google.oauth2.service_account import Credentials

# GOOGLE SHEETS SETUP
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDS = Credentials.from_service_account_file('tests/credentials.json', scopes=SCOPES)
CLIENT = gspread.authorize(CREDS)

def search_by_id(id, wb):
    for section in workbook.worksheets():
        records = section.get_all_records()

        for row, student in enumerate(records, start= 1):
            if id == student['Student Number']:
                return f'{student['Complete Name']} {student['Status']}'
                
def verify_by_sha(sha_key, filename):
    if sha_key in filename.values():
        return filename
    return

def log_attendance(id, wb):
    ...

if __name__ == '__main__':
    # Linking Google Sheets
    sheet_url = 'https://docs.google.com/spreadsheets/d/16y8xpRNcwNdvnQTWgYn48q7QIhvUdwegv1az1JTAA3k/edit?usp=sharing'
    workbook = CLIENT.open_by_url(sheet_url)

    student_id = 'A123F0029'
    result = search_by_id(student_id, workbook)
    print(result)