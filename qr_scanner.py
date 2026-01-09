import cv2, time
from pyzbar.pyzbar import decode

cam = cv2.VideoCapture(0)

# Width and Height of the app window
cam.set(3, 640)
cam.set(4, 480)

camera_open = True

# Empty list for storing QR to prevent continouos process and crashing
scanned_codes = []

while camera_open:
    success, frame = cam.read()

    if not success:
        print('Camera device not selected.')
        break

    for output in decode(frame):
        str_txt = output.data.decode('utf-8')

        if str_txt in scanned_codes:
            print('Already scanned')
            time.sleep(3)
        else:
            print(str_txt)
            scanned_codes.append(str_txt)
            time.sleep(3)

    cv2.imshow('QR Scanner', frame)
    
    if cv2.waitKey(1) == ord("q"):
        break

cam.release()   
cv2.destroyAl1lWindows()