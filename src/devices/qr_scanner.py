import cv2, hashlib
from serial import Serial
from serial.tools import list_ports
from pyzbar.pyzbar import decode

def create_key(qr: str) -> str | ValueError:
    if qr == str(''):
        return ValueError('Does not contain a valid string.')
    else:
        new_hash = hashlib.new('sha256')
        new_hash.update(qr.encode())
        new_key = new_hash.hexdigest()
        return new_key

class WebcamScanner:
    def __init__(self, cam_index=0):
        self.cam_index = cam_index
        self.cap = None

    @staticmethod
    def is_available(cam_index=0):
        cap = cv2.VideoCapture(cam_index)
        if not cap.isOpened():
            return False
        cap.release()
        return True

    def open(self):
        self.cap = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise Exception("Webcam not detected.")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def read(self):
        if not self.cap:
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None

        # Grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        gray = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )
        decoded_objects = decode(gray)
        for obj in decoded_objects:
            qr_data = obj.data.decode("utf-8").strip()
            if qr_data:
                return frame, create_key(qr_data)
        return frame, None

    def close(self):
        if self.cap:
            self.cap.release()
            self.cap = None

class USBQRScanner:
    def __init__(self, port="COM3", baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.usb = None

    @staticmethod
    def is_connected(port="COM3"):
        ports = [p.device for p in list_ports.comports()]
        return port in ports

    def open(self):
        if not USBQRScanner.is_connected(self.port):
            raise Exception("USB QR Scanner not detected.")

        self.usb = Serial(self.port, baudrate=self.baudrate, timeout=0)

    def read(self):
        if self.usb and self.usb.in_waiting:
            qr_code = self.usb.readline().decode(
                encoding="utf-8",
                errors="ignore"
            ).strip()

            if qr_code:
                return create_key(qr_code)

        return None

    def close(self):
        if self.usb and self.usb.is_open:
            self.usb.close()