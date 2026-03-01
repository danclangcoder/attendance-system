import sys
import os

sys.path.append(os.path.dirname(__file__))

from gui.app import AttendanceApp
from db.database import init_db
from sheets.excel import Excel

init_db()
local_excel = Excel(file_path=None)
app = AttendanceApp(file=local_excel)
app.mainloop()