from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
import gspread
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

@dataclass
class GoogleSheetAPI:
    creds_path: Path
    shared_drive_folder_id: Optional[str] = None
    scopes: Optional[List[str]] = None

    def __post_init__(self):
        if not self.creds_path.exists():
            raise FileNotFoundError(
                f"Google credentials not found at {self.creds_path}"
            )

        if self.scopes is None:
            self.scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]

        credentials = Credentials.from_service_account_file(
            self.creds_path,
            scopes=self.scopes
        )

        self.client = gspread.authorize(credentials)
        self.drive_service = build(
            "drive",
            "v3",
            credentials=credentials
        )