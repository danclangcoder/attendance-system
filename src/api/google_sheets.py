from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass
import json

import gspread
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


@dataclass
class GoogleSheetAPI:
    client_secret_path: Path
    token_dir: Path
    user_id: str
    scopes: Optional[List[str]] = None

    def __post_init__(self):
        if not self.client_secret_path.exists():
            raise FileNotFoundError(
                f"OAuth client secret not found at {self.client_secret_path}"
            )

        if self.scopes is None:
            self.scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]

        self.token_dir.mkdir(parents=True, exist_ok=True)
        self.token_path = self.token_dir / f"{self.user_id}_token.json"

        credentials = self._authenticate_user()

        self.client = gspread.authorize(credentials)
        self.drive_service = build("drive", "v3", credentials=credentials)

    def _authenticate_user(self) -> Credentials:
        """
        Handles OAuth login, token saving, and automatic refresh.
        """
        creds = None

        # Load existing token if available
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(
                self.token_path,
                self.scopes
            )

        # If no valid credentials, start OAuth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.client_secret_path,
                    self.scopes
                )
                creds = flow.run_local_server(port=0)

            # Save token for this user
            with open(self.token_path, "w") as token_file:
                token_file.write(creds.to_json())

        return creds