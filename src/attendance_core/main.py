from google_api import google_sheets
from devices import qr_scanner, qr_camera
from sha import sha_256
from attendance import attendance_log
from config import *
import json

if __name__ == '__main__':
    '''Scanning devices: Desktop 2D Barcode Reader (QR) or Webcam'''

    '''
    Desktop 2D Barcode Reader (QR)
        attendance_log.log_attendance(qr_scanner, users_file=USERS_FILE, logs_file=LOGS_FILE, sha=sha_256)
    '''

    '''
    Webcam
        attendance_log.log_attendance(qr_camera, users_file=USERS_FILE, logs_file=LOGS_FILE, sha=sha_256)
    '''

    # Sample scan
    attendance_log.log_attendance(qr_camera, users_file=USERS_FILE, logs_file=LOGS_FILE, sha=sha_256)