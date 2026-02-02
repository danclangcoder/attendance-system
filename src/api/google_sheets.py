import gspread
from google.oauth2.service_account import Credentials
from pathlib import Path
from dataclasses import dataclass

# GOOGLE SHEETS SETUP
@dataclass
class GoogleSheetAPI:
    # Default directory
    creds_path: Path = Path(__file__).parent / 'credentials.json'
    scopes: list = None

    def __post_init__(self):
        creds = Credentials.from_service_account_file(self.creds_path, scopes=self.scopes)
        self.client = gspread.authorize(creds)

@dataclass
class Workbook:
    sheets_url: str
    api: GoogleSheetAPI

    def __post_init__(self):
        self.workbook = self.api.client.open_by_url(self.sheets_url)
        self.workbook_title = self.workbook.title

    def search(self, student_number: str):
        for sheet in self.workbook.worksheets():
            records = sheet.get_all_records(
                expected_headers=['No.', 'Student Number', 'Complete Name']
            )

            for student in records:
                if student['Student Number'] == student_number:
                    return f'{student['Complete Name']}'
                
        return None