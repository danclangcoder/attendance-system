from serial import Serial
import cv2
from pyzbar.pyzbar import decode
from sha.sha_256 import create_key

class USBQRScanner:
    def __init__(self, port="COM3", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.usb = None

    def open(self):
        self.usb = Serial(self.port, baudrate=self.baudrate, timeout=0)

    def read(self):
        if self.usb and self.usb.in_waiting:
            qr_code = self.usb.readline().decode(encoding="utf-8", errors="ignore").strip()
            hash_key = create_key(qr_code)
            return hash_key
        return None

    def close(self):
        if self.usb and self.usb.is_open:
            self.usb.close()

class WebcamScanner:
    def __init__(self, cam_index=0):
        self.cam_index = cam_index
        self.cap = None

    def open(self):
        self.cap = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

    def read(self):
        if not self.cap:
            return None, None

        ret, frame = self.cap.read()
        if not ret:
            return None, None

        qr_data = None

        for qr in decode(frame):
            qr_data = qr.data.decode("utf-8")
            break

        # ALWAYS return frame
        if qr_data:
            return frame, create_key(qr_data)

        return frame, None

    def close(self):
        if self.cap:
            self.cap.release()
            self.cap = None