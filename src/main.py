from google_api.google_sheets import *
from devices import qr_scanner, qr_camera
import attendance

if __name__ == '__main__':
    '''Scanning devices: Desktop 2D Barcode Reader (QR) 
    or Webcam'''

    '''Desktop 2D Barcode Reader (QR)
    attendance.register(qr_scanner)
    attendance.log_attendance(qr_scanner)
    '''

    '''Webcam
    attendance.register(qr_camera)
    attendance.log_attendance(qr_camera)
    '''