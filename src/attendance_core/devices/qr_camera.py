import cv2
from pyzbar.pyzbar import decode

def scan_qr():

    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # Width and Height of the app window
    cam.set(3, 640)
    cam.set(4, 480)

    camera_open = True

    # Empty list for storing QR to prevent continouos process and crashing

    while camera_open:
        success, frame = cam.read()

        if not success:
            print('Camera device not selected.')
            break

        for output in decode(frame):
            str_txt = output.data.decode('utf-8')
            return str_txt
        
        mirror_view = cv2.flip(frame, 1)
        cv2.imshow('QR Scanner', mirror_view)
        esc_key = chr(27)
        
        if cv2.waitKey(1) == ord(esc_key):
            break
        
        if cv2.getWindowProperty('QR Scanner', cv2.WND_PROP_VISIBLE) < 1:
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    QR = scan_qr()
    print(QR)