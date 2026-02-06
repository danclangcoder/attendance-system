from attendance import attendance_log
# from devices import qr_camera, qr_scanner
from sha import sha_256
# from db import database
from gui.attendance_app import AttendanceApp
# from api import google_sheets

if __name__ == '__main__':
    app = AttendanceApp()
    app.mainloop()