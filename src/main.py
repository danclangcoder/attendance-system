from pathlib import Path
from gui.app import AttendanceApp
from db.database import init_db
from api.excel_spreadsheets import LocalExcel
from api.google_sheets import GoogleSheetAPI

PROJECT_ROOT = Path(__file__).parent
GOOGLE_CREDS_PATH = PROJECT_ROOT / "api" / "credentials.json"

# Initialize DB
init_db()

local_excel = LocalExcel(file_path=None)

# Google Sheets API
google_api = GoogleSheetAPI(creds_path=GOOGLE_CREDS_PATH)

# Initially no workbook (URL will be set via Menubar)
workbook = None

# Launch app
app = AttendanceApp(local_excel=local_excel, workbook=workbook)
app.google_api = google_api
app.mainloop()