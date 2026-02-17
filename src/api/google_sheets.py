from dataclasses import dataclass
from pathlib import Path
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


@dataclass
class GoogleSheetAPI:
    creds_path: Path = Path(__file__).parent.parent / 'src' / 'api' / 'credentials.json'
    scopes: list = None

    def __post_init__(self):
        if not self.creds_path.exists():
            raise FileNotFoundError(f"Google credentials file not found at {self.creds_path}")
        if self.scopes is None:
            self.scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        creds = Credentials.from_service_account_file(self.creds_path, scopes=self.scopes)
        self.drive_service = build('drive', 'v3', credentials=creds)
        self.client = gspread.authorize(creds)

    def share_sheet_with_service_account(self, sheet_id):
        try:
            self.drive_service.permissions().create(
                fileId=sheet_id,
                body={
                    'type': 'user',
                    'role': 'writer',
                    'emailAddress': self.client.auth.service_account_email
                },
                fields='id'
            ).execute()
            print(f"Sheet {sheet_id} shared successfully with service account.")
        except HttpError as e:
            print(f"Error sharing sheet: {e}")


@dataclass
class Workbook:
    sheets_url: str
    api: GoogleSheetAPI
    worksheet_name: str = "Sheet1"

    def __post_init__(self):
        self.workbook = self.api.client.open_by_url(self.sheets_url)
        self.sheet = self.workbook.worksheet(self.worksheet_name)

    def search(self, student_number: str):
        records = self.sheet.get_all_records()
        for student in records:
            if student['Student Number'] == student_number:
                return student['Complete Name']
        return None

    def log_attendance(self, student_number: str, complete_name: str, timestamp: str):
        self.sheet.append_row([student_number, complete_name, timestamp])